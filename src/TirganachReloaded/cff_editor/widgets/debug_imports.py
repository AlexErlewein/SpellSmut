#!/usr/bin/env python3
"""
Debug script to test PySide6 imports
"""

import sys
from pathlib import Path

# Set up path
script_path = Path(__file__).resolve()
src_dir = script_path.parent.parent.parent.parent  # widgets -> cff_editor -> TirganachReloaded -> src

if src_dir.exists() and (src_dir / "TirganachReloaded").exists():
    sys.path.insert(0, str(src_dir))
    print(f"✓ Added to Python path: {src_dir}")
else:
    print(f"✗ Could not find valid src directory: {src_dir}")
    sys.exit(1)

def test_pyside6_imports():
    """Test PySide6 imports"""
    print("Testing PySide6 imports...")

    try:
        # Test core imports
        print("  - Importing QApplication...")
        from PySide6.QtWidgets import QApplication
        print("    ✓ QApplication")

        print("  - Importing QWidget...")
        from PySide6.QtWidgets import QWidget
        print("    ✓ QWidget")

        print("  - Importing QFormLayout...")
        from PySide6.QtWidgets import QFormLayout
        print("    ✓ QFormLayout")

        print("  - Importing other widgets...")
        from PySide6.QtWidgets import (
            QVBoxLayout, QHBoxLayout, QTabWidget, QSplitter, QTreeWidget,
            QTreeWidgetItem, QTextEdit, QLineEdit, QSpinBox, QComboBox,
            QPushButton, QLabel, QGroupBox, QListWidget, QListWidgetItem,
            QMessageBox, QProgressBar, QStatusBar, QMenuBar, QToolBar,
            QDialog, QDialogButtonBox, QCheckBox, QRadioButton, QButtonGroup,
            QFrame, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
            QAbstractItemView
        )
        print("    ✓ All widgets imported successfully")

        # Test core imports
        print("  - Importing QtCore...")
        from PySide6.QtCore import (
            Qt, Signal, Slot, QThread, QTimer, QSettings, QSize, QPoint
        )
        print("    ✓ QtCore imported successfully")

        # Test GUI imports
        print("  - Importing QtGui...")
        from PySide6.QtGui import (
            QFont, QPixmap, QIcon, QAction, QKeySequence, QPalette,
            QColor, QTextCursor, QIntValidator
        )
        print("    ✓ QtGui imported successfully")

        return True

    except ImportError as e:
        print(f"    ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"    ❌ Unexpected error: {e}")
        return False

def test_minimal_app():
    """Test creating a minimal Qt application"""
    print("\nTesting minimal Qt application...")

    try:
        from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

        # Create application (but don't show it)
        app = QApplication([])

        # Create a simple widget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Test Application"))

        print("  ✓ Minimal Qt application created successfully")

        # Clean up
        widget.deleteLater()
        app.quit()

        return True

    except Exception as e:
        print(f"  ❌ Failed to create Qt application: {e}")
        return False

def main():
    """Main test function"""
    print("=== PySide6 Import Debug ===")

    # Test imports
    if not test_pyside6_imports():
        print("\n❌ PySide6 import tests failed")
        return 1

    # Test minimal app
    if not test_minimal_app():
        print("\n❌ Qt application test failed")
        return 1

    print("\n✅ All PySide6 tests passed!")
    print("The Qt framework is working correctly.")

    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)