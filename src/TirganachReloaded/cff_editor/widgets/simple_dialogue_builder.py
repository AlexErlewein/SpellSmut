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
from dataclasses import dataclass, asdict, field
from enum import Enum

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QGroupBox,
    QFormLayout,
    QScrollArea,
    QFrame,
    QMessageBox,
    QComboBox,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QListWidget,
    QListWidgetItem,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QButtonGroup,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsTextItem,
    QGraphicsLineItem,
    QGraphicsPolygonItem,
    QSizePolicy,
    QMenu,
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
    PLAYER_SPEECH = (
        "player_speech"  # Single option player speech (looks like one option)
    )
    NPC_RESPONSE = "npc_response"
    END = "end"


@dataclass
class DialogueStep:
    """A single step in the dialogue"""

    id: str
    type: DialogueStepType
    speaker: str = ""
    text: str = ""
    choices: List[Dict[str, Any]] = (
        None  # Each choice: {'text': 'Option text', 'next_step_id': 'target_step_id', 'availability_rules': []}
    )
    next_step_id: str = ""  # For linear flow when no branching
    response_to_choice: str = ""  # ID of the choice this NPC response is responding to
    actions: List[str] = field(
        default_factory=list
    )  # Actions to execute when this step is reached

    def __post_init__(self):
        if self.choices is None:
            self.choices = []

    def to_dict(self):
        """Convert to dictionary"""
        data = asdict(self)
        data["type"] = self.type.value
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
            return {DialogueStepType.NPC_SPEECH: "NPC speaks to the player"}
        elif self.current_step_type == DialogueStepType.NPC_SPEECH:
            return {
                DialogueStepType.PLAYER_CHOICE: "Player chooses a response",
                DialogueStepType.PLAYER_SPEECH: "Player says something (single option)",
                DialogueStepType.NPC_RESPONSE: "NPC continues speaking",
                DialogueStepType.END: "Conversation ends",
            }
        elif self.current_step_type == DialogueStepType.PLAYER_CHOICE:
            return {
                DialogueStepType.NPC_RESPONSE: "NPC responds to player choice",
                DialogueStepType.NPC_SPEECH: "Different NPC speaks",
                DialogueStepType.END: "Conversation ends",
            }
        elif self.current_step_type == DialogueStepType.NPC_RESPONSE:
            return {
                DialogueStepType.PLAYER_CHOICE: "Player chooses next action",
                DialogueStepType.NPC_SPEECH: "Same NPC continues",
                DialogueStepType.NPC_RESPONSE: "Same NPC responds again",
                DialogueStepType.END: "Conversation ends",
            }
        else:
            return {
                DialogueStepType.NPC_SPEECH: "NPC speaks",
                DialogueStepType.PLAYER_CHOICE: "Player choice",
                DialogueStepType.END: "End conversation",
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
            DialogueStepType.START: "#00ff88",  # Bright Green
            DialogueStepType.NPC_SPEECH: "#4488ff",  # Bright Blue
            DialogueStepType.PLAYER_CHOICE: "#ff44ff",  # Bright Magenta
            DialogueStepType.PLAYER_SPEECH: "#44ffff",  # Bright Cyan
            DialogueStepType.NPC_RESPONSE: "#ffaa44",  # Bright Orange
            DialogueStepType.END: "#ff4444",  # Bright Red
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
            DialogueStepType.END: "END",
        }

        type_name = type_names.get(self.step.type, "STEP")

        # Create display text with connection status
        if self.step.type == DialogueStepType.NPC_SPEECH:
            display_text = f"{type_name}\n{self.step.speaker}: {self.step.text[:30]}..."
        elif self.step.type == DialogueStepType.NPC_RESPONSE:
            # Show which choice this response is for
            if self.step.response_to_choice:
                # Extract a short choice identifier
                choice_info = (
                    f"→ {self.step.response_to_choice[-15:]}"
                    if len(self.step.response_to_choice) > 15
                    else f"→ {self.step.response_to_choice}"
                )
                display_text = f"{type_name} {choice_info}\n{self.step.speaker}: {self.step.text[:20]}..."
            else:
                display_text = (
                    f"{type_name}\n{self.step.speaker}: {self.step.text[:30]}..."
                )
        elif self.step.type == DialogueStepType.PLAYER_CHOICE:
            connected_choices = sum(
                1 for choice in self.step.choices if choice.get("next_step_id")
            )
            total_choices = len(self.step.choices)
            if connected_choices < total_choices:
                display_text = (
                    f"{type_name}\n{connected_choices}/{total_choices} connected"
                )
            else:
                display_text = f"{type_name}\n{total_choices} options"
        elif self.step.type == DialogueStepType.PLAYER_SPEECH:
            display_text = f"{type_name}\n{self.step.text[:30]}..."
        else:
            display_text = type_name

        self.text_item.setPlainText(display_text)
        self.text_item.setDefaultTextColor(
            Qt.black
        )  # Black text on bright colored nodes

        # Center text
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(
            (self.rect().width() - text_rect.width()) / 2,
            (self.rect().height() - text_rect.height()) / 2,
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
            QColor("#FF8844"),  # Orange
        ]
        self.color = (
            branch_colors[choice_index % len(branch_colors)]
            if choice_index is not None
            else QColor("#888888")
        )

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
            mid_point = QPointF(
                (start_point.x() + end_point.x()) / 2,
                (start_point.y() + end_point.y()) / 2,
            )

            # Position label above the line
            label_width = self.label.boundingRect().width()
            label_height = self.label.boundingRect().height()

            self.label.setPos(
                mid_point.x() - label_width / 2, mid_point.y() - label_height - 15
            )

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
        arrow_polygon = QPolygonF(
            [
                QPointF(end_point.x(), end_point.y()),
                QPointF(arrow_x1, arrow_y1),
                QPointF(arrow_x2, arrow_y2),
            ]
        )

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

    def add_connection(
        self, start_step_id, end_step_id, choice_text="", choice_index=None
    ):
        """Add a connection between two nodes with optional choice branching"""
        if start_step_id in self.nodes and end_step_id in self.nodes:
            start_node = self.nodes[start_step_id]
            end_node = self.nodes[end_step_id]

            connection = FlowChartConnection(
                start_node, end_node, choice_text, choice_index
            )
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
                if not step.choices or not any(
                    c.get("next_step_id") for c in step.choices
                ):
                    self.add_connection(step.id, step.next_step_id)

            # Connect choices to their responses with clear branching
            if step.choices:
                for i, choice in enumerate(step.choices):
                    next_step_id = choice.get("next_step_id")
                    if next_step_id and next_step_id in steps:
                        choice_text = choice.get("text", f"Option {i + 1}")
                        self.add_connection(
                            step.id, next_step_id, choice_text, choice_index=i
                        )

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
        self._position_children(
            start_step,
            steps,
            positioned,
            levels,
            start_x,
            start_y,
            level_width,
            level_height,
        )

        # Position any remaining unpositioned nodes (orphans)
        for step in steps.values():
            if step.id not in positioned:
                # Position orphan nodes to the right
                orphan_y = start_y + len(positioned) * 100
                self.add_node(step, start_x + 800, orphan_y)
                positioned[step.id] = (start_x + 800, orphan_y)

    def _position_children(
        self,
        parent_step,
        steps,
        positioned,
        levels,
        parent_x,
        parent_y,
        level_width,
        level_height,
    ):
        """Recursively position child nodes with proper branching"""
        if parent_step.type == DialogueStepType.PLAYER_CHOICE and parent_step.choices:
            # Branch out for each choice
            num_choices = len(parent_step.choices)
            total_width = (num_choices - 1) * level_width
            start_x = parent_x - total_width // 2

            for i, choice in enumerate(parent_step.choices):
                next_step_id = choice.get("next_step_id")
                if next_step_id and next_step_id in steps:
                    child_step = steps[next_step_id]
                    child_x = start_x + i * level_width
                    child_y = parent_y + level_height

                    if child_step.id not in positioned:
                        self.add_node(child_step, child_x, child_y)
                        positioned[child_step.id] = (child_x, child_y)
                        levels[child_step.id] = (levels[parent_step.id][0] + 1, i)

                        # Continue positioning children
                        self._position_children(
                            child_step,
                            steps,
                            positioned,
                            levels,
                            child_x,
                            child_y,
                            level_width,
                            level_height,
                        )

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
                self._position_children(
                    child_step,
                    steps,
                    positioned,
                    levels,
                    child_x,
                    child_y,
                    level_width,
                    level_height,
                )

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
                        start_point.x(),
                        start_point.y(),
                        start_point.x(),
                        start_point.y(),
                    )
                    self.temp_connection_line.setPen(
                        QPen(QColor("#ffff00"), 3, Qt.DashLine)
                    )
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
                start_point.x(), start_point.y(), pos.x(), pos.y()
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
            self.connection_created.emit(
                self.connection_start_node.step.id, end_node.step.id
            )

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
            DialogueStepType.END: "#7f8c8d",  # Medium gray
        }

        type_names = {
            DialogueStepType.START: "START",
            DialogueStepType.NPC_SPEECH: "NPC SPEAKS",
            DialogueStepType.PLAYER_CHOICE: "PLAYER CHOICE",
            DialogueStepType.PLAYER_SPEECH: "PLAYER SPEAKS",
            DialogueStepType.NPC_RESPONSE: "NPC RESPONSE",
            DialogueStepType.END: "END",
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
        if (
            self.step.type == DialogueStepType.NPC_SPEECH
            or self.step.type == DialogueStepType.NPC_RESPONSE
        ):
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
                speaker_label.setStyleSheet(
                    "font-weight: bold; color: #2c3e50; margin: 5px;"
                )
                layout.addWidget(speaker_label)

        # Choice selector for NPC Response steps
        if self.step.type == DialogueStepType.NPC_RESPONSE:
            if self.is_editable:
                choice_layout = QHBoxLayout()
                choice_layout.addWidget(QLabel("Responds to choice:"))
                self.choice_selector = QComboBox()
                self.choice_selector.addItem(
                    "Select which player choice this responds to", ""
                )
                self.choice_selector.currentIndexChanged.connect(
                    self.on_choice_selected
                )
                choice_layout.addWidget(self.choice_selector)
                layout.addLayout(choice_layout)
            else:
                if self.step.response_to_choice:
                    choice_label = QLabel(
                        f"Response to: {self.step.response_to_choice}"
                    )
                    choice_label.setStyleSheet(
                        "font-style: italic; color: #7f8c8d; margin: 5px;"
                    )
                    layout.addWidget(choice_label)

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
            self.question_edit.setPlaceholderText(
                "What choice does the player need to make?"
            )
            self.question_edit.setPlainText(self.step.text)
            self.question_edit.setMaximumHeight(80)
            self.question_edit.textChanged.connect(self.on_step_changed)
            layout.addWidget(self.question_edit)

            # Choices section
            choices_label = QLabel(
                "📝 Player Options (each leads to different NPC response):"
            )
            choices_label.setStyleSheet(
                "font-weight: bold; margin-top: 10px; color: #2c3e50;"
            )
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
                        background-color: #f8f9fa;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 7px;
                        padding: 0 5px 0 5px;
                        color: #7f8c8d;
                        font-weight: bold;
                    }
                """)
                choice_group.setTitle(f"Choice {i + 1}")
                choice_layout = QVBoxLayout()
                choice_group.setLayout(choice_layout)

                # Choice text
                choice_edit = QLineEdit(choice.get("text", ""))
                choice_edit.setPlaceholderText(f"Option {i + 1}...")
                choice_edit.textChanged.connect(self.on_step_changed)
                self.choice_edits.append(choice_edit)
                choice_layout.addWidget(QLabel("Player option text:"))
                choice_layout.addWidget(choice_edit)

                # Response mapping info
                target_step_id = choice.get("next_step_id", "")
                if target_step_id:
                    response_label = QLabel(f"→ Leads to: {target_step_id}")
                    response_label.setStyleSheet(
                        "color: #27ae60; font-style: italic; padding: 4px;"
                    )
                    response_label.setWordWrap(True)
                else:
                    response_label = QLabel("→ Not connected to any response yet")
                    response_label.setStyleSheet(
                        "color: #e74c3c; font-style: italic; padding: 4px;"
                    )
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
                    remove_btn.clicked.connect(
                        lambda checked, idx=i: self.remove_choice(idx)
                    )
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
                question_label.setStyleSheet(
                    "font-weight: bold; color: #2c3e50; margin: 10px;"
                )
                layout.addWidget(question_label)

            for i, choice in enumerate(self.step.choices):
                choice_text = choice.get("text", "No text")
                target_step_id = choice.get("next_step_id", "")

                if target_step_id:
                    # Show choice with connection indicator
                    choice_label = QLabel(f"• {choice_text} → Leads to response")
                    choice_label.setStyleSheet("""
                        QLabel {
                            background-color: #f8f9fa;
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
                            background-color: #f8f9fa;
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
            speech_label.setStyleSheet(
                "font-weight: bold; margin-top: 10px; color: #16a085;"
            )
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
                self.step.choices.append({"text": "", "next_step_id": ""})
            elif len(self.step.choices) > 1:
                # Keep only the first choice
                self.step.choices = [self.step.choices[0]]
        else:
            # Display mode - show as a single clear player speech option
            speech_label = QLabel("💬 Player says:")
            speech_label.setStyleSheet(
                "font-weight: bold; margin: 10px; color: #16a085;"
            )
            layout.addWidget(speech_label)

            # Show the speech text
            if self.step.text:
                speech_text_label = QLabel(self.step.text)
                speech_text_label.setStyleSheet("""
                    QLabel {
                        background-color: #f8f9fa;
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
                background-color: #f8f9fa;
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
        self.step.choices.append({"text": "", "next_step": ""})
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
            if hasattr(self, "speaker_edit"):
                self.step.speaker = self.speaker_edit.text()
            if hasattr(self, "text_edit"):
                self.step.text = self.text_edit.toPlainText()
            if hasattr(self, "question_edit"):
                self.step.text = self.question_edit.toPlainText()
            if hasattr(self, "speech_edit"):
                self.step.text = self.speech_edit.toPlainText()

            # Update choices
            if hasattr(self, "choice_edits"):
                for i, edit in enumerate(self.choice_edits):
                    if i < len(self.step.choices):
                        self.step.choices[i]["text"] = edit.text()

            self.step_changed.emit(f"update:{self.step.id}")

    def on_choice_selected(self, index):
        """Handle choice selection for NPC response"""
        if self.is_editable and hasattr(self, "choice_selector"):
            if index > 0:  # Skip placeholder item
                choice_data = self.choice_selector.itemData(index)
                if choice_data:
                    self.step.response_to_choice = choice_data
                    # Auto-link the choice to this response step
                    self._link_choice_to_response(choice_data, self.step.id)
                    self.step_changed.emit(f"update:{self.step.id}")
            else:
                self.step.response_to_choice = ""
                self.step_changed.emit(f"update:{self.step.id}")

    def _link_choice_to_response(self, choice_id, response_step_id):
        """Automatically link a player choice to an NPC response step"""
        # Parse choice_id to get parent step and choice index
        # Format: "{parent_step_id}_choice_{choice_index}"
        if "_choice_" in choice_id:
            parts = choice_id.split("_choice_")
            if len(parts) == 2:
                parent_step_id = parts[0]
                try:
                    choice_index = int(parts[1])
                    # Find all steps in the dialogue (we'll need access to parent)
                    # This is a simplified approach - in practice, we'd need better access to all steps
                    # For now, we'll emit a signal that the parent can handle
                    self.step_changed.emit(
                        f"link_choice:{parent_step_id}:{choice_index}:{response_step_id}"
                    )
                except ValueError:
                    pass  # Invalid choice index

    def update_choice_options(self, all_steps):
        """Update the choice selector with available player choices"""
        if (
            hasattr(self, "choice_selector")
            and self.step.type == DialogueStepType.NPC_RESPONSE
        ):
            # Clear current items
            self.choice_selector.clear()
            self.choice_selector.addItem(
                "Select which player choice this responds to", ""
            )

            # Find all player choice steps and add their options
            for step in all_steps.values():
                if step.type == DialogueStepType.PLAYER_CHOICE:
                    for i, choice in enumerate(step.choices):
                        choice_id = f"{step.id}_choice_{i}"
                        choice_text = choice.get("text", f"Choice {i + 1}")
                        display_text = f"{step.id}: {choice_text[:30]}..."
                        self.choice_selector.addItem(display_text, choice_id)

            # Select current choice if set
            if self.step.response_to_choice:
                for i in range(self.choice_selector.count()):
                    if self.choice_selector.itemData(i) == self.step.response_to_choice:
                        self.choice_selector.setCurrentIndex(i)
                        break

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

        # Tree view title
        title_label = QLabel("Dialogue Structure")
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2c3e50;"
        )
        left_layout.addWidget(title_label)

        # Tree widget for dialogue structure
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        self.tree_widget.setMinimumHeight(400)
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
        start_step = DialogueStep(id="step_1", type=DialogueStepType.START)
        self.add_step(start_step)

        # Create first NPC speech
        npc_step = DialogueStep(
            id="step_2",
            type=DialogueStepType.NPC_SPEECH,
            speaker="Guard",
            text="Hello there, traveler. What brings you to our village?",
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
                {"text": "I need supplies."},
            ],
        )
        self.add_step(choice_step)
        npc_step.next_step_id = choice_step.id

        self.update_tree()
        # Select the first NPC step by default
        self.select_step("step_2")

    def add_step(self, step: DialogueStep):
        """Add a dialogue step"""
        self.steps[step.id] = step
        self.next_step_id = max(self.next_step_id, int(step.id.split("_")[1]) + 1)
        self.dialogue_changed.emit()

    def remove_step(self, step_id: str):
        """Remove a dialogue step"""
        if step_id in self.steps and self.steps[step_id].type != DialogueStepType.START:
            del self.steps[step_id]
            self.update_tree()

            # If we deleted the selected step, select another one
            if self.selected_step_id == step_id:
                # Select the first available step
                available_steps = [
                    sid
                    for sid, step in self.steps.items()
                    if step.type != DialogueStepType.START
                ]
                if available_steps:
                    self.select_step(available_steps[0])
                else:
                    # No steps left, show no selection
                    self.selected_step_id = None
                    self.current_step_widget = None
                    # Show no selection label (check if widget still exists)
                    if (
                        hasattr(self, "no_selection_label")
                        and self.no_selection_label is not None
                    ):
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
            DialogueStepType.END: "END",
        }

        self.step_info_label.setText(f"Editing: {type_names.get(step.type, 'STEP')}")

        # Hide no selection label first (before clearing layout)
        if hasattr(self, "no_selection_label") and self.no_selection_label is not None:
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

        # Update choice options for NPC Response steps
        if step.type == DialogueStepType.NPC_RESPONSE:
            self.current_step_widget.update_choice_options(self.steps)

        # Enable/disable add next button based on step type
        can_add_next = step.type != DialogueStepType.END
        self.add_next_btn.setEnabled(can_add_next)

        # Update tree selection (without triggering recursion)
        self._updating_selection = True
        self.update_tree_selection(step_id)
        self._updating_selection = False

    def update_flow_chart_selection(self, selected_step_id):
        """Update flow chart selection to highlight selected step"""
        if hasattr(self, "flow_chart") and selected_step_id in self.flow_chart.nodes:
            # Clear all selections
            for node in self.flow_chart.nodes.values():
                node.setSelected(False)

            # Select the target node
            self.flow_chart.nodes[selected_step_id].setSelected(True)

    def update_tree_selection(self, selected_step_id):
        """Update tree selection to highlight selected step (legacy - kept for compatibility)"""
        if hasattr(self, "tree_widget"):
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
        find_item(
            [
                self.tree_widget.topLevelItem(i)
                for i in range(self.tree_widget.topLevelItemCount())
            ]
        )

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
        if hasattr(self, "flow_chart"):
            self.flow_chart.update_flow_chart(self.steps)

    def update_tree(self):
        """Update the enhanced tree view with AnswerId mapping, choice connections, and visual indicators"""
        if hasattr(self, "tree_widget"):
            self.tree_widget.clear()

            step_order = self.get_step_order()
            parent_items = {}

            for step_id in step_order:
                step = self.steps[step_id]

                # Enhanced step name with AnswerId
                name = self._format_step_name_enhanced(step)

                item = QTreeWidgetItem([name])
                item.setData(0, Qt.UserRole, step_id)

                # Color code step types
                self._apply_step_color_coding(item, step)

                # Add conditional logic indicators
                self._add_conditional_indicators(item, step)

                # Add flag usage indicators
                self._add_flag_usage_indicators(item, step)

                # Add to tree
                if step_id == "step_1":  # Start step
                    self.tree_widget.addTopLevelItem(item)
                else:
                    # Find parent
                    parent_id = self.find_parent_step(step_id)
                    if parent_id and parent_id in parent_items:
                        parent_items[parent_id].addChild(item)
                    else:
                        self.tree_widget.addTopLevelItem(item)
                parent_items[step_id] = item

                # Add choice connections with arrows
                if step.type == DialogueStepType.PLAYER_CHOICE:
                    self._add_choice_connections(item, step)

                # Expand parent
                if item.parent():
                    item.parent().setExpanded(True)

    def _format_step_name_enhanced(self, step):
        """Format step name with AnswerId and enhanced information"""
        type_names = {
            DialogueStepType.START: "🏁 START",
            DialogueStepType.NPC_SPEECH: f"👤 {step.speaker or 'NPC'}",
            DialogueStepType.PLAYER_CHOICE: "❓ CHOICE",
            DialogueStepType.NPC_RESPONSE: f"👤 {step.speaker or 'NPC'}",
            DialogueStepType.END: "🏁 END",
        }

        name = type_names.get(step.type, "STEP")

        # Add AnswerId if available
        if hasattr(step, "answer_id") and step.answer_id is not None:
            name += f" [AnswerId={step.answer_id}]"

        # Add choice count for player choices
        if step.type == DialogueStepType.PLAYER_CHOICE:
            connected_choices = sum(
                1 for choice in step.choices if choice.get("next_step_id")
            )
            total_choices = len(step.choices)
            name += f" ({connected_choices}/{total_choices} connected)"

        # Add response indicator for NPC responses
        elif (
            step.type == DialogueStepType.NPC_RESPONSE
            and hasattr(step, "response_to_choice")
            and step.response_to_choice
        ):
            name += f" ← {step.response_to_choice[:20]}{'...' if len(step.response_to_choice) > 20 else ''}"

        return name

    def _apply_step_color_coding(self, item, step):
        """Apply color coding based on step type"""
        from PySide6.QtGui import QColor

        color_map = {
            DialogueStepType.START: QColor(46, 204, 113),  # Green
            DialogueStepType.NPC_SPEECH: QColor(52, 152, 219),  # Blue
            DialogueStepType.PLAYER_CHOICE: QColor(155, 89, 182),  # Purple
            DialogueStepType.NPC_RESPONSE: QColor(230, 126, 34),  # Orange
            DialogueStepType.END: QColor(231, 76, 60),  # Red
        }

        if step.type in color_map:
            item.setForeground(0, color_map[step.type])

    def _add_conditional_indicators(self, item, step):
        """Add visual indicators for conditional logic"""
        if hasattr(step, "conditions") and step.conditions:
            # Add condition icon to the name
            current_text = item.text(0)
            item.setText(0, f"⚙️ {current_text}")

            # Add tooltip with condition details
            condition_text = "\n".join(f"• {cond}" for cond in step.conditions[:3])
            if len(step.conditions) > 3:
                condition_text += f"\n• ... and {len(step.conditions) - 3} more"
            item.setToolTip(0, f"Conditions:\n{condition_text}")

    def _add_flag_usage_indicators(self, item, step):
        """Add indicators for flag usage in conditions/actions"""
        flags_used = set()

        # Check conditions for flag usage
        if hasattr(step, "conditions"):
            for condition in step.conditions:
                # Extract flag names from conditions like "IsNpcFlagTrue(flag_name)"
                import re

                flag_matches = re.findall(
                    r'Is(?:Npc|Global)Flag(?:True|False)\s*\(\s*["\']([^"\']+)["\']',
                    condition,
                )
                flags_used.update(flag_matches)

        # Check actions for flag usage
        if hasattr(step, "actions"):
            for action in step.actions:
                # Extract flag names from actions like "SetNpcFlagTrue{Name = "flag_name"}"
                import re

                flag_matches = re.findall(
                    r'Set(?:Npc|Global|Reward)Flag(?:True|False)\s*\{\s*Name\s*=\s*["\']([^"\']+)["\']',
                    action,
                )
                flags_used.update(flag_matches)

        if flags_used:
            current_text = item.text(0)
            flag_indicator = f" 🚩({len(flags_used)})"
            item.setText(0, f"{current_text}{flag_indicator}")

            flag_list = "\n".join(f"• {flag}" for flag in sorted(flags_used))
            item.setToolTip(
                0, f"{item.toolTip(0) or ''}\n\nFlags Used:\n{flag_list}".strip()
            )

    def _add_choice_connections(self, item, step):
        """Add choice connections with arrow indicators and availability status"""
        for i, choice in enumerate(step.choices):
            choice_text = choice.get("text", "No text")
            next_step_id = choice.get("next_step_id")
            availability_rules = choice.get("availability_rules", [])

            # Evaluate choice availability
            is_available = self._evaluate_choice_availability(choice, step)

            # Create choice sub-item
            choice_label = chr(65 + i)  # A, B, C, ...
            connector = "└─" if i == len(step.choices) - 1 else "├─"
            connection_icon = "✅" if next_step_id else "⭕"
            availability_icon = "🔓" if is_available else "🔒"

            choice_display = f"{connector} [{choice_label}] {connection_icon} {availability_icon} {choice_text[:25]}{'...' if len(choice_text) > 25 else ''}"

            choice_item = QTreeWidgetItem([choice_display])
            item.addChild(choice_item)

            # Color code based on availability and connection status
            if not is_available:
                choice_item.setForeground(0, QColor(231, 76, 60))  # Red for unavailable
            elif next_step_id:
                choice_item.setForeground(
                    0, QColor(39, 174, 96)
                )  # Green for connected and available
            else:
                choice_item.setForeground(
                    0, QColor(149, 165, 166)
                )  # Gray for unconnected but available

            # Add availability rules info
            if availability_rules:
                rules_item = QTreeWidgetItem(
                    [f"   📋 Rules: {len(availability_rules)} conditions"]
                )
                rules_item.setForeground(0, QColor(230, 126, 34))  # Orange
                choice_item.addChild(rules_item)

                # Add individual rules
                for rule in availability_rules[:2]:  # Show first 2 rules
                    rule_item = QTreeWidgetItem([f"      • {rule}"])
                    rule_item.setForeground(0, QColor(149, 165, 166))  # Gray
                    rules_item.addChild(rule_item)

                if len(availability_rules) > 2:
                    more_item = QTreeWidgetItem(
                        [f"      • ... and {len(availability_rules) - 2} more"]
                    )
                    more_item.setForeground(0, QColor(149, 165, 166))  # Gray
                    rules_item.addChild(more_item)

            # Add next step info if connected
            if next_step_id:
                next_item = QTreeWidgetItem([f"   ↳ Next: {next_step_id}"])
                next_item.setForeground(0, QColor(52, 152, 219))  # Blue
                choice_item.addChild(next_item)

    def _evaluate_choice_availability(self, choice, step):
        """Evaluate if a choice is available based on its rules"""
        availability_rules = choice.get("availability_rules", [])
        if not availability_rules:
            return True  # No rules means always available

        # For now, implement basic flag checking
        # In a full implementation, this would evaluate complex conditions
        for rule in availability_rules:
            if not self._evaluate_single_rule(rule):
                return False
        return True

    def _evaluate_single_rule(self, rule):
        """Evaluate a single availability rule"""
        # Simple implementation - check for flag conditions
        # Format: "IsNpcFlagTrue(flag_name)", "IsGlobalFlagTrue(flag_name)", etc.
        import re

        # Check NPC flags
        npc_flag_match = re.match(r'IsNpcFlagTrue\(\s*["\']([^"\']+)["\']\s*\)', rule)
        if npc_flag_match:
            flag_name = npc_flag_match.group(1)
            # In a real implementation, check actual flag state
            # For now, assume flags are true if they exist in our flag manager
            if hasattr(self, "flag_manager") and self.flag_manager:
                return flag_name in [f.name for f in self.flag_manager.get_all_flags()]
            return True  # Default to available for demo

        # Check global flags
        global_flag_match = re.match(
            r'IsGlobalFlagTrue\(\s*["\']([^"\']+)["\']\s*\)', rule
        )
        if global_flag_match:
            flag_name = global_flag_match.group(1)
            # Similar logic for global flags
            if hasattr(self, "flag_manager") and self.flag_manager:
                return flag_name in [f.name for f in self.flag_manager.get_all_flags()]
            return True  # Default to available for demo

        # For other rule types, default to available
        return True

    def show_choice_availability_dialog(self, step_id, choice_index):
        """Show dialog for editing choice availability rules"""
        if step_id not in self.steps:
            return

        step = self.steps[step_id]
        if choice_index >= len(step.choices):
            return

        choice = step.choices[choice_index]

        dialog = ChoiceAvailabilityDialog(
            choice, self.flag_manager if hasattr(self, "flag_manager") else None, self
        )
        if dialog.exec() == QDialog.Accepted:
            # Update the choice with new rules
            step.choices[choice_index]["availability_rules"] = dialog.get_rules()
            self.update_tree()
            self.dialogue_changed.emit()

    def simulate_choice_availability(self, step_id, choice_index):
        """Simulate and show current availability status of a choice"""
        if step_id not in self.steps:
            return False

        step = self.steps[step_id]
        if choice_index >= len(step.choices):
            return False

        choice = step.choices[choice_index]
        is_available = self._evaluate_choice_availability(choice, step)

        # Show result in a message box
        choice_text = choice.get("text", "No text")
        rules_count = len(choice.get("availability_rules", []))

        if rules_count == 0:
            message = f"Choice: {choice_text}\n\nStatus: ✅ Always Available\n(No availability rules set)"
        else:
            status = "✅ Available" if is_available else "❌ Unavailable"
            message = f"Choice: {choice_text}\n\nStatus: {status}\nRules: {rules_count} conditions"

        QMessageBox.information(self, "Choice Availability Status", message)
        return is_available

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
                    if not choice.get("next_step_id"):
                        available_choice = choice
                        break

                if not available_choice:
                    # Create a new choice
                    new_choice = {
                        "text": f"Choice {len(start_step.choices) + 1}",
                        "next_step_id": "",
                    }
                    start_step.choices.append(new_choice)
                    available_choice = new_choice

                # Set the connection
                available_choice["next_step_id"] = end_step_id

                # Update the step widget if it's currently selected
                if self.selected_step_id == start_step_id and self.current_step_widget:
                    self.current_step_widget.rebuild_ui()

            elif start_step.type != DialogueStepType.PLAYER_CHOICE:
                # For non-choice steps, set the linear next_step
                start_step.next_step_id = end_step_id

            # Update the flow chart and emit change signal
            self.update_tree()
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
        feedback_label.setPos(
            view_center.x() - feedback_label.width() // 2,
            view_center.y() - feedback_label.height() // 2,
        )

        # Remove after 2 seconds
        QTimer.singleShot(
            2000,
            lambda: self.flow_chart.scene.removeItem(feedback_label)
            if feedback_label.scene()
            else None,
        )

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
        action_type, step_id = action.split(":", 1)

        if action_type == "add_next":
            self.add_next_step(step_id)
        elif action_type == "delete":
            self.remove_step(step_id)
        elif action_type == "update":
            self.update_tree()
            self.dialogue_changed.emit()
        elif action_type == "link_choice":
            # Format: "link_choice:{parent_step_id}:{choice_index}:{response_step_id}"
            parts = action.split(":", 3)
            if len(parts) >= 4:
                parent_step_id = parts[1]
                choice_index = int(parts[2])
                response_step_id = parts[3]
                self._link_choice_to_response(
                    parent_step_id, choice_index, response_step_id
                )

    def _link_choice_to_response(self, parent_step_id, choice_index, response_step_id):
        """Link a player choice to an NPC response step"""
        parent_step = self.steps.get(parent_step_id)
        if parent_step and parent_step.type == DialogueStepType.PLAYER_CHOICE:
            if 0 <= choice_index < len(parent_step.choices):
                # Set the next_step_id for the choice
                parent_step.choices[choice_index]["next_step_id"] = response_step_id
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
                text="What would you like to say?",
            )
        elif step_type == DialogueStepType.PLAYER_CHOICE:
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.PLAYER_CHOICE,
                text="What do you want to do?",
                choices=[
                    {"text": "Continue", "next_step_id": ""},
                    {"text": "Ask something else", "next_step_id": ""},
                ],
            )
        elif step_type == DialogueStepType.PLAYER_SPEECH:
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.PLAYER_SPEECH,
                text="I'd like to know more about this.",
                choices=[{"text": "Continue", "next_step_id": ""}],
            )
        elif step_type == DialogueStepType.NPC_RESPONSE:
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.NPC_RESPONSE,
                speaker="NPC",
                text="I understand. Let me help you with that.",
            )
        elif step_type == DialogueStepType.END:
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}", type=DialogueStepType.END
            )
        else:
            # Default to NPC speech
            new_step = DialogueStep(
                id=f"step_{self.next_step_id}",
                type=DialogueStepType.NPC_SPEECH,
                speaker="NPC",
                text="Hello!",
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
        has_start = any(
            step.type == DialogueStepType.START for step in self.steps.values()
        )
        if not has_start:
            errors.append("Missing start step")

        # Check for empty text
        for step_id, step in self.steps.items():
            if step.type in [
                DialogueStepType.NPC_SPEECH,
                DialogueStepType.NPC_RESPONSE,
                DialogueStepType.PLAYER_CHOICE,
            ]:
                if not step.text.strip():
                    warnings.append(f"Step {step_id} has empty text")
                if (
                    step.type
                    in [DialogueStepType.NPC_SPEECH, DialogueStepType.NPC_RESPONSE]
                    and not step.speaker.strip()
                ):
                    warnings.append(f"NPC step {step_id} has no speaker name")

        # Check choices
        for step_id, step in self.steps.items():
            if step.type == DialogueStepType.PLAYER_CHOICE:
                if len(step.choices) < 2:
                    errors.append(f"Choice step {step_id} must have at least 2 options")

                for i, choice in enumerate(step.choices):
                    if not choice.get("text", "").strip():
                        warnings.append(f"Choice {i + 1} in step {step_id} is empty")

        # Show results
        if errors:
            error_text = "❌ Validation Errors:\n" + "\n".join(
                f"• {error}" for error in errors
            )
            QMessageBox.critical(self, "Validation Failed", error_text)
        elif warnings:
            warning_text = "⚠️ Validation Warnings:\n" + "\n".join(
                f"• {warning}" for warning in warnings
            )
            QMessageBox.warning(self, "Validation Warnings", warning_text)
        else:
            QMessageBox.information(
                self, "Validation Success", "✅ Dialogue looks good!"
            )

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
            lua_code += f'        id = "{step_id}",\n'
            lua_code += f'        type = "{step.type.value}",\n'

            if step.speaker:
                lua_code += f'        speaker = "{step.speaker}",\n'
            if step.text:
                lua_code += f'        text = "{step.text}",\n'

            if step.choices:
                lua_code += f"        choices = {{\n"
                for choice in step.choices:
                    lua_code += f'            {{text = "{choice.get("text", "")}"}},\n'
                lua_code += f"        }},\n"

            if step.next_step_id:
                lua_code += f'        next = "{step.next_step_id}",\n'

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
        return {"steps": [step.to_dict() for step in self.steps.values()]}


class ChoiceAvailabilityDialog(QDialog):
    """Dialog for editing choice availability rules"""

    def __init__(self, choice, flag_manager, parent=None):
        super().__init__(parent)
        self.choice = choice
        self.flag_manager = flag_manager
        self.current_rules = choice.get("availability_rules", []).copy()
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Choice Availability Rules")
        self.setMinimumWidth(500)
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        # Header
        choice_text = self.choice.get("text", "No text")
        header = QLabel(f'Configure availability rules for choice:\n"{choice_text}"')
        header.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)

        # Instructions
        instructions = QLabel(
            "This choice will only be available if ALL rules below are true:"
        )
        instructions.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(instructions)

        # Rules list
        self.rules_list = QListWidget()
        self.rules_list.setMaximumHeight(150)
        for rule in self.current_rules:
            item = QListWidgetItem(rule)
            self.rules_list.addItem(item)
        layout.addWidget(self.rules_list)

        # Rule management buttons
        rules_buttons = QHBoxLayout()

        self.add_rule_btn = QPushButton("Add Rule")
        self.add_rule_btn.clicked.connect(self.add_rule)
        rules_buttons.addWidget(self.add_rule_btn)

        self.remove_rule_btn = QPushButton("Remove")
        self.remove_rule_btn.clicked.connect(self.remove_selected_rule)
        rules_buttons.addWidget(self.remove_rule_btn)

        self.clear_rules_btn = QPushButton("Clear All")
        self.clear_rules_btn.clicked.connect(self.clear_all_rules)
        rules_buttons.addWidget(self.clear_rules_btn)

        layout.addLayout(rules_buttons)

        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_label = QLabel(
            "Click 'Test Rules' to see current availability status"
        )
        preview_layout.addWidget(self.preview_label)

        self.test_rules_btn = QPushButton("Test Rules")
        self.test_rules_btn.clicked.connect(self.test_rules)
        preview_layout.addWidget(self.test_rules_btn)

        layout.addWidget(preview_group)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.update_button_states()

    def add_rule(self):
        """Add a new availability rule"""
        if not self.flag_manager:
            QMessageBox.warning(
                self,
                "No Flag Manager",
                "Flag manager not available. Cannot add flag-based rules.",
            )
            return

        # Get available flags
        flags = self.flag_manager.get_all_flags()

        # Create rule selection dialog
        rule_dialog = QDialog(self)
        rule_dialog.setWindowTitle("Add Availability Rule")
        rule_dialog.setMinimumWidth(400)

        layout = QVBoxLayout(rule_dialog)

        layout.addWidget(QLabel("Select rule type:"))

        rule_type_combo = QComboBox()
        rule_type_combo.addItems(["NPC Flag Check", "Global Flag Check"])
        layout.addWidget(rule_type_combo)

        layout.addWidget(QLabel("Select flag:"))

        flag_combo = QComboBox()
        for flag in sorted(flags, key=lambda f: f.name):
            flag_combo.addItem(f"{flag.name} ({flag.flag_type})")
        layout.addWidget(flag_combo)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(rule_dialog.accept)
        buttons.rejected.connect(rule_dialog.reject)
        layout.addWidget(buttons)

        if rule_dialog.exec() == QDialog.Accepted:
            flag_text = flag_combo.currentText()
            if flag_text:
                flag_name = flag_text.split(" (")[0]  # Extract flag name
                rule_type = rule_type_combo.currentText()

                if "NPC Flag" in rule_type:
                    rule = f'IsNpcFlagTrue("{flag_name}")'
                else:
                    rule = f'IsGlobalFlagTrue("{flag_name}")'

                self.current_rules.append(rule)
                self.rules_list.addItem(QListWidgetItem(rule))
                self.update_button_states()

    def remove_selected_rule(self):
        """Remove the selected rule"""
        current_row = self.rules_list.currentRow()
        if current_row >= 0:
            self.rules_list.takeItem(current_row)
            self.current_rules.pop(current_row)
            self.update_button_states()

    def clear_all_rules(self):
        """Clear all rules"""
        self.rules_list.clear()
        self.current_rules.clear()
        self.update_button_states()

    def test_rules(self):
        """Test current rules and show availability status"""
        # Simple test - in real implementation this would evaluate against game state
        rule_count = len(self.current_rules)
        if rule_count == 0:
            status = "✅ Available (no rules)"
        else:
            # For demo, assume all rules pass
            status = f"✅ Available ({rule_count} rules would be evaluated)"

        self.preview_label.setText(f"Current Status: {status}")

    def update_button_states(self):
        """Update button enabled states"""
        has_selection = self.rules_list.currentRow() >= 0
        self.remove_rule_btn.setEnabled(has_selection)
        self.clear_rules_btn.setEnabled(len(self.current_rules) > 0)

    def get_rules(self):
        """Get the current rules list"""
        return self.current_rules.copy()


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
