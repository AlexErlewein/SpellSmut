#!/usr/bin/env python3
"""Quick test to verify quest editor can be launched"""

import sys
from pathlib import Path

# Setup paths
script_dir = Path(__file__).parent.resolve()
src_dir = script_dir / "src"

if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    print("Testing imports...")
    from TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview import TextModeDialogueOverview
    print("✅ TextModeDialogueOverview imported successfully")
    
    from TirganachReloaded.cff_editor.widgets.unified_quest_editor import UnifiedQuestEditor
    print("✅ UnifiedQuestEditor imported successfully")
    
    print("\n✅ All imports successful! You can launch the quest editor with:")
    print("   uv run python quest_creator.py")
    print("   or")
    print("   python3 quest_creator.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

