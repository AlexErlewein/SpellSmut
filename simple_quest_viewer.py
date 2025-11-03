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
    QPushButton, QGroupBox, QProgressDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSize

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.logging_config import configure_logging, get_logger
from TirganachReloaded.cff_editor.lua_parser.lua_data_manager import LuaDataManager
from TirganachReloaded.cff_editor.data_model import CFFDataModel


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
        self.quest_tree.setHeaderLabels(["Quest ID", "Name"])
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
        self.details_text.setPlainText("Select a quest to view details...")
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

        # Create quest items
        items_created = 0
        for quest_id, quest_info in sorted(self.quest_data.items()):
            name = quest_info.get('name', f'Quest {quest_id}')
            item = QTreeWidgetItem(self.quest_tree, [str(quest_id), name])
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
        """Show details for selected quest"""
        quest_info = self.quest_data[quest_id]
        
        details = []
        details.append(f"Quest ID: {quest_id}")
        details.append(f"Name: {quest_info.get('name', 'Unknown')}")
        details.append("")
        
        # Description
        if quest_info.get('description'):
            details.append("Description:")
            details.append(quest_info['description'])
            details.append("")
        
        # Basic info
        details.append("Basic Information:")
        if quest_info.get('parent_id'):
            details.append(f"  Parent Quest: {quest_info['parent_id']}")
        if quest_info.get('platform'):
            details.append(f"  Platform: {quest_info['platform']}")
        if quest_info.get('npc_id'):
            details.append(f"  NPC ID: {quest_info['npc_id']}")
        details.append("")
        
        # Objectives
        objectives = quest_info.get('objectives', [])
        if objectives:
            details.append("Objectives:")
            for obj in objectives:
                obj_type = getattr(obj, 'objective_type', 'Unknown')
                obj_text = getattr(obj, 'description', '')
                details.append(f"  - [{obj_type}] {obj_text}")
            details.append("")
        
        # Requirements
        requirements = quest_info.get('requirements', [])
        if requirements:
            details.append("Requirements:")
            for req in requirements:
                req_type = getattr(req, 'requirement_type', 'Unknown')
                req_text = getattr(req, 'description', '')
                details.append(f"  - [{req_type}] {req_text}")
            details.append("")
        
        # Rewards
        rewards = quest_info.get('rewards')
        if rewards:
            details.append("Rewards:")
            if hasattr(rewards, 'xp') and rewards.xp > 0:
                details.append(f"  - XP: {rewards.xp}")
            if hasattr(rewards, 'gold') and rewards.gold > 0:
                details.append(f"  - Gold: {rewards.gold}")
            if hasattr(rewards, 'items') and rewards.items:
                details.append(f"  - Items: {', '.join(map(str, rewards.items))}")
            details.append("")
        
        # Dialogues
        dialogues = quest_info.get('dialogues', [])
        if dialogues:
            details.append("Dialogues:")
            for dlg in dialogues:
                dlg_text = getattr(dlg, 'text', '')
                if dlg_text:
                    details.append(f"  - {dlg_text}")
            details.append("")
        
        if len(details) <= 3:  # Only header and empty lines
            details.append("No additional details available for this quest.")
        
        self.details_text.setPlainText('\n'.join(details))
    
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