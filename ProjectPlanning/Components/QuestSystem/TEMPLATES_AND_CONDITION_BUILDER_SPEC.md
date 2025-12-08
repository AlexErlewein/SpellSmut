# Templates & Condition Builder Spec

## Goals
- Provide quest templates to speed up creation.
- Enable visual condition building with AND/OR grouping and negation.

## Quest Templates

### Built-in Templates
1. **Kill Quest**: Target entity, count, reward structure.
2. **Collect Quest**: Item(s), quantity, reward structure.
3. **Escort Quest**: NPC to escort, destination, reward structure.
4. **Fetch-Deliver Quest**: Item to fetch, target NPC, reward structure.
5. **Dialogue Choice Quest**: Branching dialogue with consequence flags.

### Template Customization
- Pre-fill basic info, objectives, rewards, dialogue skeleton.
- Auto-generate objectives, dialogue prompts, and reward hints.
- Allow full editing after creation.

### Template UI
- Template picker with previews.
- Parameters form (target entity/item, counts, difficulty).
- Preview of generated structure before creation.

## Condition Builder

### Visual Builder UI
- Tree/list view of conditions with AND/OR groups.
- Add condition: pick function (PlayerHasItem, QuestState, etc.), set operands, operator, value(s).
- Grouping: create AND/OR groups, drag to reorder, nest groups.
- Negation: wrap conditions/groups with NOT.

### Supported Condition Types
- **Quest State**: QuestState{QuestId, State}
- **Flags**: IsGlobalFlagTrue/False, IsNpcFlagTrue/False, IsItemFlagTrue/False
- **Items**: PlayerHasItem{ItemId}
- **Entities**: FigureDead{FigureId}, NpcExists{NpcId}, PlayerInArea{X,Y,Range}
- **Time**: GameTimeGreaterThan{Hours}, DayTime{IsDay}

### Preview & Export
- Readable preview (e.g., "IF PlayerHasItem(3421) AND QuestState(9001, Completed)").
- Machine-readable form stored with quest.
- Lua generation maps to correct Conditions blocks.
## Acceptance Criteria

### Templates
- Users can create quests from templates with minimal input.
- Template-generated quests are fully editable.
- Custom templates can be saved and reused.

### Condition Builder
- Users can add/edit/delete conditions and groups.
- AND/OR logic is visually clear and correctly exported.
- Preview shows readable human logic.
- Generated Lua matches expected pattern.

## Implementation Notes

### Template System
- Store templates as JSON with parameterized fields.
- Template engine substitutes parameters into skeleton structure.
- Validation ensures template-generated quests are valid.

### Condition Builder
- Internal representation: tree of ConditionNode with type (condition/group), operator (AND/OR/NOT), children.
- Serialization: JSON for persistence, Lua for export.
- Validation: type-check operands, resolve references, detect circular dependencies.

## Examples

### Kill Quest Template
```
Template: Kill Quest
Parameters:
  - Target Entity: [Select NPC/Unit]
  - Count: [1]
  - Reward XP: [500]
  - Reward Items: [Select items...]

Generated:
  - Objective: Kill [Target] x[Count]
  - Dialogue: "Kill [Target] for me..."
  - Reward: XP + Items
  - Completion: Check FigureDead{FigureId = [Target]}
```

### Condition Builder Example
```
IF (
  PlayerHasItem(3421) AND
  QuestState(9001, Completed)
) OR (
  IsGlobalFlagTrue("AlternativePath") AND
  NOT FigureDead(6045)
)
```
