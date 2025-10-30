# CRUSH.md - SpellForce Modding Development Guide

## Build/Test Commands

```bash
# Install dependencies (using uv package manager)
uv sync

# Run all tests
pytest

# Run single test file
pytest src/tests/test_cff_extract.py

# Run specific test
pytest src/tests/test_cff_extract.py::TestCFFExtraction::test_gamedata_loads_successfully

# Run tests excluding GUI/slow tests
pytest -m "not gui and not slow"

# Format code
black src/ --line-length 88
isort src/ --profile black

# Type checking
mypy src/
```

## Code Style

- **Line length**: 88 characters (Black default)
- **Imports**: stdlib, third-party, local (separated by blank lines); use `isort --profile black`
- **Types**: Use type hints for all function signatures
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Docstrings**: Triple quotes for all modules/classes/functions
- **Error handling**: Use specific exceptions, avoid bare `except:`
- **Relative imports**: Use `from . import module` within packages, `from TirganachReloaded import` from tests

## Project Structure

- **AI instructions**: `.ai/CRUSH.md` (this file should be there, not root)
- **Planning docs**: `ProjectPlanning/` (never in root or docs/)
- **Documentation**: `docs/` with topic subfolders
- **Source code**: `src/TirganachReloaded/` for main library, `src/helper_tools/` for utilities
- **Tests**: `src/tests/` (pytest discovers `test_*.py` files)
- **Never modify**: `OriginalGameFiles/` (pristine reference only)

## Common Patterns

```python
# CFF file editing
from TirganachReloaded.tirganach import GameData
gd = GameData('OriginalGameFiles/data/GameData.cff')
items = gd.items.where(item_type=ItemType.EQUIPMENT)
gd.save('ModdedGameFiles/GameData_modified.cff')

# Test fixtures
@pytest.fixture
def game_data():
    path = Path("OriginalGameFiles/data/GameData.cff")
    if not path.exists():
        pytest.skip(f"GameData.cff not found")
    return GameData(str(path))
```
