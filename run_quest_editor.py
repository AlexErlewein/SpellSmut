#!/usr/bin/env python3
"""
Simple wrapper to run the unified quest editor from the project root
"""

import sys
import os
from pathlib import Path

def main():
    # Change to the widgets directory
    script_dir = Path(__file__).parent
    widgets_dir = script_dir / "src" / "TirganachReloaded" / "cff_editor" / "widgets"

    if not widgets_dir.exists():
        print(f"❌ Could not find widgets directory: {widgets_dir}")
        return 1

    # Change to widgets directory
    os.chdir(widgets_dir)
    print(f"Changed to directory: {widgets_dir}")

    # Import and run the launcher
    try:
        # Add current directory to Python path
        current_dir = Path.cwd()
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

        from launch_unified_quest_editor import main as launcher_main
        return launcher_main()
    except Exception as e:
        print(f"❌ Failed to run launcher: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())