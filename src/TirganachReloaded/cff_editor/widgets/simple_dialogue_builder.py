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
    QTreeWidgetItem, QCheckBox, QRadioButton, QButtonGroup,
    QDialog, QDialogButtonBox, QButtonGroup
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
    PLAYER_SPEECH = "player_speech"  # Single option player speech (looks like one option)
    NPC_RESPONSE = "npc_response"
    END = "end"


@dataclass
class DialogueStep:
    """A single step in the dialogue"""
    id: str
    type: DialogueStepType
    speaker: str = ""
    text: str = ""
    choices: List[Dict[str, str]] = None  # Each choice: {'text': 'Option text', 'next_step_id': 'target_step_id'}
    next_step_id: str = ""  # For linear flow when no branching

    def __post_init__(self):
        if self.choices is None:
            self.choices = []

    def to_dict(self):
        """Convert to dictionary"""
        data = asdict(self)
        data['type'] = self.type.value
        return data


class StepTypeSelectionDialog(QDialog):
    """Dialog for selecting the type of next step"""

    def __init__(self, current_step_type, parent=None):
        super().__init__(parent)
        self.current_step_type = current_step_type
        self.selected_type = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Choose Next Step Type")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Instructions
        instructions = QLabel("What type of step comes next in the conversation?")
        instructions.setStyleSheet("font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(instructions)

        # Step type options
        self.button_group = QButtonGroup()
        self.step_buttons = {}

        # Determine available options based on current step type
        available_types = self.get_available_step_types()

        for step_type, description in available_types.items():
            radio = QRadioButton(f"{step_type.name}: {description}")
            radio.setStyleSheet("""
                QRadioButton {
                    padding: 8px;
                    margin: 2px;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                }
            """)
            self.button_group.addButton(radio)
            self.step_buttons[step_type] = radio
            layout.addWidget(radio)

        # Select first option by default
        if self.step_buttons:
            first_radio = next(iter(self.step_buttons.values()))
            first_radio.setChecked(True)
            self.selected_type = first_radio.text().split(":")[0]

        # Connect button group
        self.button_group.buttonClicked.connect(self.on_selection_changed)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_available_step_types(self):
        """Get available step types based on current step type"""
        if self.current_step_type == DialogueStepType.START:
            return {
                DialogueStepType.NPC_SPEECH: "NPC speaks to the player"
            }
        elif self.current_step_type == DialogueStepType.NPC_SPEECH:
            return {
                DialogueStepType.PLAYER_CHOICE: "Player chooses a response",
                DialogueStepType.PLAYER_SPEECH: "Player says something (single option)",
                DialogueStepType.NPC_RESPONSE: "NPC continues speaking",
                DialogueStepType.END: "Conversation ends"
            }
        elif self.current_step_type == DialogueStepType.PLAYER_CHOICE:
            return {
                DialogueStepType.NPC_RESPONSE: "NPC responds to player choice",
                DialogueStepType.NPC_SPEECH: "Different NPC speaks",
                DialogueStepType.END: "Conversation ends"
            }
        elif self.current_step_type == DialogueStepType.NPC_RESPONSE:
            return {
                DialogueStepType.PLAYER_CHOICE: "Player chooses next action",
                DialogueStepType.NPC_SPEECH: "Same NPC continues",
                DialogueStepType.NPC_RESPONSE: "Same NPC responds again",
                DialogueStepType.END: "Conversation ends"
            }
        else:
            return {
                DialogueStepType.NPC_SPEECH: "NPC speaks",
                DialogueStepType.PLAYER_CHOICE: "Player choice",
                DialogueStepType.END: "End conversation"
            }

    def on_selection_changed(self, button):
        """Handle selection change"""
        text = button.text()
        self.selected_type = text.split(":")[0]

    def get_selected_type(self):
        """Get the selected step type"""
        if self.selected_type:
            for step_type in DialogueStepType:
                if step_type.name == self.selected_type:
                    return step_type
        return DialogueStepType.NPC_SPEECH  # Default


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

        # Step type indicator - subtle colors with good contrast
        type_colors = {
            DialogueStepType.START: "#2c3e50",  # Dark blue-gray
            DialogueStepType.NPC_SPEECH: "#34495e",  # Dark gray
            DialogueStepType.PLAYER_CHOICE: "#2c3e50",  # Dark blue-gray
            DialogueStepType.PLAYER_SPEECH: "#16a085",  # Dark teal
            DialogueStepType.NPC_RESPONSE: "#34495e",  # Dark gray
            DialogueStepType.END: "#7f8c8d"  # Medium gray
        }

        type_names = {
            DialogueStepType.START: "START",
            DialogueStepType.NPC_SPEECH: "NPC SPEAKS",
            DialogueStepType.PLAYER_CHOICE: "PLAYER CHOICE",
            DialogueStepType.PLAYER_SPEECH: "PLAYER SPEAKS",
            DialogueStepType.NPC_RESPONSE: "NPC RESPONSE",
            DialogueStepType.END: "END"
        }

        color = type_colors.get(self.step.type, "#34495e")
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
                border: 1px solid #1a252f;
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
        elif self.step.type == DialogueStepType.PLAYER_SPEECH:
            self.setup_player_speech_ui(layout)
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
                speaker_label = QLabel(f"{self.step.speaker}:")
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
                        background-color: #ffffff;
                        color: #2c3e50;
                        padding: 15px;
                        border-radius: 8px;
                        border-left: 4px solid #34495e;
                        margin: 5px;
                        border: 1px solid #bdc3c7;
                    }
                """)
                layout.addWidget(text_label)

        # Add next step button
        if self.is_editable:
            self.add_next_btn = QPushButton("Add Next Part")
            self.add_next_btn.clicked.connect(self.add_next_step)
            self.add_next_btn.setStyleSheet("""
                QPushButton {
                    background-color: #34495e;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    margin-top: 10px;
                    border: 1px solid #2c3e50;
                }
                QPushButton:hover {
                    background-color: #2c3e50;
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
            choices_label = QLabel("📝 Player Options (each leads to different NPC response):")
            choices_label.setStyleSheet("font-weight: bold; margin-top: 10px; color: #2c3e50;")
            layout.addWidget(choices_label)

            self.choices_widget = QWidget()
            self.choices_layout = QVBoxLayout()
            self.choices_widget.setLayout(self.choices_layout)

            self.choice_edits = []
            self.choice_response_labels = []
            for i, choice in enumerate(self.step.choices):
                # Choice group
                choice_group = QGroupBox()
                choice_group.setStyleSheet("""
                    QGroupBox {
                        border: 1px solid #bdc3c7;
                        border-radius: 6px;
                        margin-top: 6px;
                        padding-top: 8px;
                        background-color: #ffffff;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 7px;
                        padding: 0 5px 0 5px;
                        color: #7f8c8d;
                        font-weight: bold;
                    }
                """)
                choice_group.setTitle(f"Choice {i+1}")
                choice_layout = QVBoxLayout()
                choice_group.setLayout(choice_layout)

                # Choice text
                choice_edit = QLineEdit(choice.get('text', ''))
                choice_edit.setPlaceholderText(f"Option {i+1}...")
                choice_edit.textChanged.connect(self.on_step_changed)
                self.choice_edits.append(choice_edit)
                choice_layout.addWidget(QLabel("Player option text:"))
                choice_layout.addWidget(choice_edit)

                # Response mapping info
                target_step_id = choice.get('next_step_id', '')
                if target_step_id:
                    response_label = QLabel(f"→ Leads to: {target_step_id}")
                    response_label.setStyleSheet("color: #27ae60; font-style: italic; padding: 4px;")
                    response_label.setWordWrap(True)
                else:
                    response_label = QLabel("→ Not connected to any response yet")
                    response_label.setStyleSheet("color: #e74c3c; font-style: italic; padding: 4px;")
                    response_label.setWordWrap(True)

                self.choice_response_labels.append(response_label)
                choice_layout.addWidget(response_label)

                # Remove button
                if len(self.step.choices) > 2:  # Allow removal if more than 2 choices
                    remove_btn = QPushButton("🗑️ Remove this choice")
                    remove_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e74c3c;
                            color: white;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 4px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #c0392b;
                        }
                    """)
                    remove_btn.clicked.connect(lambda checked, idx=i: self.remove_choice(idx))
                    choice_layout.addWidget(remove_btn)

                self.choices_layout.addWidget(choice_group)

            layout.addWidget(self.choices_widget)

            # Add choice button
            add_choice_btn = QPushButton("➕ Add Choice")
            add_choice_btn.clicked.connect(self.add_choice)
            layout.addWidget(add_choice_btn)
        else:
            # Display mode
            if self.step.text:
                question_label = QLabel("What do you want to say?")
                question_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin: 10px;")
                layout.addWidget(question_label)

            for i, choice in enumerate(self.step.choices):
                choice_text = choice.get('text', 'No text')
                target_step_id = choice.get('next_step_id', '')

                if target_step_id:
                    # Show choice with connection indicator
                    choice_label = QLabel(f"• {choice_text} → Leads to response")
                    choice_label.setStyleSheet("""
                        QLabel {
                            background-color: #ffffff;
                            color: #2c3e50;
                            padding: 8px 12px;
                            border-radius: 4px;
                            margin: 3px;
                            border-left: 3px solid #27ae60;
                            border: 1px solid #bdc3c7;
                        }
                    """)
                else:
                    # Show choice without connection
                    choice_label = QLabel(f"• {choice_text}")
                    choice_label.setStyleSheet("""
                        QLabel {
                            background-color: #ffffff;
                            color: #2c3e50;
                            padding: 8px 12px;
                            border-radius: 4px;
                            margin: 3px;
                            border-left: 3px solid #e74c3c;
                            border: 1px solid #bdc3c7;
                        }
                    """)

                layout.addWidget(choice_label)

    def setup_player_speech_ui(self, layout):
        """Setup player speech UI (single option that looks like a speech)"""
        if self.is_editable:
            # Speech text label
            speech_label = QLabel("💬 Player says:")
            speech_label.setStyleSheet("font-weight: bold; margin-top: 10px; color: #16a085;")
            layout.addWidget(speech_label)

            # Single speech text edit
            self.speech_edit = QTextEdit()
            self.speech_edit.setPlaceholderText("What does the player say?")
            self.speech_edit.setPlainText(self.step.text)
            self.speech_edit.setMaximumHeight(80)
            self.speech_edit.textChanged.connect(self.on_step_changed)
            layout.addWidget(self.speech_edit)

            # Ensure we have exactly one choice
            if len(self.step.choices) == 0:
                self.step.choices.append({'text': '', 'next_step_id': ''})
            elif len(self.step.choices) > 1:
                # Keep only the first choice
                self.step.choices = [self.step.choices[0]]
        else:
            # Display mode - show as a single clear player speech option
            speech_label = QLabel("💬 Player says:")
            speech_label.setStyleSheet("font-weight: bold; margin: 10px; color: #16a085;")
            layout.addWidget(speech_label)

            # Show the speech text
            if self.step.text:
                speech_text_label = QLabel(self.step.text)
                speech_text_label.setStyleSheet("""
                    QLabel {
                        background-color: #ffffff;
                        color: #2c3e50;
                        padding: 12px 16px;
                        border-radius: 8px;
                        margin: 5px;
                        border-left: 4px solid #16a085;
                        border: 1px solid #bdc3c7;
                        font-style: italic;
                    }
                """)
                speech_text_label.setWordWrap(True)
                layout.addWidget(speech_text_label)

    def setup_end_ui(self, layout):
        """Setup end dialogue UI"""
        end_label = QLabel("Conversation Ends Here")
        end_label.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                color: #2c3e50;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #bdc3c7;
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
            if hasattr(self, 'speech_edit'):
                self.step.text = self.speech_edit.toPlainText()

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
        self.selected_step_id = None
        self.current_step_widget = None
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
        title_label = QLabel("Dialogue Tree")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        left_layout.addWidget(title_label)

        # Tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        left_layout.addWidget(self.tree_widget)

        main_layout.addWidget(left_panel)

        # Right panel - Selected step editor
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        # Top section with step info and controls
        top_section = QWidget()
        top_layout = QVBoxLayout()
        top_section.setLayout(top_layout)

        # Current step info
        self.step_info_label = QLabel("No step selected")
        self.step_info_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 4px;
                margin-bottom: 10px;
                border: 1px solid #dee2e6;
            }
        """)
        top_layout.addWidget(self.step_info_label)

        # Add Next Part button (at the top)
        self.add_next_btn = QPushButton("Add Next Part")
        self.add_next_btn.clicked.connect(self.add_next_step_for_selected)
        self.add_next_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #2c3e50;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                border: 1px solid #95a5a6;
            }
        """)
        self.add_next_btn.setEnabled(False)  # Disabled until step is selected
        top_layout.addWidget(self.add_next_btn)

        right_layout.addWidget(top_section)

        # Selected step editor area
        self.step_editor_widget = QWidget()
        self.step_editor_layout = QVBoxLayout()
        self.step_editor_layout.setAlignment(Qt.AlignTop)
        self.step_editor_widget.setLayout(self.step_editor_layout)

        # No selection placeholder
        self.no_selection_label = QLabel("Select a step from the tree to edit")
        self.no_selection_label.setAlignment(Qt.AlignCenter)
        self.no_selection_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-style: italic;
                padding: 40px;
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 2px dashed #dee2e6;
            }
        """)
        self.step_editor_layout.addWidget(self.no_selection_label)

        right_layout.addWidget(self.step_editor_widget)

        # Bottom toolbar
        toolbar_layout = QHBoxLayout()

        self.validate_btn = QPushButton("Validate")
        self.validate_btn.clicked.connect(self.validate_dialogue)
        toolbar_layout.addWidget(self.validate_btn)

        self.export_btn = QPushButton("Export Lua")
        self.export_btn.clicked.connect(self.export_to_lua)
        toolbar_layout.addWidget(self.export_btn)

        self.help_btn = QPushButton("Help")
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
        # Select the first NPC step by default
        self.select_step("step_2")

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

            # If we deleted the selected step, select another one
            if self.selected_step_id == step_id:
                # Select the first available step
                available_steps = [sid for sid, step in self.steps.items() if step.type != DialogueStepType.START]
                if available_steps:
                    self.select_step(available_steps[0])
                else:
                    # No steps left, show no selection
                    self.selected_step_id = None
                    self.current_step_widget = None
                    # Show no selection label (check if widget still exists)
                    if hasattr(self, 'no_selection_label') and self.no_selection_label is not None:
                        try:
                            self.no_selection_label.show()
                        except RuntimeError:
                            # Widget was already deleted, ignore
                            pass
                    self.add_next_btn.setEnabled(False)
                    self.step_info_label.setText("No step selected")

            self.dialogue_changed.emit()

    def select_step(self, step_id):
        """Select a step for editing"""
        if step_id not in self.steps:
            return

        self.selected_step_id = step_id
        step = self.steps[step_id]

        # Update step info label
        type_names = {
            DialogueStepType.START: "START",
            DialogueStepType.NPC_SPEECH: f"NPC SPEECH ({step.speaker})",
            DialogueStepType.PLAYER_CHOICE: f"PLAYER CHOICE ({len(step.choices)} options)",
            DialogueStepType.NPC_RESPONSE: f"NPC RESPONSE ({step.speaker})",
            DialogueStepType.END: "END"
        }

        self.step_info_label.setText(f"Editing: {type_names.get(step.type, 'STEP')}")

        # Hide no selection label first (before clearing layout)
        if hasattr(self, 'no_selection_label') and self.no_selection_label is not None:
            try:
                self.no_selection_label.hide()
            except RuntimeError:
                # Widget was already deleted, ignore
                pass

        # Clear current step editor
        while self.step_editor_layout.count():
            item = self.step_editor_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create step widget for selected step
        self.current_step_widget = DialogueStepWidget(step, is_editable=True)
        self.current_step_widget.step_changed.connect(self.on_step_widget_changed)
        self.step_editor_layout.addWidget(self.current_step_widget)

        # Enable/disable add next button based on step type
        can_add_next = step.type != DialogueStepType.END
        self.add_next_btn.setEnabled(can_add_next)

        # Update tree selection
        self.update_tree_selection(step_id)

    def update_tree_selection(self, selected_step_id):
        """Update tree selection to highlight selected step"""
        # Clear current selection
        self.tree_widget.clearSelection()

        # Find and select the tree item
        def find_item(items):
            for item in items:
                if item.data(0, Qt.UserRole) == selected_step_id:
                    item.setSelected(True)
                    return True
                if find_item([item.child(i) for i in range(item.childCount())]):
                    return True
            return False

        # Search top level items
        find_item([self.tree_widget.topLevelItem(i) for i in range(self.tree_widget.topLevelItemCount())])

    def add_next_step_for_selected(self):
        """Add next step for the currently selected step"""
        if self.selected_step_id:
            self.add_next_step(self.selected_step_id)

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
            self.select_step(step_id)

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

        # Show step type selection dialog
        dialog = StepTypeSelectionDialog(parent_step.type, self)
        if dialog.exec() == QDialog.Accepted:
            selected_type = dialog.get_selected_type()
            self.create_step_of_type(selected_type, parent_step)
        else:
            # User cancelled, don't add step
            pass

    def create_step_of_type(self, step_type, parent_step):
        """Create a step of the specified type"""
        new_step = None

        if step_type == DialogueStepType.NPC_SPEECH:
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.NPC_SPEECH,
                speaker="NPC",
                text="What would you like to say?"
            )
        elif step_type == DialogueStepType.PLAYER_CHOICE:
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.PLAYER_CHOICE,
                text="What do you want to do?",
                choices=[
                    {"text": "Continue", "next_step_id": ""},
                    {"text": "Ask something else", "next_step_id": ""}
                ]
            )
        elif step_type == DialogueStepType.PLAYER_SPEECH:
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.PLAYER_SPEECH,
                text="I'd like to know more about this.",
                choices=[
                    {"text": "Continue", "next_step_id": ""}
                ]
            )
        elif step_type == DialogueStepType.NPC_RESPONSE:
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.NPC_RESPONSE,
                speaker="NPC",
                text="I understand. Let me help you with that."
            )
        elif step_type == DialogueStepType.END:
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.END
            )
        else:
            # Default to NPC speech
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.NPC_SPEECH,
                speaker="NPC",
                text="Hello!"
            )

        if new_step:
            self.add_step(new_step)
            parent_step.next_step_id = new_step.id
            self.update_tree()
            # Automatically select the newly created step
            self.select_step(new_step.id)

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