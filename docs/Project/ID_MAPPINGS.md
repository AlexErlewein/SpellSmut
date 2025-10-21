# SpellForce Platinum Edition - ID Mappings Reference

**Auto-generated from Lua sources**
**Last Updated:** 2025-10-19 21:24:54
**Game Version:** SpellForce: Platinum Edition (v1.x)

---

## About This Document

This document provides comprehensive mappings between symbolic constants (used in Lua scripts) and their corresponding numeric IDs in the game engine. All data has been automatically extracted from the SpellForce Lua source files and verified against the game data.

**Note:** Most numeric ID values are defined in the C++ engine executable and exposed to Lua through the engine's binding layer. The constants listed here are C++ enums made available to the Lua scripting environment.

## Table of Contents

1. [Overview](#overview)
2. [Weapon Types](#weapon-types)
3. [Effect Types](#effect-types)
4. [Spell Lines](#spell-lines)
5. [Races](#races)
6. [Job/Animation Types](#jobanimation-types)
7. [Equipment Slots](#equipment-slots)
8. [Quest States](#quest-states)
9. [Figure Tasks](#figure-tasks)
10. [Directions](#directions)
11. [Target Types](#target-types)
12. [Variable Operators](#variable-operators)
13. [Movement Modes](#movement-modes)
14. [Monument Types](#monument-types)
15. [Usage Examples](#usage-examples)
16. [Tools & Scripts](#tools--scripts)

---

## Overview

**Total Categories:** 13
**Total Mappings:** 360

### Categories Summary

- **Directions**: 8 entries
- **Effect Types**: 39 entries
- **Equipment Slots**: 7 entries
- **Figure Tasks**: 11 entries
- **Job Types**: 20 entries
- **Monument Types**: 7 entries
- **Movement Modes**: 2 entries
- **Quest States**: 5 entries
- **Races**: 6 entries
- **Spell Lines**: 227 entries
- **Target Types**: 5 entries
- **Variable Operators**: 3 entries
- **Weapon Types**: 20 entries

---

## Weapon Types

Weapon type constants map to combat animations, sound effects, and damage calculations.

**Total:** 20 weapon types

| ID | Name | Constant | Hit Sound | Miss Sound |
|----|------|----------|-----------|------------|
| 0 | Default/Fist | `kDrwWtDefault` | battle_hit_fist | battle_miss_fist |
| 1 | Mouth/Bite | `kDrwWtMouth` | battle_hit_mouth | battle_hit_mouth |
| 2 | Unarmed/Fist | `kDrwWtHand` | battle_hit_fist | battle_miss_fist |
| 3 | One-handed Dagger | `kDrwWt1HDagger` | battle_hit_1hdagger | battle_miss_sword |
| 4 | One-handed Sword | `kDrwWt1HSword` | battle_hit_1hsword | battle_miss_sword |
| 5 | One-handed Axe | `kDrwWt1HAxe` | battle_hit_1haxe | battle_miss_sword |
| 6 | One-handed Mace (Spiky) | `kDrwWt1HMaceSpiky` | battle_hit_1hmacespiky | battle_miss_hammer |
| 7 | One-handed Mace (Blunt) | `kDrwWt1HMaceBlunt` | battle_hit_1hmaceblunt | battle_miss_hammer |
| 8 | One-handed Hammer | `kDrwWt1HHammer` | battle_hit_1hhammer | battle_miss_hammer |
| 9 | One-handed Staff | `kDrwWt1HStaff` | battle_hit_1hstaff | battle_miss_staff |
| 10 | Two-handed Sword | `kDrwWt2HSword` | battle_hit_2hsword | battle_miss_sword |
| 11 | Two-handed Axe | `kDrwWt2HAxe` | battle_hit_2haxe | battle_miss_sword |
| 12 | Two-handed Mace | `kDrwWt2HMace` | battle_hit_2hmace | battle_miss_hammer |
| 13 | Two-handed Hammer | `kDrwWt2HHammer` | battle_hit_2hhammer | battle_miss_hammer |
| 14 | Two-handed Staff | `kDrwWt2HStaff` | battle_hit_2hstaff | battle_miss_staff |
| 15 | Two-handed Spear | `kDrwWt2HSpear` | battle_hit_2hspear | battle_miss_staff |
| 16 | Two-handed Halberd | `kDrwWt2HHalberd` | battle_hit_2hhalberd | battle_miss_sword |
| 17 | Two-handed Bow | `kDrwWt2HBow` | battle_hit_2hbow | battle_miss_staff |
| 18 | Two-handed Crossbow | `kDrwWt2HCrossbow` | battle_hit_2hcrossbow | battle_miss_bow |
| 19 | One-handed Claw | `kDrwWt1HClaw` | battle_hit_claw | - |

**Usage:**
```lua
-- Example: Check if unit has a sword
if figure:GetWeaponType() == kDrwWt1HSword then
    -- One-handed sword logic
end
```

**Sound Mapping:**
- **Hit Sounds**: Played when weapon connects with target
- **Miss Sounds**: Played when weapon swings through air

---

## Effect Types

Visual and gameplay effects triggered by spells, summons, and game events.

**Total:** 39 effect types

| ID | Name | Constant | Description |
|----|------|----------|-------------|
| 0 | None | `kGdEffectNone` | No visual effect |
| 1 | Spell Cast | `kGdEffectSpellCast` | Spell casting initiation visual |
| 2 | Spell Hit World | `kGdEffectSpellHitWorld` | Spell hits terrain (AOE ground impact) |
| 3 | Spell Hit Target | `kGdEffectSpellHitTarget` | Spell hits target (direct damage) |
| 4 | Spell DOT Hit Target | `kGdEffectSpellDOTHitTarget` | Damage over time tick visual |
| 5 | Spell Miss Target | `kGdEffectSpellMissTarget` | Spell missed target feedback |
| 6 | Spell Resolve | `kGdEffectSpellResolve` | Spell completion visual |
| 7 | Summon Worker | `kGdEffectSummonWorker` | Worker summoning effect |
| 8 | Worker Appears | `kGdEffectWorkerAppears` | Worker materialization |
| 9 | Summon Hero | `kGdEffectSummonHero` | Hero summoning effect |
| 10 | Hero Appears | `kGdEffectHeroAppears` | Hero materialization |
| 11 | Spell Target Resisted | `kGdEffectSpellTargetResisted` | Target resisted spell visual |
| 12 | Spell Resolve Self | `kGdEffectSpellResolveSelf` | Self-targeted spell resolution |
| 13 | Meteor Fall | `kGdEffectMeteorFall` | Meteor falling (Fire Rain) |
| 14 | Meteor Hit | `kGdEffectMeteorHit` | Meteor impact |
| 15 | Blizzard Fall | `kGdEffectBlizzardFall` | Blizzard ice falling |
| 16 | Blizzard Hit | `kGdEffectBlizzardHit` | Blizzard ice impact |
| 17 | Stone Fall | `kGdEffectStoneFall` | Stone falling (Stone Rain) |
| 18 | Stone Hit | `kGdEffectStoneHit` | Stone impact |
| 19 | Pet Appears | `kGdEffectPetAppears` | Pet materialization |
| 20 | Test Effect | `kGdEffectTest` | Test/debug effect |
| 21 | Monument Claimed | `kGdEffectMonumentClaimed` | Monument claimed by player |
| 22 | Monument Working | `kGdEffectMonumentWorking` | Monument actively producing |
| 23 | Aura Resolve | `kGdEffectAuraResolve` | Aura activation visual |
| 24 | Projectile | `kGdEffectProjectile` | Projectile visual (arrows, bolts) |
| 25 | Building | `kGdEffectBuilding` | Building-related effect |
| 26 | Player Bind | `kGdEffectPlayerBind` | Player bindstone activation |
| 27 | Summon Main Character | `kGdEffectSummonMainChar` | Main character summoning |
| 28 | Main Character Appears | `kGdEffectMainCharAppears` | Main character materialization |
| 29 | Titan Production | `kGdEffectTitanProduction` | Titan being created |
| 30 | Titan Appears | `kGdEffectTitanAppears` | Titan materialization |
| 31 | Mental Tower Cast | `kGdEffectMentalTowerCast` | Mental tower casting |
| 32 | Mental Tower Idle | `kGdEffectMentalTowerIdle` | Mental tower idle state |
| 33 | Monument Bullet | `kGdEffectMonumentBullet` | Monument projectile |
| 34 | Monument Hit Figure | `kGdEffectMonumentHitFigure` | Monument hit on unit |
| 35 | Spell Assistance Hit | `kGdEffectSpellAssistanceHitFigure` | Assistance spell hit |
| 36 | Chain Resolve | `kGdEffectChainResolve` | Chain spell resolution (Chain Lightning) |
| 37 | Spell Voodoo Hit | `kGdEffectSpellVoodooHitFigure` | Voodoo spell hit |
| 38 | Spell Mana Shield Hit | `kGdEffectSpellManaShieldHitFigure` | Mana shield absorb visual |

**Usage:**
```lua
-- Example: Register effect for spell
RegisterEffect(kGdEffectSpellCast, 0, EffectGet("CastFire"))
```

---

## Spell Lines

SpellForce contains **227** spell lines organized into magic schools. Each spell line represents a progression of spell levels.

**Total:** 227 spell lines

**Note:** Numeric IDs for spell lines are stored in GameData.cff files and not available in Lua sources. This section lists the constant names only.

### Black Magic

**Count:** 50 spells

| Spell Name | Constant |
|------------|----------|
| Almightiness Black | `kGdSpellLineAlmightinessBlack` |
| Aura Inability | `kGdSpellLineAuraInability` |
| Aura Inflexibility | `kGdSpellLineAuraInflexibility` |
| Aura Life Tap | `kGdSpellLineAuraLifeTap` |
| Aura Siege Dark Elf | `kGdSpellLineAuraSiegeDarkElf` |
| Aura Suffocation | `kGdSpellLineAuraSuffocation` |
| Cannibalize | `kGdSpellLineCannibalize` |
| Chain Mutation | `kGdSpellLineChainMutation` |
| Chain Pain | `kGdSpellLineChainPain` |
| Cure Poison | `kGdSpellLineCurePoison` |
| Dark Banishing | `kGdSpellLineDarkBanishing` |
| Dark Might | `kGdSpellLineDarkMight` |
| Darkness Area | `kGdSpellLineDarknessArea` |
| Death | `kGdSpellLineDeath` |
| Death Grasp | `kGdSpellLineDeathGrasp` |
| Dispel Black Aura | `kGdSpellLineDispelBlackAura` |
| Dominate Undead | `kGdSpellLineDominateUndead` |
| Essence Black | `kGdSpellLineEssenceBlack` |
| Extinct | `kGdSpellLineExtinct` |
| Extinct Tower | `kGdSpellLineExtinctTower` |
| Feign Death | `kGdSpellLineFeignDeath` |
| Inability | `kGdSpellLineInability` |
| Inflexibility | `kGdSpellLineInflexibility` |
| Inflexibility Area | `kGdSpellLineInflexibilityArea` |
| Life Tap | `kGdSpellLineLifeTap` |
| Life Tap Aura | `kGdSpellLineLifeTapAura` |
| Life Tap Chained | `kGdSpellLineLifeTapChained` |
| Mutation | `kGdSpellLineMutation` |
| Mutation Chained | `kGdSpellLineMutationChained` |
| Pain | `kGdSpellLinePain` |
| Pain Area | `kGdSpellLinePainArea` |
| Pain Chained | `kGdSpellLinePainChained` |
| Pain Tower | `kGdSpellLinePainTower` |
| Pestilence | `kGdSpellLinePestilence` |
| Pestilence Area | `kGdSpellLinePestilenceArea` |
| Poison | `kGdSpellLinePoison` |
| Raise Dead | `kGdSpellLineRaiseDead` |
| Remediless | `kGdSpellLineRemediless` |
| Remediless Area | `kGdSpellLineRemedilessArea` |
| Remove Curse | `kGdSpellLineRemoveCurse` |
| Slowness | `kGdSpellLineSlowness` |
| Slowness Area | `kGdSpellLineSlownessArea` |
| Suffocation | `kGdSpellLineSuffocation` |
| Suicide Death | `kGdSpellLineSuicideDeath` |
| Summon Blade | `kGdSpellLineSummonBlade` |
| Summon Goblin | `kGdSpellLineSummonGoblin` |
| Summon Skeleton | `kGdSpellLineSummonSkeleton` |
| Summon Spectre | `kGdSpellLineSummonSpectre` |
| Weaken | `kGdSpellLineWeaken` |
| Weaken Area | `kGdSpellLineWeakenArea` |

### White Magic

**Count:** 46 spells

| Spell Name | Constant |
|------------|----------|
| Ability Blessing | `kGdSpellLineAbilityBlessing` |
| Ability Endurance | `kGdSpellLineAbilityEndurance` |
| Almightiness White | `kGdSpellLineAlmightinessWhite` |
| Assistance | `kGdSpellLineAssistance` |
| Aura Dexterity | `kGdSpellLineAuraDexterity` |
| Aura Endurance | `kGdSpellLineAuraEndurance` |
| Aura Flexibility | `kGdSpellLineAuraFlexibility` |
| Aura Healing | `kGdSpellLineAuraHealing` |
| Aura Light | `kGdSpellLineAuraLight` |
| Aura Regeneration | `kGdSpellLineAuraRegeneration` |
| Aura Strength | `kGdSpellLineAuraStrength` |
| Chain Hallow | `kGdSpellLineChainHallow` |
| Charm Animal | `kGdSpellLineCharmAnimal` |
| Cure Disease | `kGdSpellLineCureDisease` |
| Dexterity | `kGdSpellLineDexterity` |
| Dispel White Aura | `kGdSpellLineDispelWhiteAura` |
| Dominate Animal | `kGdSpellLineDominateAnimal` |
| Endurance | `kGdSpellLineEndurance` |
| Essence White | `kGdSpellLineEssenceWhite` |
| Flexibility | `kGdSpellLineFlexibility` |
| Flexibility Area | `kGdSpellLineFlexibilityArea` |
| Greater Healing | `kGdSpellLineGreaterHealing` |
| Guard | `kGdSpellLineGuard` |
| Hallow | `kGdSpellLineHallow` |
| Hallow Chained | `kGdSpellLineHallowChained` |
| Healing | `kGdSpellLineHealing` |
| Healing Area | `kGdSpellLineHealingArea` |
| Healing Aura | `kGdSpellLineHealingAura` |
| Healing Tower | `kGdSpellLineHealingTower` |
| Holy Touch | `kGdSpellLineHolyTouch` |
| Invulnerability | `kGdSpellLineInvulnerability` |
| Quickness | `kGdSpellLineQuickness` |
| Quickness Area | `kGdSpellLineQuicknessArea` |
| Regenerate | `kGdSpellLineRegenerate` |
| Reinforcement | `kGdSpellLineReinforcement` |
| Revenge | `kGdSpellLineRevenge` |
| Roots | `kGdSpellLineRoots` |
| Roots Area | `kGdSpellLineRootsArea` |
| Sentinel Healing | `kGdSpellLineSentinelHealing` |
| Strengthen | `kGdSpellLineStrengthen` |
| Strengthen Area | `kGdSpellLineStrengthenArea` |
| Suicide Heal | `kGdSpellLineSuicideHeal` |
| Summon Bear | `kGdSpellLineSummonBear` |
| Summon Tree Wraith | `kGdSpellLineSummonTreeWraith` |
| Summon Wolf | `kGdSpellLineSummonWolf` |
| Thorn Shield | `kGdSpellLineThornShield` |

### Fire Magic

**Count:** 18 spells

| Spell Name | Constant |
|------------|----------|
| Chain Fireball | `kGdSpellLineChainFireball` |
| Chain Fireburst | `kGdSpellLineChainFireburst` |
| Fire Ball | `kGdSpellLineFireBall` |
| Fire Ball Chained | `kGdSpellLineFireBallChained` |
| Fire Ball Effect | `kGdSpellLineFireBallEffect` |
| Fire Block Effect | `kGdSpellLineFireBlockEffect` |
| Fire Burst | `kGdSpellLineFireBurst` |
| Fire Burst Chained | `kGdSpellLineFireBurstChained` |
| Fire Burst Tower | `kGdSpellLineFireBurstTower` |
| Fire Elemental | `kGdSpellLineFireElemental` |
| Fire Resistance | `kGdSpellLineFireResistance` |
| Fire Shield | `kGdSpellLineFireShield` |
| Fire Shield Damage | `kGdSpellLineFireShieldDamage` |
| Illuminate | `kGdSpellLineIlluminate` |
| Melt Resistance | `kGdSpellLineMeltResistance` |
| Rain Of Fire | `kGdSpellLineRainOfFire` |
| Summon Fire Golem | `kGdSpellLineSummonFireGolem` |
| Wave Of Fire | `kGdSpellLineWaveOfFire` |

### Ice Magic

**Count:** 16 spells

| Spell Name | Constant |
|------------|----------|
| Blizzard | `kGdSpellLineBlizzard` |
| Chain Iceburst | `kGdSpellLineChainIceburst` |
| Chill Resistance | `kGdSpellLineChillResistance` |
| Fog | `kGdSpellLineFog` |
| Freeze | `kGdSpellLineFreeze` |
| Freeze Area | `kGdSpellLineFreezeArea` |
| Ice Arrow Effect | `kGdSpellLineIceArrowEffect` |
| Ice Block Effect | `kGdSpellLineIceBlockEffect` |
| Ice Burst | `kGdSpellLineIceBurst` |
| Ice Burst Chained | `kGdSpellLineIceBurstChained` |
| Ice Elemental | `kGdSpellLineIceElemental` |
| Ice Shield | `kGdSpellLineIceShield` |
| Ice Shield Stun | `kGdSpellLineIceShieldStun` |
| Iceburst Tower | `kGdSpellLineIceburstTower` |
| Summon Ice Golem | `kGdSpellLineSummonIceGolem` |
| Wave Of Ice | `kGdSpellLineWaveOfIce` |

### Earth Magic

**Count:** 14 spells

| Spell Name | Constant |
|------------|----------|
| Chain Rock Bullet | `kGdSpellLineChainRockBullet` |
| Conservation | `kGdSpellLineConservation` |
| Decay | `kGdSpellLineDecay` |
| Decay Area | `kGdSpellLineDecayArea` |
| Detect Metal | `kGdSpellLineDetectMetal` |
| Earth Elemental | `kGdSpellLineEarthElemental` |
| Feet Clay | `kGdSpellLineFeetClay` |
| Petrify | `kGdSpellLinePetrify` |
| Rock Bullet | `kGdSpellLineRockBullet` |
| Rock Bullet Chained | `kGdSpellLineRockBulletChained` |
| Stone Rain | `kGdSpellLineStoneRain` |
| Stone Tower | `kGdSpellLineStoneTower` |
| Summon Earth Golem | `kGdSpellLineSummonEarthGolem` |
| Wave Of Rocks | `kGdSpellLineWaveOfRocks` |

### Mental Magic

**Count:** 42 spells

| Spell Name | Constant |
|------------|----------|
| Almightiness Mental | `kGdSpellLineAlmightinessMental` |
| Amok | `kGdSpellLineAmok` |
| Aura Brilliance | `kGdSpellLineAuraBrilliance` |
| Aura Mana Tap | `kGdSpellLineAuraManaTap` |
| Befriend | `kGdSpellLineBefriend` |
| Brilliance | `kGdSpellLineBrilliance` |
| Chain Charm | `kGdSpellLineChainCharm` |
| Chain Manatap | `kGdSpellLineChainManatap` |
| Chain Shock | `kGdSpellLineChainShock` |
| Charisma | `kGdSpellLineCharisma` |
| Charm | `kGdSpellLineCharm` |
| Charm Chained | `kGdSpellLineCharmChained` |
| Confuse | `kGdSpellLineConfuse` |
| Confuse Area | `kGdSpellLineConfuseArea` |
| Demoralization | `kGdSpellLineDemoralization` |
| Detect Magic | `kGdSpellLineDetectMagic` |
| Disenchant | `kGdSpellLineDisenchant` |
| Disrupt | `kGdSpellLineDisrupt` |
| Distract | `kGdSpellLineDistract` |
| Dominate | `kGdSpellLineDominate` |
| Enlightenment | `kGdSpellLineEnlightenment` |
| Essence Mental | `kGdSpellLineEssenceMental` |
| Forget | `kGdSpellLineForget` |
| Hypnotize | `kGdSpellLineHypnotize` |
| Hypnotize Area | `kGdSpellLineHypnotizeArea` |
| Hypnotize Tower | `kGdSpellLineHypnotizeTower` |
| Hypnotize Two | `kGdSpellLineHypnotizeTwo` |
| Mana Drain | `kGdSpellLineManaDrain` |
| Mana Shield | `kGdSpellLineManaShield` |
| Mana Tap | `kGdSpellLineManaTap` |
| Mana Tap Aura | `kGdSpellLineManaTapAura` |
| Mana Tap Chained | `kGdSpellLineManaTapChained` |
| Meditation | `kGdSpellLineMeditation` |
| Mirror Image | `kGdSpellLineMirrorImage` |
| Object Illusion | `kGdSpellLineObjectIllusion` |
| Sacrifice Mana | `kGdSpellLineSacrificeMana` |
| Self Illusion | `kGdSpellLineSelfIllusion` |
| Shift Mana | `kGdSpellLineShiftMana` |
| Shock | `kGdSpellLineShock` |
| Shock Chained | `kGdSpellLineShockChained` |
| Shockwave | `kGdSpellLineShockwave` |
| Voodoo | `kGdSpellLineVoodoo` |

### Abilities

**Count:** 12 spells

| Spell Name | Constant |
|------------|----------|
| Ability Benefactions | `kGdSpellLineAbilityBenefactions` |
| Ability Berserk | `kGdSpellLineAbilityBerserk` |
| Ability Critical Hits | `kGdSpellLineAbilityCriticalHits` |
| Ability Durability | `kGdSpellLineAbilityDurability` |
| Ability Patronize | `kGdSpellLineAbilityPatronize` |
| Ability Riposte | `kGdSpellLineAbilityRiposte` |
| Ability Salvo | `kGdSpellLineAbilitySalvo` |
| Ability Shelter | `kGdSpellLineAbilityShelter` |
| Ability Shift Life | `kGdSpellLineAbilityShiftLife` |
| Ability Steel Skin | `kGdSpellLineAbilitySteelSkin` |
| Ability True Shot | `kGdSpellLineAbilityTrueShot` |
| Ability War Cry | `kGdSpellLineAbilityWarCry` |

### Towers

**Count:** 1 spells

| Spell Name | Constant |
|------------|----------|
| Arrow Tower | `kGdSpellLineArrowTower` |

### Other

**Count:** 28 spells

| Spell Name | Constant |
|------------|----------|
| Acid Cloud | `kGdSpellLineAcidCloud` |
| Almightiness Elemental | `kGdSpellLineAlmightinessElemental` |
| Aura Eternity | `kGdSpellLineAuraEternity` |
| Aura Fast Fighting | `kGdSpellLineAuraFastFighting` |
| Aura Fast Walking | `kGdSpellLineAuraFastWalking` |
| Aura Hypnotization | `kGdSpellLineAuraHypnotization` |
| Aura Siege Elf | `kGdSpellLineAuraSiegeElf` |
| Aura Siege Human | `kGdSpellLineAuraSiegeHuman` |
| Aura Siege Orc | `kGdSpellLineAuraSiegeOrc` |
| Aura Siege Troll | `kGdSpellLineAuraSiegeTroll` |
| Aura Slow Fighting | `kGdSpellLineAuraSlowFighting` |
| Aura Slow Walking | `kGdSpellLineAuraSlowWalking` |
| Aura Weakness | `kGdSpellLineAuraWeakness` |
| Chain Lifetap | `kGdSpellLineChainLifetap` |
| Essence Elemental | `kGdSpellLineEssenceElemental` |
| Eternity | `kGdSpellLineEternity` |
| Fake Spell One Figure | `kGdSpellLineFakeSpellOneFigure` |
| Fast Fighting | `kGdSpellLineFastFighting` |
| Fear | `kGdSpellLineFear` |
| Holy Might | `kGdSpellLineHolyMight` |
| Invisibility | `kGdSpellLineInvisibility` |
| Plague Area | `kGdSpellLinePlagueArea` |
| Slow Fighting | `kGdSpellLineSlowFighting` |
| Spark | `kGdSpellLineSpark` |
| Summon Channeler | `kGdSpellLineSummonChanneler` |
| Summon Demon | `kGdSpellLineSummonDemon` |
| Torture | `kGdSpellLineTorture` |
| Torture Receive | `kGdSpellLineTortureReceive` |

**Usage:**
```lua
-- Example: Register spell effect
SpellEffect{line=kGdSpellLinePain, hit="DefaultBlack", cast="CastBlack"}
```

---

## Races

Playable races in SpellForce, each with unique units, buildings, and monuments.

**Total:** 6 races

| ID | Race | Constant | Monument ID |
|----|------|----------|-------------|
| 1 | Human | `kGtRaceHuman` | 0x303 (771) |
| 2 | Elf | `kGtRaceElf` | 0x305 (773) |
| 3 | Dwarf | `kGtRaceDwarf` | 0x304 (772) |
| 4 | Orc | `kGtRaceOrc` | 0x307 (775) |
| 5 | Troll | `kGtRaceTroll` | 0x308 (776) |
| 6 | Dark Elf | `kGtRaceDarkElf` | 0x306 (774) |

**Usage:**
```lua
-- Example: Check if unit is human
if figure:GetRace() == kGtRaceHuman then
    -- Human-specific logic
end
```

**Monument Types:**
Each race has a corresponding monument type for worker production and respawn.

---

## Job/Animation Types

Unit job/action constants that determine animations and behaviors.

**Total:** 20 job types

**Note:** Numeric IDs for job types are not available in Lua sources. This section lists constant names only.

### Core Job Types

| Job Name | Constant |
|----------|----------|
| Death | `kGdJobDie` |
| Default/Idle | `kGdJobDefault` |
| Feign Death | `kGdJobFeignDeath` |
| Hit Reaction | `kGdJobCriticalHit` |
| Melee Strike | `kGdJobStrike` |
| No Action | `kGdJobGroupNothing` |
| Pickup/Loot | `kGdJobStoop` |
| Ranged Aim | `kGdJobHitTargetRange1` |
| Ranged Fire | `kGdJobHitTargetRange2` |
| Spell Cast | `kGdJobCast` |
| Spell Complete | `kGdJobCastResolve` |
| Stabbing Attack | `kGdJobStab` |
| Unarmed Attack | `kGdJobPunch` |
| Walking | `kGdJobGroupWalk` |

### Worker Job Types

| Job Name | Constant |
|----------|----------|
| Blacksmithing | `kGdJobSmithWork` |
| Chop Trees | `kGdJobWoodCutterCutTree` |
| Construction | `kGdJobBuilderBuild` |
| Fishing | `kGdJobFisherWork` |
| Mine Ore | `kGdJobMinerWork` |
| Mine Stone | `kGdJobStoneMinerCrushStone` |

**Usage:**
```lua
-- Example: Set unit job
figure:SetJob(kGdJobWoodCutterCutTree)
```

---

## Equipment Slots

Character equipment slot indices for inventory management.

**Total:** 7 equipment slots

| ID | Slot | Constant |
|----|------|----------|
| 0 | Head/Helmet | `SlotHead` |
| 1 | Right Hand | `SlotRightHand` |
| 2 | Chest/Armor | `SlotChest` |
| 3 | Left Hand/Shield | `SlotLeftHand` |
| 4 | Right Ring | `SlotRightRing` |
| 5 | Legs/Pants | `SlotLegs` |
| 6 | Left Ring | `SlotLeftRing` |

**Usage:**
```lua
-- Example: Equip item to right hand
figure:EquipItem(item, SlotRightHand)
```

---

## Quest States

Quest progression states for tracking player progress.

**Total:** 5 quest states

| ID | State | Constant | Description |
|----|-------|----------|-------------|
| 0 | Unknown | `StateUnknown` | Quest not yet discovered |
| 1 | Unsolvable | `StateUnsolvable` | Quest failed or locked |
| 2 | Known | `StateKnown` | Quest discovered but not started |
| 3 | Active | `StateActive` | Quest in progress |
| 4 | Solved | `StateSolved` | Quest completed successfully |

**Usage:**
```lua
-- Example: Check if quest is active
if quest:GetState() == StateActive then
    -- Quest is active
end
```

---

## Figure Tasks

Unit/character task/role type identifiers.

**Total:** 11 task types

| ID | Task | Constant |
|----|------|----------|
| 2 | Worker | `TASK_WORKER` |
| 3 | Woodcutter | `TASK_WOODCUTTER` |
| 4 | Quarry Worker | `TASK_QUARRY` |
| 5 | Miner | `TASK_MINE` |
| 6 | Blacksmith | `TASK_FORGE` |
| 9 | Hero | `TASK_HERO` |
| 10 | Main Character | `TASK_MAINCHAR` |
| 11 | NPC | `TASK_NPC` |
| 12 | Pet | `TASK_PET` |
| 14 | Hunter | `TASK_HUNTING_LODGE` |
| 17 | Merchant | `TASK_MERCHANT` |

**Usage:**
```lua
-- Example: Check if figure is a hero
if figure:GetTask() == TASK_HERO then
    -- Hero-specific logic
end
```

---

## Directions

Cardinal and intercardinal direction constants.

**Total:** 8 directions

| ID | Direction | Constant | Angle |
|----|-----------|----------|-------|
| 0 | East | `East` | 0° |
| 1 | Southeast | `SouthEast` | 45° |
| 2 | South | `South` | 90° |
| 3 | Southwest | `SouthWest` | 135° |
| 4 | West | `West` | 180° |
| 5 | Northwest | `NorthWest` | 225° |
| 6 | North | `North` | 270° |
| 7 | Northeast | `NorthEast` | 315° |

**Usage:**
```lua
-- Example: Face unit east
figure:SetDirection(East)
```

---

## Target Types

Entity types for the targeting system.

**Total:** 5 target types

| ID | Target Type | Constant |
|----|-------------|----------|
| 1 | Character/Unit | `Figure` |
| 2 | Structure | `Building` |
| 3 | Interactive Object | `Object` |
| 4 | Terrain/World | `World` |
| 5 | Area/Region | `Area` |

**Usage:**
```lua
-- Example: Check if target is a building
if target:GetType() == Building then
    -- Building-specific logic
end
```

---

## Variable Operators

Script variable manipulation operators.

**Total:** 3 operators

| ID | Operator | Constant |
|----|----------|----------|
| 0 | Addition (+) | `Add` |
| 1 | Boolean NOT (!) | `OperatorInvertBool` |
| 2 | Set Random | `OperatorSetRandom` |

**Usage:**
```lua
-- Example: Add to variable
ModifyVariable(varId, 10, OperatorAdd)
```

---

## Movement Modes

Unit movement speed modes.

**Total:** 2 movement modes

| ID | Mode | Constant |
|----|------|----------|
| 0 | Walking | `Walk` |
| 1 | Running | `Run` |

**Usage:**
```lua
-- Example: Make unit run
figure:SetMovementMode(Run)
```

---

## Monument Types

Race-specific monument building types for worker production and respawn.

**Total:** 7 monument types

| Decimal ID | Hex ID | Monument Type | Constant |
|------------|--------|---------------|----------|
| 771 | 0x303 | Human Monument | `kGdObjMonumentHuman` |
| 772 | 0x304 | Dwarf Monument | `kGdObjMonumentDwarf` |
| 773 | 0x305 | Elf Monument | `kGdObjMonumentElf` |
| 774 | 0x306 | Dark Elf Monument | `kGdObjMonumentDarkElf` |
| 775 | 0x307 | Orc Monument | `kGdObjMonumentOrc` |
| 776 | 0x308 | Troll Monument | `kGdObjMonumentTroll` |
| 777 | 0x309 | Hero Monument | `kGdObjMonumentHero` |

**Usage:**
```lua
-- Example: Register monument effect
RegisterEffect(kGdEffectMonumentClaimed, kGdObjMonumentHuman, EffectGet("HumanMonumentClaimed"))
```

**Note:** Monument IDs are defined in hexadecimal in the Lua sources.

---

## Usage Examples

### Displaying Names in Editor

```python
from TiganachReloaded.gui_editor.utils import get_resolver

resolver = get_resolver()

# Get display name: "One-handed Sword [4]"
display = resolver.get_display_name(4, "weapon_types")

# Get just the name: "One-handed Sword"
name = resolver.get_name_only(4, "weapon_types")

# Get the constant: "kDrwWt1HSword"
constant = resolver.get_constant(4, "weapon_types")

# Search for entries
results = resolver.search_by_name("sword", "weapon_types")
```

### Using in Lua Scripts

```lua
-- Check weapon type
if figure:GetWeaponType() == kDrwWt1HSword then
    print("Unit has a one-handed sword")
end

-- Register spell effect
SpellEffect{
    line = kGdSpellLinePain,
    hit = "DefaultBlack",
    cast = "CastBlack",
    resolve = "ResolveBlack"
}

-- Check race
if figure:GetRace() == kGtRaceHuman then
    -- Human-specific logic
end
```

---

## Tools & Scripts

### Extract Mappings from Lua Sources

```bash
python3 src/helper_tools/extract_lua_mappings.py
```

Extracts all ID mappings from SpellForce Lua source files and generates `id_name_mappings.json`.

### Generate This Documentation

```bash
python3 src/helper_tools/generate_mappings_doc.py
```

Auto-generates this enhanced ID_MAPPINGS.md file from the extracted JSON data.

### Test Mapping Resolver

```bash
python3 src/TiganachReloaded/gui_editor/utils/mapping_resolver.py
```

Tests the MappingResolver class and displays sample lookups.

---

## References

### Source Files Analyzed
- `ModdingTools/SpellForceLUASources/script/DrwSound.lua` - Weapon sounds
- `ModdingTools/SpellForceLUASources/script/GdsDefines.lua` - Core constants
- `ModdingTools/SpellForceLUASources/object/object_effect_register.lua` - Effects and spells

### External Documentation
- SpellForce Modding SDK
- SFSF (SpellForce Spell Framework) API Documentation
- Community modding guides

### Tools
- **extract_lua_mappings.py** - Automated extraction tool
- **mapping_resolver.py** - Python API for ID resolution
- **id_name_mappings.json** - Machine-readable mapping database

---

**Auto-generated:** 2025-10-19 21:24:54
**Source:** `id_name_mappings.json`
**Game Version:** SpellForce: Platinum Edition (v1.x)
**Documentation Version:** 2.0.0 (Enhanced)