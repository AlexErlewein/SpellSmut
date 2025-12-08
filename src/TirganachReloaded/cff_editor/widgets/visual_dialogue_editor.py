#!/usr/bin/env python3
"""
Visual Dialogue Editor

A comprehensive visual dialogue editor with node-based interface,
tree view, and visual connections between dialogue nodes.
"""

import sys
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import math

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QPushButton,
    QLabel,
    QGroupBox,
    QFormLayout,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QStatusBar,
    QMenuBar,
    QToolBar,
    QDialog,
    QDialogButtonBox,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QFrame,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsTextItem,
    QGraphicsLineItem,
    QGraphicsPolygonItem,
    QSlider,
    QStyleOptionViewItem,
    QStyle,
)
from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
    QThread,
    QTimer,
    QSettings,
    QSize,
    QPoint,
    QSortFilterProxyModel,
    QItemSelectionModel,
    QRectF,
    QPointF,
    QObject,
    Signal,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtGui import (
    QFont,
    QPixmap,
    QIcon,
    QAction,
    QKeySequence,
    QPalette,
    QColor,
    QTextCursor,
    QIntValidator,
    QPen,
    QBrush,
    QPainter,
    QPolygonF,
    QTransform,
    QMouseEvent,
    QWheelEvent,
    QKeyEvent,
)

# Import CFF components
try:
    from TirganachReloaded.cff_editor.models.quest_models import Dialogue
    from TirganachReloaded.cff_editor.logging_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    # Fallback for standalone testing
    import logging

    logger = logging.getLogger(__name__)

    # Simple Dialogue class for fallback
    @dataclass
    class Dialogue:
        id: str = ""
        speaker: str = ""
        text: str = ""
        choices: List[Dict[str, str]] = field(default_factory=list)
        conditions: List[str] = field(default_factory=list)
        actions: List[str] = field(default_factory=list)
        next_dialogue: Optional[str] = None


class NodeType(Enum):
    """Types of dialogue nodes"""

    PLAYER = "player"
    NPC = "npc"
    CONDITIONAL = "conditional"
    CHOICE = "choice"
    START = "start"
    END = "end"


@dataclass
class DialogueNode:
    """Represents a single dialogue node"""

    id: str
    node_type: NodeType
    speaker: str = ""
    text: str = ""
    choices: List[Dict[str, str]] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    position: Tuple[float, float] = (0.0, 0.0)
    next_nodes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        return {
            "id": self.id,
            "type": self.node_type.value,
            "speaker": self.speaker,
            "text": self.text,
            "choices": self.choices,
            "conditions": self.conditions,
            "actions": self.actions,
            "position": self.position,
            "next_nodes": self.next_nodes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DialogueNode":
        """Create node from dictionary"""
        # Handle both "type" and "node_type" for backward compatibility
        node_type_key = "type" if "type" in data else "node_type"
        return cls(
            id=data["id"],
            node_type=NodeType(data[node_type_key]),
            speaker=data.get("speaker", ""),
            text=data.get("text", ""),
            choices=data.get("choices", []),
            conditions=data.get("conditions", []),
            actions=data.get("actions", []),
            position=tuple(data.get("position", (0.0, 0.0))),
            next_nodes=data.get("next_nodes", []),
        )


class DialogueNodeItem(QGraphicsRectItem):
    """Visual representation of a dialogue node"""

    def __init__(self, node: DialogueNode, width: int = 200, height: int = 120):
        super().__init__(0, 0, width, height)

        self.node = node
        self.width = width
        self.height = height
        self.selected = False
        self.hovering = False

        # Set visual properties based on node type
        self.setup_appearance()

        # Create text elements
        self.create_text_elements()

        # Create connection points
        self.create_connection_points()

        # Set position
        self.setPos(node.position[0], node.position[1])

        # Make item movable and selectable
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # Accept hover events
        self.setAcceptHoverEvents(True)

    def setup_appearance(self):
        """Setup visual appearance based on node type"""
        colors = {
            NodeType.START: QColor(100, 200, 100),
            NodeType.END: QColor(200, 100, 100),
            NodeType.NPC: QColor(100, 150, 200),
            NodeType.PLAYER: QColor(150, 200, 100),
            NodeType.CHOICE: QColor(200, 150, 100),
            NodeType.CONDITIONAL: QColor(200, 100, 200),
        }

        color = colors.get(self.node.node_type, QColor(150, 150, 150))

        # Set pen and brush
        self.setPen(QPen(color.darker(150), 2))
        self.setBrush(QBrush(color))

        # Add rounded corners
        self.setRect(0, 0, self.width, self.height)

    def create_text_elements(self):
        """Create text elements for the node"""
        # Title text (node type and ID)
        title_text = f"{self.node.node_type.value.upper()}: {self.node.id}"
        if self.node.speaker:
            title_text = f"{self.node.speaker}\n{title_text}"

        self.title_item = QGraphicsTextItem(title_text, self)
        title_font = QFont("Arial", 10, QFont.Bold)
        self.title_item.setFont(title_font)
        self.title_item.setDefaultTextColor(QColor(255, 255, 255))

        # Position title at top
        title_rect = self.title_item.boundingRect()
        self.title_item.setPos(5, 5)

        # Content text (dialogue text)
        if self.node.text:
            # Truncate long text
            display_text = self.node.text
            if len(display_text) > 50:
                display_text = display_text[:47] + "..."

            self.text_item = QGraphicsTextItem(display_text, self)
            text_font = QFont("Arial", 9)
            self.text_item.setFont(text_font)
            self.text_item.setDefaultTextColor(QColor(255, 255, 255))

            # Position text below title
            self.text_item.setPos(5, 30)

    def create_connection_points(self):
        """Create visual connection points"""
        self.input_point = QPointF(0, self.height / 2)
        self.output_point = QPointF(self.width, self.height / 2)

        # Draw connection points as small circles
        input_circle = QGraphicsRectItem(-5, self.height / 2 - 5, 10, 10, self)
        input_circle.setBrush(QBrush(QColor(255, 255, 0)))
        input_circle.setPen(QPen(QColor(200, 200, 0), 1))

        output_circle = QGraphicsRectItem(
            self.width - 5, self.height / 2 - 5, 10, 10, self
        )
        output_circle.setBrush(QBrush(QColor(0, 255, 0)))
        output_circle.setPen(QPen(QColor(0, 200, 0), 1))

    def itemChange(self, change, value):
        """Handle item changes"""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Update node position
            self.node.position = (value.x(), value.y())

        return super().itemChange(change, value)

    def paint(self, painter, option, widget):
        """Custom paint method"""
        super().paint(painter, option, widget)

        # Draw selection highlight
        if self.isSelected():
            painter.setPen(QPen(QColor(255, 255, 0), 3, Qt.DashLine))
            painter.drawRect(self.rect().adjusted(-2, -2, 2, 2))

        # Draw hover effect
        if self.hovering:
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawRect(self.rect().adjusted(1, 1, -1, -1))

    def hoverEnterEvent(self, event):
        """Handle hover enter"""
        self.hovering = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Handle hover leave"""
        self.hovering = False
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.setSelected(True)
            # Selection will be handled by the scene/view

        super().mousePressEvent(event)


class DialogueConnectionItem(QGraphicsLineItem):
    """Visual representation of a connection between dialogue nodes"""

    def __init__(self, start_node: DialogueNodeItem, end_node: DialogueNodeItem):
        super().__init__()

        self.start_node = start_node
        self.end_node = end_node

        # Set visual properties
        self.setPen(QPen(QColor(100, 100, 100), 2))
        self.setZValue(-1)  # Render behind nodes

        # Update position
        self.update_position()

        # Track node movements (handled by scene updates)

    def update_position(self):
        """Update line position based on node positions"""
        start_pos = self.start_node.scenePos()
        end_pos = self.end_node.scenePos()

        # Calculate connection points
        start_point = QPointF(
            start_pos.x() + self.start_node.width,
            start_pos.y() + self.start_node.height / 2,
        )
        end_point = QPointF(end_pos.x(), end_pos.y() + self.end_node.height / 2)

        self.setLine(start_point.x(), start_point.y(), end_point.x(), end_point.y())

    def paint(self, painter, option, widget):
        """Custom paint method for arrow"""
        super().paint(painter, option, widget)

        # Draw arrowhead
        line = self.line()
        angle = math.atan2(line.dy(), line.dx())

        # Arrowhead points
        arrow_length = 10
        arrow_angle = 0.5

        x1 = line.x2()
        y1 = line.y2()

        x2 = x1 - arrow_length * math.cos(angle - arrow_angle)
        y2 = y1 - arrow_length * math.sin(angle - arrow_angle)

        x3 = x1 - arrow_length * math.cos(angle + arrow_angle)
        y3 = y1 - arrow_length * math.sin(angle + arrow_angle)

        # Draw arrowhead
        arrow = QPolygonF([QPointF(x1, y1), QPointF(x2, y2), QPointF(x3, y3)])
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawPolygon(arrow)


class DialogueGraphicsView(QGraphicsView):
    """Custom graphics view for dialogue editing"""

    # Signals
    node_selected = Signal(object)
    connection_created = Signal(str, str)

    def __init__(self, scene):
        super().__init__(scene)

        self.scene = scene
        self.nodes = {}
        self.connections = []
        self.selected_node = None
        self.connecting_from = None

        # Enable mouse tracking
        self.setMouseTracking(True)

        # Set render hints
        self.setRenderHint(QPainter.Antialiasing)

        # Set drag mode
        self.setDragMode(QGraphicsView.RubberBandDrag)

        # Connect scene selection change
        scene.selectionChanged.connect(self.on_selection_changed)

    def add_node(self, node: DialogueNode):
        """Add a dialogue node to the scene"""
        node_item = DialogueNodeItem(node)
        self.scene.addItem(node_item)

        # Store reference
        self.nodes[node.id] = node_item

        # Signals handled by scene selection changes

        return node_item

    def add_connection(self, from_node_id: str, to_node_id: str):
        """Add a connection between nodes"""
        if from_node_id in self.nodes and to_node_id in self.nodes:
            from_item = self.nodes[from_node_id]
            to_item = self.nodes[to_node_id]

            connection = DialogueConnectionItem(from_item, to_item)
            self.scene.addItem(connection)
            self.connections.append(connection)

            # Update node data
            from_item.node.next_nodes.append(to_node_id)

            return connection
        return None

    def on_node_selected(self, node: DialogueNode):
        """Handle node selection"""
        self.selected_node = node
        self.node_selected.emit(node)

    def on_node_moved(self, node_id: str, x: float, y: float):
        """Handle node movement"""
        # Connections will update automatically
        pass

    def on_selection_changed(self):
        """Handle scene selection change"""
        try:
            if self.scene is None:
                return
            selected_items = self.scene.selectedItems()
            if selected_items:
                for item in selected_items:
                    if isinstance(item, DialogueNodeItem):
                        self.on_node_selected(item.node)
                        break
        except RuntimeError:
            # Scene was deleted, ignore
            pass

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        # Save the scene pos
        old_pos = self.mapToScene(event.position())

        # Zoom
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)

        # Get the new position
        new_pos = self.mapToScene(event.position())

        # Move scene to old position
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            # Check if clicking on empty space
            # Convert QPointF to QPoint for mapToScene
            pos = self.mapToScene(event.position().toPoint())
            item = self.scene.itemAt(pos, self.transform())

            if not item:
                # Deselect all
                self.scene.clearSelection()
                self.selected_node = None

        super().mousePressEvent(event)


class DialoguePropertiesWidget(QWidget):
    """Widget for editing dialogue node properties"""

    # Signals
    properties_changed = Signal(str, dict)

    def __init__(self):
        super().__init__()
        self.current_node = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Node Properties")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        # Node information
        self.info_group = QGroupBox("Node Information")
        info_layout = QFormLayout()

        self.id_label = QLabel("")
        self.type_label = QLabel("")

        info_layout.addRow("ID:", self.id_label)
        info_layout.addRow("Type:", self.type_label)
        self.info_group.setLayout(info_layout)
        layout.addWidget(self.info_group)

        # Speaker
        speaker_layout = QHBoxLayout()
        self.speaker_edit = QLineEdit()
        self.speaker_edit.textChanged.connect(self.on_properties_changed)
        speaker_layout.addWidget(QLabel("Speaker:"))
        speaker_layout.addWidget(self.speaker_edit)
        layout.addLayout(speaker_layout)

        # Dialogue text
        text_label = QLabel("Dialogue Text:")
        layout.addWidget(text_label)

        self.text_edit = QTextEdit()
        self.text_edit.setMaximumHeight(100)
        self.text_edit.textChanged.connect(self.on_properties_changed)
        layout.addWidget(self.text_edit)

        # Choices (for choice nodes)
        self.choices_group = QGroupBox("Choices")
        choices_layout = QVBoxLayout()

        self.choices_table = QTableWidget(0, 2)
        self.choices_table.setHorizontalHeaderLabels(["Text", "Next Node"])
        self.choices_table.horizontalHeader().setStretchLastSection(True)
        self.choices_table.cellChanged.connect(self.on_choice_changed)
        choices_layout.addWidget(self.choices_table)

        choices_buttons = QHBoxLayout()
        self.add_choice_btn = QPushButton("Add Choice")
        self.add_choice_btn.clicked.connect(self.add_choice)
        self.remove_choice_btn = QPushButton("Remove Choice")
        self.remove_choice_btn.clicked.connect(self.remove_choice)
        choices_buttons.addWidget(self.add_choice_btn)
        choices_buttons.addWidget(self.remove_choice_btn)
        choices_layout.addLayout(choices_buttons)

        self.choices_group.setLayout(choices_layout)
        layout.addWidget(self.choices_group)

        # Conditions
        self.conditions_group = QGroupBox("Conditions")
        conditions_layout = QVBoxLayout()

        self.conditions_list = QListWidget()
        self.conditions_list.setMaximumHeight(80)
        conditions_layout.addWidget(self.conditions_list)

        condition_buttons = QHBoxLayout()
        self.add_condition_btn = QPushButton("Add Condition")
        self.add_condition_btn.clicked.connect(self.add_condition)
        self.remove_condition_btn = QPushButton("Remove Condition")
        self.remove_condition_btn.clicked.connect(self.remove_condition)
        condition_buttons.addWidget(self.add_condition_btn)
        condition_buttons.addWidget(self.remove_condition_btn)
        conditions_layout.addLayout(condition_buttons)

        self.conditions_group.setLayout(conditions_layout)
        layout.addWidget(self.conditions_group)

        # Actions
        self.actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()

        self.actions_list = QListWidget()
        self.actions_list.setMaximumHeight(80)
        actions_layout.addWidget(self.actions_list)

        action_buttons = QHBoxLayout()
        self.add_action_btn = QPushButton("Add Action")
        self.add_action_btn.clicked.connect(self.add_action)
        self.remove_action_btn = QPushButton("Remove Action")
        self.remove_action_btn.clicked.connect(self.remove_action)
        action_buttons.addWidget(self.add_action_btn)
        action_buttons.addWidget(self.remove_action_btn)
        actions_layout.addLayout(action_buttons)

        self.actions_group.setLayout(actions_layout)
        layout.addWidget(self.actions_group)

        # Connections
        self.connections_group = QGroupBox("Connections")
        connections_layout = QVBoxLayout()

        self.connections_list = QListWidget()
        self.connections_list.setMaximumHeight(80)
        connections_layout.addWidget(self.connections_list)

        self.connections_group.setLayout(connections_layout)
        layout.addWidget(self.connections_group)

        layout.addStretch()
        self.setLayout(layout)

        # Initially hide all groups
        self.choices_group.setVisible(False)
        self.conditions_group.setVisible(False)
        self.actions_group.setVisible(False)
        self.connections_group.setVisible(False)

    def set_node(self, node: DialogueNode):
        """Set the current node being edited"""
        self.current_node = node

        if not node:
            # Clear all fields
            self.id_label.setText("")
            self.type_label.setText("")
            self.speaker_edit.setText("")
            self.text_edit.setText("")
            self.choices_table.setRowCount(0)
            self.conditions_list.clear()
            self.actions_list.clear()
            self.connections_list.clear()

            # Hide all groups
            self.choices_group.setVisible(False)
            self.conditions_group.setVisible(False)
            self.actions_group.setVisible(False)
            self.connections_group.setVisible(False)
            return

        # Update basic info
        self.id_label.setText(node.id)
        self.type_label.setText(node.node_type.value.title())
        self.speaker_edit.setText(node.speaker)
        self.text_edit.setText(node.text)

        # Update choices
        self.update_choices_table()

        # Update conditions
        self.conditions_list.clear()
        for condition in node.conditions:
            self.conditions_list.addItem(condition)

        # Update actions
        self.actions_list.clear()
        for action in node.actions:
            self.actions_list.addItem(action)

        # Update connections
        self.connections_list.clear()
        for next_node in node.next_nodes:
            self.connections_list.addItem(f"→ {next_node}")

        # Show/hide groups based on node type
        self.choices_group.setVisible(node.node_type == NodeType.CHOICE)
        self.conditions_group.setVisible(node.node_type == NodeType.CONDITIONAL)
        self.actions_group.setVisible(True)  # Actions available for most types
        self.connections_group.setVisible(True)

    def update_choices_table(self):
        """Update the choices table"""
        if not self.current_node:
            return

        self.choices_table.setRowCount(len(self.current_node.choices))

        for row, choice in enumerate(self.current_node.choices):
            text_item = QTableWidgetItem(choice.get("text", ""))
            next_node_item = QTableWidgetItem(choice.get("next_node", ""))

            self.choices_table.setItem(row, 0, text_item)
            self.choices_table.setItem(row, 1, next_node_item)

    def add_choice(self):
        """Add a new choice"""
        if not self.current_node:
            return

        new_choice = {"text": "", "next_node": ""}
        self.current_node.choices.append(new_choice)
        self.update_choices_table()
        self.on_properties_changed()

    def remove_choice(self):
        """Remove selected choice"""
        if not self.current_node:
            return

        current_row = self.choices_table.currentRow()
        if current_row >= 0:
            del self.current_node.choices[current_row]
            self.update_choices_table()
            self.on_properties_changed()

    def add_condition(self):
        """Add a new condition"""
        if not self.current_node:
            return

        # Simple dialog for condition input
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Condition")
        layout = QVBoxLayout()

        edit = QLineEdit()
        edit.setPlaceholderText("Enter condition (e.g., 'player_level >= 5')")
        layout.addWidget(edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            condition = edit.text().strip()
            if condition:
                self.current_node.conditions.append(condition)
                self.conditions_list.addItem(condition)
                self.on_properties_changed()

    def remove_condition(self):
        """Remove selected condition"""
        if not self.current_node:
            return

        current_item = self.conditions_list.currentItem()
        if current_item:
            row = self.conditions_list.row(current_item)
            del self.current_node.conditions[row]
            self.conditions_list.takeItem(row)
            self.on_properties_changed()

    def add_action(self):
        """Add a new action"""
        if not self.current_node:
            return

        # Simple dialog for action input
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Action")
        layout = QVBoxLayout()

        edit = QLineEdit()
        edit.setPlaceholderText("Enter action (e.g., 'give_item(sword_01)')")
        layout.addWidget(edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            action = edit.text().strip()
            if action:
                self.current_node.actions.append(action)
                self.actions_list.addItem(action)
                self.on_properties_changed()

    def remove_action(self):
        """Remove selected action"""
        if not self.current_node:
            return

        current_item = self.actions_list.currentItem()
        if current_item:
            row = self.actions_list.row(current_item)
            del self.current_node.actions[row]
            self.actions_list.takeItem(row)
            self.on_properties_changed()

    def on_properties_changed(self):
        """Handle property changes"""
        if not self.current_node:
            return

        # Update node data
        self.current_node.speaker = self.speaker_edit.text()
        self.current_node.text = self.text_edit.toPlainText()

        # Update choices from table
        self.current_node.choices.clear()
        for row in range(self.choices_table.rowCount()):
            text_item = self.choices_table.item(row, 0)
            next_node_item = self.choices_table.item(row, 1)

            if text_item:
                choice = {
                    "text": text_item.text(),
                    "next_node": next_node_item.text() if next_node_item else "",
                }
                self.current_node.choices.append(choice)

        # Emit signal
        self.properties_changed.emit(self.current_node.id, self.current_node.to_dict())

    def on_choice_changed(self, row, column):
        """Handle choice table changes"""
        self.on_properties_changed()


class DialogueTreeWidget(QWidget):
    """Tree view of dialogue structure"""

    # Signals
    node_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.nodes = {}
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Dialogue Tree")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        # Tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["ID", "Type", "Speaker", "Text Preview"])
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree_widget)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.expand_btn = QPushButton("Expand All")
        self.expand_btn.clicked.connect(self.tree_widget.expandAll)
        buttons_layout.addWidget(self.expand_btn)

        self.collapse_btn = QPushButton("Collapse All")
        self.collapse_btn.clicked.connect(self.tree_widget.collapseAll)
        buttons_layout.addWidget(self.collapse_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def set_nodes(self, nodes: Dict[str, DialogueNode]):
        """Set the dialogue nodes"""
        self.nodes = nodes
        self.refresh_tree()

    def refresh_tree(self):
        """Refresh the tree view"""
        self.tree_widget.clear()

        if not self.nodes:
            return

        # Find start node
        start_node = None
        for node in self.nodes.values():
            if node.node_type == NodeType.START:
                start_node = node
                break

        if not start_node:
            # If no start node, pick the first one
            start_node = list(self.nodes.values())[0]

        # Build tree
        self.add_tree_item(None, start_node, set())

        # Expand first level
        self.tree_widget.expandToDepth(0)

    def add_tree_item(self, parent_item, node: DialogueNode, visited: set):
        """Add a node to the tree"""
        if node.id in visited:
            # Prevent infinite loops
            return

        visited.add(node.id)

        # Create tree item
        if parent_item:
            tree_item = QTreeWidgetItem(parent_item)
        else:
            tree_item = QTreeWidgetItem(self.tree_widget)

        # Set item data
        tree_item.setText(0, node.id)
        tree_item.setText(1, node.node_type.value.title())
        tree_item.setText(2, node.speaker)

        # Text preview
        text_preview = node.text
        if len(text_preview) > 30:
            text_preview = text_preview[:27] + "..."
        tree_item.setText(3, text_preview)

        # Store node ID
        tree_item.setData(0, Qt.UserRole, node.id)

        # Add children
        for next_node_id in node.next_nodes:
            if next_node_id in self.nodes:
                self.add_tree_item(tree_item, self.nodes[next_node_id], visited)

    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item click"""
        node_id = item.data(0, Qt.UserRole)
        if node_id:
            self.node_selected.emit(node_id)


class VisualDialogueEditor(QMainWindow):
    """Main visual dialogue editor window"""

    def __init__(self):
        super().__init__()
        self.nodes = {}
        self.selected_node = None

        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()

        logger.info("Visual Dialogue Editor initialized")

    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("Visual Dialogue Editor")
        self.setGeometry(100, 100, 1400, 900)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Node palette and tree view
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # Node palette (NPC button first as it's the most common starting point)
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

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_node_palette(self, layout):
        """Setup node palette"""
        palette_group = QGroupBox("Node Palette")
        palette_layout = QVBoxLayout()

        # Node type buttons
        self.start_btn = QPushButton("Start Node")
        self.start_btn.clicked.connect(lambda: self.add_node(NodeType.START))
        palette_layout.addWidget(self.start_btn)

        self.npc_btn = QPushButton("NPC Dialogue")
        self.npc_btn.clicked.connect(lambda: self.add_node(NodeType.NPC))
        palette_layout.addWidget(self.npc_btn)

        self.player_btn = QPushButton("Player Dialogue")
        self.player_btn.clicked.connect(lambda: self.add_node(NodeType.PLAYER))
        palette_layout.addWidget(self.player_btn)

        self.choice_btn = QPushButton("Choice Node")
        self.choice_btn.clicked.connect(lambda: self.add_node(NodeType.CHOICE))
        palette_layout.addWidget(self.choice_btn)

        self.conditional_btn = QPushButton("Conditional Node")
        self.conditional_btn.clicked.connect(
            lambda: self.add_node(NodeType.CONDITIONAL)
        )
        palette_layout.addWidget(self.conditional_btn)

        self.end_btn = QPushButton("End Node")
        self.end_btn.clicked.connect(lambda: self.add_node(NodeType.END))
        palette_layout.addWidget(self.end_btn)

        # Connection button
        palette_layout.addWidget(QLabel(""))

        self.connection_btn = QPushButton("Create Connection")
        self.connection_btn.clicked.connect(self.create_connection_mode)
        palette_layout.addWidget(self.connection_btn)

        palette_group.setLayout(palette_layout)
        layout.addWidget(palette_group)

    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Dialogue", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_dialogue)
        file_menu.addAction(new_action)

        open_action = QAction("Open Dialogue", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_dialogue)
        file_menu.addAction(open_action)

        save_action = QAction("Save Dialogue", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_dialogue)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        export_action = QAction("Export to Lua", self)
        export_action.triggered.connect(self.export_to_lua)
        file_menu.addAction(export_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        delete_action = QAction("Delete Node", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_selected_node)
        edit_menu.addAction(delete_action)

        # View menu
        view_menu = menubar.addMenu("View")

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)

    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # File operations
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_dialogue)
        toolbar.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_dialogue)
        toolbar.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_dialogue)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Edit operations
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected_node)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        # View operations
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)

    def add_node(self, node_type: NodeType):
        """Add a new dialogue node"""
        # Generate unique ID
        node_id = f"{node_type.value}_{len(self.nodes) + 1}"

        # Calculate position based on selected node or default
        if self.selected_node:
            # Position new node to the right of selected node
            selected_pos = self.selected_node.position
            new_x = selected_pos[0] + 250  # Space nodes horizontally
            new_y = selected_pos[1]
        else:
            # Default positioning
            new_x = 100 + len(self.nodes) * 50
            new_y = 100 + len(self.nodes) * 50

        # Create node
        node = DialogueNode(
            id=node_id,
            node_type=node_type,
            position=(new_x, new_y),
        )

        # Add to collection
        self.nodes[node_id] = node

        # Auto-connect to selected node if appropriate
        if self.selected_node and node_type != NodeType.START:
            # For NPC responses, auto-connect from selected player choice
            if (
                node_type == NodeType.NPC
                and self.selected_node.node_type == NodeType.PLAYER
            ):
                # This is a response to a player choice
                node.speaker = "NPC"  # Default speaker
                # Note: In a full implementation, we'd need to handle choice indexing
            elif self.selected_node.node_type in [NodeType.NPC, NodeType.START]:
                # Connect sequentially
                self.selected_node.next_nodes.append(node_id)
                self.graphics_view.add_connection(self.selected_node.id, node_id)

        # Add to graphics view
        self.graphics_view.add_node(node)

        # Update tree view
        self.tree_widget.set_nodes(self.nodes)

        # Auto-select the new node
        self.select_node(node_id)

        self.status_bar.showMessage(f"Added {node_type.value} node: {node_id}")

    def create_connection_mode(self):
        """Enter connection creation mode"""
        if self.selected_node:
            self.status_bar.showMessage("Click on target node to create connection")
            # In a full implementation, this would enter a special mode
            # For now, we'll just show a message
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

    def on_node_selected(self, node: DialogueNode):
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
                # Update visual representation if needed
                node_item.node = self.nodes[node_id]
                node_item.update()

            # Update tree view
            self.tree_widget.set_nodes(self.nodes)

            self.status_bar.showMessage(f"Updated node: {node_id}")

    def connect_choice_to_response(self, choice_node_id: str, choice_index: int):
        """Show dialog to connect a choice to a response"""
        if choice_node_id not in self.nodes:
            return

        choice_node = self.nodes[choice_node_id]
        if choice_index >= len(choice_node.choices):
            return

        # Create dialog to select response node
        dialog = QDialog(self)
        dialog.setWindowTitle(
            f"Connect Choice '{choice_node.choices[choice_index].get('text', '')}'"
        )
        dialog.setMinimumWidth(400)

        layout = QVBoxLayout(dialog)

        # Instructions
        instructions = QLabel(
            "Select which NPC response this player choice should lead to:"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Node selection
        self.response_combo = QComboBox()
        self.response_combo.addItem("Select a response node...", "")

        # Add all NPC response nodes
        for node_id, node in self.nodes.items():
            if node.node_type in [NodeType.NPC, NodeType.CONDITIONAL]:
                display_text = (
                    f"{node_id}: {node.text[:50]}..."
                    if len(node.text) > 50
                    else f"{node_id}: {node.text}"
                )
                self.response_combo.addItem(display_text, node_id)

        layout.addWidget(self.response_combo)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_response_id = self.response_combo.currentData()
            if selected_response_id:
                # Connect the choice to the response
                choice_node.choices[choice_index]["next_node"] = selected_response_id

                # Update connections
                self.graphics_view.add_connection(choice_node_id, selected_response_id)

                # Update tree view
                self.tree_widget.set_nodes(self.nodes)

                # Update properties if this node is selected
                if self.selected_node and self.selected_node.id == choice_node_id:
                    self.properties_widget.set_node(choice_node)

                self.status_bar.showMessage(
                    f"Connected choice to response: {selected_response_id}"
                )

    def delete_selected_node(self):
        """Delete the selected node"""
        if not self.selected_node:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Node",
            f"Are you sure you want to delete node '{self.selected_node.id}'?",
            QMessageBox.Yes | QMessageBox.No,
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
                if (
                    connection.start_node.node.id == node_id
                    or connection.end_node.node.id == node_id
                ):
                    connections_to_remove.append(connection)

            for connection in connections_to_remove:
                self.graphics_view.scene.removeItem(connection)
                self.graphics_view.connections.remove(connection)

            # Clear selection
            self.selected_node = None
            self.properties_widget.set_node(None)

            # Update tree view
            self.tree_widget.set_nodes(self.nodes)

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

        self.status_bar.showMessage("Created new dialogue")

    def open_dialogue(self):
        """Open dialogue from file"""
        # In a full implementation, this would show a file dialog
        # For now, we'll create a sample dialogue
        self.create_sample_dialogue()
        self.status_bar.showMessage("Loaded sample dialogue")

    def save_dialogue(self):
        """Save dialogue to file"""
        if not self.nodes:
            QMessageBox.warning(self, "Warning", "No dialogue to save")
            return

        # Convert to dictionary
        dialogue_data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "connections": [],
        }

        # Add connections
        for connection in self.graphics_view.connections:
            dialogue_data["connections"].append(
                {
                    "from": connection.start_node.node.id,
                    "to": connection.end_node.node.id,
                }
            )

        # In a full implementation, this would show a file dialog
        filename = "dialogue_export.json"

        try:
            with open(filename, "w") as f:
                json.dump(dialogue_data, f, indent=2)

            QMessageBox.information(self, "Success", f"Dialogue saved to {filename}")
            self.status_bar.showMessage(f"Saved dialogue to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save dialogue: {e}")

    def export_to_lua(self):
        """Export dialogue to Lua format"""
        if not self.nodes:
            QMessageBox.warning(self, "Warning", "No dialogue to export")
            return

        # Generate Lua code
        lua_code = self.generate_lua_dialogue()

        # In a full implementation, this would show a file dialog
        filename = "dialogue_export.lua"

        try:
            with open(filename, "w") as f:
                f.write(lua_code)

            QMessageBox.information(self, "Success", f"Dialogue exported to {filename}")
            self.status_bar.showMessage(f"Exported dialogue to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export dialogue: {e}")

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
                    lua_lines.append(
                        f'        {{text = "{choice["text"]}", next = "{choice["next_node"]}"}},'
                    )
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
            position=(100, 100),
        )

        npc_node = DialogueNode(
            id="npc_greeting",
            node_type=NodeType.NPC,
            speaker="Guard",
            text="Welcome to our town, traveler. How can I help you?",
            position=(350, 100),
        )

        choice_node = DialogueNode(
            id="player_choice",
            node_type=NodeType.CHOICE,
            speaker="Player",
            choices=[
                {"text": "I'm looking for work.", "next_node": "quest_node"},
                {"text": "Just passing through.", "next_node": "leave_node"},
                {"text": "Tell me about this town.", "next_node": "info_node"},
            ],
            position=(600, 100),
        )

        quest_node = DialogueNode(
            id="quest_node",
            node_type=NodeType.NPC,
            speaker="Guard",
            text="We have a goblin problem in the nearby caves. Could you help us?",
            position=(850, 50),
        )

        info_node = DialogueNode(
            id="info_node",
            node_type=NodeType.NPC,
            speaker="Guard",
            text="This is the town of Greenhaven. We're a peaceful community of traders and farmers.",
            position=(850, 150),
        )

        leave_node = DialogueNode(
            id="leave_node",
            node_type=NodeType.NPC,
            speaker="Guard",
            text="Safe travels, then!",
            position=(850, 250),
        )

        end_node = DialogueNode(
            id="end",
            node_type=NodeType.END,
            speaker="System",
            text="Dialogue ends",
            position=(1100, 150),
        )

        # Set up connections
        start_node.next_nodes = ["npc_greeting"]
        npc_node.next_nodes = ["player_choice"]
        quest_node.next_nodes = ["end"]
        info_node.next_nodes = ["end"]
        leave_node.next_nodes = ["end"]

        # Add nodes
        self.nodes.update(
            {
                "start": start_node,
                "npc_greeting": npc_node,
                "player_choice": choice_node,
                "quest_node": quest_node,
                "info_node": info_node,
                "leave_node": leave_node,
                "end": end_node,
            }
        )

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

        logger.info("Created sample dialogue with 7 nodes")


def main():
    """Main function to run the visual dialogue editor"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Visual Dialogue Editor")
    app.setOrganizationName("Quest Editor System")

    # Create and show main window
    editor = VisualDialogueEditor()
    editor.show()

    # Create sample dialogue for demonstration
    editor.create_sample_dialogue()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
