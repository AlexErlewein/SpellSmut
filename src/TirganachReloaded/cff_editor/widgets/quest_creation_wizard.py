#!/usr/bin/env python3
"""
Quest Creation Wizard

A multi-step wizard for creating new quests with all necessary data.
Saves directly to GameData.cff with full CFF data model integration.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List, Any

from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QSpinBox, QComboBox, QPushButton,
    QLabel, QGroupBox, QListWidget, QListWidgetItem, QMessageBox,
    QCheckBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator

# Platform mappings (reuse from simple_quest_viewer.py)
PLATFORM_NAMES = {
    "P1": "Liannon", "P2": "Eloni", "P3": "Leafshade", "P4": "Wildland Pass",
    "P5": "Shiel", "P7": "Ice Gate", "P8": "Gol Halad", "P9": "Gate of Swords",
    "P10": "Murmuring Valley", "P11": "Fire Peak", "P12": "Iron Fields",
    "P13": "The Abyss", "P14": "Fastholme", "P15": "The Refuge",
    "P16": "Dream Shrine", "P17": "Undergound", "P18": "Gate of Justice",
    "P19": "Needle", "P20": "Whisper", "P21": "Windwall Fog", "P22": "Steel Shore",
    "P23": "The Shattered", "P24": "Magnet Stones", "P25": "Golden Fields",
    "P26": "Mor Duine", "P27": "City of Souls", "P32": "Soul Forge",
    "P33": "Tower of Souls", "P35": "City Ship"
}


class QuestIdentityPage(QWizardPage):
    """Page 1: Quest Identity - ID, name, description, type"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Quest Identity")
        self.setSubTitle("Enter basic information about the quest")

        layout = QFormLayout(self)

        # Quest ID (auto-generated, read-only)
        self.quest_id_label = QLabel()
        self.quest_id_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        layout.addRow("Quest ID:", self.quest_id_label)

        # Quest name (required)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter quest name (e.g., 'The Lost Artifact')")
        self.name_edit.textChanged.connect(self.completeChanged)
        layout.addRow("Quest Name*:", self.name_edit)

        # Quest description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter quest description...")
        self.description_edit.setMaximumHeight(100)
        layout.addRow("Description:", self.description_edit)

        # Quest type
        self.type_group = QButtonGroup(self)
        type_layout = QHBoxLayout()

        self.main_quest_radio = QRadioButton("Main Quest")
        self.main_quest_radio.setChecked(True)
        self.side_quest_radio = QRadioButton("Side Quest")
        self.sub_quest_radio = QRadioButton("Sub-Quest")

        self.type_group.addButton(self.main_quest_radio, 0)
        self.type_group.addButton(self.side_quest_radio, 1)
        self.type_group.addButton(self.sub_quest_radio, 2)

        type_layout.addWidget(self.main_quest_radio)
        type_layout.addWidget(self.side_quest_radio)
        type_layout.addWidget(self.sub_quest_radio)
        type_layout.addStretch()

        layout.addRow("Quest Type:", type_layout)

        # Register fields
        self.registerField("questName*", self.name_edit)
        self.registerField("questDescription", self.description_edit, "plainText")

    def initializePage(self):
        """Initialize with auto-generated quest ID"""
        wizard = self.wizard()
        if hasattr(wizard, 'next_quest_id'):
            self.quest_id_label.setText(str(wizard.next_quest_id))

    def isComplete(self):
        """Validate that name is not empty"""
        return bool(self.name_edit.text().strip())


class QuestHierarchyPage(QWizardPage):
    """Page 2: Quest Hierarchy - parent quest, order index"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Quest Hierarchy")
        self.setSubTitle("Set parent quest and order for sub-quests")

        layout = QFormLayout(self)

        # Parent quest selector
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("None (Main Quest)", 0)
        layout.addRow("Parent Quest:", self.parent_combo)

        # Order index (for sub-quests)
        self.order_spin = QSpinBox()
        self.order_spin.setMinimum(0)
        self.order_spin.setMaximum(99)
        self.order_spin.setValue(0)
        self.order_spin.setToolTip("Display order among sibling sub-quests (0 = first)")
        layout.addRow("Order Index:", self.order_spin)

        # Info label
        info_label = QLabel("💡 Main quests have no parent. Sub-quests must have a parent quest.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic; margin-top: 10px;")
        layout.addRow(info_label)

    def initializePage(self):
        """Populate parent quest combo with existing quests"""
        wizard = self.wizard()

        # Clear existing items except "None"
        while self.parent_combo.count() > 1:
            self.parent_combo.removeItem(1)

        # Add available parent quests from wizard's quest_data
        if hasattr(wizard, 'quest_data') and wizard.quest_data:
            for quest_id, quest_info in sorted(wizard.quest_data.items()):
                name = quest_info.get('name', f'Quest {quest_id}')
                self.parent_combo.addItem(f"{name} [{quest_id}]", quest_id)


class QuestLocationPage(QWizardPage):
    """Page 3: Location & NPC - platform, quest giver"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Location & Quest Giver")
        self.setSubTitle("Specify where the quest takes place and who gives it")

        layout = QFormLayout(self)

        # Platform selector
        self.platform_combo = QComboBox()
        self.platform_combo.addItem("Select Location...", "")
        for pid in sorted(PLATFORM_NAMES.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 999):
            name = PLATFORM_NAMES[pid]
            self.platform_combo.addItem(f"{name} ({pid})", pid)
        layout.addRow("Location*:", self.platform_combo)

        # Quest giver NPC ID
        self.npc_id_edit = QLineEdit()
        self.npc_id_edit.setPlaceholderText("Enter NPC ID (e.g., 100)")
        self.npc_id_edit.setValidator(QIntValidator(0, 99999))
        layout.addRow("Quest Giver (NPC ID):", self.npc_id_edit)

        # Register fields
        self.registerField("platform*", self.platform_combo, "currentData")
        self.registerField("npcId", self.npc_id_edit)

    def isComplete(self):
        """Validate that platform is selected"""
        return bool(self.platform_combo.currentData())


class QuestObjectivesPage(QWizardPage):
    """Page 4: Objectives & Requirements"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Objectives & Requirements")
        self.setSubTitle("Define what the player needs to do and any prerequisites")

        layout = QVBoxLayout(self)

        # Objectives section
        objectives_group = QGroupBox("Objectives")
        objectives_layout = QVBoxLayout(objectives_group)

        self.objectives_list = QListWidget()
        objectives_layout.addWidget(self.objectives_list)

        objectives_btn_layout = QHBoxLayout()
        add_obj_btn = QPushButton("Add Objective")
        add_obj_btn.clicked.connect(self.add_objective)
        remove_obj_btn = QPushButton("Remove Selected")
        remove_obj_btn.clicked.connect(self.remove_objective)
        objectives_btn_layout.addWidget(add_obj_btn)
        objectives_btn_layout.addWidget(remove_obj_btn)
        objectives_btn_layout.addStretch()
        objectives_layout.addLayout(objectives_btn_layout)

        layout.addWidget(objectives_group)

        # Requirements section
        requirements_group = QGroupBox("Requirements")
        requirements_layout = QVBoxLayout(requirements_group)

        self.requirements_list = QListWidget()
        requirements_layout.addWidget(self.requirements_list)

        requirements_btn_layout = QHBoxLayout()
        add_req_btn = QPushButton("Add Requirement")
        add_req_btn.clicked.connect(self.add_requirement)
        remove_req_btn = QPushButton("Remove Selected")
        remove_req_btn.clicked.connect(self.remove_requirement)
        requirements_btn_layout.addWidget(add_req_btn)
        requirements_btn_layout.addWidget(remove_req_btn)
        requirements_btn_layout.addStretch()
        requirements_layout.addLayout(requirements_btn_layout)

        layout.addWidget(requirements_group)

    def add_objective(self):
        """Add a new objective"""
        from PySide6.QtWidgets import QInputDialog

        # Get objective type
        types = ["talk", "kill", "gather", "explore", "escort", "other"]
        obj_type, ok = QInputDialog.getItem(self, "Objective Type", "Select objective type:", types, 0, False)
        if not ok:
            return

        # Get objective text
        obj_text, ok = QInputDialog.getText(self, "Objective Text", "Enter objective description:")
        if not ok or not obj_text.strip():
            return

        # Add to list
        item = QListWidgetItem(f"[{obj_type}] {obj_text}")
        item.setData(Qt.UserRole, {'type': obj_type, 'text': obj_text})
        self.objectives_list.addItem(item)

    def remove_objective(self):
        """Remove selected objective"""
        current_row = self.objectives_list.currentRow()
        if current_row >= 0:
            self.objectives_list.takeItem(current_row)

    def add_requirement(self):
        """Add a new requirement"""
        from PySide6.QtWidgets import QInputDialog

        # Get requirement type
        types = ["quest", "level", "item", "flag", "other"]
        req_type, ok = QInputDialog.getItem(self, "Requirement Type", "Select requirement type:", types, 0, False)
        if not ok:
            return

        # Get requirement text
        req_text, ok = QInputDialog.getText(self, "Requirement Text", "Enter requirement description:")
        if not ok or not req_text.strip():
            return

        # Add to list
        item = QListWidgetItem(f"[{req_type}] {req_text}")
        item.setData(Qt.UserRole, {'type': req_type, 'text': req_text})
        self.requirements_list.addItem(item)

    def remove_requirement(self):
        """Remove selected requirement"""
        current_row = self.requirements_list.currentRow()
        if current_row >= 0:
            self.requirements_list.takeItem(current_row)


class QuestRewardsPage(QWizardPage):
    """Page 5: Rewards & Dialogues"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Rewards & Dialogues")
        self.setSubTitle("Define quest rewards and dialogue options")

        layout = QVBoxLayout(self)

        # Rewards section
        rewards_group = QGroupBox("Rewards")
        rewards_layout = QFormLayout(rewards_group)

        self.xp_spin = QSpinBox()
        self.xp_spin.setMaximum(999999)
        self.xp_spin.setValue(0)
        rewards_layout.addRow("XP:", self.xp_spin)

        self.gold_spin = QSpinBox()
        self.gold_spin.setMaximum(999999)
        self.gold_spin.setValue(0)
        rewards_layout.addRow("Gold:", self.gold_spin)

        self.silver_spin = QSpinBox()
        self.silver_spin.setMaximum(99)
        self.silver_spin.setValue(0)
        rewards_layout.addRow("Silver:", self.silver_spin)

        self.copper_spin = QSpinBox()
        self.copper_spin.setMaximum(99)
        self.copper_spin.setValue(0)
        rewards_layout.addRow("Copper:", self.copper_spin)

        self.items_edit = QLineEdit()
        self.items_edit.setPlaceholderText("Item IDs separated by commas (e.g., 101, 102, 103)")
        rewards_layout.addRow("Items:", self.items_edit)

        layout.addWidget(rewards_group)

        # Dialogues section
        dialogues_group = QGroupBox("Dialogues")
        dialogues_layout = QVBoxLayout(dialogues_group)

        self.dialogues_list = QListWidget()
        dialogues_layout.addWidget(self.dialogues_list)

        dialogues_btn_layout = QHBoxLayout()
        add_dlg_btn = QPushButton("Add Dialogue")
        add_dlg_btn.clicked.connect(self.add_dialogue)
        remove_dlg_btn = QPushButton("Remove Selected")
        remove_dlg_btn.clicked.connect(self.remove_dialogue)
        dialogues_btn_layout.addWidget(add_dlg_btn)
        dialogues_btn_layout.addWidget(remove_dlg_btn)
        dialogues_btn_layout.addStretch()
        dialogues_layout.addLayout(dialogues_btn_layout)

        layout.addWidget(dialogues_group)

    def add_dialogue(self):
        """Add a new dialogue"""
        from PySide6.QtWidgets import QInputDialog, QDialog, QDialogButtonBox

        # Create custom dialog for dialogue input
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Dialogue")
        dialog_layout = QVBoxLayout(dialog)

        # Speaker selection
        speaker_layout = QHBoxLayout()
        speaker_layout.addWidget(QLabel("Speaker:"))
        speaker_combo = QComboBox()
        speaker_combo.addItems(["NPC", "Player"])
        speaker_layout.addWidget(speaker_combo)
        speaker_layout.addStretch()
        dialog_layout.addLayout(speaker_layout)

        # Text input
        dialog_layout.addWidget(QLabel("Text:"))
        text_edit = QTextEdit()
        text_edit.setMaximumHeight(80)
        dialog_layout.addWidget(text_edit)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)

        if dialog.exec() != QDialog.Accepted:
            return

        speaker = speaker_combo.currentText()
        text = text_edit.toPlainText().strip()
        if not text:
            return

        # Add to list
        item = QListWidgetItem(f"[{speaker}] {text[:50]}{'...' if len(text) > 50 else ''}")
        item.setData(Qt.UserRole, {'speaker': speaker, 'text': text, 'is_player': speaker == 'Player'})
        self.dialogues_list.addItem(item)

    def remove_dialogue(self):
        """Remove selected dialogue"""
        current_row = self.dialogues_list.currentRow()
        if current_row >= 0:
            self.dialogues_list.takeItem(current_row)


class QuestCreationWizard(QWizard):
    """Main Quest Creation Wizard"""

    quest_created = Signal(dict)  # Emitted when quest is successfully created

    def __init__(self, data_model, quest_data, parent=None):
        super().__init__(parent)

        self.data_model = data_model
        self.quest_data = quest_data  # Reference to existing quests
        self.next_quest_id = self._generate_quest_id()

        self.setWindowTitle("Quest Creation Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.HaveHelpButton, False)
        self.setMinimumSize(700, 500)

        # Add pages
        self.identity_page = QuestIdentityPage()
        self.hierarchy_page = QuestHierarchyPage()
        self.location_page = QuestLocationPage()
        self.objectives_page = QuestObjectivesPage()
        self.rewards_page = QuestRewardsPage()

        self.addPage(self.identity_page)
        self.addPage(self.hierarchy_page)
        self.addPage(self.location_page)
        self.addPage(self.objectives_page)
        self.addPage(self.rewards_page)

        # Connect finish button
        self.button(QWizard.FinishButton).clicked.connect(self.create_quest)

    def _generate_quest_id(self):
        """Generate next available quest ID in custom range (9000-9999)"""
        # Find highest existing custom quest ID
        custom_ids = [qid for qid in self.quest_data.keys() if 9000 <= qid <= 9999]
        if custom_ids:
            return max(custom_ids) + 1
        return 9000

    def create_quest(self):
        """Create the quest from wizard data"""
        try:
            # Collect data from all pages
            quest_data = {
                'quest_id': self.next_quest_id,
                'name': self.field("questName"),
                'description': self.field("questDescription") or "",
                'parent_id': self.hierarchy_page.parent_combo.currentData() or 0,
                'order_index': self.hierarchy_page.order_spin.value(),
                'platform': self.field("platform"),
                'npc_id': int(self.field("npcId")) if self.field("npcId") else 0,
            }

            # Collect objectives
            objectives = []
            for i in range(self.objectives_page.objectives_list.count()):
                item = self.objectives_page.objectives_list.item(i)
                objectives.append(item.data(Qt.UserRole))
            quest_data['objectives'] = objectives

            # Collect requirements
            requirements = []
            for i in range(self.objectives_page.requirements_list.count()):
                item = self.objectives_page.requirements_list.item(i)
                requirements.append(item.data(Qt.UserRole))
            quest_data['requirements'] = requirements

            # Collect rewards
            quest_data['rewards'] = {
                'xp': self.rewards_page.xp_spin.value(),
                'gold': self.rewards_page.gold_spin.value(),
                'silver': self.rewards_page.silver_spin.value(),
                'copper': self.rewards_page.copper_spin.value(),
                'items': []
            }

            # Parse items
            items_text = self.rewards_page.items_edit.text().strip()
            if items_text:
                try:
                    items = [int(item.strip()) for item in items_text.split(',') if item.strip()]
                    quest_data['rewards']['items'] = items
                except ValueError:
                    QMessageBox.warning(self, "Invalid Items", "Item IDs must be numbers separated by commas")
                    return

            # Collect dialogues
            dialogues = []
            for i in range(self.rewards_page.dialogues_list.count()):
                item = self.rewards_page.dialogues_list.item(i)
                dialogues.append(item.data(Qt.UserRole))
            quest_data['dialogues'] = dialogues

            # Emit signal with quest data
            self.quest_created.emit(quest_data)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create quest:\n{e}")


# Example usage
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Mock data for testing
    mock_data_model = None
    mock_quest_data = {
        1: {'name': 'Staub der Sterne', 'description': '...'},
        12: {'name': 'Darius der Kartograph', 'description': '...'},
    }

    wizard = QuestCreationWizard(mock_data_model, mock_quest_data)
    wizard.quest_created.connect(lambda data: print(f"Quest created: {data}"))
    wizard.show()

    sys.exit(app.exec())
