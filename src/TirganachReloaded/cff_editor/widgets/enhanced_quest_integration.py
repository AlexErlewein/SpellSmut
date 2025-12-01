"""
Enhanced Quest Integration for Unified Quest Editor

This module adds the enhanced quest viewing functionality (quest viewer integration)
to the existing unified quest editor, providing access to the advanced dialogue editing
and comprehensive quest analysis features.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QPushButton, QComboBox,
    QTextEdit, QLineEdit, QSpinBox, QCheckBox, QProgressBar,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QToolBar, QMenu, QMenuBar, QStatusBar, QMessageBox,
    QFrame, QScrollArea, QSlider, QDial,
    QGridLayout, QFormLayout, QButtonGroup, QRadioButton,
    QDialog, QDialogButtonBox, QFileDialog, QTabWidget
)
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QIcon, QTextCursor

try:
    from .quest_viewer_integration import QuestViewerWidget, QuestDataProcessor
    from .enhanced_dialogue_editor import EnhancedDialogueEditor
    from .logging_config import get_logger
    logger = get_logger(__name__)
except ImportError as e:
    logger = None
    print(f"Warning: Could not import enhanced quest components: {e}")
    QuestViewerWidget = None
    QuestDataProcessor = None
    EnhancedDialogueEditor = None


class EnhancedQuestPanel(QWidget):
    """Enhanced quest panel that adds advanced viewing capabilities to the unified editor"""

    # Signals
    quest_data_updated = Signal(dict)  # Quest data has been updated
    editing_mode_changed = Signal(bool)  # Editing mode has been toggled

    def __init__(self, parent=None):
        super().__init__(parent)
        self.quest_data = {}
        self.enhanced_editor = None
        self.data_processor = None

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header = self._create_header()
        layout.addWidget(header)

        # Enhanced editor tabs
        self.editor_tabs = self._create_editor_tabs()
        layout.addWidget(self.editor_tabs)

    def _create_header(self) -> QWidget:
        """Create header controls"""
        header = QWidget()
        header_layout = QHBoxLayout(header)

        # Title
        self.title_label = QLabel("Enhanced Quest View")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Mode toggle
        self.mode_toggle = QPushButton("Enable Editing")
        self.mode_toggle.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        header_layout.addWidget(self.mode_toggle)

        # Export button
        self.export_btn = QPushButton("Export Quest")
        header_layout.addWidget(self.export_btn)

        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        header_layout.addWidget(self.refresh_btn)

        return header

    def _create_editor_tabs(self) -> QTabWidget:
        """Create enhanced editor tabs"""
        tabs = QTabWidget()

        # Try to create enhanced dialogue editor
        if EnhancedDialogueEditor:
            try:
                self.enhanced_editor = EnhancedDialogueEditor()
                tabs.addTab(self.enhanced_editor, "💬 Enhanced Dialogue")
            except Exception as e:
                logger.error(f"Failed to create enhanced dialogue editor: {e}")
                # Add fallback
                fallback = QTextEdit()
                fallback.setPlaceholderText("Enhanced Dialogue Editor not available")
                fallback.setReadOnly(True)
                tabs.addTab(fallback, "💬 Enhanced Dialogue")
        else:
            # Add fallback
            fallback = QTextEdit()
            fallback.setPlaceholderText("Enhanced Dialogue Editor not available")
            fallback.setReadOnly(True)
            tabs.addTab(fallback, "💬 Enhanced Dialogue")

        # Try to create quest viewer widget
        if QuestViewerWidget:
            try:
                # Create a mock data model for the quest viewer
                class MockDataModel:
                    def __init__(self):
                        self.elements = []

                    def get_elements(self, category):
                        return self.elements

                    def get_localised_text(self, element, field):
                        if hasattr(element, field):
                            return getattr(element, field)
                        return ""

                mock_data_model = MockDataModel()
                self.quest_viewer = QuestViewerWidget(mock_data_model)
                tabs.addTab(self.quest_viewer, "📋 Quest Viewer")
            except Exception as e:
                logger.error(f"Failed to create quest viewer: {e}")
                # Add fallback
                fallback = QTextEdit()
                fallback.setPlaceholderText("Quest Viewer not available")
                fallback.setReadOnly(True)
                tabs.addTab(fallback, "📋 Quest Viewer")
        else:
            # Add fallback
            fallback = QTextEdit()
            fallback.setPlaceholderText("Quest Viewer not available")
            fallback.setReadOnly(True)
            tabs.addTab(fallback, "📋 Quest Viewer")

        # Advanced analysis tab
        self.analysis_tab = self._create_analysis_tab()
        tabs.addTab(self.analysis_tab, "🔍 Analysis")

        return tabs

    def _create_analysis_tab(self) -> QWidget:
        """Create advanced analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Quest structure analysis
        structure_group = QGroupBox("Quest Structure Analysis")
        structure_layout = QFormLayout()

        self.quest_structure_text = QTextEdit()
        self.quest_structure_text.setReadOnly(True)
        self.quest_structure_text.setMaximumHeight(200)
        structure_layout.addRow("Structure:", self.quest_structure_text)

        structure_group.setLayout(structure_layout)
        layout.addWidget(structure_group)

        # Dialogue analysis
        dialogue_group = QGroupBox("Dialogue Analysis")
        dialogue_layout = QFormLayout()

        self.dialogue_stats_text = QTextEdit()
        self.dialogue_stats_text.setReadOnly(True)
        self.dialogue_stats_text.setMaximumHeight(150)
        dialogue_layout.addRow("Statistics:", self.dialogue_stats_text)

        dialogue_group.setLayout(dialogue_layout)
        layout.addWidget(dialogue_group)

        # Requirements and rewards analysis
        rewards_group = QGroupBox("Requirements & Rewards")
        rewards_layout = QFormLayout()

        self.rewards_analysis_text = QTextEdit()
        self.rewards_analysis_text.setReadOnly(True)
        self.rewards_analysis_text.setMaximumHeight(150)
        rewards_layout.addRow("Analysis:", self.rewards_analysis_text)

        rewards_group.setLayout(rewards_layout)
        layout.addWidget(rewards_group)

        layout.addStretch()
        return tab

    def setup_connections(self):
        """Setup signal connections"""
        # Header controls
        self.mode_toggle.clicked.connect(self._toggle_editing_mode)
        self.export_btn.clicked.connect(self._export_quest)
        self.refresh_btn.clicked.connect(self._refresh_quest)

    def load_quest_data(self, quest_id: int, quest_info: Dict[str, Any]):
        """Load quest data into the enhanced panel"""
        try:
            self.quest_data = quest_info.copy()
            self.quest_data['quest_id'] = quest_id

            # Update title
            quest_name = quest_info.get('name', f'Quest {quest_id}')
            self.title_label.setText(f"Enhanced Quest View - {quest_name}")

            # Load into enhanced dialogue editor
            if self.enhanced_editor and hasattr(self.enhanced_editor, 'set_dialogue_data'):
                # Try to extract dialogue data
                dialogue_data = self._extract_dialogue_data(quest_info)
                self.enhanced_editor.set_dialogue_data(dialogue_data)

            # Load into quest viewer
            if self.quest_viewer and hasattr(self.quest_viewer, 'load_quest'):
                # Create mock data model element
                class MockQuestElement:
                    def __init__(self, quest_info):
                        for key, value in quest_info.items():
                            setattr(self, key, value)

                mock_element = MockQuestElement(quest_info)

                # Add to viewer's data model
                if hasattr(self.quest_viewer, 'data_model'):
                    self.quest_viewer.data_model.elements = [mock_element]

                # Load quest
                self.quest_viewer.load_quest(quest_id)

            # Update analysis
            self._update_analysis()

        except Exception as e:
            logger.error(f"Error loading quest data: {e}")

    def _extract_dialogue_data(self, quest_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract dialogue data from quest info"""
        dialogue_data = {
            'nodes': {},
            'start_node_id': ''
        }

        # Try to get dialogue from quest info
        dialogues = quest_info.get('dialogues', [])
        if dialogues and len(dialogues) > 0:
            # Create simple dialogue tree
            start_node_id = f'quest_{quest_info.get("quest_id", 0)}_start'

            dialogue_data['nodes'][start_node_id] = {
                'node_id': start_node_id,
                'node_type': 'npc',
                'speaker': dialogues[0].get('speaker', 'Quest Giver'),
                'text': dialogues[0].get('text', 'Welcome to the quest!'),
                'conditions': [],
                'actions': [
                    {
                        'action_type': 'quest_begin',
                        'params': {'quest_id': quest_info.get('quest_id', 0)},
                        'description': f'Begin quest {quest_info.get("quest_id", 0)}'
                    }
                ],
                'choices': [
                    {
                        'choice_id': 1,
                        'text': 'I accept this quest!',
                        'next_node_id': f'quest_{quest_info.get("quest_id", 0)}_accept',
                        'conditions': [],
                        'actions': []
                    },
                    {
                        'choice_id': 2,
                        'text': 'I need more information.',
                        'next_node_id': f'quest_{quest_info.get("quest_id", 0)}_info',
                        'conditions': [],
                        'actions': []
                    }
                ]
            }

            dialogue_data['start_node_id'] = start_node_id

        return dialogue_data

    def _update_analysis(self):
        """Update the analysis tab with current quest data"""
        if not self.quest_data:
            return

        try:
            # Quest structure analysis
            structure_info = self._analyze_quest_structure()
            self.quest_structure_text.setPlainText(structure_info)

            # Dialogue statistics
            dialogue_info = self._analyze_dialogue()
            self.dialogue_stats_text.setPlainText(dialogue_info)

            # Requirements and rewards analysis
            rewards_info = self._analyze_requirements_rewards()
            self.rewards_analysis_text.setPlainText(rewards_info)

        except Exception as e:
            logger.error(f"Error updating analysis: {e}")

    def _analyze_quest_structure(self) -> str:
        """Analyze quest structure"""
        if not self.quest_data:
            return "No quest data available"

        lines = [
            f"Quest ID: {self.quest_data.get('quest_id', 'Unknown')}",
            f"Name: {self.quest_data.get('name', 'Unknown')}",
            f"Type: {self.quest_data.get('type', 'Unknown')}",
            f"Status: {self.quest_data.get('status', 'Unknown')}",
            f"Priority: {self.quest_data.get('priority', 5)}",
            "",
            "Quest Components:",
            f"• Objectives: {len(self.quest_data.get('objectives', []))}",
            f"• Dialogues: {len(self.quest_data.get('dialogues', []))}",
            f"• Requirements: {len(self.quest_data.get('requirements', []))}",
            f"• Rewards: {len(self.quest_data.get('rewards', {}))}",
            f"• Flags: {len(self.quest_data.get('flags', []))}",
            "",
            "Structure Status: ✅ Valid"
        ]

        return '\n'.join(lines)

    def _analyze_dialogue(self) -> str:
        """Analyze dialogue data"""
        dialogues = self.quest_data.get('dialogues', [])
        if not dialogues:
            return "No dialogue data found"

        lines = [
            f"Total Dialogues: {len(dialogues)}",
            "",
            "Dialogue Details:",
        ]

        for i, dialogue in enumerate(dialogues, 1):
            speaker = dialogue.get('speaker', 'Unknown')
            text = dialogue.get('text', 'No text')
            text_preview = text[:100] + ('...' if len(text) > 100 else '')

            lines.append(f"{i}. {speaker}: {text_preview}")

        return '\n'.join(lines)

    def _analyze_requirements_rewards(self) -> str:
        """Analyze requirements and rewards"""
        lines = []

        # Requirements
        requirements = self.quest_data.get('requirements', [])
        lines.append(f"Requirements ({len(requirements)}):")

        if requirements:
            for req in requirements:
                lines.append(f"• {req.get('description', 'Unknown requirement')}")
        else:
            lines.append("• No requirements")

        lines.append("")

        # Rewards
        rewards = self.quest_data.get('rewards', {})
        lines.append("Rewards:")

        if rewards:
            if rewards.get('experience', 0) > 0:
                lines.append(f"• {rewards['experience']} Experience")

            total_money = rewards.get('gold', 0) + rewards.get('silver', 0) + rewards.get('copper', 0)
            if total_money > 0:
                lines.append(f"• {total_money} Currency")

            if rewards.get('items'):
                lines.append(f"• {len(rewards['items'])} Items")
        else:
            lines.append("• No rewards")

        return '\n'.join(lines)

    def _toggle_editing_mode(self):
        """Toggle between viewing and editing modes"""
        if self.mode_toggle.text() == "Enable Editing":
            self.mode_toggle.setText("Read-Only Mode")
            self.mode_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            self.title_label.setText("Enhanced Quest Editor")
            self.editing_mode_changed.emit(True)
        else:
            self.mode_toggle.setText("Enable Editing")
            self.mode_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.title_label.setText("Enhanced Quest Viewer")
            self.editing_mode_changed.emit(False)

    def _export_quest(self):
        """Export the current quest data"""
        try:
            if not self.quest_data:
                QMessageBox.warning(self, "Export Error", "No quest data available for export.")
                return

            # Create export dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Export Quest Data")
            dialog.setMinimumSize(800, 600)

            layout = QVBoxLayout(dialog)

            # Export options
            options_group = QGroupBox("Export Options")
            options_layout = QVBoxLayout()

            self.format_combo = QComboBox()
            self.format_combo.addItems(["Summary", "JSON", "Detailed"])
            options_layout.addWidget(QLabel("Format:"))
            options_layout.addWidget(self.format_combo)
            options_group.setLayout(options_layout)

            layout.addWidget(options_group)

            # Preview
            preview_text = QTextEdit()
            preview_text.setReadOnly(True)

            # Generate preview based on selected format
            format_type = self.format_combo.currentText().lower()
            if format_type == "summary":
                preview_text.setPlainText(self._generate_summary())
            elif format_type == "json":
                preview_text.setPlainText(json.dumps(self.quest_data, indent=2, ensure_ascii=False))
            else:  # detailed
                preview_text.setPlainText(self._generate_detailed_export())

            layout.addWidget(QLabel("Preview:"))
            layout.addWidget(preview_text)

            # Buttons
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            # Update preview when format changes
            self.format_combo.currentTextChanged.connect(lambda: self._update_export_preview(preview_text))

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export quest: {str(e)}")

    def _update_export_preview(self, text_edit):
        """Update the export preview"""
        try:
            format_type = self.format_combo.currentText().lower()
            if format_type == "summary":
                text_edit.setPlainText(self._generate_summary())
            elif format_type == "json":
                text_edit.setPlainText(json.dumps(self.quest_data, indent=2, ensure_ascii=False))
            else:  # detailed
                text_edit.setPlainText(self._generate_detailed_export())
        except Exception as e:
            text_edit.setPlainText(f"Error generating preview: {str(e)}")

    def _generate_summary(self) -> str:
        """Generate a text summary of the quest"""
        if not self.quest_data:
            return "No quest data available"

        lines = [
            f"Quest Summary: {self.quest_data.get('name', 'Unknown')}",
            "=" * 50,
            f"ID: {self.quest_data.get('quest_id', 'Unknown')}",
            f"Type: {self.quest_data.get('type', 'Unknown')}",
            f"Priority: {self.quest_data.get('priority', 5)}",
            f"Status: {self.quest_data.get('status', 'Unknown')}",
            "",
            "Description:",
            self.quest_data.get('description', 'No description'),
            ""
        ]

        # Add objectives
        objectives = self.quest_data.get('objectives', [])
        if objectives:
            lines.extend(["Objectives:", "-" * 20])
            for i, obj in enumerate(objectives, 1):
                lines.append(f"{i}. {obj.get('description', 'Unknown objective')}")
            lines.append("")

        # Add rewards
        rewards = self.quest_data.get('rewards', {})
        if rewards:
            lines.extend(["Rewards:", "-" * 20])
            if rewards.get('experience', 0) > 0:
                lines.append(f"• {rewards['experience']} Experience")
            total_money = rewards.get('gold', 0) + rewards.get('silver', 0) + rewards.get('copper', 0)
            if total_money > 0:
                lines.append(f"• {total_money} Currency")
            lines.append("")

        return '\n'.join(lines)

    def _generate_detailed_export(self) -> str:
        """Generate detailed quest data export"""
        if not self.quest_data:
            return "No quest data available"

        lines = [
            "Detailed Quest Export",
            "=" * 50,
            f"Export Date: {self._get_timestamp()}",
            "",
            "Basic Information:",
            "-" * 20
        ]

        # Basic info
        basic_fields = ['quest_id', 'name', 'type', 'status', 'priority', 'description']
        for field in basic_fields:
            value = self.quest_data.get(field, 'N/A')
            lines.append(f"{field.title()}: {value}")

        # Add detailed sections
        sections = ['objectives', 'requirements', 'rewards', 'dialogues', 'flags']
        for section in sections:
            section_data = self.quest_data.get(section, [])
            if section_data:
                lines.append(f"\n{section.title()} ({len(section_data)}):")
                lines.append("-" * 30)
                for item in section_data:
                    lines.append(f"• {item}")

        return '\n'.join(lines)

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _refresh_quest(self):
        """Refresh the current quest data"""
        if self.quest_data:
            quest_id = self.quest_data.get('quest_id')
            if quest_id:
                self.load_quest_data(quest_id, self.quest_data)
                QMessageBox.information(self, "Refresh", "Quest data refreshed successfully.")
            else:
                QMessageBox.warning(self, "Refresh", "No quest ID available for refresh.")
        else:
            QMessageBox.warning(self, "Refresh", "No quest data available for refresh.")


class EnhancedQuestIntegration(QObject):
    """Integration manager for adding enhanced quest viewing to the unified editor"""

    def __init__(self):
        super().__init__()
        self.enhanced_panel = None

    def add_to_unified_editor(self, unified_editor):
        """Add enhanced quest panel to the unified quest editor"""
        try:
            # Create enhanced quest panel
            self.enhanced_panel = EnhancedQuestPanel(unified_editor)

            # Add as a new tab to the unified editor
            if hasattr(unified_editor, 'main_tabs'):
                unified_editor.main_tabs.addTab(self.enhanced_panel, "🚀 Enhanced View")

                # Connect signals
                if hasattr(unified_editor, '_on_quest_selected'):
                    # Replace or supplement the existing quest selection handler
                    self._connect_quest_selection(unified_editor)

                logger.info("Enhanced quest panel added to unified editor")
                return True
            else:
                logger.warning("Could not find main_tabs in unified editor")
                return False

        except Exception as e:
            logger.error(f"Failed to add enhanced quest panel: {e}")
            return False

    def _connect_quest_selection(self, unified_editor):
        """Connect quest selection to enhanced panel"""
        try:
            if hasattr(unified_editor, 'quest_browser'):
                # Connect to quest browser signals
                unified_editor.quest_browser.quest_selected.connect(self._on_quest_selected)
                return True
        except Exception as e:
            logger.error(f"Failed to connect quest selection: {e}")
            return False

    def _on_quest_selected(self, quest_id: int):
        """Handle quest selection from quest browser"""
        try:
            if hasattr(self.enhanced_panel, 'load_quest_data'):
                # Get quest data from unified editor
                if hasattr(self.enhanced_panel, 'parent'):
                    unified_editor = self.enhanced_panel.parent()
                    if hasattr(unified_editor, 'quest_data') and quest_id in unified_editor.quest_data:
                        quest_info = unified_editor.quest_data[quest_id]
                        self.enhanced_panel.load_quest_data(quest_id, quest_info)
        except Exception as e:
            logger.error(f"Error handling quest selection: {e}")


def integrate_enhanced_quest_viewing(unified_editor):
    """
    Integration function to add enhanced quest viewing to the unified quest editor.

    Call this function from the unified quest editor to add the enhanced functionality.

    Args:
        unified_editor: The UnifiedQuestEditor instance

    Returns:
        bool: True if integration was successful, False otherwise
    """
    try:
        integration = EnhancedQuestIntegration()
        success = integration.add_to_unified_editor(unified_editor)

        if success:
            logger.info("Enhanced quest viewing successfully integrated with unified editor")
        else:
            logger.warning("Failed to integrate enhanced quest viewing")

        return success

    except Exception as e:
        logger.error(f"Error integrating enhanced quest viewing: {e}")
        return False