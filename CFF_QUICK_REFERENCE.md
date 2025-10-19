# GameData.cff Quick Reference Card

## Loading & Saving

```python
from tirganach import GameData
from tirganach.types import *

# Load
gd = GameData('path/to/GameData.cff')

# Save
gd.save('path/to/GameData_modified.cff')
```

---

## Query Patterns

```python
# By exact field match
items = gd.items.where(item_id=7065)
spells = gd.spells.where(level=20, req1_class=School.FIRE)

# By filter (list comprehension)
rings = [item for item in gd.items
         if item.item_type == ItemType.EQUIPMENT
         and item.item_subtype == EquipmentType.RING]

# Get all entries
all_spells = gd.spells
all_items = gd.items
```

---

## Common Tables

| Table | What It Contains |
|-------|------------------|
| `gd.spells` | All spells |
| `gd.items` | All items (base data) |
| `gd.armor` | Armor stats (health/mana/etc.) |
| `gd.weapons` | Weapon stats (damage/etc.) |
| `gd.creatures` | All units/monsters |
| `gd.creature_stats` | Unit stat blocks |
| `gd.buildings` | All buildings |
| `gd.localisation` | All text strings |
| `gd.hero_spells` | Hero spell lists |
| `gd.skills` | Skill definitions |

---

## Common Item Modifications

```python
# Find ring by ID
ring = gd.armor.where(item_id=7065)[0]

# Modify stats
ring.health = 500
ring.mana = 500
ring.stamina = 300
ring.strength = 50
ring.intelligence = 50
ring.wisdom = 50
ring.dexterity = 50
ring.agility = 50

# Rename
ring.item.name = "New Name"
```

---

## Common Spell Modifications

```python
# Find spell
spell = gd.spells.where(spell_id=100)[0]

# Modify
spell.mana_cost = 50
spell.level = 25
spell.range = 100
```

---

## Common Unit Modifications

```python
# Find hero rune
hero = gd.items.where(item_id=4425)[0]

# Modify stats
hero.unit_stats.strength = 150
hero.unit_stats.dexterity = 150
hero.unit_stats.intelligence = 150

# Modify skills
hero.unit_stats.skills[0].set(
    skill_school=School.LIGHT_COMBAT,
    skill_level=20
)

# Modify spells
hero.unit_stats.hero_spells[0].set(spell_id=123)
```

---

## ItemType Values

```python
ItemType.EQUIPMENT              # Armor, weapons, rings
ItemType.RUNE_INVENTORY         # Worker/warrior runes
ItemType.RUNE_ADDED            # Added to monument
ItemType.SCROLL                # Spell scrolls
ItemType.SPELL                 # Spell items
ItemType.UNIT_PLAN_INVENTORY   # Unit plans
ItemType.BUILDING_PLAN_INVENTORY  # Building plans
ItemType.QUEST_ITEM            # Quest items
```

---

## EquipmentType Values

```python
EquipmentType.HELMET
EquipmentType.UPPER           # Chest
EquipmentType.LOWER           # Legs
EquipmentType.RING
EquipmentType.ONEHANDED_WEAPON
EquipmentType.TWOHANDED_WEAPON
EquipmentType.SHIELD
EquipmentType.BOW
EquipmentType.FULL_BODY
```

---

## Magic School Values

```python
# Combat
School.LIGHT_COMBAT
School.HEAVY_COMBAT
School.RANGED_COMBAT

# Weapons
School.LIGHT_BLADE_WEAPONS
School.HEAVY_BLADE_WEAPONS
School.BOWS
School.CROSSBOWS

# White Magic
School.WHITE_MAGIC
School.LIFE
School.NATURE
School.BOONS

# Elemental
School.ELEMENTAL_MAGIC
School.FIRE
School.ICE
School.EARTH

# Mental
School.MIND_MAGIC
School.ENCHANTMENT
School.OFFENSIVE
School.DEFENSIVE

# Black Magic
School.BLACK_MAGIC
School.DEATH
School.NECROMANCY
School.CURSE
```

---

## Race Values

```python
# Standard races
Race.HUMANS
Race.ELVES
Race.DWARVES
Race.TROLLS
Race.ORCS
Race.DARKELVES

# For rune items
RuneRace.HEROES
RuneRace.HUMANS
RuneRace.ELVES
RuneRace.DWARVES
RuneRace.ORCS
RuneRace.TROLLS
RuneRace.DARKELVES
```

---

## Language Values

```python
Language.ENGLISH
Language.GERMAN
Language.FRENCH
Language.SPANISH
Language.ITALIAN
```

---

## Safety Checklist

- ✅ Backup original GameData.cff first
- ✅ Start with small changes
- ✅ Test after each modification
- ✅ Use version control (git) for mod scripts
- ✅ Save to new filename, compare before copying
- ❌ Don't exceed string length limits
- ❌ Don't delete entities (breaks references)
- ❌ Don't use invalid enum values

---

## Useful Commands

```bash
# Install tirganach
cd H:\SpellSmut\ModdingTools\tirganach
pip install -e .

# Run test
python H:\SpellSmut\test_cff_extract.py

# Run examples
python H:\SpellSmut\cff_modding_examples.py

# Compare files
python -m tirganach.compare GameData.cff GameData_mod.cff

# Backup original
copy "OriginalGameFiles\data\GameData.cff" "OriginalGameFiles\data\GameData_BACKUP.cff"
```

---

## Common Patterns

### Boost all items of a type
```python
for ring in gd.armor.where(item_subtype=EquipmentType.RING):
    ring.health *= 2
    ring.mana *= 2
```

### Make all fire spells cheaper
```python
for spell in gd.spells:
    if spell.req1_class == School.FIRE:
        spell.mana_cost = spell.mana_cost // 2
```

### Buff a race
```python
for rune in gd.items.where(item_type=ItemType.RUNE_INVENTORY,
                           item_subtype=RuneRace.ELVES):
    if rune.unit_stats:
        rune.unit_stats.strength += 20
```

### Change text
```python
text = gd.localisation.where(text_id=100, language=Language.ENGLISH)[0]
text.text = "My new text"
```

---

## Files Created

| File | Purpose |
|------|---------|
| `test_cff_extract.py` | Basic functionality test |
| `cff_modding_examples.py` | Comprehensive examples |
| `create_mod.py` | Template for creating mods |
| `CFF_MODDING_GUIDE.md` | Full documentation |
| `CFF_QUICK_REFERENCE.md` | This file |

---

**For full documentation, see:** `CFF_MODDING_GUIDE.md`
