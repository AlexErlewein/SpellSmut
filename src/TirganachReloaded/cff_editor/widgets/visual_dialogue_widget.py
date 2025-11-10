#!/usr/bin/env python3
"""
Visual Dialogue Widget

A widget version of the visual dialogue editor that can be embedded
in the unified quest editor as a tab.
"""

import sys
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget,
    QTreeWidgetItem, QTextEdit, QLineEdit, QSpinBox, QComboBox,
    QPushButton, QLabel, QGroupBox, QFormLayout, QListWidget,
    QListWidgetItem, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QGraphicsView, QGraphicsScene, QToolBar,
    QStatusBar, QScrollArea, QFrame, QApplication, QDialog,
    QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import (
    QFont, QPixmap, QIcon, QAction, QKeySequence, QPen,
    QBrush, QPainter, QColor, QPolygonF
)

# Import from visual_dialogue_editor
try:
    from visual_dialogue_editor import (
        DialogueNode, NodeType, DialogueNodeItem, DialogueConnectionItem,
        DialogueGraphicsView, DialoguePropertiesWidget, DialogueTreeWidget
    )
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Fallback for standalone testing
    import logging
    logger = logging.getLogger(__name__)

    # Define fallback classes
    @dataclass
    class DialogueNode:
        id: str
        node_type: str
        speaker: str = ""
        text: str = ""
        choices: List[Dict[str, str]] = None
        conditions: List[str] = None
        actions: List[str] = None
        position: Tuple[float, float] = (0.0, 0.0)
        next_nodes: List[str] = None

    class NodeType:
        START = "start"
        END = "end"
        NPC = "npc"
        PLAYER = "player"
        CHOICE = "choice"
        CONDITIONAL = "conditional"

    # Create stub classes
    class DialogueNodeItem:
        def __init__(self, node):
            self.node = node

    class DialogueConnectionItem:
        def __init__(self, start_node, end_node):
            self.start_node = start_node
            self.end_node = end_node


class VisualDialogueWidget(QWidget):
    """Widget version of the visual dialogue editor"""

    # Signals
    dialogue_changed = Signal(dict)  # Emitted when dialogue data changes

    def __init__(self):
        super().__init__()
        self.nodes = {}
        self.selected_node = None

        self.setup_ui()
        self.setup_toolbar()

        logger.info("Visual Dialogue Widget initialized")

    def setup_ui(self):
        """Setup the main UI"""
        # Create main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create toolbar
        self.toolbar = QToolBar()
        main_layout.addWidget(self.toolbar)

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Node palette and tree view
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # Node palette
        self.setup_node_palette(left_layout)

        # Tree view
        self.tree_widget = DialogueTreeWidget()
        self.tree_widget.node_selected.connect(self.select_node)
        left_layout.addWidget(self.tree_widget)

        splitter.addWidget(left_panel)

        # Center - Graphics view
        self.scene = QGraphicsScene()
        self.graphics_view = DialogueGraphicsView(self.scene)
        self.graphics_view.node_selected.connect(self.on_node_selected)
        splitter.addWidget(self.graphics_view)

        # Right panel - Properties
        self.properties_widget = DialoguePropertiesWidget()
        self.properties_widget.properties_changed.connect(self.on_properties_changed)
        splitter.addWidget(self.properties_widget)

        # Set splitter sizes
        splitter.setSizes([250, 700, 350])

        # Status bar (at bottom)
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_node_palette(self, layout):
        """Setup node palette"""
        palette_group = QGroupBox("Node Palette")
        palette_layout = QVBoxLayout()

        # Node type buttons
        self.start_btn = QPushButton("🟢 Start Node")
        self.start_btn.clicked.connect(lambda: self.add_node(NodeType.START))
        self.start_btn.setToolTip("Starting point of your dialogue tree\nEvery conversation begins here")
        palette_layout.addWidget(self.start_btn)

        self.npc_btn = QPushButton("👤 NPC Dialogue")
        self.npc_btn.clicked.connect(lambda: self.add_node(NodeType.NPC))
        self.npc_btn.setToolTip("NPC speaks to the player\nAdd dialogue text for characters")
        palette_layout.addWidget(self.npc_btn)

        self.player_btn = QPushButton("🗣️ Player Dialogue")
        self.player_btn.clicked.connect(lambda: self.add_node(NodeType.PLAYER))
        self.player_btn.setToolTip("Player response options\nWhat the player can say back")
        palette_layout.addWidget(self.player_btn)

        self.choice_btn = QPushButton("🔀 Choice Node")
        self.choice_btn.clicked.connect(lambda: self.add_node(NodeType.CHOICE))
        self.choice_btn.setToolTip("Branching dialogue choices\nCreate multiple conversation paths")
        palette_layout.addWidget(self.choice_btn)

        self.conditional_btn = QPushButton("❓ Conditional Node")
        self.conditional_btn.clicked.connect(lambda: self.add_node(NodeType.CONDITIONAL))
        self.conditional_btn.setToolTip("Conditional dialogue\nShow different text based on conditions")
        palette_layout.addWidget(self.conditional_btn)

        self.end_btn = QPushButton("🔴 End Node")
        self.end_btn.clicked.connect(lambda: self.add_node(NodeType.END))
        self.end_btn.setToolTip("End of conversation\nWhere dialogue paths conclude")
        palette_layout.addWidget(self.end_btn)

        # Spacer
        palette_layout.addWidget(QLabel(""))

        # Action buttons
        self.connection_btn = QPushButton("Create Connection")
        self.connection_btn.clicked.connect(self.create_connection_mode)
        palette_layout.addWidget(self.connection_btn)

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected_node)
        palette_layout.addWidget(self.delete_btn)

        palette_group.setLayout(palette_layout)
        layout.addWidget(palette_group)

    def setup_toolbar(self):
        """Setup toolbar"""
        # Clear actions
        self.toolbar.clear()

        # File operations
        new_action = QAction("📄 New", self)
        new_action.triggered.connect(self.new_dialogue)
        new_action.setToolTip("Create a new dialogue tree\nClears all current nodes")
        new_action.setShortcut(QKeySequence.New)
        self.toolbar.addAction(new_action)

        open_action = QAction("📂 Load Sample", self)
        open_action.triggered.connect(self.load_sample_dialogue)
        open_action.setToolTip("Load a sample dialogue tree\nSee how dialogue structures work")
        self.toolbar.addAction(open_action)

        save_action = QAction("💾 Save", self)
        save_action.triggered.connect(self.save_dialogue)
        save_action.setToolTip("Save current dialogue tree\nExport to JSON format")
        save_action.setShortcut(QKeySequence.Save)
        self.toolbar.addAction(save_action)

        self.toolbar.addSeparator()

        # Auto-arrange
        auto_arrange_action = QAction("🎯 Auto-Arrange", self)
        auto_arrange_action.triggered.connect(self.auto_arrange_nodes)
        auto_arrange_action.setToolTip("Automatically arrange nodes\nOrganize your dialogue tree neatly")
        self.toolbar.addAction(auto_arrange_action)

        self.toolbar.addSeparator()

        # Validation
        validate_action = QAction("✅ Validate", self)
        validate_action.triggered.connect(self.validate_dialogue)
        validate_action.setToolTip("Check dialogue tree for errors\nFind missing connections or text")
        self.toolbar.addAction(validate_action)

        self.toolbar.addSeparator()

        # Export operations
        export_lua_action = QAction("🔧 Export Lua", self)
        export_lua_action.triggered.connect(self.export_to_lua)
        export_lua_action.setToolTip("Export dialogue to Lua format\nFor use in SpellForce game")
        self.toolbar.addAction(export_lua_action)

        self.toolbar.addSeparator()

        # View operations
        zoom_in_action = QAction("🔍+ Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        zoom_in_action.setToolTip("Zoom in for better visibility\nShortcut: Ctrl++")
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        self.toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction("🔍- Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        zoom_out_action.setToolTip("Zoom out to see more\nShortcut: Ctrl+-")
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        self.toolbar.addAction(zoom_out_action)

        reset_zoom_action = QAction("🎯 Reset Zoom", self)
        reset_zoom_action.triggered.connect(self.reset_zoom)
        reset_zoom_action.setToolTip("Reset zoom to 100%\nShortcut: Ctrl+0")
        reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        self.toolbar.addAction(reset_zoom_action)

        self.toolbar.addSeparator()

        # Help
        help_action = QAction("❓ Help", self)
        help_action.triggered.connect(self.show_help)
        help_action.setToolTip("Show help and tutorial\nLearn how to use the dialogue editor")
        help_action.setShortcut(QKeySequence("F1"))
        self.toolbar.addAction(help_action)

    def add_node(self, node_type: str):
        """Add a new dialogue node"""
        # Generate unique ID
        node_id = f"{node_type}_{len(self.nodes) + 1}"

        # Create node
        node = DialogueNode(
            id=node_id,
            node_type=node_type,
            position=(100 + len(self.nodes) * 50, 100 + len(self.nodes) * 50)
        )

        # Add to collection
        self.nodes[node_id] = node

        # Add to graphics view
        self.graphics_view.add_node(node)

        # Update tree view
        self.tree_widget.set_nodes(self.nodes)

        # Emit change signal
        self.emit_dialogue_changed()

        self.status_bar.showMessage(f"Added {node_type} node: {node_id}")

    def create_connection_mode(self):
        """Enter connection creation mode"""
        if self.selected_node:
            self.status_bar.showMessage("Click on target node to create connection")
        else:
            self.status_bar.showMessage("Please select a source node first")

    def select_node(self, node_id: str):
        """Select a node by ID"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            self.selected_node = node

            # Update graphics view selection
            if node_id in self.graphics_view.nodes:
                node_item = self.graphics_view.nodes[node_id]
                self.graphics_view.scene.clearSelection()
                node_item.setSelected(True)

            # Update properties
            self.properties_widget.set_node(node)

            self.status_bar.showMessage(f"Selected node: {node_id}")

    def on_node_selected(self, node):
        """Handle node selection from graphics view"""
        self.selected_node = node
        self.properties_widget.set_node(node)
        self.status_bar.showMessage(f"Selected node: {node.id}")

    def on_properties_changed(self, node_id: str, node_data: dict):
        """Handle property changes"""
        if node_id in self.nodes:
            # Update node
            self.nodes[node_id] = DialogueNode.from_dict(node_data)

            # Update graphics view
            if node_id in self.graphics_view.nodes:
                node_item = self.graphics_view.nodes[node_id]
                node_item.node = self.nodes[node_id]
                node_item.update()

            # Update tree view
            self.tree_widget.set_nodes(self.nodes)

            # Emit change signal
            self.emit_dialogue_changed()

            self.status_bar.showMessage(f"Updated node: {node_id}")

    def delete_selected_node(self):
        """Delete the selected node"""
        if not self.selected_node:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Node",
            f"Are you sure you want to delete node '{self.selected_node.id}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            node_id = self.selected_node.id

            # Remove from collections
            del self.nodes[node_id]

            # Remove from graphics view
            if node_id in self.graphics_view.nodes:
                node_item = self.graphics_view.nodes[node_id]
                self.graphics_view.scene.removeItem(node_item)
                del self.graphics_view.nodes[node_id]

            # Remove connections
            connections_to_remove = []
            for connection in self.graphics_view.connections:
                if (connection.start_node.node.id == node_id or
                    connection.end_node.node.id == node_id):
                    connections_to_remove.append(connection)

            for connection in connections_to_remove:
                self.graphics_view.scene.removeItem(connection)
                self.graphics_view.connections.remove(connection)

            # Clear selection
            self.selected_node = None
            self.properties_widget.set_node(None)

            # Update tree view
            self.tree_widget.set_nodes(self.nodes)

            # Emit change signal
            self.emit_dialogue_changed()

            self.status_bar.showMessage(f"Deleted node: {node_id}")

    def zoom_in(self):
        """Zoom in the graphics view"""
        self.graphics_view.scale(1.2, 1.2)

    def zoom_out(self):
        """Zoom out the graphics view"""
        self.graphics_view.scale(0.8, 0.8)

    def reset_zoom(self):
        """Reset zoom to default"""
        self.graphics_view.resetTransform()

    def new_dialogue(self):
        """Create new dialogue"""
        # Clear current dialogue
        self.nodes.clear()
        self.selected_node = None
        self.properties_widget.set_node(None)

        # Clear graphics view
        self.scene.clear()
        self.graphics_view.nodes.clear()
        self.graphics_view.connections.clear()

        # Update tree view
        self.tree_widget.set_nodes(self.nodes)

        # Emit change signal
        self.emit_dialogue_changed()

        self.status_bar.showMessage("Created new dialogue")

    def load_sample_dialogue(self):
        """Load sample dialogue"""
        self.create_sample_dialogue()
        self.status_bar.showMessage("Loaded sample dialogue")

    def save_dialogue(self):
        """Save dialogue to dictionary"""
        if not self.nodes:
            QMessageBox.warning(self, "Warning", "No dialogue to save")
            return

        # Convert to dictionary
        dialogue_data = {
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'connections': []
        }

        # Add connections
        for connection in self.graphics_view.connections:
            dialogue_data['connections'].append({
                'from': connection.start_node.node.id,
                'to': connection.end_node.node.id
            })

        QMessageBox.information(self, "Success", "Dialogue data prepared")
        self.status_bar.showMessage("Dialogue data saved to memory")

        return dialogue_data

    def export_to_lua(self):
        """Export dialogue to Lua format"""
        if not self.nodes:
            QMessageBox.warning(self, "Warning", "No dialogue to export")
            return

        # Generate Lua code
        lua_code = self.generate_lua_dialogue()

        # Show in a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Exported Lua Code")
        dialog.setMinimumSize(600, 400)

        layout = QVBoxLayout()

        # Text area for Lua code
        text_edit = QTextEdit()
        text_edit.setPlainText(lua_code)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec()

        self.status_bar.showMessage("Exported dialogue to Lua")

    def generate_lua_dialogue(self) -> str:
        """Generate Lua dialogue code"""
        lua_lines = []
        lua_lines.append("-- Auto-generated dialogue")
        lua_lines.append("-- Created with Visual Dialogue Editor")
        lua_lines.append("")

        # Find start node
        start_node = None
        for node in self.nodes.values():
            if node.node_type == NodeType.START:
                start_node = node
                break

        if not start_node:
            lua_lines.append("-- ERROR: No start node found")
            return "\n".join(lua_lines)

        # Generate dialogue functions
        lua_lines.append("local dialogue = {}")
        lua_lines.append("")

        for node in self.nodes.values():
            lua_lines.append(f"dialogue.{node.id} = {{")
            lua_lines.append(f'    speaker = "{node.speaker}",')
            lua_lines.append(f'    text = "{node.text}",')

            if node.choices:
                lua_lines.append("    choices = {")
                for choice in node.choices:
                    lua_lines.append(f'        {{text = "{choice["text"]}", next = "{choice["next_node"]}"}},')
                lua_lines.append("    },")

            if node.conditions:
                lua_lines.append("    conditions = {")
                for condition in node.conditions:
                    lua_lines.append(f'        "{condition}",')
                lua_lines.append("    },")

            if node.actions:
                lua_lines.append("    actions = {")
                for action in node.actions:
                    lua_lines.append(f'        "{action}",')
                lua_lines.append("    },")

            if node.next_nodes:
                next_node = node.next_nodes[0] if node.next_nodes else "nil"
                lua_lines.append(f'    next = "{next_node}",')

            lua_lines.append("}")
            lua_lines.append("")

        # Add main dialogue function
        lua_lines.append("function start_dialogue()")
        lua_lines.append(f"    return dialogue.{start_node.id}")
        lua_lines.append("end")
        lua_lines.append("")

        lua_lines.append("return dialogue")

        return "\n".join(lua_lines)

    def create_sample_dialogue(self):
        """Create a sample dialogue for testing"""
        self.new_dialogue()

        # Create sample nodes
        start_node = DialogueNode(
            id="start",
            node_type=NodeType.START,
            speaker="System",
            text="Dialogue starts here...",
            position=(100, 100)
        )

        npc_node = DialogueNode(
            id="npc_greeting",
            node_type=NodeType.NPC,
            speaker="Guard",
            text="Welcome to our town, traveler. How can I help you?",
            position=(350, 100)
        )

        choice_node = DialogueNode(
            id="player_choice",
            node_type=NodeType.CHOICE,
            speaker="Player",
            choices=[
                {"text": "I'm looking for work.", "next_node": "quest_node"},
                {"text": "Just passing through.", "next_node": "leave_node"},
                {"text": "Tell me about this town.", "next_node": "info_node"}
            ],
            position=(600, 100)
        )

        quest_node = DialogueNode(
            id="quest_node",
            node_type=NodeType.NPC,
            speaker="Guard",
            text="We have a goblin problem in the nearby caves. Could you help us?",
            position=(850, 50)
        )

        info_node = DialogueNode(
            id="info_node",
            node_type=NodeType.NPC,
            speaker="Guard",
            text="This is the town of Greenhaven. We're a peaceful community of traders and farmers.",
            position=(850, 150)
        )

        leave_node = DialogueNode(
            id="leave_node",
            node_type=NodeType.NPC,
            speaker="Guard",
            text="Safe travels, then!",
            position=(850, 250)
        )

        end_node = DialogueNode(
            id="end",
            node_type=NodeType.END,
            speaker="System",
            text="Dialogue ends",
            position=(1100, 150)
        )

        # Set up connections
        start_node.next_nodes = ["npc_greeting"]
        npc_node.next_nodes = ["player_choice"]
        quest_node.next_nodes = ["end"]
        info_node.next_nodes = ["end"]
        leave_node.next_nodes = ["end"]

        # Add nodes
        self.nodes.update({
            "start": start_node,
            "npc_greeting": npc_node,
            "player_choice": choice_node,
            "quest_node": quest_node,
            "info_node": info_node,
            "leave_node": leave_node,
            "end": end_node
        })

        # Add to graphics view
        for node in self.nodes.values():
            self.graphics_view.add_node(node)

        # Add connections
        self.graphics_view.add_connection("start", "npc_greeting")
        self.graphics_view.add_connection("npc_greeting", "player_choice")
        self.graphics_view.add_connection("player_choice", "quest_node")
        self.graphics_view.add_connection("player_choice", "info_node")
        self.graphics_view.add_connection("player_choice", "leave_node")
        self.graphics_view.add_connection("quest_node", "end")
        self.graphics_view.add_connection("info_node", "end")
        self.graphics_view.add_connection("leave_node", "end")

        # Update tree view
        self.tree_widget.set_nodes(self.nodes)

        # Emit change signal
        self.emit_dialogue_changed()

        logger.info("Created sample dialogue with 7 nodes")

    def validate_dialogue(self):
        """Validate the dialogue flow and show results"""
        if not self.nodes:
            QMessageBox.warning(self, "Validation", "No dialogue to validate")
            return

        validation_errors = []
        validation_warnings = []
        validation_info = []

        # Check for start node
        start_nodes = [node for node in self.nodes.values() if node.node_type == NodeType.START]
        if not start_nodes:
            validation_errors.append("No start node found - dialogue cannot begin")
        elif len(start_nodes) > 1:
            validation_warnings.append(f"Multiple start nodes found ({len(start_nodes)}) - only first will be used")

        # Check for end nodes
        end_nodes = [node for node in self.nodes.values() if node.node_type == NodeType.END]
        if not end_nodes:
            validation_warnings.append("No end nodes found - dialogue may not terminate properly")

        # Check for disconnected nodes
        connected_nodes = set()
        if start_nodes:
            # Find all reachable nodes from start
            visited = set()
            to_visit = [start_nodes[0].id]

            while to_visit:
                current_id = to_visit.pop(0)
                if current_id in visited:
                    continue
                visited.add(current_id)
                connected_nodes.add(current_id)

                current_node = self.nodes.get(current_id)
                if current_node:
                    to_visit.extend(current_node.next_nodes)

            disconnected_nodes = set(self.nodes.keys()) - connected_nodes
            if disconnected_nodes:
                validation_warnings.append(f"Disconnected nodes found: {', '.join(disconnected_nodes)}")

        # Check for orphaned nodes (no incoming connections except start)
        nodes_with_incoming = set()
        for node in self.nodes.values():
            nodes_with_incoming.update(node.next_nodes)

        orphaned_nodes = []
        for node_id, node in self.nodes.items():
            if (node.node_type != NodeType.START and
                node_id not in nodes_with_incoming and
                node_id not in connected_nodes):
                orphaned_nodes.append(node_id)

        if orphaned_nodes:
            validation_warnings.append(f"Orphaned nodes (no incoming connections): {', '.join(orphaned_nodes)}")

        # Check for empty text
        empty_text_nodes = []
        for node_id, node in self.nodes.items():
            if not node.text.strip() and node.node_type not in [NodeType.START, NodeType.END]:
                empty_text_nodes.append(node_id)

        if empty_text_nodes:
            validation_warnings.append(f"Nodes with empty text: {', '.join(empty_text_nodes)}")

        # Check choice nodes
        choice_nodes = [node for node in self.nodes.values() if node.node_type == NodeType.CHOICE]
        for node in choice_nodes:
            if not node.choices:
                validation_errors.append(f"Choice node '{node.id}' has no choices")
            else:
                # Check if choices have valid next nodes
                for i, choice in enumerate(node.choices):
                    next_node = choice.get('next_node', '')
                    if next_node and next_node not in self.nodes:
                        validation_warnings.append(f"Choice {i+1} in node '{node.id}' points to non-existent node '{next_node}'")

        # Check for cycles
        def detect_cycles(start_id):
            """Detect cycles starting from a node"""
            visited = set()
            rec_stack = set()

            def dfs(node_id):
                if node_id in rec_stack:
                    return [node_id]
                if node_id in visited:
                    return None

                visited.add(node_id)
                rec_stack.add(node_id)

                node = self.nodes.get(node_id)
                if node:
                    for next_id in node.next_nodes:
                        cycle = dfs(next_id)
                        if cycle:
                            if node_id in cycle:
                                return cycle
                            else:
                                return cycle + [node_id]

                rec_stack.remove(node_id)
                return None

            return dfs(start_id)

        if start_nodes:
            cycle = detect_cycles(start_nodes[0].id)
            if cycle:
                validation_errors.append(f"Circular dialogue flow detected: {' -> '.join(reversed(cycle))}")

        # Count nodes by type
        node_counts = {}
        for node in self.nodes.values():
            node_type = node.node_type
            node_counts[node_type] = node_counts.get(node_type, 0) + 1

        validation_info.append(f"Total nodes: {len(self.nodes)}")
        for node_type, count in node_counts.items():
            validation_info.append(f"  {node_type}: {count}")

        # Show validation results
        self.show_validation_results(validation_errors, validation_warnings, validation_info)

    def show_validation_results(self, errors: List[str], warnings: List[str], info: List[str]):
        """Show validation results in a dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Dialogue Validation Results")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        # Create text widget for results
        results_text = QTextEdit()
        results_text.setReadOnly(True)

        # Format results
        result_html = "<h3>Dialogue Validation Results</h3>"

        if errors:
            result_html += "<h4 style='color: red;'>❌ Errors</h4><ul>"
            for error in errors:
                result_html += f"<li style='color: red;'>{error}</li>"
            result_html += "</ul>"

        if warnings:
            result_html += "<h4 style='color: orange;'>⚠️ Warnings</h4><ul>"
            for warning in warnings:
                result_html += f"<li style='color: orange;'>{warning}</li>"
            result_html += "</ul>"

        if info:
            result_html += "<h4 style='color: blue;'>ℹ️ Information</h4><ul>"
            for item in info:
                result_html += f"<li style='color: blue;'>{item}</li>"
            result_html += "</ul>"

        if not errors and not warnings:
            result_html += "<h4 style='color: green;'>✅ Validation Passed</h4>"
            result_html += "<p style='color: green;'>No issues found in dialogue flow.</p>"

        results_text.setHtml(result_html)
        layout.addWidget(results_text)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec()

        # Update status bar
        if errors:
            self.status_bar.showMessage(f"Validation failed: {len(errors)} errors, {len(warnings)} warnings")
        elif warnings:
            self.status_bar.showMessage(f"Validation passed with warnings: {len(warnings)} warnings")
        else:
            self.status_bar.showMessage("Validation passed: No issues found")

    def emit_dialogue_changed(self):
        """Emit dialogue changed signal with current data"""
        if self.nodes:
            dialogue_data = {
                'nodes': [node.to_dict() for node in self.nodes.values()],
                'connections': []
            }

            # Add connections
            for connection in self.graphics_view.connections:
                dialogue_data['connections'].append({
                    'from': connection.start_node.node.id,
                    'to': connection.end_node.node.id
                })

            self.dialogue_changed.emit(dialogue_data)

    def set_dialogue_data(self, dialogue_data: dict):
        """Set dialogue data from dictionary"""
        if not dialogue_data or 'nodes' not in dialogue_data:
            return

        # Clear current dialogue
        self.new_dialogue()

        # Load nodes
        for node_data in dialogue_data['nodes']:
            node = DialogueNode.from_dict(node_data)
            self.nodes[node.id] = node
            self.graphics_view.add_node(node)

        # Load connections
        if 'connections' in dialogue_data:
            for connection_data in dialogue_data['connections']:
                from_node = connection_data.get('from')
                to_node = connection_data.get('to')
                if from_node and to_node:
                    self.graphics_view.add_connection(from_node, to_node)

        # Update views
        self.tree_widget.set_nodes(self.nodes)

        self.status_bar.showMessage("Loaded dialogue data")

    def get_dialogue_data(self) -> dict:
        """Get current dialogue data as dictionary"""
        if not self.nodes:
            return {}

        dialogue_data = {
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'connections': []
        }

        # Add connections
        for connection in self.graphics_view.connections:
            dialogue_data['connections'].append({
                'from': connection.start_node.node.id,
                'to': connection.end_node.node.id
            })

        return dialogue_data

    def auto_arrange_nodes(self):
        """Automatically arrange nodes in a tree layout"""
        if not self.nodes:
            self.status_bar.showMessage("No nodes to arrange")
            return

        self.status_bar.showMessage("Auto-arranging nodes...")

        # Find start node
        start_node = None
        for node in self.nodes.values():
            if node.node_type == NodeType.START:
                start_node = node
                break

        if not start_node:
            self.status_bar.showMessage("No start node found")
            return

        # Simple tree layout algorithm
        visited = set()
        positions = {}

        def arrange_node(node, x, y, level_width):
            """Recursively arrange nodes in tree layout"""
            if node.id in visited:
                return

            visited.add(node.id)
            positions[node.id] = (x, y)

            # Get outgoing connections
            outgoing = []
            for connection in self.graphics_view.connections:
                if hasattr(connection, 'start_node') and connection.start_node.node.id == node.id:
                    outgoing.append(connection.end_node.node)

            if outgoing:
                child_width = level_width / len(outgoing)
                start_x = x - level_width / 2 + child_width / 2

                for i, child in enumerate(outgoing):
                    child_x = start_x + i * child_width
                    child_y = y + 150  # Vertical spacing
                    arrange_node(child, child_x, child_y, child_width * 0.8)

        # Start arrangement from root
        arrange_node(start_node, 400, 100, 600)

        # Apply positions
        for node_id, (x, y) in positions.items():
            if node_id in self.nodes:
                node_item = None
                for item in self.scene.items():
                    if hasattr(item, 'node') and item.node.id == node_id:
                        node_item = item
                        break

                if node_item:
                    node_item.setPos(x, y)

        self.status_bar.showMessage(f"Auto-arranged {len(positions)} nodes")

    def show_help(self):
        """Show help dialog"""
        help_text = """
# Visual Dialogue Editor Help

## 🎯 How to Use

### 1. Create Nodes
- Click buttons in the **Node Palette** (left panel)
- Each node type has a specific purpose:
  - 🟢 **Start Node**: Where every conversation begins
  - 👤 **NPC Dialogue**: What characters say to the player
  - 🗣️ **Player Dialogue**: Player response options
  - 🔀 **Choice Node**: Multiple conversation paths
  - ❓ **Conditional Node**: Show different text based on conditions
  - 🔴 **End Node**: Where dialogue paths conclude

### 2. Connect Nodes
- Click and drag from one node to another
- Create conversation flow paths
- Use right-click to delete connections

### 3. Edit Content
- Click any node to select it
- Edit text and properties in the **Properties Panel** (right)
- Changes are saved automatically

### 4. Navigation
- **Mouse Wheel**: Zoom in/out
- **Click & Drag**: Pan around the canvas
- **Double-click**: Center on node

## ⌨️ Keyboard Shortcuts

- **Ctrl+N**: New dialogue tree
- **Ctrl+S**: Save dialogue
- **Ctrl++**: Zoom in
- **Ctrl+-**: Zoom out
- **Ctrl+0**: Reset zoom
- **F1**: Show this help

## 💡 Tips

- Start with a **Start Node** and build outward
- Use **Auto-Arrange** to organize your tree
- **Validate** your dialogue to check for errors
- Export to **Lua** when ready for the game

## 🔧 Troubleshooting

- **Nodes not connecting?** Make sure you're dragging from the edge of one node to another
- **Lost in the canvas?** Use Reset Zoom or zoom out to see everything
- **Validation errors?** Check that all paths have proper connections and text

Need more help? Check the quest documentation!
        """

        help_dialog = QMessageBox(self)
        help_dialog.setWindowTitle("Visual Dialogue Editor Help")
        help_dialog.setTextFormat(Qt.MarkdownText)
        help_dialog.setText(help_text)
        help_dialog.setStandardButtons(QMessageBox.Ok)
        help_dialog.exec()


# Test function
def test_visual_dialogue_widget():
    """Test the visual dialogue widget"""
    app = QApplication(sys.argv)

    widget = VisualDialogueWidget()
    widget.setWindowTitle("Visual Dialogue Widget Test")
    widget.resize(1200, 800)
    widget.show()

    # Create sample dialogue
    widget.create_sample_dialogue()

    return app.exec()


if __name__ == "__main__":
    sys.exit(test_visual_dialogue_widget())