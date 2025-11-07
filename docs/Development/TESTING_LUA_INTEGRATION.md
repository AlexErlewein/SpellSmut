# Testing Lua Quest Integration - Checklist

## Prerequisites

✅ Application starts without errors  
✅ CFF file is loaded  
✅ Lua quest scripts have been loaded via `Tools → Load Lua Quest Scripts...`

---

## Test 1: Verify Lua Scripts Loaded Successfully

### Steps:
1. Start the application
2. Open a CFF file (`File → Open CFF...`)
3. Go to `Tools → Load Lua Quest Scripts...`
4. Select the `script` directory (e.g., `OriginalGameFiles/modding/Original Scripts/script/`)
5. Click "Select Folder"

### Expected Console Output:
```
Found XXX Lua files in /path/to/script
Parsing: n0.lua
Parsing: GdsQuestRewards.lua
...
Error parsing n6690.lua: ...  (some files may fail - this is OK)
...
Parsed 335 quests from Lua files
Preloading 335 quests into memory...
✓ Preloaded 335 quests
```

### Expected Dialog:
```
Successfully loaded quest data from 335 quest(s).

Quest objectives, requirements, and rewards from Lua scripts
are now available in the Quest Editor.
```

### ✅ Pass Criteria:
- No crash during loading
- Dialog shows number of quests loaded (should be > 0)
- Some encoding errors are OK (German characters in filenames)

---

## Test 2: Verify Cache is Loaded in Memory

### Steps:
1. After loading Lua scripts, open Quest Editor (`Tools → Quest Editor`)
2. Check the console output

### Expected Console Output:
```
[DEBUG] has_lua_data check: cache_loaded=True, cache_size=335, has_data=True
```

### ✅ Pass Criteria:
- `cache_loaded=True`
- `cache_size > 0`
- `has_data=True`

### ❌ Fail If:
```
[DEBUG] has_lua_data check: cache_loaded=False, cache_size=0, has_data=False
```
This means cache didn't load - check if preload_cache() is being called.

---

## Test 3: Quest Tree Loads Automatically

### Steps:
1. Open Quest Editor (`Tools → Quest Editor`)
2. The Quest Hierarchy tab should be active by default

### Expected Behavior:
- Tree view shows quests immediately
- No need to click between tabs
- Quests are organized in parent-child hierarchy
- Quest count shows in header (e.g., "Quests: 50 (Main: 20)")

### ✅ Pass Criteria:
- Tree populates without user interaction
- Quest names are visible
- Can expand/collapse nodes

---

## Test 4: Lua Data Appears in Quest Details

### Steps:
1. In Quest Editor, go to **Quest Hierarchy** tab
2. Click on any quest in the tree
3. Switch to **Quest Details** tab
4. Scroll through all sections

### Expected Console Output (when selecting a quest):
```
[DEBUG] Updating quest details for quest ID: 12
[DEBUG] Has Lua data available: True
[DEBUG] Quest Giver - Lua data for quest 12: True
[DEBUG]   NPC ID: 1240, Platform: P1
[DEBUG] Requirements - Lua data for quest 12: True
[DEBUG]   Requirements count: 2
[DEBUG] Objectives - Lua data for quest 12: True
[DEBUG]   Objectives count: 3
[DEBUG] Rewards - Lua data for quest 12: True
[DEBUG]   XP: 500, Gold: 5, Items: 2
```

### Expected Visual Output:

#### Quest Giver Section:
```
NPC ID: 1240
Location/Map: P1 [from Lua]
```

#### Requirements Section:
```
[Lua] Player must be level 10 or higher (Type: Level) - Value: 10
[Lua] Complete Quest 8 first (Type: Quest) - Value: 8
```

#### Objectives Section:
```
Objective                                    | Type    | Target    | Count
[Lua] Defeat 5 Goblins                      | Kill    | Goblin    | 5
[Lua] Collect Quest Item                    | Collect | Item 2336 | 1
[Lua] Talk to NPC                           | Talk    | NPC 1450  | -
```

#### Rewards Section:
```
XP Reward: 500 XP [from Lua]
Money: 5 Gold, 10 Silver, 0 Copper [from Lua]
Items:
  [Lua] Item ID: 626
  [Lua] Item ID: 707
```

### ✅ Pass Criteria:
- See `[Lua]` or `[from Lua]` prefixes on data
- Console shows debug output confirming Lua data found
- Data is populated (not empty or "Unknown")

### ❌ Fail If:
```
[DEBUG] Lua data for quest 12: False
```
Or if sections show:
```
No objectives defined (check Lua scripts)
No special requirements (check Lua scripts)
No item rewards (check Lua scripts)
```

---

## Test 5: Quest Without Lua Data

### Steps:
1. Select different quests until you find one without Lua data
2. Check console output

### Expected Console Output:
```
[DEBUG] Updating quest details for quest ID: 999
[DEBUG] Has Lua data available: True
[DEBUG] Quest Giver - Lua data for quest 999: False
[DEBUG] Requirements - Lua data for quest 999: False
[DEBUG] Objectives - Lua data for quest 999: False
[DEBUG] Rewards - Lua data for quest 999: False
```

### Expected Visual Output:
```
Quest Giver: Unknown (check Lua scripts)
Requirements: No special requirements (check Lua scripts)
Objectives: No objectives defined (check Lua scripts)
Rewards: No item rewards (check Lua scripts)
```

### ✅ Pass Criteria:
- Application doesn't crash
- Shows helpful messages about checking Lua scripts
- Falls back to CFF data if available

---

## Test 6: Encoding Handling

### Steps:
1. Check console output during Lua loading
2. Look for encoding error messages

### Expected Behavior:
```
Error parsing n6690.lua: 'utf-8' codec can't decode byte 0xfc in position 678: invalid start byte
```

### Note:
- Some encoding errors are **normal** for files with special German characters
- The parser should continue and parse other files
- Total parsed count should still be high (335+)

### ✅ Pass Criteria:
- Parser continues after encoding errors
- Other files parse successfully
- Final count shows many quests parsed

---

## Test 7: Cache Persistence

### Steps:
1. Load Lua scripts (first time)
2. Note the parse time
3. Close the application
4. Restart application
5. Load same CFF file
6. Load Lua scripts again (same directory)

### Expected Behavior:
- First load: Slower (parses all files)
- Second load: Much faster (uses cache)
- Console shows: "File already cached and up-to-date"

### ✅ Pass Criteria:
- Second load completes in < 5 seconds
- Quest count matches first load
- Data still displays correctly

---

## Test 8: Different Quest Types

### Test Main Quest:
- Select a quest with no parent (root level)
- Should have complete data

### Test Sub-Quest:
- Select a child quest (indented in tree)
- Should show parent quest relationship
- May have less Lua data (inherited from parent)

### Test Quest Chain:
- Select quests 12, 13, 14 (sequential)
- Check if one requires previous quest
- Verify requirement shows in Requirements section

---

## Common Issues and Solutions

### Issue: "No Quest Data Found"
**Cause**: Wrong directory selected  
**Solution**: Select the `script` directory that contains P1, P2, P3 folders

### Issue: cache_loaded=False
**Cause**: Cache not being preloaded  
**Solution**: Check that `preload_cache()` is called in `parse_lua_directory()`

### Issue: Lua data is None
**Cause**: Method name mismatch  
**Solution**: Verify `get_quest_data()` not `get_quest()` is called

### Issue: Debug output doesn't appear
**Cause**: Debug prints removed or suppressed  
**Solution**: Re-add debug output or run with verbose logging

---

## Debug Output Reference

### Good Output (Working):
```
[DEBUG] has_lua_data check: cache_loaded=True, cache_size=335, has_data=True
[DEBUG] Updating quest details for quest ID: 12
[DEBUG] Has Lua data available: True
[DEBUG] Quest Giver - Lua data for quest 12: True
[DEBUG]   NPC ID: 1240, Platform: P1
```

### Bad Output (Not Working):
```
[DEBUG] Lua manager not available
[DEBUG] has_lua_data check: cache_loaded=False, cache_size=0, has_data=False
[DEBUG] Quest Giver - Lua data for quest 12: False
```

---

## Performance Benchmarks

### Expected Performance:
- **First Lua load**: 5-30 seconds (335 quests)
- **Cached load**: < 5 seconds
- **Quest selection**: Instant (< 100ms)
- **Tab switching**: Instant

### Performance Issues:
- If first load > 60 seconds: Check disk speed or file count
- If cached load > 10 seconds: Cache may not be working
- If quest selection slow: Check if loading from DB every time (should use memory cache)

---

## Cleanup

### Remove Debug Output:
Once testing is complete, you may want to remove debug print statements:

**Files with debug output:**
- `src/TirganachReloaded/cff_editor/data_model.py`
- `src/TirganachReloaded/cff_editor/widgets/quest_details_viewer.py`

**Search for**: `[DEBUG]` and remove those print statements

---

## Success Checklist

- [ ] Lua scripts load without crash
- [ ] Console shows "Parsed XXX quests"
- [ ] Cache preloads into memory
- [ ] `has_lua_data()` returns True
- [ ] Quest tree loads automatically
- [ ] Clicking quest shows Lua data
- [ ] `[Lua]` prefixes appear in Quest Details
- [ ] Objectives display correctly
- [ ] Requirements display correctly
- [ ] Rewards display correctly
- [ ] Encoding errors handled gracefully
- [ ] Cache works on second load (fast)
- [ ] No crashes during normal operation

---

**All checks passing? Lua integration is working! 🎉**