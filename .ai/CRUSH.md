# CRUSH.md - SpellSmut Development Guide

## Project Structure Rules
- AI instructions in `.ai/`, docs in `docs/`, code in `src/`, planning in `ProjectPlanning/`
- Tests only in `src/tests/` with `test_*.py` naming
- Use UV for Python package management (Python 3.10+)

## Build/Test Commands
```bash
# Main Applications
uv run python src/OrthancsSchmiede/orthancs_schmiede.py    # Weapon/Armor Forge
cd src/TirganachReloaded && uv run python run_cff_editor.py # CFF Editor

# Testing
uv run pytest src/tests/ -v                  # All tests
uv run pytest src/tests/test_file.py -v       # Single test
uv run pytest src/tests/ -k "keyword" -v       # By keyword
uv run pytest src/tests/ -m "unit" -v          # Unit tests only
uv run pytest src/tests/ -m "not gui" -v       # Skip GUI tests

# Code Quality
uv run black src/                             # Format (100 char line length)
uv run isort src/                             # Sort imports
uv run mypy src/                              # Type checking
uv run flake8 src/                            # Linting
```

## Code Style
### Python
- 4 spaces, 100 char line length, Black formatter
- Imports: stdlib → third-party → local (blank lines between)
- Type hints required for function signatures
- `snake_case` functions/variables, `PascalCase` classes
- PySide6 only (no PyQt6), Python 3.10+

### Error Handling
- Use specific exceptions, avoid bare except
- Log errors with context, validate inputs early
- Use result objects or raise custom exceptions for domain errors

## Critical Patterns
### CFF Loading
```python
from OrthancsSchmiede.cff_weapon_loader import CFFWeaponLoader
loader = CFFWeaponLoader()
items = loader.load_all_weapons()  # Returns dict with requirements
```

### Requirements Structure
```python
requirements = {
    "strength": 0, "dexterity": 0, "intelligence": 0, "level": 1,
    "school_requirements": [{"requirement_school": "School.ELEMENTAL", "level": 5}]
}
```

## Essential Rules
- Always backup GameData.cff before modifications
- Use UV, never pip directly
- Run linting/type checking before commits
- Test mod compatibility after changes
- Lua scripts use Lua 4.0 syntax (not modern Lua)