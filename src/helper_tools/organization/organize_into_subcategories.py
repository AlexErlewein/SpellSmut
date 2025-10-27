"""
Organize extracted files into detailed subcategories based on naming patterns.

This script analyzes file naming patterns and creates a more detailed
folder structure within each main category.
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
EXTRACTED_DIR = PROJECT_ROOT / "ExtractedAssets"


def organize_audio_files():
    """Organize audio files into subcategories."""
    print("\n" + "=" * 70)
    print("Organizing Audio Files...")
    print("=" * 70)

    audio_dir = EXTRACTED_DIR / "Audio" / "extracted"
    if not audio_dir.exists():
        print(f"Audio directory not found: {audio_dir}")
        return

    # Audio subcategories based on naming patterns
    categories = {
        'music_dialogue': {
            'pattern': lambda f: f.startswith('a_') and f.endswith('.mp3'),
            'description': 'Dialogue/voice acting (numbered MP3 files)'
        },
        'ambient': {
            'pattern': lambda f: f.startswith('atmo_'),
            'description': 'Atmospheric/environmental sounds'
        },
        'battle': {
            'pattern': lambda f: f.startswith('battle_'),
            'description': 'Combat sounds'
        },
        'spell': {
            'pattern': lambda f: f.startswith('spell_'),
            'description': 'Magic spell effects'
        },
        'work': {
            'pattern': lambda f: f.startswith('work_'),
            'description': 'Work/resource gathering'
        },
        'object': {
            'pattern': lambda f: f.startswith('object_'),
            'description': 'Object/building sounds'
        },
        'step': {
            'pattern': lambda f: f.startswith('step_') or f.startswith('wings_'),
            'description': 'Movement/footstep sounds'
        },
        'idle': {
            'pattern': lambda f: f.startswith('idle_'),
            'description': 'Idle character sounds'
        },
        'ui': {
            'pattern': lambda f: f.startswith('ui_') and f.endswith('.wav'),
            'description': 'User interface sounds'
        },
        'world': {
            'pattern': lambda f: f.startswith('world_'),
            'description': 'World event sounds'
        },
        'dummy': {
            'pattern': lambda f: f.startswith('dummy_'),
            'description': 'Placeholder/silence files'
        },
        'other': {
            'pattern': lambda f: True,  # Catch-all
            'description': 'Uncategorized audio'
        }
    }

    # Count and organize
    file_counts = defaultdict(int)

    for file in os.listdir(audio_dir):
        source = audio_dir / file
        if not source.is_file():
            continue

        # Find matching category
        categorized = False
        for cat_name, cat_info in categories.items():
            if cat_name == 'other':
                continue  # Skip catch-all for now

            if cat_info['pattern'](file):
                # Create subcategory folder
                dest_dir = audio_dir / cat_name
                dest_dir.mkdir(exist_ok=True)

                # Move file
                dest = dest_dir / file
                try:
                    shutil.move(str(source), str(dest))
                    file_counts[cat_name] += 1
                    categorized = True
                    break
                except Exception as e:
                    print(f"Error moving {file}: {e}")

        # If not categorized, put in "other"
        if not categorized:
            dest_dir = audio_dir / 'other'
            dest_dir.mkdir(exist_ok=True)
            dest = dest_dir / file
            try:
                shutil.move(str(source), str(dest))
                file_counts['other'] += 1
            except Exception as e:
                print(f"Error moving {file}: {e}")

    # Print summary
    print("\nAudio Organization Summary:")
    print("-" * 70)
    for cat in sorted(file_counts.keys()):
        count = file_counts[cat]
        desc = categories[cat]['description']
        print(f"  {cat:20s}: {count:5d} files - {desc}")
    print("-" * 70)
    print(f"  {'TOTAL':20s}: {sum(file_counts.values()):5d} files")


def organize_ui_files():
    """Organize UI files into subcategories."""
    print("\n" + "=" * 70)
    print("Organizing UI Files...")
    print("=" * 70)

    ui_dir = EXTRACTED_DIR / "UI" / "extracted"
    if not ui_dir.exists():
        print(f"UI directory not found: {ui_dir}")
        return

    # UI subcategories
    categories = {
        'fonts': {
            'pattern': lambda f: f.startswith('font_'),
            'description': 'Font textures'
        },
        'backgrounds': {
            'pattern': lambda f: f.startswith('ui_bgr'),
            'description': 'UI backgrounds/panels'
        },
        'buttons': {
            'pattern': lambda f: f.startswith('ui_btn'),
            'description': 'Button graphics'
        },
        'items': {
            'pattern': lambda f: f.startswith('ui_item') or f.startswith('ui_itm'),
            'description': 'Item icons'
        },
        'cursors': {
            'pattern': lambda f: f.startswith('ui_cursor'),
            'description': 'Mouse cursors'
        },
        'containers': {
            'pattern': lambda f: f.startswith('ui_cnt'),
            'description': 'Container frames'
        },
        'spells': {
            'pattern': lambda f: f.startswith('ui_spell'),
            'description': 'Spell icons'
        },
        'buildings': {
            'pattern': lambda f: f.startswith('ui_building'),
            'description': 'Building icons'
        },
        'mainmenu': {
            'pattern': lambda f: f.startswith('ui_mainmenu'),
            'description': 'Main menu graphics'
        },
        'splashscreen': {
            'pattern': lambda f: f.startswith('ui_splashscreen'),
            'description': 'Loading screens'
        },
        'clock': {
            'pattern': lambda f: f.startswith('ui_clock'),
            'description': 'Time/day-night UI'
        },
        'logo': {
            'pattern': lambda f: f.startswith('ui_logo'),
            'description': 'Game logos'
        },
        'portraits': {
            'pattern': lambda f: f.startswith('ui_portrait'),
            'description': 'Character portraits'
        },
        'minimap': {
            'pattern': lambda f: f.startswith('ui_minimap'),
            'description': 'Minimap elements'
        },
        'other': {
            'pattern': lambda f: True,
            'description': 'Other UI elements'
        }
    }

    file_counts = defaultdict(int)

    for file in os.listdir(ui_dir):
        source = ui_dir / file
        if not source.is_file():
            continue

        # Find matching category
        categorized = False
        for cat_name, cat_info in categories.items():
            if cat_name == 'other':
                continue

            if cat_info['pattern'](file):
                dest_dir = ui_dir / cat_name
                dest_dir.mkdir(exist_ok=True)

                dest = dest_dir / file
                try:
                    shutil.move(str(source), str(dest))
                    file_counts[cat_name] += 1
                    categorized = True
                    break
                except Exception as e:
                    print(f"Error moving {file}: {e}")

        if not categorized:
            dest_dir = ui_dir / 'other'
            dest_dir.mkdir(exist_ok=True)
            dest = dest_dir / file
            try:
                shutil.move(str(source), str(dest))
                file_counts['other'] += 1
            except Exception as e:
                print(f"Error moving {file}: {e}")

    # Print summary
    print("\nUI Organization Summary:")
    print("-" * 70)
    for cat in sorted(file_counts.keys()):
        count = file_counts[cat]
        desc = categories[cat]['description']
        print(f"  {cat:20s}: {count:5d} files - {desc}")
    print("-" * 70)
    print(f"  {'TOTAL':20s}: {sum(file_counts.values()):5d} files")


def organize_scripts():
    """Organize scripts into subcategories."""
    print("\n" + "=" * 70)
    print("Organizing Script Files...")
    print("=" * 70)

    scripts_dir = EXTRACTED_DIR / "Scripts"
    if not scripts_dir.exists():
        print(f"Scripts directory not found: {scripts_dir}")
        return

    # Count files by extension/type
    extensions = defaultdict(int)
    for file in os.listdir(scripts_dir):
        if (scripts_dir / file).is_file():
            ext = Path(file).suffix.lower()
            extensions[ext if ext else 'no_extension'] += 1

    print("\nScript Files by Extension:")
    print("-" * 70)
    for ext in sorted(extensions.keys()):
        print(f"  {ext:20s}: {extensions[ext]:5d} files")
    print("-" * 70)
    print(f"  {'TOTAL':20s}: {sum(extensions.values()):5d} files")

    # Could organize further if Lua scripts have clear naming patterns
    # For now, just report the breakdown


def main():
    """Main execution."""
    print("=" * 70)
    print(" " * 15 + "Advanced File Organization")
    print(" " * 10 + "Organizing into detailed subcategories")
    print("=" * 70)

    # Organize each category
    organize_audio_files()
    organize_ui_files()
    organize_scripts()

    print("\n" + "=" * 70)
    print("Organization Complete!")
    print("=" * 70)
    print("\nFiles have been organized into detailed subcategories.")
    print(f"Location: {EXTRACTED_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
