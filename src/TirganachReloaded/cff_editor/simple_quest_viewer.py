#!/usr/bin/env python3
"""
Simple Standalone Quest Viewer Application
==========================================

A lightweight application for viewing SpellForce quest data.
Uses cached Lua files and triggers cache creation if needed.

Usage:
    python simple_quest_viewer.py [--debug] [--rebuild-cache]
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


class SimpleQuestViewer(QMainWindow):
    """Simple standalone quest viewer"""
    
    def __init__(self):
        super().__init__()
        self.logger = None
        self.lua_manager = None
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
        self.quest_tree.itemSelectionChanged.connect(self.on_quest_selected)
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
            
            # Initialize Lua data manager
            cache_dir = Path(__file__).parent.parent.parent / "src" / "TirganachReloaded" / "data" / "cache"
            self.lua_manager = LuaDataManager(cache_dir=cache_dir)
            
            # Load quest data from various sources
            self.load_cff_quest_data()
            self.load_lua_quest_data()
            
            # Populate tree
            self.populate_quest_tree()
            
            quest_count = len(self.quest_data)
            self.statusBar().showMessage(f"Loaded {quest_count} quests")
            
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to load quest data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load quest data:\n{e}")
            self.statusBar().showMessage("Failed to load data")
    
    def load_cff_quest_data(self):
        """Load CFF quest data if available"""
        try:
            # Try to load from the standard location
            cff_data_path = Path(__file__).parent.parent.parent / "src" / "TirganachReloaded" / "data" / "cff_quest_data.json"
            if cff_data_path.exists():
                with open(cff_data_path, 'r', encoding='utf-8') as f:
                    cff_data = json.load(f)
                    
                # Extract quest information
                for quest_id_str, quest_info in cff_data.items():
                    quest_id = int(quest_id_str)
                    if quest_id not in self.quest_data:
                        self.quest_data[quest_id] = {}
                    
                    self.quest_data[quest_id].update({
                        'id': quest_id,
                        'name': quest_info.get('name', f'Quest {quest_id}'),
                        'description': quest_info.get('description', ''),
                        'parent_id': quest_info.get('parent_quest_id'),
                        'order_index': quest_info.get('order_index', 0)
                    })
                    
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load CFF quest data: {e}")
    
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
                    quest_data = self.lua_manager.get_quest_data(quest_id)
                    if quest_data:
                        if quest_id not in self.quest_data:
                            self.quest_data[quest_id] = {}
                    
                    self.quest_data[quest_id].update({
                        'id': quest_id,
                        'name': quest_data.name or f'Quest {quest_id}',
                        'description': quest_data.description or '',
                        'platform': quest_data.platform,
                        'npc_id': quest_data.npc_id,
                        'objectives': quest_data.objectives,
                        'requirements': quest_data.requirements,
                        'rewards': quest_data.rewards,
                        'dialogues': quest_data.dialogues
                    })
                    
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load Lua quest data: {e}")
    
    def populate_quest_tree(self):
        """Populate the quest tree"""
        self.quest_tree.clear()
        
        if not self.quest_data:
            return
        
        # Create quest items
        quest_items = []
        for quest_id, quest_info in sorted(self.quest_data.items()):
            name = quest_info.get('name', f'Quest {quest_id}')
            item = QTreeWidgetItem(self.quest_tree, [str(quest_id), name])
            item.setData(0, Qt.UserRole, quest_id)
            quest_items.append(item)
        
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
    
    def on_quest_selected(self):
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
                obj_type = getattr(obj, 'type', 'Unknown')
                obj_text = getattr(obj, 'description', '')
                details.append(f"  - [{obj_type}] {obj_text}")
            details.append("")
        
        # Requirements
        requirements = quest_info.get('requirements', [])
        if requirements:
            details.append("Requirements:")
            for req in requirements:
                req_type = getattr(req, 'type', 'Unknown')
                req_text = getattr(req, 'description', '')
                details.append(f"  - [{req_type}] {req_text}")
            details.append("")
        
        # Rewards
        rewards = quest_info.get('rewards', [])
        if rewards:
            details.append("Rewards:")
            for reward in rewards:
                reward_type = getattr(reward, 'type', 'Unknown')
                reward_amount = getattr(reward, 'amount', '')
                if reward_amount:
                    details.append(f"  - {reward_type}: {reward_amount}")
                else:
                    details.append(f"  - {reward_type}")
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
        self.load_data()
    
    def rebuild_cache(self):
        """Rebuild quest cache from Lua files"""
        try:
            # Look for Lua files
            lua_paths = [
                Path(__file__).parent.parent.parent / "ModdingTools" / "SpellForceLUASources",
                Path(__file__).parent.parent.parent / "OriginalGameFiles" / "lua",
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