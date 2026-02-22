# Getting Started Guide

Welcome to the SpellForce Data Editor! This guide will help you get started with modding SpellForce games.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [First Launch](#first-launch)
4. [Basic Concepts](#basic-concepts)
5. [Your First Mod](#your-first-mod)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

Before using the SpellForce Data Editor, you need:

### Required
- **SpellForce Game Installation** - Any SpellForce game (Platinum Edition recommended)
  - SpellForce: The Order of the Dawn
  - SpellForce: Shadow of the Phoenix
  - SpellForce: Breath of Winter
  - SpellForce 2 (limited support)

### Recommended
- Windows 10 or later
- 4GB+ RAM
- Modern GPU with OpenGL 3.0+ support

## Installation

### Option 1: Use Pre-built Binary

1. Download the latest release from [GitHub Releases](https://github.com/leszekd25/spellforce_data_editor/releases)
2. Extract to a folder (e.g., `C:\SpellForceEditor\`)
3. Run `SpellforceDataEditor.exe`

### Option 2: Build from Source

1. Install [.NET 8.0 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)
2. Clone the repository
3. Open `SpellforceDataEditor.sln` in Visual Studio
4. Build in Release configuration
5. Run from `bin\Release\net8.0-windows\`

## First Launch

### Step 1: Specify Game Directory

1. Launch the editor
2. Click **"Specify Game Directory"**
3. Navigate to your SpellForce installation folder
4. Select the folder containing `GameData.cff`

**Example**: `C:\GOG Games\SpellForce Platinum\`

### Step 2: Verify Setup

After specifying the directory, you should see:
- ✅ "Game directory: Specified"
- ✅ All editor buttons enabled

## Basic Concepts

### What is GameData.cff?

The `GameData.cff` file is the **master database** for SpellForce games. It contains:
- 66+ data categories (spells, units, items, buildings, etc.)
- Text in multiple languages
- Game balance values
- Entity definitions

### What are Maps?

Map files (`.map`) contain:
- Terrain/heightmap data
- Placed entities (buildings, units, objects)
- Environment settings
- Player spawn points
- Quest triggers

### What are PAK Files?

PAK files are compressed archives containing:
- 3D models (`.msb`)
- Textures (`.dds`, `.tga`)
- Sounds (`.wav`, `.mp3`)
- Scripts (`.lua`)

### Modding Workflow

```
┌─────────────────┐
│  Extract Assets │ (Optional - view original assets)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Edit GameData  │ (Modify game database)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Edit/Create    │ (Modify or create maps)
│     Maps        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Package Mod   │ (Distribute your changes)
└─────────────────┘
```

## Your First Mod

Let's create a simple mod that makes all weapons do double damage.

### Step 1: Open Game Data Editor

1. Click **"Game Data Editor"**
2. Select `GameData.cff` from your game directory

### Step 2: Navigate to Weapon Data

1. In the category list, find **"Item weapon data"** (Category 2015)
2. Click to expand and view all weapons

### Step 3: Edit Weapon Damage

1. Select a weapon from the list
2. In the details panel, find **"MinDamage"** and **"MaxDamage"**
3. Double-click the value and enter the new doubled value
4. Repeat for desired weapons

### Step 4: Save Your Changes

1. Click **"Save GameData"** in the toolbar
2. Save as `GameData_mod.cff` (keep original as backup)

### Step 5: Test Your Mod

1. Backup your original `GameData.cff`
2. Replace it with your modified file
3. Launch SpellForce and test!

## Common Workflows

### Creating a New Item

```
Game Data Editor → Category 2003 (Items)
→ Click "Add" → Set ItemID → Fill in fields
→ Set NameID (points to text in Category 2016)
→ Save
```

### Creating a New Spell

```
Game Data Editor → Category 2002 (Spells)
→ Click "Add" → Set SpellID
→ Configure spell parameters (damage, range, duration)
→ Link to spell line (Category 2054)
→ Save
```

### Editing a Map

```
Map Editor → Open existing map
→ Use tools to modify terrain, place entities
→ Test in-game
→ Save
```

### Extracting Assets

```
Asset Viewer → Browse to asset
→ Right-click → Extract
→ Use extracted files for reference/modding
```

## File Locations

### Game Files
- **GameData.cff**: Game root directory
- **Maps**: `maps\` subdirectory
- **PAK files**: `pak\` subdirectory
- **Scripts**: `scripts\` subdirectory

### Editor Files
- **Config**: `config.txt` (editor settings)
- **Logs**: `UserLog.txt` (debug logs)
- **Cache**: `pakdata.dat` (PAK file index)

## Tips and Best Practices

### 1. Always Backup Original Files

Before modifying:
```batch
copy GameData.cff GameData_backup.cff
```

### 2. Use Incremental IDs

When adding new items, use IDs that won't conflict:
- Items: 10000+
- Spells: 5000+
- Units: 8000+

### 3. Test in Small Batches

Test your changes frequently:
1. Make a few changes
2. Save and test in-game
3. Verify everything works
4. Continue with more changes

### 4. Document Your Changes

Keep notes on:
- Which IDs you've used
- What values you changed
- Why you made specific changes

### 5. Use Search Effectively

Find items by reference:
- Search for items that use a specific spell
- Find all text references to an item
- Locate all units using a specific model

## Troubleshooting

### Editor Won't Start

**Problem**: Editor crashes on startup

**Solutions**:
- Ensure .NET 8.0 is installed
- Run as administrator
- Check `UserLog.txt` for error details

### Game Directory Not Recognized

**Problem**: "Game directory: NOT specified"

**Solution**:
- Verify `GameData.cff` exists in the selected directory
- Check you have read permissions

### Changes Not Appearing In-Game

**Problem**: Modified game data doesn't show up

**Solutions**:
- Ensure you saved `GameData.cff`
- Check you're modifying the correct installation
- Verify the file was actually written (check file size)

### Map Editor Crashes

**Problem**: Editor crashes when loading a map

**Solutions**:
- Ensure game directory is specified
- Check the map file isn't corrupted
- Try a different map first

### Text Displays Garbled

**Problem**: Special characters (é, ñ, etc.) appear wrong

**Solution**:
- Ensure Windows-1252 encoding is properly configured
- Check your system locale settings

## Next Steps

Now that you understand the basics:

- [Game Data Editor Guide](gamedata-editor.md) - Deep dive into data editing
- [Map Editor Guide](map-editor.md) - Create custom maps
- [Asset Management](assets.md) - Work with game assets
- [Script Editing](scripts.md) - Modify game scripts

## Community Resources

- **GitHub Issues**: Report bugs and request features
- **Forums**: Share mods and get help from community

---

**Need help?** Check the [troubleshooting section](#troubleshooting) or see other documentation in this folder.
