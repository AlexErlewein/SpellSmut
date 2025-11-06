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
    QSplitter,
    QTextEdit,
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

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlainText("Select an item to view details...")

        # Dark theme details styling
        self.details_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3c3c3c;
                padding: 10px;
                selection-background-color: #094771;
            }
        """)

        details_layout.addWidget(self.details_text)

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
        """Load weapon data from various sources"""
        try:
            # Try to load from enhanced weapons data
            enhanced_weapons_path = Path("src/TirganachReloaded/enhanced_weapons.json")
            if enhanced_weapons_path.exists():
                import json

                with open(enhanced_weapons_path, "r", encoding="utf-8") as f:
                    weapons_data = json.load(f)

                for weapon in weapons_data:
                    weapon_id = weapon.get("weapon_id", weapon.get("item_id"))
                    if weapon_id:
                        # Normalize field names for consistency
                        normalized_weapon = weapon.copy()
                        if "name" in weapon and "weapon_name" not in weapon:
                            normalized_weapon["weapon_name"] = weapon["name"]
                        self.weapon_data[weapon_id] = normalized_weapon

                if self.logger:
                    self.logger.info(
                        f"✓ Loaded {len(weapons_data)} weapons from enhanced data"
                    )
            else:
                if self.logger:
                    self.logger.warning("Enhanced weapons data not found")

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load weapon data: {e}")

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

    def load_armor_data(self):
        """Load armor data from enhanced_armor.json"""
        try:
            # Try to load from enhanced armor data
            enhanced_armor_path = Path("src/TirganachReloaded/enhanced_armor.json")
            if enhanced_armor_path.exists():
                import json

                with open(enhanced_armor_path, "r", encoding="utf-8") as f:
                    armor_data = json.load(f)

                # Get the list of armor items from the JSON structure
                armor_items = armor_data.get("armors", [])

                for armor in armor_items:
                    armor_id = armor.get("id")
                    if armor_id:
                        # Normalize field names for consistency with UI expectations
                        normalized_armor = {
                            "armor_id": armor_id,
                            "armor_name": armor.get(
                                "display_name", armor.get("name", f"Armor {armor_id}")
                            ),
                            "name": armor.get("name", f"Armor {armor_id}"),
                            "slot": self.get_armor_slot_name(armor.get("slot", 0)),
                            "armor_type": armor.get("armor_type", "Unknown"),
                            "tier": armor.get("tier", "Unknown"),
                            "material_name": armor.get("material", "Unknown"),
                            "base_armor": armor.get("armor_value", 0),
                            "magic_resistance": armor.get("magic_resist", 0),
                            "physical_resistance": armor.get("physical_resist", 0),
                            "move_speed_bonus": armor.get("run_speed", 0),
                            "health_bonus": armor.get("health", 0),
                            "mana_bonus": armor.get("mana", 0),
                            # Requirements section
                            "requirements": {
                                "strength": armor.get("strength", 0),
                                "dexterity": armor.get("dexterity", 0),
                                "intelligence": armor.get("intelligence", 0),
                                "level": armor.get("level_requirement", 0),
                            },
                            "sell_value": armor.get("sell_value", 0),
                            "buy_value": armor.get("buy_value", 0),
                            "rarity": armor.get("tier", "Unknown"),
                        }
                        self.armor_data[armor_id] = normalized_armor

                if self.logger:
                    self.logger.info(
                        f"✓ Loaded {len(armor_items)} armor items from enhanced data"
                    )
            else:
                if self.logger:
                    self.logger.warning(
                        "Enhanced armor data not found, using sample data"
                    )

                # Fallback to sample armor data if the file is not found
                sample_armor = [
                    {
                        "armor_id": 20000,
                        "armor_name": "Iron Helmet",
                        "slot": "Head",
                        "armor_type": "Plate",
                        "tier": "Common",
                        "base_armor": 15,
                        "material_name": "Iron",
                    },
                    {
                        "armor_id": 20001,
                        "armor_name": "Dragon Scale Chest",
                        "slot": "Chest",
                        "armor_type": "Plate",
                        "tier": "Epic",
                        "base_armor": 45,
                        "material_name": "Dragon Scale",
                    },
                ]

                for armor in sample_armor:
                    armor_id = armor["armor_id"]
                    self.armor_data[armor_id] = armor

                if self.logger:
                    self.logger.info(f"✓ Loaded {len(sample_armor)} sample armor items")

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

        details = []

        # Header
        weapon_name = weapon_info.get("weapon_name", weapon_info.get("name", "Unknown"))
        if not weapon_name or weapon_name == "Unknown":
            weapon_name = weapon_info.get("name", "Unknown")
        details.append(
            "╔══════════════════════════════════════════════════════════════╗"
        )
        details.append(f"║ Weapon ID: {weapon_id} - {weapon_name}")
        details.append(
            "╚══════════════════════════════════════════════════════════════╝"
        )
        details.append("")

        # Basic information
        details.append("BASIC INFORMATION:")
        details.append("=" * 60)
        details.append(
            f"Name: {weapon_info.get('weapon_name', weapon_info.get('name', 'Unknown'))}"
        )
        details.append(
            f"Type: {weapon_info.get('weapon_type_name', weapon_info.get('item_subtype', 'Unknown'))}"
        )
        details.append(
            f"Material: {weapon_info.get('weapon_material_name', 'Unknown')}"
        )
        details.append(f"Hands: {weapon_info.get('hands', 'Unknown')}")
        details.append(f"Category: {weapon_info.get('damage_category', 'Unknown')}")
        details.append("")

        # Combat stats
        # Combat stats
        details.append("COMBAT STATISTICS:")
        details.append("-" * 60)
        details.append(
            f"  Damage: {weapon_info.get('min_damage', 0)} - {weapon_info.get('max_damage', 0)}"
        )
        details.append(f"  Damage Type: {weapon_info.get('damage_type', 'Unknown')}")
        details.append(f"  Attack Speed: {weapon_info.get('attack_speed', 0)}")
        details.append(
            f"  Range: {weapon_info.get('min_range', 0)} - {weapon_info.get('max_range', 0)}"
        )
        details.append(f"  Attack Arc: {weapon_info.get('attack_arc', 0)}°")
        details.append("")

        # Special properties
        details.append("SPECIAL PROPERTIES:")
        details.append("-" * 60)
        details.append(f"  Critical Chance: {weapon_info.get('critical_chance', 0)}%")
        details.append(
            f"  Armor Penetration: {weapon_info.get('armor_penetration', 0)}%"
        )
        details.append(f"  Knockback Chance: {weapon_info.get('knockback_chance', 0)}%")
        details.append("")

        # Requirements
        details.append("REQUIREMENTS:")
        details.append("-" * 60)
        req = weapon_info.get("requirements", {})
        details.append(f"  Strength: {req.get('strength', 0)}")
        details.append(f"  Dexterity: {req.get('dexterity', 0)}")
        details.append(f"  Intelligence: {req.get('intelligence', 0)}")
        details.append(f"  Level: {req.get('level', 0)}")
        details.append("")

        # Economy
        details.append("ECONOMY:")
        details.append("-" * 60)
        details.append(f"  Sell Value: {weapon_info.get('sell_value', 0)} gold")
        details.append(f"  Buy Value: {weapon_info.get('buy_value', 0)} gold")
        details.append(f"  Rarity: {weapon_info.get('rarity', 'Unknown')}")
        details.append("")

        # Footer
        details.append(
            "╔══════════════════════════════════════════════════════════════╗"
        )
        details.append(f"║ End of Weapon {weapon_id} Details")
        details.append(
            "╚══════════════════════════════════════════════════════════════╝"
        )

        self.details_text.setPlainText("\n".join(details))

    def show_armor_details(self, armor_id):
        """Show detailed information for selected armor"""
        armor_info = self.armor_data[armor_id]

        details = []

        # Header
        armor_name = armor_info.get("armor_name", "Unknown")
        details.append(
            "╔══════════════════════════════════════════════════════════════╗"
        )
        details.append(f"║ Armor ID: {armor_id} - {armor_name}")
        details.append(
            "╚══════════════════════════════════════════════════════════════╝"
        )
        details.append("")

        # Basic information
        details.append("BASIC INFORMATION:")
        details.append("=" * 60)
        details.append(f"Name: {armor_info.get('armor_name', 'Unknown')}")
        details.append(f"Slot: {armor_info.get('slot', 'Unknown')}")
        details.append(f"Type: {armor_info.get('armor_type', 'Unknown')}")
        details.append(f"Tier: {armor_info.get('tier', 'Unknown')}")
        details.append(f"Material: {armor_info.get('material_name', 'Unknown')}")
        details.append("")

        # Defense stats
        details.append("DEFENSE STATISTICS:")
        details.append("=" * 60)
        details.append(f"Base Armor: {armor_info.get('base_armor', 0)}")
        details.append(f"Magic Resistance: {armor_info.get('magic_resistance', 0)}")
        details.append(
            f"Physical Resistance: {armor_info.get('physical_resistance', 0)}"
        )
        details.append("")

        # Special properties
        details.append("SPECIAL PROPERTIES:")
        details.append("=" * 60)
        details.append(
            f"Movement Speed: {armor_info.get('move_speed_bonus', 0) if armor_info.get('move_speed_bonus') else 0}%"
        )
        details.append(
            f"Health Bonus: {armor_info.get('health_bonus', 0) if armor_info.get('health_bonus') else 0}"
        )
        details.append(
            f"Mana Bonus: {armor_info.get('mana_bonus', 0) if armor_info.get('mana_bonus') else 0}"
        )
        details.append("")

        # Requirements
        details.append("REQUIREMENTS:")
        details.append("=" * 60)
        req = armor_info.get("requirements", {})
        details.append(f"Strength: {req.get('strength', 0)}")
        details.append(f"Dexterity: {req.get('dexterity', 0)}")
        details.append(f"Intelligence: {req.get('intelligence', 0)}")
        details.append(f"Level: {req.get('level', 0)}")
        details.append("")

        # Economy
        details.append("ECONOMY:")
        details.append("=" * 60)
        details.append(f"Sell Value: {armor_info.get('sell_value', 0)} gold")
        details.append(f"Buy Value: {armor_info.get('buy_value', 0)} gold")
        details.append(f"Rarity: {armor_info.get('rarity', 'Unknown')}")
        details.append("")

        # Defense stats
        details.append("DEFENSE STATISTICS:")
        details.append("-" * 60)
        details.append(f"  Base Armor: {armor_info.get('base_armor', 0)}")
        details.append("")

        # Footer
        details.append(
            "╔══════════════════════════════════════════════════════════════╗"
        )
        details.append(f"║ End of Armor {armor_id} Details")
        details.append(
            "╚══════════════════════════════════════════════════════════════╝"
        )

        self.details_text.setPlainText("\n".join(details))

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

            # Create armor data object
            from TirganachReloaded.cff_editor.models.armor_creation_data import (
                ArmorCreationData,
            )

            armor_data = ArmorCreationData()

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
