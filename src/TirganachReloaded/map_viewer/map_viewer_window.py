"""
SpellForce Map Viewer Window
Main window with OpenGL rendering for viewing SpellForce maps

Uses PySide6's QOpenGLWidget for 3D rendering with modern OpenGL
"""

import sys
import time
from pathlib import Path
from typing import Optional

from loguru import logger
from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import QKeyEvent, QMouseEvent, QSurfaceFormat, QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError:
    logger.error("PyOpenGL not installed. Install with: pip install PyOpenGL")
    raise

from .camera import Camera
from .map_loader import MapLoader


class MapViewerWidget(QOpenGLWidget):
    """
    OpenGL widget for rendering the map
    Handles all 3D rendering and user input
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set OpenGL format
        fmt = QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        fmt.setDepthBufferSize(24)
        fmt.setStencilBufferSize(8)
        fmt.setSamples(4)  # Anti-aliasing
        self.setFormat(fmt)

        # Map data
        self.map_loader: Optional[MapLoader] = None
        self.camera = Camera()

        # Input state
        self.last_mouse_pos = QPointF(0, 0)
        self.mouse_dragging = False
        self.keys_pressed = set()

        # Rendering state
        self.gl_initialized = False
        self.frame_count = 0
        self.last_time = time.time()
        self.fps = 0.0

        # Timer for continuous updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_frame)
        self.update_timer.start(16)  # ~60 FPS

        # Enable mouse tracking
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def load_map(self, filepath: Path) -> bool:
        """Load a map file"""
        try:
            self.map_loader = MapLoader()
            if self.map_loader.load(filepath):
                # Reset camera to center of map
                if self.map_loader.header:
                    self.camera.reset(
                        self.map_loader.header.width, self.map_loader.header.height
                    )
                    # Adjust camera elevation
                    center_x = self.map_loader.header.width / 2
                    center_y = self.map_loader.header.height / 2
                    terrain_height = self.map_loader.get_height_at(center_x, center_y)
                    self.camera.set_elevation(
                        self.camera.base_elevation * self.camera.zoom_level,
                        terrain_height,
                    )
                self.update()
                return True
            return False
        except Exception as e:
            logger.exception(f"Failed to load map: {e}")
            return False

    def initializeGL(self):
        """Initialize OpenGL context"""
        try:
            logger.info("Initializing OpenGL...")

            # Set background color (sky blue)
            glClearColor(0.53, 0.81, 0.92, 1.0)

            # Enable depth testing
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LEQUAL)

            # Enable backface culling
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)

            # Enable blending for transparency
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            # Smooth shading
            glShadeModel(GL_SMOOTH)

            # Nice perspective calculations
            glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

            # Anti-aliasing hints
            glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
            glEnable(GL_LINE_SMOOTH)

            self.gl_initialized = True
            logger.info("OpenGL initialized successfully")

        except Exception as e:
            logger.exception(f"OpenGL initialization failed: {e}")
            self.gl_initialized = False

    def resizeGL(self, w: int, h: int):
        """Handle window resize"""
        if h == 0:
            h = 1

        glViewport(0, 0, w, h)

        # Update projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect = w / h
        gluPerspective(60.0, aspect, 0.1, 1000.0)

        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Render the scene"""
        if not self.gl_initialized:
            return

        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set up view matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Apply camera transformation
        eye = self.camera.position
        lookat = self.camera.lookat
        up = self.camera.up

        gluLookAt(
            eye[0], eye[1], eye[2], lookat[0], lookat[1], lookat[2], up[0], up[1], up[2]
        )

        # Draw the scene
        if self.map_loader and self.map_loader.heightmap:
            self._draw_heightmap()
            self._draw_grid()
            self._draw_units()
            self._draw_buildings()

        # Draw coordinate axes (debug)
        self._draw_axes()

        # Update FPS counter
        self._update_fps()

    def _draw_heightmap(self):
        """Draw the terrain heightmap"""
        heightmap = self.map_loader.heightmap
        if not heightmap:
            return

        width = heightmap.width
        height = heightmap.height

        # Draw terrain as triangle strips
        glColor3f(0.4, 0.6, 0.3)  # Green terrain

        for y in range(height - 1):
            glBegin(GL_TRIANGLE_STRIP)
            for x in range(width):
                # Current row
                h1 = heightmap.get_height(x, y)
                glVertex3f(x, h1, y)

                # Next row
                h2 = heightmap.get_height(x, y + 1)
                glVertex3f(x, h2, y + 1)

            glEnd()

    def _draw_grid(self):
        """Draw a grid overlay on the terrain"""
        if not self.map_loader or not self.map_loader.heightmap:
            return

        heightmap = self.map_loader.heightmap
        width = heightmap.width
        height = heightmap.height

        glColor3f(0.3, 0.3, 0.3)  # Gray grid lines
        glLineWidth(1.0)

        # Grid spacing (draw every 10 units)
        spacing = 10

        # Draw vertical lines
        for x in range(0, width, spacing):
            glBegin(GL_LINE_STRIP)
            for y in range(height):
                h = heightmap.get_height(x, y) + 0.1  # Slightly above terrain
                glVertex3f(x, h, y)
            glEnd()

        # Draw horizontal lines
        for y in range(0, height, spacing):
            glBegin(GL_LINE_STRIP)
            for x in range(width):
                h = heightmap.get_height(x, y) + 0.1
                glVertex3f(x, h, y)
            glEnd()

    def _draw_units(self):
        """Draw unit markers"""
        if not self.map_loader:
            return

        glColor3f(0.0, 0.5, 1.0)  # Blue for units

        for unit in self.map_loader.units:
            # Get terrain height at unit position
            terrain_h = self.map_loader.get_height_at(unit.x, unit.y)

            # Draw a simple cube marker
            glPushMatrix()
            glTranslatef(unit.x, terrain_h + 1.0, unit.y)
            self._draw_cube(0.5)
            glPopMatrix()

    def _draw_buildings(self):
        """Draw building markers"""
        if not self.map_loader:
            return

        glColor3f(0.7, 0.3, 0.1)  # Brown for buildings

        for building in self.map_loader.buildings:
            terrain_h = self.map_loader.get_height_at(building.x, building.y)

            # Draw a larger cube for buildings
            glPushMatrix()
            glTranslatef(building.x, terrain_h + 2.0, building.y)
            self._draw_cube(1.5)
            glPopMatrix()

    def _draw_cube(self, size: float):
        """Draw a simple cube"""
        s = size / 2

        glBegin(GL_QUADS)

        # Front
        glVertex3f(-s, -s, s)
        glVertex3f(s, -s, s)
        glVertex3f(s, s, s)
        glVertex3f(-s, s, s)

        # Back
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(s, -s, -s)

        # Top
        glVertex3f(-s, s, -s)
        glVertex3f(-s, s, s)
        glVertex3f(s, s, s)
        glVertex3f(s, s, -s)

        # Bottom
        glVertex3f(-s, -s, -s)
        glVertex3f(s, -s, -s)
        glVertex3f(s, -s, s)
        glVertex3f(-s, -s, s)

        # Right
        glVertex3f(s, -s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(s, s, s)
        glVertex3f(s, -s, s)

        # Left
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, -s, s)
        glVertex3f(-s, s, s)
        glVertex3f(-s, s, -s)

        glEnd()

    def _draw_axes(self):
        """Draw coordinate axes for debugging"""
        glLineWidth(2.0)

        glBegin(GL_LINES)

        # X axis (red)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(10, 0, 0)

        # Y axis (green)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 10, 0)

        # Z axis (blue)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 10)

        glEnd()

    def _update_fps(self):
        """Update FPS counter"""
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.last_time

        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_time = current_time

    def update_frame(self):
        """Called by timer to update the scene"""
        # Handle continuous key presses
        delta_time = 0.016  # ~60 FPS

        forward = 0.0
        right = 0.0

        # Arrow keys for movement
        if Qt.Key.Key_Up in self.keys_pressed or Qt.Key.Key_W in self.keys_pressed:
            forward += 1.0
        if Qt.Key.Key_Down in self.keys_pressed or Qt.Key.Key_S in self.keys_pressed:
            forward -= 1.0
        if Qt.Key.Key_Left in self.keys_pressed or Qt.Key.Key_A in self.keys_pressed:
            right -= 1.0
        if Qt.Key.Key_Right in self.keys_pressed or Qt.Key.Key_D in self.keys_pressed:
            right += 1.0

        if forward != 0.0 or right != 0.0:
            self.camera.move(forward, right, delta_time)

            # Adjust camera elevation based on terrain
            if self.map_loader and self.map_loader.heightmap:
                pos = self.camera.position
                terrain_h = self.map_loader.get_height_at(pos[0], pos[2])
                self.camera.set_elevation(
                    self.camera.base_elevation * self.camera.zoom_level, terrain_h
                )

            self.update()

        # Rotation with Home/End/PageUp/PageDown
        rotation_delta = 0.0
        altitude_delta = 0.0

        if Qt.Key.Key_Home in self.keys_pressed:
            rotation_delta -= self.camera.rotation_speed * delta_time
        if Qt.Key.Key_End in self.keys_pressed:
            rotation_delta += self.camera.rotation_speed * delta_time
        if Qt.Key.Key_PageUp in self.keys_pressed:
            altitude_delta += self.camera.rotation_speed * delta_time
        if Qt.Key.Key_PageDown in self.keys_pressed:
            altitude_delta -= self.camera.rotation_speed * delta_time

        if rotation_delta != 0.0 or altitude_delta != 0.0:
            self.camera.rotate(rotation_delta, altitude_delta)
            self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouse_dragging = True
            self.last_mouse_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouse_dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse movement"""
        if self.mouse_dragging:
            current_pos = event.position()
            delta = current_pos - self.last_mouse_pos

            # Rotate camera based on mouse movement
            rotation_speed = 0.005  # Sensitivity
            self.camera.rotate(-delta.x() * rotation_speed, delta.y() * rotation_speed)

            self.last_mouse_pos = current_pos
            self.update()

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel (zoom)"""
        delta = event.angleDelta().y()
        self.camera.add_zoom(-1 if delta > 0 else 1)

        # Adjust camera elevation
        if self.map_loader and self.map_loader.heightmap:
            pos = self.camera.position
            terrain_h = self.map_loader.get_height_at(pos[0], pos[2])
            self.camera.set_elevation(
                self.camera.base_elevation * self.camera.zoom_level, terrain_h
            )

        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press"""
        self.keys_pressed.add(event.key())

        # Zoom with Insert/Delete
        if event.key() == Qt.Key.Key_Insert:
            self.camera.add_zoom(-1)
            self.update()
        elif event.key() == Qt.Key.Key_Delete:
            self.camera.add_zoom(1)
            self.update()

    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release"""
        self.keys_pressed.discard(event.key())


class MapViewerWindow(QMainWindow):
    """Main window for the map viewer application"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SpellForce Map Viewer")
        self.setMinimumSize(1024, 768)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create toolbar
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)

        self.open_button = QPushButton("Open Map")
        self.open_button.clicked.connect(self.open_map)
        toolbar_layout.addWidget(self.open_button)

        self.reset_button = QPushButton("Reset Camera")
        self.reset_button.clicked.connect(self.reset_camera)
        toolbar_layout.addWidget(self.reset_button)

        toolbar_layout.addStretch()

        self.info_label = QLabel("No map loaded")
        toolbar_layout.addWidget(self.info_label)

        self.fps_label = QLabel("FPS: 0")
        toolbar_layout.addWidget(self.fps_label)

        layout.addWidget(toolbar_widget)

        # Create OpenGL viewer widget
        self.viewer = MapViewerWidget()
        layout.addWidget(self.viewer)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # FPS update timer
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self.update_info)
        self.fps_timer.start(500)  # Update twice per second

        # Apply styling
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3c3f41;
                border: 1px solid #555555;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4c4f51;
            }
            QPushButton:pressed {
                background-color: #2c2f31;
            }
            QLabel {
                padding: 5px;
            }
        """
        )

    def open_map(self):
        """Open a map file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open SpellForce Map",
            "",
            "Map Files (*.map);;All Files (*)",
        )

        if filepath:
            self.status_bar.showMessage(f"Loading {filepath}...")
            if self.viewer.load_map(Path(filepath)):
                map_loader = self.viewer.map_loader
                info = f"Map: {map_loader.header.width}x{map_loader.header.height}"
                if map_loader.metadata.map_name:
                    info += f" - {map_loader.metadata.map_name}"
                self.info_label.setText(info)
                self.status_bar.showMessage(f"Loaded: {Path(filepath).name}")
            else:
                QMessageBox.warning(self, "Error", "Failed to load map file")
                self.status_bar.showMessage("Failed to load map")

    def reset_camera(self):
        """Reset camera to default position"""
        if self.viewer.map_loader and self.viewer.map_loader.header:
            self.viewer.camera.reset(
                self.viewer.map_loader.header.width,
                self.viewer.map_loader.header.height,
            )
            self.viewer.update()
            self.status_bar.showMessage("Camera reset")

    def update_info(self):
        """Update FPS and other info"""
        self.fps_label.setText(f"FPS: {self.viewer.fps:.1f}")


def main():
    """Run the map viewer application"""
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("SpellForce Map Viewer")

    window = MapViewerWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
