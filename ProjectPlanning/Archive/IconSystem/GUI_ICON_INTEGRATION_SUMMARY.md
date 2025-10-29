> **⚠️ OUTDATED PLAN ⚠️**
> 
> This document outlines the original icon integration plan, which was based on the assumption that re-extracting assets with original filenames would be sufficient. **This assumption was proven incomplete.**
> 
> **The primary blocker is now the handle-to-atlas mapping.** We need to discover how the game links an item's UI handle to a specific texture atlas file.
> 
> For the current status and plan, please see **[ICON_SYSTEM.md](./ICON_SYSTEM.md)**.

# GUI Icon Integration - Planning Summary

## Key Discovery 🎯

**The UIHandle IS the filename!** No mapping file needed.

From analyzing the SpellForce Data Editor C# source code, we discovered:

```
UIHandle: "ui_item_equip_weapon_dagger_flame"
↓
Game loads: "texture\ui_item_equip_weapon_dagger_flame.dds"
↓
We need: "ExtractedAssets/UI/extracted/items/ui_item_equip_weapon_dagger_flame.png"
```

## Current Problem

Our extracted files are numbered:
- `ui_item0.png`, `ui_item1.png`, `ui_item2.png`...
- `ui_spell0.png`, `ui_spell1.png`, `ui_spell2.png`...

**These are useless** - we can't map them to UIHandles.

## Solution

**Re-extract UI assets from PAK files preserving original filenames.**

### Step 1: Re-extract with QuickBMS

```bash
cd ModdingTools/quickbms
quickbms spellforce.bms ../../OriginalGameFiles/pak/sf*.pak ../../ExtractedAssets/UI_reextracted/
```

This should give us:
```
texture/ui_item_equip_weapon_dagger_flame.dds
texture/ui_spell_EM_Fire_FireBurst.dds
texture/ui_spell_WM_Life_Healing.dds
...
```

### Step 2: Convert DDS → PNG

```python
# src/helper_tools/convert_ui_textures.py
from pathlib import Path
import subprocess

def convert_all_ui_textures():
    input_dir = Path("ExtractedAssets/UI_reextracted/texture")
    output_dir = Path("ExtractedAssets/UI/extracted")
    
    for dds_file in input_dir.glob("ui_*.dds"):
        # Categorize
        if dds_file.stem.startswith("ui_item_"):
            category = "items"
        elif dds_file.stem.startswith("ui_spell_"):
            category = "spells"
        else:
            category = "other"
        
        # Convert
        output_path = output_dir / category / f"{dds_file.stem}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        subprocess.run([
            "magick", "convert", 
            str(dds_file), 
            str(output_path)
        ])
```

### Step 3: Update GameData Class

```python
# TirganachReloaded/tirganach/gamedata.py
def get_icon_path(self, category, item_id):
    """Get icon path for item/spell."""
    # Get UIHandle from data
    if category in ["items", "weapons", "armor"]:
        ui_entry = self._find_item_ui(item_id)
        if ui_entry:
            handle = ui_entry["item_ui_handle"]
    elif category == "spells":
        spell = self._find_spell(item_id)
        handle = spell.get("spell_ui_handle") if spell else None
    else:
        return None
    
    if not handle:
        return None
    
    # Direct lookup: handle.png
    icon_path = Path("ExtractedAssets/UI/extracted") / category / f"{handle}.png"
    return str(icon_path) if icon_path.exists() else None
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User selects item in GUI (item_id: 27)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Look up in item_ui table                                 │
│    item_id: 27 → item_ui_handle: "ui_item_equip_weapon_... │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Construct path                                           │
│    "ExtractedAssets/UI/extracted/items/" +                  │
│    "ui_item_equip_weapon_dagger_flame.png"                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Load PNG and display in GUI                              │
│    QPixmap(icon_path).scaled(64, 64)                        │
└─────────────────────────────────────────────────────────────┘
```

## Tables Involved

### item_ui (Category 2012)
```json
{
  "item_id": 27,
  "item_ui_index": 1,
  "item_ui_handle": "ui_item_equip_weapon_dagger_flame",
  "scaled_down": 0
}
```

### spell_names
```json
{
  "spell_name_id": 1,
  "spell_ui_handle": "ui_spell_EM_Fire_FireBurst",
  ...
}
```

## GUI Layout

```
┌─────────────────────────────────────────────────────────────┐
│ SpellForce CFF Editor                                       │
├──────────┬──────────────────────────┬───────────────────────┤
│          │                          │  ┌─────────────────┐  │
│ Category │  [Icon] ID   Name  Value │  │   [ICON 128x]   │  │
│ Tree     │  ────────────────────────│  └─────────────────┘  │
│          │   [⚔️]  27  Flame Dagger │  Flame Dagger         │
│ Items    │   [🗡️]  28  Fire Sword   │                       │
│ Weapons  │   [🏹]  29  Ice Bow      │  Min Damage: [10]     │
│ Spells   │   [⚡]  30  Thunder Axe  │  Max Damage: [25]     │
│ ...      │                          │  Speed: [1.2]         │
│          │                          │  Type: [Dagger ▼]     │
└──────────┴──────────────────────────┴───────────────────────┘
```

## Action Items

- [ ] Re-extract UI assets from PAK files with original names
- [ ] Convert DDS to PNG preserving filenames
- [ ] Organize into categories (items/, spells/, other/)
- [ ] Update GameData class with icon loading methods
- [ ] Add icon display to property editor panel
- [ ] Add icon column to table view
- [ ] Create fallback icons for missing assets
- [ ] Test with various items/spells

## Estimated Time

- Re-extraction: 30 minutes
- Conversion script: 1 hour
- GameData integration: 1 hour
- GUI integration: 2 hours
- Testing: 1 hour

**Total: ~5-6 hours**

## References

- **Category2012.cs**: Item UI data structure
- **SFResourceContainer.cs**: Texture loading logic
- **Control13.cs**: Item UI editor form
- Full plan: `GUI_ICON_INTEGRATION_PLAN.md`
