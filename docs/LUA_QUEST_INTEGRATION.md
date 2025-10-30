# Lua Quest Integration Guide

## Overview

The CFF Editor now supports loading quest data from Lua scripts to provide complete quest information including objectives, requirements, and rewards that are not stored in the CFF file.

## Why Lua Integration?

SpellForce quest data is split between two sources:

### CFF File Contains:
- ✅ Quest hierarchy (parent-child relationships)
- ✅ Quest names and descriptions (localized text)
- ✅ Quest IDs and text references
- ✅ Basic quest structure
- ✅ Dialogue text strings

### Lua Scripts Contain:
- ✅ Quest objectives (Kill X enemies, Collect Y items)
- ✅ Quest requirements (Level, previous quests)
- ✅ Quest rewards (XP, Gold, Items)
- ✅ Quest giver NPC assignments
- ✅ Dialogue branching logic and player choices
- ✅ Quest state management and triggers

## Usage Instructions

### Step 1: Load Your CFF File
First, open your SpellForce CFF file as usual:
1. Go to **File → Open CFF...**
2. Select your `GameData.cff` or modded CFF file
3. Wait for it to load

### Step 2: Load Lua Quest Scripts
Once your CFF is loaded:
1. Go to **Tools → Load Lua Quest Scripts...**
2. Navigate to your SpellForce Lua scripts directory
   - **Typical path**: `OriginalGameFiles/modding/Original Scripts/script/`
   - This directory should contain subdirectories like `P1`, `P2`, `P3`, etc.
3. Click **Select Folder**
4. Wait for the parser to load the quest data

You'll see a confirmation message showing how many quests were parsed.

### Step 3: View Quest Data in Quest Editor
Now when you use the Quest Editor:
1. Go to **Tools → Quest Editor** (or press `Ctrl+Q, E`)
2. Browse quests in the **Quest Hierarchy** tab
3. Select any quest
4. Switch to the **Quest Details** tab

Quest data from Lua scripts will be displayed with a `[Lua]` prefix.

## What Information is Available

### Quest Objectives
The Quest Details viewer will show objectives parsed from Lua scripts, including:
- **Objective Type**: Kill, Collect, Talk, Escort, etc.
- **Target**: What enemy, item, or NPC is involved
- **Count**: How many are required
- **Description**: Human-readable objective text

Example:
```
[Lua] Defeat 5 Goblins (Type: Kill) - Target: Goblin - Count: 5
```

### Quest Requirements
Requirements to accept the quest:
- **Level Requirements**: Minimum player level
- **Previous Quests**: Which quests must be completed first
- **Item Requirements**: What items the player must have
- **Custom Conditions**: Any special Lua conditions

Example:
```
[Lua] Player must be level 10 or higher (Type: Level) - Value: 10
[Lua] Complete Quest 42 first (Type: Quest) - Value: 42
```

### Quest Rewards
Rewards given upon quest completion:
- **Experience Points**: XP gained
- **Gold/Silver/Copper**: Money rewards
- **Items**: Item IDs of rewards
- **Flags**: Game flags set on completion

Example:
```
XP: 500 XP [from Lua]
Money: 5 Gold, 10 Silver, 0 Copper [from Lua]
Items: [Lua] Item ID: 626 (Simple Metal Helmet)
```

### Quest Giver Information
- **NPC ID**: Which NPC gives the quest
- **Platform**: Which map/region the quest is in (P1 = Liannon, P2 = Eloni, etc.)

## File Structure

The Lua quest parser looks for:

### Quest Reward Files
- `GdsQuestRewards.lua` - Contains reward definitions for all quests
- Example structure:
  ```lua
  QuestRewardsP1 = {
      QuestName = { XP = {25}, Items = {626}, Money = {Gold = 1, Silver = 2} }
  }
  ```

### Quest Logic Files
- `P1/n0.lua`, `P2/n0.lua`, etc. - Main quest logic per map
- Contains `OnOneTimeEvent` blocks with quest conditions and actions
- Example patterns:
  ```lua
  OnOneTimeEvent {
      Conditions = {
          QuestState{QuestId = 12, State = StateActive},
          FigureIsDead{NpcId = 1234}
      },
      Actions = {
          QuestSolve{QuestId = 12}
      }
  }
  ```

## Caching

The Lua parser uses SQLite caching for performance:
- **Cache Location**: `~/.spellforce_editor/lua_cache/lua_quest_cache.db`
- **Auto-Update**: Files are automatically reparsed if modified
- **Force Refresh**: Use the `force_refresh` option if data seems stale

## Troubleshooting

### "No Quest Data Found"
**Problem**: Parser couldn't find any quest data in the selected directory.

**Solutions**:
1. Make sure you selected the `script` directory, not a parent directory
2. Verify the directory contains subdirectories like `P1`, `P2`, `P3`
3. Check that the Lua files are readable (not corrupted)

### "Lua Data Manager Not Available"
**Problem**: The Lua parser module is not installed or has an import error.

**Solutions**:
1. Check that `lua_parser` module exists in `cff_editor/`
2. Verify all dependencies are installed
3. Check console for detailed error messages

### Quest Shows No Lua Data
**Problem**: Quest is displayed but no `[Lua]` tags appear.

**Possible Reasons**:
1. The quest data genuinely isn't in the Lua files (some quests are script-less)
2. The quest ID in CFF doesn't match the ID in Lua scripts
3. The Lua parser couldn't extract the data (complex/unusual Lua patterns)

**Solutions**:
- Check the original Lua files manually to verify the data exists
- Report unusual Lua patterns for parser improvement

### Performance Issues
**Problem**: Loading Lua scripts takes a long time.

**Notes**:
- First-time parsing will take longer (builds cache)
- Subsequent loads should be fast (uses cache)
- You only need to load Lua data once per session
- Cache persists between editor sessions

## Data Model Integration

For developers working on the editor:

### Checking if Lua Data is Available
```python
if data_model.has_lua_data():
    # Lua quest data is loaded
    quest_data = data_model.get_lua_quest_data(quest_id)
```

### Getting Quest Data
```python
lua_quest = data_model.get_lua_quest_data(42)
if lua_quest:
    print(f"Objectives: {len(lua_quest.objectives)}")
    print(f"XP Reward: {lua_quest.rewards.xp}")
```

### Listing All Quests with Lua Data
```python
quest_ids = data_model.get_all_lua_quest_ids()
print(f"Found Lua data for {len(quest_ids)} quests")
```

## Platform IDs (Map Names)

| Platform ID | Map Name |
|-------------|----------|
| P1 | Liannon |
| P2 | Eloni |
| P3 | Leafshade |
| P4 | (varies) |
| P5 | Shiel |
| P7 | Greyfell |
| P63 | (varies) |

## Future Enhancements

Planned features:
- [ ] Bidirectional editing (modify Lua from editor)
- [ ] Generate new quest Lua scripts
- [ ] Quest template library
- [ ] Advanced dialogue tree visualization
- [ ] Quest dependency graph
- [ ] Quest state machine editor

## Support

If you encounter issues:
1. Check this documentation
2. Review the console output for error messages
3. Verify your Lua files are from a valid SpellForce installation
4. Report bugs with example Lua files that fail to parse

---

**Last Updated**: 2024
**Version**: 1.0
**Compatibility**: SpellForce: Conquest of Eo / SpellForce 3