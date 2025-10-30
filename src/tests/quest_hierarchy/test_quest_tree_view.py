"""
Test Quest Hierarchy Tree View
Displays all main quests with their subquests in a tree structure
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from TirganachReloaded.cff_editor.data_model import CFFDataModel


class QuestHierarchyViewer(QMainWindow):
    """Test window to view quest hierarchy"""

    def __init__(self, cff_path=None):
        super().__init__()
        self.data_model = CFFDataModel()
        self.quest_nodes = {}  # Map of quest_id -> quest data
        self.cff_path = cff_path

        self.setup_ui()

        if cff_path:
            self.load_cff(cff_path)

    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("Quest Hierarchy Tree Viewer - Test Implementation")
        self.setGeometry(100, 100, 1000, 700)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Title
        title = QLabel("Quest Hierarchy Tree View")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # File path section
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("CFF File:"))
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        file_layout.addWidget(self.file_path_edit)

        self.load_btn = QPushButton("Load CFF")
        self.load_btn.clicked.connect(self.browse_and_load)
        file_layout.addWidget(self.load_btn)

        layout.addLayout(file_layout)

        # Controls
        controls_layout = QHBoxLayout()

        self.expand_all_btn = QPushButton("Expand All")
        self.expand_all_btn.clicked.connect(self.expand_all)
        controls_layout.addWidget(self.expand_all_btn)

        self.collapse_all_btn = QPushButton("Collapse All")
        self.collapse_all_btn.clicked.connect(self.collapse_all)
        controls_layout.addWidget(self.collapse_all_btn)

        self.reload_btn = QPushButton("Reload Quest Data")
        self.reload_btn.clicked.connect(self.reload_quests)
        controls_layout.addWidget(self.reload_btn)

        controls_layout.addStretch()

        self.quest_count_label = QLabel("Quests: 0")
        self.quest_count_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(self.quest_count_label)

        layout.addLayout(controls_layout)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(
            ["Quest Name", "Quest ID", "Type", "Parent ID", "Order"]
        )
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(False)
        self.tree.setColumnWidth(0, 400)
        self.tree.setColumnWidth(1, 80)
        self.tree.setColumnWidth(2, 100)
        self.tree.setColumnWidth(3, 80)
        self.tree.setColumnWidth(4, 60)

        # Connect double-click to show details
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)

        layout.addWidget(self.tree)

        # Status bar
        self.statusBar().showMessage("Ready - Load a CFF file to view quest hierarchy")

    def browse_and_load(self):
        """Browse for CFF file and load it"""
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CFF File",
            str(Path.home()),
            "CFF Files (*.cff);;All Files (*.*)",
        )

        if file_path:
            self.load_cff(file_path)

    def load_cff(self, file_path):
        """Load CFF file"""
        self.statusBar().showMessage(f"Loading {file_path}...")

        try:
            if self.data_model.load_file(file_path):
                self.file_path_edit.setText(file_path)
                self.cff_path = file_path
                self.build_quest_tree()
                self.statusBar().showMessage(f"Loaded {file_path}", 3000)
            else:
                QMessageBox.warning(self, "Error", "Failed to load CFF file")
                self.statusBar().showMessage("Failed to load CFF file", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading CFF file:\n{str(e)}")
            self.statusBar().showMessage(f"Error: {str(e)}", 5000)

    def reload_quests(self):
        """Reload quest data"""
        if self.cff_path:
            self.build_quest_tree()

    def build_quest_tree(self):
        """Build the quest hierarchy tree"""
        self.tree.clear()
        self.quest_nodes.clear()

        # Get all quests
        quests = self.data_model.get_elements("quests")
        if not quests:
            self.statusBar().showMessage("No quests found in CFF file", 3000)
            return

        # Build quest node map
        for quest in quests:
            quest_id = getattr(quest, "quest_id", None)
            if quest_id is not None:
                parent_id = getattr(quest, "parent_quest_id", None)
                order_index = getattr(quest, "order_index", 0)

                # Get quest name (try localized first)
                name = self.data_model.get_localised_text(quest, "name")
                if not name:
                    name = getattr(quest, "name", f"Quest {quest_id}")

                self.quest_nodes[quest_id] = {
                    "quest": quest,
                    "quest_id": quest_id,
                    "name": name,
                    "parent_id": parent_id,
                    "order_index": order_index,
                    "children": [],
                }

        # Build parent-child relationships
        root_quests = []
        for quest_id, node in self.quest_nodes.items():
            parent_id = node["parent_id"]
            if parent_id and parent_id in self.quest_nodes:
                # Add as child to parent
                self.quest_nodes[parent_id]["children"].append(quest_id)
            else:
                # Root level quest (no parent or parent not found)
                root_quests.append(quest_id)

        # Sort children by order_index
        for node in self.quest_nodes.values():
            node["children"].sort(key=lambda qid: self.quest_nodes[qid]["order_index"])

        # Sort root quests by order_index
        root_quests.sort(key=lambda qid: self.quest_nodes[qid]["order_index"])

        # Create tree items
        for quest_id in root_quests:
            self.create_tree_item(quest_id, None)

        # Update count
        self.quest_count_label.setText(
            f"Quests: {len(self.quest_nodes)} (Main: {len(root_quests)})"
        )

        # Expand top level by default
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.childCount() > 0:
                item.setExpanded(True)

        self.statusBar().showMessage(f"Loaded {len(self.quest_nodes)} quests", 3000)

    def create_tree_item(self, quest_id, parent_item):
        """Create a tree item for a quest and its children"""
        node = self.quest_nodes[quest_id]

        # Determine type
        if node["parent_id"] is None or node["parent_id"] == 0:
            quest_type = "Main Quest"
        else:
            # Check if it has children
            if node["children"]:
                quest_type = "Sub-quest (Parent)"
            else:
                quest_type = "Sub-quest"

        # Create item
        item = QTreeWidgetItem(
            [
                str(node["name"]),
                str(quest_id),
                quest_type,
                str(node["parent_id"]) if node["parent_id"] else "-",
                str(node["order_index"]),
            ]
        )

        # Store quest data in item
        item.setData(0, Qt.ItemDataRole.UserRole, quest_id)

        # Set colors based on type
        if quest_type == "Main Quest":
            item.setForeground(0, Qt.GlobalColor.darkBlue)
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)
        elif quest_type == "Sub-quest (Parent)":
            item.setForeground(0, Qt.GlobalColor.darkGreen)

        # Add to tree
        if parent_item:
            parent_item.addChild(item)
        else:
            self.tree.addTopLevelItem(item)

        # Recursively create children
        for child_id in node["children"]:
            self.create_tree_item(child_id, item)

        return item

    def expand_all(self):
        """Expand all tree items"""
        self.tree.expandAll()

    def collapse_all(self):
        """Collapse all tree items"""
        self.tree.collapseAll()

    def on_item_double_clicked(self, item, column):
        """Handle double-click on quest item"""
        quest_id = item.data(0, Qt.ItemDataRole.UserRole)
        if quest_id and quest_id in self.quest_nodes:
            node = self.quest_nodes[quest_id]
            quest = node["quest"]

            # Get quest details
            name_id = getattr(quest, "name_id", "None")
            desc_id = getattr(quest, "description_id", "None")
            description = self.data_model.get_advanced_description(quest)
            if not description:
                description = "No description available"

            # Show details
            details = f"Quest ID: {quest_id}\n"
            details += f"Name: {node['name']}\n"
            details += f"Name ID: {name_id}\n"
            details += f"Description ID: {desc_id}\n"
            details += f"Parent ID: {node['parent_id'] if node['parent_id'] else 'None (Main Quest)'}\n"
            details += f"Order Index: {node['order_index']}\n"
            details += f"Children: {len(node['children'])}\n"
            details += f"\nDescription:\n{description}"

            QMessageBox.information(self, f"Quest Details - {node['name']}", details)


def main():
    """Run the test viewer"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Check for CFF file argument
    cff_path = None
    if len(sys.argv) > 1:
        cff_path = sys.argv[1]
    else:
        # Try default path
        default_path = (
            Path.home()
            / "Desktop"
            / "code"
            / "Others"
            / "SpellSmut"
            / "data"
            / "spellforce.cff"
        )
        if default_path.exists():
            cff_path = str(default_path)

    viewer = QuestHierarchyViewer(cff_path)
    viewer.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
