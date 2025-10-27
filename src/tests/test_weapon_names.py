"""
Test weapon name display functionality
"""
import pytest
from pathlib import Path
from TirganachReloaded.cff_editor.data_model import CFFDataModel


class TestWeaponNames:
    """Test weapon name loading and display functionality"""

    @pytest.fixture
    def data_model(self):
        """Fixture to create a data model instance"""
        return CFFDataModel()

    def test_weapon_names_loading(self, data_model):
        """Test that weapon names are loaded from JSON file"""
        data_model._load_weapon_names()

        # Should have loaded some weapon names
        assert len(data_model.weapon_name_mapping) > 0, "Should load weapon names"

        # Test some known weapon IDs
        test_ids = [27, 28, 29, 31, 58]
        for item_id in test_ids:
            name = data_model.get_weapon_name(item_id)
            assert name is not None, f"Should have name for weapon ID {item_id}"

    def test_weapon_name_retrieval(self, data_model):
        """Test retrieving weapon names by item_id"""
        data_model._load_weapon_names()

        # Test that we can retrieve names
        name = data_model.get_weapon_name(27)  # Known weapon ID
        assert isinstance(name, str), "Weapon name should be a string"
        assert len(name) > 0, "Weapon name should not be empty"

    @pytest.mark.integration
    def test_weapon_integration_with_cff(self, data_model):
        """Test weapon name integration with loaded CFF data"""
        # Load CFF file
        cff_path_str = data_model.get_default_file_path()
        cff_path = Path(cff_path_str)
        assert cff_path.exists(), f"CFF file should exist at {cff_path}"

        success = data_model.load_file(cff_path_str)
        assert success, "Should successfully load CFF file"

        # Load weapon names
        data_model._load_weapon_names()

        # Get weapons table
        weapons_table = data_model.get_table("weapons")
        assert weapons_table is not None, "Should have weapons table"
        assert len(weapons_table) > 0, "Weapons table should have entries"

        # Test that first few weapons have valid data
        for weapon in weapons_table[:3]:
            assert hasattr(weapon, 'item_id'), "Weapon should have item_id"
            item_id = weapon.item_id
            assert item_id > 0, f"Weapon should have valid item_id, got {item_id}"