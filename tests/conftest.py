"""
Pytest configuration and shared fixtures for SpellSmut tests
"""
import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "TirganachReloaded"))


@pytest.fixture
def project_root_path():
    """Fixture providing the project root path"""
    return Path(__file__).parent.parent


@pytest.fixture
def gamedata_path(project_root_path):
    """Fixture providing the path to GameData.cff"""
    path = project_root_path / "OriginalGameFiles" / "data" / "GameData.cff"
    if not path.exists():
        pytest.skip(f"GameData.cff not found at {path}")
    return path


@pytest.fixture
def tirganach_path(project_root_path):
    """Fixture providing the TirganachReloaded path"""
    return project_root_path / "TirganachReloaded"