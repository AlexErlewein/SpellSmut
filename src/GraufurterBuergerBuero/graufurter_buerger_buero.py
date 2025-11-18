#!/usr/bin/env python3
"""
Graufurter Bürger Büro - NPC Browser and Creation Suite
========================================================

A comprehensive application for browsing and creating SpellForce NPCs.
Features enhanced UI/UX, integrated creation wizards, and detailed NPC inspection.

Usage:
    python graufurter_buerger_buero.py [--debug] [--rebuild-cache]

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
from TirganachReloaded.tirganach.types import Language  # noqa: E402

# Import NPC-specific modules (will need path adjustments)
from npc_creator_wizard import NpcCreatorWizard  # noqa: E402
from id_manager import IDManager  # noqa: E402


class GraufurterBuergerBuero(QMainWindow):
    """Main application window for Graufurter Bürger Büro (NPC Creator)"""

    def __init__(self):
        super().__init__()
        self.logger = None
        self.id_manager = None
        self.npc_data = {}
        self.current_language = Language.GERMAN
        self.custom_cff_path = None

        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the enhanced user interface"""
        self.setWindowTitle("Graufurter Bürger Büro - NPC Creation Suite")
        self.setMinimumSize(QSize(1600, 1000))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Header with enhanced controls
        header_layout = QHBoxLayout()
        title_label = QLabel("Graufurter Bürger Büro")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #6fb3d2;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

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
        self.search_edit.setPlaceholderText("Search NPCs...")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        header_layout.addWidget(self.search_edit)

        # Enhanced buttons
        create_npc_btn = QPushButton("Create NPC")
        create_npc_btn.clicked.connect(self.create_npc)
        create_npc_btn.setStyleSheet(
            "QPushButton { background-color: #3c3c3c; color: #e0e0e0; font-weight: bold; padding: 8px; border-radius: 4px; border: 1px solid #555; } QPushButton:hover { background-color: #4a4a4a; }"
        )
        header_layout.addWidget(create_npc_btn)

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

        # Left side - NPC tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.tree_group = QGroupBox("NPCs (Loading...)")
        tree_layout = QVBoxLayout(self.tree_group)

        self.npc_tree = QTreeWidget()
        self.npc_tree.setHeaderLabels(["Name", "Type", "Class", "Level", "ID"])
        self.npc_tree.itemSelectionChanged.connect(self.on_npc_selection_changed)

        # Dark theme tree styling
        self.npc_tree.setStyleSheet("""
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

        tree_layout.addWidget(self.npc_tree)

        # Enhanced tree controls
        tree_controls = QHBoxLayout()
        expand_btn = QPushButton("Expand All")
        expand_btn.clicked.connect(self.npc_tree.expandAll)
        expand_btn.setStyleSheet("QPushButton { padding: 6px; }")
        collapse_btn = QPushButton("Collapse All")
        collapse_btn.clicked.connect(self.npc_tree.collapseAll)
        collapse_btn.setStyleSheet("QPushButton { padding: 6px; }")
        tree_controls.addWidget(expand_btn)
        tree_controls.addWidget(collapse_btn)
        tree_controls.addStretch()

        # Add NPC count label
        self.npc_count_label = QLabel("Loading...")
        tree_controls.addWidget(self.npc_count_label)

        tree_layout.addLayout(tree_controls)

        left_layout.addWidget(self.tree_group)
        splitter.addWidget(left_widget)

        # Right side - NPC details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        details_group = QGroupBox("NPC Details")
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
        self.statusBar().showMessage("Ready - Graufurter Bürger Büro Loaded")

        # Update status with current file info
        self.update_status_with_file_info()

    def load_data(self):
        """Load NPC data"""
        try:
            self.statusBar().showMessage("Initializing Graufurter Bürger Büro...")

            # Configure logging
            if not self.logger:
                configure_logging()
                self.logger = get_logger("graufurter_buerger_buero")

            # Initialize ID manager
            if not self.id_manager:
                self.id_manager = IDManager()

            # Update status message based on whether we're loading custom CFF
            if self.custom_cff_path:
                file_name = Path(self.custom_cff_path).name
                self.statusBar().showMessage(f"Loading NPCs from {file_name}...")
            else:
                self.statusBar().showMessage("Loading NPC data...")
            
            self.load_npc_data()

            self.statusBar().showMessage("Building NPC trees...")
            self.populate_npc_tree()

            total_npcs = len(self.npc_data)
            self.npc_count_label.setText(f"Total: {total_npcs} NPCs")

            # Update final status message
            self.update_status_with_file_info("Graufurter Bürger Büro Ready")

        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to load NPC data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load NPC data:\n{e}")
            self.statusBar().showMessage("❌ Failed to load data")

    def load_npc_data(self):
        """Load NPC data from CFF or JSON files"""
        try:
            # Import loaders
            from npc_loader import load_all_npcs
            from cff_npc_loader import CFFNpcLoader

            # Load custom NPCs from JSON (always)
            custom_npcs = load_all_npcs()
            if self.logger:
                self.logger.info(f"✓ Loaded {len(custom_npcs)} custom NPCs from JSON")

            # Load game NPCs from CFF if requested
            game_npcs = {}
            if self.custom_cff_path:
                try:
                    if self.logger:
                        self.logger.info(f"Loading NPCs from CFF: {self.custom_cff_path}")
                    
                    cff_loader = CFFNpcLoader()
                    game_npcs = cff_loader.load_all_npcs(cff_file_path=self.custom_cff_path)
                    
                    if self.logger:
                        self.logger.info(f"✓ Loaded {len(game_npcs)} game NPCs from CFF")
                except Exception as cff_error:
                    if self.logger:
                        self.logger.error(f"Failed to load CFF NPCs: {cff_error}")
                        self.logger.exception(cff_error)

            # Merge both datasets (custom NPCs override game NPCs if same ID)
            self.npc_data = {**game_npcs, **custom_npcs}
            
            if self.logger:
                self.logger.info(f"✓ Total NPCs available: {len(self.npc_data)} ({len(custom_npcs)} custom + {len(game_npcs)} game)")

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load NPC data: {e}")
                self.logger.exception(e)
            self.npc_data = {}

    def clear_details_content(self):
        """Clear all widgets in the details content area"""
        while self.details_content_layout.count():
            child = self.details_content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def populate_npc_tree(self):
        """Populate the NPC tree with NPCs grouped by type"""
        self.npc_tree.clear()

        # Update tree title regardless of whether we have NPCs
        total_npcs = len(self.npc_data)
        self.tree_group.setTitle(f"NPCs ({total_npcs} loaded)")

        if not self.npc_data:
            if self.logger:
                self.logger.info("No custom NPCs found. Click 'Create NPC' to create your first NPC!")
            # Show helpful message in tree
            placeholder = QTreeWidgetItem(self.npc_tree, ["No NPCs created yet", "", "", "", ""])
            placeholder.setForeground(0, Qt.GlobalColor.gray)
            return

        # Separate custom and game NPCs
        custom_npcs = {}
        game_npcs = {}
        
        for npc_id, npc_info in self.npc_data.items():
            # Custom NPCs have ID >= 40000
            if npc_id >= 40000:
                custom_npcs[npc_id] = npc_info
            else:
                game_npcs[npc_id] = npc_info

        # Create Custom NPCs section
        if custom_npcs:
            custom_root = QTreeWidgetItem(self.npc_tree, [f"Custom NPCs ({len(custom_npcs)})", "", "", "", ""])
            custom_root.setFont(0, QFont("", -1, QFont.Weight.Bold))
            self._populate_npc_categories(custom_root, custom_npcs)
            custom_root.setExpanded(True)

        # Create Game NPCs section
        if game_npcs:
            game_root = QTreeWidgetItem(self.npc_tree, [f"Game NPCs ({len(game_npcs)})", "", "", "", ""])
            game_root.setFont(0, QFont("", -1, QFont.Weight.Bold))
            self._populate_npc_categories(game_root, game_npcs)
            game_root.setExpanded(False)  # Collapsed by default

        # Resize columns to fit content
        self.npc_tree.resizeColumnToContents(0)
        self.npc_tree.resizeColumnToContents(1)
        self.npc_tree.resizeColumnToContents(2)
        self.npc_tree.resizeColumnToContents(3)
        self.npc_tree.resizeColumnToContents(4)

        if self.logger:
            self.logger.info(f"✓ NPC tree populated: {len(custom_npcs)} custom, {len(game_npcs)} game")

        # Re-apply any active search filter after repopulating
        if hasattr(self, "search_edit") and self.search_edit is not None:
            self.apply_search_filter(self.search_edit.text())

    def _populate_npc_categories(self, parent_node, npcs_dict):
        """Helper to populate NPC categories under a parent node"""
        # Group NPCs by type
        npc_categories = {}

        for npc_id, npc_info in npcs_dict.items():
            npc_type = npc_info.get("npc_type", "Unknown")
            if npc_type not in npc_categories:
                npc_categories[npc_type] = []
            npc_categories[npc_type].append((npc_id, npc_info))

        # Create category nodes
        for category_name in sorted(npc_categories.keys()):
            category_node = QTreeWidgetItem(
                parent_node,
                [
                    category_name.title(),
                    "",
                    "",
                    "",
                    f"({len(npc_categories[category_name])} NPCs)",
                ],
            )
            category_node.setFont(0, QFont("", -1, QFont.Weight.Bold))

            # Add NPCs under this category
            for npc_id, npc_info in sorted(npc_categories[category_name]):
                name = npc_info.get("name", f"NPC {npc_id}")
                npc_type = npc_info.get("npc_type", "Unknown")
                char_class = npc_info.get("character_class", "Unknown")
                level = npc_info.get("level", 0)
                
                item = QTreeWidgetItem(
                    category_node, [name, npc_type, char_class, str(level), str(npc_id)]
                )
                item.setData(0, Qt.ItemDataRole.UserRole, ("npc", npc_id))

    def on_search_text_changed(self, text: str):
        self.apply_search_filter(text)

    def apply_search_filter(self, text: str):
        query = (text or "").strip().lower()
        # Nothing to filter: show everything
        if query == "":
            for i in range(self.npc_tree.topLevelItemCount()):
                root = self.npc_tree.topLevelItem(i)
                root.setHidden(False)
                self._set_visibility_recursive(root, True)
            return

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

        for i in range(self.npc_tree.topLevelItemCount()):
            root = self.npc_tree.topLevelItem(i)
            filter_node(root)

    def _set_visibility_recursive(self, node, visible: bool):
        node.setHidden(not visible)
        for i in range(node.childCount()):
            self._set_visibility_recursive(node.child(i), visible)

    def on_language_changed(self, label: str):
        # Update current language based on dropdown
        self.current_language = self._lang_map.get(label, Language.GERMAN)
        # Rebuild tree with new localisation
        self.populate_npc_tree()

    def on_npc_selection_changed(self):
        """Handle NPC selection"""
        selected_items = self.npc_tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        item_data = item.data(0, Qt.ItemDataRole.UserRole)

        if item_data:
            item_type, npc_id = item_data
            if item_type == "npc" and npc_id in self.npc_data:
                self.show_npc_details(npc_id)

    def show_npc_details(self, npc_id):
        """Show detailed information for selected NPC"""
        npc_info = self.npc_data[npc_id]

        # Clear previous content
        self.clear_details_content()

        # Main title
        npc_name = npc_info.get("name", f"NPC {npc_id}")
        title_label = QLabel(f"NPC ID: {npc_id} - {npc_name}")
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
            ("Name", npc_name),
            ("Type", npc_info.get("npc_type", "Unknown")),
            ("Class", npc_info.get("character_class", "Unknown")),
            ("Level", str(npc_info.get("level", 0))),
            ("Faction", npc_info.get("faction", "Unknown")),
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

        self.details_content_layout.addWidget(basic_group)

        # Combat Stats Section
        derived_stats = npc_info.get("derived_stats", {})
        if derived_stats:
            stats_group = QGroupBox("COMBAT STATS")
            stats_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    color: #d2916f;
                    border: 2px solid #d2916f;
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

            stats_info = [
                ("Health", str(derived_stats.get("health", 0))),
                ("Mana", str(derived_stats.get("mana", 0))),
                ("Melee Attack", str(derived_stats.get("melee_attack", 0))),
                ("Ranged Attack", str(derived_stats.get("ranged_attack", 0))),
                ("Magic Attack", str(derived_stats.get("magic_attack", 0))),
                ("Physical Defense", str(derived_stats.get("physical_defense", 0))),
                ("Magic Defense", str(derived_stats.get("magic_defense", 0))),
            ]

            for label, value in stats_info:
                row_layout = QHBoxLayout()
                label_widget = QLabel(f"<strong>{label}:</strong>")
                label_widget.setStyleSheet("color: #a0a0a0; min-width: 150px;")
                value_widget = QLabel(str(value))
                value_widget.setStyleSheet("color: #e0e0e0;")
                row_layout.addWidget(label_widget)
                row_layout.addWidget(value_widget)
                row_layout.addStretch()
                stats_layout.addLayout(row_layout)

            self.details_content_layout.addWidget(stats_group)

        # Equipment Section
        equipment = npc_info.get("equipment", {})
        if equipment and any(v is not None for v in equipment.values()):
            equip_group = QGroupBox("EQUIPMENT")
            equip_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    color: #9fd26f;
                    border: 2px solid #9fd26f;
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
            equip_layout = QVBoxLayout(equip_group)

            equip_slots = [
                ("Helmet", equipment.get("helmet_item_id")),
                ("Chest", equipment.get("chest_item_id")),
                ("Legs", equipment.get("legs_item_id")),
                ("Right Hand", equipment.get("right_hand_item_id")),
                ("Left Hand", equipment.get("left_hand_item_id")),
                ("Right Ring", equipment.get("right_ring_item_id")),
                ("Left Ring", equipment.get("left_ring_item_id")),
            ]

            for label, item_id in equip_slots:
                if item_id is not None:
                    row_layout = QHBoxLayout()
                    label_widget = QLabel(f"<strong>{label}:</strong>")
                    label_widget.setStyleSheet("color: #a0a0a0; min-width: 120px;")
                    value_widget = QLabel(f"Item ID {item_id}")
                    value_widget.setStyleSheet("color: #e0e0e0;")
                    row_layout.addWidget(label_widget)
                    row_layout.addWidget(value_widget)
                    row_layout.addStretch()
                    equip_layout.addLayout(row_layout)

            self.details_content_layout.addWidget(equip_group)

        # Skills Section
        skills = npc_info.get("skills", [])
        if skills:
            skills_group = QGroupBox(f"SKILLS ({len(skills)})")
            skills_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    color: #d26fc4;
                    border: 2px solid #d26fc4;
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
            skills_layout = QVBoxLayout(skills_group)

            for skill in skills:
                row_layout = QHBoxLayout()
                school = skill.get("school", "Unknown")
                level = skill.get("level", 0)
                label_widget = QLabel(f"<strong>{school}:</strong>")
                label_widget.setStyleSheet("color: #a0a0a0; min-width: 200px;")
                value_widget = QLabel(f"Level {level}")
                value_widget.setStyleSheet("color: #e0e0e0;")
                row_layout.addWidget(label_widget)
                row_layout.addWidget(value_widget)
                row_layout.addStretch()
                skills_layout.addLayout(row_layout)

            self.details_content_layout.addWidget(skills_group)

        # Spells Section
        spells = npc_info.get("spells", [])
        if spells:
            spells_group = QGroupBox(f"SPELLS ({len(spells)})")
            spells_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    color: #6fd2d2;
                    border: 2px solid #6fd2d2;
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
            spells_layout = QVBoxLayout(spells_group)

            for spell in spells[:10]:  # Show first 10 spells
                row_layout = QHBoxLayout()
                spell_id = spell.get("spell_id", 0)
                position = spell.get("position", 0)
                label_widget = QLabel(f"<strong>Spell ID {spell_id}:</strong>")
                label_widget.setStyleSheet("color: #a0a0a0; min-width: 150px;")
                value_widget = QLabel(f"Position {position}")
                value_widget.setStyleSheet("color: #e0e0e0;")
                row_layout.addWidget(label_widget)
                row_layout.addWidget(value_widget)
                row_layout.addStretch()
                spells_layout.addLayout(row_layout)

            if len(spells) > 10:
                more_label = QLabel(f"<i>... and {len(spells) - 10} more spells</i>")
                more_label.setStyleSheet("color: #808080; font-style: italic;")
                spells_layout.addWidget(more_label)

            self.details_content_layout.addWidget(spells_group)

        # Rewards Section
        rewards = npc_info.get("rewards", {})
        if rewards and (rewards.get("experience", 0) > 0 or rewards.get("gold", 0) > 0):
            rewards_group = QGroupBox("REWARDS")
            rewards_group.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    color: #d2d26f;
                    border: 2px solid #d2d26f;
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
            rewards_layout = QVBoxLayout(rewards_group)

            rewards_info = [
                ("Experience", str(rewards.get("experience", 0))),
                ("Gold", str(rewards.get("gold", 0))),
            ]

            for label, value in rewards_info:
                if int(value) > 0:
                    row_layout = QHBoxLayout()
                    label_widget = QLabel(f"<strong>{label}:</strong>")
                    label_widget.setStyleSheet("color: #a0a0a0; min-width: 120px;")
                    value_widget = QLabel(str(value))
                    value_widget.setStyleSheet("color: #e0e0e0;")
                    row_layout.addWidget(label_widget)
                    row_layout.addWidget(value_widget)
                    row_layout.addStretch()
                    rewards_layout.addLayout(row_layout)

            self.details_content_layout.addWidget(rewards_group)

        # Add stretch to push everything to the top
        self.details_content_layout.addStretch()

    def create_npc(self):
        """Open NPC creation wizard"""
        try:
            wizard = NpcCreatorWizard(self.id_manager, self)
            if wizard.exec():
                # Reload data after successful creation
                self.reload_data()
                if self.logger:
                    self.logger.info("✓ NPC created successfully")
                QMessageBox.information(self, "Success", "NPC created successfully!")
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to create NPC: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create NPC:\n{e}")

    def load_cff_file(self):
        """Load NPCs from a custom CFF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CFF File",
            "",
            "CFF Files (*.cff);;All Files (*)",
        )
        if file_path:
            self.custom_cff_path = file_path
            self.reload_data()

    def reload_data(self):
        """Reload all NPC data"""
        self.load_data()

    def update_status_with_file_info(self, prefix=""):
        """Update status bar with current file information"""
        if self.custom_cff_path:
            file_name = Path(self.custom_cff_path).name
            msg = f"{prefix} - Viewing: {file_name}" if prefix else f"Viewing: {file_name}"
        else:
            msg = f"{prefix} - Viewing: Default Game Data" if prefix else "Viewing: Default Game Data"
        self.statusBar().showMessage(msg)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Graufurter Bürger Büro - NPC Creation Suite")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--rebuild-cache", action="store_true", help="Rebuild game data cache")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = GraufurterBuergerBuero()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
