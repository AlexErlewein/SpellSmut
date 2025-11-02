#!/usr/bin/env python3
"""
SpellForce Map Viewer Launcher
Standalone launcher for viewing SpellForce .map files in 3D
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
)
logger.add(
    "map_viewer.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
)


def check_dependencies():
    """Check if all required dependencies are installed"""
    missing = []

    try:
        import PySide6
    except ImportError:
        missing.append("PySide6")

    try:
        import OpenGL
    except ImportError:
        missing.append("PyOpenGL")

    try:
        import numpy
    except ImportError:
        missing.append("numpy")

    if missing:
        logger.error("Missing required dependencies:")
        for dep in missing:
            logger.error(f"  - {dep}")
        logger.error("\nInstall with: pip install PySide6 PyOpenGL numpy")
        return False

    return True


def main():
    """Main entry point"""
    logger.info("Starting SpellForce Map Viewer...")

    if not check_dependencies():
        sys.exit(1)

    try:
        from PySide6.QtWidgets import QApplication

        from TirganachReloaded.map_viewer import MapViewerWindow

        app = QApplication(sys.argv)
        app.setApplicationName("SpellForce Map Viewer")
        app.setOrganizationName("SpellSmut Modding Tools")

        window = MapViewerWindow()
        window.show()

        logger.info("Map Viewer started successfully")
        logger.info("Controls:")
        logger.info("  - Arrow keys / WASD: Move camera")
        logger.info("  - Middle mouse drag: Rotate camera")
        logger.info("  - Mouse wheel: Zoom in/out")
        logger.info("  - Home/End: Rotate left/right")
        logger.info("  - Page Up/Down: Tilt camera")
        logger.info("  - Insert/Delete: Zoom in/out")

        sys.exit(app.exec())

    except Exception as e:
        logger.exception(f"Failed to start map viewer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
