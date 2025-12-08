#!/usr/bin/env python3
"""
Quest Creator Launcher

This is the main launcher for the Quest Creator system.
It provides a comprehensive quest editor with visual dialogue creation capabilities,
including the new Text Mode Overview for dialogue trees.

Usage:
    # Using uv (recommended):
    uv run python quest_creator.py

    # Or directly with python (if dependencies are installed):
    python3 quest_creator.py
"""

import os
import sys
from pathlib import Path


def main():
    """Launch the Quest Creator"""
    print("🎯 Starting Quest Creator...")

    # Setup paths
    script_dir = Path(__file__).parent.resolve()
    src_dir = script_dir / "src"

    # Add to Python path (add src_dir first so imports work correctly)
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    try:
        # Import and launch the unified quest editor
        from TirganachReloaded.cff_editor.widgets.unified_quest_editor import (
            main as editor_main,
        )

        return editor_main()
    except ImportError as e:
        print(f"❌ Failed to import quest editor: {e}")
        print(f"   Script dir: {script_dir}")
        print(f"   Src dir: {src_dir}")
        print(f"   Python path: {sys.path[:3]}")
        print("\n💡 Make sure you have the required dependencies installed:")
        print("   uv add PySide6")
        import traceback

        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"❌ Failed to launch quest creator: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
