"""
Pytest tests for the SpellSmut engine services
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.engine.game_data.models import ItemDataModel, SpellDataModel
from src.engine.services.data_service import DataService
from src.engine.services.validation_service import ValidationService


class TestDataService:
    """Test the data service functionality"""

    @pytest.fixture
    def data_service(self):
        """Fixture providing a data service instance"""
        return DataService()

    def test_data_service_creation(self):
        """Test that data service initializes correctly"""
        service = DataService()
        assert service is not None

    def test_category_loading(self, data_service):
        """Test loading categories"""
        result = data_service.load_category("items", "test_path")
        assert result is True
        assert data_service.is_category_loaded("items") is True

    def test_add_and_get_entry(self, data_service):
        """Test adding and retrieving entries"""
        item = ItemDataModel(id=100, name="Test Item", value=50)

        # Add entry
        success = data_service.add_entry("items", item.id, item)
        assert success is True

        # Retrieve entry
        retrieved_item = data_service.get_entry("items", item.id)
        assert retrieved_item is not None
        assert retrieved_item.name == "Test Item"
        assert retrieved_item.value == 50

    def test_category_entries(self, data_service):
        """Test getting all entries in a category"""
        # Add some items
        item1 = ItemDataModel(id=100, name="Item 1", value=50)
        item2 = ItemDataModel(id=101, name="Item 2", value=75)

        data_service.add_entry("items", item1.id, item1)
        data_service.add_entry("items", item2.id, item2)

        # Get all entries
        entries = data_service.get_category_entries("items")
        assert len(entries) == 2
        assert 100 in entries
        assert 101 in entries

    def test_cache_clearing(self, data_service):
        """Test clearing cache"""
        item = ItemDataModel(id=100, name="Test Item", value=50)
        data_service.add_entry("items", item.id, item)

        # Verify item exists
        assert data_service.get_entry("items", item.id) is not None

        # Clear cache
        data_service.clear_cache("items")

        # Verify item no longer exists
        assert data_service.get_entry("items", item.id) is None


class TestValidationService:
    """Test the validation service functionality"""

    @pytest.fixture
    def validation_service(self):
        """Fixture providing a validation service instance"""
        service = ValidationService()
        service.register_default_validators()
        return service

    def test_validation_service_creation(self):
        """Test that validation service initializes correctly"""
        service = ValidationService()
        assert service is not None

    def test_valid_item_validation(self, validation_service):
        """Test validating a valid item"""
        item = ItemDataModel(id=200, name="Valid Item", value=100)
        is_valid = validation_service.validate(item, "item")
        assert is_valid is True
        assert len(validation_service.get_errors()) == 0

    def test_valid_spell_validation(self, validation_service):
        """Test validating a valid spell"""
        spell = SpellDataModel(
            id=300, name="Valid Spell", school="fire", level=5, mana_cost=30
        )
        is_valid = validation_service.validate(spell, "spell")
        assert is_valid is True

    def test_cross_category_validation(self, validation_service):
        """Test cross-category validation with multiple data types"""
        # Create valid items
        items = [
            ItemDataModel(id=400, name="Sword", value=100),
            ItemDataModel(id=401, name="Shield", value=75),
        ]

        # Create valid spells
        spells = [
            SpellDataModel(
                id=500, name="Fireball", school="fire", level=3, mana_cost=25
            ),
            SpellDataModel(id=501, name="Heal", school="water", level=2, mana_cost=20),
        ]

        # Validate collections
        item_valid = validation_service.validate_category(items, "item")
        spell_valid = validation_service.validate_category(spells, "spell")

        assert item_valid is True
        assert spell_valid is True
