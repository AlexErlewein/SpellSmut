# Icon System - Next Steps & Planning

## Completed ✅

1. **Item Icon Extraction**
   - 27,648 icons from 432 atlases
   - 32×32 pixels, 8×8 grid, no offset
   - Working correctly

2. **Spell Icon Extraction** 
   - 162 icons from 18 atlases
   - 64×64 pixels, 4×4 grid
   - (3,3) offset for centering
   - 180° rotation applied
   - Working correctly

3. **Empty Icon Detection**
   - Analyzed 6,434 icons
   - Identified 2,070 empty icons (32.2%)
   - Created visual report and metadata
   - Icon index updated with `is_empty` flags

4. **Interactive GUI Mapper**
   - PyQt6 interface created
   - Manual verification capability
   - Saves to `verified_icon_mappings.json`

5. **CFF Editor Integration**
   - Icon data loading on startup
   - 4-tier priority system
   - Automatic empty icon avoidance

---

## Step 3: Check Other Categories (IN PROGRESS)

**Status**: Analyzing bgr, btn, oth, cnt, itm, logo categories

**Goal**: Determine if other categories need special extraction settings (offset, rotation, different grid sizes)

**Categories to Check**:
- `bgr` (1,161 atlases) - Backgrounds? 256×256
- `btn` (77 atlases) - Buttons? 256×256
- `oth` (9 atlases) - Other UI? 256×256
- `cnt` (37 atlases) - Unknown, 256×256
- `itm` (16 atlases) - Items variant? 256×256
- `logo` (4 atlases) - Logos, 512×512

**Action Items**:
- [ ] Visual inspection of sample atlases
- [ ] Determine actual grid patterns used
- [ ] Test extraction with detected settings
- [ ] Document findings
- [ ] Update extraction script if needed

---

## Step 4: Test CFF Editor Integration

**Goal**: Verify end-to-end functionality with corrected spell icons

**Prerequisites**: 
- Step 3 complete (know all icon formats)
- All icons properly extracted

**Testing Checklist**:
- [ ] Launch CFF editor
- [ ] Load GameData.cff file
- [ ] Navigate to item editor
- [ ] Verify item icons display correctly
- [ ] Navigate to spell editor (if exists)
- [ ] Verify spell icons display correctly
- [ ] Test icon priority system (verified > automatic > fallback)
- [ ] Test empty icon avoidance
- [ ] Check icon loading performance
- [ ] Document any issues found

**Considerations**:
- Does spell data in CFF have icon references?
- Are spell icons referenced by handle or index?
- Do we need to build spell icon mappings?
- Performance: 6,434 icons - is loading fast enough?

---

## Step 5: Manual Verification GUI

**Goal**: Build verified mapping database for high-priority items

**Strategy**:
1. Identify "important" items to verify first:
   - Unique/legendary weapons
   - Quest items
   - Key consumables
   - Special equipment

2. Use interactive GUI to manually verify:
   - Load item by handle/name
   - View assigned icon
   - Search through atlases if wrong
   - Assign correct icon
   - Save to verified database

3. Build priority list:
   - How many items total?
   - Which items are most commonly used?
   - Which items have incorrect auto-mappings?

**Considerations**:
- Time investment: Manual verification is slow
- ROI: Is it worth verifying all items?
- Alternative: Only verify items that are reported wrong
- Could we improve automatic mapping instead?

**Questions to Answer**:
- [ ] How many items exist in total?
- [ ] What percentage have icons currently?
- [ ] What's the accuracy of auto-mapping?
- [ ] Sample 50 items - how many are correct?
- [ ] Is there a pattern to incorrect mappings?

---

## Step 6: Build Complete Icon Mapping System

**Goal**: Create comprehensive handle-to-icon lookup system

**Current State (2025-10-25)**:
- ✅ **ITM icons extracted**: 4096 icons from 16 atlases, weapons reassembled
- ✅ **Extraction pipeline working**: DDS→PNG, weapon detection, reassembly
- ❌ **Critical gap identified**: No atlas numbers in GameData exports
- ❌ **Handle-to-atlas mapping missing**: Cannot connect UI handles to icon files

**Key Discovery**: GameData exports lack atlas information. The `item_ui_texture` field (atlas number) is not included in the JSON export.

### Updated Architecture Plan

#### Phase 1: Find Missing Atlas Data 🔍
**URGENT**: Locate atlas mapping information
- Search original game files for atlas assignments
- Check PAK file structures or embedded data
- Reverse engineer from C++ game code
- Look for Lua scripts with atlas mappings

#### Phase 2: ITM Mapping Solution
Since ITM extraction works, create mapping for items:
```python
# Current GameData (missing atlas info):
{
  "item_id": 27,
  "item_ui_index": 1,
  "item_ui_handle": "ui_item_equip_weapon_dagger_flame",
  "scaled_down": 0
}

# Needed: atlas number discovery
# Possible approaches:
# 1. Visual pattern matching
# 2. Item ID range analysis
# 3. Manual mapping with verification
```

#### Phase 3: Spell Mapping Investigation
Spells use different system (4×4 grid, 64×64 icons):
- Extract ui_spell8.dds, ui_spell9.dds
- Test grid extraction
- Find spell-to-atlas relationships

#### Phase 4: Fallback Systems
For unmapped icons:
- Name-based similarity matching
- Category defaults (weapon → sword icon, etc.)
- Placeholder icons with "needs mapping" indicators

#### Phase 5: Manual Override System
Community-assisted mapping:
- Web interface for icon verification
- Confidence scoring for mappings
- Version control for mapping database

### Phase 4: API
Create lookup functions:

```python
def get_icon(handle: str) -> Path:
    """Get icon path for item handle."""
    
def get_icon_info(handle: str) -> dict:
    """Get full icon metadata."""
    
def search_icons(query: str) -> list:
    """Search for icons by name/category."""
```

**Considerations**:
- **Data Quality**: Are item_ui_* fields complete in GameData.json?
- **Missing Data**: What % of items have icon references?
- **Spells**: Do spells have similar fields? Different structure?
- **Performance**: Cache mappings? Lazy load?
- **Updates**: How to handle game data updates?

**Action Items**:
- [ ] Analyze GameData.json structure
  - [ ] Count items with icon data
  - [ ] Identify field names for spells
  - [ ] Check data completeness
  - [ ] Document edge cases

- [ ] Build automatic mapper
  - [ ] Parse GameData.json
  - [ ] Extract icon references
  - [ ] Validate against icon_index.json
  - [ ] Generate mapping.json

- [ ] Test mapping accuracy
  - [ ] Sample random items
  - [ ] Visual verification
  - [ ] Measure success rate

- [ ] Integrate with CFF editor
  - [ ] Update data_model.py
  - [ ] Add icon lookup methods
  - [ ] Test performance

---

## Step 7: Documentation

**Goal**: Complete documentation for icon system

**Documents to Create/Update**:

1. **User Guide**: `ICON_SYSTEM_USER_GUIDE.md`
   - How to extract icons
   - How to use icon mapper
   - How to verify mappings
   - Troubleshooting

2. **Technical Spec**: `ICON_SYSTEM_TECHNICAL.md`
   - Atlas format specifications
   - Extraction algorithm
   - Mapping system architecture
   - File format documentation

3. **API Reference**: Update existing docs
   - Icon lookup functions
   - Data structures
   - Integration examples

4. **Update Existing Docs**:
   - QUICK_START_ICON_EXTRACTION.md
   - QUICK_START_ICON_SYSTEM.md
   - CFF_EDITOR_README.md

**Content to Include**:
- Step-by-step guides
- Screenshots/examples
- Code snippets
- Troubleshooting tips
- Known issues
- Future improvements

---

## Priority Ordering

**Suggested Order**:

1. **Step 3** (Current) - Complete category analysis
   - Ensures all icons extracted correctly
   - Foundational for everything else

2. **Step 6 Phase 1** - Build automatic mapping
   - Unlock icon functionality
   - High value, medium effort
   - Required for testing editor

3. **Step 4** - Test CFF editor
   - Validate entire system works
   - Identify missing pieces
   - Real-world usage test

4. **Step 6 Phase 2-3** - Improve mapping
   - Based on editor testing results
   - Address accuracy issues found

5. **Step 5** - Manual verification (as needed)
   - Only for problem items
   - Not bulk verification
   - On-demand approach

6. **Step 7** - Documentation
   - After system stabilizes
   - Document actual behavior
   - Include lessons learned

---

## Open Questions

### Data Structure
- [ ] What icon fields exist in spell data?
- [ ] Are there other entity types with icons? (buildings, units, etc.)
- [ ] What's in the other categories (bgr, btn, oth)?

### Performance
- [ ] Icon loading speed acceptable?
- [ ] Need icon caching?
- [ ] Memory usage with 6K+ icons?

### Accuracy
- [ ] What's auto-mapping success rate?
- [ ] Common failure patterns?
- [ ] Worth investing in ML/similarity matching?

### Scope
- [ ] Extract ALL categories or just item/spell?
- [ ] Build mappings for non-game entities?
- [ ] Support modded icons?

---

## Success Criteria

**Step 3**: All categories analyzed, extraction settings documented
**Step 4**: CFF editor displays icons correctly, no crashes, acceptable performance
**Step 5**: High-priority items verified, tools exist for on-demand verification  
**Step 6**: Automatic mapping working, >90% accuracy, integrated with editor
**Step 7**: Complete documentation, new users can extract and use icons

---

## Timeline Estimates

- **Step 3**: 1-2 hours (depends on findings)
- **Step 6 Phase 1**: 2-4 hours (data analysis + implementation)
- **Step 4**: 1 hour (testing + fixes)
- **Step 6 Phase 2-3**: 2-3 hours (algorithm improvements)
- **Step 5**: Ongoing (as needed)
- **Step 7**: 3-4 hours (comprehensive docs)

**Total**: ~10-15 hours for complete system

---

## Notes

- Focus on item/spell icons first (core functionality)
- Other categories may not need extraction (UI elements, not game content)
- Prioritize working system over perfect accuracy
- Can iterate on accuracy after basic functionality works
- Community could help with manual verification later
