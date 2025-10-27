"""
Test the full CFF editor GUI functionality
"""
import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from TirganachReloaded.cff_editor.main_window import MainWindow
from TirganachReloaded.cff_editor.data_model import CFFDataModel


class TestFullEditor:
    """Test the complete CFF editor functionality"""

    @pytest.fixture
    def qapp(self):
        """Fixture to provide QApplication instance"""
        return QApplication.instance() or QApplication([])

    @pytest.fixture
    def data_model(self):
        """Fixture to create data model"""
        return CFFDataModel()

    def test_data_model_creation(self, data_model):
        """Test that data model can be created"""
        assert data_model is not None
        assert data_model.game_data is None  # Should start empty

    def test_default_file_path(self, data_model):
        """Test that default file path is correctly determined"""
        default_path = data_model.get_default_file_path()
        assert default_path is not None
        assert isinstance(default_path, str)

        # Should point to OriginalGameFiles/data/GameData.cff
        assert "OriginalGameFiles" in default_path
        assert "GameData.cff" in default_path

    @pytest.mark.gui
    def test_main_window_creation(self, qapp):
        """Test that main window can be created (requires GUI)"""
        window = MainWindow()
        assert window is not None
        assert window.data_model is not None

        # Clean up
        window.close()

    @pytest.mark.integration
    def test_data_loading(self, data_model):
        """Test loading CFF data"""
        default_path = data_model.get_default_file_path()
        if not Path(default_path).exists():
            pytest.skip(f"GameData.cff not found at {default_path}")

        success = data_model.load_file(default_path)
        assert success, "Should successfully load CFF file"
        assert data_model.game_data is not None

    @pytest.mark.integration
    def test_quest_category_access(self, data_model):
        """Test accessing quest data"""
        default_path = data_model.get_default_file_path()
        if not Path(default_path).exists():
            pytest.skip(f"GameData.cff not found at {default_path}")

        # Load data
        data_model.load_file(default_path)

        # Switch to quests category
        data_model.current_category = "quests"

        # Get quest elements
        quests = data_model.get_elements("quests")
        assert isinstance(quests, list), "Should return list of quests"
        assert len(quests) > 0, "Should have quest entries"

        # Test first quest has expected attributes
        first_quest = quests[0]
        assert hasattr(first_quest, 'quest_id'), "Quest should have quest_id"
        assert hasattr(first_quest, 'name_id'), "Quest should have name_id"