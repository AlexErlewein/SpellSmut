"""
Quest Tree Editor Widget
Interactive hierarchical quest tree view with drag-drop editing capabilities
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QTreeWidget, QTreeWidgetItem, QPushButton,
                                QMenu, QMessageBox, QInputDialog, QSplitter,
                                QGroupBox, QTextEdit, QLineEdit, QComboBox,
                                QTabWidget, QListWidget)
from .dialog_branching_editor import DialogBranchingEditorWidget, DialogNode
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QPushButton, QMenu, QMessageBox, QInputDialog, QSplitter, QGroupBox, QTextEdit, QLineEdit, QComboBox, QTabWidget
from typing import Optional, List, Dict, Any
import json


class QuestNode:
    """Data model for quest nodes in the tree"""

    def __init__(self, quest_id: Optional[int] = None, name: str = "", description: str = "",
                  parent_id: Optional[int] = None, order_index: int = 0, is_new: bool = False,
                  dialog_nodes: Optional[List[DialogNode]] = None, rewards: Optional[Dict[str, Any]] = None,
                  requirements: Optional[List[Dict[str, Any]]] = None):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.order_index = order_index
        self.is_new = is_new  # Flag for newly created quests
        self.children: List['QuestNode'] = []
        self.dialog_nodes: List[DialogNode] = dialog_nodes or []  # Associated dialog nodes
        self.original_data: Dict[str, Any] = {}  # Store original quest data
        self.rewards: Dict[str, Any] = rewards or {}  # Rewards data (XP, Items, Money)
        self.requirements: List[Dict[str, Any]] = requirements or []  # Requirements/conditions

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'quest_id': self.quest_id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'order_index': self.order_index,
            'is_new': self.is_new,
            'dialog_nodes': [dialog_node.to_dict() for dialog_node in self.dialog_nodes],
            'children': [child.to_dict() for child in self.children],
            'rewards': self.rewards,
            'requirements': self.requirements
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestNode':
        """Create from dictionary"""
        from .dialog_branching_editor import DialogNode  # Import here to avoid circular import
        
        node = cls(
            quest_id=data.get('quest_id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            parent_id=data.get('parent_id'),
            order_index=data.get('order_index', 0),
            is_new=data.get('is_new', False),
            dialog_nodes=[DialogNode.from_dict(dialog_data) for dialog_data in data.get('dialog_nodes', [])],
            rewards=data.get('rewards', {}),
            requirements=data.get('requirements', [])
        )
        node.children = [cls.from_dict(child) for child in data.get('children', [])]
        return node

    def add_child(self, child: 'QuestNode'):
        """Add a child node"""
        child.parent_id = self.quest_id
        self.children.append(child)
        self.children.sort(key=lambda x: x.order_index)

    def remove_child(self, child: 'QuestNode'):
        """Remove a child node"""
        if child in self.children:
            self.children.remove(child)

    def add_dialog_node(self, dialog_node: 'DialogNode'):
        """Add a dialog node to this quest"""
        self.dialog_nodes.append(dialog_node)
        # Sort dialog nodes if needed by some criteria
        # self.dialog_nodes.sort(key=lambda x: x.dialogue_name)

    def remove_dialog_node(self, dialog_node: 'DialogNode'):
        """Remove a dialog node from this quest"""
        if dialog_node in self.dialog_nodes:
            self.dialog_nodes.remove(dialog_node)

    def get_next_quest_id(self) -> int:
        """Get next available quest ID (simple increment)"""
        # This is a placeholder - in real implementation, we'd check existing IDs
        return max([node.quest_id for node in self.get_all_nodes() if node.quest_id] + [0]) + 1

    def get_all_nodes(self) -> List['QuestNode']:
        """Get all nodes in the tree recursively"""
        nodes: List['QuestNode'] = [self]
        for child in self.children:
            nodes.extend(child.get_all_nodes())
        return nodes


class QuestTreeWidget(QTreeWidget):
    """Interactive tree widget for quest hierarchy editing"""

    quest_selected = Signal(object)  # QuestNode
    quest_modified = Signal()  # Emitted when tree structure changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the tree widget UI"""
        self.setHeaderLabels(["Quest Name", "ID", "Type", "Status"])
        self.setAlternatingRowColors(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Set column widths
        self.setColumnWidth(0, 250)  # Name
        self.setColumnWidth(1, 60)   # ID
        self.setColumnWidth(2, 80)   # Type
        self.setColumnWidth(3, 80)   # Status

    def setup_connections(self):
        """Setup signal connections"""
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemChanged.connect(self.on_item_changed)

    def load_quest_hierarchy(self, root_quests: List[QuestNode]):
        """Load quest hierarchy into the tree"""
        self.clear()

        for root_quest in sorted(root_quests, key=lambda x: x.order_index):
            root_item = self.create_tree_item(root_quest)
            self.addTopLevelItem(root_item)
            self.populate_children(root_item, root_quest)

        self.expandAll()

    def create_tree_item(self, quest_node: QuestNode) -> QTreeWidgetItem:
        """Create a tree item for a quest node"""
        item = QTreeWidgetItem()

        # Set quest name (editable)
        item.setText(0, quest_node.name or f"Quest {quest_node.quest_id}")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)

        # Set quest ID
        item.setText(1, str(quest_node.quest_id) if quest_node.quest_id else "New")

        # Set type
        if quest_node.parent_id is None:
            item.setText(2, "Main Quest")
        else:
            item.setText(2, "Sub-quest")

        # Set status
        if quest_node.is_new:
            item.setText(3, "New")
            item.setBackground(3, self.palette().highlight().color())
        else:
            item.setText(3, "Existing")

        # Store reference to quest node
        item.setData(0, Qt.ItemDataRole.UserRole, quest_node)

        return item

    def populate_children(self, parent_item: QTreeWidgetItem, parent_node: QuestNode):
        """Recursively populate child items"""
        for child_node in sorted(parent_node.children, key=lambda x: x.order_index):
            child_item = self.create_tree_item(child_node)
            parent_item.addChild(child_item)
            self.populate_children(child_item, child_node)

    def show_context_menu(self, position: QPoint):
        """Show context menu for tree items"""
        item = self.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        # Add quest actions
        add_main_quest_action = QAction("Add Main Quest", self)
        add_main_quest_action.triggered.connect(lambda: self.add_quest(None))
        menu.addAction(add_main_quest_action)

        add_subquest_action = QAction("Add Sub-quest", self)
        add_subquest_action.triggered.connect(lambda: self.add_subquest(item))
        menu.addAction(add_subquest_action)

        menu.addSeparator()

        # Edit actions
        edit_action = QAction("Edit Quest", self)
        edit_action.triggered.connect(lambda: self.edit_quest(item))
        menu.addAction(edit_action)

        menu.addSeparator()

        # Delete action
        delete_action = QAction("Delete Quest", self)
        delete_action.triggered.connect(lambda: self.delete_quest(item))
        menu.addAction(delete_action)

        menu.exec(self.mapToGlobal(position))

    def add_quest(self, parent_item: Optional[QTreeWidgetItem] = None):
        """Add a new quest"""
        # Get next available quest ID
        next_id = self.get_next_quest_id()

        # Create new quest node
        new_quest = QuestNode(
            quest_id=next_id,
            name=f"New Quest {next_id}",
            is_new=True
        )

        if parent_item:
            # Add as subquest
            parent_node = parent_item.data(0, Qt.ItemDataRole.UserRole)
            parent_node.add_child(new_quest)
            child_item = self.create_tree_item(new_quest)
            parent_item.addChild(child_item)
            parent_item.setExpanded(True)
        else:
            # Add as main quest
            root_item = self.create_tree_item(new_quest)
            self.addTopLevelItem(root_item)

        self.quest_modified.emit()

    def add_subquest(self, parent_item: QTreeWidgetItem):
        """Add a subquest to the selected parent"""
        self.add_quest(parent_item)

    def edit_quest(self, item: QTreeWidgetItem):
        """Edit quest properties"""
        quest_node = item.data(0, Qt.ItemDataRole.UserRole)
        if not quest_node:
            return

        # For now, just make the name editable (already is)
        self.editItem(item, 0)

    def delete_quest(self, item: QTreeWidgetItem):
        """Delete a quest"""
        quest_node = item.data(0, Qt.ItemDataRole.UserRole)
        if not quest_node:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Quest",
            f"Are you sure you want to delete quest '{quest_node.name}' and all its subquests?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove from parent
            parent = item.parent()
            if parent:
                parent_node = parent.data(0, Qt.ItemDataRole.UserRole)
                parent_node.remove_child(quest_node)
                parent.removeChild(item)
            else:
                # Root level quest
                index = self.indexOfTopLevelItem(item)
                if index >= 0:
                    self.takeTopLevelItem(index)

            self.quest_modified.emit()

    def get_next_quest_id(self) -> int:
        """Get next available quest ID"""
        # Find all existing quest IDs
        all_nodes = []
        for i in range(self.topLevelItemCount()):
            root_item = self.topLevelItem(i)
            root_node = root_item.data(0, Qt.ItemDataRole.UserRole)
            if root_node:
                all_nodes.extend(root_node.get_all_nodes())

        existing_ids = [node.quest_id for node in all_nodes if node.quest_id and not node.is_new]
        if existing_ids:
            return max(existing_ids) + 1
        else:
            return 1

    def on_selection_changed(self):
        """Handle item selection change"""
        current_item = self.currentItem()
        if current_item:
            quest_node = current_item.data(0, Qt.ItemDataRole.UserRole)
            if quest_node:
                self.quest_selected.emit(quest_node)

    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handle item text changes"""
        if column == 0:  # Name column
            quest_node = item.data(0, Qt.ItemDataRole.UserRole)
            if quest_node:
                new_name = item.text(0)
                quest_node.name = new_name
                self.quest_modified.emit()

    def get_root_quests(self) -> List[QuestNode]:
        """Get all root quest nodes"""
        root_quests = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            node = item.data(0, Qt.ItemDataRole.UserRole)
            if node:
                root_quests.append(node)
        return root_quests

    def dropEvent(self, event):
        """Handle drag and drop events"""
        super().dropEvent(event)

        # Update the data model to reflect new hierarchy
        # This is a simplified implementation - in practice, you'd need more sophisticated
        # logic to handle reparenting and order updates
        self.quest_modified.emit()


class QuestTreeEditorWidget(QWidget):
    """Main quest tree editor widget"""

    quest_selected = Signal(object)  # QuestNode
    quests_modified = Signal()  # Emitted when quests are modified

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.current_quest_nodes: List[QuestNode] = []

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the main UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title_label = QLabel("Quest Tree Editor")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        self.add_main_quest_btn = QPushButton("Add Main Quest")
        self.add_main_quest_btn.setToolTip("Add a new main quest at the root level")
        toolbar_layout.addWidget(self.add_main_quest_btn)

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setToolTip("Save quest hierarchy changes to CFF file")
        toolbar_layout.addWidget(self.save_btn)

        self.load_btn = QPushButton("Load from CFF")
        self.load_btn.setToolTip("Load quest hierarchy from CFF file")
        toolbar_layout.addWidget(self.load_btn)

        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Quest tree
        tree_group = QGroupBox("Quest Hierarchy")
        tree_layout = QVBoxLayout(tree_group)

        self.quest_tree = QuestTreeWidget()
        tree_layout.addWidget(self.quest_tree)

        splitter.addWidget(tree_group)

        # Right side - Quest properties
        properties_group = QGroupBox("Quest Properties")
        properties_layout = QVBoxLayout(properties_group)

        # Quest basic info
        self.setup_properties_ui(properties_layout)

        splitter.addWidget(properties_group)

        # Set splitter proportions
        splitter.setSizes([400, 300])

        layout.addWidget(splitter)

    def setup_properties_ui(self, layout):
        """Setup the quest properties UI with tabs for properties, rewards, requirements, and dialogs"""
        # Create tab widget
        tab_widget = QTabWidget()

        # Quest properties tab
        properties_tab = QWidget()
        properties_layout = QVBoxLayout(properties_tab)

        # Quest ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Quest ID:"))
        self.quest_id_edit = QLineEdit()
        self.quest_id_edit.setReadOnly(True)  # IDs are auto-generated
        id_layout.addWidget(self.quest_id_edit)
        properties_layout.addLayout(id_layout)

        # Quest Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.quest_name_edit = QLineEdit()
        name_layout.addWidget(self.quest_name_edit)
        properties_layout.addLayout(name_layout)

        # Description
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        desc_layout.addWidget(self.description_edit)
        properties_layout.addLayout(desc_layout)

        # Parent quest selector
        parent_layout = QHBoxLayout()
        parent_layout.addWidget(QLabel("Parent Quest:"))
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("None (Main Quest)", None)
        parent_layout.addWidget(self.parent_combo)
        properties_layout.addLayout(parent_layout)

        # Properties buttons
        properties_buttons_layout = QHBoxLayout()

        self.update_btn = QPushButton("Update Quest")
        self.update_btn.setToolTip("Update quest properties")
        properties_buttons_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Delete Quest")
        self.delete_btn.setToolTip("Delete this quest and all subquests")
        properties_buttons_layout.addWidget(self.delete_btn)

        properties_buttons_layout.addStretch()

        # Generate Lua script button
        self.generate_lua_btn = QPushButton("Generate Lua Script")
        self.generate_lua_btn.setToolTip("Generate Lua script for this quest")
        properties_buttons_layout.addWidget(self.generate_lua_btn)

        properties_layout.addLayout(properties_buttons_layout)

        # Add properties tab
        tab_widget.addTab(properties_tab, "Properties")

        # Rewards tab
        rewards_tab = QWidget()
        rewards_layout = QVBoxLayout(rewards_tab)

        # XP reward
        xp_layout = QHBoxLayout()
        xp_layout.addWidget(QLabel("XP Reward:"))
        self.xp_edit = QLineEdit()
        self.xp_edit.setPlaceholderText("Enter XP amount")
        xp_layout.addWidget(self.xp_edit)
        rewards_layout.addLayout(xp_layout)

        # Items reward
        items_layout = QVBoxLayout()
        items_layout.addWidget(QLabel("Item Rewards (comma-separated IDs):"))
        self.items_edit = QLineEdit()
        self.items_edit.setPlaceholderText("e.g., 100, 200, 300")
        items_layout.addWidget(self.items_edit)
        rewards_layout.addLayout(items_layout)

        # Money reward
        money_layout = QVBoxLayout()
        money_layout.addWidget(QLabel("Money Rewards:"))
        gold_layout = QHBoxLayout()
        gold_layout.addWidget(QLabel("Gold:"))
        self.gold_edit = QLineEdit()
        self.gold_edit.setPlaceholderText("0")
        gold_layout.addWidget(self.gold_edit)
        money_layout.addLayout(gold_layout)
        silver_layout = QHBoxLayout()
        silver_layout.addWidget(QLabel("Silver:"))
        self.silver_edit = QLineEdit()
        self.silver_edit.setPlaceholderText("0")
        silver_layout.addWidget(self.silver_edit)
        money_layout.addLayout(silver_layout)
        copper_layout = QHBoxLayout()
        copper_layout.addWidget(QLabel("Copper:"))
        self.copper_edit = QLineEdit()
        self.copper_edit.setPlaceholderText("0")
        copper_layout.addWidget(self.copper_edit)
        money_layout.addLayout(copper_layout)
        rewards_layout.addLayout(money_layout)

        rewards_layout.addStretch()
        tab_widget.addTab(rewards_tab, "Rewards")

        # Requirements tab
        requirements_tab = QWidget()
        requirements_layout = QVBoxLayout(requirements_tab)

        # Requirements list
        requirements_layout.addWidget(QLabel("Quest Requirements:"))
        self.requirements_list = QListWidget()
        self.requirements_list.setMaximumHeight(150)
        requirements_layout.addWidget(self.requirements_list)

        # Add requirement button
        add_req_layout = QHBoxLayout()
        self.add_requirement_btn = QPushButton("Add Requirement")
        self.add_requirement_btn.setToolTip("Add a new requirement condition")
        add_req_layout.addWidget(self.add_requirement_btn)
        self.remove_requirement_btn = QPushButton("Remove Selected")
        self.remove_requirement_btn.setToolTip("Remove selected requirement")
        add_req_layout.addWidget(self.remove_requirement_btn)
        add_req_layout.addStretch()
        requirements_layout.addLayout(add_req_layout)

        requirements_layout.addStretch()
        tab_widget.addTab(requirements_tab, "Requirements")

        # Dialogs tab
        dialogs_tab = QWidget()
        dialogs_layout = QVBoxLayout(dialogs_tab)

        # Create dialog branching editor
        self.dialog_editor = DialogBranchingEditorWidget(self.data_model)
        dialogs_layout.addWidget(self.dialog_editor)

        # Add dialogs tab
        tab_widget.addTab(dialogs_tab, "Dialogs")

        # Add tab widget to main layout
        layout.addWidget(tab_widget)

        # Connect to dialog editor signals
        self.dialog_editor.dialogs_modified.connect(self.on_quests_modified)

    def setup_connections(self):
        """Setup signal connections"""
        self.add_main_quest_btn.clicked.connect(lambda: self.quest_tree.add_quest())
        self.save_btn.clicked.connect(self.save_quests)
        self.load_btn.clicked.connect(self.load_quests)

        self.quest_tree.quest_selected.connect(self.on_quest_selected)
        self.quest_tree.quest_modified.connect(self.on_quests_modified)

        self.update_btn.clicked.connect(self.update_quest_properties)
        self.delete_btn.clicked.connect(self.delete_selected_quest)
        self.add_requirement_btn.clicked.connect(self.add_requirement)
        self.remove_requirement_btn.clicked.connect(self.remove_requirement)
        self.generate_lua_btn.clicked.connect(self.generate_lua_script)

        # Connect to language changes
        self.data_model.language_changed.connect(self.on_language_changed)

    def load_quests(self):
        """Load quests from the CFF data model"""
        if not self.data_model.game_data:
            QMessageBox.warning(self, "No Data", "No CFF file is loaded.")
            return

        try:
            # Get all quests from data model
            quests_data = self.data_model.get_elements('quests')

            # Build quest node hierarchy
            quest_nodes = self.build_quest_hierarchy(quests_data)

            # Load into tree
            self.current_quest_nodes = quest_nodes
            self.quest_tree.load_quest_hierarchy(quest_nodes)

            # Update parent combo box
            self.update_parent_combo()

            QMessageBox.information(self, "Success", f"Loaded {len(quest_nodes)} root quests.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load quests: {str(e)}")

    def build_quest_hierarchy(self, quests_data) -> List[QuestNode]:
        """Build quest node hierarchy from raw quest data"""
        # Create node map
        node_map = {}

        # First pass: create all nodes
        for quest in quests_data:
            quest_id = getattr(quest, 'quest_id', None)
            if quest_id is None:
                continue

            # Get any related dialogues for this quest
            # For now, we'll create empty dialog nodes - they can be populated when the quest is selected
            node = QuestNode(
                quest_id=quest_id,
                name=getattr(quest, 'name', f'Quest {quest_id}'),
                description=getattr(quest, 'description', ''),
                parent_id=getattr(quest, 'parent_quest_id', None),
                order_index=getattr(quest, 'order_index', 0)
            )
            node.original_data = {
                'quest_id': quest_id,
                'parent_quest_id': getattr(quest, 'parent_quest_id', None),
                'name_id': getattr(quest, 'name_id', None),
                'description_id': getattr(quest, 'description_id', None),
                'order_index': getattr(quest, 'order_index', 0)
            }
            node_map[quest_id] = node

        # Second pass: build hierarchy
        root_quests = []
        for node in node_map.values():
            if node.parent_id and node.parent_id in node_map:
                # Add as child to parent
                parent_node = node_map[node.parent_id]
                parent_node.add_child(node)
            else:
                # Root level quest
                root_quests.append(node)

        return sorted(root_quests, key=lambda x: x.order_index)

    def save_quests(self):
        """Save quest hierarchy changes to CFF"""
        if not self.data_model.game_data:
            QMessageBox.warning(self, "No Data", "No CFF file is loaded.")
            return

        try:
            # Get all quest nodes
            all_nodes = []
            for root_node in self.current_quest_nodes:
                all_nodes.extend(root_node.get_all_nodes())

            # Validate quest data
            if not self.validate_quests(all_nodes):
                return

            # Apply changes to CFF data
            self.apply_quest_changes(all_nodes)

            # Mark data as modified
            self.data_model.modified = True
            self.data_model.data_modified.emit()

            QMessageBox.information(self, "Success", f"Saved {len(all_nodes)} quests.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save quests: {str(e)}")

    def validate_quests(self, quest_nodes: List[QuestNode]) -> bool:
        """Validate quest data before saving"""
        errors = []

        # Check for duplicate IDs
        ids = set()
        for node in quest_nodes:
            if node.quest_id in ids:
                errors.append(f"Duplicate quest ID: {node.quest_id}")
            ids.add(node.quest_id)

        # Check for empty names
        for node in quest_nodes:
            if not node.name or node.name.strip() == "":
                errors.append(f"Quest {node.quest_id} has no name")

        # Check for circular references (simplified check)
        for node in quest_nodes:
            visited = set()
            current = node
            while current.parent_id:
                if current.quest_id in visited:
                    errors.append(f"Circular reference detected involving quest {node.quest_id}")
                    break
                visited.add(current.quest_id)
                # Find parent node
                parent_found = False
                for n in quest_nodes:
                    if n.quest_id == current.parent_id:
                        current = n
                        parent_found = True
                        break
                if not parent_found:
                    break

        if errors:
            error_text = "\n".join(errors)
            QMessageBox.warning(self, "Validation Errors", f"Please fix the following errors:\n\n{error_text}")
            return False

        return True

    def apply_quest_changes(self, quest_nodes: List[QuestNode]):
        """Apply quest changes to the CFF data model"""
        # This is a placeholder implementation
        # In a full implementation, you'd need to:
        # 1. Update existing quest records
        # 2. Add new quest records
        # 3. Handle localisation table updates for names/descriptions
        # 4. Update parent relationships

        print(f"Applying changes for {len(quest_nodes)} quests")
        # TODO: Implement actual CFF data updates

    def update_parent_combo(self):
        """Update the parent quest combo box"""
        self.parent_combo.clear()
        self.parent_combo.addItem("None (Main Quest)", None)

        # Add all existing quests as potential parents
        all_nodes = []
        for root_node in self.current_quest_nodes:
            all_nodes.extend(root_node.get_all_nodes())

        for node in sorted(all_nodes, key=lambda x: x.quest_id or 0):
            if node.quest_id:
                self.parent_combo.addItem(f"{node.name} (ID: {node.quest_id})", node.quest_id)

    def on_quest_selected(self, quest_node: QuestNode):
        """Handle quest selection"""
        self.update_properties_ui(quest_node)
        self.quest_selected.emit(quest_node)

    def update_properties_ui(self, quest_node: QuestNode):
        """Update the properties UI for selected quest"""
        self.quest_id_edit.setText(str(quest_node.quest_id) if quest_node.quest_id else "New")
        self.quest_name_edit.setText(quest_node.name)
        self.description_edit.setPlainText(quest_node.description)

        # Set parent combo
        if quest_node.parent_id:
            index = self.parent_combo.findData(quest_node.parent_id)
            if index >= 0:
                self.parent_combo.setCurrentIndex(index)
        else:
            self.parent_combo.setCurrentIndex(0)  # None

        # Update rewards fields
        self.xp_edit.setText(str(quest_node.rewards.get('xp', 0)))
        self.items_edit.setText(', '.join(map(str, quest_node.rewards.get('items', []))))
        self.gold_edit.setText(str(quest_node.rewards.get('gold', 0)))
        self.silver_edit.setText(str(quest_node.rewards.get('silver', 0)))
        self.copper_edit.setText(str(quest_node.rewards.get('copper', 0)))

        # Update requirements list
        self.requirements_list.clear()
        for req in quest_node.requirements:
            self.requirements_list.addItem(req.get('condition', ''))

        # Update dialog editor with quest's dialog nodes
        self.dialog_editor.current_dialog_nodes = quest_node.dialog_nodes
        self.dialog_editor.dialog_tree.load_dialog_tree(quest_node.dialog_nodes)

    def update_quest_properties(self):
        """Update quest properties from UI"""
        current_item = self.quest_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a quest to update.")
            return

        quest_node = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not quest_node:
            return

        # Update properties
        quest_node.name = self.quest_name_edit.text()
        quest_node.description = self.description_edit.toPlainText()

        # Update parent
        new_parent_id = self.parent_combo.currentData()
        if new_parent_id != quest_node.parent_id:
            # TODO: Handle parent change (reparenting logic)
            quest_node.parent_id = new_parent_id

        # Update rewards
        try:
            quest_node.rewards['xp'] = int(self.xp_edit.text()) if self.xp_edit.text() else 0
        except ValueError:
            quest_node.rewards['xp'] = 0
        try:
            quest_node.rewards['items'] = [int(i.strip()) for i in self.items_edit.text().split(',') if i.strip()]
        except ValueError:
            quest_node.rewards['items'] = []
        try:
            quest_node.rewards['gold'] = int(self.gold_edit.text()) if self.gold_edit.text() else 0
        except ValueError:
            quest_node.rewards['gold'] = 0
        try:
            quest_node.rewards['silver'] = int(self.silver_edit.text()) if self.silver_edit.text() else 0
        except ValueError:
            quest_node.rewards['silver'] = 0
        try:
            quest_node.rewards['copper'] = int(self.copper_edit.text()) if self.copper_edit.text() else 0
        except ValueError:
            quest_node.rewards['copper'] = 0

        # Update requirements
        quest_node.requirements = [{"condition": self.requirements_list.item(i).text()} for i in range(self.requirements_list.count())]

        # Update dialog nodes from the dialog editor
        quest_node.dialog_nodes = self.dialog_editor.current_dialog_nodes

        # Update tree display
        current_item.setText(0, quest_node.name or f"Quest {quest_node.quest_id}")

        self.on_quests_modified()

    def delete_selected_quest(self):
        """Delete the currently selected quest"""
        current_item = self.quest_tree.currentItem()
        if current_item:
            self.quest_tree.delete_quest(current_item)

    def on_language_changed(self, language):
        """Handle language change"""
        # Update UI to reflect new language - names and descriptions may need updating
        # This will be handled by refreshing the currently selected quest
        current_item = self.quest_tree.currentItem()
        if current_item:
            quest_node = current_item.data(0, Qt.ItemDataRole.UserRole)
            if quest_node:
                self.update_properties_ui(quest_node)

    def on_quests_modified(self):
        """Handle quest modifications"""
        self.update_parent_combo()
        self.quests_modified.emit()

    def generate_lua_script(self):
        """Generate Lua script for the current quest"""
        current_item = self.quest_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a quest to generate Lua script.")
            return

        quest_node = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not quest_node:
            return

        # Generate Lua script
        lua_script = self._generate_quest_lua(quest_node)

        # Show in a dialog
        dialog = QInputDialog()
        dialog.setWindowTitle("Generated Lua Script")
        dialog.setLabelText("Copy the Lua script below:")
        dialog.setTextValue(lua_script)
        dialog.setOption(QInputDialog.TextSelect, True)
        dialog.exec()

    def _generate_quest_lua(self, quest_node: QuestNode) -> str:
        """Generate Lua script for a quest node"""
        script = f"-- Quest: {quest_node.name}\n"
        script += f"QuestId = {quest_node.quest_id}\n\n"

        # Rewards
        if quest_node.rewards:
            script += "-- Rewards\n"
            if 'xp' in quest_node.rewards and quest_node.rewards['xp'] > 0:
                script += f"SetRewardFlagTrue('QuestRewardXP', {quest_node.rewards['xp']})\n"
            if 'items' in quest_node.rewards and quest_node.rewards['items']:
                for item_id in quest_node.rewards['items']:
                    script += f"SetRewardFlagTrue('QuestRewardItem', {item_id})\n"
            if 'gold' in quest_node.rewards and quest_node.rewards['gold'] > 0:
                script += f"SetRewardFlagTrue('QuestRewardGold', {quest_node.rewards['gold']})\n"
            if 'silver' in quest_node.rewards and quest_node.rewards['silver'] > 0:
                script += f"SetRewardFlagTrue('QuestRewardSilver', {quest_node.rewards['silver']})\n"
            if 'copper' in quest_node.rewards and quest_node.rewards['copper'] > 0:
                script += f"SetRewardFlagTrue('QuestRewardCopper', {quest_node.rewards['copper']})\n"
            script += "\n"

        # Requirements
        if quest_node.requirements:
            script += "-- Requirements\n"
            for req in quest_node.requirements:
                script += f"-- Requirement: {req.get('condition', '')}\n"
            script += "\n"

        # Dialogs
        if quest_node.dialog_nodes:
            script += "-- Dialogs\n"
            for dialog in quest_node.dialog_nodes:
                script += f"-- Dialog: {dialog.dialogue_name}\n"
                script += f"-- Text: {dialog.text}\n"
                script += f"-- Speaker: {dialog.speaker}\n"
                if dialog.children:
                    script += f"-- Branches: {len(dialog.children)}\n"
                script += "\n"

        return script

    def add_requirement(self):
        """Add a new requirement"""
        current_item = self.quest_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a quest to add a requirement.")
            return

        quest_node = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not quest_node:
            return

        # Simple requirement input
        condition, ok = QInputDialog.getText(
            self, "Add Requirement",
            "Enter requirement condition (e.g., 'PlayerHasItem{ItemId = 100}'):"
        )

        if ok and condition:
            quest_node.requirements.append({"condition": condition})
            self.requirements_list.addItem(condition)
            self.on_quests_modified()

    def remove_requirement(self):
        """Remove selected requirement"""
        current_item = self.requirements_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a requirement to remove.")
            return

        current_item = self.quest_tree.currentItem()
        if not current_item:
            return

        quest_node = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not quest_node:
            return

        row = self.requirements_list.currentRow()
        if row >= 0:
            del quest_node.requirements[row]
            self.requirements_list.takeItem(row)
            self.on_quests_modified()