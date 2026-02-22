# Game Data Editor Guide

The Game Data Editor is the primary tool for modifying SpellForce's master game database (GameData.cff).

## Table of Contents

1. [Interface Overview](#interface-overview)
2. [Working with Categories](#working-with-categories)
3. [Common Editing Tasks](#common-editing-tasks)
4. [Advanced Features](#advanced-features)
5. [Search and Filter](#search-and-filter)
6. [Reference Management](#reference-management)

## Interface Overview

### Main Window

```
┌─────────────────────────────────────────────────────────┐
│ Game Data Editor                          [Save] [Undo] │
├──────────────┬──────────────────────────────┬──────────┤
│ Category     │ Item List                    │ Details  │
│ List         │                              │ Panel    │
│              │                              │          │
│ - Spells     │ [1] Fireburst                │ ID: 1     │
│ - Units       │ [2] Healing                  │ Name: ... │
│ - Items       │ [3] Death                    │ ...       │
│ - Buildings   │ ...                          │          │
│ - ...         │                              │          │
└──────────────┴──────────────────────────────┴──────────┘
```

### Components

1. **Category List** (left): 66+ data categories
2. **Item List** (middle): Items in selected category
3. **Details Panel** (right): Edit selected item
4. **Toolbar**: Save, undo, redo, search, etc.

## Working with Categories

### Opening GameData.cff

1. Click **"Game Data Editor"** on main window
2. Navigate to your SpellForce directory
3. Select `GameData.cff`
4. Wait for load (usually < 1 second)

### Category Types

Categories come in two varieties:

**Single Categories** (one item per ID):
- Spells (2002)
- Units (2024)
- Items (2003)
- Buildings (2029)
- Weapons (2015)

**Multiple Categories** (multiple sub-items per ID):
- Text (2016) - translations in multiple languages
- Unit Equipment (2025) - equipment slots

### Selecting a Category

1. Click category name in left panel
2. Item list populates with all items
3. Items are sorted by ID

### Viewing Item Details

1. Click item in item list
2. Details panel shows all fields
3. Fields show raw values and resolved names

## Common Editing Tasks

### Modifying a Field

1. Select item
2. Double-click field value in details panel
3. Enter new value
4. Press Enter or click away to apply

**Example**: Change spell damage
```
1. Select "Spell data" (2002)
2. Select "Fireburst"
3. Find "Params[0]" (Initial damage)
4. Double-click value
5. Enter "50"
6. Press Enter
```

### Adding a New Item

1. Select category
2. Click **"Add"** button
3. Editor finds next available ID
4. Fill in required fields
5. Click **"Apply"**

**Example**: Create a new spell
```
1. Select "Spell data" (2002)
2. Click "Add"
3. New item created with ID 5000 (first available)
4. Set name ID (points to text in category 2016)
5. Set parameters
6. Set mana cost, range, etc.
7. Save
```

### Copying an Item

1. Select item to copy
2. Click **"Copy"** button
3. Paste creates new item with next available ID

### Removing an Item

1. Select item to remove
2. Click **"Remove"** button
3. Confirm deletion

**Warning**: This cannot be undone except with the global undo button.

### Bulk Operations

Multiple items can be modified using clusters:

1. Enable **"Cluster Mode"**
2. Select multiple items
3. Apply changes to all selected items

## Advanced Features

### Spell Parameter System

Spells have up to 10 parameters (`Params[0]` through `Params[9]`).

The meaning of each parameter varies by spell type. Use `SFSpellDescriptor` to get descriptions:

```csharp
// For spell ID 1 (Fireburst):
string[] params = SFSpellDescriptor.get(1);
// params[0] = "Initial damage"
// params[1] = "Damage per tick"
// params[2] = "Tick count"
// params[3] = "Time between ticks (ms)"
```

### Text References

Many fields reference text by ID:

```
NameID: 12345  →  Category 2016, Text ID 12345, Language 0
```

To view the actual text:
1. Click the reference (blue link)
2. Text editor opens with the text

### Foreign Key Lookups

Items often reference other items:
- Spells → Spell Lines (2054)
- Units → Stats (2005)
- Items → Models/Textures

These are automatically resolved and displayed.

## Search and Filter

### Quick Search

Type in the search box to filter items by name or ID.

### Advanced Search

Click **"Search"** button for complex queries:

```
Search for items where:
  Field: MinDamage
  Operator: >
  Value: 10
```

### Search Options

| Option | Description |
|--------|-------------|
| IS_NUMBER | Numeric comparison |
| IS_STRING | Text comparison |
| IGNORE_CASE | Case-insensitive search |
| REGEX | Regular expression |

### Finding References

Find all items that reference a specific item:

1. Right-click item
2. Select **"Find References"**
3. Results show all referencing items

**Example**: Find all spells that use a specific effect
```
1. Right-click effect in Category 2002
2. "Find References"
3. Shows all spells with this effect
```

## Reference Management

### Undo/Redo

The editor tracks all changes:

- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo
- **Undo History**: Shows all operations

### Saving Changes

1. Click **"Save GameData"** button
2. Choose save location
3. **Important**: Keep original as backup!

### Export/Import

**Export to CSV**:
```
1. Select category
2. Click "Export"
3. Choose CSV format
4. Edit in spreadsheet software
```

**Import from CSV**:
```
1. Select category
2. Click "Import"
3. Select CSV file
4. Preview changes
5. Apply
```

## Tips and Tricks

### 1. Use the Descriptor Helper

For spells, use `SFSpellDescriptor` to understand parameters:
```csharp
// In the immediate window or plugin
string[] desc = SFSpellDescriptor.get(spell_id);
// Returns parameter descriptions
```

### 2. Check Valid Ranges

Before setting values, check valid ranges:
- **Text IDs**: Must exist in Category 2016
- **Spell IDs**: 1-1000 for base game
- **Unit IDs**: Varies by race/faction

### 3. Test Incrementally

Make small changes, save, and test:
```
1. Change one spell
2. Save
3. Test in-game
4. Repeat
```

### 4. Use Search for Balance

Find all items with specific values:
```
Search: Damage > 50 AND Mana Cost < 50
Shows: Overpowered spells
```

### 5. Document Your Changes

Keep notes on:
- New IDs you've added
- Balance changes made
- Reference chains you've modified

## Common Workflows

### Creating a Custom Spell

```
1. Add spell in Category 2002
2. Set parameters for desired effect
3. Create text entry in Category 2016
4. Link spell to text
5. Add to spell line in Category 2054
6. Test in-game
```

### Adding a New Unit

```
1. Add unit in Category 2024
2. Set stats (use Category 2005 reference)
3. Add equipment (Category 2025)
4. Set model references
5. Create name text (Category 2016)
6. Test spawning in map
```

### Balancing Weapons

```
1. Search Category 2015 for weapon type
2. Export to CSV
3. Sort by damage
4. Adjust balance
5. Import back
6. Verify changes
```

## Troubleshooting

### "Item ID Already Exists"

The ID you're trying to add is already in use. Try:
- Using the "Add" button (auto-finds next available)
- Checking for gaps in ID sequence

### "Text ID Not Found"

The text reference doesn't exist in Category 2016. Fix by:
1. Adding the text to Category 2016
2. Changing the text ID to an existing one

### Changes Not Appearing In-Game

1. Ensure you saved `GameData.cff`
2. Check you're editing the correct installation
3. Clear any game caches

### Editor Crashes on Load

1. Check `UserLog.txt` for errors
2. Verify `GameData.cff` isn't corrupted
3. Try loading a backup

## Next Steps

- [Map Editor Guide](map-editor.md) - Edit game maps
- [Asset Management](assets.md) - Work with game assets
- [Script Editing](scripts.md) - Modify game scripts

---

**Related**: [Getting Started Guide](README.md), [Architecture: Categories](../architecture/categories.md)
