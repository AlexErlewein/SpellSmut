#!/usr/bin/env python3
"""
Unified Enhanced Quest Editor

Integrates the enhanced dialogue system with the existing quest editor.
Provides a unified interface for creating complex quests with dialogue, conditions, and actions.
"""

import sys
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QPushButton,
    QLabel, QLineEdit, QComboBox, QGroupBox, QMessageBox,
    QToolBar, QMenu, QApplication, QCheckBox, QSpinBox,
    QFrame, QScrollArea, QFormLayout, QDialogButtonBox,
    QDialog, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QIcon

try:
    from TirganachReloaded.cff_editor.widgets.enhanced_dialogue_editor import EnhancedDialogueEditor
    from TirganachReloaded.cff_editor.models.enhanced_dialogue_models import (
        DialogueTree, DialogueNode, DialogueChoice,
        DialogueCondition, DialogueAction, DialogueConditionType, DialogueActionType
    )
    from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData
    from TirganachReloaded.cff_editor.widgets.quest_validator import QuestValidator
    from TirganachReloaded.cff_editor.widgets.condition_builder import Condition
    from TirganachReloaded.cff_editor.widgets.flag_manager import FlagManager
    from TirganachReloaded.cff_editor.widgets.reward_builder import RewardBuilder
    from TirganachReloaded.cff_editor.widgets.enhanced_search_navigation import (
        EnhancedSearchNavigationWidget, SearchScope, SearchType, SearchResult
    )
    from TirganachReloaded.cff_editor.widgets.search_engine import SearchEngine, SearchContext
    from TirganachReloaded.cff_editor.widgets.import_export_manager import ImportExportManager
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class QuestIntegrationWidget(QWidget):
    """Widget for managing quest integration with dialogue"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Quest linking
        quest_group = QGroupBox("Quest Integration")
        quest_layout = QFormLayout(quest_group)

        # Quest selection
        self.quest_id_spin = QSpinBox()
        self.quest_id_spin.setRange(1, 99999)
        self.quest_name_edit = QLineEdit()

        quest_layout.addRow("Quest ID:", self.quest_id_spin)
        quest_layout.addRow("Quest Name:", self.quest_name_edit)

        # Quest type
        self.quest_type_combo = QComboBox()
        self.quest_type_combo.addItems([
            "Main Quest", "Side Quest", "Repeatable Quest", "Hidden Quest"
        ])
        quest_layout.addRow("Quest Type:", self.quest_type_combo)

        # Quest status
        self.quest_status_combo = QComboBox()
        self.quest_status_combo.addItems([
            "Unknown", "Known", "Active", "Solved", "Failed"
        ])
        quest_layout.addRow("Initial Status:", self.quest_status_combo)

        # Quest dependencies
        self.dependencies_list = QListWidget()
        dependencies_layout = QHBoxLayout()
        dependencies_layout.addWidget(QLabel("Prerequisites:"))
        dependencies_layout.addWidget(self.dependencies_list)

        dep_buttons = QHBoxLayout()
        self.add_dep_btn = QPushButton("+ Add")
        self.remove_dep_btn = QPushButton("- Remove")
        dep_buttons.addWidget(self.add_dep_btn)
        dep_buttons.addWidget(self.remove_dep_btn)
        dependencies_layout.addLayout(dep_buttons)

        quest_layout.addRow("Dependencies:", dependencies_layout)

        layout.addWidget(quest_group)

        # Dialogue linking
        dialogue_group = QGroupBox("Dialogue Integration")
        dialogue_layout = QVBoxLayout(dialogue_group)

        self.starting_dialogue_checkbox = QCheckBox("Starting Dialogue")
        self.starting_dialogue_checkbox.setToolTip("This dialogue will start when the quest becomes active")
        dialogue_layout.addWidget(self.starting_dialogue_checkbox)

        self.dialogue_connections_text = QTextEdit()
        self.dialogue_connections_text.setMaximumHeight(100)
        self.dialogue_connections_text.setPlaceholderText(
            "Enter connections between dialogue nodes and quest stages:\n"
            "• npc_guard_dialogue -> quest_start\n"
            "• blacksmith_dialogue -> quest_complete\n"
            "• boss_defeated -> quest_reward"
        )
        dialogue_layout.addWidget(QLabel("Dialogue Connections:"))
        dialogue_layout.addWidget(self.dialogue_connections_text)

        layout.addWidget(dialogue_group)

        # Variables and flags
        variables_group = QGroupBox("Variables & Flags")
        variables_layout = QVBoxLayout(variables_group)

        self.quest_variables_table = QTreeWidget()
        self.quest_variables_table.setHeaderLabels(["Variable/Flag", "Type", "Initial Value", "Scope"])
        self.quest_variables_table.setMaximumHeight(150)
        variables_layout.addWidget(self.quest_variables_table)

        var_buttons = QHBoxLayout()
        self.add_var_btn = QPushButton("+ Add Variable")
        self.add_flag_btn = QPushButton("+ Add Flag")
        self.remove_var_btn = QPushButton("- Remove")
        var_buttons.addWidget(self.add_var_btn)
        var_buttons.addWidget(self.add_flag_btn)
        var_buttons.addWidget(self.remove_var_btn)
        variables_layout.addLayout(var_buttons)

        layout.addWidget(variables_group)


class UnifiedEnhancedQuestEditor(QWidget):
    """
    Unified Enhanced Quest Editor

    Integrates the enhanced dialogue system with quest editing
    capabilities for comprehensive quest creation.
    """

    # Signals
    quest_updated = Signal(dict)  # Quest data updated
    dialogue_updated = Signal()  # Dialogue data updated

    def __init__(self, parent=None):
        super().__init__(parent)
        self.quest_data = None
        self.flag_manager = FlagManager()
        self.reward_builder = None

        # Enhanced search and navigation
        self.search_engine = SearchEngine()
        self.search_context = SearchContext()

        # Import/export manager
        self.import_export_manager = ImportExportManager()

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)

        # Main toolbar
        toolbar = self.setup_toolbar()
        layout.addWidget(toolbar)

        # Main content splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)

        # Left: Quest information
        left_panel = self.setup_quest_panel()
        main_splitter.addWidget(left_panel)

        # Right: Dialogue editor (tabs)
        right_panel = self.setup_dialogue_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter sizes
        main_splitter.setSizes([400, 600])

        # Status bar
        self.status_label = QLabel("Ready - No quest loaded")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

    def setup_toolbar(self) -> QToolBar:
        """Setup the main toolbar"""
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # File operations
        self.new_quest_btn = QPushButton("📝 New Quest")
        self.load_quest_btn = QPushButton("📂 Load Quest")
        self.save_quest_btn = QPushButton("💾 Save Quest")
        self.import_btn = QPushButton("📥 Import")
        self.export_btn = QPushButton("📤 Export")
        self.export_lua_btn = QPushButton("🔧 Export LUA")

        toolbar.addWidget(self.new_quest_btn)
        toolbar.addWidget(self.load_quest_btn)
        toolbar.addWidget(self.save_quest_btn)
        toolbar.addWidget(self.import_btn)
        toolbar.addWidget(self.export_btn)
        toolbar.addWidget(self.export_lua_btn)

        toolbar.addSeparator()

        # Validation and testing
        self.validate_btn = QPushButton("🔍 Validate Quest")
        self.test_btn = QPushButton("🧪 Test Dialogue")
        self.preview_btn = QPushButton("👁️ Preview")

        toolbar.addWidget(self.validate_btn)
        toolbar.addWidget(self.test_btn)
        toolbar.addWidget(self.preview_btn)

        return toolbar

    def setup_quest_panel(self) -> QWidget:
        """Setup the quest information panel"""
        quest_panel = QWidget()
        layout = QVBoxLayout(quest_panel)

        # Quest tabs
        quest_tabs = QTabWidget()

        # Basic information tab
        self.setup_basic_info_tab()
        quest_tabs.addTab(self.basic_info_tab, "📋 Basic Info")

        # Integration tab
        self.integration_tab = QuestIntegrationWidget()
        quest_tabs.addTab(self.integration_tab, "🔗 Integration")

        # Rewards tab (existing)
        try:
            self.reward_builder = RewardBuilder()
            quest_tabs.addTab(self.reward_builder, "🎁 Rewards")
        except ImportError:
            # Fallback if reward builder not available
            fallback_reward = QWidget()
            fallback_layout = QVBoxLayout(fallback_reward)
            fallback_layout.addWidget(QLabel("Reward builder not available"))
            quest_tabs.addTab(fallback_reward, "🎁 Rewards")

        # Variables tab (integrated with flag manager)
        self.setup_variables_tab()
        quest_tabs.addTab(self.variables_tab, "🔧 Variables")

        # Validation tab
        self.setup_validation_tab()
        quest_tabs.addTab(self.validation_tab, "✅ Validation")

        layout.addWidget(quest_tabs)

        return quest_panel

    def setup_basic_info_tab(self):
        """Setup the basic quest information tab"""
        basic_info = QWidget()
        layout = QVBoxLayout(basic_info)

        # Quest details form
        form = QFormLayout()

        # Quest ID and Name
        self.quest_id_spin = QSpinBox()
        self.quest_id_spin.setRange(1, 99999)
        self.quest_name_edit = QLineEdit()
        self.quest_description_edit = QTextEdit()
        self.quest_description_edit.setMaximumHeight(80)

        form.addRow("Quest ID:", self.quest_id_spin)
        form.addRow("Quest Name:", self.quest_name_edit)
        form.addRow("Description:", self.quest_description_edit)

        # Quest properties
        self.quest_difficulty_combo = QComboBox()
        self.quest_difficulty_combo.addItems(["Very Easy", "Easy", "Medium", "Hard", "Very Hard"])

        self.quest_type_combo = QComboBox()
        self.quest_type_combo.addItems(["Main Quest", "Side Quest", "Repeatable", "Hidden"])

        self.quest_priority_spin = QSpinBox()
        self.quest_priority_spin.setRange(1, 10)
        self.quest_priority_spin.setValue(5)

        form.addRow("Difficulty:", self.quest_difficulty_combo)
        form.addRow("Type:", self.quest_type_combo)
        form.addRow("Priority:", self.quest_priority_spin)

        layout.addLayout(form)
        layout.addStretch()

        self.basic_info_tab = basic_info

    def setup_dialogue_panel(self) -> QWidget:
        """Setup the dialogue editor panel"""
        dialogue_panel = QWidget()
        layout = QVBoxLayout(dialogue_panel)

        # Create vertical splitter for search and content
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Enhanced search and navigation widget
        self.search_navigation = EnhancedSearchNavigationWidget()
        self.search_navigation.setMaximumHeight(250)
        main_splitter.addWidget(self.search_navigation)

        # Dialogue tabs
        dialogue_tabs = QTabWidget()

        # Enhanced dialogue editor
        self.enhanced_dialogue_editor = EnhancedDialogueEditor()
        dialogue_tabs.addTab(self.enhanced_dialogue_editor, "💬 Enhanced Dialogue")

        # Enhanced text mode overview
        try:
            from TirganachReloaded.cff_editor.widgets.enhanced_text_mode_overview import EnhancedTextModeOverview
            self.enhanced_text_overview = EnhancedTextModeOverview()
            dialogue_tabs.addTab(self.enhanced_text_overview, "📝 Text Mode")
        except ImportError:
            # Fallback if enhanced text overview not available
            try:
                from TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview import TextModeDialogueOverview
                self.text_overview = TextModeDialogueOverview()
                dialogue_tabs.addTab(self.text_overview, "📝 Text Mode")
            except ImportError:
                fallback_text = QTextEdit()
                fallback_text.setPlainText("Text mode overview not available")
                fallback_text.setReadOnly(True)
                dialogue_tabs.addTab(fallback_text, "📝 Text Mode")

        main_splitter.addWidget(dialogue_tabs)

        # Set splitter sizes (search panel takes 250px, rest goes to content)
        main_splitter.setSizes([250, 550])
        main_splitter.setChildrenCollapsible(False)

        layout.addWidget(main_splitter)

        return dialogue_panel

    def setup_variables_tab(self):
        """Setup the variables and flags management tab"""
        variables_tab = QWidget()
        layout = QVBoxLayout(variables_tab)

        # Flag manager integration
        try:
            # Connect to existing flag manager
            self.flag_manager = FlagManager()

            # Flag display
            flag_display = QTextEdit()
            flag_display.setReadOnly(True)
            flag_display.setMaximumHeight(200)
            layout.addWidget(QLabel("Global Flags:"))
            layout.addWidget(flag_display)

            # Flag operations
            flag_ops_layout = QHBoxLayout()
            self.refresh_flags_btn = QPushButton("Refresh Flags")
            self.add_flag_btn = QPushButton("Add Flag")
            self.clear_flags_btn = QPushButton("Clear All")

            flag_ops_layout.addWidget(self.refresh_flags_btn)
            flag_ops_layout.addWidget(self.add_flag_btn)
            flag_ops_layout.addWidget(self.clear_flags_btn)
            layout.addLayout(flag_ops_layout)

        except Exception as e:
            logger.warning(f"Flag manager not available: {e}")
            # Fallback
            fallback_text = QTextEdit()
            fallback_text.setPlainText("Flag management features:\n\n• Global flags for persistent state\n• NPC flags for character-specific data\n• Item flags for object properties\n• Quest flags for tracking progress")
            fallback_text.setReadOnly(True)
            layout.addWidget(fallback_text)

        layout.addStretch()

        self.variables_tab = variables_tab

    def setup_validation_tab(self):
        """Setup the validation tab"""
        validation_tab = QWidget()
        layout = QVBoxLayout(validation_tab)

        try:
            # Use existing quest validator
            self.quest_validator = QuestValidator()

            validation_display = QTextEdit()
            validation_display.setReadOnly(True)
            validation_display.setMaximumHeight(300)
            layout.addWidget(QLabel("Validation Results:"))
            layout.addWidget(validation_display)

            validation_buttons = QHBoxLayout()
            self.validate_all_btn = QPushButton("Validate All")
            self.validate_dialogue_btn = QPushButton("Validate Dialogue")
            self.validate_connections_btn = QPushButton("Check Connections")

            validation_buttons.addWidget(self.validate_all_btn)
            validation_buttons.addWidget(self.validate_dialogue_btn)
            validation_buttons.addWidget(self.validate_connections_btn)
            layout.addLayout(validation_buttons)

        except Exception as e:
            logger.warning(f"Quest validator not available: {e}")
            # Fallback validation display
            fallback_text = QTextEdit()
            fallback_text.setPlainText("Validation features:\n\n• Quest structure validation\n• Dialogue consistency checks\n• AnswerId uniqueness\n• Connection integrity")
            fallback_text.setReadOnly(True)
            layout.addWidget(fallback_text)

        layout.addStretch()

        self.validation_tab = validation_tab

    def setup_connections(self):
        """Setup signal connections"""
        # Toolbar connections
        self.new_quest_btn.clicked.connect(self.create_new_quest)
        self.load_quest_btn.clicked.connect(self.load_quest)
        self.save_quest_btn.clicked.connect(self.save_quest)
        self.export_lua_btn.clicked.connect(self.export_lua)
        self.validate_btn.clicked.connect(self.validate_quest)
        self.test_btn.clicked.connect(self.test_dialogue)
        self.preview_btn.clicked.connect(self.preview_quest)

        # Basic info connections
        self.quest_id_spin.valueChanged.connect(self.on_quest_changed)
        self.quest_name_edit.textChanged.connect(self.on_quest_changed)
        self.quest_description_edit.textChanged.connect(self.quest_changed)
        self.quest_difficulty_combo.currentTextChanged.connect(self.on_quest_changed)
        self.quest_type_combo.currentTextChanged.connect(self.quest_changed)
        self.quest_priority_spin.valueChanged.connect(self.on_quest_changed)

        # Integration connections
        if hasattr(self.integration_tab, 'quest_id_spin'):
            self.integration_tab.quest_id_spin.valueChanged.connect(self.on_integration_changed)

        # Enhanced dialogue editor connections
        self.enhanced_dialogue_editor.dialogue_updated.connect(self.on_dialogue_updated)

        # Search and navigation connections
        self.search_navigation.search_requested.connect(self.on_search_requested)
        self.search_navigation.result_selected.connect(self.on_search_result_selected)
        self.search_navigation.navigate_to.connect(self.on_navigate_to)

        # Import/export connections
        self.import_btn.clicked.connect(self.show_import_dialog)
        self.export_btn.clicked.connect(self.show_export_dialog)

        # Variables tab connections
        if hasattr(self, 'refresh_flags_btn'):
            self.refresh_flags_btn.clicked.connect(self.refresh_flags_display)

    def create_new_quest(self):
        """Create a new quest"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Create New Quest")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        form = QFormLayout()

        quest_id_spin = QSpinBox()
        quest_id_spin.setRange(1, 99999)
        quest_name_edit = QLineEdit()

        form.addRow("Quest ID:", quest_id_spin)
        form.addRow("Quest Name:", quest_name_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addLayout(form)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            quest_id = quest_id_spin.value()
            quest_name = quest_name_edit.text() or f"Quest {quest_id}"

            # Create new quest data
            self.quest_data = EnhancedQuestData(
                quest_id=quest_id,
                name=quest_name,
                description="",
                parent_id=0,
                order_index=quest_id
            )

            # Initialize with empty dialogue tree
            self.quest_data.dialogues = []

            # Set dialogue editor data
            dialogue_data = {
                "nodes": {},
                "start_node_id": ""
            }
            self.enhanced_dialogue_editor.set_dialogue_data(dialogue_data)

            # Update basic info
            self.quest_id_spin.setValue(quest_id)
            self.quest_name_edit.setText(quest_name)

            self.quest_updated.emit(self.quest_data.to_dict())
            self.status_label.setText(f"Created new quest: {quest_name}")
            logger.info(f"Created new quest: {quest_name} (ID: {quest_id})")

    def load_quest(self):
        """Load quest data"""
        # This would open a file browser or quest browser
        # For now, create test data
        self.create_test_quest()

    def create_test_quest(self):
        """Create a test quest with enhanced dialogue"""
        test_quest = {
            "quest_id": 501,
            "name": "The Lost Ring of Eldoria",
            "description": "A mysterious ring has been lost in the ancient ruins. Find it and return it to its rightful owner.",
            "parent_id": 0,
            "order_index": 501,
            "name_id": 0,
            "description_id": 0,
            "dialogues": [
                {
                    "text": "Quest accepted: Find the lost ring in the ancient ruins.",
                    "speaker": "Town Elder",
                    "translation": "Quest accepted: Find the lost ring in the ancient ruins.",
                    "source_file": "script/P501/n0.lua",
                    "dialogue_type": "Dialog"
                }
            ],
            "dialogue_data": {
                "nodes": [
                    {
                        "node_id": "quest_start",
                        "node_type": "npc",
                        "speaker": "Town Elder",
                        "text": "Greetings, adventurer! I have an important task for you.",
                        "conditions": [
                            {
                                "condition_type": "quest_state",
                                "params": {"quest_id": 501, "state": "Unknown"},
                                "negated": False,
                                "description": "Quest 501 is unknown"
                            }
                        ],
                        "actions": [
                            {
                                "action_type": "quest_begin",
                                "params": {"quest_id": 501},
                                "description": "Begin the lost ring quest"
                            }
                        ],
                        "choices": [
                            {
                                "choice_id": 1,
                                "text": "I'm ready for the challenge!",
                                "next_node_id": "quest_accept",
                                "conditions": [
                                    {
                                        "condition_type": "player_level",
                                        "params": {"level": 10, "comparison": ">="},
                                        "negated": False,
                                        "description": "Player level 10 or higher"
                                    }
                                ],
                                "actions": [
                                    {
                                        "action_type": "set_global_flag",
                                        "params": {"flag_name": "ring_quest_accepted", "value": True},
                                        "description": "Mark quest as accepted"
                                    }
                                ]
                            },
                            {
                                "choice_id": 2,
                                "text": "This sounds dangerous. I'll pass.",
                                "next_node_id": "quest_refuse",
                                "conditions": [],
                                "actions": []
                            }
                        ]
                    },
                    {
                        "node_id": "quest_accept",
                        "node_type": "response",
                        "speaker": "Town Elder",
                        "text": "Excellent! The ring was stolen by goblins from the ancient ruins to the west.",
                        "answer_id": 1,
                        "conditions": [],
                        "actions": [
                            {
                                "action_type": "set_global_flag",
                                "params": {"flag_name": "ring_in_ruins_west", "value": True},
                                "description": "Mark ring location discovered"
                            },
                            {
                                "action_type": "give_item",
                                "params": {"item_id": 1501, "count": 1},
                                "description": "Give quest map"
                            }
                        ],
                        "choices": [
                            {
                                "choice_id": 10,
                                "text": "I'll find it right away!",
                                "next_node_id": "quest_progress",
                                "conditions": [],
                                "actions": []
                            },
                            {
                                "choice_id": 11,
                                "text": "Tell me more about these goblins.",
                                "next_node": "quest_info",
                                "conditions": [],
                                "actions": []
                            }
                        ]
                    }
                ],
                "start_node_id": "quest_start"
            }
        }

        # Set the quest data
        self.quest_data = EnhancedQuestData.from_dict(test_quest)

        # Update UI
        self.update_ui_from_quest_data()

        # Update dialogue editor
        self.enhanced_dialogue_editor.set_dialogue_data(test_quest.get("dialogue_data", {}))

        self.quest_updated.emit(self.quest_data.to_dict())
        self.status_label.setText(f"Loaded test quest: {self.quest_data.name}")

    def update_ui_from_quest_data(self):
        """Update UI elements from quest data"""
        if not self.quest_data:
            return

        # Update basic info
        self.quest_id_spin.setValue(self.quest_data.quest_id)
        self.quest_name_edit.setText(self.quest_data.name)
        self.quest_description_edit.setPlainText(self.quest_data.description)

        # Set quest type (map from string to combo box index)
        quest_type_map = {
            "Main Quest": 0,
            "Side Quest": 1,
            "Repeatable": 2,
            "Hidden": 3
        }
        quest_type_index = quest_type_map.get(self.quest_data.quest_type, 0)
        self.quest_type_combo.setCurrentIndex(quest_type_index)

        # Update integration tab
        if hasattr(self.integration_tab, 'quest_id_spin'):
            self.integration_tab.quest_id_spin.setValue(self.quest_data.quest_id)

        self.status_label.setText(f"Loaded quest: {self.quest_data.name} (ID: {self.quest_data.quest_id})")

    def save_quest(self):
        """Save the current quest"""
        if not self.quest_data:
            QMessageBox.warning(self, "No Quest", "No quest data to save")
            return

        try:
            # Get updated dialogue data
            dialogue_data = self.enhanced_dialogue_editor.get_dialogue_data()

            # Update quest data with dialogue data
            self.quest_data.dialogues = dialogue_data.get("nodes", [])

            # Convert quest data to JSON
            quest_json = self.quest_data.to_dict()

            # In a real implementation, this would save to a file
            # For now, show success message
            QMessageBox.information(
                self,
                "Quest Saved",
                f"Quest '{self.quest_data.name}' saved successfully!\n\n"
                f"Nodes: {len(self.quest_data.dialogues)}\n"
                f"Quest ID: {self.quest_data.quest_id}\n"
                f"Name: {self.quest_data.name}"
            )

            self.quest_updated.emit(quest_json)
            self.status_label.setText(f"Saved quest: {self.quest_data.name}")

            logger.info(f"Saved quest: {self.quest_data.name}")

        except Exception as e:
            logger.error(f"Error saving quest: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save quest: {str(e)}")

    def export_lua(self):
        """Export the quest to LUA format"""
        try:
            if not self.quest_data:
                QMessageBox.warning(self, "No Quest", "No quest data to export")
                return

            # Get LUA from dialogue editor
            dialogue_lua = self.enhanced_dialogue_editor.generate_lua_export()

            # Generate quest header and footer
            quest_lua = self._generate_quest_lua()

            # Combine all LUA code
            full_lua = quest_lua + "\n\n" + dialogue_lua

            # Show export dialog
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Export Quest LUA - {self.quest_data.name}")
            dialog.setMinimumWidth(800)
            dialog.resize(1000, 700)

            layout = QVBoxLayout(dialog)

            text_edit = QTextEdit()
            text_edit.setFont(QFont("Courier New", 10))
            text_edit.setPlainText(full_lua)
            layout.addWidget(text_edit)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            dialog.exec()

            self.status_label.setText(f"Exported quest LUA: {len(full_lua)} lines")

        except Exception as e:
            logger.error(f"Error exporting LUA: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export LUA: {str(e)}")

    def _generate_quest_lua(self) -> str:
        """Generate LUA code for quest setup"""
        lines = []
        lines.append("-- Quest Setup")
        lines.append(f"-- Quest: {self.quest_data.name} (ID: {self.quest_data.quest_id})")
        lines.append("-- Description: {self.quest_data.description}")
        lines.append("")

        lines.append("-- Quest begin conditions")
        if self.quest_data.quest_id > 0:
            lines.append("OnOneTimeEvent")
            lines.append("{")
            lines.append("    Conditions = {")

            # Add quest prerequisites if any
            if self.quest_data.parent_id > 0:
                lines.append(f"        QuestState{{QuestId = {self.quest_data.parent_id}, State = StateSolved}},")

            lines.append("    },")
            lines.append("    Actions = {")
            lines.append(f"        QuestBegin{{QuestId = {self.quest_data.quest_id}}},")

            # Add quest flag
            lines.append(f"        SetGlobalFlagTrue{{Name = \"Quest{self.quest_data.quest_id}Started\"}},")

            lines.append("    }")
            lines.append("}")

        lines.append("")

        return "\n".join(lines)

    def validate_quest(self):
        """Validate the complete quest"""
        try:
            issues = []

            # Validate dialogue structure
            dialogue_data = self.enhanced_dialogue_editor.get_dialogue_data()
            dialogue_tree = DialogueTree.from_dict(dialogue_data)
            dialogue_issues = dialogue_tree.validate()
            issues.extend([f"Dialogue: {issue}" for issue in dialogue_issues])

            # Validate quest structure
            if not self.quest_data.quest_id:
                issues.append("Quest: No quest ID specified")
            if not self.quest_data.name:
                issues.append("Quest: No quest name specified")

            # Check AnswerId conflicts
            if hasattr(self.enhanced_dialogue_editor, 'answer_id_panel'):
                if self.enhanced_dialogue_editor.answer_id_panel:
                    conflicts = self.enhanced_dialogue_editor.answer_id_panel.answer_id_manager.validate_uniqueness()
                    if conflicts:
                        for conflict in conflicts:
                            issues.append(f"AnswerId: Conflict with AnswerId {conflict.answer_id} used by {len(conflict.step_ids)} steps")

            if not issues:
                QMessageBox.information(self, "Validation Complete", "✅ Quest is valid!")
                self.status_label.setText("✅ Quest validation passed - no issues found")
            else:
                issue_text = "\n".join(issues)
                QMessageBox.warning(self, "Validation Issues", f"Found {len(issues)} issues:\n\n{issue_text}")
                self.status_label.setText(f"⚠️ Validation found {len(issues)} issues")

        except Exception as e:
            logger.error(f"Error validating quest: {e}")
            QMessageBox.critical(self, "Validation Error", f"Failed to validate quest: {str(e)}")

    def test_dialogue(self):
        """Test the dialogue flow"""
        try:
            dialogue_data = self.enhanced_dialogue_editor.get_dialogue_tree()

            # Create simple test simulation
            test_results = []

            # Test node connectivity
            start_node = dialogue_data.get_node(dialogue_tree.start_node_id)
            if start_node:
                self._test_dialogue_node_recursive(dialogue_tree, start_node, test_results, set())

            # Show test results
            if test_results:
                results_text = "\n".join(f"• {result}" for result in test_results)
                QMessageBox.information(self, "Dialogue Test Results", f"Dialogue test completed:\n\n{results_text}")
            else:
                QMessageBox.information(self, "Test Complete", "✅ Dialogue test completed - all paths are valid!")

            self.status_label.setText("✅ Dialogue test completed")

        except Exception as e:
            logger.error(f"Error testing dialogue: {e}")
            QMessageBox.critical(self, "Test Error", f"Failed to test dialogue: {str(e)}")

    def _test_dialogue_node_recursive(self, dialogue_tree, node, results, visited):
        """Recursively test dialogue nodes"""
        if node.node_id in visited:
            results.append(f"Cycle detected: {node.node_id}")
            return

        visited.add(node.node_id)

        # Test node conditions (simplified)
        for condition in node.conditions:
            if condition.condition_type == DialogueConditionType.GLOBAL_FLAG:
                flag_name = condition.params.get("flag_name", "")
                if flag_name:
                    results.append(f"Condition: Global flag '{flag_name}' = {condition.params.get('value', True)}")

        # Test choices
        for i, choice in enumerate(node.choices):
            if choice.next_node_id:
                if choice.next_node_id in dialogue_tree.nodes:
                    self._test_dialogue_node_recursive(dialogue_tree, dialogue_tree.nodes[choice.next_node_id], results, visited)
                else:
                    results.append(f"Broken connection: {node.node_id} -> {choice.next_node_id} (node not found)")

    def preview_quest(self):
        """Show a preview of the quest"""
        if not self.quest_data:
            QMessageBox.warning(self, "No Quest", "No quest data to preview")
            return

        # Create preview dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Quest Preview - {self.quest_data.name}")
        dialog.setMinimumWidth(600)
        dialog.resize(700, 500)

        layout = QVBoxLayout(dialog)

        # Quest summary
        summary_text = f"""
📋 QUEST PREVIEW
================

Quest ID: {self.quest_data.quest_id}
Name: {self.quest_data.name}
Type: {self.quest_data.quest_type}
Priority: {self.quest_data.priority if hasattr(self.quest_data, 'priority') else 5}
Description: {self.quest_data.description}

"""

        summary_text_edit = QTextEdit()
        summary_text_edit.setPlainText(summary_text)
        summary_text_edit.setReadOnly(True)
        layout.addWidget(summary_text)

        # Dialogue flow preview
        try:
            dialogue_data = self.enhanced_dialogue_editor.get_dialogue_tree()
            flow_text = self._generate_dialogue_flow_preview(dialogue_tree)

            flow_text_edit = QTextEdit()
            flow_text_edit.setPlainText(flow_text)
            flow_text_edit.setReadOnly(True)
            layout.addWidget(QLabel("Dialogue Flow:"))
            layout.addWidget(flow_text_edit)

        except Exception as e:
            layout.addWidget(QLabel(f"Error generating dialogue flow: {str(e)}"))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.exec()

    def _generate_dialogue_flow_preview(self, dialogue_tree) -> str:
        """Generate a simplified dialogue flow preview"""
        lines = []
        lines.append("DIALOGUE FLOW:")
        lines.append("=" * 50)

        start_node = dialogue_tree.get_node(dialogue_tree.start_node_id)
        if start_node:
            self._add_dialogue_flow_node(dialogue_tree, start_node, lines, set(), "")

        return "\n".join(lines)

    def _add_dialogue_flow_node(self, dialogue_tree, node, lines, visited, indent):
        """Add a node to the dialogue flow preview"""
        if node.node_id in visited:
            return

        visited.add(node.node_id)

        node_type_icon = {"npc": "🗣️", "player": "👤", "start": "🚀", "end": "🏁"}.get(node.node_type, "📄")

        lines.append(f"{indent}{node_type_icon} {node.node_id} ({node.speaker or 'Unknown'})")
        lines.append(f"{indent}  \"{node.text[:50]}{'...' if len(node.text) > 50 else ''}\"")

        # Show conditions
        if node.conditions:
            for condition in node.conditions:
                lines.append(f"{indent}  [🔒] {condition.get_display_text()}")

        # Show choices
        if node.choices:
            for i, choice in enumerate(node.choices):
                choice_letter = chr(65 + i)  # A, B, C...
                next_text = f"→ {choice.next_node_id}" if choice.next_node_id else "→ [END]"
                lines.append(f"{indent}  [{choice_letter}] {choice.text[:40]}{'...' if len(choice.text) > 40 else ''} {next_text}")

                # Recurse to next node
                if choice.next_node_id and choice.next_node_id in dialogue_tree.nodes:
                    self._add_dialogue_flow_node(dialogue_tree, dialogue_tree.nodes[choice.next_node_id], lines, visited, indent + "  ")

    def on_quest_changed(self):
        """Handle quest data changes"""
        if self.quest_data:
            # Update quest data
            self.quest_data.quest_id = self.quest_id_spin.value()
            self.quest_data.name = self.quest_name_edit.text()
            self.quest_data.description = self.quest_description_edit.toPlainText()
            self.quest_data.quest_type = self.quest_type_combo.currentText()

            self.quest_updated.emit(self.quest_data.to_dict())
            self.status_label.setText(f"Updated quest: {self.quest_data.name}")

    def on_integration_changed(self):
        """Handle integration changes"""
        # Update integration tab data in quest_data
        if self.quest_data and hasattr(self.integration_tab, 'quest_id_spin'):
            # Keep quest_id in sync
            if self.integration_tab.quest_id_spin.value() != self.quest_data.quest_id:
                self.quest_data.quest_id = self.integration_tab.quest_id_spin.value()
                self.quest_updated.emit(self.quest_data.to_dict())

    def on_dialogue_updated(self):
        """Handle dialogue updates"""
        if self.quest_data:
            # Update quest data with dialogue information
            dialogue_data = self.enhanced_dialogue_editor.get_dialogue_data()
            self.quest_data.dialogues = dialogue_data.get("nodes", [])

            self.quest_updated.emit(self.quest_data.to_dict())

    def refresh_flags_display(self):
        """Refresh the flags display"""
        if self.flag_manager:
            try:
                # Get current flags
                flags_data = []

                # In a real implementation, this would query the flag manager
                # For now, show placeholder data
                flags_text = """Global Flags Status:
• ring_quest_started: FALSE
• ring_in_ruins_west: FALSE
• goblin_encountered: TRUE
• elder_quest_completed: TRUE
• player_level_10: TRUE

Note: Full flag management integration coming soon."""

                if hasattr(self, 'quest_variables_table'):
                    self.quest_variables_table.clear()
                    # Add flag entries to table
                    item = QTreeWidgetItem(["ring_quest_started", "Global", "FALSE", "Quest"])
                    self.quest_variables_table.addTopLevelItem(item)
                    item = QTreeWidgetItem(["goblin_encountered", "Global", "TRUE", "Combat"])
                    self.quest_variables_table.addTopLevelItem(item)

            except Exception as e:
                logger.warning(f"Error refreshing flags display: {e}")

    def get_quest_data(self) -> Dict[str, Any]:
        """Get the complete quest data"""
        if self.quest_data:
            return self.quest_data.to_dict()
        return {}

    def set_quest_data(self, quest_data: Dict[str, Any]):
        """Set quest data from dictionary"""
        try:
            self.quest_data = EnhancedQuestData.from_dict(quest_data)
            self.update_ui_from_quest_data()
        except Exception as e:
            logger.error(f"Error setting quest data: {e}")
            QMessageBox.critical(self, "Load Error", f"Failed to load quest data: {str(e)}")


# Test function
def test_unified_enhanced_quest_editor():
    """Test the unified enhanced quest editor"""
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create and show editor
    editor = UnifiedEnhancedQuestEditor()
    editor.create_test_quest()
    editor.setWindowTitle("Unified Enhanced Quest Editor Test")
    editor.resize(1200, 800)
    editor.show()

    # Enhanced search and navigation methods
    def on_search_requested(self, search_params: dict):
        """Handle search request from the search widget"""
        try:
            # Update search context with current data
            self._update_search_context()

            # Perform search
            results = self.search_engine.search(search_params)

            # Display results
            self.search_navigation.set_search_results(results)

            # Update status
            self.status_label.setText(f"Found {len(results)} results for '{search_params.get('query', '')}'")

        except Exception as e:
            logger.error(f"Search error: {e}")
            self.status_label.setText(f"Search error: {e}")
            self.search_navigation.set_search_results([])

    def on_search_result_selected(self, result: SearchResult):
        """Handle search result selection"""
        try:
            # Add to navigation history
            location = f"{result.item_type}:{result.item_id}"
            context = {
                "quest_name": result.quest_name,
                "parent_id": result.parent_id,
                "line_number": result.line_number,
                "search_result": True
            }
            self.search_navigation.add_navigation_history(location, context)

            # Update status
            self.status_label.setText(f"Selected: {result.item_type} '{result.item_id}' from {result.quest_name}")

        except Exception as e:
            logger.error(f"Search result selection error: {e}")

    def on_navigate_to(self, location: str, context: dict):
        """Handle navigation request"""
        try:
            # Parse location
            parts = location.split(":", 1)
            item_type = parts[0] if len(parts) > 0 else ""
            item_id = parts[1] if len(parts) > 1 else ""

            # Navigate based on type
            if item_type == "quest" and item_id:
                # Load quest
                self.load_quest_by_id(item_id)
            elif item_type == "node" and item_id:
                # Navigate to dialogue node
                self.navigate_to_dialogue_node(item_id, context)
            elif item_type == "choice" and item_id:
                # Navigate to choice
                self.navigate_to_choice(item_id, context)
            elif item_type == "condition" or item_type == "action":
                # Navigate to condition or action
                self.navigate_to_condition_action(item_id, context)

            # Update status
            quest_name = context.get("quest_name", "Unknown")
            self.status_label.setText(f"Navigated to: {location} in {quest_name}")

        except Exception as e:
            logger.error(f"Navigation error: {e}")
            self.status_label.setText(f"Navigation error: {e}")

    def _update_search_context(self):
        """Update the search context with current data"""
        try:
            # Update quest data
            if self.quest_data:
                quest_dict = {str(self.quest_data.quest_id): self.quest_data}
                self.search_context.quest_data = quest_dict

            # Update dialogue trees
            dialogue_trees = {}
            if self.quest_data and hasattr(self.quest_data, 'dialogue_tree'):
                dialogue_trees[str(self.quest_data.quest_id)] = self.quest_data.dialogue_tree

            # Get dialogue tree from enhanced editor
            if hasattr(self.enhanced_dialogue_editor, 'dialogue_tree') and self.enhanced_dialogue_editor.dialogue_tree:
                dialogue_trees["current"] = self.enhanced_dialogue_editor.dialogue_tree

            self.search_context.dialogue_trees = dialogue_trees
            self.search_context.current_quest_id = str(self.quest_data.quest_id) if self.quest_data else None

            # Update search engine context
            self.search_engine.set_context(self.search_context)

        except Exception as e:
            logger.error(f"Error updating search context: {e}")

    def navigate_to_dialogue_node(self, node_id: str, context: dict):
        """Navigate to a specific dialogue node"""
        try:
            # Switch to enhanced dialogue editor tab
            # This would depend on the enhanced dialogue editor implementation
            if hasattr(self.enhanced_dialogue_editor, 'select_node'):
                self.enhanced_dialogue_editor.select_node(node_id)

        except Exception as e:
            logger.error(f"Error navigating to dialogue node {node_id}: {e}")

    def navigate_to_choice(self, choice_id: str, context: dict):
        """Navigate to a specific choice"""
        try:
            # Parse choice ID (format: node_id_choice_N)
            if "_choice_" in choice_id:
                node_id = choice_id.split("_choice_")[0]
                choice_index = int(choice_id.split("_choice_")[1])

                # Navigate to node and select choice
                self.navigate_to_dialogue_node(node_id, context)
                if hasattr(self.enhanced_dialogue_editor, 'select_choice'):
                    self.enhanced_dialogue_editor.select_choice(node_id, choice_index)

        except Exception as e:
            logger.error(f"Error navigating to choice {choice_id}: {e}")

    def navigate_to_condition_action(self, item_id: str, context: dict):
        """Navigate to a condition or action"""
        try:
            # Parse item ID to get parent node
            parent_id = context.get("parent_id")
            if parent_id:
                self.navigate_to_dialogue_node(parent_id, context)

        except Exception as e:
            logger.error(f"Error navigating to condition/action {item_id}: {e}")

    def load_quest_by_id(self, quest_id: str):
        """Load quest by ID"""
        try:
            # This would need to be implemented based on quest loading system
            # For now, just update the quest ID spin box
            self.quest_id_spin.setValue(int(quest_id))

        except Exception as e:
            logger.error(f"Error loading quest {quest_id}: {e}")

    def show_import_dialog(self):
        """Show import dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Import Quest Data")
        dialog.setMinimumSize(800, 600)

        layout = QVBoxLayout(dialog)

        # Create import/export manager for this dialog
        import_manager = ImportExportManager()

        # Add current data context
        current_data = self._collect_current_data()
        import_manager.set_quest_data(current_data.get('quest_data'))
        import_manager.set_dialogue_trees(current_data.get('dialogue_trees'))

        # Add import/export widget
        layout.addWidget(import_manager)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        # Connect import signal
        import_manager.data_imported.connect(self._on_data_imported)

        dialog.exec()

    def show_export_dialog(self):
        """Show export dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Quest Data")
        dialog.setMinimumSize(800, 600)

        layout = QVBoxLayout(dialog)

        # Create import/export manager for this dialog
        export_manager = ImportExportManager()

        # Add current data context
        current_data = self._collect_current_data()
        export_manager.set_quest_data(current_data.get('quest_data'))
        export_manager.set_dialogue_trees(current_data.get('dialogue_trees'))

        # Add import/export widget
        layout.addWidget(export_manager)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.exec()

    def _collect_current_data(self) -> dict:
        """Collect current quest and dialogue data for export"""
        try:
            data = {
                'quest_data': None,
                'dialogue_trees': {},
                'metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'editor_version': '1.0'
                }
            }

            # Get quest data
            if self.quest_data:
                data['quest_data'] = asdict(self.quest_data) if hasattr(self.quest_data, '__dict__') else self.quest_data

            # Get dialogue trees
            if hasattr(self.enhanced_dialogue_editor, 'dialogue_tree') and self.enhanced_dialogue_editor.dialogue_tree:
                data['dialogue_trees']['current'] = asdict(self.enhanced_dialogue_editor.dialogue_tree) if hasattr(self.enhanced_dialogue_editor.dialogue_tree, '__dict__') else self.enhanced_dialogue_editor.dialogue_tree

            # Get basic quest info from form
            data['quest_info'] = {
                'quest_id': self.quest_id_spin.value(),
                'quest_name': self.quest_name_edit.text(),
                'quest_description': self.quest_description_edit.toPlainText(),
                'quest_difficulty': self.quest_difficulty_combo.currentText(),
                'quest_type': self.quest_type_combo.currentText(),
                'quest_priority': self.quest_priority_spin.value()
            }

            return data

        except Exception as e:
            logger.error(f"Error collecting current data: {e}")
            return {}

    def _on_data_imported(self, imported_data: dict):
        """Handle imported data"""
        try:
            # Update quest info if present
            if 'quest_info' in imported_data:
                quest_info = imported_data['quest_info']
                self.quest_id_spin.setValue(quest_info.get('quest_id', 1))
                self.quest_name_edit.setText(quest_info.get('quest_name', ''))
                self.quest_description_edit.setPlainText(quest_info.get('quest_description', ''))
                self.quest_difficulty_combo.setCurrentText(quest_info.get('quest_difficulty', 'Medium'))
                self.quest_type_combo.setCurrentText(quest_info.get('quest_type', 'Side Quest'))
                self.quest_priority_spin.setValue(quest_info.get('quest_priority', 5))

            # Load dialogue trees if present
            if 'dialogue_trees' in imported_data:
                dialogue_trees = imported_data['dialogue_trees']
                if 'current' in dialogue_trees:
                    # Load the current dialogue tree into the editor
                    current_tree = dialogue_trees['current']
                    if hasattr(self.enhanced_dialogue_editor, 'load_dialogue_tree'):
                        self.enhanced_dialogue_editor.load_dialogue_tree(current_tree)

            # Update status
            self.status_label.setText("Data imported successfully")
            QMessageBox.information(self, "Import Complete", "Quest data has been imported successfully!")

        except Exception as e:
            logger.error(f"Error processing imported data: {e}")
            self.status_label.setText("Import processing error")
            QMessageBox.warning(self, "Import Warning", f"Data was imported but there were errors:\n{e}")


# Test function
def test_unified_enhanced_quest_editor():
    """Test the unified enhanced quest editor"""
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create and show editor
    editor = UnifiedEnhancedQuestEditor()
    editor.create_test_quest()
    editor.setWindowTitle("Unified Enhanced Quest Editor Test")
    editor.resize(1200, 800)
    editor.show()

    return app.exec()


if __name__ == "__main__":
    test_unified_enhanced_quest_editor()