"""
Integrated Quest Editor Widget
Combines quest tree editing with dialog branching editor and quest creator
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QTabWidget, QSplitter, QGroupBox)
from .quest_tree_editor import QuestTreeEditorWidget
from .dialog_branching_editor import DialogBranchingEditorWidget
from .quest_creator import QuestCreatorWidget


class QuestEditorWidget(QWidget):
    """Main integrated quest editor widget with quest tree, dialog editor, and quest creator"""

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model

        self.setup_ui()

    def setup_ui(self):
        """Setup the main UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title_label = QLabel("Quest Editor")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Create a tabbed interface for different views
        self.tab_widget = QTabWidget()

        # Tab 1: Quest Tree Editor
        self.quest_tree_editor = QuestTreeEditorWidget(self.data_model)
        self.tab_widget.addTab(self.quest_tree_editor, "Quest Tree Editor")

        # Tab 2: Standalone Dialog Editor
        self.dialog_editor = DialogBranchingEditorWidget(self.data_model)
        self.tab_widget.addTab(self.dialog_editor, "Dialog Editor")

        # Tab 3: Quest Creator
        self.quest_creator = QuestCreatorWidget(self.data_model)
        quest_creator_tab = self.tab_widget.addTab(self.quest_creator, "Quest Creator")
        
        # Set icon for the quest creator tab
        try:
            from PySide6.QtGui import QIcon
            import os
            icon_path = os.path.join(os.path.dirname(__file__), "..", "icons", "quest_icon.png")
            if os.path.exists(icon_path):
                self.tab_widget.setTabIcon(quest_creator_tab, QIcon(icon_path))
        except Exception as e:
            print(f"Could not load quest creator icon: {e}")

        layout.addWidget(self.tab_widget)

        # Connect the quest tree editor's quest selection to the dialog editor
        self.quest_tree_editor.quest_selected.connect(self.on_quest_selected)
        
        # Connect to language changes
        self.data_model.language_changed.connect(self.on_language_changed)

    def on_quest_selected(self, quest_node):
        """Handle when a quest is selected in the tree editor"""
        # Update the dialog editor to show the dialogs for this quest
        self.dialog_editor.current_dialog_nodes = quest_node.dialog_nodes
        self.dialog_editor.dialog_tree.load_dialog_tree(quest_node.dialog_nodes)

    def on_language_changed(self, language):
        """Handle language change"""
        # Update both the quest tree editor and dialog editor to reflect the new language
        # For now, we just need to make sure the quest details widget updates
        # The quest tree itself doesn't directly show text that needs language change
        pass  # The main window handles language changes which trigger UI refreshes