"""
Test tirganach library functionality with GameData.cff
"""
import pytest
from pathlib import Path
from tirganach import GameData


class TestCFFExtraction:
    """Test basic CFF file loading and data extraction"""

    @pytest.fixture
    def gamedata_path(self):
        """Fixture to provide the path to GameData.cff"""
        path = Path("OriginalGameFiles/data/GameData.cff")
        if not path.exists():
            pytest.skip(f"GameData.cff not found at {path}")
        return str(path)

    @pytest.fixture
    def game_data(self, gamedata_path):
        """Fixture to load GameData.cff"""
        return GameData(gamedata_path)

    def test_gamedata_loads_successfully(self, game_data):
        """Test that GameData.cff loads without errors"""
        assert game_data is not None
        assert hasattr(game_data, 'spells')
        assert hasattr(game_data, 'items')

    def test_basic_statistics(self, game_data):
        """Test that basic data tables have expected content"""
        # Check that we have data in major tables
        assert len(game_data.spells) > 0, "Should have spells"
        assert len(game_data.items) > 0, "Should have items"
        assert len(game_data.creatures) > 0, "Should have creatures"
        assert len(game_data.buildings) > 0, "Should have buildings"
        assert len(game_data.armor) > 0, "Should have armor"
        assert len(game_data.weapons) > 0, "Should have weapons"
        assert len(game_data.localisation) > 0, "Should have localisation entries"

    def test_spell_data_structure(self, game_data):
        """Test that spells have expected attributes"""
        first_spell = game_data.spells[0]
        # Check for common spell attributes
        expected_attrs = ['spell_id', 'spell_name_id']
        for attr in expected_attrs:
            assert hasattr(first_spell, attr), f"Spell should have {attr} attribute"

    def test_item_data_structure(self, game_data):
        """Test that items have expected attributes"""
        first_item = game_data.items[0]
        # Check for common item attributes
        expected_attrs = ['item_id', 'name_id']
        for attr in expected_attrs:
            assert hasattr(first_item, attr), f"Item should have {attr} attribute"

    def test_localization_entries(self, game_data):
        """Test that localisation entries have expected structure"""
        first_entry = game_data.localisation[0]
        # Check for common localisation attributes
        expected_attrs = ['text_id', 'language', 'text']
        for attr in expected_attrs:
            assert hasattr(first_entry, attr), f"Localisation entry should have {attr} attribute"
