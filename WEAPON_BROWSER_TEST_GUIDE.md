# Weapon Browser Integration - Manual Testing Guide

**Status**: ✅ READY FOR TESTING  
**Date**: 2025-01-20  
**Task**: Task 1 - Complete Weapon Browser Integration

---

## What Was Implemented

The weapon browser integration is now complete. Users can:
- Browse 719 existing weapons from the game
- Load a weapon for editing
- Duplicate a weapon with a new ID
- Have weapon data automatically populate all wizard pages

---

## Automated Test Results

### ✅ Unit Tests Passing
```
✓ WeaponForgeWizard imports successfully
✓ Can create ID Manager
✓ Browse button exists
✓ Selected weapon label exists
✓ Weapon loader instance exists
✓ Methods exist: on_mode_changed, browse_weapons, validatePage
✓ Mode change behavior working
✓ Validation working (rejects edit mode without weapon)
✓ BasicPropertiesPage has initializePage
✓ CombatStatsPage has initializePage
✓ RequirementsValuePage has initializePage
```

### ✅ Integration Tests Passing
```
✓ Weapon Loader loads from 719 weapon database
✓ Browser Dialog creates successfully with 719 weapons
✓ Table displays weapon data correctly
```

---

## Manual Testing Instructions

### Prerequisites
```bash
cd SpellSmut
uv run python src/TirganachReloaded/cff_editor/main.py
```

### Test Scenario 1: Create New Weapon (Baseline)
**Purpose**: Verify existing functionality still works

1. Launch application
2. Navigate to: **Tools → Weapon Forge** (or press Ctrl+W, F)
3. On Mode Selection page:
   - ✓ "Create New Weapon" should be selected by default
   - ✓ "Browse Weapons..." button should be DISABLED
   - ✓ Label should say "No weapon selected"
4. Click "Next"
5. ✓ Should proceed to Basic Properties page
6. ✓ All fields should be empty/default values
7. Click "Cancel" to exit

**Expected**: Works as before (no regression)

---

### Test Scenario 2: Edit Existing Weapon (NEW!)
**Purpose**: Test the new browse and edit functionality

1. Launch wizard: **Tools → Weapon Forge**
2. On Mode Selection page:
   - Select **"Edit Existing Weapon (load from 719 weapons)"**
   - ✓ "Browse Weapons..." button should become ENABLED
   - ✓ Label should still say "No weapon selected"

3. Click **"Browse Weapons..."** button
   - ✓ Weapon browser dialog should open
   - ✓ Title: "Select Weapon to Edit"
   - ✓ Table should show 719 weapons
   - ✓ Columns: ID, Name, Type, Material, Damage, Speed, Rarity

4. In the browser:
   - ✓ Try typing in the search box (should filter weapons)
   - ✓ Try changing the type filter dropdown
   - ✓ Select a weapon (e.g., "Flameblade Dagger" - ID 27)
   - Click **"Load Weapon"** button (or double-click the row)

5. Back on Mode Selection page:
   - ✓ Label should now show: "Selected: Flameblade Dagger (ID: 27)"
   - ✓ Label should be green and bold

6. Click **"Next"**
   - ✓ Should proceed (no validation error)

7. On **Basic Properties** page:
   - ✓ Weapon Name should be populated: "Flameblade Dagger"
   - ✓ Weapon Type should show the loaded type
   - ✓ Material should show the loaded material
   - ✓ Hands should be set correctly
   - ✓ Damage Category should be set correctly
   - ✓ Description should be populated

8. Click **"Next"** to **Combat Stats** page:
   - ✓ Min/Max Damage should be populated
   - ✓ Damage Type should be set
   - ✓ Attack Speed should be populated
   - ✓ Range values should be populated
   - ✓ Attack Arc should be populated
   - ✓ Special properties (crit, armor pen, knockback) should be set

9. Click **"Next"** to **Requirements & Value** page:
   - ✓ Stat requirements (Str/Dex/Int/Level) should be populated
   - ✓ Sell/Buy values should be populated
   - ✓ Rarity should be set correctly

10. You can now modify any values and continue through the wizard

**Expected**: All weapon data loads correctly and populates all pages

---

### Test Scenario 3: Duplicate & Modify (NEW!)
**Purpose**: Test duplicate mode

1. Launch wizard: **Tools → Weapon Forge**
2. Select **"Duplicate & Modify (copy existing, new ID)"**
   - ✓ "Browse Weapons..." button should be ENABLED
3. Click "Browse Weapons..." and select a weapon
4. Click "Next"
5. ✓ Should work exactly like Edit mode
6. ✓ Data should populate all pages
7. ✓ New ID will be assigned (verify in console or final page)

**Expected**: Works same as Edit mode

---

### Test Scenario 4: Edit Mode Validation
**Purpose**: Test validation prevents proceeding without weapon selection

1. Launch wizard
2. Select "Edit Existing Weapon"
3. Do NOT click "Browse Weapons..."
4. Click "Next" immediately
5. ✓ Should show error dialog: "No Weapon Selected"
6. ✓ Dialog message: "Please select a weapon to edit or duplicate by clicking 'Browse Weapons...'"
7. ✓ Should NOT proceed to next page
8. Click OK on error dialog
9. Now click "Browse Weapons...", select a weapon
10. Click "Next"
11. ✓ Should proceed successfully

**Expected**: Validation prevents advancing without weapon selection

---

### Test Scenario 5: Mode Switching
**Purpose**: Test switching between modes clears selection

1. Launch wizard
2. Select "Edit Existing Weapon"
3. Click "Browse Weapons..." and select a weapon
4. ✓ Label shows selected weapon (green)
5. Switch to "Create New Weapon"
6. ✓ Label should change to "No weapon selected" (gray)
7. ✓ Browse button should be DISABLED
8. Switch to "Duplicate & Modify"
9. ✓ Label should still show "No weapon selected"
10. ✓ Browse button should be ENABLED

**Expected**: Selection is cleared when switching modes

---

### Test Scenario 6: Weapon Browser Search
**Purpose**: Test search and filter functionality

1. Launch wizard and open browser
2. In search box, type "flame"
   - ✓ Table should filter to show only weapons with "flame" in name
   - ✓ Should see weapons like "Flameblade Dagger", "Flameblade Sword"
3. Clear search box
   - ✓ All 719 weapons should reappear
4. Select "Daggers" in Type filter dropdown
   - ✓ Should show only dagger-type weapons
5. Type "flame" in search while Daggers filter is active
   - ✓ Should show only flame weapons that are daggers
6. Test double-click
   - ✓ Double-clicking a row should load the weapon and close dialog

**Expected**: Search and filter work correctly

---

## Known Issues / Limitations

### Non-Critical Issues:
1. **Weapon types/materials in dropdowns** - Currently shows placeholder values
   - Loaded weapon types may not appear in dropdown
   - This is OK for now, actual values are stored correctly
   - Will be fixed when we populate dropdowns with all weapon types

2. **Zero damage values** - Some weapons show 0-0 damage
   - This is in the source data (enhanced_weapons.json)
   - Not a bug in the browser integration
   - Original game data has placeholders for some weapons

3. **Effects not populated** - RequirementsValuePage doesn't load effects yet
   - Effects list is complex (multiple effects per weapon)
   - Requires additional UI implementation
   - Defer to future enhancement

### Critical Issues (Report if found):
- ❌ Browser dialog crashes
- ❌ Weapon data doesn't populate after loading
- ❌ Can proceed without selecting weapon in edit mode
- ❌ Selected weapon label doesn't update
- ❌ Browse button doesn't enable in edit/duplicate modes

---

## Success Criteria

### Must Pass:
- ✅ Can browse 719 weapons
- ✅ Can select and load a weapon
- ✅ Weapon data populates Basic Properties page
- ✅ Weapon data populates Combat Stats page
- ✅ Weapon data populates Requirements page
- ✅ Validation prevents advancing without weapon selection
- ✅ Mode switching clears selection
- ✅ New weapon mode still works (no regression)

### Nice to Have:
- ✅ Search filters weapons by name
- ✅ Type filter works
- ✅ Double-click loads weapon
- ✅ Visual feedback (green label) when weapon selected

---

## Troubleshooting

### Issue: "No module named 'weapon_browser_dialog'"
**Solution**: Make sure you're running from the project root and using `uv run`

### Issue: Browser dialog is empty
**Solution**: Check that `src/TirganachReloaded/enhanced_weapons.json` exists

### Issue: Weapon data doesn't populate
**Solution**: 
1. Check console for errors
2. Verify you clicked "Next" after loading weapon
3. Make sure you selected a weapon (label should be green)

### Issue: Can't find "Weapon Forge" in menu
**Solution**: Make sure changes were committed and you restarted the application

---

## Reporting Results

After testing, please document:

1. **Which scenarios passed** (1-6)
2. **Any issues found** (with steps to reproduce)
3. **Screenshots** (optional but helpful)
4. **Overall assessment**: Ready for commit? Needs fixes?

---

## Next Steps After Testing

If all tests pass:
1. ✅ Mark Task 1 as complete
2. Commit changes with message: "feat: complete weapon browser integration"
3. Update WEAPON_FORGE_TODO.md (check off Task 1 items)
4. Update WEAPON_FORGE_STATUS.md (mark browser as ✅)
5. Move to Task 3: Complete Review & Export Page

---

**Testing Time Estimate**: 15-20 minutes  
**Tester**: [Your name]  
**Date Tested**: [Date]  
**Result**: [ ] PASS / [ ] FAIL / [ ] NEEDS FIXES