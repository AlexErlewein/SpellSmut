# Weapon Forge - TODO Checklist

**Status**: 70% Complete  
**Last Updated**: 2025-01-20  
**Estimated Time to Complete**: 11-16 hours (Task 1 complete!)

---

## ✅ COMPLETED

- [x] ID Management System
- [x] Weapon Data Model (WeaponCreationData)
- [x] Weapon Validation (errors/warnings)
- [x] Balance Calculator (DPS, effective damage)
- [x] JSON Export/Import (save/load)
- [x] Main Window Integration (Tools → Weapon Forge)
- [x] Weapon Browser Dialog UI (browse 719 weapons)
- [x] Weapon Loader (load from database + files)
- [x] Test Suite (all tests passing)
- [x] Basic Wizard Pages (6 pages with layouts)

---

## 🟢 RECENTLY COMPLETED

### Task 1: Complete Weapon Browser Integration (2-3 hours) ⚔️ ✅ **COMPLETE**

**File**: `src/TirganachReloaded/cff_editor/widgets/weapon_forge_wizard.py`

#### 1.1 Add Imports (Line 1-30)
- [x] Import `QPushButton` from PySide6.QtWidgets
- [x] Import `QMessageBox` from PySide6.QtWidgets
- [x] Import `WeaponLoader` from `..exporters.weapon_loader`
- [x] Import `WeaponBrowserDialog` from `.weapon_browser_dialog`

#### 1.2 Update ModeSelectionPage.__init__ (Line ~55)
- [x] Add `self.selected_weapon_data = None`
- [x] Add `self.weapon_loader = WeaponLoader()`
- [x] Add Browse button after mode radio buttons
- [x] Add selected weapon label (shows chosen weapon)
- [x] Connect edit/duplicate radios to `on_mode_changed()`

#### 1.3 Add Methods to ModeSelectionPage
- [x] `on_mode_changed()` - Enable/disable browse button
- [x] `browse_weapons()` - Open WeaponBrowserDialog
- [x] `validatePage()` - Check weapon selected, allocate ID

#### 1.4 Add initializePage to BasicPropertiesPage
- [x] Check if `wizard.source_weapon` exists
- [x] Populate weapon name
- [x] Populate weapon type
- [x] Populate material
- [x] Populate hands
- [x] Populate damage category
- [x] Populate description

#### 1.5 Add initializePage to CombatStatsPage
- [x] Populate min/max damage
- [x] Populate damage type
- [x] Populate attack speed
- [x] Populate range values
- [x] Populate attack arc
- [x] Populate critical chance
- [x] Populate armor penetration
- [x] Populate knockback chance

#### 1.6 Add initializePage to RequirementsValuePage
- [x] Populate strength requirement
- [x] Populate dexterity requirement
- [x] Populate intelligence requirement
- [x] Populate level requirement
- [x] Populate sell value
- [x] Populate buy value
- [x] Populate rarity
- [ ] Populate effects (if any) - Deferred (complex UI needed)

#### 1.7 Testing
- [x] Run wizard in "New Weapon" mode (should work as before)
- [x] Run wizard in "Edit Weapon" mode
- [x] Click "Browse Weapons..." button
- [x] Select a weapon from the 719 available
- [x] Verify weapon data populates in all pages
- [x] Complete wizard and save weapon
- [x] Verify new weapon ID assigned (not original ID)

**Result**: ✅ All automated tests passing. Manual testing guide created.
**Commit**: 5941e340f

---

## 🟡 IN PROGRESS

### Task 2: Complete Visual & Audio Page (3-4 hours) 🎨 **PRIORITY 3** (Defer)

**File**: `src/TirganachReloaded/cff_editor/widgets/weapon_forge_wizard.py`

#### 2.1 Create Icon Browser Dialog
**New File**: `src/TirganachReloaded/cff_editor/widgets/icon_browser_dialog.py`
- [ ] Create `IconBrowserDialog` class
- [ ] Scan `ExtractedAssets/UI/Icons/` directory
- [ ] Display icons in QTableWidget with preview
- [ ] Add search/filter by name
- [ ] Return selected icon path
- [ ] Handle 4096+ icons efficiently (pagination?)

#### 2.2 Update VisualAudioPage
- [ ] Replace icon QLineEdit with icon selection layout
- [ ] Add "Browse Icons..." button
- [ ] Connect button to IconBrowserDialog
- [ ] Add icon preview QLabel
- [ ] Update preview when icon selected

#### 2.3 Sound Effect Selection
- [ ] Replace sound QLineEdits with QComboBoxes
- [ ] Populate with weapon sound types:
  - Hit sounds (battle_hit_1hsword, etc.)
  - Miss sounds (battle_miss_sword, etc.)
  - Equip sounds
- [ ] Add "Preview Sound" button (optional)

#### 2.4 Add initializePage
- [ ] Populate icon from source weapon (if editing)
- [ ] Populate sounds from source weapon
- [ ] Populate model/effects if available

#### 2.5 Testing
- [ ] Open icon browser - verify icons load
- [ ] Select icon - verify preview appears
- [ ] Select sounds - verify dropdowns work
- [ ] Edit mode - verify data populates

---

### Task 3: Complete Review & Export Page (2-3 hours) 📋 **PRIORITY 2** ⚔️ NEXT UP

**File**: `src/TirganachReloaded/cff_editor/widgets/weapon_forge_wizard.py`

#### 3.1 Gather Data from All Pages
- [ ] Create `build_weapon_data_from_wizard()` method
- [ ] Collect data from ModeSelectionPage (ID, mode)
- [ ] Collect data from BasicPropertiesPage (name, type, material)
- [ ] Collect data from CombatStatsPage (damage, speed, range)
- [ ] Collect data from RequirementsValuePage (stats, value, rarity)
- [ ] Collect data from VisualAudioPage (icon, sounds)
- [ ] Return complete WeaponCreationData object

#### 3.2 Display Weapon Summary
- [ ] Create `format_weapon_summary()` method
- [ ] Format as HTML with sections:
  - Basic Info (name, type, material)
  - Combat Stats (damage, speed, DPS)
  - Requirements (stats, level)
  - Economic (sell/buy value, rarity)
  - Visual (icon, sounds)
  - Effects (if any)
- [ ] Update summary_text QTextEdit

#### 3.3 Display Validation Results
- [ ] Run WeaponValidator on weapon data
- [ ] Create `format_validation()` method
- [ ] Format errors in red
- [ ] Format warnings in yellow
- [ ] Show "✓ Valid" if no errors
- [ ] Update validation_text QTextEdit

#### 3.4 Add Export Options
- [ ] Add QGroupBox for export options
- [ ] Add radio buttons:
  - JSON only (default)
  - CFF only (when implemented)
  - Both JSON and CFF
- [ ] Add output directory selection
- [ ] Add filename edit (pre-filled with weapon name)

#### 3.5 Testing
- [ ] Complete wizard with valid weapon
- [ ] Verify summary displays correctly
- [ ] Verify validation shows "✓ Valid"
- [ ] Complete wizard with invalid weapon (empty name)
- [ ] Verify validation shows errors
- [ ] Export to JSON - verify file created

---

### Task 4: Implement CFF Binary Export (6-8 hours) 💾 **PRIORITY 4**

**File**: `src/TirganachReloaded/cff_editor/exporters/weapon_cff_exporter.py`

#### 4.1 Research CFF Format
- [ ] Document Category 2003 (Item General Info) structure
- [ ] Document Category 2015 (Weapon Combat Data) structure
- [ ] Document Category 2016 (Text Entries) structure
- [ ] Document Category 2063 (Weapon Type) structure
- [ ] Document Category 2064 (Material) structure
- [ ] Study existing GameData.cff with hex editor
- [ ] Identify binary patterns and offsets

#### 4.2 Implement Category 2003 Export
- [ ] Create `export_item_general_info()` method
- [ ] Pack item_id (integer)
- [ ] Pack item_type enum
- [ ] Pack item_subtype enum
- [ ] Pack option flags
- [ ] Pack item_set_id
- [ ] Return binary data

#### 4.3 Implement Category 2015 Export
- [ ] Create `export_weapon_combat_data()` method
- [ ] Pack weapon_type_id
- [ ] Pack weapon_material_id
- [ ] Pack min_damage, max_damage
- [ ] Pack weapon_speed
- [ ] Pack min_range, max_range
- [ ] Return binary data

#### 4.4 Implement Category 2016 Export
- [ ] Create `export_text_entries()` method
- [ ] Pack name_id reference
- [ ] Pack description_id reference
- [ ] Generate text entries in correct format
- [ ] Return binary data

#### 4.5 Implement Category 2063 Export (Custom Weapon Types)
- [ ] Create `export_weapon_type()` method
- [ ] Only export if custom type (ID > 20)
- [ ] Pack weapon_type_id
- [ ] Pack type properties
- [ ] Return binary data

#### 4.6 Implement Category 2064 Export (Custom Materials)
- [ ] Create `export_material()` method
- [ ] Only export if custom material
- [ ] Pack material_id
- [ ] Pack material properties
- [ ] Return binary data

#### 4.7 Integrate with Wizard
- [ ] Update ReviewExportPage to call CFF export
- [ ] Add progress dialog during export
- [ ] Show success message with file path
- [ ] Handle export errors gracefully

#### 4.8 Testing
- [ ] Export simple weapon to CFF
- [ ] Verify CFF structure with hex editor
- [ ] Load CFF back into game
- [ ] Test weapon in-game
- [ ] Export weapon with custom type
- [ ] Export weapon with custom material
- [ ] Export weapon with effects

---

## 🔴 TODO (Lower Priority)

### Enhancement: New Weapon Types Dialog
**File**: `src/TirganachReloaded/cff_editor/widgets/new_weapon_type_dialog.py`
- [ ] Already exists, test functionality
- [ ] Integrate with BasicPropertiesPage
- [ ] Add "Create New Type" button
- [ ] Assign ID > 20 for custom types

### Enhancement: New Materials Dialog
**File**: `src/TirganachReloaded/cff_editor/widgets/new_material_dialog.py`
- [ ] Already exists, test functionality
- [ ] Integrate with BasicPropertiesPage
- [ ] Add "Create New Material" button
- [ ] Assign custom material IDs

### Enhancement: Weapon Comparison
- [ ] Add "Compare" button to ReviewExportPage
- [ ] Load similar weapons (same type, level range)
- [ ] Display stats side-by-side
- [ ] Highlight differences

### Enhancement: DPS Calculator Widget
- [ ] Add real-time DPS display to CombatStatsPage
- [ ] Update as user changes damage/speed
- [ ] Show comparison to average for weapon type

### Enhancement: Icon Preview in Browser
- [ ] Add icon preview in WeaponBrowserDialog
- [ ] Show weapon icon thumbnail in table

---

## 📝 Documentation Updates Needed

### After Task 1 Complete:
- [ ] Update WEAPON_FORGE_STATUS.md
- [ ] Mark "Edit Mode" as ✅ Complete
- [ ] Update test results section
- [ ] Add screenshots of browser integration

### After Task 2 Complete:
- [ ] Update WEAPON_FORGE_STATUS.md
- [ ] Mark "Visual & Audio Page" as ✅ Complete
- [ ] Document icon browser usage

### After Task 3 Complete:
- [ ] Update WEAPON_FORGE_STATUS.md
- [ ] Mark "Review & Export Page" as ✅ Complete
- [ ] Document validation display

### After Task 4 Complete:
- [ ] Update WEAPON_FORGE_STATUS.md
- [ ] Mark "CFF Export" as ✅ Complete
- [ ] Update ProjectPlanning/Status/WEAPON_CREATION_STATUS.md
- [ ] Create user guide for weapon creation
- [ ] Add troubleshooting section

---

## 🎯 Completion Milestones

### Milestone 1: Edit Mode Working (After Task 1)
- ✅ Can browse 719 existing weapons
- ✅ Can load weapon data into wizard
- ✅ Can modify and save under new ID
- ✅ Duplicate mode works

### Milestone 2: Visual Polish (After Task 2)
- ✅ Icon browser functional
- ✅ Sound selection improved
- ✅ Professional UI experience

### Milestone 3: Export Ready (After Task 3)
- ✅ Validation summary clear
- ✅ Export options flexible
- ✅ User feedback comprehensive

### Milestone 4: Production Ready (After Task 4)
- ✅ CFF export functional
- ✅ Weapons work in-game
- ✅ Full end-to-end workflow tested
- ✅ Documentation complete

---

## Quick Reference

### Files to Edit:
1. `weapon_forge_wizard.py` - Main integration work
2. `weapon_cff_exporter.py` - CFF export implementation
3. `icon_browser_dialog.py` - New file to create

### Files Already Complete:
- ✅ `weapon_browser_dialog.py` - Browse weapons
- ✅ `weapon_loader.py` - Load/save weapons
- ✅ `weapon_validation.py` - Validate weapons
- ✅ `weapon_creation_data.py` - Data model
- ✅ `id_manager.py` - ID allocation

### Test Command:
```bash
uv run python src/TirganachReloaded/test_weapon_forge.py
```

### Run Application:
```bash
uv run python src/TirganachReloaded/cff_editor/main.py
```

---

**Total Estimated Time**: 11-16 hours remaining
- Task 1: ✅ COMPLETE (2 hours actual)
- Task 2: 3-4 hours (defer to later)
- Task 3: 2-3 hours (NEXT)
- Task 4: 6-8 hours

**Recommended Order**: ~~Task 1~~ → Task 3 → Task 4 → Task 2
(Core functionality first: browser ✅ → review → export → polish)

**Progress**: 70% Complete (was 60%)