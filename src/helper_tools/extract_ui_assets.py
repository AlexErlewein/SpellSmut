"""
Script to help identify and extract UI assets from SpellForce game files.
This script will search through the pakdata.dat file to find UI-related assets.
"""

import os
import re
import struct
from pathlib import Path

# Directories
GAME_DIR = Path(r"H:\SpellSmut\OriginalGameFiles")
EDITOR_DIR = Path(r"H:\SpellSmut\ModdingTools\spellforce_data_editor\bin")
PAKDATA_FILE = EDITOR_DIR / "pakdata.dat"
OUTPUT_DIR = Path(r"H:\SpellSmut\ExtractedAssets\UI")

# UI-related keywords to search for
UI_KEYWORDS = [
    'ui', 'menu', 'button', 'icon', 'interface', 'cursor',
    'window', 'panel', 'hud', 'minimap', 'portrait',
    'inventory', 'spell', 'skill', 'frame', 'border',
    'scroll', 'tab', 'dialog', 'tooltip', 'bar'
]

def search_pakdata_for_ui_assets():
    """Search the pakdata.dat file for UI-related assets."""
    print(f"Reading pakdata file: {PAKDATA_FILE}")

    if not PAKDATA_FILE.exists():
        print(f"ERROR: pakdata.dat not found at {PAKDATA_FILE}")
        return []

    ui_files = []

    try:
        with open(PAKDATA_FILE, 'rb') as f:
            data = f.read()

            # Convert to string, ignoring errors
            try:
                text = data.decode('latin-1', errors='ignore')
            except:
                text = data.decode('utf-8', errors='ignore')

            # Search for file paths (look for patterns like .tga, .dds, .bmp)
            # Common image extensions in SpellForce
            patterns = [
                rb'[\x20-\x7E]+\.tga',
                rb'[\x20-\x7E]+\.dds',
                rb'[\x20-\x7E]+\.bmp',
                rb'[\x20-\x7E]+\.png',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, data)
                for match in matches:
                    try:
                        filepath = match.decode('latin-1').strip()
                        # Check if it contains UI keywords
                        filepath_lower = filepath.lower()
                        if any(keyword in filepath_lower for keyword in UI_KEYWORDS):
                            if filepath not in ui_files:
                                ui_files.append(filepath)
                                print(f"Found UI asset: {filepath}")
                    except:
                        pass

    except Exception as e:
        print(f"Error reading pakdata: {e}")

    return ui_files

def search_texture_directory():
    """List all textures in the texture directory."""
    print(f"\nSearching texture directory: {GAME_DIR / 'texture'}")

    texture_dir = GAME_DIR / "texture"
    if texture_dir.exists():
        textures = list(texture_dir.glob("*.tga"))
        print(f"Found {len(textures)} TGA files in texture directory")
        return textures
    return []

def list_pak_files():
    """List all PAK files."""
    pak_dir = GAME_DIR / "pak"
    if pak_dir.exists():
        pak_files = sorted(pak_dir.glob("*.pak"))
        print(f"\nFound {len(pak_files)} PAK files:")
        for pak in pak_files:
            size_mb = pak.stat().st_size / (1024 * 1024)
            print(f"  {pak.name}: {size_mb:.1f} MB")
        return pak_files
    return []

def create_output_directory():
    """Create output directory for extracted assets."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory created: {OUTPUT_DIR}")

def main():
    print("=" * 70)
    print("SpellForce UI Asset Extraction Helper")
    print("=" * 70)

    # Create output directory
    create_output_directory()

    # List PAK files
    pak_files = list_pak_files()

    # Search for UI assets in pakdata
    print("\n" + "=" * 70)
    print("Searching for UI-related assets in pakdata.dat...")
    print("=" * 70)
    ui_files = search_pakdata_for_ui_assets()

    if ui_files:
        print(f"\n[OK] Found {len(ui_files)} UI-related files in pakdata")

        # Save to text file
        output_list = OUTPUT_DIR / "ui_assets_list.txt"
        with open(output_list, 'w', encoding='utf-8') as f:
            f.write("UI Assets found in SpellForce PAK files\n")
            f.write("=" * 70 + "\n\n")
            for filepath in sorted(ui_files):
                f.write(f"{filepath}\n")
        print(f"[OK] Saved list to: {output_list}")
    else:
        print("[WARNING] No UI assets found in pakdata.dat")

    # List texture directory
    print("\n" + "=" * 70)
    print("Texture Directory Contents")
    print("=" * 70)
    textures = search_texture_directory()

    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("1. Use SpellforceDataEditor.exe to extract the UI assets")
    print("2. In the Asset Viewer tab, search for UI-related files")
    print("3. Set ExtractDirectory in config.txt to extract files")
    print(f"4. Extracted files will be organized in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
