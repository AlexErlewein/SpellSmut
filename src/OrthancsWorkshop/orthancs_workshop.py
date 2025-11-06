#!/usr/bin/env python3
"""
Orthanc's Workshop - Weapon & Armor Browser and Creation Suite
================================================================

A comprehensive application for browsing and creating SpellForce weapons and armor.
Features enhanced UI/UX, integrated creation wizards, and detailed item inspection.

Usage:
    python orthancs_workshop.py [--debug] [--rebuild-cache]

Author: TirganachReloaded Modding Tools
"""

import argparse
import sys
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.logging_config import configure_logging, get_logger
from TirganachReloaded.cff_editor.shared.id_manager import IDManager
from TirganachReloaded.cff_editor.widgets.armor_forge_wizard import ArmorForgeWizard
from TirganachReloaded.cff_editor.widgets.weapon_forge_wizard import WeaponForgeWizard


class OrthancsWorkshop(QMainWindow):
    """Main application window for Orthanc's Workshop"""

    def __init__(self):
        super().__init__()
        self.logger = None
        self.id_manager = None
        self.weapon_data = {}
        self.armor_data = {}

        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the enhanced user interface"""
        self.setWindowTitle("Orthanc's Workshop - Weapon & Armor Suite")
        self.setMinimumSize(QSize(1600, 1000))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Header with enhanced controls
        header_layout = QHBoxLayout()
        title_label = QLabel("Orthanc's Workshop")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #6fb3d2;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Mode selector
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Weapons", "Armor"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        header_layout.addWidget(QLabel("Mode:"))
        header_layout.addWidget(self.mode_combo)

        # Enhanced buttons
        create_weapon_btn = QPushButton("Forge Weapon")
        create_weapon_btn.clicked.connect(self.create_weapon)
        create_weapon_btn.setStyleSheet(
            "QPushButton { background-color: #3c3c3c; color: #e0e0e0; font-weight: bold; padding: 8px; border-radius: 4px; border: 1px solid #555; } QPushButton:hover { background-color: #4a4a4a; }"
        )
        header_layout.addWidget(create_weapon_btn)

        create_armor_btn = QPushButton("Forge Armor")
        create_armor_btn.clicked.connect(self.create_armor)
        create_armor_btn.setStyleSheet(
            "QPushButton { background-color: #3c3c3c; color: #e0e0e0; font-weight: bold; padding: 8px; border-radius: 4px; border: 1px solid #555; } QPushButton:hover { background-color: #4a4a4a; }"
        )
        header_layout.addWidget(create_armor_btn)

        reload_btn = QPushButton("Reload Data")
        reload_btn.clicked.connect(self.reload_data)
        header_layout.addWidget(reload_btn)

        layout.addLayout(header_layout)

        # Main splitter with better proportions
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left side - Item tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.tree_group = QGroupBox("Weapons (Loading...)")
        tree_layout = QVBoxLayout(self.tree_group)

        self.item_tree = QTreeWidget()
        self.item_tree.setHeaderLabels(["Item", "Type", "ID"])
        self.item_tree.itemSelectionChanged.connect(self.on_item_selection_changed)

        # Dark theme tree styling
        self.item_tree.setStyleSheet("""
            QTreeWidget {
                font-size: 12px;
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3c3c3c;
                alternate-background-color: #252525;
            }
            QTreeWidget::item {
                padding: 3px;
                border-bottom: 1px solid #2d2d30;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
                color: #e0e0e0;
            }
            QTreeWidget::item:hover {
                background-color: #2d2d30;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #3c3c3c;
                font-weight: bold;
            }
        """)

        tree_layout.addWidget(self.item_tree)

        # Enhanced tree controls
        tree_controls = QHBoxLayout()
        expand_btn = QPushButton("Expand All")
        expand_btn.clicked.connect(self.item_tree.expandAll)
        expand_btn.setStyleSheet("QPushButton { padding: 6px; }")
        collapse_btn = QPushButton("Collapse All")
        collapse_btn.clicked.connect(self.item_tree.collapseAll)
        collapse_btn.setStyleSheet("QPushButton { padding: 6px; }")
        tree_controls.addWidget(expand_btn)
        tree_controls.addWidget(collapse_btn)
        tree_controls.addStretch()

        # Add item count label
        self.item_count_label = QLabel("Loading...")
        tree_controls.addWidget(self.item_count_label)

        tree_layout.addLayout(tree_controls)

        left_layout.addWidget(self.tree_group)
        splitter.addWidget(left_widget)

        # Right side - Item details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        details_group = QGroupBox("Item Details")
        details_layout = QVBoxLayout(details_group)

        # Create scroll area for details
        self.details_scroll_area = QScrollArea()
        self.details_scroll_area.setWidgetResizable(True)
        self.details_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # Create content widget for details
        self.details_content = QWidget()
        self.details_content_layout = QVBoxLayout(self.details_content)
        self.details_content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Set content widget in scroll area
        self.details_scroll_area.setWidget(self.details_content)

        # Add scroll area to layout
        details_layout.addWidget(self.details_scroll_area)

        right_layout.addWidget(details_group)
        splitter.addWidget(right_widget)

        # Set better splitter proportions
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([800, 800])

        # Simple status bar
        self.statusBar().showMessage("Ready - Orthanc's Workshop Loaded")

    def load_data(self):
        """Load weapon and armor data"""
        try:
            self.statusBar().showMessage("Initializing Orthanc's Workshop...")

            # Configure logging
            if not self.logger:
                configure_logging()
                self.logger = get_logger("orthancs_workshop")

            # Initialize ID manager
            if not self.id_manager:
                self.id_manager = IDManager()

            self.statusBar().showMessage("Loading weapon data...")
            self.load_weapon_data()

            self.statusBar().showMessage("Loading armor data...")
            self.load_armor_data()

            self.statusBar().showMessage("Building item trees...")
            self.populate_item_tree()

            total_items = len(self.weapon_data) + len(self.armor_data)
            self.item_count_label.setText(f"Total: {total_items} items")
            self.update_tree_title()

            self.statusBar().showMessage(
                f"✅ Loaded {total_items} items - Orthanc's Workshop Ready"
            )

        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to load item data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load item data:\n{e}")
            self.statusBar().showMessage("❌ Failed to load data")

    def load_weapon_data(self):
        """Load weapon data directly from CFF file using CFF-based loader"""
        try:
            # Import the CFF Weapon Loader
            from cff_weapon_loader import CFFWeaponLoader

            # Initialize the loader
            loader = CFFWeaponLoader()

            # Connect loader signals if needed for progress updates
            # loader.progress_updated.connect(lambda p, msg: self.statusBar().showMessage(msg))

            # Load weapons from CFF file (with fallback to JSON)
            self.weapon_data = loader.load_all_weapons()

            if self.logger:
                self.logger.info(
                    f"✓ Loaded {len(self.weapon_data)} weapons from CFF data"
                )

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load weapon data: {e}")
                self.logger.exception(e)

    def get_armor_slot_name(self, slot_id):
        """Convert armor slot ID to human-readable name"""
        slot_names = {
            0: "Unknown",
            1: "Head",
            2: "Chest",
            3: "Shield",  # This is likely the offhand slot
            4: "Hands",
            5: "Legs",
            6: "Feet",
            7: "Cloak",
            8: "Belt",
            9: "Ring",
            10: "Amulet",
        }
        return slot_names.get(slot_id, f"Slot {slot_id}")

    def clear_details_content(self):
        """Clear all widgets in the details content area"""
        while self.details_content_layout.count():
            child = self.details_content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def load_armor_data(self):
        """Load armor data directly from CFF file using CFF-based loader"""
        try:
            # Import the CFF Armor Loader
            from cff_armor_loader import CFFArmorLoader

            # Initialize the loader
            loader = CFFArmorLoader()

            # Load armor from CFF file (with fallback to JSON)
            self.armor_data = loader.load_all_armor()

            if self.logger:
                self.logger.info(
                    f"✓ Loaded {len(self.armor_data)} armor pieces from CFF data"
                )

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load armor data: {e}")
                self.logger.exception(e)

    def populate_item_tree(self):
        """Populate the item tree with weapons and armor grouped by type"""
        self.item_tree.clear()

        if not self.weapon_data and not self.armor_data:
            if self.logger:
                self.logger.warning("No item data to populate tree")
            return

        # Create weapon items grouped by type
        if self.weapon_data:
            weapons_root = QTreeWidgetItem(self.item_tree, ["Weapons", "", ""])
            weapons_root.setFont(0, QFont("", -1, QFont.Weight.Bold))

            # Group weapons by type
            weapons_by_type = {}
            for weapon_id, weapon_info in self.weapon_data.items():
                weapon_type = weapon_info.get(
                    "weapon_type_name", weapon_info.get("item_subtype", "Unknown")
                )
                if weapon_type not in weapons_by_type:
                    weapons_by_type[weapon_type] = []
                weapons_by_type[weapon_type].append((weapon_id, weapon_info))

            # Create type category nodes
            for weapon_type in sorted(weapons_by_type.keys()):
                # Clean up the weapon type name for display
                display_type = weapon_type.replace("WeaponType ", "").replace("_", " ")
                type_node = QTreeWidgetItem(
                    weapons_root,
                    [display_type, "", f"({len(weapons_by_type[weapon_type])} items)"],
                )
                type_node.setFont(0, QFont("", -1, QFont.Weight.Bold))

                # Add weapons under this type
                for weapon_id, weapon_info in sorted(weapons_by_type[weapon_type]):
                    name = weapon_info.get(
                        "weapon_name", weapon_info.get("name", f"Weapon {weapon_id}")
                    )
                    item = QTreeWidgetItem(type_node, [name, "", str(weapon_id)])
                    item.setData(0, Qt.ItemDataRole.UserRole, ("weapon", weapon_id))

            weapons_root.setExpanded(True)

        # Create armor items grouped by slot
        if self.armor_data:
            armor_root = QTreeWidgetItem(self.item_tree, ["Armor", "", ""])
            armor_root.setFont(0, QFont("", -1, QFont.Weight.Bold))

            # Group armor by slot
            armor_by_slot = {}
            for armor_id, armor_info in self.armor_data.items():
                armor_slot = armor_info.get("slot", "Unknown")
                if armor_slot not in armor_by_slot:
                    armor_by_slot[armor_slot] = []
                armor_by_slot[armor_slot].append((armor_id, armor_info))

            # Create slot category nodes
            for armor_slot in sorted(armor_by_slot.keys()):
                slot_node = QTreeWidgetItem(
                    armor_root,
                    [armor_slot, "", f"({len(armor_by_slot[armor_slot])} items)"],
                )
                slot_node.setFont(0, QFont("", -1, QFont.Weight.Bold))

                # Add armor under this slot
                for armor_id, armor_info in sorted(armor_by_slot[armor_slot]):
                    name = armor_info.get("armor_name", f"Armor {armor_id}")
                    armor_type = armor_info.get("armor_type", "Unknown")
                    item = QTreeWidgetItem(slot_node, [name, armor_type, str(armor_id)])
                    item.setData(0, Qt.ItemDataRole.UserRole, ("armor", armor_id))

            armor_root.setExpanded(True)

        # Resize columns to fit content
        self.item_tree.resizeColumnToContents(0)
        self.item_tree.resizeColumnToContents(1)
        self.item_tree.resizeColumnToContents(2)

        if self.logger:
            self.logger.info(
                f"✓ Item tree populated: {len(self.weapon_data)} weapons, {len(self.armor_data)} armor"
            )

    def on_mode_changed(self, mode):
        """Handle mode change between weapons and armor"""
        self.update_tree_title()

    def update_tree_title(self):
        """Update the tree group title based on current mode"""
        mode = self.mode_combo.currentText()
        if mode == "Weapons":
            count = len(self.weapon_data)
            self.tree_group.setTitle(f"Weapons ({count} loaded)")
        else:
            count = len(self.armor_data)
            self.tree_group.setTitle(f"Armor ({count} loaded)")

    def on_item_selection_changed(self):
        """Handle item selection"""
        selected_items = self.item_tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        item_data = item.data(0, Qt.ItemDataRole.UserRole)

        if item_data:
            item_type, item_id = item_data
            if item_type == "weapon" and item_id in self.weapon_data:
                self.show_weapon_details(item_id)
            elif item_type == "armor" and item_id in self.armor_data:
                self.show_armor_details(item_id)

    def show_weapon_details(self, weapon_id):
        """Show detailed information for selected weapon"""
        weapon_info = self.weapon_data[weapon_id]

        # Clear previous content
        self.clear_details_content()

        # Main title
        title_label = QLabel(
            f"WEAPON ID: {weapon_id} - {weapon_info.get('weapon_name', weapon_info.get('name', 'Unknown'))}"
        )
        title_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d30;
                color: #ffffff;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_content_layout.addWidget(title_label)

        # Create a grid layout for perfect alignment
        basic_info_layout = QHBoxLayout()

        # Basic Information Section
        basic_group = QGroupBox("BASIC INFORMATION")
        basic_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #6fb3d2;
                border: 2px solid #6fb3d2;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        basic_layout = QVBoxLayout(basic_group)

        basic_info = [
            (
                "Name",
                weapon_info.get("weapon_name", weapon_info.get("name", "Unknown")),
            ),
            (
                "Type",
                weapon_info.get(
                    "weapon_type_name", weapon_info.get("item_subtype", "Unknown")
                ),
            ),
            ("Material", weapon_info.get("weapon_material_name", "Unknown")),
            ("Hands", weapon_info.get("hands", "Unknown")),
            ("Category", weapon_info.get("damage_category", "Unknown")),
        ]

        for label, value in basic_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 100px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            basic_layout.addLayout(row_layout)

        # Add basic info to the layout
        basic_info_layout.addWidget(basic_group)

        # Create icon widget with exact height matching
        icon_widget = QLabel()
        icon_widget.setText("ICON")
        icon_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_widget.setStyleSheet("""
            QLabel {
                background-color: #2d2d30;
                color: #a0a0a0;
                border: 1px dashed #6fb3d2;
                font-size: 12px;
                min-width: 120px;
                min-height: 1px;  /* Start with minimal height */
            }
        """)
        icon_widget.setFixedWidth(120)  # Fixed width for the icon space
        # Create container for icon to ensure proper vertical alignment
        icon_container = QWidget()
        icon_container.setStyleSheet("""
            QWidget {
                background-color: #2d2d30;
                border: 1px dashed #6fb3d2;
            }
        """)
        icon_container.setFixedWidth(120)  # Fixed width for the icon space

        # Create layout for the icon container to center the icon
        icon_container_layout = QVBoxLayout(icon_container)
        icon_container_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center vertically and horizontally

        # Create the icon label
        icon_label = QLabel("ICON")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                color: #a0a0a0;
                font-size: 12px;
            }
        """)

        # Add the icon label to the container's layout
        icon_container_layout.addWidget(icon_label)
        icon_container_layout.addStretch()  # Add stretch to push the icon to the center

        # Add icon container to the same layout
        basic_info_layout.addWidget(icon_container)

        # Add the layout to main content
        self.details_content_layout.addLayout(basic_info_layout)

        # Combat Statistics Section
        combat_group = QGroupBox("COMBAT STATISTICS")
        combat_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #76b36f;
                border: 2px solid #76b36f;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        combat_layout = QVBoxLayout(combat_group)

        combat_info = [
            (
                "Damage",
                f"{weapon_info.get('min_damage', 0)} - {weapon_info.get('max_damage', 0)}",
            ),
            ("Damage Type", weapon_info.get("damage_type", "Unknown")),
            ("Attack Speed", str(weapon_info.get("attack_speed", 0))),
            (
                "Range",
                f"{weapon_info.get('min_range', 0)} - {weapon_info.get('max_range', 0)}",
            ),
            ("Attack Arc", f"{weapon_info.get('attack_arc', 0)}°"),
        ]

        for label, value in combat_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 100px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            combat_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(combat_group)

        # Special Properties Section
        special_group = QGroupBox("SPECIAL PROPERTIES")
        special_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #d28b6f;
                border: 2px solid #d28b6f;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        special_layout = QVBoxLayout(special_group)

        special_info = [
            ("Critical Chance", f"{weapon_info.get('critical_chance', 0)}%"),
            ("Armor Penetration", f"{weapon_info.get('armor_penetration', 0)}%"),
            ("Knockback Chance", f"{weapon_info.get('knockback_chance', 0)}%"),
        ]

        for label, value in special_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 130px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            special_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(special_group)

        # Requirements Section
        req_group = QGroupBox("REQUIREMENTS")
        req_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #9e6fb3;
                border: 2px solid #9e6fb3;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        req_layout = QVBoxLayout(req_group)

        req_data = weapon_info.get("requirements", {})
        req_info = [
            ("Strength", str(req_data.get("strength", 0))),
            ("Dexterity", str(req_data.get("dexterity", 0))),
            ("Intelligence", str(req_data.get("intelligence", 0))),
            ("Level", str(req_data.get("level", 0))),
        ]

        for label, value in req_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 100px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            req_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(req_group)

        # Economy Section
        eco_group = QGroupBox("ECONOMY")
        eco_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #b3a26f;
                border: 2px solid #b3a26f;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        eco_layout = QVBoxLayout(eco_group)

        eco_info = [
            ("Sell Value", f"{weapon_info.get('sell_value', 0)} gold"),
            ("Buy Value", f"{weapon_info.get('buy_value', 0)} gold"),
            ("Rarity", weapon_info.get("rarity", "Unknown")),
        ]

        for label, value in eco_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 100px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            eco_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(eco_group)

        # Additional Properties Section
        addl_group = QGroupBox("ADDITIONAL PROPERTIES")
        addl_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #6fb3a9;
                border: 2px solid #6fb3a9;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        addl_layout = QVBoxLayout(addl_group)

        addl_info = [
            ("Item ID", str(weapon_info.get("item_id", "N/A"))),
            ("Name ID", str(weapon_info.get("name_id", "N/A"))),
            ("Item Type", str(weapon_info.get("item_type", "N/A"))),
            ("Item Subtype", str(weapon_info.get("item_subtype", "N/A"))),
            ("Weapon Type ID", str(weapon_info.get("weapon_type_id", "N/A"))),
            ("Weapon Material ID", str(weapon_info.get("weapon_material_id", "N/A"))),
            (
                "Weapon Material Name",
                str(weapon_info.get("weapon_material_name", "N/A")),
            ),
            ("Weapon Speed", str(weapon_info.get("weapon_speed", 0))),
            ("Item Set ID", str(weapon_info.get("item_set_id", 0))),
            ("Min Range", str(weapon_info.get("min_range", 0))),
            ("Max Range", str(weapon_info.get("max_range", 0))),
            ("Weapon Arc", str(weapon_info.get("attack_arc", 0))),
            ("Icon Handle", str(weapon_info.get("icon_handle", "N/A"))),
        ]

        for label, value in addl_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 130px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            value_widget.setWordWrap(True)  # Allow long icon handles to wrap
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            addl_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(addl_group)

        # CFF-Specific Data Section
        cff_group = QGroupBox("CFF DATA FIELDS")
        cff_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #b36f9e;
                border: 2px solid #b36f9e;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        cff_layout = QVBoxLayout(cff_group)

        # Show school requirements if available
        reqs = weapon_info.get("requirements", {})
        school_reqs = reqs.get("school_requirements", [])
        if school_reqs:
            school_label = QLabel("<strong>School Requirements:</strong>")
            school_label.setStyleSheet("color: #a0a0a0;")
            cff_layout.addWidget(school_label)
            
            for school_req in school_reqs:
                req_text = f"  • {school_req['requirement_school']} Level {school_req['level']}"
                req_label = QLabel(req_text)
                req_label.setStyleSheet("color: #e0e0e0; margin-left: 10px;")
                cff_layout.addWidget(req_label)
        else:
            no_school_label = QLabel("<strong>School Requirements:</strong> None")
            no_school_label.setStyleSheet("color: #a0a0a0;")
            cff_layout.addWidget(no_school_label)

        # Show effects if available
        effects = weapon_info.get("effects", [])
        if effects:
            effects_label = QLabel(f"<strong>Item Effects:</strong> {len(effects)} effect(s)")
            effects_label.setStyleSheet("color: #a0a0a0;")
            cff_layout.addWidget(effects_label)
            
            for effect in effects[:5]:  # Show first 5 effects
                effect_text = f"  • Effect ID {effect['effect_id']} (Index {effect['effect_index']})"
                effect_label = QLabel(effect_text)
                effect_label.setStyleSheet("color: #e0e0e0; margin-left: 10px;")
                cff_layout.addWidget(effect_label)
                
            if len(effects) > 5:
                more_label = QLabel(f"  • ... and {len(effects) - 5} more")
                more_label.setStyleSheet("color: #a0a0a0; margin-left: 10px;")
                cff_layout.addWidget(more_label)
        else:
            no_effects_label = QLabel("<strong>Item Effects:</strong> None")
            no_effects_label.setStyleSheet("color: #a0a0a0;")
            cff_layout.addWidget(no_effects_label)

        # Show additional CFF fields
        additional_fields = [
            ("Unit Stats ID", str(weapon_info.get("unit_stats_id", "N/A"))),
            ("Army Unit ID", str(weapon_info.get("army_unit_id", "N/A"))),
            ("Building ID", str(weapon_info.get("building_id", "N/A"))),
        ]

        for label, value in additional_fields:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 130px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            cff_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(cff_group)

        # Add stretch to push everything to the top
        self.details_content_layout.addStretch()

    def show_armor_details(self, armor_id):
        """Show detailed information for selected armor"""
        armor_info = self.armor_data[armor_id]

        # Clear previous content
        self.clear_details_content()

        # Main title
        title_label = QLabel(
            f"ARMOR ID: {armor_id} - {armor_info.get('armor_name', 'Unknown')}"
        )
        title_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d30;
                color: #ffffff;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_content_layout.addWidget(title_label)

        # Create a grid layout for perfect alignment
        basic_info_layout = QHBoxLayout()

        # Basic Information Section
        basic_group = QGroupBox("BASIC INFORMATION")
        basic_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #6fb3d2;
                border: 2px solid #6fb3d2;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        basic_layout = QVBoxLayout(basic_group)

        basic_info = [
            ("Name", armor_info.get("armor_name", "Unknown")),
            ("Slot", armor_info.get("slot", "Unknown")),
            ("Type", armor_info.get("armor_type", "Unknown")),
            ("Tier", armor_info.get("tier", "Unknown")),
            ("Material", armor_info.get("material_name", "Unknown")),
        ]

        for label, value in basic_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 100px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            basic_layout.addLayout(row_layout)

        # Add basic info to the layout
        basic_info_layout.addWidget(basic_group)

        # Create icon widget with exact height matching
        icon_widget = QLabel()
        icon_widget.setText("ICON")
        icon_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_widget.setStyleSheet("""
            QLabel {
                background-color: #2d2d30;
                color: #a0a0a0;
                border: 1px dashed #6fb3d2;
                font-size: 12px;
                min-width: 120px;
                min-height: 1px;  /* Start with minimal height */
            }
        """)
        icon_widget.setFixedWidth(120)  # Fixed width for the icon space
        # Create container for icon to ensure proper vertical alignment
        icon_container = QWidget()
        icon_container.setStyleSheet("""
            QWidget {
                background-color: #2d2d30;
                border: 1px dashed #6fb3d2;
            }
        """)
        icon_container.setFixedWidth(120)  # Fixed width for the icon space

        # Create layout for the icon container to center the icon
        icon_container_layout = QVBoxLayout(icon_container)
        icon_container_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )  # Center vertically and horizontally

        # Create the icon label
        icon_label = QLabel("ICON")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                color: #a0a0a0;
                font-size: 12px;
            }
        """)

        # Add the icon label to the container's layout
        icon_container_layout.addWidget(icon_label)
        icon_container_layout.addStretch()  # Add stretch to push the icon to the center

        # Add icon container to the same layout
        basic_info_layout.addWidget(icon_container)

        # Add the layout to main content
        self.details_content_layout.addLayout(basic_info_layout)

        # Defense Statistics Section
        def_group = QGroupBox("DEFENSE STATISTICS")
        def_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #76b36f;
                border: 2px solid #76b36f;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        def_layout = QVBoxLayout(def_group)

        def_info = [
            ("Base Armor", str(armor_info.get("base_armor", 0))),
            ("Magic Resistance", str(armor_info.get("magic_resistance", 0))),
            ("Physical Resistance", str(armor_info.get("physical_resistance", 0))),
        ]

        for label, value in def_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 150px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            def_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(def_group)

        # Special Properties Section
        special_group = QGroupBox("SPECIAL PROPERTIES")
        special_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #d28b6f;
                border: 2px solid #d28b6f;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        special_layout = QVBoxLayout(special_group)

        special_info = [
            ("Movement Speed", f"{armor_info.get('move_speed_bonus', 0)}%"),
            ("Health Bonus", str(armor_info.get("health_bonus", 0))),
            ("Mana Bonus", str(armor_info.get("mana_bonus", 0))),
        ]

        for label, value in special_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 130px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            special_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(special_group)

        # Requirements Section
        req_group = QGroupBox("REQUIREMENTS")
        req_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #9e6fb3;
                border: 2px solid #9e6fb3;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        req_layout = QVBoxLayout(req_group)

        req_data = armor_info.get("requirements", {})
        req_info = [
            ("Strength", str(req_data.get("strength", 0))),
            ("Dexterity", str(req_data.get("dexterity", 0))),
            ("Intelligence", str(req_data.get("intelligence", 0))),
            ("Level", str(req_data.get("level", 0))),
        ]

        for label, value in req_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 100px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            req_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(req_group)

        # Economy Section
        eco_group = QGroupBox("ECONOMY")
        eco_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #b3a26f;
                border: 2px solid #b3a26f;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        eco_layout = QVBoxLayout(eco_group)

        eco_info = [
            ("Sell Value", f"{armor_info.get('sell_value', 0)} gold"),
            ("Buy Value", f"{armor_info.get('buy_value', 0)} gold"),
            ("Rarity", armor_info.get("rarity", "Unknown")),
        ]

        for label, value in eco_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 100px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            eco_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(eco_group)

        # Additional Properties Section (similar to weapons)
        addl_group = QGroupBox("ADDITIONAL PROPERTIES")
        addl_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #6fb3a9;
                border: 2px solid #6fb3a9;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        addl_layout = QVBoxLayout(addl_group)

        # Additional armor properties from the CFF data
        addl_info = [
            ("Item ID", str(armor_info.get("item_id", "N/A"))),
            ("Name ID", str(armor_info.get("name_id", "N/A"))),
            ("Item Type", str(armor_info.get("item_type", "N/A"))),
            ("Item Subtype", str(armor_info.get("item_subtype", "N/A"))),
            ("Item Set ID", str(armor_info.get("item_set_id", "N/A"))),
            ("Icon Handle", str(armor_info.get("icon_handle", "N/A"))),
        ]

        for label, value in addl_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 130px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            value_widget.setWordWrap(True)  # Allow long icon handles to wrap
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            addl_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(addl_group)

        # CFF-Specific Data Section
        cff_group = QGroupBox("CFF DATA FIELDS")
        cff_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #b36f9e;
                border: 2px solid #b36f9e;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        cff_layout = QVBoxLayout(cff_group)

        # Show school requirements if available
        reqs = armor_info.get("requirements", {})
        school_reqs = reqs.get("school_requirements", [])
        if school_reqs:
            school_label = QLabel("<strong>School Requirements:</strong>")
            school_label.setStyleSheet("color: #a0a0a0;")
            cff_layout.addWidget(school_label)
            
            for school_req in school_reqs:
                req_text = f"  • {school_req['requirement_school']} Level {school_req['level']}"
                req_label = QLabel(req_text)
                req_label.setStyleSheet("color: #e0e0e0; margin-left: 10px;")
                cff_layout.addWidget(req_label)
        else:
            no_school_label = QLabel("<strong>School Requirements:</strong> None")
            no_school_label.setStyleSheet("color: #a0a0a0;")
            cff_layout.addWidget(no_school_label)

        # Show effects if available
        effects = armor_info.get("effects", [])
        if effects:
            effects_label = QLabel(f"<strong>Item Effects:</strong> {len(effects)} effect(s)")
            effects_label.setStyleSheet("color: #a0a0a0;")
            cff_layout.addWidget(effects_label)
            
            for effect in effects[:5]:  # Show first 5 effects
                effect_text = f"  • Effect ID {effect['effect_id']} (Index {effect['effect_index']})"
                effect_label = QLabel(effect_text)
                effect_label.setStyleSheet("color: #e0e0e0; margin-left: 10px;")
                cff_layout.addWidget(effect_label)
                
            if len(effects) > 5:
                more_label = QLabel(f"  • ... and {len(effects) - 5} more")
                more_label.setStyleSheet("color: #a0a0a0; margin-left: 10px;")
                cff_layout.addWidget(more_label)
        else:
            no_effects_label = QLabel("<strong>Item Effects:</strong> None")
            no_effects_label.setStyleSheet("color: #a0a0a0;")
            cff_layout.addWidget(no_effects_label)

        # Show additional CFF fields
        additional_fields = [
            ("Unit Stats ID", str(armor_info.get("unit_stats_id", "N/A"))),
            ("Army Unit ID", str(armor_info.get("army_unit_id", "N/A"))),
            ("Building ID", str(armor_info.get("building_id", "N/A"))),
        ]

        for label, value in additional_fields:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 130px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            cff_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(cff_group)

        # Add stretch to push everything to the top
        self.details_content_layout.addStretch()

    def create_weapon(self):
        """Launch the Weapon Forge Wizard"""
        try:
            if not self.id_manager:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "ID manager not initialized. Please reload data first.",
                )
                return

            # Create and show the wizard
            wizard = WeaponForgeWizard(self.id_manager, self)
            result = wizard.exec()

            if result == wizard.DialogCode.Accepted:
                # Weapon creation successful - reload data
                self.reload_data()
                QMessageBox.information(self, "Success", "Weapon created successfully!")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to launch weapon forge wizard:\n{e}"
            )

    def create_armor(self):
        """Launch the Armor Forge Wizard"""
        try:
            if not self.id_manager:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "ID manager not initialized. Please reload data first.",
                )
                return

            # Create and show the wizard
            wizard = ArmorForgeWizard(self.id_manager, self)
            result = wizard.exec()

            if result == wizard.DialogCode.Accepted:
                # Armor creation successful - reload data
                self.reload_data()
                QMessageBox.information(self, "Success", "Armor created successfully!")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to launch armor forge wizard:\n{e}"
            )

    def reload_data(self):
        """Reload all item data"""
        self.weapon_data.clear()
        self.armor_data.clear()
        self.load_data()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Orthanc's Workshop - Weapon & Armor Suite"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Configure logging if debug mode
    if args.debug:
        configure_logging()

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Orthanc's Workshop")
    app.setOrganizationName("TirganachReloaded Modding Tools")

    # Set application style
    app.setStyle("Fusion")

    # Apply dark theme stylesheet (matching simple_quest_viewer.py)
    app.setStyleSheet("""
        /* Main application background */
        QMainWindow {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }

        /* Widgets */
        QWidget {
            background-color: #2b2b2b;
            color: #e0e0e0;
        }

        /* Group boxes */
        QGroupBox {
            font-weight: bold;
            border: 2px solid #3c3c3c;
            border-radius: 5px;
            margin-top: 1ex;
            background-color: #2b2b2b;
            color: #e0e0e0;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: #e0e0e0;
            font-weight: bold;
        }

        /* Buttons */
        QPushButton {
            background-color: #3c3c3c;
            color: #e0e0e0;
            border: 1px solid #555;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: normal;
        }

        QPushButton:hover {
            background-color: #4a4a4a;
        }

        QPushButton:pressed {
            background-color: #2d2d30;
        }

        QPushButton:disabled {
            background-color: #252525;
            color: #808080;
        }

        /* Labels */
        QLabel {
            color: #e0e0e0;
        }

        /* Line edits */
        QLineEdit {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #3c3c3c;
            padding: 3px;
            selection-background-color: #094771;
        }

        /* Combo boxes */
        QComboBox {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #3c3c3c;
            padding: 3px;
            selection-background-color: #094771;
        }

        QComboBox::drop-down {
            border: none;
        }

        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #e0e0e0;
            margin-right: 5px;
        }

        QComboBox QAbstractItemView {
            background-color: #1e1e1e;
            color: #e0e0e0;
            selection-background-color: #094771;
            border: 1px solid #3c3c3c;
        }

        /* Spin boxes */
        QSpinBox, QDoubleSpinBox {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #3c3c3c;
            padding: 3px;
            selection-background-color: #094771;
        }

        /* Text edits */
        QTextEdit {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #3c3c3c;
            selection-background-color: #094771;
        }

        /* Status bar */
        QStatusBar {
            background-color: #2b2b2b;
            color: #e0e0e0;
            border-top: 1px solid #3c3c3c;
        }

        /* Menu bar */
        QMenuBar {
            background-color: #2b2b2b;
            color: #e0e0e0;
            border-bottom: 1px solid #3c3c3c;
        }

        QMenuBar::item {
            background-color: transparent;
            padding: 5px 10px;
        }

        QMenuBar::item:selected {
            background-color: #3c3c3c;
        }

        /* Tooltips */
        QToolTip {
            background-color: #2d2d30;
            color: #e0e0e0;
            border: 1px solid #3c3c3c;
        }
    """)

    # Create and show main window
    window = OrthancsWorkshop()
    window.show()

    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
