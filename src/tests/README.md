# SpellSmut Test Suite

## Overview

This directory contains all test files for the SpellSmut project, using the pytest framework for comprehensive testing of the CFF editor and related functionality.

## Test Organization

### Test Categories

- **Unit Tests**: Individual component testing (e.g., `test_weapon_names.py`, `test_armor_names.py`)
- **Integration Tests**: Full workflow testing (marked with `@pytest.mark.integration`)
- **GUI Tests**: Interface testing (marked with `@pytest.mark.gui`)
- **Data Tests**: CFF file loading and manipulation (e.g., `test_cff_extract.py`)

### Test Files

| File | Description |
|------|-------------|
| `test_cff_extract.py` | Basic CFF file loading and data extraction |
| `test_weapon_names.py` | Weapon name loading and display functionality |
| `test_armor_names.py` | Armor name functionality |
| `test_element_names.py` | Element name display |
| `test_full_editor.py` | Complete GUI editor functionality |
| `test_quest_*.py` | Quest system functionality (access, dialogs, logic, UI, widgets) |
| `test_weapon_fields.py` | Weapon field validation |
| `test_widget_creation.py` | Widget creation tests |
| `test_final_verification.py` | End-to-end verification |

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Skip GUI tests
pytest -m "not gui"

# Only integration tests
pytest -m integration

# Specific test file
pytest tests/test_weapon_names.py

# Specific test class or method
pytest tests/test_cff_extract.py::TestCFFExtraction::test_basic_statistics
```

### Run with Coverage

```bash
pytest --cov=TirganachReloaded --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

### Run and Stop on First Failure

```bash
pytest -x
```

## Test Configuration

### pytest.ini

The `pytest.ini` file contains pytest configuration:
- Test discovery paths
- Custom markers
- Default options

### conftest.py

Shared fixtures and configuration:
- `project_root_path`: Project root directory
- `gamedata_path`: Path to GameData.cff file
- `tirganach_path`: Path to TirganachReloaded directory

## Test Results

**Current Status**: ✅ **24/24 tests passing**

```
======================== 24 passed, 4 warnings in 36.72s ========================
```

### Test Coverage

- ✅ CFF file loading and data extraction
- ✅ Weapon and armor name functionality
- ✅ GUI editor creation and data model
- ✅ Quest system (access, dialogs, logic, UI)
- ✅ Widget creation and functionality
- ✅ Multilingual support
- ✅ Element name display
- ✅ Integration with GameData.cff

## Writing New Tests

### Basic Test Structure

```python
import pytest
from pathlib import Path

class TestMyFeature:
    """Test my feature functionality"""

    @pytest.fixture
    def setup_data(self):
        """Fixture to set up test data"""
        return SomeData()

    def test_basic_functionality(self, setup_data):
        """Test basic functionality"""
        assert setup_data is not None
        # Your test code here

    @pytest.mark.integration
    def test_integration(self, gamedata_path):
        """Test integration with CFF file"""
        # Uses gamedata_path fixture from conftest.py
        assert gamedata_path.exists()
```

### Using Fixtures

Fixtures are defined in `conftest.py` and available to all tests:

```python
def test_with_gamedata(gamedata_path):
    """Test that uses GameData.cff path"""
    from tirganach import GameData
    gd = GameData(str(gamedata_path))
    assert gd is not None
```

### Test Markers

Use markers to categorize tests:

```python
@pytest.mark.gui
def test_gui_component():
    """This test requires GUI"""
    pass

@pytest.mark.integration
def test_integration_workflow():
    """This test requires external resources"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """This test takes a long time"""
    pass
```

## Best Practices

1. **Descriptive Test Names**: Use clear, descriptive names for test functions
2. **One Assertion Per Test**: Focus each test on a single behavior
3. **Use Fixtures**: Reuse setup code via fixtures
4. **Mark Appropriately**: Use markers to categorize tests
5. **Clean Up**: Use fixtures for setup/teardown
6. **Isolated Tests**: Each test should be independent
7. **Fast Tests**: Keep unit tests fast, mark slow tests appropriately

## Troubleshooting

### Import Errors

If you see import errors, ensure the project root is in your Python path:

```python
# conftest.py already handles this
sys.path.insert(0, str(project_root))
```

### QApplication Errors

For GUI tests, use `QApplication.instance()` to avoid creating multiple instances:

```python
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)
```

### GameData.cff Not Found

Tests requiring GameData.cff will be skipped if the file is not found. Ensure:

```
OriginalGameFiles/data/GameData.cff
```

exists in your project root.

## Continuous Integration

For CI/CD pipelines:

```bash
# Run all tests except GUI tests
pytest -m "not gui" --cov=TirganachReloaded --cov-report=xml

# Generate HTML report
pytest --html=report.html --self-contained-html
```

## Future Improvements

- [ ] Add more edge case tests
- [ ] Increase test coverage to 90%+
- [ ] Add performance benchmarks
- [ ] Add property-based testing with Hypothesis
- [ ] Add mutation testing
- [ ] Set up GitHub Actions CI/CD
