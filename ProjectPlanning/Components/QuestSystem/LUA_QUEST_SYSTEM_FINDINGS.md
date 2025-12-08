# Lua Quest System Findings (SpellForce Platinum)

## Scope
- Summarize where quest data lives in Lua and how it maps to our editor features.
- Provide concrete examples from game files for: pre-start requirements, dialogue branching, rewards, and quest state changes.
- Inventory core condition/action primitives we must support first.
- Note alignment points with CFF/SQL exports for NPCs, items, etc.

## Key Findings
- Pre-start requirements are implemented as `Conditions` in `OnOneTimeEvent` blocks that trigger `QuestBegin{QuestId=...}` or set gating flags. Conditions also control `OnBeginDialog` availability.
- Dialogues and choices are scripted with `OnBeginDialog` and `OnAnswer{N; ...}`, each carrying its own `Conditions` and `Actions`.
- NPC references appear via `_NpcId`/`NpcId` (state machines and actions) and localized dialogue `Tag`s; catalogs of entities live in SQL-style Lua exports (e.g., `sql_unit.lua`).
- Rewards are delivered via `Actions`: `TransferItem{GiveItem=...}`, `UpdateVariable{Name="PlayerXP"}`, and quest state changes (`QuestSolve`, `QuestBegin`).
- Catalog data for items/units/buildings is provided via `sql_*.lua` exports and should be mirrored/derivable from CFF for the editor’s browsers.

## Examples from game files

### A. Dialogue with item reward (P110/n6045.lua)
```lua
OnBeginDialog{
    Conditions = {},
    Actions = {
        Say{Tag = "sternenpriester110_001", String = "..."},
        Answer{Tag = "sternenpriester110_002PC", String = "...", AnswerId = 1},
    }
}

OnAnswer{5;
    Conditions = {},
    Actions = {
        TransferItem{GiveItem = 2648 , Flag = Give}, -- reward
        RemoveDialog{NpcId = self},
        Say{Tag = "", String = ""},
        Answer{Tag = "", String = "", AnswerId = 6},
    }
}
```

### B. Gated dialogue and quest state transitions (P110/n6046.lua)
```lua
OnBeginDialog{
    Conditions = {
        IsGlobalFlagTrue{Name = "HaendlerFireCitySpawnP110"},
    },
    Actions = {
        Say{Tag = "craig110_001", String = "Ihr habt die Waffe?"},
        Answer{Tag = "", String = "", AnswerId = 1},
    }
}

OnAnswer{5;
    Conditions = {},
    Actions = {
        SetItemFlagTrue {Name = "PlayerHasItemGlowstone"},
        QuestSolve { QuestId = 747},
        QuestBegin { QuestId = 749},
        RemoveDialog {NpcId = self},
    }
}
```

### C. Pre-start requirement pattern (flags → actions) (P110/n6232.lua)
```lua
OnOneTimeEvent
{
    Conditions = {
        IsGlobalFlagTrue {Name = "GargoyleActionP110"},
    },
    Actions = {
        SetFreezeFlagFalse { NpcId = self },
        SetNpcFlagTrue {Name = "GargoyleStartP110"},
    }
}
```

## Inventory: primitives to support first

### Conditions (gating and availability)
- Quest/State: `QuestState{QuestId=..., State=StateActive|StateSolved|StateUnknown|...}`
- Flags: `IsGlobalFlagTrue/False{Name=...}`, `IsNpcFlagTrue/False{Name=...}`, `IsItemFlagTrue/False{Name=...}`
- Items: `PlayerHasItem{ItemId=...}`; `Negated(...)` wrapper for NOT
- Entities: `FigureDead{FigureId=...}`, `NpcExists{NpcId=...}`, `PlayerInArea{X=...,Y=...,Range=...}`
- Time: `GameTimeGreaterThan{Hours=...}`, `DayTime{IsDay=true|false}`

### Actions (effects and progression)
- Quest state: `QuestBegin{QuestId=...}`, `QuestSolve{QuestId=...}`
- Rewards: `TransferItem{GiveItem=...|TakeItem=..., Flag=Give|Take}`, `UpdateVariable{Name="PlayerXP"|"PlayerGold", Value=...}`
- Flags/Variables: `SetGlobalFlagTrue/False{Name=...}`, `SetItemFlagTrue/False{Name=...}`, `SetNpcFlagTrue/False{Name=...}`
- Dialogue flow: `Say{...}`, `Answer{...}` / `OfferAnswer{...}`, `EndDialog()`, `RemoveDialog{NpcId=...}`
- Spawning/Transforms: `SpawnFigure{...}`, `Umspawn{...}`, `Despawn{...}`, `ChangeUnit{...}`

## Alignment with CFF/SQL exports
- Items/NPCs/Units: Editor browsers can source from `sql_item.lua`, `sql_unit.lua`, `sql_building.lua` (or CFF-derived tables). Store stable IDs in quest data; display localized names.
- Localization: Dialogue uses `Tag` keys; ensure localization keys exist/are generated on export to CFF/localization tables.
- ID management: Quest IDs must follow game ranges; handle conflicts and provide next-free suggestions during CFF export.

## Editor implications
- Pre-Start Requirements UI → builds `Conditions` blocks for activation and availability.
- Dialogue Editors → map 1:1 to `OnBeginDialog`/`OnAnswer` nodes; ASCII Overview provides fast tree navigation and edits.
- Reward Builder → composes `TransferItem`, `UpdateVariable`, and quest state transitions.
- NPC Chooser → selects `NpcId` and per-node `speakerNpcId` from catalogs.

## Next steps
1. Expand the primitives list with any rare but important condition/actions discovered during broader scan.
2. Map each primitive to a UI control and validation rule.
3. Define Lua codegen templates per pattern (activation, dialogue, completion).
