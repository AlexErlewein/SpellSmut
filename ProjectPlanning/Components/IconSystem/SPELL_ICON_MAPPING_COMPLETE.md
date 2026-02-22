# Spell Icon Mapping - Complete

## Summary

Successfully created a complete spell handle → icon file mapping by parsing MSB mesh files.

## Key Discovery

The **MSB mesh files** contain the mapping data:
- Filename = spell handle (e.g., `ui_spell_wm_life_healing.msb`)
- Embedded texture reference = atlas number (e.g., `ui_spell5`)
- UV coordinates = grid position within the 4×4 atlas

## Results

| Metric | Value |
|--------|-------|
| Total spell mappings | 156 |
| Atlases used | 18 (0-17) |
| Spells in game data | 152 |
| **Coverage** | **100%** |

All 152 spell handles referenced in ui_icon_mapping.json now have accurate icon paths.

## File Structure

### Generated Mapping
```
src/TirganachReloaded/data/spell_icon_mapping.json
```

Contains:
- `mappings`: Full mapping data (handle, atlas, row, col, icon_number, path)
- `handle_to_path`: Simple lookup dictionary

### Extracted Icons
```
ExtractedAssets/UI/icons_extracted/spell/
├── atlas_0/
│   ├── icon_001.png through icon_011.png
├── atlas_1/
│   ├── ...
└── atlas_17/
    └── ...
```

Each atlas contains 9 icons (3×3 grid within the 4×4 atlas structure).

## MSB Parser

**Script**: `src/helper_tools/analysis/parse_spell_msb_mapping.py`

Parses MSB files from:
```
ExtractedAssets/UI/raw_reextraction/sf35/mesh/ui_spell_*.msb
```

### MSB File Structure
- Header: 16 bytes
- 4 vertices, ~40 bytes each
- UV coordinates at offsets: 0x2C/0x30, 0x54/0x58, 0x7C/0x80, 0xA4/0xA8
- Texture reference at ~0xD0 (null-terminated string)

## Sample Mappings

| Spell Handle | Icon Path |
|-------------|-----------|
| ui_spell_em_fire_fireburst | spell/atlas_5/icon_009.png |
| ui_spell_wm_life_healing | spell/atlas_14/icon_002.png |
| ui_spell_bm_death_death | spell/atlas_1/icon_011.png |
| ui_spell_mm_enchantment_charm | spell/atlas_9/icon_009.png |

## Integration

### Using the Mapping in Code
```python
import json

with open('src/TirganachReloaded/data/spell_icon_mapping.json') as f:
    mapping = json.load(f)

# Simple lookup
icon_path = mapping['handle_to_path'].get('ui_spell_em_fire_fireburst')
# Returns: 'spell/atlas_5/icon_009.png'

# Full path
full_path = Path('ExtractedAssets/UI/icons_extracted') / icon_path
```

## Grid Position Distribution

```
Row 0:   18   18   18    0
Row 1:   17   17   17    0
Row 2:   17   17   17    0
Row 3:    0    0    0    0
```

Each atlas uses a 3×3 section of the 4×4 grid (9 icons per atlas).

## Next Steps

1. ✅ **Spell icon mapping complete**
2. [ ] Integrate mapping into CFF editor data model
3. [ ] Test spell icon display in GUI
4. [ ] Update icon resolution logic to use new mapping

## Related Files

- `parse_spell_msb_mapping.py` - MSB parser script
- `extract_spell_icons.py` - Icon extraction script
- `spell_icon_mapping.json` - Generated mapping file
- `ui_icon_mapping.json` - Game data references
