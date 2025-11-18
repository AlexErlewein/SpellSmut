"""
Spell Browser - Browse and search original game spells from CFF files with collapsible level data

This dialog allows browsing, filtering, and selecting spells from the original game data
with detailed level progression information displayed in collapsible sections.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLineEdit, QLabel, QGroupBox, QTextEdit,
    QMessageBox, QHeaderView, QTabWidget, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from typing import Dict, Any, Optional, List
import json
from pathlib import Path

# Import the spell loading functionality
from populate_spell_templates import load_spells_from_json, load_spells_from_cff_extraction

try:
    from TirganachReloaded.cff_editor.models.spell_creation_data import SpellCreationData
    from TirganachReloaded.cff_editor.models.spell_enums import MagicSchool, SpellType
except ImportError:
    print("Warning: Could not import spell models, using basic functionality")


class SpellBrowser(QDialog):
    """Advanced spell browser for viewing original game spells with level data"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Spell Browser - Original Game Spells")
        self.setMinimumSize(1000, 700)

        # Data structures
        self.spell_data = {}  # Dictionary indexed by spell_id
        self.selected_spell = None
        self.selected_spell_id = None

        # Initialize UI
        self.init_ui()

        # Load spells
        self.load_spells()
        self.populate_spell_tree()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type to search spells by name, school, or type...")
        self.search_edit.textChanged.connect(self.filter_spells)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)

        # Main content area (split between tree and details)
        content_layout = QHBoxLayout()

        # Left side: Spell tree
        tree_group = QGroupBox("Spells")
        tree_layout = QVBoxLayout()

        self.spell_tree = QTreeWidget()
        self.spell_tree.setHeaderLabels(["Name", "School", "Type", "Levels", "ID"])
        self.spell_tree.setColumnWidth(0, 200)
        self.spell_tree.setColumnWidth(1, 100)
        self.spell_tree.setColumnWidth(2, 100)
        self.spell_tree.setColumnWidth(3, 60)
        self.spell_tree.setColumnWidth(4, 80)
        self.spell_tree.itemSelectionChanged.connect(self.on_spell_selected)
        self.spell_tree.itemDoubleClicked.connect(self.on_spell_double_clicked)
        tree_layout.addWidget(self.spell_tree)

        # Spell count label
        self.count_label = QLabel("Spells: 0")
        tree_layout.addWidget(self.count_label)

        tree_group.setLayout(tree_layout)
        content_layout.addWidget(tree_group, 2)

        # Right side: Spell details
        details_group = QGroupBox("Spell Details")
        details_layout = QVBoxLayout()

        # Use tab widget for different views
        self.tab_widget = QTabWidget()

        # General info tab
        self.general_info_text = QTextEdit()
        self.general_info_text.setReadOnly(True)
        self.tab_widget.addTab(self.general_info_text, "General")

        # Level progression tab
        self.level_info_text = QTextEdit()
        self.level_info_text.setReadOnly(True)
        self.tab_widget.addTab(self.level_info_text, "Level Progression")

        # Raw data tab
        self.raw_data_text = QTextEdit()
        self.raw_data_text.setReadOnly(True)
        self.tab_widget.addTab(self.raw_data_text, "Raw Data")

        details_layout.addWidget(self.tab_widget)

        details_group.setLayout(details_layout)
        content_layout.addWidget(details_group, 1)

        layout.addLayout(content_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        self.open_forge_btn = QPushButton("Open in Spell Forge")
        self.open_forge_btn.setEnabled(False)
        self.open_forge_btn.clicked.connect(self.open_spell_forge)
        button_layout.addWidget(self.open_forge_btn)

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

    def load_spells(self):
        """Load spells from both template JSON and CFF extraction"""
        try:
            # Load template spells from JSON
            template_spells = load_spells_from_json()
            print(f"Loaded {len(template_spells)} template spells")

            # Load original game spells from CFF extraction
            cff_spells = load_spells_from_cff_extraction()
            print(f"Loaded {len(cff_spells)} original game spells from CFF")

            # Combine all spells
            self.spell_data = {**template_spells, **cff_spells}

            total_spells = len(self.spell_data)
            print(f"Total spells available: {total_spells} ({len(template_spells)} templates + {len(cff_spells)} game)")

        except Exception as e:
            print(f"Error loading spells: {e}")
            QMessageBox.warning(
                self,
                "Loading Error",
                f"Failed to load spells: {e}"
            )

    def populate_spell_tree(self):
        """Populate the spell tree with all spells grouped by magic school"""
        self.spell_tree.clear()

        total_spells = len(self.spell_data)

        # If no spells at all, show helpful message
        if total_spells == 0:
            placeholder_item = QTreeWidgetItem(
                self.spell_tree,
                ["No spells found", "", "", "", ""]
            )
            placeholder_item.setForeground(0, Qt.GlobalColor.gray)

            help_item = QTreeWidgetItem(
                self.spell_tree,
                ["Add some spells to get started!", "", "", "", ""]
            )
            help_item.setForeground(0, Qt.GlobalColor.blue)

            self.count_label.setText("Spells: 0")
            return

        # Group spells by magic school
        spells_by_school = {}
        for spell_id, spell_info in self.spell_data.items():
            school = spell_info.get('magic_school', 'unknown')
            # Convert integer school values to readable names
            if isinstance(school, int):
                school_names = {
                    0: 'WHITE', 1: 'FIRE', 2: 'ICE', 3: 'BLACK', 4: 'MENTAL', 5: 'EARTH',
                    100: 'LIGHT_COMBAT', 101: 'HEAVY_COMBAT', 102: 'RANGED_COMBAT',
                    110: 'WHITE_MAGIC', 111: 'LIFE', 112: 'NATURE', 113: 'BOONS',
                    120: 'ELEMENTAL_MAGIC', 121: 'FIRE', 122: 'ICE', 123: 'EARTH',
                    130: 'MIND_MAGIC', 131: 'ENCHANTMENT', 132: 'OFFENSIVE', 133: 'DEFENSIVE',
                    140: 'BLACK_MAGIC', 141: 'DEATH', 142: 'NECROMANCY', 143: 'CURSE'
                }
                readable_school = school_names.get(school, f'UNKNOWN({school})')
            else:
                readable_school = school
            if readable_school not in spells_by_school:
                spells_by_school[readable_school] = []
            spells_by_school[readable_school].append((spell_id, spell_info))

        # Create school categories
        for readable_school, spells in sorted(spells_by_school.items()):
            school_node = QTreeWidgetItem(
                self.spell_tree,
                [f"{readable_school} Magic ({len(spells)})", readable_school, "", "", ""]
            )
            school_node.setExpanded(True)

            # Sort spells by name within each school
            spells.sort(key=lambda x: x[1].get("spell_name", "Unnamed"))

            # Add spell items under each school
            for spell_id, spell_info in spells:
                name = spell_info.get("spell_name", "Unnamed Spell")
                
                # Get original school value for the tree item
                original_school = spell_info.get('magic_school', 'unknown')
                spell_type = spell_info.get("spell_type", "unknown")
                num_levels = len(spell_info.get("levels", []))

                item = QTreeWidgetItem(
                    school_node,
                    [name, str(original_school), spell_type, str(num_levels), str(spell_id)]
                )
                # Store spell_id in user data
                item.setData(0, Qt.ItemDataRole.UserRole, spell_id)

        # Update count
        self.count_label.setText(f"Spells: {total_spells}")

    def filter_spells(self, search_text: str):
        """Filter spells based on search text"""
        search_text = search_text.lower()

        # If search is empty, show all
        if not search_text:
            for i in range(self.spell_tree.topLevelItemCount()):
                category = self.spell_tree.topLevelItem(i)
                category.setHidden(False)
                for j in range(category.childCount()):
                    category.child(j).setHidden(False)
            return

        # Filter spells
        visible_count = 0
        for i in range(self.spell_tree.topLevelItemCount()):
            category = self.spell_tree.topLevelItem(i)
            category_has_visible = False

            for j in range(category.childCount()):
                item = category.child(j)
                spell_id = item.data(0, Qt.ItemDataRole.UserRole)

                if spell_id is not None:
                    spell_info = self.spell_data.get(spell_id, {})

                    # Search in name, school, type
                    name = spell_info.get("spell_name", "").lower()
                    
                    # Handle school - convert to readable format for search
                    original_school = spell_info.get("magic_school", "unknown")
                    if isinstance(original_school, int):
                        school_names = {
                            0: 'WHITE', 1: 'FIRE', 2: 'ICE', 3: 'BLACK', 4: 'MENTAL', 5: 'EARTH',
                            100: 'LIGHT_COMBAT', 101: 'HEAVY_COMBAT', 102: 'RANGED_COMBAT',
                            110: 'WHITE_MAGIC', 111: 'LIFE', 112: 'NATURE', 113: 'BOONS',
                            120: 'ELEMENTAL_MAGIC', 121: 'FIRE', 122: 'ICE', 123: 'EARTH',
                            130: 'MIND_MAGIC', 131: 'ENCHANTMENT', 132: 'OFFENSIVE', 133: 'DEFENSIVE',
                            140: 'BLACK_MAGIC', 141: 'DEATH', 142: 'NECROMANCY', 143: 'CURSE'
                        }
                        readable_school = school_names.get(original_school, f'UNKNOWN({original_school})')
                    else:
                        readable_school = str(original_school)
                    
                    school = readable_school.lower()
                    spell_type = spell_info.get("spell_type", "").lower()
                    description = spell_info.get("description", "").lower()

                    matches = (
                        search_text in name or
                        search_text in school or
                        search_text in spell_type or
                        search_text in description or
                        search_text in str(spell_id)
                    )

                    item.setHidden(not matches)
                    if matches:
                        category_has_visible = True
                        visible_count += 1

            category.setHidden(not category_has_visible)

        self.count_label.setText(f"Spells: {visible_count} / {len(self.spell_data)}")

    def on_spell_selected(self):
        """Handle spell selection"""
        selected_items = self.spell_tree.selectedItems()
        if not selected_items:
            self.selected_spell = None
            self.selected_spell_id = None
            self.general_info_text.clear()
            self.level_info_text.clear()
            self.raw_data_text.clear()
            self.open_forge_btn.setEnabled(False)
            self.select_btn.setEnabled(False)
            return

        item = selected_items[0]
        spell_id = item.data(0, Qt.ItemDataRole.UserRole)

        # Skip if this is a category node
        if spell_id is None:
            return

        self.selected_spell_id = spell_id
        self.selected_spell = self.spell_data.get(spell_id)

        # Enable action buttons
        self.open_forge_btn.setEnabled(True)
        self.select_btn.setEnabled(True)

        # Display spell details
        self.display_spell_details(self.selected_spell)

    def display_spell_details(self, spell_info: Dict[str, Any]):
        """Display detailed information about selected spell with collapsible level data"""
        if not spell_info:
            return

        # General info tab
        source_badge = "📝 Template" if spell_info.get('is_template', False) else "🎮 Game"
        general_details = f"<h2>{spell_info.get('spell_name', 'Unnamed Spell')} <small style='color: gray;'>({source_badge})</small></h2>"

        if spell_info.get('description'):
            general_details += f"<p><b>Description:</b><br>{spell_info['description']}</p>"

        general_details += f"<p><b>ID:</b> {spell_info.get('spell_line_id', 'Unknown')}</p>"
        
        # Handle school - convert integer to readable name
        original_school = spell_info.get('magic_school', 'unknown')
        if isinstance(original_school, int):
            school_names = {
                0: 'WHITE', 1: 'FIRE', 2: 'ICE', 3: 'BLACK', 4: 'MENTAL', 5: 'EARTH',
                100: 'LIGHT_COMBAT', 101: 'HEAVY_COMBAT', 102: 'RANGED_COMBAT',
                110: 'WHITE_MAGIC', 111: 'LIFE', 112: 'NATURE', 113: 'BOONS',
                120: 'ELEMENTAL_MAGIC', 121: 'FIRE', 122: 'ICE', 123: 'EARTH',
                130: 'MIND_MAGIC', 131: 'ENCHANTMENT', 132: 'OFFENSIVE', 133: 'DEFENSIVE',
                140: 'BLACK_MAGIC', 141: 'DEATH', 142: 'NECROMANCY', 143: 'CURSE'
            }
            readable_school = school_names.get(original_school, f'UNKNOWN({original_school})')
        else:
            readable_school = str(original_school)
        
        general_details += f"<p><b>School:</b> {readable_school} Magic</p>"
        general_details += f"<p><b>Type:</b> {spell_info.get('spell_type', 'unknown').capitalize()}</p>"
        general_details += f"<p><b>Target:</b> {spell_info.get('target_type', 'single').capitalize()}</p>"
        general_details += f"<p><b>Range:</b> {spell_info.get('base_range', 0)}m</p>"
        general_details += f"<p><b>AOE Radius:</b> {spell_info.get('aoe_radius', 0)}m</p>"
        general_details += f"<p><b>Duration:</b> {spell_info.get('duration', 0)}s</p>"
        general_details += f"<p><b>Has Projectile:</b> {'Yes' if spell_info.get('has_projectile', False) else 'No'}</p>"

        # Requirements
        requirements = spell_info.get('requirements', [])
        if requirements:
            general_details += "<h3>Requirements</h3><ul>"
            for req in requirements:
                req_name = req.get('requirement_name', 'Unknown')
                req_level = req.get('requirement_level', 0)
                general_details += f"<li>{req_name}: Level {req_level}</li>"
            general_details += "</ul>"

        self.general_info_text.setHtml(general_details)

        # Level progression tab - show detailed progression data
        level_details = f"<h2>Level Progression for {spell_info.get('spell_name', 'Unnamed Spell')}</h2>"
        
        levels = spell_info.get('levels', [])
        if levels:
            level_details += f"<p><b>Total Levels:</b> {len(levels)}</p>"
            
            for i, level_info in enumerate(levels):
                level_num = i + 1
                level_details += f"<h3>Level {level_num}</h3>"
                
                # Create a table for level data
                level_details += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
                
                # Add various stats to the table
                stats = [
                    ("Mana Cost", level_info.get('mana_cost', 0)),
                    ("Cast Time", f"{level_info.get('cast_time', 0)}s"),
                    ("Cooldown", f"{level_info.get('cooldown', 0)}s"),
                    ("Min Damage", level_info.get('damage_min', 0)),
                    ("Max Damage", level_info.get('damage_max', 0)),
                    ("DPS", f"{level_info.get('dps', 0):.2f}"),
                    ("Effect Power", level_info.get('effect_power', 0)),
                    ("Effect Range", f"{level_info.get('effect_range', 0)}m"),
                    ("Projectile Speed", f"{level_info.get('projectile_speed', 0)}m/s"),
                    ("Range", f"{level_info.get('range', 0)}m"),
                ]
                
                for stat_name, stat_value in stats:
                    level_details += f"<tr><td style='padding: 5px; font-weight: bold;'>{stat_name}</td><td style='padding: 5px;'>{stat_value}</td></tr>"
                
                level_details += "</table><br>"
        else:
            level_details += "<p>No level progression data available.</p>"
        
        self.level_info_text.setHtml(level_details)

        # Raw data tab
        raw_data = f"<h2>Raw Spell Data for {spell_info.get('spell_name', 'Unnamed Spell')}</h2>"
        raw_data += f"<pre>{json.dumps(spell_info, indent=2, ensure_ascii=False)}</pre>"
        self.raw_data_text.setHtml(raw_data)

    def on_spell_double_clicked(self, item, column):
        """Handle double-click on spell (same as selecting and clicking OK)"""
        spell_id = item.data(0, Qt.ItemDataRole.UserRole)
        if spell_id is not None:
            self.accept()

    def open_spell_forge(self):
        """Open the selected spell in the Spell Forge"""
        if not self.selected_spell_id:
            return

        # For now, just select and close to pass the spell data back
        # In a real implementation, this would open the spell forge with the selected spell
        self.accept()

    def get_selected_spell_data(self) -> Optional[Dict[str, Any]]:
        """Get the selected spell as a dictionary"""
        return self.selected_spell

    def get_selected_spell_id(self) -> Optional[int]:
        """Get the selected spell ID"""
        return self.selected_spell_id


class CFFSpellBrowser(SpellBrowser):
    """Specialized spell browser that loads only CFF extracted spells"""
    
    def load_spells(self):
        """Load only spells from CFF extraction"""
        try:
            # Load original game spells from CFF extraction
            self.spell_data = load_spells_from_cff_extraction()
            
            total_spells = len(self.spell_data)
            print(f"Loaded {total_spells} original game spells from CFF")
            
            if total_spells == 0:
                print("Warning: No spells loaded from CFF extraction. Check that extracted_spells directory exists.")

        except Exception as e:
            print(f"Error loading CFF spells: {e}")
            QMessageBox.warning(
                self,
                "Loading Error",
                f"Failed to load CFF spells: {e}"
            )


def open_spell_browser(parent=None, cff_only=False):
    """Convenience function to open the spell browser dialog"""
    if cff_only:
        dialog = CFFSpellBrowser(parent)
    else:
        dialog = SpellBrowser(parent)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_selected_spell_data(), dialog.get_selected_spell_id()
    return None, None


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create and show the spell browser
    browser = SpellBrowser()
    browser.show()
    
    sys.exit(app.exec())