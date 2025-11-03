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
    QPushButton, QGroupBox, QProgressDialog, QMessageBox, QLineEdit, QComboBox
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
                self.logger.debug(f"Created tree item: {display_text}")
        
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
            return
        
        item = selected_items[0]
        quest_id = item.data(0, Qt.UserRole)
        
        if quest_id and quest_id in self.quest_data:
            self.show_quest_details(quest_id)
    
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