#!/usr/bin/env python3
"""
Clean up and re-extract all UI icons with latest updates.

This script will:
1. Clean up existing extracted icons
2. Re-extract all icon categories with latest methods
3. Apply ITM 16x16 grid extraction
4. Apply item 32x32 grid extraction
5. Apply spell 64x64 grid extraction
6. Create unified icon index
"""

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image


def convert_dds_to_png(dds_path: Path, png_path: Path) -> bool:
    """Convert DDS file to PNG using ImageMagick."""
    try:
        png_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["magick", "convert", str(dds_path), str(png_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0 and png_path.exists()
    except Exception as e:
        print(f"  ⚠ Conversion failed for {dds_path.name}: {e}")
        return False


def extract_icons_from_atlas(
    atlas_png: Path,
    output_dir: Path,
    grid_size: int,
    icon_size: int,
    offset_x: int = 0,
    offset_y: int = 0,
    rotate: int = 0,
) -> list[Path]:
    """Extract icons from atlas with given parameters."""
    try:
        atlas = Image.open(atlas_png)
        output_dir.mkdir(parents=True, exist_ok=True)
        extracted = []

        for row in range(grid_size):
            for col in range(grid_size):
                x = offset_x + (col * icon_size)
                y = offset_y + (row * icon_size)

                if x + icon_size > atlas.size[0] or y + icon_size > atlas.size[1]:
                    continue

                icon = atlas.crop((x, y, x + icon_size, y + icon_size))

                if rotate != 0:
                    icon = icon.rotate(rotate, expand=False)

                index = row * grid_size + col + 1
                icon_path = output_dir / f"icon_{index:03d}.png"
                icon.save(icon_path)
                extracted.append(icon_path)

        return extracted
    except Exception as e:
        print(f"  ⚠ Error extracting from {atlas_png}: {e}")
        return []


def analyze_itm_patterns(output_dir: Path) -> dict:
    """Analyze ITM icons for multi-icon weapons."""
    patterns = {
        "single_icons": [],
        "horizontal_pairs": [],
        "horizontal_quads": [],
        "empty_slots": [],
    }

    icons = {}
    for icon_path in output_dir.glob("icon_*.png"):
        index = int(icon_path.stem.replace("icon_", ""))
        try:
            icons[index] = Image.open(icon_path)
        except:
            continue

    if not icons:
        return patterns

    # Check for empty icons
    for index, icon in sorted(icons.items()):
        rgb_icon = icon.convert("RGB")
        pixels = list(rgb_icon.getdata())
        if len(set(pixels)) == 1:
            patterns["empty_slots"].append(index)
        else:
            patterns["single_icons"].append(index)

    # Check for 1x2 patterns
    single_copy = patterns["single_icons"].copy()
    for index in single_copy:
        if index in patterns["empty_slots"]:
            continue
        if (index + 1) in icons and (index + 1) not in patterns["empty_slots"]:
            if index % 16 <= 14:  # Not at right edge
                patterns["horizontal_pairs"].append((index, index + 1))
                if index in patterns["single_icons"]:
                    patterns["single_icons"].remove(index)
                if (index + 1) in patterns["single_icons"]:
                    patterns["single_icons"].remove(index + 1)

    # Check for 1x4 patterns
    single_copy = patterns["single_icons"].copy()
    for index in single_copy:
        if all(
            (index + i) in icons and (index + i) not in patterns["empty_slots"]
            for i in range(4)
        ):
            if index % 16 <= 12:  # Not too close to right edge
                patterns["horizontal_quads"].append(
                    (index, index + 1, index + 2, index + 3)
                )
                for i in range(4):
                    if (index + i) in patterns["single_icons"]:
                        patterns["single_icons"].remove(index + i)

    return patterns


def create_multi_icon_weapons(output_dir: Path, patterns: dict) -> list[Path]:
    """Create combined weapon images."""
    created = []

    # Create 1x2 weapons
    for icon1_idx, icon2_idx in patterns["horizontal_pairs"]:
        try:
            icon1 = Image.open(output_dir / f"icon_{icon1_idx:03d}.png")
            icon2 = Image.open(output_dir / f"icon_{icon2_idx:03d}.png")

            width = icon1.width + icon2.width
            height = max(icon1.height, icon2.height)
            combined = Image.new("RGBA", (width, height))
            combined.paste(icon1, (0, 0))
            combined.paste(icon2, (icon1.width, 0))

            weapon_path = output_dir / f"weapon_1x2_{icon1_idx:03d}.png"
            combined.save(weapon_path)
            created.append(weapon_path)
        except Exception as e:
            print(f"    ⚠ Could not combine {icon1_idx}+{icon2_idx}: {e}")

    # Create 1x4 weapons
    for icon_indices in patterns["horizontal_quads"]:
        try:
            icons = [
                Image.open(output_dir / f"icon_{idx:03d}.png") for idx in icon_indices
            ]
            width = sum(icon.width for icon in icons)
            height = max(icon.height for icon in icons)
            combined = Image.new("RGBA", (width, height))

            x_offset = 0
            for icon in icons:
                combined.paste(icon, (x_offset, 0))
                x_offset += icon.width

            weapon_path = output_dir / f"weapon_1x4_{icon_indices[0]:03d}.png"
            combined.save(weapon_path)
            created.append(weapon_path)
        except Exception as e:
            print(f"    ⚠ Could not combine {icon_indices}: {e}")

    return created


def clean_icon_directories(base_dir: Path):
    """Clean up existing icon directories."""
    print("Cleaning up existing icon directories...")

    dirs_to_clean = [
        base_dir / "icons_extracted",
        base_dir / "itm_icons_extracted",
    ]

    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print(f"  Removing {dir_path.name}...")
            shutil.rmtree(dir_path)

    print("  ✓ Cleanup complete")


def main():
    """Main cleanup and re-extraction process."""

    project_root = Path(__file__).parent.parent.parent
    extracted_ui = project_root / "ExtractedAssets" / "UI" / "extracted"
    output_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"

    print("=" * 80)
    print("CLEAN UP AND RE-EXTRACT ALL ICONS")
    print("=" * 80)
    print(f"Input:  {extracted_ui}")
    print(f"Output: {output_root}")
    print()

    # Clean up first
    clean_icon_directories(project_root / "ExtractedAssets" / "UI")

    # Statistics
    stats = {
        "categories_processed": 0,
        "atlases_converted": 0,
        "icons_extracted": 0,
        "weapons_created": 0,
        "categories": {},
    }

    # Find all UI DDS files
    dds_files = list(extracted_ui.rglob("ui_*.dds"))
    print(f"Found {len(dds_files)} UI texture files")
    print()

    # Group by category
    by_category = {}
    for dds in dds_files:
        parts = dds.stem.split("_")
        if len(parts) >= 2:
            category = parts[1]
            import re

            match = re.match(r"([a-z]+)(\d+)", category)
            if match:
                cat_name = match.group(1)
                cat_num = match.group(2)
                by_category.setdefault(cat_name, []).append((cat_num, dds))

    print(f"Found {len(by_category)} categories:")
    for cat, files in sorted(by_category.items()):
        print(f"  - {cat}: {len(files)} atlases")
    print()

    # Process each category with appropriate settings
    category_settings = {
        "itm": {
            "grid_size": 16,
            "icon_size": 16,
            "offset_x": 0,
            "offset_y": 0,
            "rotate": 0,
            "analyze_patterns": True,
        },
        "item": {
            "grid_size": 8,
            "icon_size": 32,
            "offset_x": 0,
            "offset_y": 0,
            "rotate": 0,
            "analyze_patterns": False,
        },
        "spell": {
            "grid_size": 4,
            "icon_size": 64,
            "offset_x": 3,
            "offset_y": 3,
            "rotate": 180,
            "analyze_patterns": False,
        },
    }

    # Process categories
    for cat_name, settings in category_settings.items():
        if cat_name not in by_category:
            print(f"⚠ Category '{cat_name}' not found, skipping")
            continue

        print(f"Processing category: {cat_name.upper()}")
        print("-" * 80)

        cat_files = sorted(by_category[cat_name], key=lambda x: int(x[0]))
        cat_stats = {
            "atlases_found": len(cat_files),
            "atlases_converted": 0,
            "icons_extracted": 0,
            "weapons_created": 0,
        }

        for atlas_num, dds_path in cat_files:
            # Create output directory
            atlas_output = output_root / cat_name / f"atlas_{atlas_num}"

            # Convert DDS to PNG
            temp_png = atlas_output / f"_atlas_{atlas_num}.png"
            print(f"  [{cat_name}_{atlas_num}] Converting...", end=" ", flush=True)

            if convert_dds_to_png(dds_path, temp_png):
                print("✓")
                cat_stats["atlases_converted"] += 1

                # Extract icons
                print(f"  [{cat_name}_{atlas_num}] Extracting...", end=" ", flush=True)
                extracted = extract_icons_from_atlas(
                    temp_png,
                    atlas_output,
                    **{k: v for k, v in settings.items() if k != "analyze_patterns"},
                )

                if extracted:
                    print(f"✓ ({len(extracted)} icons)")
                    cat_stats["icons_extracted"] += len(extracted)

                    # Analyze patterns for ITM
                    if settings.get("analyze_patterns", False):
                        print(
                            f"  [{cat_name}_{atlas_num}] Analyzing patterns...",
                            end=" ",
                            flush=True,
                        )
                        patterns = analyze_itm_patterns(atlas_output)
                        weapons = create_multi_icon_weapons(atlas_output, patterns)
                        cat_stats["weapons_created"] += len(weapons)
                        print(
                            f"✓ ({len(patterns['horizontal_pairs'])} pairs, {len(patterns['horizontal_quads'])} quads)"
                        )
                else:
                    print("✗")
            else:
                print("✗")

        stats["categories"][cat_name] = cat_stats
        stats["categories_processed"] += 1
        stats["atlases_converted"] += cat_stats["atlases_converted"]
        stats["icons_extracted"] += cat_stats["icons_extracted"]
        stats["weapons_created"] += cat_stats["weapons_created"]
        print()

    # Create unified icon index
    print("Creating unified icon index...")
    index_data = {
        "stats": stats,
        "icons": {},
        "extraction_info": {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "categories_processed": list(category_settings.keys()),
        },
    }

    # Build index from all extracted icons
    for icon_file in output_root.rglob("icon_*.png"):
        parts = icon_file.relative_to(output_root).parts
        if len(parts) == 3:
            category = parts[0]
            atlas = parts[1].replace("atlas_", "")
            icon_num = icon_file.stem.replace("icon_", "")

            key = f"{category}_{atlas}_{icon_num}"
            index_data["icons"][key] = {
                "category": category,
                "atlas_number": atlas,
                "icon_index": int(icon_num),
                "path": str(icon_file.relative_to(output_root)),
            }

    # Save unified index
    index_path = output_root / "icon_index.json"
    with open(index_path, "w") as f:
        json.dump(index_data, f, indent=2)
    print(f"✓ Unified index saved: {index_path.name}")
    print()

    # Print summary
    print("=" * 80)
    print("RE-EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"Categories processed: {stats['categories_processed']}")
    print(f"Atlases converted:  {stats['atlases_converted']}")
    print(f"Icons extracted:    {stats['icons_extracted']}")
    print(f"Weapons created:    {stats['weapons_created']}")
    print()

    for cat_name, cat_stats in stats["categories"].items():
        print(f"{cat_name.upper()}:")
        print(f"  Atlases:  {cat_stats['atlases_found']}")
        print(f"  Icons:    {cat_stats['icons_extracted']}")
        if cat_stats["weapons_created"] > 0:
            print(f"  Weapons:  {cat_stats['weapons_created']}")
    print()

    print(f"Output: {output_root}")
    print("=" * 80)
    print()
    print("✅ CLEAN UP AND RE-EXTRACTION COMPLETE!")
    print()
    print("All icons have been re-extracted with latest methods:")
    print("- ITM: 16x16 icons with multi-icon weapon detection")
    print("- Item: 32x32 icons with standard 8x8 grid")
    print("- Spell: 64x64 icons with rotation and offset")
    print()


if __name__ == "__main__":
    main()
