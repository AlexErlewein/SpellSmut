# CRUSH.md - SpellSmut Development Guide

## 📍 File Location Notice

**This file is located at:** `.ai/CRUSH.md`

**Purpose:** Instructions specifically for Crush AI assistant

**Note:** Other AI assistants have their own instruction files:
- Claude Code → `.ai/CLAUDE.md`
- Gemini CLI → `.ai/GEMINI.md`
- Qwen → `.ai/QWEN.md`

All AI instruction files are in the `.ai/` hidden folder, separate from user documentation.

---

## Project Rules

This project follows the organization rules defined in `.rules/RULES.md`. Key rules include:
- File organization: `.ai/` for AI instructions, `docs/` for documentation, `src/` for code
- AI assistant file naming: Each AI has their own instruction file in `.ai/`
- Planning docs go in `ProjectPlanning/`, never in `docs/` or root
- All tests go in `src/tests/` with proper naming conventions

See `.rules/RULES.md` for complete project organization rules.

## Build/Test Commands

```bash
# Orthancs Schmiede (Main Forge Application)
python3 src/OrthancsSchmiede/orthancs_schmiede.py    # Launch unified forge suite
# Features: Weapon Forge, Armor Forge, item browsers with localization

# Python (TirganachReloaded CFF editor)
cd src/TirganachReloaded
python run_cff_editor.py                     # Launch GUI editor

# Testing (using pytest with uv)
uv run pytest src/tests/ -v                # Run all tests
uv run pytest src/tests/test_name.py -v      # Run specific test
uv run pytest src/tests/ -k "quest" -v     # Run tests matching keyword

# Code quality (if available)
uv run black src/                           # Format code
uv run isort src/                           # Sort imports
uv run mypy src/                            # Type checking
uv run flake8 src/                          # Linting
uv run pre-commit run --all-files          # Pre-commit hooks
uv run pytest src/tests/ --cov=src          # Run tests with coverage
uv run pytest src/tests/ -m "unit"          # Run unit tests only
uv run pytest src/tests/ -m "cff"           # Run CFF-specific tests only

# Application launch
uv run python -m TirganachReloaded.cff_editor.main    # Launch GUI editor
uv run cff-editor                                     # Launch via script entry
uv run tirganach                                     # Launch via script entry
```

## Code Style

### Python
- **Indentation**: 4 spaces (never tabs)
- **Line length**: 100 characters (updated from 88)
- **Imports**: Standard library, third-party, local (separated by blank lines)
- **Types**: Use type hints for function signatures
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Docstrings**: Use triple quotes for module/class/function docs
- **Code formatting**: Use Black formatter, isort for import sorting
- **Target Python**: 3.10+ (updated from 3.9+, removed 3.9 support)
- **Qt Framework**: PySide6 only (removed PyQt6 duplicates)

### Lua (Lua 4.0 - NOT modern Lua!)
- **Indentation**: 4 spaces
- **Functions**: `PascalCase()` for global, `snake_case()` for local
- **Variables**: `snake_case` for local, `PascalCase` for global tables
- **Constants**: `UPPER_SNAKE_CASE`
- **Syntax**: Use `getn(table)` not `#table`, `tremove()` not `table.remove()`
- **Upvalues**: Use `%variable` syntax for closures
- **Comments**: Explain C++ engine interactions and complex logic

### File Organization
- **Planning docs**: `ProjectPlanning/` (never in root or docs/)
- **Documentation**: `docs/` with subfolders by topic
- **Source code**: `src/` with subfolders by module
- **Never modify**: `OriginalGameFiles/` (pristine reference only)

## Common Patterns

### Orthancs Schmiede (Weapon/Armor Forge)
```python
# CFF Loaders - Load items with complete data including requirements
from OrthancsSchmiede.cff_weapon_loader import CFFWeaponLoader
from OrthancsSchmiede.cff_armor_loader import CFFArmorLoader

# Load weapons with school requirements
weapon_loader = CFFWeaponLoader()
weapons = weapon_loader.load_all_weapons()
# Returns: dict[int, dict] with requirements field

# Load armor with school requirements
armor_loader = CFFArmorLoader()
armors = armor_loader.load_all_armor()
# Returns: dict[int, dict] with requirements field

# Requirements structure:
# {
#   "strength": 0,
#   "dexterity": 0,
#   "intelligence": 0,
#   "level": 1,
#   "school_requirements": [
#     {"requirement_school": "School.ELEMENTAL", "level": 5}
#   ]
# }
```

### Python CFF Editing
```python
from TirganachReloaded import GameData
from TirganachReloaded.types import *

gd = GameData('path/to/GameData.cff')
items = gd.items.where(item_type=ItemType.EQUIPMENT)

# Access item requirements
if hasattr(gd, 'item_requirements'):
    reqs = gd.item_requirements.where(item_id=item_id)
    for req in reqs:
        print(f"School: {req.requirement_school}, Level: {req.level}")

gd.save('path/to/GameData_modified.cff')
```

### Lua Asset Loading (Lua 4.0)
```lua
local files = dir_readdirectory("path\\*.ext")
local manifest = strsplit("\n", gsub(readfile("manifest.txt"), "\r", ""))
local assets = list_concat(files, manifest)
```

## Critical Rules
- Use UV for Python package management (not pip directly)
- Use Lua 4.0 syntax only (no modern Lua 5.x features)
- Windows paths use backslashes in Lua scripts
- Always backup GameData.cff before modifications
- Test mod compatibility after changes
- Update docs/index.md when adding new guides
- Place planning docs in ProjectPlanning/, not docs/
- Run linting and type checking before committing changes
- Use test markers: `-m "not gui"` to skip GUI tests, `-m "not slow"` for fast tests

## Project-Specific Knowledge

### Armor System (Updated Nov 2025)
- **Armor Model**: Located at `src/TirganachReloaded/cff_editor/systems/armor_system/armor_model.py`
- **Requirements Field**: Added to Armor model to support school requirements
  - Structure matches weapon requirements format
  - Preserved through `to_dict()` and `from_dict()` serialization
- **CFFArmorLoader**: `src/OrthancsSchmiede/cff_armor_loader.py`
  - Loads complete armor data from GameData.cff
  - Includes school requirements from `item_requirements` table
  - Used by EnhancedArmorBrowser for consistent data loading
- **EnhancedArmorBrowser**: `src/TirganachReloaded/cff_editor/widgets/enhanced_armor_browser.py`
  - Uses CFFArmorLoader for complete data with requirements
  - Displays school requirements in details panel
  - Preserves requirements when duplicating armor

### Weapon System
- **CFFWeaponLoader**: `src/OrthancsSchmiede/cff_weapon_loader.py`
- Similar requirements loading pattern as armor system
- Both systems share common requirements structure

### School Requirements
School requirements are stored in the `item_requirements` table:
- Fields: `item_id`, `requirement_number`, `requirement_school`, `level`
- Schools include: ELEMENTAL, WHITE, BLACK, and other magic schools
- Multiple requirements can exist per item
- Displayed as formatted text: "Elemental L5, White L3"

### Key Data Structures
```python
# Requirements structure (armor and weapons)
requirements = {
    "strength": 0,
    "dexterity": 0,
    "intelligence": 0,
    "level": 1,
    "school_requirements": [
        {
            "requirement_number": 0,
            "requirement_school": "School.ELEMENTAL",
            "level": 5
        }
    ]
}
```
