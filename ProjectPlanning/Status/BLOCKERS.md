# Current Blockers & Issues

**Last Updated**: October 26, 2025

## Critical Blockers 🚨

### 1. Icon Handle-to-Atlas Mapping
**Status**: ❌ BLOCKING
**Impact**: High - Prevents full automation of icon system
**Description**: GameData exports contain `item_ui_handle` and `item_ui_index` but no `item_ui_texture` field specifying which atlas file contains each icon.

**Evidence**:
```json
{
  "item_id": 27,
  "item_ui_handle": "ui_item_equip_weapon_dagger_flame",
  "item_ui_index": 1
  // Missing: item_ui_texture/atlas number
}
```

**Workarounds Considered**:
- Manual mapping with visual verification
- On-demand icon lookup system
- Community-assisted mapping project

**Next Steps**:
1. Search original PAK files for embedded mapping data
2. Reverse engineer game's icon loading system
3. Check for configuration files or lookup tables

### 2. Quest Editor Data Models
**Status**: 🔄 IN PROGRESS
**Impact**: Medium - Delays quest editing features
**Description**: QuestNode and DialogNode classes need completion with full serialization and validation.

**Current State**:
- Basic class structures designed
- Integration points identified
- Validation logic partially implemented

**Next Steps**:
1. Complete serialization/deserialization
2. Add comprehensive validation
3. Integrate with CFF data structures

## Medium Priority Issues ⚠️

### 3. Spell Icon GUI Display
**Status**: ❌ NOT WORKING
**Impact**: Medium - Spell icons don't show in editor
**Description**: Spell icons extracted successfully but not displaying in GUI editor tables.

**Possible Causes**:
- Mapping issue (same as item icons)
- Different atlas structure (4×4 grid vs 16×16)
- GUI integration bug

**Debugging Needed**:
1. Verify icon loading code paths
2. Check spell category icon display
3. Test with known spell handles

### 4. GUI Error Handling
**Status**: 🔄 PARTIALLY COMPLETE
**Impact**: Low-Medium - Occasional crashes on edge cases
**Description**: Some error conditions not handled gracefully in GUI editor.

**Known Issues**:
- Large file loading edge cases
- Invalid data validation
- Memory management with very large datasets

## Low Priority Issues 📝

### 5. Recent Files Menu
**Status**: ⏳ PENDING
**Impact**: Low - Convenience feature missing
**Description**: GUI editor lacks recent files menu for quick access.

**Implementation**:
- Add QSettings-based persistence
- Integrate with main window menu
- Limit to last 10 files

### 6. Advanced GUI Features
**Status**: 📋 PLANNED
**Impact**: Low - Nice-to-have features
**Description**: Phase 5 features not yet implemented.

**Missing Features**:
- Undo/Redo functionality
- Add/Clone/Delete elements
- Global search across categories
- Batch edit operations
- CSV export/import

## Resolved Issues ✅

### 7. Asset Extraction Pipeline
**Status**: ✅ RESOLVED
**Description**: Complete extraction of 59,500+ assets working reliably.

### 8. ITM Icon Extraction
**Status**: ✅ RESOLVED
**Description**: 4096+ icons extracted with weapon reassembly working.

### 9. GUI Core Functionality
**Status**: ✅ RESOLVED
**Description**: Basic editing, navigation, and saving working across all categories.

### 10. Multilingual Support
**Status**: ✅ RESOLVED
**Description**: 6 languages with real-time switching implemented.

## Risk Mitigation Strategies

### For Critical Blockers
1. **Parallel Investigation**: Multiple approaches to icon mapping
2. **Fallback Systems**: Manual mapping interfaces
3. **Community Help**: Open mapping challenges to community

### For Development Delays
1. **Modular Design**: Quest editor can be developed independently
2. **Feature Flags**: Incomplete features can be disabled
3. **Incremental Releases**: Working features released while others develop

### For Quality Issues
1. **Comprehensive Testing**: Automated test suites
2. **Error Boundaries**: Graceful degradation on failures
3. **User Feedback**: Beta testing with detailed reporting

## Monitoring & Escalation

### Weekly Check-ins
- Review blocker status every Monday
- Update timelines based on progress
- Escalate if no progress for 2+ weeks

### Escalation Triggers
- **Critical**: No progress on icon mapping after 4 weeks
- **High**: Quest editor blocked for 3+ weeks
- **Medium**: GUI stability issues affecting core functionality

### Success Criteria
- **Icon Mapping**: Resolved or acceptable workaround implemented
- **Quest Editor**: Basic functionality working within 6 weeks
- **GUI Stability**: No crashes on common operations
- **All Features**: Either working or properly disabled with clear messaging