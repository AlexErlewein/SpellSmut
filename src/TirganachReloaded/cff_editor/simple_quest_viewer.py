#!/usr/bin/env python3
"""
Enhanced Quest Viewer Application - COMPLETE VERSION
===================================================

A comprehensive application for viewing SpellForce quest data with enhanced UI/UX.
Features German quest names, bold main quests, proper hierarchy display, and quest creation wizard.

Usage:
    python simple_quest_viewer.py [--debug] [--rebuild-cache]
"""

import sys
import argparse
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QTextEdit, QLabel,
    QPushButton, QGroupBox, QProgressDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.logging_config import configure_logging, get_logger
from TirganachReloaded.cff_editor.lua_parser.lua_data_manager import LuaDataManager
from TirganachReloaded.cff_editor.widgets.quest_creation_wizard import QuestCreationWizard


class EnhancedQuestViewer(QMainWindow):
    """Enhanced quest viewer with German names and better UI"""

    def __init__(self):
        super().__init__()
        self.logger = None
        self.lua_manager = None
        self.data_model = None
        self.quest_data = {}

        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the enhanced user interface"""
        self.setWindowTitle("TirganachReloaded: Enhanced Quest Viewer")
        self.setMinimumSize(QSize(1400, 900))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Header with enhanced controls
        header_layout = QHBoxLayout()
        title_label = QLabel("Quest Viewer - Enhanced Edition")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Enhanced buttons
        create_quest_btn = QPushButton("Create Quest")
        create_quest_btn.clicked.connect(self.create_new_quest)
        create_quest_btn.setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 8px; border-radius: 4px; }")
        header_layout.addWidget(create_quest_btn)

        reload_btn = QPushButton("Reload Data")
        reload_btn.clicked.connect(self.reload_data)
        header_layout.addWidget(reload_btn)

        rebuild_cache_btn = QPushButton("Rebuild Cache")
        rebuild_cache_btn.clicked.connect(self.rebuild_cache)
        header_layout.addWidget(rebuild_cache_btn)

        layout.addLayout(header_layout)

        # Main splitter with better proportions
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left side - Enhanced Quest tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        tree_group = QGroupBox("Quests (1040 loaded)")
        tree_layout = QVBoxLayout(tree_group)

        self.quest_tree = QTreeWidget()
        self.quest_tree.setHeaderLabels(["Quest", "Type"])
        self.quest_tree.itemSelectionChanged.connect(self.on_quest_selection_changed)

        # Minimal tree styling (clean interface)
        self.quest_tree.setStyleSheet("""
            QTreeWidget {
                font-size: 12px;
                border: 1px solid #ccc;
            }
            QTreeWidget::item {
                padding: 3px;
            }
            QTreeWidget::item:selected {
                background-color: #e0e0e0;
                color: black;
            }
        """)

        tree_layout.addWidget(self.quest_tree)

        # Enhanced tree controls
        tree_controls = QHBoxLayout()
        expand_btn = QPushButton("Expand All")
        expand_btn.clicked.connect(self.quest_tree.expandAll)
        expand_btn.setStyleSheet("QPushButton { padding: 6px; }")
        collapse_btn = QPushButton("Collapse All")
        collapse_btn.clicked.connect(self.quest_tree.collapseAll)
        collapse_btn.setStyleSheet("QPushButton { padding: 6px; }")
        tree_controls.addWidget(expand_btn)
        tree_controls.addWidget(collapse_btn)
        tree_controls.addStretch()

        # Add quest count label
        self.quest_count_label = QLabel("Loading...")
        tree_controls.addWidget(self.quest_count_label)

        tree_layout.addLayout(tree_controls)

        left_layout.addWidget(tree_group)
        splitter.addWidget(left_widget)

        # Right side - Enhanced Quest details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        details_group = QGroupBox("Quest Details")
        details_layout = QVBoxLayout(details_group)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlainText("Select a quest to view details...")

        # Minimal details styling (clean interface)
        self.details_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                background-color: white;
                color: black;
                border: 1px solid #ccc;
                padding: 10px;
            }
        """)

        details_layout.addWidget(self.details_text)

        right_layout.addWidget(details_group)
        splitter.addWidget(right_widget)

        # Set better splitter proportions (give more space to quest tree)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([700, 700])

        # Simple status bar
        self.statusBar().showMessage("Ready - Quest Viewer Loaded")

    def load_data(self):
        """Load quest data - Fast version with Lua priority"""
        try:
            self.statusBar().showMessage("Initializing quest viewer...")

            # Configure logging
            if not self.logger:
                configure_logging()
                self.logger = get_logger("enhanced_quest_viewer")

            # Initialize data model for CFF operations (used for quest creation)
            if not self.data_model:
                from TirganachReloaded.cff_editor.data_model import CFFDataModel
                self.data_model = CFFDataModel()
                self.data_model.data_modified.connect(self.on_data_model_modified)

            # Start with Lua data (fast and reliable)
            self.statusBar().showMessage("Loading Lua quest data...")
            cache_dir = Path("src/TirganachReloaded/data/cache")
            self.lua_manager = LuaDataManager(cache_dir=cache_dir)

            # Make sure Lua cache is loaded
            if not self.lua_manager.cache_loaded:
                self.statusBar().showMessage("Preloading Lua cache...")
                self.lua_manager.preload_cache()

            self.statusBar().showMessage("Loading quest information...")
            self.load_lua_quest_data()

            # Try CFF data in background (non-blocking)
            self.statusBar().showMessage("Loading CFF enhancements...")
            try:
                # Load game data quickly
                game_data_path = Path("OriginalGameFiles/data/GameData.cff")
                if game_data_path.exists():
                    if self.data_model.load_file(str(game_data_path)):
                        self.logger.info("✓ Successfully loaded GameData.cff")
                        # Try to load CFF quests, but don't block if it's slow
                        self.load_cff_quest_data_fast()
                    else:
                        self.logger.warning("⚠ Failed to load GameData.cff")
            except Exception as cff_error:
                self.logger.warning(f"CFF loading skipped: {cff_error}")

            self.statusBar().showMessage("Building quest tree...")
            self.populate_quest_tree()

            quest_count = len(self.quest_data)
            self.quest_count_label.setText(f"Total: {quest_count} quests")
            tree_group_title = self.findChild(QGroupBox)
            if tree_group_title:
                tree_group_title.setTitle(f"Quests ({quest_count} loaded)")

            self.statusBar().showMessage(f"✅ Loaded {quest_count} quests - Enhanced Viewer Ready")

        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to load quest data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load quest data:\n{e}")
            self.statusBar().showMessage("❌ Failed to load data")

    def load_cff_quest_data_fast(self):
        """Load CFF quest data - Fast version with limited quests"""
        try:
            if not self.data_model or not self.data_model.game_data:
                return

            # Get quests from CFF
            quests_table = getattr(self.data_model.game_data, 'quests', None)
            if not quests_table:
                return

            # Only load first 200 quests to be fast
            quests_to_load = list(quests_table)[:200]
            self.logger.info(f"Loading {len(quests_to_load)} quests from CFF (fast mode)...")

            for quest in quests_to_load:
                quest_id = quest.quest_id

                # Only enhance existing quests from Lua
                if quest_id in self.quest_data:
                    # Try to get German localized name (quick attempt)
                    try:
                        localized_name = self.data_model.get_localised_text(quest, "name")
                        if localized_name and localized_name.strip():
                            self.quest_data[quest_id]['name'] = localized_name.strip()
                            self.quest_data[quest_id]['cff_loaded'] = True
                    except Exception:
                        # Skip localization if it fails
                        pass

            self.logger.info(f"✓ Enhanced {len(quests_to_load)} quests with CFF data")

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Fast CFF loading failed: {e}")

    def load_cff_quest_data(self):
        """Load CFF quest data with optimized loading"""
        try:
            if not self.data_model or not self.data_model.game_data:
                self.logger.warning("No CFF game data available")
                return

            # Get quests from CFF
            quests_table = getattr(self.data_model.game_data, 'quests', None)
            if not quests_table:
                self.logger.warning("No quests table found in CFF data")
                return

            self.logger.info(f"Loading {len(quests_table)} quests from CFF data...")

            # Batch load all quests first, then get names
            quests_to_process = []
            for quest in quests_table:
                quest_id = quest.quest_id
                quests_to_process.append((quest_id, quest))

            # Process in batches to show progress
            batch_size = 100
            total_processed = 0

            for i in range(0, len(quests_to_process), batch_size):
                batch = quests_to_process[i:i + batch_size]

                for quest_id, quest in batch:
                    if quest_id not in self.quest_data:
                        self.quest_data[quest_id] = {}

                    # Use fallback name first (faster)
                    quest_name = f"Quest {quest_id}"

                    # Try to get German localized name (might be slow)
                    try:
                        localized_name = self.data_model.get_localised_text(quest, "name")
                        if localized_name and localized_name.strip():
                            quest_name = localized_name.strip()
                    except Exception as name_error:
                        # If localisation fails, use fallback name
                        pass

                    # Get description
                    quest_description = ""
                    try:
                        if hasattr(quest, 'description') and quest.description:
                            quest_description = str(quest.description)
                    except Exception as desc_error:
                        # If description fails, use empty string
                        pass

                    self.quest_data[quest_id].update({
                        'id': quest_id,
                        'name': quest_name,
                        'description': quest_description,
                        'parent_id': quest.parent_quest_id,
                        'order_index': quest.order_index,
                        'cff_loaded': True
                    })

                    total_processed += 1

                # Update status periodically
                if i % (batch_size * 2) == 0:
                    self.statusBar().showMessage(f"Loading CFF quests: {total_processed}/{len(quests_to_process)}")

            self.logger.info(f"✓ Loaded {len(quests_table)} quests from CFF")

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load CFF quest data: {e}")
                import traceback
                traceback.print_exc()

    def load_lua_quest_data(self):
        """Load Lua quest data to enhance CFF data"""
        try:
            if self.lua_manager and self.lua_manager.cache_loaded:
                # Get quests from Lua cache
                quest_ids = self.lua_manager.get_all_quest_ids()
                if self.logger:
                    self.logger.info(f"Found {len(quest_ids)} quests in Lua cache")

                enhanced_count = 0
                for quest_id in quest_ids:
                    quest_data_obj = self.lua_manager.get_quest_data(quest_id)
                    if quest_data_obj:
                        if quest_id not in self.quest_data:
                            self.quest_data[quest_id] = {
                                'id': quest_id,
                                'name': f'Quest {quest_id}',
                                'description': '',
                                'parent_id': 0,
                                'order_index': 0
                            }

                        # Enhance with Lua data (don't overwrite CFF names!)
                        self.quest_data[quest_id].update({
                            'platform': quest_data_obj.platform,
                            'npc_id': quest_data_obj.npc_id,
                            'objectives': quest_data_obj.objectives,
                            'requirements': quest_data_obj.requirements,
                            'rewards': quest_data_obj.rewards,
                            'dialogues': quest_data_obj.dialogues,
                            'lua_loaded': True
                        })
                        enhanced_count += 1

                if self.logger:
                    self.logger.info(f"✓ Enhanced {enhanced_count} quests with Lua data")
                    self.logger.info(f"✓ Total quests in data: {len(self.quest_data)}")
            else:
                if self.logger:
                    self.logger.warning("Lua manager not available or cache not loaded")

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load Lua quest data: {e}")
                import traceback
                traceback.print_exc()

    def populate_quest_tree(self):
        """Populate the enhanced quest tree with German names and proper formatting"""
        self.quest_tree.clear()

        if self.logger:
            self.logger.info(f"populate_quest_tree called with {len(self.quest_data)} quests")

        if not self.quest_data:
            if self.logger:
                self.logger.warning("No quest data to populate tree")
            return

        # Create quest items with enhanced formatting
        items_created = 0
        for quest_id, quest_info in sorted(self.quest_data.items()):
            name = quest_info.get('name', f'Quest {quest_id}')

            # Format as "Name [ID]" as documented
            display_text = f"{name} [{quest_id}]"

            # Determine quest type for display
            quest_type = "Main Quest" if quest_info.get('parent_id') == 0 else "Sub-Quest"

            item = QTreeWidgetItem(self.quest_tree, [display_text, quest_type])
            item.setData(0, Qt.UserRole, quest_id)

            # Make main quests bold as documented
            if quest_info.get('parent_id') == 0:
                font = item.font(0)
                font.setBold(True)
                font.setPointSize(12)
                item.setFont(0, font)

                # Also make the type column bold
                type_font = item.font(1)
                type_font.setBold(True)
                type_font.setPointSize(10)
                item.setFont(1, type_font)

                # Set a light background for main quests
                item.setBackground(0, Qt.lightGray)
                item.setBackground(1, Qt.lightGray)

            items_created += 1

        if self.logger:
            self.logger.info(f"Created {items_created} tree items")

        # Create hierarchy (parent-child relationships)
        hierarchy_moved = 0
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
                    hierarchy_moved += 1

        if self.logger:
            self.logger.info(f"Moved {hierarchy_moved} items to create hierarchy")

        # Expand main quests by default for better visibility
        expanded_count = 0
        for i in range(self.quest_tree.topLevelItemCount()):
            item = self.quest_tree.topLevelItem(i)
            if item.childCount() > 0:
                item.setExpanded(True)
                expanded_count += 1

        # Resize columns to fit content
        self.quest_tree.resizeColumnToContents(0)
        self.quest_tree.resizeColumnToContents(1)

        if self.logger:
            self.logger.info(f"✓ Enhanced quest tree populated: {items_created} items, {hierarchy_moved} hierarchy moves, {expanded_count} expanded")
            self.logger.info(f"Tree now has {self.quest_tree.topLevelItemCount()} top-level items")

    def on_quest_selection_changed(self):
        """Handle quest selection with enhanced details display"""
        selected_items = self.quest_tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        quest_id = item.data(0, Qt.UserRole)

        if quest_id and quest_id in self.quest_data:
            self.show_enhanced_quest_details(quest_id)

    def show_enhanced_quest_details(self, quest_id):
        """Show enhanced details for selected quest"""
        quest_info = self.quest_data[quest_id]

        details = []

        # Header with quest ID and name
        quest_name = quest_info.get('name', 'Unknown')
        details.append(f"╔══════════════════════════════════════════════════════════════╗")
        details.append(f"║ Quest ID: {quest_id} - {quest_name}")
        details.append(f"╚══════════════════════════════════════════════════════════════╝")
        details.append("")

        # Description
        if quest_info.get('description'):
            details.append("📜 DESCRIPTION:")
            details.append("─" * 60)
            description = quest_info['description']
            # Wrap description for better readability
            words = description.split(' ')
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + word) < 80:
                    current_line += word + " "
                else:
                    lines.append(current_line)
                    current_line = word + " "
            if current_line:
                lines.append(current_line)

            for line in lines:
                details.append(f"  {line}")
            details.append("")

        # Basic information
        details.append("📋 BASIC INFORMATION:")
        details.append("─" * 60)
        if quest_info.get('parent_id'):
            parent_id = quest_info['parent_id']
            parent_name = self.quest_data.get(parent_id, {}).get('name', f'Quest {parent_id}')
            details.append(f"  🏛️  Parent Quest: {parent_name} [{parent_id}]")
        if quest_info.get('order_index'):
            details.append(f"  📊 Order Index: {quest_info['order_index']}")
        if quest_info.get('platform'):
            details.append(f"  🗺️  Platform/Location: {quest_info['platform']}")
        if quest_info.get('npc_id'):
            details.append(f"  👤 Quest Giver NPC ID: {quest_info['npc_id']}")

        # Data sources info
        data_sources = []
        if quest_info.get('cff_loaded'):
            data_sources.append("CFF (German names)")
        if quest_info.get('lua_loaded'):
            data_sources.append("Lua (enhanced data)")
        if data_sources:
            details.append(f"  💾 Data Sources: {', '.join(data_sources)}")
        details.append("")

        # Objectives
        objectives = quest_info.get('objectives', [])
        if objectives:
            details.append("🎯 OBJECTIVES:")
            details.append("─" * 60)
            for i, obj in enumerate(objectives, 1):
                obj_type = getattr(obj, 'objective_type', 'Unknown')
                obj_text = getattr(obj, 'description', '')
                if obj_text:
                    details.append(f"  {i}. [{obj_type}] {obj_text}")
            details.append("")

        # Requirements
        requirements = quest_info.get('requirements', [])
        if requirements:
            details.append("🔒 REQUIREMENTS:")
            details.append("─" * 60)
            for i, req in enumerate(requirements, 1):
                req_type = getattr(req, 'requirement_type', 'Unknown')
                req_text = getattr(req, 'description', '')
                if req_text:
                    details.append(f"  {i}. [{req_type}] {req_text}")
            details.append("")

        # Rewards
        rewards = quest_info.get('rewards')
        if rewards:
            details.append("🏆 REWARDS:")
            details.append("─" * 60)
            if hasattr(rewards, 'xp') and rewards.xp > 0:
                details.append(f"  ⭐ Experience Points: {rewards.xp:,}")
            if hasattr(rewards, 'gold') and rewards.gold > 0:
                details.append(f"  💰 Gold: {rewards.gold:,}")
            if hasattr(rewards, 'silver') and rewards.silver > 0:
                details.append(f"  🪙 Silver: {rewards.silver:,}")
            if hasattr(rewards, 'copper') and rewards.copper > 0:
                details.append(f"  🪙 Copper: {rewards.copper:,}")
            if hasattr(rewards, 'items') and rewards.items:
                items_str = ', '.join(map(str, rewards.items))
                details.append(f"  🎒 Items: {items_str}")
            details.append("")

        # Dialogues
        dialogues = quest_info.get('dialogues', [])
        if dialogues:
            details.append("💬 DIALOGUES:")
            details.append("─" * 60)
            for i, dlg in enumerate(dialogues, 1):
                dlg_text = getattr(dlg, 'text', '')
                dlg_speaker = getattr(dlg, 'speaker', 'Unknown')
                if dlg_text:
                    details.append(f"  {i}. {dlg_speaker}:")
                    # Wrap dialogue text
                    words = dlg_text.split(' ')
                    lines = []
                    current_line = ""
                    for word in words:
                        if len(current_line + word) < 70:
                            current_line += word + " "
                        else:
                            lines.append(current_line)
                            current_line = word + " "
                    if current_line:
                        lines.append(current_line)

                    for line in lines:
                        details.append(f"     {line}")
                    details.append("")

        # Footer
        details.append("╔══════════════════════════════════════════════════════════════╗")
        details.append(f"║ End of Quest {quest_id} Details")
        details.append("╚══════════════════════════════════════════════════════════════╝")

        if len(details) <= 5:  # Only header and footer lines
            details.append("ℹ️  No additional details available for this quest.")

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

    def create_new_quest(self):
        """Launch the Quest Creation Wizard"""
        try:
            if not self.data_model:
                QMessageBox.warning(self, "Warning", "Data model not initialized. Please reload data first.")
                return

            # Create and show the wizard
            wizard = QuestCreationWizard(self.quest_data, self)
            wizard.quest_created.connect(self.on_quest_created)

            # Execute wizard
            if wizard.exec() == QWizard.Accepted:
                # Quest creation handled by on_quest_created signal
                pass

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch quest creation wizard:\n{e}")

    def on_quest_created(self, quest_data):
        """Handle quest creation from wizard"""
        try:
            if not self.data_model:
                QMessageBox.critical(self, "Error", "Data model not available")
                return

            # Create quest in CFF
            new_quest = self.data_model.create_quest(quest_data)

            if new_quest:
                # Add to our quest data
                quest_id = quest_data['quest_id']
                self.quest_data[quest_id] = {
                    'id': quest_id,
                    'name': quest_data['name'],
                    'description': quest_data.get('description', ''),
                    'parent_id': quest_data.get('parent_id', 0),
                    'order_index': quest_data.get('order_index', 0),
                    'platform': quest_data.get('platform'),
                    'npc_id': quest_data.get('npc_id', 0),
                    'objectives': quest_data.get('objectives', []),
                    'requirements': quest_data.get('requirements', []),
                    'rewards': quest_data.get('rewards', {}),
                    'dialogues': quest_data.get('dialogues', []),
                    'cff_loaded': True
                }

                # Refresh quest tree
                self.populate_quest_tree()

                # Find and select the new quest
                self.select_quest_in_tree(quest_id)

                # Update quest count
                quest_count = len(self.quest_data)
                self.quest_count_label.setText(f"Total: {quest_count} quests")

                # Show success message
                QMessageBox.information(self, "Success",
                                      f"Quest '{quest_data['name']}' (ID: {quest_id}) created successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to create quest in data model")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create quest:\n{e}")

    def on_data_model_modified(self):
        """Handle data model modification signals"""
        # Refresh data when CFF changes
        self.reload_data()

    def select_quest_in_tree(self, quest_id):
        """Select a quest in the tree by ID"""
        def find_item(parent, target_id):
            for i in range(parent.childCount()):
                child = parent.child(i)
                child_id = child.data(0, Qt.UserRole)
                if child_id == target_id:
                    return child
                # Recursively search
                found = find_item(child, target_id)
                if found:
                    return found
            return None

        # Search top level items first
        for i in range(self.quest_tree.topLevelItemCount()):
            item = self.quest_tree.topLevelItem(i)
            item_id = item.data(0, Qt.UserRole)
            if item_id == quest_id:
                self.quest_tree.setCurrentItem(item)
                return
            # Search children
            found = find_item(item, quest_id)
            if found:
                self.quest_tree.setCurrentItem(found)
                return


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="TirganachReloaded Enhanced Quest Viewer")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Configure logging if debug mode
    if args.debug:
        configure_logging()

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("TirganachReloaded Enhanced Quest Viewer")
    app.setOrganizationName("SpellSmut Modding Tools")

    # Set application style
    app.setStyle('Fusion')

    # Create and show main window
    window = EnhancedQuestViewer()
    window.show()

    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())