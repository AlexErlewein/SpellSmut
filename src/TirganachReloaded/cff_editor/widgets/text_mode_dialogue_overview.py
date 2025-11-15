#!/usr/bin/env python3
"""
Text Mode Dialogue Overview Widget

A keyboard-first, ASCII/text-based overview of dialogue trees that works
alongside the visual dialogue editor. Provides:
- Indented tree view of dialogue nodes
- Quick navigation and editing
- Bidirectional sync with visual editor
- Search and jump-to functionality
"""

import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QKeySequence,
    QShortcut,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
)
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTextEdit,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt


@dataclass
class DialogueNodeData:
    """Simplified dialogue node data for text mode"""

    id: str
    node_type: str  # "start", "npc", "player", "choice", "conditional", "end"
    speaker: str = ""
    text: str = ""
    choices: List[Dict[str, str]] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    next_nodes: List[str] = field(default_factory=list)
    answer_id: Optional[int] = None  # For OnAnswer{N; ...} patterns
    tag: str = ""  # Localization tag

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "node_type": self.node_type,
            "speaker": self.speaker,
            "text": self.text,
            "choices": self.choices,
            "conditions": self.conditions,
            "actions": self.actions,
            "next_nodes": self.next_nodes,
            "answer_id": self.answer_id,
            "tag": self.tag,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DialogueNodeData":
        """Create from dictionary"""
        return cls(
            id=data.get("id", ""),
            node_type=data.get("node_type", "npc"),
            speaker=data.get("speaker", ""),
            text=data.get("text", ""),
            choices=data.get("choices", []),
            conditions=data.get("conditions", []),
            actions=data.get("actions", []),
            next_nodes=data.get("next_nodes", []),
            answer_id=data.get("answer_id"),
            tag=data.get("tag", ""),
        )


class DialogueTextHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for dialogue text mode"""

    def __init__(self, document):
        super().__init__(document)
        self.setup_highlighting()

    def setup_highlighting(self):
        """Setup syntax highlighting rules"""
        # Node ID format
        node_id_format = QTextCharFormat()
        node_id_format.setForeground(QColor(41, 128, 185))  # Blue
        node_id_format.setFontWeight(QFont.Weight.Bold)
        self.node_id_pattern = r"#\d+|node_\w+|answer_\d+"

        # Speaker format
        speaker_format = QTextCharFormat()
        speaker_format.setForeground(QColor(39, 174, 96))  # Green
        speaker_format.setFontWeight(QFont.Weight.Bold)
        self.speaker_pattern = r"\(NPC\)|\(Player\)"

        # Choice format
        choice_format = QTextCharFormat()
        choice_format.setForeground(QColor(142, 68, 173))  # Purple
        self.choice_pattern = r"->\s*\[[A-Z]\]"

        # Action format
        action_format = QTextCharFormat()
        action_format.setForeground(QColor(230, 126, 34))  # Orange
        self.action_pattern = r"\(Action\):.*"

        # Error format
        error_format = QTextCharFormat()
        error_format.setForeground(QColor(231, 76, 60))  # Red
        error_format.setFontWeight(QFont.Weight.Bold)
        self.error_pattern = r"\[ERROR\].*"

        # Warning format
        warning_format = QTextCharFormat()
        warning_format.setForeground(QColor(243, 156, 18))  # Orange
        self.warning_pattern = r"\[WARN\].*"

        # Info format
        info_format = QTextCharFormat()
        info_format.setForeground(QColor(52, 152, 219))  # Light blue
        self.info_pattern = r"\[INFO\].*"

    def highlightBlock(self, text):
        """Apply syntax highlighting to a text block"""
        import re

        # Highlight node IDs
        for match in re.finditer(self.node_id_pattern, text):
            format = QTextCharFormat()
            format.setForeground(QColor(41, 128, 185))
            format.setFontWeight(QFont.Weight.Bold)
            self.setFormat(match.start(), match.end() - match.start(), format)

        # Highlight speakers
        for match in re.finditer(self.speaker_pattern, text):
            format = QTextCharFormat()
            format.setForeground(QColor(39, 174, 96))
            format.setFontWeight(QFont.Weight.Bold)
            self.setFormat(match.start(), match.end() - match.start(), format)

        # Highlight choices
        for match in re.finditer(self.choice_pattern, text):
            format = QTextCharFormat()
            format.setForeground(QColor(142, 68, 173))
            self.setFormat(match.start(), match.end() - match.start(), format)

        # Highlight actions
        for match in re.finditer(self.action_pattern, text):
            format = QTextCharFormat()
            format.setForeground(QColor(230, 126, 34))
            self.setFormat(match.start(), match.end() - match.start(), format)

        # Highlight errors
        for match in re.finditer(self.error_pattern, text):
            format = QTextCharFormat()
            format.setForeground(QColor(231, 76, 60))
            format.setFontWeight(QFont.Weight.Bold)
            self.setFormat(match.start(), match.end() - match.start(), format)

        # Highlight warnings
        for match in re.finditer(self.warning_pattern, text):
            format = QTextCharFormat()
            format.setForeground(QColor(243, 156, 18))
            self.setFormat(match.start(), match.end() - match.start(), format)

        # Highlight info
        for match in re.finditer(self.info_pattern, text):
            format = QTextCharFormat()
            format.setForeground(QColor(52, 152, 219))
            self.setFormat(match.start(), match.end() - match.start(), format)


class TextModeDialogueOverview(QWidget):
    """Text mode overview widget for dialogue trees"""

    # Signals
    node_selected = Signal(str)  # node_id
    node_edited = Signal(str, dict)  # node_id, node_data
    node_added = Signal(str, dict)  # node_id, node_data
    node_deleted = Signal(str)  # node_id
    jump_to_visual = Signal(str)  # node_id - request to jump to node in visual editor
    choice_selected = Signal(
        str, int
    )  # node_id, choice_index - for connecting choices to responses

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes: Dict[str, DialogueNodeData] = {}
        self.node_hierarchy: Dict[str, List[str]] = {}  # parent_id -> [child_ids]
        self.selected_node_id: Optional[str] = None
        self.selected_choice_node_id: Optional[str] = None
        self.selected_choice_index: int = -1
        self.search_text: str = ""
        self.filter_speaker: str = "All"

        self.setup_ui()
        self.setup_shortcuts()
        self.setup_connections()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(toolbar)

        # Search and filter
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(5, 5, 5, 5)

        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search nodes...")
        self.search_edit.setMaximumWidth(200)
        search_layout.addWidget(self.search_edit)

        search_layout.addWidget(QLabel("Speaker:"))
        self.speaker_filter = QComboBox()
        self.speaker_filter.addItems(["All", "NPC", "Player"])
        self.speaker_filter.setMaximumWidth(100)
        search_layout.addWidget(self.speaker_filter)

        search_layout.addStretch()

        # Action buttons
        self.add_node_btn = QPushButton("+ Add Node")
        self.add_node_btn.setMaximumWidth(100)
        search_layout.addWidget(self.add_node_btn)

        self.add_response_btn = QPushButton("💬 Add Response")
        self.add_response_btn.setMaximumWidth(110)
        self.add_response_btn.setToolTip(
            "Quickly add an NPC response to the selected choice"
        )
        self.add_response_btn.setEnabled(False)  # Disabled until a choice is selected
        search_layout.addWidget(self.add_response_btn)

        self.jump_to_visual_btn = QPushButton("🔍 Jump to Visual")
        self.jump_to_visual_btn.setMaximumWidth(120)
        search_layout.addWidget(self.jump_to_visual_btn)

        layout.addWidget(search_frame)

        # Main content area - splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left: Tree view (optional, for navigation)
        tree_frame = QFrame()
        tree_layout = QVBoxLayout(tree_frame)
        tree_layout.setContentsMargins(0, 0, 0, 0)

        tree_label = QLabel("Node Tree")
        tree_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        tree_layout.addWidget(tree_label)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Node ID", "Type", "Speaker"])
        self.tree_widget.setMaximumWidth(250)
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        tree_layout.addWidget(self.tree_widget)

        splitter.addWidget(tree_frame)

        # Center: ASCII text view
        text_frame = QFrame()
        text_layout = QVBoxLayout(text_frame)
        text_layout.setContentsMargins(0, 0, 0, 0)

        text_label = QLabel("Dialogue Tree (Text Mode)")
        text_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        text_layout.addWidget(text_label)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)  # Start as read-only, can make editable later
        self.text_edit.setFont(QFont("Courier New", 10))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 3px;
            }
        """)

        # Setup syntax highlighter
        self.highlighter = DialogueTextHighlighter(self.text_edit.document())

        text_layout.addWidget(self.text_edit)
        splitter.addWidget(text_frame)

        # Right: Node details (optional)
        details_frame = QFrame()
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(0, 0, 0, 0)

        details_label = QLabel("Node Details")
        details_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        details_layout.addWidget(details_label)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumWidth(300)
        self.details_text.setFont(QFont("Arial", 9))
        details_layout.addWidget(self.details_text)

        splitter.addWidget(details_frame)

        # Set splitter sizes
        splitter.setSizes([200, 600, 250])

        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        self.status_bar.showMessage("Ready - No dialogue loaded")

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Search
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.focus_search)

        # Jump to node
        jump_shortcut = QShortcut(QKeySequence("Ctrl+J"), self)
        jump_shortcut.activated.connect(self.jump_to_selected_node)

        # Refresh
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.refresh_view)

    def setup_connections(self):
        """Setup signal connections"""
        self.search_edit.textChanged.connect(self.on_search_changed)
        self.speaker_filter.currentTextChanged.connect(self.on_filter_changed)
        self.add_node_btn.clicked.connect(self.on_add_node)
        self.add_response_btn.clicked.connect(self.on_add_response)
        self.jump_to_visual_btn.clicked.connect(self.on_jump_to_visual)
        self.text_edit.cursorPositionChanged.connect(self.on_cursor_changed)

        # Connect mouse press for choice selection
        self.text_edit.mousePressEvent = self._text_mouse_press_event

    def _text_mouse_press_event(self, event):
        """Custom mouse press event for text edit to handle choice selection"""
        # Call the original mouse press event first
        QTextEdit.mousePressEvent(self.text_edit, event)

        # Then handle our custom choice selection
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_text_clicked(event.pos())

    def set_dialogue_data(self, dialogue_data: Dict[str, Any]):
        """Set dialogue data from dictionary (compatible with visual editor format)"""
        self.nodes.clear()
        self.node_hierarchy.clear()

        if not dialogue_data or "nodes" not in dialogue_data:
            self.refresh_view()
            return

        # Load nodes
        for node_data in dialogue_data["nodes"]:
            node = DialogueNodeData.from_dict(node_data)
            self.nodes[node.id] = node

            # Build hierarchy
            for next_id in node.next_nodes:
                if next_id not in self.node_hierarchy:
                    self.node_hierarchy[next_id] = []
                # Track parent-child relationships
                if node.id not in self.node_hierarchy:
                    self.node_hierarchy[node.id] = []
                self.node_hierarchy[node.id].append(next_id)

        # Build connections from visual editor format
        if "connections" in dialogue_data:
            for conn in dialogue_data["connections"]:
                from_id = conn.get("from")
                to_id = conn.get("to")
                if from_id and to_id and from_id in self.nodes:
                    if from_id not in self.node_hierarchy:
                        self.node_hierarchy[from_id] = []
                    if to_id not in self.node_hierarchy[from_id]:
                        self.node_hierarchy[from_id].append(to_id)
                    # Update next_nodes
                    if to_id not in self.nodes[from_id].next_nodes:
                        self.nodes[from_id].next_nodes.append(to_id)

        self.refresh_view()
        self.status_bar.showMessage(f"Loaded {len(self.nodes)} dialogue nodes")

    def get_dialogue_data(self) -> Dict[str, Any]:
        """Get dialogue data as dictionary (compatible with visual editor format)"""
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "connections": self._build_connections(),
        }

    def _build_connections(self) -> List[Dict[str, str]]:
        """Build connections list from node hierarchy"""
        connections = []
        for parent_id, child_ids in self.node_hierarchy.items():
            for child_id in child_ids:
                connections.append({"from": parent_id, "to": child_id})
        return connections

    def refresh_view(self):
        """Refresh the text view"""
        if not self.nodes:
            self.text_edit.setPlainText(
                "No dialogue nodes. Click '+ Add Node' to create one."
            )
            self.tree_widget.clear()
            return

        # Generate ASCII tree
        ascii_tree = self._generate_ascii_tree()
        self.text_edit.setPlainText(ascii_tree)

        # Update tree widget
        self._update_tree_widget()

    def _generate_ascii_tree(self) -> str:
        """Generate ASCII representation of dialogue tree"""
        lines = []
        lines.append("=" * 80)
        lines.append("DIALOGUE TREE OVERVIEW")
        lines.append("=" * 80)
        lines.append("")  # Empty line for spacing

        # Find start node
        start_node = None
        for node in self.nodes.values():
            if node.node_type == "start" or node.node_type == "START":
                start_node = node
                break

        if not start_node:
            # If no start node, use first node or show all nodes
            if self.nodes:
                start_node = list(self.nodes.values())[0]
            else:
                lines.append("No dialogue nodes found.")
                return "\n".join(lines)

        # Build tree recursively
        visited = set()
        self._build_tree_lines(start_node.id, lines, visited, "", True, 0)

        # Add any unvisited nodes
        unvisited = set(self.nodes.keys()) - visited
        if unvisited:
            lines.append("")
            lines.append("Unconnected nodes:")
            for node_id in unvisited:
                node = self.nodes[node_id]
                lines.append(f"  {self._format_node(node, 0)}")

        return "\n".join(lines)

    def _build_tree_lines(
        self,
        node_id: str,
        lines: List[str],
        visited: Set[str],
        prefix: str,
        is_last: bool,
        depth: int,
    ):
        """Build tree lines recursively"""
        if node_id in visited:
            lines.append(f"{prefix}[CYCLE: {node_id}]")
            return

        if node_id not in self.nodes:
            lines.append(f"{prefix}[MISSING: {node_id}]")
            return

        visited.add(node_id)
        node = self.nodes[node_id]

        # Format node
        node_line = self._format_node(node, depth)
        lines.append(f"{prefix}{node_line}")

        # Get children
        children = self.node_hierarchy.get(node_id, [])
        if not children and node.next_nodes:
            children = node.next_nodes

        # Add children
        for i, child_id in enumerate(children):
            is_last_child = i == len(children) - 1
            child_prefix = prefix + ("    " if is_last else "│   ")
            tree_prefix = "└── " if is_last_child else "├── "
            self._build_tree_lines(
                child_id,
                lines,
                visited,
                child_prefix + tree_prefix,
                is_last_child,
                depth + 1,
            )

    def _format_node(self, node: DialogueNodeData, depth: int) -> str:
        """Format a single node for display"""
        indent = "  " * depth

        # Node ID
        node_id_display = f"#{node.id}" if not node.id.startswith("#") else node.id

        # Speaker
        speaker_display = ""
        if node.speaker:
            speaker_display = f"({node.speaker}) "
        elif node.node_type.lower() in ["npc", "start"]:
            speaker_display = "(NPC) "
        elif node.node_type.lower() == "player":
            speaker_display = "(Player) "

        # Text preview (first 50 chars)
        text_preview = node.text[:50] + "..." if len(node.text) > 50 else node.text
        if not text_preview:
            text_preview = "[No text]"

        # Answer ID for OnAnswer patterns
        answer_id_display = ""
        if node.answer_id is not None:
            answer_id_display = f" [AnswerId={node.answer_id}]"

        # Format line
        line = f"{node_id_display}  {speaker_display}{text_preview}{answer_id_display}"

        # Add choices if present
        if node.choices:
            connected_count = sum(
                1 for choice in node.choices if choice.get("next_node")
            )
            total_count = len(node.choices)
            line += (
                f"\n{indent}    ┌─ Choices ({connected_count}/{total_count} connected):"
            )

            for i, choice in enumerate(node.choices):
                choice_text = choice.get("text", "")
                choice_label = chr(65 + i)  # A, B, C, ...
                next_node = choice.get("next_node", "")

                # Use different symbols for connected vs unconnected choices
                connector = "└─" if i == len(node.choices) - 1 else "├─"
                status_icon = "✓" if next_node else "○"

                choice_line = f"\n{indent}    {connector} [{choice_label}] {status_icon} {choice_text[:35]}"
                if len(choice_text) > 35:
                    choice_line += "..."

                if next_node:
                    choice_line += f" → {next_node}"
                else:
                    choice_line += f" → [UNCONNECTED]"

                line += choice_line

        # Add actions if present
        if node.actions:
            for action in node.actions[:3]:  # Show first 3 actions
                action_preview = str(action)[:40]
                line += f"\n{indent}    (Action): {action_preview}"
            if len(node.actions) > 3:
                line += f"\n{indent}    ... and {len(node.actions) - 3} more actions"

        # Add validation indicators
        validation_issues = self._validate_node(node)
        if validation_issues:
            for issue_type, issue_text in validation_issues:
                if issue_type == "error":
                    line += f"\n{indent}    [ERROR] {issue_text}"
                elif issue_type == "warning":
                    line += f"\n{indent}    [WARN] {issue_text}"
                elif issue_type == "info":
                    line += f"\n{indent}    [INFO] {issue_text}"

        return line

    def _validate_node(self, node: DialogueNodeData) -> List[Tuple[str, str]]:
        """Validate a node and return list of issues"""
        issues = []

        # Check for empty text (except for start/end nodes)
        if not node.text.strip() and node.node_type.lower() not in ["start", "end"]:
            issues.append(("warning", "Empty text"))

        # Check for missing speaker (except for choice/conditional nodes)
        if not node.speaker and node.node_type.lower() not in [
            "choice",
            "conditional",
            "start",
            "end",
        ]:
            issues.append(("warning", "No speaker assigned"))

        # Check for invalid next nodes
        for next_id in node.next_nodes:
            if next_id not in self.nodes:
                issues.append(("error", f"Invalid next node: {next_id}"))

        # Check for choices without next nodes
        for choice in node.choices:
            next_node = choice.get("next_node", "")
            if next_node and next_node not in self.nodes:
                issues.append(
                    ("warning", f"Choice points to invalid node: {next_node}")
                )

        return issues

    def _update_tree_widget(self):
        """Update the tree widget"""
        self.tree_widget.clear()

        if not self.nodes:
            return

        # Find start node
        start_node = None
        for node in self.nodes.values():
            if node.node_type.lower() == "start":
                start_node = node
                break

        if not start_node and self.nodes:
            start_node = list(self.nodes.values())[0]

        if start_node:
            self._add_tree_item(None, start_node, set())

        # Add any unvisited nodes
        visited = set()
        if start_node:
            self._collect_visited(start_node.id, visited)

        for node_id, node in self.nodes.items():
            if node_id not in visited:
                self._add_tree_item(None, node, set())

    def _add_tree_item(
        self,
        parent: Optional[QTreeWidgetItem],
        node: DialogueNodeData,
        visited: Set[str],
    ):
        """Add tree item recursively"""
        if node.id in visited:
            return

        visited.add(node.id)

        item = QTreeWidgetItem([node.id, node.node_type.upper(), node.speaker or "N/A"])
        item.setData(0, Qt.ItemDataRole.UserRole, node.id)

        if parent:
            parent.addChild(item)
        else:
            self.tree_widget.addTopLevelItem(item)

        # Add children
        children = self.node_hierarchy.get(node.id, [])
        if not children and node.next_nodes:
            children = node.next_nodes

        for child_id in children:
            if child_id in self.nodes:
                child_node = self.nodes[child_id]
                self._add_tree_item(item, child_node, visited)

    def _collect_visited(self, node_id: str, visited: Set[str]):
        """Collect all visited nodes from a starting node"""
        if node_id in visited or node_id not in self.nodes:
            return

        visited.add(node_id)
        node = self.nodes[node_id]

        children = self.node_hierarchy.get(node_id, [])
        if not children and node.next_nodes:
            children = node.next_nodes

        for child_id in children:
            self._collect_visited(child_id, visited)

    def on_search_changed(self, text: str):
        """Handle search text change"""
        self.search_text = text.lower()
        self.refresh_view()

    def on_filter_changed(self, speaker: str):
        """Handle speaker filter change"""
        self.filter_speaker = speaker
        self.refresh_view()

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item click"""
        node_id = item.data(0, Qt.ItemDataRole.UserRole)
        if node_id:
            self.select_node(node_id)

    def select_node(self, node_id: str):
        """Select a node"""
        if node_id in self.nodes:
            self.selected_node_id = node_id
            node = self.nodes[node_id]

            # Update details
            details = self._format_node_details(node)
            self.details_text.setPlainText(details)

            # Scroll to node in text view
            self._scroll_to_node(node_id)

            # Emit signal
            self.node_selected.emit(node_id)

            self.status_bar.showMessage(f"Selected node: {node_id}")

    def _format_node_details(self, node: DialogueNodeData) -> str:
        """Format node details for display"""
        lines = []
        lines.append(f"Node ID: {node.id}")
        lines.append(f"Type: {node.node_type}")
        lines.append(f"Speaker: {node.speaker or 'N/A'}")
        lines.append(f"Tag: {node.tag or 'N/A'}")
        if node.answer_id is not None:
            lines.append(f"Answer ID: {node.answer_id}")
        lines.append("")
        lines.append(f"Text:")
        lines.append(node.text or "[No text]")
        lines.append("")

        if node.choices:
            lines.append("Choices:")
            for i, choice in enumerate(node.choices):
                choice_label = chr(65 + i)
                lines.append(f"  [{choice_label}] {choice.get('text', '')}")
                if choice.get("next_node"):
                    lines.append(f"    -> {choice.get('next_node')}")
            lines.append("")

        if node.conditions:
            lines.append("Conditions:")
            for condition in node.conditions:
                lines.append(f"  - {condition}")
            lines.append("")

        if node.actions:
            lines.append("Actions:")
            for action in node.actions:
                lines.append(f"  - {action}")
            lines.append("")

        if node.next_nodes:
            lines.append("Next Nodes:")
            for next_id in node.next_nodes:
                lines.append(f"  -> {next_id}")

        return "\n".join(lines)

    def _scroll_to_node(self, node_id: str):
        """Scroll to node in text view"""
        # Find node in text
        text = self.text_edit.toPlainText()
        node_pattern = f"#{node_id}" if not node_id.startswith("#") else node_id

        # Find position
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        # Search for node
        if node_pattern in text:
            position = text.find(node_pattern)
            cursor.setPosition(position)
            self.text_edit.setTextCursor(cursor)
            self.text_edit.ensureCursorVisible()

    def on_cursor_changed(self):
        """Handle cursor position change"""
        # Could implement node selection based on cursor position
        pass

    def on_text_clicked(self, position):
        """Handle clicks on the text view to detect choice selection"""
        cursor = self.text_edit.cursorForPosition(position)
        line = cursor.block().text()

        # Check if this line contains a choice
        if (
            "[A]" in line
            or "[B]" in line
            or "[C]" in line
            or "[D]" in line
            or "[E]" in line
        ):
            # Extract choice letter and find the node
            for i, letter in enumerate(["A", "B", "C", "D", "E"]):
                if f"[{letter}]" in line:
                    choice_index = i
                    # Find which node this choice belongs to by looking backwards
                    current_block = cursor.block()
                    node_id = None

                    # Look up to 10 lines back for a node ID
                    for _ in range(10):
                        current_block = current_block.previous()
                        if not current_block.isValid():
                            break

                        block_text = current_block.text()
                        # Look for node ID pattern like #node_123 or #answer_456
                        import re

                        node_match = re.search(r"#(\w+)", block_text)
                        if node_match:
                            node_id = node_match.group(1)
                            if not node_id.startswith(
                                "node_"
                            ) and not node_id.startswith("answer_"):
                                node_id = (
                                    f"node_{node_id}" if node_id.isdigit() else node_id
                                )
                            break

                    if node_id and node_id in self.nodes:
                        node = self.nodes[node_id]
                        if choice_index < len(node.choices):
                            # Track selected choice for quick response feature
                            self.selected_choice_node_id = node_id
                            self.selected_choice_index = choice_index
                            self.add_response_btn.setEnabled(True)

                            self.choice_selected.emit(node_id, choice_index)
                            self.status_bar.showMessage(
                                f"Selected choice {letter} for node {node_id} - Click 'Add Response' to create NPC response"
                            )
                            return

        # If not a choice, try to select the node this line belongs to
        cursor = self.text_edit.textCursor()
        line_text = cursor.block().text()

        # Look for node ID in current line
        import re

        node_match = re.search(r"#(\w+)", line_text)
        if node_match:
            node_id = node_match.group(1)
            if not node_id.startswith("node_") and not node_id.startswith("answer_"):
                node_id = f"node_{node_id}" if node_id.isdigit() else node_id

            if node_id in self.nodes:
                self.select_node(node_id)

    def on_add_node(self):
        """Add a new node"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Dialogue Node")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        form = QFormLayout()

        # Node type
        node_type_combo = QComboBox()
        node_type_combo.addItems(
            ["NPC", "Player", "Choice", "Conditional", "Start", "End"]
        )
        # Default to NPC for new dialogues (most common starting point)
        node_type_combo.setCurrentText("NPC")
        form.addRow("Node Type:", node_type_combo)

        # Node ID
        node_id_edit = QLineEdit()
        node_id_edit.setPlaceholderText("node_001")
        form.addRow("Node ID:", node_id_edit)

        # Speaker
        speaker_edit = QLineEdit()
        speaker_edit.setPlaceholderText("NPC name or 'Player'")
        form.addRow("Speaker:", speaker_edit)

        # Text
        text_edit = QTextEdit()
        text_edit.setMaximumHeight(100)
        text_edit.setPlaceholderText("Dialogue text...")
        form.addRow("Text:", text_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            node_type = node_type_combo.currentText().lower()
            node_id = (
                node_id_edit.text().strip() or f"{node_type}_{len(self.nodes) + 1}"
            )
            speaker = speaker_edit.text().strip()
            text = text_edit.toPlainText().strip()

            # Check if node ID already exists
            if node_id in self.nodes:
                QMessageBox.warning(
                    self, "Error", f"Node ID '{node_id}' already exists!"
                )
                return

            # Create node
            node = DialogueNodeData(
                id=node_id, node_type=node_type, speaker=speaker, text=text
            )

            # Add node to collection
            self.nodes[node_id] = node

            # Auto-connect to previous node if one exists
            if self.selected_node_id and self.selected_node_id in self.nodes:
                # Connect the new node after the selected node
                selected_node = self.nodes[self.selected_node_id]
                if node_id not in selected_node.next_nodes:
                    selected_node.next_nodes.append(node_id)

                # Update hierarchy
                if self.selected_node_id not in self.node_hierarchy:
                    self.node_hierarchy[self.selected_node_id] = []
                if node_id not in self.node_hierarchy[self.selected_node_id]:
                    self.node_hierarchy[self.selected_node_id].append(node_id)

                self.status_bar.showMessage(
                    f"Added node: {node_id} (connected after {self.selected_node_id})"
                )
            elif self.nodes:
                # If no selection but nodes exist, connect to the last added node
                # Find the most recently added node
                sorted_nodes = sorted(self.nodes.keys(), key=lambda x: x)
                if sorted_nodes:
                    last_node_id = sorted_nodes[-1]
                    last_node = self.nodes[last_node_id]
                    if node_id not in last_node.next_nodes:
                        last_node.next_nodes.append(node_id)

                    # Update hierarchy
                    if last_node_id not in self.node_hierarchy:
                        self.node_hierarchy[last_node_id] = []
                    if node_id not in self.node_hierarchy[last_node_id]:
                        self.node_hierarchy[last_node_id].append(node_id)

                    self.status_bar.showMessage(
                        f"Added node: {node_id} (connected after {last_node_id})"
                    )
            else:
                self.status_bar.showMessage(f"Added node: {node_id}")

            # Emit signal to notify other components (like visual editor)
            self.node_added.emit(node_id, node.to_dict())

            # Refresh the view to show the new node
            self.refresh_view()

    def on_add_response(self):
        """Quickly add an NPC response to the selected choice"""
        if self.selected_choice_node_id is None or self.selected_choice_index < 0:
            QMessageBox.information(
                self,
                "No Choice Selected",
                "Please click on a choice option (like [A], [B], etc.) in the dialogue tree to select it first.",
            )
            return

        choice_node_id = self.selected_choice_node_id
        choice_index = self.selected_choice_index

        if choice_node_id not in self.nodes:
            return

        node = self.nodes[choice_node_id]
        if choice_index >= len(node.choices):
            return

        choice = node.choices[choice_index]

        # Create a quick response dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Add Response to Choice '{choice.get('text', '')}'")
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Instructions
        instructions = QLabel("Create a quick NPC response for this player choice:")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        form = QFormLayout()

        # Response speaker
        speaker_edit = QLineEdit("NPC")
        speaker_edit.setPlaceholderText(
            "Who is responding? (e.g., NPC, Guard, Merchant)"
        )
        form.addRow("Speaker:", speaker_edit)

        # Response text
        response_edit = QTextEdit()
        response_edit.setPlaceholderText("What does the character say in response?")
        response_edit.setMaximumHeight(80)
        form.addRow("Response:", response_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            speaker = speaker_edit.text().strip() or "NPC"
            response_text = response_edit.toPlainText().strip()

            if response_text:
                # Generate response node ID
                response_id = f"response_{choice_node_id}_choice_{choice_index}"

                # Ensure unique ID
                counter = 1
                original_id = response_id
                while response_id in self.nodes:
                    response_id = f"{original_id}_{counter}"
                    counter += 1

                # Create response node
                response_node = DialogueNodeData(
                    id=response_id, node_type="npc", speaker=speaker, text=response_text
                )

                # Connect the choice to this response
                choice["next_node"] = response_id

                # Update hierarchy
                if choice_node_id not in self.node_hierarchy:
                    self.node_hierarchy[choice_node_id] = []
                if response_id not in self.node_hierarchy[choice_node_id]:
                    self.node_hierarchy[choice_node_id].append(response_id)

                self.nodes[response_id] = response_node
                self.refresh_view()

                # Select the new response
                self.select_node(response_id)

                # Emit signal
                self.node_added.emit(response_id, response_node.to_dict())

                self.status_bar.showMessage(f"Added response: {response_id}")
            else:
                QMessageBox.warning(
                    self, "Empty Response", "Please enter some response text."
                )

    def on_jump_to_visual(self):
        """Jump to selected node in visual editor"""
        if self.selected_node_id:
            self.jump_to_visual.emit(self.selected_node_id)
        else:
            QMessageBox.information(self, "No Selection", "Please select a node first.")

    def focus_search(self):
        """Focus the search box"""
        self.search_edit.setFocus()
        self.search_edit.selectAll()

    def jump_to_selected_node(self):
        """Jump to selected node"""
        if self.selected_node_id:
            self._scroll_to_node(self.selected_node_id)

    def update_node(self, node_id: str, node_data: Dict[str, Any]):
        """Update a node"""
        if node_id in self.nodes:
            # Update node data
            updated_node = DialogueNodeData.from_dict(node_data)
            self.nodes[node_id] = updated_node

            # Refresh view
            self.refresh_view()

            # Emit signal
            self.node_edited.emit(node_id, node_data)

            self.status_bar.showMessage(f"Updated node: {node_id}")

    def connect_choice_to_response(
        self, choice_node_id: str, choice_index: int, response_node_id: str
    ):
        """Connect a player choice to an NPC response"""
        if choice_node_id in self.nodes:
            node = self.nodes[choice_node_id]
            if choice_index < len(node.choices):
                # Update the choice to point to the response
                node.choices[choice_index]["next_node"] = response_node_id

                # Update the hierarchy
                if choice_node_id not in self.node_hierarchy:
                    self.node_hierarchy[choice_node_id] = []
                if response_node_id not in self.node_hierarchy[choice_node_id]:
                    self.node_hierarchy[choice_node_id].append(response_node_id)

                # Refresh the view
                self.refresh_view()

                # Emit change signal
                self.node_edited.emit(choice_node_id, node.to_dict())

                self.status_bar.showMessage(
                    f"Connected choice {chr(65 + choice_index)} to response {response_node_id}"
                )

    def delete_node(self, node_id: str):
        """Delete a node"""
        if node_id in self.nodes:
            # Remove from nodes
            del self.nodes[node_id]

            # Remove from hierarchy
            if node_id in self.node_hierarchy:
                del self.node_hierarchy[node_id]

            # Remove from other nodes' next_nodes
            for node in self.nodes.values():
                if node_id in node.next_nodes:
                    node.next_nodes.remove(node_id)

            # Remove from hierarchy entries
            for parent_id, children in list(self.node_hierarchy.items()):
                if node_id in children:
                    children.remove(node_id)

            # Clear selection if deleted node was selected
            if self.selected_node_id == node_id:
                self.selected_node_id = None
                self.details_text.clear()

            # Refresh view
            self.refresh_view()

            # Emit signal
            self.node_deleted.emit(node_id)

            self.status_bar.showMessage(f"Deleted node: {node_id}")


# Test function
def test_text_mode_overview():
    """Test the text mode overview widget"""
    from PySide6.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Text Mode Dialogue Overview Test")
    window.resize(1200, 800)

    overview = TextModeDialogueOverview()
    window.setCentralWidget(overview)

    # Load sample data
    sample_data = {
        "nodes": [
            {
                "id": "node_001",
                "node_type": "npc",
                "speaker": "Rolf",
                "text": "Greetings, traveler.",
                "choices": [],
                "conditions": [],
                "actions": [],
                "next_nodes": ["node_002"],
                "answer_id": None,
                "tag": "rolf_001",
            },
            {
                "id": "node_002",
                "node_type": "player",
                "speaker": "Player",
                "text": "Need help?",
                "choices": [
                    {"text": "I'll find it.", "next_node": "node_003"},
                    {"text": "Not interested.", "next_node": "node_004"},
                ],
                "conditions": [],
                "actions": [],
                "next_nodes": [],
                "answer_id": 1,
                "tag": "player_001",
            },
            {
                "id": "node_003",
                "node_type": "npc",
                "speaker": "Rolf",
                "text": "I've lost my hammer.",
                "choices": [],
                "conditions": [],
                "actions": [{"type": "AddObjective", "text": "Find Hammer"}],
                "next_nodes": [],
                "answer_id": None,
                "tag": "rolf_002",
            },
            {
                "id": "node_004",
                "node_type": "npc",
                "speaker": "Rolf",
                "text": "Very well.",
                "choices": [],
                "conditions": [],
                "actions": [],
                "next_nodes": [],
                "answer_id": None,
                "tag": "rolf_003",
            },
        ],
        "connections": [
            {"from": "node_001", "to": "node_002"},
            {"from": "node_002", "to": "node_003"},
            {"from": "node_002", "to": "node_004"},
        ],
    }

    overview.set_dialogue_data(sample_data)

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(test_text_mode_overview())
