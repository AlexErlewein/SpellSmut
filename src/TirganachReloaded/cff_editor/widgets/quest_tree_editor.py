"""
Quest Tree Editor Widget
Interactive hierarchical quest tree view with drag-drop editing capabilities
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QTreeWidget, QTreeWidgetItem, QPushButton,
                               QMenu, QMessageBox, QInputDialog, QSplitter,
                               QGroupBox, QTextEdit, QLineEdit, QComboBox)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QAction, QIcon
from typing import Optional, List, Dict, Any
import json


class QuestNode:
    """Data model for quest nodes in the tree"""

    def __init__(self, quest_id: Optional[int] = None, name: str = "", description: str = "",
                 parent_id: Optional[int] = None, order_index: int = 0, is_new: bool = False):
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.order_index = order_index
        self.is_new = is_new  # Flag for newly created quests
        self.children: List['QuestNode'] = []
        self.original_data: Dict[str, Any] = {}  # Store original quest data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'quest_id': self.quest_id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'order_index': self.order_index,
            'is_new': self.is_new,
            'children': [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestNode':
        """Create from dictionary"""
        node = cls(
            quest_id=data.get('quest_id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            parent_id=data.get('parent_id'),
            order_index=data.get('order_index', 0),
            is_new=data.get('is_new', False)
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
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

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
        item.setFlags(item.flags() | Qt.ItemIsEditable)

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
        item.setData(0, Qt.UserRole, quest_node)

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
            parent_node = parent_item.data(0, Qt.UserRole)
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
        quest_node = item.data(0, Qt.UserRole)
        if not quest_node:
            return

        # For now, just make the name editable (already is)
        self.editItem(item, 0)

    def delete_quest(self, item: QTreeWidgetItem):
        """Delete a quest"""
        quest_node = item.data(0, Qt.UserRole)
        if not quest_node:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Quest",
            f"Are you sure you want to delete quest '{quest_node.name}' and all its subquests?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Remove from parent
            parent = item.parent()
            if parent:
                parent_node = parent.data(0, Qt.UserRole)
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
            root_node = root_item.data(0, Qt.UserRole)
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
            quest_node = current_item.data(0, Qt.UserRole)
            if quest_node:
                self.quest_selected.emit(quest_node)

    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handle item text changes"""
        if column == 0:  # Name column
            quest_node = item.data(0, Qt.UserRole)
            if quest_node:
                new_name = item.text(0)
                quest_node.name = new_name
                self.quest_modified.emit()

    def get_root_quests(self) -> List[QuestNode]:
        """Get all root quest nodes"""
        root_quests = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            node = item.data(0, Qt.UserRole)
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
        splitter = QSplitter(Qt.Horizontal)

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
        """Setup the quest properties UI"""
        # Quest ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Quest ID:"))
        self.quest_id_edit = QLineEdit()
        self.quest_id_edit.setReadOnly(True)  # IDs are auto-generated
        id_layout.addWidget(self.quest_id_edit)
        layout.addLayout(id_layout)

        # Quest Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.quest_name_edit = QLineEdit()
        name_layout.addWidget(self.quest_name_edit)
        layout.addLayout(name_layout)

        # Description
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        desc_layout.addWidget(self.description_edit)
        layout.addLayout(desc_layout)

        # Parent quest selector
        parent_layout = QHBoxLayout()
        parent_layout.addWidget(QLabel("Parent Quest:"))
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("None (Main Quest)", None)
        parent_layout.addWidget(self.parent_combo)
        layout.addLayout(parent_layout)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.update_btn = QPushButton("Update Quest")
        self.update_btn.setToolTip("Update quest properties")
        buttons_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Delete Quest")
        self.delete_btn.setToolTip("Delete this quest and all subquests")
        buttons_layout.addWidget(self.delete_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    def setup_connections(self):
        """Setup signal connections"""
        self.add_main_quest_btn.clicked.connect(lambda: self.quest_tree.add_quest())
        self.save_btn.clicked.connect(self.save_quests)
        self.load_btn.clicked.connect(self.load_quests)

        self.quest_tree.quest_selected.connect(self.on_quest_selected)
        self.quest_tree.quest_modified.connect(self.on_quests_modified)

        self.update_btn.clicked.connect(self.update_quest_properties)
        self.delete_btn.clicked.connect(self.delete_selected_quest)

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

    def update_quest_properties(self):
        """Update quest properties from UI"""
        current_item = self.quest_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a quest to update.")
            return

        quest_node = current_item.data(0, Qt.UserRole)
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

        # Update tree display
        current_item.setText(0, quest_node.name or f"Quest {quest_node.quest_id}")

        self.on_quests_modified()

    def delete_selected_quest(self):
        """Delete the currently selected quest"""
        current_item = self.quest_tree.currentItem()
        if current_item:
            self.quest_tree.delete_quest(current_item)

    def on_quests_modified(self):
        """Handle quest modifications"""
        self.update_parent_combo()
        self.quests_modified.emit()