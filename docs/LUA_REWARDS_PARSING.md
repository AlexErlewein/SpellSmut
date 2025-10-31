# Lua Quest Rewards Parsing - Technical Guide

## Overview

SpellForce quest rewards are stored in a separate file (`GdsQuestRewards.lua`) and indexed by **quest name**, not quest ID. This creates a challenge for matching rewards to quests loaded from the CFF.

## The Problem

### What We Expected
Quest data all in one place with quest IDs:
```lua
Quest[12] = {
    name = "Find Darius",
    rewards = { XP = 25, Gold = 5 }
}
```

### What SpellForce Actually Has

**File 1: Quest Logic (`P1/n0.lua`, etc.)**
```lua
-- Quest state management by ID
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

**File 2: Rewards (`GdsQuestRewards.lua`)**
```lua
-- Rewards indexed by quest NAME, not ID!
QuestRewardsP1 = {
    DariusDerKarthograph = { XP = {25} },
    WegNachEloni1Snarf = { XP = {25}, Items = {626} },
    KleineFische1 = { XP = {10} },
}
```

**The Challenge**: We have quest ID 12, but the rewards file only has quest names like "DariusDerKarthograph". There's no direct mapping!

## Current Implementation

### What's Been Improved

1. **Better Objective Extraction** ✅
   - Parse `FigureIsDead` conditions → Kill objectives
   - Parse `PlayerHasItem` conditions → Collect objectives  
   - Parse `FigureIsInRange` conditions → Reach location objectives

2. **GdsQuestRewards Parser** ✅
   - New dedicated parser for the rewards file
   - Extracts XP, Gold, Silver, Copper, Items
   - Groups by platform (P1, P2, P3, etc.)

3. **Map Names** ✅
   - Platform IDs now show human-readable names
   - Example: `P1` → `Liannon (P1)`

### How Reward Matching Works (Fuzzy)

Since we can't directly match quest IDs to reward names, we use **fuzzy matching**:

```python
# Try to find quest by searching for reward name in quest description
SELECT quest_id FROM lua_quests 
WHERE platform = 'P1' 
AND (quest_name LIKE '%DariusDerKarthograph%' 
     OR description LIKE '%DariusDerKarthograph%')
```

**This means**:
- ✅ Some quests will match and show rewards
- ⚠️ Some quests won't match (name doesn't appear in description)
- ❌ Quest rewards that don't match will show as 0

## What You'll See Now

### Objectives Section
After reloading Lua scripts, you should see:

```
Objectives:
[Lua] Defeat NPC 1234 (Type: Kill) - Target: NPC 1234
[Lua] Collect item 2336 (Type: Collect) - Target: 2336 - Count: 1
[Lua] Reach Portal (Type: Reach) - Target: Portal
```

### Rewards Section (When Match Found)
```
XP Reward: 25 XP [from Lua]
Money: 5 Gold, 10 Silver, 0 Copper [from Lua]
Items:
  [Lua] Item ID: 626
```

### Location/Platform
```
Location/Map: Liannon (P1) [from Lua]
```

### When No Match Found
```
XP Reward: 0 XP
Money: 0 Gold, 0 Silver, 0 Copper
Items: No item rewards (check Lua scripts)
```

## Testing the Improvements

### Step 1: Clear Old Cache
```bash
# Remove old cached data
rm -rf src/TirganachReloaded/data/cache/lua_cache/lua_quest_cache.db
```

### Step 2: Reload Lua Scripts
1. Start the application
2. Load your CFF file
3. Go to `Tools → Load Lua Quest Scripts...`
4. Select the script directory
5. Wait for parsing

### Step 3: Check Console Output
You should see:
```
Found XXX Lua files in /path/to/script
Parsing: n0.lua
Parsing: GdsQuestRewards.lua
Parsing GdsQuestRewards.lua for reward data...
  Parsed rewards from GdsQuestRewards.lua
Parsed 335 quests from Lua files
Preloading 335 quests into memory...
✓ Preloaded 335 quests
```

**Key line**: `Parsing GdsQuestRewards.lua for reward data...`

### Step 4: View Quest Details
1. Open Quest Editor
2. Select different quests
3. Check Quest Details tab
4. Look for:
   - Objectives with `[Lua]` prefix
   - XP rewards > 0
   - Map names (not just P1, P2)

### Step 5: Database Verification
Check what's actually in the database:

```bash
cd SpellSmut
python3 << 'EOF'
import sqlite3

db = "./src/TirganachReloaded/data/cache/lua_cache/lua_quest_cache.db"
conn = sqlite3.connect(db)
cursor = conn.cursor()

# Check objectives
cursor.execute("SELECT COUNT(*) FROM quest_objectives")
print(f"Objectives: {cursor.fetchone()[0]}")

# Check rewards with actual data
cursor.execute("SELECT COUNT(*) FROM quest_rewards WHERE xp > 0")
print(f"Rewards with XP: {cursor.fetchone()[0]}")

# Sample rewards
cursor.execute("SELECT quest_id, xp, gold, items FROM quest_rewards WHERE xp > 0 LIMIT 5")
print("\nSample rewards:")
for row in cursor.fetchall():
    print(f"  Quest {row[0]}: {row[1]} XP, {row[2]} Gold, Items: {row[3]}")

conn.close()
EOF
```

**Expected**:
- Objectives: > 0 (should have many)
- Rewards with XP: > 0 (at least some)

## Known Limitations

### 1. Reward Matching is Approximate
**Problem**: Quest names in rewards file don't always appear in quest descriptions.

**Example**:
- Reward key: `"WegNachEloni1Snarf"`
- Quest description: "Travel to Eloni"
- Match: ❌ (name doesn't appear in description)

**Impact**: Some quests will show 0 rewards even though they exist in `GdsQuestRewards.lua`

### 2. No Direct Quest Name in CFF
**Problem**: CFF file doesn't store the internal quest names used in Lua.

**Why**: Quest names in CFF are localized text IDs, not the Lua variable names.

### 3. Objectives are Condition-Based
**Problem**: We parse conditions that solve the quest, but some objectives might be optional or have complex logic.

**Example**:
```lua
-- Quest has 3 paths to completion
Conditions = {
    OR {
        FigureIsDead{NpcId = 1234},  -- Path 1
        PlayerHasItem{ItemId = 999},  -- Path 2
        FlagIsTrue{Name = "Sneaked"}  -- Path 3
    }
}
```

We'll extract all three as objectives, but player only needs one.

## Improvement Ideas

### Short Term (Feasible)
1. **Better Name Matching**
   - Use edit distance (Levenshtein)
   - Match on quest description keywords
   - Match on quest giver NPC

2. **Manual Mapping File**
   - Create `quest_id_to_name.json` mapping
   - Users can contribute mappings
   - Load this as first-class data

3. **Parse Quest Comments**
   - Many Lua files have comments like `-- Quest: Way to Eloni`
   - Extract these and use for matching

### Long Term (Complex)
1. **Full Lua Execution**
   - Actually run the Lua (in sandbox)
   - Track which rewards get assigned
   - Map through game state

2. **CFF Enhancement**
   - Modify CFF to store Lua quest name
   - Requires understanding CFF format deeply

3. **AI-Based Matching**
   - Use LLM to match quest descriptions to reward names
   - Would require API calls

## Reward File Format Reference

### Structure
```lua
-- Rewards grouped by platform
QuestRewardsP1 = {
    QuestName1 = { XP = {25} },
    QuestName2 = { XP = {50}, Items = {626, 707} },
    QuestName3 = { 
        XP = {100}, 
        Money = {Gold = 5, Silver = 10, Copper = 25},
        Items = {3352}
    },
}

QuestRewardsP2 = {
    -- ... more quests
}
```

### Reward Types
- **XP**: `XP = {value}` or `XP = value`
- **Money**: `Money = {Gold = x, Silver = y, Copper = z}`
- **Items**: `Items = {id1, id2, id3}`
- **Flags**: `Flags = {name1, name2}` (rarely used)

### Platform Codes
- P1 = Liannon
- P2 = Eloni
- P3 = Leafshade
- P5 = Shiel
- P7 = Greyfell
- P63 = Greyfell (alternate)

## Troubleshooting

### No Objectives Show Up
**Check**:
1. Lua files were actually parsed
2. Console shows "Parsing: n0.lua" etc.
3. Database has objectives: `SELECT COUNT(*) FROM quest_objectives`

**If count is 0**:
- The regex patterns might not match the Lua format
- Check actual Lua file format vs our patterns

### All Rewards Show 0
**Check**:
1. `GdsQuestRewards.lua` was found and parsed
2. Console shows "Parsing GdsQuestRewards.lua for reward data..."
3. Database has rewards: `SELECT COUNT(*) FROM quest_rewards WHERE xp > 0`

**If rewards exist in DB but not showing**:
- Check quest ID being queried
- Check if `get_lua_quest_data()` is being called
- Check debug output in console

### Map Names Don't Show
**Check**:
- Platform field is populated in database
- `get_platform_name()` method exists
- Platform code is in `PLATFORM_NAMES` dictionary

## Success Metrics

✅ **Good State**:
- Objectives count: > 50
- Rewards with XP: > 100  
- Quest details show `[Lua]` prefixed data
- Map names displayed (not just codes)

⚠️ **Partial Success**:
- Objectives count: 10-50
- Rewards with XP: 10-100
- Some quests show data, others don't

❌ **Not Working**:
- Objectives count: 0
- Rewards with XP: 0
- No `[Lua]` tags in UI

## Next Steps

1. **Test with real data** - See what percentage of quests match
2. **Build manual mapping** - Create quest_id_to_name.json for unmapped quests
3. **Improve regex patterns** - Handle more Lua formats
4. **Add statistics** - Show match rate in UI

---

**Remember**: This is a best-effort system. SpellForce's architecture makes perfect matching impossible without game files or manual mapping data.