"""
Item Browser Widget
==================
Comprehensive browser for items, weapons, armor, and creatures.

Author: Quest Editor Team
Date: November 17, 2025
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QLineEdit,
    QLabel,
    QPushButton,
    QComboBox,
    QGroupBox,
    QHeaderView,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from typing import Dict, List, Optional, Any
import json


class ItemData:
    """Represents an item/creature in the browser"""

    def __init__(
        self,
        item_id: int,
        name: str,
        item_type: str = "item",
        description: str = "",
        icon: str = "",
        stats: Optional[Dict] = None,
    ):
        self.item_id = item_id
        self.name = name
        self.item_type = item_type  # item, weapon, armor, creature
        self.description = description
        self.icon = icon
        self.stats = stats or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.item_id,
            "name": self.name,
            "type": self.item_type,
            "description": self.description,
            "icon": self.icon,
            "stats": self.stats,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return ItemData(
            item_id=data.get("id", 0),
            name=data.get("name", ""),
            item_type=data.get("type", "item"),
            description=data.get("description", ""),
            icon=data.get("icon", ""),
            stats=data.get("stats", {}),
        )


class ItemBrowserWidget(QWidget):
    """
    Comprehensive item browser for items, weapons, armor, and creatures.

    Features:
    - Search and filter functionality
    - Category filtering
    - Item details display
    - Selection support for objective/reward systems
    """

    item_selected = Signal(dict)  # Emitted when item is selected

    def __init__(self, parent=None, data_model=None):
        super().__init__(parent)
        self.items_data: List[ItemData] = []
        self.filtered_items: List[ItemData] = []
        self.data_model = data_model
        self.setup_ui()
        if data_model:
            self.load_from_data_model()
        else:
            self.load_sample_data()

    def setup_ui(self):
        """Setup the browser UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header_label = QLabel("Item Browser")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(header_label)

        # Search and filter controls
        controls_layout = QHBoxLayout()

        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search items by name...")
        self.search_edit.textChanged.connect(self.filter_items)
        controls_layout.addWidget(QLabel("Search:"))
        controls_layout.addWidget(self.search_edit, 1)

        # Category filter
        self.category_combo = QComboBox()
        self.category_combo.addItems(
            [
                "All Items",
                "General Items",
                "Weapons",
                "Armor",
                "Creatures/Enemies",
                "Consumables",
                "Quest Items",
                "Materials",
            ]
        )
        self.category_combo.currentTextChanged.connect(self.filter_items)
        controls_layout.addWidget(QLabel("Category:"))
        controls_layout.addWidget(self.category_combo)

        layout.addLayout(controls_layout)

        # Items tree
        self.items_tree = QTreeWidget()
        self.items_tree.setHeaderLabels(["Name", "Type", "ID", "Description"])
        self.items_tree.setAlternatingRowColors(True)
        self.items_tree.setSortingEnabled(True)
        self.items_tree.setRootIsDecorated(False)
        self.items_tree.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Configure columns
        header = self.items_tree.header()
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )  # Name column stretches
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )  # Type column
        header.setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )  # ID column
        header.setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )  # Description column stretches

        layout.addWidget(self.items_tree)

        # Details panel
        self.details_group = QGroupBox("Item Details")
        details_layout = QVBoxLayout(self.details_group)

        self.details_name = QLabel("Select an item to view details")
        self.details_name.setWordWrap(True)
        self.details_name.setStyleSheet("font-weight: bold; font-size: 12px;")
        details_layout.addWidget(self.details_name)

        self.details_stats = QLabel("")
        self.details_stats.setWordWrap(True)
        self.details_stats.setStyleSheet("color: #666; font-size: 10px;")
        details_layout.addWidget(self.details_stats)

        self.details_group.setMaximumHeight(150)
        layout.addWidget(self.details_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.select_btn = QPushButton("Select Item")
        self.select_btn.clicked.connect(self.select_current_item)
        self.select_btn.setEnabled(False)
        button_layout.addWidget(self.select_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)

    def load_from_data_model(self):
        """Load comprehensive item data from CFF data model"""
        if not self.data_model:
            print("DEBUG: No data model provided, loading sample data")
            self.load_sample_data()
            return

        try:
            self.items_data = []

            # Load weapons
            weapons = self.data_model.get_elements("weapons") or []
            for weapon in weapons:
                item_data = self._convert_weapon_to_item_data(weapon)
                if item_data:
                    self.items_data.append(item_data)

            # Load armor
            armor = self.data_model.get_elements("armor") or []
            for armor_item in armor:
                item_data = self._convert_armor_to_item_data(armor_item)
                if item_data:
                    self.items_data.append(item_data)

            # Load general items
            items = self.data_model.get_elements("items") or []
            for item in items:
                item_data = self._convert_item_to_item_data(item)
                if item_data:
                    self.items_data.append(item_data)

            # Load creatures (if available)
            creatures = self.data_model.get_elements("creatures") or []
            for creature in creatures:
                item_data = self._convert_creature_to_item_data(creature)
                if item_data:
                    self.items_data.append(item_data)

            self.filtered_items = self.items_data.copy()
            self.populate_tree()

        except Exception as e:
            print(f"Error loading from data model: {e}")
            self.load_sample_data()

    def _convert_weapon_to_item_data(self, weapon) -> Optional[ItemData]:
        """Convert weapon entity to ItemData"""
        try:
            item_id = getattr(weapon, "item_id", 0)
            if item_id == 0:
                return None

            name = (
                self.data_model.get_localised_text(weapon, "name")
                if self.data_model
                else None
            )
            if not name:
                name = getattr(weapon, "name", f"Weapon {item_id}")

            # Get weapon stats
            stats = {}
            if hasattr(weapon, "damage_min") and hasattr(weapon, "damage_max"):
                stats["damage"] = f"{weapon.damage_min}-{weapon.damage_max}"
            if hasattr(weapon, "weapon_speed"):
                stats["speed"] = weapon.weapon_speed
            if hasattr(weapon, "attack_speed"):
                stats["attack_speed"] = weapon.attack_speed
            if hasattr(weapon, "weapon_type_name"):
                stats["type"] = weapon.weapon_type_name
            if hasattr(weapon, "weapon_material_name"):
                stats["material"] = weapon.weapon_material_name

            # Get requirements
            if hasattr(weapon, "level_requirement"):
                stats["level_req"] = weapon.level_requirement

            # Get icon
            icon = self._get_item_icon(weapon)

            return ItemData(
                item_id=item_id,
                name=name,
                item_type="weapon",
                description=f"Weapon - {name}",
                icon=icon,
                stats=stats,
            )
        except Exception as e:
            print(
                f"Error converting weapon {getattr(weapon, 'item_id', 'unknown')}: {e}"
            )
            return None

    def _convert_armor_to_item_data(self, armor) -> Optional[ItemData]:
        """Convert armor entity to ItemData"""
        try:
            item_id = getattr(armor, "item_id", 0)
            if item_id == 0:
                return None

            name = (
                self.data_model.get_localised_text(armor, "name")
                if self.data_model
                else None
            )
            if not name:
                name = (
                    self.data_model.get_armor_name(item_id) if self.data_model else None
                ) or getattr(armor, "name", f"Armor {item_id}")

            # Get armor stats
            stats = {}
            if hasattr(armor, "armor_value"):
                stats["defense"] = armor.armor_value
            if hasattr(armor, "slot"):
                stats["slot"] = armor.slot
            if hasattr(armor, "armor_type"):
                stats["type"] = armor.armor_type

            # Get attributes
            attributes = [
                "strength",
                "stamina",
                "agility",
                "dexterity",
                "health",
                "charisma",
                "intelligence",
                "wisdom",
                "mana",
            ]
            for attr in attributes:
                if hasattr(armor, attr):
                    value = getattr(armor, attr)
                    if value != 0:  # Only include non-zero attributes
                        stats[attr] = value

            # Get resistances
            resistances = ["resist_fire", "resist_ice", "resist_black", "resist_mind"]
            for resist in resistances:
                if hasattr(armor, resist):
                    value = getattr(armor, resist)
                    if value != 0:
                        stats[resist.replace("resist_", "") + "_resist"] = value

            # Get speed modifiers
            if hasattr(armor, "run_speed"):
                stats["run_speed"] = armor.run_speed
            if hasattr(armor, "fight_speed"):
                stats["fight_speed"] = armor.fight_speed
            if hasattr(armor, "cast_speed"):
                stats["cast_speed"] = armor.cast_speed

            # Get requirements
            if hasattr(armor, "level_requirement"):
                stats["level_req"] = armor.level_requirement

            # Get icon
            icon = self._get_item_icon(armor)

            return ItemData(
                item_id=item_id,
                name=name,
                item_type="armor",
                description=f"Armor - {name}",
                icon=icon,
                stats=stats,
            )
        except Exception as e:
            print(f"Error converting armor {getattr(armor, 'item_id', 'unknown')}: {e}")
            return None

    def _convert_item_to_item_data(self, item) -> Optional[ItemData]:
        """Convert general item entity to ItemData"""
        try:
            item_id = getattr(item, "item_id", 0)
            if item_id == 0:
                return None

            name = (
                self.data_model.get_localised_text(item, "name")
                if self.data_model
                else None
            )
            if not name:
                name = getattr(item, "name", f"Item {item_id}")

            # Determine item type based on properties
            item_type = "item"
            if hasattr(item, "item_type"):
                raw_type = str(getattr(item, "item_type", "")).lower()
                if "potion" in raw_type or "consumable" in raw_type:
                    item_type = "consumable"
                elif "quest" in raw_type:
                    item_type = "quest"
                elif "material" in raw_type:
                    item_type = "material"

            # Get item stats
            stats = {}
            if hasattr(item, "value"):
                stats["value"] = item.value
            if hasattr(item, "level_requirement"):
                stats["level_req"] = item.level_requirement

            # Get icon
            icon = self._get_item_icon(item)

            description = (
                self.data_model.get_localised_text(item, "description")
                if self.data_model
                else None
            ) or f"Item - {name}"

            return ItemData(
                item_id=item_id,
                name=name,
                item_type=item_type,
                description=description,
                icon=icon,
                stats=stats,
            )
        except Exception as e:
            print(f"Error converting item {getattr(item, 'item_id', 'unknown')}: {e}")
            return None

    def _convert_creature_to_item_data(self, creature) -> Optional[ItemData]:
        """Convert creature entity to ItemData"""
        try:
            item_id = getattr(creature, "id", 0) or getattr(creature, "creature_id", 0)
            if item_id == 0:
                return None

            name = (
                self.data_model.get_localised_text(creature, "name")
                if self.data_model
                else None
            )
            if not name:
                name = getattr(creature, "name", f"Creature {item_id}")

            # Get creature stats
            stats = {}
            if hasattr(creature, "level"):
                stats["level"] = creature.level
            if hasattr(creature, "hp"):
                stats["hp"] = creature.hp
            if hasattr(creature, "damage"):
                stats["damage"] = creature.damage
            if hasattr(creature, "armor"):
                stats["armor"] = creature.armor

            # Get icon (creatures might not have icons, use generic)
            icon = "👺"  # Default creature icon

            return ItemData(
                item_id=item_id,
                name=name,
                item_type="creature",
                description=f"Creature - {name}",
                icon=icon,
                stats=stats,
            )
        except Exception as e:
            print(
                f"Error converting creature {getattr(creature, 'id', 'unknown')}: {e}"
            )
            return None

    def _get_item_icon(self, item) -> str:
        """Get icon for an item using data model"""
        try:
            if self.data_model:
                icon_path = self.data_model.get_icon_for_element(item, "items")
                if icon_path:
                    return icon_path
        except:
            pass
        return ""  # Return empty string for no icon

    def load_sample_data(self):
        """Load sample item data (fallback when CFF data not available)"""
        # Sample items
        sample_items = [
            # General Items
            ItemData(
                1001,
                "Health Potion",
                "item",
                "Restores 50 HP",
                "🧪",
                {"healing": 50, "value": 25},
            ),
            ItemData(
                1002,
                "Mana Potion",
                "item",
                "Restores 30 MP",
                "🧪",
                {"mana": 30, "value": 30},
            ),
            ItemData(
                1003,
                "Antidote",
                "item",
                "Cures poison effects",
                "💊",
                {"effect": "cure_poison"},
            ),
            ItemData(
                1004,
                "Torch",
                "item",
                "Provides light in dark areas",
                "🔦",
                {"duration": 300},
            ),
            # Weapons
            ItemData(
                2001,
                "Iron Sword",
                "weapon",
                "Basic one-handed sword",
                "⚔️",
                {"damage": 15, "speed": 1.2, "type": "slashing"},
            ),
            ItemData(
                2002,
                "Longbow",
                "weapon",
                "Two-handed ranged weapon",
                "🏹",
                {"damage": 20, "range": 30, "type": "piercing"},
            ),
            ItemData(
                2003,
                "Fire Staff",
                "weapon",
                "Magical staff with fire damage",
                "🔥",
                {"damage": 25, "magic_power": 15, "element": "fire"},
            ),
            ItemData(
                2004,
                "Warhammer",
                "weapon",
                "Heavy two-handed hammer",
                "🔨",
                {"damage": 30, "speed": 0.8, "type": "bludgeoning"},
            ),
            # Armor
            ItemData(
                3001,
                "Leather Armor",
                "armor",
                "Basic light armor",
                "🛡️",
                {"defense": 10, "weight": 15, "type": "light"},
            ),
            ItemData(
                3002,
                "Chain Mail",
                "armor",
                "Medium metal armor",
                "🛡️",
                {"defense": 20, "weight": 30, "type": "medium"},
            ),
            ItemData(
                3003,
                "Plate Armor",
                "armor",
                "Heavy metal armor",
                "🛡️",
                {"defense": 35, "weight": 50, "type": "heavy"},
            ),
            ItemData(
                3004,
                "Magic Robe",
                "armor",
                "Light magical robe",
                "🧙",
                {"defense": 8, "magic_resist": 20, "weight": 5},
            ),
            # Creatures/Enemies
            ItemData(
                4001,
                "Goblin",
                "creature",
                "Weak but numerous enemy",
                "👺",
                {"level": 3, "hp": 30, "damage": 8},
            ),
            ItemData(
                4002,
                "Orc Warrior",
                "creature",
                "Medium strength enemy",
                "👹",
                {"level": 8, "hp": 80, "damage": 15},
            ),
            ItemData(
                4003,
                "Troll",
                "creature",
                "Strong but slow enemy",
                "🧟",
                {"level": 12, "hp": 150, "damage": 25, "regeneration": 5},
            ),
            ItemData(
                4004,
                "Dragon",
                "creature",
                "Powerful flying enemy",
                "🐉",
                {"level": 20, "hp": 500, "damage": 40, "breath": "fire"},
            ),
            # Quest Items
            ItemData(
                5001,
                "Ancient Key",
                "quest",
                "Opens mysterious door",
                "🗝️",
                {"quest_id": 646, "door_id": 1001},
            ),
            ItemData(
                5002,
                "Magic Crystal",
                "quest",
                "Powers ancient device",
                "💎",
                {"quest_id": 647, "power_level": 5},
            ),
            ItemData(
                5003,
                "Sacred Scroll",
                "quest",
                "Contains ancient spell",
                "📜",
                {"quest_id": 648, "spell": "teleport"},
            ),
            # Materials
            ItemData(
                6001,
                "Iron Ore",
                "material",
                "Raw metal for crafting",
                "⛏️",
                {"crafting": True, "quality": "common"},
            ),
            ItemData(
                6002,
                "Magic Herbs",
                "material",
                "Alchemical ingredients",
                "🌿",
                {"crafting": True, "potency": 3},
            ),
            ItemData(
                6003,
                "Dragon Scale",
                "material",
                "Rare crafting component",
                "🐉",
                {"crafting": True, "quality": "rare", "resistance": "fire"},
            ),
            # Consumables
            ItemData(
                7001,
                "Bread",
                "consumable",
                "Basic food item",
                "🍞",
                {"hunger": -20, "nutrition": 5},
            ),
            ItemData(
                7002,
                "Water Flask",
                "consumable",
                "Refills thirst meter",
                "💧",
                {"thirst": -30, "capacity": 3},
            ),
            ItemData(
                7003,
                "Ration Pack",
                "consumable",
                "Travel food supplies",
                "🎒",
                {"hunger": -50, "nutrition": 8, "duration": 3600},
            ),
        ]

        self.items_data = sample_items
        self.filtered_items = sample_items.copy()
        self.populate_tree()

    def populate_tree(self):
        """Populate the tree with filtered items"""
        self.items_tree.clear()

        # Group items by type for better organization
        items_by_type = {}
        for item in self.filtered_items:
            if item.item_type not in items_by_type:
                items_by_type[item.item_type] = []
            items_by_type[item.item_type].append(item)

        # Add items to tree
        for item_type, items in items_by_type.items():
            # Create type group item
            type_item = QTreeWidgetItem(self.items_tree)
            type_item.setText(0, f"{item_type.capitalize()}s ({len(items)})")
            type_item.setData(0, Qt.ItemDataRole.UserRole, None)  # Not selectable

            # Add items of this type
            for item in items:
                item_widget = QTreeWidgetItem(type_item)
                item_widget.setText(0, item.name)
                item_widget.setText(1, item.item_type.capitalize())
                item_widget.setText(2, str(item.item_id))
                item_widget.setText(
                    3,
                    item.description[:50] + "..."
                    if len(item.description) > 50
                    else item.description,
                )
                item_widget.setData(0, Qt.ItemDataRole.UserRole, item.to_dict())

                # Color code by type
                type_colors = {
                    "item": QColor(52, 152, 219),  # Blue
                    "weapon": QColor(231, 76, 60),  # Red
                    "armor": QColor(46, 204, 113),  # Green
                    "creature": QColor(155, 89, 182),  # Purple
                    "quest": QColor(241, 196, 15),  # Yellow
                    "material": QColor(230, 126, 34),  # Orange
                    "consumable": QColor(52, 73, 94),  # Dark blue
                }
                color = type_colors.get(item.item_type, QColor(0, 0, 0))
                item_widget.setForeground(0, color)
                item_widget.setForeground(1, color)

        self.items_tree.expandAll()

    def filter_items(self):
        """Filter items based on search text and category"""
        search_text = self.search_edit.text().lower()
        category = self.category_combo.currentText().lower()

        self.filtered_items = []

        for item in self.items_data:
            # Category filter
            if category != "all items":
                if category == "general items" and item.item_type != "item":
                    continue
                elif category == "weapons" and item.item_type != "weapon":
                    continue
                elif category == "armor" and item.item_type != "armor":
                    continue
                elif category == "creatures/enemies" and item.item_type != "creature":
                    continue
                elif category == "quest items" and item.item_type != "quest":
                    continue
                elif category == "materials" and item.item_type != "material":
                    continue
                elif category == "consumables" and item.item_type != "consumable":
                    continue

            # Search filter
            if search_text:
                if (
                    search_text not in item.name.lower()
                    and search_text not in item.description.lower()
                    and search_text not in str(item.item_id)
                ):
                    continue

            self.filtered_items.append(item)

        self.populate_tree()
        self.update_details()

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double-click"""
        if item and item.data(0, Qt.ItemDataRole.UserRole):
            self.select_current_item()

    def select_current_item(self):
        """Select the current item and emit signal"""
        current_item = self.items_tree.currentItem()
        if current_item and current_item.data(0, Qt.ItemDataRole.UserRole):
            item_data = current_item.data(0, Qt.ItemDataRole.UserRole)
            self.item_selected.emit(item_data)

            # Close parent dialog if we're in one
            parent_dialog = self.parent()
            while parent_dialog and not isinstance(parent_dialog, QDialog):
                parent_dialog = parent_dialog.parent()
            if isinstance(parent_dialog, QDialog):
                parent_dialog.accept()

    def update_details(self):
        """Update the details panel with current selection"""
        current_item = self.items_tree.currentItem()
        if not current_item or not current_item.data(0, Qt.ItemDataRole.UserRole):
            self.details_name.setText("Select an item to view details")
            self.details_stats.setText("")
            self.select_btn.setEnabled(False)
            return

        item_data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not item_data:
            return

        # Update details
        self.details_name.setText(
            f"{item_data.get('icon', '')} {item_data.get('name', '')}"
        )
        self.select_btn.setEnabled(True)

        # Format stats
        stats = item_data.get("stats", {})
        if stats:
            stats_text = []
            for key, value in stats.items():
                formatted_key = key.replace("_", " ").title()
                stats_text.append(f"{formatted_key}: {value}")
            self.details_stats.setText("\n".join(stats_text))
        else:
            self.details_stats.setText(item_data.get("description", ""))

    def get_selected_item(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected item data"""
        current_item = self.items_tree.currentItem()
        if current_item:
            return current_item.data(0, Qt.ItemDataRole.UserRole)
        return None

    def set_filter_categories(self, categories: List[str]):
        """Set available filter categories"""
        self.category_combo.clear()
        self.category_combo.addItems(["All Items"] + categories)
        # If categories were specified, select the first one instead of "All Items"
        if categories:
            self.category_combo.setCurrentText(categories[0])
        self.filter_items()

    def load_from_data(self, items_data: List[Dict[str, Any]]):
        """Load items from external data source"""
        self.items_data = [ItemData.from_dict(item) for item in items_data]
        self.filtered_items = self.items_data.copy()
        self.populate_tree()


class ItemBrowserDialog(QDialog):
    """Dialog version of item browser for selection"""

    def __init__(
        self, parent=None, title="Select Item", categories=None, data_model=None
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # Create browser widget
        self.browser = ItemBrowserWidget(data_model=data_model)
        if categories:
            self.browser.set_filter_categories(categories)

        layout.addWidget(self.browser)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Connect signals
        self.browser.item_selected.connect(self.on_item_selected)

    def on_item_selected(self, item_data: Dict[str, Any]):
        """Handle item selection"""
        self.selected_item = item_data

    def get_selected_item(self) -> Optional[Dict[str, Any]]:
        """Get the selected item"""
        return getattr(self, "selected_item", None)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test dialog
    dialog = ItemBrowserDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        selected = dialog.get_selected_item()
        if selected:
            print(f"Selected item: {selected}")

    sys.exit(app.exec())
