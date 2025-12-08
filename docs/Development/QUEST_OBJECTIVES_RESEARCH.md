# Quest Objectives & Requirements Research

**Date**: November 16, 2025  
**Status**: ✅ Research Complete  
**Purpose**: Document SpellForce quest objective/requirement data formats for UI implementation

---

## 📋 Executive Summary

Based on analysis of SpellForce LUA quest files and reward data, quests use a **flag-based objective system** rather than explicit objective tracking. Progress is managed through:
1. **Quest States** (StateActive, StateSolved, StateFailed)
2. **Item Flags** (PlayerHasItem*)  
3. **NPC Flags** (dialogue/interaction markers)
4. **Global Flags** (world state changes)

---

## 🎯 Quest Objective Types Identified

### 1. **Kill Objectives**
**Implementation**: Kill count tracked via global/NPC flags

**Pattern**:
```lua
-- Example: Kopfjagd (Bounty Hunt) Quest
Quest Flags:
- Kopfjagd1Head1 (15 XP)
- Kopfjagd2Head2 (15 XP)
- Kopfjagd3Head3 (15 XP)
- Kopfjagd4Head4 (15 XP)
- Kopfjagd5Head5 (15 XP)
- Kopfjagd6Complete (60 XP + rewards)
```

**Data Structure**:
```python
{
    "type": "kill",
    "target_npc_id": 12345,
    "target_name": "Orc Warrior",
    "count_required": 5,
    "tracking_flags": ["Kopfjagd1Head1", "Kopfjagd2Head2", ...],
    "completion_flag": "Kopfjagd6Complete"
}
```

---

### 2. **Collect/Gather Objectives**
**Implementation**: Item possession tracked via IsItemFlagTrue

**Pattern**:
```lua
-- Example: Collect 3 ritual items
Conditions = {
    IsItemFlagTrue{Name = "PlayerHasItemSanduhr"},  -- Hourglass
    IsItemFlagTrue{Name = "PlayerHasItemBlutphiole"},  -- Blood vial
    IsItemFlagTrue{Name = "PlayerHasItemKerze"},  -- Candle
}
```

**Data Structure**:
```python
{
    "type": "collect",
    "items": [
        {"item_id": 2191, "name": "Sanduhr", "quantity": 1},
        {"item_id": 2193, "name": "Blutphiole", "quantity": 1},
        {"item_id": 2194, "name": "Kerze", "quantity": 1}
    ],
    "tracking_flags": ["PlayerHasItemSanduhr", "PlayerHasItemBlutphiole", "PlayerHasItemKerze"]
}
```

---

### 3. **Talk/Dialogue Objectives**
**Implementation**: NPC interaction tracked via dialogue flags

**Pattern**:
```lua
-- Example: Multi-stage dialogue quest
Quest Flags:
- AmraUndLea1Liannon1 (200 XP) -- Talk to Shan, option 1
- AmraUndLea1Liannon2 (400 XP) -- Talk to Shan, option 2
- AmraUndLea2Liannon1 (500 XP) -- Return to Shan
```

**Data Structure**:
```python
{
    "type": "talk",
    "npc_id": 1394,
    "npc_name": "Shan Muir",
    "dialogue_stages": [
        {"flag": "AmraUndLea1Liannon1", "xp": 200},
        {"flag": "AmraUndLea1Liannon2", "xp": 400}
    ]
}
```

---

### 4. **Reach/Explore Objectives**
**Implementation**: Location reach tracked via quest state changes

**Pattern**:
```lua
-- Example: Reach a location
Conditions = {
    QuestState{QuestId = 652, State = StateActive, UpdateInterval = 60}
}
Actions = {
    QuestSetSolved{QuestId = 652}
}
```

**Data Structure**:
```python
{
    "type": "reach",
    "location_name": "Wildland Pass",
    "platform_id": "P6",
    "coordinates": {"x": 100, "y": 200},  # Optional
    "completion_flag": "AmWildlandPass1"
}
```

---

### 5. **Deliver Item Objectives**
**Implementation**: Item delivery = collect + talk combined

**Pattern**:
```lua
-- Example: Deliver Darius's Map
Quest: DariusDerKarthograph
Items: 626 (given)
Actions: TakeItem{ItemId = 626}
```

**Data Structure**:
```python
{
    "type": "deliver",
    "item_id": 626,
    "item_name": "Karte",
    "recipient_npc_id": 1240,
    "recipient_name": "Darius",
    "delivery_flag": "DariusDerKarthograph"
}
```

---

## 📊 Quest State System

### Quest States
```lua
-- Three primary states
StateActive    -- Quest is active
StateSolved    -- Quest completed successfully
StateFailed    -- Quest failed (rare)
```

### State Conditions
```lua
-- Check quest state
QuestState{QuestId = 652, State = StateSolved}

-- Negated state check
Negated(QuestState{QuestId = 646, State = StateSolved})

-- Combined conditions
UND(
    QuestState{QuestId = 646, State = StateActive},
    Negated(QuestState{QuestId = 652, State = StateSolved})
)
```

---

## 🎁 Reward System Analysis

### Reward Types

**1. Experience Points (XP)**
```lua
-- Quest rewards from analysis
{
    "quest_flag": "DariusDerKarthograph",
    "xp": 25,
    "gold": 0,
    "silver": 0,
    "copper": 0
}
```

**2. Currency**
```lua
-- Gold/Silver/Copper rewards
{
    "xp": 45,
    "gold": 0,
    "silver": 10,
    "copper": 0
}
```

**3. Items**
```lua
-- Items given/taken
"items": "626 (given), 2336 (taken)"

-- Parsed structure:
{
    "items_given": [626],  // Items player receives
    "items_taken": [2336]  // Items removed from player
}
```

### Reward Distribution Patterns

**Pattern 1: Multi-stage rewards**
```
AmraUndLea1Liannon1: 200 XP
AmraUndLea1Liannon2: 400 XP
AmraUndLea2Liannon1: 500 XP + items
```

**Pattern 2: Incremental bounty**
```
Kopfjagd1Head1: 15 XP
Kopfjagd2Head2: 15 XP
...
Kopfjagd6Complete: 60 XP + 5 items
```

---

## 🔧 Condition System

### Condition Types

**1. Quest State Conditions**
```lua
QuestState{QuestId = 652, State = StateSolved}
```

**2. Item Flag Conditions**
```lua
IsItemFlagTrue{Name = "PlayerHasItemSanduhr"}
IsItemFlagFalse{Name = "PlayerHasItemKerze"}
```

**3. NPC Flag Conditions**
```lua
IsNpcFlagTrue{Name = "n_P213_Talked"}
IsNpcFlagFalse{Name = "known"}
```

**4. Global Flag Conditions**
```lua
IsGlobalFlagTrue{Name = "DschungelWeisenDialog"}
IsGlobalFlagFalse{Name = "PleaseRemoveDialog_10983"}
```

**5. Time Conditions**
```lua
TimeDay()        -- Is it daytime?
TimeNight()      -- Is it nighttime?
```

### Logical Operators

**UND() - AND operator**
```lua
UND(
    QuestState{QuestId = 646, State = StateActive},
    IsNpcFlagTrue{Name = "n_P213_Talked"}
)
```

**ODER() - OR operator**
```lua
ODER(
    TimeDay(),
    QuestState{QuestId = 652, State = StateSolved}
)
```

**Negated() - NOT operator**
```lua
Negated(QuestState{QuestId = 652, State = StateSolved})
```

**Nested Conditions**
```lua
UND(
    QuestState{QuestId = 646, State = StateActive},
    Negated(QuestState{QuestId = 652, State = StateSolved})
)
```

---

## 📝 Data Structure Recommendations

### Quest Objective Model

```python
@dataclass
class QuestObjective:
    """Base quest objective model"""
    objective_type: str  # "kill", "collect", "talk", "reach", "deliver"
    description: str     # Human-readable description
    tracking_flags: List[str]  # Flags used to track progress
    completion_flag: str       # Flag set when objective complete
    xp_reward: int = 0
    optional: bool = False
    
    # Type-specific fields
    target_npc_id: Optional[int] = None      # For kill/talk
    item_ids: Optional[List[int]] = None     # For collect/deliver
    location: Optional[str] = None           # For reach
    count_required: int = 1                  # For kill/collect
```

### Quest Requirements Model

```python
@dataclass
class QuestRequirement:
    """Quest activation requirements"""
    min_level: Optional[int] = None
    required_quests: List[int] = field(default_factory=list)  # Must be solved
    required_items: List[int] = field(default_factory=list)
    required_flags: List[str] = field(default_factory=list)
    
    # Conditions
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    # Example: [{"type": "QuestState", "quest_id": 652, "state": "StateSolved"}]
```

### Quest Reward Model

```python
@dataclass
class QuestReward:
    """Quest completion rewards"""
    xp: int = 0
    gold: int = 0
    silver: int = 0
    copper: int = 0
    
    items_given: List[int] = field(default_factory=list)
    items_taken: List[int] = field(default_factory=list)
    
    # Optional: Choice rewards (pick 1 of N)
    choice_items: Optional[List[List[int]]] = None
```

---

## 🎨 UI Implementation Recommendations

### Objectives Tab Improvements

**1. Objective Type Selector**
```
[Dropdown: Select Objective Type]
  - Kill Enemies
  - Collect Items
  - Talk to NPC
  - Reach Location
  - Deliver Item
```

**2. Type-Specific Forms**

**Kill Objective UI**:
```
Target NPC: [Browse NPCs...] [ID: 12345] [Name: Orc Warrior]
Kill Count: [5]
Tracking Flags: [Auto-generate ✓]
```

**Collect Objective UI**:
```
Item 1: [Browse Items...] [ID: 626] [Name: Karte] [Qty: 1]
Item 2: [Browse Items...] [ID: 833] [Name: Ring] [Qty: 1]
[+ Add Item]
```

**Talk Objective UI**:
```
NPC: [Browse NPCs...] [ID: 1394] [Name: Shan Muir]
Dialogue Stages:
  Stage 1: [200 XP] [Flag: AmraUndLea1Liannon1]
  Stage 2: [400 XP] [Flag: AmraUndLea1Liannon2]
[+ Add Stage]
```

**3. Reward Builder**
```
Experience: [250] XP
Currency:   [0] Gold [2] Silver [50] Copper

Items to Give:
  - [626] Karte
  - [833] Ring
  [+ Add Item]

Items to Take:
  - [2336] Old Map
  [+ Add Item]
```

**4. Requirements Builder**
```
Minimum Level: [10]

Required Quests (must be completed):
  - [652] Jungle Path
  - [646] Dark Elves
  [+ Add Quest]

Required Items:
  - [2191] Sanduhr
  [+ Add Item]
```

---

## 📊 Real-World Examples

### Example 1: Simple Kill Quest

```yaml
Quest: Kopfjagd (Bounty Hunt)
Type: Kill
Giver: Sergeant Einar (1362)
Objectives:
  - Kill 5 specific enemies
  - Each kill: 15 XP
  - Complete all: 60 XP + 5 items

Tracking:
  - Kopfjagd1Head1 (enemy 1 killed)
  - Kopfjagd2Head2 (enemy 2 killed)
  - Kopfjagd3Head3 (enemy 3 killed)
  - Kopfjagd4Head4 (enemy 4 killed)
  - Kopfjagd5Head5 (enemy 5 killed)
  - Kopfjagd6Complete (all killed)

Rewards:
  - 60 XP (completion)
  - 75 XP (total with stages)
  - Items: 3202, 3203, 3204, 3205, 3206 (taken)
```

### Example 2: Multi-Stage Dialogue Quest

```yaml
Quest: Amra und Lea (Amra and Lea)
Type: Talk + Multi-stage
Giver: Sunder Blackhand (1390)
Parent Quest: 379

Objectives:
  Stage 1: Talk to Shan - Option 1 (200 XP)
  Stage 2: Talk to Shan - Option 2 (400 XP)
  Stage 3: Return to Shan (500 XP + items)
  Stage 4: Final dialogue (1200 XP)

Total Rewards:
  - 2300 XP total
  - Various progression items
```

### Example 3: Collection Quest

```yaml
Quest: Bannwerk (Banner Work)
Type: Collect
Objectives:
  - Collect 6 specific items
  - Return to Lord Kommandant Tynar Utran

Items Required:
  - 2191, 2193, 2194, 2200, 2201, 2205

Rewards:
  - 60 XP
  - Items taken from player
```

---

## 🔍 Key Findings

1. **No Explicit Objective System**: SpellForce uses a **flag-based approach** where quest progress is tracked through state flags rather than explicit "kill 5 orcs" objectives.

2. **Flexible Tracking**: Multiple flags can track progress for complex quests (multi-stage, optional objectives).

3. **Reward Patterns**:
   - XP scales with quest difficulty (10-1500 XP range)
   - Currency rewards are relatively rare
   - Item rewards use "given" and "taken" patterns

4. **Conditions Are Core**: Quest availability and progression heavily rely on condition checks (quest states, flags, items).

5. **Parent-Child Structure**: Quests can have parent quests and chains, forming quest lines.

---

## ✅ Recommendations for Quest Editor

### Phase 1: Basic Objective Support
- [ ] Objective type selector (kill, collect, talk, reach, deliver)
- [ ] Simple reward builder (XP, gold, items)
- [ ] Auto-generate tracking flags based on quest name

### Phase 2: Advanced Features
- [ ] Condition builder integration
- [ ] Multi-stage objective support
- [ ] Parent quest linking
- [ ] Quest chain visualization

### Phase 3: Export & Validation
- [ ] LUA export with proper flag structure
- [ ] Validation against game data
- [ ] Preview of generated quest flow

---

## 📁 Related Files

- **Reward Data**: `ModdingTools/SpellForceLUASources/QuestKnowledge/QuestRewards.md`
- **Dialogue Data**: `ModdingTools/SpellForceLUASources/QuestKnowledge/CompleteQuestDialogues.md`
- **Example Scripts**: `ModdingTools/SpellForceLUASources/script/P109/*.lua`

---

**Research Completed**: November 16, 2025  
**Next Steps**: Implement Reward Builder UI → Condition Builder → LUA Export
