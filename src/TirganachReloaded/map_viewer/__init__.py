"""
SpellForce Map Viewer
A Python implementation of the map viewer for SpellForce maps (.map files)

This package provides:
- Map file loading and parsing
- 3D OpenGL-based rendering
- Camera controls for navigation
- Heightmap visualization
- Texture rendering
"""

__version__ = "0.1.0"

from .map_loader import MapLoader
from .map_viewer_window import MapViewerWindow
from .simple_map_loader import SimpleMapLoader

__all__ = [
    "MapLoader",
    "SimpleMapLoader",
    "MapViewerWindow",
]
