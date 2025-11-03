"""
Camera System for Map Viewer
Handles 3D camera controls including position, rotation, and movement
"""

import math
from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass
class CameraState:
    """Current camera state"""

    position: np.ndarray  # [x, y, z]
    azimuth: float  # Horizontal rotation (radians)
    altitude: float  # Vertical rotation (radians)
    zoom_level: float  # Zoom factor (0.1 to 6.0)


class Camera:
    """
    3D Camera for map navigation

    Controls:
    - Position: Move around the map
    - Azimuth: Horizontal rotation (left/right)
    - Altitude: Vertical rotation (up/down)
    - Zoom: Distance from terrain
    """

    def __init__(
        self,
        position: Tuple[float, float, float] = (0, 0, 0),
        azimuth: float = math.pi / 2,  # 90 degrees (facing forward)
        altitude: float = -math.pi * 45 / 180,  # -45 degrees (looking down)
        zoom_level: float = 1.0,
    ):
        """
        Initialize camera

        Args:
            position: Initial [x, y, z] position
            azimuth: Horizontal angle in radians (0 = East, π/2 = North)
            altitude: Vertical angle in radians (negative = looking down)
            zoom_level: Zoom multiplier (0.1 to 6.0)
        """
        self.position = np.array(position, dtype=np.float32)
        self.azimuth = azimuth
        self.altitude = altitude
        self.zoom_level = max(0.1, min(6.0, zoom_level))

        # Camera properties
        self.base_elevation = (
            100.0  # Base height above terrain (increased for better view)
        )
        self.movement_speed = 60.0  # Units per second
        self.rotation_speed = 2.0  # Radians per second

        # Derived vectors (calculated from angles)
        self.forward = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.right = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.lookat = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        self._update_vectors()

    def _update_vectors(self):
        """Update camera direction vectors based on azimuth and altitude"""
        # Calculate forward direction from angles
        cos_altitude = math.cos(self.altitude)
        sin_altitude = math.sin(self.altitude)
        cos_azimuth = math.cos(self.azimuth)
        sin_azimuth = math.sin(self.azimuth)

        # Forward vector (where camera is looking)
        self.forward = np.array(
            [
                cos_altitude * cos_azimuth,
                sin_altitude,
                cos_altitude * sin_azimuth,
            ],
            dtype=np.float32,
        )

        # Right vector (perpendicular to forward, parallel to ground)
        self.right = np.array([-sin_azimuth, 0.0, cos_azimuth], dtype=np.float32)

        # Up vector (perpendicular to both)
        self.up = np.cross(self.right, self.forward)

        # Normalize vectors
        self.forward = self.forward / np.linalg.norm(self.forward)
        self.right = self.right / np.linalg.norm(self.right)
        self.up = self.up / np.linalg.norm(self.up)

        # Calculate lookat point
        self.lookat = self.position + self.forward * 10.0

    def set_position(self, x: float, y: float, z: float):
        """Set camera position directly"""
        self.position = np.array([x, y, z], dtype=np.float32)
        self._update_vectors()

    def set_elevation(self, height: float, terrain_height: float = 0.0):
        """
        Set camera elevation above terrain

        Args:
            height: Desired height above terrain
            terrain_height: Current terrain height at camera position
        """
        self.position[1] = terrain_height + height

    def move(self, forward: float, right: float, delta_time: float):
        """
        Move camera relative to current orientation

        Args:
            forward: Forward/backward amount (-1 to 1)
            right: Left/right amount (-1 to 1)
            delta_time: Time elapsed since last frame (seconds)
        """
        movement = np.zeros(3, dtype=np.float32)

        # Forward/backward on XZ plane only
        forward_xz = np.array([self.forward[0], 0.0, self.forward[2]], dtype=np.float32)
        forward_xz = forward_xz / (np.linalg.norm(forward_xz) + 1e-6)
        movement += forward_xz * forward

        # Left/right
        movement += self.right * right

        # Apply movement with speed and time
        self.position += movement * self.movement_speed * delta_time
        self._update_vectors()

    def rotate(self, delta_azimuth: float, delta_altitude: float):
        """
        Rotate camera

        Args:
            delta_azimuth: Change in horizontal angle (radians)
            delta_altitude: Change in vertical angle (radians)
        """
        self.azimuth += delta_azimuth
        self.altitude += delta_altitude

        # Clamp altitude to prevent flipping
        self.altitude = max(-math.pi * 89 / 180, min(-math.pi * 1 / 180, self.altitude))

        # Normalize azimuth to [0, 2π)
        self.azimuth = self.azimuth % (2 * math.pi)

        self._update_vectors()

    def set_azimuth_altitude(self, azimuth: float, altitude: float):
        """Set camera angles directly"""
        self.azimuth = azimuth
        self.altitude = max(-math.pi * 89 / 180, min(-math.pi * 1 / 180, altitude))
        self._update_vectors()

    def add_zoom(self, delta: float):
        """
        Adjust zoom level

        Args:
            delta: Zoom change (negative = zoom in, positive = zoom out)
        """
        if delta < 0:
            self.zoom_level *= 1.1
        else:
            self.zoom_level *= 0.9

        # Clamp zoom level
        self.zoom_level = max(0.1, min(6.0, self.zoom_level))

    def reset(self, map_width: int, map_height: int):
        """
        Reset camera to default position (center of map)

        Args:
            map_width: Map width in grid units
            map_height: Map height in grid units
        """
        # Position camera high above center of map
        camera_height = max(map_width, map_height) * 0.5  # 50% of map size as height
        self.position = np.array(
            [map_width / 2, camera_height, map_height / 2 + map_height * 0.3],
            dtype=np.float32,
        )
        self.azimuth = math.pi / 2  # 90 degrees (facing north)
        self.altitude = -math.pi * 45 / 180  # -45 degrees (looking down at angle)
        self.zoom_level = 1.0
        self._update_vectors()

    def get_view_matrix(self) -> np.ndarray:
        """
        Get view matrix for rendering

        Returns:
            4x4 view matrix
        """
        # Create view matrix using lookAt
        eye = self.position
        center = self.lookat
        up = self.up

        f = center - eye
        f = f / np.linalg.norm(f)

        s = np.cross(f, up)
        s = s / np.linalg.norm(s)

        u = np.cross(s, f)

        view_matrix = np.array(
            [
                [s[0], s[1], s[2], -np.dot(s, eye)],
                [u[0], u[1], u[2], -np.dot(u, eye)],
                [-f[0], -f[1], -f[2], np.dot(f, eye)],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float32,
        )

        return view_matrix

    def get_projection_matrix(
        self,
        fov: float = 60.0,
        aspect: float = 1.333,
        near: float = 0.1,
        far: float = 1000.0,
    ) -> np.ndarray:
        """
        Get projection matrix for rendering

        Args:
            fov: Field of view in degrees
            aspect: Aspect ratio (width/height)
            near: Near clipping plane
            far: Far clipping plane

        Returns:
            4x4 projection matrix
        """
        fov_rad = math.radians(fov)
        f = 1.0 / math.tan(fov_rad / 2.0)

        proj_matrix = np.array(
            [
                [f / aspect, 0.0, 0.0, 0.0],
                [0.0, f, 0.0, 0.0],
                [
                    0.0,
                    0.0,
                    (far + near) / (near - far),
                    (2 * far * near) / (near - far),
                ],
                [0.0, 0.0, -1.0, 0.0],
            ],
            dtype=np.float32,
        )

        return proj_matrix

    def get_state(self) -> CameraState:
        """Get current camera state"""
        return CameraState(
            position=self.position.copy(),
            azimuth=self.azimuth,
            altitude=self.altitude,
            zoom_level=self.zoom_level,
        )

    def set_state(self, state: CameraState):
        """Restore camera from saved state"""
        self.position = state.position.copy()
        self.azimuth = state.azimuth
        self.altitude = state.altitude
        self.zoom_level = state.zoom_level
        self._update_vectors()

    def screen_to_world_ray(
        self, screen_x: float, screen_y: float, width: int, height: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert screen coordinates to world-space ray

        Args:
            screen_x: Screen X coordinate
            screen_y: Screen Y coordinate
            width: Viewport width
            height: Viewport height

        Returns:
            (ray_origin, ray_direction) tuple
        """
        # Normalize screen coordinates to [-1, 1]
        x_ndc = (2.0 * screen_x) / width - 1.0
        y_ndc = 1.0 - (2.0 * screen_y) / height

        # Get inverse projection and view matrices
        aspect = width / height
        proj = self.get_projection_matrix(aspect=aspect)
        view = self.get_view_matrix()

        # Ray in clip space
        ray_clip = np.array([x_ndc, y_ndc, -1.0, 1.0])

        # Ray in eye space
        ray_eye = np.linalg.inv(proj) @ ray_clip
        ray_eye[2] = -1.0
        ray_eye[3] = 0.0

        # Ray in world space
        ray_world = (np.linalg.inv(view) @ ray_eye)[:3]
        ray_world = ray_world / np.linalg.norm(ray_world)

        return self.position, ray_world

    def __repr__(self) -> str:
        return (
            f"Camera(pos={self.position}, "
            f"azimuth={math.degrees(self.azimuth):.1f}°, "
            f"altitude={math.degrees(self.altitude):.1f}°, "
            f"zoom={self.zoom_level:.2f})"
        )
