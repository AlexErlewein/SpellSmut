#!/usr/bin/env python3
"""
Standalone Icon Browser Tool
============================

A simple standalone tool to browse and view game icons.
Run this script to launch the icon browser without the full CFF editor.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication, QMessageBox
from TirganachReloaded.cff_editor.data_model import CFFDataModel
from TirganachReloaded.cff_editor.widgets.icon_browser import IconBrowserDialog


def main():
    """Main entry point for icon browser"""
    app = QApplication(sys.argv)
    app.setApplicationName("SpellForce Icon Browser")
    app.setOrganizationName("SpellSmut Modding Tools")
    
    try:
        # Create data model
        data_model = CFFDataModel()
        
        # Create and show icon browser
        icon_browser = IconBrowserDialog(data_model, category="item")
        icon_browser.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to start icon browser:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()