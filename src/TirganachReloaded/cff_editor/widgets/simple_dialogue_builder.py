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
import math
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QGroupBox, QFormLayout, QScrollArea,
    QFrame, QMessageBox, QComboBox, QSplitter, QTreeWidget,
    QTreeWidgetItem, QCheckBox, QRadioButton, QButtonGroup,
    QDialog, QDialogButtonBox, QButtonGroup, QGraphicsView,
    QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem,
    QGraphicsPolygonItem, QSizePolicy, QMenu
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QTimer
from PySide6.QtWidgets import QStyle
from PySide6.QtGui import QFont, QPixmap, QPen, QBrush, QColor, QPainter, QPolygonF

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


class FlowChartNode(QGraphicsRectItem):
    """A single node in the flow chart representing a dialogue step"""

    def __init__(self, step, x=0, y=0, width=200, height=80):
        super().__init__(0, 0, width, height)
        self.step = step
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

        # Set vibrant colors based on step type (better contrast with dark background)
        self.colors = {
            DialogueStepType.START: "#00ff88",      # Bright Green
            DialogueStepType.NPC_SPEECH: "#4488ff", # Bright Blue
            DialogueStepType.PLAYER_CHOICE: "#ff44ff", # Bright Magenta
            DialogueStepType.PLAYER_SPEECH: "#44ffff", # Bright Cyan
            DialogueStepType.NPC_RESPONSE: "#ffaa44", # Bright Orange
            DialogueStepType.END: "#ff4444"          # Bright Red
        }

        self.color = QColor(self.colors.get(step.type, "#aaaaaa"))
        self.selected_color = QColor("#ffffff")  # White for selection

        # Create text item
        self.text_item = QGraphicsTextItem(self)
        self.update_text()

    def update_text(self):
        """Update the text displayed in the node"""
        type_names = {
            DialogueStepType.START: "START",
            DialogueStepType.NPC_SPEECH: "NPC",
            DialogueStepType.PLAYER_CHOICE: "CHOICE",
            DialogueStepType.PLAYER_SPEECH: "SPEAK",
            DialogueStepType.NPC_RESPONSE: "RESPONSE",
            DialogueStepType.END: "END"
        }

        type_name = type_names.get(self.step.type, "STEP")

        # Create display text with connection status
        if self.step.type == DialogueStepType.NPC_SPEECH or self.step.type == DialogueStepType.NPC_RESPONSE:
            display_text = f"{type_name}\n{self.step.speaker}: {self.step.text[:30]}..."
        elif self.step.type == DialogueStepType.PLAYER_CHOICE:
            connected_choices = sum(1 for choice in self.step.choices if choice.get('next_step_id'))
            total_choices = len(self.step.choices)
            if connected_choices < total_choices:
                display_text = f"{type_name}\n{connected_choices}/{total_choices} connected"
            else:
                display_text = f"{type_name}\n{total_choices} options"
        elif self.step.type == DialogueStepType.PLAYER_SPEECH:
            display_text = f"{type_name}\n{self.step.text[:30]}..."
        else:
            display_text = type_name

        self.text_item.setPlainText(display_text)
        self.text_item.setDefaultTextColor(Qt.black)  # Black text on bright colored nodes

        # Center text
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(
            (self.rect().width() - text_rect.width()) / 2,
            (self.rect().height() - text_rect.height()) / 2
        )

    def paint(self, painter, option, widget):
        """Paint the node"""
        # Set brush based on selection
        if option.state & QStyle.State_Selected:
            painter.setBrush(QBrush(self.selected_color))
        else:
            painter.setBrush(QBrush(self.color))

        # Draw rounded rectangle
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRoundedRect(self.rect(), 10, 10)

    def get_connection_point(self, direction="bottom"):
        """Get connection point position"""
        rect = self.rect()
        if direction == "bottom":
            return self.pos() + QPointF(rect.width() / 2, rect.height())
        elif direction == "top":
            return self.pos() + QPointF(rect.width() / 2, 0)
        elif direction == "left":
            return self.pos() + QPointF(0, rect.height() / 2)
        elif direction == "right":
            return self.pos() + QPointF(rect.width(), rect.height() / 2)
        return self.pos() + QPointF(rect.width() / 2, rect.height() / 2)


class FlowChartConnection(QGraphicsLineItem):
    """A connection line between two nodes with choice branching support"""

    def __init__(self, start_node, end_node, choice_text="", choice_index=None):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.choice_text = choice_text
        self.choice_index = choice_index

        # Vibrant, high-contrast colors for different choice branches
        branch_colors = [
            QColor("#FF4444"),  # Bright Red
            QColor("#4444FF"),  # Bright Blue
            QColor("#44FF44"),  # Bright Green
            QColor("#FFAA00"),  # Bright Orange/Yellow
            QColor("#FF44FF"),  # Bright Magenta
            QColor("#00FFFF"),  # Cyan
            QColor("#FF8844")   # Orange
        ]
        self.color = branch_colors[choice_index % len(branch_colors)] if choice_index is not None else QColor("#888888")

        self.setPen(QPen(self.color, 4, Qt.SolidLine))
        self.setZValue(-1)  # Draw behind nodes

        # Create arrow
        self.arrow = QGraphicsPolygonItem(self)
        self.arrow.setBrush(QBrush(self.color))

        # Create choice label if provided - no white background, just outline text
        self.label = QGraphicsTextItem(self)
        if choice_text:
            self.label.setPlainText(choice_text)
            self.label.setDefaultTextColor(Qt.white)  # White text for better contrast
            self.label.setFont(QFont("Arial", 10, QFont.Bold))

            # Add outline effect for better visibility
            outline_effect = self.create_text_outline()
            self.label.setGraphicsEffect(outline_effect)

        self.update_position()

    def create_text_outline(self):
        """Create a text outline effect for better visibility"""
        from PySide6.QtWidgets import QGraphicsDropShadowEffect

        shadow = QGraphicsDropShadowEffect()
        shadow.setColor(QColor(0, 0, 0, 200))  # Semi-transparent black
        shadow.setOffset(1, 1)
        shadow.setBlurRadius(2)
        return shadow

    def update_position(self):
        """Update the line position based on node positions"""
        start_point = self.start_node.get_connection_point("bottom")
        end_point = self.end_node.get_connection_point("top")

        self.setLine(start_point.x(), start_point.y(), end_point.x(), end_point.y())

        # Update arrow
        self.update_arrow(start_point, end_point)

        # Update label position
        if self.choice_text:
            mid_point = QPointF((start_point.x() + end_point.x()) / 2,
                              (start_point.y() + end_point.y()) / 2)

            # Position label above the line
            label_width = self.label.boundingRect().width()
            label_height = self.label.boundingRect().height()

            self.label.setPos(mid_point.x() - label_width / 2, mid_point.y() - label_height - 15)

    def update_arrow(self, start_point, end_point):
        """Update arrow head"""
        # Calculate arrow direction
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        angle = math.atan2(dy, dx)

        # Arrow size
        arrow_length = 10
        arrow_angle = math.pi / 6

        # Calculate arrow points
        arrow_x1 = end_point.x() - arrow_length * math.cos(angle - arrow_angle)
        arrow_y1 = end_point.y() - arrow_length * math.sin(angle - arrow_angle)
        arrow_x2 = end_point.x() - arrow_length * math.cos(angle + arrow_angle)
        arrow_y2 = end_point.y() - arrow_length * math.sin(angle + arrow_angle)

        # Create arrow polygon
        arrow_polygon = QPolygonF([
            QPointF(end_point.x(), end_point.y()),
            QPointF(arrow_x1, arrow_y1),
            QPointF(arrow_x2, arrow_y2)
        ])

        self.arrow.setPolygon(arrow_polygon)


class FlowChartView(QGraphicsView):
    """Flow chart view for visualizing dialogue structure with interactive connection drawing"""

    node_selected = Signal(str)  # step_id
    connection_created = Signal(str, str)  # start_step_id, end_step_id

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Set a dark background for better contrast with colorful branches
        self.scene.setBackgroundBrush(QBrush(QColor("#2b3e50")))

        self.nodes = {}
        self.connections = []

        # Interactive connection drawing state
        self.is_drawing_connection = False
        self.connection_start_node = None
        self.temp_connection_line = None
        self.connection_mode = False  # Toggle for connection mode

        # Set view properties
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Enable selection
        self.scene.selectionChanged.connect(self.on_selection_changed)

    def clear_flow_chart(self):
        """Clear all items from the flow chart"""
        self.scene.clear()
        self.nodes.clear()
        self.connections.clear()

    def add_node(self, step, x=0, y=0):
        """Add a node to the flow chart"""
        node = FlowChartNode(step, x, y)
        self.scene.addItem(node)
        self.nodes[step.id] = node
        return node

    def add_connection(self, start_step_id, end_step_id, choice_text="", choice_index=None):
        """Add a connection between two nodes with optional choice branching"""
        if start_step_id in self.nodes and end_step_id in self.nodes:
            start_node = self.nodes[start_step_id]
            end_node = self.nodes[end_step_id]

            connection = FlowChartConnection(start_node, end_node, choice_text, choice_index)
            self.scene.addItem(connection)
            self.connections.append(connection)

            # Note: Auto-layout is now handled by the branching layout system
            connection.update_position()

    def update_flow_chart(self, steps):
        """Update the entire flow chart based on steps with proper branching layout"""
        self.clear_flow_chart()

        if not steps:
            return

        # Create a hierarchical layout for branching
        self.create_branching_layout(steps)

        # Add connections based on dialogue flow
        for step in steps.values():
            if step.next_step_id and step.next_step_id in steps:
                # Only add linear connection if there are no choices branching from this step
                if not step.choices or not any(c.get('next_step_id') for c in step.choices):
                    self.add_connection(step.id, step.next_step_id)

            # Connect choices to their responses with clear branching
            if step.choices:
                for i, choice in enumerate(step.choices):
                    next_step_id = choice.get('next_step_id')
                    if next_step_id and next_step_id in steps:
                        choice_text = choice.get('text', f'Option {i+1}')
                        self.add_connection(step.id, next_step_id, choice_text, choice_index=i)

        # Fit all items in view
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def create_branching_layout(self, steps):
        """Create a hierarchical layout that shows branching clearly"""
        if not steps:
            return

        # Find the start step
        start_step = None
        for step in steps.values():
            if step.type == DialogueStepType.START:
                start_step = step
                break

        if not start_step:
            return

        # Position nodes hierarchically
        level_width = 250  # Horizontal spacing
        level_height = 180  # Vertical spacing
        start_x = 100
        start_y = 50

        # Track positioned nodes and their levels
        positioned = {}
        levels = {}  # step_id -> (level, position_in_level)

        # Position start step at top center
        self.add_node(start_step, start_x, start_y)
        positioned[start_step.id] = (start_x, start_y)
        levels[start_step.id] = (0, 0)

        # Build the tree structure and position nodes
        self._position_children(start_step, steps, positioned, levels, start_x, start_y, level_width, level_height)

        # Position any remaining unpositioned nodes (orphans)
        for step in steps.values():
            if step.id not in positioned:
                # Position orphan nodes to the right
                orphan_y = start_y + len(positioned) * 100
                self.add_node(step, start_x + 800, orphan_y)
                positioned[step.id] = (start_x + 800, orphan_y)

    def _position_children(self, parent_step, steps, positioned, levels, parent_x, parent_y, level_width, level_height):
        """Recursively position child nodes with proper branching"""
        if parent_step.type == DialogueStepType.PLAYER_CHOICE and parent_step.choices:
            # Branch out for each choice
            num_choices = len(parent_step.choices)
            total_width = (num_choices - 1) * level_width
            start_x = parent_x - total_width // 2

            for i, choice in enumerate(parent_step.choices):
                next_step_id = choice.get('next_step_id')
                if next_step_id and next_step_id in steps:
                    child_step = steps[next_step_id]
                    child_x = start_x + i * level_width
                    child_y = parent_y + level_height

                    if child_step.id not in positioned:
                        self.add_node(child_step, child_x, child_y)
                        positioned[child_step.id] = (child_x, child_y)
                        levels[child_step.id] = (levels[parent_step.id][0] + 1, i)

                        # Continue positioning children
                        self._position_children(child_step, steps, positioned, levels, child_x, child_y, level_width, level_height)

        elif parent_step.next_step_id and parent_step.next_step_id in steps:
            # Linear connection (single child)
            child_step = steps[parent_step.next_step_id]
            child_x = parent_x
            child_y = parent_y + level_height

            if child_step.id not in positioned:
                self.add_node(child_step, child_x, child_y)
                positioned[child_step.id] = (child_x, child_y)
                levels[child_step.id] = (levels[parent_step.id][0] + 1, 0)

                # Continue positioning children
                self._position_children(child_step, steps, positioned, levels, child_x, child_y, level_width, level_height)

    def mousePressEvent(self, event):
        """Handle mouse press for interactive connection drawing"""
        if event.button() == Qt.LeftButton and self.connection_mode:
            # Get the item under the mouse
            pos = self.mapToScene(event.pos())
            item = self.scene.itemAt(pos, self.transform())

            if isinstance(item, FlowChartNode):
                if not self.is_drawing_connection:
                    # Start drawing a connection
                    self.is_drawing_connection = True
                    self.connection_start_node = item

                    # Create a temporary line for visual feedback
                    start_point = item.get_connection_point("bottom")
                    self.temp_connection_line = QGraphicsLineItem(
                        start_point.x(), start_point.y(),
                        start_point.x(), start_point.y()
                    )
                    self.temp_connection_line.setPen(QPen(QColor("#ffff00"), 3, Qt.DashLine))
                    self.scene.addItem(self.temp_connection_line)
                else:
                    # Finish drawing a connection
                    if item != self.connection_start_node:
                        self.finish_connection(item)
                    else:
                        # Cancel if clicking the same node
                        self.cancel_connection()
            else:
                # Clicked on empty space - cancel connection drawing
                self.cancel_connection()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for connection drawing preview"""
        if self.is_drawing_connection and self.temp_connection_line:
            pos = self.mapToScene(event.pos())
            start_point = self.connection_start_node.get_connection_point("bottom")

            # Update the temporary line
            self.temp_connection_line.setLine(
                start_point.x(), start_point.y(),
                pos.x(), pos.y()
            )
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release for connection drawing"""
        if event.button() == Qt.LeftButton and self.is_drawing_connection:
            pos = self.mapToScene(event.pos())
            item = self.scene.itemAt(pos, self.transform())

            if isinstance(item, FlowChartNode) and item != self.connection_start_node:
                self.finish_connection(item)
            else:
                self.cancel_connection()
        else:
            super().mouseReleaseEvent(event)

    def finish_connection(self, end_node):
        """Finish drawing a connection between two nodes"""
        if self.connection_start_node and end_node:
            # Emit signal to create the connection
            self.connection_created.emit(self.connection_start_node.step.id, end_node.step.id)

        self.cancel_connection()

    def cancel_connection(self):
        """Cancel the current connection drawing"""
        self.is_drawing_connection = False
        self.connection_start_node = None

        if self.temp_connection_line:
            self.scene.removeItem(self.temp_connection_line)
            self.temp_connection_line = None

    def toggle_connection_mode(self):
        """Toggle connection drawing mode"""
        self.connection_mode = not self.connection_mode
        if self.connection_mode:
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.CrossCursor)
        else:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setCursor(Qt.ArrowCursor)
            self.cancel_connection()

        return self.connection_mode

    def on_selection_changed(self):
        """Handle node selection"""
        selected_items = self.scene.selectedItems()
        if selected_items:
            for item in selected_items:
                if isinstance(item, FlowChartNode):
                    self.node_selected.emit(item.step.id)
                    break


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
        self._updating_selection = False  # Prevent recursive selection updates
        self.setup_ui()
        self.create_initial_dialogue()

    def setup_ui(self):
        """Setup the main UI"""
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left panel - Flow chart view
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setMinimumWidth(400)
        left_panel.setMaximumWidth(600)

        # Flow chart title
        title_label = QLabel("Dialogue Flow Chart")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2c3e50;")
        left_layout.addWidget(title_label)

        # Instructions and controls
        instructions_widget = QWidget()
        instructions_layout = QVBoxLayout()
        instructions_widget.setLayout(instructions_layout)

        instructions = QLabel("📊 Click nodes to select • See colored branches for player choices • Connection status shows in choice nodes")
        instructions.setStyleSheet("font-size: 11px; color: #7f8c8d; margin-bottom: 10px; padding: 8px; background-color: #f8f9fa; border-radius: 4px; border-left: 4px solid #3498db;")
        instructions.setWordWrap(True)
        instructions_layout.addWidget(instructions)

        # Connection mode toggle
        connection_controls = QHBoxLayout()

        self.connection_mode_btn = QPushButton("🔗 Enable Connection Mode")
        self.connection_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                border: 1px solid #2980b9;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:checked {
                background-color: #27ae60;
                border: 1px solid #229954;
            }
        """)
        self.connection_mode_btn.setCheckable(True)
        self.connection_mode_btn.clicked.connect(self.toggle_connection_mode)
        connection_controls.addWidget(self.connection_mode_btn)

        connection_help = QLabel("Click and drag between nodes to create connections")
        connection_help.setStyleSheet("font-size: 10px; color: #95a5a6; font-style: italic;")
        connection_controls.addWidget(connection_help)
        connection_controls.addStretch()

        instructions_layout.addLayout(connection_controls)
        left_layout.addWidget(instructions_widget)

        # Flow chart view
        self.flow_chart = FlowChartView()
        self.flow_chart.node_selected.connect(self.on_flow_chart_node_selected)
        self.flow_chart.connection_created.connect(self.on_connection_created)
        self.flow_chart.setMinimumHeight(300)
        left_layout.addWidget(self.flow_chart)

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

        self.update_flow_chart()
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
            self.update_flow_chart()

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
        if step_id not in self.steps or self._updating_selection:
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

        # Update flow chart selection (without triggering recursion)
        self._updating_selection = True
        self.update_flow_chart_selection(step_id)
        self._updating_selection = False

    def update_flow_chart_selection(self, selected_step_id):
        """Update flow chart selection to highlight selected step"""
        if hasattr(self, 'flow_chart') and selected_step_id in self.flow_chart.nodes:
            # Clear all selections
            for node in self.flow_chart.nodes.values():
                node.setSelected(False)

            # Select the target node
            self.flow_chart.nodes[selected_step_id].setSelected(True)

    def update_tree_selection(self, selected_step_id):
        """Update tree selection to highlight selected step (legacy - kept for compatibility)"""
        if hasattr(self, 'tree_widget'):
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

    def update_flow_chart(self):
        """Update the flow chart view"""
        if hasattr(self, 'flow_chart'):
            self.flow_chart.update_flow_chart(self.steps)

    def update_tree(self):
        """Update the tree view (legacy - kept for compatibility)"""
        if hasattr(self, 'tree_widget'):
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

    def toggle_connection_mode(self):
        """Toggle connection drawing mode"""
        is_enabled = self.flow_chart.toggle_connection_mode()
        if is_enabled:
            self.connection_mode_btn.setText("🔗 Connection Mode ON")
            self.connection_mode_btn.setChecked(True)
        else:
            self.connection_mode_btn.setText("🔗 Enable Connection Mode")
            self.connection_mode_btn.setChecked(False)

    def on_connection_created(self, start_step_id, end_step_id):
        """Handle connection created by user"""
        if start_step_id in self.steps and end_step_id in self.steps:
            start_step = self.steps[start_step_id]
            end_step = self.steps[end_step_id]

            # Check if this is a player choice step
            if start_step.type == DialogueStepType.PLAYER_CHOICE:
                # Find an available choice slot or create a new one
                available_choice = None
                for choice in start_step.choices:
                    if not choice.get('next_step_id'):
                        available_choice = choice
                        break

                if not available_choice:
                    # Create a new choice
                    new_choice = {'text': f'Choice {len(start_step.choices) + 1}', 'next_step_id': ''}
                    start_step.choices.append(new_choice)
                    available_choice = new_choice

                # Set the connection
                available_choice['next_step_id'] = end_step_id

                # Update the step widget if it's currently selected
                if self.selected_step_id == start_step_id and self.current_step_widget:
                    self.current_step_widget.rebuild_ui()

            elif start_step.type != DialogueStepType.PLAYER_CHOICE:
                # For non-choice steps, set the linear next_step
                start_step.next_step_id = end_step_id

            # Update the flow chart and emit change signal
            self.update_flow_chart()
            self.dialogue_changed.emit()

            # Show success feedback
            self.show_connection_feedback(f"Connected: {start_step.id} → {end_step_id}")

    def show_connection_feedback(self, message):
        """Show temporary feedback for connection creation"""
        feedback_label = QLabel(message)
        feedback_label.setStyleSheet("""
            QLabel {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        feedback_label.setAlignment(Qt.AlignCenter)

        # Add to the flow chart scene temporarily
        self.flow_chart.scene.addWidget(feedback_label)

        # Position at center of view
        view_center = self.flow_chart.mapToScene(self.flow_chart.rect().center())
        feedback_label.setPos(view_center.x() - feedback_label.width()//2,
                              view_center.y() - feedback_label.height()//2)

        # Remove after 2 seconds
        QTimer.singleShot(2000, lambda: self.flow_chart.scene.removeItem(feedback_label) if feedback_label.scene() else None)

    def on_flow_chart_node_selected(self, step_id):
        """Handle flow chart node selection"""
        if step_id and step_id in self.steps and not self._updating_selection:
            self.select_step(step_id)

    def on_tree_item_clicked(self, item, column):
        """Handle tree item click (legacy - kept for compatibility)"""
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
            self.update_flow_chart()
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
            self.update_flow_chart()
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