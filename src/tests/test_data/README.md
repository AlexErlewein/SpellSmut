# Test Data Directory

This directory contains test data files and pytest output artifacts for the SpellSmut test suite.

## Directory Contents

### 📁 Committed Test Data Files
These files are version-controlled and used by tests:

- **`test_integration_ids.json`** - Test IDs for integration tests
- **`test_weapon_ids.json`** - Test weapon IDs for weapon-related tests

### 📁 Generated Pytest Artifacts (Git-ignored)
These are automatically generated when running tests:

- **`.pytest_cache/`** - Pytest cache directory
  - Stores test result information for faster re-runs
  - Created automatically by pytest
  - Location configured in `pytest.ini`: `cache_dir = src/tests/test_data/.pytest_cache`

- **`tmp/`** - Temporary test files
  - Used by pytest for temporary file operations during tests
  - Cleaned up automatically after tests complete
  - Location configured in `pytest.ini`: `--basetemp=src/tests/test_data/tmp`

- **`.coverage`** - Coverage data file (if running coverage)
  - Contains coverage measurement data
  - Generated when running `pytest --cov`

- **`htmlcov/`** - HTML coverage reports (if running coverage)
  - Human-readable coverage reports
  - Generated with `pytest --cov --cov-report=html`

## Configuration

Test output locations are configured in:

### pytest.ini (root directory)
```ini
[pytest]
cache_dir = src/tests/test_data/.pytest_cache
addopts = 
    --basetemp=src/tests/test_data/tmp
```

### pyproject.toml
```toml
[tool.coverage.run]
data_file = "src/tests/test_data/.coverage"

[tool.coverage.html]
directory = "src/tests/test_data/htmlcov"
```

## Running Tests

```bash
# Run all tests (outputs to this directory)
uv run pytest

# Run with coverage
uv run pytest --cov --cov-report=html

# Run specific test file
uv run pytest src/tests/test_weapon_names.py

# Clear pytest cache
rm -rf src/tests/test_data/.pytest_cache
```

## Adding New Test Data

When adding new test data files:

1. Place the file in this directory (`src/tests/test_data/`)
2. Add an entry to `.gitignore` to **keep** it (everything else is ignored by default)
3. Document it in this README
4. Reference it in your tests using relative paths:

```python
from pathlib import Path

TEST_DATA_DIR = Path(__file__).parent / "test_data"
test_file = TEST_DATA_DIR / "your_test_data.json"
```

## Maintenance

- **Keep committed**: Test data files that are needed by tests
- **Ignore generated**: All pytest artifacts and temporary files
- **Clean periodically**: Remove old cache and temp files if disk space is needed
