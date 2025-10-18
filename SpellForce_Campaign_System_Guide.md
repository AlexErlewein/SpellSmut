# SpellForce Platinum Edition - Campaign System Guide

## Table of Contents
1. [Campaign Architecture Overview](#campaign-architecture-overview)
2. [Platform System](#platform-system)
3. [Campaign Flow](#campaign-flow)
4. [Platform Scripts (n0.lua)](#platform-scripts-n0lua)
5. [Global Campaign State](#global-campaign-state)
6. [Quest Chains](#quest-chains)
7. [Platform Transitions](#platform-transitions)
8. [Cutscene System](#cutscene-system)
9. [Campaign Variables](#campaign-variables)
10. [Creating a Custom Campaign](#creating-a-custom-campaign)

---

## Campaign Architecture Overview

### What is a Campaign?

SpellForce's **single-player campaign** is a **linked sequence of maps (platforms)** connected by:
- **Portal Travel**: Player moves between maps via portals
- **Quest Chains**: Quests from one map continue on another
- **Persistent State**: Variables, quest progress, and items carry over
- **Story Progression**: Narrative unfolds across multiple locations

### Key Components

| Component | Description | File Location |
|-----------|-------------|---------------|
| **Platform Scripts** | Map-specific logic (n0.lua) | `script/P1/n0.lua`, `script/P9/n0.lua` |
| **NPC Scripts** | Character behaviors | `script/P1/n2016.lua`, etc. |
| **Cutscenes** | Story cinematics | `script/P9/n2016_CutsceneMarciaEntry.lua` |
| **Global Events** | Cross-map triggers | `GdsGlobalEventSystem.lua` |
| **Quest Rewards** | Per-platform rewards | `GdsQuestRewards.lua` |
| **Campaign State** | Global flags/variables | Stored in savegame |

---

## Platform System

### What is a Platform?

A **platform** is a single playable map in SpellForce. Each platform has:
- **Platform ID**: Numeric identifier (e.g., `P1` = Greyfell, `P9` = Northern Windwalls)
- **n0.lua Script**: Main platform logic
- **NPC Scripts**: Individual character behaviors
- **Quest Definitions**: Platform-specific quests

### Platform ID System

**Platform Numbering Convention**:

| Platform ID | Map Name | Type |
|-------------|----------|------|
| **P1** | Greyfell (Liannon) | Campaign Map |
| **P2** | Eloni | Campaign Map |
| **P4** | Leafshade | Campaign Map |
| **P5** | Shiel | Campaign Map |
| **P6** | Wildland Pass | Campaign Map |
| **P7** | Icegate Marsh | Campaign Map |
| **P9** | Northern Windwalls | Campaign Map |
| **P10** | Southern Windwalls | Campaign Map |
| **P11** | Stoneblade Mountain | Campaign Map |
| **P12** | Greydusk Vale | Campaign Map |
| **P15** | Howling Mounds | Campaign Map |
| **P16** | Whisper | Campaign Map |
| **P17** | Godwall | Campaign Map |
| **P19** | Mulandir | Campaign Map |
| **P21** | Farlorn's Hope | Campaign Map |
| **P23** | The Rift | Campaign Map |
| **P25** | Southern Godmark | Campaign Map |
| **P27** | Nightwhisper Dale | Campaign Map |
| **P30** | Breathing Forest | Campaign Map |
| **P32** | Sharrowdale (Final Map) | Campaign Map |
| **P63** | Greyfell (Tutorial) | Campaign Map |
| **P101-P116** | Expansion 1 Maps | Breath of Winter |
| **P200-P213** | Expansion 2 Maps | Shadow of the Phoenix |

### Platform Types

```lua
-- In GdsBase.lua
-- Platform types are defined in config
StateMachineType = kGdsStateMachineTypeFigureScript    -- NPC script
StateMachineType = kGdsStateMachineTypeBuildingScript  -- Platform script (n0.lua)
StateMachineType = kGdsStateMachineTypePatch           -- Patch script
```

---

## Campaign Flow

### Campaign Progression Model

```
[Tutorial: Greyfell P63]
         ↓
[Start: Greyfell P1] → [Eloni P2] → [Leafshade P4] → [Shiel P5]
                                                            ↓
         ← ← ← ← ← ← [Wildland Pass P6] ← ← ← ← ← ← ← ← ←
         ↓
[Northern Windwalls P9] → [Southern Windwalls P10] → [Stoneblade Mountain P11]
                                                                  ↓
         ← ← ← ← ← ← ← [Greydusk Vale P12] ← ← ← ← ← ← ← ← ← ←
         ↓
[Howling Mounds P15] → [Whisper P16] → [Godwall P17] → [Mulandir P19]
         ↓
[Farlorn's Hope P21] → [The Rift P23] → [Southern Godmark P25]
         ↓
[Nightwhisper Dale P27] → [Breathing Forest P30] → [Sharrowdale P32 - FINAL BOSS]
```

### Campaign State Management

The game tracks:
- **Current Platform**: Where player is now
- **Visited Platforms**: Which maps player has unlocked
- **Quest Progress**: Which quests are active/solved across all maps
- **Global Flags**: Story progress markers
- **Player Inventory**: Items persist across maps
- **Hero Roster**: Heroes travel with player

---

## Platform Scripts (n0.lua)

### Purpose of n0.lua

Every platform has an **n0.lua** file that serves as the **map controller**:
- Initializes quests for that platform
- Handles platform-wide events
- Manages quest state transitions
- Controls portal activation
- Spawns RTS units (if applicable)
- Manages special map mechanics

### n0.lua Structure

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- QUEST INITIALIZATION
-- Initialize quests when platform loads

-- QUEST STATE MANAGEMENT
-- Track quest progress and trigger events

-- PLATFORM EVENTS
-- Special mechanics for this map

-- SPAWN MANAGEMENT
-- RTS spawn logic

-- PORTAL CONTROL
-- Portal activation conditions

EndDefinition()
end
```

### Example: Greyfell (P1) n0.lua

**Location**: `script/p1/n0.lua`

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

---Quest status initialization
---- Quest 12: Entry to Greyfell
OnOneTimeEvent
{
    Conditions = {
        QuestState{QuestId = 12, State = StateUnknown}
    },
    Actions = {
        QuestBegin{QuestId = 12},   -- Main quest: Explore Greyfell
        QuestBegin{QuestId = 446},  -- Tutorial quest
        QuestBegin{QuestId = 447},  -- Tutorial quest
        QuestSolve{QuestId = 446},  -- Auto-solve tutorial
    }
}

-- Check if player has dagger AND quest
---- Quest 65: Snarf's Dagger Quest
OnOneTimeEvent
{
    Conditions = {
        PlayerHasItem{ItemId = 2336},  -- Dagger
        QuestState{QuestId = 65, State = StateActive}
    },
    Actions = {
        SetPlayerFlagTrue{Name = "Q65HasDaggerAndQuest"}
    }
}

-- Victory condition for West Camp
---- Quest 63, 64, 65: Clear West Camp
OnOneTimeEvent
{
    Conditions = {
        Negated(EnemyUnitInRange{
            X = 66, Y = 122, 
            NpcId = Avatar, 
            Range = 4, 
            UnitId = 0, 
            UpdateInterval = 60
        }),
        FigureDead{NpcId = 1716},  -- Boss dead
        QuestState{QuestId = 65, State = StateActive}
    },
    Actions = {
        QuestSolve{QuestId = 63},   -- West camp cleared
        QuestBegin{QuestId = 64}    -- Start next quest
    }
}

-- Check if scribes are killed (Ghost quest)
OnOneTimeEvent
{
    Conditions = {
        IsPlayerFlagTrue{Name = "Q43ScribeDead"},
        QuestState{QuestId = 41, State = StateActive},
    },
    Actions = {
        QuestBegin{QuestId = 43},  -- Investigate scribe death
        QuestBegin{QuestId = 45},  -- Find ghost cause
    }
}

-- Portal troops escort quest
OnToggleEvent
{
    UpdateInterval = 20,
    OnConditions = {
        -- All troops reached portal
        FigureInRange{NpcId = 1406, X = 123, Y = 112, Range = 1},
        FigureInRange{NpcId = 1608, X = 124, Y = 113, Range = 1},
        FigureInRange{NpcId = 1609, X = 126, Y = 113, Range = 1},
        FigureInRange{NpcId = 1610, X = 124, Y = 111, Range = 1},
        FigureInRange{NpcId = 1611, X = 126, Y = 111, Range = 1},
    },
    OnActions = {
        SetGlobalFlagFalse{Name = "PortalTroopsSpawning"},
        SetGlobalFlagTrue{Name = "PortalTroopsWalking"},
        ResetGlobalCounter{Name = "NumTroopsSpawned"},
        ResetGlobalCounter{Name = "NumTroopsDead"},
    },
    OffConditions = {
        -- All troops died
        IsGlobalCounter{Name = "NumTroopsDead", Operator = IsGreaterOrEqual, Value = 5},
        QuestState{QuestId = 16, State = StateActive},
    },
    OffActions = {
        -- Restart quest from scratch
        QuestBegin{QuestId = 14, SubQuestActivate = TRUE},
        SetGlobalFlagFalse{Name = "PortalTroopsWalking"},
    },
}

-- Portal to Eloni opens
OnOneTimeEvent
{
    Conditions = {
        ODER(
            UND(
                IsGlobalTimeElapsed{Name = "ForceLiannonPortalKeepOpen", Seconds = 8},
                IsGlobalFlagTrue{Name = "EinerGehtZumPortal"}
            ),
            UND(
                IsGlobalCounter{Name = "NumTroopsDead", Operator = IsGreaterOrEqual, Value = 5},
                QuestState{QuestId = 17, State = StateActive}
            )
        ),
        QuestState{QuestId = 262, State = StateUnknown},
    },
    Actions = {
        QuestSolve{QuestId = 17},
        QuestBegin{QuestId = 262},  -- Portal to Eloni opened!
        SetPlayerFlagTrue{Name = "QuestGetToEloniSolved"},
    },
}

EndDefinition()
end
```

### Key Patterns in n0.lua

#### 1. **Quest Initialization Pattern**
```lua
OnOneTimeEvent
{
    Conditions = {
        QuestState{QuestId = X, State = StateUnknown}  -- Not started yet
    },
    Actions = {
        QuestBegin{QuestId = X}  -- Start main quest
    }
}
```

#### 2. **Quest Progress Checker Pattern**
```lua
OnOneTimeEvent
{
    Conditions = {
        PlayerHasItem{ItemId = Y},           -- Player has required item
        QuestState{QuestId = X, State = StateActive}  -- Quest is active
    },
    Actions = {
        SetPlayerFlagTrue{Name = "QX_Completed"}  -- Mark as ready
    }
}
```

#### 3. **Quest Chain Pattern**
```lua
OnOneTimeEvent
{
    Conditions = {
        QuestState{QuestId = A, State = StateSolved},  -- Quest A done
        QuestState{QuestId = B, State = StateSolved},  -- Quest B done
        QuestState{QuestId = C, State = StateSolved},  -- Quest C done
    },
    Actions = {
        QuestSolve{QuestId = MainQuest},  -- Complete main quest
        QuestBegin{QuestId = NextQuest}   -- Start next quest
    }
}
```

#### 4. **Portal Activation Pattern**
```lua
OnOneTimeEvent
{
    Conditions = {
        QuestState{QuestId = FinalQuest, State = StateSolved},
        -- Other conditions...
    },
    Actions = {
        QuestBegin{QuestId = PortalQuest},  -- Open portal to next map
        SetGlobalFlagTrue{Name = "PortalToNextMapOpen"}
    }
}
```

---

## Global Campaign State

### Campaign Mode vs. Load Map Mode

SpellForce distinguishes between two modes:

**Campaign Mode** (Normal gameplay):
```lua
-- In GdsBase.lua
if not (Debug and Debug.Developer == 1) then
    OneTimeInitAction( SetGlobalFlagTrue{Name = "GDS_>>_GAME_IS_IN_CAMPAIGN_MODE!!!"} )
    OneTimeInitAction( SetGlobalFlagTrue{Name = "GDS_>>_GAME_BEGAN_ON_PLATFORM_P" .. PlatformId} )
end
```
- Quest progress persists
- Can travel between maps
- Story progresses linearly

**Load Map Mode** (Debug/testing):
```lua
if Debug and Debug.Developer == 1 then
    OneTimeInitAction( SetGlobalFlagTrue{Name = "GDS_>>_GAME_IS_IN_LOADMAP_MODE!!!"} )
end
```
- Load individual maps
- No campaign persistence
- For testing only

### Global Variables

**Variable Scopes**:

| Scope | Prefix | Persistence | Example |
|-------|--------|-------------|---------|
| **Global** | `gf` | All maps | `gfMarciaJonirIdleOn` |
| **Player** | `pf` | All maps | `pfFlagMarciaKnown` |
| **NPC** | `nf` | Single NPC | `nfHasMainquest_Npc2017_P9` |
| **Platform** | `vf` | Single map | `vfPortalOpen_P9` |
| **Item** | `gi` | Global | `giPlayerHasItemErdklinge` |
| **Reward** | `gr` | Global | `grMarcia1` |

### Tracking Platform Visits

```lua
-- Automatically set when player enters platform
OneTimeInitAction( SetGlobalFlagTrue{Name = "GDS_PlayerWasOnPlatform_P" .. PlatformId} )
```

**Usage**:
```lua
-- Check if player has been to Northern Windwalls
IsGlobalFlagTrue{Name = "GDS_PlayerWasOnPlatform_P9"}
```

---

## Quest Chains

### Multi-Platform Quest Chains

Some quests span multiple platforms. Example: **Amra and Lea Quest Chain**

**Platform 1 (Greyfell)**:
```lua
-- Quest 387-393: Amra and Lea questline begins
OnOneTimeEvent
{
    Conditions = {
        QuestState {QuestId = 387, State = StateActive},
    },
    Actions = {
        -- Player learns about Amra and Lea
    }
}
```

**Platform 6 (Wildland Pass)**:
```lua
-- Quest 160: Amra and Lea continue
OnOneTimeEvent
{
    Conditions = {
        QuestState{QuestId = 160, State = StateSolved},  -- Previous step
    },
    Actions = {
        QuestBegin{QuestId = 161}  -- Next step
    }
}
```

**Platform 63 (Greyfell)**:
```lua
-- Quest 159: Amra and Lea conclude
OnOneTimeEvent
{
    Conditions = {
        QuestState{QuestId = 159, State = StateSolved},
    },
    Actions = {
        SetRewardFlagTrue{Name = "AmraUndLea3Sentos"}  -- Quest complete!
    }
}
```

### Quest Chain Management

**Best Practices**:
1. **Use Sequential Quest IDs** where possible
2. **Set Global Flags** to track major milestones
3. **Check Platform Visits** before triggering cross-map quests
4. **Document Dependencies** in comments

**Example**:
```lua
-- QUEST CHAIN: "Journey to the North"
-- Q116 (P9) → Q121 (P9) → Q124 (P9) → Q125 (P10) → Q452 (P10)
-- Player must complete each quest in order

OnOneTimeEvent
{
    Conditions = {
        QuestState{QuestId = 116, State = StateSolved},  -- Previous quest
        IsGlobalFlagTrue{Name = "GDS_PlayerWasOnPlatform_P9"}  -- Been to P9
    },
    Actions = {
        QuestBegin{QuestId = 121}  -- Start next quest
    }
}
```

---

## Platform Transitions

### Portal System

Portals connect platforms. They can be:
- **Active**: Player can use immediately
- **Locked**: Requires quest completion
- **Conditional**: Opens based on flags/quests

### Portal Control Example

**Location**: `script/P9/n3258.lua` (Dwarf Gate)

```lua
-- Portal opens when flag is set
OnPortalEvent
{
    UpdateInterval = 15,
    X = 122, Y = 231,  -- Portal position
    Type = StadtTor,   -- City gate type
    OpenConditions = { 
        IsGlobalFlagTrue{Name = "Q112DwarfGateUnlocked", UpdateInterval = 15}
    },
    CloseConditions = {},  -- Never closes
    StayOpen = TRUE,
}
```

### Player Death and Respawn

**Platform-Specific Respawn Logic**:

```lua
-- Actions when player dies or leaves platform
OnPlayerDeathOrPlatformChange
{
    Actions = {
        -- Save state before platform change
        SetGlobalFlagTrue{Name = "PlayerDiedOnP9"},
    }
}

-- Actions when player respawns or re-enters platform
OnPlayerReviveOrPlatformEnter
{
    Actions = {
        -- Restore state when returning
        SetGlobalFlagFalse{Name = "PlayerDiedOnP9"},
    }
}
```

### Platform Load Order

```lua
-- In GdsBase.lua: PostScriptLoad() is called AFTER all NPCs load

function PostScriptLoad(_PlatformId)
    DefineGlobalConstants2()
    
    -- Load platform effects
    dofile("script/P" .. _PlatformId .. "/EffectsP" .. _PlatformId .. ".lua")
    
    -- Load RTS spawn logic
    dofile("script/P" .. _PlatformId .. "/ClanRtsSpawnP" .. _PlatformId .. ".lua")
    
    -- Set platform loaded flag
    SetGlobalFlagTrue{Name = "GDS_PlatformLoaded"}
end
```

---

## Cutscene System

### Cutscene Structure

Cutscenes are **scripted camera sequences** with dialog and actions.

**Example**: `script/P9/n2016_CutsceneMarciaEntry.lua`

```lua
-- Camera definitions (camera movement paths)
CameraMarciaEntryI = 
[[
    Camera:ScriptReset()
    Camera:ScriptAddSpline(0,25,1,"script\\p9\\n2016_CameraMarciaEntryI.lua")
    Camera:ScriptStart()
]]

CreateCutScene
{
    Name = "MarciaEntry", 
    CameraScript = "", 
    PlayOnlyOnce = TRUE,
    
    BeginConditions =
    {
        FigureAlive {NpcId = 2016},  -- Marcia must be alive
        FigureAlive {NpcId = 2017},  -- Jonir must be alive
        FigureInRange {X = 257, Y = 408, Range = 10, NpcId = 0},  -- Player in range
    },
    
    BeginActions =
    {
        SetGlobalFlagFalse {Name = "MarciaJonirIdleOn"},
        SetNoFightFlagTrue {NpcId = 0},        -- Player can't fight
        SetNoFightFlagTrue {NpcId = 2016},     -- Marcia can't fight
        SetNoFightFlagTrue {NpcId = 2017},     -- Jonir can't fight
        RemoveDialog {NpcId = 2016},           -- Disable dialogs
        RemoveDialog {NpcId = 2017},
    },
    
    TimedActions =
    {
        -- Time in GD Steps (10 = 1 second)
        [0] = {
            -- First 2 seconds: No camera
        },
        [20] = {
            ExecuteCameraScript{Script = CameraMarciaEntryI},  -- Start camera
            Goto {NpcId = 0, X = 257, Y = 382, WalkMode = Run},  -- Player walks
        },
        [160] = {
            LookAtFigure{NpcId = 0, Target = 2016},
            LookAtFigure{NpcId = 2016, Target = 0},
            CutSceneSay {
                Tag = "cutmaincharNW001", 
                NpcId = 0, 
                String = "Are you Marcia? The Order sends me..."
            },
        },
        [190] = {
            WaitForEndOfSpeech,
            ExecuteCameraScript{Script = CameraMarciaEntryII},
            CutSceneSay {
                Tag = "cutmarciaNW001",
                NpcId = 2016,
                String = "Are you the reinforcements? Finally! Where are your troops?"
            },
        },
        -- ... many more timed actions ...
        [1350] = {
            WaitForEndOfSpeech,
            SetGlobalFlagTrue {Name = "MarciaJonirIdleOn"},
            SetNoFightFlagFalse {NpcId = 0},
            SetNoFightFlagFalse {NpcId = 2016},
            SetNoFightFlagFalse {NpcId = 2017},
            RevealUnExplored {X = 353, Y = 452, Range = 10},  -- Reveal monument
            QuestSolve{QuestId = 126},        -- Complete entry quest
            QuestBegin{QuestId = 116},        -- Start main quest
            QuestBegin{QuestId = 114},        -- Start iron wagon quest
            QuestBegin{QuestId = 127},
            TransferResource{Resource = GoodIron, Amount = 400, Side = SideLight, Flag = Give},
            EnableDialog {NpcId = 2016},
            EnableDialog {NpcId = 2017},
        },
    },
}
```

### Cutscene Components

| Component | Purpose | Example |
|-----------|---------|---------|
| **BeginConditions** | When to trigger | `FigureInRange{...}` |
| **BeginActions** | Setup (disable controls) | `SetNoFightFlagTrue{...}` |
| **TimedActions** | Scripted sequence | Camera, dialog, movement |
| **EndActions** | Cleanup (re-enable controls) | `EnableDialog{...}` |

### Cutscene Best Practices

1. **Always disable player control**:
   ```lua
   SetNoFightFlagTrue {NpcId = 0}  -- Avatar
   ```

2. **Wait for speech to end**:
   ```lua
   WaitForEndOfSpeech  -- Before next dialog
   ```

3. **Re-enable controls at end**:
   ```lua
   SetNoFightFlagFalse {NpcId = 0}
   ```

4. **Use PlayOnlyOnce**:
   ```lua
   PlayOnlyOnce = TRUE  -- Don't replay cutscene
   ```

---

## Campaign Variables

### Variable Naming Conventions

**From `GdsVariables.lua`**:

```lua
-- Global Flag
function CreateGlobalFlagName(Name)
    return "gf" .. Name  -- e.g., "gfMarciaJonirIdleOn"
end

-- Player Flag
function CreatePlayerFlagName(Name)
    return "pf" .. Name  -- e.g., "pfFlagMarciaKnown"
end

-- NPC Flag (includes NPC ID and Platform ID)
function CreateNpcFlagName(Name)
    return "nf" .. Name .. "_Npc" .. tostring(NpcId) .. "_P" .. tostring(PlatformId)
    -- e.g., "nfHasMainquest_Npc2017_P9"
end

-- Platform Flag
function CreatePlatformFlagName(Name)
    return "vf" .. Name .. "_P" .. tostring(PlatformId)
    -- e.g., "vfPortalOpen_P9"
end

-- Item Flag
function CreateItemFlagName(Name)
    return "gi" .. Name  -- e.g., "giPlayerHasItemErdklinge"
end

-- Reward Flag
function CreateRewardFlagName(Name)
    return "gr" .. Name  -- e.g., "grMarcia1"
end
```

### Variable Scope and Persistence

| Variable Type | Persists Across Maps? | Persists After Death? | Use Case |
|---------------|----------------------|----------------------|----------|
| **Global Flag** | ✅ Yes | ✅ Yes | Story progress |
| **Player Flag** | ✅ Yes | ✅ Yes | Player choices |
| **NPC Flag** | ❌ No (per-platform) | ✅ Yes (if NPC respawns) | NPC state |
| **Platform Flag** | ❌ No (per-platform) | ✅ Yes | Map state |
| **Item Flag** | ✅ Yes | ✅ Yes | Quest items |

### Quest Item Tracking

SpellForce has a **special system** for tracking quest items:

```lua
-- In n0.lua (Platform Script)

-- Track when player finds quest item
OnQuestItemFound
{
    ItemId = 1234,                    -- Item ID
    ItemFlagName = "Erdklinge",       -- Quest item name
    Amount = 1,
    Actions = {
        -- Optional additional actions
    }
}

-- Track when player loses quest item
OnQuestItemLost
{
    ItemId = 1234,
    ItemFlagName = "Erdklinge",
    Amount = 1,
    Actions = {}
}

-- Remove quest item when flag is cleared
OnQuestItemRemove
{
    ItemId = 1234,
    ItemFlagName = "Erdklinge",
    Amount = 1,
    Actions = {}
}
```

**This automatically creates flags**:
- `giPlayerHasItemErdklinge` - Player currently has item
- `giPlayerHasHadItemErdklinge` - Player has had item at some point
- `giPlayerHasLostItemErdklinge` - Player lost the item

---

## Creating a Custom Campaign

### Step 1: Plan Your Campaign

Define:
- **Number of Maps**: How many platforms?
- **Story Arc**: What's the narrative?
- **Quest Flow**: Which quests lead where?
- **Map Order**: Linear or branching?

**Example Campaign Concept**:
```
"The Lost Kingdom"
- 3 Maps (P500, P501, P502)
- Story: Find 3 artifacts to unlock ancient kingdom
- Linear progression
```

---

### Step 2: Create Platform Scripts

**Create**: `script/P500/n0.lua`

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- Initialize campaign entry quest
OnOneTimeEvent
{
    Conditions = {
        QuestState{QuestId = 9000, State = StateUnknown}  -- Custom quest ID
    },
    Actions = {
        QuestBegin{QuestId = 9000},  -- "Welcome to the Lost Kingdom"
        -- Show intro message
        Outcry{
            Tag = "intro001",
            NpcId = 0,
            String = "You have arrived at the Lost Kingdom...",
            Color = ColorWhite
        },
    }
}

-- Quest: Find the First Artifact
OnOneTimeEvent
{
    Conditions = {
        QuestState{QuestId = 9000, State = StateActive},
        PlayerHasItem{ItemId = 5000}  -- Custom item: "Sun Medallion"
    },
    Actions = {
        QuestSolve{QuestId = 9000},
        QuestBegin{QuestId = 9001},  -- "Journey to the Moon Temple"
        SetGlobalFlagTrue{Name = "Artifact1Found"},
        SetRewardFlagTrue{Name = "Artifact1Reward"},
    }
}

-- Open portal to next map when quest complete
OnOneTimeEvent
{
    Conditions = {
        QuestState{QuestId = 9001, State = StateActive},
        IsGlobalFlagTrue{Name = "Artifact1Found"}
    },
    Actions = {
        QuestBegin{QuestId = 9002},  -- "Portal to Moon Temple"
        SetGlobalFlagTrue{Name = "PortalToP501Open"},
        RevealUnExplored{X = 200, Y = 200, Range = 15},  -- Reveal portal
    }
}

EndDefinition()
end
```

---

### Step 3: Create NPCs

**Create**: `script/P500/n5000.lua` (Quest Giver)

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

OnIdleGoHome{WalkMode = Walk, X = _X, Y = _Y, Direction = 2}
Respawn{WaitTime = 60}

-- Dialog: Give quest
OnBeginDialog{
    Conditions = {
        QuestState{QuestId = 9000, State = StateUnknown}
    },
    Actions = {
        Say{Tag = "elder001", String = "Traveler! The kingdom needs your help!"},
        Answer{Tag = "", String = "", AnswerId = 1},
    }
}

OnAnswer{1;
    Conditions = {},
    Actions = {
        Say{Tag = "elder002", String = "Find the Sun Medallion in the old ruins!"},
        OfferAnswer{Tag = "elder002PC", String = "I will find it.", AnswerId = 2},
    }
}

OnAnswer{2;
    Conditions = {},
    Actions = {
        QuestBegin{QuestId = 9000},
        RevealUnExplored{X = 300, Y = 400, Range = 10},  -- Reveal ruins
        Say{Tag = "elder003", String = "Thank you! The medallion is to the east."},
        Answer{Tag = "", String = "", AnswerId = 3},
    }
}

OnAnswer{3;
    Conditions = {},
    Actions = {
        EndDialog(),
    }
}

-- Dialog: Quest complete
OnBeginDialog{
    Conditions = {
        QuestState{QuestId = 9000, State = StateActive},
        PlayerHasItem{ItemId = 5000}  -- Has medallion
    },
    Actions = {
        Say{Tag = "elder004", String = "You found it! Incredible!"},
        Answer{Tag = "elder004PC", String = "Here is the medallion.", AnswerId = 10},
    }
}

OnAnswer{10;
    Conditions = {},
    Actions = {
        TransferItem{TakeItem = 5000, Amount = 1, Flag = Take},
        QuestSolve{QuestId = 9000},
        QuestBegin{QuestId = 9001},
        SetRewardFlagTrue{Name = "Artifact1Reward"},
        Say{Tag = "elder005", String = "Now find the Moon Temple!"},
        Answer{Tag = "", String = "", AnswerId = 11},
    }
}

OnAnswer{11;
    Conditions = {},
    Actions = {
        EndDialog(),
    }
}

EndDefinition()
end
```

---

### Step 4: Create Quest Rewards

**Edit**: `script/GdsQuestRewards.lua`

```lua
-- Add your campaign rewards
QuestRewardsP500 = 
{
    Artifact1Reward = { XP = {300}, Money = {Gold = 10} },
}

QuestRewardsP501 = 
{
    Artifact2Reward = { XP = {500}, Items = {5001} },  -- Special weapon
}

QuestRewardsP502 = 
{
    FinalBossReward = { XP = {1000}, Money = {Gold = 50}, Items = {5002} },
}
```

---

### Step 5: Create Portal

**Create**: `script/P500/n5001.lua` (Portal to P501)

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type, _PlatformId, _NpcId, _X, _Y)

OnPortalEvent
{
    UpdateInterval = 15,
    X = 200, Y = 200,  -- Portal position
    Type = MonumentPortal,  -- Portal type
    OpenConditions = { 
        IsGlobalFlagTrue{Name = "PortalToP501Open", UpdateInterval = 15}
    },
    CloseConditions = {},
    StayOpen = TRUE,
}

-- Dialog when portal opens
OnBeginDialog{
    Conditions = {
        IsGlobalFlagTrue{Name = "PortalToP501Open"},
        IsGlobalFlagFalse{Name = "PortalToP501Explained"}
    },
    Actions = {
        Say{
            Tag = "portal001",
            String = "(The portal glows with ancient power. It will take you to the Moon Temple.)"
        },
        Answer{Tag = "", String = "", AnswerId = 1},
    }
}

OnAnswer{1;
    Conditions = {},
    Actions = {
        SetGlobalFlagTrue{Name = "PortalToP501Explained"},
        EndDialog(),
    }
}

EndDefinition()
end
```

---

### Step 6: Link Maps Together

**In P501 (Moon Temple)**:

```lua
-- In script/P501/n0.lua

-- Check if player arrived from P500
OnOneTimeEvent
{
    Conditions = {
        IsGlobalFlagTrue{Name = "GDS_PlayerWasOnPlatform_P500"},  -- Been to P500
        QuestState{QuestId = 9002, State = StateUnknown}
    },
    Actions = {
        QuestBegin{QuestId = 9002},  -- "Find the Moon Crystal"
        Outcry{
            NpcId = 0,
            String = "You have arrived at the Moon Temple...",
            Color = ColorWhite
        },
    }
}
```

---

### Step 7: Test Your Campaign

1. **Place Maps**: Put map files in `map/` directory
2. **Test Each Map**: Use Load Map mode to test individually
3. **Test Campaign Flow**: Play through entire sequence
4. **Check Quest Chains**: Verify quests link correctly
5. **Test Portals**: Ensure transitions work
6. **Balance Rewards**: Adjust XP/items as needed

---

## Campaign Design Best Practices

### 1. **Clear Quest Progression**
```lua
-- Always provide clear next steps
Actions = {
    QuestSolve{QuestId = CurrentQuest},
    QuestBegin{QuestId = NextQuest},
    RevealUnExplored{X = NextObjective, ...},  -- Show where to go
}
```

### 2. **Handle Quest Failures**
```lua
-- Allow quest retry if player fails
OnToggleEvent
{
    OnConditions = {
        -- Quest failed condition
    },
    OnActions = {
        QuestChangeState{QuestId = X, State = StateUnknown},
        QuestBegin{QuestId = X},  -- Restart quest
    }
}
```

### 3. **Track Platform Visits**
```lua
-- Check if player has unlocked previous content
IsGlobalFlagTrue{Name = "GDS_PlayerWasOnPlatform_P500"}
```

### 4. **Use Cutscenes Sparingly**
- Only for major story moments
- Keep them short (< 2 minutes)
- Always allow skipping (if possible)

### 5. **Test Multiplayer Compatibility**
- Avoid random() in critical paths (causes desyncs)
- Use deterministic logic
- Test in co-op mode

---

## Campaign Debugging

### Debug Commands

```lua
-- Add debug init actions (only in debug mode)
DebugInitAction( SetGlobalFlagTrue{Name = "DebugSkipToPortal"} )

-- Show debug text
if _DEBUG == 1 then
    OneTimeInitAction( ShowDebugText{String = "Debug: Campaign started on P500"} )
end
```

### Debug Flags

```lua
-- Check if in debug mode
if Debug and Debug.Developer == 1 then
    -- Debug-only code
    DebugInitAction( QuestSolve{QuestId = 9000} )  -- Auto-complete quest
end
```

### Logging

```lua
-- Log quest state
DebugLog{String = "Quest 9000 started on platform " .. PlatformId}
```

---

## Advanced Campaign Features

### Dynamic Quest Chains

```lua
-- Branch based on player choice
OnToggleEvent
{
    OnConditions = {
        IsPlayerFlagTrue{Name = "PlayerChosePathA"}
    },
    OnActions = {
        QuestBegin{QuestId = PathAQuest}
    },
    OffConditions = {
        IsPlayerFlagTrue{Name = "PlayerChosePathB"}
    },
    OffActions = {
        QuestBegin{QuestId = PathBQuest}
    }
}
```

### Time-Limited Quests

```lua
-- Quest expires after time limit
OnOneTimeEvent
{
    Conditions = {
        QuestState{QuestId = X, State = StateActive},
        IsGlobalTimeElapsed{Name = "QuestXTimer", Seconds = 600}  -- 10 minutes
    },
    Actions = {
        QuestFail{QuestId = X},
        Outcry{NpcId = 0, String = "Quest failed! Time ran out."}
    }
}
```

### Companion Systems

```lua
-- Hero joins party
OnFollowForever
{
    Target = Avatar,  -- Follow player
    Conditions = {
        QuestState{QuestId = RecruitQuest, State = StateSolved}
    },
    Actions = {
        ChangeFigureOwner{NpcId = HeroNpcId, Owner = OwnerPlayer}
    }
}
```

---

## Conclusion

SpellForce's campaign system is **sophisticated and modular**:

✅ **Platform-based**: Each map is independent yet connected  
✅ **Quest-driven**: Story progresses through quest chains  
✅ **Persistent state**: Variables carry across maps  
✅ **Cutscene integration**: Cinematic storytelling  
✅ **Flexible architecture**: Easy to add new maps  

With this guide, you can:
- Understand how the campaign works
- Create custom campaigns
- Link maps together
- Design quest chains
- Script cutscenes

**Happy Campaign Building!** 🎮⚔️🗺️

---

## Reference Files

### Key Campaign Files
1. `script/GdsBase.lua` - Core system initialization
2. `script/GdsGlobalEventSystem.lua` - Global event handlers
3. `script/GdsVariables.lua` - Variable management
4. `script/GdsQuestRewards.lua` - Reward definitions
5. `script/p1/n0.lua` - Example platform script
6. `script/P9/n2016_CutsceneMarciaEntry.lua` - Example cutscene

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-21  
**Author**: SpellForce Modding Community
