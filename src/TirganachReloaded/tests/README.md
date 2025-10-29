# Tests Directory

This directory contains unit tests for TirganachReloaded components that are not part of the main test suite in `src/tests/`.

## Test Files

### `test_armor_forge.py`
Tests for the Armor Forge system.

**What it tests:**
- Armor creation and modification
- Armor set management
- ID allocation for armor items
- Armor data validation
- JSON export/import

**Usage:**
```bash
python test_armor_forge.py
```

---

### `test_weapon_forge.py`
Tests for the Weapon Forge system.

**What it tests:**
- ID Manager system
- Weapon data model
- Weapon validation
- Balance calculations
- Weapon loader (save/load)
- Weapon types and materials
- Full integration workflow

**Usage:**
```bash
python test_weapon_forge.py
```

---

## Running Tests

### Individual Test Files
```bash
# Run armor forge tests
cd src/TirganachReloaded
python tests/test_armor_forge.py

# Run weapon forge tests
python tests/test_weapon_forge.py
```

### Using pytest
These tests can also be run with pytest:
```bash
# Run all tests in this directory
pytest src/TirganachReloaded/tests/

# Run specific test file
pytest src/TirganachReloaded/tests/test_weapon_forge.py

# Run with verbose output
pytest src/TirganachReloaded/tests/ -v
```

## Test Data

Test files may create temporary data files:
- `test_weapon_ids.json` - Test ID allocations
- `test_validation_ids.json` - Validation test IDs
- `test_integration_weapon.json` - Integration test data

These are gitignored and cleaned up automatically.

## Main Test Suite

For comprehensive project tests, see:
- `src/tests/` - Main pytest test suite
- `src/tests/README.md` - Main testing documentation

## Adding New Tests

When adding new tests to this directory:

1. **Follow naming convention:** `test_*.py`
2. **Import from parent:**
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   ```
3. **Document what you're testing** in the docstring
4. **Clean up test data** in teardown/cleanup
5. **Update this README** with your test description

## Dependencies

```bash
# Required packages
pip install PySide6 pillow pyyaml pytest

# Or use uv
uv pip install PySide6 pillow pyyaml pytest
```

## Related Documentation

- `../docs/CFF_EDITOR_README.md` - Editor documentation
- `../README.md` - Main TirganachReloaded README
- `../../tests/README.md` - Main test suite documentation