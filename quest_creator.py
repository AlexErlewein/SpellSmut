#!/usr/bin/env python3
"""
Quest Creator Launcher

This is the main launcher for the Quest Creator system.
It provides a comprehensive quest editor with visual dialogue creation capabilities.

Usage:
    python quest_creator.py
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the Quest Creator"""
    print("🎯 Starting Quest Creator...")

    # Setup paths
    script_dir = Path(__file__).parent
    src_dir = script_dir / "src"
    widgets_dir = src_dir / "TirganachReloaded" / "cff_editor" / "widgets"

    # Add to Python path
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    if str(widgets_dir) not in sys.path:
        sys.path.insert(0, str(widgets_dir))

    # Change to the working directory
    os.chdir(widgets_dir)

    try:
        # Import and launch the unified quest editor
        from unified_quest_editor import main as editor_main
        return editor_main()
    except ImportError as e:
        print(f"❌ Failed to import quest editor: {e}")
        print("\n💡 Make sure you have the required dependencies installed:")
        print("   uv add PySide6")
        return 1
    except Exception as e:
        print(f"❌ Failed to launch quest creator: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())