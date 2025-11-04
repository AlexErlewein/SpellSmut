# Quest Viewer - Current Status

## ✅ Fixed Issues

### Quest Names Now Loading from CFF Data
- **Problem**: Quest names were not displaying in the tree view
- **Root Cause**: The code was trying to access `quest_info.get('name')` but the actual structure has names in `quest_info['attributes']['name']`
- **Solution**: Updated `simple_quest_viewer.py:load_cff_quest_data()` to correctly access the attributes dictionary

### Test Results
```
✅ Loaded 14 quests from CFF data

📋 Sample quest names:
  Quest 379: Amra and Lea
  Quest 380: Talk to Sunder in Liannon about Amra's armor
  Quest 381: Ask Shan Muir about Arma and Lea
  Quest 382: Examine the events by the house of the Muir family in Liannon.
  Quest 383: A search of the aggressors should deliver further information.
  ...
```

## 📊 Current Data Sources

### CFF Quest Data
- **Location**: `src/TirganachReloaded/data/cff_quest_data.json`
- **Quests**: 14 quests with full information
- **Has**: Quest names, descriptions, parent relationships, hierarchies
- **Status**: ✅ Working correctly

### Lua Cache Data
- **Location**: `src/TirganachReloaded/data/cache/lua_quest_cache.db`
- **Quests**: 998 quests
- **Has**: Quest structure, objectives, requirements, rewards, dialogues
- **Missing**: **Actual quest names** (only has generic "Quest 1", "Quest 12", etc.)
- **Status**: ⚠️ Partially working

## 🔍 Remaining Issue

### Generic Names in Lua Cache
The 998 quests from the Lua cache have generic names like "Quest 1", "Quest 12", etc. because:
1. The Lua parser doesn't extract quest names from the script files
2. Quest names are likely stored in separate string tables or CFF files
3. Need to find the mapping between quest IDs and actual quest names

### Where Quest Names Might Be
- CFF string tables (checked: `cff_strings_german.json` - contains UI strings)
- Separate quest name mapping files
- Within the Lua scripts themselves (needs enhanced parser)
- In the game's string table files

## 🎯 Current Functionality

### What Works
- ✅ Quest viewer launches successfully
- ✅ 14 CFF quests display with proper names
- ✅ Quest hierarchy (parent-child relationships)
- ✅ Quest details panel shows comprehensive information
- ✅ Tree view with expand/collapse functionality
- ✅ Quest selection updates details panel

### What Needs Improvement
- ⚠️ 998 Lua cache quests show generic names
- ⚠️ Need to find/create quest name mappings for Lua quests

## 🚀 How to Run

```bash
# Launch the quest viewer
uv run python simple_quest_viewer.py

# With debug output
uv run python simple_quest_viewer.py --debug

# Test the fix
python3 test_final.py
```

## 📝 Code Changes Made

### File: `simple_quest_viewer.py`

**Lines 167-182** - Fixed CFF quest data loading:
```python
# OLD CODE (broken):
self.quest_data[quest_id].update({
    'id': quest_id,
    'name': quest_info.get('name', f'Quest {quest_id}'),  # ❌ Wrong path
    ...
})

# NEW CODE (working):
attributes = quest_info.get('attributes', {})
self.quest_data[quest_id].update({
    'id': quest_id,
    'name': attributes.get('name', f'Quest {quest_id}'),  # ✅ Correct path
    ...
})
```

## 🎯 Next Steps

To fully complete the quest viewer with proper names for all quests:

1. **Find Quest Name Source**
   - Search for string table files that map quest IDs to names
   - Check if Lua scripts contain quest names that can be parsed
   - Look for additional CFF files with quest metadata

2. **Enhance Lua Parser**
   - Update `quest_lua_parser.py` to extract quest names if they exist in scripts
   - Add support for parsing quest string references

3. **Create Name Mappings**
   - If names are scattered, create a consolidated mapping file
   - Map quest IDs from Lua cache to their display names

4. **Integrate Mappings**
   - Update `load_lua_quest_data()` to use the name mappings
   - Merge CFF and Lua data more intelligently

## 📊 Summary

- **Total Quests**: 1012 (14 from CFF + 998 from Lua cache)
- **With Proper Names**: 14 (1.4%)
- **With Generic Names**: 998 (98.6%)
- **Quest Viewer**: ✅ Functional and working
- **User Experience**: ⚠️ Needs quest name mappings for full usability
