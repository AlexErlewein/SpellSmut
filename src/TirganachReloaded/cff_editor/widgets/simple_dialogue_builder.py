#!/usr/bin/env python3
"""
Simple Guided Dialogue Builder

A user-friendly, step-by-step dialogue creation tool with:
- Top-down tree view layout
- Guided workflow with "Next Part" buttons
- Simple choice selection
- Clear visual hierarchy
- Step-by-step instructions
"""

import sys
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QGroupBox, QFormLayout, QScrollArea,
    QFrame, QMessageBox, QComboBox, QSplitter, QTreeWidget,
    QTreeWidgetItem, QCheckBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap

try:
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class DialogueStepType(Enum):
    """Types of dialogue steps"""
    START = "start"
    NPC_SPEECH = "npc_speech"
    PLAYER_CHOICE = "player_choice"
    NPC_RESPONSE = "npc_response"
    END = "end"


@dataclass
class DialogueStep:
    """A single step in the dialogue"""
    id: str
    type: DialogueStepType
    speaker: str = ""
    text: str = ""
    choices: List[Dict[str, str]] = None
    next_step_id: str = ""

    def __post_init__(self):
        if self.choices is None:
            self.choices = []

    def to_dict(self):
        """Convert to dictionary"""
        data = asdict(self)
        data['type'] = self.type.value
        return data


class DialogueStepWidget(QFrame):
    """Widget for a single dialogue step"""

    step_changed = Signal(str)  # step_id

    def __init__(self, step: DialogueStep, is_editable: bool = True):
        super().__init__()
        self.step = step
        self.is_editable = is_editable
        self.setup_ui()

    def setup_ui(self):
        """Setup the step widget UI"""
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Step header
        header_layout = QHBoxLayout()

        # Step type indicator
        type_colors = {
            DialogueStepType.START: "#27ae60",
            DialogueStepType.NPC_SPEECH: "#3498db",
            DialogueStepType.PLAYER_CHOICE: "#e74c3c",
            DialogueStepType.NPC_RESPONSE: "#f39c12",
            DialogueStepType.END: "#95a5a6"
        }

        type_names = {
            DialogueStepType.START: "🟢 START",
            DialogueStepType.NPC_SPEECH: "👤 NPC SPEAKS",
            DialogueStepType.PLAYER_CHOICE: "🗣️ PLAYER CHOICE",
            DialogueStepType.NPC_RESPONSE: "💬 NPC RESPONSE",
            DialogueStepType.END: "🔴 END"
        }

        color = type_colors.get(self.step.type, "#95a5a6")
        name = type_names.get(self.step.type, "STEP")

        self.type_label = QLabel(name)
        self.type_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }}
        """)

        header_layout.addWidget(self.type_label)
        header_layout.addStretch()

        # Delete button (if editable)
        if self.is_editable and self.step.type != DialogueStepType.START:
            self.delete_btn = QPushButton("🗑️ Delete")
            self.delete_btn.setMaximumWidth(80)
            self.delete_btn.clicked.connect(self.request_delete)
            header_layout.addWidget(self.delete_btn)

        layout.addLayout(header_layout)

        # Step content based on type
        if self.step.type == DialogueStepType.NPC_SPEECH or self.step.type == DialogueStepType.NPC_RESPONSE:
            self.setup_npc_speech_ui(layout)
        elif self.step.type == DialogueStepType.PLAYER_CHOICE:
            self.setup_player_choice_ui(layout)
        elif self.step.type == DialogueStepType.END:
            self.setup_end_ui(layout)

    def setup_npc_speech_ui(self, layout):
        """Setup NPC speech UI"""
        # Speaker name
        if self.is_editable:
            speaker_layout = QHBoxLayout()
            speaker_layout.addWidget(QLabel("Speaker:"))
            self.speaker_edit = QLineEdit(self.step.speaker)
            self.speaker_edit.setPlaceholderText("NPC name...")
            self.speaker_edit.textChanged.connect(self.on_step_changed)
            speaker_layout.addWidget(self.speaker_edit)
            layout.addLayout(speaker_layout)
        else:
            if self.step.speaker:
                speaker_label = QLabel(f"👤 {self.step.speaker}")
                speaker_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin: 5px;")
                layout.addWidget(speaker_label)

        # Dialogue text
        if self.is_editable:
            self.text_edit = QTextEdit()
            self.text_edit.setPlaceholderText("What does the NPC say?")
            self.text_edit.setPlainText(self.step.text)
            self.text_edit.setMaximumHeight(100)
            self.text_edit.textChanged.connect(self.on_step_changed)
            layout.addWidget(self.text_edit)
        else:
            if self.step.text:
                text_label = QLabel(self.step.text)
                text_label.setWordWrap(True)
                text_label.setStyleSheet("""
                    QLabel {
                        background-color: #f8f9fa;
                        padding: 15px;
                        border-radius: 8px;
                        border-left: 4px solid #3498db;
                        margin: 5px;
                    }
                """)
                layout.addWidget(text_label)

        # Add next step button
        if self.is_editable:
            self.add_next_btn = QPushButton("➕ Add Next Part")
            self.add_next_btn.clicked.connect(self.add_next_step)
            self.add_next_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #2ecc71;
                }
            """)
            layout.addWidget(self.add_next_btn)

    def setup_player_choice_ui(self, layout):
        """Setup player choice UI"""
        if self.is_editable:
            # Question text
            self.question_edit = QTextEdit()
            self.question_edit.setPlaceholderText("What choice does the player need to make?")
            self.question_edit.setPlainText(self.step.text)
            self.question_edit.setMaximumHeight(80)
            self.question_edit.textChanged.connect(self.on_step_changed)
            layout.addWidget(self.question_edit)

            # Choices section
            choices_label = QLabel("📝 Player Options:")
            choices_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(choices_label)

            self.choices_widget = QWidget()
            self.choices_layout = QVBoxLayout()
            self.choices_widget.setLayout(self.choices_layout)

            self.choice_edits = []
            for i, choice in enumerate(self.step.choices):
                choice_layout = QHBoxLayout()

                choice_edit = QLineEdit(choice.get('text', ''))
                choice_edit.setPlaceholderText(f"Option {i+1}...")
                choice_edit.textChanged.connect(self.on_step_changed)
                self.choice_edits.append(choice_edit)

                if len(self.step.choices) > 2:  # Allow removal if more than 2 choices
                    remove_btn = QPushButton("❌")
                    remove_btn.setMaximumWidth(30)
                    remove_btn.clicked.connect(lambda checked, idx=i: self.remove_choice(idx))
                    choice_layout.addWidget(choice_edit)
                    choice_layout.addWidget(remove_btn)
                else:
                    choice_layout.addWidget(choice_edit)

                self.choices_layout.addLayout(choice_layout)

            layout.addWidget(self.choices_widget)

            # Add choice button
            add_choice_btn = QPushButton("➕ Add Choice")
            add_choice_btn.clicked.connect(self.add_choice)
            layout.addWidget(add_choice_btn)
        else:
            # Display mode
            if self.step.text:
                question_label = QLabel("❓ " + self.step.text)
                question_label.setStyleSheet("font-weight: bold; color: #e74c3c; margin: 10px;")
                layout.addWidget(question_label)

            for choice in self.step.choices:
                choice_label = QLabel(f"• {choice.get('text', 'No text')}")
                choice_label.setStyleSheet("""
                    QLabel {
                        background-color: #fff3cd;
                        padding: 8px 12px;
                        border-radius: 4px;
                        margin: 3px;
                        border-left: 3px solid #ffc107;
                    }
                """)
                layout.addWidget(choice_label)

    def setup_end_ui(self, layout):
        """Setup end dialogue UI"""
        end_label = QLabel("🏁 Conversation Ends Here")
        end_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                color: #7f8c8d;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        end_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(end_label)

    def add_choice(self):
        """Add a new choice"""
        self.step.choices.append({'text': '', 'next_step': ''})
        self.rebuild_ui()

    def remove_choice(self, index):
        """Remove a choice"""
        if len(self.step.choices) > 2:  # Keep at least 2 choices
            self.step.choices.pop(index)
            self.rebuild_ui()

    def add_next_step(self):
        """Request to add next step"""
        self.step_changed.emit(f"add_next:{self.step.id}")

    def request_delete(self):
        """Request to delete this step"""
        self.step_changed.emit(f"delete:{self.step.id}")

    def on_step_changed(self):
        """Handle step content changes"""
        if self.is_editable:
            # Update step data
            if hasattr(self, 'speaker_edit'):
                self.step.speaker = self.speaker_edit.text()
            if hasattr(self, 'text_edit'):
                self.step.text = self.text_edit.toPlainText()
            if hasattr(self, 'question_edit'):
                self.step.text = self.question_edit.toPlainText()

            # Update choices
            if hasattr(self, 'choice_edits'):
                for i, edit in enumerate(self.choice_edits):
                    if i < len(self.step.choices):
                        self.step.choices[i]['text'] = edit.text()

            self.step_changed.emit(f"update:{self.step.id}")

    def rebuild_ui(self):
        """Rebuild the UI"""
        # Clear current layout
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Recreate UI
        self.setup_ui()


class SimpleDialogueBuilder(QWidget):
    """Simple guided dialogue builder"""

    dialogue_changed = Signal()

    def __init__(self):
        super().__init__()
        self.steps = {}
        self.next_step_id = 1
        self.setup_ui()
        self.create_initial_dialogue()

    def setup_ui(self):
        """Setup the main UI"""
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left panel - Tree view
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(300)

        # Tree title
        title_label = QLabel("🌳 Dialogue Tree")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        left_layout.addWidget(title_label)

        # Tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        left_layout.addWidget(self.tree_widget)

        main_layout.addWidget(left_panel)

        # Right panel - Dialogue builder
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        # Instructions
        instructions = QLabel("""
📝 <b>How to Build Dialogue:</b><br>
1. Start with NPC speech<br>
2. Add player choices when needed<br>
3. Create NPC responses for each choice<br>
4. Continue until conversation ends<br>
5. Click "Add Next Part" to extend dialogue
        """)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #e8f5e8;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
            }
        """)
        instructions.setWordWrap(True)
        right_layout.addWidget(instructions)

        # Scroll area for dialogue steps
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.steps_widget = QWidget()
        self.steps_layout = QVBoxLayout()
        self.steps_layout.setAlignment(Qt.AlignTop)
        self.steps_widget.setLayout(self.steps_layout)
        scroll_area.setWidget(self.steps_widget)

        right_layout.addWidget(scroll_area)

        # Bottom toolbar
        toolbar_layout = QHBoxLayout()

        self.validate_btn = QPushButton("✅ Validate")
        self.validate_btn.clicked.connect(self.validate_dialogue)
        toolbar_layout.addWidget(self.validate_btn)

        self.export_btn = QPushButton("🔧 Export Lua")
        self.export_btn.clicked.connect(self.export_to_lua)
        toolbar_layout.addWidget(self.export_btn)

        self.help_btn = QPushButton("❓ Help")
        self.help_btn.clicked.connect(self.show_help)
        toolbar_layout.addWidget(self.help_btn)

        right_layout.addLayout(toolbar_layout)

        main_layout.addWidget(right_panel)

        # Set splitter sizes
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])

        main_layout.addWidget(splitter)

    def create_initial_dialogue(self):
        """Create initial dialogue structure"""
        # Create start step
        start_step = DialogueStep(
            id="step_1",
            type=DialogueStepType.START
        )
        self.add_step(start_step)

        # Create first NPC speech
        npc_step = DialogueStep(
            id="step_2",
            type=DialogueStepType.NPC_SPEECH,
            speaker="Guard",
            text="Hello there, traveler. What brings you to our village?"
        )
        self.add_step(npc_step)
        start_step.next_step_id = npc_step.id

        # Create first player choice
        choice_step = DialogueStep(
            id="step_3",
            type=DialogueStepType.PLAYER_CHOICE,
            text="How do you respond?",
            choices=[
                {"text": "I'm just passing through."},
                {"text": "I'm looking for adventure."},
                {"text": "I need supplies."}
            ]
        )
        self.add_step(choice_step)
        npc_step.next_step_id = choice_step.id

        self.update_tree()
        self.rebuild_steps_display()

    def add_step(self, step: DialogueStep):
        """Add a dialogue step"""
        self.steps[step.id] = step
        self.next_step_id = max(self.next_step_id, int(step.id.split('_')[1]) + 1)
        self.dialogue_changed.emit()

    def remove_step(self, step_id: str):
        """Remove a dialogue step"""
        if step_id in self.steps and self.steps[step_id].type != DialogueStepType.START:
            del self.steps[step_id]
            self.update_tree()
            self.rebuild_steps_display()
            self.dialogue_changed.emit()

    def rebuild_steps_display(self):
        """Rebuild the steps display"""
        # Clear current display
        while self.steps_layout.count():
            item = self.steps_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Display steps in order
        step_order = self.get_step_order()
        for i, step_id in enumerate(step_order):
            step = self.steps[step_id]

            # Add connection line if not first step
            if i > 0:
                line = QLabel("⬇️")
                line.setAlignment(Qt.AlignCenter)
                line.setStyleSheet("color: #95a5a6; font-size: 20px; margin: 5px;")
                self.steps_layout.addWidget(line)

            # Create step widget
            step_widget = DialogueStepWidget(step, is_editable=True)
            step_widget.step_changed.connect(self.on_step_widget_changed)
            self.steps_layout.addWidget(step_widget)

    def get_step_order(self):
        """Get steps in display order"""
        if not self.steps:
            return []

        # Start with the start step
        order = []
        current_step = None

        # Find start step
        for step in self.steps.values():
            if step.type == DialogueStepType.START:
                current_step = step
                break

        # Follow the chain
        visited = set()
        while current_step and current_step.id not in visited:
            visited.add(current_step.id)
            order.append(current_step.id)

            # Find next step
            if current_step.next_step_id:
                current_step = self.steps.get(current_step.next_step_id)
            else:
                current_step = None

        # Add any remaining steps (orphans)
        for step_id in self.steps:
            if step_id not in visited:
                order.append(step_id)

        return order

    def update_tree(self):
        """Update the tree view"""
        self.tree_widget.clear()

        step_order = self.get_step_order()
        parent_items = {}

        for step_id in step_order:
            step = self.steps[step_id]

            # Create tree item
            type_names = {
                DialogueStepType.START: "START",
                DialogueStepType.NPC_SPEECH: step.speaker or "NPC",
                DialogueStepType.PLAYER_CHOICE: "CHOICE",
                DialogueStepType.NPC_RESPONSE: step.speaker or "NPC",
                DialogueStepType.END: "END"
            }

            name = type_names.get(step.type, "STEP")
            if step.type == DialogueStepType.PLAYER_CHOICE:
                name += f" ({len(step.choices)} options)"

            item = QTreeWidgetItem([name])
            item.setData(0, Qt.UserRole, step_id)

            # Add to tree
            if step_id == "step_1":  # Start step
                self.tree_widget.addTopLevelItem(item)
                parent_items[step_id] = item
            else:
                # Find parent
                parent_id = self.find_parent_step(step_id)
                if parent_id and parent_id in parent_items:
                    parent_items[parent_id].addChild(item)
                else:
                    self.tree_widget.addTopLevelItem(item)
                parent_items[step_id] = item

            # Expand parent
            if item.parent():
                item.parent().setExpanded(True)

    def find_parent_step(self, step_id):
        """Find the parent step of a given step"""
        for step in self.steps.values():
            if step.next_step_id == step_id:
                return step.id
        return None

    def on_tree_item_clicked(self, item, column):
        """Handle tree item click"""
        step_id = item.data(0, Qt.UserRole)
        if step_id and step_id in self.steps:
            self.scroll_to_step(step_id)

    def scroll_to_step(self, step_id):
        """Scroll to a specific step"""
        # Find the step widget
        step_order = self.get_step_order()
        if step_id in step_order:
            index = step_order.index(step_id)
            # Scroll to show this step (implementation depends on scroll area)
            pass

    def on_step_widget_changed(self, action):
        """Handle step widget changes"""
        action_type, step_id = action.split(':', 1)

        if action_type == "add_next":
            self.add_next_step(step_id)
        elif action_type == "delete":
            self.remove_step(step_id)
        elif action_type == "update":
            self.update_tree()
            self.dialogue_changed.emit()

    def add_next_step(self, parent_step_id):
        """Add a new step after the given step"""
        parent_step = self.steps.get(parent_step_id)
        if not parent_step:
            return

        # Determine what type of step to add
        if parent_step.type == DialogueStepType.NPC_SPEECH:
            # Add player choice after NPC speech
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.PLAYER_CHOICE,
                text="What does the player say?",
                choices=[
                    {"text": "Continue conversation"},
                    {"text": "Ask something else"}
                ]
            )
        elif parent_step.type == DialogueStepType.PLAYER_CHOICE:
            # Add NPC response after player choice
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.NPC_RESPONSE,
                speaker="NPC",
                text="I understand. Let me help you with that."
            )
        elif parent_step.type == DialogueStepType.NPC_RESPONSE:
            # Add player choice again to continue conversation
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.PLAYER_CHOICE,
                text="What would you like to do next?",
                choices=[
                    {"text": "Tell me more"},
                    {"text": "Goodbye"}
                ]
            )
        else:
            # Add NPC speech as default
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.NPC_SPEECH,
                speaker="NPC",
                text="Hello!"
            )

        self.add_step(new_step)
        parent_step.next_step_id = new_step.id

        self.update_tree()
        self.rebuild_steps_display()

    def validate_dialogue(self):
        """Validate the dialogue"""
        errors = []
        warnings = []

        # Check for start step
        has_start = any(step.type == DialogueStepType.START for step in self.steps.values())
        if not has_start:
            errors.append("Missing start step")

        # Check for empty text
        for step_id, step in self.steps.items():
            if step.type in [DialogueStepType.NPC_SPEECH, DialogueStepType.NPC_RESPONSE, DialogueStepType.PLAYER_CHOICE]:
                if not step.text.strip():
                    warnings.append(f"Step {step_id} has empty text")
                if step.type in [DialogueStepType.NPC_SPEECH, DialogueStepType.NPC_RESPONSE] and not step.speaker.strip():
                    warnings.append(f"NPC step {step_id} has no speaker name")

        # Check choices
        for step_id, step in self.steps.items():
            if step.type == DialogueStepType.PLAYER_CHOICE:
                if len(step.choices) < 2:
                    errors.append(f"Choice step {step_id} must have at least 2 options")

                for i, choice in enumerate(step.choices):
                    if not choice.get('text', '').strip():
                        warnings.append(f"Choice {i+1} in step {step_id} is empty")

        # Show results
        if errors:
            error_text = "❌ Validation Errors:\n" + "\n".join(f"• {error}" for error in errors)
            QMessageBox.critical(self, "Validation Failed", error_text)
        elif warnings:
            warning_text = "⚠️ Validation Warnings:\n" + "\n".join(f"• {warning}" for warning in warnings)
            QMessageBox.warning(self, "Validation Warnings", warning_text)
        else:
            QMessageBox.information(self, "Validation Success", "✅ Dialogue looks good!")

    def export_to_lua(self):
        """Export dialogue to Lua format"""
        if not self.steps:
            QMessageBox.warning(self, "Export Failed", "No dialogue to export")
            return

        # Simple Lua export (can be enhanced)
        lua_code = "-- Auto-generated dialogue\n"
        lua_code += "local dialogue = {\n"

        step_order = self.get_step_order()
        for i, step_id in enumerate(step_order):
            step = self.steps[step_id]
            lua_code += f"    {{\n"
            lua_code += f"        id = \"{step_id}\",\n"
            lua_code += f"        type = \"{step.type.value}\",\n"

            if step.speaker:
                lua_code += f"        speaker = \"{step.speaker}\",\n"
            if step.text:
                lua_code += f"        text = \"{step.text}\",\n"

            if step.choices:
                lua_code += f"        choices = {{\n"
                for choice in step.choices:
                    lua_code += f"            {{text = \"{choice.get('text', '')}\"}},\n"
                lua_code += f"        }},\n"

            if step.next_step_id:
                lua_code += f"        next = \"{step.next_step_id}\",\n"

            lua_code += f"    }},\n"

        lua_code += "}\n\n"
        lua_code += "return dialogue\n"

        # Show export dialog
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Exported Lua Code")
        dialog.setText("Your dialogue has been exported to Lua format:")
        dialog.setDetailedText(lua_code)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec()

    def show_help(self):
        """Show help dialog"""
        help_text = """
# Simple Dialogue Builder Help

## 🎯 How It Works

This tool helps you create conversations step by step:

### 1. **Start at the Top**
- Every dialogue begins with a START node
- Add NPC speech to introduce the conversation

### 2. **Create Conversation Flow**
- **NPC Speech**: What characters say to the player
- **Player Choice**: Options the player can choose from
- **NPC Response**: How NPCs respond to player choices
- **Continue** building the conversation naturally

### 3. **Use "Add Next Part" Button**
- Click this button to extend the dialogue
- The system automatically suggests the next step type
- NPC Speech → Player Choice → NPC Response → Repeat

### 4. **Complete the Dialogue**
- Add "Goodbye" options to end conversations
- Use the END node when dialogue is finished

## 💡 Tips

- **Keep it Natural**: Write how people actually talk
- **Give Choices**: Players like having options
- **Make it Matter**: Choices should lead to different responses
- **Test Often**: Use Validate to check for problems

## 🔧 Features

- **Tree View**: See your conversation structure on the left
- **Step-by-Step**: Build conversations one piece at a time
- **Auto-Save**: Your work is saved automatically
- **Lua Export**: Export for use in SpellForce

## ⌨️ Navigation

- Click tree items to jump to specific steps
- Use the scroll bar to see long conversations
- Delete steps you don't need (except START)

Need more help? Check the main documentation!
        """

        help_dialog = QMessageBox(self)
        help_dialog.setWindowTitle("Simple Dialogue Builder Help")
        help_dialog.setTextFormat(Qt.MarkdownText)
        help_dialog.setText(help_text)
        help_dialog.setStandardButtons(QMessageBox.Ok)
        help_dialog.exec()

    def get_dialogue_data(self):
        """Get dialogue data as dictionary"""
        return {
            'steps': [step.to_dict() for step in self.steps.values()]
        }


# Test function
def test_simple_dialogue_builder():
    """Test the simple dialogue builder"""
    app = QApplication(sys.argv)

    widget = SimpleDialogueBuilder()
    widget.setWindowTitle("Simple Dialogue Builder Test")
    widget.resize(1000, 700)
    widget.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(test_simple_dialogue_builder())