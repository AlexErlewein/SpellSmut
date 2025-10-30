"""
Integrated Quest Editor Widget
Combines quest tree editing with dialog branching editor and quest creator
"""

from PySide6.QtWidgets import (
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .dialog_branching_editor import DialogBranchingEditorWidget
from .quest_creator import QuestCreatorWidget
from .quest_details_viewer import QuestDetailsViewer
from .quest_hierarchy_tree import QuestHierarchyTreeWidget


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
        title_label.setStyleSheet(
            "font-weight: bold; font-size: 16px; margin-bottom: 10px;"
        )
        layout.addWidget(title_label)

        # Create a tabbed interface for different views
        self.tab_widget = QTabWidget()

        # Tab 1: Quest Hierarchy View (same as main editor)
        self.quest_hierarchy_view = QuestHierarchyTreeWidget(self.data_model)
        self.tab_widget.addTab(self.quest_hierarchy_view, "Quest Hierarchy")

        # Tab 2: Quest Details Viewer (comprehensive quest information)
        self.quest_details_viewer = QuestDetailsViewer(self.data_model)
        self.tab_widget.addTab(self.quest_details_viewer, "Quest Details")

        # Tab 3: Standalone Dialog Editor
        self.dialog_editor = DialogBranchingEditorWidget(self.data_model)
        self.tab_widget.addTab(self.dialog_editor, "Dialog Editor")

        # Tab 4: Quest Creator
        self.quest_creator = QuestCreatorWidget(self.data_model)
        quest_creator_tab = self.tab_widget.addTab(self.quest_creator, "Quest Creator")

        # Set icon for the quest creator tab
        try:
            import os

            from PySide6.QtGui import QIcon

            icon_path = os.path.join(
                os.path.dirname(__file__), "..", "icons", "quest_icon.png"
            )
            if os.path.exists(icon_path):
                self.tab_widget.setTabIcon(quest_creator_tab, QIcon(icon_path))
        except Exception as e:
            print(f"Could not load quest creator icon: {e}")

        layout.addWidget(self.tab_widget)

        # Connect to language changes
        self.data_model.language_changed.connect(self.on_language_changed)

        # Connect to data loaded signal to auto-load quests
        self.data_model.data_loaded.connect(self.on_data_loaded)

        # Connect to tab changes to load quests when hierarchy tab is shown
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        """Handle tab change"""
        # If switching to Quest Hierarchy tab and data is loaded, load quests
        if index == 0 and self.data_model.game_data:  # Tab 0 is Quest Hierarchy
            self.quest_hierarchy_view.load_quests()
        # If switching to Quest Details tab and a quest is selected, refresh details
        elif index == 1 and self.data_model.game_data:  # Tab 1 is Quest Details
            self.quest_details_viewer.refresh()

    def on_data_loaded(self):
        """Handle when data is loaded"""
        # Auto-load quests in the hierarchy view
        self.quest_hierarchy_view.load_quests()

    def on_language_changed(self, language):
        """Handle language change"""
        # Refresh quest hierarchy to show text in new language
        self.quest_hierarchy_view.refresh()
