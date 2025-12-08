#!/usr/bin/env python3
"""
Visual Dialogue Canvas

Provides a visual, node-based interface for editing dialogue trees
with drag-and-drop, connection lines, and real-time collaboration.
"""

import math
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsItem, QGraphicsPathItem, QGraphicsRectItem, QGraphicsTextItem,
    QGraphicsEllipseItem, QGraphicsProxyWidget, QPushButton, QLabel,
    QComboBox, QCheckBox, QSlider, QGroupBox, QFrame, QScrollArea,
    QToolBar, QToolButton, QMenu, QSpinBox, QColorDialog, QFontDialog
)
from PySide6.QtCore import (
    Qt, QRectF, QPointF, QSizeF, Signal, QPropertyAnimation, QEasingCurve,
    QTimer, QEvent, QMimeData, QRect, QPoint
)
from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPalette, QMouseEvent,
    QKeyEvent, QWheelEvent, QDragEnterEvent, QDropEvent, QPainterPath,
    QLinearGradient, QRadialGradient, QPolygonF, QTransform, QIcon,
    QKeySequence, QCursor, QPixmap, QPainterPathStroker
)

try:
    from TirganachReloaded.cff_editor.models.enhanced_dialogue_models import (
        DialogueTree, DialogueNode, DialogueChoice, DialogueCondition, DialogueAction
    )
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class NodeZLevel:
    """Z-levels for layering nodes and connections"""
    BACKGROUND = 0
    GRID = 1
    CONNECTION = 2
    NODE_SHADOW = 3
    NODE_BODY = 4
    NODE_CONTENT = 5
    NODE_PORT = 6
    SELECTION = 7
    HUD = 8


class NodeType(Enum):
    """Node types with visual characteristics"""
    START = "start"
    NPC = "npc"
    PLAYER = "player"
    END = "end"
    CHOICE = "choice"
    CONDITION = "condition"
    ACTION = "action"
    COMMENT = "comment"


class ConnectionType(Enum):
    """Connection types with visual styles"""
    DIALOGUE = "dialogue"      # Normal dialogue flow
    CHOICE = "choice"          # Player choice
    CONDITION = "condition"    # Conditional connection
    DEFAULT = "default"        # Default/unconditional
    BACKREF = "backref"        # Back reference
    JUMP = "jump"             # Direct jump


class ConnectionStyle:
    """Visual styles for connections"""

    STYLES = {
        ConnectionType.DIALOGUE: {
            'color': QColor(100, 150, 200),
            'width': 2,
            'style': Qt.SolidLine,
            'arrow': True,
            'curve': True
        },
        ConnectionType.CHOICE: {
            'color': QColor(150, 200, 100),
            'width': 2,
            'style': Qt.SolidLine,
            'arrow': True,
            'curve': True
        },
        ConnectionType.CONDITION: {
            'color': QColor(200, 150, 100),
            'width': 2,
            'style': Qt.DashLine,
            'arrow': True,
            'curve': True
        },
        ConnectionType.DEFAULT: {
            'color': QColor(150, 150, 150),
            'width': 1,
            'style': Qt.DotLine,
            'arrow': False,
            'curve': False
        },
        ConnectionType.BACKREF: {
            'color': QColor(200, 100, 100),
            'width': 1,
            'style': Qt.DashLine,
            'arrow': True,
            'curve': True
        },
        ConnectionType.JUMP: {
            'color': QColor(200, 100, 200),
            'width': 2,
            'style': Qt.SolidLine,
            'arrow': True,
            'curve': False
        }
    }


@dataclass
class ConnectionPoint:
    """Represents a connection point on a node"""
    node_id: str
    point_type: str  # "input" or "output"
    index: int = 0
    position: QPointF = None
    label: str = ""


class ConnectionLine(QGraphicsPathItem):
    """Visual connection line between nodes"""

    def __init__(self, start_point: ConnectionPoint, end_point: ConnectionPoint,
                 connection_type: ConnectionType = ConnectionType.DIALOGUE):
        super().__init__()

        self.start_point = start_point
        self.end_point = end_point
        self.connection_type = connection_type
        self.style = ConnectionStyle.STYLES.get(connection_type, ConnectionStyle.STYLES[ConnectionType.DIALOGUE])

        self.setZValue(NodeZLevel.CONNECTION)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.PointingHandCursor)

        self.setup_appearance()
        self.update_path()

    def setup_appearance(self):
        """Setup visual appearance"""
        pen = QPen(self.style['color'])
        pen.setWidth(self.style['width'])
        pen.setStyle(self.style['style'])
        self.setPen(pen)

        # Set brush for arrow fill
        if self.style['arrow']:
            self.setBrush(QBrush(self.style['color']))

    def update_path(self):
        """Update the connection path"""
        if not self.start_point.position or not self.end_point.position:
            return

        start = self.start_point.position
        end = self.end_point.position

        path = QPainterPath()

        if self.style['curve']:
            # Curved connection with bezier curves
            dx = end.x() - start.x()
            dy = end.y() - start.y()

            # Control points for smooth curve
            ctrl1 = QPointF(start.x() + dx * 0.5, start.y())
            ctrl2 = QPointF(end.x() - dx * 0.5, end.y())

            path.moveTo(start)
            path.cubicTo(ctrl1, ctrl2, end)
        else:
            # Straight connection
            path.moveTo(start)
            path.lineTo(end)

        self.setPath(path)

        # Add arrow if needed
        if self.style['arrow']:
            self.add_arrow(path)

    def add_arrow(self, path: QPainterPath):
        """Add arrow to the end of the path"""
        if not self.end_point.position:
            return

        # Calculate arrow position and angle
        end_point = self.end_point.position
        angle = math.atan2(
            end_point.y() - (end_point.y() - 10),
            end_point.x() - (end_point.x() - 10)
        )

        # Create arrow polygon
        arrow_size = 8
        arrow = QPolygonF([
            QPointF(end_point.x(), end_point.y()),
            QPointF(
                end_point.x() - arrow_size * math.cos(angle - math.pi/6),
                end_point.y() - arrow_size * math.sin(angle - math.pi/6)
            ),
            QPointF(
                end_point.x() - arrow_size * math.cos(angle + math.pi/6),
                end_point.y() - arrow_size * math.sin(angle + math.pi/6)
            )
        ])

        # Store arrow for painting
        self.arrow_polygon = arrow

    def paint(self, painter: QPainter, option: QWidget, widget: QWidget):
        """Custom paint with arrow"""
        super().paint(painter, option, widget)

        if self.style['arrow'] and hasattr(self, 'arrow_polygon'):
            painter.setPen(QPen(self.style['color']))
            painter.setBrush(QBrush(self.style['color']))
            painter.drawPolygon(self.arrow_polygon)

    def hoverEnterEvent(self, event):
        """Handle hover enter"""
        # Highlight connection
        pen = self.pen()
        pen.setWidth(self.style['width'] + 1)
        self.setPen(pen)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Handle hover leave"""
        # Reset highlight
        self.setup_appearance()
        super().hoverLeaveEvent(event)


class DialogueNodeItem(QGraphicsRectItem):
    """Visual representation of a dialogue node"""

    # Signals
    node_selected = pyqtSignal(str)  # node_id
    node_moved = pyqtSignal(str, QPointF)  # node_id, position
    connection_requested = pyqtSignal(str, str)  # start_node, end_node
    node_double_clicked = pyqtSignal(str)  # node_id

    def __init__(self, node_id: str, node_data: dict, node_type: NodeType = NodeType.NPC):
        super().__init__()

        self.node_id = node_id
        self.node_data = node_data
        self.node_type = node_type
        self.input_ports = []
        self.output_ports = []

        # Visual properties
        self.width = 200
        self.height = 120
        self.corner_radius = 8
        self.selected = False

        # Setup appearance
        self.setup_appearance()
        self.create_content()
        self.create_ports()

        # Enable interactions
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setZValue(NodeZLevel.NODE_BODY)

        self.setCursor(Qt.OpenHandCursor)

    def setup_appearance(self):
        """Setup visual appearance based on node type"""
        # Colors for different node types
        colors = {
            NodeType.START: QColor(100, 200, 100),      # Green
            NodeType.NPC: QColor(100, 150, 200),        # Blue
            NodeType.PLAYER: QColor(200, 150, 100),     # Orange
            NodeType.END: QColor(200, 100, 100),        # Red
            NodeType.CHOICE: QColor(200, 100, 200),     # Purple
            NodeType.CONDITION: QColor(200, 200, 100),  # Yellow
            NodeType.ACTION: QColor(100, 200, 200),     # Cyan
            NodeType.COMMENT: QColor(150, 150, 150)     # Gray
        }

        # Create gradient fill
        base_color = colors.get(self.node_type, QColor(150, 150, 150))
        gradient = QLinearGradient(0, 0, 0, self.height)
        gradient.setColorAt(0, base_color.lighter(120))
        gradient.setColorAt(1, base_color.darker(110))

        self.setRect(QRectF(0, 0, self.width, self.height))
        self.setBrush(QBrush(gradient))

        # Border
        pen = QPen(base_color.darker(130))
        pen.setWidth(2)
        self.setPen(pen)

        # Shadow effect (simulated with offset rectangle)
        self.shadow_rect = QGraphicsRectItem(self.rect().translated(3, 3), self)
        self.shadow_rect.setBrush(QBrush(QColor(0, 0, 0, 50)))
        self.shadow_rect.setPen(Qt.NoPen)
        self.shadow_rect.setZValue(NodeZLevel.NODE_SHADOW)

    def create_content(self):
        """Create node content (text, icons, etc.)"""
        # Node title
        self.title_text = QGraphicsTextItem(self.get_node_title(), self)
        self.title_text.setPos(10, 5)

        # Setup font
        title_font = self.title_text.font()
        title_font.setBold(True)
        title_font.setPointSize(10)
        self.title_text.setFont(title_font)
        self.title_text.setDefaultTextColor(QColor(255, 255, 255))

        # Node content/dialogue text
        content_text = self.get_node_content()
        if content_text:
            self.content_text = QGraphicsTextItem(content_text, self)
            self.content_text.setPos(10, 25)

            # Setup content font
            content_font = self.content_text.font()
            content_font.setPointSize(9)
            self.content_text.setFont(content_font)
            self.content_text.setDefaultTextColor(QColor(240, 240, 240))

            # Limit text width
            self.content_text.setTextWidth(self.width - 20)

        # Node type indicator
        self.type_indicator = QGraphicsEllipseItem(self.width - 25, 5, 20, 20, self)
        self.type_indicator.setBrush(QBrush(QColor(255, 255, 255, 200)))
        self.type_indicator.setPen(Qt.NoPen)

        # Type icon/text
        self.type_text = QGraphicsTextItem(self.get_type_symbol(), self.type_indicator)
        type_font = self.type_text.font()
        type_font.setBold(True)
        type_font.setPointSize(8)
        self.type_text.setFont(type_font)
        self.type_text.setDefaultTextColor(QColor(50, 50, 50))
        self.type_text.setPos(2, 0)

    def create_ports(self):
        """Create connection ports"""
        # Input port (top)
        input_port = QGraphicsEllipseItem(-5, -5, 10, 10, self)
        input_port.setBrush(QBrush(QColor(255, 200, 100)))
        input_port.setPen(QPen(QColor(200, 150, 50), 2))
        input_port.setPos(self.width // 2, 0)
        input_port.setCursor(Qt.CrossCursor)
        input_port.setZValue(NodeZLevel.NODE_PORT)

        self.input_ports.append(input_port)

        # Output ports (bottom) - one for each choice
        choices = self.node_data.get('choices', [])
        port_count = max(1, len(choices))  # At least one output port

        port_spacing = min(self.width // (port_count + 1), 40)
        start_x = (self.width - (port_count - 1) * port_spacing) // 2

        for i in range(port_count):
            output_port = QGraphicsEllipseItem(-5, -5, 10, 10, self)
            output_port.setBrush(QBrush(QColor(100, 255, 100)))
            output_port.setPen(QPen(QColor(50, 200, 50), 2))
            output_port.setPos(start_x + i * port_spacing, self.height)
            output_port.setCursor(Qt.CrossCursor)
            output_port.setZValue(NodeZLevel.NODE_PORT)

            self.output_ports.append(output_port)

    def get_node_title(self) -> str:
        """Get display title for the node"""
        if self.node_type == NodeType.START:
            return "START"
        elif self.node_type == NodeType.END:
            return "END"
        else:
            # Use node ID or speaker name
            speaker = self.node_data.get('speaker', '')
            if speaker:
                return speaker.upper()
            return self.node_id.upper()

    def get_node_content(self) -> str:
        """Get display content for the node"""
        # Get dialogue text, limit length
        text = self.node_data.get('text', '')
        if len(text) > 60:
            text = text[:57] + "..."
        return text

    def get_type_symbol(self) -> str:
        """Get symbol for node type"""
        symbols = {
            NodeType.START: "▶",
            NodeType.END: "■",
            NodeType.NPC: "💬",
            NodeType.PLAYER: "👤",
            NodeType.CHOICE: "🔀",
            NodeType.CONDITION: "❓",
            NodeType.ACTION: "⚡",
            NodeType.COMMENT: "📝"
        }
        return symbols.get(self.node_type, "•")

    def get_port_position(self, port_type: str, index: int = 0) -> QPointF:
        """Get world position of a port"""
        if port_type == "input" and self.input_ports:
            port = self.input_ports[0]
        elif port_type == "output" and index < len(self.output_ports):
            port = self.output_ports[index]
        else:
            return QPointF()

        return self.mapToScene(port.pos())

    def update_position(self, pos: QPointF):
        """Update node position"""
        self.setPos(pos)

        # Update shadow position
        self.shadow_rect.setRect(self.rect().translated(3, 3))

        # Emit signal
        self.node_moved.emit(self.node_id, pos)

    def set_selected(self, selected: bool):
        """Set selection state"""
        self.selected = selected

        if selected:
            # Highlight selection
            pen = self.pen()
            pen.setColor(QColor(255, 200, 100))
            pen.setWidth(3)
            self.setPen(pen)

            self.setCursor(Qt.ClosedHandCursor)
        else:
            # Reset appearance
            self.setup_appearance()
            self.setCursor(Qt.OpenHandCursor)

    def itemChange(self, change, value):
        """Handle item changes"""
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.node_moved.emit(self.node_id, value)
        elif change == QGraphicsItem.ItemSelectedHasChanged:
            self.set_selected(value)

        return super().itemChange(change, value)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.node_selected.emit(self.node_id)

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle double click"""
        self.node_double_clicked.emit(self.node_id)
        super().mouseDoubleClickEvent(event)


class DialogueScene(QGraphicsScene):
    """Graphics scene for dialogue nodes"""

    # Signals
    node_selected = pyqtSignal(str)
    node_moved = pyqtSignal(str, QPointF)
    connection_requested = pyqtSignal(str, str)
    node_double_clicked = pyqtSignal(str)
    scene_changed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.nodes = {}
        self.connections = []
        self.grid_size = 20
        self.show_grid = True

        # Setup background
        self.setBackgroundBrush(QBrush(QColor(45, 45, 55)))

        # Create grid
        self.create_grid()

    def create_grid(self):
        """Create background grid"""
        self.grid_item = None
        self.update_grid()

    def update_grid(self):
        """Update grid visibility"""
        if self.grid_item:
            self.removeItem(self.grid_item)
            self.grid_item = None

        if self.show_grid:
            # Create grid pattern
            self.grid_item = self.create_grid_item()
            self.addItem(self.grid_item)

    def create_grid_item(self) -> QGraphicsItem:
        """Create grid background item"""
        width = 2000
        height = 2000

        grid_path = QPainterPath()

        # Vertical lines
        for x in range(0, width, self.grid_size):
            grid_path.moveTo(x, 0)
            grid_path.lineTo(x, height)

        # Horizontal lines
        for y in range(0, height, self.grid_size):
            grid_path.moveTo(0, y)
            grid_path.lineTo(width, y)

        grid_item = QGraphicsPathItem(grid_path)
        grid_item.setZValue(NodeZLevel.GRID)

        pen = QPen(QColor(60, 60, 70))
        pen.setWidth(1)
        grid_item.setPen(pen)

        return grid_item

    def add_node(self, node_id: str, node_data: dict, position: QPointF = None,
                 node_type: NodeType = NodeType.NPC) -> DialogueNodeItem:
        """Add a node to the scene"""
        if position is None:
            position = QPointF(100, 100)

        node = DialogueNodeItem(node_id, node_data, node_type)
        node.setPos(position)

        # Connect signals
        node.node_selected.connect(self.node_selected.emit)
        node.node_moved.connect(self.node_moved.emit)
        node.node_double_clicked.connect(self.node_double_clicked.emit)

        self.addItem(node)
        self.nodes[node_id] = node

        self.scene_changed.emit()
        return node

    def remove_node(self, node_id: str):
        """Remove a node from the scene"""
        if node_id in self.nodes:
            node = self.nodes[node_id]

            # Remove connections first
            self.remove_connections_for_node(node_id)

            self.removeItem(node)
            del self.nodes[node_id]

            self.scene_changed.emit()

    def add_connection(self, start_node: str, end_node: str,
                      start_port: int = 0, end_port: int = 0,
                      connection_type: ConnectionType = ConnectionType.DIALOGUE):
        """Add a connection between nodes"""
        if start_node not in self.nodes or end_node not in self.nodes:
            return

        start_pos = self.nodes[start_node].get_port_position("output", start_port)
        end_pos = self.nodes[end_node].get_port_position("input", end_port)

        start_point = ConnectionPoint(start_node, "output", start_port, start_pos)
        end_point = ConnectionPoint(end_node, "input", end_port, end_pos)

        connection = ConnectionLine(start_point, end_point, connection_type)
        self.addItem(connection)

        self.connections.append({
            'connection': connection,
            'start_node': start_node,
            'end_node': end_node,
            'start_port': start_port,
            'end_port': end_port
        })

        self.scene_changed.emit()

    def remove_connections_for_node(self, node_id: str):
        """Remove all connections for a node"""
        connections_to_remove = []

        for conn_data in self.connections:
            if conn_data['start_node'] == node_id or conn_data['end_node'] == node_id:
                connections_to_remove.append(conn_data)

        for conn_data in connections_to_remove:
            self.removeItem(conn_data['connection'])
            self.connections.remove(conn_data)

    def snap_to_grid(self, position: QPointF) -> QPointF:
        """Snap position to grid"""
        x = round(position.x() / self.grid_size) * self.grid_size
        y = round(position.y() / self.grid_size) * self.grid_size
        return QPointF(x, y)

    def set_grid_visible(self, visible: bool):
        """Set grid visibility"""
        self.show_grid = visible
        self.update_grid()

    def set_grid_size(self, size: int):
        """Set grid size"""
        self.grid_size = size
        if self.show_grid:
            self.update_grid()

    def auto_layout_nodes(self):
        """Automatically layout nodes in a tree structure"""
        if not self.nodes:
            return

        # Find start node
        start_node = None
        for node_id, node in self.nodes.items():
            if node.node_type == NodeType.START:
                start_node = node
                break

        if not start_node:
            # If no start node, use first node
            start_node = next(iter(self.nodes.values()))

        # Simple tree layout
        self._layout_node_tree(start_node, QPointF(400, 100), 0, set())

    def _layout_node_tree(self, node: DialogueNodeItem, position: QPointF,
                         level: int, visited: Set[str]):
        """Recursively layout nodes in a tree"""
        if node.node_id in visited:
            return

        visited.add(node.node_id)

        # Animate to position
        node.setPos(position)

        # Layout child nodes
        child_positions = self._get_child_positions(node, position, level)

        for i, child_pos in enumerate(child_positions):
            # This would need to be connected to actual dialogue tree structure
            pass

    def _get_child_positions(self, node: DialogueNodeItem, parent_pos: QPointF,
                           level: int) -> List[QPointF]:
        """Get positions for child nodes"""
        positions = []
        child_count = len(node.output_ports)

        if child_count == 0:
            return positions

        # Horizontal spread based on level
        spread = max(150, 300 - level * 50)
        vertical_spacing = 120

        start_x = parent_pos.x() - (child_count - 1) * spread / 2

        for i in range(child_count):
            x = start_x + i * spread
            y = parent_pos.y() + vertical_spacing
            positions.append(QPointF(x, y))

        return positions


class DialogueCanvasView(QGraphicsView):
    """View for the dialogue canvas with zoom and pan controls"""

    # Signals
    zoom_changed = pyqtSignal(float)
    view_updated = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)

        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)

        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0

        # Setup view
        self.setup_view()
        self.setup_shortcuts()

    def setup_view(self):
        """Setup view properties"""
        # Set scene
        self.setScene(QGraphicsScene())

        # Set background
        self.setBackgroundBrush(QBrush(QColor(35, 35, 45)))

        # Set initial size
        self.setRenderHint(QPainter.Antialiasing)

        # Enable mouse tracking
        self.setMouseTracking(True)

        # Enable drag and drop
        self.setAcceptDrops(True)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Zoom shortcuts
        self.zoom_in_action = self.create_shortcut("Ctrl+Plus", self.zoom_in)
        self.zoom_out_action = self.create_shortcut("Ctrl+Minus", self.zoom_out)
        self.reset_zoom_action = self.create_shortcut("Ctrl+0", self.reset_zoom)

        # View shortcuts
        self.fit_in_view_action = self.create_shortcut("Ctrl+F", self.fit_in_view)

    def create_shortcut(self, key_sequence: str, target_func):
        """Create keyboard shortcut"""
        from PySide6.QtWidgets import QShortcut
        from PySide6.QtGui import QKeySequence

        shortcut = QShortcut(QKeySequence(key_sequence), self)
        shortcut.activated.connect(target_func)
        return shortcut

    def set_dialogue_scene(self, scene: DialogueScene):
        """Set the dialogue scene"""
        self.setScene(scene)

        # Fit initial view
        self.fit_in_view()

    def zoom_in(self):
        """Zoom in"""
        self.set_zoom(self.zoom_factor * 1.2)

    def zoom_out(self):
        """Zoom out"""
        self.set_zoom(self.zoom_factor / 1.2)

    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.set_zoom(1.0)

    def set_zoom(self, factor: float):
        """Set zoom factor"""
        self.zoom_factor = max(self.min_zoom, min(self.max_zoom, factor))

        # Apply transformation
        self.resetTransform()
        self.scale(self.zoom_factor, self.zoom_factor)

        self.zoom_changed.emit(self.zoom_factor)

    def fit_in_view(self):
        """Fit all items in view"""
        if self.scene():
            self.scene().setSceneRect(self.scene().itemsBoundingRect())
            self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)

            # Update zoom factor
            transform = self.transform()
            self.zoom_factor = transform.m11()  # Get scale factor

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming"""
        if event.modifiers() & Qt.ControlModifier:
            # Zoom with Ctrl+Wheel
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Pan with wheel
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.MiddleButton:
            # Start panning
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            # Fake left button press for panning
            fake_event = QMouseEvent(
                event.type(),
                event.pos(),
                event.button(),
                Qt.LeftButton,
                event.modifiers()
            )
            super().mousePressEvent(fake_event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if event.button() == Qt.MiddleButton:
            # Stop panning
            self.setDragMode(QGraphicsView.RubberBandDrag)

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press"""
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            # Temporary pan mode with spacebar
            self.setDragMode(QGraphicsView.ScrollHandDrag)
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release"""
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            # Restore normal drag mode
            self.setDragMode(QGraphicsView.RubberBandDrag)
        else:
            super().keyReleaseEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        if event.mimeData().hasText():
            # Get drop position in scene coordinates
            scene_pos = self.mapToScene(event.pos())

            # Handle node creation from drag
            # This would be implemented based on the dragged content

            event.acceptProposedAction()
        super().dropEvent(event)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create view and scene
    view = DialogueCanvasView()
    scene = DialogueScene()
    view.set_dialogue_scene(scene)

    # Add some test nodes
    start_node = scene.add_node("start", {"text": "Welcome to the quest!"},
                               QPointF(100, 100), NodeType.START)

    npc_node = scene.add_node("guard", {
        "speaker": "Guard",
        "text": "Halt! Who goes there?",
        "choices": [
            {"text": "I'm a traveler", "answer_id": 1},
            {"text": "None of your business", "answer_id": 2}
        ]
    }, QPointF(300, 100), NodeType.NPC)

    player_node = scene.add_node("player_response", {
        "text": "What do you want to do?",
        "choices": [
            {"text": "Show papers", "answer_id": 3},
            {"text": "Try to intimidate", "answer_id": 4}
        ]
    }, QPointF(500, 100), NodeType.PLAYER)

    end_node = scene.add_node("end", {"text": "Quest complete"},
                              QPointF(700, 100), NodeType.END)

    # Add connections
    scene.add_connection("start", "guard", 0, 0, ConnectionType.DIALOGUE)
    scene.add_connection("guard", "player_response", 0, 0, ConnectionType.CHOICE)
    scene.add_connection("player_response", "end", 0, 0, ConnectionType.DIALOGUE)

    # Show view
    view.setWindowTitle("Visual Dialogue Canvas")
    view.resize(1000, 700)
    view.show()

    sys.exit(app.exec())