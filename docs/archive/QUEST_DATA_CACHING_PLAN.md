# Quest Data Caching & Lua Path Update Plan

## Overview
Implement caching for quest data similar to CFF caching, and update default Lua script location to `ModdingTools/SpellForceLUASources`.

---

## ✅ Completed Changes

### 1. Quest Data Service Caching
**File**: `src/TirganachReloaded/cff_editor/services/quest_data_service.py`

#### Added Features:
- **Pickle-based caching** (similar to CFF cache)
- **Cache directory**: `src/TirganachReloaded/data/cache/quest_data/`
- **Cache files**:
  - `quest_data_cache.pkl` - Serialized quest data
  - `cache_timestamp.txt` - Cache creation timestamp
- **Cache validity**: 24 hours (configurable)

#### New Methods:
```python
def _load_from_cache(self):
    """Load quest data from cache if available and valid"""
    # Checks cache age (24 hours)
    # Loads pickled data
    # Returns True if successful

def _save_to_cache(self):
    """Save quest data to cache"""
    # Saves all quest data to pickle file
    # Saves timestamp

def rebuild_cache(self, force: bool = True):
    """Rebuild the quest data cache"""
    # Clears existing cache
    # Reloads all data
    # Pre-caches common quests (379-393)
    # Saves to disk

def clear_cache(self):
    """Clear all cached data (in-memory and disk)"""
    # Clears memory cache
    # Deletes cache files
```

#### Cache Behavior:
1. **On initialization**: Automatically loads from cache if available and valid
2. **Cache expiry**: After 24 hours, cache is considered stale
3. **Automatic rebuild**: If cache is missing or expired, data is loaded fresh
4. **Manual rebuild**: Can be triggered via `rebuild_cache()` method

---

## 🔄 Pending Changes

### 2. Update Default Lua Script Path
**Current**: `OriginalGameFiles/modding/Original Scripts/`  
**New**: `ModdingTools/SpellForceLUASources/`

#### Files to Update:

1. **Quest Data Service** ✅ (Already uses project root, no hardcoded paths)
   - `src/TirganachReloaded/cff_editor/services/quest_data_service.py`
   - Loads from: `quest_descriptions_complete.json` (project root)
   - No changes needed

2. **Spell Browser Dialog** ⏳
   - `src/TirganachReloaded/cff_editor/widgets/spell_browser_dialog.py`
   - Line 198: Update path
   ```python
   # OLD:
   script_path = Path(__file__).parent.parent.parent.parent.parent / "OriginalGameFiles" / "modding" / "Original Scripts" / "script" / "sql_spellline.lua"
   
   # NEW:
   script_path = Path(__file__).parent.parent.parent.parent.parent / "ModdingTools" / "SpellForceLUASources" / "script" / "sql_spellline.lua"
   ```

3. **Spell Loader** ⏳
   - `src/TirganachReloaded/cff_editor/widgets/spell_loader.py`
   - Line 11: Update path
   ```python
   # OLD:
   self.game_script_path = Path(__file__).parent.parent.parent.parent.parent / "OriginalGameFiles" / "modding" / "Original Scripts" / "script" / "sql_spellline.lua"
   
   # NEW:
   self.game_script_path = Path(__file__).parent.parent.parent.parent.parent / "ModdingTools" / "SpellForceLUASources" / "script" / "sql_spellline.lua"
   ```

4. **Lua Data Manager** ⏳
   - `src/TirganachReloaded/cff_editor/lua_parser/lua_data_manager.py`
   - Check if there are any hardcoded paths
   - Update default directory parameter if needed

5. **Data Model** ⏳
   - `src/TirganachReloaded/cff_editor/data_model.py`
   - Check `set_lua_quest_directory()` method
   - Update any default path references

---

## 📋 Implementation Steps

### Step 1: Update Spell Browser & Loader ⏳
```bash
# Update both files to use new path
ModdingTools/SpellForceLUASources/script/sql_spellline.lua
```

### Step 2: Update Lua Data Manager ⏳
- Check for hardcoded paths
- Update default directory
- Ensure compatibility with new structure

### Step 3: Update Data Model ⏳
- Set default Lua directory to new path
- Update any path resolution logic

### Step 4: Update Extraction Scripts ⏳
- `extract_quest_descriptions.py`
- `extract_map_and_descriptions.py`
- Update to use new Lua source directory

### Step 5: Test Cache System ✅
- Start app → Cache should be created
- Restart app → Cache should be loaded (fast startup)
- After 24 hours → Cache should rebuild
- Manual rebuild → `quest_service.rebuild_cache()`

---

## 🎯 Benefits

### Caching Benefits:
1. **Faster startup** - No need to parse JSON files every time
2. **Reduced I/O** - Data loaded from memory-efficient pickle format
3. **Automatic refresh** - 24-hour expiry ensures data stays current
4. **Manual control** - Can force rebuild when needed
5. **Similar to CFF** - Consistent caching strategy across app

### Path Update Benefits:
1. **Better organization** - Modding tools separate from original files
2. **More complete data** - SpellForceLUASources has full Lua scripts
3. **Easier maintenance** - Single source of truth for Lua scripts
4. **Consistent with extraction** - Same path used in our quest extraction

---

## 🧪 Testing Checklist

- [ ] Cache is created on first run
- [ ] Cache is loaded on subsequent runs (check console output)
- [ ] Cache expires after 24 hours
- [ ] Manual cache rebuild works
- [ ] Cache clear works
- [ ] Quest data loads correctly from cache
- [ ] All Lua paths point to ModdingTools/SpellForceLUASources
- [ ] Spell browser still works with new path
- [ ] Quest extraction scripts work with new path

---

## 📁 Cache File Structure

```
src/TirganachReloaded/data/cache/quest_data/
├── quest_data_cache.pkl          # Pickled quest data
└── cache_timestamp.txt           # Human-readable timestamp
```

### Cache Contents:
```python
{
    'descriptions': {...},  # quest_descriptions_complete.json data
    'maps': {...},          # quest_maps_and_descriptions.json data
    'rewards': {...},       # quest rewards data
    'merged': {...},        # Pre-merged EnhancedQuestData objects
    'timestamp': '2025-11-02T13:45:00'
}
```

---

## 🔧 Usage Examples

### In Code:
```python
# Initialize with caching (default)
service = QuestDataService(project_root)

# Initialize without caching
service = QuestDataService(project_root, use_cache=False)

# Rebuild cache manually
service.rebuild_cache()

# Clear cache
service.clear_cache()
```

### Console Output:
```
[INFO] Loaded quest data from cache (14 quests)
[INFO] Quest data cache expired, will reload
[INFO] Rebuilding quest data cache...
[INFO] Cache rebuilt with 14 quests
[INFO] Saved quest data to cache
[INFO] Quest data cache cleared
```

---

*Plan created: 2025-11-02*  
*Status: Caching implemented ✅, Path updates pending ⏳*
