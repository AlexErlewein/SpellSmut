# Loading Lua Quest Scripts Guide

## Overview

Quest data is split between two locations:
- **CFF File**: Quest structure, names, descriptions (database)
- **Lua Scripts**: Quest logic, objectives, rewards, requirements (game scripts)

This guide explains how to load and cache Lua quest scripts so you can see complete quest information.

## Architecture

```
┌─────────────────────┐
│   CFF File          │  ← Quest structure
│   (GameData.cff)    │     (loaded automatically)
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ Quest IDs:   │
    │ 1001, 1002.. │
    └──────┬───────┘
           │
           ├─────────────────┐
           ▼                 ▼
┌─────────────────┐   ┌─────────────────┐
│  Lua Scripts    │   │  Lua Cache DB   │
│  quest_*.lua    │──▶│  (SQLite)       │
└─────────────────┘   └────────┬────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Quest Details View  │
                    │  (Merged Data)       │
                    └──────────────────────┘
```

## Where Are Lua Scripts?

Lua quest scripts are typically located in:

```
SpellForce Game Directory/
├── Scripts/
│   ├── Quests/
│   │   ├── quest_1001.lua
│   │   ├── quest_1002.lua
│   │   └── ...
│   ├── P7/           ← Platform-specific quests
│   ├── P8/
│   └── ...
└── Data/
    └── GameData.cff  ← We load this
```

**Common Locations:**
- `C:\Program Files (x86)\SpellForce\Scripts\Quests\`
- `C:\Steam\steamapps\common\SpellForce\Scripts\Quests\`
- Custom mod directories

## How It Works

### 1. Parse Lua Scripts Once

The `LuaDataManager` parses all Lua quest files and extracts:
- Quest objectives (Kill, Collect, Talk, Reach)
- Quest requirements (Level, previous quests)
- Quest rewards (XP, Gold, Items)
- Quest giver NPC ID
- Dialogue references

### 2. Store in Database

Parsed data is stored in SQLite database:
- Location: `~/.spellforce_editor/lua_cache/lua_quest_cache.db`
- Tables: `lua_quests`, `quest_objectives`, `quest_requirements`, `quest_rewards`, `quest_dialogues`
- Indexed by quest ID for fast lookup

### 3. Cache in Memory

Frequently accessed quests are cached in memory for instant access.

### 4. Merge with CFF Data

When viewing a quest:
- CFF provides: Name, description, hierarchy
- Lua cache provides: Objectives, rewards, requirements
- Combined view shows complete quest information

## Using the Lua Data Manager

### Basic Usage

```python
from TirganachReloaded.cff_editor.lua_parser import (
    get_lua_data_manager,
    parse_lua_scripts,
    get_quest_lua_data
)

# Parse Lua scripts directory
lua_dir = "/path/to/SpellForce/Scripts/Quests"
quests_parsed = parse_lua_scripts(lua_dir)
print(f"Parsed {quests_parsed} quests")

# Get quest data
quest_data = get_quest_lua_data(1001)
if quest_data:
    print(f"Quest: {quest_data.quest_name}")
    print(f"Objectives: {len(quest_data.objectives)}")
    print(f"Rewards: {quest_data.rewards.xp} XP")
```

### From Python Script

```python
from TirganachReloaded.cff_editor.lua_parser import LuaDataManager
from pathlib import Path

# Create manager
manager = LuaDataManager()

# Parse directory
lua_dir = Path("/path/to/SpellForce/Scripts/Quests")
manager.parse_lua_directory(lua_dir, force_refresh=False)

# Get quest data
quest = manager.get_quest_data(1001)
if quest:
    for obj in quest.objectives:
        print(f"- {obj.description} ({obj.objective_type})")
```

### Refresh Cache

```python
manager = get_lua_data_manager()

# Force reparse (when Lua files are updated)
manager.parse_lua_directory(lua_dir, force_refresh=True)

# Or clear and rebuild
manager.clear_cache()
manager.parse_lua_directory(lua_dir)
```

## Integrating with Quest Details Viewer

The Quest Details viewer can automatically load Lua data:

```python
# In quest_details_viewer.py
from TirganachReloaded.cff_editor.lua_parser import get_quest_lua_data

def update_quest_details(self):
    quest = self.current_quest
    quest_id = getattr(quest, "quest_id", None)
    
    # Try to get Lua data
    lua_data = get_quest_lua_data(quest_id)
    
    if lua_data:
        # Update objectives
        for obj in lua_data.objectives:
            item = QTreeWidgetItem([
                obj.description,
                obj.objective_type,
                obj.target or "-",
                str(obj.count)
            ])
            self.objectives_tree.addTopLevelItem(item)
        
        # Update rewards
        self.xp_reward_label.setText(f"{lua_data.rewards.xp} XP")
        self.money_reward_label.setText(
            f"{lua_data.rewards.gold} Gold, "
            f"{lua_data.rewards.silver} Silver, "
            f"{lua_data.rewards.copper} Copper"
        )
        
        # Update requirements
        for req in lua_data.requirements:
            self.requirements_list.addItem(req.description)
```

## Cache Management

### Check Cache Status

```python
manager = get_lua_data_manager()

# Get statistics
stats = manager.get_cache_stats()
print(f"Cached quests: {stats['total_quests']}")
print(f"Objectives: {stats['total_objectives']}")
print(f"Requirements: {stats['total_requirements']}")

# Check if specific quest is cached
has_data = manager.has_quest_data(1001)
print(f"Quest 1001 cached: {has_data}")

# Get all cached quest IDs
quest_ids = manager.get_all_quest_ids()
print(f"Cached quest IDs: {quest_ids}")
```

### Preload Cache

```python
# Preload all quests into memory for fast access
manager.preload_cache()
```

### Clear Cache

```python
# Clear all cached data
manager.clear_cache()
```

## Setup Instructions

### Step 1: Locate Lua Scripts

Find your SpellForce installation directory and locate the Scripts folder.

**Windows:**
```
C:\Program Files (x86)\SpellForce\Scripts\Quests\
C:\Steam\steamapps\common\SpellForce\Scripts\Quests\
```

**Mac/Linux (Wine):**
```
~/.wine/drive_c/Program Files/SpellForce/Scripts/Quests/
```

### Step 2: Parse Scripts

```python
from TirganachReloaded.cff_editor.lua_parser import parse_lua_scripts

# Point to your Lua scripts directory
lua_dir = "C:/Program Files (x86)/SpellForce/Scripts/Quests"

# Parse all scripts
count = parse_lua_scripts(lua_dir)
print(f"Parsed {count} quests")
```

### Step 3: Verify Cache

```python
from TirganachReloaded.cff_editor.lua_parser import get_lua_data_manager

manager = get_lua_data_manager()
stats = manager.get_cache_stats()

print(f"Quests cached: {stats['total_quests']}")
print(f"Objectives: {stats['total_objectives']}")
print(f"Requirements: {stats['total_requirements']}")
```

## File Naming Conventions

The parser looks for Lua files with these patterns:

- `quest_<ID>.lua` - Single quest file (e.g., `quest_1001.lua`)
- `quest_*.lua` - Any file starting with "quest_"
- `*.lua` - All Lua files (will parse and look for quests inside)

## What Gets Parsed

### From Lua Scripts:

✅ **Quest Objectives:**
- Kill objectives: `FigureIsDead{Tag = "Enemy"}`
- Collect objectives: `PlayerHasItem{ItemId = 100, Amount = 5}`
- Reach objectives: `FigureIsInRange{Tag = "Location"}`

✅ **Quest Requirements:**
- Level requirements: `AvatarLevel{Level = 10}`
- Quest prerequisites: `QuestState{QuestId = 1000, State = StateSolved}`

✅ **Quest Rewards:**
- XP, Gold, Silver, Copper
- Item rewards (by ID)
- Flags set on completion

✅ **Quest Metadata:**
- Quest giver NPC ID
- Platform/map
- Quest events

### Not Parsed (Complex Logic):

❌ Complex conditional logic
❌ Custom Lua functions
❌ Advanced state machines
❌ Dynamic quest generation

For complex quests, use the raw Lua file directly.

## Troubleshooting

### Problem: No quests found after parsing

**Check:**
1. Lua directory path is correct
2. Directory contains `.lua` files
3. Lua files contain quest scripts (have `QuestId = ` patterns)
4. Files are readable

**Solution:**
```python
from pathlib import Path
lua_dir = Path("/your/path")
print(f"Directory exists: {lua_dir.exists()}")
print(f"Lua files: {list(lua_dir.glob('*.lua'))}")
```

### Problem: Quest data incomplete

**Reason:** Parser extracts common patterns. Complex or non-standard Lua may not parse fully.

**Solution:** 
- Check the actual Lua file to see its structure
- Use `quest.init_event` and `quest.complete_event` for raw Lua
- Manually edit generated quests for complex logic

### Problem: Cache is stale

**Solution:**
```python
# Force refresh
manager.parse_lua_directory(lua_dir, force_refresh=True)
```

### Problem: Quest ID mismatch

**Check:** Quest IDs in Lua match Quest IDs in CFF.

```python
# Compare CFF quests vs Lua quests
cff_quest_ids = [q.quest_id for q in cff_data.get_elements('quests')]
lua_quest_ids = manager.get_all_quest_ids()

missing_in_lua = set(cff_quest_ids) - set(lua_quest_ids)
print(f"Quests in CFF but not in Lua: {missing_in_lua}")
```

## Performance

### Initial Parse
- ~1000 quests: 5-10 seconds
- Creates SQLite database
- Subsequent loads are instant

### Cache Lookup
- Database lookup: ~1-2ms per quest
- Memory cache: <0.1ms per quest
- Preloading recommended for large quest sets

### Memory Usage
- ~1KB per quest in memory
- ~5KB per quest in database
- 1000 quests ≈ 5MB database

## Best Practices

### 1. Parse Once, Use Many Times

```python
# On first run or when Lua files change
if not manager.has_quest_data(1001):
    manager.parse_lua_directory(lua_dir)

# All subsequent uses are instant
quest = manager.get_quest_data(1001)
```

### 2. Preload for Bulk Operations

```python
# Before displaying many quests
manager.preload_cache()

# Now all lookups are instant
for quest_id in quest_ids:
    quest = manager.get_quest_data(quest_id)
```

### 3. Refresh Periodically

```python
# Check if Lua directory was modified
last_parse = manager.get_metadata("last_parse_time")
current_mtime = Path(lua_dir).stat().st_mtime

if not last_parse or float(last_parse) < current_mtime:
    manager.parse_lua_directory(lua_dir, force_refresh=True)
```

### 4. Handle Missing Data Gracefully

```python
quest = manager.get_quest_data(quest_id)
if quest:
    # Use Lua data
    for obj in quest.objectives:
        print(obj.description)
else:
    # Fallback to CFF-only data
    print("No Lua data available for this quest")
```

## Integration Checklist

- [ ] Locate SpellForce Lua scripts directory
- [ ] Parse scripts using `parse_lua_scripts()`
- [ ] Verify cache with `get_cache_stats()`
- [ ] Update Quest Details viewer to load Lua data
- [ ] Test with known quest IDs
- [ ] Add refresh button to UI
- [ ] Handle quests without Lua data
- [ ] Document Lua directory path for users

## Future Enhancements

Planned features:
- [ ] Automatic Lua directory detection
- [ ] Watch Lua files for changes
- [ ] Incremental parsing (only changed files)
- [ ] Export cached data to JSON
- [ ] Lua script validation
- [ ] Missing quest detection (CFF vs Lua)

## Related Documentation

- [Lua Quest Parser](LUA_QUEST_PARSER.md) - Parser API and usage
- [Quest Editor Tabs](QUEST_EDITOR_TABS.md) - Quest Creator integration
- [Quest Data Structure](../tests/quest_hierarchy/README.md) - CFF vs Lua comparison

## Support

For questions about Lua script loading:
1. Check cache stats to verify parsing
2. Examine Lua files directly for structure
3. Use test scripts to verify parser
4. Check SpellForce modding documentation

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Maintainer:** SpellForce CFF Editor Team