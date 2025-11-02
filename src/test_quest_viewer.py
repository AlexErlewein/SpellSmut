#!/usr/bin/env python3
"""
Standalone Quest Viewer Test
Test the enhanced quest details viewer in isolation
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QObject, Signal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from TirganachReloaded.cff_editor.widgets.quest_details_viewer import QuestDetailsViewer


class MockDataModel(QObject):
    """Mock data model for testing"""
    
    element_selected = Signal(str, int)
    language_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.current_language = "German"
        
    def get_current_language(self):
        return self.current_language
    
    def get_localised_text(self, element, field):
        """Mock localized text"""
        if field == "name":
            return getattr(element, "name", "Test Quest")
        return None
    
    def get_advanced_description(self, element):
        """Mock description"""
        return getattr(element, "description", "Test description")
    
    def has_lua_data(self):
        return False
    
    def get_lua_quest_data(self, quest_id):
        return None
    
    def get_elements(self, category):
        return []


class MockQuest:
    """Mock quest object"""
    def __init__(self, quest_id):
        self.quest_id = quest_id
        self.name = f"Test Quest {quest_id}"
        self.description = "This is a test quest"
        self.parent_quest_id = 0
        self.order_index = 0
        self.name_id = quest_id
        self.description_id = quest_id + 1000


class TestQuestViewer(QMainWindow):
    """Test window for quest viewer"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Quest Viewer Test")
        self.setMinimumSize(1200, 800)
        
        # Create mock data model
        self.data_model = MockDataModel()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Buttons to test different quests
        button_layout = QHBoxLayout()
        for quest_id in [379, 380, 381, 390, 391]:
            btn = QPushButton(f"Load Quest {quest_id}")
            btn.clicked.connect(lambda checked, qid=quest_id: self.load_quest(qid))
            button_layout.addWidget(btn)
        layout.addLayout(button_layout)
        
        # Quest viewer
        print("Creating QuestDetailsViewer...")
        self.quest_viewer = QuestDetailsViewer(self.data_model)
        layout.addWidget(self.quest_viewer)
        
        # Load first quest
        self.load_quest(380)
    
    def load_quest(self, quest_id):
        """Load a quest"""
        print(f"\n{'='*80}")
        print(f"Loading Quest {quest_id}")
        print(f"{'='*80}")
        
        mock_quest = MockQuest(quest_id)
        self.quest_viewer.current_quest = mock_quest
        self.quest_viewer.update_quest_details()


def main():
    print("="*80)
    print("STANDALONE QUEST VIEWER TEST")
    print("="*80)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Quest Viewer Test")
    
    window = TestQuestViewer()
    window.show()
    
    print("\n✅ Window shown - check the GUI!")
    print("Click the buttons to load different quests")
    print("You should see:")
    print("  - Map Locations section")
    print("  - Reward Flags")
    print("  - Dialogues with translations")
    print("="*80)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
