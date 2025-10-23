#!/bin/bash
# Shell script to run the complete UI icon integration pipeline
# This script runs on macOS/Linux
#
# Pipeline:
# 1. Extract UI assets with original names
# 2. Convert DDS to PNG
# 3. Rotate PNGs by 180 degrees
# 4. Organize by category
#
# Requirements:
# - UV package manager installed (project standard)
# - ImageMagick installed (for DDS conversion)
# - Pillow installed (for PNG rotation)
# - PAK files available in OriginalGameFiles/pak/

set -e  # Exit on error

echo "========================================"
echo "SpellForce UI Icon Integration Pipeline"
echo "========================================"
echo

# Check if we're in the right directory
if [ ! -f "extract_ui_with_names.py" ]; then
    echo "ERROR: Please run this script from the src/helper_tools directory"
    exit 1
fi

# Check UV
if ! command -v uv &> /dev/null; then
    echo "ERROR: UV package manager not found. Please install UV."
    echo "Visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Check ImageMagick
if ! command -v magick &> /dev/null; then
    echo "WARNING: ImageMagick not found."
    echo "Install with: brew install imagemagick (macOS) or apt install imagemagick (Linux)"
    echo
    read -p "Continue anyway? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Pillow
if ! uv run python -c "from PIL import Image" 2>/dev/null; then
    echo "WARNING: Pillow not found."
    echo "Install with: uv pip install Pillow"
    echo
    read -p "Continue anyway? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Step 1: Extracting UI assets with original filenames..."
echo
uv run extract_ui_with_names.py
if [ $? -ne 0 ]; then
    echo "ERROR: UI asset extraction failed"
    exit 1
fi
echo
echo "Step 1 completed successfully."
echo

echo "Step 2: Converting DDS files to PNG..."
echo
uv run convert_ui_textures.py
if [ $? -ne 0 ]; then
    echo "ERROR: DDS to PNG conversion failed"
    exit 1
fi
echo
echo "Step 2 completed successfully."
echo

echo "Step 3: Rotating PNGs by 180 degrees..."
echo
uv run rotate_ui_pngs.py
if [ $? -ne 0 ]; then
    echo "ERROR: PNG rotation failed"
    exit 1
fi
echo
echo "Step 3 completed successfully."
echo

echo "Step 4: Organizing assets by category..."
echo
uv run organize_ui_assets.py
if [ $? -ne 0 ]; then
    echo "ERROR: Asset organization failed"
    exit 1
fi
echo
echo "Step 4 completed successfully."
echo

echo "========================================"
echo "UI ICON INTEGRATION COMPLETE!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Verify the extracted assets have correct filenames"
echo "2. Run the GUI editor to test icon display"
echo "3. Check icons appear in both table and property editor"
echo
echo "Extracted assets location:"
echo "  ExtractedAssets/UI/extracted/"
echo
echo "To test:"
echo "  cd ../../TirganachReloaded"
echo "  uv run tirganach"
echo

echo "Done! Press any key to exit..."
read -n 1 -s
