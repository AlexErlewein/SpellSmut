# Pending GUI Issues

## 1. ITM Extraction Quality Issues

### Problem
The current ITM extraction script has alignment and offset issues that affect icon quality and positioning. Weapon reassembly also needs optimization.

### Required Actions
- [ ] Replace current ITM extraction script with improved version
- [ ] Fix alignment/offset calculation in icon extraction
- [ ] Optimize weapon reassembly algorithms (1x2 and 1x4 patterns)
- [ ] Verify icon quality and positioning accuracy
- [ ] Test with various weapon types to ensure consistency

### Priority
HIGH - Affects the quality of item icons in the GUI

## 2. Spell Icon Display Issues

### Problem
Although spell icons have been extracted and mapped, they are not displaying correctly in the GUI editor.

### Status Update
✅ Identified the root cause: The `_resolve_icon_path` method in the data model was not correctly resolving spell icon paths
✅ Fixed the method to look in the correct directory structure
✅ Spell icons are now being correctly located on the filesystem

### Required Actions
- [x] Debug why spell icons aren't displaying in GUI
- [x] Verify icon mapping is correctly loaded  
- [x] Check GUI icon resolution paths and file lookups
- [ ] Test spell category icon display in actual GUI
- [ ] Improve spell icon mapping to ensure correct icons are shown for each spell

### Priority
HIGH - Prevents proper visualization of spell data

## 3. Root Cause Analysis

### Previously Identified Issues for Spell Icons Not Displaying:
1. **Path Resolution**: ✅ FIXED - The GUI wasn't resolving spell icon paths correctly
2. **Category Mapping**: ✅ VERIFIED - Spell category was properly mapped in the data model
3. **File Format**: ✅ VERIFIED - PNG files are loading correctly
4. **Cache Issues**: ✅ VERIFIED - No caching issues found
5. **Size Scaling**: ✅ VERIFIED - Spell icons are 64x64 and scale correctly to 32x32 for table view

### Current Status
The data model now correctly locates spell icons, but there may still be issues with ensuring the correct icon is shown for each specific spell. The current implementation finds spell icons but may not be mapping them correctly to specific spell handles.

## 4. Next Steps

1. **Immediate Debugging**:
   - [x] Add debug logging to trace icon loading in data_model.py ✅ COMPLETED
   - [x] Verify spell icons exist in expected directories ✅ COMPLETED
   - [x] Check that ui_icon_mapping.json contains spell entries ✅ COMPLETED
   - [ ] Run the GUI editor to test actual spell icon display
   - [ ] Add logging to trace which specific icons are being loaded for spells

2. **Code Review**:
   - [x] Review get_icon_path method for spell category handling ✅ COMPLETED
   - [x] Check _resolve_icon_path method for spell icon resolution ✅ COMPLETED
   - [ ] Examine GUI widget code for icon display logic
   - [ ] Review the detailed icon mapping implementation

3. **Testing**:
   - [ ] Create minimal test to load a specific spell icon
   - [ ] Verify spell entries exist in spell_names table
   - [ ] Test direct file loading of spell icons
   - [ ] Run the GUI editor to verify spell icons display correctly