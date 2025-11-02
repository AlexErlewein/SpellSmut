"""
Launch SpellForce GameData.cff Editor
==========================================

This script launches GUI editor for viewing and editing CFF files.

Usage:
    python run_cff_editor.py
"""

import sys
import os

from loguru import logger
from PySide6.QtWidgets import QApplication
from cff_editor.main_window import MainWindow


def main():
    """Main entry point"""
    logger.info("="*60)
    logger.info("SpellForce GameData.cff Editor")
    logger.info("="*60)
    logger.info("Starting GUI application...")
    print("Starting GUI application...")
    print()

    app = QApplication(sys.argv)
    app.setApplicationName("SpellForce CFF Editor")
    app.setOrganizationName("SpellSmut Modding Tools")

    # Create and show main window
    window = MainWindow()
    window.show()

    logger.info("Application started successfully!")
    logger.info("Use File > Open to load a GameData.cff file.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
