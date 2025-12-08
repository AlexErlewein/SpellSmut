"""
Enhanced weapon browser with CFF loading and German localization support
"""

import json
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QSplitter,
    QScrollArea,
    QWidget,
    QMessageBox,
    QHeaderView,
    QApplication,
    QCheckBox
)

from ..exporters.weapon_loader import WeaponLoader
from ..shared.gamedata_resolver import find_gamedata_path
from ..models.weapon_creation_data import (
    DamageCategory,
    DamageType,
    Rarity,
    WeaponHands,
    WeaponCreationData,
    WeaponRequirements,
)

# Import Language enum for localization
try:
    from ...tirganach.types import Language
except ImportError:
    # Define a fallback Language enum if the import fails
    from enum import Enum
    class Language(Enum):
        GERMAN = 0
        ENGLISH = 1
        FRENCH = 2
        SPANISH = 3
        ITALIAN = 4


def find_json_data_path():
    json_path = Path(__file__).parent.parent.parent / "enhanced_weapons.json"
    return str(json_path) if json_path.exists() else None

class EnhancedWeaponBrowser(QDialog):
    """Enhanced weapon browser dialog with detailed weapon inspection"""

    def __init__(self, parent=None, gamedata_path_override=None):
        super().__init__(parent)
        self.setWindowTitle("Enhanced Weapon Browser")
        self.setMinimumSize(QSize(1400, 800))
        self.weapon_loader = WeaponLoader()
        self.weapons_data = {}
        self.selected_weapon = None
        self.gamedata_path_override = gamedata_path_override
        
        # Initialize localization support
        self.current_language = Language.GERMAN  # Default to German
        self.gamedata = None
        self.logger = None  # Initialize logger attribute
        self._init_localization()
        
        # Load weapon data from CFF first, with JSON fallback
        self.load_weapons_from_cff()
        
        self.init_ui()
        self.populate_item_tree()

    def _init_localization(self):
        """Initialize localization support from GameData"""
        try:
            gamedata_path_str = self.gamedata_path_override or find_gamedata_path()
            if gamedata_path_str:
                try:
                    from ...tirganach import GameData
                    self.gamedata = GameData(gamedata_path_str)
                    print(f"Loaded GameData from {gamedata_path_str} for localization")
                except ImportError:
                    import sys
                    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
                    try:
                        from tirganach import GameData
                        self.gamedata = GameData(gamedata_path_str)
                        print(f"Loaded GameData from {gamedata_path_str} for localization")
                    except ImportError:
                        print("Could not import GameData from tirganach module")
            else:
                print("GameData.cff not found in any of the expected locations")
        except Exception as e:
            print(f"Warning: Could not initialize GameData for localization: {e}")
            import traceback
            traceback.print_exc()

    def load_weapons_from_cff(self):
        """Load weapons directly from GameData.cff for consistent localization"""
        try:
            gamedata_path_str = self.gamedata_path_override or find_gamedata_path()
            if gamedata_path_str:
                from ...tirganach import GameData
                gamedata = GameData(gamedata_path_str)
                
                # Load weapons from GameData
                for weapon in gamedata.weapons:
                    if hasattr(weapon, 'item') and weapon.item:  # Ensure item data exists
                        weapon_dict = {
                            'item_id': weapon.item_id,
                            'name': weapon.item.name,
                            'name_id': weapon.item.name_id,  # Critical for localization
                            'item_type': 'EQUIPMENT',
                            'item_subtype': 'WEAPON',
                            'weapon_type_id': weapon.weapon_type,
                            'weapon_material_id': weapon.material,
                            'min_damage': weapon.min_damage,
                            'max_damage': weapon.max_damage,
                            'attack_speed': weapon.speed,
                            'min_range': weapon.min_range,
                            'max_range': weapon.max_range,
                            'attack_arc': getattr(weapon, 'attack_arc', 90),
                            'critical_chance': getattr(weapon, 'critical_chance', 5.0),
                            'armor_penetration': getattr(weapon, 'armor_penetration', 0.0),
                            'knockback_chance': getattr(weapon, 'knockback_chance', 0.0),
                            'selling_price': weapon.item.selling_price if hasattr(weapon.item, 'selling_price') else 0,
                            'buying_price': weapon.item.buying_price if hasattr(weapon.item, 'buying_price') else 0,
                            'item_set_id': weapon.item.item_set_id if hasattr(weapon.item, 'item_set_id') else 0,
                            'data_source': 'CFF',
                        }

                        # Try to get type and material names from GameData
                        try:
                            type_names = gamedata.weapon_type_names.where(weapon_type_id=weapon.weapon_type)
                            if type_names:
                                weapon_dict['weapon_type_name'] = type_names[0].name
                        except:
                            weapon_dict['weapon_type_name'] = f"Weapon Type {weapon.weapon_type}"

                        try:
                            material_names = gamedata.weapon_material_names.where(weapon_material_id=weapon.material)
                            if material_names:
                                weapon_dict['weapon_material_name'] = material_names[0].name
                        except:
                            weapon_dict['weapon_material_name'] = f"Material {weapon.material}"

                        # Try to get UI handle
                        try:
                            item_ui_handles = [ui for ui in gamedata.item_ui if ui.item_id == weapon.item_id]
                            if item_ui_handles and item_ui_handles[0].item_ui_handle:
                                weapon_dict['ui_handle'] = item_ui_handles[0].item_ui_handle.strip()
                            else:
                                weapon_dict['ui_handle'] = f"icon_{weapon.item_id}"
                        except:
                            weapon_dict['ui_handle'] = f"icon_{weapon.item_id}"

                        # Try to get school requirements from item_requirements
                        try:
                            if hasattr(gamedata, 'item_requirements'):
                                item_reqs = gamedata.item_requirements.where(item_id=weapon.item_id)
                                if item_reqs:
                                    school_reqs = [
                                        {
                                            'requirement_school': str(req.requirement_school),
                                            'level': getattr(req, 'level', 0),
                                            'requirement_number': getattr(req, 'requirement_number', 0),
                                        }
                                        for req in item_reqs
                                    ]
                                    weapon_dict['requirements'] = {
                                        'level': max([getattr(req, 'level', 0) for req in item_reqs]) if item_reqs else 1,
                                        'school_requirements': school_reqs,
                                        'strength': 0,
                                        'dexterity': 0,
                                        'intelligence': 0,
                                    }
                                else:
                                    weapon_dict['requirements'] = {
                                        'level': 1,
                                        'school_requirements': [],
                                        'strength': 0,
                                        'dexterity': 0,
                                        'intelligence': 0,
                                    }
                        except Exception:
                            weapon_dict['requirements'] = {
                                'level': 1,
                                'school_requirements': [],
                                'strength': 0,
                                'dexterity': 0,
                                'intelligence': 0,
                            }

                        # Add to weapons data
                        self.weapons_data[weapon.item_id] = weapon_dict

                print(f"EnhancedWeaponBrowser loaded {len(self.weapons_data)} weapons from GameData.cff with proper localization IDs")
            else:
                print("GameData.cff not found in expected locations")
                # Fallback loading from JSON
                json_data_path = find_json_data_path()
                if json_data_path:
                    with open(json_data_path, 'r') as f:
                        weapons_list = json.load(f)
                    
                    # Convert list to dict with item_id as key
                    for weapon_dict in weapons_list:
                        weapon_dict['data_source'] = 'JSON'
                        # Ensure required fields exist
                        weapon_dict.setdefault('requirements', {
                            'level': 1,
                            'school_requirements': [],
                            'strength': 0,
                            'dexterity': 0,
                            'intelligence': 0,
                        })
                        self.weapons_data[weapon_dict['item_id']] = weapon_dict
                    
                    print(f"Loaded {len(self.weapons_data)} weapons from {json_data_path}")
                else:
                    print("Both GameData.cff and enhanced_weapons.json not found")
                
        except Exception as e:
            print(f"Error loading weapons from GameData.cff: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to JSON
            json_data_path = find_json_data_path()
            if json_data_path:
                with open(json_data_path, 'r') as f:
                    weapons_list = json.load(f)
                
                # Convert list to dict with item_id as key
                for weapon_dict in weapons_list:
                    weapon_dict['data_source'] = 'JSON'
                    self.weapons_data[weapon_dict['item_id']] = weapon_dict
                
                print(f"Loaded {len(self.weapons_data)} weapons from {json_data_path} (fallback)")
            else:
                print("GameData.cff and enhanced_weapons.json files not found")

    def get_localised_text(self, text_id: int) -> str:
        """Return localized text for current language by text_id, with fallback to English."""
        if not self.gamedata or not text_id:
            return ""
        try:
            # Try to get the localized text in the current language (German)
            rows = self.gamedata.localisation.where(text_id=text_id, language=self.current_language)
            if rows:
                localized_text = getattr(rows[0], 'text', '') or ''
                if localized_text:
                    return localized_text
        except Exception as e:
            print(f"Error getting localized text for ID {text_id} in German: {e}")
            pass
        
        # Fallback: try English
        try:
            rows_en = self.gamedata.localisation.where(text_id=text_id, language=Language.ENGLISH)
            if rows_en:
                localized_text = getattr(rows_en[0], 'text', '') or ''
                if localized_text:
                    return localized_text
        except Exception as e:
            print(f"Error getting localized text for ID {text_id} in English: {e}")
            pass
        
        return ""

    def get_display_name(self, info, is_weapon: bool) -> str:
        """Resolve display name from CFF localization by name_id, fallback to stored name."""
        # Check if info is a dictionary or an object
        if isinstance(info, dict):
            name_id = info.get('name_id', 0)
            loc = self.get_localised_text(name_id) if name_id else ''
            if loc:
                return loc
            # Fallback to existing fields
            if is_weapon:
                return info.get('name', info.get('weapon_name', f"Weapon {info.get('item_id', 'Unknown')}"))
            else:
                return info.get('name', info.get('armor_name', f"Armor {info.get('item_id', 'Unknown')}"))
        else:
            # It's an object (likely WeaponCreationData)
            name_id = getattr(info, 'name_id', 0)
            loc = self.get_localised_text(name_id) if name_id else ''
            if loc:
                return loc
            # Fallback to existing fields
            if is_weapon:
                return getattr(info, 'name', getattr(info, 'weapon_name', f"Weapon {getattr(info, 'id', 'Unknown')}"))
            else:
                return getattr(info, 'name', getattr(info, 'armor_name', f"Armor {getattr(info, 'id', 'Unknown')}"))

    def init_ui(self):
        """Initialize the enhanced user interface"""
        layout = QVBoxLayout(self)
        
        # Header with search
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Search Weapons:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search weapons by name...")
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        header_layout.addWidget(self.search_edit)
        
        # Type filter
        header_layout.addWidget(QLabel("Filter Type:"))
        self.type_filter = QLineEdit()
        self.type_filter.setPlaceholderText("Filter by weapon type...")
        self.type_filter.textChanged.connect(self.on_filter_changed)
        header_layout.addWidget(self.type_filter)

        # Custom ID toggle
        self.only_custom_checkbox = QCheckBox("Show only custom (10000–19999)")
        self.only_custom_checkbox.toggled.connect(lambda _: self.apply_filter(self.search_edit.text(), self.type_filter.text()))
        header_layout.addWidget(self.only_custom_checkbox)
        
        layout.addLayout(header_layout)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left - Weapon tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        tree_group = QGroupBox("Weapons")
        tree_layout = QVBoxLayout(tree_group)

        self.item_tree = QTreeWidget()
        self.item_tree.setHeaderLabels(["Name", "Type", "ID", "Damage"])
        self.item_tree.itemSelectionChanged.connect(self.on_item_selection_changed)

        # Dark theme tree styling
        self.item_tree.setStyleSheet("""
            QTreeWidget {
                font-size: 12px;
                background-color: #1e1e1e;
                color: #e0e0e0;
                border: 1px solid #3c3c3c;
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
        left_layout.addWidget(tree_group)
        splitter.addWidget(left_widget)

        # Right - Weapon details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        details_group = QGroupBox("Weapon Details")
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
        splitter.setSizes([700, 700])

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        select_btn = QPushButton("Select Weapon")
        select_btn.clicked.connect(self.accept)
        select_btn.setStyleSheet("padding: 8px; font-weight: bold;")
        btn_layout.addWidget(select_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def populate_item_tree(self):
        """Populate the item tree with weapons grouped by type"""
        self.item_tree.clear()

        if not self.weapons_data:
            print("No weapon data to populate tree")
            return

        # Group weapons by category (One-Handed, Two-Handed, Others)
        one_handed_weapons = {}
        two_handed_weapons = {}
        other_weapons = {}

        # Process actual weapons from weapons_data
        for weapon_id, weapon_info in self.weapons_data.items():
            weapon_type_id = weapon_info.get("weapon_type_id", 0)
            name = self.get_display_name(weapon_info, is_weapon=True)

            # Simplified categorization based on name and type
            name_lower = name.lower()  # Define name_lower here for consistent access
            hand = None
            category = self.get_weapon_category_name(weapon_type_id)
            if not category or category == "Unknown":
                # Determine from name if type name is not available
                if any(keyword in name_lower for keyword in ["1h", "one-hand", "dagger", "sword", "axe", "mace", "hammer", "wand"]):
                    category = "Melee Weapons" 
                elif any(keyword in name_lower for keyword in ["2h", "two-hand", "great", "large"]):
                    category = "Two-Handed Weapons"
                elif any(keyword in name_lower for keyword in ["bow", "crossbow"]):
                    category = "Ranged Weapons"
                else:
                    category = "Other Weapons"

            # Determine handedness from category or name
            category_lower = category.lower()

            # Check if it's one-handed
            is_one_handed_by_category = any(handed in category_lower for handed in ["1h", "one-hand", "single", "dual"])
            is_one_handed_by_name = any(keyword in name_lower for keyword in ["1h", "one-hand", "dagger", "short", "light"])
            
            if is_one_handed_by_category or is_one_handed_by_name:
                hand = "One-Handed"
            else:
                # Check if it's two-handed
                is_two_handed_by_category = any(handed in category_lower for handed in ["2h", "two-hand", "great", "large"])
                is_two_handed_by_name = any(keyword in name_lower for keyword in ["2h", "two-hand", "great", "large", "heavy"])
                
                if is_two_handed_by_category or is_two_handed_by_name:
                    hand = "Two-Handed"
                else:
                    hand = "Other"
            
            # Add to appropriate group
            if hand == "One-Handed":
                if category not in one_handed_weapons:
                    one_handed_weapons[category] = []
                one_handed_weapons[category].append((weapon_id, weapon_info))
            elif hand == "Two-Handed":
                if category not in two_handed_weapons:
                    two_handed_weapons[category] = []
                two_handed_weapons[category].append((weapon_id, weapon_info))
            else:
                if category not in other_weapons:
                    other_weapons[category] = []
                other_weapons[category].append((weapon_id, weapon_info))

        # Create One-Handed Weapons category
        if one_handed_weapons:
            oh_root = QTreeWidgetItem(self.item_tree, ["One-Handed Weapons", "", "", ""])
            oh_root.setFont(0, QFont("", -1, QFont.Weight.Bold))

            for weapon_type in sorted(one_handed_weapons.keys()):
                display_type = weapon_type 
                if not display_type:
                    display_type = "Unknown"
                type_node = QTreeWidgetItem(
                    oh_root,
                    [display_type, "", f"({len(one_handed_weapons[weapon_type])} items)", ""],
                )
                type_node.setFont(0, QFont("", -1, QFont.Weight.Bold))

                for weapon_id, weapon_info in sorted(one_handed_weapons[weapon_type], key=lambda x: self.get_display_name(x[1], True)):
                    name = self.get_display_name(weapon_info, is_weapon=True)
                    damage_str = f"{weapon_info.get('min_damage', 0)}-{weapon_info.get('max_damage', 0)}"
                    item = QTreeWidgetItem(type_node, [name, weapon_type, str(weapon_id), damage_str])
                    item.setData(0, Qt.ItemDataRole.UserRole, ("weapon", weapon_id))

        # Create Two-Handed Weapons category
        if two_handed_weapons:
            th_root = QTreeWidgetItem(self.item_tree, ["Two-Handed Weapons", "", "", ""])
            th_root.setFont(0, QFont("", -1, QFont.Weight.Bold))

            for weapon_type in sorted(two_handed_weapons.keys()):
                display_type = weapon_type
                if not display_type:
                    display_type = "Unknown"
                type_node = QTreeWidgetItem(
                    th_root,
                    [display_type, "", f"({len(two_handed_weapons[weapon_type])} items)", ""],
                )
                type_node.setFont(0, QFont("", -1, QFont.Weight.Bold))

                for weapon_id, weapon_info in sorted(two_handed_weapons[weapon_type], key=lambda x: self.get_display_name(x[1], True)):
                    name = self.get_display_name(weapon_info, is_weapon=True)
                    damage_str = f"{weapon_info.get('min_damage', 0)}-{weapon_info.get('max_damage', 0)}"
                    item = QTreeWidgetItem(type_node, [name, weapon_type, str(weapon_id), damage_str])
                    item.setData(0, Qt.ItemDataRole.UserRole, ("weapon", weapon_id))

        # Create Others category
        if other_weapons:
            others_root = QTreeWidgetItem(self.item_tree, ["Other Weapons", "", "", ""])
            others_root.setFont(0, QFont("", -1, QFont.Weight.Bold))

            for category in sorted(other_weapons.keys()):
                type_node = QTreeWidgetItem(others_root, [category, "", f"({len(other_weapons[category])} items)", ""])
                type_node.setFont(0, QFont("", -1, QFont.Weight.Bold))

                for weapon_id, weapon_info in sorted(other_weapons[category], key=lambda x: self.get_display_name(x[1], True)):
                    name = self.get_display_name(weapon_info, is_weapon=True)
                    damage_str = f"{weapon_info.get('min_damage', 0)}-{weapon_info.get('max_damage', 0)}"
                    item = QTreeWidgetItem(type_node, [name, category, str(weapon_id), damage_str])
                    item.setData(0, Qt.ItemDataRole.UserRole, ("weapon", weapon_id))

        self.item_tree.expandAll()

        # Resize columns to fit content
        self.item_tree.resizeColumnToContents(0)
        self.item_tree.resizeColumnToContents(1)
        self.item_tree.resizeColumnToContents(2)
        self.item_tree.resizeColumnToContents(3)

    def get_weapon_category_name(self, weapon_type_id):
        """Convert weapon type ID to human-readable category name"""
        # Try to get the name from GameData if available
        if self.gamedata and hasattr(self.gamedata, 'weapon_type_names'):
            try:
                results = self.gamedata.weapon_type_names.where(weapon_type_id=weapon_type_id)
                if results:
                    return getattr(results[0], 'name', f"Weapon Type {weapon_type_id}")
            except:
                pass
        
        # Fallback category names based on typical IDs
        weapon_type_map = {
            1: "Swords",
            2: "Axes", 
            3: "Maces/Hammers",
            4: "Daggers",
            5: "Staves",
            6: "Spears",
            7: "Bows",
            8: "Crossbows",
            9: "Wands/Magic",
        }
        return weapon_type_map.get(weapon_type_id, f"Weapon Type {weapon_type_id}")

    def on_search_text_changed(self, text):
        """Handle search text changes"""
        self.apply_filter(text, self.type_filter.text())

    def on_filter_changed(self, text):
        """Handle filter text changes"""
        self.apply_filter(self.search_edit.text(), text)

    def apply_filter(self, search_text, filter_text):
        """Apply search and filter to the tree"""
        search_query = (search_text or "").strip().lower()
        filter_query = (filter_text or "").strip().lower()
        
        only_custom = getattr(self, 'only_custom_checkbox', None)
        only_custom_on = only_custom.isChecked() if only_custom else False

        def filter_node(node):
            # Leaf node
            if node.childCount() == 0:
                name_matches = search_query in node.text(0).lower() if search_query else True
                type_matches = filter_query in node.text(1).lower() if filter_query else True
                id_matches = search_query in node.text(2).lower() if search_query else True
                custom_ok = True
                if only_custom_on:
                    try:
                        wid = int(node.text(2))
                        custom_ok = 10000 <= wid <= 19999
                    except Exception:
                        custom_ok = False
                # Match if either name OR ID matches, and type filter matches
                text_matches = name_matches or id_matches
                matches = text_matches and type_matches and custom_ok
                node.setHidden(not matches)
                return matches

            # Category/root node
            any_visible = False
            for idx in range(node.childCount()):
                if filter_node(node.child(idx)):
                    any_visible = True

            # Also match category titles themselves
            if search_query in node.text(0).lower() or filter_query in node.text(1).lower():
                any_visible = True

            node.setHidden(not any_visible)
            if any_visible:
                node.setExpanded(True)
            return any_visible

        for i in range(self.item_tree.topLevelItemCount()):
            root = self.item_tree.topLevelItem(i)
            filter_node(root)

    def _set_visibility_recursive(self, node, visible: bool):
        node.setHidden(not visible)
        for i in range(node.childCount()):
            self._set_visibility_recursive(node.child(i), visible)

    def on_item_selection_changed(self):
        """Handle item selection"""
        selected_items = self.item_tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        item_data = item.data(0, Qt.ItemDataRole.UserRole)

        if item_data:
            item_type, item_id = item_data
            if item_type == "weapon" and item_id in self.weapons_data:
                self.show_weapon_details(item_id)

    def show_weapon_details(self, weapon_id):
        """Show detailed information for selected weapon"""
        weapon_info = self.weapons_data[weapon_id]

        # Clear previous content in the details area
        self.clear_details_content()

        # Main title with display name
        name = self.get_display_name(weapon_info, is_weapon=True)
        title_label = QLabel(f"WEAPON ID: {weapon_id} - {name}")
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

        # Create a layout for basic information
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

        # Get localized names if available
        localized_type = self.get_localised_text(weapon_info.get('weapon_type_name', 0)) or weapon_info.get("weapon_type_name", "Unknown")
        localized_material = self.get_localised_text(weapon_info.get('weapon_material_name', 0)) or weapon_info.get("weapon_material_name", "Unknown")
        
        basic_info = [
            ("Name", name),
            ("Type", localized_type),
            ("Material", localized_material),
            ("Hands", weapon_info.get("hands", "Unknown")),
            ("Category", weapon_info.get("damage_category", "Unknown")),
            ("Source", weapon_info.get("data_source", "Unknown")),
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

        # Add basic info to layout
        basic_info_layout.addWidget(basic_group)

        # Add icon placeholder
        icon_label = QLabel("ICON")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d30;
                color: #a0a0a0;
                border: 1px dashed #6fb3d2;
                font-size: 12px;
                min-width: 120px;
            }
        """)
        basic_info_layout.addWidget(icon_label)

        # Add the basic info layout to main details layout
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
            ("Damage", f"{weapon_info.get('min_damage', 0)} - {weapon_info.get('max_damage', 0)}"),
            ("Damage Type", weapon_info.get("damage_type", "Unknown")),
            ("Attack Speed", str(weapon_info.get("attack_speed", 100))),
            ("Range", f"{weapon_info.get('min_range', 0)} - {weapon_info.get('max_range', 0)}"),
            ("Attack Arc", f"{weapon_info.get('attack_arc', 90)}°"),
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
            ("Critical Chance", f"{weapon_info.get('critical_chance', 5.0)}%"),
            ("Armor Penetration", f"{weapon_info.get('armor_penetration', 0.0)}%"),
            ("Knockback Chance", f"{weapon_info.get('knockback_chance', 0.0)}%"),
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

        # Add school requirements if available
        school_requirements = req_data.get("school_requirements", [])
        if school_requirements:
            # Separator
            separator_label = QLabel("─")
            separator_label.setStyleSheet("color: #6fb3d2; font-weight: bold;")
            separator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            req_layout.addWidget(separator_label)

            # Title
            school_title = QLabel("<strong>SCHOOL REQUIREMENTS:</strong>")
            school_title.setStyleSheet("color: #6fb3d2; font-weight: bold; margin-top: 10px;")
            req_layout.addWidget(school_title)

            # List each school requirement
            for sr in school_requirements:
                raw_name = sr.get("requirement_school", "")
                level = sr.get("level", 0)
                # Normalize/format name
                name = str(raw_name)
                if "." in name:
                    name = name.split(".")[-1]
                name = name.replace("_", " ").title()

                row = QHBoxLayout()
                school_label = QLabel(f"  • {name}")
                school_label.setStyleSheet("color: #6fb3d2; min-width: 150px;")
                level_label = QLabel(f"Level {level}")
                level_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
                row.addWidget(school_label)
                row.addWidget(level_label)
                row.addStretch()
                req_layout.addLayout(row)

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
            ("Sell Value", f"{weapon_info.get('selling_price', 0)} gold"),
            ("Buy Value", f"{weapon_info.get('buying_price', 0)} gold"),
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

        # Add stretch to push everything to the top
        self.details_content_layout.addStretch()

    def clear_details_content(self):
        """Clear all widgets in the details content area"""
        # Remove and delete all widgets in the layout
        while self.details_content_layout.count():
            child = self.details_content_layout.takeAt(0)
            if child.widget():
                widget = child.widget()
                widget.setParent(None)  # Remove from parent
                widget.deleteLater()  # Schedule for deletion

    def get_selected_weapon(self) -> dict:
        """Get the selected weapon data"""
        selected_items = self.item_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data:
                item_type, item_id = item_data
                if item_type == "weapon" and item_id in self.weapons_data:
                    return self.weapons_data[item_id]
        return None
    
    def get_selected_weapon_data(self) -> dict:
        """Alias method name to match what the weapon forge wizard expects"""
        return self.get_selected_weapon()