# TirganachReloaded

A Python library and GUI editor for modding SpellForce Platinum Edition's `GameData.cff` files.

## Features

- 🎨 **GUI Editor** - Professional PySide6-based editor with dark theme
- 📝 **Python Library** - Programmatic access to game data
- 🔧 **Creation Wizards** - Create weapons, armor, spells, quests, NPCs, and more
- 📊 **Data Export** - Export to JSON/XML for analysis
- 🎯 **ID Management** - Automatic ID allocation to prevent conflicts

## Directory Structure

```
TirganachReloaded/
├── README.md                 # This file
├── cff_editor/              # GUI editor application
├── tirganach/               # Core CFF parsing library
├── data/                    # Reference data files
├── docs/                    # Documentation
├── examples/                # Example scripts and utilities
├── tests/                   # Unit tests
└── exports/                 # Exported data files (gitignored)
```

## Quick Start

### Launch the GUI Editor

```bash
cd src/TirganachReloaded
python run_cff_editor.py
```

Or from project root:
```bash
uv run python src/TirganachReloaded/run_cff_editor.py
```

### Documentation

- **[CFF Editor Guide](docs/CFF_EDITOR_README.md)** - Complete editor documentation
- **[Installation Guide](docs/INSTALLATION.md)** - Setup instructions
- **[Format Comparison](docs/FORMAT_COMPARISON.md)** - JSON vs XML vs CFF
- **[CFF Format Explanation](docs/CFF_FORMAT_EXPLANATION.md)** - File structure details
- **[Scripts Guide](docs/SCRIPTS_GUIDE.md)** - Using utility scripts

## Credits

Information about the CFF file structure was gathered from:
* [Hokan-Ashir/SFGameDataEditor](https://github.com/Hokan-Ashir/SFGameDataEditor)
* [leszekd25/spellforce_data_editor](https://github.com/leszekd25/spellforce_data_editor)

## Exporting to JSON/XML

Export GameData.cff to JSON or XML format for analysis:

```bash
# Export to JSON (fastest: 2-3s load time)
python examples/export_to_json.py path/to/GameData.cff

# Export to XML (human-readable: 10-15s load time)
python examples/export_to_xml.py path/to/GameData.cff
```

Exported files are saved to `exports/` directory:
- `exports/GameData.json` (73 MB) - Machine-readable, fastest loading
- `exports/GameData.xml` (63 MB) - Human-readable, good for diffs
- `exports/c2003_items.json` (3.3 MB) - Item reference data

See [examples/README.md](examples/README.md) for more export scripts and usage examples.

### Using Exported JSON

```python
import json

with open("exports/GameData.json") as f:
    data = json.load(f)

# Access spells
spells = data["spells"]
print(f"Total spells: {len(spells)}")

# Find a specific spell
fireball = [s for s in spells if s["spell_id"] == 1][0]
print(f"Mana cost: {fireball['mana']}")
```

See [docs/JSON_EXPORT_GUIDE.md](docs/JSON_EXPORT_GUIDE.md) for detailed JSON usage.

## Editing GameData

Here's how you use `tirganach`:

```python
from tirganach import GameData
from tirganach.types import *
import random

gd = GameData('/games/SpellForce/data/GameData.cff')

# let's make a cool item
ring = gd.armor.where(item_id=7065)[0]
ring.mana = 500
ring.health = 300
ring.item.name = "Ring of Cheaters"

# make Azula one of our heroes
sondra = gd.items.where(item_id=4425)[0]
sondra.inventory_match.name = "Rune Princess Azula"
sondra.name = "Princess Azula"
sondra.unit_stats.head_id = 27
sondra.unit_stats.size = 90 # canonically smol

sondra.unit_stats.skills[0].set(skill_school=School.LIGHT_COMBAT, skill_level=20)
sondra.unit_stats.skills[1].set(skill_school=School.LIGHT_BLADE_WEAPONS, skill_level=20)
sondra.unit_stats.skills[2].set(skill_school=School.LIGHT_ARMOR, skill_level=20)
sondra.unit_stats.skills[3].set(skill_school=School.RANGED_COMBAT, skill_level=15)
sondra.unit_stats.skills[4].set(skill_school=School.BOWS, skill_level=15)
sondra.unit_stats.skills[5].set(skill_school=School.ELEMENTAL_MAGIC, skill_level=20)
sondra.unit_stats.skills[6].set(skill_school=School.FIRE, skill_level=20)

cool_fire_spells = gd.spells.where(level=20, req1_class=School.FIRE)
random.shuffle(cool_fire_spells)

sondra.unit_stats.hero_spells[0].set(spell_id=cool_fire_spells[0].spell_id)
sondra.unit_stats.hero_spells[1].set(spell_id=cool_fire_spells[1].spell_id)
sondra.unit_stats.hero_spells[2].set(spell_id=cool_fire_spells[2].spell_id)

# now let's make elves OP
for rune in gd.items.where(item_type=ItemType.RUNE_INVENTORY, item_subtype=RuneRace.ELVES):
    rune.unit_stats.set(agility=120, dexterity=120, intelligence=120, wisdom=150)

gd.save("/games/SpellForce/data/GameData.cff")
```

Compare two versions:

```bash
python -m tirganach.compare GameData.cff GameData_patched.cff
```

## More Examples

Check the [examples/](examples/) directory for:
- `cff_modding_examples.py` - Collection of modding examples
- `create_mod.py` - Mod creation template
- `search_xml_data.py` - Search utility for XML exports
- `example_use_json.py` - JSON data analysis examples

## Testing

```bash
# Run TirganachReloaded-specific tests
python tests/test_armor_forge.py
python tests/test_weapon_forge.py

# Or use pytest
pytest src/TirganachReloaded/tests/ -v
```

See [tests/README.md](tests/README.md) for more information.

## Project Structure

- **cff_editor/** - GUI application with wizards and editors
- **tirganach/** - Core library for CFF file parsing
- **data/** - Reference data (ID mappings, icon mappings, project IDs)
- **docs/** - Documentation files
- **examples/** - Example scripts and utilities
- **tests/** - Unit tests for components
- **exports/** - Exported data files (gitignored)

## License

See [LICENSE](LICENSE) file for details.