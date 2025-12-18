"""
Armor Browser Dialog - Browse and select existing armor for editing
"""

import json
from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ..logging_config import get_logger


class ArmorBrowserDialog(QDialog):
    """Browse and select existing armor pieces"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.setWindowTitle("Select Armor to Edit")
        self.setModal(True)
        self.resize(900, 600)

        self.selected_armor = None
        self.armor_data = self.load_armor_data()
        self.logger.debug(f"Loaded {len(self.armor_data)} armor pieces")

        self.init_ui()
        self.populate_table()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()

        # Search/Filter section
        search_layout = QHBoxLayout()

        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_armor)
        search_layout.addWidget(self.search_edit)

        search_layout.addWidget(QLabel("Slot:"))
        self.slot_filter = QComboBox()
        self.slot_filter.addItem("All Slots")
        self.slot_filter.addItems(
            [
                "Helmet",
                "Chest Armor",
                "Leg Armor",
                "Boots",
                "Right Ring",
                "Left Ring",
                "Shield",
            ]
        )
        self.slot_filter.currentTextChanged.connect(self.filter_armor)
        search_layout.addWidget(self.slot_filter)

        search_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types")
        self.type_filter.addItems(["Cloth", "Leather", "Chain", "Plate", "Magic"])
        self.type_filter.currentTextChanged.connect(self.filter_armor)
        search_layout.addWidget(self.type_filter)

        layout.addLayout(search_layout)

        # Armor table
        self.armor_table = QTableWidget(0, 9)
        self.armor_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Name",
                "Slot",
                "Type",
                "Material",
                "Armor",
                "Tier",
                "Stats",
                "Requirements",
            ]
        )
        self.armor_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.armor_table.setSelectionMode(QTableWidget.SingleSelection)
        self.armor_table.doubleClicked.connect(self.accept)
        self.armor_table.setSortingEnabled(True)

        # Make columns resize properly
        header = self.armor_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        layout.addWidget(self.armor_table)

        # Statistics
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Total armor pieces: 0")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load Selected Armor")
        self.load_btn.clicked.connect(self.accept)
        self.load_btn.setEnabled(False)  # Disabled until selection

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # Connect table selection
        self.armor_table.itemSelectionChanged.connect(self.on_selection_changed)

        self.setLayout(layout)

    def load_armor_data(self) -> list:
        """Load armor data from CFF loader with fallback to JSON"""
        try:
            # Try to load from Orthancs Schmiede CFF armor loader first
            import sys
            from pathlib import Path

            # Add the src directory to Python path to access orthancs_schmiede
            project_root = Path(__file__).parent.parent.parent.parent.parent
            sys.path.insert(0, str(project_root / "src"))

            from OrthancsSchmiede.cff_armor_loader import CFFArmorLoader

            armor_loader = CFFArmorLoader()
            armor_data = armor_loader.load_all_armor()

            if armor_data:
                # Convert dict values to list for the dialog
                armor_list = list(armor_data.values())
                if len(armor_list) > 0:
                    return armor_list

        except Exception as e:
            self.logger.warning(f"Failed to load from CFF armor loader: {e}")

        # Fallback to JSON
        try:
            with open("src/TirganachReloaded/enhanced_armor.json", "r") as f:
                json_data = json.load(f)
                # Handle different JSON structures
                if isinstance(json_data, dict):
                    if "armors" in json_data:
                        return json_data["armors"]
                    elif isinstance(json_data.get("armors", []), list):
                        return json_data["armors"]
                    else:
                        return list(json_data.values()) if json_data else []
                return json_data if isinstance(json_data, list) else []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            QMessageBox.warning(
                self,
                "Load Error",
                f"Failed to load armor data from CFF or JSON: {str(e)}",
            )
            return []

    def populate_table(self, armor_list=None):
        """Populate the armor table"""
        if armor_list is None:
            armor_list = self.armor_data

        self.armor_table.setRowCount(0)  # Clear existing rows

        for armor in armor_list:
            row_count = self.armor_table.rowCount()
            self.armor_table.insertRow(row_count)

            # ID
            self.armor_table.setItem(
                row_count, 0, QTableWidgetItem(str(armor.get("item_id", 0)))
            )

            # Name
            self.armor_table.setItem(
                row_count, 1, QTableWidgetItem(armor.get("name", "Unknown"))
            )

            # Slot (map from item_subtype or infer from context)
            slot_name = self.get_slot_name(armor)
            self.armor_table.setItem(row_count, 2, QTableWidgetItem(slot_name))

            # Type (infer from armor value and other stats)
            armor_type = self.infer_armor_type(armor)
            self.armor_table.setItem(row_count, 3, QTableWidgetItem(armor_type))

            # Material (placeholder - would need material mapping)
            self.armor_table.setItem(row_count, 4, QTableWidgetItem("Unknown"))

            # Armor value
            armor_value = armor.get("armor", 0)
            self.armor_table.setItem(row_count, 5, QTableWidgetItem(str(armor_value)))

            # Tier (infer from armor value and other factors)
            tier = self.infer_tier(armor)
            self.armor_table.setItem(row_count, 6, QTableWidgetItem(tier))

            # Total stats
            total_stats = self.calculate_total_stats(armor)
            self.armor_table.setItem(row_count, 7, QTableWidgetItem(str(total_stats)))

            # Requirements
            requirements_text = self.format_requirements(armor)
            self.armor_table.setItem(row_count, 8, QTableWidgetItem(requirements_text))

        # Update statistics
        self.update_stats(len(armor_list))

    def get_slot_name(self, armor: dict) -> str:
        """Get human-readable slot name from armor data"""
        subtype = armor.get("item_subtype", "")

        # Map subtypes to slots
        slot_map = {
            "HEAD": "Helmet",
            "CHEST": "Chest Armor",
            "LEGS": "Leg Armor",
            "FEET": "Boots",
            "RIGHT_RING": "Right Ring",
            "LEFT_RING": "Left Ring",
            "SHIELD": "Shield",
        }

        return slot_map.get(subtype, "Unknown")

    def infer_armor_type(self, armor: dict) -> str:
        """Infer armor type from stats"""
        armor_value = armor.get("armor", 0)

        if armor_value >= 50:
            return "Plate"
        elif armor_value >= 30:
            return "Chain"
        elif armor_value >= 15:
            return "Leather"
        elif armor_value >= 5:
            return "Cloth"
        else:
            # Check for magic stats
            magic_stats = (
                armor.get("intelligence", 0)
                + armor.get("wisdom", 0)
                + armor.get("mana", 0)
            )
            if magic_stats > 0:
                return "Magic"
            return "Cloth"

    def infer_tier(self, armor: dict) -> str:
        """Infer armor tier from stats"""
        armor_value = armor.get("armor", 0)
        total_stats = self.calculate_total_stats(armor)

        # Simple tier inference
        if armor_value >= 60 or total_stats >= 20:
            return "Epic"
        elif armor_value >= 40 or total_stats >= 10:
            return "Rare"
        elif armor_value >= 20 or total_stats >= 5:
            return "Uncommon"
        else:
            return "Common"

    def calculate_total_stats(self, armor: dict) -> int:
        """Calculate total stat bonuses"""
        return (
            armor.get("strength", 0)
            + armor.get("stamina", 0)
            + armor.get("agility", 0)
            + armor.get("dexterity", 0)
            + armor.get("intelligence", 0)
            + armor.get("wisdom", 0)
            + armor.get("charisma", 0)
        )

    def format_requirements(self, armor: dict) -> str:
        """Format school requirements for display - matches weapon browser formatting"""
        # Get requirements data (same as weapon browser)
        req = armor.get("requirements", {}) or {}
        school_reqs = req.get("school_requirements", []) or []

        if school_reqs:
            # Use same formatting logic as weapon browser
            def fmt_school(name: str) -> str:
                s = str(name)
                if "." in s:
                    s = s.split(".")[-1]
                return s.replace("_", " ").title()

            parts = [
                f"{fmt_school(sr.get('requirement_school', ''))} L{sr.get('level', 0)}"
                for sr in school_reqs
            ]
            return ", ".join(parts)
        else:
            # Show level only if present, otherwise '-'
            lvl = req.get("level", None)
            return f"Level {lvl}" if lvl else "-"

    def filter_armor(self):
        """Filter armor based on search and filters"""
        search_text = self.search_edit.text().lower()
        slot_filter = self.slot_filter.currentText()
        type_filter = self.type_filter.currentText()

        filtered = []

        for armor in self.armor_data:
            # Text search
            if search_text and search_text not in armor.get("name", "").lower():
                continue

            # Slot filter
            if slot_filter != "All Slots":
                armor_slot = self.get_slot_name(armor)
                if slot_filter.lower() not in armor_slot.lower():
                    continue

            # Type filter
            if type_filter != "All Types":
                armor_type = self.infer_armor_type(armor)
                if type_filter.lower() not in armor_type.lower():
                    continue

            filtered.append(armor)

        self.populate_table(filtered)

    def on_selection_changed(self):
        """Handle table selection changes"""
        selected_rows = self.armor_table.selectedIndexes()
        self.load_btn.setEnabled(len(selected_rows) > 0)

    def update_stats(self, count: int):
        """Update statistics display"""
        self.stats_label.setText(f"Showing {count} armor pieces")

    def get_selected_armor(self) -> Optional[dict]:
        """Get the selected armor data"""
        selected_rows = self.armor_table.selectedIndexes()
        if not selected_rows:
            return None

        row = selected_rows[0].row()
        armor_id_item = self.armor_table.item(row, 0)
        if not armor_id_item:
            return None

        armor_id = int(armor_id_item.text())

        # Find the armor in our data
        for armor in self.armor_data:
            if armor.get("item_id") == armor_id:
                return armor

        return None

    def accept(self):
        """Handle dialog acceptance"""
        self.selected_armor = self.get_selected_armor()
        if self.selected_armor:
            super().accept()
        else:
            QMessageBox.warning(
                self, "No Selection", "Please select an armor piece to edit."
            )
