#!/usr/bin/env python3
"""
Direct Quest Editor Launcher

Simple direct launcher that bypasses the complex launcher logic
"""

import sys
import os
from pathlib import Path

def main():
    """Direct launcher function"""
    print("=== Direct Quest Editor Launcher ===")

    # Set up path
    script_dir = Path(__file__).parent
    widgets_dir = script_dir / "src" / "TirganachReloaded" / "cff_editor" / "widgets"

    if not widgets_dir.exists():
        print(f"❌ Could not find widgets directory: {widgets_dir}")
        return 1

    # Add both the src directory and widgets directory to Python path
    src_dir = script_dir / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))
        print(f"✓ Added src to Python path: {src_dir}")

    sys.path.insert(0, str(widgets_dir))
    print(f"✓ Added widgets to Python path: {widgets_dir}")

    # Change to widgets directory
    os.chdir(widgets_dir)
    print(f"Changed to directory: {widgets_dir}")

    try:
        print("\nLaunching Unified Quest Editor...")

        # Direct import and run
        from unified_quest_editor import main as editor_main

        print("✓ Successfully imported unified quest editor")
        print("Starting GUI...")

        # Run the editor
        return editor_main()

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("\nDebugging info:")
        print(f"Current directory: {Path.cwd()}")
        print(f"Python path:")
        for i, p in enumerate(sys.path[:5]):
            print(f"  {i}: {p}")
        return 1

    except Exception as e:
        print(f"❌ Failed to launch: {e}")
        import traceback
        traceback.print_exc()
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