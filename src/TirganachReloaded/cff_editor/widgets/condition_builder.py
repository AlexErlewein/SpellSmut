"""
Condition Builder Widget
========================
Visual builder for quest conditions with AND/OR/NOT logic.

Author: Quest Editor Team
Date: November 16, 2025
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QComboBox, QLineEdit, QSpinBox, QDialog,
    QDialogButtonBox, QGroupBox, QMessageBox, QTextEdit, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from typing import Dict, List, Optional, Any
import json


class Condition:
    """Base class for all condition types"""
    
    def __init__(self, condition_type: str, params: Dict[str, Any] = None, negated: bool = False):
        self.condition_type = condition_type  # "QuestState", "ItemFlag", "NpcFlag", etc.
        self.params = params or {}
        self.negated = negated
        self.id = id(self)  # Unique ID for this condition
    
    def to_dict(self):
        return {
            "type": self.condition_type,
            "params": self.params,
            "negated": self.negated
        }
    
    def to_lua(self) -> str:
        """Generate LUA code for this condition"""
        lua = self._generate_lua()
        if self.negated:
            return f"Negated({lua})"
        return lua
    
    def _generate_lua(self) -> str:
        """Override in subclasses"""
        if self.condition_type == "QuestState":
            quest_id = self.params.get("quest_id", 0)
            state = self.params.get("state", "StateActive")
            return f"QuestState{{QuestId = {quest_id}, State = {state}}}"
        
        elif self.condition_type == "ItemFlag":
            flag_name = self.params.get("flag_name", "")
            flag_state = self.params.get("flag_state", "true")
            func = "IsItemFlagTrue" if flag_state == "true" else "IsItemFlagFalse"
            return f'{func}{{Name = "{flag_name}"}}'
        
        elif self.condition_type == "NpcFlag":
            flag_name = self.params.get("flag_name", "")
            flag_state = self.params.get("flag_state", "true")
            func = "IsNpcFlagTrue" if flag_state == "true" else "IsNpcFlagFalse"
            return f'{func}{{Name = "{flag_name}"}}'
        
        elif self.condition_type == "GlobalFlag":
            flag_name = self.params.get("flag_name", "")
            flag_state = self.params.get("flag_state", "true")
            func = "IsGlobalFlagTrue" if flag_state == "true" else "IsGlobalFlagFalse"
            return f'{func}{{Name = "{flag_name}"}}'
        
        elif self.condition_type == "TimeDay":
            return "TimeDay()"
        
        elif self.condition_type == "TimeNight":
            return "TimeNight()"
        
        return f"-- Unknown condition: {self.condition_type}"
    
    def __str__(self):
        """Human-readable description"""
        desc = self._describe()
        if self.negated:
            return f"NOT ({desc})"
        return desc
    
    def _describe(self) -> str:
        """Override in subclasses"""
        if self.condition_type == "QuestState":
            quest_id = self.params.get("quest_id", 0)
            state = self.params.get("state", "StateActive")
            return f"Quest {quest_id} is {state}"
        
        elif self.condition_type in ["ItemFlag", "NpcFlag", "GlobalFlag"]:
            flag_name = self.params.get("flag_name", "")
            flag_state = self.params.get("flag_state", "true")
            state_str = "TRUE" if flag_state == "true" else "FALSE"
            type_prefix = {"ItemFlag": "Item", "NpcFlag": "NPC", "GlobalFlag": "Global"}
            return f"{type_prefix[self.condition_type]} flag '{flag_name}' is {state_str}"
        
        elif self.condition_type == "TimeDay":
            return "Is daytime"
        
        elif self.condition_type == "TimeNight":
            return "Is nighttime"
        
        return f"{self.condition_type}"
    
    @staticmethod
    def from_dict(data: dict):
        return Condition(
            condition_type=data.get("type", "QuestState"),
            params=data.get("params", {}),
            negated=data.get("negated", False)
        )


class LogicalCondition:
    """Logical operator combining conditions (AND/OR)"""
    
    def __init__(self, operator: str, children: List[Any] = None):
        self.operator = operator  # "UND" (AND) or "ODER" (OR)
        self.children = children or []  # List of Condition or LogicalCondition
        self.negated = False
        self.id = id(self)
    
    def to_dict(self):
        return {
            "operator": self.operator,
            "children": [c.to_dict() for c in self.children],
            "negated": self.negated
        }
    
    def to_lua(self) -> str:
        """Generate LUA code for this logical condition"""
        if not self.children:
            return "-- Empty condition"
        
        if len(self.children) == 1:
            return self.children[0].to_lua()
        
        # SpellForce uses binary operators, so nest them
        # UND(c1, UND(c2, UND(c3, c4)))
        lua = self.children[-1].to_lua()
        for i in range(len(self.children) - 2, -1, -1):
            child_lua = self.children[i].to_lua()
            lua = f"{self.operator}({child_lua}, {lua})"
        
        if self.negated:
            return f"Negated({lua})"
        
        return lua
    
    def __str__(self):
        """Human-readable description"""
        if not self.children:
            return "Empty group"
        
        op_str = " AND " if self.operator == "UND" else " OR "
        children_str = op_str.join(f"({str(c)})" for c in self.children)
        
        if self.negated:
            return f"NOT ({children_str})"
        return children_str
    
    @staticmethod
    def from_dict(data: dict):
        children = []
        for child_data in data.get("children", []):
            if "operator" in child_data:
                children.append(LogicalCondition.from_dict(child_data))
            else:
                children.append(Condition.from_dict(child_data))
        
        logical = LogicalCondition(
            operator=data.get("operator", "UND"),
            children=children
        )
        logical.negated = data.get("negated", False)
        return logical


class ConditionEditorDialog(QDialog):
    """Dialog for adding/editing a single condition"""
    
    def __init__(self, parent=None, condition: Condition = None, flag_manager=None):
        super().__init__(parent)
        self.condition = condition
        self.flag_manager = flag_manager
        self.setup_ui()
        
        if condition:
            self.load_condition(condition)
    
    def setup_ui(self):
        self.setWindowTitle("Condition Editor")
        self.setModal(True)
        self.resize(550, 400)
        
        layout = QVBoxLayout(self)
        
        # Condition Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Condition Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "QuestState",
            "ItemFlag",
            "NpcFlag",
            "GlobalFlag",
            "TimeDay",
            "TimeNight"
        ])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo, 1)
        layout.addLayout(type_layout)
        
        # Negated checkbox
        self.negated_check = QCheckBox("Negate this condition (NOT)")
        layout.addWidget(self.negated_check)
        
        # Parameters group (changes based on type)
        self.params_group = QGroupBox("Parameters")
        self.params_layout = QVBoxLayout(self.params_group)
        layout.addWidget(self.params_group)
        
        # Initialize with first type
        self.on_type_changed(self.type_combo.currentText())
        
        layout.addStretch()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def on_type_changed(self, condition_type: str):
        """Update parameters UI based on condition type"""
        # Clear existing widgets
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if condition_type == "QuestState":
            # Quest ID
            quest_layout = QHBoxLayout()
            quest_layout.addWidget(QLabel("Quest ID:"))
            self.quest_id_input = QSpinBox()
            self.quest_id_input.setRange(0, 99999)
            quest_layout.addWidget(self.quest_id_input)
            self.params_layout.addLayout(quest_layout)
            
            # State
            state_layout = QHBoxLayout()
            state_layout.addWidget(QLabel("State:"))
            self.state_combo = QComboBox()
            self.state_combo.addItems(["StateActive", "StateSolved", "StateFailed"])
            state_layout.addWidget(self.state_combo)
            self.params_layout.addLayout(state_layout)
        
        elif condition_type in ["ItemFlag", "NpcFlag", "GlobalFlag"]:
            # Flag name
            flag_layout = QHBoxLayout()
            flag_layout.addWidget(QLabel("Flag Name:"))
            self.flag_name_input = QLineEdit()
            self.flag_name_input.setPlaceholderText("Enter flag name...")
            flag_layout.addWidget(self.flag_name_input, 1)
            
            # Browse button if flag manager available
            if self.flag_manager:
                browse_btn = QPushButton("🔍 Browse")
                browse_btn.clicked.connect(lambda: self.browse_flags(condition_type))
                flag_layout.addWidget(browse_btn)
            
            self.params_layout.addLayout(flag_layout)
            
            # Flag state (true/false)
            state_layout = QHBoxLayout()
            state_layout.addWidget(QLabel("Check if flag is:"))
            self.flag_state_combo = QComboBox()
            self.flag_state_combo.addItems(["true", "false"])
            state_layout.addWidget(self.flag_state_combo)
            state_layout.addStretch()
            self.params_layout.addLayout(state_layout)
        
        elif condition_type in ["TimeDay", "TimeNight"]:
            info_label = QLabel("No parameters needed - checks current time of day.")
            info_label.setStyleSheet("color: #666; font-style: italic;")
            self.params_layout.addWidget(info_label)
        
        self.params_layout.addStretch()
    
    def browse_flags(self, flag_type: str):
        """Browse available flags"""
        # Extract flag type from condition type
        type_map = {
            "ItemFlag": "item",
            "NpcFlag": "npc",
            "GlobalFlag": "global"
        }
        
        flag_type_filter = type_map.get(flag_type, "global")
        flags = self.flag_manager.get_flags_by_type(flag_type_filter)
        
        if not flags:
            QMessageBox.information(
                self, "No Flags",
                f"No {flag_type_filter} flags defined yet. Create them in the Flag Manager first."
            )
            return
        
        # Simple selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Select {flag_type_filter.capitalize()} Flag")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        flag_list = QTreeWidget()
        flag_list.setHeaderLabels(["Flag Name", "Description"])
        flag_list.setColumnWidth(0, 200)
        
        for flag in flags:
            item = QTreeWidgetItem([flag.name, flag.description])
            flag_list.addTopLevelItem(item)
        
        flag_list.itemDoubleClicked.connect(dialog.accept)
        layout.addWidget(flag_list)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.Accepted:
            selected = flag_list.currentItem()
            if selected:
                self.flag_name_input.setText(selected.text(0))
    
    def load_condition(self, condition: Condition):
        """Load condition data into editor"""
        self.type_combo.setCurrentText(condition.condition_type)
        self.negated_check.setChecked(condition.negated)
        
        if condition.condition_type == "QuestState":
            self.quest_id_input.setValue(condition.params.get("quest_id", 0))
            self.state_combo.setCurrentText(condition.params.get("state", "StateActive"))
        
        elif condition.condition_type in ["ItemFlag", "NpcFlag", "GlobalFlag"]:
            self.flag_name_input.setText(condition.params.get("flag_name", ""))
            self.flag_state_combo.setCurrentText(condition.params.get("flag_state", "true"))
    
    def get_condition(self) -> Optional[Condition]:
        """Get the edited condition"""
        condition_type = self.type_combo.currentText()
        params = {}
        
        if condition_type == "QuestState":
            params = {
                "quest_id": self.quest_id_input.value(),
                "state": self.state_combo.currentText()
            }
        
        elif condition_type in ["ItemFlag", "NpcFlag", "GlobalFlag"]:
            flag_name = self.flag_name_input.text().strip()
            if not flag_name:
                QMessageBox.warning(self, "Invalid Input", "Flag name cannot be empty!")
                return None
            
            params = {
                "flag_name": flag_name,
                "flag_state": self.flag_state_combo.currentText()
            }
        
        condition = Condition(
            condition_type=condition_type,
            params=params,
            negated=self.negated_check.isChecked()
        )
        
        return condition


class ConditionBuilderWidget(QWidget):
    """
    Visual builder for complex quest conditions.
    
    Features:
    - Tree view of nested conditions
    - AND/OR/NOT logic operators
    - Multiple condition types
    - LUA code generation
    """
    
    conditions_changed = Signal()
    
    def __init__(self, parent=None, flag_manager=None):
        super().__init__(parent)
        self.flag_manager = flag_manager
        self.root_condition = LogicalCondition("UND")  # Root is always AND
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel("Condition Builder")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Build complex conditions using AND/OR/NOT logic. "
                     "Conditions determine when quests appear or progress.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(desc)
        
        # Tree view
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Condition", "Type", "LUA"])
        self.tree.setColumnWidth(0, 300)
        self.tree.setColumnWidth(1, 100)
        self.tree.itemDoubleClicked.connect(self.edit_item)
        layout.addWidget(self.tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_cond_btn = QPushButton("➕ Add Condition")
        add_cond_btn.clicked.connect(self.add_condition)
        button_layout.addWidget(add_cond_btn)
        
        add_group_btn = QPushButton("➕ Add Group (AND/OR)")
        add_group_btn.clicked.connect(self.add_logical_group)
        button_layout.addWidget(add_group_btn)
        
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.clicked.connect(self.edit_item)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.clicked.connect(self.delete_item)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        preview_btn = QPushButton("👁️ Preview LUA")
        preview_btn.clicked.connect(self.preview_lua)
        button_layout.addWidget(preview_btn)
        
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        self.refresh_tree()
    
    def add_condition(self):
        """Add a new condition"""
        dialog = ConditionEditorDialog(self, flag_manager=self.flag_manager)
        if dialog.exec() == QDialog.Accepted:
            condition = dialog.get_condition()
            if condition:
                # Add to selected group or root
                selected = self.tree.currentItem()
                if selected and hasattr(selected, 'condition_obj'):
                    obj = selected.condition_obj
                    if isinstance(obj, LogicalCondition):
                        obj.children.append(condition)
                    else:
                        # Add to root
                        self.root_condition.children.append(condition)
                else:
                    self.root_condition.children.append(condition)
                
                self.refresh_tree()
                self.conditions_changed.emit()
    
    def add_logical_group(self):
        """Add a new AND/OR group"""
        # Ask for operator
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Logical Group")
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Select logical operator:"))
        
        operator_combo = QComboBox()
        operator_combo.addItems(["UND (AND)", "ODER (OR)"])
        layout.addWidget(operator_combo)
        
        negated_check = QCheckBox("Negate this group (NOT)")
        layout.addWidget(negated_check)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.Accepted:
            operator = "UND" if "UND" in operator_combo.currentText() else "ODER"
            group = LogicalCondition(operator)
            group.negated = negated_check.isChecked()
            
            # Add to selected group or root
            selected = self.tree.currentItem()
            if selected and hasattr(selected, 'condition_obj'):
                obj = selected.condition_obj
                if isinstance(obj, LogicalCondition):
                    obj.children.append(group)
                else:
                    self.root_condition.children.append(group)
            else:
                self.root_condition.children.append(group)
            
            self.refresh_tree()
            self.conditions_changed.emit()
    
    def edit_item(self):
        """Edit the selected item"""
        selected = self.tree.currentItem()
        if not selected or not hasattr(selected, 'condition_obj'):
            QMessageBox.information(self, "No Selection", "Please select an item to edit.")
            return
        
        obj = selected.condition_obj
        
        if isinstance(obj, Condition):
            dialog = ConditionEditorDialog(self, obj, self.flag_manager)
            if dialog.exec() == QDialog.Accepted:
                edited = dialog.get_condition()
                if edited:
                    # Update the condition in place
                    obj.condition_type = edited.condition_type
                    obj.params = edited.params
                    obj.negated = edited.negated
                    self.refresh_tree()
                    self.conditions_changed.emit()
        
        elif isinstance(obj, LogicalCondition):
            # Edit operator and negation
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Logical Group")
            layout = QVBoxLayout(dialog)
            
            layout.addWidget(QLabel("Logical operator:"))
            operator_combo = QComboBox()
            operator_combo.addItems(["UND (AND)", "ODER (OR)"])
            if obj.operator == "ODER":
                operator_combo.setCurrentIndex(1)
            layout.addWidget(operator_combo)
            
            negated_check = QCheckBox("Negate this group (NOT)")
            negated_check.setChecked(obj.negated)
            layout.addWidget(negated_check)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            if dialog.exec() == QDialog.Accepted:
                obj.operator = "UND" if "UND" in operator_combo.currentText() else "ODER"
                obj.negated = negated_check.isChecked()
                self.refresh_tree()
                self.conditions_changed.emit()
    
    def delete_item(self):
        """Delete the selected item"""
        selected = self.tree.currentItem()
        if not selected or not hasattr(selected, 'condition_obj'):
            QMessageBox.information(self, "No Selection", "Please select an item to delete.")
            return
        
        obj = selected.condition_obj
        
        # Find parent and remove
        def remove_from_tree(parent_obj, target_obj):
            if hasattr(parent_obj, 'children'):
                if target_obj in parent_obj.children:
                    parent_obj.children.remove(target_obj)
                    return True
                for child in parent_obj.children:
                    if remove_from_tree(child, target_obj):
                        return True
            return False
        
        if remove_from_tree(self.root_condition, obj):
            self.refresh_tree()
            self.conditions_changed.emit()
    
    def clear_all(self):
        """Clear all conditions"""
        reply = QMessageBox.question(
            self, "Clear All",
            "Are you sure you want to clear all conditions?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.root_condition.children.clear()
            self.refresh_tree()
            self.conditions_changed.emit()
    
    def refresh_tree(self):
        """Refresh the tree view"""
        self.tree.clear()
        
        if not self.root_condition.children:
            placeholder = QTreeWidgetItem(["No conditions defined", "", ""])
            placeholder.setForeground(0, QColor(150, 150, 150))
            self.tree.addTopLevelItem(placeholder)
            return
        
        # Build tree recursively
        for child in self.root_condition.children:
            item = self.build_tree_item(child)
            self.tree.addTopLevelItem(item)
        
        self.tree.expandAll()
    
    def build_tree_item(self, obj) -> QTreeWidgetItem:
        """Recursively build tree items"""
        if isinstance(obj, Condition):
            item = QTreeWidgetItem([
                str(obj),
                obj.condition_type,
                obj.to_lua()[:50] + "..." if len(obj.to_lua()) > 50 else obj.to_lua()
            ])
            item.condition_obj = obj
            
            # Color code by type
            type_colors = {
                "QuestState": QColor(52, 152, 219),   # Blue
                "ItemFlag": QColor(46, 204, 113),     # Green
                "NpcFlag": QColor(155, 89, 182),      # Purple
                "GlobalFlag": QColor(230, 126, 34),   # Orange
                "TimeDay": QColor(241, 196, 15),      # Yellow
                "TimeNight": QColor(52, 73, 94)       # Dark blue
            }
            item.setForeground(1, type_colors.get(obj.condition_type, Qt.black))
            
            if obj.negated:
                font = item.font(0)
                font.setBold(True)
                item.setFont(0, font)
            
            return item
        
        elif isinstance(obj, LogicalCondition):
            op_str = "AND" if obj.operator == "UND" else "OR"
            if obj.negated:
                op_str = f"NOT ({op_str})"
            
            item = QTreeWidgetItem([
                f"{op_str} Group ({len(obj.children)} conditions)",
                op_str,
                obj.to_lua()[:50] + "..." if len(obj.to_lua()) > 50 else obj.to_lua()
            ])
            item.condition_obj = obj
            
            # Bold for logical groups
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)
            
            # Color code by operator
            color = QColor(231, 76, 60) if obj.operator == "ODER" else QColor(41, 128, 185)
            item.setForeground(1, color)
            
            # Add children
            for child in obj.children:
                child_item = self.build_tree_item(child)
                item.addChild(child_item)
            
            return item
        
        return QTreeWidgetItem(["Unknown", "", ""])
    
    def preview_lua(self):
        """Preview generated LUA code"""
        lua_code = self.root_condition.to_lua()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("LUA Preview")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Generated LUA code:"))
        
        text_edit = QTextEdit()
        text_edit.setPlainText(lua_code)
        text_edit.setReadOnly(True)
        text_edit.setFontFamily("Courier")
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def get_root_condition(self) -> LogicalCondition:
        """Get the root condition"""
        return self.root_condition
    
    def load_from_dict(self, data: dict):
        """Load conditions from dictionary"""
        if "operator" in data:
            self.root_condition = LogicalCondition.from_dict(data)
        else:
            # Legacy: single condition
            self.root_condition = LogicalCondition("UND")
            self.root_condition.children = [Condition.from_dict(data)]
        
        self.refresh_tree()
    
    def to_dict(self) -> dict:
        """Export conditions to dictionary"""
        return self.root_condition.to_dict()
    
    def to_lua(self) -> str:
        """Generate LUA code"""
        return self.root_condition.to_lua()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Test widget
    widget = ConditionBuilderWidget()
    
    # Add some test conditions
    cond1 = Condition("QuestState", {"quest_id": 646, "state": "StateActive"})
    cond2 = Condition("ItemFlag", {"flag_name": "PlayerHasItemSanduhr", "flag_state": "true"})
    cond3 = Condition("GlobalFlag", {"flag_name": "TrollCampDestroyed", "flag_state": "false"}, negated=True)
    
    or_group = LogicalCondition("ODER")
    or_group.children.append(Condition("TimeDay", {}))
    or_group.children.append(Condition("TimeNight", {}))
    
    widget.root_condition.children = [cond1, cond2, cond3, or_group]
    widget.refresh_tree()
    
    widget.resize(800, 600)
    widget.show()
    
    sys.exit(app.exec())
