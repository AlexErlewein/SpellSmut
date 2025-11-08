#!/usr/bin/env python3
"""
Test imports specifically for the unified quest editor
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

def test_unified_editor_imports():
    """Test imports from unified quest editor"""
    print("Testing unified quest editor imports...")

    # Test Qt imports
    try:
        print("  - Importing QtWidgets...")
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QTabWidget, QSplitter, QTreeWidget, QTreeWidgetItem, QTextEdit,
            QLineEdit, QSpinBox, QComboBox, QPushButton, QLabel, QGroupBox,
            QFormLayout, QListWidget, QListWidgetItem, QMessageBox, QProgressBar,
            QStatusBar, QMenuBar, QToolBar, QDialog, QDialogButtonBox,
            QCheckBox, QRadioButton, QButtonGroup, QFrame, QScrollArea,
            QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
        )
        print("    ✓ All QtWidgets imported successfully")
        print(f"    ✓ QFormLayout: {QFormLayout}")
    except ImportError as e:
        print(f"    ❌ QtWidgets import failed: {e}")
        return False

    # Test QtCore imports
    try:
        from PySide6.QtCore import (
            Qt, Signal, Slot, QThread, QTimer, QSettings, QSize, QPoint,
            QSortFilterProxyModel, QItemSelectionModel
        )
        print("    ✓ QtCore imported successfully")
    except ImportError as e:
        print(f"    ❌ QtCore import failed: {e}")
        return False

    # Test QtGui imports
    try:
        from PySide6.QtGui import (
            QFont, QPixmap, QIcon, QAction, QKeySequence, QPalette,
            QColor, QTextCursor, QIntValidator
        )
        print("    ✓ QtGui imported successfully")
    except ImportError as e:
        print(f"    ❌ QtGui import failed: {e}")
        return False

    # Test CFF imports
    try:
        from TirganachReloaded.cff_editor.data_model import CFFDataModel
        from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData, QuestReward, Dialogue, MapLocation
        from TirganachReloaded.cff_editor.logging_config import configure_logging, get_logger
        print("    ✓ CFF components imported successfully")
    except ImportError as e:
        print(f"    ❌ CFF components import failed: {e}")
        return False

    # Test quest validator
    try:
        from TirganachReloaded.cff_editor.widgets.quest_validator import QuestValidator
        print("    ✓ Quest validator imported successfully")
    except ImportError as e:
        print(f"    ❌ Quest validator import failed: {e}")

    # Test dialogue editor (optional)
    try:
        from TirganachReloaded.cff_editor.widgets.dialogue_editor import DialogueTreeEditor
        print("    ✓ Dialogue editor imported successfully")
    except ImportError as e:
        print(f"    ⚠ Dialogue editor import failed (optional): {e}")

    return True

def main():
    """Main test function"""
    print("=== Unified Quest Editor Import Test ===")

    if not test_unified_editor_imports():
        print("\n❌ Import tests failed")
        return 1

    print("\n✅ All imports successful!")
    print("The unified quest editor should work correctly.")

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