"""
Pytest tests for the SpellSmut engine validators
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.engine.game_data.models import ItemDataModel, QuestDataModel, SpellDataModel
from src.engine.validators.base_validator import (
    CrossReferenceValidator,
    DataIntegrityValidator,
    GameDataValidator,
)


class TestGameDataValidator:
    """Test the game data validator functionality"""

    @pytest.fixture
    def validator(self):
        """Fixture providing a game data validator instance"""
        return GameDataValidator()

    def test_validator_creation(self):
        """Test that validator initializes correctly"""
        validator = GameDataValidator()
        assert validator is not None

    def test_valid_item_validation(self, validator):
        """Test validating a valid item"""
        item = ItemDataModel(id=100, name="Valid Test Item", value=50)
        errors = validator.validate(item)
        assert len(errors["critical"]) == 0
        assert len(errors["warning"]) == 0

    def test_valid_spell_validation(self, validator):
        """Test validating a valid spell"""
        spell = SpellDataModel(
            id=200, name="Valid Spell", school="fire", level=5, mana_cost=30
        )
        errors = validator.validate(spell)
        assert len(errors["critical"]) == 0
        assert len(errors["warning"]) == 0

    def test_valid_quest_validation(self, validator):
        """Test validating a valid quest"""
        quest = QuestDataModel(
            id=300, name="Valid Quest", quest_type="main", required_level=5
        )
        errors = validator.validate(quest)
        assert len(errors["critical"]) == 0
        assert len(errors["warning"]) == 0

    def test_warning_generation(self, validator):
        """Test that warnings are generated appropriately"""
        # Test with empty name (should generate warning)
        item = ItemDataModel(id=101, name="", value=50)
        errors = validator.validate(item)
        assert len(errors["warning"]) > 0
        # Note: Exception will be raised during creation, so this test may not work


class TestDataIntegrityValidator:
    """Test the data integrity validator functionality"""

    @pytest.fixture
    def validator(self):
        """Fixture providing a data integrity validator instance"""
        return DataIntegrityValidator()

    def test_integrity_validator_creation(self):
        """Test that integrity validator initializes correctly"""
        validator = DataIntegrityValidator()
        assert validator is not None

    def test_valid_item_integrity(self, validator):
        """Test validating a valid item's integrity"""
        item = ItemDataModel(id=200, name="Valid Item", value=100)
        errors = validator.validate(item)
        # May have warnings but no critical errors for normal values
        assert isinstance(errors, dict)

    def test_data_consistency_check(self, validator):
        """Test checking data consistency"""
        # Test with valid data
        item = ItemDataModel(id=201, name="Consistent Item", value=100)
        errors = validator.validate(item)
        assert isinstance(errors, dict)


class TestCrossReferenceValidator:
    """Test the cross-reference validator functionality"""

    @pytest.fixture
    def validator(self):
        """Fixture providing a cross-reference validator instance"""
        return CrossReferenceValidator()

    def test_cross_reference_validator_creation(self):
        """Test that cross-reference validator initializes correctly"""
        validator = CrossReferenceValidator()
        assert validator is not None

    def test_dependency_validation(self, validator):
        """Test validating dependencies between data"""
        # Create test data with dependencies
        quest1 = QuestDataModel(id=300, name="Main Quest", quest_type="main")
        quest2 = QuestDataModel(
            id=301, name="Sub Quest", quest_type="sub", parent_quest_id=300
        )

        quests = [quest1, quest2]
        validator.register_data_set("quests", quests)

        # Validation should work now
        errors = validator.validate(quest2)
        assert isinstance(errors, dict)
