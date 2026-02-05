#!/usr/bin/env python3
"""
Standalone Allwissende Almacht Tool
==================================

A standalone tool to browse and view game icons and assets.
Run this script to launch Allwissende Almacht without the full CFF editor.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
# Current file is in src/AllwissendeAlmacht/run_allwissende_almacht.py
# src path is one level up
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication, QMessageBox
from TirganachReloaded.cff_editor.data_model import CFFDataModel
from AllwissendeAlmacht.allwissende_almacht import AllwissendeAlmachtDialog


def main():
    """Main entry point for Allwissende Almacht"""
    app = QApplication(sys.argv)
    app.setApplicationName("Allwissende Almacht")
    app.setOrganizationName("SpellSmut Modding Tools")
    
    try:
        # Create data model
        data_model = CFFDataModel()
        
        # Create and show Allwissende Almacht
        almacht_dialog = AllwissendeAlmachtDialog(data_model, category="item")
        almacht_dialog.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to start Allwissende Almacht:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()