#!/bin/bash
# Shell script to run the complete UI icon integration pipeline
# This script works on macOS and Linux
#
# Pipeline:
# 1. Extract UI assets with original names
# 2. Convert DDS to PNG (parallel processing)
# 3. Rotate PNGs by 180 degrees
# 4. Organize by category
#
# Requirements:
# - UV package manager installed (project standard)
# - ImageMagick installed (for DDS conversion)
# - Pillow installed (for PNG rotation)
# - SpellForce game installed

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

echo "Step 1: Extracting UI assets with original filenames..."
echo
uv run extract_ui_with_names.py --yes
if [ $? -ne 0 ]; then
    echo "ERROR: UI asset extraction failed"
    exit 1
fi
echo
echo "Step 1 completed successfully."
echo

echo "Step 2: Converting DDS files to PNG (parallel processing)..."
echo
uv run convert_ui_textures.py --yes
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
echo "2. Run the GUI editor to test icon display:"
echo "   cd ../../TirganachReloaded"
echo "   uv run tirganach"
echo "3. Verify icons appear in both table and property editor"
echo
echo "Extracted assets location:"
echo "  ExtractedAssets/UI/extracted/"
echo
echo "Fallback icons location:"
echo "  ExtractedAssets/UI/fallback_icons/"
echo
