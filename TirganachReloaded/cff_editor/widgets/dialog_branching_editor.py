"""
Dialog Branching Editor Widget
Interactive editor for quest dialog trees with branching conversations
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QTreeWidget, QTreeWidgetItem, QPushButton,
                               QMenu, QMessageBox, QInputDialog, QSplitter,
                               QGroupBox, QTextEdit, QComboBox, QListWidget,
                               QListWidgetItem, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QAction, QIcon, QFont
from typing import Optional, List, Dict, Any, Tuple
import re


class DialogNode:
    """Data model for dialog nodes in the conversation tree"""

    def __init__(self, dialogue_name: str = "", text: str = "", speaker: str = "NPC",
                 is_player_choice: bool = False, parent_choice: Optional[str] = None):
        self.dialogue_name = dialogue_name  # e.g., "ashawe001"
        self.text = text
        self.speaker = speaker  # "NPC" or "Player"
        self.is_player_choice = is_player_choice
        self.parent_choice = parent_choice  # Which player choice leads to this
        self.children: List['DialogNode'] = []  # NPC responses or player choices
        self.order_index = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'dialogue_name': self.dialogue_name,
            'text': self.text,
            'speaker': self.speaker,
            'is_player_choice': self.is_player_choice,
            'parent_choice': self.parent_choice,
            'order_index': self.order_index,
            'children': [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogNode':
        """Create from dictionary"""
        node = cls(
            dialogue_name=data.get('dialogue_name', ''),
            text=data.get('text', ''),
            speaker=data.get('speaker', 'NPC'),
            is_player_choice=data.get('is_player_choice', False),
            parent_choice=data.get('parent_choice')
        )
        node.order_index = data.get('order_index', 0)
        node.children = [cls.from_dict(child) for child in data.get('children', [])]
        return node

    def add_child(self, child: 'DialogNode'):
        """Add a child node"""
        self.children.append(child)
        self.children.sort(key=lambda x: x.order_index)

    def remove_child(self, child: 'DialogNode'):
        """Remove a child node"""
        if child in self.children:
            self.children.remove(child)

    def get_all_nodes(self) -> List['DialogNode']:
        """Get all nodes in the tree recursively"""
        nodes = [self]
        for child in self.children:
            nodes.extend(child.get_all_nodes())
        return nodes

    def get_next_dialogue_name(self, base_name: str) -> str:
        """Get next available dialogue name in sequence"""
        # Extract base and number from current name
        match = re.match(r'(.+?)(\d+)$', self.dialogue_name)
        if match:
            base, num = match.groups()
            next_num = int(num) + 1
            return f"{base}{next_num:03d}"
        else:
            # If no number, start with 001
            return f"{base_name}001"


class DialogTreeWidget(QTreeWidget):
    """Interactive tree widget for dialog branching"""

    dialog_selected = Signal(object)  # DialogNode
    dialog_modified = Signal()  # Emitted when tree structure changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the tree widget UI"""
        self.setHeaderLabels(["Speaker", "Dialog Name", "Text Preview"])
        self.setAlternatingRowColors(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        # Set column widths
        self.setColumnWidth(0, 80)   # Speaker
        self.setColumnWidth(1, 120)  # Dialog Name
        self.setColumnWidth(2, 300)  # Text Preview

    def setup_connections(self):
        """Setup signal connections"""
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemChanged.connect(self.on_item_changed)

    def load_dialog_tree(self, root_nodes: List[DialogNode]):
        """Load dialog tree into the widget"""
        self.clear()

        for root_node in sorted(root_nodes, key=lambda x: x.order_index):
            root_item = self.create_tree_item(root_node)
            self.addTopLevelItem(root_item)
            self.populate_children(root_item, root_node)

        self.expandAll()

    def create_tree_item(self, dialog_node: DialogNode) -> QTreeWidgetItem:
        """Create a tree item for a dialog node"""
        item = QTreeWidgetItem()

        # Speaker
        speaker = "Player" if dialog_node.is_player_choice else dialog_node.speaker
        item.setText(0, speaker)

        # Dialog name
        item.setText(1, dialog_node.dialogue_name or "New Dialog")

        # Text preview (truncated)
        preview = dialog_node.text[:50] + "..." if dialog_node.text and len(dialog_node.text) > 50 else dialog_node.text or "No text"
        item.setText(2, preview)

        # Set font and color based on type
        font = item.font(0)
        if dialog_node.is_player_choice:
            font.setItalic(True)
            item.setForeground(0, Qt.blue)
            item.setForeground(1, Qt.blue)
            item.setForeground(2, Qt.blue)
        else:
            font.setBold(True)
            item.setForeground(0, Qt.darkGreen)

        for col in range(3):
            item.setFont(col, font)

        # Make editable
        item.setFlags(item.flags() | Qt.ItemIsEditable)

        # Store reference
        item.setData(0, Qt.UserRole, dialog_node)

        return item

    def populate_children(self, parent_item: QTreeWidgetItem, parent_node: DialogNode):
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
        dialog_node = item.data(0, Qt.UserRole)

        # Add dialog actions
        add_npc_response_action = QAction("Add NPC Response", self)
        add_npc_response_action.triggered.connect(lambda: self.add_dialog_response(item, "NPC"))
        menu.addAction(add_npc_response_action)

        add_player_choice_action = QAction("Add Player Choice", self)
        add_player_choice_action.triggered.connect(lambda: self.add_dialog_response(item, "Player"))
        menu.addAction(add_player_choice_action)

        menu.addSeparator()

        # Edit actions
        edit_text_action = QAction("Edit Dialog Text", self)
        edit_text_action.triggered.connect(lambda: self.edit_dialog_text(item))
        menu.addAction(edit_text_action)

        menu.addSeparator()

        # Delete action
        delete_action = QAction("Delete Dialog", self)
        delete_action.triggered.connect(lambda: self.delete_dialog(item))
        menu.addAction(delete_action)

        menu.exec(self.mapToGlobal(position))

    def add_dialog_response(self, parent_item: QTreeWidgetItem, speaker_type: str):
        """Add a dialog response"""
        parent_node = parent_item.data(0, Qt.UserRole)
        if not parent_node:
            return

        # Determine if this is a player choice or NPC response
        is_player_choice = (speaker_type == "Player")

        # Generate dialogue name
        base_name = self.extract_base_name(parent_node.dialogue_name)
        next_name = parent_node.get_next_dialogue_name(base_name)

        # Create new dialog node
        new_dialog = DialogNode(
            dialogue_name=next_name,
            text=f"New {speaker_type.lower()} dialog text...",
            speaker=speaker_type,
            is_player_choice=is_player_choice
        )

        # Add as child
        parent_node.add_child(new_dialog)

        # Add to tree
        child_item = self.create_tree_item(new_dialog)
        parent_item.addChild(child_item)
        parent_item.setExpanded(True)

        self.dialog_modified.emit()

    def extract_base_name(self, dialogue_name: str) -> str:
        """Extract base name from dialogue name (remove numbers)"""
        match = re.match(r'(.+?)\d*$', dialogue_name)
        return match.group(1) if match else dialogue_name

    def edit_dialog_text(self, item: QTreeWidgetItem):
        """Edit dialog text"""
        dialog_node = item.data(0, Qt.UserRole)
        if not dialog_node:
            return

        # Open text edit dialog
        text, ok = QInputDialog.getMultiLineText(
            self, "Edit Dialog Text",
            "Dialog text:",
            dialog_node.text
        )

        if ok and text != dialog_node.text:
            dialog_node.text = text
            # Update tree display
            preview = text[:50] + "..." if len(text) > 50 else text
            item.setText(2, preview)
            self.dialog_modified.emit()

    def delete_dialog(self, item: QTreeWidgetItem):
        """Delete a dialog"""
        dialog_node = item.data(0, Qt.UserRole)
        if not dialog_node:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Dialog",
            f"Are you sure you want to delete dialog '{dialog_node.dialogue_name}' and all its branches?",
            QMessageBox.Yes, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Remove from parent
            parent = item.parent()
            if parent:
                parent_node = parent.data(0, Qt.UserRole)
                parent_node.remove_child(dialog_node)
                parent.removeChild(item)
            else:
                # Root level dialog
                index = self.indexOfTopLevelItem(item)
                if index >= 0:
                    self.takeTopLevelItem(index)

            self.dialog_modified.emit()

    def on_selection_changed(self):
        """Handle item selection change"""
        current_item = self.currentItem()
        if current_item:
            dialog_node = current_item.data(0, Qt.UserRole)
            if dialog_node:
                self.dialog_selected.emit(dialog_node)

    def on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handle item text changes"""
        dialog_node = item.data(0, Qt.UserRole)
        if not dialog_node:
            return

        if column == 1:  # Dialog name column
            new_name = item.text(1)
            dialog_node.dialogue_name = new_name
            self.dialog_modified.emit()

    def get_root_dialogs(self) -> List[DialogNode]:
        """Get all root dialog nodes"""
        root_dialogs = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            node = item.data(0, Qt.UserRole)
            if node:
                root_dialogs.append(node)
        return root_dialogs


class DialogBranchingEditorWidget(QWidget):
    """Main dialog branching editor widget"""

    dialog_selected = Signal(object)  # DialogNode
    dialogs_modified = Signal()  # Emitted when dialogs are modified

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.current_dialog_nodes: List[DialogNode] = []

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the main UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title_label = QLabel("Dialog Branching Editor")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        self.add_root_dialog_btn = QPushButton("Add Root Dialog")
        self.add_root_dialog_btn.setToolTip("Add a new root-level NPC dialog")
        toolbar_layout.addWidget(self.add_root_dialog_btn)

        self.load_from_quest_btn = QPushButton("Load from Quest")
        self.load_from_quest_btn.setToolTip("Load dialogs related to selected quest")
        toolbar_layout.addWidget(self.load_from_quest_btn)

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setToolTip("Save dialog tree changes")
        toolbar_layout.addWidget(self.save_btn)

        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left side - Dialog tree
        tree_group = QGroupBox("Dialog Tree")
        tree_layout = QVBoxLayout(tree_group)

        self.dialog_tree = DialogTreeWidget()
        tree_layout.addWidget(self.dialog_tree)

        splitter.addWidget(tree_group)

        # Right side - Dialog properties and preview
        properties_group = QGroupBox("Dialog Properties")
        properties_layout = QVBoxLayout(properties_group)

        self.setup_properties_ui(properties_layout)

        splitter.addWidget(properties_group)

        # Set splitter proportions
        splitter.setSizes([400, 300])

        layout.addWidget(splitter)

    def setup_properties_ui(self, layout):
        """Setup the dialog properties UI"""
        # Dialog name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Dialog Name:"))
        self.dialog_name_edit = QLineEdit()
        self.dialog_name_edit.setReadOnly(True)  # Auto-generated
        name_layout.addWidget(self.dialog_name_edit)
        layout.addLayout(name_layout)

        # Speaker type
        speaker_layout = QHBoxLayout()
        speaker_layout.addWidget(QLabel("Speaker:"))
        self.speaker_combo = QComboBox()
        self.speaker_combo.addItems(["NPC", "Player"])
        speaker_layout.addWidget(self.speaker_combo)
        layout.addLayout(speaker_layout)

        # Dialog text
        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel("Dialog Text:"))
        self.dialog_text_edit = QTextEdit()
        self.dialog_text_edit.setMaximumHeight(150)
        text_layout.addWidget(self.dialog_text_edit)
        layout.addLayout(text_layout)

        # Preview section
        preview_group = QGroupBox("Conversation Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.conversation_preview = QTextEdit()
        self.conversation_preview.setReadOnly(True)
        self.conversation_preview.setMaximumHeight(200)
        preview_layout.addWidget(self.conversation_preview)

        layout.addWidget(preview_group)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.update_btn = QPushButton("Update Dialog")
        self.update_btn.setToolTip("Update dialog properties")
        buttons_layout.addWidget(self.update_btn)

        self.delete_btn = QPushButton("Delete Dialog")
        self.delete_btn.setToolTip("Delete this dialog and all branches")
        buttons_layout.addWidget(self.delete_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    def setup_connections(self):
        """Setup signal connections"""
        self.add_root_dialog_btn.clicked.connect(self.add_root_dialog)
        self.load_from_quest_btn.clicked.connect(self.load_from_selected_quest)
        self.save_btn.clicked.connect(self.save_dialogs)

        self.dialog_tree.dialog_selected.connect(self.on_dialog_selected)
        self.dialog_tree.dialog_modified.connect(self.on_dialogs_modified)

        self.update_btn.clicked.connect(self.update_dialog_properties)
        self.delete_btn.clicked.connect(self.delete_selected_dialog)

        self.speaker_combo.currentTextChanged.connect(self.on_speaker_changed)
        self.dialog_text_edit.textChanged.connect(self.update_preview)

    def add_root_dialog(self):
        """Add a new root-level dialog"""
        # Get base name from user
        base_name, ok = QInputDialog.getText(
            self, "New Root Dialog",
            "Enter base name for the dialog sequence (e.g., 'myquest'):"
        )

        if ok and base_name:
            # Create root NPC dialog
            root_dialog = DialogNode(
                dialogue_name=f"{base_name}001",
                text="Hello, adventurer! How can I help you?",
                speaker="NPC",
                is_player_choice=False
            )

            # Add to tree
            self.current_dialog_nodes.append(root_dialog)
            self.dialog_tree.load_dialog_tree(self.current_dialog_nodes)

            self.on_dialogs_modified()

    def load_from_selected_quest(self):
        """Load dialogs related to the currently selected quest"""
        # This would need integration with the quest selection system
        # For now, show a placeholder
        QMessageBox.information(
            self, "Load from Quest",
            "This feature will load dialogs associated with the currently selected quest.\n\n"
            "Integration with quest selection system needed."
        )

    def save_dialogs(self):
        """Save dialog tree changes"""
        if not self.data_model.game_data:
            QMessageBox.warning(self, "No Data", "No CFF file is loaded.")
            return

        try:
            # Get all dialog nodes
            all_nodes = []
            for root_node in self.current_dialog_nodes:
                all_nodes.extend(root_node.get_all_nodes())

            # Validate dialog data
            if not self.validate_dialogs(all_nodes):
                return

            # Apply changes to localisation table
            self.apply_dialog_changes(all_nodes)

            # Mark data as modified
            self.data_model.modified = True
            self.data_model.data_modified.emit()

            QMessageBox.information(self, "Success", f"Saved {len(all_nodes)} dialog entries.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save dialogs: {str(e)}")

    def validate_dialogs(self, dialog_nodes: List[DialogNode]) -> bool:
        """Validate dialog data before saving"""
        errors = []

        # Check for duplicate dialogue names
        names = set()
        for node in dialog_nodes:
            if node.dialogue_name in names:
                errors.append(f"Duplicate dialogue name: {node.dialogue_name}")
            names.add(node.dialogue_name)

        # Check for empty text
        for node in dialog_nodes:
            if not node.text or node.text.strip() == "":
                errors.append(f"Dialog {node.dialogue_name} has no text")

        # Check for invalid dialogue names
        for node in dialog_nodes:
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\d*$', node.dialogue_name):
                errors.append(f"Invalid dialogue name: {node.dialogue_name}")

        if errors:
            error_text = "\n".join(errors)
            QMessageBox.warning(self, "Validation Errors", f"Please fix the following errors:\n\n{error_text}")
            return False

        return True

    def apply_dialog_changes(self, dialog_nodes: List[DialogNode]):
        """Apply dialog changes to the localisation table"""
        # This is a placeholder implementation
        # In a full implementation, you'd need to:
        # 1. Update existing localisation entries
        # 2. Add new localisation entries
        # 3. Handle multiple languages
        # 4. Update dialogue_name and text fields

        print(f"Applying changes for {len(dialog_nodes)} dialog entries")
        # TODO: Implement actual localisation table updates

    def on_dialog_selected(self, dialog_node: DialogNode):
        """Handle dialog selection"""
        self.update_properties_ui(dialog_node)
        self.update_preview()
        self.dialog_selected.emit(dialog_node)

    def update_properties_ui(self, dialog_node: DialogNode):
        """Update the properties UI for selected dialog"""
        self.dialog_name_edit.setText(dialog_node.dialogue_name)
        self.speaker_combo.setCurrentText(dialog_node.speaker)
        self.dialog_text_edit.setPlainText(dialog_node.text)

    def update_preview(self):
        """Update the conversation preview"""
        current_node = self.dialog_tree.currentItem()
        if not current_node:
            self.conversation_preview.clear()
            return

        dialog_node = current_node.data(0, Qt.UserRole)
        if not dialog_node:
            self.conversation_preview.clear()
            return

        # Build conversation preview by walking up the tree
        conversation = self.build_conversation_preview(dialog_node)
        self.conversation_preview.setPlainText(conversation)

    def build_conversation_preview(self, dialog_node: DialogNode) -> str:
        """Build a conversation preview showing the path to this dialog"""
        lines = []

        # Walk up the tree to find the conversation path
        current = dialog_node
        path = []

        # Build path from root to current node
        while current:
            path.insert(0, current)
            # Find parent (this is simplified - in reality you'd need to track parent relationships)
            current = None  # TODO: Implement proper parent tracking

        # Format conversation
        for node in path:
            speaker = "Player" if node.is_player_choice else node.speaker
            lines.append(f"{speaker}: {node.text}")

        return "\n\n".join(lines)

    def on_speaker_changed(self, speaker: str):
        """Handle speaker type change"""
        current_item = self.dialog_tree.currentItem()
        if current_item:
            dialog_node = current_item.data(0, Qt.UserRole)
            if dialog_node:
                dialog_node.speaker = speaker
                dialog_node.is_player_choice = (speaker == "Player")
                # Update tree display
                current_item.setText(0, speaker)
                self.on_dialogs_modified()

    def update_dialog_properties(self):
        """Update dialog properties from UI"""
        current_item = self.dialog_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a dialog to update.")
            return

        dialog_node = current_item.data(0, Qt.UserRole)
        if not dialog_node:
            return

        # Update properties
        dialog_node.speaker = self.speaker_combo.currentText()
        dialog_node.is_player_choice = (dialog_node.speaker == "Player")
        dialog_node.text = self.dialog_text_edit.toPlainText()

        # Update tree display
        current_item.setText(0, dialog_node.speaker)
        preview = dialog_node.text[:50] + "..." if len(dialog_node.text) > 50 else dialog_node.text
        current_item.setText(2, preview)

        self.on_dialogs_modified()

    def delete_selected_dialog(self):
        """Delete the currently selected dialog"""
        current_item = self.dialog_tree.currentItem()
        if current_item:
            self.dialog_tree.delete_dialog(current_item)

    def on_dialogs_modified(self):
        """Handle dialog modifications"""
        self.update_preview()
        self.dialogs_modified.emit()