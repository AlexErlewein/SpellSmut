"""
Launch the SpellForce GameData.cff Editor
==========================================

This script launches the GUI editor for viewing and editing CFF files.

Usage:
    python run_cff_editor.py
"""

import sys
import os

# Add the cff_editor directory to the path
editor_dir = os.path.join(os.path.dirname(__file__), 'cff_editor')
sys.path.insert(0, editor_dir)

from PySide6.QtWidgets import QApplication
from main_window import MainWindow


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
