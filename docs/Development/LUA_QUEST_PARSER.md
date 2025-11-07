# Lua Quest Parser Documentation

## Overview

The **Lua Quest Parser** is a bidirectional parser for SpellForce quest Lua scripts. It can:

1. **READ** existing quest Lua files and extract quest data
2. **WRITE** new quest Lua files from structured quest data

This enables the Quest Creator to generate complete, working quest scripts that can be used in SpellForce mods.

## Why Do We Need This?

As discovered through analyzing the CFF file structure:

### What's in the CFF File:
- ✅ Quest hierarchy (parent-child relationships)
- ✅ Quest names and descriptions (localized text)
- ✅ Quest IDs and references
- ✅ Basic structure

### What's in Lua Scripts:
- ✅ Quest objectives ("Kill 10 wolves", "Collect 5 items")
- ✅ Quest requirements (level, previous quests, items)
- ✅ Quest rewards (XP, gold, items)
- ✅ Quest giver NPC assignments
- ✅ Dialogue branching logic and player choices
- ✅ Quest state management and triggers

**The CFF is the database. The Lua is the game logic.**

## Architecture

```
┌─────────────────────┐
│   Quest Creator     │  ← User creates quest in GUI
│   (GUI Interface)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    QuestData        │  ← Structured data object
│  (Python Class)     │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌─────────┐  ┌─────────┐
│  READ   │  │  WRITE  │
│ Parser  │  │ Parser  │
└────┬────┘  └────┬────┘
     │            │
     ▼            ▼
┌─────────────────────┐
│   Lua Script File   │  ← Actual game script
│   quest_1001.lua    │
└─────────────────────┘
```

## Data Structures

### QuestData

Main quest container:

```python
@dataclass
class QuestData:
    quest_id: int                           # Unique quest ID
    quest_name: str                         # Quest name
    description: str = ""                   # Quest description
    platform: str = "P7"                    # Map/platform (P7, P8, etc.)
    npc_id: Optional[int] = None           # Quest giver NPC ID
    
    # Quest flow
    objectives: List[QuestObjective] = []   # What to do
    requirements: List[QuestRequirement] = []  # Prerequisites
    rewards: QuestReward                    # Rewards
    
    # Dialogues
    dialogues: List[QuestDialogue] = []
    
    # Raw Lua (for advanced users)
    init_event: Optional[str] = None
    complete_event: Optional[str] = None
    custom_events: List[str] = []
    
    # Metadata
    author: str = ""
    notes: str = ""
```

### QuestObjective

What the player needs to do:

```python
@dataclass
class QuestObjective:
    description: str                        # Human-readable description
    objective_type: str = "Unknown"        # Kill, Collect, Talk, Escort, Reach
    target: Optional[str] = None           # Target entity/item
    count: int = 1                         # How many
    lua_condition: Optional[str] = None    # Raw Lua for complex objectives
```

**Supported Types:**
- **Kill**: Defeat enemies
- **Collect**: Gather items
- **Talk**: Speak with NPC
- **Escort**: Protect/guide NPC
- **Reach**: Arrive at location
- **Quest**: Complete another quest

### QuestRequirement

Prerequisites to accept the quest:

```python
@dataclass
class QuestRequirement:
    description: str                        # Human-readable description
    requirement_type: str = "Unknown"      # Level, Quest, Item, Flag
    value: Optional[Any] = None            # Requirement value
    lua_condition: Optional[str] = None    # Raw Lua for complex requirements
```

**Supported Types:**
- **Level**: Minimum player level
- **Quest**: Previous quest must be completed
- **Item**: Player must have item
- **Flag**: Game flag must be set

### QuestReward

What the player receives:

```python
@dataclass
class QuestReward:
    xp: int = 0                            # Experience points
    gold: int = 0                          # Gold
    silver: int = 0                        # Silver
    copper: int = 0                        # Copper
    items: List[int] = []                  # Item IDs
    flags: List[str] = []                  # Flags to set
```

### QuestDialogue

Dialogue nodes:

```python
@dataclass
class QuestDialogue:
    dialogue_id: str                       # Unique dialogue ID
    speaker: str = "NPC"                   # NPC or Player
    text: str = ""                         # Dialogue text
    is_player_choice: bool = False         # Is this a player option?
    conditions: List[str] = []             # When to show
    actions: List[str] = []                # What happens
    next_dialogues: List[str] = []         # Branching options
```

## Usage Examples

### Example 1: Generate Lua from Quest Data

```python
from TirganachReloaded.cff_editor.lua_parser import (
    LuaQuestParser,
    QuestData,
    QuestObjective,
    QuestRequirement,
    QuestReward
)

# Create quest
quest = QuestData(
    quest_id=1001,
    quest_name="The Bandit Problem",
    description="Help the village by eliminating bandits",
    platform="P7",
    npc_id=205
)

# Add requirements
quest.requirements.append(
    QuestRequirement(
        description="Reach level 5",
        requirement_type="Level",
        value=5
    )
)

# Add objectives
quest.objectives.append(
    QuestObjective(
        description="Defeat the Bandit Leader",
        objective_type="Kill",
        target="BanditLeader"
    )
)

quest.objectives.append(
    QuestObjective(
        description="Collect stolen goods",
        objective_type="Collect",
        target="150",  # Item ID
        count=5
    )
)

# Set rewards
quest.rewards = QuestReward(
    xp=500,
    gold=25,
    silver=50,
    items=[301, 302]
)

# Generate Lua script
parser = LuaQuestParser()
lua_script = parser.generate_lua_script(quest)

# Save to file
parser.save_to_file(quest, "quest_1001.lua")
```

**Generated Output:**

```lua
-- Generated Quest Script: The Bandit Problem
-- Quest ID: 1001
-- Platform: P7
--
-- This script was generated by the SpellForce CFF Editor

function CreateStateMachine(_Type, _PlatformId, _NpcId, _X, _Y)
BeginDefinition(_Type, _PlatformId, _NpcId, _X, _Y)

--------------------------------------------------------------------------
-- QUEST: THE BANDIT PROBLEM
-- ID: 1001
--------------------------------------------------------------------------

-- Quest Initialization
OnOneTimeEvent
{
    EventName = "Init_TheBanditProblem",
    Conditions =
    {
        AvatarLevel{Level = 5}
    },
    Actions =
    {
        QuestBegin{QuestId = 1001},
        Outcry{
            NpcId = 205,
            String = "Help the village by eliminating bandits",
            Color = ColorYellow
        }
    }
}

-- Quest Completion
OnOneTimeEvent
{
    EventName = "Complete_TheBanditProblem",
    Conditions =
    {
        QuestState{QuestId = 1001, State = StateActive},
        FigureIsDead{Tag = "BanditLeader"},
        PlayerHasItem{ItemId = 150, Amount = 5}
    },
    Actions =
    {
        QuestSolve{QuestId = 1001},
        SetRewardFlagTrue{Name = "Quest1001Reward"},
        Outcry{
            NpcId = 0,
            String = "Quest completed: The Bandit Problem!",
            Color = ColorGreen
        }
    }
}

-- Quest Rewards (typically in GdsQuestRewards.lua)
-- Quest1001Reward = {
--     XP = {500},
--     Money = {Gold = 25, Silver = 50, Copper = 0},
--     Items = {301, 302}
-- }

EndDefinition()
end
```

### Example 2: Parse Existing Lua File

```python
from TirganachReloaded.cff_editor.lua_parser import parse_quest_file

# Parse existing quest file
quests = parse_quest_file("path/to/quest_script.lua")

# Access quest data
for quest in quests:
    print(f"Quest ID: {quest.quest_id}")
    print(f"Name: {quest.quest_name}")
    print(f"Objectives: {len(quest.objectives)}")
    
    for obj in quest.objectives:
        print(f"  - {obj.description}")
    
    print(f"Rewards: {quest.rewards.xp} XP")
```

### Example 3: Create Example Quest

```python
from TirganachReloaded.cff_editor.lua_parser import create_example_quest

# Get a pre-made example quest
quest = create_example_quest()

# Modify it
quest.quest_name = "My Custom Quest"
quest.rewards.xp = 2000

# Generate Lua
parser = LuaQuestParser()
lua_script = parser.generate_lua_script(quest)
```

### Example 4: Validate Quest

```python
from TirganachReloaded.cff_editor.lua_parser import LuaQuestParser

parser = LuaQuestParser()
quest = create_example_quest()

# Validate before generating
valid, messages = parser.validate_quest(quest)

if valid:
    print("✓ Quest is valid!")
    lua_script = parser.generate_lua_script(quest)
else:
    print("✗ Quest has errors:")
    for msg in messages:
        print(f"  - {msg}")
```

## Integration with Quest Creator

The Quest Creator wizard can use the parser to generate Lua scripts:

```python
# In Quest Creator widget
def on_generate_clicked(self):
    # Collect data from UI
    quest = QuestData(
        quest_id=int(self.quest_id_edit.text()),
        quest_name=self.quest_name_edit.text(),
        description=self.description_edit.toPlainText(),
        platform=self.platform_combo.currentText()
    )
    
    # Add objectives from list
    for i in range(self.objectives_list.count()):
        obj_text = self.objectives_list.item(i).text()
        quest.objectives.append(
            QuestObjective(description=obj_text)
        )
    
    # Add rewards
    quest.rewards = QuestReward(
        xp=int(self.xp_edit.text() or 0),
        gold=int(self.gold_edit.text() or 0)
    )
    
    # Generate Lua
    parser = LuaQuestParser()
    lua_script = parser.generate_lua_script(quest)
    
    # Show in preview
    self.lua_preview.setPlainText(lua_script)
```

## Quest Objective Types

### Kill Objectives

```python
QuestObjective(
    description="Defeat 10 wolves",
    objective_type="Kill",
    target="Wolf",  # Entity tag
    count=10
)
```

**Generated Lua:**
```lua
FigureIsDead{Tag = "Wolf"}
```

### Collect Objectives

```python
QuestObjective(
    description="Collect 5 healing herbs",
    objective_type="Collect",
    target="201",  # Item ID
    count=5
)
```

**Generated Lua:**
```lua
PlayerHasItem{ItemId = 201, Amount = 5}
```

### Reach Objectives

```python
QuestObjective(
    description="Reach the ancient temple",
    objective_type="Reach",
    target="TempleMarker"
)
```

**Generated Lua:**
```lua
FigureIsInRange{Tag = "TempleMarker", Range = 10}
```

### Custom Objectives

For complex objectives, use raw Lua:

```python
QuestObjective(
    description="Custom condition",
    lua_condition="MyCustomFunction() == true"
)
```

## Quest Requirement Types

### Level Requirements

```python
QuestRequirement(
    description="Reach level 10",
    requirement_type="Level",
    value=10
)
```

**Generated Lua:**
```lua
AvatarLevel{Level = 10}
```

### Quest Requirements

```python
QuestRequirement(
    description="Complete 'The First Step'",
    requirement_type="Quest",
    value=1000  # Quest ID
)
```

**Generated Lua:**
```lua
QuestState{QuestId = 1000, State = StateSolved}
```

### Custom Requirements

```python
QuestRequirement(
    description="Custom condition",
    lua_condition="PlayerHasFlag{Name = 'CustomFlag'}"
)
```

## Advanced Features

### Custom Events

For advanced quest logic, add custom events:

```python
quest.custom_events.append("""
OnOneTimeEvent
{
    EventName = "MyCustomEvent",
    Conditions =
    {
        -- Your conditions here
    },
    Actions =
    {
        -- Your actions here
    }
}
""")
```

### Raw Lua Sections

Override generated init/complete events:

```python
quest.init_event = """
OnOneTimeEvent
{
    EventName = "CustomInit",
    Conditions = { ... },
    Actions = { ... }
}
"""
```

## File Naming Convention

Generated quest files should follow this pattern:

- `quest_<ID>.lua` - Individual quest script
- `quest_chain_<NAME>.lua` - Related quest series
- `gds_quest_rewards.lua` - Reward definitions

Example:
- `quest_1001.lua`
- `quest_1002.lua`
- `quest_chain_bandits.lua`

## Testing the Parser

Run the test suite:

```bash
cd SpellSmut/src/tests/lua_parser
python test_quest_lua_parser.py
```

**Tests include:**
1. Generate Lua from quest data
2. Save to file and load back
3. Parse existing Lua files
4. Round-trip testing (Create → Generate → Parse → Generate)
5. Multiple related quests

## Best Practices

### 1. Always Validate Before Generating

```python
valid, messages = parser.validate_quest(quest)
if not valid:
    # Show errors to user
    display_errors(messages)
    return
```

### 2. Use Meaningful Quest IDs

- Reserve ranges for different quest types
- Example: 1000-1999 for main quests, 2000-2999 for side quests

### 3. Add Metadata

```python
quest.author = "YourName"
quest.notes = "Part of the Bandit campaign"
```

### 4. Test Generated Scripts

Always test generated Lua in the game before releasing.

### 5. Keep Descriptions Clear

```python
# Good
QuestObjective(description="Defeat the Bandit Leader in the camp")

# Too vague
QuestObjective(description="Kill something")
```

## Limitations

### Current Limitations:

1. **Dialogue Parsing**: Simple extraction only; complex dialogue trees need manual editing
2. **State Management**: Basic events; advanced state machines may need custom events
3. **Trigger Types**: Not all SpellForce trigger types are supported yet
4. **NPC Behavior**: NPC AI and behavior not included

### Workarounds:

- Use `custom_events` for advanced logic
- Use `lua_condition` for unsupported conditions
- Manually edit generated Lua for fine-tuning

## Troubleshooting

### Problem: Generated Lua has syntax errors

**Solution:** Validate quest data before generating:
```python
valid, messages = parser.validate_quest(quest)
```

### Problem: Quest doesn't start in game

**Check:**
1. Quest ID is unique
2. Requirements are satisfiable
3. Platform ID matches map
4. NPC ID exists in game

### Problem: Parser can't read existing Lua

**Reason:** Parser looks for specific patterns. Complex or non-standard Lua may not parse correctly.

**Solution:** Use as a starting point and manually edit complex quests.

### Problem: Objectives don't work in game

**Check:**
1. Entity tags match game entities
2. Item IDs are valid
3. Conditions are logically correct

## Future Enhancements

Planned features:

- [ ] GUI integration in Quest Creator
- [ ] More objective types (Craft, Trade, Equip)
- [ ] Dialogue tree generation
- [ ] Quest chain helper (auto-link prerequisites)
- [ ] Template library (common quest patterns)
- [ ] Lua beautifier/formatter
- [ ] In-editor Lua syntax checking

## Related Documentation

- [Quest Editor Tabs Guide](QUEST_EDITOR_TABS.md) - Using the Quest Creator
- [Dialogue System Documentation](DIALOGUE_SYSTEM.md) - Player choices and branching
- [Quest Data Structure Analysis](../tests/quest_hierarchy/README.md) - What's in CFF vs Lua

## API Reference

### LuaQuestParser

**Methods:**

- `parse_file(lua_file_path: str) -> List[QuestData]`
- `parse_string(lua_content: str) -> List[QuestData]`
- `generate_lua_script(quest: QuestData) -> str`
- `save_to_file(quest: QuestData, output_path: str)`
- `validate_quest(quest: QuestData) -> Tuple[bool, List[str]]`

### Convenience Functions

- `parse_quest_file(lua_file_path: str) -> List[QuestData]`
- `generate_quest_file(quest: QuestData, output_path: str)`
- `create_example_quest() -> QuestData`

## Examples Directory

Find more examples in:
- `SpellSmut/src/tests/lua_parser/test_quest_lua_parser.py`
- `SpellSmut/src/tests/lua_parser/output/` (generated files)

## Support

For questions or issues:
1. Check the test suite for examples
2. Review generated Lua for patterns
3. Consult SpellForce scripting documentation
4. Manually edit generated Lua as needed

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Maintainer:** SpellForce CFF Editor Team