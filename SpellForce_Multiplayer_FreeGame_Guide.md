# SpellForce Platinum Edition - Multiplayer & Free Game Guide

## Table of Contents
1. [Overview](#overview)
2. [Game Modes](#game-modes)
3. [RTS Spawn System](#rts-spawn-system)
4. [Co-op Spawn System](#co-op-spawn-system)
5. [Spawn Groups](#spawn-groups)
6. [AI System](#ai-system)
7. [Free Game Quests](#free-game-quests)
8. [Multiplayer Balancing](#multiplayer-balancing)
9. [Creating Free Game Maps](#creating-free-game-maps)
10. [Example Implementations](#example-implementations)

---

## Overview

SpellForce has **three distinct game modes**:
1. **Campaign Mode**: Single-player story with linked maps
2. **Free Game Mode**: Skirmish/RTS maps for single-player or co-op
3. **Multiplayer Mode**: Competitive or co-operative multiplayer

The **Free Game** and **Multiplayer** systems use specialized **RTS spawning mechanics** that differ from campaign quest-based systems.

---

## Game Modes

### Campaign vs Free Game vs Multiplayer

| Feature | Campaign | Free Game (Solo) | Free Game (Co-op) | Multiplayer (PvP) |
|---------|----------|------------------|-------------------|-------------------|
| **Quest System** | ✅ Full quests | ✅ Optional quests | ✅ Shared quests | ❌ No quests |
| **RTS Spawning** | ❌ Manual spawns | ✅ RtsSpawn system | ✅ RtsCoopSpawn | ✅ RtsCoopSpawn |
| **Enemy AI** | ✅ Scripted | ✅ AI clans | ✅ AI clans | ❌ Human players |
| **Persistent State** | ✅ Cross-map | ❌ Single map | ❌ Single map | ❌ Single map |
| **Player Count** | 1 | 1 | 1-4 | 2-4 |
| **Difficulty Scaling** | ❌ Fixed | ✅ By level | ✅ By player count | ❌ Balanced |

---

## RTS Spawn System

### Purpose

The **RTS Spawn System** dynamically spawns enemy units for **Free Game** and **Co-op** modes. It:
- Creates **waves of enemies** over time
- Scales based on **player level** and **number of players**
- Maintains **clan populations** (max units per clan)
- Supports **multi-stage spawn progression**

### Architecture

**Files**:
- `GdsRtsSpawnSystem.lua` - Single-player RTS spawn logic
- `GdsRtsCoopSpawnSystem.lua` - Co-op/multiplayer spawn logic
- `GdsRtsCoopSpawnGroups.lua` - Pre-defined spawn configurations
- `script/P72/ClanRtsSpawnP72.lua` - Map-specific spawn definitions

---

### InitSpawn - Initial Map Population

**Purpose**: Spawn units when the map loads (starting enemies)

**Syntax**:
```lua
InitSpawn
{
    Clan = <clan_id>,          -- Clan number (0-31)
    Groups = {<spawn_groups>}, -- List of spawn group tables
    Conditions = {}            -- Optional conditions to activate
}
```

**Example**:
```lua
-- Define spawn group
Bauplatz1a =
{
    X = 463,                   -- Spawn position
    Y = 409,
    Range = 5,                 -- Random spawn range (square)
    Chief = 0,                 -- Spawn boss NPC ID (0 = none)
    WaitTime = 0,              -- For InitSpawn, always 0
    AvatarMinLevel = 0,        -- Min player level (0 = any)
    AvatarMaxLevel = 0,        -- Max player level (0 = any)
    Conditions = {},           -- Additional spawn conditions
    Units = 
    {
        777, 777, 779, 779, 779  -- Unit IDs to spawn
    },
    ShuffleUnits = FALSE,      -- Randomize spawn order?
}

-- Spawn units at map start
InitSpawn
{
    Clan = 27,                 -- Animal clan
    Groups = {Bauplatz1a, Bauplatz1b, Bauplatz1c},
    Conditions = {}
}
```

**What Gets Spawned**:
- All units in the `Units` table spawn **immediately**
- Each spawn group spawns at its defined coordinates
- Units belong to the specified clan

---

### RtsSpawn - Continuous Spawning

**Purpose**: Continuously spawn units over time (enemy waves)

**Syntax**:
```lua
RtsSpawn
{
    Clan = <clan_id>,
    MaxClanSize = <max_units>,    -- Limit total clan population
    MaxClanLevel = <max_level>,   -- Limit by total clan levels (optional)
    Groups = {<spawn_groups>},
    Conditions = {},
    Effect = <spawn_effect>,      -- Spawn visual effect (optional)
    Length = <effect_duration>    -- Effect duration in ms (optional)
}
```

**Spawn Group Structure**:
```lua
SpawnGroup =
{
    X = <x>,
    Y = <y>,
    Range = <range>,
    Chief = <chief_npc_id>,       -- Only spawn if boss alive
    WaitTime = <seconds>,          -- Delay between spawns
    AvatarMinLevel = <min_level>,  -- Level gating
    AvatarMaxLevel = <max_level>,
    SpawnLimit = <max_spawns>,     -- Max units from this group
                                   -- 0 = unlimited
                                   -- -1 or Once = spawn each unit once
    Conditions = {},               -- Extra conditions
    Units = {<unit_ids>},          -- Unit IDs to spawn (cycles)
    ShuffleUnits = <true/false>    -- Randomize order?
}
```

**Example - Goblin Camp**:
```lua
GoblinWave1 =
{
    X = 100,
    Y = 200,
    Range = 10,
    Chief = 0,
    WaitTime = 60,           -- Spawn every 60 seconds
    AvatarMinLevel = 1,      -- Only spawn for level 1+
    AvatarMaxLevel = 5,      -- Stop at level 6
    SpawnLimit = 0,          -- Unlimited
    Conditions = {},
    Units = {777, 779, 784}, -- Cycles: Goblin1, Goblin2, Goblin3, repeat
    ShuffleUnits = TRUE
}

GoblinWave2 =
{
    X = 120,
    Y = 210,
    Range = 5,
    Chief = 1500,            -- Only spawn if Chief 1500 alive
    WaitTime = 90,
    AvatarMinLevel = 6,      -- Starts at level 6
    AvatarMaxLevel = 10,
    SpawnLimit = 10,         -- Max 10 units
    Conditions = {},
    Units = {838, 265, 267}, -- Stronger goblins
    ShuffleUnits = FALSE
}

RtsSpawn
{
    Clan = 3,               -- Goblin clan
    MaxClanSize = 40,       -- Max 40 units total
    Groups = {GoblinWave1, GoblinWave2},
    Conditions = {}
}
```

**How It Works**:
1. **WaitTime Elapses**: After X seconds, spawn triggers
2. **Check Conditions**:
   - Clan size < MaxClanSize?
   - Avatar level in range?
   - Chief alive (if specified)?
   - Custom conditions met?
3. **Spawn Unit**: Pick next unit from Units list
4. **Cycle**: Return to start of Units list when end reached
5. **Repeat**: Wait WaitTime, spawn again

---

### RtsSpawnNT - Advanced Spawn System

**Purpose**: "New Technology" spawn system with **time-based waves**

**Syntax**:
```lua
RtsSpawnNT
{
    Clan = <clan_id>,
    MaxClanSize = <max_units>,
    X = <spawn_x>,
    Y = <spawn_y>,
    Range = <range>,
    Chief = <chief_id>,
    AvatarMinLevel = <min_level>,
    AvatarMaxLevel = <max_level>,
    Timer = <timer_name>,             -- Global timer name
    Init = {<initial_units>},         -- Units at map start
    SpawnData =
    {
        [<minutes>] = {Minutes = <delay>, Seconds = <delay>, Units = {<unit_ids>}}
    },
    NpcBuildingsExist = {X = <x>, Y = <y>, Range = <range>},  -- Spawn camp
    CampDestroyedActions = {}         -- Actions when camp destroyed
}
```

**Example - Timed Goblin Waves**:
```lua
RtsSpawnNT
{
    Clan = 22,
    MaxClanSize = 30,
    X = 240,
    Y = 146,
    Range = 10,
    Chief = 1800,                    -- Gubble the Chief
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Timer = "GoblinCampTimer",       -- Unique timer name
    Init = {779, 262, 784, 784},     -- 4 starting goblins
    SpawnData =
    {
        -- Format: [minute wave starts] = {delay between spawns, unit types}
        [0]  = {Minutes = 5, Units = {779}},           -- Every 5 min: basic goblin
        [5]  = {Minutes = 3, Units = {779}},           -- Every 3 min: basic goblin
        [10] = {Minutes = 2, Units = {784}},           -- Every 2 min: archer
        [20] = {Minutes = 1.5, Units = {779}},         -- Every 90 sec: basic
        [28] = {Minutes = 1, Units = {266, 22}},       -- Every 60 sec: 2 types
        [36] = {Seconds = 45, Units = {784, 266, 262}}, -- Every 45 sec: 3 types
        [44] = {Seconds = 30, Units = {777}},          -- Every 30 sec: elite
    },
    NpcBuildingsExist = {X = 240, Y = 150, Range = 15},  -- Check for buildings
    CampDestroyedActions = 
    {
        SetGlobalFlagTrue{Name = "GoblinCampDestroyed"}
    }
}
```

**How SpawnData Works**:
- **Key** `[0]`: Wave starts at **0 minutes** (immediately)
- **Key** `[5]`: Wave starts at **5 minutes** (after timer starts)
- **Key** `[10]`: Wave starts at **10 minutes**
- Each wave spawns units at its defined interval
- Multiple waves can run **simultaneously**

**Timer Behavior**:
```lua
-- Timer starts when NpcBuildingsExist condition is met
SetGlobalTimeStamp{Name = "GoblinCampTimer"}

-- Wave 1 triggers at 0 minutes (immediate)
-- Wave 2 triggers at 5 minutes (300 seconds after timer start)
-- Wave 3 triggers at 10 minutes (600 seconds after timer start)
```

**Camp Destruction**:
- If no buildings in range, spawning stops
- `CampDestroyedActions` execute
- Visual effects (GroundWave) removed
- Timer cleared

---

## Co-op Spawn System

### Purpose

The **Co-op Spawn System** adjusts spawning for **multiplayer games**:
- Scales based on **number of players** (2-4)
- Scales based on **skill level** (Easy/Normal/Hard)
- Uses pre-defined **spawn group templates**

### Key Differences from RTS Spawn

| Feature | RtsSpawn (Single) | RtsCoopSpawn (Multi) |
|---------|------------------|----------------------|
| **Player Scaling** | By avatar level | By player count |
| **Difficulty** | Avatar level ranges | Skill presets |
| **Spawn Groups** | Custom defined | Template-based |
| **Max Clan Size** | Fixed | Scaled by multiplier |
| **Initial Units** | Fixed count | Scaled by InitSpawnFactor |

---

### RtsCoopSpawnNT2 - Co-op Spawn

**Syntax**:
```lua
RtsCoopSpawnNT2
{
    Clan = <clan_id>,
    MaxClanSize = <base_size>,      -- Multiplied by MaxClanSizeFactor
    X = <x>,
    Y = <y>,
    Goal = <ai_goal>,               -- GoalCoopAggressive, etc.
    Timer = <timer_name>,
    Init = {<initial_units>},       -- Multiplied by InitSpawnFactor
    SpawnData =
    {
        [<minutes>] = {Minutes = <delay>, Units = {<unit_ids>}}
    },
    NpcBuildingsExist = {X = <x>, Y = <y>, Range = <range>},
    CampDestroyedActions = {}
}
```

**Scaling Factors**:
```lua
-- These are set based on NumPlayers and SkillLevel

InitSpawnFactor = 1.0        -- For 1 player, Easy
InitSpawnFactor = 1.5        -- For 2 players, Normal
InitSpawnFactor = 2.0        -- For 4 players, Hard

MaxClanSizeFactor = 1.0      -- For 1 player
MaxClanSizeFactor = 1.5      -- For 2 players
MaxClanSizeFactor = 2.5      -- For 4 players

SpawnDelayFactor = 1.0       -- Easy difficulty
SpawnDelayFactor = 0.75      -- Normal difficulty
SpawnDelayFactor = 0.5       -- Hard difficulty

BeginWaveFactor = 1.0        -- Easy (waves start as scheduled)
BeginWaveFactor = 0.8        -- Normal (waves start 20% earlier)
BeginWaveFactor = 0.6        -- Hard (waves start 40% earlier)
```

**Example**:
```lua
RtsCoopSpawnNT2
{
    Clan = 10,
    MaxClanSize = 20,        -- Actual: 20 * MaxClanSizeFactor
    X = 300,
    Y = 200,
    Goal = GoalCoopAggressive,
    Timer = "CoopOrcTimer",
    Init = {370, 370, 369},  -- Actual: 3 * InitSpawnFactor units
    SpawnData =
    {
        [5]  = {Minutes = 3, Units = {370}},  -- Delay: 3 * SpawnDelayFactor minutes
        [10] = {Minutes = 2, Units = {369}},  -- Start: 10 * BeginWaveFactor minutes
    },
    NpcBuildingsExist = {X = 300, Y = 200, Range = 20},
    CampDestroyedActions = {}
}
```

**Calculation Example** (4 players, Hard difficulty):
```
InitSpawn:
- Base: 3 units (370, 370, 369)
- Factor: 2.0
- Actual: 6 units spawned

MaxClanSize:
- Base: 20
- Factor: 2.5
- Actual: 50 max units

Wave 1 (starts at 5 minutes):
- Base start: 5 minutes
- BeginWaveFactor: 0.6
- Actual start: 3 minutes

Wave 1 delay:
- Base delay: 3 minutes
- SpawnDelayFactor: 0.5
- Actual delay: 1.5 minutes between spawns
```

---

## Spawn Groups

### Pre-defined Templates

**Location**: `GdsRtsCoopSpawnGroups.lua`

SpellForce includes **30+ pre-configured spawn groups** for common enemy types.

**Structure**:
```lua
return
{
    [<group_id>] = {
        Name = "<group_name>",
        LevelRange = "<level_range>",
        Goal = <ai_goal>,
        MaxClanSize = <max_units>,
        Init = {<initial_units>},
        SpawnData =
        {
            [<minutes>] = {Minutes/Seconds = <delay>, Units = {<units>}}
        }
    }
}
```

---

### Example Templates

#### 1. Random Group (ID 01)
```lua
[01] = {
    Name = "Random",
    LevelRange = "Random",
}
```
**Behavior**: Randomly selects one of the other spawn groups

#### 2. Grim Reaper (ID 02)
```lua
[02] = {
    Name = "Grim Reaper",
    LevelRange = "RIP",           -- Ultra hard
    Goal = GoalCoopAggressive,
    MaxClanSize = 4,
    Init = {788},                 -- 1 Grim Reaper
    SpawnData =
    {
        [3] = {Minutes = 5, Units = {788}}  -- +1 every 5 minutes
    }
}
```
**Purpose**: Boss-level challenge

#### 3. Animal Tiny Spiders (ID 03)
```lua
[03] = {
    Name = "Animal Tiny Spiders",
    LevelRange = "01",            -- Level 1 enemies
    Goal = GoalCoopAggressive,
    MaxClanSize = 80,             -- Lots of weak units
    Init = {750, 750, 750, 750},  -- 4 spiders
    SpawnData =
    {
        [3] = {Seconds = 15, Units = {750}}  -- +1 every 15 seconds
    }
}
```
**Purpose**: Early game swarm

#### 4. Goblin Green Easy (ID 07)
```lua
[07] = {
    Name = "Goblin Green easy 1",
    LevelRange = "01-03",
    Goal = GoalCoopAggressive,
    MaxClanSize = 5,
    Init = {262, 262, 838, 838},
    SpawnData =
    {
        [3] = {Minutes = 2, Units = {784}},
        [5] = {Minutes = 1, Units = {783}}
    }
}
```

#### 5. Demon High (ID 19)
```lua
[19] = {
    Name = "Demon high 1",
    LevelRange = "20 +25",        -- Late game
    Goal = GoalCoopAggressive,
    MaxClanSize = 10,
    Init = {1307, 1306, 186, 185, 185},
    SpawnData =
    {
        [5]  = {Minutes = 2.5, Units = {186}},  -- Fire Elemental
        [10] = {Minutes = 2, Units = {185}},    -- Wave of Fire
        [20] = {Minutes = 1.5, Units = {186}},
        [30] = {Minutes = 1, Units = {185}}
    }
}
```

#### 6. Brannigan's Orcs (ID 31)
```lua
[31] = {
    Name = "Brannigans Orcs medium 1",
    LevelRange = "9 +12",
    Goal = GoalCoopAggressive,
    MaxClanSize = 30,
    Init = {673, 741, 741, 741, 741},
    -- 673 = The Assassin (unique boss)
    -- 741 = Fist Orc warriors
    SpawnData =
    {
        [5]  = {Minutes = 2.5, Units = {740, 741, 742}},
        [10] = {Minutes = 2, Units = {740, 741, 742}},
        [20] = {Minutes = 1.5, Units = {740, 741, 742}},
        [35] = {Minutes = 1, Units = {740, 741, 742}}
    }
}
```

---

### Using Spawn Groups

**In Map Script**:
```lua
-- Load spawn group definitions
local SpawnGroups = doscript("GdsRtsCoopSpawnGroups.lua")

-- Use a specific group
local group = SpawnGroups[07]  -- Goblin Green easy

-- Apply to spawn
RtsCoopSpawnNT2
{
    Clan = 5,
    MaxClanSize = group.MaxClanSize,
    X = 250,
    Y = 300,
    Goal = group.Goal,
    Timer = "SpawnTimer1",
    Init = group.Init,
    SpawnData = group.SpawnData,
    NpcBuildingsExist = {X = 250, Y = 300, Range = 15}
}
```

---

## AI System

### AI Goals

**Location**: `AiFreeGame.lua`

**Aggressive AI**:
```lua
Aggressive =
{
    MinimalHomePointCrew = 5,        -- Min units at base
    MaximalHomePointCrew = 20,       -- Max units at base
    StandbyCrew = 0,                 -- Units on standby
    ScoutGroupSize = 2,              -- Units per scout group
    MaximalNumberScoutGroups = 2,    -- Max scout groups
    Enemy = {Clan = Player},         -- Target player clan
    Range = 256,                     -- Attack range
}
```
**Behavior**: Actively hunts player, sends scouts, attacks in waves

**Defensive AI**:
```lua
Defensive =
{
    MinimalHomePointCrew = 5,
    Enemy = {Clan = Player},
    Range = 64,                      -- Short range = defensive
}
```
**Behavior**: Stays near base, only attacks when player approaches

**Co-op Goals** (from spawn groups):
- `GoalCoopAggressive` - Hunt players
- `GoalCoopDefensive` - Defend spawn point
- `GoalCoopPassive` - Don't attack unless attacked

---

### AI Usage

**In Free Game Maps**:
```lua
-- Define spawn with AI behavior
RtsSpawnNT
{
    Clan = 10,
    MaxClanSize = 30,
    -- ... spawn config ...
}

-- AI is assigned in editor to clan 10
-- Clan 10 follows "Aggressive" or "Defensive" profile
```

**AI Clans**:
- Clans 1-15: Usually reserved for AI enemies
- Clans 16-23: Player/hero clans
- Clans 24-31: Neutral/animal clans

---

## Free Game Quests

### Quest Integration

Free Game maps can include **optional quests** for bonus objectives.

**Differences from Campaign Quests**:

| Feature | Campaign | Free Game |
|---------|----------|-----------|
| **Required** | ✅ Yes | ❌ Optional |
| **Cross-map** | ✅ Yes | ❌ No |
| **Quest Chains** | ✅ Complex | ⚠️ Simple |
| **Rewards** | Story items | Bonus XP/items |
| **State Persistence** | ✅ Saves | ❌ Lost on exit |

---

### Free Game Quest Example

**Objective**: Destroy all enemy spawn camps

```lua
-- In map's n0.lua

-- Track camps destroyed
OnOneTimeEvent
{
    Conditions = {
        IsGlobalFlagTrue{Name = "Camp1Destroyed"},
        IsGlobalFlagTrue{Name = "Camp2Destroyed"},
        IsGlobalFlagTrue{Name = "Camp3Destroyed"}
    },
    Actions = {
        QuestSolve{QuestId = 5000},
        SetRewardFlagTrue{Name = "AllCampsDestroyed"},
        Outcry{
            NpcId = 0,
            String = "All enemy camps destroyed!",
            Color = ColorGreen
        }
    }
}

-- Bonus reward definition
-- In GdsQuestRewards.lua
QuestRewardsFreeGameP72 = 
{
    AllCampsDestroyed = { XP = {500}, Money = {Gold = 20} }
}
```

**Common Free Game Quest Types**:
1. **Survival**: Survive for X minutes
2. **Destruction**: Destroy all enemy buildings
3. **Collection**: Gather X resources
4. **Protection**: Keep NPC/building alive
5. **Speed Run**: Complete within time limit

---

## Multiplayer Balancing

### Difficulty Scaling

**Skill Levels**:
```lua
SkillLevel = SkillEasy    -- Beginner
SkillLevel = SkillNormal  -- Standard
SkillLevel = SkillHard    -- Expert
```

**Player Count**:
```lua
NumPlayers = 1  -- Solo
NumPlayers = 2  -- Duo
NumPlayers = 3  -- Trio
NumPlayers = 4  -- Full squad
```

---

### Balancing Formula

**Total Enemy Strength** = `BaseStrength * PlayerCountFactor * DifficultyFactor`

**Example Calculation**:

| Players | Difficulty | InitSpawnFactor | MaxClanSizeFactor | SpawnDelayFactor |
|---------|-----------|-----------------|-------------------|------------------|
| 1 | Easy | 0.8 | 1.0 | 1.2 |
| 1 | Normal | 1.0 | 1.0 | 1.0 |
| 1 | Hard | 1.2 | 1.2 | 0.8 |
| 2 | Normal | 1.5 | 1.5 | 0.9 |
| 3 | Normal | 1.8 | 2.0 | 0.8 |
| 4 | Normal | 2.0 | 2.5 | 0.7 |
| 4 | Hard | 2.5 | 3.0 | 0.5 |

---

### Hit & Run Protection

**Problem**: Players could kite enemies, killing them one by one without risk.

**Solution**:
```lua
-- In RtsSpawnNT
if SkillLevel == SkillHard or PlatformId >= 100 then
    local size = floor(getn(params.Init) / 2)
    OnPlatformOneTimeEvent
    {
        Conditions = {
            IsGlobalFlagFalse{Name = CampDestroyedVar},
            Negated(IsClanSize{Clan = params.Clan, Size = size}),
        },
        Actions = {
            SetGlobalTimeStamp{Name = params.Timer},  -- START SPAWNING
        }
    }
end
```

**How It Works**:
- If clan size drops below 50% of initial units
- Timer starts automatically
- Spawning begins (reinforcements arrive)
- Prevents cheesing with hit-and-run tactics

---

## Creating Free Game Maps

### Step 1: Create Map Structure

**Directory**: `script/P72/` (P72 = Free Game map ID)

**Required Files**:
1. `n0.lua` - Platform script (can be empty)
2. `ClanRtsSpawnP72.lua` - Spawn definitions
3. `EffectsP72.lua` - Visual effects (optional)

---

### Step 2: Define Spawn Camps

**Create**: `script/P72/ClanRtsSpawnP72.lua`

```lua
-- Define spawn point coordinates
SpawnCamp1 =
{
    X = 100,
    Y = 200,
    Range = 10,
    Chief = 0,
    WaitTime = 60,
    AvatarMinLevel = 1,
    AvatarMaxLevel = 10,
    Conditions = {},
    Units = {777, 779, 784},  -- Goblin unit IDs
    ShuffleUnits = TRUE
}

SpawnCamp2 =
{
    X = 300,
    Y = 400,
    Range = 10,
    Chief = 0,
    WaitTime = 90,
    AvatarMinLevel = 5,
    AvatarMaxLevel = 15,
    Conditions = {},
    Units = {838, 265, 267},  -- Stronger goblins
    ShuffleUnits = FALSE
}

-- Initial spawn (units at map start)
InitSpawn
{
    Clan = 3,
    Groups = {SpawnCamp1},
    Conditions = {}
}

-- Continuous spawn (waves over time)
RtsSpawn
{
    Clan = 3,
    MaxClanSize = 40,
    Groups = {SpawnCamp1, SpawnCamp2},
    Conditions = {}
}
```

---

### Step 3: Add Advanced Waves (Optional)

**Using RtsSpawnNT**:

```lua
RtsSpawnNT
{
    Clan = 5,
    MaxClanSize = 50,
    X = 250,
    Y = 350,
    Range = 15,
    Chief = 0,
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Timer = "OrcCampTimer",
    Init = {370, 370, 369, 369},
    SpawnData =
    {
        [0]  = {Minutes = 3, Units = {370}},      -- Basic orcs from start
        [10] = {Minutes = 2, Units = {370, 369}}, -- Mixed at 10 min
        [20] = {Minutes = 1.5, Units = {369}},    -- Fire orcs at 20 min
        [30] = {Minutes = 1, Units = {376, 377}}  -- Elite orcs at 30 min
    },
    NpcBuildingsExist = {X = 250, Y = 350, Range = 20},
    CampDestroyedActions =
    {
        SetGlobalFlagTrue{Name = "OrcCampDestroyed"},
        SetEffect{Effect = "BuildingFire", X = 250, Y = 350, Length = 5000}
    }
}
```

---

### Step 4: Add Animal Spawns

**Peaceful Animals**:

```lua
-- Deer herd
DeerHerd =
{
    X = 450,
    Y = 100,
    Range = 10,
    Chief = 0,
    WaitTime = 300,  -- 5 minutes between spawns
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Conditions = {},
    Units = {355, 354, 354, 354, 353},  -- Stag, Does, Fawns
    ShuffleUnits = TRUE
}

InitSpawn
{
    Clan = 27,  -- Neutral animal clan
    Groups = {DeerHerd},
    Conditions = {}
}

RtsSpawn
{
    Clan = 27,
    MaxClanSize = 15,
    Groups = {DeerHerd},
    Conditions = {}
}
```

---

### Step 5: Add Co-op Support

**For Multiplayer/Co-op Maps**:

```lua
-- Use Co-op spawn system
RtsCoopSpawnNT2
{
    Clan = 10,
    MaxClanSize = 30,          -- Scales with NumPlayers
    X = 300,
    Y = 300,
    Goal = GoalCoopAggressive,
    Timer = "CoopTimer1",
    Init = {370, 370, 369},    -- Scales with InitSpawnFactor
    SpawnData =
    {
        [5]  = {Minutes = 3, Units = {370}},
        [10] = {Minutes = 2, Units = {369}},
        [20] = {Minutes = 1, Units = {370, 369}}
    },
    NpcBuildingsExist = {X = 300, Y = 300, Range = 20},
    CampDestroyedActions = {}
}
```

---

### Step 6: Add Optional Quests

**Bonus Objectives**:

```lua
-- In n0.lua

-- Quest: Destroy 3 camps
OnOneTimeEvent
{
    Conditions = {
        IsGlobalFlagTrue{Name = "Camp1Destroyed"},
        IsGlobalFlagTrue{Name = "Camp2Destroyed"},
        IsGlobalFlagTrue{Name = "Camp3Destroyed"}
    },
    Actions = {
        QuestSolve{QuestId = 7200},  -- Free game quest ID
        SetRewardFlagTrue{Name = "FreeGameP72AllCamps"},
        Outcry{
            NpcId = 0,
            String = "Bonus objective complete!",
            Color = ColorGold
        }
    }
}

-- Quest: Survive 30 minutes
OnOneTimeEvent
{
    Conditions = {
        IsGlobalTimeElapsed{Name = "MapStartTime", Seconds = 1800}
    },
    Actions = {
        QuestSolve{QuestId = 7201},
        SetRewardFlagTrue{Name = "FreeGameP72Survival"},
        Outcry{
            NpcId = 0,
            String = "Survival bonus achieved!",
            Color = ColorGreen
        }
    }
}
```

---

## Example Implementations

### Example 1: Basic Free Game Map

**Scenario**: Simple goblin survival map

```lua
-- script/P72/ClanRtsSpawnP72.lua

-- Single spawn camp
GoblinCamp =
{
    X = 256,
    Y = 256,
    Range = 15,
    Chief = 0,
    WaitTime = 45,
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Conditions = {},
    Units = {777, 779, 784, 838},
    ShuffleUnits = TRUE
}

-- Spawn 5 goblins at start
InitSpawn
{
    Clan = 3,
    Groups = {GoblinCamp},
    Conditions = {}
}

-- Spawn goblins continuously
RtsSpawn
{
    Clan = 3,
    MaxClanSize = 25,
    Groups = {GoblinCamp},
    Conditions = {}
}
```

---

### Example 2: Multi-Wave Progressive Map

**Scenario**: Increasing difficulty over time

```lua
RtsSpawnNT
{
    Clan = 8,
    MaxClanSize = 60,
    X = 300,
    Y = 200,
    Range = 10,
    Chief = 0,
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Timer = "ProgressiveWaveTimer",
    Init = {262, 262, 262, 262},  -- 4 weak goblins
    SpawnData =
    {
        [0]  = {Minutes = 2, Units = {262}},          -- Weak goblins: every 2 min
        [5]  = {Minutes = 1.5, Units = {784}},        -- Add archers: every 90 sec
        [10] = {Minutes = 1, Units = {838, 784}},     -- Mixed units: every 60 sec
        [20] = {Seconds = 45, Units = {838, 265}},    -- Stronger units: every 45 sec
        [30] = {Seconds = 30, Units = {266, 267}},    -- Elite units: every 30 sec
    },
    NpcBuildingsExist = {X = 300, Y = 200, Range = 15},
    CampDestroyedActions =
    {
        SetGlobalFlagTrue{Name = "ProgressiveCampDestroyed"}
    }
}
```

---

### Example 3: Co-op Demon Boss Fight

**Scenario**: Late-game boss encounter with scaling

```lua
-- Load spawn groups
local SpawnGroups = doscript("GdsRtsCoopSpawnGroups.lua")

-- Use pre-defined Demon High group (ID 19)
local DemonGroup = SpawnGroups[19]

RtsCoopSpawnNT2
{
    Clan = 15,
    MaxClanSize = DemonGroup.MaxClanSize,  -- Scales with player count
    X = 400,
    Y = 400,
    Goal = DemonGroup.Goal,                -- GoalCoopAggressive
    Timer = "DemonBossTimer",
    Init = DemonGroup.Init,                -- Fire Elementals + Wave of Fire
    SpawnData = DemonGroup.SpawnData,      -- Progressive waves
    NpcBuildingsExist = {X = 400, Y = 400, Range = 25},
    CampDestroyedActions =
    {
        SetGlobalFlagTrue{Name = "DemonBossDefeated"},
        QuestSolve{QuestId = 7300},
        SetEffect{Effect = "DemonPortalClose", X = 400, Y = 400, Length = 3000}
    }
}
```

---

### Example 4: Multi-Camp Free Game Map

**Scenario**: Complete map with multiple camps and quest integration

```lua
-- script/P72/ClanRtsSpawnP72.lua

-- NORTH CAMP: Early game goblins
NorthCamp =
{
    X = 150,
    Y = 450,
    Range = 12,
    Chief = 0,
    WaitTime = 60,
    AvatarMinLevel = 1,
    AvatarMaxLevel = 8,
    Conditions = {},
    Units = {262, 779, 784},
    ShuffleUnits = TRUE
}

-- EAST CAMP: Mid-game orcs
EastCamp =
{
    X = 450,
    Y = 250,
    Range = 15,
    Chief = 1500,  -- Orc Chieftain
    WaitTime = 90,
    AvatarMinLevel = 5,
    AvatarMaxLevel = 15,
    Conditions = {},
    Units = {370, 369, 376},
    ShuffleUnits = FALSE
}

-- SOUTH CAMP: Late-game undead
SouthCamp =
{
    X = 250,
    Y = 50,
    Range = 10,
    Chief = 1800,  -- Necromancer
    WaitTime = 120,
    AvatarMinLevel = 10,
    AvatarMaxLevel = 0,
    Conditions = {},
    Units = {407, 408, 409, 410},
    ShuffleUnits = TRUE
}

-- Initial spawns
InitSpawn
{
    Clan = 5,
    Groups = {NorthCamp},
    Conditions = {}
}

InitSpawn
{
    Clan = 7,
    Groups = {EastCamp},
    Conditions = {}
}

InitSpawn
{
    Clan = 9,
    Groups = {SouthCamp},
    Conditions = {}
}

-- Continuous spawning
RtsSpawn
{
    Clan = 5,
    MaxClanSize = 30,
    Groups = {NorthCamp},
    Conditions = {}
}

RtsSpawn
{
    Clan = 7,
    MaxClanSize = 25,
    Groups = {EastCamp},
    Conditions = {}
}

RtsSpawn
{
    Clan = 9,
    MaxClanSize = 20,
    Groups = {SouthCamp},
    Conditions = {}
}

-- Advanced timed spawn (west camp)
RtsSpawnNT
{
    Clan = 11,
    MaxClanSize = 40,
    X = 50,
    Y = 250,
    Range = 20,
    Chief = 0,
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Timer = "WestCampTimer",
    Init = {777, 777, 779, 779, 784},
    SpawnData =
    {
        [0]  = {Minutes = 3, Units = {777}},
        [10] = {Minutes = 2, Units = {779}},
        [20] = {Minutes = 1, Units = {784}},
        [30] = {Seconds = 45, Units = {838, 266}}
    },
    NpcBuildingsExist = {X = 50, Y = 250, Range = 18},
    CampDestroyedActions =
    {
        SetGlobalFlagTrue{Name = "WestCampDestroyed"},
        SetEffect{Effect = "BuildingSmoke", X = 50, Y = 250, Length = 10000}
    }
}
```

**Quest Integration** (in `n0.lua`):

```lua
-- Track all camps destroyed
OnOneTimeEvent
{
    EventName = "AllCampsDestroyed",
    Conditions = 
    {
        IsGlobalFlagTrue{Name = "WestCampDestroyed"},
        IsClanSize{Clan = 5, Size = 0},  -- North camp cleared
        IsClanSize{Clan = 7, Size = 0},  -- East camp cleared
        IsClanSize{Clan = 9, Size = 0}   -- South camp cleared
    },
    Actions = 
    {
        QuestSolve{QuestId = 7200},
        SetRewardFlagTrue{Name = "FreeGameP72Complete"},
        Outcry{
            NpcId = 0,
            String = "Victory! All enemy camps destroyed!",
            Color = ColorGold
        },
        SetEffect{Effect = "FireworkGold", X = 256, Y = 256, Length = 5000}
    }
}

-- Survival bonus quest
OnOneTimeEvent
{
    EventName = "SurvivalBonus",
    Conditions = 
    {
        IsGlobalTimeElapsed{Name = "MapStartTime", Seconds = 1800}  -- 30 minutes
    },
    Actions = 
    {
        QuestSolve{QuestId = 7201},
        SetRewardFlagTrue{Name = "FreeGameP72Survival"},
        Outcry{
            NpcId = 0,
            String = "Survival Bonus: +1000 XP!",
            Color = ColorBlue
        }
    }
}
```

---

### Example 5: Mixed Environment (Animals + Enemies)

**Scenario**: Living ecosystem with neutral and hostile creatures

```lua
-- PEACEFUL ANIMALS
DeerGrove =
{
    X = 100,
    Y = 100,
    Range = 20,
    Chief = 0,
    WaitTime = 300,  -- 5 minutes
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Conditions = {},
    Units = {355, 354, 353},  -- Stag, Doe, Fawn
    ShuffleUnits = TRUE
}

WolfPack =
{
    X = 500,
    Y = 500,
    Range = 15,
    Chief = 0,
    WaitTime = 180,  -- 3 minutes
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Conditions = {},
    Units = {749, 749, 748},  -- Alpha wolf + wolves
    ShuffleUnits = FALSE
}

-- HOSTILE SPIDERS
SpiderNest =
{
    X = 300,
    Y = 300,
    Range = 10,
    Chief = 0,
    WaitTime = 120,  -- 2 minutes
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Conditions = {},
    Units = {750, 750, 751},  -- Tiny spiders + Medium spider
    ShuffleUnits = TRUE
}

-- Spawn peaceful animals
InitSpawn
{
    Clan = 27,  -- Neutral animal clan
    Groups = {DeerGrove},
    Conditions = {}
}

RtsSpawn
{
    Clan = 27,
    MaxClanSize = 12,
    Groups = {DeerGrove},
    Conditions = {}
}

-- Spawn hostile wolves
InitSpawn
{
    Clan = 26,  -- Hostile animal clan
    Groups = {WolfPack},
    Conditions = {}
}

RtsSpawn
{
    Clan = 26,
    MaxClanSize = 8,
    Groups = {WolfPack},
    Conditions = {}
}

-- Spawn spiders
InitSpawn
{
    Clan = 25,
    Groups = {SpiderNest},
    Conditions = {}
}

RtsSpawn
{
    Clan = 25,
    MaxClanSize = 20,  -- Lots of small spiders
    Groups = {SpiderNest},
    Conditions = {}
}
```

---

## Advanced Techniques

### Dynamic Spawn Control

**Conditional Spawning Based on Player Progress**:

```lua
-- Early game spawn
EarlyGameSpawn =
{
    X = 200,
    Y = 200,
    Range = 10,
    Chief = 0,
    WaitTime = 60,
    AvatarMinLevel = 1,
    AvatarMaxLevel = 5,
    Conditions = {},
    Units = {262, 779},
    ShuffleUnits = TRUE
}

-- Mid game spawn (only after flag set)
MidGameSpawn =
{
    X = 200,
    Y = 200,
    Range = 10,
    Chief = 0,
    WaitTime = 45,
    AvatarMinLevel = 6,
    AvatarMaxLevel = 12,
    Conditions = 
    {
        IsGlobalFlagTrue{Name = "FirstBossDefeated"}
    },
    Units = {838, 265, 266},
    ShuffleUnits = TRUE
}

-- Late game spawn (multiple conditions)
LateGameSpawn =
{
    X = 200,
    Y = 200,
    Range = 10,
    Chief = 0,
    WaitTime = 30,
    AvatarMinLevel = 13,
    AvatarMaxLevel = 0,
    Conditions = 
    {
        IsGlobalFlagTrue{Name = "FirstBossDefeated"},
        IsGlobalFlagTrue{Name = "SecondBossDefeated"},
        IsGlobalTimeElapsed{Name = "MapStartTime", Seconds = 1200}  -- 20 minutes
    },
    Units = {267, 268, 269},
    ShuffleUnits = FALSE
}

RtsSpawn
{
    Clan = 10,
    MaxClanSize = 50,
    Groups = {EarlyGameSpawn, MidGameSpawn, LateGameSpawn},
    Conditions = {}
}
```

**How It Works**:
- All groups share same spawn point
- Each group has level gates + custom conditions
- Spawns naturally progress from easy → medium → hard
- Player controls progression by defeating bosses

---

### Boss-Gated Spawning

**Only spawn reinforcements while boss is alive**:

```lua
-- Boss NPC
BossNpcId = 1900  -- Dragon King

-- Elite guard spawn
DragonGuards =
{
    X = 450,
    Y = 450,
    Range = 5,
    Chief = BossNpcId,  -- Only spawn if boss alive
    WaitTime = 45,
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Conditions = {},
    Units = {1901, 1902},  -- Dragon knights
    ShuffleUnits = FALSE
}

-- Minion spawn
DragonMinions =
{
    X = 440,
    Y = 460,
    Range = 10,
    Chief = BossNpcId,  -- Only spawn if boss alive
    WaitTime = 30,
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Conditions = {},
    Units = {1903, 1904, 1905},  -- Lesser dragons
    ShuffleUnits = TRUE
}

RtsSpawn
{
    Clan = 20,
    MaxClanSize = 30,
    Groups = {DragonGuards, DragonMinions},
    Conditions = {}
}

-- In n0.lua: Boss death event
OnOneTimeEvent
{
    Conditions = 
    {
        IsDead{NpcId = BossNpcId}
    },
    Actions = 
    {
        SetGlobalFlagTrue{Name = "DragonKingDefeated"},
        QuestSolve{QuestId = 7400},
        Outcry{
            NpcId = 0,
            String = "The Dragon King has fallen!",
            Color = ColorRed
        }
    }
}
```

**Result**:
- Reinforcements spawn continuously during fight
- When boss dies, all spawning stops immediately
- Remaining enemies can be mopped up
- Prevents endless reinforcements

---

### Area-Based Spawning

**Spawn different enemy types in different map regions**:

```lua
-- NORTH REGION: Goblin territory
NorthSpawn1 = {X = 100, Y = 450, Range = 10, Chief = 0, WaitTime = 60, 
               AvatarMinLevel = 0, AvatarMaxLevel = 0, Conditions = {},
               Units = {777, 779, 784}, ShuffleUnits = TRUE}
NorthSpawn2 = {X = 200, Y = 480, Range = 10, Chief = 0, WaitTime = 60,
               AvatarMinLevel = 0, AvatarMaxLevel = 0, Conditions = {},
               Units = {838, 262, 266}, ShuffleUnits = TRUE}

-- EAST REGION: Orc territory
EastSpawn1 = {X = 450, Y = 300, Range = 12, Chief = 0, WaitTime = 90,
              AvatarMinLevel = 0, AvatarMaxLevel = 0, Conditions = {},
              Units = {370, 369, 376}, ShuffleUnits = FALSE}
EastSpawn2 = {X = 480, Y = 200, Range = 12, Chief = 0, WaitTime = 90,
              AvatarMinLevel = 0, AvatarMaxLevel = 0, Conditions = {},
              Units = {377, 378, 379}, ShuffleUnits = FALSE}

-- SOUTH REGION: Undead territory
SouthSpawn1 = {X = 300, Y = 50, Range = 8, Chief = 0, WaitTime = 120,
               AvatarMinLevel = 0, AvatarMaxLevel = 0, Conditions = {},
               Units = {407, 408, 409}, ShuffleUnits = TRUE}
SouthSpawn2 = {X = 200, Y = 80, Range = 8, Chief = 0, WaitTime = 120,
               AvatarMinLevel = 0, AvatarMaxLevel = 0, Conditions = {},
               Units = {410, 411, 412}, ShuffleUnits = TRUE}

-- WEST REGION: Mixed monsters
WestSpawn1 = {X = 50, Y = 250, Range = 15, Chief = 0, WaitTime = 75,
              AvatarMinLevel = 0, AvatarMaxLevel = 0, Conditions = {},
              Units = {750, 751, 749, 748}, ShuffleUnits = TRUE}

-- SEPARATE CLANS PER REGION
RtsSpawn{Clan = 5, MaxClanSize = 30, Groups = {NorthSpawn1, NorthSpawn2}, Conditions = {}}
RtsSpawn{Clan = 7, MaxClanSize = 25, Groups = {EastSpawn1, EastSpawn2}, Conditions = {}}
RtsSpawn{Clan = 9, MaxClanSize = 20, Groups = {SouthSpawn1, SouthSpawn2}, Conditions = {}}
RtsSpawn{Clan = 11, MaxClanSize = 15, Groups = {WestSpawn1}, Conditions = {}}
```

**Advantages**:
- Each region has unique enemy composition
- Separate clan limits prevent one area overwhelming others
- Creates varied gameplay across map
- Players can choose which region to tackle first

---

### Wave Survival Mode

**Escalating waves with breaks**:

```lua
RtsSpawnNT
{
    Clan = 15,
    MaxClanSize = 100,
    X = 256,
    Y = 256,
    Range = 30,
    Chief = 0,
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Timer = "SurvivalWaveTimer",
    Init = {262, 262, 779, 779},  -- Starting wave
    SpawnData =
    {
        -- Wave 1: Goblins (0-3 min)
        [0] = {Seconds = 15, Units = {262, 779, 784}},
        
        -- Break (3-5 min): No spawns
        
        -- Wave 2: Orcs (5-10 min)
        [5] = {Seconds = 20, Units = {370, 369, 376}},
        
        -- Break (10-12 min)
        
        -- Wave 3: Mixed (12-20 min)
        [12] = {Seconds = 15, Units = {838, 377, 751}},
        
        -- Break (20-22 min)
        
        -- Wave 4: Elite (22-30 min)
        [22] = {Seconds = 10, Units = {267, 378, 410}},
        
        -- Wave 5: Boss rush (30+ min)
        [30] = {Seconds = 5, Units = {788, 1307, 1500}}  -- All bosses!
    },
    NpcBuildingsExist = {X = 256, Y = 256, Range = 5},
    CampDestroyedActions = {}
}

-- Victory condition: Survive wave 5 for 5 minutes
OnOneTimeEvent
{
    Conditions = 
    {
        IsGlobalTimeElapsed{Name = "SurvivalWaveTimer", Seconds = 2100}  -- 35 minutes
    },
    Actions = 
    {
        QuestSolve{QuestId = 7500},
        SetGlobalFlagTrue{Name = "SurvivalVictory"},
        Outcry{
            NpcId = 0,
            String = "VICTORY! You have survived the onslaught!",
            Color = ColorGold
        }
    }
}
```

---

## Performance Optimization

### Spawn Limits

**Problem**: Too many units cause lag

**Solution**: Careful MaxClanSize tuning

```lua
-- BAD: Can spawn 200+ units
RtsSpawn
{
    Clan = 5,
    MaxClanSize = 200,  -- Way too high!
    Groups = {Spawn1, Spawn2, Spawn3, Spawn4, Spawn5},
    Conditions = {}
}

-- GOOD: Reasonable limits
RtsSpawn
{
    Clan = 5,
    MaxClanSize = 40,  -- Manageable
    Groups = {Spawn1, Spawn2, Spawn3, Spawn4, Spawn5},
    Conditions = {}
}
```

**Recommended Limits**:
- Weak enemies (goblins, spiders): 30-50
- Medium enemies (orcs, undead): 20-30
- Strong enemies (trolls, demons): 10-20
- Boss-tier enemies: 5-10

---

### Spawn Timing

**Problem**: All groups spawn simultaneously, causing lag spikes

**Solution**: Stagger WaitTime values

```lua
-- BAD: All spawn at same time
Spawn1 = {..., WaitTime = 60, ...}
Spawn2 = {..., WaitTime = 60, ...}
Spawn3 = {..., WaitTime = 60, ...}

-- GOOD: Staggered timing
Spawn1 = {..., WaitTime = 60, ...}
Spawn2 = {..., WaitTime = 65, ...}  -- +5 seconds offset
Spawn3 = {..., WaitTime = 70, ...}  -- +10 seconds offset
```

---

### Conditional Spawning

**Problem**: Map full of enemies from the start

**Solution**: Level-gate spawns

```lua
-- Only spawn harder enemies when player is ready
WeakSpawn  = {..., AvatarMinLevel = 1,  AvatarMaxLevel = 5,  ...}
MediumSpawn = {..., AvatarMinLevel = 6,  AvatarMaxLevel = 12, ...}
StrongSpawn = {..., AvatarMinLevel = 13, AvatarMaxLevel = 0,  ...}
```

---

## Troubleshooting

### Common Issues

#### 1. **Spawns not appearing**

**Symptoms**: No enemies spawn at designated points

**Possible Causes**:
- Incorrect coordinates (X/Y outside map bounds)
- Clan ID conflicts (clan already used elsewhere)
- MaxClanSize already reached
- Avatar level outside range
- Conditions not met

**Debug**:
```lua
-- Add debug output
print("DEBUG: Spawning clan " .. params.Clan .. " at " .. params.X .. "," .. params.Y)

-- Check if conditions are met
if IsGlobalFlagTrue{Name = "SomeFlag"} then
    print("DEBUG: Flag is TRUE")
else
    print("DEBUG: Flag is FALSE - spawn blocked!")
end
```

---

#### 2. **Too many enemies**

**Symptoms**: Map is flooded with units, game lags

**Causes**:
- MaxClanSize too high
- Too many spawn groups per clan
- WaitTime too short
- Multiple clans spawning same unit types

**Fix**:
```lua
-- Reduce MaxClanSize
MaxClanSize = 30  -- Instead of 100

-- Increase WaitTime
WaitTime = 90  -- Instead of 30

-- Add SpawnLimit
SpawnLimit = 20  -- Max 20 units from this group
```

---

#### 3. **Spawning stops prematurely**

**Symptoms**: Enemies stop spawning after a while

**Causes**:
- Chief NPC died (if Chief parameter used)
- AvatarMaxLevel exceeded
- SpawnLimit reached
- Camp buildings destroyed (for RtsSpawnNT)

**Fix**:
```lua
-- Remove Chief restriction
Chief = 0  -- Instead of specific NPC ID

-- Remove level cap
AvatarMaxLevel = 0  -- Instead of specific level

-- Remove spawn limit
SpawnLimit = 0  -- Instead of fixed number

-- Check building condition
NpcBuildingsExist = {X = x, Y = y, Range = large_range}  -- Bigger range
```

---

#### 4. **Co-op scaling not working**

**Symptoms**: Multiplayer difficulty same as single-player

**Causes**:
- Using RtsSpawn instead of RtsCoopSpawnNT2
- Scaling factors not configured
- NumPlayers not set correctly

**Fix**:
```lua
-- Use correct spawn function
RtsCoopSpawnNT2  -- NOT RtsSpawn or RtsSpawnNT
{
    -- ... params ...
}

-- Verify in n0.lua
NumPlayers = GetNumPlayers()  -- Make sure this is called
SkillLevel = GetSkillLevel()
```

---

#### 5. **Quest not completing**

**Symptoms**: Quest objectives met but quest doesn't solve

**Causes**:
- Wrong quest ID
- Flag names don't match
- Event already triggered (not OneTimeEvent)
- Conditions not fully met

**Debug**:
```lua
-- Add debug outcry
OnOneTimeEvent
{
    Conditions = 
    {
        IsGlobalFlagTrue{Name = "Camp1Destroyed"},
        IsGlobalFlagTrue{Name = "Camp2Destroyed"}
    },
    Actions = 
    {
        Outcry{NpcId = 0, String = "DEBUG: Quest conditions met!", Color = ColorYellow},
        QuestSolve{QuestId = 7200},
        -- ... rest ...
    }
}
```

---

## Best Practices

### 1. **Use Descriptive Names**

```lua
-- BAD
Spawn1 = {X = 100, Y = 200, ...}
Spawn2 = {X = 300, Y = 400, ...}

-- GOOD
GoblinCampNorth = {X = 100, Y = 200, ...}
OrcFortressEast = {X = 300, Y = 400, ...}
```

---

### 2. **Comment Your Code**

```lua
-- NORTH REGION: Early game goblin camps
-- Players encounter these first, designed for levels 1-5
GoblinCampNorth =
{
    X = 150,
    Y = 450,
    Range = 12,
    Chief = 0,
    WaitTime = 60,  -- 1 minute between spawns
    AvatarMinLevel = 1,
    AvatarMaxLevel = 5,
    Conditions = {},
    Units = {777, 779, 784},  -- Basic goblins + archers
    ShuffleUnits = TRUE
}
```

---

### 3. **Test Incrementally**

```lua
-- Start simple
RtsSpawn
{
    Clan = 5,
    MaxClanSize = 10,  -- Small number for testing
    Groups = {TestSpawn1},
    Conditions = {}
}

-- Once working, expand
RtsSpawn
{
    Clan = 5,
    MaxClanSize = 40,  -- Production value
    Groups = {Spawn1, Spawn2, Spawn3},
    Conditions = {}
}
```

---

### 4. **Balance Difficulty Curves**

```lua
-- Progression: Weak → Medium → Strong
EarlyGame  = {WaitTime = 90,  MaxClanSize = 30, Units = {weak_ids}}
MidGame    = {WaitTime = 60,  MaxClanSize = 25, Units = {medium_ids}}
LateGame   = {WaitTime = 45,  MaxClanSize = 20, Units = {strong_ids}}
EndGame    = {WaitTime = 30,  MaxClanSize = 15, Units = {elite_ids}}
```

---

### 5. **Provide Player Feedback**

```lua
-- Notify player of significant events
CampDestroyedActions =
{
    SetGlobalFlagTrue{Name = "CampDestroyed"},
    Outcry{
        NpcId = 0,
        String = "Enemy camp destroyed! Reinforcements stopped.",
        Color = ColorGreen
    },
    SetEffect{Effect = "BuildingFire", X = x, Y = y, Length = 5000}
}
```

---

## Appendix A: Unit ID Reference

### Common Enemy Units

**Goblins** (Levels 1-5):
- 262: Goblin Warrior
- 777: Goblin Elite
- 779: Goblin Scout
- 784: Goblin Archer
- 838: Goblin Shaman

**Orcs** (Levels 5-12):
- 369: Fire Orc
- 370: Orc Warrior
- 376: Orc Blade Master
- 377: Orc Spearman
- 378: Orc Brute

**Undead** (Levels 10-18):
- 407: Skeleton Warrior
- 408: Skeleton Archer
- 409: Skeleton Mage
- 410: Wraith
- 411: Death Knight
- 412: Bone Horror

**Animals** (Levels 1-8):
- 353: Fawn (peaceful)
- 354: Doe (peaceful)
- 355: Stag (peaceful)
- 748: Wolf
- 749: Alpha Wolf
- 750: Tiny Spider
- 751: Medium Spider

**Demons** (Levels 15-25):
- 185: Wave of Fire
- 186: Fire Elemental
- 1306: Demon Guard
- 1307: Demon Lord

**Bosses**:
- 788: Grim Reaper
- 1500: Gubble (Goblin Chief)
- 1800: Orc Warlord
- 1900: Dragon King

*(Note: This is a partial list. Full unit IDs available in game data files)*

---

## Appendix B: Clan Assignment Guide

**Recommended Clan Usage**:

| Clan Range | Purpose | Example |
|------------|---------|---------|
| 1-5 | Primary AI enemies | Goblin clans |
| 6-10 | Secondary AI enemies | Orc clans |
| 11-15 | Tertiary AI enemies | Undead, demon clans |
| 16-20 | Player/Hero clans | Player units, heroes |
| 21-23 | Allied NPC clans | Friendly NPCs |
| 24-27 | Neutral animals | Wildlife |
| 28-31 | Hostile animals | Monsters |

---

## Appendix C: Spawn Template Library

Quick-reference spawn templates for copy-paste:

### Basic Spawn (Single Group)
```lua
BasicSpawn =
{
    X = 0,
    Y = 0,
    Range = 10,
    Chief = 0,
    WaitTime = 60,
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Conditions = {},
    Units = {0},
    ShuffleUnits = FALSE
}

InitSpawn{Clan = 0, Groups = {BasicSpawn}, Conditions = {}}
RtsSpawn{Clan = 0, MaxClanSize = 30, Groups = {BasicSpawn}, Conditions = {}}
```

### Timed Wave Spawn
```lua
RtsSpawnNT
{
    Clan = 0,
    MaxClanSize = 40,
    X = 0,
    Y = 0,
    Range = 10,
    Chief = 0,
    AvatarMinLevel = 0,
    AvatarMaxLevel = 0,
    Timer = "TimerName",
    Init = {0, 0, 0},
    SpawnData =
    {
        [0]  = {Minutes = 3, Units = {0}},
        [10] = {Minutes = 2, Units = {0}},
        [20] = {Minutes = 1, Units = {0}}
    },
    NpcBuildingsExist = {X = 0, Y = 0, Range = 15},
    CampDestroyedActions = {SetGlobalFlagTrue{Name = "CampDestroyed"}}
}
```

### Co-op Spawn
```lua
RtsCoopSpawnNT2
{
    Clan = 0,
    MaxClanSize = 30,
    X = 0,
    Y = 0,
    Goal = GoalCoopAggressive,
    Timer = "CoopTimer",
    Init = {0, 0, 0},
    SpawnData =
    {
        [5]  = {Minutes = 3, Units = {0}},
        [10] = {Minutes = 2, Units = {0}}
    },
    NpcBuildingsExist = {X = 0, Y = 0, Range = 15},
    CampDestroyedActions = {}
}
```

---

## Conclusion

The SpellForce RTS spawn system is a **powerful and flexible** framework for creating dynamic enemy encounters in Free Game and Multiplayer modes.

**Key Takeaways**:

1. **Three Spawn Systems**:
   - `InitSpawn`: Initial map population
   - `RtsSpawn`: Basic continuous spawning
   - `RtsSpawnNT`: Advanced timed waves
   - `RtsCoopSpawnNT2`: Multiplayer scaling

2. **Scaling Mechanisms**:
   - Avatar level ranges (single-player)
   - Player count + difficulty (co-op)
   - Progressive waves over time

3. **Best Practices**:
   - Start simple, test incrementally
   - Use descriptive names and comments
   - Balance difficulty curves
   - Optimize spawn limits and timing
   - Provide player feedback

4. **Advanced Techniques**:
   - Boss-gated spawning
   - Area-based enemy distribution
   - Conditional dynamic spawning
   - Wave survival modes

With this system, you can create compelling Free Game maps ranging from simple skirmishes to complex multi-stage battles with dynamic difficulty scaling.

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Author**: SpellForce Community Documentation Project