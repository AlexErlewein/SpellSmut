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
from .simple_map_loader import SimpleMapLoader
from .simple_texture_manager import SimpleTextureManager


class MapViewerWidget(QOpenGLWidget):
    """
    OpenGL widget for rendering the map
    Handles all 3D rendering and user input
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set OpenGL format - use Compatibility Profile for macOS
        fmt = QSurfaceFormat()
        fmt.setVersion(2, 1)  # OpenGL 2.1 for better compatibility
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CompatibilityProfile)
        fmt.setDepthBufferSize(24)
        fmt.setStencilBufferSize(8)
        fmt.setSamples(4)  # Anti-aliasing
        fmt.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
        self.setFormat(fmt)

        # Ensure Qt doesn't interfere with OpenGL rendering
        self.setAutoFillBackground(False)

        # Force full updates
        self.setUpdateBehavior(QOpenGLWidget.UpdateBehavior.NoPartialUpdate)

        # Map data
        self.map_loader: Optional[SimpleMapLoader] = None
        self.camera = Camera()

        # Texture system
        self.texture_manager: Optional[SimpleTextureManager] = None
        self.textures_loaded = False
        self.texture_ids = []  # OpenGL texture IDs
        self.base_textures = {}  # Index -> texture data
        self.use_textures = True  # Enable/disable texture rendering

        # Terrain texture mapping system
        self.terrain_texture_mapper: Optional[TerrainTextureMapper] = None
        self.texture_map = {}  # Maps tile coordinates to texture assignments

        # Input state
        self.last_mouse_pos = QPointF(0, 0)
        self.mouse_dragging = False
        self.keys_pressed = set()

        # Lighting state
        self.lighting_enabled = True
        self.sun_azimuth = 45.0  # Degrees
        self.sun_altitude = 45.0  # Degrees

        # Display state
        self.grid_enabled = True

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
            # Initialize texture manager if not already done
            if self.texture_manager is None:
                self._init_texture_manager()

            self.map_loader = SimpleMapLoader()
            if self.map_loader.load(filepath):
                # Reset camera to center of map
                if self.map_loader.heightmap:
                    width = self.map_loader.heightmap.width
                    height = self.map_loader.heightmap.height

                    logger.info(f"Map loaded: {width}x{height}")

                    # Position camera at center of map
                    center_x = width / 2.0
                    center_y = height / 2.0

                    # Get terrain height at center
                    terrain_height = self.map_loader.get_height_at(center_x, center_y)

                    # Set camera position with elevation above terrain
                    camera_elevation = (
                        self.camera.base_elevation * self.camera.zoom_level
                    )
                    camera_y = terrain_height + camera_elevation

                    logger.info(
                        f"Camera at ({center_x}, {camera_y}, {center_y}), terrain height: {terrain_height}"
                    )

                    # Reset camera with proper elevation
                    self.camera.reset(width, height)
                    self.camera.position[1] = camera_y  # Set Y elevation
                    self.camera._update_vectors()

                    logger.info(f"Camera: {self.camera}")

                # Create terrain texture map after map is loaded
                if self.terrain_texture_mapper and self.texture_manager:
                    texture_ids = list(self.base_textures.keys())
                    if texture_ids:
                        logger.info("Creating terrain texture map...")
                        self.texture_map = (
                            self.terrain_texture_mapper.create_simple_height_based_map(
                                self.map_loader.heightmap, texture_ids
                            )
                        )
                        logger.info(
                            f"Created texture map for {len(self.texture_map)} tiles"
                        )

                self.update()
                return True
            return False
        except Exception as e:
            logger.exception(f"Failed to load map: {e}")
            return False

    def _init_texture_manager(self):
        """Initialize texture manager and load test textures"""
        try:
            logger.info("Initializing texture manager...")
            self.texture_manager = SimpleTextureManager()

            # Initialize terrain texture mapper
            self.terrain_texture_mapper = TerrainTextureMapper()

            # Try to load from ExtractedAssets
            assets_path = Path("ExtractedAssets")
            if not assets_path.exists():
                assets_path = Path("../../ExtractedAssets")

            if assets_path.exists():
                count = self.texture_manager.load_available_textures(str(assets_path))
                logger.info(f"Found {count} available textures")

            # Create test texture set (colorful textures for now)
            logger.info("Creating test texture set...")
            self.base_textures = self.texture_manager.create_test_texture_set(32)
            logger.info(f"Created {len(self.base_textures)} test textures")

            # Upload to OpenGL if initialized
            if self.gl_initialized:
                self._upload_textures_to_opengl()

        except Exception as e:
            logger.error(f"Failed to initialize texture manager: {e}")
            self.texture_manager = None

    def _upload_textures_to_opengl(self):
        """Upload textures to OpenGL"""
        if not self.base_textures or self.textures_loaded:
            return

        try:
            logger.info("Uploading textures to OpenGL...")

            # Generate texture IDs
            num_textures = len(self.base_textures)
            self.texture_ids = glGenTextures(num_textures)

            # Handle single texture case
            if not isinstance(self.texture_ids, (list, tuple)):
                self.texture_ids = [self.texture_ids]

            # Upload each texture
            for i, texture_data in self.base_textures.items():
                if i >= len(self.texture_ids):
                    break

                tex_id = self.texture_ids[i]

                glBindTexture(GL_TEXTURE_2D, tex_id)

                # Set texture parameters
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

                # Upload texture data
                height, width = texture_data.shape[:2]
                glTexImage2D(
                    GL_TEXTURE_2D,
                    0,
                    GL_RGBA,
                    width,
                    height,
                    0,
                    GL_RGBA,
                    GL_UNSIGNED_BYTE,
                    texture_data,
                )

            glBindTexture(GL_TEXTURE_2D, 0)
            self.textures_loaded = True
            logger.info(f"✓ Uploaded {len(self.texture_ids)} textures to OpenGL")

        except Exception as e:
            logger.error(f"Failed to upload textures: {e}")
            self.textures_loaded = False

    def initializeGL(self):
        """Initialize OpenGL context"""
        try:
            logger.info("Initializing OpenGL...")

            # Set background color (sky blue)
            glClearColor(0.53, 0.81, 0.92, 1.0)

            # Enable depth testing
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LEQUAL)

            # Disable backface culling for now to debug visibility
            glDisable(GL_CULL_FACE)
            # glEnable(GL_CULL_FACE)
            # glCullFace(GL_BACK)

            # Enable blending for transparency
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            # Enable color material so colors work with lighting
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

            # Anti-aliasing hints (only if supported)
            try:
                glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
                glEnable(GL_LINE_SMOOTH)
            except:
                pass  # Ignore if not supported

            # Log OpenGL info
            try:
                vendor = glGetString(GL_VENDOR)
                renderer = glGetString(GL_RENDERER)
                version = glGetString(GL_VERSION)
                logger.info(f"OpenGL Vendor: {vendor}")
                logger.info(f"OpenGL Renderer: {renderer}")
                logger.info(f"OpenGL Version: {version}")
            except:
                pass

            self.gl_initialized = True
            logger.info("OpenGL initialized successfully")

            # Upload textures if texture manager is ready
            if self.texture_manager and self.base_textures:
                self._upload_textures_to_opengl()

        except Exception as e:
            logger.exception(f"OpenGL initialization failed: {e}")
            self.gl_initialized = False

    def resizeGL(self, w: int, h: int):
        """Handle window resize"""
        if h == 0:
            h = 1

        # Set viewport
        glViewport(0, 0, w, h)

        logger.info(f"Viewport resized to {w}x{h}")

    def paintGL(self):
        """Render the scene"""
        if not self.gl_initialized:
            logger.warning("OpenGL not initialized, skipping render")
            return

        try:
            # Make sure we're using the right context
            self.makeCurrent()

            # Clear buffers
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Set up projection matrix
            w = self.width()
            h = self.height() if self.height() > 0 else 1
            aspect = w / h

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(60.0, aspect, 1.0, 5000.0)

            # Set up view matrix
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Apply camera transformation
            eye = self.camera.position
            lookat = self.camera.lookat
            up = self.camera.up

            # Debug output occasionally
            if self.frame_count % 60 == 0:
                logger.debug(f"Rendering frame {self.frame_count}")
                logger.debug(f"Viewport: {w}x{h}, Camera: {eye}")

            gluLookAt(
                eye[0],
                eye[1],
                eye[2],
                lookat[0],
                lookat[1],
                lookat[2],
                up[0],
                up[1],
                up[2],
            )

            # Update lighting
            self._update_lighting()
        except Exception as e:
            logger.error(f"Error in paintGL setup: {e}")
            return

        # Draw the scene
        if self.map_loader and self.map_loader.heightmap:
            heightmap = self.map_loader.heightmap

            # Only log once per second
            if self.frame_count % 60 == 0:
                logger.debug(f"Rendering map: {heightmap.width}x{heightmap.height}")
                logger.debug(f"Camera position: {self.camera.position}")
                logger.debug(f"Camera lookat: {self.camera.lookat}")

            self._draw_heightmap()
            self._draw_grid()
            self._draw_units()
            self._draw_buildings()
        else:
            # Draw something to verify rendering is working
            logger.warning("No map loaded, drawing test scene")
            self._draw_test_triangle()

        # Draw coordinate axes (debug) - always draw for reference
        self._draw_axes()

        # Draw large test box at map center for debugging
        self._draw_test_box()

        # Draw 2D test overlay to verify rendering works AT ALL
        self._draw_2d_test()

        # Draw status overlay
        self._draw_status_overlay()

        # Update FPS counter
        self._update_fps()

    def _update_lighting(self):
        """Update sun light position based on azimuth and altitude"""
        import math

        if self.lighting_enabled:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)

            # Convert angles to radians
            azimuth_rad = math.radians(self.sun_azimuth)
            altitude_rad = math.radians(self.sun_altitude)

            # Calculate light direction
            lx = math.cos(altitude_rad) * math.cos(azimuth_rad)
            ly = math.sin(altitude_rad)
            lz = math.cos(altitude_rad) * math.sin(azimuth_rad)

            light_position = [lx, ly, lz, 0.0]  # Directional light (w=0)
            light_ambient = [0.3, 0.3, 0.3, 1.0]
            light_diffuse = [0.8, 0.8, 0.7, 1.0]
            light_specular = [0.2, 0.2, 0.2, 1.0]

            glLightfv(GL_LIGHT0, GL_POSITION, light_position)
            glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
            glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
            glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
        else:
            glDisable(GL_LIGHTING)

    def _draw_heightmap(self):
        """Draw the terrain heightmap with proper texture mapping based on height and slope"""
        heightmap = self.map_loader.heightmap
        if not heightmap:
            logger.warning("No heightmap data available")
            return

        width = heightmap.width
        height = heightmap.height

        # Only log once per second
        if self.frame_count % 60 == 0:
            logger.debug(f"Drawing heightmap: {width}x{height}")
            # Sample some heights to verify data
            sample_heights = [
                heightmap.get_height(0, 0),
                heightmap.get_height(width // 2, height // 2),
                heightmap.get_height(width - 1, height - 1),
            ]
            logger.debug(f"Sample heights: {sample_heights}")

        # Enable depth testing
        glEnable(GL_DEPTH_TEST)

        # Disable culling to see both sides
        glDisable(GL_CULL_FACE)

        # Enable lighting for this terrain if enabled
        if self.lighting_enabled:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)

        # Get height range for coloring
        all_heights = [
            heightmap.get_height(x, y)
            for y in range(0, height, 8)
            for x in range(0, width, 8)
        ]
        min_h = min(all_heights)
        max_h = max(all_heights)
        height_range = max_h - min_h if max_h > min_h else 1.0

        # Texture scaling factor (controls texture repeat)
        texture_scale = 0.05  # Lower value = more repetition for better texture detail

        # Draw with reduced resolution for better performance
        step = 2  # Changed from 4 to 2 for better detail
        vertices_drawn = 0

        # Determine if we have texture mapping available
        has_texture_mapping = bool(
            self.texture_map
            and self.textures_loaded
            and self.use_textures
            and len(self.texture_ids) > 0
        )

        if has_texture_mapping:
            # Use improved texture mapping approach based on tile coordinates
            glEnable(GL_TEXTURE_2D)

            # Draw terrain in blocks where each block can have different textures
            block_size = 32  # Size of blocks for texture switching

            for block_y in range(0, height, block_size):
                for block_x in range(0, width, block_size):
                    # Calculate which texture to use for this block based on center position
                    center_x = block_x + block_size // 2
                    center_y = block_y + block_size // 2

                    # Get texture assignment for this block
                    tile_x = center_x // 4  # Assuming 4-unit tiles from texture mapper
                    tile_y = center_y // 4
                    tile_key = (tile_x, tile_y)

                    texture_id = 0  # Default texture
                    if tile_key in self.texture_map:
                        # Use the texture with the highest weight
                        texture_assignments = self.texture_map[tile_key]
                        if texture_assignments:
                            primary_texture_id = max(
                                texture_assignments.items(), key=lambda x: x[1]
                            )[0]
                            if primary_texture_id < len(self.texture_ids):
                                texture_id = primary_texture_id
                    else:
                        # If no texture assignment, use height-based approach
                        avg_height = 0
                        height_count = 0
                        for by in range(block_y, min(block_y + block_size, height)):
                            for bx in range(block_x, min(block_x + block_size, width)):
                                avg_height += heightmap.get_height(bx, by)
                                height_count += 1
                        if height_count > 0:
                            avg_height /= height_count

                        # Map height to texture: low = grass, mid = mix, high = rock
                        if avg_height < (min_h + height_range * 0.3):
                            # Low elevation - grass type
                            texture_id = 0
                        elif avg_height < (min_h + height_range * 0.7):
                            # Mid elevation - mixed
                            texture_id = 1 if len(self.texture_ids) > 1 else 0
                        else:
                            # High elevation - rock type
                            texture_id = 2 if len(self.texture_ids) > 2 else 0

                    # Bind the texture for this block
                    glBindTexture(GL_TEXTURE_2D, self.texture_ids[texture_id])

                    # Draw this block
                    for y in range(
                        block_y, min(block_y + block_size, height - step), step
                    ):
                        glBegin(GL_TRIANGLE_STRIP)
                        for x in range(block_x, min(block_x + block_size, width), step):
                            # Get heights for normal calculation
                            h_center = heightmap.get_height(x, y)
                            h_right = (
                                heightmap.get_height(x + step, y)
                                if x + step < width
                                else h_center
                            )
                            h_down = (
                                heightmap.get_height(x, y + step)
                                if y + step < height
                                else h_center
                            )

                            # Calculate normal vector (cross product of tangent vectors)
                            # Tangent along x: (step, h_right - h_center, 0)
                            # Tangent along z: (0, h_down - h_center, step)
                            tx = [float(step), h_right - h_center, 0.0]
                            tz = [0.0, h_down - h_center, float(step)]

                            # Cross product: tx × tz
                            nx = tx[1] * tz[2] - tx[2] * tz[1]
                            ny = tx[2] * tz[0] - tx[0] * tz[2]
                            nz = tx[0] * tz[1] - tx[1] * tz[0]

                            # Normalize
                            length = (nx * nx + ny * ny + nz * nz) ** 0.5
                            if length > 0:
                                nx, ny, nz = nx / length, ny / length, nz / length
                            else:
                                nx, ny, nz = 0.0, 1.0, 0.0

                            # Current row
                            h1 = h_center
                            t1 = (h1 - min_h) / height_range

                            # Color: use white to show texture properly
                            glColor3f(1.0, 1.0, 1.0)

                            # Texture coordinates
                            glTexCoord2f(x * texture_scale, y * texture_scale)
                            glNormal3f(nx, ny, nz)  # Set normal for lighting
                            glVertex3f(float(x), h1, float(y))
                            vertices_drawn += 1

                            # Next row vertex
                            if y + step < height:
                                h2 = h_down
                                h_right2 = (
                                    heightmap.get_height(x + step, y + step)
                                    if x + step < width and y + step < height
                                    else h_center
                                )
                                h_down2 = (
                                    heightmap.get_height(x, y + step * 2)
                                    if y + step * 2 < height
                                    else h2
                                )

                                tx2 = [float(step), h_right2 - h2, 0.0]
                                tz2 = [0.0, h_down2 - h2, float(step)]

                                nx2 = tx2[1] * tz2[2] - tx2[2] * tz2[1]
                                ny2 = tx2[2] * tz2[0] - tx2[0] * tz2[2]
                                nz2 = tx2[0] * tz2[1] - tx2[1] * tz2[0]

                                length2 = (nx2 * nx2 + ny2 * ny2 + nz2 * nz2) ** 0.5
                                if length2 > 0:
                                    nx2, ny2, nz2 = (
                                        nx2 / length2,
                                        ny2 / length2,
                                        nz2 / length2,
                                    )
                                else:
                                    nx2, ny2, nz2 = 0.0, 1.0, 0.0

                                t2 = (h2 - min_h) / height_range

                                # Color: use white to show texture properly
                                glColor3f(1.0, 1.0, 1.0)

                                # Texture coordinates
                                glTexCoord2f(
                                    x * texture_scale, (y + step) * texture_scale
                                )
                                glNormal3f(nx2, ny2, nz2)
                                glVertex3f(float(x), h2, float(y + step))
                                vertices_drawn += 1

                        glEnd()
        else:
            # Fallback: Draw with single texture as before if no texture mapping is available
            if self.textures_loaded and self.use_textures and len(self.texture_ids) > 0:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(
                    GL_TEXTURE_2D, self.texture_ids[0] if self.texture_ids else 0
                )

            for y in range(0, height - step, step):
                glBegin(GL_TRIANGLE_STRIP)
                for x in range(0, width, step):
                    # Get heights for normal calculation
                    h_center = heightmap.get_height(x, y)
                    h_right = heightmap.get_height(x + step, y)
                    h_down = heightmap.get_height(x, y + step)

                    # Calculate normal vector (cross product of tangent vectors)
                    # Tangent along x: (step, h_right - h_center, 0)
                    # Tangent along z: (0, h_down - h_center, step)
                    tx = [float(step), h_right - h_center, 0.0]
                    tz = [0.0, h_down - h_center, float(step)]

                    # Cross product: tx × tz
                    nx = tx[1] * tz[2] - tx[2] * tz[1]
                    ny = tx[2] * tz[0] - tx[0] * tz[2]
                    nz = tx[0] * tz[1] - tx[1] * tz[0]

                    # Normalize
                    length = (nx * nx + ny * ny + nz * nz) ** 0.5
                    if length > 0:
                        nx, ny, nz = nx / length, ny / length, nz / length
                    else:
                        nx, ny, nz = 0.0, 1.0, 0.0

                    # Current row
                    h1 = h_center
                    t1 = (h1 - min_h) / height_range

                    # Color: use white if textured, height-based if not
                    if self.textures_loaded and self.use_textures:
                        glColor3f(1.0, 1.0, 1.0)  # White to show texture
                    else:
                        glColor3f(0.2 + t1 * 0.5, 0.4 + t1 * 0.4, 0.1 + t1 * 0.2)

                    # Texture coordinates
                    glTexCoord2f(x * texture_scale, y * texture_scale)
                    glNormal3f(nx, ny, nz)  # Set normal for lighting
                    glVertex3f(float(x), h1, float(y))
                    vertices_drawn += 1

                    # Next row vertex
                    h2 = h_down
                    h_right2 = heightmap.get_height(x + step, y + step)
                    h_down2 = heightmap.get_height(x, y + step * 2)

                    tx2 = [float(step), h_right2 - h2, 0.0]
                    tz2 = [0.0, h_down2 - h2, float(step)]

                    nx2 = tx2[1] * tz2[2] - tx2[2] * tz2[1]
                    ny2 = tx2[2] * tz2[0] - tx2[0] * tz2[2]
                    nz2 = tx2[0] * tz2[1] - tx2[1] * tz2[0]

                    length2 = (nx2 * nx2 + ny2 * ny2 + nz2 * nz2) ** 0.5
                    if length2 > 0:
                        nx2, ny2, nz2 = nx2 / length2, ny2 / length2, nz2 / length2
                    else:
                        nx2, ny2, nz2 = 0.0, 1.0, 0.0

                    t2 = (h2 - min_h) / height_range

                    # Color: use white if textured, height-based if not
                    if self.textures_loaded and self.use_textures:
                        glColor3f(1.0, 1.0, 1.0)  # White to show texture
                    else:
                        glColor3f(0.2 + t2 * 0.5, 0.4 + t2 * 0.4, 0.1 + t2 * 0.2)

                    # Texture coordinates
                    glTexCoord2f(x * texture_scale, (y + step) * texture_scale)
                    glNormal3f(nx2, ny2, nz2)
                    glVertex3f(float(x), h2, float(y + step))
                    vertices_drawn += 1

                glEnd()

        # Disable lighting and texturing after terrain
        glDisable(GL_LIGHTING)
        if self.textures_loaded and self.use_textures:
            glDisable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)

        if self.frame_count % 60 == 0:
            logger.debug(
                f"Drew {vertices_drawn} vertices (textures: {self.textures_loaded}, texture_map: {bool(self.texture_map)})"
            )

    def _draw_grid(self):
        """Draw a grid overlay on the terrain"""
        if (
            not self.map_loader
            or not self.map_loader.heightmap
            or not self.grid_enabled
        ):
            return

        heightmap = self.map_loader.heightmap
        width = heightmap.width
        height = heightmap.height

        glColor3f(0.3, 0.3, 0.3)  # Gray grid lines
        glLineWidth(1.0)

        # Grid spacing (draw every 16 units for better visibility on larger maps)
        spacing = max(16, width // 16)

        # Draw vertical lines
        for x in range(0, width, spacing):
            glBegin(GL_LINE_STRIP)
            for y in range(0, height, 4):  # Sample every 4th point for performance
                h = heightmap.get_height(x, y) + 0.2  # Slightly above terrain
                glVertex3f(x, h, y)
            glEnd()

        # Draw horizontal lines
        for y in range(0, height, spacing):
            glBegin(GL_LINE_STRIP)
            for x in range(0, width, 4):  # Sample every 4th point for performance
                h = heightmap.get_height(x, y) + 0.2
                glVertex3f(x, h, y)
            glEnd()

    def _draw_units(self):
        """Draw unit markers"""
        # Units not yet supported in simplified loader
        # TODO: Load units from companion files
        pass

    def _draw_buildings(self):
        """Draw building markers"""
        # Buildings not yet supported in simplified loader
        # TODO: Load buildings from companion files
        pass

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

    def _draw_test_triangle(self):
        """Draw a test triangle to verify OpenGL is working"""
        glPushMatrix()
        glTranslatef(0, 0, -20)  # Move it in front of camera

        glColor3f(1.0, 0.0, 0.0)  # Red
        glBegin(GL_TRIANGLES)
        glVertex3f(-5.0, -5.0, 0.0)
        glVertex3f(5.0, -5.0, 0.0)
        glVertex3f(0.0, 5.0, 0.0)
        glEnd()

        glPopMatrix()

    def _draw_axes(self):
        """Draw coordinate axes for debugging at map center"""
        glLineWidth(3.0)
        glDisable(GL_DEPTH_TEST)  # Draw on top
        glDisable(GL_LIGHTING)  # No lighting on axes

        # Draw axes at map center if map is loaded
        if self.map_loader and self.map_loader.heightmap:
            center_x = self.map_loader.heightmap.width / 2
            center_z = self.map_loader.heightmap.height / 2
            center_y = self.map_loader.get_height_at(center_x, center_z)
        else:
            center_x, center_y, center_z = 0, 0, 0

        glBegin(GL_LINES)

        # X axis (red)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(center_x, center_y, center_z)
        glVertex3f(center_x + 30, center_y, center_z)

        # Y axis (green) - up
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(center_x, center_y, center_z)
        glVertex3f(center_x, center_y + 30, center_z)

        # Z axis (blue)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(center_x, center_y, center_z)
        glVertex3f(center_x, center_y, center_z + 30)

        glEnd()

        glEnable(GL_DEPTH_TEST)  # Re-enable depth testing

    def _draw_test_box(self):
        """Draw a large colorful box at map center to verify rendering"""
        if not self.map_loader or not self.map_loader.heightmap:
            return

        glDisable(GL_DEPTH_TEST)  # Draw on top
        glDisable(GL_LIGHTING)  # No lighting on debug box

        # Get map center
        center_x = self.map_loader.heightmap.width / 2
        center_z = self.map_loader.heightmap.height / 2
        center_y = (
            self.map_loader.get_height_at(center_x, center_z) + 10
        )  # 10 units above terrain

        # Draw a large wireframe cube
        size = 20.0
        glColor3f(1.0, 1.0, 0.0)  # Yellow
        glLineWidth(5.0)

        # Draw wireframe box
        glPushMatrix()
        glTranslatef(center_x, center_y, center_z)

        # Bottom square
        glBegin(GL_LINE_LOOP)
        glVertex3f(-size, -size, -size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size, size)
        glVertex3f(-size, -size, size)
        glEnd()

        # Top square
        glBegin(GL_LINE_LOOP)
        glVertex3f(-size, size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, size, size)
        glVertex3f(-size, size, size)
        glEnd()

        # Vertical lines
        glBegin(GL_LINES)
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, size, -size)

        glVertex3f(size, -size, -size)
        glVertex3f(size, size, -size)

        glVertex3f(size, -size, size)
        glVertex3f(size, size, size)

        glVertex3f(-size, -size, size)
        glVertex3f(-size, size, size)
        glEnd()

        glPopMatrix()

        glEnable(GL_DEPTH_TEST)

    def _draw_2d_test(self):
        """Draw simple 2D overlay to verify OpenGL is working at all"""
        # Only draw this if no map is loaded
        if self.map_loader and self.map_loader.heightmap:
            return

        glDisable(GL_LIGHTING)  # No lighting on 2D overlay

        # Switch to 2D orthographic projection
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width(), self.height(), 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)

        # Draw a large red rectangle that MUST be visible
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(100, 100)
        glVertex2f(300, 100)
        glVertex2f(300, 300)
        glVertex2f(100, 300)
        glEnd()

        # Draw green outline
        glColor3f(0.0, 1.0, 0.0)
        glLineWidth(5.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(100, 100)
        glVertex2f(300, 100)
        glVertex2f(300, 300)
        glVertex2f(100, 300)
        glEnd()

        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)

    def _draw_status_overlay(self):
        """Draw status text overlay showing FPS and info"""
        if not self.map_loader or not self.map_loader.heightmap:
            return

        glDisable(GL_LIGHTING)  # No lighting on 2D overlay

        # Switch to 2D orthographic projection
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width(), self.height(), 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)

        # Draw semi-transparent background (larger to fit labels)
        glColor4f(0.0, 0.0, 0.0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(10, 10)
        glVertex2f(320, 10)
        glVertex2f(320, 130)
        glVertex2f(10, 130)
        glEnd()

        h = self.map_loader.heightmap

        # Draw colored bars with labels using simple geometric shapes

        # FPS indicator (green = good)
        fps_color = 0.0 if self.fps < 30 else (1.0 if self.fps > 60 else 0.5)
        glColor3f(1.0 - fps_color, fps_color, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(90, 20)
        glVertex2f(90 + min(self.fps * 2, 220), 20)
        glVertex2f(90 + min(self.fps * 2, 220), 35)
        glVertex2f(90, 35)
        glEnd()

        # FPS label using simple shapes (F P S)
        glColor3f(1.0, 1.0, 1.0)
        # F
        glBegin(GL_QUADS)
        glVertex2f(20, 20)
        glVertex2f(22, 20)
        glVertex2f(22, 35)
        glVertex2f(20, 35)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(20, 20)
        glVertex2f(28, 20)
        glVertex2f(28, 22)
        glVertex2f(20, 22)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(20, 26)
        glVertex2f(26, 26)
        glVertex2f(26, 28)
        glVertex2f(20, 28)
        glEnd()

        # P
        glBegin(GL_QUADS)
        glVertex2f(32, 20)
        glVertex2f(34, 20)
        glVertex2f(34, 35)
        glVertex2f(32, 35)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(32, 20)
        glVertex2f(40, 20)
        glVertex2f(40, 22)
        glVertex2f(32, 22)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(38, 20)
        glVertex2f(40, 20)
        glVertex2f(40, 28)
        glVertex2f(38, 28)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(32, 26)
        glVertex2f(40, 26)
        glVertex2f(40, 28)
        glVertex2f(32, 28)
        glEnd()

        # S
        glBegin(GL_QUADS)
        glVertex2f(44, 20)
        glVertex2f(52, 20)
        glVertex2f(52, 22)
        glVertex2f(44, 22)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(44, 20)
        glVertex2f(46, 20)
        glVertex2f(46, 28)
        glVertex2f(44, 28)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(44, 26)
        glVertex2f(52, 26)
        glVertex2f(52, 28)
        glVertex2f(44, 28)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(50, 26)
        glVertex2f(52, 26)
        glVertex2f(52, 35)
        glVertex2f(50, 35)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(44, 33)
        glVertex2f(52, 33)
        glVertex2f(52, 35)
        glVertex2f(44, 35)
        glEnd()

        # Colon
        glBegin(GL_QUADS)
        glVertex2f(56, 22)
        glVertex2f(58, 22)
        glVertex2f(58, 24)
        glVertex2f(56, 24)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(56, 31)
        glVertex2f(58, 31)
        glVertex2f(58, 33)
        glVertex2f(56, 33)
        glEnd()

        # Display FPS number as bar length indicator
        # (actual number rendering would need font texture)

        # Map size indicator
        glColor3f(0.3, 0.7, 1.0)
        map_width_bar = (h.width / 1024.0) * 220
        glBegin(GL_QUADS)
        glVertex2f(90, 50)
        glVertex2f(90 + map_width_bar, 50)
        glVertex2f(90 + map_width_bar, 65)
        glVertex2f(90, 65)
        glEnd()

        # MAP label
        glColor3f(1.0, 1.0, 1.0)
        # M
        glBegin(GL_QUADS)
        glVertex2f(20, 50)
        glVertex2f(22, 50)
        glVertex2f(22, 65)
        glVertex2f(20, 65)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(30, 50)
        glVertex2f(32, 50)
        glVertex2f(32, 65)
        glVertex2f(30, 65)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(20, 50)
        glVertex2f(26, 56)
        glVertex2f(24, 56)
        glVertex2f(20, 52)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(26, 56)
        glVertex2f(32, 50)
        glVertex2f(32, 52)
        glVertex2f(28, 56)
        glEnd()

        # A
        glBegin(GL_QUADS)
        glVertex2f(36, 50)
        glVertex2f(38, 50)
        glVertex2f(38, 65)
        glVertex2f(36, 65)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(44, 50)
        glVertex2f(46, 50)
        glVertex2f(46, 65)
        glVertex2f(44, 65)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(36, 50)
        glVertex2f(46, 50)
        glVertex2f(46, 52)
        glVertex2f(36, 52)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(36, 56)
        glVertex2f(46, 56)
        glVertex2f(46, 58)
        glVertex2f(36, 58)
        glEnd()

        # P
        glBegin(GL_QUADS)
        glVertex2f(50, 50)
        glVertex2f(52, 50)
        glVertex2f(52, 65)
        glVertex2f(50, 65)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(50, 50)
        glVertex2f(58, 50)
        glVertex2f(58, 52)
        glVertex2f(50, 52)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(56, 50)
        glVertex2f(58, 50)
        glVertex2f(58, 58)
        glVertex2f(56, 58)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(50, 56)
        glVertex2f(58, 56)
        glVertex2f(58, 58)
        glVertex2f(50, 58)
        glEnd()

        # Colon
        glBegin(GL_QUADS)
        glVertex2f(62, 52)
        glVertex2f(64, 52)
        glVertex2f(64, 54)
        glVertex2f(62, 54)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(62, 61)
        glVertex2f(64, 61)
        glVertex2f(64, 63)
        glVertex2f(62, 63)
        glEnd()

        # Camera height indicator
        glColor3f(1.0, 0.7, 0.3)
        cam_height_bar = min((self.camera.position[1] / 200.0) * 220, 220)
        glBegin(GL_QUADS)
        glVertex2f(90, 80)
        glVertex2f(90 + cam_height_bar, 80)
        glVertex2f(90 + cam_height_bar, 95)
        glVertex2f(90, 95)
        glEnd()

        # CAM label
        glColor3f(1.0, 1.0, 1.0)
        # C
        glBegin(GL_QUADS)
        glVertex2f(20, 80)
        glVertex2f(28, 80)
        glVertex2f(28, 82)
        glVertex2f(20, 82)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(20, 80)
        glVertex2f(22, 80)
        glVertex2f(22, 95)
        glVertex2f(20, 95)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(20, 93)
        glVertex2f(28, 93)
        glVertex2f(28, 95)
        glVertex2f(20, 95)
        glEnd()

        # A
        glBegin(GL_QUADS)
        glVertex2f(32, 80)
        glVertex2f(34, 80)
        glVertex2f(34, 95)
        glVertex2f(32, 95)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(40, 80)
        glVertex2f(42, 80)
        glVertex2f(42, 95)
        glVertex2f(40, 95)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(32, 80)
        glVertex2f(42, 80)
        glVertex2f(42, 82)
        glVertex2f(32, 82)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(32, 86)
        glVertex2f(42, 86)
        glVertex2f(42, 88)
        glVertex2f(32, 88)
        glEnd()

        # M
        glBegin(GL_QUADS)
        glVertex2f(46, 80)
        glVertex2f(48, 80)
        glVertex2f(48, 95)
        glVertex2f(46, 95)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(56, 80)
        glVertex2f(58, 80)
        glVertex2f(58, 95)
        glVertex2f(56, 95)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(46, 80)
        glVertex2f(52, 86)
        glVertex2f(50, 86)
        glVertex2f(46, 82)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(52, 86)
        glVertex2f(58, 80)
        glVertex2f(58, 82)
        glVertex2f(54, 86)
        glEnd()

        # Colon
        glBegin(GL_QUADS)
        glVertex2f(62, 82)
        glVertex2f(64, 82)
        glVertex2f(64, 84)
        glVertex2f(62, 84)
        glEnd()
        glBegin(GL_QUADS)
        glVertex2f(62, 91)
        glVertex2f(64, 91)
        glVertex2f(64, 93)
        glVertex2f(62, 93)
        glEnd()

        # Add small text indicator for values
        # FPS value indicator (small dots representing ~60, 120, etc.)
        glColor4f(0.8, 0.8, 0.8, 0.5)
        # 60 FPS marker
        glBegin(GL_QUADS)
        glVertex2f(210, 24)
        glVertex2f(211, 24)
        glVertex2f(211, 31)
        glVertex2f(210, 31)
        glEnd()

        # Map size indicators (256, 512, 1024)
        # Small tick marks
        for i, size in enumerate([256, 512, 1024]):
            x_pos = 90 + (size / 1024.0) * 220
            glBegin(GL_QUADS)
            glVertex2f(x_pos, 54)
            glVertex2f(x_pos + 1, 54)
            glVertex2f(x_pos + 1, 61)
            glVertex2f(x_pos, 61)
            glEnd()

        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_DEPTH_TEST)

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

        # Sun position adjustment with Shift + Arrow keys
        if Qt.Key.Key_Shift in self.keys_pressed:
            sun_changed = False
            if (
                Qt.Key.Key_Left in self.keys_pressed
                or Qt.Key.Key_A in self.keys_pressed
            ):
                self.sun_azimuth -= 30.0 * delta_time
                sun_changed = True
            if (
                Qt.Key.Key_Right in self.keys_pressed
                or Qt.Key.Key_D in self.keys_pressed
            ):
                self.sun_azimuth += 30.0 * delta_time
                sun_changed = True
            if Qt.Key.Key_Up in self.keys_pressed or Qt.Key.Key_W in self.keys_pressed:
                self.sun_altitude = min(90.0, self.sun_altitude + 30.0 * delta_time)
                sun_changed = True
            if (
                Qt.Key.Key_Down in self.keys_pressed
                or Qt.Key.Key_S in self.keys_pressed
            ):
                self.sun_altitude = max(-90.0, self.sun_altitude - 30.0 * delta_time)
                sun_changed = True

            if sun_changed:
                self.sun_azimuth = self.sun_azimuth % 360.0
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
        elif event.key() == Qt.Key.Key_L:
            # Toggle lighting (handled by parent window)
            pass
        elif event.key() == Qt.Key.Key_G:
            # Toggle grid (handled by parent window)
            pass
        elif event.key() == Qt.Key.Key_D:
            # Debug info
            logger.info("=== DEBUG INFO ===")
            logger.info(f"Camera: {self.camera}")
            logger.info(f"Position: {self.camera.position}")
            logger.info(f"Lookat: {self.camera.lookat}")
            logger.info(f"Forward: {self.camera.forward}")
            logger.info(f"Up: {self.camera.up}")
            logger.info(f"Lighting: {'ON' if self.lighting_enabled else 'OFF'}")
            logger.info(
                f"Sun: azimuth={self.sun_azimuth:.1f}°, altitude={self.sun_altitude:.1f}°"
            )
            if self.map_loader and self.map_loader.heightmap:
                h = self.map_loader.heightmap
                logger.info(f"Map size: {h.width}x{h.height}")
                center_h = h.get_height(h.width // 2, h.height // 2)
                logger.info(f"Center terrain height: {center_h}")
            logger.info("==================")

    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release"""
        self.keys_pressed.discard(event.key())

    def toggle_lighting(self):
        """Toggle lighting state"""
        self.lighting_enabled = not self.lighting_enabled
        logger.info(f"Lighting: {'ON' if self.lighting_enabled else 'OFF'}")
        self.update()

    def toggle_grid(self):
        """Toggle grid state"""
        self.grid_enabled = not self.grid_enabled
        logger.info(f"Grid: {'ON' if self.grid_enabled else 'OFF'}")
        self.update()


class MapViewerWindow(QMainWindow):
    """Main window for the map viewer application"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SpellForce Map Viewer")
        self.setMinimumSize(1280, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout - horizontal split
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left side: Compact controls panel
        controls_widget = QWidget()
        controls_widget.setMaximumWidth(200)
        controls_widget.setMinimumWidth(200)
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(5, 5, 5, 5)

        # Buttons
        self.open_button = QPushButton("📂 Open Map")
        self.open_button.clicked.connect(self.open_map)
        controls_layout.addWidget(self.open_button)

        self.reset_button = QPushButton("🔄 Reset Camera")
        self.reset_button.clicked.connect(self.reset_camera)
        controls_layout.addWidget(self.reset_button)

        controls_layout.addSpacing(5)

        # Checkboxes for toggles
        from PySide6.QtWidgets import QCheckBox

        self.lighting_checkbox = QCheckBox("💡 Lighting (L)")
        self.lighting_checkbox.setChecked(True)
        self.lighting_checkbox.stateChanged.connect(self.toggle_lighting_checkbox)
        controls_layout.addWidget(self.lighting_checkbox)

        self.grid_checkbox = QCheckBox("⊞ Grid (G)")
        self.grid_checkbox.setChecked(True)
        self.grid_checkbox.stateChanged.connect(self.toggle_grid_checkbox)
        controls_layout.addWidget(self.grid_checkbox)

        controls_layout.addSpacing(10)

        # Info section
        info_group = QWidget()
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(0, 0, 0, 0)

        self.info_label = QLabel("No map loaded")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 11px; color: #aaa;")
        info_layout.addWidget(self.info_label)

        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setStyleSheet("font-size: 11px; color: #0a0;")
        info_layout.addWidget(self.fps_label)

        controls_layout.addWidget(info_group)
        controls_layout.addSpacing(10)

        # Shortcuts section
        shortcuts_label = QLabel("<b>⌨️ Controls</b>")
        shortcuts_label.setStyleSheet("font-size: 12px;")
        controls_layout.addWidget(shortcuts_label)

        shortcuts_text = QLabel(
            "<small>"
            "<b>Movement:</b><br>"
            "• WASD / Arrows<br>"
            "• Middle Mouse Drag<br><br>"
            "<b>View:</b><br>"
            "• Mouse Wheel: Zoom<br>"
            "• Home/End: Rotate<br>"
            "• PgUp/PgDn: Tilt<br><br>"
            "<b>Lighting:</b><br>"
            "• L: Toggle light<br>"
            "• Shift + WASD: Sun<br><br>"
            "<b>Display:</b><br>"
            "• G: Toggle grid<br><br>"
            "<b>Other:</b><br>"
            "• D: Debug info<br>"
            "• Insert/Del: Zoom<br>"
            "</small>"
        )
        shortcuts_text.setWordWrap(True)
        shortcuts_text.setStyleSheet("font-size: 10px; color: #ccc;")
        controls_layout.addWidget(shortcuts_text)

        controls_layout.addStretch()

        main_layout.addWidget(controls_widget)

        # Right side: OpenGL viewer widget (takes all remaining space)
        self.viewer = MapViewerWidget()
        main_layout.addWidget(self.viewer, 1)  # Stretch factor 1

        # Status bar at bottom
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready • Phase 2: Lighting System Active ✨")

        # FPS update timer
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self.update_info)
        self.fps_timer.start(500)  # Update twice per second

        # Apply styling
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3c3f41;
                border: 1px solid #555555;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4c4f51;
                border: 1px solid #6c6f71;
            }
            QPushButton:pressed {
                background-color: #2c2f31;
            }
            QLabel {
                padding: 3px;
            }
            QStatusBar {
                background-color: #1e1e1e;
                color: #888;
                font-size: 10px;
            }
            QCheckBox {
                color: #ccc;
                font-size: 11px;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #2b2b2b;
            }
            QCheckBox::indicator:checked {
                background-color: #4a9eff;
                border: 1px solid #6ab0ff;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #6c6f71;
            }
        """
        )

        # Set up global shortcuts
        from PySide6.QtGui import QKeySequence, QShortcut

        # Lighting toggle shortcut
        self.lighting_shortcut = QShortcut(QKeySequence("L"), self)
        self.lighting_shortcut.activated.connect(self.toggle_lighting_shortcut)

        # Grid toggle shortcut
        self.grid_shortcut = QShortcut(QKeySequence("G"), self)
        self.grid_shortcut.activated.connect(self.toggle_grid_shortcut)

    def toggle_lighting_shortcut(self):
        """Toggle lighting from keyboard shortcut"""
        self.viewer.toggle_lighting()
        self.lighting_checkbox.setChecked(self.viewer.lighting_enabled)

    def toggle_grid_shortcut(self):
        """Toggle grid from keyboard shortcut"""
        self.viewer.toggle_grid()
        self.grid_checkbox.setChecked(self.viewer.grid_enabled)

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
            try:
                if self.viewer.load_map(Path(filepath)):
                    map_loader = self.viewer.map_loader
                    if map_loader.heightmap:
                        info = f"<b>Map:</b> {map_loader.heightmap.width}x{map_loader.heightmap.height}<br>"
                        info += f"<small>{Path(filepath).name}</small>"
                        self.info_label.setText(info)
                    self.status_bar.showMessage(f"✓ Loaded: {Path(filepath).name}")
                else:
                    QMessageBox.warning(
                        self,
                        "Load Error",
                        "Failed to load map file. Check the log for details.\n\n"
                        "The map format may not be fully supported yet.",
                    )
                    self.status_bar.showMessage("✗ Failed to load map")
            except Exception as e:
                logger.exception(f"Error loading map: {e}")
                QMessageBox.critical(
                    self,
                    "Load Error",
                    f"Failed to load map file:\n\n{str(e)}\n\n"
                    "This map format may not be fully supported yet.\n"
                    "Try using the map inspector tool to analyze the file:\n"
                    "python -m TirganachReloaded.map_viewer.inspect_map <file.map>",
                )
                self.status_bar.showMessage(f"✗ Error: {str(e)}")

    def reset_camera(self):
        """Reset camera to default position"""
        if self.viewer.map_loader and self.viewer.map_loader.heightmap:
            self.viewer.camera.reset(
                self.viewer.map_loader.heightmap.width,
                self.viewer.map_loader.heightmap.height,
            )
            self.viewer.update()
            self.status_bar.showMessage("✓ Camera reset to center")

    def update_info(self):
        """Update FPS and other info"""
        self.fps_label.setText(f"FPS: {self.viewer.fps:.1f}")

    def toggle_lighting_checkbox(self, state):
        """Toggle lighting from checkbox"""
        self.viewer.lighting_enabled = bool(state)
        self.viewer.update()

    def toggle_grid_checkbox(self, state):
        """Toggle grid from checkbox"""
        self.viewer.grid_enabled = bool(state)
        self.viewer.update()


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
