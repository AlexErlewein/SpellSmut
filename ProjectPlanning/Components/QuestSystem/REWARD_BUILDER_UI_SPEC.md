# Reward Builder UI Spec

## Goal
Configure quest rewards: items (with quantity), XP, and gold, aligned with Lua actions and CFF catalogs.

## UI
- Fields: XP [number], Gold [number].
- Items list: rows with Item (searchable picker), Quantity, Remove.
- Add Item: opens item browser (powered by CFF/sql_item.lua). Filters by type/rarity.
- Hints: balance guidance based on quest tier/difficulty (non-blocking).

## Behavior
- Adds corresponding Lua actions: `TransferItem{GiveItem=ID, Flag=Give}` repeated by quantity (or encoded as count if pattern supported); `UpdateVariable{Name="PlayerXP"}`, `UpdateVariable{Name="PlayerGold"}`.
- Supports item removal when completing objectives: `TransferItem{TakeItem=ID, Flag=Take}`.

## Validation
- Item IDs must exist; quantity ≥ 1.
- XP/Gold non-negative; upper bounds warn.
- Duplicate items merge quantities unless explicitly separated for branching.

## Acceptance Criteria
- Users can add/edit/remove item rewards, XP, and gold.
- Exported Lua reflects configured rewards accurately.
- Validation blocks export only on hard errors (missing IDs, invalid qty).
## Lua Mapping Examples
```lua
-- XP and Gold
UpdateVariable{Name = "PlayerXP", Value = 500}
UpdateVariable{Name = "PlayerGold", Value = 100}

-- Item rewards
TransferItem{GiveItem = 2648, Flag = Give}
TransferItem{GiveItem = 4079, Flag = Give}

-- Remove quest items on turn-in
TransferItem{TakeItem = 3955, Flag = Take}
```

## Implementation Notes
- Batch similar `TransferItem` calls if acceptable; otherwise emit one per count.
- Hook into item browser from icon system once mapping is available.
- Allow branching-specific rewards by linking rows to dialogue answers.
