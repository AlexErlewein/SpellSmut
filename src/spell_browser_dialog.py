"""
Spell Browser Dialog with Advanced Filtering

This dialog allows browsing, filtering, and selecting spells with a rich UI.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QComboBox, QGroupBox, QTextEdit,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from typing import Optional, Dict, Any
from pathlib import Path
import json

try:
    from TirganachReloaded.cff_editor.models.spell_creation_data import SpellCreationData
    from TirganachReloaded.cff_editor.models.spell_enums import MagicSchool, SpellType
except ImportError:
    print("Warning: Could not import spell models")


class SpellBrowserDialog(QDialog):
    """Advanced spell browser with filtering capabilities"""

    spellSelected = Signal(dict)  # Emits spell data dictionary when selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.spells = {}
        self.selected_spell_data = None

        self.setWindowTitle("Spell Browser")
        self.setMinimumSize(1000, 700)

        self.setup_ui()
        self.load_spells()
        self.populate_table()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)

        # Filter section
        filter_group = QGroupBox("Filters")
        filter_layout = QVBoxLayout()

        # Row 1: School and Type filters
        row1 = QHBoxLayout()

        row1.addWidget(QLabel("Magic School:"))
        self.school_filter = QComboBox()
        self.school_filter.addItem("All Schools", None)
        for school in MagicSchool:
            self.school_filter.addItem(school.name, school.value)
        self.school_filter.currentIndexChanged.connect(self.apply_filters)
        row1.addWidget(self.school_filter)

        row1.addWidget(QLabel("Spell Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types", None)
        for spell_type in SpellType:
            self.type_filter.addItem(spell_type.value.capitalize(), spell_type.value)
        self.type_filter.currentIndexChanged.connect(self.apply_filters)
        row1.addWidget(self.type_filter)

        row1.addStretch()
        filter_layout.addLayout(row1)

        # Row 2: Name search
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Search Name:"))
        self.name_search = QLineEdit()
        self.name_search.setPlaceholderText("Enter spell name...")
        self.name_search.textChanged.connect(self.apply_filters)
        row2.addWidget(self.name_search)

        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self.clear_filters)
        row2.addWidget(clear_btn)

        filter_layout.addLayout(row2)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Spell table
        self.spell_table = QTableWidget()
        self.spell_table.setColumnCount(7)
        self.spell_table.setHorizontalHeaderLabels([
            "ID", "Name", "School", "Type", "Levels", "Max DPS", "Range"
        ])
        self.spell_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.spell_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.spell_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.spell_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.spell_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.spell_table.doubleClicked.connect(self.accept)
        layout.addWidget(self.spell_table)

        # Spell details preview
        preview_group = QGroupBox("Spell Preview")
        preview_layout = QVBoxLayout()
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        preview_layout.addWidget(self.preview_text)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Status label
        self.status_label = QLabel("No spells loaded")
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        select_btn = QPushButton("Select Spell")
        select_btn.clicked.connect(self.accept)
        button_layout.addWidget(select_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def load_spells(self):
        """Load spells from the spells.json file"""
        spells_file = Path(__file__).parent / 'custom_spells' / 'spells.json'

        if spells_file.exists():
            try:
                with open(spells_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for spell_data in data:
                        spell = SpellCreationData.from_dict(spell_data)
                        self.spells[spell.spell_line_id] = spell

                self.status_label.setText(f"Loaded {len(self.spells)} spells")
            except Exception as e:
                self.status_label.setText(f"Error loading spells: {e}")
        else:
            self.status_label.setText("No spells file found - create some spells first!")

    def populate_table(self, filtered_spells=None):
        """Populate the spell table"""
        if filtered_spells is None:
            filtered_spells = self.spells

        self.spell_table.setRowCount(0)

        for spell_id, spell in sorted(filtered_spells.items()):
            row = self.spell_table.rowCount()
            self.spell_table.insertRow(row)

            # ID
            item = QTableWidgetItem(str(spell.spell_line_id))
            item.setData(Qt.UserRole, spell_id)
            self.spell_table.setItem(row, 0, item)

            # Name
            item = QTableWidgetItem(spell.spell_name)
            self.spell_table.setItem(row, 1, item)

            # School
            school_name = spell.magic_school.name if hasattr(spell.magic_school, 'name') else str(spell.magic_school)
            item = QTableWidgetItem(school_name)
            item.setForeground(self.get_school_color(spell.magic_school))
            self.spell_table.setItem(row, 2, item)

            # Type
            spell_type = spell.spell_type.value if hasattr(spell.spell_type, 'value') else str(spell.spell_type)
            self.spell_table.setItem(row, 3, QTableWidgetItem(spell_type.capitalize()))

            # Levels
            self.spell_table.setItem(row, 4, QTableWidgetItem(str(spell.num_levels)))

            # Max DPS
            max_dps = spell.levels[-1].dps if spell.levels else 0
            item = QTableWidgetItem(f"{max_dps:.1f}")
            self.spell_table.setItem(row, 5, item)

            # Range
            self.spell_table.setItem(row, 6, QTableWidgetItem(f"{spell.base_range:.1f}"))

        self.status_label.setText(f"Showing {len(filtered_spells)} of {len(self.spells)} spells")

    def get_school_color(self, school):
        """Get color for magic school"""
        colors = {
            MagicSchool.WHITE: QColor("#FFD700"),    # Gold
            MagicSchool.FIRE: QColor("#FF4500"),     # Red-Orange
            MagicSchool.ICE: QColor("#00BFFF"),      # Deep Sky Blue
            MagicSchool.BLACK: QColor("#8B008B"),    # Dark Magenta
            MagicSchool.MENTAL: QColor("#9370DB"),   # Medium Purple
            MagicSchool.EARTH: QColor("#8B4513"),    # Saddle Brown
        }
        return colors.get(school, QColor("#FFFFFF"))

    def apply_filters(self):
        """Apply current filters to the spell list"""
        filtered_spells = {}

        school_filter = self.school_filter.currentData()
        type_filter = self.type_filter.currentData()
        name_filter = self.name_search.text().lower()

        for spell_id, spell in self.spells.items():
            # School filter
            if school_filter is not None:
                if spell.magic_school.value != school_filter:
                    continue

            # Type filter
            if type_filter is not None:
                if spell.spell_type.value != type_filter:
                    continue

            # Name filter
            if name_filter:
                if name_filter not in spell.spell_name.lower():
                    continue

            filtered_spells[spell_id] = spell

        self.populate_table(filtered_spells)

    def clear_filters(self):
        """Clear all filters"""
        self.school_filter.setCurrentIndex(0)
        self.type_filter.setCurrentIndex(0)
        self.name_search.clear()

    def on_selection_changed(self):
        """Handle spell selection change"""
        selected_items = self.spell_table.selectedItems()
        if not selected_items:
            self.preview_text.clear()
            return

        # Get spell ID from first column
        row = selected_items[0].row()
        spell_id = self.spell_table.item(row, 0).data(Qt.UserRole)
        spell = self.spells.get(spell_id)

        if spell:
            self.selected_spell_data = spell.to_dict()
            self.show_spell_preview(spell)

    def show_spell_preview(self, spell: SpellCreationData):
        """Show spell preview in the text area"""
        html = f"""
        <h3>{spell.spell_name}</h3>
        <p><b>School:</b> {spell.magic_school.name} | <b>Type:</b> {spell.spell_type.value.capitalize()}</p>
        <p><b>Target:</b> {spell.target_type.value.capitalize()} |
           <b>Range:</b> {spell.base_range} |
           <b>AOE:</b> {spell.aoe_radius}</p>
        <p><b>Projectile:</b> {'Yes' if spell.has_projectile else 'No'} |
           <b>Duration:</b> {spell.duration}s</p>
        """

        if spell.levels:
            lvl1 = spell.levels[0]
            html += f"<p><b>Level 1:</b> Damage {lvl1.damage_min}-{lvl1.damage_max}, Mana {lvl1.mana_cost}, DPS {lvl1.dps:.1f}</p>"

            if len(spell.levels) > 1:
                lvl_max = spell.levels[-1]
                html += f"<p><b>Level {spell.num_levels}:</b> Damage {lvl_max.damage_min}-{lvl_max.damage_max}, Mana {lvl_max.mana_cost}, DPS {lvl_max.dps:.1f}</p>"

        if spell.description:
            html += f"<p><i>{spell.description}</i></p>"

        self.preview_text.setHtml(html)

    def get_selected_spell_data(self) -> Optional[Dict[str, Any]]:
        """Get the selected spell data"""
        return self.selected_spell_data
