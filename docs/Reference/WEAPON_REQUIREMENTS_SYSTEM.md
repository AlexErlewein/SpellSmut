# SpellForce Weapon Requirements System Reference

This document provides a comprehensive reference for the SpellForce weapon requirements system, including skills, stats, and implementation details for the weapon forge and editor tools.

## Overview

SpellForce uses a sophisticated skill-based weapon requirement system where weapons require specific skills at certain levels, along with stat requirements and minimum character levels. This system ensures that players must progress through skill trees to use advanced weapons.

## Skill System Structure

### Main Skill Categories
The skill system is organized into 7 main categories, each with specializations:

| Skill ID | Category | Description |
|----------|----------|-------------|
| 1 | LeichteKriegskunst (Light Combat Arts) | Light weapons and armor |
| 2 | SchwereKriegskunst (Heavy Combat Arts) | Heavy weapons and armor |
| 3 | Fernkampf (Ranged Combat) | Bows and crossbows |
| 4 | WeisseMagie (White Magic) | Life, nature, blessing magic |
| 5 | ElementarMagie (Elementary Magic) | Fire, ice, earth magic |
| 6 | MentalMagie (Mental Magic) | Enchantment, offensive, defensive magic |
| 7 | SchwarzeMagie (Black Magic) | Death, necromancy, curse magic |

## Weapon Skills Detail

### Light Combat Arts (Skill 1)
| Spec ID | Skill Name | German Name | Typical Weapons | Level Range |
|---------|------------|-------------|-----------------|-------------|
| 1 | Stichwaffen | Dagger Weapons | Daggers, short blades | 1-10 |
| 2 | KleineSchwerter | Small Swords | Short swords, scimitars | 1-10 |
| 3 | KleineSchlagwaffen | Small Blunt Weapons | Maces, clubs, small hammers | 1-10 |
| 4 | LeichteRuestungen | Light Armor | Leather, cloth armor | 1-10 |

### Heavy Combat Arts (Skill 2)
| Spec ID | Skill Name | German Name | Typical Weapons | Level Range |
|---------|------------|-------------|-----------------|-------------|
| 1 | GrosseSchwerter | Large Swords | Long swords, greatswords, claymores | 1-10 |
| 2 | GrosseSchlagwaffen | Large Blunt Weapons | War hammers, mauls, battle axes | 1-10 |
| 3 | SchwereRuestungen | Heavy Armor | Plate armor, chain mail | 1-10 |
| 4 | Schilde | Shields | All shield types | 1-10 |

### Ranged Combat (Skill 3)
| Spec ID | Skill Name | German Name | Typical Weapons | Level Range |
|---------|------------|-------------|-----------------|-------------|
| 1 | Bogen | Bow | Short bows, long bows, composite bows | 1-10 |
| 2 | Armbrust | Crossbow | Light crossbows, heavy crossbows | 1-10 |

## Magic Schools (Skills 4-7)

### White Magic (Skill 4)
| Spec ID | Skill Name | German Name | Focus |
|---------|------------|-------------|-------|
| 1 | Leben | Life | Healing, restoration magic |
| 2 | Natur | Nature | Nature-based spells, summoning |
| 3 | Segnung | Blessing | Buffs, protective magic |

### Elementary Magic (Skill 5)
| Spec ID | Skill Name | German Name | Focus |
|---------|------------|-------------|-------|
| 1 | Feuer | Fire | Fire damage, fire spells |
| 2 | Eis | Ice | Ice damage, ice spells |
| 3 | Erde | Earth | Earth damage, earth spells |

### Mental Magic (Skill 6)
| Spec ID | Skill Name | German Name | Focus |
|---------|------------|-------------|-------|
| 1 | Verzauberung | Enchantment | Charm, control spells |
| 2 | Offensiv | Offensive | Direct damage mental spells |
| 3 | Defensiv | Defensive | Mental protection spells |

### Black Magic (Skill 7)
| Spec ID | Skill Name | German Name | Focus |
|---------|------------|-------------|-------|
| 1 | Tod | Death | Death spells, life drain |
| 2 | Nekromantie | Necromancy | Undead, necromantic spells |
| 3 | Fluch | Curse | Curses, debuffs |

## Stat Requirements

### Base Stats
| Stat | German | Typical Usage | Common for Weapons |
|------|--------|---------------|-------------------|
| Str | Stärke | Physical power, melee damage | Heavy weapons, axes, hammers |
| Dex | Geschick | Precision, ranged damage | Bows, crossbows, daggers |
| Int | Intelligenz | Magical power, spell damage | Magic staffs, wands |
| Sta | Ausdauer | Health, fatigue resistance | Heavy armor, large weapons |
| Wis | Weisheit | Magic resistance, mana | Holy weapons, defensive items |
| Cha | Charisma | Leadership, prices | Commander weapons |

### Level Requirements
- **Minimum Character Level**: 1-30 (typical range)
- **Skill Level Requirement**: 1-10 (per skill)

## Weapon Categories and Typical Requirements

### One-Handed Weapons
| Type | Skill | Stat | Level Range | Examples |
|------|-------|------|-------------|----------|
| Dagger | Stichwaffen (1.1) | Dex | 1-5 | Basic daggers, poisoned blades |
| Short Sword | KleineSchwerter (1.2) | Str/Dex | 2-8 | Scimitars, short swords |
| Mace | KleineSchlagwaffen (1.3) | Str | 2-8 | Flanged maces, morning stars |
| Long Sword | GrosseSchwerter (2.1) | Str | 5-15 | Bastard swords, long swords |
| Battle Axe | GrosseSchlagwaffen (2.2) | Str | 6-18 | Battle axes, war axes |

### Two-Handed Weapons
| Type | Skill | Stat | Level Range | Examples |
|------|-------|------|-------------|----------|
| Greatsword | GrosseSchwerter (2.1) | Str | 10-20 | Claymores, greatswords |
| War Hammer | GrosseSchlagwaffen (2.2) | Str | 12-22 | Mauls, war hammers |
| Polearm | GrosseSchwerter (2.1) | Str | 15-25 | Halberds, pikes |

### Ranged Weapons
| Type | Skill | Stat | Level Range | Examples |
|------|-------|------|-------------|----------|
| Short Bow | Bogen (3.1) | Dex | 3-10 | Hunting bows, short bows |
| Long Bow | Bogen (3.1) | Dex | 8-18 | Long bows, composite bows |
| Light Crossbow | Armbrust (3.2) | Dex/Str | 5-12 | Light crossbows, repeating crossbows |
| Heavy Crossbow | Armbrust (3.2) | Str/Dex | 12-25 | Heavy crossbows, siege crossbows |

### Magic Weapons
| Type | Skill | Stat | Level Range | Examples |
|------|-------|------|-------------|----------|
| Magic Staff | Any Magic | Int | 5-20 | Fire staff, ice staff |
| Wand | Any Magic | Int | 3-12 | Wand of fire, wand of healing |
| Holy Weapon | WeisseMagie (4.x) | Wis/Str | 10-25 | Holy avenger, blessed sword |

## Implementation in LUA

### Skill Requirement Syntax
```lua
-- Basic skill requirement
AvatarSkill{Skill = Armbrust, Level = 5}

-- With update interval for performance
AvatarSkill{Skill = Bogen, Level = 3, UpdateInterval = 60}

-- Magic skill requirement
AvatarSkill{Skill = Feuer, Level = 7}
```

### Combined Requirements
```lua
-- Multiple requirements using UND (AND)
UND{
    AvatarSkill{Skill = Armbrust, Level = 5},
    AvatarLevel{Level = 10},
    AvatarStat{Stat = Dex, Value = 30}
}
```

## Data Structure for Weapon Editor

### WeaponRequirements Class
```python
@dataclass
class WeaponRequirements:
    strength: int = 0
    dexterity: int = 0
    intelligence: int = 0
    level: int = 1
    school_requirements: List[SchoolRequirement] = field(default_factory=list)

@dataclass
class SchoolRequirement:
    school_name: str  # "Armbrust", "GrosseSchwerter", "Feuer", etc.
    level: int = 1
```

### Skill Mapping
```python
SKILL_MAPPING = {
    # Combat Skills
    "Stichwaffen": {"skill_id": 1, "spec_id": 1, "name": "Dagger Weapons"},
    "KleineSchwerter": {"skill_id": 1, "spec_id": 2, "name": "Small Swords"},
    "KleineSchlagwaffen": {"skill_id": 1, "spec_id": 3, "name": "Small Blunt"},
    "GrosseSchwerter": {"skill_id": 2, "spec_id": 1, "name": "Large Swords"},
    "GrosseSchlagwaffen": {"skill_id": 2, "spec_id": 2, "name": "Large Blunt"},
    "Schilde": {"skill_id": 2, "spec_id": 4, "name": "Shields"},
    "Bogen": {"skill_id": 3, "spec_id": 1, "name": "Bow"},
    "Armbrust": {"skill_id": 3, "spec_id": 2, "name": "Crossbow"},
    
    # Magic Schools
    "Leben": {"skill_id": 4, "spec_id": 1, "name": "Life"},
    "Natur": {"skill_id": 4, "spec_id": 2, "name": "Nature"},
    "Segnung": {"skill_id": 4, "spec_id": 3, "name": "Blessing"},
    "Feuer": {"skill_id": 5, "spec_id": 1, "name": "Fire"},
    "Eis": {"skill_id": 5, "spec_id": 2, "name": "Ice"},
    "Erde": {"skill_id": 5, "spec_id": 3, "name": "Earth"},
    "Verzauberung": {"skill_id": 6, "spec_id": 1, "name": "Enchantment"},
    "Offensiv": {"skill_id": 6, "spec_id": 2, "name": "Offensive"},
    "Defensiv": {"skill_id": 6, "spec_id": 3, "name": "Defensive"},
    "Tod": {"skill_id": 7, "spec_id": 1, "name": "Death"},
    "Nekromantie": {"skill_id": 7, "spec_id": 2, "name": "Necromancy"},
    "Fluch": {"skill_id": 7, "spec_id": 3, "name": "Curse"},
}
```

## Example Weapon Configurations

### Basic Crossbow
```python
requirements = WeaponRequirements(
    dexterity=25,
    level=8,
    school_requirements=[
        SchoolRequirement(school_name="Armbrust", level=3)
    ]
)
```

### Greatsword of Fire
```python
requirements = WeaponRequirements(
    strength=35,
    level=15,
    school_requirements=[
        SchoolRequirement(school_name="GrosseSchwerter", level=7),
        SchoolRequirement(school_name="Feuer", level=5)
    ]
)
```

### Holy Avenger
```python
requirements = WeaponRequirements(
    strength=30,
    wisdom=25,
    level=20,
    school_requirements=[
        SchoolRequirement(school_name="GrosseSchwerter", level=8),
        SchoolRequirement(school_name="Leben", level=6),
        SchoolRequirement(school_name="Segnung", level=4)
    ]
)
```

## File Locations

### LUA Source Files
- **Skill Definitions**: `ModdingTools/SpellForceLUASources/script/GdsDefines.lua`
- **Skill Conditions**: `ModdingTools/SpellForceLUASources/script/GdsConditions.lua`
- **Item Data**: `ModdingTools/SpellForceLUASources/script/sql_item.lua`

### CFF Data Tables
- `item_requirements` - Individual item requirements
- `skill_requirements` - Skill-based requirements
- `weapons` - Weapon base data
- `items` - General item data

### Python Implementation
- **Weapon Data Model**: `src/TirganachReloaded/cff_editor/models/weapon_creation_data.py`
- **Weapon Loader**: `src/TirganachReloaded/cff_editor/exporters/weapon_loader.py`

## Integration Notes

1. **UI Updates**: Weapon forge should display skill requirements prominently
2. **Validation**: Prevent creation of weapons with impossible requirement combinations
3. **Auto-suggestion**: Suggest appropriate requirements based on weapon type
4. **Level Scaling**: Automatically scale requirements with weapon power level
5. **Cross-skill Requirements**: Some weapons may require multiple skills (e.g., magic + combat)

## Future Enhancements

1. **Requirement Templates**: Pre-defined templates for common weapon types
2. **Skill Tree Visualization**: Show skill progression paths
3. **Requirement Validation**: Check if requirements are achievable within game constraints
4. **Export to LUA**: Generate LUA condition code for created weapons
5. **Integration with Quest System**: Link weapon requirements to quest rewards

## Armor Requirements

- **Light Armor**: LeichteRuestungen (1.4) — typically low Str/Dex thresholds, early levels.
- **Heavy Armor**: SchwereRuestungen (2.3) — higher Str/Sta thresholds, mid-to-late levels.
- **Shields**: Schilde (2.4) — often paired with Heavy Combat; might have minimum Str or Level.

Example armor requirement representation:

```json
{
  "requirements": {
    "level": 12,
    "school_requirements": [
      { "requirement_school": "SchwereRuestungen", "level": 5 }
    ]
  }
}
```

## CFF Requirements Schema

The core requirement records are stored in `item_requirements` (and in some builds also `skill_requirements`). Typical fields:

- `item_id`: The item the requirement applies to (weapon or armor).
- `requirement_number`: Sequential index of the requirement for the item.
- `requirement_school`: Skill school/specialization (e.g., Armbrust, GrosseSchwerter, LeichteRuestungen).
- `level`: Required level in that school.

Notes:

- Numeric stats (strength/dexterity/intelligence) are not always present in CFF; many items rely solely on school and level requirements.
- The UI should therefore always display school requirements when available and fall back to stats/level when schools are absent.

## Display Guidelines (UI)

- Show base stats (Str/Dex/Int) and minimum character Level.
- If `school_requirements` exist, render a “School Requirements” list:
  - Format: `<School Name> — Level <N>`
  - Clean names by removing enum prefixes and replacing underscores with spaces (title-case).
- Prefer localized or human-friendly names when available.

## UI Integration Status

- **Enhanced Weapon Browser**: Displays School Requirements in the right-side "REQUIREMENTS" panel when available.
- **Weapon Forge Wizard**: Review & Export step lists School Requirements alongside stat/level requirements.
- **OrthancsSchmiede Item Details**: Weapon and armor detail views render school requirements (cleaned display names).

## CFF Path Discovery

Tools search for `GameData.cff` in the following locations:

- **Preferred (works for both app and browser)**:
  - `forge/OriginalGameFiles/data/GameData.cff`
- **Wizard/Test harness additional attempts**:
  - `forge/src/OriginalGameFiles/data/GameData.cff`
  - `forge/src/OriginalGameFiles/GameData.cff`
  - System install fallback (example on macOS): `/Users/<you>/SpellForce Platinum Edition/data/GameData.cff`

Recommendation: Place a copy at `forge/OriginalGameFiles/data/GameData.cff` so all tools find it without falling back to JSON.

## Name Normalization

When displaying school requirements, names are normalized for readability:

- Strip enum/class prefixes (e.g., `EquipmentType.HEAVY_ARMOR` → `HEAVY_ARMOR`).
- Replace underscores with spaces.
- Title-case the result (e.g., `Heavy Armor`).

This normalization is applied consistently across browser details, wizard review, and OrthancsSchmiede detail panels.

## Current Limitations

- Exporting `item_requirements` to CFF is planned but not yet implemented in `WeaponCFFExporter`.
- No automatic validation/auto-suggestion of requirements yet (future enhancement).
