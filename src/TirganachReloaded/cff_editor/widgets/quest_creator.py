"""
Quest Creator Widget
Standalone tool for generating SpellForce Lua quest scripts from GUI inputs
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QTextEdit, QTreeWidget, QTreeWidgetItem,
                               QGroupBox, QScrollArea, QSplitter, QPushButton,
                               QLineEdit, QComboBox, QListWidget, QListWidgetItem,
                               QTabWidget, QMessageBox, QFrame, QSplitter,
                               QApplication)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import List, Dict, Any
import json
import re


class QuestCreatorWidget(QWidget):
    """Standalone quest creation tool that generates Lua scripts from GUI inputs"""

    quest_created = Signal(str)  # Emits generated Lua script

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the quest creator UI with tabs for different sections"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title_label = QLabel("Quest Creator - Standalone Quest Generator")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Main content area with tabs
        tab_widget = QTabWidget()

        # Basic Info Tab
        tab_widget.addTab(self.create_basic_info_tab(), "Basic Info")

        # Objectives Tab
        tab_widget.addTab(self.create_objectives_tab(), "Objectives")

        # Rewards Tab
        tab_widget.addTab(self.create_rewards_tab(), "Rewards")

        # Requirements Tab
        tab_widget.addTab(self.create_requirements_tab(), "Requirements")

        # NPCs & Dialog Tab
        tab_widget.addTab(self.create_dialog_tab(), "NPCs & Dialog")

        # Lua Preview Tab
        tab_widget.addTab(self.create_lua_preview_tab(), "Lua Preview")

        layout.addWidget(tab_widget)

        # Generate button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.generate_btn = QPushButton("Generate Lua Script")
        self.generate_btn.setStyleSheet("font-weight: bold; padding: 10px;")
        button_layout.addWidget(self.generate_btn)

        layout.addLayout(button_layout)

    def create_basic_info_tab(self) -> QWidget:
        """Create the basic info tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Quest ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Quest ID:"))
        self.quest_id_edit = QLineEdit()
        self.quest_id_edit.setPlaceholderText("e.g., 1001 - Use unique numeric ID")
        id_layout.addWidget(self.quest_id_edit)
        layout.addLayout(id_layout)

        # Quest Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Quest Name:"))
        self.quest_name_edit = QLineEdit()
        self.quest_name_edit.setPlaceholderText("e.g., The Lost Sword")
        name_layout.addWidget(self.quest_name_edit)
        layout.addLayout(name_layout)

        # Description
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Quest Description:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("Brief description of the quest objective")
        desc_layout.addWidget(self.description_edit)
        layout.addLayout(desc_layout)

        # Quest Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Quest Type:"))
        self.quest_type_combo = QComboBox()
        self.quest_type_combo.addItems(["Main Quest", "Side Quest", "Sub-quest", "Collection", "Kill", "Escort", "Exploration"])
        type_layout.addWidget(self.quest_type_combo)
        layout.addLayout(type_layout)

        # Map/Platform
        map_layout = QHBoxLayout()
        map_layout.addWidget(QLabel("Map/Platform:"))
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["P7", "P8", "P9", "P10", "P11", "P12", "P13", "P14", "P15", "P16", "P17", "P18", "P19", "P20", "Custom"])
        type_layout.addWidget(self.platform_combo)
        layout.addLayout(map_layout)

        layout.addStretch()
        return tab

    def create_objectives_tab(self) -> QWidget:
        """Create the objectives tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Objective list
        obj_layout = QVBoxLayout()
        obj_layout.addWidget(QLabel("Quest Objectives:"))
        self.objectives_list = QListWidget()
        obj_layout.addWidget(self.objectives_list)
        layout.addLayout(obj_layout)

        # Add objective input
        add_obj_layout = QHBoxLayout()
        self.objective_input = QLineEdit()
        self.objective_input.setPlaceholderText("Enter a quest objective (e.g., Find the Lost Sword, Defeat 5 enemies)")
        add_obj_layout.addWidget(self.objective_input)

        self.add_objective_btn = QPushButton("Add Objective")
        add_obj_layout.addWidget(self.add_objective_btn)
        layout.addLayout(add_obj_layout)

        # Remove objective button
        remove_obj_layout = QHBoxLayout()
        remove_obj_layout.addStretch()
        self.remove_objective_btn = QPushButton("Remove Selected")
        remove_obj_layout.addWidget(self.remove_objective_btn)
        layout.addLayout(remove_obj_layout)

        layout.addStretch()
        return tab

    def create_rewards_tab(self) -> QWidget:
        """Create the rewards tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # XP Reward
        xp_layout = QHBoxLayout()
        xp_layout.addWidget(QLabel("XP Reward:"))
        self.xp_reward_edit = QLineEdit()
        self.xp_reward_edit.setPlaceholderText("e.g., 100")
        xp_layout.addWidget(self.xp_reward_edit)
        layout.addLayout(xp_layout)

        # Item Rewards
        items_layout = QVBoxLayout()
        items_layout.addWidget(QLabel("Item Rewards (comma-separated IDs):"))
        self.item_rewards_edit = QLineEdit()
        self.item_rewards_edit.setPlaceholderText("e.g., 100, 200, 300")
        items_layout.addWidget(self.item_rewards_edit)
        layout.addLayout(items_layout)

        # Money Rewards
        money_group = QGroupBox("Money Reward")
        money_layout = QVBoxLayout(money_group)

        gold_layout = QHBoxLayout()
        gold_layout.addWidget(QLabel("Gold:"))
        self.gold_reward_edit = QLineEdit()
        self.gold_reward_edit.setPlaceholderText("e.g., 5")
        gold_layout.addWidget(self.gold_reward_edit)
        money_layout.addLayout(gold_layout)

        silver_layout = QHBoxLayout()
        silver_layout.addWidget(QLabel("Silver:"))
        self.silver_reward_edit = QLineEdit()
        self.silver_reward_edit.setPlaceholderText("e.g., 50")
        silver_layout.addWidget(self.silver_reward_edit)
        money_layout.addLayout(silver_layout)

        copper_layout = QHBoxLayout()
        copper_layout.addWidget(QLabel("Copper:"))
        self.copper_reward_edit = QLineEdit()
        self.copper_reward_edit.setPlaceholderText("e.g., 100")
        copper_layout.addWidget(self.copper_reward_edit)
        money_layout.addLayout(copper_layout)

        layout.addWidget(money_group)

        layout.addStretch()
        return tab

    def create_requirements_tab(self) -> QWidget:
        """Create the requirements tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Requirements list
        req_layout = QVBoxLayout()
        req_layout.addWidget(QLabel("Quest Requirements:"))
        self.requirements_list = QListWidget()
        req_layout.addWidget(self.requirements_list)
        layout.addLayout(req_layout)

        # Requirement type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Requirement Type:"))
        self.req_type_combo = QComboBox()
        self.req_type_combo.addItems([
            "Quest State", 
            "Item Required", 
            "Player Level", 
            "Global Flag", 
            "Player Has Not Item"
        ])
        type_layout.addWidget(self.req_type_combo)
        layout.addLayout(type_layout)

        # Requirement input
        input_layout = QHBoxLayout()
        self.req_input = QLineEdit()
        self.req_input.setPlaceholderText("Enter requirement value (Quest ID, Item ID, Level, Flag name, etc.)")
        input_layout.addWidget(self.req_input)
        layout.addLayout(input_layout)

        # Add requirement button
        add_req_layout = QHBoxLayout()
        self.add_requirement_btn = QPushButton("Add Requirement")
        add_req_layout.addWidget(self.add_requirement_btn)

        self.remove_requirement_btn = QPushButton("Remove Selected")
        add_req_layout.addWidget(self.remove_requirement_btn)
        add_req_layout.addStretch()
        layout.addLayout(add_req_layout)

        layout.addStretch()
        return tab

    def create_dialog_tab(self) -> QWidget:
        """Create the dialog tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Dialog Tree
        dialog_tree_group = QGroupBox("Dialog Structure")
        dialog_tree_layout = QVBoxLayout(dialog_tree_group)

        self.dialog_tree = QTreeWidget()
        self.dialog_tree.setHeaderLabels(["Speaker", "Text", "Type"])
        self.dialog_tree.setAlternatingRowColors(True)
        self.dialog_tree.setDragEnabled(True)
        self.dialog_tree.setAcceptDrops(True)
        self.dialog_tree.setDropIndicatorShown(True)

        dialog_tree_layout.addWidget(self.dialog_tree)
        layout.addWidget(dialog_tree_group)

        # Dialog Editor
        dialog_edit_group = QGroupBox("Edit Dialog")
        dialog_edit_layout = QVBoxLayout(dialog_edit_group)

        # Speaker type
        speaker_layout = QHBoxLayout()
        speaker_layout.addWidget(QLabel("Speaker:"))
        self.speaker_combo = QComboBox()
        self.speaker_combo.addItems(["NPC", "Player"])
        speaker_layout.addWidget(self.speaker_combo)
        dialog_edit_layout.addLayout(speaker_layout)

        # Dialog text
        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel("Dialog Text:"))
        self.dialog_text_edit = QTextEdit()
        self.dialog_text_edit.setMaximumHeight(80)
        text_layout.addWidget(self.dialog_text_edit)
        dialog_edit_layout.addLayout(text_layout)

        # Add dialog buttons
        button_layout = QHBoxLayout()
        self.add_root_dialog_btn = QPushButton("Add Root Dialog")
        button_layout.addWidget(self.add_root_dialog_btn)

        self.add_child_dialog_btn = QPushButton("Add Child Dialog")
        button_layout.addWidget(self.add_child_dialog_btn)

        self.update_dialog_btn = QPushButton("Update Dialog")
        button_layout.addWidget(self.update_dialog_btn)
        dialog_edit_layout.addLayout(button_layout)

        layout.addWidget(dialog_edit_group)

        layout.addStretch()
        return tab

    def create_lua_preview_tab(self) -> QWidget:
        """Create the Lua preview tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Lua script preview
        self.lua_preview = QTextEdit()
        self.lua_preview.setReadOnly(True)
        self.lua_preview.setFont(QFont("Courier New", 10))
        layout.addWidget(self.lua_preview)

        # Copy button
        copy_layout = QHBoxLayout()
        copy_layout.addStretch()
        self.copy_lua_btn = QPushButton("Copy Lua Script")
        copy_layout.addWidget(self.copy_lua_btn)
        layout.addLayout(copy_layout)

        return tab

    def setup_connections(self):
        """Setup all signal connections"""
        # Basic info tab
        self.generate_btn.clicked.connect(self.generate_lua_script)

        # Objectives tab
        self.add_objective_btn.clicked.connect(self.add_objective)
        self.remove_objective_btn.clicked.connect(self.remove_objective)

        # Requirements tab
        self.add_requirement_btn.clicked.connect(self.add_requirement)
        self.remove_requirement_btn.clicked.connect(self.remove_requirement)

        # Dialog tab
        self.add_root_dialog_btn.clicked.connect(self.add_root_dialog)
        self.add_child_dialog_btn.clicked.connect(self.add_child_dialog)
        self.update_dialog_btn.clicked.connect(self.update_dialog_node)
        self.dialog_tree.itemClicked.connect(self.on_dialog_selected)

        # Lua preview tab
        self.copy_lua_btn.clicked.connect(self.copy_lua_script)

    def add_objective(self):
        """Add an objective to the list"""
        objective = self.objective_input.text().strip()
        if objective:
            self.objectives_list.addItem(objective)
            self.objective_input.clear()

    def remove_objective(self):
        """Remove selected objective"""
        current_row = self.objectives_list.currentRow()
        if current_row >= 0:
            self.objectives_list.takeItem(current_row)

    def add_requirement(self):
        """Add a requirement to the list"""
        req_type = self.req_type_combo.currentText()
        req_value = self.req_input.text().strip()
        
        if req_value:
            # Format the requirement based on type
            if req_type == "Quest State":
                requirement = f"QuestState{{QuestId = {req_value}, State = StateActive}}"
            elif req_type == "Item Required":
                requirement = f"PlayerHasItem{{ItemId = {req_value}}}"
            elif req_type == "Player Level":
                requirement = f"PlayerLevel{{Level = {req_value}, Relation = GreaterOrEqual}}"
            elif req_type == "Global Flag":
                requirement = f"IsGlobalFlagTrue{{Name = \"{req_value}\"}}"
            elif req_type == "Player Has Not Item":
                requirement = f"PlayerHasNotItem{{ItemId = {req_value}}}"
            else:
                requirement = f"{req_type}: {req_value}"
            
            self.requirements_list.addItem(requirement)
            self.req_input.clear()

    def remove_requirement(self):
        """Remove selected requirement"""
        current_row = self.requirements_list.currentRow()
        if current_row >= 0:
            self.requirements_list.takeItem(current_row)

    def add_root_dialog(self):
        """Add a root dialog node"""
        if not self.dialog_text_edit.toPlainText().strip():
            QMessageBox.warning(self, "Missing Text", "Please enter dialog text.")
            return

        item = QTreeWidgetItem(self.dialog_tree)
        item.setText(0, self.speaker_combo.currentText())
        item.setText(1, self.dialog_text_edit.toPlainText()[:50] + "...")
        item.setText(2, "Root")
        item.setData(0, Qt.UserRole, {
            'speaker': self.speaker_combo.currentText(),
            'text': self.dialog_text_edit.toPlainText(),
            'type': 'root'
        })

        self.dialog_text_edit.clear()

    def add_child_dialog(self):
        """Add a child dialog node to selected item"""
        selected_item = self.dialog_tree.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select a dialog to add a child to.")
            return

        if not self.dialog_text_edit.toPlainText().strip():
            QMessageBox.warning(self, "Missing Text", "Please enter dialog text.")
            return

        item = QTreeWidgetItem(selected_item)
        item.setText(0, self.speaker_combo.currentText())
        item.setText(1, self.dialog_text_edit.toPlainText()[:50] + "...")
        item.setText(2, "Child")
        item.setData(0, Qt.UserRole, {
            'speaker': self.speaker_combo.currentText(),
            'text': self.dialog_text_edit.toPlainText(),
            'type': 'child'
        })

        selected_item.setExpanded(True)
        self.dialog_text_edit.clear()

    def update_dialog_node(self):
        """Update the selected dialog node"""
        selected_item = self.dialog_tree.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No Selection", "Please select a dialog to update.")
            return

        if not self.dialog_text_edit.toPlainText().strip():
            QMessageBox.warning(self, "Missing Text", "Please enter dialog text.")
            return

        selected_item.setText(0, self.speaker_combo.currentText())
        selected_item.setText(1, self.dialog_text_edit.toPlainText()[:50] + "...")
        selected_item.setData(0, Qt.UserRole, {
            'speaker': self.speaker_combo.currentText(),
            'text': self.dialog_text_edit.toPlainText(),
            'type': selected_item.text(2)
        })

    def on_dialog_selected(self, item, column):
        """Handle dialog selection"""
        data = item.data(0, Qt.UserRole)
        if data:
            self.speaker_combo.setCurrentText(data['speaker'])
            self.dialog_text_edit.setPlainText(data['text'])

    def copy_lua_script(self):
        """Copy the Lua script to clipboard"""
        script = self.lua_preview.toPlainText()
        if script:
            clipboard = QApplication.clipboard()
            clipboard.setText(script)
            QMessageBox.information(self, "Copied", "Lua script copied to clipboard!")

    def generate_lua_script(self):
        """Generate Lua script from the form inputs"""
        try:
            # Validate required fields
            quest_id = self.quest_id_edit.text().strip()
            quest_name = self.quest_name_edit.text().strip()
            
            if not quest_id or not quest_name:
                QMessageBox.warning(self, "Missing Information", "Please enter Quest ID and Quest Name.")
                return

            # Validate quest ID is numeric
            try:
                quest_id = int(quest_id)
            except ValueError:
                QMessageBox.warning(self, "Invalid Quest ID", "Quest ID must be a number.")
                return

            # Build Lua script
            lua_script = self.build_lua_script(quest_id, quest_name)
            self.lua_preview.setPlainText(lua_script)
            
            # Emit the signal to let other components know
            self.quest_created.emit(lua_script)

            QMessageBox.information(self, "Success", "Lua script generated successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate Lua script: {str(e)}")

    def build_lua_script(self, quest_id: int, quest_name: str) -> str:
        """Build the complete Lua script"""
        # Start with the function definition
        script = f"""-- Generated Quest Script: {quest_name}
-- Quest ID: {quest_id}
-- Platform: {self.platform_combo.currentText()}

function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- Quest: {quest_name}
-- ID: {quest_id}

"""
        
        # Add quest initialization
        script += f"""-- Initialize quest when conditions are met
OnOneTimeEvent
{{
    EventName = "Init_{quest_name.replace(' ', '')}",
    Conditions = 
    {{
        -- Add prerequisites here if needed
"""
        
        # Add requirements
        for i in range(self.requirements_list.count()):
            req = self.requirements_list.item(i).text()
            script += f"        {req},\n"
        
        script += f"""    }},
    Actions = 
    {{
        -- Begin the quest
        QuestBegin{{QuestId = {quest_id}}},
        -- Add quest to journal
        Outcry{{
            NpcId = 0,  -- Player
            String = "{quest_name}: " + self.description_edit.toPlainText()[:100].replace('"', '') + "...",
            Color = ColorYellow
        }},
    }}
}}

-- Quest completion conditions
OnOneTimeEvent
{{
    EventName = "Complete_{quest_name.replace(' ', '')}",
    Conditions = 
    {{
        QuestState{{QuestId = {quest_id}, State = StateActive}},
"""
        
        # Add objectives as conditions
        for i in range(self.objectives_list.count()):
            objective = self.objectives_list.item(i).text()
            # Convert objectives to conditions if possible
            # This is a simplified conversion - in a real implementation,
            # you'd need more sophisticated parsing
            if "defeat" in objective.lower() or "kill" in objective.lower():
                # This is a kill quest - would need more info about enemies to add
                script += f"        -- Complete objective: {objective}\n"
            elif "collect" in objective.lower() or "find" in objective.lower():
                # This is a collection quest - would need item IDs
                script += f"        -- Complete objective: {objective}\n"
        
        script += f"""    }},
    Actions = 
    {{
        -- Complete the quest
        QuestSolve{{QuestId = {quest_id}}},
        -- Grant rewards
        SetRewardFlagTrue{{Name = "Quest{quest_id}Reward"}},
        -- Success message
        Outcry{{
            NpcId = 0,
            String = "Quest completed: {quest_name}!",
            Color = ColorGreen
        }},
    }}
}}

-- Define quest rewards
-- This would typically be in GdsQuestRewards.lua
-- Quest{quest_id}Reward = {{
--     XP = {{{self.xp_reward_edit.text() or 0}}},
--     Money = {{Gold = {self.gold_reward_edit.text() or 0}, Silver = {self.silver_reward_edit.text() or 0}, Copper = {self.copper_reward_edit.text() or 0}}},
--     Items = [{self.item_rewards_edit.text() or ""}]
-- }}

--------------------------------------------------------------------------
-- DIALOG SECTION
--------------------------------------------------------------------------
"""

        # Add dialog section if any dialogs exist
        if self.dialog_tree.topLevelItemCount() > 0:
            script += self.generate_dialog_section()
        
        script += "\nEndDefinition()\nend\n"
        
        return script

    def generate_dialog_section(self) -> str:
        """Generate the dialog section of the script"""
        script = "-- Dialog Section\n"
        
        # Process each top-level dialog item
        for i in range(self.dialog_tree.topLevelItemCount()):
            top_item = self.dialog_tree.topLevelItem(i)
            dialog_data = top_item.data(0, Qt.UserRole)
            
            if dialog_data['speaker'] == 'NPC':
                # This would be an OnBeginDialog
                script += f"""OnBeginDialog{{
    Conditions = {{
        -- Add conditions for when this dialog should start
    }},
    Actions = {{
        Say{{Tag = "{dialog_data['text'][:20].replace(' ', '')}001", String = "{dialog_data['text'].replace('"', '')}"}},
        Answer{{Tag = "", String = "", AnswerId = 1}},  -- Continue to next dialog
    }}
}}
"""
            elif dialog_data['speaker'] == 'Player':
                # This would be an OnAnswer
                script += f"""OnAnswer{{1;  -- Answer ID
    Conditions = {{
        -- Conditions for this answer
    }},
    Actions = {{
        Say{{Tag = "{dialog_data['text'][:20].replace(' ', '')}002", String = "{dialog_data['text'].replace('"', '')}"}},
        Answer{{Tag = "", String = "", AnswerId = 2}},  -- Continue to next dialog
    }}
}}
"""
            
            # Process child dialogs
            for j in range(top_item.childCount()):
                child_item = top_item.child(j)
                child_data = child_item.data(0, Qt.UserRole)
                
                if child_data['speaker'] == 'NPC':
                    script += f"""OnAnswer{{2;  -- Answer ID
    Conditions = {{
        -- Conditions for this response
    }},
    Actions = {{
        Say{{Tag = "{child_data['text'][:20].replace(' ', '')}003", String = "{child_data['text'].replace('"', '')}"}},
        Answer{{Tag = "", String = "", AnswerId = 3}},  -- Continue to next dialog
    }}
}}
"""
                elif child_data['speaker'] == 'Player':
                    script += f"""OnAnswer{{3;  -- Answer ID
    Conditions = {{
        -- Conditions for this answer
    }},
    Actions = {{
        Say{{Tag = "{child_data['text'][:20].replace(' ', '')}004", String = "{child_data['text'].replace('"', '')}"}},
        EndDialog{{}},  -- End dialog
    }}
}}
"""
        
        return script