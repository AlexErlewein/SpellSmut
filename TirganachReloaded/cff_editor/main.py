"""
SpellForce GameData.cff Editor - Main Entry Point
==================================================

A modern GUI application for viewing and editing GameData.cff files.

Usage:
    python main.py
"""

import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("SpellForce CFF Editor")
    app.setOrganizationName("SpellSmut Modding Tools")

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
