#!/usr/bin/env python3
"""
Enhanced Dialogue Editor

An advanced dialogue editor with conditions, actions, and consequences.
Integrates with the existing text mode dialogue overview and AnswerId management.
"""

import sys
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QPushButton,
    QLabel, QLineEdit, QComboBox, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QMessageBox, QCheckBox, QSpinBox,
    QScrollArea, QFrame, QToolBar, QMenu, QApplication,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QIcon, QKeySequence

try:
    from TirganachReloaded.cff_editor.models.enhanced_dialogue_models import (
        DialogueTree, DialogueNode, DialogueChoice,
        DialogueCondition, DialogueAction, DialogueConditionType, DialogueActionType
    )
    from TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview import TextModeDialogueOverview
    from TirganachReloaded.cff_editor.widgets.answer_id_management_panel import AnswerIdManagementPanel
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

    # Fallback imports if modules not available
    class DialogueTree: pass
    class DialogueNode: pass
    class DialogueChoice: pass
    class DialogueCondition: pass
    class DialogueAction: pass


class ConditionBuilderDialog(QDialog):
    """Dialog for building and editing dialogue conditions"""

    def __init__(self, parent=None, condition: Optional[DialogueCondition] = None):
        super().__init__(parent)
        self.condition = condition or DialogueCondition(DialogueConditionType.GLOBAL_FLAG)
        self.setup_ui()
        self.setWindowTitle("Edit Condition")
        self.setMinimumWidth(500)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Form layout
        form = QFormLayout()

        # Condition type
        self.condition_combo = QComboBox()
        condition_types = [
            ("Global Flag", DialogueConditionType.GLOBAL_FLAG),
            ("Quest Complete", DialogueConditionType.QUEST_COMPLETE),
            ("Player Has Item", DialogueConditionType.PLAYER_HAS_ITEM),
            ("Player Level", DialogueConditionType.PLAYER_LEVEL),
            ("NPC Dead", DialogueConditionType.NPC_DEAD),
            ("Time of Day", DialogueConditionType.TIME_DAY),
            ("Custom Lua", DialogueConditionType.CUSTOM_LUA)
        ]

        for display_text, cond_type in condition_types:
            self.condition_combo.addItem(display_text, cond_type)

        self.condition_combo.setCurrentText(self.get_condition_display_text())
        self.condition_combo.currentTextChanged.connect(self.on_condition_type_changed)
        form.addRow("Condition Type:", self.condition_combo)

        # Parameters (dynamic based on condition type)
        self.params_frame = QFrame()
        self.params_layout = QVBoxLayout(self.params_frame)
        self.setup_params_for_condition()
        form.addRow("Parameters:", self.params_frame)

        # Description
        self.description_edit = QLineEdit()
        self.description_edit.setText(self.condition.description)
        form.addRow("Description:", self.description_edit)

        # Negated checkbox
        self.negated_checkbox = QCheckBox("Negated (NOT)")
        self.negated_checkbox.setChecked(self.condition.negated)
        form.addRow(self.negated_checkbox)

        layout.addLayout(form)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Set initial values
        self.set_condition_values()

    def get_condition_display_text(self) -> str:
        """Get display text for current condition type"""
        condition_type = self.condition.condition_type
        type_map = {
            DialogueConditionType.GLOBAL_FLAG: "Global Flag",
            DialogueConditionType.QUEST_COMPLETE: "Quest Complete",
            DialogueConditionType.PLAYER_HAS_ITEM: "Player Has Item",
            DialogueConditionType.PLAYER_LEVEL: "Player Level",
            DialogueConditionType.NPC_DEAD: "NPC Dead",
            DialogueConditionType.TIME_DAY: "Time of Day",
            DialogueConditionType.CUSTOM_LUA: "Custom Lua"
        }
        return type_map.get(condition_type, "Unknown")

    def setup_params_for_condition(self):
        """Setup parameter widgets based on current condition type"""
        # Clear existing widgets
        for i in reversed(range(self.params_layout.count())):
            child = self.params_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        condition_type = self.condition.condition_type

        if condition_type == DialogueConditionType.GLOBAL_FLAG:
            self.flag_name_edit = QLineEdit()
            self.flag_name_edit.setPlaceholderText("Flag name")
            self.flag_value_check = QCheckBox("Flag is True")
            self.flag_value_check.setChecked(True)
            self.params_layout.addWidget(QLabel("Flag Name:"))
            self.params_layout.addWidget(self.flag_name_edit)
            self.params_layout.addWidget(QLabel("Flag Value:"))
            self.params_layout.addWidget(self.flag_value_check)

        elif condition_type == DialogueConditionType.QUEST_COMPLETE:
            self.quest_id_spin = QSpinBox()
            self.quest_id_spin.setRange(0, 99999)
            self.params_layout.addWidget(QLabel("Quest ID:"))
            self.params_layout.addWidget(self.quest_id_spin)

        elif condition_type == DialogueConditionType.PLAYER_HAS_ITEM:
            self.item_id_spin = QSpinBox()
            self.item_id_spin.setRange(0, 99999)
            self.item_count_spin = QSpinBox()
            self.item_count_spin.setRange(1, 9999)
            self.item_count_spin.setValue(1)
            self.params_layout.addWidget(QLabel("Item ID:"))
            self.params_layout.addWidget(self.item_id_spin)
            self.params_layout.addWidget(QLabel("Item Count:"))
            self.params_layout.addWidget(self.item_count_spin)

        elif condition_type == DialogueConditionType.PLAYER_LEVEL:
            self.level_spin = QSpinBox()
            self.level_spin.setRange(1, 100)
            self.combo_comparison = QComboBox()
            self.combo_comparison.addItems(["=", ">", "<", ">=", "<="])
            self.params_layout.addWidget(QLabel("Player Level:"))
            self.params_layout.addWidget(self.level_spin)
            self.params_layout.addWidget(QLabel("Comparison:"))
            self.params_layout.addWidget(self.combo_comparison)

        elif condition_type == DialogueConditionType.NPC_DEAD:
            self.npc_id_spin = QSpinBox()
            self.npc_id_spin.setRange(0, 99999)
            self.params_layout.addWidget(QLabel("NPC ID:"))
            self.params_layout.addWidget(self.npc_id_spin)

        elif condition_type == DialogueConditionType.TIME_DAY:
            self.day_checkbox = QCheckBox("Is Daytime")
            self.day_checkbox.setChecked(True)
            self.params_layout.addWidget(self.day_checkbox)

        elif condition_type == DialogueConditionType.CUSTOM_LUA:
            self.lua_edit = QTextEdit()
            self.lua_edit.setMaximumHeight(100)
            self.lua_edit.setPlaceholderText("Enter custom LUA condition code...")
            self.params_layout.addWidget(QLabel("LUA Code:"))
            self.params_layout.addWidget(self.lua_edit)

    def set_condition_values(self):
        """Set parameter values from current condition"""
        condition_type = self.condition.condition_type
        params = self.condition.params

        if condition_type == DialogueConditionType.GLOBAL_FLAG:
            if hasattr(self, 'flag_name_edit'):
                self.flag_name_edit.setText(params.get("flag_name", ""))
            if hasattr(self, 'flag_value_check'):
                self.flag_value_check.setChecked(params.get("value", True))

        elif condition_type == DialogueConditionType.QUEST_COMPLETE:
            if hasattr(self, 'quest_id_spin'):
                self.quest_id_spin.setValue(params.get("quest_id", 0))

        elif condition_type == DialogueConditionType.PLAYER_HAS_ITEM:
            if hasattr(self, 'item_id_spin'):
                self.item_id_spin.setValue(params.get("item_id", 0))
            if hasattr(self, 'item_count_spin'):
                self.item_count_spin.setValue(params.get("count", 1))

        elif condition_type == DialogueConditionType.PLAYER_LEVEL:
            if hasattr(self, 'level_spin'):
                self.level_spin.setValue(params.get("level", 1))
            if hasattr(self, 'combo_comparison'):
                self.combo_comparison.setCurrentText(params.get("comparison", ">="))

        elif condition_type == DialogueConditionType.NPC_DEAD:
            if hasattr(self, 'npc_id_spin'):
                self.npc_id_spin.setValue(params.get("npc_id", 0))

        elif condition_type == DialogueConditionType.TIME_DAY:
            if hasattr(self, 'day_checkbox'):
                self.day_checkbox.setChecked(params.get("is_day", True))

        elif condition_type == DialogueConditionType.CUSTOM_LUA:
            if hasattr(self, 'lua_edit'):
                self.lua_edit.setPlainText(params.get("lua_code", ""))

    def on_condition_type_changed(self, text: str):
        """Handle condition type change"""
        self.setup_params_for_condition()

    def get_condition(self) -> DialogueCondition:
        """Get the constructed condition"""
        # Get selected condition type
        current_data = self.condition_combo.currentData()
        if current_data:
            self.condition.condition_type = current_data

        # Update parameters
        params = {}
        condition_type = self.condition.condition_type

        if condition_type == DialogueConditionType.GLOBAL_FLAG:
            if hasattr(self, 'flag_name_edit'):
                params["flag_name"] = self.flag_name_edit.text()
            if hasattr(self, 'flag_value_check'):
                params["value"] = self.flag_value_check.isChecked()

        elif condition_type == DialogueConditionType.QUEST_COMPLETE:
            if hasattr(self, 'quest_id_spin'):
                params["quest_id"] = self.quest_id_spin.value()

        elif condition_type == DialogueConditionType.PLAYER_HAS_ITEM:
            if hasattr(self, 'item_id_spin'):
                params["item_id"] = self.item_id_spin.value()
            if hasattr(self, 'item_count_spin'):
                params["count"] = self.item_count_spin.value()

        elif condition_type == DialogueConditionType.PLAYER_LEVEL:
            if hasattr(self, 'level_spin'):
                params["level"] = self.level_spin.value()
            if hasattr(self, 'combo_comparison'):
                params["comparison"] = self.combo_comparison.currentText()

        elif condition_type == DialogueConditionType.NPC_DEAD:
            if hasattr(self, 'npc_id_spin'):
                params["npc_id"] = self.npc_id_spin.value()

        elif condition_type == DialogueConditionType.TIME_DAY:
            if hasattr(self, 'day_checkbox'):
                params["is_day"] = self.day_checkbox.isChecked()

        elif condition_type == DialogueConditionType.CUSTOM_LUA:
            if hasattr(self, 'lua_edit'):
                params["lua_code"] = self.lua_edit.toPlainText()

        self.condition.params = params
        self.condition.description = self.description_edit.text()
        self.condition.negated = self.negated_checkbox.isChecked()

        return self.condition


class ActionBuilderDialog(QDialog):
    """Dialog for building and editing dialogue actions"""

    def __init__(self, parent=None, action: Optional[DialogueAction] = None):
        super().__init__(parent)
        self.action = action or DialogueAction(DialogueActionType.SET_GLOBAL_FLAG)
        self.setup_ui()
        self.setWindowTitle("Edit Action")
        self.setMinimumWidth(500)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Form layout
        form = QFormLayout()

        # Action type
        self.action_combo = QComboBox()
        action_types = [
            ("Set Global Flag", DialogueActionType.SET_GLOBAL_FLAG),
            ("Clear Global Flag", DialogueActionType.CLEAR_GLOBAL_FLAG),
            ("Begin Quest", DialogueActionType.QUEST_BEGIN),
            ("Complete Quest", DialogueActionType.QUEST_COMPLETE),
            ("Give Item", DialogueActionType.GIVE_ITEM),
            ("Take Item", DialogueActionType.TAKE_ITEM),
            ("Give XP", DialogueActionType.GIVE_XP),
            ("Give Gold", DialogueActionType.GIVE_GOLD),
            ("Play Sound", DialogueActionType.PLAY_SOUND),
            ("Remove NPC", DialogueActionType.REMOVE_NPC),
            ("Custom Lua", DialogueActionType.CUSTOM_LUA)
        ]

        for display_text, action_type in action_types:
            self.action_combo.addItem(display_text, action_type)

        self.action_combo.setCurrentText(self.get_action_display_text())
        self.action_combo.currentTextChanged.connect(self.on_action_type_changed)
        form.addRow("Action Type:", self.action_combo)

        # Parameters (dynamic based on action type)
        self.params_frame = QFrame()
        self.params_layout = QVBoxLayout(self.params_frame)
        self.setup_params_for_action()
        form.addRow("Parameters:", self.params_frame)

        # Description
        self.description_edit = QLineEdit()
        self.description_edit.setText(self.action.description)
        form.addRow("Description:", self.description_edit)

        layout.addLayout(form)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Set initial values
        self.set_action_values()

    def get_action_display_text(self) -> str:
        """Get display text for current action type"""
        action_type = self.action.action_type
        type_map = {
            DialogueActionType.SET_GLOBAL_FLAG: "Set Global Flag",
            DialogueActionType.CLEAR_GLOBAL_FLAG: "Clear Global Flag",
            DialogueActionType.QUEST_BEGIN: "Begin Quest",
            DialogueActionType.QUEST_COMPLETE: "Complete Quest",
            DialogueActionType.GIVE_ITEM: "Give Item",
            DialogueActionType.TAKE_ITEM: "Take Item",
            DialogueActionType.GIVE_XP: "Give XP",
            DialogueActionType.GIVE_GOLD: "Give Gold",
            DialogueActionType.PLAY_SOUND: "Play Sound",
            DialogueActionType.REMOVE_NPC: "Remove NPC",
            DialogueActionType.CUSTOM_LUA: "Custom Lua"
        }
        return type_map.get(action_type, "Unknown")

    def setup_params_for_action(self):
        """Setup parameter widgets based on current action type"""
        # Clear existing widgets
        for i in reversed(range(self.params_layout.count())):
            child = self.params_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        action_type = self.action.action_type

        if action_type in [DialogueActionType.SET_GLOBAL_FLAG, DialogueActionType.CLEAR_GLOBAL_FLAG]:
            self.flag_name_edit = QLineEdit()
            self.flag_name_edit.setPlaceholderText("Flag name")
            self.params_layout.addWidget(QLabel("Flag Name:"))
            self.params_layout.addWidget(self.flag_name_edit)

            if action_type == DialogueActionType.SET_GLOBAL_FLAG:
                self.flag_value_check = QCheckBox("Flag is True")
                self.flag_value_check.setChecked(True)
                self.params_layout.addWidget(QLabel("Flag Value:"))
                self.params_layout.addWidget(self.flag_value_check)

        elif action_type in [DialogueActionType.QUEST_BEGIN, DialogueActionType.QUEST_COMPLETE]:
            self.quest_id_spin = QSpinBox()
            self.quest_id_spin.setRange(0, 99999)
            self.params_layout.addWidget(QLabel("Quest ID:"))
            self.params_layout.addWidget(self.quest_id_spin)

        elif action_type in [DialogueActionType.GIVE_ITEM, DialogueActionType.TAKE_ITEM]:
            self.item_id_spin = QSpinBox()
            self.item_id_spin.setRange(0, 99999)
            self.item_count_spin = QSpinBox()
            self.item_count_spin.setRange(1, 9999)
            self.item_count_spin.setValue(1)
            self.params_layout.addWidget(QLabel("Item ID:"))
            self.params_layout.addWidget(self.item_id_spin)
            self.params_layout.addWidget(QLabel("Item Count:"))
            self.params_layout.addWidget(self.item_count_spin)

        elif action_type == DialogueActionType.GIVE_XP:
            self.xp_spin = QSpinBox()
            self.xp_spin.setRange(0, 999999)
            self.params_layout.addWidget(QLabel("XP Amount:"))
            self.params_layout.addWidget(self.xp_spin)

        elif action_type == DialogueActionType.GIVE_GOLD:
            self.gold_spin = QSpinBox()
            self.gold_spin.setRange(0, 999999)
            self.params_layout.addWidget(QLabel("Gold Amount:"))
            self.params_layout.addWidget(self.gold_spin)

        elif action_type == DialogueActionType.PLAY_SOUND:
            self.sound_id_spin = QSpinBox()
            self.sound_id_spin.setRange(0, 99999)
            self.params_layout.addWidget(QLabel("Sound ID:"))
            self.params_layout.addWidget(self.sound_id_spin)

        elif action_type == DialogueActionType.REMOVE_NPC:
            self.npc_id_spin = QSpinBox()
            self.npc_id_spin.setRange(0, 99999)
            self.params_layout.addWidget(QLabel("NPC ID:"))
            self.params_layout.addWidget(self.npc_id_spin)

        elif action_type == DialogueActionType.CUSTOM_LUA:
            self.lua_edit = QTextEdit()
            self.lua_edit.setMaximumHeight(100)
            self.lua_edit.setPlaceholderText("Enter custom LUA action code...")
            self.params_layout.addWidget(QLabel("LUA Code:"))
            self.params_layout.addWidget(self.lua_edit)

    def set_action_values(self):
        """Set parameter values from current action"""
        action_type = self.action.action_type
        params = self.action.params

        if action_type in [DialogueActionType.SET_GLOBAL_FLAG, DialogueActionType.CLEAR_GLOBAL_FLAG]:
            if hasattr(self, 'flag_name_edit'):
                self.flag_name_edit.setText(params.get("flag_name", ""))
            if hasattr(self, 'flag_value_check'):
                self.flag_value_check.setChecked(params.get("value", True))

        elif action_type in [DialogueActionType.QUEST_BEGIN, DialogueActionType.QUEST_COMPLETE]:
            if hasattr(self, 'quest_id_spin'):
                self.quest_id_spin.setValue(params.get("quest_id", 0))

        elif action_type in [DialogueActionType.GIVE_ITEM, DialogueActionType.TAKE_ITEM]:
            if hasattr(self, 'item_id_spin'):
                self.item_id_spin.setValue(params.get("item_id", 0))
            if hasattr(self, 'item_count_spin'):
                self.item_count_spin.setValue(params.get("count", 1))

        elif action_type == DialogueActionType.GIVE_XP:
            if hasattr(self, 'xp_spin'):
                self.xp_spin.setValue(params.get("amount", 0))

        elif action_type == DialogueActionType.GIVE_GOLD:
            if hasattr(self, 'gold_spin'):
                self.gold_spin.setValue(params.get("amount", 0))

        elif action_type == DialogueActionType.PLAY_SOUND:
            if hasattr(self, 'sound_id_spin'):
                self.sound_id_spin.setValue(params.get("sound_id", 0))

        elif action_type == DialogueActionType.REMOVE_NPC:
            if hasattr(self, 'npc_id_spin'):
                self.npc_id_spin.setValue(params.get("npc_id", 0))

        elif action_type == DialogueActionType.CUSTOM_LUA:
            if hasattr(self, 'lua_edit'):
                self.lua_edit.setPlainText(params.get("lua_code", ""))

    def on_action_type_changed(self, text: str):
        """Handle action type change"""
        self.setup_params_for_action()

    def get_action(self) -> DialogueAction:
        """Get the constructed action"""
        # Get selected action type
        current_data = self.action_combo.currentData()
        if current_data:
            self.action.action_type = current_data

        # Update parameters
        params = {}
        action_type = self.action.action_type

        if action_type in [DialogueActionType.SET_GLOBAL_FLAG, DialogueActionType.CLEAR_GLOBAL_FLAG]:
            if hasattr(self, 'flag_name_edit'):
                params["flag_name"] = self.flag_name_edit.text()
            if hasattr(self, 'flag_value_check'):
                params["value"] = self.flag_value_check.isChecked()

        elif action_type in [DialogueActionType.QUEST_BEGIN, DialogueActionType.QUEST_COMPLETE]:
            if hasattr(self, 'quest_id_spin'):
                params["quest_id"] = self.quest_id_spin.value()

        elif action_type in [DialogueActionType.GIVE_ITEM, DialogueActionType.TAKE_ITEM]:
            if hasattr(self, 'item_id_spin'):
                params["item_id"] = self.item_id_spin.value()
            if hasattr(self, 'item_count_spin'):
                params["count"] = self.item_count_spin.value()

        elif action_type == DialogueActionType.GIVE_XP:
            if hasattr(self, 'xp_spin'):
                params["amount"] = self.xp_spin.value()

        elif action_type == DialogueActionType.GIVE_GOLD:
            if hasattr(self, 'gold_spin'):
                params["amount"] = self.gold_spin.value()

        elif action_type == DialogueActionType.PLAY_SOUND:
            if hasattr(self, 'sound_id_spin'):
                params["sound_id"] = self.sound_id_spin.value()

        elif action_type == DialogueActionType.REMOVE_NPC:
            if hasattr(self, 'npc_id_spin'):
                params["npc_id"] = self.npc_id_spin.value()

        elif action_type == DialogueActionType.CUSTOM_LUA:
            if hasattr(self, 'lua_edit'):
                params["lua_code"] = self.lua_edit.toPlainText()

        self.action.params = params
        self.action.description = self.description_edit.text()

        return self.action


class EnhancedDialogueEditor(QWidget):
    """
    Enhanced Dialogue Editor

    Extends the text mode dialogue overview with condition and action management.
    """

    # Signals
    dialogue_updated = Signal()  # Emitted when dialogue is modified
    node_selected = Signal(str)   # Emitted when a node is selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dialogue_tree = DialogueTree()
        self.current_node_id = None
        self.current_choice_index = None

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.new_node_btn = QPushButton("+ Node")
        self.new_choice_btn = QPushButton("+ Choice")
        self.validate_btn = QPushButton("Validate")
        self.export_lua_btn = QPushButton("Export LUA")

        toolbar.addWidget(self.new_node_btn)
        toolbar.addWidget(self.new_choice_btn)
        toolbar.addSeparator()
        toolbar.addWidget(self.validate_btn)
        toolbar.addWidget(self.export_lua_btn)

        layout.addWidget(toolbar)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left: Text mode dialogue overview
        try:
            self.text_overview = TextModeDialogueOverview()
            splitter.addWidget(self.text_overview)
        except ImportError:
            # Fallback if text overview not available
            self.text_overview = None
            placeholder = QTextEdit()
            placeholder.setPlainText("Text mode overview not available")
            splitter.addWidget(placeholder)

        # Right: Tabbed panels
        self.tab_widget = QTabWidget()

        # Node details tab
        self.setup_node_details_tab()

        # Conditions tab
        self.setup_conditions_tab()

        # Actions tab
        self.setup_actions_tab()

        # Variables tab
        self.setup_variables_tab()

        splitter.addWidget(self.tab_widget)

        # Set splitter sizes
        splitter.setSizes([600, 400])

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

    def setup_node_details_tab(self):
        """Setup the node details tab"""
        details_frame = QWidget()
        layout = QVBoxLayout(details_frame)

        # Basic node info
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)

        self.node_id_edit = QLineEdit()
        self.speaker_edit = QLineEdit()
        self.node_type_combo = QComboBox()
        self.node_type_combo.addItems(["npc", "player", "start", "end"])
        self.text_edit = QTextEdit()
        self.text_edit.setMaximumHeight(80)

        basic_layout.addRow("Node ID:", self.node_id_edit)
        basic_layout.addRow("Speaker:", self.speaker_edit)
        basic_layout.addRow("Type:", self.node_type_combo)
        basic_layout.addRow("Text:", self.text_edit)

        layout.addWidget(basic_group)
        layout.addStretch()

        self.tab_widget.addTab(details_frame, "📝 Node Details")

    def setup_conditions_tab(self):
        """Setup the conditions tab"""
        conditions_frame = QWidget()
        layout = QVBoxLayout(conditions_frame)

        # Node conditions
        node_conditions_group = QGroupBox("Node Conditions")
        node_conditions_layout = QVBoxLayout(node_conditions_group)

        self.node_conditions_list = QTreeWidget()
        self.node_conditions_list.setHeaderLabels(["Condition", "Type", "Status"])
        self.node_conditions_list.setMaximumHeight(150)
        node_conditions_layout.addWidget(self.node_conditions_list)

        node_conditions_buttons = QHBoxLayout()
        self.add_node_condition_btn = QPushButton("+ Add")
        self.edit_node_condition_btn = QPushButton("Edit")
        self.remove_node_condition_btn = QPushButton("Remove")
        node_conditions_buttons.addWidget(self.add_node_condition_btn)
        node_conditions_buttons.addWidget(self.edit_node_condition_btn)
        node_conditions_buttons.addWidget(self.remove_node_condition_btn)
        node_conditions_layout.addLayout(node_conditions_buttons)

        layout.addWidget(node_conditions_group)

        # Choice conditions
        choice_conditions_group = QGroupBox("Choice Conditions")
        choice_conditions_layout = QVBoxLayout(choice_conditions_group)

        self.choice_selector = QComboBox()
        choice_conditions_layout.addWidget(QLabel("Select Choice:"))
        choice_conditions_layout.addWidget(self.choice_selector)

        self.choice_conditions_list = QTreeWidget()
        self.choice_conditions_list.setHeaderLabels(["Condition", "Type", "Status"])
        self.choice_conditions_list.setMaximumHeight(150)
        choice_conditions_layout.addWidget(self.choice_conditions_list)

        choice_conditions_buttons = QHBoxLayout()
        self.add_choice_condition_btn = QPushButton("+ Add")
        self.edit_choice_condition_btn = QPushButton("Edit")
        self.remove_choice_condition_btn = QPushButton("Remove")
        choice_conditions_buttons.addWidget(self.add_choice_condition_btn)
        choice_conditions_buttons.addWidget(self.edit_choice_condition_btn)
        choice_conditions_buttons.addWidget(self.remove_choice_condition_btn)
        choice_conditions_layout.addLayout(choice_conditions_buttons)

        layout.addWidget(choice_conditions_group)
        layout.addStretch()

        self.tab_widget.addTab(conditions_frame, "🔒 Conditions")

    def setup_actions_tab(self):
        """Setup the actions tab"""
        actions_frame = QWidget()
        layout = QVBoxLayout(actions_frame)

        # Node actions
        node_actions_group = QGroupBox("Node Actions")
        node_actions_layout = QVBoxLayout(node_actions_group)

        self.node_actions_list = QTreeWidget()
        self.node_actions_list.setHeaderLabels(["Action", "Type", "Status"])
        self.node_actions_list.setMaximumHeight(150)
        node_actions_layout.addWidget(self.node_actions_list)

        node_actions_buttons = QHBoxLayout()
        self.add_node_action_btn = QPushButton("+ Add")
        self.edit_node_action_btn = QPushButton("Edit")
        self.remove_node_action_btn = QPushButton("Remove")
        node_actions_buttons.addWidget(self.add_node_action_btn)
        node_actions_buttons.addWidget(self.edit_node_action_btn)
        node_actions_buttons.addWidget(self.remove_node_action_btn)
        node_actions_layout.addLayout(node_actions_buttons)

        layout.addWidget(node_actions_group)

        # Choice actions
        choice_actions_group = QGroupBox("Choice Actions")
        choice_actions_layout = QVBoxLayout(choice_actions_group)

        self.choice_action_selector = QComboBox()
        choice_actions_layout.addWidget(QLabel("Select Choice:"))
        choice_actions_layout.addWidget(self.choice_action_selector)

        self.choice_actions_list = QTreeWidget()
        self.choice_actions_list.setHeaderLabels(["Action", "Type", "Status"])
        self.choice_actions_list.setMaximumHeight(150)
        choice_actions_layout.addWidget(self.choice_actions_list)

        choice_actions_buttons = QHBoxLayout()
        self.add_choice_action_btn = QPushButton("+ Add")
        self.edit_choice_action_btn = QPushButton("Edit")
        self.remove_choice_action_btn = QPushButton("Remove")
        choice_actions_buttons.addWidget(self.add_choice_action_btn)
        choice_actions_buttons.addWidget(self.edit_choice_action_btn)
        choice_actions_buttons.addWidget(self.remove_choice_action_btn)
        choice_actions_layout.addLayout(choice_actions_buttons)

        layout.addWidget(choice_actions_group)
        layout.addStretch()

        self.tab_widget.addTab(actions_frame, "⚡ Actions")

    def setup_variables_tab(self):
        """Setup the variables tab"""
        variables_frame = QWidget()
        layout = QVBoxLayout(variables_frame)

        # Variables overview
        variables_group = QGroupBox("Variables & Flags")
        variables_layout = QVBoxLayout(variables_group)

        self.variables_table = QTableWidget()
        self.variables_table.setColumnCount(4)
        self.variables_table.setHorizontalHeaderLabels(["Name", "Type", "Value", "Scope"])
        self.variables_table.horizontalHeader().setStretchLastSection(True)
        variables_layout.addWidget(self.variables_table)

        variables_buttons = QHBoxLayout()
        self.add_variable_btn = QPushButton("+ Add Variable")
        self.edit_variable_btn = QPushButton("Edit")
        self.remove_variable_btn = QPushButton("Remove")
        variables_buttons.addWidget(self.add_variable_btn)
        variables_buttons.addWidget(self.edit_variable_btn)
        variables_buttons.addWidget(self.remove_variable_btn)
        variables_layout.addLayout(variables_buttons)

        layout.addWidget(variables_group)

        # Quest linking
        quest_group = QGroupBox("Quest Integration")
        quest_layout = QVBoxLayout(quest_group)

        self.quest_combo = QComboBox()
        self.quest_combo.setEditable(True)
        self.quest_combo.setPlaceholderText("Select or enter quest ID")
        quest_layout.addWidget(QLabel("Linked Quest:"))
        quest_layout.addWidget(self.quest_combo)

        self.quest_notes_edit = QTextEdit()
        self.quest_notes_edit.setMaximumHeight(80)
        self.quest_notes_edit.setPlaceholderText("Quest integration notes...")
        quest_layout.addWidget(QLabel("Integration Notes:"))
        quest_layout.addWidget(self.quest_notes_edit)

        layout.addWidget(quest_group)
        layout.addStretch()

        self.tab_widget.addTab(variables_frame, "🔧 Variables")

    def setup_connections(self):
        """Setup signal connections"""
        # Toolbar buttons
        self.new_node_btn.clicked.connect(self.add_new_node)
        self.new_choice_btn.clicked.connect(self.add_new_choice)
        self.validate_btn.clicked.connect(self.validate_dialogue)
        self.export_lua_btn.clicked.connect(self.export_lua)

        # Node details
        self.node_id_edit.textChanged.connect(self.on_node_changed)
        self.speaker_edit.textChanged.connect(self.on_node_changed)
        self.node_type_combo.currentTextChanged.connect(self.on_node_changed)
        self.text_edit.textChanged.connect(self.on_node_changed)

        # Conditions
        self.add_node_condition_btn.clicked.connect(self.add_node_condition)
        self.edit_node_condition_btn.clicked.connect(self.edit_node_condition)
        self.remove_node_condition_btn.clicked.connect(self.remove_node_condition)

        self.add_choice_condition_btn.clicked.connect(self.add_choice_condition)
        self.edit_choice_condition_btn.clicked.connect(self.edit_choice_condition)
        self.remove_choice_condition_btn.clicked.connect(self.remove_choice_condition)

        # Actions
        self.add_node_action_btn.clicked.connect(self.add_node_action)
        self.edit_node_action_btn.clicked.connect(self.edit_node_action)
        self.remove_node_action_btn.clicked.connect(self.remove_node_action)

        self.add_choice_action_btn.clicked.connect(self.add_choice_action)
        self.edit_choice_action_btn.clicked.connect(self.edit_choice_action)
        self.remove_choice_action_btn.clicked.connect(self.remove_choice_action)

        # Variables
        self.add_variable_btn.clicked.connect(self.add_variable)
        self.edit_variable_btn.clicked.connect(self.edit_variable)
        self.remove_variable_btn.clicked.connect(self.remove_variable)

    def load_dialogue_data(self, dialogue_data: Dict[str, Any]):
        """Load dialogue data into the editor"""
        try:
            self.dialogue_tree = DialogueTree.from_dict(dialogue_data)
            self.refresh_display()
            self.status_label.setText(f"Loaded dialogue with {len(self.dialogue_tree.nodes)} nodes")
        except Exception as e:
            logger.error(f"Error loading dialogue data: {e}")
            QMessageBox.critical(self, "Load Error", f"Failed to load dialogue data: {e}")

    def refresh_display(self):
        """Refresh all display elements"""
        self.update_node_selector()
        self.update_choice_selectors()
        self.update_conditions_list()
        self.update_actions_list()

    def update_node_selector(self):
        """Update node selector dropdowns"""
        if not self.dialogue_tree.nodes:
            return

        node_ids = list(self.dialogue_tree.nodes.keys())

        # Update choice selectors
        self.choice_selector.clear()
        self.choice_action_selector.clear()

        if self.current_node_id and self.current_node_id in self.dialogue_tree.nodes:
            node = self.dialogue_tree.nodes[self.current_node_id]
            for i, choice in enumerate(node.choices):
                choice_text = f"Choice {i+1}: {choice.text[:30]}..."
                self.choice_selector.addItem(choice_text, i)
                self.choice_action_selector.addItem(choice_text, i)

    def update_choice_selectors(self):
        """Update choice selector dropdowns"""
        self.update_node_selector()

    def update_conditions_list(self):
        """Update conditions display"""
        # Update node conditions
        self.node_conditions_list.clear()
        if self.current_node_id and self.current_node_id in self.dialogue_tree.nodes:
            node = self.dialogue_tree.nodes[self.current_node_id]
            for condition in node.conditions:
                item = QTreeWidgetItem([
                    condition.get_display_text(),
                    condition.condition_type.value,
                    "✓ Active" if not condition.negated else "⚠️ Negated"
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, condition)
                self.node_conditions_list.addTopLevelItem(item)

        # Update choice conditions
        self.choice_conditions_list.clear()
        if self.current_node_id and self.current_node_id in self.dialogue_tree.nodes:
            node = self.dialogue_tree.nodes[self.current_node_id]
            current_choice = self.choice_selector.currentData()
            if current_choice is not None and current_choice < len(node.choices):
                choice = node.choices[current_choice]
                for condition in choice.conditions:
                    item = QTreeWidgetItem([
                        condition.get_display_text(),
                        condition.condition_type.value,
                        "✓ Active" if not condition.negated else "⚠️ Negated"
                    ])
                    item.setData(0, Qt.ItemDataRole.UserRole, condition)
                    self.choice_conditions_list.addTopLevelItem(item)

    def update_actions_list(self):
        """Update actions display"""
        # Update node actions
        self.node_actions_list.clear()
        if self.current_node_id and self.current_node_id in self.dialogue_tree.nodes:
            node = self.dialogue_tree.nodes[self.current_node_id]
            for action in node.actions:
                item = QTreeWidgetItem([
                    action.get_display_text(),
                    action.action_type.value,
                    "✓ Active"
                ])
                item.setData(0, Qt.ItemDataRole.UserRole, action)
                self.node_actions_list.addTopLevelItem(item)

        # Update choice actions
        self.choice_actions_list.clear()
        if self.current_node_id and self.current_node_id in self.dialogue_tree.nodes:
            node = self.dialogue_tree.nodes[self.current_node_id]
            current_choice = self.choice_action_selector.currentData()
            if current_choice is not None and current_choice < len(node.choices):
                choice = node.choices[current_choice]
                for action in choice.actions:
                    item = QTreeWidgetItem([
                        action.get_display_text(),
                        action.action_type.value,
                        "✓ Active"
                    ])
                    item.setData(0, Qt.ItemDataRole.UserRole, action)
                    self.choice_actions_list.addTopLevelItem(item)

    def on_node_changed(self):
        """Handle node data changes"""
        if not self.current_node_id:
            return

        node = self.dialogue_tree.get_node(self.current_node_id)
        if not node:
            return

        # Update node data
        node.node_id = self.node_id_edit.text() or node.node_id
        node.speaker = self.speaker_edit.text()
        node.node_type = self.node_type_combo.currentText()
        node.text = self.text_edit.toPlainText()

        self.dialogue_updated.emit()
        self.status_label.setText(f"Updated node: {node.node_id}")

    def add_new_node(self):
        """Add a new dialogue node"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Node")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        node_id_edit = QLineEdit()
        node_id_edit.setPlaceholderText("node_001")

        layout.addLayout(form)
        form.addRow("Node ID:", node_id_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            node_id = node_id_edit.text() or "node_001"

            # Create new node
            new_node = DialogueNode(
                node_id=node_id,
                node_type="npc",
                text="New dialogue text",
                choices=[]
            )

            self.dialogue_tree.add_node(new_node)
            self.current_node_id = node_id
            self.refresh_display()
            self.status_label.setText(f"Added new node: {node_id}")

    def add_new_choice(self):
        """Add a new choice to current node"""
        if not self.current_node_id:
            QMessageBox.warning(self, "No Node", "Please select a node first")
            return

        node = self.dialogue_tree.get_node(self.current_node_id)
        if not node:
            return

        # Create new choice
        new_choice = DialogueChoice(
            text="New choice text",
            next_node_id=""
        )

        node.choices.append(new_choice)
        self.refresh_display()
        self.status_label.setText(f"Added new choice to node: {self.current_node_id}")

    def add_node_condition(self):
        """Add condition to current node"""
        if not self.current_node_id:
            QMessageBox.warning(self, "No Node", "Please select a node first")
            return

        dialog = ConditionBuilderDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            condition = dialog.get_condition()

            node = self.dialogue_tree.get_node(self.current_node_id)
            if node:
                node.conditions.append(condition)
                self.update_conditions_list()
                self.status_label.setText(f"Added condition to node: {self.current_node_id}")

    def edit_node_condition(self):
        """Edit selected node condition"""
        selected_items = self.node_conditions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a condition to edit")
            return

        condition = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if condition:
            dialog = ConditionBuilderDialog(self, condition)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_condition = dialog.get_condition()
                # Update the condition in the node
                self.update_conditions_list()
                self.status_label.setText("Updated node condition")

    def remove_node_condition(self):
        """Remove selected node condition"""
        selected_items = self.node_conditions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a condition to remove")
            return

        condition = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if condition and self.current_node_id:
            node = self.dialogue_tree.get_node(self.current_node_id)
            if node and condition in node.conditions:
                node.conditions.remove(condition)
                self.update_conditions_list()
                self.status_label.setText("Removed node condition")

    def add_choice_condition(self):
        """Add condition to current choice"""
        if not self.current_node_id:
            QMessageBox.warning(self, "No Node", "Please select a node first")
            return

        current_choice = self.choice_selector.currentData()
        if current_choice is None:
            QMessageBox.warning(self, "No Choice", "Please select a choice first")
            return

        dialog = ConditionBuilderDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            condition = dialog.get_condition()

            node = self.dialogue_tree.get_node(self.current_node_id)
            if node and current_choice < len(node.choices):
                node.choices[current_choice].conditions.append(condition)
                self.update_conditions_list()
                self.status_label.setText(f"Added condition to choice {current_choice + 1}")

    def edit_choice_condition(self):
        """Edit selected choice condition"""
        selected_items = self.choice_conditions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a condition to edit")
            return

        condition = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if condition:
            dialog = ConditionBuilderDialog(self, condition)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_condition = dialog.get_condition()
                self.update_conditions_list()
                self.status_label.setText("Updated choice condition")

    def remove_choice_condition(self):
        """Remove selected choice condition"""
        selected_items = self.choice_conditions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a condition to remove")
            return

        condition = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if condition and self.current_node_id:
            node = self.dialogue_tree.get_node(self.current_node_id)
            current_choice = self.choice_selector.currentData()
            if node and current_choice < len(node.choices):
                choice = node.choices[current_choice]
                if condition in choice.conditions:
                    choice.conditions.remove(condition)
                    self.update_conditions_list()
                    self.status_label.setText(f"Removed condition from choice {current_choice + 1}")

    def add_node_action(self):
        """Add action to current node"""
        if not self.current_node_id:
            QMessageBox.warning(self, "No Node", "Please select a node first")
            return

        dialog = ActionBuilderDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            action = dialog.get_action()

            node = self.dialogue_tree.get_node(self.current_node_id)
            if node:
                node.actions.append(action)
                self.update_actions_list()
                self.status_label.setText(f"Added action to node: {self.current_node_id}")

    def edit_node_action(self):
        """Edit selected node action"""
        selected_items = self.node_actions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an action to edit")
            return

        action = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if action:
            dialog = ActionBuilderDialog(self, action)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_action = dialog.get_action()
                self.update_actions_list()
                self.status_label.setText("Updated node action")

    def remove_node_action(self):
        """Remove selected node action"""
        selected_items = self.node_actions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an action to remove")
            return

        action = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if action and self.current_node_id:
            node = self.dialogue_tree.get_node(self.current_node_id)
            if node and action in node.actions:
                node.actions.remove(action)
                self.update_actions_list()
                self.status_label.setText("Removed node action")

    def add_choice_action(self):
        """Add action to current choice"""
        if not self.current_node_id:
            QMessageBox.warning(self, "No Node", "Please select a node first")
            return

        current_choice = self.choice_action_selector.currentData()
        if current_choice is None:
            QMessageBox.warning(self, "No Choice", "Please select a choice first")
            return

        dialog = ActionBuilderDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            action = dialog.get_action()

            node = self.dialogue_tree.get_node(self.current_node_id)
            if node and current_choice < len(node.choices):
                node.choices[current_choice].actions.append(action)
                self.update_actions_list()
                self.status_label.setText(f"Added action to choice {current_choice + 1}")

    def edit_choice_action(self):
        """Edit selected choice action"""
        selected_items = self.choice_actions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an action to edit")
            return

        action = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if action:
            dialog = ActionBuilderDialog(self, action)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_action = dialog.get_action()
                self.update_actions_list()
                self.status_label.setText("Updated choice action")

    def remove_choice_action(self):
        """Remove selected choice action"""
        selected_items = self.choice_actions_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an action to remove")
            return

        action = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if action and self.current_node_id:
            node = self.dialogue_tree.get_node(self.current_node_id)
            current_choice = self.choice_action_selector.currentData()
            if node and current_choice < len(node.choices):
                choice = node.choices[current_choice]
                if action in choice.actions:
                    choice.actions.remove(action)
                    self.update_actions_list()
                    self.status_label.setText(f"Removed action from choice {current_choice + 1}")

    def add_variable(self):
        """Add a new variable"""
        QMessageBox.information(self, "Variable Management", "Variable management feature coming soon!")

    def edit_variable(self):
        """Edit selected variable"""
        QMessageBox.information(self, "Variable Management", "Variable management feature coming soon!")

    def remove_variable(self):
        """Remove selected variable"""
        QMessageBox.information(self, "Variable Management", "Variable management feature coming soon!")

    def validate_dialogue(self):
        """Validate the dialogue and show results"""
        issues = self.dialogue_tree.validate()

        if not issues:
            QMessageBox.information(self, "Validation Complete", "✅ Dialogue is valid!")
            self.status_label.setText("✅ Validation passed - no issues found")
        else:
            QMessageBox.warning(self, "Validation Issues", f"Found {len(issues)} issues:\n\n" + "\n".join(f"• {issue}" for issue in issues))
            self.status_label.setText(f"⚠️ Validation found {len(issues)} issues")

    def export_lua(self):
        """Export dialogue to LUA code"""
        try:
            lua_code = self.generate_lua_export()

            # Show dialog with export options
            dialog = QDialog(self)
            dialog.setWindowTitle("Export LUA")
            dialog.setMinimumWidth(600)

            layout = QVBoxLayout(dialog)

            text_edit = QTextEdit()
            text_edit.setFont(QFont("Courier New", 10))
            text_edit.setPlainText(lua_code)
            layout.addWidget(text_edit)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            layout.addWidget(buttons)

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export LUA: {e}")

    def generate_lua_export(self) -> str:
        """Generate LUA code for the dialogue"""
        lines = []
        lines.append("-- Generated Enhanced Dialogue Script")
        lines.append(f"-- Nodes: {len(self.dialogue_tree.nodes)}")
        lines.append("")

        lines.append("function CreateStateMachine(_Type, _PlatformId, _NpcId, _X, _Y)")
        lines.append("BeginDefinition(_Type, _PlatformId, _NpcId, _X, _Y)")
        lines.append("")

        # Export all nodes
        for node_id, node in self.dialogue_tree.nodes.items():
            lines.extend(node.to_lua().split('\n'))
            lines.append("")

        lines.append("EndDefinition()")
        lines.append("end")
        lines.append("")

        return '\n'.join(lines)

    def get_dialogue_data(self) -> Dict[str, Any]:
        """Get the dialogue data as dictionary"""
        return self.dialogue_tree.to_dict()

    def set_current_node(self, node_id: str):
        """Set the current node for editing"""
        self.current_node_id = node_id

        # Update UI with node data
        node = self.dialogue_tree.get_node(node_id)
        if node:
            self.node_id_edit.setText(node.node_id)
            self.speaker_edit.setText(node.speaker)
            self.node_type_combo.setCurrentText(node.node_type)
            self.text_edit.setPlainText(node.text)

        self.refresh_display()
        self.node_selected.emit(node_id)


# Test function
def test_enhanced_dialogue_editor():
    """Test the enhanced dialogue editor"""
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create test dialogue data
    test_data = {
        "nodes": [
            {
                "node_id": "start_node",
                "node_type": "npc",
                "speaker": "Guard",
                "text": "Hello, adventurer!",
                "conditions": [
                    {
                        "condition_type": "global_flag",
                        "params": {"flag_name": "player_entered_town", "value": True},
                        "negated": False,
                        "description": "Player has entered town"
                    }
                ],
                "actions": [],
                "choices": [
                    {
                        "choice_id": 1,
                        "text": "I need help with a quest.",
                        "next_node_id": "quest_node",
                        "conditions": [],
                        "actions": [
                            {
                                "action_type": "set_global_flag",
                                "params": {"flag_name": "quest_started", "value": True},
                                "description": "Mark quest as started"
                            }
                        ]
                    },
                    {
                        "choice_id": 2,
                        "text": "Just passing through.",
                        "next_node_id": "goodbye_node",
                        "conditions": [],
                        "actions": []
                    }
                ]
            }
        ],
        "start_node_id": "start_node"
    }

    # Create and show editor
    editor = EnhancedDialogueEditor()
    editor.load_dialogue_data(test_data)
    editor.setWindowTitle("Enhanced Dialogue Editor Test")
    editor.resize(1200, 800)
    editor.show()

    return app.exec()


if __name__ == "__main__":
    test_enhanced_dialogue_editor()