"""
Quest Hierarchy Tree Widget
Displays quests in a hierarchical tree structure with main quests and sub-quests
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class QuestHierarchyTreeWidget(QWidget):
    """Widget displaying quest hierarchy in a tree structure"""

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.quest_nodes = {}
        self.quest_elements = []  # Store quest elements for index lookup

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title and controls
        header_layout = QHBoxLayout()

        title = QLabel("Quest Hierarchy")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Control buttons
        self.expand_all_btn = QPushButton("Expand All")
        self.expand_all_btn.setMaximumWidth(100)
        header_layout.addWidget(self.expand_all_btn)

        self.collapse_all_btn = QPushButton("Collapse All")
        self.collapse_all_btn.setMaximumWidth(100)
        header_layout.addWidget(self.collapse_all_btn)

        # Quest count label
        self.count_label = QLabel("Quests: 0")
        self.count_label.setStyleSheet("font-weight: bold; margin-left: 10px;")
        header_layout.addWidget(self.count_label)

        layout.addLayout(header_layout)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(
            ["Quest Name", "Quest ID", "Type", "Parent ID", "Order"]
        )
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(False)
        self.tree.setColumnWidth(0, 350)
        self.tree.setColumnWidth(1, 80)
        self.tree.setColumnWidth(2, 120)
        self.tree.setColumnWidth(3, 80)
        self.tree.setColumnWidth(4, 60)

        layout.addWidget(self.tree)

    def connect_signals(self):
        """Connect signals"""
        self.expand_all_btn.clicked.connect(self.tree.expandAll)
        self.collapse_all_btn.clicked.connect(self.tree.collapseAll)
        self.tree.itemSelectionChanged.connect(self.on_selection_changed)

        # Connect to data model signals
        self.data_model.data_loaded.connect(self.on_data_loaded)
        self.data_model.category_changed.connect(self.on_category_changed)

    def on_data_loaded(self):
        """Handle data loaded signal"""
        # Refresh if we're currently showing quests
        if self.isVisible():
            self.load_quests()

    def on_category_changed(self, category):
        """Handle category change"""
        if category == "quests":
            self.load_quests()

    def load_quests(self):
        """Load and display quest hierarchy"""
        self.tree.clear()
        self.quest_nodes.clear()
        self.quest_elements = []

        # Get all quests
        quests = self.data_model.get_elements("quests")
        if not quests:
            self.count_label.setText("Quests: 0")
            return

        self.quest_elements = list(quests)

        # Build quest node map
        for i, quest in enumerate(quests):
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
                    "element_index": i,  # Store original index for selection
                }

        # Build parent-child relationships
        root_quests = []
        for quest_id, node in self.quest_nodes.items():
            parent_id = node["parent_id"]
            if parent_id and parent_id != 0 and parent_id in self.quest_nodes:
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
        self.count_label.setText(
            f"Quests: {len(self.quest_nodes)} (Main: {len(root_quests)})"
        )

        # Expand top level by default
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.childCount() > 0:
                item.setExpanded(True)

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

        # Store quest ID in item
        item.setData(0, Qt.ItemDataRole.UserRole, quest_id)

        # Set formatting based on type (no colors, just bold)
        if quest_type == "Main Quest" or quest_type == "Sub-quest (Parent)":
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)

        # Add to tree
        if parent_item:
            parent_item.addChild(item)
        else:
            self.tree.addTopLevelItem(item)

        # Recursively create children
        for child_id in node["children"]:
            self.create_tree_item(child_id, item)

        return item

    def on_selection_changed(self):
        """Handle tree selection change"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            quest_id = item.data(0, Qt.ItemDataRole.UserRole)

            if quest_id and quest_id in self.quest_nodes:
                # Get the element index
                element_index = self.quest_nodes[quest_id]["element_index"]
                # Emit signal through data model (same as element_table)
                self.data_model.current_element_index = element_index
                self.data_model.element_selected.emit("quests", element_index)

    def refresh(self):
        """Refresh the quest tree"""
        self.load_quests()
