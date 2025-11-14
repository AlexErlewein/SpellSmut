#!/usr/bin/env python3
"""
Orthancs Schmiede - Weapon & Armor Browser and Creation Suite
=============================================================

A comprehensive application for browsing and creating SpellForce weapons and armor.
Features enhanced UI/UX, integrated creation wizards, and detailed item inspection.

Usage:
    python orthancs_schmiede.py [--debug] [--rebuild-cache]

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
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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

from TirganachReloaded.cff_editor.logging_config import (  # noqa: E402
    configure_logging,
    get_logger,
)
from TirganachReloaded.cff_editor.shared.id_manager import IDManager  # noqa: E402
from TirganachReloaded.cff_editor.widgets.armor_forge_wizard import (
    ArmorForgeWizard,  # noqa: E402
)
from TirganachReloaded.cff_editor.widgets.weapon_forge_wizard import (
    WeaponForgeWizard,  # noqa: E402
)
from TirganachReloaded.tirganach.types import Language  # noqa: E402


class OrthancsSchmiede(QMainWindow):
    """Main application window for Orthancs Schmiede"""

    def __init__(self):
        super().__init__()
        self.logger = None
        self.id_manager = None
        self.weapon_data = {}
        self.armor_data = {}
        self.current_language = Language.GERMAN
        self.custom_cff_path = None

        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the enhanced user interface"""
        self.setWindowTitle("Orthancs Schmiede - Weapon & Armor Suite")
        self.setMinimumSize(QSize(1600, 1000))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Header with enhanced controls
        header_layout = QHBoxLayout()
        title_label = QLabel("Orthancs Schmiede")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #6fb3d2;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Mode selector
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Weapons", "Armor"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        header_layout.addWidget(QLabel("Mode:"))
        header_layout.addWidget(self.mode_combo)

        # Language selector
        header_layout.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        # Visible labels mapped to Language enum
        self._lang_map = {
            "Deutsch": Language.GERMAN,
            "English": Language.ENGLISH,
            "Français": Language.FRENCH,
            "Español": Language.SPANISH,
            "Italiano": Language.ITALIAN,
        }
        self.lang_combo.addItems(list(self._lang_map.keys()))
        # Default to German
        self.lang_combo.setCurrentText("Deutsch")
        self.lang_combo.currentTextChanged.connect(self.on_language_changed)
        header_layout.addWidget(self.lang_combo)

        # Search field
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search weapons...")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        header_layout.addWidget(self.search_edit)

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

        # CFF File loading button
        cff_btn = QPushButton("Load CFF File")
        cff_btn.clicked.connect(self.load_cff_file)
        cff_btn.setStyleSheet(
            "QPushButton { background-color: #2d5a2d; color: #e0e0e0; font-weight: bold; padding: 8px; border-radius: 4px; border: 1px solid #555; } QPushButton:hover { background-color: #3a6a3a; }"
        )
        header_layout.addWidget(cff_btn)

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
        self.statusBar().showMessage("Ready - Orthancs Schmiede Loaded")

        # Update status with current file info
        self.update_status_with_file_info()

    def load_data(self):
        """Load weapon and armor data"""
        try:
            self.statusBar().showMessage("Initializing Orthancs Schmiede...")

            # Configure logging
            if not self.logger:
                configure_logging()
                self.logger = get_logger("orthancs_schmiede")

            # Initialize ID manager
            if not self.id_manager:
                self.id_manager = IDManager()

            # Update status message based on whether we're loading custom CFF
            if self.custom_cff_path:
                file_name = Path(self.custom_cff_path).name
                self.statusBar().showMessage(f"Loading weapons from {file_name}...")
            else:
                self.statusBar().showMessage("Loading weapon data...")
            self.load_weapon_data()

            if self.custom_cff_path:
                file_name = Path(self.custom_cff_path).name
                self.statusBar().showMessage(f"Loading armor from {file_name}...")
            else:
                self.statusBar().showMessage("Loading armor data...")
            self.load_armor_data()

            self.statusBar().showMessage("Building item trees...")
            self.populate_item_tree()

            total_items = len(self.weapon_data) + len(self.armor_data)
            self.item_count_label.setText(f"Total: {total_items} items")
            self.update_tree_title()

            # Update final status message
            self.update_status_with_file_info("Orthancs Schmiede Ready")

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
            self.weapon_loader = CFFWeaponLoader()

            # Connect loader signals if needed for progress updates
            # loader.progress_updated.connect(lambda p, msg: self.statusBar().showMessage(msg))

            # Load weapons from CFF file (with fallback to JSON)
            if self.custom_cff_path:
                self.weapon_data = self.weapon_loader.load_all_weapons(cff_file_path=self.custom_cff_path)
                if self.logger:
                    self.logger.info(f"✓ Loaded {len(self.weapon_data)} weapons from custom CFF: {self.custom_cff_path}")
            else:
                self.weapon_data = self.weapon_loader.load_all_weapons()
                if self.logger:
                    self.logger.info(
                        f"✓ Loaded {len(self.weapon_data)} weapons from default CFF data"
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
            if self.custom_cff_path:
                self.armor_data = loader.load_all_armor(cff_file_path=self.custom_cff_path)
                if self.logger:
                    self.logger.info(f"✓ Loaded {len(self.armor_data)} armor pieces from custom CFF: {self.custom_cff_path}")
            else:
                self.armor_data = loader.load_all_armor()
                if self.logger:
                    self.logger.info(
                        f"✓ Loaded {len(self.armor_data)} armor pieces from CFF data"
                    )

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load armor data: {e}")
                self.logger.exception(e)

    def get_weapon_category_name(self, weapon_type_id):
        """Convert weapon type ID to human-readable category name"""
        try:
            hand, category = self.get_weapon_hand_and_category(weapon_type_id)
            return category
        except Exception:
            return "Unknown"

    def _get_gamedata(self):
        # Access shared GameData instance
        try:
            if hasattr(self, "weapon_loader") and getattr(
                self.weapon_loader, "gamedata", None
            ):
                return self.weapon_loader.gamedata
            from cff_weapon_loader import CFFWeaponLoader

            self.weapon_loader = CFFWeaponLoader()
            return self.weapon_loader.gamedata
        except Exception:
            return None

    def get_localised_text(self, text_id: int) -> str:
        """Return localisation text for current language by text_id, with fallback."""
        gd = self._get_gamedata()
        if not gd or not hasattr(gd, "localisation") or not text_id:
            return ""
        try:
            rows = gd.localisation.where(
                text_id=text_id, language=self.current_language
            )
            if rows:
                return getattr(rows[0], "text", "") or ""
        except Exception:
            pass
        # Fallback: try English
        try:
            rows_en = gd.localisation.where(text_id=text_id, language=Language.ENGLISH)
            if rows_en:
                return getattr(rows_en[0], "text", "") or ""
        except Exception:
            pass
        return ""

    def get_localized_weapon_type_name(self, weapon_type_id: int) -> str:
        gd = self._get_gamedata()
        if not gd or not hasattr(gd, "weapon_type_names"):
            return ""
        try:
            res = gd.weapon_type_names.where(weapon_type_id=weapon_type_id)
            if res:
                text_id = getattr(res[0], "text_id", 0)
                return self.get_localised_text(text_id) or ""
        except Exception:
            pass
        return ""

    def get_localized_weapon_material_name(self, material_id: int) -> str:
        gd = self._get_gamedata()
        if not gd or not hasattr(gd, "weapon_material_names"):
            return ""
        try:
            res = gd.weapon_material_names.where(weapon_material_id=material_id)
            if res:
                text_id = getattr(res[0], "text_id", 0)
                return self.get_localised_text(text_id) or ""
        except Exception:
            pass
        return ""

    def get_item_set_description_text(self, item_set_id: int) -> str:
        """Return localized ItemSet description by set_id if available."""
        if not item_set_id:
            return ""
        gd = self._get_gamedata()
        if not gd or not hasattr(gd, "item_sets"):
            return ""
        try:
            rows = gd.item_sets.where(set_id=item_set_id)
        except Exception:
            rows = []
        if rows:
            text_id = getattr(rows[0], "text_id", 0)
            return self.get_localised_text(text_id) or ""
        return ""

    def get_display_name(self, info: dict, is_weapon: bool) -> str:
        """Resolve display name from CFF localisation by name_id, fallback to stored name."""
        name_id = info.get("name_id", 0)
        loc = self.get_localised_text(name_id) if name_id else ""
        if loc:
            return loc
        # Fallback to existing fields
        if is_weapon:
            return info.get("weapon_name", info.get("name", "Unknown"))
        else:
            return info.get("armor_name", info.get("name", "Unknown"))

    def get_weapon_hand_and_category(self, weapon_type_id, name: str | None = None):
        """Return (handedness, category) derived from weapon_type_names.
        handedness: 'One-Handed', 'Two-Handed', or None
        category: cleaned label like 'Swords', 'Axes', etc., or 'Unknown'
        """
        try:
            # Access game data via existing loader
            if hasattr(self, "weapon_loader") and hasattr(
                self.weapon_loader, "gamedata"
            ):
                gd = self.weapon_loader.gamedata
            else:
                from cff_weapon_loader import CFFWeaponLoader

                self.weapon_loader = CFFWeaponLoader()
                gd = self.weapon_loader.gamedata

            if not hasattr(gd, "weapon_type_names"):
                return (None, "Unknown")

            if weapon_type_id >= len(gd.weapon_type_names):
                return (None, "Unknown")

            # Prefer exact lookup by ID; indexing can be misaligned across tables
            type_name_str = None
            try:
                results = gd.weapon_type_names.where(weapon_type_id=weapon_type_id)
            except Exception:
                results = []

            if results:
                first = results[0]
                type_name_str = getattr(first, "name", str(first))
            else:
                # Safe fallback: attempt index, but this may be misaligned in some dumps
                try:
                    maybe_obj = gd.weapon_type_names[weapon_type_id]
                    type_name_str = getattr(maybe_obj, "name", str(maybe_obj))
                except Exception:
                    return (None, "Unknown")

            # Determine category
            category = "Unknown"
            if "Dagger" in type_name_str:
                category = "Daggers"
            elif "Sword" in type_name_str:
                category = "Swords"
            elif "Axe" in type_name_str:
                category = "Axes"
            elif "Mace" in type_name_str:
                category = "Maces"
            elif "Hammer" in type_name_str:
                category = "Hammers"
            elif "Staff" in type_name_str:
                category = "Staves"
            elif "Spear" in type_name_str:
                category = "Spears"
            elif "Halberd" in type_name_str:
                category = "Halberds"
            elif "Crossbow" in type_name_str:
                category = "Crossbows"
            elif "Bow" in type_name_str:
                category = "Bows"
            elif "Hand" in type_name_str:
                category = "Hand Weapons"

            # Determine handedness strictly from 1H/2H markers.
            hand = None
            if "2H" in type_name_str:
                hand = "Two-Handed"
            elif "1H" in type_name_str or " Hand" in type_name_str:
                # Treat explicit Hand types as one-handed
                hand = "One-Handed"
            else:
                # Sensible defaults when no marker exists
                if category in ["Bows", "Crossbows"]:
                    hand = "Two-Handed"

            # Secondary correction using weapon display name, if provided
            if name:
                n = name.lower()

                def has(term):
                    return term in n

                # Crossbow before Bow to avoid substring collision
                if has("crossbow") and category != "Crossbows":
                    category = "Crossbows"
                    hand = "Two-Handed"
                elif has("bow") and category != "Bows":
                    category = "Bows"
                    if hand is None:
                        hand = "Two-Handed"
                elif has("dagger") and category != "Daggers":
                    category = "Daggers"
                    if hand is None:
                        hand = "One-Handed"
                elif has("sword") and category != "Swords":
                    category = "Swords"
                elif has("axe") and category != "Axes":
                    category = "Axes"
                elif has("mace") and category != "Maces":
                    category = "Maces"
                elif has("hammer") and category != "Hammers":
                    category = "Hammers"
                elif has("halberd") and category != "Halberds":
                    category = "Halberds"
                elif has("spear") and category != "Spears":
                    category = "Spears"
                elif has("staff") and category != "Staves":
                    category = "Staves"

                # Fine-grained hand detection for bows and crossbows if still ambiguous
                if category == "Bows":
                    if any(
                        k in n
                        for k in [
                            "hand bow",
                            "one-hand",
                            "one handed",
                            "1h",
                            "short",
                            "light",
                            "compact",
                        ]
                    ):
                        hand = "One-Handed"
                    elif any(
                        k in n
                        for k in [
                            "two-hand",
                            "two handed",
                            "2h",
                            "long",
                            "greatbow",
                            "warbow",
                            "heavy",
                        ]
                    ):
                        hand = "Two-Handed"
                elif category == "Crossbows":
                    if any(
                        k in n
                        for k in [
                            "hand crossbow",
                            "pistol crossbow",
                            "wrist crossbow",
                            "one-hand",
                            "one handed",
                            "1h",
                        ]
                    ):
                        hand = "One-Handed"
                    elif any(
                        k in n
                        for k in ["two-hand", "two handed", "2h", "heavy", "siege"]
                    ):
                        hand = "Two-Handed"

            return (hand, category)
        except Exception:
            return (None, "Unknown")

    def populate_item_tree(self):
        """Populate the item tree with weapons and armor grouped by type"""
        self.item_tree.clear()

        if not self.weapon_data and not self.armor_data:
            if self.logger:
                self.logger.warning("No item data to populate tree")
            return

        # Create weapon items with proper categorization
        if self.weapon_data:
            weapons_root = QTreeWidgetItem(self.item_tree, ["Weapons", "", ""])
            weapons_root.setFont(0, QFont("", -1, QFont.Weight.Bold))

            # Group weapons by category (One-Handed, Two-Handed, Others)
            one_handed_weapons = {}
            two_handed_weapons = {}
            other_weapons = {}

            # Process actual weapons from weapon_data (based on weapon_type, with name correction)
            for weapon_id, weapon_info in self.weapon_data.items():
                weapon_type_id = weapon_info.get("weapon_type_id", 0)
                name = self.get_display_name(weapon_info, is_weapon=True)

                hand, category = self.get_weapon_hand_and_category(weapon_type_id, name)
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

            # Process Wands from armor_data (they appear as ONEHANDED_WEAPON/TWOHANDED_WEAPON in armor table)
            for armor_id, armor_info in self.armor_data.items():
                armor_subtype = armor_info.get("item_subtype", "")
                subtype_str = str(armor_subtype)

                # Only process Wands from armor table
                if subtype_str in [
                    "EquipmentType.ONEHANDED_WEAPON",
                    "EquipmentType.TWOHANDED_WEAPON",
                ]:
                    name = armor_info.get("armor_name", f"Wand {armor_id}")

                    if subtype_str == "EquipmentType.ONEHANDED_WEAPON":
                        if "Wands" not in one_handed_weapons:
                            one_handed_weapons["Wands"] = []
                        one_handed_weapons["Wands"].append((armor_id, armor_info))
                    elif subtype_str == "EquipmentType.TWOHANDED_WEAPON":
                        if "Wands" not in two_handed_weapons:
                            two_handed_weapons["Wands"] = []
                        two_handed_weapons["Wands"].append((armor_id, armor_info))

            # Create One-Handed Weapons category
            if one_handed_weapons:
                oh_root = QTreeWidgetItem(weapons_root, ["One-Handed Weapons", "", ""])
                oh_root.setFont(0, QFont("", -1, QFont.Weight.Bold))

                for weapon_type in sorted(one_handed_weapons.keys()):
                    display_type = (
                        weapon_type  # Already formatted from get_weapon_category_name
                    )
                    if not display_type:
                        display_type = "Unknown"
                    type_node = QTreeWidgetItem(
                        oh_root,
                        [
                            display_type,
                            "",
                            f"({len(one_handed_weapons[weapon_type])} items)",
                        ],
                    )
                    type_node.setFont(0, QFont("", -1, QFont.Weight.Bold))

                    for weapon_id, weapon_info in sorted(
                        one_handed_weapons[weapon_type]
                    ):
                        name = self.get_display_name(weapon_info, is_weapon=True)
                        type_text = self.get_localized_weapon_type_name(
                            weapon_info.get("weapon_type_id", 0)
                        ) or weapon_info.get(
                            "weapon_type_name", weapon_info.get("item_subtype", "")
                        )
                        if not isinstance(type_text, str):
                            type_text = str(type_text)

                        # Detect entries originating from armor_data (e.g., Wands)
                        is_armor_entry = (
                            "armor_type" in weapon_info
                            or "slot" in weapon_info
                            or (isinstance(weapon_info.get("item_subtype", ""), str) and
                                weapon_info.get("item_subtype", "").startswith("EquipmentType."))
                        )

                        item = QTreeWidgetItem(
                            type_node, [name, type_text, str(weapon_id)]
                        )
                        # Mark item type for proper handling in UI
                        item.setData(
                            0,
                            Qt.ItemDataRole.UserRole,
                            ("armor", weapon_id) if is_armor_entry else ("weapon", weapon_id),
                        )

            # Create Two-Handed Weapons category
            if two_handed_weapons:
                th_root = QTreeWidgetItem(weapons_root, ["Two-Handed Weapons", "", ""])
                th_root.setFont(0, QFont("", -1, QFont.Weight.Bold))

                for weapon_type in sorted(two_handed_weapons.keys()):
                    display_type = (
                        weapon_type  # Already formatted from get_weapon_category_name
                    )
                    if not display_type:
                        display_type = "Unknown"
                    type_node = QTreeWidgetItem(
                        th_root,
                        [
                            display_type,
                            "",
                            f"({len(two_handed_weapons[weapon_type])} items)",
                        ],
                    )
                    type_node.setFont(0, QFont("", -1, QFont.Weight.Bold))

                    for weapon_id, weapon_info in sorted(
                        two_handed_weapons[weapon_type]
                    ):
                        name = self.get_display_name(weapon_info, is_weapon=True)
                        type_text = self.get_localized_weapon_type_name(
                            weapon_info.get("weapon_type_id", 0)
                        ) or weapon_info.get(
                            "weapon_type_name", weapon_info.get("item_subtype", "")
                        )
                        if not isinstance(type_text, str):
                            type_text = str(type_text)

                        # Detect entries originating from armor_data (e.g., Wands)
                        is_armor_entry = (
                            "armor_type" in weapon_info
                            or "slot" in weapon_info
                            or (isinstance(weapon_info.get("item_subtype", ""), str) and
                                weapon_info.get("item_subtype", "").startswith("EquipmentType."))
                        )

                        item = QTreeWidgetItem(
                            type_node, [name, type_text, str(weapon_id)]
                        )
                        # Mark item type for proper handling in UI
                        item.setData(
                            0,
                            Qt.ItemDataRole.UserRole,
                            ("armor", weapon_id) if is_armor_entry else ("weapon", weapon_id),
                        )

            # Create Others category
            if other_weapons:
                others_root = QTreeWidgetItem(weapons_root, ["Others", "", ""])
                others_root.setFont(0, QFont("", -1, QFont.Weight.Bold))

                for category in sorted(other_weapons.keys()):
                    type_node = QTreeWidgetItem(
                        others_root,
                        [category, "", f"({len(other_weapons[category])} items)"],
                    )
                    type_node.setFont(0, QFont("", -1, QFont.Weight.Bold))

                    for weapon_id, weapon_info in sorted(other_weapons[category]):
                        name = self.get_display_name(weapon_info, is_weapon=True)
                        type_text = self.get_localized_weapon_type_name(
                            weapon_info.get("weapon_type_id", 0)
                        ) or weapon_info.get(
                            "weapon_type_name", weapon_info.get("item_subtype", "")
                        )
                        if not isinstance(type_text, str):
                            type_text = str(type_text)

                        # Detect entries originating from armor_data
                        is_armor_entry = (
                            "armor_type" in weapon_info
                            or "slot" in weapon_info
                            or (isinstance(weapon_info.get("item_subtype", ""), str) and
                                weapon_info.get("item_subtype", "").startswith("EquipmentType."))
                        )

                        item = QTreeWidgetItem(
                            type_node, [name, type_text, str(weapon_id)]
                        )
                        item.setData(
                            0,
                            Qt.ItemDataRole.UserRole,
                            ("armor", weapon_id) if is_armor_entry else ("weapon", weapon_id),
                        )

            weapons_root.setExpanded(True)

        # Create armor items with proper categorization
        if self.armor_data:
            armor_root = QTreeWidgetItem(self.item_tree, ["Armor", "", ""])
            armor_root.setFont(0, QFont("", -1, QFont.Weight.Bold))

            # Group armor by proper category names
            armor_categories = {}

            for armor_id, armor_info in self.armor_data.items():
                armor_subtype = armor_info.get("item_subtype", "")

                # Convert enum to string for comparison
                subtype_str = str(armor_subtype)

                # Skip NOTHING items and WANDS (they should be in weapons)
                if subtype_str == "EquipmentType.NOTHING" or subtype_str in [
                    "EquipmentType.ONEHANDED_WEAPON",
                    "EquipmentType.TWOHANDED_WEAPON",
                ]:
                    continue

                # Determine proper category name
                category_name = None
                if subtype_str == "EquipmentType.HELMET":
                    category_name = "Helmets"
                elif subtype_str == "EquipmentType.UPPER":
                    category_name = "Chest Armor"
                elif subtype_str == "EquipmentType.LOWER":
                    category_name = "Leg Armor"
                elif subtype_str == "EquipmentType.RING":
                    category_name = "Rings"
                elif subtype_str == "EquipmentType.SHIELD":
                    category_name = "Shields"
                elif subtype_str == "EquipmentType.FULL_BODY":
                    category_name = "Robes"
                elif subtype_str == "EquipmentType.FIGURE_NPC":
                    category_name = "Others"
                else:
                    category_name = (
                        subtype_str.replace("EquipmentType.", "")
                        .replace("_", " ")
                        .title()
                    )

                if category_name not in armor_categories:
                    armor_categories[category_name] = []
                armor_categories[category_name].append((armor_id, armor_info))

            # Create category nodes
            for category_name in sorted(armor_categories.keys()):
                category_node = QTreeWidgetItem(
                    armor_root,
                    [
                        category_name,
                        "",
                        f"({len(armor_categories[category_name])} items)",
                    ],
                )
                category_node.setFont(0, QFont("", -1, QFont.Weight.Bold))

                # Add armor under this category
                for armor_id, armor_info in sorted(armor_categories[category_name]):
                    name = self.get_display_name(armor_info, is_weapon=False)
                    armor_type = armor_info.get("armor_type", "Unknown")
                    item = QTreeWidgetItem(
                        category_node, [name, armor_type, str(armor_id)]
                    )
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

        # Re-apply any active search filter after repopulating
        if hasattr(self, "search_edit") and self.search_edit is not None:
            self.apply_search_filter(self.search_edit.text())

    def on_search_text_changed(self, text: str):
        self.apply_search_filter(text)

    def apply_search_filter(self, text: str):
        query = (text or "").strip().lower()
        # Nothing to filter: show everything
        if query == "":
            for i in range(self.item_tree.topLevelItemCount()):
                root = self.item_tree.topLevelItem(i)
                root.setHidden(False)
                self._set_visibility_recursive(root, True)
            return

        # Determine which root to filter based on current mode
        current_mode = (
            self.mode_combo.currentText() if hasattr(self, "mode_combo") else "Weapons"
        )

        def filter_node(node):
            # Leaf node
            if node.childCount() == 0:
                name_matches = query in node.text(0).lower()
                node.setHidden(not name_matches)
                return name_matches

            # Category/root node
            any_visible = False
            for idx in range(node.childCount()):
                if filter_node(node.child(idx)):
                    any_visible = True

            # Also match category titles themselves
            if query in node.text(0).lower():
                any_visible = True

            node.setHidden(not any_visible)
            if any_visible:
                node.setExpanded(True)
            return any_visible

        for i in range(self.item_tree.topLevelItemCount()):
            root = self.item_tree.topLevelItem(i)
            root_name = (root.text(0) or "").lower()
            is_weapons_root = root_name.startswith("weapons")
            is_armor_root = root_name.startswith("armor")

            # Only filter within the current mode; hide the other root during search
            if (current_mode == "Weapons" and is_weapons_root) or (
                current_mode == "Armor" and is_armor_root
            ):
                filter_node(root)
            else:
                root.setHidden(True)

    def _set_visibility_recursive(self, node, visible: bool):
        node.setHidden(not visible)
        for i in range(node.childCount()):
            self._set_visibility_recursive(node.child(i), visible)

    def on_mode_changed(self, mode):
        """Handle mode change between weapons and armor"""
        self.update_tree_title()
        if hasattr(self, "search_edit") and self.search_edit is not None:
            self.search_edit.setPlaceholderText(
                "Search weapons..." if mode == "Weapons" else "Search armor..."
            )
            # Re-apply current filter when mode changes
            self.apply_search_filter(self.search_edit.text())

    def on_language_changed(self, label: str):
        # Update current language based on dropdown
        self.current_language = self._lang_map.get(label, Language.GERMAN)
        # Rebuild tree with new localisation
        self.populate_item_tree()

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
        display_name = self.get_display_name(weapon_info, is_weapon=True)
        title_label = QLabel(f"WEAPON ID: {weapon_id} - {display_name}")
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

        # Localize type/material
        localized_type = self.get_localized_weapon_type_name(
            weapon_info.get("weapon_type_id", 0)
        ) or weapon_info.get(
            "weapon_type_name", weapon_info.get("item_subtype", "Unknown")
        )
        localized_material = self.get_localized_weapon_material_name(
            weapon_info.get("weapon_material_id", 0)
        ) or weapon_info.get("weapon_material_name", "Unknown")
        basic_info = [
            ("Name", display_name),
            ("Type", localized_type),
            ("Material", localized_material),
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

        # Description Section (from Item Set when available)
        desc_text = self.get_item_set_description_text(
            weapon_info.get("item_set_id", 0)
        )
        if desc_text:
            desc_group = QGroupBox("DESCRIPTION")
            desc_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    color: #c7c76f;
                    border: 2px solid #c7c76f;
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
            desc_layout = QVBoxLayout(desc_group)
            desc_label = QLabel(desc_text)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #e0e0e0;")
            desc_layout.addWidget(desc_label)
            self.details_content_layout.addWidget(desc_group)

        # (Removed erroneous armor description block in weapon details)

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
            effects_label = QLabel(
                f"<strong>Item Effects:</strong> {len(effects)} effect(s)"
            )
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
        armor_display_name = self.get_display_name(armor_info, is_weapon=False)
        title_label = QLabel(f"ARMOR ID: {armor_id} - {armor_display_name}")
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

        # Only show stats that have non-zero values
        stats_info = []
        if armor_info.get("strength", 0) != 0:
            stats_info.append(("Strength", f"+{armor_info.get('strength', 0)}"))
        if armor_info.get("stamina", 0) != 0:
            stats_info.append(("Stamina", f"+{armor_info.get('stamina', 0)}"))
        if armor_info.get("agility", 0) != 0:
            stats_info.append(("Agility", f"+{armor_info.get('agility', 0)}"))
        if armor_info.get("dexterity", 0) != 0:
            stats_info.append(("Dexterity", f"+{armor_info.get('dexterity', 0)}"))
        if armor_info.get("intelligence", 0) != 0:
            stats_info.append(("Intelligence", f"+{armor_info.get('intelligence', 0)}"))
        if armor_info.get("wisdom", 0) != 0:
            stats_info.append(("Wisdom", f"+{armor_info.get('wisdom', 0)}"))
        if armor_info.get("charisma", 0) != 0:
            stats_info.append(("Charisma", f"+{armor_info.get('charisma', 0)}"))

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

        special_info = [
            ("Movement Speed", f"{armor_info.get('move_speed_bonus', 0)}%"),
            ("Fight Speed", f"{armor_info.get('fight_speed_bonus', 0)}%"),
            ("Cast Speed", f"{armor_info.get('cast_speed_bonus', 0)}%"),
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

        # Add school requirements if available
        school_requirements = req_data.get("school_requirements", [])
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
            effects_label = QLabel(
                f"<strong>Item Effects:</strong> {len(effects)} effect(s)"
            )
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

    def load_cff_file(self):
        """Open a file dialog to select and load a specific CFF file"""
        try:
            # Open file dialog for CFF files
            # Start in current working directory (script directory)
            current_dir = Path.cwd()
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select CFF File",
                str(current_dir),
                "CFF Files (*.cff);;All Files (*)"
            )

            if not file_path:
                # User cancelled the dialog
                return

            # Validate that the file exists
            if not Path(file_path).exists():
                QMessageBox.critical(
                    self,
                    "Error",
                    f"The selected file does not exist:\n{file_path}"
                )
                return

            # Set the custom CFF path
            self.custom_cff_path = file_path

            # Clear current data and reload with new file
            self.weapon_data.clear()
            self.armor_data.clear()
            self.load_data()

            # Show success message with file info
            file_name = Path(file_path).name
            QMessageBox.information(
                self,
                "Success",
                f"Successfully loaded CFF file:\n{file_name}\n\n"
                f"Path: {file_path}"
            )

            # Update status bar
            self.update_status_with_file_info(f"Loaded custom CFF")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load CFF file:\n{e}"
            )
            if self.logger:
                self.logger.exception("Error loading CFF file")

    def reload_data(self):
        """Reload all item data"""
        self.weapon_data.clear()
        self.armor_data.clear()
        # Don't reset custom_cff_path anymore - preserve it
        self.load_data()

    def update_status_with_file_info(self, message_suffix: str = "Ready"):
        """Update status bar with current file information"""
        if self.custom_cff_path:
            file_name = Path(self.custom_cff_path).name
            total_items = len(self.weapon_data) + len(self.armor_data)
            self.statusBar().showMessage(
                f"📁 {file_name} | {total_items} items | {message_suffix}"
            )
        else:
            total_items = len(self.weapon_data) + len(self.armor_data)
            self.statusBar().showMessage(
                f"📁 Default GameData.cff | {total_items} items | {message_suffix}"
            )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Orthancs Schmiede - Weapon & Armor Suite"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Configure logging if debug mode
    if args.debug:
        configure_logging()

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Orthancs Schmiede")
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
    window = OrthancsSchmiede()
    window.show()

    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
