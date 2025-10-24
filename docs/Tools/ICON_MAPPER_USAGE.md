# Icon Mapper Tools Usage Guide

## Overview

After extracting 32,320 icons and building initial mappings, these tools help verify and correct icon-to-handle assignments.

## Tools Available

### 1. Empty Icon Filter ✅

**Purpose**: Identify and mark empty/placeholder icons

**Script**: `src/helper_tools/filter_empty_icons.py`

**Run**:
```bash
cd /path/to/SpellSmut
uv run src/helper_tools/filter_empty_icons.py
```

**Output**:
- `icon_analysis.json`: Detailed analysis of all icons
- `empty_icons_report.html`: Visual report with samples
- Updated `icon_index.json`: Icons marked with `is_empty` flag

**Results**:
- ✅ Analyzed 7,424 icons in ~8 seconds
- ✅ Found 2,384 empty icons (32.1%)
- ✅ Identified 79 duplicate groups (163 total duplicates)
- ✅ Categorized by reason: fully_transparent, mostly_transparent, solid_color

**Empty Icon Detection Methods**:
1. **Fully transparent**: All pixels have alpha = 0
2. **Mostly transparent**: >95% of pixels are transparent
3. **Solid color**: No color variation (variance < 10)
4. **Low content**: Low edge detection score + high transparency

**View Report**:
```bash
open ExtractedAssets/UI/reports/empty_icons_report.html
```

### 2. Interactive GUI Mapper

**Purpose**: Visual tool for verifying and correcting icon mappings

**Script**: `src/helper_tools/interactive_icon_mapper.py`

**Features**:
- Browse all items with icon data
- View current icon assignments
- Preview icons from different atlases
- Manually select correct icons
- Save verified mappings
- Search and filter items
- Export verified mappings

**Run**:
```bash
cd /path/to/SpellSmut
uv run src/helper_tools/interactive_icon_mapper.py
```

**Usage**:

1. **Browse Items**:
   - Left panel shows all items (6,237 total)
   - Use search box to filter by ID or name
   - Check "Show verified only" to see progress

2. **Verify Icons**:
   - Click an item to view its icons
   - Each icon index shows:
     - Handle name
     - Current icon preview
     - Atlas selector dropdown
   
3. **Change Atlas**:
   - Select different atlas number from dropdown
   - Preview updates automatically
   - Red border = empty icon (avoid these)

4. **Save Verification**:
   - Click "Save Verification" for current item
   - Click "Save All to File" to persist changes
   - Verified items show checkmark (✓) in list

5. **Export**:
   - Click "Export Mappings" to save to custom location
   - Default: `TirganachReloaded/data/verified_icon_mappings.json`

**Keyboard Shortcuts**:
- Arrow keys: Navigate item list
- Ctrl+S: Save current item (when implemented)
- Ctrl+E: Export mappings (when implemented)

### 3. Atlas Number Verification

**Purpose**: Determine correct atlas numbers using pattern analysis

**Coming soon**: Script to analyze GameData patterns and deduce atlas numbering

**Approach**:
1. Group items by ID ranges
2. Analyze which handles appear together
3. Cross-reference with atlas file sizes
4. Detect patterns in item_ui_index usage

## Data Files

### Icon Index (`icon_index.json`)

```json
{
  "stats": {...},
  "icons": {
    "item_14_003": {
      "category": "item",
      "atlas_number": "14",
      "icon_index": 3,
      "path": "item/atlas_14/icon_003.png",
      "is_empty": false,
      "empty_reasons": [],
      "metrics": {
        "alpha_mean": 245.3,
        "transparency_ratio": 0.15,
        "color_variance": 1250.5,
        "edge_score": 12.3
      }
    }
  }
}
```

### Icon Analysis (`icon_analysis.json`)

```json
{
  "total_icons": 7424,
  "empty_count": 2384,
  "duplicate_groups": 79,
  "total_duplicates": 163,
  "empty_by_reason": {
    "fully_transparent": 1833,
    "mostly_transparent": 548,
    "solid_color": 3
  },
  "analyses": [...]
}
```

### Icon Mapping (`ui_icon_mapping.json`)

```json
{
  "item_to_icons": {
    "27": [
      {
        "index": 1,
        "handle": "ui_item_equip_weapon_dagger_flame",
        "scaled": false
      }
    ]
  },
  "detailed_mapping": {...}
}
```

### Verified Mappings (`verified_icon_mappings.json`)

```json
{
  "27": {
    "1": "item/atlas_5/icon_001.png"
  },
  "32": {
    "1": "item/atlas_8/icon_001.png",
    "2": "spell/atlas_2/icon_002.png"
  }
}
```

## Workflow

### Complete Verification Workflow

1. **Run Empty Icon Filter** (one-time):
   ```bash
   uv run src/helper_tools/filter_empty_icons.py
   ```
   This marks empty icons to avoid selecting them.

2. **Launch GUI Mapper**:
   ```bash
   uv run src/helper_tools/interactive_icon_mapper.py
   ```

3. **Verify High-Priority Items First**:
   - Focus on commonly used items (weapons, armor, consumables)
   - Spell scrolls (items 32-100 typically)
   - Quest items

4. **Verification Strategy**:
   
   **For each item**:
   - Look at the handle name (tells you what it should look like)
   - Try different atlas numbers
   - Avoid icons with red borders (empty)
   - Save when you find the right match

   **Handle name patterns**:
   - `ui_item_equip_weapon_dagger_flame` → Flaming dagger
   - `ui_spell_EM_Fire_FireBurst` → Fire burst spell icon
   - `ui_item_consume_potion_health` → Health potion

5. **Save Progress**:
   - Click "Save Verification" after each item
   - Click "Save All to File" every 10-20 items
   - Export backups periodically

6. **Track Progress**:
   - Check stats at bottom of left panel
   - Filter "Show unverified only" to see remaining work

## Integration with CFF Editor

Once you have verified mappings, update the CFF editor:

**Edit**: `TirganachReloaded/cff_editor/data_model.py`

```python
def _load_verified_mappings(self):
    """Load verified icon mappings."""
    mapping_path = self.data_dir / "verified_icon_mappings.json"
    
    if mapping_path.exists():
        with open(mapping_path, 'r') as f:
            self.verified_icons = json.load(f)
    else:
        self.verified_icons = {}

def get_icon_path(self, category: str, element: Any) -> Optional[str]:
    """Get icon path for element with verified mapping priority."""
    
    item_id = self._get_element_id(category, element)
    if not item_id:
        return None
    
    # Priority 1: Use verified mapping
    item_id_str = str(item_id)
    if item_id_str in self.verified_icons:
        # Get primary icon (index 1)
        if '1' in self.verified_icons[item_id_str]:
            icon_path = self.ui_assets_dir / self.verified_icons[item_id_str]['1']
            if icon_path.exists():
                return str(icon_path)
    
    # Priority 2: Fall back to automatic mapping
    # (existing code...)
```

## Statistics

### Current Status

**After Empty Icon Filter**:
- Total icons: 7,424
- Valid icons: 5,040 (67.9%)
- Empty icons: 2,384 (32.1%)
- Unique icons: 7,261 (after removing 163 duplicates)

**Items to Verify**:
- Total items: 6,237
- Items verified: 0 (as of initial extraction)
- Remaining: 6,237

**Estimated Time**:
- Per item: 10-30 seconds (depending on atlas searching)
- Total time: ~17-52 hours for full verification
- Recommended: Verify top 500-1000 most-used items first

### Optimization Tips

1. **Focus on Important Items**:
   - Items 1-500: Basic game items
   - Items 1000-2000: Equipment
   - Items 3000+: Quest/special items

2. **Use Handle Names**:
   - Handle tells you what icon should look like
   - Search functionality helps find similar items

3. **Pattern Recognition**:
   - Once you find correct atlas for a category, others nearby often use same atlas
   - Spell scrolls typically cluster in same atlas range

4. **Batch Verification**:
   - Verify similar items together (all daggers, all potions)
   - Use duplicate detection to find repeated icons

## Troubleshooting

### GUI Won't Launch

```bash
# Install PyQt6
uv pip install PyQt6

# Check installation
python3 -c "from PyQt6.QtWidgets import QApplication; print('OK')"
```

### Icons Not Showing

1. Check icon path exists:
   ```bash
   ls ExtractedAssets/UI/icons_extracted/item/atlas_0/
   ```

2. Verify icon_index.json loaded:
   - Should have 7,424 entries
   - Check file size: ~15-20 MB

### Slow Performance

1. **Reduce icon analysis detail**:
   - Comment out edge detection in `filter_empty_icons.py`
   - Skip perceptual hash calculation

2. **Use command-line tools**:
   - Faster than GUI for batch operations

## Next Steps

1. ✅ **Empty Icon Filtering**: Complete
2. ✅ **Interactive GUI Mapper**: Complete
3. ⏳ **Verify Top 100 Items**: In progress
4. ⏳ **Pattern Analysis**: Pending
5. ⏳ **CFF Editor Integration**: Pending

## FAQ

**Q: Do I need to verify all 6,237 items?**
A: No, focus on the most commonly used items first. Many items (quest items, special events) may not need icon verification.

**Q: What if I can't find the right icon?**
A: Some handles may not have corresponding icons in the extracted atlases. Mark as "not found" and move on.

**Q: Can I automate this?**
A: Partially. Pattern analysis can suggest likely atlases, but visual verification is recommended for accuracy.

**Q: How do I know which atlas is correct?**
A: Compare the icon with the handle name. For example, `ui_item_equip_weapon_dagger_flame` should show a flaming dagger.

**Q: What about spell icons?**
A: Spell icons follow similar patterns but use `ui_spell_` prefix. They're in the `spell` category atlases (0-17).

---

**Last Updated**: October 24, 2025
