# SpellForce - Spell Line IDs Reference

This document catalogs all spell line constants (`kGdSpellLine*`) found in the game's Lua scripts. Each spell line represents a progression of spell levels within a specific spell type.

**Source File:** `object/object_effect_register.lua`

---

## Table of Contents

1. [Ability Spells (Combat Skills)](#ability-spells-combat-skills)
2. [Tower Spells](#tower-spells)
3. [Black Magic Spells](#black-magic-spells)
4. [White Magic Spells](#white-magic-spells)
5. [Fire Magic Spells](#fire-magic-spells)
6. [Ice Magic Spells](#ice-magic-spells)
7. [Earth Magic Spells](#earth-magic-spells)
8. [Mental Magic Spells](#mental-magic-spells)
9. [Elemental Magic Spells](#elemental-magic-spells)
10. [Buff/Debuff Spells](#buffdebuff-spells)
11. [Utility Spells](#utility-spells)

---

## Ability Spells (Combat Skills)

Special combat abilities that units can use in battle.

| Constant Name | Effect Type | Sound | Description |
|--------------|-------------|-------|-------------|
| `kGdSpellLineAbilityBerserk` | DecalBerserk | spell_melee_berserk | Increases damage output |
| `kGdSpellLineAbilityBlessing` | DecalBlessing | spell_melee_heal | Healing blessing |
| `kGdSpellLineAbilityTrueShot` | DecalTrueshot | spell_melee_berserk | Ranged accuracy boost |
| `kGdSpellLineAbilitySalvo` | DecalSalvo | spell_melee_berserk | Multiple shot ability |
| `kGdSpellLineAbilitySteelSkin` | DecalSteelskin | spell_melee_damageprotect | Physical damage reduction |
| `kGdSpellLineAbilityDurability` | DecalDurability | spell_melee_magicprotect | Magic damage reduction |
| `kGdSpellLineAbilityWarCry` | DecalBerserk | spell_melee_berserk | Battle cry buff |
| `kGdSpellLineAbilityBenefactions` | DecalBlessing | spell_melee_heal | Group blessing |
| `kGdSpellLineAbilityPatronize` | DecalTrueshot | spell_melee_magicprotect | Magic protection |
| `kGdSpellLineAbilityEndurance` | DecalSalvo | spell_melee_damageprotect | Endurance buff |
| `kGdSpellLineAbilityShelter` | DecalShelter | spell_melee_heal | Protective shelter |
| `kGdSpellLineAbilityShiftLife` | DecalShiftLife | spell_melee_shiftlife | Life transfer |
| `kGdSpellLineAbilityRiposte` | DecalRiposte | spell_melee_riposte | Counter-attack |
| `kGdSpellLineAbilityCriticalHits` | DecalCriticalHits | spell_melee_criticalhits | Critical strike chance |

---

## Tower Spells

Defensive tower attack spells.

| Constant Name | Effect Type | Sound | Description |
|--------------|-------------|-------|-------------|
| `kGdSpellLineIceburstTower` | IceBurst | spell_hit_iceburst | Ice tower attack |
| `kGdSpellLineArrowTower` | ArrowTower | - | Arrow tower projectile |
| `kGdSpellLineFireBurstTower` | FireBall | - | Fire tower burst |
| `kGdSpellLineHealingTower` | SimpleHeal | - | Healing tower aura |
| `kGdSpellLineHypnotizeTower` | Hypnotize | - | Mind control tower |
| `kGdSpellLinePainTower` | NoEffect | spell_hit_default_black | Pain tower |
| `kGdSpellLineStoneTower` | NoEffect | - | Stone tower |
| `kGdSpellLineExtinctTower` | Extinct | spell_hit_puff | Extinction tower |

---

## Black Magic Spells

Dark magic offensive and debuff spells.

| Constant Name | Effect Type | Sound | Description |
|--------------|-------------|-------|-------------|
| `kGdSpellLinePain` | DefaultBlack | spell_hit_default_black | Direct dark damage |
| `kGdSpellLineAuraWeakness` | AuraBlack | spell_hit_aura_black | Weakness aura (debuff) |
| `kGdSpellLineExtinct` | Extinct | spell_hit_puff | Instant kill (low level) |
| `kGdSpellLineDeath` | Death | spell_hit_puff | Death spell |
| `kGdSpellLinePestilence` | Pestilence | spell_hit_pestilence | Disease DOT |
| `kGdSpellLinePainArea` | DefaultBlack | spell_hit_default_black | AOE pain |
| `kGdSpellLineAuraSuffocation` | AuraBlack | spell_hit_puff | Suffocation aura |
| `kGdSpellLineSuicideDeath` | Death | spell_hit_default_black | Suicide damage |
| `kGdSpellLineSummonSkeleton` | - | - | Summon skeleton |
| `kGdSpellLineLifeTap` | LifeTap | spell_hit_weaken | Drain life |
| `kGdSpellLineDeathGrasp` | DeathGrasp | - | Death grip |
| `kGdSpellLineSummonGoblin` | - | - | Summon goblin |
| `kGdSpellLineRaiseDead` | RaiseDead | - | Raise undead from corpses |
| `kGdSpellLineAuraLifeTap` | AuraBlack | spell_hit_explosion | Life drain aura |
| `kGdSpellLineSummonSpectre` | - | - | Summon spectre |
| `kGdSpellLineFeignDeath` | - | - | Feign death |
| `kGdSpellLineAuraSlowFighting` | AuraBlack | spell_hit_aura_black | Slow attack speed aura |
| `kGdSpellLinePoison` | Poison | spell_hit_poison | Poison DOT |
| `kGdSpellLineAuraInflexibility` | AuraBlack | spell_hit_aura_black | Dexterity reduction aura |
| `kGdSpellLineDispelWhiteAura` | AuraBounceWhite | - | Remove white magic auras |
| `kGdSpellLineAuraSlowWalking` | AuraBlack | spell_hit_aura_black | Movement speed aura |
| `kGdSpellLineDarkBanishing` | DarkBanishing | - | Banish light creatures |
| `kGdSpellLineAuraInability` | AuraBlack | spell_hit_aura_black | Disable ability aura |
| `kGdSpellLineRemediless` | Remediless | spell_hit_remediless | Prevent healing DOT |
| `kGdSpellLineSlowness` | Slowness | spell_hit_slowness | Movement slow |
| `kGdSpellLineInflexibility` | Inflex | spell_hit_inflexibility | Dexterity debuff |
| `kGdSpellLineWeaken` | Weaken | spell_hit_weaken | Strength debuff |
| `kGdSpellLineSlowFighting` | SlowFighting | spell_hit_slowness | Attack speed slow |
| `kGdSpellLineInability` | Inability | spell_hit_puff | Disable abilities |
| `kGdSpellLineSuffocation` | Suffocation | spell_hit_puff | Mana drain |

---

## White Magic Spells

Holy magic healing and buff spells.

| Constant Name | Effect Type | Sound | Description |
|--------------|-------------|-------|-------------|
| `kGdSpellLineHealing` | SimpleHeal | spell_hit_healing | Basic healing |
| `kGdSpellLineHealingArea` | SimpleHeal | spell_hit_healing | AOE healing |
| `kGdSpellLineAuraStrength` | AuraWhite | spell_hit_aura_white | Strength buff aura |
| `kGdSpellLineGreaterHealing` | GreaterHeal | spell_hit_healing | Powerful healing |
| `kGdSpellLineAuraHealing` | AuraWhite | spell_hit_aura_white | Healing over time aura |
| `kGdSpellLineAuraEndurance` | AuraWhite | spell_hit_aura_white | Endurance aura |
| `kGdSpellLineSentinelHealing` | GreaterHeal | spell_hit_healing | Sentinel heal |
| `kGdSpellLineSuicideHeal` | SuicideHeal | - | Suicide heal (sacrifice) |
| `kGdSpellLineThornShield` | ThornShield | spell_hit_iceshield | Damage reflection |
| `kGdSpellLineCureDisease` | CureDisease | spell_hit_curedisease | Remove disease |
| `kGdSpellLineSummonWolf` | - | - | Summon wolf companion |
| `kGdSpellLineAuraRegeneration` | AuraWhite | spell_hit_aura_white | Regeneration aura |
| `kGdSpellLineDominateAnimal` | CharmChainWhite | spell_hit | Dominate animal |
| `kGdSpellLineCurePoison` | CurePoison | spell_hit_curedisease | Remove poison |
| `kGdSpellLineSummonBear` | - | - | Summon bear companion |
| `kGdSpellLineCharmAnimal` | CharmChainWhite2 | spell_hit | Charm animal |
| `kGdSpellLineAuraFastFighting` | AuraWhite | spell_hit_aura_white | Attack speed buff aura |
| `kGdSpellLineHallow` | StaticCloud | - | Holy ground |
| `kGdSpellLineAuraFlexibility` | AuraWhite | spell_hit_aura_white | Dexterity buff aura |
| `kGdSpellLineDispelBlackAura` | AuraBounceBlack | - | Remove dark magic auras |
| `kGdSpellLineAuraFastWalking` | AuraWhite | spell_hit_aura_white | Movement speed aura |
| `kGdSpellLineAuraLight` | AuraWhite | spell_hit_aura_white | Light aura (vision) |
| `kGdSpellLineAuraDexterity` | AuraWhite | spell_hit_aura_white | Dexterity aura |
| `kGdSpellLineInvulnerability` | SparkleSphere | spell_hit_strengthen | Temporary invulnerability |
| `kGdSpellLineQuickness` | Quickness | spell_hit_quickness | Movement speed buff |
| `kGdSpellLineFlexibility` | Flexibility | spell_hit_flexibility | Dexterity buff |
| `kGdSpellLineStrengthen` | Strengthen | - | Strength buff |
| `kGdSpellLineGuard` | Guard | spell_hit_flexibility | Defense buff |
| `kGdSpellLineRegenerate` | Regenerate | - | Health regeneration |
| `kGdSpellLineFastFighting` | FastFighting | spell_hit_quickness | Attack speed buff |

---

## Fire Magic Spells

Fire-based offensive spells.

| Constant Name | Effect Type | Sound | Description |
|--------------|-------------|-------|-------------|
| `kGdSpellLineFireBurst` | NoEffect | spell_hit_fireburst | Fire burst damage |
| `kGdSpellLineFireShield` | FireShield | spell_hit_fireshield | Fire shield (reflect damage) |
| `kGdSpellLineFireBall` | FireBall | spell_hit_fireball | Fireball projectile |
| `kGdSpellLineFireBallEffect` | NoEffect | - | Fireball secondary effect |
| `kGdSpellLineIlluminate` | Illuminate | spell_hit_illuminate | Create light |
| `kGdSpellLineFireElemental` | - | - | Summon fire elemental |
| `kGdSpellLineWaveOfFire` | WaveFire | - | Fire wave projectile |
| `kGdSpellLineMeltResistance` | MeltResistance | - | Reduce fire resistance |
| `kGdSpellLineFireShieldDamage` | BurnFromFeet | - | Fire shield damage proc |
| `kGdSpellLineRainOfFire` | AreaHitFire | - | AOE fire rain |
| `kGdSpellLineFireBlock` | FireBall | - | Fire blocking effect |

---

## Ice Magic Spells

Ice-based offensive and control spells.

| Constant Name | Effect Type | Sound | Description |
|--------------|-------------|-------|-------------|
| `kGdSpellLineIceBurst` | IcePackFast | spell_hit_iceburst | Ice burst damage |
| `kGdSpellLineIceShield` | IceShield | spell_hit_iceshield | Ice shield protection |
| `kGdSpellLineIceShieldStun` | IcePackFast | - | Ice shield stun effect |
| `kGdSpellLineFreeze` | IcePack | spell_hit_freeze | Freeze target |
| `kGdSpellLineFog` | Fog | - | Create fog |
| `kGdSpellLineIceElemental` | - | - | Summon ice elemental |
| `kGdSpellLineChillResistance` | ChillResistance | - | Reduce ice resistance |
| `kGdSpellLineBlizzard` | AreaHitIce | - | AOE blizzard |
| `kGdSpellLineIceArrowEffect` | IceBurst | - | Ice arrow effect |
| `kGdSpellLineIceBlock` | IceBurst | - | Ice blocking effect |

---

## Earth Magic Spells

Earth-based offensive and defensive spells.

| Constant Name | Effect Type | Sound | Description |
|--------------|-------------|-------|-------------|
| `kGdSpellLineRockBullet` | RockBullet | - | Rock projectile |
| `kGdSpellLineConservation` | Conservation | spell_hit_petrify | Damage reduction |
| `kGdSpellLineDetectMetal` | - | - | Detect metal resources |
| `kGdSpellLineDecay` | Decay | spell_hit_decay | Decay damage |
| `kGdSpellLineEarthElemental` | - | - | Summon earth elemental |
| `kGdSpellLineWaveOfRocks` | RockBullet | - | Rock wave projectile |
| `kGdSpellLinePetrify` | Petrify | spell_hit_petrify | Turn to stone |
| `kGdSpellLineStoneRain` | AreaHitEarth | - | AOE stone rain |
| `kGdSpellLineAuraSiegeTroll` | SiegeStone | - | Troll siege aura |
| `kGdSpellLineAuraSiegeHuman` | SiegeFlash | - | Human siege aura |
| `kGdSpellLineAuraSiegeElf` | SiegeStars | - | Elf siege aura |
| `kGdSpellLineAuraSiegeDarkElf` | SiegePlanets | - | Dark Elf siege aura |
| `kGdSpellLineAuraSiegeOrc` | SiegeFire | - | Orc siege aura |

---

## Mental Magic Spells

Mind-control and psychic spells.

| Constant Name | Effect Type | Sound | Description |
|--------------|-------------|-------|-------------|
| `kGdSpellLineSelfIllusion` | SelfIllusion | - | Create illusion of self |
| `kGdSpellLineDistract` | Forget | spell_hit_elektro | Distract enemy |
| `kGdSpellLineDominate` | CharmChain | spell_hit | Dominate mind |
| `kGdSpellLineInvisibility` | Invisibility | - | Turn invisible |
| `kGdSpellLineCharm` | CharmChain2 | spell_hit | Charm enemy |
| `kGdSpellLineBefriend` | Forget | - | Make friendly |
| `kGdSpellLineDisenchant` | CharmChainBreak | - | Break enchantments |
| `kGdSpellLineCharisma` | Charisma | - | Charisma buff |
| `kGdSpellLineShock` | HeadShock | spell_hit_shock | Mental shock |
| `kGdSpellLineConfuse` | Confuse | - | Confuse enemy |
| `kGdSpellLineHypnotize` | MentalHit | spell_hit_hypnotize | Hypnotize target |
| `kGdSpellLineHypnotizeTwo` | MentalHit | spell_hit_hypnotize | Hypnotize (level 2) |
| `kGdSpellLineAmok` | Amok | spell_hit | Cause berserker rage |
| `kGdSpellLineShockwave` | HeadShock | spell_hit_elektro | Mental shockwave |
| `kGdSpellLineDisrupt` | HeadFlash | spell_hit_slowness | Disrupt magic |
| `kGdSpellLineAuraHypnotization` | AuraMental | spell_hit_hypnotize | Hypnosis aura |
| `kGdSpellLineDemoralization` | Demoralize | - | Demoralize enemies |
| `kGdSpellLineManaDrain` | ManaOut | spell_hit_manadrain | Drain mana |
| `kGdSpellLineSacrificeMana` | ManaIn | spell_hit_quickness | Sacrifice mana for power |
| `kGdSpellLineDetectMagic` | - | - | Detect magic |
| `kGdSpellLineManaTap` | ManaOut | spell_hit_manatap | Mana tap |
| `kGdSpellLineAuraBrilliance` | AuraMental | spell_hit_aura_mental | Brilliance aura (mana regen) |
| `kGdSpellLineEnlightenment` | Enlightenment | - | Enlightenment buff |
| `kGdSpellLineAuraManaTap` | AuraMental | spell_hit_aura_mental | Mana tap aura |
| `kGdSpellLineMeditation` | NoEffect | - | Meditation (mana regen) |

---

## Elemental Magic Spells

Multi-element and elemental summoning spells.

| Constant Name | Effect Type | Sound | Description |
|--------------|-------------|-------|-------------|
| `kGdSpellLineFireElemental` | - | - | Summon fire elemental |
| `kGdSpellLineIceElemental` | - | - | Summon ice elemental |
| `kGdSpellLineEarthElemental` | - | - | Summon earth elemental |
| `kGdSpellLineAcidCloud` | Poison | spell_hit_poison | Acid cloud AOE |
| `kGdSpellLineSpark` | Spark | - | Electric spark |

---

## Utility Spells

Non-combat and utility spells.

| Constant Name | Effect Type | Sound | Description |
|--------------|-------------|-------|-------------|
| `kGdSpellLineIlluminate` | Illuminate | spell_hit_illuminate | Create light |
| `kGdSpellLineFog` | Fog | - | Create fog |
| `kGdSpellLineDetectMetal` | - | - | Detect metal |
| `kGdSpellLineDetectMagic` | - | - | Detect magic |
| `kGdSpellLineInvisibility` | Invisibility | - | Invisibility |
| `kGdSpellLineMeditation` | NoEffect | - | Meditation |

---

## Spell Effect Components

Each spell can have multiple effect components:

- **cast**: Visual/sound when spell is initiated
- **resolve**: Visual/sound when spell completes
- **hit**: Visual/sound when spell hits target
- **dot**: Damage-over-time visual effect
- **projectile**: Projectile visual (for ranged spells)
- **world**: World effect (for AOE/environmental)
- **aura**: Continuous aura effect

### Sound Components
- **castsound**: Sound on cast
- **hitsound**: Sound on hit
- **resolvesound**: Sound on resolve
- **dotsound**: Sound for DOT ticks

---

## Notes

1. **Spell Lines vs Spell IDs**: Each `kGdSpellLine*` represents a spell progression (e.g., Healing I, II, III). Individual spell levels have separate IDs in the game data.

2. **Effect Registration**: These constants are registered in `object_effect_register.lua` which maps them to visual/audio effects.

3. **Numeric Values**: The actual numeric IDs for these constants are defined in the C++ engine and not visible in Lua scripts.

4. **Aura Spells**: Auras are persistent area effects that continuously affect units within range.

5. **DOT Spells**: Damage-over-time spells apply periodic damage after initial hit.

6. **Suicide Spells**: Some spells (SuicideDeath, SuicideHeal) kill the caster as part of their effect.

---

## Spell Schools Summary

| School | Spell Count | Primary Focus |
|--------|-------------|---------------|
| Black Magic | 30+ | Damage, debuffs, necromancy |
| White Magic | 30+ | Healing, buffs, protection |
| Fire Magic | 10+ | Direct damage, burning |
| Ice Magic | 9+ | Damage, slowing, freezing |
| Earth Magic | 13+ | Defense, petrification, siege |
| Mental Magic | 24+ | Mind control, mana manipulation |
| Abilities | 14 | Combat skills |
| Towers | 8 | Defensive structures |

**Total Documented Spell Lines: 140+**

---

**Last Updated:** 2025-10-18  
**Source:** SpellForce Lua Sources - object/object_effect_register.lua  
**Game Version:** SpellForce Platinum Edition
