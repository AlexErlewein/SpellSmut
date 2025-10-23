"""
Launch the SpellForce GameData.cff Editor
==========================================

This script launches the GUI editor for viewing and editing CFF files.

Usage:
    python run_cff_editor.py
"""

import sys
import os

from PySide6.QtWidgets import QApplication
from cff_editor.main_window import MainWindow


def main():
    """Main entry point"""
    print("="*60)
    print("SpellForce GameData.cff Editor")
    print("="*60)
    print()
    print("Starting GUI application...")
    print()

    app = QApplication(sys.argv)
    app.setApplicationName("SpellForce CFF Editor")
    app.setOrganizationName("SpellSmut Modding Tools")

    # Create and show main window
    window = MainWindow()
    window.show()

    print("Application started successfully!")
    print("Use File > Open to load a GameData.cff file.")
    print()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
