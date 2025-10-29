# TirganachReloaded Data Directory

This directory contains reference data files used by the CFF Editor and related tools.

## Files

### `id_name_mappings.json`
Maps internal game IDs to human-readable names for various game entities (items, spells, NPCs, etc.).

**Format:**
```json
{
  "items": {
    "27": "Flame Dagger",
    ...
  },
  "spells": {
    "100": "Fireball",
    ...
  }
}
```

**Usage:** Used by the CFF Editor to display friendly names instead of numeric IDs.

**Source:** Generated from GameData.cff analysis and manual curation.

---

### `project_ids.json`
Tracks allocated IDs for all custom content created by the wizards.

**Format:**
```json
{
  "quest": [],
  "spell": [],
  "weapon": [10000, 10001, 10002],
  "armor": [20000, 20001],
  "item": [],
  "npc": [40000, 40001, 40002],
  "creature": [],
  "building": []
}
```

**Usage:** 
- Shared by all creation wizards (Weapon Forge, Armor Forge, Quest Creator, etc.)
- Prevents duplicate ID allocation across all custom content
- Automatically managed by the `IDManager` class
- Each content type has a safe ID range (e.g., weapons: 10000-19999, armor: 20000-29999)

**Source:** Automatically updated when creating new content through the CFF Editor wizards.

**Important:** This file should be version-controlled to track your project's ID allocations.

---

### `ui_icon_mapping.json`
Maps item/spell IDs to their UI icon handles and metadata.

**Format:**
```json
{
  "description": "Mapping from item IDs to UI icon data",
  "item_to_icons": {
    "27": [
      {
        "index": 1,
        "handle": "ui_item_equip_weapon_dagger_flame",
        "scaled": false
      }
    ]
  }
}
```

**Usage:** The CFF Editor uses this to display appropriate icons for items and spells in the UI.

**Source:** Extracted from GameData.cff `item_ui` and `spell_ui` tables.

---

### `weapon_icon_mapping.json`
Detailed weapon icon atlas mapping data, including file paths and atlas coordinates.

**Format:**
```json
{
  "ui_item_equip_weapon_axe_great": {
    "atlas": 0,
    "index": 1,
    "path": "ExtractedAssets/UI/itm_icons_extracted/atlas_0/icon_001.png"
  }
}
```

**Usage:** 
- Maps weapon UI handles to specific icon files in the extracted assets
- Contains atlas number and index for each weapon icon
- Includes full relative paths to extracted icon PNG files

**Source:** Generated during UI asset extraction from game PAK files.

**Related:** See `ExtractedAssets/UI/icons_extracted/` for the actual icon files.

---

## Notes

- Most files are read-only reference data, except `project_ids.json` which is read-write
- Icon mappings are automatically generated but may benefit from manual verification
- The `weapon_icon_mapping.json` file specifically covers weapon items only; other item types may use the more general `ui_icon_mapping.json`
- Paths in `weapon_icon_mapping.json` are relative to the project root
- The `project_ids.json` file is automatically created and updated by the CFF Editor
</parameter>

<old_text line=86>
## Maintenance

When regenerating these files:
1. Back up existing files first
2. Verify mappings are correct (especially for icons)
3. Update the CFF Editor if file formats change
4. Test that the editor can still load and display icons correctly

## Maintenance

When regenerating these files:
1. Back up existing files first
2. Verify mappings are correct (especially for icons)
3. Update the CFF Editor if file formats change
4. Test that the editor can still load and display icons correctly