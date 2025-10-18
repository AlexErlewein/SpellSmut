# SpellForce Platinum Edition - Spell System Guide

## Table of Contents
1. [Overview](#overview)
2. [Spell Architecture](#spell-architecture)
3. [Magic Schools](#magic-schools)
4. [Spell Components](#spell-components)
5. [Spell Effects System](#spell-effects-system)
6. [Visual Effects](#visual-effects)
7. [Audio System](#audio-system)
8. [Spell Data Structure](#spell-data-structure)
9. [Creating Custom Spells](#creating-custom-spells)
10. [Advanced Techniques](#advanced-techniques)
11. [Reference Tables](#reference-tables)

---

## Overview

SpellForce implements a **comprehensive magic system** with:
- **5 Magic Schools**: White, Black, Elemental (Fire/Ice/Earth), Mental
- **240+ unique spells** including variants and chains
- **Modular effect system** (cast, resolve, projectile, target, over-time)
- **Lua-based visual effects** with particle systems
- **Sound integration** with spatial audio

### Core Philosophy

The spell system separates **mechanics** (C++ engine) from **presentation** (Lua scripts):
- **C++**: Damage calculation, targeting, cooldowns, mana costs
- **Lua**: Visual effects, particle systems, sound triggers
- **Data Files**: Spell definitions, stat progression, balance values

---

## Spell Architecture

### Spell Pipeline

```
Player Action → Cast Phase → Projectile Phase → Resolve Phase → Target Effects → Over-Time Effects
                    ↓              ↓                 ↓               ↓                 ↓
              Cast VFX      Travel VFX         Impact VFX      Hit VFX           Buff/Debuff VFX
              Cast SFX      Flight SFX         Resolve SFX     Hit SFX           Aura SFX
```

### File Structure

```
H:\SpellSmut/
├── script/
│   ├── sql_spellline.lua              # Spell database (240+ spells)
│   └── DrwSound.lua                   # Sound event definitions
├── object/
│   ├── object_effect_cast.lua         # Cast visual effects
│   ├── object_effect_resolve.lua      # Impact/resolve effects
│   ├── object_effect_aura.lua         # Persistent aura effects
│   ├── object_effect_area.lua         # Area-of-effect visuals
│   └── object_effect_standard.lua     # Common effects library
└── sound/
    ├── spell_white_cast_*.wav
    ├── spell_black_resolve_*.wav
    └── spell_fire_hit_*.wav
```

---

## Magic Schools

### 1. White Magic (Holy/Life)

**SpellLineBase**: `0`

**Philosophy**: Healing, protection, buffs, holy damage to undead

**Color Theme**: White, gold, light blue

**Characteristic Effects**:
- Glowing star particles
- God rays (cylinder_stripes mesh)
- Soft white light
- Ascending particles

**Key Spells**:
- **Healing** (ID 2): Single-target heal
- **HealingArea** (ID 43): AoE heal
- **GreaterHealing** (ID 45): Stronger heal
- **Invulnerability** (ID 6): Damage immunity
- **Regenerate** (ID 56): Health-over-time
- **Guard** (ID 54): Defense buff
- **Strengthen** (ID 52): Strength buff
- **HolyMight** (ID 57): Multi-stat buff
- **Hallow** (ID 58): Damage to undead
- **RemoveCurse** (ID 55): Dispel debuffs

**Visual Example** (from `object_effect_cast.lua`):
```lua
-- Cast White
local particles=33
NewMovie(particles)
Translation{max={0,0,-4}, dim=kDrwDimParticle, path=kDrwPathRandom}
Translation{min={0,0,5}}
Burst{particles=particles, radius1=0.4, radius2=0.4, height=5}
Scale{min=0.0, max=0.1, range=time/1.5, trail=1, play=kDrwPlayBounce, path=kDrwPathCosine}
Color{min={1,1,1,0}, max={1,1,1,0.5}, trail=1, range=time/2.4, play=kDrwPlayBounce, path=kDrwPathCosine}
local flitter = NewObject{billboard=flics.star6point, movie=pMovie}
```

---

### 2. Black Magic (Necromancy/Dark)

**SpellLineBase**: `3`

**Philosophy**: Damage-over-time, debuffs, summoning undead, life drain

**Color Theme**: Red, orange, dark purple, black smoke

**Characteristic Effects**:
- Lightning bolts
- Skulls and bats
- Dark smoke/fog
- Blood red particles

**Key Spells**:
- **Death** (ID 3): Instant death (bosses)
- **Decay** (ID 16): Damage-over-time
- **DecayArea** (ID 17): AoE DoT
- **Pain** (ID 18): Direct damage
- **PainArea** (ID 28): AoE damage
- **LifeTap** (ID 19): Drain health
- **Poison** (ID 5): Poison DoT
- **Pestilence** (ID 23): Disease DoT
- **Slowness** (ID 4): Movement speed debuff
- **Weaken** (ID 35): Strength debuff
- **Inflexibility** (ID 34): Dexterity debuff
- **SummonGoblin** (ID 20): Summon creature
- **SummonSkeleton** (ID 29): Summon undead
- **SummonDemon** (ID 31): Summon demon
- **RaiseDead** (ID 30): Resurrect corpse
- **DeathGrasp** (ID 32): Pull enemy
- **DarkBanishing** (ID 36): Banish summons

**Visual Example** (from `object_effect_cast.lua`):
```lua
-- Cast Black
local lightning = Lightning{range=0.08, flic=flics.simplelightning, mode=0}
NewMovie()
Color{min={0.8,0.5,0.2,1}, max={0.8,0.5,0.2,0}, dim=kDrwDimTimeScaled, path=kDrwPathParabola}
Scale{min=0, max=1, range=0.1, start=0.5, play=kDrwPlayClamped}
local right = NewObject{subobject=lightning, bone=kDrwBoneChest, bonesource=kDrwBoneRightHand}
```

**Resolve Effect**:
```lua
-- Black Resolve (Bats + Smoke)
local lParticles=8 * 2
NewMovie(lParticles)
Translation{min={0,0,0}, max={0,0,5}}
Burst{radius1=1, radius2=1, trail=0}
Color{min={0,0,0,0.8}, max={0,0,0,0.1}, play=kDrwPlayClamped, path=kDrwPathParabola}
Scale{min={0,0,0}, max={0.4,0.4,0.4}, range=0.2, play=kDrwPlayClamped}
local bats = NewObject{billboard=flics.bat, movie=pMovie}
```

---

### 3. Fire Magic (Elemental)

**SpellLineBase**: `1`

**Philosophy**: Direct damage, burn effects, explosive area damage

**Color Theme**: Red, orange, yellow flames

**Characteristic Effects**:
- Fire particles
- Smoke trails
- Heat distortion
- Explosion flashes

**Key Spells**:
- **FireBurst** (ID 1): Single-target damage
- **FireBall** (ID 13): Projectile damage
- **FireShield** (ID 12): Damage reflection
- **RainOfFire** (ID 73): AoE damage-over-time
- **FireElemental** (ID 133): Summon fire elemental
- **WaveOfFire** (ID 134): Cone attack
- **MeltResistance** (ID 135): Reduce fire resistance
- **ChainFireball** (ID 204): Chain lightning style
- **FireResistance** (ID 173): Buff fire resistance
- **SummonFireGolem** (ID 203): Summon golem

**Visual Example** (from `object_effect_cast.lua`):
```lua
-- Cast Fire
Fire{buffer=0.4, particles=9, size=1, size1=0.9, size2=0.2, height=1, 
     top=0, width=0.1, ground=0, 
     color1={1,0.8,0,0.7}, color2={1,0.2,0,0.4}, 
     path=kDrwPathParabola}
Scale{min=0, max=1, start=0.0, range=0.2, play=kDrwPlayClamped}
Scale{min=1}
local fire = NewObject{billboard=flics.smoke, movie=pMovie}
local fires = AttachToBones{object=fire, bones={kDrwBoneRightPalm, kDrwBoneLeftPalm}}
```

---

### 4. Ice Magic (Elemental)

**SpellLineBase**: `2`

**Philosophy**: Slow effects, freezing, shatter damage, defensive shields

**Color Theme**: Light blue, white, icy cyan

**Characteristic Effects**:
- Snowflake particles
- Icy mist
- Crystalline effects
- Frost accumulation

**Key Spells**:
- **IceBurst** (ID 14): Single-target damage
- **Freeze** (ID 9): Immobilize target
- **FreezeArea** (ID 207): AoE freeze
- **IceShield** (ID 15): Damage absorption
- **IceShieldStun** (ID 22): Counter-stun
- **Blizzard** (ID 74): AoE damage storm
- **IceElemental** (ID 136): Summon ice elemental
- **WaveOfIce** (ID 137): Cone attack
- **ChillResistance** (ID 138): Reduce cold resistance
- **ChainIceburst** (ID 205): Chain effect
- **SummonIceGolem** (ID 206): Summon golem

**Visual Example** (from `object_effect_cast.lua`):
```lua
-- Cast Ice
Smoke{trail=-1, time=2, particles=22, offset={0,0,-0.2}, growth=1, 
      velocity={0.5,0.2,2}, gravity={-1,0,-4}, 
      color1={0.15,0.3,0.5,0}, color2={0.15,0.3,0.5,0.8}}
Scale{min=0.1, max=1, path=kDrwPathParabola, trail=-1, range=2}
local smoke = NewObject{billboard=flics.circle, movie=pMovie}
local smoke = AttachToBones{object=smoke, bones={kDrwBoneRightHand, kDrwBoneLeftHand}}
```

---

### 5. Earth Magic (Elemental)

**SpellLineBase**: `0` (shares with White)

**Philosophy**: Protection, stone-based attacks, pet summoning

**Color Theme**: Brown, grey, earth tones

**Characteristic Effects**:
- Rock particles
- Dust clouds
- Stone formations
- Ground ripples

**Key Spells**:
- **Stone** (ID 87): Turn to stone
- **RockBullet** (ID 139): Projectile
- **StoneRain** (ID 76): AoE bombardment
- **WallOfRocks** (ID 77): Barrier
- **RingOfRocks** (ID 78): Circular wall
- **Petrify** (ID 25): Immobilize
- **CharmAnimal** (ID 46): Tame creature
- **DominateAnimal** (ID 108): Control animal
- **SummonWolf** (ID 106): Summon wolf
- **SummonBear** (ID 109): Summon bear
- **EarthElemental** (ID 141): Summon elemental
- **WaveOfRocks** (ID 142): Cone attack
- **Conservation** (ID 140): Mana preservation
- **ChainRockBullet** (ID 208): Chain effect
- **SummonEarthGolem** (ID 209): Summon golem

**Visual Example** (from `object_effect_cast.lua`):
```lua
-- Cast Earth
local whirlwind = Whirlwind{startsize=0.1, stopsize=1, flic=flics.smoke, 
                             particles=3, time=0.3, tilt=0, layers=5, 
                             radius=1, height=2, 
                             startcolor={0.8,0.6,0.4,1}, 
                             stopcolor={0.9,0.3,0.2,0}}
NewMovie()
Scale{min=-1}  -- Inverted to suck from ground
local suckup = NewObject{subobject=whirlwind, bone=kDrwBoneRightHand}
```

---

### 6. Mental Magic

**SpellLineBase**: `4`

**Philosophy**: Mind control, illusions, mana manipulation, fear

**Color Theme**: Green, yellow, purple psychic energy

**Characteristic Effects**:
- Concentric rings
- Brain/mind symbols
- Pulsing waves
- Hypnotic spirals

**Key Spells**:
- **Hypnotize** (ID 21): Mind control
- **HypnotizeArea** (ID 215): AoE control
- **Forget** (ID 62): Erase memory
- **Confusion** (ID 72): Random actions
- **ConfuseArea** (ID 216): AoE confusion
- **Fear** (ID 71): Flee effect
- **Amok** (ID 79): Berserk rage
- **Charm** (ID 122): Befriend enemy
- **Dominate** (ID 120): Full control
- **Befriend** (ID 123): Permanent ally
- **SelfIllusion** (ID 63): Change appearance
- **ObjectIllusion** (ID 121): Create fake object
- **Invisibility** (ID 86): Stealth
- **MirrorImage** (ID 211): Create copies
- **ManaTap** (ID 67): Steal mana
- **ManaDrain** (ID 68): Drain mana
- **Brilliance** (ID 65): Mana regeneration
- **SacrificeMana** (ID 66): Convert health to mana
- **Retention** (ID 64): Preserve mana
- **Shock** (ID 69): Interrupt casting
- **Disrupt** (ID 70): Silence target
- **Shockwave** (ID 126): AoE knockback
- **Demoralization** (ID 128): Fear aura
- **Charisma** (ID 125): Charm aura

**Visual Example** (from `object_effect_cast.lua`):
```lua
-- Cast Mental
NewMovie(5)
Scale{min=0, max=1.5, range=1, trail=2}  -- Expanding rings
Color{min={1,1,0,0.4}, max={0,0.5,1,0}, range=1, trail=2}
Scale{min=0, max=1, range=0.2, play=kDrwPlayClamped}
local rings = NewObject{billboard=flics.ring, movie=pMovie, bone=kDrwBoneCrown}
```

---

## Spell Components

### Component Types

Each spell can have up to **5 visual effect components**:

1. **effectscast**: Cast animation (at caster)
2. **effectsresolve**: Resolve animation (at target/impact)
3. **effectsprojectile**: Travel animation (for ranged spells)
4. **effectstarget**: Hit animation (on target)
5. **effectsovertime**: Persistent effect (buffs/debuffs/auras)

### Spell Flags

From `sql_spellline.lua`, each spell has 8 flags:

```lua
{
    includename="FireBurst",  -- Internal spell name
    player=0,                 -- Player castable (0=yes, 1=no)
    npc=0,                    -- NPC castable
    flag3=0,                  -- Aura spell (1=yes)
    flag4=0,                  -- Toggle spell
    flag5=1,                  -- Unknown
    flag6=0,                  -- Unknown
    flag7=0,                  -- Unknown
    flag8=0,                  -- Unknown
    effectscast={},           -- Cast VFX list
    effectsresolve={},        -- Resolve VFX list
    effectsprojectile={},     -- Projectile VFX list
    effectstarget={},         -- Target VFX list
    effectsovertime={},       -- Over-time VFX list
    spelllinebase=1,          -- Magic school (0=White, 1=Fire, 2=Ice, 3=Black, 4=Mental, 5=Elemental)
}
```

### Flag Meanings

**flag3 (Aura Flag)**:
- `0`: Normal spell
- `1`: Aura spell (persistent AoE effect around caster)

**Examples**:
```lua
-- Normal spell
[1] = {includename="FireBurst", flag3=0, ...}

-- Aura spell
[88] = {includename="AuraWeakness", flag3=1, flag4=1, flag5=1, ...}
```

---

## Spell Effects System

### Visual Effect Pipeline

SpellForce uses a **particle-based effect system** written in Lua:

```lua
-- Basic effect structure
NewMovie(particles)              -- Create particle system
Translation{...}                 -- Movement
Rotation{...}                    -- Rotation
Scale{...}                       -- Scaling
Color{...}                       -- Color animation
Burst/Throw/Cloud/Fire/etc{...} -- Particle behavior
NewObject{billboard/mesh/...}    -- Render object
EffectSave("EffectName")         -- Register with engine
```

### Core Effect Functions

#### 1. **NewMovie(particles)**
Creates a particle system movie

```lua
NewMovie(33)  -- 33 particles
-- Apply transformations
local effect = NewObject{billboard=flics.star6point, movie=pMovie}
```

#### 2. **Translation{...}**
Moves particles over time

```lua
Translation{min={0,0,0}, max={0,0,5}, range=1, play=kDrwPlayClamped}
-- Moves from origin to 5 units up over 1 second
```

#### 3. **Rotation{...}**
Rotates particles

```lua
Rotation{axis="z", min=0, max=360, range=2}  -- Full rotation over 2 seconds
```

#### 4. **Scale{...}**
Changes particle size

```lua
Scale{min=0.1, max=1, range=0.5, path=kDrwPathParabola}
-- Grow from 0.1 to 1.0 with parabolic easing
```

#### 5. **Color{...}**
Animates particle color

```lua
Color{min={1,0,0,0}, max={1,1,1,1}, range=1, path=kDrwPathLinear}
-- Fade from transparent red to opaque white
```

---

### Particle Behaviors

#### **Burst{...}** - Explosion pattern
```lua
Burst{particles=30, radius1=0.5, radius2=2, height=3, trail=0}
-- Particles burst outward from center
```

#### **Throw{...}** - Ballistic trajectory
```lua
Throw{velocity={0,0,6}, gravity={0,0,-4.5}, time=1, trail=0}
-- Throw particles upward with gravity
```

#### **Fire{...}** - Flame simulation
```lua
Fire{particles=9, size=1, size1=0.9, size2=0.2, height=1, 
     color1={1,0.8,0,0.7}, color2={1,0.2,0,0}}
-- Realistic fire with color transition
```

#### **Smoke{...}** - Smoke/fog simulation
```lua
Smoke{particles=22, time=2, offset={1,0,0}, velocity={3,0,0}, 
      gravity={0,0,5}, growth=0.2, 
      color1={0.5,0.5,0.5,0}, color2={0.3,0.3,0.3,0.8}}
-- Rising smoke with dissipation
```

#### **Cloud{...}** - Cloud/mist effect
```lua
Cloud{particles=11, time=1, velocity={0,0,1}, size=0.1, 
      color1={0.6,0.6,1,0.4}, color2={0.6,0.6,1,0}}
-- Expanding misty cloud
```

#### **Lightning{...}** - Electric bolt
```lua
local lightning = Lightning{range=0.1, flic=flics.simplelightning, mode=0}
-- Animated lightning texture
```

#### **Whirlwind{...}** - Tornado/vortex
```lua
Whirlwind{startsize=0.1, stopsize=1, particles=3, time=2, 
          tilt=0, layers=5, radius=1, height=2,
          startcolor={1,1,1,1}, stopcolor={1,1,1,0}}
-- Spiraling vortex effect
```

---

### Animation Paths

Control how values interpolate over time:

```lua
kDrwPathLinear       -- Constant speed
kDrwPathParabola     -- Ease in/out (parabolic)
kDrwPathNegParabola  -- Inverse parabola
kDrwPathCosine       -- Smooth wave
kDrwPathRandom       -- Random values
```

**Example**:
```lua
Scale{min=0, max=1, range=1, path=kDrwPathParabola}
-- Scales from 0 to 1 with smooth acceleration/deceleration
```

### Play Modes

```lua
kDrwPlayClamped      -- Play once, stop at end
kDrwPlayBounce       -- Bounce back and forth
kDrwPlayContinous    -- Loop forever
```

---

## Visual Effects

### Render Types

#### 1. **Billboard** - Camera-facing sprite
```lua
NewObject{billboard=flics.star6point, movie=pMovie}
-- Always faces camera
```

#### 2. **Mesh** - 3D model
```lua
NewObject{mesh=flics.cylinder_stripes, movie=pMovie}
-- Actual 3D geometry
```

#### 3. **Decal** - Ground projection
```lua
NewObject{decal=flics.circle, movie=pMovie}
-- Projects onto terrain
```

### Bone Attachment

Attach effects to character bones:

```lua
NewObject{billboard=flics.star6point, bone=kDrwBoneRightHand}
-- Follows right hand movement
```

**Common Bones**:
- `kDrwBoneMain` - Root
- `kDrwBoneChest` - Torso
- `kDrwBoneHead` - Head
- `kDrwBoneCrown` - Top of head
- `kDrwBoneRightHand` / `kDrwBoneLeftHand` - Hands
- `kDrwBoneRightPalm` / `kDrwBoneLeftPalm` - Palms
- `kDrwBoneRightShoulder` / `kDrwBoneLeftShoulder` - Shoulders

### Coordinate Systems

```lua
kDrwCsWorld          -- World space (absolute)
kDrwCsBone           -- Bone-relative space
kDrwCsFloor          -- Project to ground
kDrwCsSpan           -- Line between two bones
kDrwCsProjectile     -- Follow projectile path
kDrwCsAim            -- Aim at target
kDrwCsResetRotation  -- Ignore parent rotation
```

**Example - Lightning Between Hands**:
```lua
NewObject{subobject=lightning, 
          bone=kDrwBoneChest,           -- End point
          bonesource=kDrwBoneRightHand, -- Start point
          restriction=kDrwCsSpan}       -- Draw line between
```

---

### Lighting Effects

Add dynamic lights to spells:

```lua
LightMovie{offset={0,0.5,0}, size=1.5, deviation=0.1, 
           color={1,0,0,0.5}, flicker=2}
local radiosity = Radiosity{movie=pMovie, bone=kDrwBoneChest, restriction=kDrwCsBone}
```

**Parameters**:
- `offset`: Position offset from attach point
- `size`: Light radius
- `deviation`: Random flicker amount
- `color`: Light color (RGBA)
- `flicker`: Flicker intensity

---

## Audio System

### Sound Event Structure

From `DrwSound.lua`:

```lua
spell_white_cast = {
    File = "spell_white_cast",       -- Sound file name (without .wav)
    Volume = 1.0,                    -- 0.0 to 1.0+
    FallOffMin = 10,                 -- Start attenuation distance
    FallOffMax = 90,                 -- Inaudible distance
}
```

### Spell Sound Categories

#### Cast Sounds
Played when spell begins:
```lua
spell_white_cast
spell_black_cast
spell_fire_cast
spell_ice_cast
spell_earth_cast
spell_mental_cast
```

#### Resolve Sounds
Played on impact/effect:
```lua
spell_white_resolve
spell_black_resolve
spell_fire_resolve
spell_ice_resolve
spell_earth_resolve
spell_mental_resolve
```

#### Hit Sounds
Played when target takes damage:
```lua
spell_fire_hit
spell_ice_hit
spell_black_hit
spell_mental_hit
```

#### Damage-Over-Time Sounds
Played periodically:
```lua
spell_fire_dot
spell_poison_dot
spell_disease_dot
```

#### Summon Sounds
Creature summoning:
```lua
spell_summon_goblin
spell_summon_skeleton
spell_summon_demon
spell_summon_elemental_fire
spell_summon_elemental_ice
spell_summon_elemental_earth
```

#### Resist Sounds
Played when spell is resisted:
```lua
spell_resist_white
spell_resist_black
spell_resist_fire
spell_resist_ice
spell_resist_mental
```

---

## Spell Data Structure

### Complete Spell Definition

```lua
-- sql_spellline.lua
[13] = {
    includename="FireBall",          -- Spell identifier
    player=0,                        -- Castable by player (0=yes)
    npc=0,                           -- Castable by NPC
    flag3=0,                         -- Not an aura
    flag4=0,                         -- Not a toggle
    flag5=1,                         -- Flag 5
    flag6=0,                         -- Flag 6
    flag7=0,                         -- Flag 7
    flag8=0,                         -- Flag 8
    effectscast={},                  -- Cast visual effects
    effectsresolve={},               -- Resolve effects
    effectsprojectile={},            -- Projectile trail
    effectstarget={},                -- Target hit effect
    effectsovertime={},              -- Persistent effects
    spelllinebase=1,                 -- Fire magic (1)
}
```

### Spell Schools (spelllinebase)

```lua
0 = White Magic
1 = Fire Magic
2 = Ice Magic
3 Black Magic
4 = Mental Magic
5 = Elemental Magic (generic)
```

---

## Creating Custom Spells

### Step 1: Design the Spell

**Define**:
1. **Name**: `MyCustomFireBolt`
2. **School**: Fire (spelllinebase=1)
3. **Effect**: Single-target projectile damage
4. **Visual**: Flaming projectile with smoke trail
5. **Sound**: Fire cast, fire resolve, fire hit

---

### Step 2: Create Visual Effects

**File**: `object/object_effect_custom.lua`

```lua
-- Cast Effect
Fire{particles=15, size=0.8, height=1, 
     color1={1,0.8,0,1}, color2={1,0.2,0,0.5}}
Scale{min=0.5}
local castfire = NewObject{billboard=flics.smoke, movie=pMovie}
local casteffect = AttachToBones{object=castfire, bones={kDrwBoneRightPalm}}
NewObject{subobject=casteffect}
EffectSave("CastMyFireBolt")

-- Projectile Effect
Fire{particles=7, size=0.5, height=0.5, ground=0, width=0.1,
     color1={1,0.5,0,1}, color2={0.5,0,0,0}}
local trail = NewObject{billboard=flics.smoke, movie=pMovie}

NewMovie()
Rotation{axis="x", min=90, direction=0}
Scale{min=1.5}
local projectile = NewObject{subobject=trail, movie=pMovie, 
                             restriction=kDrwCsProjectile, 
                             bone=kDrwBoneChest, 
                             bonesource=kDrwBoneRightHand}
NewObject{subobject=projectile}
EffectSave("ProjectileMyFireBolt")

-- Resolve Effect (Impact)
-- Explosion burst
NewMovie(22)
Throw{velocity={0,0,3}, gravity={0,0,-3}, time=0.8, trail=0}
Burst{particles=22, radius1=0.5, radius2=2, trail=0}
Color{min={1,0.5,0,1}, max={1,0,0,0}, range=0.8, path=kDrwPathParabola}
Scale{min=0.3}
local burst = NewObject{billboard=flics.smoke, movie=pMovie}

-- Flash
NewMovie()
Scale{min=2, max=0, range=0.3, play=kDrwPlayClamped}
Color{min={1,1,0,0.8}, max={1,0,0,0}, range=0.3, play=kDrwPlayClamped}
local flash = NewObject{billboard=flics.circle, movie=pMovie}

NewObject{subobject={burst, flash}}
EffectSave("ResolveMyFireBolt")
```

---

### Step 3: Register Sound Events

**File**: `script/DrwSound.lua`

Add to spell sound definitions:

```lua
spell_myfirebolt_cast = {
    File = "spell_fire_cast",   -- Reuse existing sound
    Volume = 1.0,
    FallOffMin = 10,
    FallOffMax = 80,
}

spell_myfirebolt_resolve = {
    File = "spell_fire_hit",
    Volume = 1.0,
    FallOffMin = 10,
    FallOffMax = 90,
}
```

---

### Step 4: Add to Spell Database

**File**: `script/sql_spellline.lua`

```lua
[300] = {
    includename="MyCustomFireBolt",
    player=0,                        -- Player can cast
    npc=0,                           -- NPC can cast
    flag3=0,                         -- Not an aura
    flag4=0,                         -- Not a toggle
    flag5=1,                         
    flag6=0,
    flag7=0,
    flag8=0,
    effectscast={"CastMyFireBolt"},
    effectsresolve={"ResolveMyFireBolt"},
    effectsprojectile={"ProjectileMyFireBolt"},
    effectstarget={},
    effectsovertime={},
    spelllinebase=1,                 -- Fire magic
}
```

---

### Step 5: Define Spell Stats

**(Game data files - not in provided scripts)**

Create spell stats in game database:

```
Spell ID: 300
Name: My Custom Fire Bolt
Description: Hurls a fiery projectile at the target
Mana Cost: 15
Cast Time: 1.5 seconds
Cooldown: 3 seconds
Range: 20 meters
Damage: 50-80 fire damage
```

---

## Advanced Techniques

### Chain Spells

**Chain Lightning Effect**:

```lua
-- Chain spell hits multiple targets in sequence
[204] = {includename="ChainFireball", spelllinebase=1, ...}

-- Visual: Lightning arc between targets
function ChainLightning(params)
    local lightning = Lightning{range=0.2, flic=flics.lightning_chain}
    
    NewMovie()
    -- Draw line from source to target
    local arc = NewObject{subobject=lightning, 
                          restriction=kDrwCsSpan,
                          bonesource="PreviousTarget",
                          bone="CurrentTarget"}
    return arc
end
```

---

### Aura Spells

**Persistent AoE around caster**:

```lua
[88] = {
    includename="AuraWeakness",
    flag3=1,              -- Aura flag
    flag4=1,              -- Toggle
    flag5=1,
    ...
}
```

**Visual** (from `object_effect_aura.lua`):

```lua
-- Rotating particle circle
function Aura(params)
    params.particles = params.particles or 11
    params.rolltime = params.rolltime or 15
    params.radius = params.radius or 0.5
    
    CircleTrail{time=10, rolltime=params.rolltime, 
                radius=params.radius, length=1}
    Scale{min=1.2}
    local trail = NewObject{billboard=params.flic, movie=pMovie}
    
    NewMovie(3)  -- 3 layers rotated
    Rotation{axis="z", dim=kDrwDimParticle}
    return NewObject{subobject=trail, bone=kDrwBoneMain, 
                     restriction=kDrwCsWorld, movie=pMovie}
end

-- Fire aura
Aura{flic=flics.star6point, particles=15, 
     startcolor={1,0.5,0,1}, stopcolor={1,0,0,0}}
EffectSave("AuraFire")
```

---

### Area-of-Effect Spells

**Blizzard** (from `object_effect_area.lua`):

```lua
-- Falling projectiles
NewMovie()
Translation{min={10,0,30}, max={0,0,-1}, range=2.1, play=kDrwPlayClamped}
Rotation{axis="y", min=15, max=15, direction=0}
Scale{min=0, max=1, range=0.2, play=kDrwPlayClamped}

-- Ice particle
local iceflame = NewObject{billboard=flics.circle, ...}
local stone = NewObject{mesh=flics.icerocks[4], ...}
local fallout = NewObject{subobject={iceflame, stone}, movie=pMovie}

-- Shadow on ground
NewMovie()
Translation{min={10,0,30}, max={0,0,-1}, range=2.1, play=kDrwPlayClamped}
Scale{min=0.5, max=1, range=2.2}
Color{min={0,0,0,0}, max={0,0,0,0.4}, range=2, play=kDrwPlayClamped}
local decal = NewObject{decal=flics.circledark, movie=pMovie}

NewObject{subobject={decal, fallout}}
EffectSave("BlizzardFall")

-- Impact effect
Cloud{particles=22, time=1, velocity={1,0,2}, 
      color1={0.6,0.8,1,1}, color2={1,1,1,0}}
Scale{min=3}
local cloud = NewObject{billboard=flics.ice, movie=pMovie}

-- Ice burst
NewMovie(11)
Throw{time=1, particles=11, velocity={0,0,2}, gravity={0,0,-1.5}, trail=0}
Burst{particles=11, radius1=0.2, radius2=3.7, trail=0}
Color{min={0.3,0.5,1,1}, max={0,0,1,0}, range=1, path=kDrwPathParabola}
Scale{min=0.1}
local burst = NewObject{mesh=flics.icerocks, movie=pMovie}

NewObject{subobject={burst, cloud}}
EffectSave("BlizzardHit")
```

---

### Summon Spells

**Summon with Portal Effect**:

```lua
-- Portal appears
NewMovie()
Rotation{range=5}
Scale{min=0, max=2, range=0.5, play=kDrwPlayClamped}
Color{min={0.5,0,1,0}, max={0.5,0,1,1}, range=0.5, play=kDrwPlayClamped}
local portal = NewObject{decal=flics.runes, movie=pMovie}

-- Energy burst
NewMovie(33)
Burst{particles=33, radius1=0, radius2=2, height=3}
Translation{max={0,0,3}, range=0.8, play=kDrwPlayClamped}
Color{min={1,0,1,1}, max={1,0,1,0}, range=0.8, path=kDrwPathParabola}
Scale{min=0.3}
local energy = NewObject{billboard=flics.star6point, movie=pMovie}

-- Flash
NewMovie()
Scale{min=3, max=0, range=0.3, play=kDrwPlayClamped}
Color{min={1,1,1,1}, max={1,1,1,0}, range=0.3}
local flash = NewObject{billboard=flics.circle, movie=pMovie}

NewObject{subobject={portal, energy, flash}}
EffectSave("SummonPortal")
```

---

### Buff/Debuff Effects

**Strength Buff** (persistent glow):

```lua
-- Body glow
BodyGlow{time=10, size2=3, particles=4, radius2=0.2, 
         color1={1,0.5,0,0.4}, color2={1,0,0,0}}
Scale{min=0.15}
local glow = NewObject{billboard=flics.star6point, movie=pMovie, 
                       bone=kDrwBoneChest}

-- Light radiosity
LightMovie{offset={0,0.5,0}, size=1.2, deviation=0.1, 
           color={1,0.5,0,0.3}, flicker=0.5}
local light = Radiosity{movie=pMovie, bone=kDrwBoneChest, 
                        restriction=kDrwCsBone}

NewObject{subobject={glow, light}}
EffectSave("BuffStrength")
```

---

## Reference Tables

### Spell ID Quick Reference

| ID | Name | School | Type | Description |
|----|------|--------|------|-------------|
| 1 | FireBurst | Fire | Direct | Single-target fire damage |
| 2 | Healing | White | Heal | Single-target heal |
| 3 | Death | Black | Direct | Instant death |
| 4 | Slowness | Black | Debuff | Reduce movement speed |
| 5 | Poison | Black | DoT | Poison damage over time |
| 6 | Invulnerability | White | Buff | Immunity to damage |
| 9 | Freeze | Ice | CC | Immobilize target |
| 13 | FireBall | Fire | Projectile | Fire projectile damage |
| 14 | IceBurst | Ice | Direct | Ice damage |
| 16 | Decay | Black | DoT | Decay damage over time |
| 18 | Pain | Black | Direct | Direct damage |
| 19 | LifeTap | Black | Drain | Steal health |
| 20 | SummonGoblin | Black | Summon | Summon goblin |
| 21 | Hypnotize | Mental | CC | Mind control |
| 29 | SummonSkeleton | Black | Summon | Raise skeleton |
| 31 | SummonDemon | Black | Summon | Summon demon |
| 43 | HealingArea | White | AoE Heal | Area heal |
| 46 | CharmAnimal | Earth | CC | Tame animal |
| 52 | Strengthen | White | Buff | Strength buff |
| 56 | Regenerate | White | HoT | Health regen |
| 62 | Forget | Mental | Debuff | Memory loss |
| 67 | ManaTap | Mental | Drain | Steal mana |
| 73 | RainOfFire | Fire | AoE | Fire damage area |
| 74 | Blizzard | Ice | AoE | Ice storm area |
| 76 | StoneRain | Earth | AoE | Stone bombardment |
| 86 | Invisibility | Mental | Buff | Stealth |
| 106 | SummonWolf | Earth | Summon | Summon wolf |
| 109 | SummonBear | Earth | Summon | Summon bear |
| 122 | Charm | Mental | CC | Charm enemy |
| 133 | FireElemental | Fire | Summon | Fire elemental |
| 136 | IceElemental | Ice | Summon | Ice elemental |
| 141 | EarthElemental | Earth | Summon | Earth elemental |
| 211 | MirrorImage | Mental | Summon | Create illusions |

---

### Visual Effect Assets

**Billboards** (flics table):
- `flics.star6point` - 6-pointed star
- `flics.circle` - Simple circle
- `flics.circledark` - Dark circle (shadow)
- `flics.smoke` - Smoke texture
- `flics.fog` - Fog/mist texture
- `flics.solar` - Fireball texture
- `flics.ice` - Ice/frost texture
- `flics.bat` - Bat silhouette
- `flics.skull` - Skull icon
- `flics.ring` - Ring shape
- `flics.ring2` - Alternative ring
- `flics.diamond` - Diamond shape
- `flics.sparks` - Spark particles
- `flics.explo` - Explosion texture
- `flics.blurry` - Blurred circle

**Meshes** (flics table):
- `flics.cylinder_stripes` - Striped cylinder (god rays)
- `flics.cylinder` - Plain cylinder
- `flics.beampointy2` - Pointed beam
- `flics.hypno` - Hypnosis spiral
- `flics.iceshield[1-4]` - Ice shield variants
- `flics.icerocks[1-4]` - Ice rock models
- `flics.stones[1-4]` - Stone models
- `flics.fadeout` - Fade mesh
- `flics.runes` - Rune circle
- `flics.runessmall` - Small runes

**Special**:
- `flics.simplelightning` - Lightning texture
- `flics.lightning_chain` - Chain lightning

---

### Sound Event IDs

From `DrwSound.lua`:

**Cast Sounds**:
- `spell_white_cast`
- `spell_black_cast`
- `spell_fire_cast`
- `spell_ice_cast`
- `spell_earth_cast`
- `spell_mental_cast`
- `spell_elemental_cast`

**Resolve Sounds**:
- `spell_white_resolve`
- `spell_black_resolve`
- `spell_fire_resolve`
- `spell_ice_resolve`
- `spell_earth_resolve`
- `spell_mental_resolve`

**Hit Sounds**:
- `spell_fire_hit`
- `spell_ice_hit`
- `spell_black_hit`
- `spell_white_hit`
- `spell_mental_hit`

**Special Sounds**:
- `spell_summon`
- `spell_summon_worker`
- `spell_summon_hero`
- `spell_resist`
- `spell_dispel`
- `spell_buff`
- `spell_debuff`

---

## Best Practices

### Performance Optimization

1. **Limit Particle Counts**:
   ```lua
   -- BAD: Too many particles
   NewMovie(500)  -- Causes lag
   
   -- GOOD: Reasonable count
   NewMovie(22)   -- Smooth performance
   ```

2. **Use Clamp for Finite Effects**:
   ```lua
   Clamp{range=2}  -- Effect disappears after 2 seconds
   ```

3. **Avoid Infinite Loops**:
   ```lua
   -- BAD
   Rotation{range=999999, play=kDrwPlayContinous}
   
   -- GOOD
   FadeScale{fadein=0.5, fadeout=0.5}  -- Auto-cleanup
   ```

4. **Reuse Common Effects**:
   ```lua
   -- Define once
   local fireEffect = NewObject{billboard=flics.smoke, ...}
   
   -- Reuse multiple times
   local cast1 = NewObject{subobject=fireEffect, bone=kDrwBoneRightHand}
   local cast2 = NewObject{subobject=fireEffect, bone=kDrwBoneLeftHand}
   ```

---

### Visual Design Tips

1. **Match School Aesthetics**:
   - White: Bright, uplifting, golden/white
   - Black: Dark, ominous, red/black
   - Fire: Hot colors, orange/red/yellow
   - Ice: Cold colors, blue/cyan/white
   - Earth: Natural, brown/grey/green
   - Mental: Psychedelic, green/purple/yellow

2. **Layering**:
   ```lua
   -- Core glow
   local glow = NewObject{billboard=flics.circle, ...}
   
   -- Outer particles
   local particles = NewObject{billboard=flics.sparks, ...}
   
   -- Flash
   local flash = NewObject{billboard=flics.star6point, ...}
   
   -- Combine
   NewObject{subobject={glow, particles, flash}}
   ```

3. **Timing**:
   - Cast: 0.5-1.5 seconds
   - Projectile: Match game projectile speed
   - Resolve: 0.3-0.8 seconds (punchy impact)
   - Buffs: Subtle, persistent

4. **Scale Appropriately**:
   ```lua
   -- Small spell
   Scale{min=0.5}
   
   -- Medium spell
   Scale{min=1.5}
   
   -- Epic spell
   Scale{min=3}
   ```

---

## Troubleshooting

### Common Issues

#### **Effect doesn't appear**
- Check `EffectSave("EffectName")` is called
- Verify effect name matches spell definition
- Ensure particles > 0 in NewMovie()
- Check color alpha > 0

#### **Effect is too dark/invisible**
```lua
-- Check color values
Color{min={1,1,1,1}}  -- GOOD: Full opacity
Color{min={1,1,1,0}}  -- BAD: Transparent
```

#### **Effect doesn't attach to character**
```lua
-- Missing bone parameter
NewObject{billboard=flics.star6point}  -- Wrong

-- Correct
NewObject{billboard=flics.star6point, bone=kDrwBoneRightHand}
```

#### **Sound doesn't play**
- Verify sound file exists in `sound/` directory
- Check sound ID in DrwSound.lua
- Ensure Volume > 0
- Check FallOffMax > FallOffMin

---

## Conclusion

SpellForce's spell system demonstrates **professional game architecture** with:

- **Modular design**: Separate mechanics, visuals, and audio
- **Flexible particle system**: Powerful Lua-based effects
- **Rich magic diversity**: 5 schools, 240+ spells
- **Modding-friendly**: Easy to extend and customize

The system allows creators to build **compelling magical experiences** through thoughtful combination of:
- Visual particle effects
- Spatial audio
- Character animations
- Gameplay mechanics

With this guide, you can create custom spells that feel native to SpellForce's magical world.

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Author**: SpellForce Community Documentation Project
