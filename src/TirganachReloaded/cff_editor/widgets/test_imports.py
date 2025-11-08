#!/usr/bin/env python3
"""
Test script to verify imports work correctly without GUI dependencies
"""

import sys
from pathlib import Path

# Set up path
script_path = Path(__file__).resolve()
# script_path is in: quest-wizard/src/TirganachReloaded/cff_editor/widgets/
# We need to go up 4 levels to reach src directory
# widgets -> cff_editor -> TirganachReloaded -> src
src_dir = script_path.parent.parent.parent.parent

print(f"Script path: {script_path}")
print(f"Calculated src_dir: {src_dir}")
print(f"Src dir exists: {src_dir.exists()}")
if src_dir.exists():
    print(f"TirganachReloaded exists in src: {(src_dir / 'TirganachReloaded').exists()}")

if src_dir.exists() and (src_dir / "TirganachReloaded").exists():
    sys.path.insert(0, str(src_dir))
    print(f"✓ Added to Python path: {src_dir}")
else:
    print(f"✗ Could not find valid src directory: {src_dir}")
    sys.exit(1)

def test_imports():
    """Test all the imports we need"""
    print("Testing imports...")

    # Test basic Python modules
    try:
        import json
        import re
        import os
        from pathlib import Path
        print("✓ Basic Python modules")
    except ImportError as e:
        print(f"✗ Basic Python modules: {e}")
        return False

    # Test CFF components
    try:
        from TirganachReloaded.cff_editor.data_model import CFFDataModel
        from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData, QuestReward, Dialogue, MapLocation
        print("✓ CFF Components")
    except ImportError as e:
        print(f"✗ CFF Components: {e}")
        return False

    # Test quest validator
    try:
        from TirganachReloaded.cff_editor.widgets.quest_validator import QuestValidator
        print("✓ Quest Validator")
    except ImportError as e:
        print(f"✗ Quest Validator: {e}")
        return False

    # Test Darius Almanach (for reference)
    try:
        sys.path.insert(0, str(src_dir / "DariusAlmanach"))
        from darius_almanach import SimpleQuestViewer
        print("✓ Darius Almanach")
    except ImportError as e:
        print(f"⚠ Darius Almanach (optional): {e}")

    return True

def test_data_structures():
    """Test creating data structures"""
    print("\nTesting data structures...")

    try:
        from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData, QuestReward, Dialogue, MapLocation

        # Create test quest
        quest = EnhancedQuestData(
            quest_id=9001,
            name="Test Quest",
            description="A test quest for validation",
            parent_id=0,
            order_index=0
        )

        # Add location
        quest.map_locations.append(MapLocation(code="P1", name="Liannon"))

        # Add dialogue
        quest.dialogues.append(Dialogue(text="Hello, adventurer!", speaker="NPC"))

        # Add rewards
        quest.rewards = QuestReward(xp=100, gold=10)

        print("✓ Created EnhancedQuestData successfully")
        print(f"  - Quest ID: {quest.quest_id}")
        print(f"  - Name: {quest.name}")
        print(f"  - Locations: {len(quest.map_locations)}")
        print(f"  - Dialogues: {len(quest.dialogues)}")
        print(f"  - Rewards: XP={quest.rewards.xp}, Gold={quest.rewards.gold}")

        return True

    except Exception as e:
        print(f"✗ Data structure test failed: {e}")
        return False

def test_validator():
    """Test quest validation"""
    print("\nTesting quest validation...")

    try:
        from TirganachReloaded.cff_editor.widgets.quest_validator import QuestValidator
        from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData, QuestReward, Dialogue, MapLocation

        # Create test quest
        quest = EnhancedQuestData(
            quest_id=9001,
            name="Test Validation Quest",
            description="A quest for testing validation",
            parent_id=0,
            order_index=0
        )

        quest.map_locations.append(MapLocation(code="P1", name="Liannon"))
        quest.dialogues.append(Dialogue(text="Welcome!", speaker="NPC"))
        quest.rewards = QuestReward(xp=50, gold=5)

        # Validate
        validator = QuestValidator()
        result = validator.validate_quest_detailed(quest)

        print(f"✓ Validation completed")
        print(f"  - Valid: {result.is_valid}")
        print(f"  - Errors: {len(result.errors)}")
        print(f"  - Warnings: {len(result.warnings)}")

        if result.errors:
            print("  Errors:")
            for error in result.errors:
                print(f"    - {error.message}")

        if result.warnings:
            print("  Warnings:")
            for warning in result.warnings:
                print(f"    - {warning.message}")

        return True

    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Quest Editor Component Test ===")

    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return 1

    # Test data structures
    if not test_data_structures():
        print("\n❌ Data structure tests failed")
        return 1

    # Test validation
    if not test_validator():
        print("\n❌ Validation tests failed")
        return 1

    print("\n✅ All tests passed!")
    print("\nThe quest editor components are working correctly.")
    print("To run the full GUI editor, install PySide6:")
    print("pip install PySide6")

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