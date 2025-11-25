#!/usr/bin/env python3
"""
Enhanced Text Mode Dialogue Overview

Extended text mode overview that displays conditions, actions, and consequences
with enhanced formatting and color coding.
"""

import sys
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QColor, QFont, QKeySequence, QSyntaxHighlighter,
    QTextCharFormat, QTextCursor, QTextDocument, QBrush
)
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QSplitter, QStatusBar, QTextEdit,
    QToolBar, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget, QTabWidget, QCheckBox, QSpinBox
)

try:
    from TirganachReloaded.cff_editor.models.enhanced_dialogue_models import (
        DialogueTree, DialogueNode, DialogueChoice,
        DialogueCondition, DialogueAction
    )
    from TirganachReloaded.cff_editor.widgets.answer_id_management_panel import AnswerIdManagementPanel
    from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

    # Fallback classes if modules not available
    class DialogueTree:
        def __init__(self):
            self.nodes = {}
            self.start_node_id = ""

        def to_dict(self):
            return {"nodes": {}, "start_node_id": ""}

        @classmethod
        def from_dict(cls, data):
            tree = cls()
            tree.start_node_id = data.get("start_node_id", "")
            return tree


class EnhancedDialogueSyntaxHighlighter(QSyntaxHighlighter):
    """Enhanced syntax highlighter for dialogue with conditions and actions"""

    def __init__(self, document):
        super().__init__(document)
        self.setup_highlighting()

    def setup_highlighting(self):
        """Setup enhanced syntax highlighting rules"""

        # Node ID format
        node_id_format = QTextCharFormat()
        node_id_format.setForeground(QColor(41, 128, 185))  # Blue
        node_id_format.setFontWeight(QFont.Weight.Bold)
        self.node_id_pattern = r"#\w+|node_\w+"

        # Speaker format
        speaker_format = QTextCharFormat()
        speaker_format.setForeground(QColor(39, 174, 96))  # Green
        speaker_format.setFontWeight(QFont.Weight.Bold)
        self.speaker_pattern = r"\(NPC\)|\(Player\)|\(START\)|\(END\)"

        # Choice format
        choice_format = QTextCharFormat()
        choice_format.setForeground(QColor(142, 68, 173))  # Purple
        self.choice_pattern = r"->\s*\[[A-Z]\]|\[[A-Z]\]"

        # AnswerId format
        answer_id_format = QTextCharFormat()
        answer_id_format.setForeground(QColor(52, 152, 219))  # Light blue
        answer_id_format.setFontWeight(QFont.Weight.Bold)
        self.answer_id_pattern = r"\[🏷️\d+\]|\[AnswerId=\d+\]"

        # Condition format
        condition_format = QTextCharFormat()
        condition_format.setForeground(QColor(241, 196, 15))  # Yellow
        condition_format.setFontWeight(QFont.Weight.Bold)
        self.condition_pattern = r"\[🔒\]|\[CONDITION\]"

        # Action format
        action_format = QTextCharFormat()
        action_format.setForeground(QColor(230, 126, 34))  # Orange
        action_format.setFontWeight(QFont.Weight.Bold)
        self.action_pattern = r"\[⚡\]|\[ACTION\]"

        # Quest format
        quest_format = QTextCharFormat()
        quest_format.setForeground(QColor(46, 204, 113))  # Green
        quest_format.setFontWeight(QFont.Weight.Bold)
        self.quest_pattern = r"\[📋\]|\[QUEST\]"

        # Variable format
        variable_format = QTextCharFormat()
        variable_format.setForeground(QColor(231, 76, 60))  # Red
        variable_format.setFontWeight(QFont.Weight.Bold)
        self.variable_pattern = r"\[🔧\]|\[VARIABLE\]"

        # Error format
        error_format = QTextCharFormat()
        error_format.setForeground(QColor(231, 76, 60))  # Red
        error_format.setFontWeight(QFont.Weight.Bold)
        self.error_pattern = r"\[ERROR\].*"

        # Warning format
        warning_format = QTextCharFormat()
        warning_format.setForeground(QColor(243, 156, 18))  # Orange
        self.warning_pattern = r"\[WARN\].*"

        # Success format
        success_format = QTextCharFormat()
        success_format.setForeground(QColor(39, 174, 96))  # Green
        self.success_pattern = r"\[✓\]|\[SUCCESS\]"

    def highlightBlock(self, text):
        """Apply syntax highlighting to a text block"""
        import re

        patterns = [
            (self.node_id_pattern, node_id_format),
            (self.speaker_pattern, speaker_format),
            (self.choice_pattern, choice_format),
            (self.answer_id_pattern, answer_id_format),
            (self.condition_pattern, condition_format),
            (self.action_format, action_format),
            (self.quest_pattern, quest_format),
            (self.variable_pattern, variable_format),
            (self.error_pattern, error_format),
            (self.warning_pattern, warning_format),
            (self.success_pattern, success_format)
        ]

        for pattern, format_obj in patterns:
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), format_obj)


class EnhancedTextModeOverview(QWidget):
    """
    Enhanced text mode overview with conditions, actions, and consequences
    """

    # Signals
    node_selected = Signal(str)  # node_id
    choice_selected = Signal(str, int)  # node_id, choice_index
    dialogue_updated = Signal()  # dialogue data changed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dialogue_tree = DialogueTree()
        self.selected_node_id: Optional[str] = None
        self.search_text: str = ""
        self.show_conditions = True
        self.show_actions = True
        self.show_variables = True

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)

        # Toolbar with controls
        toolbar = self.setup_toolbar()
        layout.addWidget(toolbar)

        # Main content area
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)

        # Top: Enhanced text view
        self.setup_text_view(splitter)

        # Bottom: Details and options
        self.setup_bottom_panel(splitter)

        # Set splitter sizes
        splitter.setSizes([500, 200])

        # Status bar
        self.status_label = QLabel("Ready - No dialogue loaded")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

    def setup_toolbar(self) -> QToolBar:
        """Setup the toolbar"""
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # Search
        toolbar.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setMaximumWidth(200)
        self.search_edit.setPlaceholderText("Search dialogue...")
        toolbar.addWidget(self.search_edit)

        # Display options
        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Show:"))

        self.show_conditions_checkbox = QCheckBox("Conditions")
        self.show_conditions_checkbox.setChecked(True)
        toolbar.addWidget(self.show_conditions_checkbox)

        self.show_actions_checkbox = QCheckBox("Actions")
        self.show_actions_checkbox.setChecked(True)
        toolbar.addWidget(self.show_actions_checkbox)

        self.show_variables_checkbox = QCheckBox("Variables")
        self.show_variables_checkbox.setChecked(True)
        toolbar.addWidget(self.show_variables_checkbox)

        toolbar.addSeparator()

        # Action buttons
        self.validate_btn = QPushButton("🔍 Validate")
        self.export_btn = QPushButton("📤 Export LUA")
        self.refresh_btn = QPushButton("🔄 Refresh")

        toolbar.addWidget(self.validate_btn)
        toolbar.addWidget(self.export_btn)
        toolbar.addWidget(self.refresh_btn)

        return toolbar

    def setup_text_view(self, parent):
        """Setup the enhanced text view"""
        # Text widget with syntax highlighting
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Courier New", 10))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 3px;
                selection-background-color: #34495e;
            }
        """)

        # Setup syntax highlighter
        self.highlighter = EnhancedDialogueSyntaxHighlighter(self.text_edit.document())

        parent.addWidget(self.text_edit)

    def setup_bottom_panel(self, parent):
        """Setup the bottom details panel"""
        # Create tabbed panel
        self.details_tabs = QTabWidget()

        # Node details tab
        self.setup_node_details_tab()
        self.details_tabs.addTab(self.node_details_tab, "📝 Details")

        # Statistics tab
        self.setup_statistics_tab()
        self.details_tabs.addTab(self.stats_tab, "📊 Statistics")

        # Legend tab
        self.setup_legend_tab()
        self.details_tabs.addTab(self.legend_tab, "📖 Legend")

        parent.addWidget(self.details_tabs)

    def setup_node_details_tab(self):
        """Setup the node details tab"""
        self.node_details_tab = QWidget()
        layout = QVBoxLayout(self.node_details_tab)

        # Node info
        self.node_info_text = QTextEdit()
        self.node_info_text.setReadOnly(True)
        self.node_info_text.setMaximumHeight(150)
        self.node_info_text.setFont(QFont("Arial", 9))
        layout.addWidget(QLabel("Node Information:"))
        layout.addWidget(self.node_info_text)

        # Conditions info
        self.conditions_info_text = QTextEdit()
        self.conditions_info_text.setReadOnly(True)
        self.conditions_info_text.setMaximumHeight(150)
        self.conditions_info_text.setFont(QFont("Arial", 9))
        layout.addWidget(QLabel("Node Conditions:"))
        layout.addWidget(self.conditions_info_text)

        # Actions info
        self.actions_info_text = QTextEdit()
        self.actions_info_text.setReadOnly(True)
        self.actions_info_text.setMaximumHeight(150)
        self.actions_info_text.setFont(QFont("Arial", 9))
        layout.addWidget(QLabel("Node Actions:"))
        layout.addWidget(self.actions_info_text)

        layout.addStretch()

    def setup_statistics_tab(self):
        """Setup the statistics tab"""
        self.stats_tab = QWidget()
        layout = QVBoxLayout(self.stats_tab)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(QFont("Arial", 9))
        layout.addWidget(self.stats_text)

    def setup_legend_tab(self):
        """Setup the legend tab"""
        self.legend_tab = QWidget()
        layout = QVBoxLayout(self.legend_tab)

        legend_text = """
📖 ENHANCED DIALOGUE LEGEND
========================================

NODE TYPES & FORMATTING:
• #node_id - Node identifier (blue, bold)
• (Speaker) - Character speaking (green, bold)
• [A], [B], [C] - Choice letters (purple)

CONNECTIONS & STATUS:
• ✓ - Connected/Available
• ○ - Unconnected/Unavailable
• → node_name - Navigation to next node
• → [UNCONNECTED] - No target defined

ENHANCED FEATURES:
• [🏷️123] - AnswerId for game integration (light blue)
• [🔒] - Conditions for availability (yellow)
• [⚡] - Actions triggered by choice (orange)
• [📋] - Quest integration (green)
• [🔧] - Variable changes (red)

CONDITION EXAMPLES:
• [🔒] Global flag 'player_has_key' is TRUE
• [🔒] Quest 501 is complete
• [🔒] Player level >= 10
• [🔒] NPC 2045 is dead

ACTION EXAMPLES:
• [⚡] Set global flag 'door_opened' to TRUE
• [⚡] Give item 1503 (ancient_key)
• [⚡] Begin quest 502
• [⚡] Give 500 XP

QUEST INTEGRATION:
• [📋] Links to quest IDs
• [📋] Triggers quest state changes
• [📋] Updates quest variables

VARIABLES & FLAGS:
• [🔧] Global flags: persistent game state
• [🔧] NPC flags: character-specific state
• [🔧] Item flags: item-specific properties
"""

        self.legend_text = QTextEdit()
        self.legend_text.setPlainText(legend_text)
        self.legend_text.setReadOnly(True)
        self.legend_text.setFont(QFont("Courier New", 9))
        self.legend_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                color: #2c3e50;
                border: 1px solid #dee2e6;
            }
        """)

        layout.addWidget(self.legend_text)

    def setup_connections(self):
        """Setup signal connections"""
        # Toolbar connections
        self.search_edit.textChanged.connect(self.on_search_changed)
        self.show_conditions_checkbox.toggled.connect(self.on_display_options_changed)
        self.show_actions_checkbox.toggled.connect(self.on_display_options_changed)
        self.show_variables_checkbox.toggled.connect(self.on_display_options_changed)
        self.validate_btn.clicked.connect(self.validate_dialogue)
        self.export_btn.clicked.connect(self.export_lua)
        self.refresh_btn.clicked.connect(self.refresh_display)

        # Text view connections
        self.text_edit.cursorPositionChanged.connect(self.on_cursor_changed)

    def set_dialogue_data(self, dialogue_data: Dict[str, Any]):
        """Set dialogue data and refresh display"""
        try:
            self.dialogue_tree = DialogueTree.from_dict(dialogue_data)
            self.refresh_display()
            self.status_label.setText(f"Loaded dialogue with {len(self.dialogue_tree.nodes)} nodes")
        except Exception as e:
            logger.error(f"Error loading dialogue data: {e}")
            self.status_label.setText(f"Error: {str(e)}")

    def get_dialogue_data(self) -> Dict[str, Any]:
        """Get dialogue data as dictionary"""
        return self.dialogue_tree.to_dict()

    def refresh_display(self):
        """Refresh the text display"""
        if not self.dialogue_tree.nodes:
            self.text_edit.setPlainText(
                "No dialogue nodes found.\n\nUse the toolbar to create new nodes or load dialogue data."
            )
            self.update_statistics()
            return

        # Generate enhanced ASCII tree
        ascii_tree = self._generate_enhanced_ascii_tree()
        self.text_edit.setPlainText(ascii_tree)

        # Update statistics
        self.update_statistics()

    def _generate_enhanced_ascii_tree(self) -> str:
        """Generate enhanced ASCII representation of the dialogue tree"""
        lines = []
        lines.append("=" * 80)
        lines.append("ENHANCED DIALOGUE TREE OVERVIEW")
        lines.append("=" * 80)
        lines.append("")

        # Find start node
        start_node = None
        if self.dialogue_tree.start_node_id:
            start_node = self.dialogue_tree.get_node(self.dialogue_tree.start_node_id)

        if not start_node and self.dialogue_tree.nodes:
            start_node = list(self.dialogue_tree.nodes.values())[0]

        if not start_node:
            lines.append("No dialogue nodes found.")
            return "\n".join(lines)

        # Build tree recursively
        visited = set()
        self._build_enhanced_tree_lines(start_node.node_id, lines, visited, "", True, 0)

        # Add unvisited nodes
        unvisited = set(self.dialogue_tree.nodes.keys()) - visited
        if unvisited:
            lines.append("")
            lines.append("UNCONNECTED NODES:")
            for node_id in sorted(unvisited):
                node = self.dialogue_tree.nodes[node_id]
                lines.append(f"  {self._format_node_enhanced(node, 0)}")

        return "\n".join(lines)

    def _build_enhanced_tree_lines(
        self,
        node_id: str,
        lines: List[str],
        visited: Set[str],
        prefix: str,
        is_last: bool,
        depth: int,
    ):
        """Build enhanced tree lines recursively"""
        if node_id in visited:
            lines.append(f"{prefix}[CYCLE: {node_id}]")
            return

        if node_id not in self.dialogue_tree.nodes:
            lines.append(f"{prefix}[MISSING: {node_id}]")
            return

        visited.add(node_id)
        node = self.dialogue_tree.nodes[node_id]

        # Format node with enhanced information
        node_line = self._format_node_enhanced(node, depth)
        lines.append(f"{prefix}{node_line}")

        # Show node conditions
        if self.show_conditions and node.conditions:
            for condition in node.conditions:
                cond_line = f"{prefix}    [🔒] {condition.get_display_text()}"
                if condition.negated:
                    cond_line += " (NEGATED)"
                lines.append(cond_line)

        # Show node actions
        if self.show_actions and node.actions:
            for action in node.actions:
                action_line = f"{prefix}    [⚡] {action.get_display_text()}"
                lines.append(action_line)

        # Add choices
        if node.choices:
            connected_count = sum(1 for choice in node.choices if choice.next_node_id)
            total_count = len(node.choices)
            lines.append(f"{prefix}    ┌─ Choices ({connected_count}/{total_count} connected):")

            for i, choice in enumerate(node.choices):
                choice_text = choice.text[:50] + "..." if len(choice.text) > 50 else choice.text
                choice_letter = chr(65 + i)  # A, B, C, ...
                next_node = choice.next_node_id
                choice_answer_id = choice.choice_id

                # Tree structure symbols
                connector = "└─" if i == len(node.choices) - 1 else "├─"
                status_icon = "✓" if next_node else "○"

                # Build choice line
                choice_line = f"{prefix}    {connector} [{choice_letter}] {status_icon}"
                if choice_answer_id is not None:
                    choice_line += f" [🏷️{choice_answer_id}]"
                choice_line += f" {choice_text}"

                if len(choice_text) > 50:
                    choice_line += "..."

                if next_node:
                    choice_line += f" → {next_node}"
                else:
                    choice_line += f" → [UNCONNECTED]"

                lines.append(choice_line)

                # Show choice conditions
                if self.show_conditions and choice.conditions:
                    for condition in choice.conditions:
                        cond_line = f"{prefix}        [🔒] {condition.get_display_text()}"
                        if condition.negated:
                            cond_line += " (NEGATED)"
                        lines.append(cond_line)

                # Show choice actions
                if self.show_actions and choice.actions:
                    for action in choice.actions:
                        action_line = f"{prefix}        [⚡] {action.get_display_text()}"
                        lines.append(action_line)

        # Show AnswerId for response nodes
        if node.answer_id:
            answer_id_line = f"{prefix}    [🏷️ AnswerId={node.answer_id}] (Responds to player choice)"
            lines.append(answer_id_line)

        # Recurse to connected nodes
        connected_nodes = set()
        for choice in node.choices:
            if choice.next_node_id and choice.next_node_id in self.dialogue_tree.nodes:
                connected_nodes.add(choice.next_node_id)

        for connected_node_id in sorted(connected_nodes):
            child_prefix = prefix + ("    " if is_last else "│   ")
            tree_prefix = "└── " if connected_node_id == list(connected_nodes)[-1] else "├── "
            self._build_enhanced_tree_lines(
                connected_node_id,
                lines,
                visited,
                child_prefix + tree_prefix,
                connected_node_id == list(connected_nodes)[-1],
                depth + 1
            )

    def _format_node_enhanced(self, node, depth: int) -> str:
        """Format a node with enhanced information display"""
        # Node ID
        node_id_display = f"#{node.node_id}" if not node.node_id.startswith("#") else node.node_id

        # Node type
        type_indicator = {
            "npc": "🗣️",
            "player": "👤",
            "start": "🚀",
            "end": "🏁"
        }.get(node.node_type, "📄")

        # Speaker
        speaker_display = ""
        if node.speaker:
            speaker_display = f"({node.speaker}) "
        elif node.node_type.lower() in ["npc", "start"]:
            speaker_display = "(NPC) "
        elif node.node_type.lower() == "player":
            speaker_display = "(Player) "

        # Text preview with truncation
        text_preview = node.text[:60] + "..." if len(node.text) > 60 else node.text
        if not text_preview:
            text_preview = "[No text]"

        # Status indicators
        status_indicators = []

        if node.conditions:
            status_indicators.append(f"[🔒{len(node.conditions)}]")

        if node.actions:
            status_indicators.append(f"[⚡{len(node.actions)}]")

        if node.choices:
            connected_count = sum(1 for choice in node.choices if choice.next_node_id)
            status_indicators.append(f"[↗️{connected_count}/{len(node.choices)}]")

        # Format main line
        line = f"{type_indicator} {node_id_display}  {speaker_display}{text_preview}"
        if status_indicators:
            line += f" {' '.join(status_indicators)}"

        # Add AnswerId for response nodes
        if node.answer_id:
            line += f" [🏷️AnswerId={node.answer_id}]"

        return line

    def update_statistics(self):
        """Update the statistics display"""
        if not self.dialogue_tree.nodes:
            self.stats_text.setPlainText("No dialogue data to analyze.")
            return

        # Calculate statistics
        total_nodes = len(self.dialogue_tree.nodes)
        total_choices = sum(len(node.choices) for node in self.dialogue_tree.nodes.values())
        total_conditions = sum(len(node.conditions) for node in self.dialogue_tree.nodes.values())
        total_actions = sum(len(node.actions) for node in self.dialogue_tree.nodes.values())
        total_choice_conditions = sum(len(choice.conditions) for node in self.dialogue_tree.nodes.values() for choice in node.choices)
        total_choice_actions = sum(len(choice.actions) for node in self.dialogue_tree.nodes.values() for choice in node.choices)

        connected_choices = sum(1 for node in self.dialogue_tree.nodes.values() for choice in node.choices if choice.next_node_id)
        answer_ids = [node.answer_id for node in self.dialogue_tree.nodes.values() if node.answer_id] + [choice.choice_id for node in self.dialogue_tree.nodes.values() for choice in node.choices if choice.choice_id]

        # Build statistics text
        stats_text = f"""📊 DIALOGUE STATISTICS
========================================

BASIC STRUCTURE:
• Total Dialogue Nodes: {total_nodes}
• Total Player Choices: {total_choices}
• Connected Choices: {connected_choices}
• Unconnected Choices: {total_choices - connected_choices}

ENHANCED FEATURES:
• Node Conditions: {total_conditions}
• Node Actions: {total_actions}
• Choice Conditions: {total_choice_conditions}
• Choice Actions: {total_choice_actions}

GAME INTEGRATION:
• Total AnswerIds Assigned: {len(answer_ids)}
• AnswerId Range: {min(answer_ids) if answer_ids else 'N/A'} - {max(answer_ids) if answer_ids else 'N/A'}
• Response Nodes: {sum(1 for node in self.dialogue_tree.nodes.values() if node.answer_id > 0)}

NODE TYPE BREAKDOWN:
"""

        # Count nodes by type
        type_counts = {}
        for node in self.dialogue_tree.nodes.values():
            type_counts[node.node_type] = type_counts.get(node.node_type, 0) + 1

        for node_type, count in type_counts.items():
            type_icon = {
                "npc": "🗣️",
                "player": "👤",
                "start": "🚀",
                "end": "🏁"
            }.get(node_type, "📄")
            stats_text += f"• {type_icon} {node_type.title()}: {count}\n"

        stats_text += f"""
COMPLEXITY METRICS:
• Average Choices per Node: {total_choices / total_nodes:.1f}
• Average Conditions per Node: {total_conditions / total_nodes:.1f}
• Average Actions per Node: {total_actions / total_nodes:.1f}
• Condition Density: {(total_conditions + total_choice_conditions) / (total_nodes + total_choices) * 100:.1f}%
• Action Density: {(total_actions + total_choice_actions) / (total_nodes + total_choices) * 100:.1f}%
"""

        self.stats_text.setPlainText(stats_text)

    def update_node_details(self, node_id: str):
        """Update the node details panel"""
        node = self.dialogue_tree.get_node(node_id)
        if not node:
            return

        # Node information
        node_info = f"""Node ID: {node.node_id}
Node Type: {node.node_type.upper()}
Speaker: {node.speaker or 'N/A'}
AnswerId: {node.answer_id or 'N/A'}
Text Length: {len(node.text)} characters
Choices: {len(node.choices)}
"""

        self.node_info_text.setPlainText(node_info)

        # Conditions information
        if node.conditions:
            conditions_info = f"Node Conditions ({len(node.conditions)}):\n"
            for i, condition in enumerate(node.conditions, 1):
                lua_code = condition.to_lua()
                description = condition.get_display_text()
                negated_text = " (NEGATED)" if condition.negated else ""
                conditions_info += f"{i}. {description}{negated_text}\n   LUA: {lua_code}\n"
        else:
            conditions_info = "No node conditions defined."

        self.conditions_info_text.setPlainText(conditions_info)

        # Actions information
        if node.actions:
            actions_info = f"Node Actions ({len(node.actions)}):\n"
            for i, action in enumerate(node.actions, 1):
                lua_code = action.to_lua()
                description = action.get_display_text()
                actions_info += f"{i}. {description}\n   LUA: {lua_code}\n"
        else:
            actions_info = "No node actions defined."

        self.actions_info_text.setPlainText(actions_info)

    def on_search_changed(self, text: str):
        """Handle search text change"""
        self.search_text = text.lower()
        self.refresh_display()

    def on_display_options_changed(self):
        """Handle display options changes"""
        self.show_conditions = self.show_conditions_checkbox.isChecked()
        self.show_actions = self.show_actions_checkbox.isChecked()
        self.show_variables = self.show_variables_checkbox.isChecked()
        self.refresh_display()

    def on_cursor_changed(self):
        """Handle cursor position change"""
        # Could be implemented to show node details based on cursor position
        pass

    def validate_dialogue(self):
        """Validate the dialogue and show results"""
        issues = self.dialogue_tree.validate()

        if not issues:
            QMessageBox.information(self, "Validation Complete", "✅ Enhanced dialogue is valid!")
            self.status_label.setText("✅ Validation passed - no issues found")
        else:
            issue_text = "\n".join(f"• {issue}" for issue in issues)
            QMessageBox.warning(self, "Validation Issues", f"Found {len(issues)} issues:\n\n{issue_text}")
            self.status_label.setText(f"⚠️ Validation found {len(issues)} issues")

    def export_lua(self):
        """Export dialogue to LUA code"""
        try:
            lua_code = self.generate_lua_export()

            # Show export dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Export Enhanced LUA")
            dialog.setMinimumWidth(800)
            dialog.resize(900, 600)

            layout = QVBoxLayout(dialog)

            text_edit = QTextEdit()
            text_edit.setFont(QFont("Courier New", 10))
            text_edit.setPlainText(lua_code)
            layout.addWidget(text_edit)

            # Add validation section
            validation_group = QGroupBox("Validation Status")
            validation_layout = QVBoxLayout(validation_group)

            issues = self.dialogue_tree.validate()
            if not issues:
                validation_label = QLabel("✅ All validations passed!")
                validation_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 12px;")
            else:
                validation_label = QLabel(f"⚠️ {len(issues)} validation issues found")
                validation_label.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 12px;")

            validation_layout.addWidget(validation_label)
            layout.addWidget(validation_group)

            # Buttons
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            dialog.exec()

            self.status_label.setText(f"LUA export complete - {len(lua_code.split())} lines generated")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export LUA: {e}")
            self.status_label.setText(f"❌ Export error: {str(e)}")

    def generate_lua_export(self) -> str:
        """Generate enhanced LUA code for the dialogue"""
        lines = []
        lines.append("-- Enhanced Dialogue Script")
        lines.append("-- Generated with conditions, actions, and consequences")
        lines.append(f"-- Total nodes: {len(self.dialogue_tree.nodes)}")
        lines.append(f"-- Total choices: {sum(len(node.choices) for node in self.dialogue_tree.nodes.values())}")
        lines.append("")

        lines.append("function CreateStateMachine(_Type, _PlatformId, _NpcId, _X, _Y)")
        lines.append("BeginDefinition(_Type, _PlatformId, _NpcId, _X, _Y)")
        lines.append("")

        # Add comments for each section
        lines.append("--------------------------------------------------------------------------------")
        lines.append("-- DIALOGUE NODES WITH CONDITIONS AND ACTIONS")
        lines.append("--------------------------------------------------------------------------------")
        lines.append("")

        # Export all nodes with enhanced formatting
        for node_id, node in self.dialogue_tree.nodes.items():
            lines.extend(self._export_node_enhanced(node))
            lines.append("")

        lines.append("EndDefinition()")
        lines.append("end")
        lines.append("")

        return '\n'.join(lines)

    def _export_node_enhanced(self, node) -> List[str]:
        """Export a single node with enhanced LUA generation"""
        lines = []
        lines.append(f"-- Node: {node.node_id} ({node.node_type})")
        lines.append(f"-- Speaker: {node.speaker or 'N/A'}")

        # Export node conditions
        if node.conditions:
            lines.append("-- Node Conditions:")
            for condition in node.conditions:
                lua_condition = condition.to_lua()
                comment = f"-- {condition.get_display_text()}"
                if condition.negated:
                    lines.append(f"{lua_condition}, -- {comment} (NEGATED)")
                else:
                    lines.append(f"{lua_condition}, -- {comment}")

        if node.node_type in ["npc", "start"] or (not node.choices and node.node_type != "player"):
            # NPC or start node
            if not node.choices:
                # Simple node without choices
                if node.actions:
                    lines.append("OnOneTimeEvent{")
                    lines.append("    Conditions = {")
                    for condition in node.conditions:
                        lines.append(f"        {condition.to_lua()},")
                    lines.append("    },")
                    lines.append("    Actions = {")
                    lines.append(f"        Say{{Tag = \"{node.tag or node.node_id}\", String = \"{node.text}\"}},")
                    for action in node.actions:
                        lines.append(f"        {action.to_lua()},")
                    lines.append("    }")
                    lines.append("}")
                else:
                    lines.append(f"Say{{Tag = \"{node.tag or node.node_id}\", String = \"{node.text}\"}}")
            else:
                # Node with choices
                lines.append("OnBeginDialog{")
                lines.append("    Conditions = {")
                for condition in node.conditions:
                    lines.append(f"        {condition.to_lua()},")
                lines.append("    },")
                lines.append("    Actions = {")
                lines.append(f"        Say{{Tag = \"{node.tag or node.node_id}\", String = \"{node.text}\"}},")
                for action in node.actions:
                    lines.append(f"        {action.to_lua()},")
                lines.append("    }")
                lines.append("}")

                # Add choices
                for choice in node.choices:
                    lines.append(f"    Answer{{Tag = \"{node.tag or node.node_id}_choice_{choice.text[:20].replace(' ', '_')}\", String = \"{choice.text}\", AnswerId = {choice.choice_id or 'NIL'}}}")

        elif node.node_type == "response" and node.answer_id:
            # Response node
            lines.append(f"OnAnswer{{{node.answer_id};")
            lines.append("    Conditions = {")
            for condition in node.conditions:
                lines.append(f"        {condition.to_lua()},")
            lines.append("    },")
            lines.append("    Actions = {")
            lines.append(f"        Say{{Tag = \"{node.tag or node.node_id}\", String = \"{node.text}\"}},")
            for action in node.actions:
                lines.append(f"        {action.to_lua()},")
            lines.append("    }")
            lines.append("}")

        return lines

    def set_current_node(self, node_id: str):
        """Set the current node for detailed viewing"""
        self.selected_node_id = node_id
        self.update_node_details(node_id)
        self.node_selected.emit(node_id)


# Test function
def test_enhanced_text_mode_overview():
    """Test the enhanced text mode overview"""
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create enhanced dialogue data with conditions and actions
    test_data = {
        "nodes": [
            {
                "node_id": "guard_dialogue",
                "node_type": "npc",
                "speaker": "Town Guard",
                "text": "Halt, traveler! What brings you to our town?",
                "conditions": [
                    {
                        "condition_type": "global_flag",
                        "params": {"flag_name": "player_entered_town", "value": True},
                        "negated": False,
                        "description": "Player has entered town"
                    }
                ],
                "actions": [
                    {
                        "action_type": "play_sound",
                        "params": {"sound_id": 1501},
                        "description": "Play greeting sound"
                    }
                ],
                "choices": [
                    {
                        "choice_id": 1,
                        "text": "I'm looking for work. Do you have any quests?",
                        "next_node_id": "quest_offering",
                        "conditions": [
                            {
                                "condition_type": "player_level",
                                "params": {"level": 5, "comparison": ">="},
                                "negated": False,
                                "description": "Player level 5 or higher"
                            }
                        ],
                        "actions": [
                            {
                                "action_type": "set_global_flag",
                                "params": {"flag_name": "quest_requested", "value": True},
                                "description": "Mark quest as requested"
                            }
                        ]
                    },
                    {
                        "choice_id": 2,
                        "text": "Just passing through, nothing to see here.",
                        "next_node_id": "goodbye_response",
                        "conditions": [],
                        "actions": []
                    },
                    {
                        "choice_id": 3,
                        "text": "I'm new here and need directions.",
                        "next_node_id": "directions_response",
                        "conditions": [],
                        "actions": [
                            {
                                "action_type": "give_xp",
                                "params": {"amount": 10},
                                "description": "Give small XP bonus for asking"
                            }
                        ]
                    }
                ]
            },
            {
                "node_id": "quest_offering",
                "node_type": "response",
                "speaker": "Town Guard",
                "text": "Ah, an adventurer! We have some tasks that need doing.",
                "answer_id": 1,
                "conditions": [],
                "actions": [
                    {
                        "action_type": "quest_begin",
                        "params": {"quest_id": 501},
                        "description": "Begin the lost ring quest"
                    }
                ],
                "choices": [
                    {
                        "choice_id": 10,
                        "text": "Tell me about the quests available.",
                        "next_node_id": "quest_list",
                        "conditions": [],
                        "actions": []
                    },
                    {
                        "choice_id": 11,
                        "text": "I'll help you! What do you need?",
                        "next_node_id": "quest_assignment",
                        "conditions": [],
                        "actions": [
                            {
                                "action_type": "set_global_flag",
                                "params": {"flag_name": "player_accepted_quest", "value": True},
                                "description": "Mark player as quest-taker"
                            }
                        ]
                    }
                ]
            }
        ],
        "start_node_id": "guard_dialogue"
    }

    # Create and show enhanced text mode overview
    overview = EnhancedTextModeOverview()
    overview.set_dialogue_data(test_data)
    overview.setWindowTitle("Enhanced Text Mode Overview Test")
    overview.resize(1000, 700)
    overview.show()

    return app.exec()


if __name__ == "__main__":
    test_enhanced_text_mode_overview()