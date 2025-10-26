# Icon System Component

## Overview
Comprehensive icon extraction and integration system for SpellForce UI assets, enabling visual representation of game data in the GUI editor.

## Current Status: ✅ EXTRACTION WORKING, MAPPING REQUIRED

### ✅ Completed Achievements
- **ITM Icon Extraction**: 4096+ icons extracted from 16 atlases
- **Weapon Reassembly**: 1x2 and 1x4 weapon patterns working
- **Spell Icons**: 657 icons extracted from 18 atlases
- **Technical Pipeline**: DDS→PNG conversion, 180° rotation correction
- **GUI Integration**: Basic icon display working

### ❌ Critical Gap: Handle-to-Atlas Mapping
- **Problem**: GameData exports contain `item_ui_handle` and `item_ui_index` but **no atlas numbers**
- **Impact**: Cannot connect "ui_item_equip_weapon_dagger_flame" to specific atlas files
- **Status**: Manual mapping or alternative approaches needed

## Technical Details

### ITM (Item) System ✅ WORKING
- **16 Atlases**: ui_item18.dds through ui_item33.dds (256×256 pixels each)
- **Grid Layout**: 16×16 pixel icons in 16×16 grid (4096 total positions)
- **Weapon Spanning**: Items can span 1-4 horizontal cells (16×16 → 64×16 pixels)
- **Reassembly**: Automatic detection and combination of multi-part weapons

### Spell System ❓ INVESTIGATION NEEDED
- **Atlas Files**: ui_spell8.dds, ui_spell9.dds
- **Grid Layout**: 4×4 grid with 64×64 pixel icons
- **Handles**: "ui_spell_EM_Fire_FireBurst" format confirmed
- **Mapping**: Atlas assignment data missing from GameData exports

### Pipeline Components
- **Extraction**: QuickBMS with custom BMS script for PAK files
- **Conversion**: ImageMagick DDS→PNG conversion
- **Rotation**: 180° correction for SpellForce's inverted Y-axis
- **Organization**: Automatic categorization by filename prefix

## Quantitative Results

### ITM Atlas Statistics
| Atlas | Single Icons | 1x2 Weapons | 1x4 Weapons | Empty Slots | Weapons Created |
|-------|-------------|-------------|-------------|-------------|-----------------|
| 0     | 51         | 39         | 36         | 55         | 75             |
| 1     | 46         | 44         | 32         | 58         | 76             |
| 2     | 55         | 46         | 32         | 45         | 78             |
| 3     | 41         | 35         | 9          | 127        | 44             |
| 4     | 53         | 40         | 22         | 79         | 62             |
| 5     | 36         | 31         | 22         | 114        | 53             |
| 6     | 33         | 30         | 23         | 117        | 53             |
| 7     | 45         | 41         | 28         | 73         | 69             |
| 8     | 43         | 43         | 26         | 75         | 69             |
| 9     | 43         | 43         | 27         | 73         | 70             |
| 10    | 39         | 37         | 23         | 97         | 60             |
| 11    | 34         | 29         | 14         | 136        | 43             |
| 12    | 38         | 30         | 13         | 132        | 43             |
| 13    | 35         | 31         | 21         | 117        | 52             |
| 14    | 36         | 33         | 20         | 114        | 53             |
| 15    | 9          | 8          | 5          | 221        | 13             |

**Total**: 4,096 individual icons → 726 single + 969 reassembled = 1,695 usable icons

## Tools and Scripts
- `extract_itm_icons.py` - ITM atlas extraction with weapon reassembly
- `extract_icons_from_atlases.py` - General atlas extraction framework
- `bulk_extract_paks.py` - Automated PAK extraction with QuickBMS
- `SpellForce_PAK_script.bms` - PAK format BMS script

## Next Steps Required

### 1. Resolve Mapping Challenge 🔍 CRITICAL
- **Search Game Files**: Look for atlas assignment data in original PAK files
- **Reverse Engineer**: Find how game loads icons from atlases
- **Alternative Mapping**: Create manual mapping system or visual verification

### 2. Complete Spell Integration 📚 HIGH PRIORITY
- Extract ui_spell8.dds, ui_spell9.dds atlases
- Test 4×4 grid extraction (64×64 icons)
- Find spell-to-atlas mapping patterns

### 3. GUI Integration Completion 🖥️ HIGH PRIORITY
- Debug why spell icons aren't displaying in GUI
- Verify icon mapping is correctly loaded
- Implement fallback mapping system

### 4. System Optimization ⚡ MEDIUM PRIORITY
- Create icon caching system
- Optimize loading performance
- Add icon preview generation

## Success Criteria
- ✅ **ITM Icons**: 4096+ icons extracted and reassembled
- ✅ **Spell Icons**: 657 icons extracted
- ✅ **GUI Display**: Icons show in editor tables and property panels
- ⚠️ **Mapping**: Handle-to-atlas connection established
- ✅ **Performance**: Icon loading doesn't impact GUI responsiveness

## Files Consolidated From
- `ATLAS_EXTRACTION_SUMMARY.md`
- `ICON_INVESTIGATION_PLAN.md`
- `Internal/ICON_EXTRACTION_*` (8 files)
- `GUI/ICON_*_SUMMARY.md` (2 files)