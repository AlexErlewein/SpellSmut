# SpellForce Asset Extraction Setup

## Prerequisites

To use the asset extraction tool, you need to have the original SpellForce Platinum Edition game files.

## Setup Instructions

1. **Locate your SpellForce installation directory**
   - This is typically located in your Steam library at:
     `Steam/steamapps/common/SpellForce Platinum Edition/`

2. **Copy PAK files**
   - Copy all `.pak` files from your SpellForce installation directory to:
     `OriginalGameFiles/pak/`
   - The PAK files are usually named like:
     - `sf0.pak`
     - `sf1.pak`
     - `sf2.pak`
     - etc.

3. **Verify setup**
   - After copying, your `OriginalGameFiles/pak/` directory should contain all the `.pak` files from the game.

## Using the Asset Extraction Tool

Once you've set up the PAK files, you can use either:

1. **Command-line version:**
   ```bash
   python3 src/helper_tools/extraction/asset_extractor.py --extract --create-reference
   ```

2. **GUI version:**
   ```bash
   python3 src/helper_tools/extraction/asset_extractor_gui.py
   ```

## Troubleshooting

If you encounter issues:

1. **Missing PAK files**: Make sure you've copied all `.pak` files from your SpellForce installation
2. **Permission errors**: Ensure you have read permissions for the PAK files
3. **QuickBMS not found**: Run `bulk_extract_paks.py` first to install QuickBMS