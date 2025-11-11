# Data Model Updates Spec

## Overview
Define the updated quest data model to support pre-start requirements, NPC references, rewards, conditions, and templates.

## Core Quest Data Model

### QuestNode Structure
```python
@dataclass
class QuestNode:
    id: int  # Quest ID (9000-9999 for new quests)
    name: str  # Quest name
    description: str  # Quest description
    campaign: str  # Campaign identifier (e.g., "P110", "FreeGame")
    quest_type: str  # "Main", "Side", "Sub-quest"
    status: str  # "Draft", "Complete", "Published"
    
    # Pre-start requirements
    start_requirements: ConditionGroup  # Conditions that must be true to start quest
    
    # NPC references
    quest_giver_npc_id: Optional[int]  # NPC who gives the quest
    involved_npc_ids: List[int]  # NPCs involved in quest
    
    # Objectives (existing)
    objectives: List[Objective]
    
    # Rewards
    rewards: QuestRewards
    
    # Dialogue tree
    dialogue_nodes: List[DialogueNode]
    
    # Metadata
    location: Optional[str]  # Map/region where quest takes place
    created_at: datetime
    updated_at: datetime
```

### ConditionGroup Structure
```python
@dataclass
class ConditionGroup:
    operator: str  # "AND", "OR"
    conditions: List[Union['Condition', 'ConditionGroup']]  # Nested conditions
    
@dataclass
class Condition:
    type: str  # "QuestState", "PlayerHasItem", "IsGlobalFlagTrue", etc.
    operands: Dict[str, Any]  # Function-specific operands
    negated: bool = False  # Wrapped in Negated() if True
```

### QuestRewards Structure
```python
@dataclass
class QuestRewards:
    xp: int = 0
    gold: int = 0
    items: List[RewardItem] = field(default_factory=list)
    
@dataclass
class RewardItem:
    item_id: int
    quantity: int = 1
```

### DialogueNode Structure
```python
@dataclass
class DialogueNode:
    id: str  # Node ID (e.g., "node_001")
    speaker_npc_id: Optional[int]  # NPC speaking (None for player)
    text: str  # Dialogue text
    tag: str  # Localization tag
    conditions: ConditionGroup  # Conditions for node availability
    answers: List[DialogueAnswer]  # Player choices
    actions: List[Action]  # Actions triggered by this node
    
@dataclass
class DialogueAnswer:
    id: int  # Answer ID (for OnAnswer{N; ...})
    text: str  # Answer text
    tag: str  # Localization tag
    conditions: ConditionGroup  # Conditions for answer availability
    next_node_id: Optional[str]  # Next dialogue node
    actions: List[Action]  # Actions triggered by this answer
```

### Action Structure
```python
@dataclass
class Action:
    type: str  # "TransferItem", "QuestSolve", "SetGlobalFlagTrue", etc.
    parameters: Dict[str, Any]  # Action-specific parameters
```
## Serialization

### JSON Format
- Standard JSON serialization for persistence
- Human-readable format for version control
- Support for nested ConditionGroups and DialogueNodes

### Backward Compatibility
- Migration path for older quest files
- Default values for new fields (e.g., `start_requirements: ConditionGroup` defaults to empty)
- Graceful handling of missing fields

### Validation
- Type checking on deserialization
- Reference validation (NPC IDs, item IDs, quest IDs)
- Circular dependency detection

## Template Model

### QuestTemplate Structure
```python
@dataclass
class QuestTemplate:
    id: str  # Template ID
    name: str  # Template name
    description: str  # Template description
    category: str  # "Kill", "Collect", "Escort", etc.
    parameters: List[TemplateParameter]  # Parameterizable fields
    skeleton: QuestNode  # Template skeleton with placeholders
    
@dataclass
class TemplateParameter:
    name: str  # Parameter name
    type: str  # "int", "string", "npc_id", "item_id", etc.
    default: Any  # Default value
    required: bool  # Whether parameter is required
```

## Acceptance Criteria

### Data Model
- All new fields are properly typed and validated
- Serialization/deserialization works correctly
- Backward compatibility maintained for existing quests
- Templates can be saved and loaded

### Migration
- Older quest files load without errors
- Missing fields get sensible defaults
- Migration tool can upgrade old files to new format

## Implementation Notes

### Type Safety
- Use dataclasses with type hints
- Validate types on deserialization
- Provide type-checked accessors

### Performance
- Lazy loading for large dialogue trees
- Caching for frequently accessed data
- Efficient serialization for large quests
