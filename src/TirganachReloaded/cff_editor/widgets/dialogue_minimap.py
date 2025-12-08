#!/usr/bin/env python3
"""
Dialogue Mini-Map Widget

Provides a bird's-eye view of the dialogue tree with navigation
and overview capabilities.
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QSlider, QFrame, QToolTip, QColorDialog
)
from PySide6.QtCore import (
    Qt, QRectF, QPointF, QSizeF, Signal, QTimer, QPropertyAnimation,
    QEasingCurve, pyqtSignal
)
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QMouseEvent, QWheelEvent,
    QLinearGradient, QRadialGradient, QPainterPath, QCursor
)

try:
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class MinimapViewport(QFrame):
    """Viewport indicator showing current view area"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #ff9800;
                background-color: rgba(255, 152, 0, 30);
                border-radius: 2px;
            }
        """)

        self.dragging = False
        self.drag_start = None

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move"""
        if self.dragging and self.drag_start:
            # Emit position change signal
            delta = event.pos() - self.drag_start
            self.parent().viewport_dragged(delta)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.drag_start = None
            self.setCursor(Qt.ArrowCursor)


class DialogueMinimap(QWidget):
    """Mini-map widget for dialogue tree overview"""

    # Signals
    viewport_changed = pyqtSignal(QRectF)  # New viewport rectangle
    node_clicked = pyqtSignal(str)  # Node ID
    zoom_requested = pyqtSignal(float)  # Zoom level

    def __init__(self, parent=None):
        super().__init__(parent)

        # Scene and view data
        self.scene_rect = QRectF(0, 0, 1000, 1000)
        self.viewport_rect = QRectF(0, 0, 200, 150)
        self.nodes = {}  # node_id -> node_data
        self.connections = []  # List of connection data

        # Display options
        self.show_connections = True
        self.show_node_labels = False
        self.show_grid = True
        self.auto_fit = True

        # Visual settings
        self.bg_color = QColor(45, 45, 55)
        self.grid_color = QColor(60, 60, 70)
        self.viewport_color = QColor(255, 152, 0)
        self.node_colors = {
            'start': QColor(100, 200, 100),
            'npc': QColor(100, 150, 200),
            'player': QColor(200, 150, 100),
            'end': QColor(200, 100, 100),
            'choice': QColor(200, 100, 200),
            'condition': QColor(200, 200, 100),
            'action': QColor(100, 200, 200),
            'comment': QColor(150, 150, 150)
        }

        # Interaction
        self.viewport_indicator = None
        self.hovered_node = None
        self.selected_node = None

        # Performance
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update)
        self.pending_update = False

        self.setup_ui()
        self.setMinimumSize(200, 150)

    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        # Title bar
        title_layout = QHBoxLayout()

        title_label = QLabel("Mini-Map")
        title_label.setStyleSheet("font-weight: bold; color: #ddd;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Settings button
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(20, 20)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #666;
                border-radius: 3px;
                background-color: #444;
                color: #ddd;
                font-size: 10px;
                padding: 1px;
            }
            QPushButton:hover {
                background-color: #555;
                border-color: #888;
            }
        """)
        self.settings_btn.setContextMenuPolicy(Qt.CustomContextMenu)
        self.settings_btn.customContextMenuRequested.connect(self.show_settings_menu)

        title_layout.addWidget(self.settings_btn)
        layout.addLayout(title_layout)

        # Mini-map area will be drawn directly on this widget
        self.setMouseTracking(True)

    def update_scene_data(self, scene_rect: QRectF, nodes: Dict, connections: List):
        """Update scene data"""
        self.scene_rect = scene_rect
        self.nodes = nodes
        self.connections = connections

        self.schedule_update()

    def update_viewport(self, viewport_rect: QRectF):
        """Update viewport rectangle"""
        self.viewport_rect = viewport_rect
        self.schedule_update()

    def schedule_update(self):
        """Schedule an update (with throttling)"""
        if not self.pending_update:
            self.pending_update = True
            self.update_timer.start(50)  # 50ms throttle

    def paintEvent(self, event):
        """Paint the mini-map"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate scale
        widget_rect = self.rect()
        if widget_rect.isEmpty() or self.scene_rect.isEmpty():
            return

        scale_x = (widget_rect.width() - 4) / self.scene_rect.width()
        scale_y = (widget_rect.height() - 20) / self.scene_rect.height()  # Account for title
        scale = min(scale_x, scale_y)

        # Center the scene in the widget
        offset_x = (widget_rect.width() - self.scene_rect.width() * scale) / 2
        offset_y = (widget_rect.height() - 20 - self.scene_rect.height() * scale) / 2 + 15  # Account for title

        # Save painter state
        painter.save()

        # Translate and scale
        painter.translate(offset_x, offset_y)
        painter.scale(scale, scale)

        # Draw background
        self.draw_background(painter)

        # Draw grid
        if self.show_grid:
            self.draw_grid(painter)

        # Draw connections
        if self.show_connections:
            self.draw_connections(painter)

        # Draw nodes
        self.draw_nodes(painter)

        # Restore painter state for viewport
        painter.restore()

        # Draw viewport indicator
        self.draw_viewport(painter, scale, offset_x, offset_y)

    def draw_background(self, painter: QPainter):
        """Draw background"""
        painter.fillRect(self.scene_rect, self.bg_color)

        # Add subtle gradient
        gradient = QLinearGradient(0, 0, 0, self.scene_rect.height())
        gradient.setColorAt(0, QColor(45, 45, 55))
        gradient.setColorAt(1, QColor(35, 35, 45))
        painter.fillRect(self.scene_rect, gradient)

    def draw_grid(self, painter: QPainter):
        """Draw grid"""
        grid_size = 50

        pen = QPen(self.grid_color)
        pen.setWidthF(0.5)  # Very thin lines
        painter.setPen(pen)

        # Vertical lines
        for x in range(int(self.scene_rect.left()), int(self.scene_rect.right()), grid_size):
            painter.drawLine(QPointF(x, self.scene_rect.top()), QPointF(x, self.scene_rect.bottom()))

        # Horizontal lines
        for y in range(int(self.scene_rect.top()), int(self.scene_rect.bottom()), grid_size):
            painter.drawLine(QPointF(self.scene_rect.left(), y), QPointF(self.scene_rect.right(), y))

    def draw_connections(self, painter: QPainter):
        """Draw connections between nodes"""
        pen = QPen(QColor(100, 100, 150, 100))
        pen.setWidthF(1.0)
        painter.setPen(pen)

        for conn in self.connections:
            start_pos = conn.get('start_pos', QPointF())
            end_pos = conn.get('end_pos', QPointF())

            if start_pos and end_pos:
                # Draw connection line
                painter.drawLine(start_pos, end_pos)

                # Draw small arrow
                self.draw_connection_arrow(painter, start_pos, end_pos)

    def draw_connection_arrow(self, painter: QPainter, start: QPointF, end: QPointF):
        """Draw small arrow for connection"""
        # Calculate arrow position
        if start == end:
            return

        # Calculate direction
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = math.sqrt(dx*dx + dy*dy)

        if length < 1:
            return

        # Normalize direction
        dx /= length
        dy /= length

        # Arrow position (near end)
        arrow_pos = QPointF(
            end.x() - dx * 10,
            end.y() - dy * 10
        )

        # Arrow size
        arrow_size = 4

        # Calculate arrow points
        perp_x = -dy * arrow_size
        perp_y = dx * arrow_size

        arrow_points = [
            end,
            QPointF(arrow_pos.x() + perp_x, arrow_pos.y() + perp_y),
            QPointF(arrow_pos.x() - perp_x, arrow_pos.y() - perp_y)
        ]

        # Draw arrow
        painter.setBrush(QBrush(QColor(100, 100, 150, 150)))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(*arrow_points)

    def draw_nodes(self, painter: QPainter):
        """Draw nodes"""
        node_size = 6  # Size of nodes in minimap

        for node_id, node_data in self.nodes.items():
            pos = node_data.get('position', QPointF())
            node_type = node_data.get('type', 'npc')
            is_selected = node_id == self.selected_node
            is_hovered = node_id == self.hovered_node

            # Get node color
            base_color = self.node_colors.get(node_type, QColor(150, 150, 150))

            # Draw node
            if is_selected:
                # Selected node - larger and brighter
                painter.setBrush(QBrush(base_color.lighter(150)))
                painter.setPen(QPen(base_color.lighter(200), 1))
                painter.drawEllipse(pos, node_size + 2, node_size + 2)
            elif is_hovered:
                # Hovered node
                painter.setBrush(QBrush(base_color.lighter(120)))
                painter.setPen(QPen(base_color.lighter(160), 1))
                painter.drawEllipse(pos, node_size + 1, node_size + 1)
            else:
                # Normal node
                painter.setBrush(QBrush(base_color))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(pos, node_size, node_size)

            # Draw node labels if enabled
            if self.show_node_labels:
                self.draw_node_label(painter, node_id, node_data, pos)

    def draw_node_label(self, painter: QPainter, node_id: str, node_data: dict, pos: QPointF):
        """Draw node label"""
        label = node_data.get('label', node_id)

        # Setup font
        font = QFont()
        font.setPointSize(6)
        painter.setFont(font)

        # Calculate text position
        text_rect = painter.boundingRect(QRectF(), Qt.AlignLeft, label)
        text_pos = QPointF(
            pos.x() + 10,
            pos.y() - text_rect.height() / 2
        )

        # Draw text background
        painter.fillRect(text_rect.adjusted(-2, -1, 2, 1), QColor(0, 0, 0, 150))

        # Draw text
        painter.setPen(QPen(QColor(255, 255, 255, 200)))
        painter.drawText(text_pos, label)

    def draw_viewport(self, painter: QPainter, scale: float, offset_x: float, offset_y: float):
        """Draw viewport indicator"""
        # Map viewport to minimap coordinates
        minimap_viewport = QRectF(
            (self.viewport_rect.x() - self.scene_rect.x()) * scale + offset_x,
            (self.viewport_rect.y() - self.scene_rect.y()) * scale + offset_y,
            self.viewport_rect.width() * scale,
            self.viewport_rect.height() * scale
        )

        # Draw viewport rectangle
        painter.setPen(QPen(self.viewport_color, 2))
        painter.setBrush(QBrush(QColor(self.viewport_color.red(), self.viewport_color.green(),
                                      self.viewport_color.blue(), 30)))
        painter.drawRect(minimap_viewport)

        # Draw viewport handles (corners)
        handle_size = 4
        painter.setBrush(QBrush(self.viewport_color))
        painter.setPen(Qt.NoPen)

        # Corner handles
        corners = [
            minimap_viewport.topLeft(),
            minimap_viewport.topRight(),
            minimap_viewport.bottomLeft(),
            minimap_viewport.bottomRight()
        ]

        for corner in corners:
            handle_rect = QRectF(
                corner.x() - handle_size/2,
                corner.y() - handle_size/2,
                handle_size,
                handle_size
            )
            painter.drawEllipse(handle_rect)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            # Check if clicking on a node
            node_id = self.get_node_at_position(event.pos())
            if node_id:
                self.node_clicked.emit(node_id)
                self.selected_node = node_id
                self.update()
                return

            # Check if clicking on viewport - start dragging
            if self.is_in_viewport(event.pos()):
                self.viewport_drag_start = event.pos()
                self.dragging_viewport = True
                self.setCursor(Qt.ClosedHandCursor)
            else:
                # Click on minimap - move viewport
                self.move_viewport_to_position(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move"""
        # Check for node hover
        node_id = self.get_node_at_position(event.pos())
        if node_id != self.hovered_node:
            self.hovered_node = node_id
            self.update()

            # Show tooltip for hovered node
            if node_id and node_id in self.nodes:
                node_data = self.nodes[node_id]
                tooltip_text = f"{node_id}"
                if 'label' in node_data:
                    tooltip_text += f": {node_data['label']}"
                if 'type' in node_data:
                    tooltip_text += f" ({node_data['type']})"
                QToolTip.showText(event.globalPos(), tooltip_text, self)
            else:
                QToolTip.hideText()

        # Handle viewport dragging
        if hasattr(self, 'dragging_viewport') and self.dragging_viewport:
            if hasattr(self, 'viewport_drag_start'):
                delta = event.pos() - self.viewport_drag_start
                self.drag_viewport(delta)
                self.viewport_drag_start = event.pos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            if hasattr(self, 'dragging_viewport'):
                self.dragging_viewport = False
                self.setCursor(Qt.ArrowCursor)

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming"""
        if event.modifiers() & Qt.ControlModifier:
            # Zoom in/out with Ctrl+Wheel
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_requested.emit(1.2)
            else:
                self.zoom_requested.emit(0.8)
            event.accept()

    def get_node_at_position(self, pos: QPointF) -> Optional[str]:
        """Get node ID at given position"""
        # Convert position to scene coordinates
        widget_rect = self.rect()
        if widget_rect.isEmpty() or self.scene_rect.isEmpty():
            return None

        scale_x = (widget_rect.width() - 4) / self.scene_rect.width()
        scale_y = (widget_rect.height() - 20) / self.scene_rect.height()
        scale = min(scale_x, scale_y)

        offset_x = (widget_rect.width() - self.scene_rect.width() * scale) / 2
        offset_y = (widget_rect.height() - 20 - self.scene_rect.height() * scale) / 2 + 15

        scene_pos = QPointF(
            (pos.x() - offset_x) / scale,
            (pos.y() - offset_y) / scale
        )

        # Check nodes (with some tolerance for clicking)
        tolerance = 10 / scale

        for node_id, node_data in self.nodes.items():
            node_pos = node_data.get('position', QPointF())
            dist = (node_pos - scene_pos).manhattanLength()

            if dist <= tolerance:
                return node_id

        return None

    def is_in_viewport(self, pos: QPointF) -> bool:
        """Check if position is within viewport indicator"""
        # Similar transformation to get viewport rectangle
        widget_rect = self.rect()
        scale_x = (widget_rect.width() - 4) / self.scene_rect.width()
        scale_y = (widget_rect.height() - 20) / self.scene_rect.height()
        scale = min(scale_x, scale_y)

        offset_x = (widget_rect.width() - self.scene_rect.width() * scale) / 2
        offset_y = (widget_rect.height() - 20 - self.scene_rect.height() * scale) / 2 + 15

        minimap_viewport = QRectF(
            (self.viewport_rect.x() - self.scene_rect.x()) * scale + offset_x,
            (self.viewport_rect.y() - self.scene_rect.y()) * scale + offset_y,
            self.viewport_rect.width() * scale,
            self.viewport_rect.height() * scale
        )

        return minimap_viewport.contains(pos)

    def move_viewport_to_position(self, pos: QPointF):
        """Move viewport center to given position"""
        # Convert position to scene coordinates
        widget_rect = self.rect()
        scale_x = (widget_rect.width() - 4) / self.scene_rect.width()
        scale_y = (widget_rect.height() - 20) / self.scene_rect.height()
        scale = min(scale_x, scale_y)

        offset_x = (widget_rect.width() - self.scene_rect.width() * scale) / 2
        offset_y = (widget_rect.height() - 20 - self.scene_rect.height() * scale) / 2 + 15

        scene_pos = QPointF(
            (pos.x() - offset_x) / scale,
            (pos.y() - offset_y) / scale
        )

        # Center viewport on scene position
        new_viewport = QRectF(
            scene_pos.x() - self.viewport_rect.width() / 2,
            scene_pos.y() - self.viewport_rect.height() / 2,
            self.viewport_rect.width(),
            self.viewport_rect.height()
        )

        self.viewport_changed.emit(new_viewport)

    def drag_viewport(self, delta: QPointF):
        """Drag viewport by given delta"""
        # Convert delta to scene coordinates
        widget_rect = self.rect()
        scale_x = (widget_rect.width() - 4) / self.scene_rect.width()
        scale_y = (widget_rect.height() - 20) / self.scene_rect.height()
        scale = min(scale_x, scale_y)

        scene_delta = QPointF(delta.x() / scale, delta.y() / scale)

        new_viewport = self.viewport_rect.translated(scene_delta)
        self.viewport_changed.emit(new_viewport)

    def show_settings_menu(self, pos):
        """Show settings context menu"""
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)

        # Show connections
        connections_action = menu.addAction("Show Connections")
        connections_action.setCheckable(True)
        connections_action.setChecked(self.show_connections)
        connections_action.triggered.connect(lambda checked: self.toggle_connections(checked))

        # Show node labels
        labels_action = menu.addAction("Show Node Labels")
        labels_action.setCheckable(True)
        labels_action.setChecked(self.show_node_labels)
        labels_action.triggered.connect(lambda checked: self.toggle_labels(checked))

        # Show grid
        grid_action = menu.addAction("Show Grid")
        grid_action.setCheckable(True)
        grid_action.setChecked(self.show_grid)
        grid_action.triggered.connect(lambda checked: self.toggle_grid(checked))

        # Auto-fit
        auto_fit_action = menu.addAction("Auto-fit")
        auto_fit_action.setCheckable(True)
        auto_fit_action.setChecked(self.auto_fit)
        auto_fit_action.triggered.connect(lambda checked: self.toggle_auto_fit(checked))

        menu.addSeparator()

        # Reset view
        reset_action = menu.addAction("Reset View")
        reset_action.triggered.connect(self.reset_view)

        menu.exec(self.settings_btn.mapToGlobal(pos))

    def toggle_connections(self, checked: bool):
        """Toggle connection visibility"""
        self.show_connections = checked
        self.update()

    def toggle_labels(self, checked: bool):
        """Toggle node label visibility"""
        self.show_node_labels = checked
        self.update()

    def toggle_grid(self, checked: bool):
        """Toggle grid visibility"""
        self.show_grid = checked
        self.update()

    def toggle_auto_fit(self, checked: bool):
        """Toggle auto-fit mode"""
        self.auto_fit = checked
        self.update()

    def reset_view(self):
        """Reset to default view"""
        self.viewport_rect = QRectF(0, 0, 200, 150)
        self.selected_node = None
        self.hovered_node = None
        self.update()

    def viewport_dragged(self, delta: QPointF):
        """Handle viewport drag from indicator"""
        self.drag_viewport(delta)


# Add math import for calculations
import math