# SpellForce Platinum Edition - Quest & Campaign Creation Guide

## Table of Contents
1. [Overview](#overview)
2. [Quest System Architecture](#quest-system-architecture)
3. [Map Structure](#map-structure)
4. [Creating Your First Quest](#creating-your-first-quest)
5. [Event System](#event-system)
6. [NPC Scripting](#npc-scripting)
7. [Dialog System](#dialog-system)
8. [Quest Rewards](#quest-rewards)
9. [Creating a Campaign](#creating-a-campaign)
10. [Advanced Quest Techniques](#advanced-quest-techniques)
11. [Reference API](#reference-api)
12. [Complete Examples](#complete-examples)

---

## Overview

SpellForce uses a **Lua-based event system** for quests and campaigns:

- **Event-driven**: Quests trigger when conditions are met
- **State machines**: NPCs have behavior scripts
- **Modular design**: Each map has separate script files
- **Global persistence**: Flags and states carry across maps

### Key Concepts

1. **Platforms**: Individual maps (e.g., P7 = "Ice Gate")
2. **NPCs**: Numbered entities with unique IDs
3. **Events**: Condition → Action pairs
4. **States**: Global game progression markers
5. **Flags**: Boolean variables for quest tracking

---

## Quest System Architecture

### File Structure

```
script/
├── GdsActions.lua              # Action functions (Goto, Spawn, etc.)
├── GdsConditions.lua           # Condition functions (FigureAlive, etc.)
├── GdsQuestRewards.lua         # Quest reward definitions
├── GdsDialogSystem.lua         # Dialog framework
├── GdsBase.lua                 # Core scripting engine
├── GdsHelper.lua               # Utility functions
└── P7/                         # Map-specific scripts (Platform 7)
    ├── n0.lua                  # Platform script (main map logic)
    ├── n5059.lua               # NPC 5059's behavior script
    ├── n4009.lua               # NPC 4009's behavior script
    ├── ClanRtsSpawnP7.lua      # Enemy spawning
    ├── EffectsP7.lua           # Visual effects
    └── Ai.lua                  # AI definitions
```

### Quest Flow

```
Map Load → Platform Init → NPC Scripts Load → Events Register → Player Actions → Conditions Check → Actions Execute
```

---

## Map Structure

### Creating a New Map (Platform)

**Step 1: Create Map Directory**

```
script/P999/              # P999 = Your custom map ID
```

**Step 2: Required Files**

```
script/P999/
├── n0.lua                # Main platform script (required)
├── ClanRtsSpawnP999.lua  # Enemy spawns (optional)
├── EffectsP999.lua       # Custom effects (optional)
└── Ai.lua                # AI behavior (optional)
```

### Platform Script (n0.lua)

**Basic Template**:

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
    BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)
    
    -- Your quest code goes here
    
    EndDefinition()
end
```

**What it does**:
- `BeginDefinition()`: Initializes the script context
- Your code: Defines events, quests, spawns
- `EndDefinition()`: Finalizes the script

---

## Creating Your First Quest

### Quest Structure

Every quest needs:
1. **Quest ID**: Unique number (e.g., 1000)
2. **Start Trigger**: When quest begins
3. **Objectives**: What player must do
4. **Completion Check**: When quest is solved
5. **Reward**: XP, items, gold

---

### Example: Simple Fetch Quest

**Quest**: "Bring me 3 wolf pelts"

**File**: `script/P999/n0.lua`

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- ====================================
-- Quest: Hunter's Request
-- QuestId: 1000
-- ====================================

-- STEP 1: Start quest when player talks to hunter NPC
OnOneTimeEvent
{
    EventName = "QuestHunterStart",
    Conditions = 
    {
        -- Quest giver dialog completed (set in dialog script)
        IsGlobalFlagTrue{Name = "HunterDialogComplete"},
        -- Quest not already active
        Negated(QuestState{QuestId = 1000, State = StateActive}),
    },
    Actions = 
    {
        -- Activate the quest
        QuestBegin{QuestId = 1000},
        -- Give player journal entry
        Outcry{
            NpcId = 0,  -- 0 = Avatar
            String = "I need to collect 3 wolf pelts for the hunter.",
            Color = ColorYellow
        },
    }
}

-- STEP 2: Check if player has collected items
OnOneTimeEvent
{
    EventName = "QuestHunterItemsCollected",
    Conditions = 
    {
        -- Quest is active
        QuestState{QuestId = 1000, State = StateActive},
        -- Player has 3 wolf pelts (ItemId = 2500)
        PlayerHasItem{ItemId = 2500, Amount = 3},
    },
    Actions = 
    {
        -- Set flag to enable quest completion dialog
        SetGlobalFlagTrue{Name = "HunterQuestItemsReady"},
        -- Notify player
        Outcry{
            NpcId = 0,
            String = "I have collected the wolf pelts! I should return to the hunter.",
            Color = ColorGreen
        },
    }
}

-- STEP 3: Complete quest when player returns to NPC
OnOneTimeEvent
{
    EventName = "QuestHunterComplete",
    Conditions = 
    {
        -- Quest is active
        QuestState{QuestId = 1000, State = StateActive},
        -- Player has items
        IsGlobalFlagTrue{Name = "HunterQuestItemsReady"},
        -- Player talked to hunter again (dialog flag)
        IsGlobalFlagTrue{Name = "HunterTurnInComplete"},
    },
    Actions = 
    {
        -- Mark quest as solved
        QuestSolve{QuestId = 1000},
        -- Remove items from inventory
        PlayerRemoveItem{ItemId = 2500, Amount = 3},
        -- Give rewards (defined in GdsQuestRewards.lua)
        SetRewardFlagTrue{Name = "QuestHunterReward"},
        -- Congratulations message
        Outcry{
            NpcId = 5100,  -- Hunter NPC
            String = "Thank you! Here's your reward.",
            Color = ColorWhite
        },
    }
}

EndDefinition()
end
```

**Rewards File**: `script/GdsQuestRewards.lua`

Add to appropriate map rewards:

```lua
QuestRewardsP999 = 
{
    QuestHunterReward = { XP = {100}, Money = {Gold = 5}, Items = {600} },
    -- Items = {600} gives item ID 600 as reward
}
```

---

### Quest IDs Organization

**Campaign Quests**: 1-999
**Map-Specific Quests**: 1000+

**Recommended Structure**:
```
1000-1099: Main quests for your map
1100-1199: Side quests
1200-1299: Collection quests
1300-1399: Kill quests
```

---

## Event System

### Event Types

SpellForce has three event types:

#### 1. **OnOneTimeEvent** - Triggers once, never again

```lua
OnOneTimeEvent
{
    EventName = "FirstTimeEnterArea",  -- Optional name for debugging
    Conditions = 
    {
        -- Conditions that must all be true
        FigureInRange{NpcId = 0, X = 100, Y = 200, Range = 10},
        IsGlobalFlagFalse{Name = "AreaDiscovered"},
    },
    Actions = 
    {
        -- Actions to execute when conditions met
        SetGlobalFlagTrue{Name = "AreaDiscovered"},
        Outcry{NpcId = 0, String = "I discovered a new area!", Color = ColorGreen},
    }
}
```

**Use Cases**:
- Starting quests
- Triggering cutscenes
- One-time events
- Quest completion

---

#### 2. **OnEvent** - Triggers repeatedly while conditions are true

```lua
OnEvent
{
    EventName = "PlayerNearDanger",
    Conditions = 
    {
        FigureInRange{NpcId = 0, X = 150, Y = 150, Range = 20},
    },
    Actions = 
    {
        -- This will trigger every frame conditions are true!
        -- Use sparingly, prefer OnToggleEvent
        SetGlobalFlagTrue{Name = "InDangerZone"},
    }
}
```

**Warning**: Can cause performance issues. Use `OnToggleEvent` instead.

---

#### 3. **OnToggleEvent** - Toggles between two states

```lua
OnToggleEvent
{
    EventName = "TorchSystem",
    OnConditions = 
    {
        -- Conditions to turn ON
        TimeTorchOn(),  -- Night time (18:00-23:59)
    },
    OnActions = 
    {
        -- Actions when turning ON
        SetEffect{Effect = "TorchFire", X = 100, Y = 100, Length = 0},
        SetGlobalFlagTrue{Name = "TorchesLit"},
    },
    OffConditions = 
    {
        -- Conditions to turn OFF
        TimeTorchOff(),  -- Day time (04:15-18:00)
    },
    OffActions = 
    {
        -- Actions when turning OFF
        RemoveEffect{X = 100, Y = 100},
        SetGlobalFlagFalse{Name = "TorchesLit"},
    },
}
```

**Use Cases**:
- Day/night cycles
- Toggle switches
- Area effects
- Dynamic lighting

---

### Conditions

All conditions must be **true** for actions to execute.

#### **Logical Operators**

```lua
-- AND (all must be true) - default behavior
Conditions = 
{
    FigureAlive{NpcId = 5001},
    QuestState{QuestId = 100, State = StateActive},
}

-- OR (any can be true)
Conditions = 
{
    ODER(
        FigureAlive{NpcId = 5001},
        FigureAlive{NpcId = 5002}
    ),
}

-- NOT (invert condition)
Conditions = 
{
    Negated(FigureDead{NpcId = 5001}),
}

-- Complex logic
Conditions = 
{
    ODER(
        UND(
            FigureAlive{NpcId = 5001},
            IsGlobalFlagTrue{Name = "Route1"}
        ),
        UND(
            FigureAlive{NpcId = 5002},
            IsGlobalFlagTrue{Name = "Route2"}
        )
    ),
}
```

---

#### **Common Conditions**

**Figure/NPC Conditions**:
```lua
FigureAlive{NpcId = 5001}
FigureDead{NpcId = 5001}
FigureInRange{NpcId = 0, X = 100, Y = 200, Range = 10}
FigureInRangeNpc{NpcId = 0, TargetNpcId = 5001, Range = 5}
FigureHasItem{NpcId = 0, ItemId = 500, Amount = 1}
```

**Player Conditions**:
```lua
PlayerHasItem{ItemId = 500, Amount = 1}
PlayerLevel{Level = 10, Relation = GreaterOrEqual}
PlayerHasMoney{Gold = 100}
PlayerHasBuilding{BuildingId = 10}  -- RTS building
```

**Quest Conditions**:
```lua
QuestState{QuestId = 100, State = StateActive}
QuestState{QuestId = 100, State = StateSolved}
QuestState{QuestId = 100, State = StateInactive}
```

**Flag Conditions**:
```lua
IsGlobalFlagTrue{Name = "MyFlag"}
IsGlobalFlagFalse{Name = "MyFlag"}
```

**Time Conditions**:
```lua
TimeOfDay{Hour = 12, Minute = 0}
TimeBetween{Hour = 8, ToHour = 18}
TimeDay()
TimeNight()
```

**Global State Conditions**:
```lua
IsGlobalState{Name = "Plot", State = "JourneyFour"}
```

---

### Actions

Actions execute when all conditions are met.

#### **Common Actions**

**Quest Actions**:
```lua
QuestBegin{QuestId = 1000}
QuestSolve{QuestId = 1000}
QuestFail{QuestId = 1000}
```

**Flag Actions**:
```lua
SetGlobalFlagTrue{Name = "MyFlag"}
SetGlobalFlagFalse{Name = "MyFlag"}
```

**State Actions**:
```lua
SetGlobalState{Name = "Plot", State = "ChapterTwo"}
```

**Reward Actions**:
```lua
SetRewardFlagTrue{Name = "QuestRewardName"}
-- Actual rewards defined in GdsQuestRewards.lua
```

**Item Actions**:
```lua
PlayerGiveItem{ItemId = 500, Amount = 1}
PlayerRemoveItem{ItemId = 500, Amount = 1}
```

**NPC Actions**:
```lua
Spawn{X = 100, Y = 200, UnitId = 370, NpcId = 5500}
Vanish{NpcId = 5001}
Goto{NpcId = 5001, X = 150, Y = 150}
Follow{NpcId = 5001, Target = 0}  -- Follow player
Stop{NpcId = 5001}
```

**Dialog Actions**:
```lua
DialogBegin{NpcId = 5001}
DialogEnd{}
DialogChoice{ChoiceId = 1, Text = "Tell me more"}
```

**Effect Actions**:
```lua
SetEffect{Effect = "FireExplosion", X = 100, Y = 100, Length = 3000}
RemoveEffect{X = 100, Y = 100}
```

**Outcry (Message) Actions**:
```lua
Outcry{
    NpcId = 0,  -- 0 = player, or use NPC ID
    String = "Message text here",
    Color = ColorYellow,  -- ColorWhite, ColorGreen, ColorRed, ColorYellow
    Tag = "UniqueTagName"  -- Optional, for audio
}
```

**Object Actions**:
```lua
ChangeObject{X = 100, Y = 100, Object = 790}  -- Change to torch object
ChangeBuildingOwner{X = 100, Y = 100}  -- Give building to player
```

---

## NPC Scripting

### NPC Behavior Scripts

Each NPC can have a behavior script: `n<NpcId>.lua`

**Example**: `script/P999/n5100.lua` (Hunter NPC)

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- ====================================
-- Hunter NPC Behavior
-- NpcId: 5100
-- ====================================

-- NPC returns to spawn point when idle
OnIdleGoHome{
    WalkMode = Walk,
    X = _X,
    Y = _Y,
    Direction = South  -- Facing direction
}

-- Spawn only during certain conditions
SpawnOnlyWhen
{
    Conditions =
    {
        -- Only spawns if quest is active
        QuestState{QuestId = 1000, State = StateActive},
    },
    Actions =
    {
    }
}

-- Despawn when quest is complete
Despawn
{
    Conditions =
    {
        QuestState{QuestId = 1000, State = StateSolved},
    },
}

-- Daily routine (optional)
OnToggleEvent
{
    EventName = "HunterMorningRoutine",
    OnConditions = 
    {
        TimeForeNoon(),  -- 5:00 AM - 11:00 AM
    },
    OnActions = 
    {
        Goto{X = 120, Y = 130},  -- Go to hunting grounds
    },
    OffConditions = 
    {
        TimeAfterNoon(),  -- 1:00 PM onwards
    },
    OffActions = 
    {
        Goto{X = _X, Y = _Y},  -- Return home
    },
}

EndDefinition()
end
```

---

### NPC Spawning

#### **Spawn at Map Start**

```lua
-- In n0.lua platform script
OnOneTimeEvent
{
    Conditions = {},  -- Always true
    Actions = 
    {
        Spawn{
            X = 100,
            Y = 200,
            UnitId = 370,    -- Unit type (Orc Warrior)
            NpcId = 5500,    -- Unique NPC ID
            Clan = 5,        -- Which clan/faction
        },
    }
}
```

#### **Spawn When Conditions Met**

```lua
OnOneTimeEvent
{
    EventName = "SpawnBoss",
    Conditions = 
    {
        IsClanSize{Clan = 5, Size = 0},  -- All enemies in clan 5 dead
    },
    Actions = 
    {
        Spawn{
            X = 250,
            Y = 250,
            UnitId = 1500,   -- Boss unit
            NpcId = 5600,
            Effect = "Materialize",  -- Spawn effect
            Length = 2000,   -- Effect duration (ms)
        },
        Outcry{
            NpcId = 5600,
            String = "You dare challenge me?!",
            Color = ColorRed
        },
    }
}
```

#### **Random Spawns**

```lua
OnOneTimeEvent
{
    Conditions = {},
    Actions = 
    {
        Spawn{
            X = 150,
            Y = 150,
            Range = 20,  -- Spawn within 20 units of X,Y
            UnitId = {370, 369, 376},  -- Random unit from list
            NpcId = 0,   -- Use 0 for spawns you don't need to script
            Clan = 5,
        },
    }
}
```

---

## Dialog System

### Dialog Structure

Dialogs are defined in separate dialog files or inline.

**Basic Dialog Example**:

```lua
-- In NPC script or platform script
OnOneTimeEvent
{
    Conditions = 
    {
        FigureInRangeNpc{NpcId = 0, TargetNpcId = 5100, Range = 5},
        IsGlobalFlagFalse{Name = "HunterDialogSeen"},
    },
    Actions = 
    {
        -- Trigger dialog
        SetGlobalFlagTrue{Name = "HunterDialogSeen"},
        DialogBegin{NpcId = 5100},
    }
}

-- Dialog content (simplified)
-- Actual dialogs are more complex and use the GdsDialogSystem
OnDialog
{
    NpcId = 5100,
    Choices = 
    {
        {
            ChoiceId = 1,
            Text = "Can you help me?",
            Conditions = {},
            Actions = 
            {
                SetGlobalFlagTrue{Name = "HunterDialogComplete"},
                QuestBegin{QuestId = 1000},
            }
        },
        {
            ChoiceId = 2,
            Text = "Nevermind.",
            Conditions = {},
            Actions = 
            {
                DialogEnd{},
            }
        },
    }
}
```

**Note**: The full dialog system is complex and uses `GdsDialogSystem.lua`. For simple quests, you can use flags to track dialog progress.

---

## Quest Rewards

### Defining Rewards

**File**: `script/GdsQuestRewards.lua`

Add your map's rewards:

```lua
-- Quest rewards for your custom map P999
QuestRewardsP999 = 
{
    -- Reward name (referenced by SetRewardFlagTrue)
    QuestHunterReward = { 
        XP = {100},           -- 100 experience points
        Money = {Gold = 5},   -- 5 gold
        Items = {600}         -- Item ID 600
    },
    
    -- Multiple items
    QuestBigReward = {
        XP = {500},
        Money = {Gold = 20, Silver = 50},
        Items = {601, 602, 603}  -- Three items
    },
    
    -- XP only
    QuestSimpleReward = {
        XP = {50}
    },
    
    -- Scaled XP (different amounts for different situations)
    QuestScaledReward = {
        XP = {100, 200, 300}  -- Picks based on difficulty/level
    },
}
```

### Giving Rewards

```lua
OnOneTimeEvent
{
    Conditions = 
    {
        QuestState{QuestId = 1000, State = StateSolved},
    },
    Actions = 
    {
        -- Give reward defined in GdsQuestRewards.lua
        SetRewardFlagTrue{Name = "QuestHunterReward"},
    }
}
```

---

## Creating a Campaign

A campaign is a series of connected maps with persistent state.

### Campaign Structure

```
script/
├── P1/     # Map 1: Starting Village
├── P2/     # Map 2: Dark Forest
├── P3/     # Map 3: Mountain Pass
├── P4/     # Map 4: Final Battle
└── GdsVariableStates.lua  # Global campaign states
```

---

### Global States

**File**: `script/GdsVariableStates.lua`

Define campaign progression states:

```lua
-- Example states (already in game)
GlobalVariables = {
    Plot = {
        States = {
            "JourneyOne",
            "JourneyTwo",
            "JourneyThree",
            "JourneyFour",
            "ChapterTwo",
            "ChapterThree",
            -- Add your campaign states here
            "MyCampaignStart",
            "MyCampaignMidpoint",
            "MyCampaignEnding",
        }
    }
}
```

---

### Campaign Map 1: Starting Village (P1)

**File**: `script/P1/n0.lua`

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- ====================================
-- CAMPAIGN: Rise of the Shadow
-- Map 1: Starting Village
-- ====================================

-- Initialize campaign on first load
OnOneTimeEvent
{
    EventName = "CampaignInit",
    Conditions = {},
    Actions = 
    {
        -- Set initial campaign state
        SetGlobalState{Name = "Plot", State = "MyCampaignStart"},
        -- Give player starting quest
        QuestBegin{QuestId = 2000},  -- "Defend the Village"
        -- Spawn village NPCs
        Spawn{X = 100, Y = 100, UnitId = 500, NpcId = 6000},  -- Village Elder
        Spawn{X = 120, Y = 100, UnitId = 501, NpcId = 6001},  -- Blacksmith
        Spawn{X = 140, Y = 100, UnitId = 502, NpcId = 6002},  -- Merchant
    }
}

-- Main quest: Defend village from attack
OnOneTimeEvent
{
    EventName = "VillageAttackStart",
    Conditions = 
    {
        -- Wait 2 minutes after map start
        IsGlobalTimeElapsed{Name = "MapStartTime", Seconds = 120},
    },
    Actions = 
    {
        -- Spawn enemy waves
        Spawn{X = 300, Y = 300, UnitId = 370, NpcId = 0, Clan = 5},
        Spawn{X = 310, Y = 300, UnitId = 370, NpcId = 0, Clan = 5},
        Spawn{X = 320, Y = 300, UnitId = 369, NpcId = 0, Clan = 5},
        -- Warning message
        Outcry{
            NpcId = 0,
            String = "The village is under attack!",
            Color = ColorRed
        },
    }
}

-- Quest completion: All enemies defeated
OnOneTimeEvent
{
    EventName = "VillageDefended",
    Conditions = 
    {
        QuestState{QuestId = 2000, State = StateActive},
        IsClanSize{Clan = 5, Size = 0},  -- All enemies dead
    },
    Actions = 
    {
        -- Complete quest
        QuestSolve{QuestId = 2000},
        SetRewardFlagTrue{Name = "VillageDefenseReward"},
        -- Start next quest
        QuestBegin{QuestId = 2001},  -- "Investigate the Forest"
        -- Unlock portal to next map
        ChangeObject{X = 200, Y = 200, Object = 778},  -- Activate portal
        SetGlobalFlagTrue{Name = "PortalToForestOpen"},
    }
}

-- Portal to next map (P2)
OnOneTimeEvent
{
    EventName = "PortalToMap2",
    Conditions = 
    {
        IsGlobalFlagTrue{Name = "PortalToForestOpen"},
        FigureInRange{NpcId = 0, X = 200, Y = 200, Range = 5},
    },
    Actions = 
    {
        -- Save campaign state
        SetGlobalState{Name = "Plot", State = "MyCampaignMidpoint"},
        -- Teleport to next map (done by engine when portal used)
    }
}

EndDefinition()
end
```

---

### Campaign Map 2: Dark Forest (P2)

**File**: `script/P2/n0.lua`

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- ====================================
-- CAMPAIGN: Rise of the Shadow
-- Map 2: Dark Forest
-- ====================================

-- Check player arrived from Map 1
OnOneTimeEvent
{
    EventName = "Map2Init",
    Conditions = 
    {
        -- Campaign state check
        IsGlobalState{Name = "Plot", State = "MyCampaignMidpoint"},
    },
    Actions = 
    {
        -- Continue quest from Map 1
        -- Quest 2001 should already be active from Map 1
        Outcry{
            NpcId = 0,
            String = "I must investigate these dark woods...",
            Color = ColorYellow
        },
    }
}

-- Quest: Find the corrupted shrine
OnOneTimeEvent
{
    EventName = "ShrineDiscovered",
    Conditions = 
    {
        QuestState{QuestId = 2001, State = StateActive},
        FigureInRange{NpcId = 0, X = 150, Y = 150, Range = 10},
    },
    Actions = 
    {
        -- Spawn boss enemy
        Spawn{
            X = 150,
            Y = 150,
            UnitId = 1500,   -- Boss
            NpcId = 7000,
            Effect = "DemonPortal",
            Length = 3000,
        },
        -- Update quest
        SetGlobalFlagTrue{Name = "ShrineFound"},
        Outcry{
            NpcId = 7000,
            String = "You shall not pass!",
            Color = ColorRed
        },
    }
}

-- Quest completion: Defeat boss
OnOneTimeEvent
{
    EventName = "BossDefeated",
    Conditions = 
    {
        IsGlobalFlagTrue{Name = "ShrineFound"},
        FigureDead{NpcId = 7000},
    },
    Actions = 
    {
        -- Complete quest
        QuestSolve{QuestId = 2001},
        SetRewardFlagTrue{Name = "ShrineQuestReward"},
        -- Advance campaign
        SetGlobalState{Name = "Plot", State = "MyCampaignEnding"},
        -- Open portal to final map
        ChangeObject{X = 200, Y = 200, Object = 778},
        SetGlobalFlagTrue{Name = "PortalToFinalMap"},
    }
}

EndDefinition()
end
```

---

### Campaign Persistence

**What Carries Over Between Maps**:
- Global flags (`SetGlobalFlagTrue`)
- Global states (`SetGlobalState`)
- Quest status
- Player level and items
- Hero units

**What Doesn't Carry Over**:
- NPC positions
- Map-specific spawns
- Temporary effects
- Local variables

---

## Advanced Quest Techniques

### Multi-Stage Quests

**Example**: Collect 3 different items in any order

```lua
-- Stage 1: Quest starts
OnOneTimeEvent
{
    Conditions = {},
    Actions = 
    {
        QuestBegin{QuestId = 3000},
    }
}

-- Stage 2a: Player finds item 1
OnOneTimeEvent
{
    EventName = "Item1Found",
    Conditions = 
    {
        QuestState{QuestId = 3000, State = StateActive},
        PlayerHasItem{ItemId = 100},
    },
    Actions = 
    {
        SetGlobalFlagTrue{Name = "Quest3000_Item1"},
        Outcry{NpcId = 0, String = "Found the ancient sword!", Color = ColorGreen},
    }
}

-- Stage 2b: Player finds item 2
OnOneTimeEvent
{
    EventName = "Item2Found",
    Conditions = 
    {
        QuestState{QuestId = 3000, State = StateActive},
        PlayerHasItem{ItemId = 101},
    },
    Actions = 
    {
        SetGlobalFlagTrue{Name = "Quest3000_Item2"},
        Outcry{NpcId = 0, String = "Found the magic amulet!", Color = ColorGreen},
    }
}

-- Stage 2c: Player finds item 3
OnOneTimeEvent
{
    EventName = "Item3Found",
    Conditions = 
    {
        QuestState{QuestId = 3000, State = StateActive},
        PlayerHasItem{ItemId = 102},
    },
    Actions = 
    {
        SetGlobalFlagTrue{Name = "Quest3000_Item3"},
        Outcry{NpcId = 0, String = "Found the sacred tome!", Color = ColorGreen},
    }
}

-- Stage 3: All items collected
OnOneTimeEvent
{
    EventName = "AllItemsFound",
    Conditions = 
    {
        QuestState{QuestId = 3000, State = StateActive},
        IsGlobalFlagTrue{Name = "Quest3000_Item1"},
        IsGlobalFlagTrue{Name = "Quest3000_Item2"},
        IsGlobalFlagTrue{Name = "Quest3000_Item3"},
    },
    Actions = 
    {
        SetGlobalFlagTrue{Name = "Quest3000_AllItems"},
        Outcry{
            NpcId = 0,
            String = "I have all three artifacts! Time to return.",
            Color = ColorGold
        },
    }
}

-- Stage 4: Quest completion
OnOneTimeEvent
{
    EventName = "QuestComplete",
    Conditions = 
    {
        IsGlobalFlagTrue{Name = "Quest3000_AllItems"},
        FigureInRangeNpc{NpcId = 0, TargetNpcId = 6000, Range = 5},
    },
    Actions = 
    {
        QuestSolve{QuestId = 3000},
        PlayerRemoveItem{ItemId = 100},
        PlayerRemoveItem{ItemId = 101},
        PlayerRemoveItem{ItemId = 102},
        SetRewardFlagTrue{Name = "Quest3000Reward"},
    }
}
```

---

### Quest Branching (Player Choice)

**Example**: Player chooses to help good or evil faction

```lua
-- Quest start
OnOneTimeEvent
{
    Conditions = {},
    Actions = 
    {
        QuestBegin{QuestId = 4000},  -- "Choose Your Allegiance"
    }
}

-- Choice 1: Help the paladins (good)
OnOneTimeEvent
{
    EventName = "ChooseGood",
    Conditions = 
    {
        QuestState{QuestId = 4000, State = StateActive},
        IsGlobalFlagTrue{Name = "PlayerChoosePaladins"},  -- Set in dialog
    },
    Actions = 
    {
        QuestSolve{QuestId = 4000},
        QuestBegin{QuestId = 4001},  -- Good path quests
        SetGlobalState{Name = "Allegiance", State = "Good"},
        -- Spawn paladin allies
        Spawn{X = 100, Y = 100, UnitId = 600, NpcId = 7100, Clan = Player},
        Spawn{X = 110, Y = 100, UnitId = 601, NpcId = 7101, Clan = Player},
        -- Make necromancers hostile
        ChangeFactionNpc{NpcId = 7200, Faction = Hostile},
    }
}

-- Choice 2: Help the necromancers (evil)
OnOneTimeEvent
{
    EventName = "ChooseEvil",
    Conditions = 
    {
        QuestState{QuestId = 4000, State = StateActive},
        IsGlobalFlagTrue{Name = "PlayerChooseNecromancers"},
    },
    Actions = 
    {
        QuestSolve{QuestId = 4000},
        QuestBegin{QuestId = 4002},  -- Evil path quests
        SetGlobalState{Name = "Allegiance", State = "Evil"},
        -- Spawn necromancer allies
        Spawn{X = 200, Y = 200, UnitId = 700, NpcId = 7200, Clan = Player},
        Spawn{X = 210, Y = 200, UnitId = 701, NpcId = 7201, Clan = Player},
        -- Make paladins hostile
        ChangeFactionNpc{NpcId = 7100, Faction = Hostile},
    }
}
```

---

### Timed Quests

**Example**: Defend village for 10 minutes

```lua
-- Quest start
OnOneTimeEvent
{
    EventName = "DefenseQuestStart",
    Conditions = {},
    Actions = 
    {
        QuestBegin{QuestId = 5000},
        -- Start timer
        SetGlobalTimeStamp{Name = "DefenseTimer"},
        -- Spawn initial enemies
        Spawn{X = 300, Y = 300, UnitId = 370, NpcId = 0, Clan = 5},
    }
}

-- Enemy waves (every 2 minutes)
OnEvent
{
    EventName = "SpawnWave",
    Conditions = 
    {
        QuestState{QuestId = 5000, State = StateActive},
        IsGlobalTimeElapsed{Name = "DefenseTimer", Seconds = 120},  -- 2 min
    },
    Actions = 
    {
        -- Spawn more enemies
        Spawn{X = 300, Y = 300, UnitId = 370, NpcId = 0, Clan = 5},
        Spawn{X = 310, Y = 300, UnitId = 369, NpcId = 0, Clan = 5},
        -- Reset timer for next wave
        SetGlobalTimeStamp{Name = "DefenseTimer"},
    }
}

-- Quest success: Survived 10 minutes
OnOneTimeEvent
{
    EventName = "DefenseSuccess",
    Conditions = 
    {
        QuestState{QuestId = 5000, State = StateActive},
        IsGlobalTimeElapsed{Name = "DefenseTimer", Seconds = 600},  -- 10 min
    },
    Actions = 
    {
        QuestSolve{QuestId = 5000},
        SetRewardFlagTrue{Name = "DefenseReward"},
        Outcry{NpcId = 0, String = "We survived! The village is safe!", Color = ColorGreen},
    }
}

-- Quest failure: Village NPC died
OnOneTimeEvent
{
    EventName = "DefenseFailure",
    Conditions = 
    {
        QuestState{QuestId = 5000, State = StateActive},
        FigureDead{NpcId = 6000},  -- Village elder died
    },
    Actions = 
    {
        QuestFail{QuestId = 5000},
        Outcry{NpcId = 0, String = "I failed to protect the village...", Color = ColorRed},
    }
}
```

---

### Dynamic Difficulty

**Example**: Spawn more enemies based on player level

```lua
OnOneTimeEvent
{
    EventName = "SpawnByLevel",
    Conditions = 
    {
        PlayerLevel{Level = 10, Relation = GreaterOrEqual},
    },
    Actions = 
    {
        -- Spawn harder enemies for high-level players
        Spawn{X = 200, Y = 200, UnitId = 377, NpcId = 0, Clan = 5},  -- Elite orc
        Spawn{X = 210, Y = 200, UnitId = 378, NpcId = 0, Clan = 5},  -- Orc brute
    }
}

OnOneTimeEvent
{
    EventName = "SpawnForLowLevel",
    Conditions = 
    {
        PlayerLevel{Level = 5, Relation = LessOrEqual},
    },
    Actions = 
    {
        -- Spawn easier enemies for low-level players
        Spawn{X = 200, Y = 200, UnitId = 370, NpcId = 0, Clan = 5},  -- Basic orc
    }
}
```

---

## Reference API

### Most Common Functions

#### **Conditions**

```lua
-- Figure conditions
FigureAlive{NpcId = <id>}
FigureDead{NpcId = <id>}
FigureInRange{NpcId = <id>, X = <x>, Y = <y>, Range = <range>}
FigureInRangeNpc{NpcId = <id>, TargetNpcId = <target>, Range = <range>}
FigureHasItem{NpcId = <id>, ItemId = <item>, Amount = <amount>}

-- Player conditions
PlayerHasItem{ItemId = <item>, Amount = <amount>}
PlayerLevel{Level = <level>, Relation = GreaterOrEqual/LessOrEqual/Equal}
PlayerHasMoney{Gold = <amount>}

-- Quest conditions
QuestState{QuestId = <id>, State = StateActive/StateSolved/StateInactive}

-- Flag conditions
IsGlobalFlagTrue{Name = "<flagname>"}
IsGlobalFlagFalse{Name = "<flagname>"}

-- Time conditions
TimeOfDay{Hour = <hour>, Minute = <minute>}
TimeBetween{Hour = <hour>, ToHour = <tohour>}
IsGlobalTimeElapsed{Name = "<timer>", Seconds = <seconds>}

-- Clan conditions
IsClanSize{Clan = <clan>, Size = <size>}

-- State conditions
IsGlobalState{Name = "<variable>", State = "<state>"}

-- Logic operators
Negated(<condition>)
ODER(<condition1>, <condition2>, ...)  -- OR
UND(<condition1>, <condition2>, ...)   -- AND
```

#### **Actions**

```lua
-- Quest actions
QuestBegin{QuestId = <id>}
QuestSolve{QuestId = <id>}
QuestFail{QuestId = <id>}

-- Flag actions
SetGlobalFlagTrue{Name = "<flagname>"}
SetGlobalFlagFalse{Name = "<flagname>"}

-- State actions
SetGlobalState{Name = "<variable>", State = "<state>"}

-- Timer actions
SetGlobalTimeStamp{Name = "<timer>"}

-- Reward actions
SetRewardFlagTrue{Name = "<rewardname>"}

-- Item actions
PlayerGiveItem{ItemId = <item>, Amount = <amount>}
PlayerRemoveItem{ItemId = <item>, Amount = <amount>}

-- NPC actions
Spawn{X = <x>, Y = <y>, UnitId = <unit>, NpcId = <id>, Clan = <clan>}
Vanish{NpcId = <id>}
Goto{NpcId = <id>, X = <x>, Y = <y>, Range = <range>}
Follow{NpcId = <id>, Target = <target>}
Stop{NpcId = <id>}

-- Message actions
Outcry{NpcId = <id>, String = "<text>", Color = Color<color>}

-- Effect actions
SetEffect{Effect = "<effectname>", X = <x>, Y = <y>, Length = <ms>}
RemoveEffect{X = <x>, Y = <y>}

-- Object actions
ChangeObject{X = <x>, Y = <y>, Object = <objectid>}
ChangeBuildingOwner{X = <x>, Y = <y>}
```

---

## Complete Examples

### Example 1: Simple Kill Quest

**Quest**: Kill 10 goblins in the area

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- ====================================
-- Quest: Goblin Extermination
-- QuestId: 6000
-- ====================================

-- Quest start
OnOneTimeEvent
{
    Conditions = {},
    Actions = 
    {
        QuestBegin{QuestId = 6000},
        -- Spawn 10 goblins
        Spawn{X = 200, Y = 200, Range = 30, UnitId = {777, 779, 784}, NpcId = 0, Clan = 10},
        Spawn{X = 200, Y = 200, Range = 30, UnitId = {777, 779, 784}, NpcId = 0, Clan = 10},
        Spawn{X = 200, Y = 200, Range = 30, UnitId = {777, 779, 784}, NpcId = 0, Clan = 10},
        Spawn{X = 200, Y = 200, Range = 30, UnitId = {777, 779, 784}, NpcId = 0, Clan = 10},
        Spawn{X = 200, Y = 200, Range = 30, UnitId = {777, 779, 784}, NpcId = 0, Clan = 10},
        Spawn{X = 200, Y = 200, Range = 30, UnitId = {777, 779, 784}, NpcId = 0, Clan = 10},
        Spawn{X = 200, Y = 200, Range = 30, UnitId = {777, 779, 784}, NpcId = 0, Clan = 10},
        Spawn{X = 200, Y = 200, Range = 30, UnitId = {777, 779, 784}, NpcId = 0, Clan = 10},
        Spawn{X = 200, Y = 200, Range = 30, UnitId = {777, 779, 784}, NpcId = 0, Clan = 10},
        Spawn{X = 200, Y = 200, Range = 30, UnitId = {777, 779, 784}, NpcId = 0, Clan = 10},
    }
}

-- Quest complete: All goblins dead
OnOneTimeEvent
{
    Conditions = 
    {
        QuestState{QuestId = 6000, State = StateActive},
        IsClanSize{Clan = 10, Size = 0},  -- Clan 10 has 0 members
    },
    Actions = 
    {
        QuestSolve{QuestId = 6000},
        SetRewardFlagTrue{Name = "GoblinQuestReward"},
        Outcry{NpcId = 0, String = "The goblin threat has been eliminated!", Color = ColorGreen},
    }
}

EndDefinition()
end
```

**Rewards**:
```lua
-- In GdsQuestRewards.lua
QuestRewardsP999 = 
{
    GoblinQuestReward = { XP = {200}, Money = {Gold = 10} },
}
```

---

### Example 2: Escort Quest

**Quest**: Escort NPC from point A to point B safely

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- ====================================
-- Quest: Escort the Merchant
-- QuestId: 7000
-- NPC: 8000 (Merchant)
-- ====================================

-- Quest start
OnOneTimeEvent
{
    Conditions = {},
    Actions = 
    {
        QuestBegin{QuestId = 7000},
        -- Spawn merchant
        Spawn{
            X = 100,
            Y = 100,
            UnitId = 502,  -- Merchant unit
            NpcId = 8000,
            Clan = Player,  -- Friendly to player
        },
    }
}

-- Merchant follows player
OnOneTimeEvent
{
    Conditions = 
    {
        FigureAlive{NpcId = 8000},
        FigureInRangeNpc{NpcId = 0, TargetNpcId = 8000, Range = 10},
    },
    Actions = 
    {
        Follow{NpcId = 8000, Target = 0},  -- Follow player
        SetGlobalFlagTrue{Name = "MerchantFollowing"},
    }
}

-- Spawn bandits halfway
OnOneTimeEvent
{
    Conditions = 
    {
        IsGlobalFlagTrue{Name = "MerchantFollowing"},
        FigureInRange{NpcId = 8000, X = 200, Y = 200, Range = 20},
    },
    Actions = 
    {
        -- Spawn bandit ambush
        Spawn{X = 220, Y = 220, UnitId = 370, NpcId = 0, Clan = 15},
        Spawn{X = 230, Y = 220, UnitId = 370, NpcId = 0, Clan = 15},
        Spawn{X = 240, Y = 220, UnitId = 369, NpcId = 0, Clan = 15},
        Outcry{NpcId = 8000, String = "Bandits! Help me!", Color = ColorRed},
    }
}

-- Quest success: Merchant reaches destination
OnOneTimeEvent
{
    Conditions = 
    {
        QuestState{QuestId = 7000, State = StateActive},
        FigureAlive{NpcId = 8000},  -- Merchant still alive
        FigureInRange{NpcId = 8000, X = 300, Y = 300, Range = 10},  -- At destination
    },
    Actions = 
    {
        QuestSolve{QuestId = 7000},
        SetRewardFlagTrue{Name = "EscortReward"},
        Outcry{NpcId = 8000, String = "Thank you for your protection!", Color = ColorWhite},
        Stop{NpcId = 8000},  -- Merchant stops
    }
}

-- Quest failure: Merchant dies
OnOneTimeEvent
{
    Conditions = 
    {
        QuestState{QuestId = 7000, State = StateActive},
        FigureDead{NpcId = 8000},
    },
    Actions = 
    {
        QuestFail{QuestId = 7000},
        Outcry{NpcId = 0, String = "I failed to protect the merchant...", Color = ColorRed},
    }
}

EndDefinition()
end
```

---

### Example 3: Multi-Map Campaign

**Campaign**: The Shadow Rises (3 maps)

#### **Map 1: P101/n0.lua**

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- Initialize campaign
OnOneTimeEvent
{
    Conditions = {},
    Actions = 
    {
        SetGlobalState{Name = "ShadowCampaign", State = "Act1Start"},
        QuestBegin{QuestId = 10000},  -- "The Shadow Awakens"
        Spawn{X = 150, Y = 150, UnitId = 500, NpcId = 9000},  -- Prophet NPC
    }
}

-- Main quest
OnOneTimeEvent
{
    Conditions = 
    {
        IsGlobalFlagTrue{Name = "ProphetDialogComplete"},
    },
    Actions = 
    {
        QuestSolve{QuestId = 10000},
        QuestBegin{QuestId = 10001},  -- "Find the Ancient Artifact"
    }
}

-- Find artifact
OnOneTimeEvent
{
    Conditions = 
    {
        PlayerHasItem{ItemId = 3000},  -- Ancient Artifact
    },
    Actions = 
    {
        QuestSolve{QuestId = 10001},
        SetGlobalState{Name = "ShadowCampaign", State = "Act1Complete"},
        -- Activate portal to Map 2
        ChangeObject{X = 250, Y = 250, Object = 778},
        SetGlobalFlagTrue{Name = "PortalToMap2"},
    }
}

EndDefinition()
end
```

#### **Map 2: P102/n0.lua**

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- Check campaign state
OnOneTimeEvent
{
    Conditions = 
    {
        IsGlobalState{Name = "ShadowCampaign", State = "Act1Complete"},
    },
    Actions = 
    {
        SetGlobalState{Name = "ShadowCampaign", State = "Act2Start"},
        QuestBegin{QuestId = 10002},  -- "Confront the Necromancer"
    }
}

-- Boss fight
OnOneTimeEvent
{
    Conditions = 
    {
        FigureInRange{NpcId = 0, X = 200, Y = 200, Range = 15},
    },
    Actions = 
    {
        -- Spawn necromancer boss
        Spawn{
            X = 200,
            Y = 200,
            UnitId = 1800,  -- Necromancer boss
            NpcId = 9100,
            Effect = "DemonPortal",
        },
        Outcry{NpcId = 9100, String = "You dare challenge me?!", Color = ColorRed},
    }
}

-- Boss defeated
OnOneTimeEvent
{
    Conditions = 
    {
        FigureDead{NpcId = 9100},
    },
    Actions = 
    {
        QuestSolve{QuestId = 10002},
        SetGlobalState{Name = "ShadowCampaign", State = "Act2Complete"},
        -- Portal to final map
        ChangeObject{X = 250, Y = 250, Object = 778},
    }
}

EndDefinition()
end
```

#### **Map 3: P103/n0.lua** (Final Map)

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- Final act
OnOneTimeEvent
{
    Conditions = 
    {
        IsGlobalState{Name = "ShadowCampaign", State = "Act2Complete"},
    },
    Actions = 
    {
        SetGlobalState{Name = "ShadowCampaign", State = "Act3Start"},
        QuestBegin{QuestId = 10003},  -- "The Final Battle"
    }
}

-- Final boss spawn
OnOneTimeEvent
{
    Conditions = 
    {
        FigureInRange{NpcId = 0, X = 256, Y = 256, Range = 20},
    },
    Actions = 
    {
        Spawn{
            X = 256,
            Y = 256,
            UnitId = 1900,  -- Dragon King (final boss)
            NpcId = 9200,
            Effect = "DragonPortal",
        },
        Outcry{NpcId = 9200, String = "Face your doom!", Color = ColorRed},
    }
}

-- Campaign complete
OnOneTimeEvent
{
    Conditions = 
    {
        FigureDead{NpcId = 9200},
    },
    Actions = 
    {
        QuestSolve{QuestId = 10003},
        SetGlobalState{Name = "ShadowCampaign", State = "Complete"},
        SetRewardFlagTrue{Name = "CampaignCompleteReward"},
        Outcry{
            NpcId = 0,
            String = "The shadow has been vanquished! Peace returns to the land.",
            Color = ColorGold
        },
    }
}

EndDefinition()
end
```

---

## Best Practices

### 1. **Naming Conventions**

```lua
-- Good names (descriptive)
SetGlobalFlagTrue{Name = "Quest1000_BossDefeated"}
SetGlobalFlagTrue{Name = "VillageDefenseComplete"}

-- Bad names (unclear)
SetGlobalFlagTrue{Name = "Flag1"}
SetGlobalFlagTrue{Name = "Done"}
```

### 2. **Use EventName for Debugging**

```lua
OnOneTimeEvent
{
    EventName = "QuestStart_HunterRequest",  -- Helpful for debugging
    Conditions = {},
    Actions = {}
}
```

### 3. **Comment Your Code**

```lua
-- ====================================
-- Quest: Hunter's Request
-- QuestId: 1000
-- Description: Collect 3 wolf pelts
-- ====================================

-- Stage 1: Quest activation
OnOneTimeEvent
{
    -- ... code ...
}
```

### 4. **Test Incrementally**

Start with simple events:
```lua
-- Test 1: Just spawn an NPC
OnOneTimeEvent
{
    Conditions = {},
    Actions = { Spawn{...} }
}

-- Test 2: Add movement
-- Test 3: Add quest logic
-- etc.
```

### 5. **Use Global Flags for Quest State**

```lua
-- Track quest progress with flags
SetGlobalFlagTrue{Name = "Quest1000_Stage1"}
SetGlobalFlagTrue{Name = "Quest1000_Stage2"}
SetGlobalFlagTrue{Name = "Quest1000_Complete"}
```

### 6. **Avoid Infinite Loops**

```lua
-- BAD: Will trigger every frame!
OnEvent
{
    Conditions = { FigureInRange{...} },
    Actions = { SetGlobalFlagTrue{...} }
}

-- GOOD: Triggers once
OnOneTimeEvent
{
    Conditions = { FigureInRange{...} },
    Actions = { SetGlobalFlagTrue{...} }
}
```

---

## Conclusion

You now have a **complete framework** for creating quests and campaigns in SpellForce:

**Key Takeaways**:
1. **Events** = Condition → Action pairs
2. **Quests** = Series of events with objectives
3. **Campaigns** = Connected maps with persistent state
4. **NPCs** = Behavior scripts with state machines
5. **Rewards** = XP, gold, items defined separately

**Workflow**:
1. Design your quest/campaign on paper
2. Create map directory structure
3. Write platform script (n0.lua)
4. Write NPC scripts as needed
5. Define rewards
6. Test incrementally
7. Iterate and polish

With these tools and examples, you can create rich, engaging quests and full custom campaigns for SpellForce!

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Author**: SpellForce Community Modding Documentation Project

**Happy Modding!**
