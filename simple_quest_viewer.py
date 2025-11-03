#!/usr/bin/env python3
"""
Simple Standalone Quest Viewer Application - CLEAN VERSION
==========================================

A lightweight application for viewing SpellForce quest data.
Uses cached Lua files and triggers cache creation if needed.

Usage:
    python simple_quest_viewer_clean.py [--debug] [--rebuild-cache]
"""

import sys
import argparse
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTextEdit, QLabel,
    QPushButton, QGroupBox, QProgressDialog, QMessageBox, QLineEdit, QComboBox,
    QFileDialog
)
from PySide6.QtCore import Qt, QSize

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.logging_config import configure_logging, get_logger
from TirganachReloaded.cff_editor.lua_parser.lua_data_manager import LuaDataManager
from TirganachReloaded.cff_editor.data_model import CFFDataModel

# Platform/Map location name mappings
PLATFORM_NAMES = {
    "P1": "Liannon",
    "P2": "Eloni",
    "P3": "Leafshade",
    "P4": "Wildland Pass",
    "P5": "Shiel",
    "P6": "Wildland Pass / Greyfell area",
    "P7": "Ice Gate",
    "P8": "Underhall",
    "P10": "Iron Fields",
    "P11": "The Shiel",
    "P12": "峡谷",
    "P15": "Desert / Burning Sands",
    "P16": "Whisper",
    "P17": "Tirganach",
    "P19": "Dun Mora",
    "P23": "The Gorge",
    "P25": "Godmark / Mountains",
    "P27": "Urgath",
    "P30": "Breathing Forest",
    "P32": "Soul Forge",
    "P63": "Greyfell",
    "P101": "Tutorial",
    "P105": "Tirganach",
    "P107": "Encounter Map",
    "P108": "Encounter Map",
    "P109": "Warzone",
    "P110": "Ghost Watch",
    "P111": "Shadow Realm",
    "P113": "Undergound",
    "P115": "Dragon Storm"
}


def get_platform_display_name(platform_id):
    """Convert platform ID to display name (e.g., P1 -> Liannon (P1))"""
    if not platform_id:
        return "Unknown Location"

    platform_name = PLATFORM_NAMES.get(platform_id, None)
    if platform_name:
        return f"{platform_name} ({platform_id})"
    return platform_id


class SimpleQuestViewer(QMainWindow):
    """Simple standalone quest viewer"""

    def __init__(self):
        super().__init__()
        self.logger = None
        self.lua_manager = None
        self.data_model = None
        self.quest_data = {}
        self.current_quest_id = None

        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("TirganachReloaded: Simple Quest Viewer")
        self.setMinimumSize(QSize(1200, 800))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Header with reload button
        header_layout = QHBoxLayout()
        title_label = QLabel("Quest Viewer")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        export_btn = QPushButton("Export Quest")
        export_btn.clicked.connect(self.export_quest)
        export_btn.setEnabled(False)  # Disabled until quest is selected
        self.export_btn = export_btn
        header_layout.addWidget(export_btn)

        reload_btn = QPushButton("Reload Data")
        reload_btn.clicked.connect(self.reload_data)
        header_layout.addWidget(reload_btn)

        rebuild_cache_btn = QPushButton("Rebuild Cache")
        rebuild_cache_btn.clicked.connect(self.rebuild_cache)
        header_layout.addWidget(rebuild_cache_btn)
        
        layout.addLayout(header_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Quest tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        tree_group = QGroupBox("Quests")
        tree_layout = QVBoxLayout(tree_group)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID, name, or description...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        tree_layout.addLayout(search_layout)

        # Filter dropdowns
        filter_layout = QHBoxLayout()

        # Platform/Location filter
        platform_label = QLabel("Location:")
        self.platform_filter = QComboBox()
        self.platform_filter.addItem("All Locations", None)
        for pid in sorted(PLATFORM_NAMES.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 999):
            name = PLATFORM_NAMES[pid]
            self.platform_filter.addItem(f"{name} ({pid})", pid)
        self.platform_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(platform_label)
        filter_layout.addWidget(self.platform_filter)

        # Quest Giver filter (will be populated after data loads)
        giver_label = QLabel("Quest Giver:")
        self.giver_filter = QComboBox()
        self.giver_filter.addItem("All Quest Givers", None)
        self.giver_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(giver_label)
        filter_layout.addWidget(self.giver_filter)

        filter_layout.addStretch()
        tree_layout.addLayout(filter_layout)

        # Search results label
        self.search_results_label = QLabel("")
        self.search_results_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        tree_layout.addWidget(self.search_results_label)

        self.quest_tree = QTreeWidget()
        self.quest_tree.setHeaderLabels(["Quest Name"])
        self.quest_tree.setColumnWidth(0, 400)  # Make name column wider
        self.quest_tree.itemSelectionChanged.connect(lambda: self.on_quest_selection_changed())
        tree_layout.addWidget(self.quest_tree)
        
        # Tree controls
        tree_controls = QHBoxLayout()
        expand_btn = QPushButton("Expand All")
        expand_btn.clicked.connect(self.quest_tree.expandAll)
        collapse_btn = QPushButton("Collapse All")
        collapse_btn.clicked.connect(self.quest_tree.collapseAll)
        tree_controls.addWidget(expand_btn)
        tree_controls.addWidget(collapse_btn)
        tree_layout.addLayout(tree_controls)
        
        left_layout.addWidget(tree_group)
        splitter.addWidget(left_widget)
        
        # Right side - Quest details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        details_group = QGroupBox("Quest Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setHtml("<p>Select a quest to view details...</p>")
        details_layout.addWidget(self.details_text)
        
        right_layout.addWidget(details_group)
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def load_data(self):
        """Load quest data"""
        try:
            self.statusBar().showMessage("Loading quest data...")

            # Configure logging
            if not self.logger:
                configure_logging()
                self.logger = get_logger("quest_viewer")

            # Initialize data model (loads CFF data)
            self.data_model = CFFDataModel()

            # Load GameData.cff file
            cff_file = Path("OriginalGameFiles/data/GameData.cff")
            if not cff_file.exists():
                QMessageBox.critical(self, "Error", f"GameData.cff not found at:\n{cff_file}")
                return

            self.logger.info(f"Loading CFF file: {cff_file}")
            if not self.data_model.load_file(str(cff_file)):
                QMessageBox.critical(self, "Error", "Failed to load GameData.cff")
                return

            # Initialize Lua data manager for additional details
            cache_dir = Path("src/TirganachReloaded/data/cache")
            self.lua_manager = LuaDataManager(cache_dir=cache_dir)

            # Load quest data from CFF (all quests with names!)
            self.load_cff_quest_data()

            # Enhance with Lua data (dialogues, rewards, etc.)
            self.load_lua_quest_data()

            # Populate tree
            self.populate_quest_tree()

            # Populate quest giver filter dropdown
            self.populate_quest_giver_filter()

            quest_count = len(self.quest_data)
            self.statusBar().showMessage(f"Loaded {quest_count} quests")
            self.logger.info(f"Successfully loaded {quest_count} quests")

        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to load quest data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load quest data:\n{e}")
            self.statusBar().showMessage("Failed to load data")
    
    def load_cff_quest_data(self):
        """Load quest data from CFF file via data model"""
        try:
            # Get all quests from the data model
            quests = self.data_model.get_elements("quests")
            if not quests:
                self.logger.warning("No quests found in CFF file")
                return

            self.logger.info(f"Loading {len(quests)} quests from CFF file")

            # Extract quest information
            for quest in quests:
                quest_id = getattr(quest, "quest_id", None)
                if quest_id is None:
                    continue

                # Get quest name (try localized first)
                name = self.data_model.get_localised_text(quest, "name")
                if not name:
                    name = getattr(quest, "name", f"Quest {quest_id}")

                # Get description
                description = self.data_model.get_localised_text(quest, "description")
                if not description:
                    description = getattr(quest, "description", "")

                # Get parent ID and order
                parent_id = getattr(quest, "parent_quest_id", None)
                order_index = getattr(quest, "order_index", 0)

                # Store quest data
                self.quest_data[quest_id] = {
                    'id': quest_id,
                    'name': name,
                    'description': description,
                    'parent_id': parent_id,
                    'order_index': order_index,
                    'quest_object': quest  # Store reference for further processing
                }

            self.logger.info(f"Loaded {len(self.quest_data)} quests from CFF")

            # Debug: Check how many have names
            with_names = sum(1 for q in self.quest_data.values() if q['name'] and not q['name'].startswith('Quest '))
            self.logger.info(f"Quests with proper names: {with_names}/{len(self.quest_data)}")

            # Show first 5 quest names as sample
            sample_names = []
            for quest_id in sorted(list(self.quest_data.keys())[:5]):
                sample_names.append(f"{quest_id}: {self.quest_data[quest_id]['name']}")
            self.logger.info(f"Sample quest names: {', '.join(sample_names)}")

        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to load CFF quest data: {e}")
    
    def load_lua_quest_data(self):
        """Load Lua quest data from cache"""
        try:
            if self.lua_manager:
                # Force cache load if not loaded
                if not self.lua_manager.cache_loaded:
                    self.lua_manager.preload_cache()
                
                # Get quests from Lua cache
                quest_ids = self.lua_manager.get_all_quest_ids()
                
                for quest_id in quest_ids:
                    quest_data_obj = self.lua_manager.get_quest_data(quest_id)
                    if quest_data_obj:
                        if quest_id not in self.quest_data:
                            # New quest from Lua that wasn't in CFF
                            self.quest_data[quest_id] = {
                                'id': quest_id,
                                'name': quest_data_obj.quest_name or f'Quest {quest_id}',
                                'description': quest_data_obj.description or '',
                                'parent_id': None,
                                'order_index': 0,
                            }

                        # IMPORTANT: Don't overwrite name/description from CFF!
                        # Only add Lua-specific data (objectives, rewards, etc.)
                        self.quest_data[quest_id].update({
                            'platform': quest_data_obj.platform,
                            'npc_id': quest_data_obj.npc_id,
                            'objectives': quest_data_obj.objectives,
                            'requirements': quest_data_obj.requirements,
                            'rewards': quest_data_obj.rewards,
                            'dialogues': quest_data_obj.dialogues
                        })
                        
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load Lua quest data: {e}")
    
    def populate_quest_tree(self):
        """Populate the quest tree"""
        self.quest_tree.clear()

        if not self.quest_data:
            if self.logger:
                self.logger.warning("No quest data to populate tree")
            return

        if self.logger:
            self.logger.info(f"Populating tree with {len(self.quest_data)} quests")

        # Create quest items with format "Name [ID]"
        items_created = 0
        for quest_id, quest_info in sorted(self.quest_data.items()):
            name = quest_info.get('name', f'Quest {quest_id}')
            display_text = f"{name} [{quest_id}]"

            item = QTreeWidgetItem(self.quest_tree, [display_text])
            item.setData(0, Qt.UserRole, quest_id)
            items_created += 1

            # Debug: Log first 5 items
            if items_created <= 5 and self.logger:
                self.logger.debug(f"Created tree item: ID={quest_id}, Name={name}")
        
        # Create hierarchy (parent-child relationships)
        for quest_id, quest_info in self.quest_data.items():
            parent_id = quest_info.get('parent_id')
            if parent_id is not None and parent_id in self.quest_data:
                # Find parent and child items
                parent_item = None
                child_item = None
                
                for i in range(self.quest_tree.topLevelItemCount()):
                    item = self.quest_tree.topLevelItem(i)
                    item_quest_id = item.data(0, Qt.UserRole)
                    
                    if item_quest_id == parent_id:
                        parent_item = item
                    elif item_quest_id == quest_id:
                        child_item = item
                
                if parent_item and child_item:
                    self.quest_tree.takeTopLevelItem(self.quest_tree.indexOfTopLevelItem(child_item))
                    parent_item.addChild(child_item)

        # Make main quests (top-level items without parents) bold
        for i in range(self.quest_tree.topLevelItemCount()):
            item = self.quest_tree.topLevelItem(i)
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)

        self.quest_tree.expandAll()
    
    def on_quest_selection_changed(self):
        """Handle quest selection"""
        selected_items = self.quest_tree.selectedItems()
        if not selected_items:
            self.export_btn.setEnabled(False)
            self.current_quest_id = None
            return

        item = selected_items[0]
        quest_id = item.data(0, Qt.UserRole)

        if quest_id and quest_id in self.quest_data:
            self.current_quest_id = quest_id
            self.export_btn.setEnabled(True)
            self.show_quest_details(quest_id)
        else:
            self.current_quest_id = None
            self.export_btn.setEnabled(False)
    
    def show_quest_details(self, quest_id):
        """Show details for selected quest with enhanced formatting"""
        quest_info = self.quest_data[quest_id]

        # Build HTML content with styling
        html = "<html><body style='font-family: Arial; font-size: 11pt;'>"

        # Quest Header
        html += f"<h2 style='color: #2c3e50; margin-bottom: 5px;'>{quest_info.get('name', 'Unknown')}</h2>"
        html += f"<p style='color: #7f8c8d; margin-top: 0;'><b>Quest ID:</b> {quest_id}</p>"

        # Description
        if quest_info.get('description'):
            html += "<div style='background-color: #ecf0f1; padding: 10px; border-radius: 5px; margin: 10px 0;'>"
            html += f"<p><b>Description:</b><br>{quest_info['description']}</p>"
            html += "</div>"

        # Location & Quest Giver Section
        html += "<h3 style='color: #34495e; margin-top: 15px; margin-bottom: 5px;'>Location & Quest Giver</h3>"
        html += "<ul style='margin-top: 5px;'>"

        # Platform/Location
        platform = quest_info.get('platform')
        if platform:
            location = get_platform_display_name(platform)
            html += f"<li><b>Location:</b> {location}</li>"
        else:
            html += "<li><b>Location:</b> <span style='color: #95a5a6;'>Unknown</span></li>"

        # Quest Giver (NPC)
        npc_id = quest_info.get('npc_id')
        if npc_id:
            html += f"<li><b>Quest Giver:</b> NPC ID {npc_id}</li>"
        else:
            html += "<li><b>Quest Giver:</b> <span style='color: #95a5a6;'>Unknown</span></li>"

        # Parent Quest
        parent_id = quest_info.get('parent_id')
        if parent_id:
            parent_name = self.quest_data.get(parent_id, {}).get('name', f'Quest {parent_id}')
            html += f"<li><b>Parent Quest:</b> {parent_name} [{parent_id}]</li>"

        html += "</ul>"

        # Requirements
        requirements = quest_info.get('requirements', [])
        if requirements:
            html += "<h3 style='color: #e74c3c; margin-top: 15px; margin-bottom: 5px;'>Requirements</h3>"
            html += "<ul style='margin-top: 5px;'>"
            for req in requirements:
                req_type = getattr(req, 'requirement_type', 'Unknown')
                req_text = getattr(req, 'description', '')
                html += f"<li><span style='color: #c0392b;'>[{req_type}]</span> {req_text}</li>"
            html += "</ul>"

        # Objectives
        objectives = quest_info.get('objectives', [])
        if objectives:
            html += "<h3 style='color: #3498db; margin-top: 15px; margin-bottom: 5px;'>Objectives</h3>"
            html += "<ol style='margin-top: 5px;'>"
            for obj in objectives:
                obj_type = getattr(obj, 'objective_type', 'Unknown')
                obj_text = getattr(obj, 'description', '')
                html += f"<li><span style='color: #2980b9;'>[{obj_type}]</span> {obj_text}</li>"
            html += "</ol>"

        # Rewards
        rewards = quest_info.get('rewards')
        if rewards:
            html += "<h3 style='color: #27ae60; margin-top: 15px; margin-bottom: 5px;'>Rewards</h3>"
            html += "<ul style='margin-top: 5px;'>"

            if hasattr(rewards, 'xp') and rewards.xp > 0:
                html += f"<li><b>XP:</b> {rewards.xp}</li>"
            if hasattr(rewards, 'gold') and rewards.gold > 0:
                html += f"<li><b>Gold:</b> {rewards.gold}</li>"
            if hasattr(rewards, 'silver') and hasattr(rewards, 'copper'):
                if rewards.silver > 0 or rewards.copper > 0:
                    html += f"<li><b>Silver:</b> {getattr(rewards, 'silver', 0)} <b>Copper:</b> {getattr(rewards, 'copper', 0)}</li>"
            if hasattr(rewards, 'items') and rewards.items:
                items_str = ', '.join(map(str, rewards.items))
                html += f"<li><b>Items:</b> {items_str}</li>"

            html += "</ul>"

        # Dialogues
        dialogues = quest_info.get('dialogues', [])
        if dialogues:
            html += "<h3 style='color: #9b59b6; margin-top: 15px; margin-bottom: 5px;'>Dialogues</h3>"
            html += "<div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>"

            for dlg in dialogues:
                speaker = getattr(dlg, 'speaker', 'Unknown')
                dlg_text = getattr(dlg, 'text', '')
                is_player = getattr(dlg, 'is_player_choice', False)

                if dlg_text:
                    if speaker == 'Player' or is_player:
                        # Player dialogue in blue
                        html += f"<p style='margin: 5px 0;'><b style='color: #3498db;'>Player:</b> {dlg_text}</p>"
                    else:
                        # NPC dialogue in green
                        html += f"<p style='margin: 5px 0;'><b style='color: #27ae60;'>NPC:</b> {dlg_text}</p>"

            html += "</div>"

        # Empty state
        if not quest_info.get('description') and not objectives and not requirements and not rewards and not dialogues:
            html += "<p style='color: #95a5a6; font-style: italic; margin-top: 20px;'>No additional details available for this quest.</p>"

        html += "</body></html>"

        self.details_text.setHtml(html)

    def on_search_changed(self, text):
        """Handle search text changes - filter tree items"""
        search_text = text.lower().strip()
        platform_filter = self.platform_filter.currentData()
        giver_filter = self.giver_filter.currentData()

        visible_count = 0

        # Iterate through all top-level items
        for i in range(self.quest_tree.topLevelItemCount()):
            item = self.quest_tree.topLevelItem(i)
            visible = self.filter_tree_item(item, search_text, platform_filter, giver_filter)
            if visible:
                visible_count += 1

        # Update search results label
        if search_text or platform_filter or giver_filter:
            self.search_results_label.setText(f"Showing {visible_count} quest(s)")
        else:
            self.search_results_label.setText("")

    def on_filter_changed(self):
        """Handle filter dropdown changes"""
        # Trigger the same filtering logic as search
        self.on_search_changed(self.search_input.text())

    def filter_tree_item(self, item, search_text, platform_filter, giver_filter):
        """
        Recursively filter tree items based on search text and filters.
        Returns True if item or any child should be visible.
        """
        quest_id = item.data(0, Qt.UserRole)
        quest_info = self.quest_data.get(quest_id, {})

        # Check if this item matches filters
        matches = True

        # Search text filter (ID, name, description)
        if search_text:
            quest_id_str = str(quest_id).lower()
            name = quest_info.get('name', '').lower()
            description = quest_info.get('description', '').lower()

            matches = (search_text in quest_id_str or
                      search_text in name or
                      search_text in description)

        # Platform filter
        if matches and platform_filter:
            quest_platform = quest_info.get('platform', '')
            matches = (quest_platform == platform_filter)

        # Quest giver filter
        if matches and giver_filter:
            quest_npc = quest_info.get('npc_id')
            matches = (quest_npc == giver_filter)

        # Check children recursively
        child_visible = False
        for child_idx in range(item.childCount()):
            child = item.child(child_idx)
            if self.filter_tree_item(child, search_text, platform_filter, giver_filter):
                child_visible = True

        # Show item if it matches OR if any child is visible
        should_show = matches or child_visible
        item.setHidden(not should_show)

        # Expand item if it has visible children
        if child_visible and search_text:
            item.setExpanded(True)

        return should_show

    def populate_quest_giver_filter(self):
        """Populate quest giver filter with unique NPC IDs from loaded quests"""
        # Clear existing items (keep "All Quest Givers")
        self.giver_filter.clear()
        self.giver_filter.addItem("All Quest Givers", None)

        # Collect unique NPC IDs
        npc_ids = set()
        for quest_info in self.quest_data.values():
            npc_id = quest_info.get('npc_id')
            if npc_id:
                npc_ids.add(npc_id)

        # Add to combo box sorted
        for npc_id in sorted(npc_ids):
            self.giver_filter.addItem(f"NPC {npc_id}", npc_id)

    def reload_data(self):
        """Reload quest data"""
        self.quest_data.clear()
        self.data_model = None  # Clear data model to force reload
        self.load_data()
    
    def rebuild_cache(self):
        """Rebuild quest cache from Lua files"""
        try:
            # Look for Lua files
            lua_paths = [
                Path("ModdingTools/SpellForceLUASources"),
                Path("OriginalGameFiles/lua"),
            ]
            
            lua_source_path = None
            for path in lua_paths:
                if path.exists() and path.is_dir():
                    lua_source_path = path
                    break
            
            if lua_source_path:
                progress = QProgressDialog("Rebuilding cache from Lua files...", None, 0, 0, self)
                progress.setWindowModality(Qt.WindowModal)
                progress.show()
                
                QApplication.processEvents()
                
                self.lua_manager.parse_lua_directory(lua_source_path, force_refresh=True)
                
                progress.close()
                
                QMessageBox.information(self, "Success", "Cache rebuilt successfully!")
                self.reload_data()
            else:
                QMessageBox.warning(self, "Warning", "No Lua source directory found.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rebuild cache:\n{e}")

    def export_quest(self):
        """Export the currently selected quest"""
        if not self.current_quest_id:
            QMessageBox.warning(self, "Warning", "Please select a quest to export.")
            return

        # Ask user for export format
        from PySide6.QtWidgets import QDialog, QDialogButtonBox, QRadioButton, QCheckBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Export Quest")
        dialog_layout = QVBoxLayout(dialog)

        # Format selection
        format_label = QLabel("Select export format:")
        dialog_layout.addWidget(format_label)

        json_radio = QRadioButton("JSON")
        json_radio.setChecked(True)
        markdown_radio = QRadioButton("Markdown")

        dialog_layout.addWidget(json_radio)
        dialog_layout.addWidget(markdown_radio)

        # Include sub-quests option
        include_subquests_checkbox = QCheckBox("Include all sub-quests")
        include_subquests_checkbox.setChecked(True)
        dialog_layout.addWidget(include_subquests_checkbox)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)

        if dialog.exec() != QDialog.Accepted:
            return

        # Get export settings
        export_json = json_radio.isChecked()
        include_subquests = include_subquests_checkbox.isChecked()

        # Get file path from user
        if export_json:
            file_filter = "JSON Files (*.json)"
            default_ext = ".json"
        else:
            file_filter = "Markdown Files (*.md)"
            default_ext = ".md"

        quest_name = self.quest_data[self.current_quest_id].get('name', f'Quest_{self.current_quest_id}')
        # Sanitize filename
        safe_name = "".join(c for c in quest_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        default_filename = f"{safe_name}{default_ext}"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Quest",
            default_filename,
            file_filter
        )

        if not file_path:
            return

        try:
            # Collect quest data
            quests_to_export = [self.current_quest_id]

            if include_subquests:
                # Find all sub-quests recursively
                quests_to_export.extend(self.get_all_subquests(self.current_quest_id))

            # Export based on format
            if export_json:
                self.export_to_json(quests_to_export, file_path)
            else:
                self.export_to_markdown(quests_to_export, file_path)

            QMessageBox.information(self, "Success", f"Quest(s) exported successfully to:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export quest:\n{e}")

    def get_all_subquests(self, parent_quest_id):
        """Recursively get all sub-quest IDs for a parent quest"""
        subquests = []

        for quest_id, quest_info in self.quest_data.items():
            if quest_info.get('parent_id') == parent_quest_id:
                subquests.append(quest_id)
                # Recursively get sub-quests of this sub-quest
                subquests.extend(self.get_all_subquests(quest_id))

        return subquests

    def export_to_json(self, quest_ids, file_path):
        """Export quests to JSON format"""
        export_data = []

        for quest_id in quest_ids:
            quest_info = self.quest_data[quest_id].copy()

            # Convert complex objects to serializable format
            if 'objectives' in quest_info and quest_info['objectives']:
                quest_info['objectives'] = [
                    {
                        'type': getattr(obj, 'type', 'unknown'),
                        'text': getattr(obj, 'text', ''),
                    }
                    for obj in quest_info['objectives']
                ]

            if 'requirements' in quest_info and quest_info['requirements']:
                quest_info['requirements'] = [
                    {
                        'type': getattr(req, 'type', 'unknown'),
                        'text': getattr(req, 'text', ''),
                    }
                    for req in quest_info['requirements']
                ]

            if 'rewards' in quest_info and quest_info['rewards']:
                rewards = quest_info['rewards']
                quest_info['rewards'] = {
                    'xp': getattr(rewards, 'xp', 0),
                    'gold': getattr(rewards, 'gold', 0),
                    'silver': getattr(rewards, 'silver', 0),
                    'copper': getattr(rewards, 'copper', 0),
                    'items': list(getattr(rewards, 'items', [])),
                }

            if 'dialogues' in quest_info and quest_info['dialogues']:
                quest_info['dialogues'] = [
                    {
                        'speaker': getattr(dlg, 'speaker', 'Unknown'),
                        'text': getattr(dlg, 'text', ''),
                        'is_player': getattr(dlg, 'is_player_choice', False),
                    }
                    for dlg in quest_info['dialogues']
                ]

            export_data.append(quest_info)

        # Write to JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def export_to_markdown(self, quest_ids, file_path):
        """Export quests to Markdown format"""
        lines = []

        for idx, quest_id in enumerate(quest_ids):
            quest_info = self.quest_data[quest_id]

            # Quest header
            if idx == 0:
                lines.append(f"# {quest_info.get('name', 'Unknown Quest')}")
            else:
                lines.append(f"\n## {quest_info.get('name', 'Unknown Quest')}")

            lines.append(f"\n**Quest ID:** {quest_id}")

            # Parent quest
            parent_id = quest_info.get('parent_id')
            if parent_id:
                parent_name = self.quest_data.get(parent_id, {}).get('name', f'Quest {parent_id}')
                lines.append(f"**Parent Quest:** {parent_name} (ID: {parent_id})")

            # Location
            platform = quest_info.get('platform')
            if platform:
                location = get_platform_display_name(platform)
                lines.append(f"**Location:** {location}")

            # Quest Giver
            npc_id = quest_info.get('npc_id')
            if npc_id:
                lines.append(f"**Quest Giver:** NPC {npc_id}")

            # Description
            if quest_info.get('description'):
                lines.append(f"\n### Description\n\n{quest_info['description']}")

            # Objectives
            objectives = quest_info.get('objectives', [])
            if objectives:
                lines.append("\n### Objectives\n")
                for obj in objectives:
                    obj_type = getattr(obj, 'type', 'unknown')
                    obj_text = getattr(obj, 'text', '')
                    lines.append(f"- **[{obj_type}]** {obj_text}")

            # Requirements
            requirements = quest_info.get('requirements', [])
            if requirements:
                lines.append("\n### Requirements\n")
                for req in requirements:
                    req_type = getattr(req, 'type', 'unknown')
                    req_text = getattr(req, 'text', '')
                    lines.append(f"- **[{req_type}]** {req_text}")

            # Rewards
            rewards = quest_info.get('rewards')
            if rewards:
                lines.append("\n### Rewards\n")
                if hasattr(rewards, 'xp') and rewards.xp > 0:
                    lines.append(f"- **XP:** {rewards.xp}")
                if hasattr(rewards, 'gold') and rewards.gold > 0:
                    lines.append(f"- **Gold:** {rewards.gold}")
                if hasattr(rewards, 'silver') or hasattr(rewards, 'copper'):
                    silver = getattr(rewards, 'silver', 0)
                    copper = getattr(rewards, 'copper', 0)
                    if silver > 0 or copper > 0:
                        lines.append(f"- **Silver:** {silver}, **Copper:** {copper}")
                if hasattr(rewards, 'items') and rewards.items:
                    items_str = ', '.join(map(str, rewards.items))
                    lines.append(f"- **Items:** {items_str}")

            # Dialogues
            dialogues = quest_info.get('dialogues', [])
            if dialogues:
                lines.append("\n### Dialogues\n")
                for dlg in dialogues:
                    speaker = getattr(dlg, 'speaker', 'Unknown')
                    dlg_text = getattr(dlg, 'text', '')
                    is_player = getattr(dlg, 'is_player_choice', False)

                    if dlg_text:
                        if speaker == 'Player' or is_player:
                            lines.append(f"- **Player:** {dlg_text}")
                        else:
                            lines.append(f"- **NPC:** {dlg_text}")

            lines.append("\n---\n")

        # Write to markdown file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="TirganachReloaded Simple Quest Viewer")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Configure logging if debug mode
    if args.debug:
        configure_logging()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("TirganachReloaded Simple Quest Viewer")
    app.setOrganizationName("SpellSmut Modding Tools")
    
    # Create and show main window
    window = SimpleQuestViewer()
    window.show()
    
    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())