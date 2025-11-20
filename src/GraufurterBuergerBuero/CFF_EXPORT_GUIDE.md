# CFF Export Guide for Graufurter Bürger Büro

## Overview

The NPC Creator includes functionality to export custom NPCs to CFF (Configuration File Format) for integration into the SpellForce game.

## How to Use

### Step 1: Create Your NPC
1. Click "Create NPC" button in the main window
2. Complete all steps in the wizard:
   - Select creation mode (Create New, Edit Existing, or Duplicate)
   - Fill in NPC identity (name, title, description, type, class, etc.)
   - Set base stats and derived stats
   - Configure appearance
   - Set behavior parameters
   - Select equipment

### Step 2: Configure Export Options
On the final step ("Export & Review"), you'll see export options:

- **"Export to CFF format"** - Checked by default
  - Opens file dialog to choose export location and filename
  - Generates binary CFF category files
  - Includes integration instructions

- **"Export Lua behavior scripts"** - Checked by default
  - Saves as JSON (for future Lua script generation)

### Step 3: Export with File Dialog
1. Click "Export NPC" button
2. NPC is saved to JSON (`npcs/custom_npcs.json`)
3. If CFF export is enabled, a **File Save Dialog** appears:

   **Dialog Features:**
   - **Choose Location**: Navigate to any directory
   - **Custom Filename**: Set your preferred base name
   - **Smart Suggestions**: Auto-suggests filename based on NPC name + timestamp
   - **File Filter**: Shows "CFF Export Files (*.cff)" by default
   - **Overwrite Protection**: Warns before overwriting existing files

4. **File Selection**:
   - Enter base filename (e.g., `MyCustomNPC`)
   - System creates multiple files: `MyCustomNPC_category3001.bin`, etc.
   - Choose your preferred export directory

5. **Overwrite Confirmation**:
   - If files exist, shows list of files that will be overwritten
   - You can cancel to avoid losing previous exports

6. **Completion**:
   - Status shows success with exact file count and location
   - Creates summary file with integration instructions

## Generated Files

### CFF Category Files
Export creates multiple binary files in your chosen directory:

- `{YourBaseName}_category3001.bin` - NPC General Info
- `{YourBaseName}_category3002.bin` - NPC Base Stats
- `{YourBaseName}_category3003.bin` - NPC Combat Stats
- `{YourBaseName}_category3004.bin` - NPC Equipment
- `{YourBaseName}_category3005.bin` - NPC Behavior
- `{YourBaseName}_category2016.bin` - Text Entries (name, title, description)

### Summary File
- `{YourBaseName}_export_summary.txt` - Integration instructions

**Example**: If you choose base name `MyCoolKnight`, files will be:
- `MyCoolKnight_category3001.bin`
- `MyCoolKnight_category3002.bin`
- `MyCoolKnight_export_summary.txt`
- etc.

## Integration Instructions

### Method 1: CFF Editing Tools
1. **Backup** your original `GameData.cff` file
2. Use a CFF editing tool to:
   - Open your `GameData.cff`
   - Import the generated category files
   - Save the modified CFF

### Method 2: SpellForce Modding Tools
1. Use the official SpellForce Modding Tools
2. Create a new mod
3. Add the generated CFF data to your mod
4. Enable the mod in the game

### Method 3: Manual Integration (Advanced)
For advanced users comfortable with binary file manipulation:
1. Use hex editors or specialized tools
2. Manually merge the binary category data
3. Update CFF headers and indices

## File Format Details

### Category Structure
- **Category 3001**: General NPC information (ID, name, type, class, appearance)
- **Category 3002**: Base stats (strength, stamina, agility, etc.)
- **Category 3003**: Combat stats (health, mana, attack/defense values)
- **Category 3004**: Equipment (weapon/armor item IDs per slot)
- **Category 3005**: Behavior (movement type, spawn location, AI parameters)
- **Category 2016**: Localized text (name, title, description in various languages)

### Binary Format
The exported files use the same binary format as the original GameData.cff:
- Structured binary data with specific byte layouts
- Compatible with SpellForce engine requirements
- Optimized for game performance

## Troubleshooting

### Export Fails
- **Check**: All required fields are filled in the wizard
- **Check**: NPC ID is properly allocated (should be >= 40000 for custom NPCs)
- **Check**: Write permissions in the application directory

### Files Not Generated
- **Check**: `cff_exports/` directory creation permissions
- **Check**: Available disk space
- **Check**: Antivirus software isn't blocking file creation

### Integration Issues
- **Backup**: Always backup original GameData.cff before modification
- **Tools**: Use proper CFF editing tools (not text editors)
- **Compatibility**: Ensure CFF version compatibility with your game version

## Best Practices

1. **Test in Mods**: Create a separate mod first before modifying main GameData.cff
2. **Incremental Testing**: Test one NPC at a time
3. **Backup Strategy**: Keep multiple backups of original game files
4. **Version Control**: Track changes to your custom NPCs
5. **Documentation**: Keep notes about which NPCs you've added and their effects

## Technical Notes

- Custom NPC IDs should use range 40000+ to avoid conflicts with game NPCs
- Binary data is optimized for the SpellForce engine format
- Export preserves all NPC properties including equipment and behavior
- Files are timestamped to prevent overwriting previous exports

---

**Note**: This export functionality generates raw CFF binary data. Integration into the game requires appropriate modding tools or technical expertise with SpellForce file formats.