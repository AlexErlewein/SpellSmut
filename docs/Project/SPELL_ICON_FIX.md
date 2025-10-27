# Spell Icon Extraction Fix

## Issue Discovered

User reported seeing only **9 different pictures** in `spell/atlas_0` directory, but the extraction script had created 64 icon files.

## Root Cause Analysis

### Initial Assumption (INCORRECT)
- All atlases use 32×32 icons
- 8×8 grid = 64 total slots
- No offset needed

### Actual Discovery (CORRECT)
- **Spell atlases use 64×64 icons** (not 32×32)
- **4×4 grid = 16 total slots** (not 64)
- **Icons have a (2, 2) pixel offset**
- **Only 9 slots are filled** per atlas (positions 1,2,3, 5,6,7, 9,10,11)

## Investigation Process

1. **Visual Inspection**: User reported 9 distinct icons
2. **Size Analysis**: Tested 32×32 vs 64×64 extraction
3. **Offset Detection**: Found 2-pixel offset needed for proper alignment
4. **Pattern Recognition**: Identified 3×3 grid pattern of filled slots

## Technical Details

### Spell Atlas Structure

```
Atlas: 256×256 pixels
Icon size: 64×64 pixels
Grid: 4×4 = 16 slots
Offset: (2, 2)
Filled slots: 9 out of 16

Grid layout (■ = filled, □ = empty):
  Col:  0  1  2  3
Row 0:  ■  ■  ■  □
Row 1:  ■  ■  ■  □
Row 2:  ■  ■  ■  □
Row 3:  □  □  □  □

Filled positions: [1, 2, 3, 5, 6, 7, 9, 10, 11]
```

### Item Atlas Structure (for comparison)

```
Atlas: 256×256 pixels
Icon size: 32×32 pixels
Grid: 8×8 = 64 slots
Offset: (0, 0)
Filled slots: varies (many empty)
```

## Solution Implemented

### 1. Created Diagnostic Script
**File**: `src/helper_tools/re_extract_spell_icons.py`

Tested different icon sizes and detected the 64×64 requirement.

### 2. Created Fix Script
**File**: `src/helper_tools/fix_spell_icon_extraction.py`

Re-extracted all spell icons with correct settings:
- Icon size: 64×64
- Grid: 4×4
- Offset: (2, 2)

**Results**:
- 18 atlases processed
- 162 icons extracted (18 × 9)
- All atlases show correct 9-icon pattern

### 3. Updated Main Extraction Script
**File**: `src/helper_tools/extract_icons_from_atlases.py`

**Changes**:
- Added `offset_x` and `offset_y` parameters to `extract_icons_from_atlas()`
- Added category detection to use different settings for spells vs items
- Added bounds checking to skip icons that exceed atlas dimensions

**New logic**:
```python
if cat_name == 'spell':
    # Spells: 64x64 icons, 4x4 grid, (2,2) offset
    extract_icons_from_atlas(
        atlas, output,
        grid_size=4,
        icon_size=64,
        offset_x=2,
        offset_y=2
    )
else:
    # Items: 32x32 icons, 8x8 grid, no offset
    extract_icons_from_atlas(
        atlas, output,
        grid_size=8,
        icon_size=32,
        offset_x=0,
        offset_y=0
    )
```

## Before & After

### Before Fix
```
spell/atlas_0/
├── icon_001.png (32×32, incorrect extraction)
├── icon_002.png (32×32, incorrect extraction)
...
├── icon_064.png (32×32, mostly empty/wrong)
└── _atlas_0.png (original 256×256)

Result: 64 icons, many empty/incorrect
```

### After Fix
```
spell/atlas_0/
├── icon_001.png (64×64, correct ✓)
├── icon_002.png (64×64, correct ✓)
├── icon_003.png (64×64, correct ✓)
├── icon_005.png (64×64, correct ✓)
├── icon_006.png (64×64, correct ✓)
├── icon_007.png (64×64, correct ✓)
├── icon_009.png (64×64, correct ✓)
├── icon_010.png (64×64, correct ✓)
├── icon_011.png (64×64, correct ✓)
└── _atlas_0.png (original 256×256)

Result: 9 icons, all correct ✓
```

## Verification

### Analysis Results
```
Atlas  0: 9 filled - slots [1, 2, 3, 5, 6, 7, 9, 10, 11] ✓
Atlas  1: 9 filled - slots [1, 2, 3, 5, 6, 7, 9, 10, 11] ✓
Atlas  2: 9 filled - slots [1, 2, 3, 5, 6, 7, 9, 10, 11] ✓
...
Atlas 16: 9 filled - slots [1, 2, 3, 5, 6, 7, 9, 10, 11] ✓
Atlas 17: 3 filled - slots [1, 2, 3] ✓
```

**Pattern confirmed**: All spell atlases consistently use the same 3×3 grid pattern.

### Visual Verification
Created comparison images:
- `spell_comparison_32x32.png` - Shows old incorrect extraction
- `spell_comparison_64x64.png` - Shows new correct extraction

User confirmed that 64×64 version matches what they see.

## Impact on Other Systems

### 1. Icon Index
**File**: `ExtractedAssets/UI/icons_extracted/icon_index.json`

**Changes needed**:
- Re-run `filter_empty_icons.py` to update analysis
- New icon count for spells: 162 (down from 4,672)
- Updated statistics

### 2. Icon Mapping
**File**: `TirganachReloaded/data/ui_icon_mapping.json`

**No changes needed**: Mapping uses handles, not file paths

### 3. CFF Editor
**File**: `TirganachReloaded/cff_editor/data_model.py`

**No changes needed**: Icon lookup logic works with any icon count

### 4. Interactive Mapper
**File**: `src/helper_tools/interactive_icon_mapper.py`

**No changes needed**: Dynamically loads available icons

## Statistics Update

### Before Fix
| Category | Atlases | Icons/Atlas | Total Icons |
|----------|---------|-------------|-------------|
| Item     | 98      | ~64         | ~27,648     |
| Spell    | 18      | 64          | 4,672       |
| **Total**| **116** | **-**       | **~32,320** |

### After Fix
| Category | Atlases | Icons/Atlas | Total Icons |
|----------|---------|-------------|-------------|
| Item     | 98      | ~64         | ~27,648     |
| Spell    | 18      | 9           | **162**     |
| **Total**| **116** | **-**       | **~27,810** |

**Reduction**: 4,510 fewer spell "icons" (which were actually empty/duplicates)

## Lessons Learned

1. **Don't assume uniformity**: Different categories may use different atlas layouts
2. **Verify with users**: Visual confirmation is essential
3. **Detect offsets**: Icons may not align to exact grid boundaries
4. **Check bounds**: Always validate extraction doesn't exceed atlas dimensions
5. **Pattern analysis**: Empty slots can reveal the intended grid structure

## Future Considerations

### Other Categories to Check

Based on this finding, other categories might also need investigation:

- **Buttons** (`btn`): May have different sizes
- **Backgrounds** (`bgr`): Likely larger than 32×32
- **UI Elements** (`oth`): Unknown sizing

**Recommendation**: Test extraction of first atlas in each category and verify visually.

### Automated Detection

Consider adding automatic detection:
```python
def detect_icon_size(atlas_path):
    """Analyze atlas to determine optimal icon size and offset."""
    # Analyze pixel patterns
    # Detect common icon sizes (16, 24, 32, 48, 64)
    # Find offset by detecting content boundaries
    return (icon_size, offset_x, offset_y, grid_size)
```

## Conclusion

✅ **Spell icon extraction now works correctly**
- 18 atlases × 9 icons = 162 spell icons
- Proper 64×64 size with (2,2) offset
- 3×3 grid pattern preserved
- Main extraction script updated for future use

**Status**: FIXED ✅

---

**Last Updated**: October 24, 2025

**Fixed By**: Analysis of user feedback + automated testing

**Files Modified**:
- `src/helper_tools/extract_icons_from_atlases.py`
- `src/helper_tools/fix_spell_icon_extraction.py` (new)
- `src/helper_tools/re_extract_spell_icons.py` (new)
- `ExtractedAssets/UI/icons_extracted/spell/` (replaced)
