"""
Pytest tests for the SpellSmut engine integration
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.engine.core import EngineCore
from src.engine.game_data.models import ItemDataModel, SpellDataModel
from src.engine.services.data_service import DataService
from src.engine.services.validation_service import ValidationService


class TestEngineIntegration:
    """Test the integration of all engine components"""

    def test_full_engine_initialization(self):
        """Test initializing the full engine"""
        engine = EngineCore()
        engine.initialize()

        assert engine.is_initialized is True

        # Verify all services are available
        data_service = engine.get_service("data")
        validation_service = engine.get_service("validation")

        assert isinstance(data_service, DataService)
        assert isinstance(validation_service, ValidationService)

    def test_data_flow_through_engine(self):
        """Test data flowing through the engine components"""
        # Initialize engine
        engine = EngineCore()
        engine.initialize()

        data_service = engine.get_service("data")
        validation_service = engine.get_service("validation")
        validation_service.register_default_validators()

        # Create and validate data
        item = ItemDataModel(id=1000, name="Integration Test Item", value=250)
        spell = SpellDataModel(
            id=2000,
            name="Integration Test Spell",
            school="water",
            level=7,
            mana_cost=45,
        )

        # Validate data
        assert validation_service.validate(item, "item") is True
        assert validation_service.validate(spell, "spell") is True

        # Store data
        assert data_service.add_entry("items", item.id, item) is True
        assert data_service.add_entry("spells", spell.id, spell) is True

        # Retrieve and verify data
        retrieved_item = data_service.get_entry("items", item.id)
        retrieved_spell = data_service.get_entry("spells", spell.id)

        assert retrieved_item is not None
        assert retrieved_spell is not None
        assert retrieved_item.name == "Integration Test Item"
        assert retrieved_spell.name == "Integration Test Spell"

    def test_engine_error_handling(self):
        """Test engine handles errors gracefully"""
        engine = EngineCore()
        engine.initialize()

        # Try to access non-existent service
        nonexistent_service = engine.get_service("nonexistent")
        assert nonexistent_service is None

        # Try to use services before initialization (should still work after initialization)
        data_service = engine.get_service("data")
        assert data_service is not None

        # Test with uninitialized engine (without initialization)
        uninitialized_engine = EngineCore()
        service_before_init = uninitialized_engine.get_service("data")
        assert service_before_init is None  # Should return None when not initialized

    def test_module_imports_work(self):
        """Test that all engine modules can be imported without errors"""
        # This test verifies that all imports work and there are no circular dependencies
        try:
            from src.engine import core
            from src.engine.game_data import models
            from src.engine.parsers import cff_parser
            from src.engine.services import data_service, validation_service
            from src.engine.utils import performance
            from src.engine.validators import base_validator

            # If we get here, all imports worked
            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
