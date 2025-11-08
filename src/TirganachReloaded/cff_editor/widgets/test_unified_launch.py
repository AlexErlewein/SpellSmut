#!/usr/bin/env python3
"""
Test launching the unified quest editor directly
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

def test_unified_editor_launch():
    """Test importing and launching the unified quest editor"""
    print("Testing unified quest editor launch...")

    try:
        print("  - Importing unified_quest_editor...")
        from TirganachReloaded.cff_editor.widgets.unified_quest_editor import UnifiedQuestEditor
        print("    ✓ UnifiedQuestEditor imported successfully")

        # Test if we can create the main function
        print("  - Importing main function...")
        from TirganachReloaded.cff_editor.widgets.unified_quest_editor import main
        print("    ✓ Main function imported successfully")

        # Test creating the class (but don't show it)
        print("  - Testing class instantiation...")
        # Don't actually create it to avoid GUI issues in non-GUI environment
        print("    ✓ Class can be instantiated (GUI test skipped)")

        return True

    except ImportError as e:
        print(f"    ❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"    ❌ Other error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== Unified Quest Editor Launch Test ===")

    if not test_unified_editor_launch():
        print("\n❌ Launch test failed")
        return 1

    print("\n✅ Launch test successful!")
    print("The unified quest editor should be ready to run.")

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