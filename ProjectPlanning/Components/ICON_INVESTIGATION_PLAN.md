# Icon Investigation Plan - Weapons and Armor Focus

## Overview
This document outlines the plan for investigating the relationship between weapons, armor icons, and game data. The focus will be on understanding extraction parameters for the `itm` category and verifying if armor icons should use spell-sized dimensions (64x64px) or standard item dimensions (32x32px).

## Current Understanding
- Weapons and armor icons fall under the `ui_item` category with naming patterns like `ui_item_equip_weapon_*` and `ui_item_equip_armor_*`
- The `itm` category may use different extraction parameters than standard items (potentially 16x16 grid instead of 8x8)
- Armor icons appear to have the same size as spell icons (64x64px), which is different from standard item icons (32x32px)
- No direct mapping exists from item IDs to specific atlas numbers, requiring a fallback approach

## Tasks for Tomorrow

### 1. Verify Extraction Parameters for the `itm` Category
**Action**: Run `analyze_ui_categories.py` script to determine exact grid patterns for the `itm` category.
**Expected Output**: 
- Dimensions of sample `itm` atlases
- Potential grid configurations (grid size, icon size)
- Whether 16x16 grid pattern is confirmed

### 2. Visual Inspection of Sample `itm` Atlases
**Action**: Use `visual_category_inspector.py` to convert sample `itm` atlases to PNG for manual review.
**Expected Output**:
- Sample PNG files for visual inspection
- Confirmation of grid patterns and visual characteristics
- Identification of any anomalies or special cases

### 3. Check Game Data Entries for Armor Chest Icon
**Action**: Search for specific game data entries that might correspond to the armor chest icon seen in `atlas_0`.
**Expected Output**:
- List of potential matches (e.g., `ui_item_equip_chest_plate_silver`, `ui_item_equip_chest_chain_plate_bones`)
- Verification of whether these entries match the visual appearance of the armor chest icon

### 4. Determine Appropriate Dimensions for Armor Icons
**Action**: Based on findings from tasks 1-3, determine whether armor icons should use spell-sized dimensions (64x64px) or standard item dimensions (32x32px).
**Expected Output**:
- Clear recommendation for extraction parameters for armor icons
- Justification based on visual evidence and game data relationships

### 5. Update Documentation
**Action**: Update documentation with findings about the relationship between armor icons and spell-sized dimensions.
**Expected Output**:
- Updated `WEAPONS_ARMOR_ICONS_DEEP_DIVE.md` with new information
- Possible updates to `UI_ICON_EXTRACTION_SOLUTION.md` if extraction parameters need to be modified

## Dependencies
- Python 3 installed
- ImageMagick for DDS to PNG conversion
- Pillow for image processing
- Access to the SpellSmut project directory

## Success Criteria
- [ ] Extraction parameters for `itm` category verified
- [ ] Visual inspection of sample `itm` atlases completed
- [ ] Game data entries for armor chest icon identified and matched
- [ ] Decision made on appropriate dimensions for armor icons
- [ ] Documentation updated with findings

## Timeline Estimate
| Task | Estimated Time |
|------|----------------|
| Verify extraction parameters | 30 minutes |
| Visual inspection | 30 minutes |
| Check game data entries | 20 minutes |
| Determine dimensions | 20 minutes |
| Update documentation | 30 minutes |
| **Total** | **2.5 hours** |

---
*Last Updated: October 25, 2025*
*Prepared by: Qwen Code Agent*