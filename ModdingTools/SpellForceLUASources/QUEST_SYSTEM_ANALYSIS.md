# SpellForce Quest System Analysis - For Quest Editor Development

## Overview

This document provides a comprehensive analysis of the SpellForce quest system, including quest requirements, rewards, dialogue systems, and player choices. This analysis is specifically designed to inform the development of a quest editor for the SpellForce Lua system.

---

## QUEST SYSTEM ARCHITECTURE

### Core Quest Structure

Every quest in SpellForce follows a standardized state machine pattern:

```lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

OnOneTimeEvent
{
    Conditions = {
        -- Quest trigger conditions
    },
    Actions = {
        -- Quest activation actions
    }
}

EndDefinition()
end
```

### Quest States

The quest system uses **5 primary states**:

| State | Constant | Description | Usage |
|-------|----------|-------------|-------|
| **Unknown** | `StateUnknown` | Quest not yet discovered | Initial state, hidden from player |
| **Known** | `StateKnown` | Quest discovered but not active | Quest in journal, not started |
| **Active** | `StateActive` | Quest currently in progress | Main quest state |
| **Solved** | `StateSolved` | Quest completed successfully | End state, rewards given |
| **Unsolvable** | `StateUnsolvable` | Quest failed or cannot be completed | End state, no rewards |

---

## QUEST REQUIREMENTS SYSTEM

### Condition Types

#### 1. Quest State Conditions
```lua
Conditions = {
    QuestState{QuestId = 528, State = StateActive},
    QuestState{QuestId = 124, State = StateUnknown}
}
```

#### 2. Global Flag Conditions
```lua
Conditions = {
    IsGlobalFlagTrue{Name = "AngebotAngenommenP110"},
    IsGlobalFlagFalse{Name = "VertragsBruchP110"},
    IsGlobalFlagTrue{Name = "OpenFinalGateP110"}
}
```

#### 3. Item Conditions
```lua
Conditions = {
    PlayerHasItem{ItemId = 3955},
    PlayerHasItem{ItemId = 3957},
    Negated(PlayerHasItem{ItemId = 3955})
}
```

#### 4. Player Conditions
```lua
Conditions = {
    IsPlayer{Player = "Player1"},
    PlayerInArea{X = 100, Y = 200, Range = 50}
}
```

#### 5. Entity Conditions
```lua
Conditions = {
    FigureDead{FigureId = 6045},
    BuildingDestroyed{BuildingId = 1234},
    NpcExists{NpcId = 6043}
}
```

#### 6. Time Conditions
```lua
Conditions = {
    GameTimeGreaterThan{Hours = 12},
    DayTime{IsDay = true}
}
```

### Complex Condition Logic

#### AND Logic (Default)
```lua
Conditions = {
    IsGlobalFlagTrue{Name = "QuestStarted"},
    PlayerHasItem{ItemId = 1234},
    FigureDead{FigureId = 5678}
}
-- All conditions must be true
```

#### OR Logic
```lua
OnOneTimeEvent
{
    Conditions = {
        IsGlobalFlagTrue{Name = "Path1Complete"}
    },
    Actions = {
        -- Path 1 actions
    }
}

OnOneTimeEvent
{
    Conditions = {
        IsGlobalFlagTrue{Name = "Path2Complete"}
    },
    Actions = {
        -- Path 2 actions
    }
}
```

#### NOT Logic (Negation)
```lua
Conditions = {
    IsGlobalFlagTrue{Name = "MainQuestActive"},
    Negated(IsGlobalFlagTrue{Name = "SideQuestComplete"})
}
```

---

## QUEST REWARD SYSTEM

### Reward Types

#### 1. Item Rewards
```lua
Actions = {
    TransferItem{GiveItem = 2648, Flag = Give},
    TransferItem{GiveItem = 3956, Flag = Give},
    TransferItem{GiveItem = 4079, Flag = Give},
    TransferItem{GiveItem = 28, Flag = Give}
}
```

#### 2. Item Removal (Quest Items)
```lua
Actions = {
    TransferItem{TakeItem = 3955, Flag = Take},
    TransferItem{TakeItem = 3957, Flag = Take}
}
```

#### 3. Quest State Changes
```lua
Actions = {
    QuestBegin{QuestId = 124},
    QuestSolve{QuestId = 123},
    QuestBegin{QuestId = 125},
    QuestBegin{QuestId = 139}
}
```

#### 4. Global Flag Updates
```lua
Actions = {
    SetGlobalFlagTrue{Name = "OpenFinalGateP110"},
    SetGlobalFlagTrue{Name = "LenaHintOutcryP110"},
    SetGlobalFlagFalse{Name = "TemporaryFlag"}
}
```

#### 5. Variable Updates
```lua
Actions = {
    UpdateVariable{Name = "PlayerGold", Value = 1000},
    UpdateVariable{Name = "PlayerXP", Value = 500}
}
```

#### 6. Entity Spawning
```lua
Actions = {
    SpawnFigure{FigureId = 6045, X = 100, Y = 200},
    SpawnBuilding{BuildingId = 1234, X = 150, Y = 250}
}
```

### Reward Pattern Examples

#### Simple Item Reward
```lua
OnOneTimeEvent
{
    Conditions = {
        PlayerHasItem{ItemId = 1234},
        IsGlobalFlagTrue{Name = "QuestTargetReached"}
    },
    Actions = {
        TransferItem{TakeItem = 1234, Flag = Take},
        TransferItem{GiveItem = 5678, Flag = Give},
        QuestSolve{QuestId = 100},
        UpdateVariable{Name = "PlayerXP", Value = 1000}
    }
}
```

#### Multi-Choice Reward
```lua
OnOneTimeEvent
{
    Conditions = {
        IsGlobalFlagTrue{Name = "PlayerChoiceA"}
    },
    Actions = {
        TransferItem{GiveItem = 2001, Flag = Give}, -- Reward A
        QuestSolve{QuestId = 101}
    }
}

OnOneTimeEvent
{
    Conditions = {
        IsGlobalFlagTrue{Name = "PlayerChoiceB"}
    },
    Actions = {
        TransferItem{GiveItem = 2002, Flag = Give}, -- Reward B
        QuestSolve{QuestId = 101}
    }
}
```

---

## DIALOGUE SYSTEM ANALYSIS

### Dialogue Structure

#### Basic Dialogue Pattern
```lua
OnBeginDialog{
    Conditions = {
        -- Dialogue availability conditions
    },
    Actions = {
        Say{Tag = "npc_001", String = "Hello, adventurer!"},
        Answer{Tag = "player_001", String = "What can you tell me?", AnswerId = 1},
        Answer{Tag = "player_002", String = "Goodbye", AnswerId = 99}
    }
}
```

#### Answer Response Pattern
```lua
OnAnswer{1;
    Conditions = {
        -- Conditions for this answer to be available
    },
    Actions = {
        Say{Tag = "npc_002", String = "I can tell you about the ancient ruins..."},
        Answer{Tag = "player_003", String = "Tell me more", AnswerId = 2},
        Answer{Tag = "player_004", String = "Not interested", AnswerId = 99}
    }
}
```

### Player Choice System

#### Choice Availability Conditions
```lua
OnAnswer{2;
    Conditions = {
        PlayerHasItem{ItemId = 1234}, -- Only show if player has item
        IsGlobalFlagTrue{Name = "KnowsAboutRuins"}
    },
    Actions = {
        Say{Tag = "npc_003", String = "Since you have the artifact..."},
        Answer{Tag = "player_005", String = "I'll help you", AnswerId = 3},
        Answer{Tag = "player_006", String = "I can't help", AnswerId = 4}
    }
}
```

#### Consequence System
```lua
OnAnswer{3;
    Conditions = {},
    Actions = {
        SetGlobalFlagTrue{Name = "PlayerAcceptedQuest"},
        TransferItem{GiveItem = 5678, Flag = Give},
        QuestBegin{QuestId = 200},
        Say{Tag = "npc_004", String = "Thank you for your help!"},
        Answer{Tag = "player_007", String = "[Continue]", AnswerId = 99}
    }
}

OnAnswer{4;
    Conditions = {},
    Actions = {
        SetGlobalFlagTrue{Name = "PlayerRejectedQuest"},
        Say{Tag = "npc_005", String = "I understand. Come back if you change your mind."},
        EndDialog()
    }
}
```

### Complex Dialogue Example

From the actual game (P110/n6045.lua):

```lua
OnBeginDialog{
    Conditions = {},
    Actions = {
        Say{Tag = "sternenpriester110_001", String = "Macht schon, bringt es hinter Euch, Lichtgläubiger!"},
        Answer{Tag = "sternenpriester110_002PC", String = "Tot nützt Ihr mir nichts. Aber vielleicht habt Ihr etwas anzubieten, das mir Euer Leben wert ist?", AnswerId = 1},
    }
}

OnAnswer{1;
    Conditions = {},
    Actions = {
        Say{Tag = "sternenpriester110_003", String = "Was wäre, wenn ich Euch sage, dass es geheime Gänge in die anderen Stadtteile gibt?"},
        Answer{Tag = "sternenpriester110_004PC", String = "Sprecht weiter.", AnswerId = 2},
    }
}

OnAnswer{2;
    Conditions = {},
    Actions = {
        Say{Tag = "sternenpriester110_005", String = "Die Gänge wurden von Ulkar Kahn angelegt, bevor die Sonnenpriester ihn ermordet haben. Sie führen in die Sonnen- und Mondstadt. Aber sie sind magisch verschlossen."},
        Answer{Tag = "sternenpriester110_006PC", String = "Was nützen sie mir dann?", AnswerId = 3},
    }
}

OnAnswer{3;
    Conditions = {},
    Actions = {
        Say{Tag = "sternenpriester110_007", String = "Wartet! Nur die Hand Kahns kann die Tore öffnen! Kahn ist tot, aber seine Hand befindet sich in unserem Besitz!"},
        Answer{Tag = "", String = "", AnswerId = 4},
    }
}

OnAnswer{4;
    Conditions = {},
    Actions = {
        Say{Tag = "sternenpriester110_009", String = "Man weiß nie, wann man sie brauchen könnte. Aber nun ist es wohl soweit."},
        Answer{Tag = "sternenpriester110_008PC", String = "Gut, gebt sie mir und Ihr sollt verschont bleiben.", AnswerId = 5},
    }
}

OnAnswer{5;
    Conditions = {},
    Actions = {
        TransferItem{GiveItem = 2648, Flag = Give},  -- Reward: Khan's Hand
        RemoveDialog{NpcId = self},
        Say{Tag = "", String = ""},
        Answer{Tag = "", String = "", AnswerId = 6},
    }
}
```

---

## QUEST PATTERNS AND TYPES

### 1. Kill Quests
```lua
OnOneTimeEvent
{
    Conditions = {
        FigureDead{FigureId = 6045}
    },
    Actions = {
        QuestSolve{QuestId = 300},
        TransferItem{GiveItem = 7001, Flag = Give},
        UpdateVariable{Name = "PlayerXP", Value = 500}
    }
}
```

### 2. Collection Quests
```lua
OnOneTimeEvent
{
    Conditions = {
        PlayerHasItem{ItemId = 3001},
        PlayerHasItem{ItemId = 3002},
        PlayerHasItem{ItemId = 3003}
    },
    Actions = {
        TransferItem{TakeItem = 3001, Flag = Take},
        TransferItem{TakeItem = 3002, Flag = Take},
        TransferItem{TakeItem = 3003, Flag = Take},
        QuestSolve{QuestId = 301},
        TransferItem{GiveItem = 8001, Flag = Give}
    }
}
```

### 3. Escort Quests
```lua
OnOneTimeEvent
{
    Conditions = {
        IsGlobalFlagTrue{Name = "EscortTargetReached"},
        NpcExists{NpcId = 7001}
    },
    Actions = {
        QuestSolve{QuestId = 302},
        SetGlobalFlagTrue{Name = "EscortComplete"}
    }
}
```

### 4. Dialogue Choice Quests
```lua
OnOneTimeEvent
{
    Conditions = {
        IsGlobalFlagTrue{Name = "PlayerChoiceDiplomacy"}
    },
    Actions = {
        QuestSolve{QuestId = 303},
        SetGlobalFlagTrue{Name = "PeacefulResolution"},
        TransferItem{GiveItem = 9001, Flag = Give} -- Diplomacy reward
    }
}

OnOneTimeEvent
{
    Conditions = {
        IsGlobalFlagTrue{Name = "PlayerChoiceCombat"}
    },
    Actions = {
        QuestSolve{QuestId = 303},
        SetGlobalFlagTrue{Name = "CombatResolution"},
        TransferItem{GiveItem = 9002, Flag = Give} -- Combat reward
    }
}
```

---

## TECHNICAL IMPLEMENTATION DETAILS

### File Organization

#### Quest File Naming Convention
- **Main Quests**: `n[QuestId].lua` (e.g., `n6045.lua`)
- **Cutscenes**: `n[QuestId]_Cutscene[Name].lua`
- **Camera Scripts**: `n[QuestId]_Camera[Name].lua`
- **Campaign Controllers**: `n0.lua`

#### Directory Structure
```
script/
├── P[Number]/          # Campaign directories
│   ├── n0.lua          # Campaign controller
│   ├── n[QuestId].lua  # Individual quest files
│   ├── Ai.lua          # Campaign AI
│   └── EffectsP[Number].lua
├── p[Number]/          # Side quest directories
└── Gds*.lua           # Core system files
```

### Quest ID System

#### ID Ranges by Campaign
- **P0-P30**: Tutorial and early game (1-999)
- **P31-P116**: Main campaign (1000-5999)
- **P200-P207**: Breath of Winter (6000-7999)
- **P208-P213**: Shadow of Phoenix (8000-9999)

#### Item ID Integration
- **Items**: Referenced by database ID from `sql_item.lua`
- **Figures**: Referenced by entity ID from `sql_unit.lua`
- **Buildings**: Referenced by entity ID from `sql_building.lua`

---

## QUEST EDITOR SPECIFICATIONS

### Core Data Structures

#### Quest Definition
```lua
Quest = {
    id = 1234,
    name = "Quest Name",
    description = "Quest description",
    type = "kill|collection|escort|dialogue|explore",
    campaign = "P110",
    prerequisites = {
        {type = "quest", questId = 1233, state = "solved"},
        {type = "level", level = 10},
        {type = "flag", flagName = "PreviousQuestComplete"}
    },
    objectives = {
        {
            type = "kill",
            targetId = 6045,
            count = 1,
            description = "Kill the Star Priest"
        }
    },
    rewards = {
        {type = "item", itemId = 2648, count = 1},
        {type = "xp", amount = 1000},
        {type = "gold", amount = 500}
    },
    dialogue = {
        -- Dialogue tree structure
    }
}
```

#### Dialogue Node
```lua
DialogueNode = {
    id = "node_001",
    npcText = "Hello, adventurer!",
    npcTag = "npc_001",
    conditions = {
        {type = "quest", questId = 1234, state = "active"}
    },
    answers = {
        {
            id = 1,
            text = "What can you tell me?",
            tag = "player_001",
            conditions = {},
            actions = {
                {type = "setFlag", flagName = "AskedForInfo", value = true}
            },
            nextNode = "node_002"
        },
        {
            id = 99,
            text = "Goodbye",
            tag = "player_goodbye",
            conditions = {},
            actions = {},
            nextNode = "end"
        }
    }
}
```

### Editor Features Required

#### 1. Quest Creation Wizard
- **Quest Type Selection**: Kill, Collection, Escort, Dialogue, Explore
- **Basic Information**: Name, description, campaign assignment
- **Prerequisites**: Quest chains, level requirements, flag conditions
- **Objectives**: Target selection, count requirements
- **Rewards**: Item selection, XP, gold amounts

#### 2. Visual Quest Editor
- **Flowchart View**: Quest state visualization
- **Condition Builder**: Visual condition creation
- **Action Builder**: Visual action composition
- **Dialogue Tree Editor**: Node-based dialogue creation
- **Preview System**: Real-time quest logic validation

#### 3. Database Integration
- **Item Browser**: Search and select from `sql_item.lua`
- **Entity Browser**: Select figures, buildings, objects
- **Quest Browser**: View existing quests for dependencies
- **Flag Manager**: Create and manage global flags

#### 4. Code Generation
- **Lua File Generation**: Generate proper quest files
- **Validation System**: Check for syntax and logic errors
- **Integration Testing**: Test quest in isolation
- **Export System**: Generate mod packages

### Validation Rules

#### Quest Validation
```lua
function ValidateQuest(quest)
    local errors = {}
    
    -- Check required fields
    if not quest.id then
        table.insert(errors, "Quest ID is required")
    end
    
    if not quest.name or quest.name == "" then
        table.insert(errors, "Quest name is required")
    end
    
    -- Validate objectives
    if #quest.objectives == 0 then
        table.insert(errors, "Quest must have at least one objective")
    end
    
    -- Validate rewards
    if #quest.rewards == 0 then
        table.insert(errors, "Quest should have at least one reward")
    end
    
    -- Check for circular dependencies
    if HasCircularDependency(quest) then
        table.insert(errors, "Quest has circular dependencies")
    end
    
    return errors
end
```

#### Dialogue Validation
```lua
function ValidateDialogue(dialogue)
    local errors = {}
    
    -- Check for orphaned nodes
    local orphaned = FindOrphanedNodes(dialogue)
    for _, nodeId in ipairs(orphaned) do
        table.insert(errors, "Dialogue node " .. nodeId .. " is orphaned")
    end
    
    -- Check for infinite loops
    if HasInfiniteLoop(dialogue) then
        table.insert(errors, "Dialogue contains infinite loop")
    end
    
    -- Validate answer conditions
    for _, node in ipairs(dialogue.nodes) do
        for _, answer in ipairs(node.answers) do
            if not ValidateConditions(answer.conditions) then
                table.insert(errors, "Invalid conditions in answer " .. answer.id)
            end
        end
    end
    
    return errors
end
```

---

## BEST PRACTICES FOR QUEST CREATION

### 1. Quest Design Principles
- **Clear Objectives**: Players should understand what to do
- **Meaningful Choices**: Dialogue options should have consequences
- **Progressive Difficulty**: Quest chains should increase in complexity
- **Proper Rewards**: Rewards should match quest difficulty
- **Logical Flow**: Quest prerequisites should make story sense

### 2. Technical Guidelines
- **Unique IDs**: Use unique quest, flag, and variable names
- **Consistent Naming**: Follow naming conventions for tags and flags
- **Error Handling**: Include fallback conditions for edge cases
- **Performance**: Avoid complex nested conditions when possible
- **Documentation**: Comment complex quest logic

### 3. Dialogue Guidelines
- **Natural Language**: Write dialogue that sounds natural
- **Player Agency**: Provide meaningful choices
- **Consequences**: Ensure choices have noticeable effects
- **Branching Logic**: Use dialogue trees for complex conversations
- **Localization**: Use tags for multi-language support

---

## INTEGRATION EXAMPLES

### Complete Quest Example
```lua
-- File: script/P110/n1234.lua
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

OnOneTimeEvent
{
    Conditions = {
        IsGlobalFlagTrue{Name = "PreviousQuestComplete"},
        PlayerHasItem{ItemId = 1001}
    },
    Actions = {
        QuestBegin{QuestId = 1234},
        SetGlobalFlagTrue{Name = "Quest1234Started"}
    }
}

OnOneTimeEvent
{
    Conditions = {
        QuestState{QuestId = 1234, State = StateActive},
        FigureDead{FigureId = 6045}
    },
    Actions = {
        QuestSolve{QuestId = 1234},
        TransferItem{GiveItem = 2001, Flag = Give},
        UpdateVariable{Name = "PlayerXP", Value = 1000},
        SetGlobalFlagTrue{Name = "Quest1234Complete"}
    }
}

EndDefinition()
end
```

### Dialogue Integration Example
```lua
-- File: script/P110/n6046.lua
OnBeginDialog{
    Conditions = {
        QuestState{QuestId = 1234, State = StateActive}
    },
    Actions = {
        Say{Tag = "npc_6046_001", String = "I need your help with something."},
        Answer{Tag = "player_001", String = "What do you need?", AnswerId = 1},
        Answer{Tag = "player_002", String = "I'm busy", AnswerId = 99}
    }
}

OnAnswer{1;
    Conditions = {},
    Actions = {
        Say{Tag = "npc_6046_002", String = "There's a monster terrorizing the village."},
        Answer{Tag = "player_003", String = "I'll help you", AnswerId = 2},
        Answer{Tag = "player_004", String = "Not my problem", AnswerId = 99}
    }
}

OnAnswer{2;
    Conditions = {},
    Actions = {
        SetGlobalFlagTrue{Name = "PlayerAcceptedQuest"},
        Say{Tag = "npc_6046_003", String = "Thank you! The monster is to the east."},
        EndDialog()
    }
}
```

---

## CONCLUSION

This analysis provides a comprehensive foundation for developing a quest editor for the SpellForce Lua system. The key insights are:

### Technical Architecture
- **State-based quest system** with 5 defined states
- **Condition-action paradigm** for quest logic
- **Integrated dialogue system** with player choices
- **Database-driven content** for items and entities

### Editor Requirements
- **Visual quest flow editor** for state management
- **Dialogue tree editor** with choice consequences
- **Database integration** for content selection
- **Validation system** for error prevention
- **Code generation** for proper Lua output

### Implementation Strategy
1. **Start with core quest creation** (objectives, rewards, conditions)
2. **Add dialogue system** with choice consequences
3. **Integrate database browsers** for content selection
4. **Implement validation** and code generation
5. **Add advanced features** (quest chains, complex logic)

The SpellForce quest system is well-structured and follows consistent patterns, making it ideal for editor development. The state-based approach and clear separation of concerns provide a solid foundation for building comprehensive quest creation tools.
