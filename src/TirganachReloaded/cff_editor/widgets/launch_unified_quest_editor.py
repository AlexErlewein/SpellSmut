#!/usr/bin/env python3
"""
Unified Quest Editor Launcher

Simple launcher for the unified quest editor system.
This replaces all the fragmented launcher files with a single entry point.
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Fix path calculation
script_path = Path(__file__).resolve()
# script_path is in: quest-wizard/src/TirganachReloaded/cff_editor/widgets/
# We need to add quest-wizard/src to Python path
widgets_dir = script_path.parent
cff_editor_dir = widgets_dir.parent
tirganach_dir = cff_editor_dir.parent
src_dir = tirganach_dir.parent

# Alternative: Go up 4 levels from script to get to src directory
# widgets -> cff_editor -> TirganachReloaded -> src
src_dir_alt = script_path.parent.parent.parent

# Use whichever exists
if src_dir.exists() and (src_dir / "TirganachReloaded").exists():
    sys.path.insert(0, str(src_dir))
elif src_dir_alt.exists():
    sys.path.insert(0, str(src_dir_alt))
else:
    # Fallback: calculate from current working directory
    cwd = Path.cwd()
    if cwd.name == "widgets":
        # We're in the widgets directory
        calculated_src = cwd.parent.parent.parent
        if calculated_src.exists():
            sys.path.insert(0, str(calculated_src))

def check_dependencies() -> tuple[bool, list]:
    """Check if required dependencies are available"""
    missing = []

    # Check PySide6
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
    except ImportError as e:
        missing.append(f"PySide6: {e}")

    # Check CFF components
    try:
        from TirganachReloaded.cff_editor.data_model import CFFDataModel
        from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData
        from TirganachReloaded.cff_editor.logging_config import configure_logging
    except ImportError as e:
        missing.append(f"CFF Components: {e}")

    # Check optional components
    try:
        from TirganachReloaded.cff_editor.widgets.dialogue_editor import DialogueTreeEditor
    except ImportError:
        missing.append("Visual Dialogue Editor (optional - will use simple editor)")

    try:
        from TirganachReloaded.cff_editor.widgets.quest_validator import QuestValidator
    except ImportError:
        missing.append("Quest Validator (optional - validation limited)")

    return len(missing) == 0, missing

def main():
    """Main launcher function"""
    print("=== Unified Quest Editor Launcher ===")
    print(f"Script Path: {script_path}")
    print(f"Source Directory: {src_dir if 'src_dir' in locals() else 'Unknown'}")
    print()

    # Check dependencies
    deps_available, missing = check_dependencies()

    if not deps_available:
        print("⚠ Some dependencies are missing:")
        for dep in missing:
            print(f"   - {dep}")
        print()
        print("The editor will run with limited functionality.")
        print()
    else:
        print("✓ All dependencies are available.")
        print()

    # Try to import and launch the editor
    try:
        print("Launching Unified Quest Editor...")

        # Import here to check for import errors
        from TirganachReloaded.cff_editor.widgets.unified_quest_editor import main as editor_main

        # Run the editor
        return editor_main()

    except ImportError as e:
        print(f"❌ Failed to import the unified quest editor: {e}")
        print()
        print("This might be due to:")
        print("1. Missing PySide6 installation")
        print("2. Incorrect Python path setup")
        print("3. Missing source files")
        print()
        print("To install PySide6, run:")
        print("uv add PySide6")
        print("or: pip install PySide6")
        print()
        return 1

    except Exception as e:
        print(f"❌ Failed to launch the editor: {e}")
        print()
        print("Please check the error above and report if needed.")
        print()
        return 1

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