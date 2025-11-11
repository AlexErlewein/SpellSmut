# Pre-Start Requirements UI Spec

## Goal
Let authors define conditions that must be true before a quest can be offered/started.

## Scope
- Global/campaign flags, quest states, player inventory, level/class/faction, region/map checks, entity states.
- Grouping with AND/OR; Negation via wrappers.

## UI
- Requirements tab with list of rules.
- Add Condition dialog: pick function (e.g., PlayerHasItem), operands, operator, value(s).
- Grouping: create groups (AND/OR). Drag to reorder.
- Readable preview and machine-typed form side-by-side.

## Validation
- Typed operands; reference resolution (quest IDs, item IDs, flags).
- Inline errors/warnings; block export on errors.
## Mapped Lua Patterns
- Activation gate: `OnOneTimeEvent { Conditions = { ... }, Actions = { QuestBegin{QuestId=...}, SetGlobalFlagTrue{...} } }`
- Dialogue availability: `OnBeginDialog{ Conditions = { ... }, Actions = { ... } }`

### Condition primitives
- QuestState{QuestId, State}
- IsGlobalFlagTrue/False{Name}
- PlayerHasItem{ItemId}
- FigureDead{FigureId}, NpcExists{NpcId}
- GameTimeGreaterThan{Hours}, DayTime{IsDay}
- Negated(...)

## Acceptance Criteria
- Authors can add/edit/delete conditions and groups.
- Preview shows readable AND/OR logic.
- Validation highlights type/reference issues.
- Export produces correct Lua blocks for activation and availability.
