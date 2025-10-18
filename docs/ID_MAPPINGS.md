# SpellForce Platinum Edition - ID Mappings Reference

This document provides comprehensive mappings between symbolic constants (used in Lua scripts) and their corresponding IDs in the game engine.

**Note:** Most numeric ID values are defined in the C++ engine executable and are not directly visible in the Lua scripts. The constants listed here are C++ enums exposed to the Lua scripting environment via the engine's Lua binding layer.

---

## Table of Contents
1. [Weapon Types](#weapon-types)
2. [Job/Animation IDs](#jobanimation-ids)
3. [Effect Types](#effect-types)
4. [Spell Lines](#spell-lines)
5. [Quest States](#quest-states)
6. [Equipment Slots](#equipment-slots)
7. [Figure Tasks](#figure-tasks)
8. [Figure Flags](#figure-flags)
9. [Figure Job Flags](#figure-job-flags)
10. [Directions](#directions)
11. [Spell Tags](#spell-tags)
12. [Target Types](#target-types)

---

## Weapon Types

These constants map weapon types to their internal IDs. Used for combat mechanics, animations, and sound effects.

| Constant Name | Description | Sound Mapping (Hit) | Sound Mapping (Miss) |
|--------------|-------------|---------------------|---------------------|
| `kDrwWtDefault` | Default/Fallback weapon | battle_hit_fist | battle_miss_fist |
| `kDrwWtMouth` | Bite attack (creatures) | battle_hit_mouth | battle_hit_mouth |
| `kDrwWtHand` | Unarmed/Fist | battle_hit_fist | battle_miss_fist |
| `kDrwWt1HDagger` | One-handed dagger | battle_hit_1hdagger | battle_miss_sword |
| `kDrwWt1HSword` | One-handed sword | battle_hit_1hsword | battle_miss_sword |
| `kDrwWt1HAxe` | One-handed axe | battle_hit_1haxe | battle_miss_sword |
| `kDrwWt1HMaceSpiky` | One-handed spiky mace | battle_hit_1hmacespiky | battle_miss_hammer |
| `kDrwWt1HMaceBlunt` | One-handed blunt mace | battle_hit_1hmaceblunt | battle_miss_hammer |
| `kDrwWt1HHammer` | One-handed hammer | battle_hit_1hhammer | battle_miss_hammer |
| `kDrwWt1HStaff` | One-handed staff | battle_hit_1hstaff | battle_miss_staff |
| `kDrwWt2HSword` | Two-handed sword | battle_hit_2hsword | battle_miss_sword |
| `kDrwWt2HAxe` | Two-handed axe | battle_hit_2haxe | battle_miss_sword |
| `kDrwWt2HMace` | Two-handed mace | battle_hit_2hmace | battle_miss_hammer |
| `kDrwWt2HHammer` | Two-handed hammer | battle_hit_2hhammer | battle_miss_hammer |
| `kDrwWt2HStaff` | Two-handed staff | battle_hit_2hstaff | battle_miss_staff |
| `kDrwWt2HSpear` | Two-handed spear | battle_hit_2hspear | battle_miss_staff |
| `kDrwWt2HHalberd` | Two-handed halberd | battle_hit_2hhalberd | battle_miss_sword |
| `kDrwWt2HBow` | Two-handed bow | battle_hit_2hbow | battle_miss_staff |
| `kDrwWt2HCrossbow` | Two-handed crossbow | battle_hit_2hcrossbow | battle_miss_bow |
| `kDrwWt1HClaw` | One-handed claw | battle_hit_claw | (not specified) |

**Source Files:**
- `script/DrwSound.lua` (lines 867-909)
- `src/api/sf_general_structures.h` (SF_CGdFigureWeaponStats structure)

---

## Job/Animation IDs

Unit job/action constants that determine animations and behaviors. These are used throughout the figure initialization system.

### Core Job Types

| Constant Name | Description | Used For |
|--------------|-------------|----------|
| `kGdJobDefault` | Idle/standing animation | All units at rest |
| `kGdJobGroupNothing` | No action group | Action placeholder |
| `kGdJobGroupWalk` | Walking animations | Unit movement |
| `kGdJobPunch` | Unarmed attack | Fist/claw attacks |
| `kGdJobStrike` | Melee weapon strike | Sword/axe/mace attacks |
| `kGdJobStab` | Stabbing attack | Dagger/spear attacks |
| `kGdJobHitTargetRange1` | Ranged attack (aim) | Bow/crossbow aim |
| `kGdJobHitTargetRange2` | Ranged attack (shoot) | Bow/crossbow fire |
| `kGdJobCast` | Spell casting initiation | Magic casting |
| `kGdJobCastResolve` | Spell completion | Spell finish |
| `kGdJobDie` | Death animation | Unit death |
| `kGdJobCriticalHit` | Hit reaction | Taking damage |
| `kGdJobStoop` | Pickup/loot animation | Item interaction |
| `kGdJobFeignDeath` | Feign death | Special ability |

### Worker Job Types

| Constant Name | Description | Sound Effect |
|--------------|-------------|--------------|
| `kGdJobShrineWorkerTakeMana` | Collect mana from shrine | - |
| `kGdJobWoodCutterCutTree` | Chop trees | work_cut_tree |
| `kGdJobStoneMinerCrushStone` | Mine stone | work_cut_stone |
| `kGdJobMinerWork` | Mine ore | work_cut_stone |
| `kGdJobBuilderBuild` | Construction | work_build |
| `kGdJobHunterCutCorpse` | Harvest corpse | - |
| `kGdJobHunterHitTarget` | Hunter ranged attack | battle_fire_arrow |
| `kGdJobFisherWalkToWork` | Walk to fishing spot | - |
| `kGdJobFisherWork` | Fishing | work_johnthefisherman |
| `kGdJobFisherWalkHome` | Return from fishing | - |
| `kGdJobFisherWalkToDeliverGood` | Deliver fish | - |
| `kGdJobFarmerHarvest` | Harvest crops | - |
| `kGdJobFarmerSow` | Plant seeds | - |
| `kGdJobCattleBreederFeed` | Feed animals | work_cattlebreeding |
| `kGdJobSmithWork` | Blacksmithing | - |
| `kGdJobCarpenterWork` | Carpentry/sawmill | - |
| `kGdJobFoodWorkerWork` | Food processing | work_get_food |
| `kGdJobSmelterWork` | Smelting | - |
| `kGdJobPriestWork` | Temple work | - |
| `kGdJobGathererWork` | Gather food | work_get_food |
| `kGdJobForesterPlant` | Plant trees | - |

### Special Job Types

| Constant Name | Description |
|--------------|-------------|
| `kGdJobMeleeAbility` | Melee combat ability |
| `kGdJobGroupPatrol` | Patrol movement |
| `kGdJobGroupFlee` | Fleeing/retreat |
| `kGdJobGroupGuard` | Guard stance |

### Animation Subtype Constants

Used to specify weapon-specific animations:

| Constant Name | Description |
|--------------|-------------|
| `kDrwAnimDefault` | Default animation variant |
| `kDrwAnimMagic` | Magic/spell animation |
| `kDrwAnimShoulder` | Shoulder-mounted animation |
| `kDrwAnimFront` | Front-facing animation |

### Play Modes

Animation playback modes:

| Constant Name | Description |
|--------------|-------------|
| `kDrwPlayLooped` | Loop animation continuously |
| `kDrwPlayStretched` | Stretch animation to fit duration |
| `kDrwPlayClamped` | Play once and hold final frame |

**Source Files:**
- `object/object_figure_init.lua` (lines 283-763+)

---

## Effect Types

Visual and gameplay effects triggered by spells, summons, and game events.

| Constant Name | Numeric Value | Description | Usage |
|--------------|---------------|-------------|-------|
| `kGdEffectNone` | 0 | No effect | Default/null |
| `kGdEffectSpellCast` | 1 | Spell casting initiation | When spell starts |
| `kGdEffectSpellHitWorld` | 2 | Spell hits terrain | AOE ground impact |
| `kGdEffectSpellHitTarget` | 3 | Spell hits target | Direct damage spells |
| `kGdEffectSpellDOTHitTarget` | 4 | Damage over time tick | Poison, burn effects |
| `kGdEffectSpellMissTarget` | 5 | Spell missed target | Miss feedback |
| `kGdEffectSpellResolve` | 6 | Spell completion | Spell finishes |
| `kGdEffectSummonWorker` | 7 | Worker summoning | Summon worker spell |
| `kGdEffectWorkerAppears` | 8 | Worker materialization | Worker spawn visual |
| `kGdEffectSummonHero` | 9 | Hero summoning | Summon hero spell |
| `kGdEffectHeroAppears` | 10 | Hero materialization | Hero spawn visual |
| `kGdEffectSpellTargetResisted` | 11 | Target resisted spell | Resistance proc |
| `kGdEffectSpellResolveSelf` | 12 | Self-targeted spell resolve | Buff completion |
| `kGdEffectMeteorFall` | 13 | Meteor falling | Fire Rain spell |
| `kGdEffectMeteorHit` | 14 | Meteor impact | Fire Rain hit |
| `kGdEffectBlizzardFall` | 15 | Blizzard ice falling | Ice Rain spell |
| `kGdEffectBlizzardHit` | 16 | Blizzard ice impact | Ice Rain hit |
| `kGdEffectStoneFall` | 17 | Stone falling | Stone Rain spell |
| `kGdEffectStoneHit` | 18 | Stone impact | Stone Rain hit |
| `kGdEffectPetAppears` | 19 | Pet materialization | Pet spawn visual |
| `kGdEffectTest` | 20 | Test effect | Development |
| `kGdEffectMonumentClaimed` | 21 | Monument claimed | Monument capture |
| `kGdEffectMonumentWorking` | 22 | Monument active | Monument producing |
| `kGdEffectAuraResolve` | 23 | Aura activation | Aura spells |
| `kGdEffectProjectile` | 24 | Projectile visual | Arrows, bolts |
| `kGdEffectBuilding` | 25 | Building effect | Construction |
| `kGdEffectPlayerBind` | 26 | Player bindstone | Respawn point |
| `kGdEffectSummonMainChar` | 27 | Main character summon | Avatar summon |
| `kGdEffectMainCharAppears` | 28 | Main character appears | Avatar spawn |
| `kGdEffectTitanProduction` | 29 | Titan being created | Titan production |
| `kGdEffectTitanAppears` | 30 | Titan materialization | Titan spawn |
| `kGdEffectMentalTowerCast` | 31 | Mental tower casting | Mind tower active |
| `kGdEffectMentalTowerIdle` | 32 | Mental tower idle | Mind tower passive |
| `kGdEffectMonumentBullet` | 33 | Monument projectile | Monument attack |
| `kGdEffectMonumentHitFigure` | 34 | Monument hit unit | Monument damage |
| `kGdEffectSpellAssistanceHitFigure` | 35 | Assistance spell hit | Support spells |
| `kGdEffectChainResolve` | 36 | Chain spell resolution | Chain Lightning |
| `kGdEffectSpellVoodooHitFigure` | 37 | Voodoo spell hit | Voodoo effect |
| `kGdEffectSpellManaShieldHitFigure` | 38 | Mana shield absorb | Shield proc |
| `kGdEffectMax` | 39 | Maximum effect ID | Boundary check |

**Source Files:**
- `src/api/sf_general_structures.h` (CGdEffectType enum)
- `object/object_effect_register.lua`

---

## Spell Lines

SpellForce contains **140+ spell lines** organized into magic schools. Each spell line represents a progression of spell levels.

Due to the extensive number of spells, they are documented in a separate file:

**📖 [SPELL_IDS_REFERENCE.md](./SPELL_IDS_REFERENCE.md)** - Complete spell line documentation

### Quick Reference by School

| School | Count | Example Spells |
|--------|-------|----------------|
| **Black Magic** | 30+ | Pain, Death, Pestilence, Summon Skeleton, Life Tap |
| **White Magic** | 30+ | Healing, Cure Disease, Summon Wolf, Regeneration |
| **Fire Magic** | 10+ | Fire Burst, Fire Ball, Fire Shield, Rain of Fire |
| **Ice Magic** | 9+ | Ice Burst, Freeze, Blizzard, Ice Shield |
| **Earth Magic** | 13+ | Rock Bullet, Petrify, Stone Rain, Earth Elemental |
| **Mental Magic** | 24+ | Dominate, Charm, Hypnotize, Mana Drain, Invisibility |
| **Abilities** | 14 | Berserk, Blessing, True Shot, Steel Skin, War Cry |
| **Towers** | 8 | Arrow Tower, Fire Burst Tower, Healing Tower |

**Source Files:**
- `object/object_effect_register.lua` (complete spell effect definitions)

---

## Quest States

Quest progression states.

| Lua Constant | C++ Constant | Description |
|-------------|--------------|-------------|
| `StateUnknown` | `kDbQuestStateUnknown` | Quest not discovered |
| `StateUnsolvable` | `kDbQuestStateUnsolvable` | Quest failed/locked |
| `StateKnown` | `kDbQuestStateKnown` | Quest discovered but not started |
| `StateActive` | `kDbQuestStateActive` | Quest in progress |
| `StateSolved` | `kDbQuestStateSolved` | Quest completed |

**Source Files:**
- `script/GdsDefines.lua` (lines 15-19)

---

## Equipment Slots

Character equipment slot indices.

| Lua Constant | Numeric Value | Description |
|-------------|---------------|-------------|
| `SlotHead` | 0 | Helmet/headgear |
| `SlotRightHand` | 1 | Right hand weapon |
| `SlotChest` | 2 | Chest armor |
| `SlotLeftHand` | 3 | Left hand weapon/shield |
| `SlotRightRing` | 4 | Right ring |
| `SlotLegs` | 5 | Leg armor |
| `SlotLeftRing` | 6 | Left ring |

**Source Files:**
- `script/GdsDefines.lua` (lines 87-93)

---

## Figure Tasks

Unit/character task/role types.

| Constant Name | Numeric Value | Description |
|--------------|---------------|-------------|
| `TASK_WORKER` | 2 | Worker unit |
| `TASK_WOODCUTTER` | 3 | Lumberjack |
| `TASK_QUARRY` | 4 | Stone cutter |
| `TASK_MINE` | 5 | Miner |
| `TASK_FORGE` | 6 | Blacksmith |
| `TASK_HERO` | 9 | Hero unit |
| `TASK_MAINCHAR` | 10 | Player avatar |
| `TASK_NPC` | 11 | Non-player character |
| `TASK_PET` | 12 | Pet/companion |
| `TASK_HUNTING_LODGE` | 14 | Hunter |
| `TASK_MERCHANT` | 17 | Merchant NPC |

**Source Files:**
- `src/api/sf_general_structures.h` (CGdFigureTask enum)

---

## Figure Flags

Bitwise flags for unit states (32-bit bitmask).

| Flag Name | Hex Value | Description |
|----------|-----------|-------------|
| `UNDEAD` | 0x1 | Unit is undead |
| `RESERVED_ONLY` | 0x2 | Reserved flag |
| `AGGROED` | 0x4 | Unit is aggressive |
| `IS_DEAD` | 0x8 | Unit is dead |
| `REDO` | 0x10 | Redo action flag |
| `F_CHECK_SPELLS_BEFORE_JOB` | 0x20 | Check spells first |
| `F_CHECK_SPELLS_BEFORE_CHECK_BATTLE` | 0x40 | Check spells before combat |
| `WALK_JOB_WAIT` | 0x80 | Waiting during walk |
| `FREEZED` | 0x100 | Unit is frozen |
| `HAS_LOOT` | 0x200 | Unit has loot |
| `HAS_DIALOG` | 0x400 | Unit has dialogue |
| `FEMALE` | 0x800 | Unit is female |
| `GOT_AGGRO` | 0x1000 | Unit gained aggro |
| `RETREAT` | 0x2000 | Unit is retreating |
| `NO_WAY_TO_TARGET` | 0x4000 | Cannot reach target |
| `AURA_RUNNING` | 0x8000 | Aura is active |
| `AI_BLOCKED` | 0x10000 | AI is blocked |
| `TOWER` | 0x20000 | Unit is tower |
| `IS_SWAPPING` | 0x40000 | Swapping equipment |
| `CUR_ACTIVE_DIALOG` | 0x80000 | Dialog active |
| `IS_IN_FIGHT` | 0x100000 | In combat |
| `VIEW_MODE_1ST_3RD` | 0x200000 | Camera view mode |
| `IS_TALKING` | 0x400000 | Unit is talking |
| `IS_IMPORTANT_DIALOG` | 0x800000 | Important dialog |
| `UNKILLABLE` | 0x1000000 | Cannot be killed |
| `FOLLOW_MODE` | 0x2000000 | Following another unit |
| `HIT_LEFT_HAND_NEXT` | 0x4000000 | Next hit with left hand |
| `FOREST_SPIRIT` | 0x8000000 | Forest spirit type |
| `VIP` | 0x10000000 | Very important unit |
| `ILLUSION` | 0x20000000 | Unit is illusion |
| `SPAWN` | 0x40000000 | Unit is spawned |
| `USED_FOR_REVENGE` | 0x80000000 | Revenge flag |

**Source Files:**
- `src/api/sf_general_structures.h` (GdFigureFlags enum)

---

## Figure Job Flags

Bitwise flags for unit job/task states (16-bit bitmask).

| Flag Name | Numeric Value | Description |
|----------|---------------|-------------|
| `MANUAL_JOB_CHANGE` | 1 | Job manually changed |
| `SKIP_ONCE` | 2 | Skip this iteration |
| `MANUAL_HIT_TARGET` | 4 | Manual target selection |
| `CORPSE_CANT_ROT` | 8 | Permanent corpse |
| `START_WALK` | 16 | Begin walking |
| `RUN_MODE` | 32 | Running instead of walking |
| `WAR` | 64 | War/combat mode |
| `CHECK_BATTLE` | 128 | Check for combat |
| `PATROL_MODE` | 256 | Patrolling |
| `WAY_POINTS_READ_REVERSE` | 512 | Reverse waypoint order |
| `SUPERIOR_PATHING` | 1024 | Enhanced pathfinding |
| `ROUND_HIT` | 2048 | Round/AOE hit |
| `DEATH_BLOW` | 4096 | Killing blow |
| `START_WORK_AT_BUILDING_FORCE_JOB` | 8192 | Force building work |

**Source Files:**
- `src/api/sf_general_structures.h` (CGdFigureJobFlags enum)

---

## Directions

Cardinal and intercardinal directions.

| Lua Constant | C++ Constant | Description |
|-------------|--------------|-------------|
| `East` | `kGdDirectionEast` | East (0°) |
| `SouthEast` | `kGdDirectionSouthEast` | Southeast (45°) |
| `South` | `kGdDirectionSouth` | South (90°) |
| `SouthWest` | `kGdDirectionSouthWest` | Southwest (135°) |
| `West` | `kGdDirectionWest` | West (180°) |
| `NorthWest` | `kGdDirectionNorthWest` | Northwest (225°) |
| `North` | (implied) | North (270°) |
| `NorthEast` | (implied) | Northeast (315°) |

**Source Files:**
- `script/GdsDefines.lua` (lines 95-100)

---

## Spell Tags

Bitwise flags for spell categorization (16-bit bitmask).

| Flag Name | Hex Value | Description |
|----------|-----------|-------------|
| `NONE` | 0x0 | No special tags |
| `SUMMON_SPELL` | 0x1 | Summons creatures |
| `DOMINATION_SPELL` | 0x2 | Mind control spell |
| `CHAIN_SPELL` | 0x4 | Chain effect (Chain Lightning) |
| `WHITE_AURA_SPELL` | 0x8 | White magic aura |
| `BLACK_AURA_SPELL` | 0x10 | Black magic aura |
| `TARGET_ONHIT_SPELL` | 0x20 | Triggers on hit |
| `COMBAT_ABILITY_SPELL` | 0x40 | Combat ability |
| `AOE_SPELL` | 0x80 | Area of effect |
| `SIEGE_AURA_SPELL` | 0x100 | Siege aura |
| `AURA_SPELL` | 0x200 | Generic aura |
| `STACKABLE_SPELL` | 0x400 | Can stack multiple times |

**Note:** `SPELL_TAG_COUNT` = 12

**Source Files:**
- `src/api/sf_general_structures.h` (SpellTag enum)

---

## Target Types

Entity types for targeting system.

| Lua Constant | Numeric Value | Description |
|-------------|---------------|-------------|
| `Figure` | 1 | Character/unit |
| `Building` | 2 | Structure |
| `Object` | 3 | Interactive object |
| `World` | 4 | Terrain/world |
| `Area` | 5 | Area/region |

**Source Files:**
- `script/GdsDefines.lua` (lines 73-77)

---

## Variable Operators

Script variable manipulation operators.

| Lua Constant | C++ Constant | Description |
|-------------|--------------|-------------|
| `Add` / `OperatorAdd` | `kDbScriptVariableOperatorAdd` | Addition |
| `OperatorInvertBool` | `kDbScriptVariableOperatorInvertBool` | Boolean NOT |
| `OperatorSetRandom` | `kDbScriptVariableOperatorSetRandom` | Random value |

**Source Files:**
- `script/GdsDefines.lua` (lines 34-36)

---

## Variable Comparison

Script variable comparison operators.

| Lua Constant | C++ Constant | Description |
|-------------|--------------|-------------|
| `IsEqual` | `kDbScriptVariableCompareEqual` | == |
| `IsGreater` | `kDbScriptVariableCompareGreater` | > |
| `IsGreaterOrEqual` | `kDbScriptVariableCompareGreaterEqual` | >= |
| `IsLess` | `kDbScriptVariableCompareLess` | < |
| `IsLessOrEqual` | `kDbScriptVariableCompareLessEqual` | <= |
| `IsNotEqual` | `kDbScriptVariableCompareNotEqual` | != |

**Source Files:**
- `script/GdsDefines.lua` (lines 43-48)

---

## Transfer Flags

Item/resource transfer modes.

| Lua Constant | C++ Constant | Description |
|-------------|--------------|-------------|
| `Take` | `kGtScriptTransferFlagTake` | Remove from inventory |
| `Give` | `kGtScriptTransferFlagGive` | Add to inventory |
| `Exchange` | `kGtScriptTransferFlagExchange` | Swap items |

**Source Files:**
- `script/GdsDefines.lua` (lines 84-86)

---

## Movement Modes

| Lua Constant | Numeric Value | Description |
|-------------|---------------|-------------|
| `Walk` | 0 | Walking speed |
| `Run` | 1 | Running speed |

**Source Files:**
- `script/GdsDefines.lua` (lines 60-61)

---

## Additional Constants

### Spawn Modes
| Lua Constant | Numeric Value | Description |
|-------------|---------------|-------------|
| `None` | 0 | No spawning |
| `Once` | -1 | Spawn once only |

### Time Constants
| Lua Constant | Numeric Value | Description |
|-------------|---------------|-------------|
| `AnimalSpawnTime` | 300 | Animal clan spawn delay (seconds) |

### Boolean Constants
| Lua Constant | Numeric Value | Description |
|-------------|---------------|-------------|
| `FALSE` / `FALSCH` | 0 | Boolean false |
| `TRUE` / `WAHR` | 1 | Boolean true |

**Source Files:**
- `script/GdsDefines.lua`

---

## Data Categories (SFCFF)

These are the data chunk IDs used in the game's data files (.cff format):

| Hex ID | Decimal | Name | Description |
|--------|---------|------|-------------|
| 0x000007D0 | 2000 | PlayerMain | Player character data |
| 0x000007D1 | 2001 | UnitDependencies | Unit dependency trees |
| 0x000007D2 | 2002 | Spells | Spell definitions |
| 0x000007D3 | 2003 | Items | Item definitions |
| 0x000007D4 | 2004 | ItemStats | Item statistics |
| 0x000007D5 | 2005 | Creos | Creature definitions |
| 0x000007D6 | 2006 | CreoAbilities | Creature abilities |
| 0x000007E8 | 2024 | Units | Unit definitions |
| 0x000007E9 | 2025 | UnitEquipment | Unit equipment loadouts |
| 0x000007EA | 2026 | UnitSpells | Unit spell lists |
| 0x000007EB | 2027 | UnitActions | Unit action definitions |
| 0x000007ED | 2029 | BuildingBase | Building base data |
| 0x00000806 | 2054 | SpellLines | Spell progression lines |
| 0x00000807 | 2055 | Effects | Effect definitions |
| 0x00000808 | 2056 | SpellLineEffects | Spell-to-effect mapping |
| 0x0000080F | 2063 | WeaponTypes | Weapon type names |
| 0x00000810 | 2064 | WeaponMaterials | Weapon material names |
| 0x00000818 | 2072 | ItemSets | Item set bonuses |

**Source Files:**
- `modding/SFCFF/SFCFF.cdt`

---

## Notes on ID Resolution

### Numeric Values
Most numeric ID values are **not** explicitly defined in Lua scripts. They are C++ enums compiled into the game executable (`SpellForce.exe`). The Lua binding layer exposes these as global constants that Lua scripts can reference.

### Sound IDs
Sound IDs are **automatically generated** at runtime based on alphabetically sorted sound names:

```lua
local t = tkeys(Data)  -- Get all sound names
sort(t)                -- Sort alphabetically
DrwSoundId = {}
for i = 1,getn(t) do
    DrwSoundId[t[i]] = i  -- Assign sequential IDs
end
```

This means sound IDs are **deterministic** but **dynamic** - they're not hardcoded numbers.

### Weapon Type IDs
Weapon type IDs are referenced from C++ but their exact numeric values are not visible in the Lua codebase. The engine uses these internally for:
- Animation selection
- Sound effect mapping
- Damage calculation
- Attack range determination

### Data File IDs
The `.cff` data files use hexadecimal chunk IDs to organize game data. These are defined in `SFCFF.cdt` and can be viewed/edited with the SpellForce Data Editor tools.

---

## Tools for ID Extraction

To extract actual numeric values from the game executable:

1. **Hex Editor**: Open `SpellForce.exe` and search for constant patterns
2. **Disassembler**: Use tools like Ghidra or IDA Pro to analyze the executable
3. **Memory Scanner**: Use Cheat Engine during runtime to find values
4. **Modding Tools**: 
   - **SFGameDataEditor** - Edit game data with visual interface
   - **Tirganach** - Python library for .cff file parsing
   - **SFCFF** - Direct data file manipulation

---

## References

### Source Files Analyzed
- `OriginalGameFiles/script/DrwSound.lua`
- `modding/Original Scripts/script/GdsDefines.lua`
- `ModdingTools/Spellforce-Spell-Framework/src/api/sf_general_structures.h`
- `ModdingTools/tirganach/tirganach/entities.py`
- `OriginalGameFiles/modding/SFCFF/SFCFF.cdt`

### External Documentation
- SpellForce Modding SDK
- SFSF (Spellforce Spell Framework) API Documentation
- Community modding guides

---

**Last Updated:** 2025-10-18  
**Game Version:** SpellForce: Platinum Edition (v1.x)  
**Documentation Status:** Based on code analysis and reverse engineering
