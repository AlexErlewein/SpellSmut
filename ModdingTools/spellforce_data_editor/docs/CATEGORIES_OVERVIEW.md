# SpellForce GameData Categories - Complete Overview

**Generated:** 2025-10-18
**Total Categories:** 50

This document provides a comprehensive overview of all data categories in the SpellForce GameData.cff file.

---

## Quick Reference

### Items & Equipment (2003-2018)
- **2003** - Item general info (ID, name, type, value)
- **2004** - Item armor/stats data
- **2012** - Item UI data (icons, handles)
- **2013** - Spell scroll → installed scroll link
- **2014** - Item weapon effects (multi-valued)
- **2015** - Item weapon data (damage, speed, type, material)
- **2017** - Item skill requirements
- **2018** - Installed spell scroll → spell link

### Spells & Effects (2002, 2054-2056)
- **2002** - Spell data (core spell mechanics)
- **2054** - Spell lines (spell progression)
- **2056** - Spell requirements

### Units & Heroes (2005, 2006, 2024-2026, 2067)
- **2005** - Unit/hero stats (attributes, resistances)
- **2006** - Hero/worker skills
- **2024** - Unit general data (experience, loot, handle)
- **2025** - Unit equipment (multi-valued)
- **2026** - Unit spells (multi-valued)
- **2067** - Unit AI / Behavior

### Buildings (2001, 2029-2032)
- **2001** - Army unit building requirements
- **2029** - Building data
- **2030** - Building collision data (polygons)
- **2031** - Building resource requirements
- **2032** - Building upgrade data

### Races & Factions (2022, 2023)
- **2022** - Race stats
- **2023** - Faction relations

### Merchants & Objects (2040-2053)
- **2040** - Unknown (Interactive objects?)
- **2041** - Merchants
- **2042** - Merchant inventory
- **2044-2053** - Various object types

### Weapons & Materials (2063, 2064)
- **2063** - Weapon types (lookup table)
- **2064** - Weapon materials (lookup table)

### Skills (2039)
- **2039** - Skills

### Text & Localization (2016)
- **2016** - Text data (multilingual, multi-valued)

### Miscellaneous (20 28, 2036, 2057-2062, 2065, 2072)
- **2028** - Army unit resource requirements
- **2036** - Unknown
- **2057-2062** - Various game data
- **2065** - Unknown
- **2072** - Unknown

---

## Detailed Category Information

### ITEMS & EQUIPMENT SYSTEM

#### Category 2003: Item General Info
**Type:** CategoryBaseSingle
**Purpose:** Core item metadata - ALL items in the game

**Fields:**
- `ItemID` (ushort) - Primary key
- `ItemType1` (byte) - Item type classification (weapon, armor, etc.)
- `ItemType2` (byte) - Item subtype
- `NameID` (ushort) → **Category 2016** (Text)
- `UnitStatsID` (ushort) → **Category 2005** (Hero runes reference)
- `ArmyUnitID` (ushort) - Related army unit
- `BuildingID` (ushort) → **Category 2029** (Building reference)
- `Option` (byte) - Unknown flags
- `SellValue` (uint) - Copper value when selling
- `BuyValue` (uint) - Copper cost when buying
- `ItemSetID` (byte) - Item set membership

**Relationships:**
- References **2016** for item name
- References **2005** for hero/worker runes
- May reference **2029** for building-related items
- Extended by **2004** (stats), **2012** (UI), **2014** (effects), **2015** (weapon data), **2017** (requirements)

---

#### Category 2004: Item Armor Data
**Type:** CategoryBaseSingle
**Purpose:** Stat bonuses provided by items (primarily armor/accessories)

**Fields:**
- `ItemID` (ushort) - Foreign key → **Category 2003**
- `Strength` (short) - Strength bonus
- `Stamina` (short) - Stamina bonus
- `Agility` (short) - Agility bonus
- `Dexterity` (short) - Dexterity bonus
- `Health` (short) - HP bonus
- `Charisma` (short) - Charisma bonus
- `Intelligence` (short) - Intelligence bonus
- `Wisdom` (short) - Wisdom bonus
- `Mana` (short) - Mana bonus
- `Armor` (short) - Armor bonus
- `ResistFire` (short) - Fire resistance
- `ResistIce` (short) - Ice resistance
- `ResistBlack` (short) - Black magic resistance
- `ResistMind` (short) - Mind magic resistance
- `SpeedWalk` (short) - Walk speed modifier
- `SpeedFight` (short) - Attack speed modifier
- `SpeedCast` (short) - Cast speed modifier

**Relationships:**
- One-to-one with **Category 2003** (not all items have stats)

---

#### Category 2012: Item UI Data
**Type:** CategoryBaseMultiple
**Purpose:** UI representation of items (icons, display settings)

**Fields:**
- `ItemID` (ushort) - Foreign key → **Category 2003**
- `UIIndex` (byte) - Sub-item index (multiple UI representations possible)
- `UIHandle[64]` (byte array) - Icon/texture handle name
- `IsScaledDown` (ushort) - Scaling flag

**Relationships:**
- One-to-many with **Category 2003** (items can have multiple UI representations)

---

#### Category 2013: Inventory Spell Scroll Link
**Type:** CategoryBaseSingle
**Purpose:** Links inventory spell scrolls to their installed versions

**Fields:**
- `ItemID` (ushort) - Inventory scroll item ID → **Category 2003**
- `InstalledScrollItemID` (ushort) - Installed scroll item ID → **Category 2003**

**Relationships:**
- One-to-one with **Category 2003**

---

#### Category 2014: Item Weapon Effects
**Type:** CategoryBaseMultiple
**Purpose:** Spell effects triggered by weapons/items

**Fields:**
- `ItemID` (ushort) - Foreign key → **Category 2003**
- `EffectIndex` (byte) - Sub-item index
- `EffectID` (ushort) → **Category 2002** (Spell/Effect)

**Relationships:**
- One-to-many with **Category 2003** (weapons can have multiple effects)
- References **Category 2002** for effect details

---

#### Category 2015: Item Weapon Data ⚔️
**Type:** CategoryBaseSingle
**Purpose:** **CORE WEAPON COMBAT STATS**

**Fields:**
- `ItemID` (ushort) - Foreign key → **Category 2003**
- `MinDamage` (ushort) - Minimum damage
- `MaxDamage` (ushort) - Maximum damage
- `MinRange` (ushort) - Minimum attack range
- `MaxRange` (ushort) - Maximum attack range
- `WeaponSpeed` (ushort) - Attack speed
- `WeaponType` (ushort) → **Category 2063** (Weapon type lookup)
- `WeaponMaterial` (ushort) → **Category 2064** (Material lookup)

**Relationships:**
- One-to-one with **Category 2003** (only weapon items have this data)
- References **Category 2063** for weapon type name/properties
- References **Category 2064** for material name/properties

**Note:** This category defines which items in 2003 are weapons!

---

#### Category 2017: Item Skill Requirements
**Type:** CategoryBaseMultiple
**Purpose:** Skills required to equip/use items

**Fields:**
- `ItemID` (ushort) - Foreign key → **Category 2003**
- `ReqIndex` (byte) - Sub-item index
- `SkillMajorID` (byte) - Major skill category
- `SkillMinorID` (byte) - Minor skill category
- `SkillLevel` (byte) - Required skill level

**Relationships:**
- One-to-many with **Category 2003** (items can have multiple skill requirements)
- References **Category 2039** for skill details

---

#### Category 2018: Installed Spell Scroll → Spell Link
**Type:** CategoryBaseSingle
**Purpose:** Links installed spell scroll items to actual spell effects

**Fields:**
- `SpellItemID` (ushort) - Installed scroll item ID → **Category 2003**
- `EffectID` (ushort) → **Category 2002** (Spell effect)

**Relationships:**
- One-to-one with **Category 2003**
- References **Category 2002** for spell effect

---

### SPELLS & EFFECTS SYSTEM

#### Category 2002: Spell Data 🔮
**Type:** CategoryBaseSingle
**Purpose:** **CORE SPELL MECHANICS** - all spells and effects

**Fields:**
- `SpellID` (ushort) - Primary key
- `SpellLineID` (ushort) → **Category 2054** (Spell line)
- `SkillReq[12]` (byte array) - Skill requirements (magic schools, levels)
- `ManaCost` (ushort) - Mana required to cast
- `CastTime` (uint) - Cast time in milliseconds
- `RecastTime` (uint) - Cooldown in milliseconds
- `MinRange` (ushort) - Minimum casting range
- `MaxRange` (ushort) - Maximum casting range
- `CastType1` (byte) - Targeting type
- `CastType2` (byte) - Casting behavior
- `Params[10]` (uint array) - Spell parameters (damage, duration, radius, etc.)
- `EffectPower` (ushort) - Base spell power
- `EffectRange` (ushort) - Effect radius

**Relationships:**
- References **Category 2054** for spell line (leveling)
- Referenced by **Category 2014** (weapon effects)
- Referenced by **Category 2018** (spell scrolls)
- Referenced by **Category 2026** (unit spells)

**Special Methods:**
- `GetSpellLevel()` - Returns spell level from SkillReq[2]
- Parameter interpretation varies by spell type (see `SFSpellDescriptor` in `SFCategoryManager.cs`)

---

#### Category 2054: Spell Lines
**Type:** CategoryBaseSingle
**Purpose:** Spell progression/leveling system

**Fields:**
- `SpellLineID` (ushort) - Primary key
- `TextID` (ushort) → **Category 2016** (Spell name)
- *(Additional fields - need to verify)*

**Relationships:**
- Referenced by **Category 2002** (spell data)
- References **Category 2016** for spell name

---

#### Category 2056: Spell Requirements
**Type:** CategoryBase*
**Purpose:** Requirements to learn spells

**Fields:**
- *(Need to verify structure)*

---

### UNITS & HEROES SYSTEM

#### Category 2024: Unit General Data
**Type:** CategoryBaseSingle
**Purpose:** Core unit metadata

**Fields:**
- `UnitID` (ushort) - Primary key
- `NameID` (ushort) → **Category 2016** (Unit name)
- `StatsID` (ushort) → **Category 2005** (Stats reference)
- `ExperienceGain` (uint) - XP gained when killed
- `ExperienceFalloff` (ushort) - XP reduction over level
- `CopperLoot` (uint) - Copper dropped
- `CopperVariance` (ushort) - Loot randomization
- `Rangedness` (byte) - Melee/ranged classification
- `MeatValue` (ushort) - Meat dropped
- `Armor` (ushort) - Base armor
- `Handle[40]` (byte array) - 3D model handle
- `CanBePlaced` (byte) - Map editor flag

**Relationships:**
- References **Category 2016** for unit name
- References **Category 2005** for detailed stats
- Extended by **Category 2025** (equipment), **Category 2026** (spells)

---

#### Category 2005: Unit/Hero Stats
**Type:** CategoryBaseSingle
**Purpose:** **CORE UNIT ATTRIBUTES** - stats for all units and heroes

**Fields:**
- `StatsID` (ushort) - Primary key
- `UnitLevel` (ushort) - Unit level
- `UnitRace` (byte) → **Category 2022** (Race)
- `Agility` (ushort) - Agility attribute
- `Dexterity` (ushort) - Dexterity attribute
- `Charisma` (ushort) - Charisma attribute
- `Intelligence` (ushort) - Intelligence attribute
- `Stamina` (ushort) - Stamina attribute (HP scaling)
- `Strength` (ushort) - Strength attribute (damage scaling)
- `Wisdom` (ushort) - Wisdom attribute (mana scaling)
- `RandomInit` (ushort) - Initiative randomization
- `ResistanceFire` (ushort) - Fire resistance
- `ResistanceIce` (ushort) - Ice resistance
- `ResistanceBlack` (ushort) - Black magic resistance
- `ResistanceMind` (ushort) - Mind magic resistance
- `SpeedWalk` (ushort) - Walk speed
- `SpeedFight` (ushort) - Attack speed
- `SpeedCast` (ushort) - Cast speed
- `UnitSize` (ushort) - Collision size
- `ManaUsage` (ushort) - Mana consumption
- `SpawnBaseTime` (uint) - Base spawn time
- `UnitFlags` (byte) - Unit behavior flags
- `HeadID` (ushort) - Head model ID
- `EquipmentMode` (byte) - Equipment rendering mode

**Relationships:**
- Referenced by **Category 2024** (units)
- Referenced by **Category 2003** (hero rune items)
- References **Category 2022** for race properties

---

#### Category 2006: Hero/Worker Skills
**Type:** CategoryBaseMultiple
**Purpose:** Skills possessed by units/heroes

**Fields:**
- `UnitStatsID` (ushort) - Foreign key → **Category 2005**
- `SkillMajorID` (byte) - Major skill category (sub-ID)
- `SkillMinorID` (byte) - Minor skill category
- `SkillLevel` (byte) - Skill level

**Relationships:**
- One-to-many with **Category 2005**
- References **Category 2039** for skill details

---

#### Category 2025: Unit Equipment
**Type:** CategoryBaseMultiple
**Purpose:** Starting equipment for units

**Fields:**
- `UnitID` (ushort) - Foreign key → **Category 2024**
- `EquipmentIndex` (byte) - Equipment slot (sub-ID)
- `ItemID` (ushort) → **Category 2003** (Item)

**Relationships:**
- One-to-many with **Category 2024**
- References **Category 2003** for item details

---

#### Category 2026: Unit Spells
**Type:** CategoryBaseMultiple
**Purpose:** Spells/abilities known by units

**Fields:**
- `UnitID` (ushort) - Foreign key → **Category 2024**
- `SpellIndex` (byte) - Spell slot (sub-ID)
- `SpellID` (ushort) → **Category 2002** (Spell)

**Relationships:**
- One-to-many with **Category 2024**
- References **Category 2002** for spell details

---

#### Category 2067: Unit AI/Behavior
**Type:** CategoryBase*
**Purpose:** AI behavior parameters

**Fields:**
- *(Need to verify structure)*

---

### BUILDINGS SYSTEM

#### Category 2029: Building Data
**Type:** CategoryBaseSingle
**Purpose:** Core building metadata

**Fields:**
- `BuildingID` (ushort) - Primary key
- `RaceID` (byte) → **Category 2022** (Race)
- `CanEnter` (byte) - Enterable flag
- `Slots` (byte) - Number of unit slots
- `Health` (ushort) - Building HP
- `NameID` (ushort) → **Category 2016** (Name)
- `RotCenterX` (short) - Rotation center X
- `RotCenterY` (short) - Rotation center Y
- `NumOfPolygons` (byte) - Collision polygon count
- `WorkerCycleTime` (ushort) - Production cycle time
- `BuildingReqID` (ushort) - Building requirement ID
- `InitialAngle` (ushort) - Default rotation
- `DescriptionExtID` (ushort) → **Category 2016** (Description)
- `Flags` (byte) - Building flags

**Relationships:**
- References **Category 2022** for race
- References **Category 2016** for name and description
- Extended by **Category 2030** (collision), **Category 2031** (costs)

---

#### Category 2030: Building Collision Data
**Type:** Custom ICategory Implementation
**Purpose:** Collision polygons for buildings

**Fields:**
- `BuildingID` (ushort) - Foreign key → **Category 2029**
- `PolygonID` (byte) - Polygon index (sub-ID)
- `CastsShadow` (byte) - Shadow casting flag
- `Coords` (List<short>) - **VARIABLE LENGTH** polygon vertices (X, Y pairs)

**Relationships:**
- One-to-many with **Category 2029**

**Special:** This category has a custom implementation (not CategoryBase) due to variable-length coordinate arrays!

---

#### Category 2031: Building Resource Requirements
**Type:** CategoryBaseMultiple
**Purpose:** Resources required to build buildings

**Fields:**
- `BuildingID` (ushort) - Foreign key → **Category 2029**
- `ResourceID` (byte) - Resource type (sub-ID)
- `ResourceRequirement` (ushort) - Amount required

**Relationships:**
- One-to-many with **Category 2029**

---

#### Category 2032: Building Upgrade Data
**Type:** CategoryBase*
**Purpose:** Building upgrade chains

**Fields:**
- *(Need to verify structure)*

---

#### Category 2001: Army Unit Building Requirements
**Type:** CategoryBaseMultiple
**Purpose:** Buildings required to train army units

**Fields:**
- `ArmyUnitID` (ushort) - Army unit ID (primary ID)
- `BuildingIndex` (byte) - Building slot (sub-ID)
- `BuildingID` (ushort) → **Category 2029** (Building)

**Relationships:**
- References **Category 2029** for building requirements

---

#### Category 2028: Army Unit Resource Requirements
**Type:** CategoryBaseMultiple
**Purpose:** Resources required to train army units

**Fields:**
- `ArmyUnitID` (ushort) - Army unit ID (primary ID)
- `ResourceType` (byte) - Resource type (sub-ID)
- `ResourceValue` (byte) - Amount required

**Relationships:**
- Parallel to **Category 2001** (same army unit IDs)

---

### RACES & FACTIONS

#### Category 2022: Race Stats
**Type:** CategoryBaseSingle
**Purpose:** Race properties and behaviors

**Fields:**
- `RaceID` (byte) - Primary key
- `VisRangeDay` (byte) - Vision range during day
- `VisRangeNight` (byte) - Vision range at night
- `HearRange` (byte) - Sound detection range
- `AggroRangeFactor` (byte) - Aggression range modifier
- `Moral` (byte) - Base morale
- `Aggresiveness` (byte) - Aggression level
- `TextID` (ushort) → **Category 2016** (Race name)
- `Flags` (byte) - Race flags
- `FactionID` (ushort) - Faction affiliation
- `DmgTakenBlunt` (byte) - Blunt damage modifier
- `DmgTakenSlash` (byte) - Slash damage modifier
- `AIFlags` (ushort) - AI behavior flags
- `GroupSizeMin` (byte) - Min group size
- `GroupSizeMax` (byte) - Max group size
- `GroupChance` (byte) - Group spawn chance
- `GroupFormation` (byte) - Formation type
- `Flee` (ushort) - Flee threshold
- `RetreatOnDmg` (ushort) - Retreat damage threshold
- `RetreatFollow` (ushort) - Retreat pursuit distance
- `AttackSpeedFactor` (byte) - Attack speed modifier

**Relationships:**
- References **Category 2016** for race name
- Referenced by **Category 2005** (unit stats)
- Referenced by **Category 2029** (buildings)

---

#### Category 2023: Faction Relations
**Type:** CategoryBaseMultiple
**Purpose:** Diplomatic relations between factions

**Fields:**
- `ClanID` (byte) - Faction 1 (primary ID)
- `ClanID2` (byte) - Faction 2 (sub-ID)
- `Relation` (byte) - Relationship value (hostile, neutral, friendly)

**Relationships:**
- Symmetric matrix of faction relationships

---

### MERCHANTS & OBJECTS

#### Category 2041: Merchants
**Type:** CategoryBase*
**Purpose:** Merchant NPC definitions

**Fields:**
- *(Need to verify structure)*

---

#### Category 2042: Merchant Inventory
**Type:** CategoryBase*
**Purpose:** Items sold by merchants

**Fields:**
- *(Need to verify structure)*

---

### WEAPON LOOKUPS

#### Category 2063: Weapon Types
**Type:** CategoryBaseSingle
**Purpose:** **WEAPON TYPE LOOKUP TABLE** (1H Sword, 2H Axe, Bow, etc.)

**Fields:**
- `WeaponTypeID` (ushort) - Primary key
- `NameID` (ushort) → **Category 2016** (Type name)
- `Sharpness` (byte) - Damage type classification

**Relationships:**
- Referenced by **Category 2015** (weapon data)
- References **Category 2016** for type name

---

#### Category 2064: Weapon Materials
**Type:** CategoryBaseSingle
**Purpose:** **WEAPON MATERIAL LOOKUP TABLE** (Iron, Steel, Adamantium, etc.)

**Fields:**
- `WeaponMaterialID` (ushort) - Primary key
- `NameID` (ushort) → **Category 2016** (Material name)

**Relationships:**
- Referenced by **Category 2015** (weapon data)
- References **Category 2016** for material name

---

### SKILLS

#### Category 2039: Skills
**Type:** CategoryBase*
**Purpose:** Skill definitions

**Fields:**
- *(Need to verify - likely has SkillMajorID, SkillMinorID, TextID)*

**Relationships:**
- Referenced by **Category 2006** (unit skills)
- Referenced by **Category 2017** (item requirements)
- References **Category 2016** for skill names

---

### TEXT & LOCALIZATION

#### Category 2016: Text Data 📝
**Type:** CategoryBaseMultiple
**Purpose:** **MULTILINGUAL TEXT DATABASE** - all in-game text

**Fields:**
- `TextID` (ushort) - Text identifier (primary ID)
- `LanguageID` (byte) - Language code (sub-ID)
  - `0` = English
  - `5` = Russian (uses Windows-1251 encoding)
  - `6` = Polish (uses Windows-1250 encoding)
  - Others use Windows-1252 encoding
- `Mode` (byte) - Text mode/format
- `Handle[50]` (byte array) - Text handle/identifier
- `Content[512]` (byte array) - Actual text content (max 512 bytes)

**Special Methods:**
- `GetContentString()` - Returns decoded text content (handles encoding)
- `GetHandleString()` - Returns handle string

**Relationships:**
- Referenced by virtually every other category for names, descriptions, and text

**Note:** This is the most widely referenced category - it's the central text database!

---

## Category Type Classification

### CategoryBaseSingle (One item per ID)
Standard single-value categories - each ID has exactly one entry.

Categories: 2002, 2003, 2004, 2005, 2013, 2015, 2018, 2022, 2024, 2029, 2063, 2064, and others

### CategoryBaseMultiple (Multiple items per ID)
Multi-valued categories - each ID can have multiple sub-items.

Categories: 2001, 2006, 2012, 2014, 2016, 2017, 2023, 2025, 2026, 2028, 2031, and others

### Custom ICategory Implementation
Special categories with unique structure.

- **Category 2030** - Building collision (variable-length polygon coordinates)

---

## Data Flow Examples

### Creating a Complete Weapon
To create a functional weapon item, you need entries in:
1. **Category 2003** - Item general info (base item)
2. **Category 2015** - Weapon combat data (damage, speed, type, material)
3. **Category 2063** - Weapon type entry (if new type)
4. **Category 2064** - Weapon material entry (if new material)
5. **Category 2016** - Text entries for:
   - Item name
   - Weapon type name (if new)
   - Material name (if new)
6. *Optional:*
   - **Category 2004** - Stat bonuses
   - **Category 2012** - UI icon/handle
   - **Category 2014** - Special effects
   - **Category 2017** - Skill requirements

### Creating a Unit with Equipment
1. **Category 2024** - Unit general data
2. **Category 2005** - Unit stats
3. **Category 2025** - Unit equipment (multiple entries)
4. **Category 2026** - Unit spells (multiple entries)
5. **Category 2016** - Unit name text
6. Items from **Category 2003** must exist for equipment

---

## Import/Export Considerations

### Foreign Key Integrity
When importing/exporting data, these relationships must be maintained:
- All NameID/TextID references must exist in **Category 2016**
- Weapon items in **Category 2015** must exist in **Category 2003**
- Unit StatsID in **Category 2024** must exist in **Category 2005**
- etc.

### Multi-valued Categories
Categories like 2014, 2025, 2026 allow multiple sub-items per ID:
- Must preserve sub-item indices
- Must handle variable numbers of sub-items
- JSON arrays work well for this

### Variable-Length Data
**Category 2030** has variable-length polygon coordinates:
- Cannot use fixed struct size
- Requires special serialization handling

---

## Unknown/Unverified Categories

The following categories need further investigation:
- **2036, 2040, 2044-2053, 2057-2062, 2065, 2067, 2072**

These likely contain additional game data (quests, dialogs, AI, etc.).

---

**Next Steps:**
1. Verify unknown category structures
2. Create individual detailed MD files for each category
3. Build relationship diagram
4. Implement export/import functionality
