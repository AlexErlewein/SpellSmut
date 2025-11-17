"""
Enhanced NPC Browser - Browse, search, and manage NPCs
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLineEdit, QLabel, QGroupBox, QTextEdit,
    QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt
from typing import Dict, Any, Optional

from ..exporters.npc_loader import NpcLoader
from ..models.npc_creation_data import NpcCreationData


class EnhancedNpcBrowser(QDialog):
    """Enhanced NPC browser with search and filtering"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("NPC Browser")
        self.setMinimumSize(900, 600)

        # Data structures
        self.npc_data = {}  # Dictionary indexed by npc_id
        self.selected_npc = None
        self.selected_npc_id = None

        # Initialize UI
        self.init_ui()

        # Load NPCs
        self.load_npcs()
        self.populate_npc_tree()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type to search NPCs by name, type, or class...")
        self.search_edit.textChanged.connect(self.filter_npcs)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)

        # Main content area (split between tree and details)
        content_layout = QHBoxLayout()

        # Left side: NPC tree
        tree_group = QGroupBox("NPCs")
        tree_layout = QVBoxLayout()

        self.npc_tree = QTreeWidget()
        self.npc_tree.setHeaderLabels(["Name", "Type", "Class", "Level", "ID"])
        self.npc_tree.setColumnWidth(0, 200)
        self.npc_tree.setColumnWidth(1, 100)
        self.npc_tree.setColumnWidth(2, 100)
        self.npc_tree.setColumnWidth(3, 60)
        self.npc_tree.setColumnWidth(4, 80)
        self.npc_tree.itemSelectionChanged.connect(self.on_npc_selected)
        self.npc_tree.itemDoubleClicked.connect(self.on_npc_double_clicked)
        tree_layout.addWidget(self.npc_tree)

        # NPC count label
        self.count_label = QLabel("NPCs: 0")
        tree_layout.addWidget(self.count_label)

        tree_group.setLayout(tree_layout)
        content_layout.addWidget(tree_group, 2)

        # Right side: NPC details
        details_group = QGroupBox("NPC Details")
        details_layout = QVBoxLayout()

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("Select an NPC to view details...")
        details_layout.addWidget(self.details_text)

        details_group.setLayout(details_layout)
        content_layout.addWidget(details_group, 1)

        layout.addLayout(content_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        self.create_btn = QPushButton("Create New NPC")
        self.create_btn.clicked.connect(self.create_npc)
        button_layout.addWidget(self.create_btn)

        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.edit_npc)
        button_layout.addWidget(self.edit_btn)

        self.duplicate_btn = QPushButton("Duplicate Selected")
        self.duplicate_btn.setEnabled(False)
        self.duplicate_btn.clicked.connect(self.duplicate_npc)
        button_layout.addWidget(self.duplicate_btn)

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_npc)
        button_layout.addWidget(self.delete_btn)

        button_layout.addStretch()

        self.select_btn = QPushButton("Select && Close")
        self.select_btn.setEnabled(False)
        self.select_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.select_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_npcs(self):
        """Load NPCs from JSON file"""
        try:
            self.npc_data = NpcLoader.load_all_npcs()
            print(f"Loaded {len(self.npc_data)} NPCs")

            # Show info message if no NPCs found
            if not self.npc_data:
                print("No NPCs found - database is empty")

        except Exception as e:
            print(f"Error loading NPCs: {e}")
            QMessageBox.warning(
                self,
                "Loading Error",
                f"Failed to load NPCs: {e}"
            )

    def populate_npc_tree(self):
        """Populate the NPC tree with all NPCs grouped by type"""
        self.npc_tree.clear()

        # If no NPCs, show helpful message
        if not self.npc_data:
            placeholder_item = QTreeWidgetItem(
                self.npc_tree,
                ["No NPCs found", "", "", "", ""]
            )
            placeholder_item.setForeground(0, Qt.GlobalColor.gray)

            help_item = QTreeWidgetItem(
                self.npc_tree,
                ["Click 'Create New NPC' to get started!", "", "", "", ""]
            )
            help_item.setForeground(0, Qt.GlobalColor.blue)

            self.count_label.setText("NPCs: 0")
            return

        # Group NPCs by type
        npcs_by_type = {
            "friendly": [],
            "merchant": [],
            "guard": [],
            "hostile": []
        }

        for npc_id, npc_info in self.npc_data.items():
            npc_type = npc_info.get("npc_type", "friendly").lower()
            if npc_type in npcs_by_type:
                npcs_by_type[npc_type].append((npc_id, npc_info))

        # Create category nodes
        type_labels = {
            "friendly": "Friendly NPCs",
            "merchant": "Merchants",
            "guard": "Guards",
            "hostile": "Hostile NPCs"
        }

        for npc_type, label in type_labels.items():
            if npcs_by_type[npc_type]:
                type_node = QTreeWidgetItem(
                    self.npc_tree,
                    [label, "", "", "", f"({len(npcs_by_type[npc_type])} NPCs)"]
                )
                type_node.setExpanded(True)

                # Sort NPCs by name
                npcs_by_type[npc_type].sort(key=lambda x: x[1].get("name", "Unnamed"))

                # Add NPC items under category
                for npc_id, npc_info in npcs_by_type[npc_type]:
                    name = npc_info.get("name", "Unnamed NPC")
                    title = npc_info.get("title", "")
                    if title:
                        display_name = f"{name} - {title}"
                    else:
                        display_name = name

                    character_class = npc_info.get("character_class", "warrior").capitalize()
                    level = str(npc_info.get("level", 1))

                    item = QTreeWidgetItem(
                        type_node,
                        [display_name, npc_type.capitalize(), character_class, level, str(npc_id)]
                    )
                    item.setData(0, Qt.ItemDataRole.UserRole, npc_id)

        # Update count
        self.count_label.setText(f"NPCs: {len(self.npc_data)}")

    def filter_npcs(self, search_text: str):
        """Filter NPCs based on search text"""
        search_text = search_text.lower()

        # If search is empty, show all
        if not search_text:
            for i in range(self.npc_tree.topLevelItemCount()):
                category = self.npc_tree.topLevelItem(i)
                category.setHidden(False)
                for j in range(category.childCount()):
                    category.child(j).setHidden(False)
            return

        # Filter NPCs
        visible_count = 0
        for i in range(self.npc_tree.topLevelItemCount()):
            category = self.npc_tree.topLevelItem(i)
            category_has_visible = False

            for j in range(category.childCount()):
                item = category.child(j)
                npc_id = item.data(0, Qt.ItemDataRole.UserRole)
                npc_info = self.npc_data.get(npc_id, {})

                # Search in name, type, class
                name = npc_info.get("name", "").lower()
                title = npc_info.get("title", "").lower()
                npc_type = npc_info.get("npc_type", "").lower()
                character_class = npc_info.get("character_class", "").lower()

                matches = (
                    search_text in name or
                    search_text in title or
                    search_text in npc_type or
                    search_text in character_class or
                    search_text in str(npc_id)
                )

                item.setHidden(not matches)
                if matches:
                    category_has_visible = True
                    visible_count += 1

            category.setHidden(not category_has_visible)

        self.count_label.setText(f"NPCs: {visible_count} / {len(self.npc_data)}")

    def on_npc_selected(self):
        """Handle NPC selection"""
        selected_items = self.npc_tree.selectedItems()
        if not selected_items:
            self.selected_npc = None
            self.selected_npc_id = None
            self.details_text.clear()
            self.edit_btn.setEnabled(False)
            self.duplicate_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.select_btn.setEnabled(False)
            return

        item = selected_items[0]
        npc_id = item.data(0, Qt.ItemDataRole.UserRole)

        # Skip if this is a category node
        if npc_id is None:
            return

        self.selected_npc_id = npc_id
        self.selected_npc = self.npc_data.get(npc_id)

        # Enable action buttons
        self.edit_btn.setEnabled(True)
        self.duplicate_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.select_btn.setEnabled(True)

        # Display NPC details
        self.display_npc_details(self.selected_npc)

    def display_npc_details(self, npc_info: Dict[str, Any]):
        """Display detailed information about selected NPC"""
        if not npc_info:
            return

        details = f"<h2>{npc_info.get('name', 'Unnamed NPC')}</h2>"

        if npc_info.get('title'):
            details += f"<p><b>Title:</b> {npc_info['title']}</p>"

        details += f"<p><b>ID:</b> {npc_info.get('npc_id', 'Unknown')}</p>"
        details += f"<p><b>Type:</b> {npc_info.get('npc_type', 'unknown').capitalize()}</p>"
        details += f"<p><b>Class:</b> {npc_info.get('character_class', 'unknown').capitalize()}</p>"
        details += f"<p><b>Level:</b> {npc_info.get('level', 1)}</p>"

        if npc_info.get('description'):
            details += f"<p><b>Description:</b><br>{npc_info['description']}</p>"

        # Base stats
        base_stats = npc_info.get('base_stats', {})
        if base_stats:
            details += "<h3>Base Stats</h3><ul>"
            details += f"<li>STR: {base_stats.get('strength', 0)}</li>"
            details += f"<li>STA: {base_stats.get('stamina', 0)}</li>"
            details += f"<li>AGI: {base_stats.get('agility', 0)}</li>"
            details += f"<li>DEX: {base_stats.get('dexterity', 0)}</li>"
            details += f"<li>INT: {base_stats.get('intelligence', 0)}</li>"
            details += f"<li>WIS: {base_stats.get('wisdom', 0)}</li>"
            details += f"<li>CHA: {base_stats.get('charisma', 0)}</li>"
            details += "</ul>"

        # Combat stats
        combat_stats = npc_info.get('derived_stats', {})
        if combat_stats:
            details += "<h3>Combat Stats</h3><ul>"
            details += f"<li>Health: {combat_stats.get('health', 0)}</li>"
            details += f"<li>Mana: {combat_stats.get('mana', 0)}</li>"
            details += f"<li>Melee Attack: {combat_stats.get('melee_attack', 0)}</li>"
            details += f"<li>Physical Defense: {combat_stats.get('physical_defense', 0)}</li>"
            details += "</ul>"

        # Equipment
        equipment = npc_info.get('equipment', {})
        if equipment and any(equipment.values()):
            details += "<h3>Equipment</h3><ul>"
            if equipment.get('helmet_item_id'):
                details += f"<li>Helmet: {equipment['helmet_item_id']}</li>"
            if equipment.get('chest_item_id'):
                details += f"<li>Chest: {equipment['chest_item_id']}</li>"
            if equipment.get('legs_item_id'):
                details += f"<li>Legs: {equipment['legs_item_id']}</li>"
            if equipment.get('right_hand_item_id'):
                details += f"<li>Right Hand: {equipment['right_hand_item_id']}</li>"
            if equipment.get('left_hand_item_id'):
                details += f"<li>Left Hand: {equipment['left_hand_item_id']}</li>"
            details += "</ul>"

        self.details_text.setHtml(details)

    def on_npc_double_clicked(self, item, column):
        """Handle double-click on NPC (same as selecting and clicking OK)"""
        npc_id = item.data(0, Qt.ItemDataRole.UserRole)
        if npc_id is not None:
            self.accept()

    def create_npc(self):
        """Create a new NPC"""
        from ..shared.id_manager import IDManager
        from .npc_creator_wizard import NpcCreatorWizard

        id_manager = IDManager()
        wizard = NpcCreatorWizard(id_manager, self)

        if wizard.exec() == QDialog.DialogCode.Accepted:
            # Reload NPCs
            self.load_npcs()
            self.populate_npc_tree()

    def edit_npc(self):
        """Edit the selected NPC"""
        if not self.selected_npc_id:
            return

        from ..shared.id_manager import IDManager
        from .npc_creator_wizard import NpcCreatorWizard

        id_manager = IDManager()
        wizard = NpcCreatorWizard(id_manager, self)

        # Set to edit mode and load selected NPC
        mode_page = wizard.page(0)
        mode_page.edit_radio.setChecked(True)
        wizard.source_npc = NpcCreationData.from_dict(self.selected_npc)
        wizard.npc_id = self.selected_npc_id

        if wizard.exec() == QDialog.DialogCode.Accepted:
            # Reload NPCs
            self.load_npcs()
            self.populate_npc_tree()

    def duplicate_npc(self):
        """Duplicate the selected NPC"""
        if not self.selected_npc_id:
            return

        from ..shared.id_manager import IDManager
        from .npc_creator_wizard import NpcCreatorWizard

        id_manager = IDManager()
        wizard = NpcCreatorWizard(id_manager, self)

        # Set to duplicate mode and load selected NPC
        mode_page = wizard.page(0)
        mode_page.duplicate_radio.setChecked(True)
        wizard.source_npc = NpcCreationData.from_dict(self.selected_npc)

        if wizard.exec() == QDialog.DialogCode.Accepted:
            # Reload NPCs
            self.load_npcs()
            self.populate_npc_tree()

    def delete_npc(self):
        """Delete the selected NPC"""
        if not self.selected_npc_id:
            return

        npc_name = self.selected_npc.get('name', 'Unnamed NPC')

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete '{npc_name}' (ID: {self.selected_npc_id})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if NpcLoader.delete_npc(self.selected_npc_id):
                QMessageBox.information(self, "Success", f"NPC '{npc_name}' deleted successfully!")
                self.load_npcs()
                self.populate_npc_tree()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete NPC '{npc_name}'")

    def get_selected_npc_data(self) -> Optional[NpcCreationData]:
        """Get the selected NPC as NpcCreationData object"""
        if self.selected_npc:
            return NpcCreationData.from_dict(self.selected_npc)
        return None

    def get_selected_npc_id(self) -> Optional[int]:
        """Get the selected NPC ID"""
        return self.selected_npc_id
