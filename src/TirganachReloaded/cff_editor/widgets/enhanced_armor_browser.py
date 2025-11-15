"""
Enhanced armor browser with CFF loading and German localization support
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
    QHeaderView
)

from ..systems.armor_system.armor_forge import ArmorForge
from ..systems.armor_system.armor_model import (
    ARMOR_TYPES,
    MATERIAL_CATEGORIES,
    QUALITY_TIERS,
    CLASS_RESTRICTIONS,
    SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_FEET, SLOT_RIGHT_RING, SLOT_LEFT_RING, SLOT_LEFT_HAND
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


class EnhancedArmorBrowser(QDialog):
    """Enhanced armor browser dialog with detailed armor inspection"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enhanced Armor Browser")
        self.setMinimumSize(QSize(1400, 800))
        
        # Initialize data and localization
        self.armor_data = {}
        self.selected_armor = None
        self.current_language = Language.GERMAN  # Default to German
        self.gamedata = None
        self.logger = None  # Initialize logger attribute

        # Initialize localization
        self._init_localization()

        # Load armor data from CFF with JSON fallback
        self.load_armor_from_cff()

        self.init_ui()
        self.populate_item_tree()

    def _init_localization(self):
        """Initialize localization support from GameData"""
        try:
            # Try different possible paths for GameData.cff
            possible_paths = [
                # Path relative to this file (cff_editor/widgets/)
                Path(__file__).parent.parent.parent.parent / "OriginalGameFiles" / "data" / "GameData.cff",
                # Alternative path structures
                Path(__file__).parent.parent.parent.parent / "OriginalGameFiles" / "GameData.cff",
                Path(__file__).parent.parent.parent.parent.parent / "OriginalGameFiles" / "data" / "GameData.cff"
            ]

            for gamedata_path in possible_paths:
                if gamedata_path.exists():
                    # Try importing GameData using different approaches
                    try:
                        from ...tirganach import GameData
                        self.gamedata = GameData(str(gamedata_path))
                    except ImportError:
                        # Handle when running as a standalone module
                        import sys
                        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
                        try:
                            from tirganach import GameData
                            self.gamedata = GameData(str(gamedata_path))
                        except ImportError:
                            print(f"Could not import GameData from tirganach module")
                            continue
                    print(f"Loaded GameData from {gamedata_path} for localization")
                    return

            print(f"GameData.cff not found in any of the expected locations")
        except Exception as e:
            print(f"Warning: Could not initialize GameData for localization: {e}")
            import traceback
            traceback.print_exc()

    def load_armor_from_cff(self):
        """Load armor directly from GameData.cff for consistent localization"""
        try:
            # Try to use CFFArmorLoader from OrthancsSchmiede first (has complete requirements loading)
            try:
                import sys
                project_root = Path(__file__).parent.parent.parent.parent
                sys.path.insert(0, str(project_root / "src"))
                
                from OrthancsSchmiede.cff_armor_loader import CFFArmorLoader
                
                armor_loader = CFFArmorLoader()
                self.armor_data = armor_loader.load_all_armor()
                
                if self.armor_data:
                    print(f"EnhancedArmorBrowser loaded {len(self.armor_data)} armors from CFFArmorLoader with requirements")
                    return
            except Exception as e:
                print(f"Failed to use CFFArmorLoader: {e}")
            
            # Fallback to manual loading
            gamedata_path = Path(__file__).parent.parent.parent.parent / "OriginalGameFiles" / "data" / "GameData.cff"
            
            if gamedata_path.exists():
                from ...tirganach import GameData
                gamedata = GameData(str(gamedata_path))
                
                # Load armor/equipment from equipment table in GameData
                for item in gamedata.equipment:
                    # Identify armor items by checking if they have armor-related characteristics
                    item_subtype_str = str(item.item_subtype).upper()
                    if any(armor_tag in item_subtype_str for armor_tag in ["ARMOR", "HELMET", "CHEST", "LEGS", "BOOTS", "GLOVES", "SHIELD", "RING", "AMULET", "BELT", "CLOAK"]):
                        armor_dict = {
                            'id': item.item_id,
                            'name': item.name,
                            'name_id': item.name_id,  # Critical for localization
                            'item_type': str(item.item_type) if hasattr(item, 'item_type') else "EQUIPMENT",
                            'item_subtype': str(item.item_subtype) if hasattr(item, 'item_subtype') else "ARMOR",
                            
                            # Would need to link to actual armor stats from other tables
                            # These are likely in units_stats, armor_stats, or similar tables
                            'strength': 0,
                            'stamina': 0,
                            'agility': 0,
                            'dexterity': 0,
                            'intelligence': 0,
                            'wisdom': 0,
                            'charisma': 0,
                            'health': 0,
                            'mana': 0,
                            'armor_value': 0,
                            
                            # Resists would come from other tables
                            'resist_fire': 0,
                            'resist_ice': 0,
                            'resist_black': 0,
                            'resist_mind': 0,
                            'physical_resist': 0,
                            'magic_resist': 0,
                            'critical_resist': 0,
                            
                            # Speed modifiers
                            'run_speed': 0,
                            'fight_speed': 0,
                            'cast_speed': 0,
                            'stealth_bonus': 0,
                            'swimming_speed': 0,
                            'jump_height': 0,
                            
                            # Basic properties
                            'level_requirement': getattr(item, 'level_requirement', 1),
                            'class_restriction': "None",
                            'tier': "Common",  # Would come from other data
                            'material': "Generic",  # Would come from other data
                            'armor_type': "Generic",  # Would come from other data
                            
                            # Visual properties
                            'icon_id': getattr(item, 'icon_id', 0),
                            'model_ref': getattr(item, 'model_ref', ''),
                            'texture': getattr(item, 'texture', ''),
                            'normal_map': getattr(item, 'normal_map', ''),
                            
                            # Advanced features
                            'set_id': getattr(item, 'item_set_id', None),
                            'set_bonus': {},
                            'special_abilities': [],
                            'enchantment_slots': 0,
                            'stat_balance_rating': 0.0
                        }
                        
                        # Try to get school requirements from item_requirements
                        try:
                            if hasattr(gamedata, 'item_requirements'):
                                item_reqs = gamedata.item_requirements.where(item_id=item.item_id)
                                if item_reqs:
                                    school_reqs = [
                                        {
                                            'requirement_school': str(req.requirement_school),
                                            'level': getattr(req, 'level', 0),
                                            'requirement_number': getattr(req, 'requirement_number', 0),
                                        }
                                        for req in item_reqs
                                    ]
                                    armor_dict['requirements'] = {
                                        'level': max([getattr(req, 'level', 0) for req in item_reqs]) if item_reqs else 1,
                                        'school_requirements': school_reqs,
                                        'strength': 0,
                                        'dexterity': 0,
                                        'intelligence': 0,
                                    }
                                else:
                                    armor_dict['requirements'] = {
                                        'level': 1,
                                        'school_requirements': [],
                                        'strength': 0,
                                        'dexterity': 0,
                                        'intelligence': 0,
                                    }
                        except Exception:
                            armor_dict['requirements'] = {
                                'level': 1,
                                'school_requirements': [],
                                'strength': 0,
                                'dexterity': 0,
                                'intelligence': 0,
                            }
                        
                        # Add armor to data
                        self.armor_data[item.item_id] = armor_dict
                        
                print(f"EnhancedArmorBrowser loaded {len(self.armor_data)} armors from GameData.cff with proper localization IDs")
            else:
                print(f"GameData.cff not found at {gamedata_path}")
                # Fallback to JSON
                armor_file_path = Path(__file__).parent.parent.parent / "enhanced_armor.json"
                
                if armor_file_path.exists():
                    try:
                        with open(armor_file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # Check if the data is structured with 'armors' and 'sets' keys
                        if isinstance(data, dict) and 'armors' in data:
                            # New format: { "armors": [...], "sets": [...] }
                            for armor_data in data.get('armors', []):
                                from ..systems.armor_system.armor_model import Armor
                                armor = Armor.from_dict(armor_data)
                                self.armor_data[armor.id] = armor
                        else:
                            # Old format: list of armor objects
                            for armor_data in data:
                                # Convert old format to new format
                                from ..systems.armor_system.armor_model import Armor
                                armor = Armor.from_dict(armor_data)
                                self.armor_data[armor.id] = armor

                        print(f"EnhancedArmorBrowser loaded {len(self.armor_data)} armors from enhanced_armor.json")
                    except Exception as e_json:
                        print(f"Error loading armor data from JSON: {e_json}")
                else:
                    print(f"Neither GameData.cff nor enhanced_armor.json found")
                
        except Exception as e:
            print(f"Error loading armor from GameData.cff: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to JSON
            armor_file_path = Path(__file__).parent.parent.parent / "enhanced_armor.json"
            
            if armor_file_path.exists():
                try:
                    with open(armor_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Check if the data is structured with 'armors' and 'sets' keys
                    if isinstance(data, dict) and 'armors' in data:
                        # New format: { "armors": [...], "sets": [...] }
                        for armor_data in data.get('armors', []):
                            from .armor_model import Armor
                            armor = Armor.from_dict(armor_data)
                            self.armor_data[armor.id] = armor
                    else:
                        # Old format: list of armor objects
                        for armor_data in data:
                            # Convert old format to new format
                            from .armor_model import Armor
                            armor = Armor.from_dict(armor_data)
                            self.armor_data[armor.id] = armor

                    print(f"EnhancedArmorBrowser loaded {len(self.armor_data)} armors from enhanced_armor.json (fallback)")
                except Exception as e_json:
                    print(f"Error loading armor data from JSON fallback: {e_json}")
            else:
                print(f"Armor file does not exist at: {armor_file_path}")

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
        # Check if info is a dictionary or an Armor object
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
            # It's an Armor object
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
        header_layout.addWidget(QLabel("Search Armor:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search armor by name...")
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        header_layout.addWidget(self.search_edit)

        # Filter controls
        self.type_filter = QLineEdit()
        self.type_filter.setPlaceholderText("Filter by type...")
        self.type_filter.textChanged.connect(self.on_filter_changed)
        header_layout.addWidget(QLabel("Filter Type:"))
        header_layout.addWidget(self.type_filter)

        layout.addLayout(header_layout)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left - Armor tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        tree_group = QGroupBox("Armor")
        tree_layout = QVBoxLayout(tree_group)

        self.item_tree = QTreeWidget()
        self.item_tree.setHeaderLabels(["Name", "Type", "ID", "Slot"])
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

        # Right - Armor details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        details_group = QGroupBox("Armor Details")
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

        select_btn = QPushButton("Select Armor")
        select_btn.clicked.connect(self.accept)
        select_btn.setStyleSheet("padding: 8px; font-weight: bold;")
        btn_layout.addWidget(select_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def populate_item_tree(self):
        """Populate the item tree with armor grouped by slot"""
        self.item_tree.clear()

        if not self.armor_data:
            if self.logger:
                self.logger.warning("No armor data to populate tree")
            return

        # Group armor by slot
        armor_by_slot = {}
        for armor_id, armor_info in self.armor_data.items():
            # Check if armor_info is a dictionary or an Armor object
            if isinstance(armor_info, dict):
                slot_id = armor_info.get("slot", -1)
            else:
                # It's an Armor object
                slot_id = getattr(armor_info, 'slot', -1)
                
            slot_name = self.get_slot_name(slot_id)
            
            if slot_name not in armor_by_slot:
                armor_by_slot[slot_name] = []
            armor_by_slot[slot_name].append((armor_id, armor_info))

        # Create category nodes
        for slot_name in sorted(armor_by_slot.keys()):
            display_slot = slot_name if slot_name else "Unknown"
            slot_node = QTreeWidgetItem(
                self.item_tree,
                [display_slot, "", f"({len(armor_by_slot[slot_name])} items)", ""],
            )
            slot_node.setFont(0, QFont("", -1, QFont.Weight.Bold))

            # Add armor under this slot
            for armor_id, armor_info in sorted(
                armor_by_slot[slot_name], 
                key=lambda x: self.get_display_name(x[1], is_weapon=False)
            ):
                name = self.get_display_name(armor_info, is_weapon=False)
                # Check if armor_info is a dict or an object
                if isinstance(armor_info, dict):
                    armor_type = armor_info.get("armor_type", "Unknown")
                else:
                    armor_type = getattr(armor_info, 'armor_type', "Unknown")
                    
                item = QTreeWidgetItem(
                    slot_node, 
                    [name, armor_type, str(armor_id), slot_name]
                )
                item.setData(0, Qt.ItemDataRole.UserRole, ("armor", armor_id))

        self.item_tree.expandAll()

        # Resize columns to fit content
        self.item_tree.resizeColumnToContents(0)
        self.item_tree.resizeColumnToContents(1)
        self.item_tree.resizeColumnToContents(2)
        self.item_tree.resizeColumnToContents(3)

    def get_slot_name(self, slot_id):
        """Convert slot ID to human-readable name"""
        slot_names = {
            SLOT_HEAD: "Head",
            SLOT_CHEST: "Chest",
            SLOT_LEGS: "Legs",
            SLOT_FEET: "Feet",
            SLOT_RIGHT_RING: "Right Ring",
            SLOT_LEFT_RING: "Left Ring",
            SLOT_LEFT_HAND: "Left Hand/Shield",
        }
        return slot_names.get(slot_id, f"Slot {slot_id}")

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

        # Nothing to filter: show everything
        if search_query == "" and filter_query == "":
            for i in range(self.item_tree.topLevelItemCount()):
                root = self.item_tree.topLevelItem(i)
                root.setHidden(False)
                self._set_visibility_recursive(root, True)
            return

        def filter_node(node):
            # Leaf node
            if node.childCount() == 0:
                name_matches = search_query in node.text(0).lower() if search_query else True
                type_matches = filter_query in node.text(1).lower() if filter_query else True
                id_matches = search_query in node.text(2).lower() if search_query else True
                slot_matches = filter_query in node.text(3).lower() if filter_query else True
                matches = name_matches and type_matches and id_matches and slot_matches
                node.setHidden(not matches)
                return matches

            # Category/root node
            any_visible = False
            for idx in range(node.childCount()):
                if filter_node(node.child(idx)):
                    any_visible = True

            # Also match category titles themselves
            if search_query in node.text(0).lower() or filter_query in node.text(3).lower():
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
            if item_type == "armor" and item_id in self.armor_data:
                self.show_armor_details(item_id)

    def show_armor_details(self, armor_id):
        """Show detailed information for selected armor"""
        armor_info = self.armor_data[armor_id]

        # Clear previous content in the details area
        self.clear_details_content()

        # Main title with display name
        name = self.get_display_name(armor_info, is_weapon=False) 
        title_label = QLabel(f"ARMOR ID: {armor_id} - {name}")
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
        # Check if armor_info is a dict or an object
        if isinstance(armor_info, dict):
            slot_id = armor_info.get("slot", -1)
            armor_type = armor_info.get("armor_type", "Unknown")
            tier = armor_info.get("tier", "Common")
            material = armor_info.get("material", "Unknown")
        else:
            # It's an Armor object
            slot_id = getattr(armor_info, 'slot', -1)
            armor_type = getattr(armor_info, 'armor_type', "Unknown")
            tier = getattr(armor_info, 'tier', "Common")
            material = getattr(armor_info, 'material', "Unknown")
        
        slot_name = self.get_slot_name(slot_id)
        
        basic_info = [
            ("Name", name),
            ("Slot", slot_name),
            ("Type", armor_type),
            ("Tier", tier),
            ("Material", material),
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

        # Check if armor_info is dict or object
        if isinstance(armor_info, dict):
            base_armor = str(armor_info.get("armor_value", 0))
            physical_resist = f"{armor_info.get('physical_resist', 0)}%"
            magic_resist = f"{armor_info.get('magic_resist', 0)}%"
        else:
            base_armor = str(getattr(armor_info, 'armor_value', 0))
            physical_resist = f"{getattr(armor_info, 'physical_resist', 0)}%"
            magic_resist = f"{getattr(armor_info, 'magic_resist', 0)}%"

        def_info = [
            ("Base Armor", base_armor),
            ("Physical Resist", physical_resist),
            ("Magic Resist", magic_resist),
        ]

        for label, value in def_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 130px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            def_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(def_group)

        # Stat Bonuses Section
        stats_group = QGroupBox("STAT BONUSES")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #6f9eb3;
                border: 2px solid #6f9eb3;
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
        stats_layout = QVBoxLayout(stats_group)

        # Check if armor_info is dict or object and collect non-zero stats
        stats_info = []
        
        if isinstance(armor_info, dict):
            strength = armor_info.get("strength", 0)
            stamina = armor_info.get("stamina", 0)
            agility = armor_info.get("agility", 0)
            dexterity = armor_info.get("dexterity", 0)
            intelligence = armor_info.get("intelligence", 0)
            wisdom = armor_info.get("wisdom", 0)
            charisma = armor_info.get("charisma", 0)
        else:
            strength = getattr(armor_info, 'strength', 0)
            stamina = getattr(armor_info, 'stamina', 0)
            agility = getattr(armor_info, 'agility', 0)
            dexterity = getattr(armor_info, 'dexterity', 0)
            intelligence = getattr(armor_info, 'intelligence', 0)
            wisdom = getattr(armor_info, 'wisdom', 0)
            charisma = getattr(armor_info, 'charisma', 0)

        if strength != 0:
            stats_info.append(("Strength", f"+{strength}"))
        if stamina != 0:
            stats_info.append(("Stamina", f"+{stamina}"))
        if agility != 0:
            stats_info.append(("Agility", f"+{agility}"))
        if dexterity != 0:
            stats_info.append(("Dexterity", f"+{dexterity}"))
        if intelligence != 0:
            stats_info.append(("Intelligence", f"+{intelligence}"))
        if wisdom != 0:
            stats_info.append(("Wisdom", f"+{wisdom}"))
        if charisma != 0:
            stats_info.append(("Charisma", f"+{charisma}"))

        # If no stat bonuses, show a message
        if not stats_info:
            stats_info = [("None", "No stat bonuses")]

        for label, value in stats_info:
            row_layout = QHBoxLayout()
            label_widget = QLabel(f"<strong>{label}:</strong>")
            label_widget.setStyleSheet("color: #a0a0a0; min-width: 130px;")
            value_widget = QLabel(str(value))
            value_widget.setStyleSheet("color: #e0e0e0;")
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            stats_layout.addLayout(row_layout)

        self.details_content_layout.addWidget(stats_group)

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

        # Check if armor_info is dict or object
        if isinstance(armor_info, dict):
            movement_speed = f"{armor_info.get('run_speed', 0)}%"
            fight_speed = f"{armor_info.get('fight_speed', 0)}%"
            cast_speed = f"{armor_info.get('cast_speed', 0)}%"
            health_bonus = str(armor_info.get("health", 0))
            mana_bonus = str(armor_info.get("mana", 0))
        else:
            movement_speed = f"{getattr(armor_info, 'run_speed', 0)}%"
            fight_speed = f"{getattr(armor_info, 'fight_speed', 0)}%"
            cast_speed = f"{getattr(armor_info, 'cast_speed', 0)}%"
            health_bonus = str(getattr(armor_info, 'health', 0))
            mana_bonus = str(getattr(armor_info, 'mana', 0))

        special_info = [
            ("Movement Speed", movement_speed),
            ("Fight Speed", fight_speed),
            ("Cast Speed", cast_speed),
            ("Health Bonus", health_bonus),
            ("Mana Bonus", mana_bonus),
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

        # Check if armor_info is dict or object
        if isinstance(armor_info, dict):
            req_data = armor_info.get("requirements", {})
            strength_req = str(req_data.get("strength", armor_info.get("strength_requirement", 0)))
            dexterity_req = str(req_data.get("dexterity", armor_info.get("dexterity_requirement", 0)))
            intelligence_req = str(req_data.get("intelligence", armor_info.get("intelligence_requirement", 0)))
            level_req = str(req_data.get("level", armor_info.get("level_requirement", 1)))
        else:
            req_data = getattr(armor_info, 'requirements', {})
            strength_req = str(req_data.get("strength", getattr(armor_info, 'strength_requirement', 0)))
            dexterity_req = str(req_data.get("dexterity", getattr(armor_info, 'dexterity_requirement', 0)))
            intelligence_req = str(req_data.get("intelligence", getattr(armor_info, 'intelligence_requirement', 0)))
            level_req = str(req_data.get("level", getattr(armor_info, 'level_requirement', 1)))

        req_info = [
            ("Strength", strength_req),
            ("Dexterity", dexterity_req),
            ("Intelligence", intelligence_req),
            ("Level", level_req),
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
        school_requirements = req_data.get("school_requirements", []) if isinstance(req_data, dict) else []
        if school_requirements:
            # Add separator
            separator_label = QLabel("─")
            separator_label.setStyleSheet("color: #6fb3d2; font-weight: bold;")
            separator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            req_layout.addWidget(separator_label)

            # Add school requirements title
            school_title = QLabel("<strong>SCHOOL REQUIREMENTS:</strong>")
            school_title.setStyleSheet(
                "color: #6fb3d2; font-weight: bold; margin-top: 10px;"
            )
            req_layout.addWidget(school_title)

            # Add each school requirement
            for school_req in school_requirements:
                school_name = school_req.get("requirement_school", "Unknown School")
                school_level = school_req.get("level", 0)

                # Format school name for better display
                formatted_name = str(school_name)
                if "." in formatted_name:
                    formatted_name = formatted_name.split(".")[-1]
                formatted_name = formatted_name.replace("_", " ").title()

                row_layout = QHBoxLayout()
                school_label = QLabel(f"  • {formatted_name}")
                school_label.setStyleSheet("color: #6fb3d2; min-width: 150px;")
                level_label = QLabel(f"Level {school_level}")
                level_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
                row_layout.addWidget(school_label)
                row_layout.addWidget(level_label)
                row_layout.addStretch()
                req_layout.addLayout(row_layout)
        else:
            # Show no school requirements message
            no_school_label = QLabel("  No school requirements")
            no_school_label.setStyleSheet(
                "color: #666; font-style: italic; margin-top: 5px;"
            )
            req_layout.addWidget(no_school_label)

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

        # Check if armor_info is dict or object
        if isinstance(armor_info, dict):
            sell_value = f"{armor_info.get('sell_value', 0)} gold"
            buy_value = f"{armor_info.get('buy_value', 0)} gold"
            rarity = armor_info.get("rarity", "Unknown")
        else:
            sell_value = f"{getattr(armor_info, 'sell_value', 0)} gold"
            buy_value = f"{getattr(armor_info, 'buy_value', 0)} gold"
            rarity = getattr(armor_info, 'rarity', "Unknown")

        eco_info = [
            ("Sell Value", sell_value),
            ("Buy Value", buy_value),
            ("Rarity", rarity),
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

    def get_selected_armor(self) -> dict:
        """Get the selected armor data"""
        selected_items = self.item_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            item_data = item.data(0, Qt.ItemDataRole.UserRole)
            if item_data:
                item_type, item_id = item_data
                if item_type == "armor" and item_id in self.armor_data:
                    return self.armor_data[item_id]
        return None
    
    def get_selected_armor_data(self) -> dict:
        """Alias method name to match what the armor forge wizard expects"""
        return self.get_selected_armor()