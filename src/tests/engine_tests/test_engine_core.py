"""
Pytest tests for the SpellSmut engine core functionality
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.engine.core import EngineCore
from src.engine.game_data.models import ItemDataModel, QuestDataModel, SpellDataModel


class TestEngineCore:
    """Test the engine core functionality"""

    def test_engine_initialization(self):
        """Test that engine core initializes correctly"""
        engine = EngineCore()
        assert not engine.is_initialized

        engine.initialize()
        assert engine.is_initialized

    def test_service_access(self):
        """Test that services can be accessed after initialization"""
        engine = EngineCore()
        engine.initialize()

        # Test service access
        data_service = engine.get_service("data")
        validation_service = engine.get_service("validation")

        assert data_service is not None
        assert validation_service is not None

    def test_invalid_service_access(self):
        """Test that invalid service names return None"""
        engine = EngineCore()
        engine.initialize()

        invalid_service = engine.get_service("invalid_service")
        assert invalid_service is None


class TestDataModels:
    """Test the data models with validation"""

    def test_item_data_model_creation(self):
        """Test creating ItemDataModel instances"""
        item = ItemDataModel(id=1, name="Test Sword", type="weapon", value=100)
        assert item.id == 1
        assert item.name == "Test Sword"
        assert item.type == "weapon"
        assert item.value == 100

    def test_spell_data_model_creation(self):
        """Test creating SpellDataModel instances"""
        spell = SpellDataModel(
            id=2, name="Fireball", school="fire", level=3, mana_cost=50
        )
        assert spell.id == 2
        assert spell.name == "Fireball"
        assert spell.school == "fire"
        assert spell.level == 3
        assert spell.mana_cost == 50

    def test_quest_data_model_creation(self):
        """Test creating QuestDataModel instances"""
        quest = QuestDataModel(
            id=3, name="Test Quest", quest_type="main", required_level=5
        )
        assert quest.id == 3
        assert quest.name == "Test Quest"
        assert quest.quest_type == "main"
        assert quest.required_level == 5

    def test_invalid_id_validation(self):
        """Test that invalid IDs raise ValueError"""
        with pytest.raises(ValueError, match="ID must be positive"):
            ItemDataModel(id=0, name="Invalid Item")

    def test_negative_value_validation(self):
        """Test that negative values raise ValueError"""
        with pytest.raises(ValueError, match="Item value cannot be negative"):
            ItemDataModel(id=1, name="Invalid Item", value=-50)

    def test_invalid_level_validation(self):
        """Test that invalid levels raise ValueError"""
        with pytest.raises(ValueError, match="Spell level must be between 1-15"):
            SpellDataModel(id=1, name="Invalid Spell", level=20)
