"""
SpellForce GameData.cff Editor - Main Entry Point
==================================================

A modern GUI application for viewing and editing GameData.cff files.

Usage:
    python main.py
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .logging_config import configure_logging
from .main_window import MainWindow


def main():
    """Main entry point"""
    # Configure structured logging first
    project_root = Path(__file__).parent.parent.parent.parent
    debug_mode = "--debug" in sys.argv
    configure_logging(debug_mode=debug_mode, project_root=project_root)
    
    from .logging_config import get_logger
    logger = get_logger("main")
    logger.info("Starting SpellForce CFF Editor")
    logger.debug(f"Debug mode: {debug_mode}")
    
    app = QApplication(sys.argv)
    app.setApplicationName("SpellForce CFF Editor")
    app.setOrganizationName("SpellSmut Modding Tools")

    # Create and show main window
    try:
        window = MainWindow()
        window.show()
        logger.info("Main window created and shown")
    except Exception as e:
        logger.exception(f"Failed to create main window: {e}")
        sys.exit(1)

    try:
        logger.info("Starting Qt event loop")
        sys.exit(app.exec())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.exception(f"Application crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
