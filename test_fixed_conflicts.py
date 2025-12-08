#!/usr/bin/env python3
"""
Test Fixed AnswerId Conflict Detection and Resolution

Test the updated conflict detection and resolution functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_conflict_detection():
    """Test AnswerId conflict detection"""
    print("⚠️  Testing AnswerId Conflict Detection")
    print("=" * 60)

    try:
        from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager

        manager = AnswerIdManager(start_id=1, quest_name="Conflict Test")

        print("📝 Creating test assignments...")

        # Create assignments with conflicts
        manager.assign_answer_id("node_001", 0, "Choice A")  # Should get 1
        manager.assign_answer_id("node_002", 0, "Choice B")  # Should get 2
        manager.assign_manual_id("node_003", 0, 1, "Conflict Choice")  # Conflict with node_001

        print(f"   Assigned: node_001[0] = {manager.get_answer_id('node_001', 0)}")
        print(f"   Assigned: node_002[0] = {manager.get_answer_id('node_002', 0)}")
        print(f"   Assigned: node_003[0] = {manager.get_answer_id('node_003', 0)}")

        # Test conflict detection
        print("\n🔍 Running conflict detection...")
        conflicts = manager.validate_uniqueness()

        print(f"   Found {len(conflicts)} conflicts:")
        for i, conflict in enumerate(conflicts, 1):
            print(f"     {i}. AnswerId {conflict.answer_id} used by {len(conflict.step_ids)} nodes:")
            for step_id in conflict.step_ids:
                print(f"        - {step_id}")

        # Verify expected conflict
        expected_conflicts = 1  # AnswerId 1 should be in conflict
        if len(conflicts) == expected_conflicts:
            print(f"   ✅ Correctly detected {expected_conflicts} conflict(s)")
            return True, conflicts
        else:
            print(f"   ❌ Expected {expected_conflicts} conflicts, got {len(conflicts)}")
            return False, []

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False, []

def test_conflict_resolution():
    """Test AnswerId conflict resolution"""
    print("\n🔧 Testing AnswerId Conflict Resolution")
    print("=" * 60)

    try:
        from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager

        manager = AnswerIdManager(start_id=1, quest_name="Resolution Test")

        print("📝 Creating conflicts...")
        # Create conflicts
        manager.assign_manual_id("node_001", 0, 5, "First Choice")
        manager.assign_manual_id("node_002", 0, 5, "Second Choice")  # Conflict
        manager.assign_manual_id("node_003", 0, 5, "Third Choice")  # Conflict

        print("🔍 Before resolution:")
        conflicts_before = manager.validate_uniqueness()
        for conflict in conflicts_before:
            print(f"   AnswerId {conflict.answer_id}: {', '.join(conflict.step_ids)}")

        print(f"\n🔧 Resolving conflicts (strategy: keep_first)...")
        resolved_count = manager.resolve_conflicts("keep_first")
        print(f"   Resolved {resolved_count} assignments")

        print("\n🔍 After resolution:")
        conflicts_after = manager.validate_uniqueness()

        print(f"   Remaining conflicts: {len(conflicts_after)}")
        if len(conflicts_after) == 0:
            print("   ✅ All conflicts resolved successfully!")

            # Show final assignments
            print("\n📊 Final assignments:")
            for step_id, assignments in manager.assignments.items():
                for assignment in assignments:
                    print(f"   {step_id}[{assignment.choice_index}] = {assignment.answer_id}")

            return True
        else:
            print(f"   ❌ Still have {len(conflicts_after)} conflicts:")
            for conflict in conflicts_after:
                print(f"      AnswerId {conflict.answer_id}: {', '.join(conflict.step_ids)}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_resolution_strategies():
    """Test different conflict resolution strategies"""
    print("\n🎯 Testing Resolution Strategies")
    print("=" * 60)

    strategies = ["keep_first", "keep_last", "reassign_all"]
    results = {}

    for strategy in strategies:
        print(f"\n📝 Testing '{strategy}' strategy...")

        try:
            from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager

            manager = AnswerIdManager(start_id=100, quest_name=f"{strategy.title()} Test")

            # Create the same conflicts for each test
            manager.assign_manual_id("node_A", 0, 10, "Choice A")
            manager.assign_manual_id("node_B", 0, 10, "Choice B")
            manager.assign_manual_id("node_C", 0, 10, "Choice C")

            # Show before state
            conflicts_before = manager.validate_uniqueness()
            print(f"   Before: {len(conflicts_before)} conflicts")

            # Resolve conflicts
            resolved_count = manager.resolve_conflicts(strategy)
            print(f"   Resolved: {resolved_count} assignments")

            # Check after state
            conflicts_after = manager.validate_uniqueness()
            print(f"   After: {len(conflicts_after)} conflicts")

            success = len(conflicts_after) == 0
            results[strategy] = {
                "success": success,
                "resolved": resolved_count,
                "final_conflicts": len(conflicts_after)
            }

            if success:
                print(f"   ✅ {strategy.title()} strategy successful")
            else:
                print(f"   ❌ {strategy.title()} strategy failed")

        except Exception as e:
            print(f"   ❌ {strategy} test failed: {e}")
            results[strategy] = {"success": False, "error": str(e)}

    # Summary
    print(f"\n📊 Strategy Test Summary:")
    for strategy, result in results.items():
        if result.get("success"):
            print(f"   ✅ {strategy.title()}: Resolved {result.get('resolved', 0)} assignments")
        else:
            print(f"   ❌ {strategy.title()}: Failed ({result.get('error', 'Unknown error')})")

    return all(result.get("success", False) for result in results.values())

def test_real_world_workflow():
    """Test a realistic workflow with conflict detection and resolution"""
    print("\n🎮 Testing Real-World Workflow")
    print("=" * 60)

    try:
        from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager

        manager = AnswerIdManager(start_id=1, quest_name="Real World Test")

        print("📋 Step 1: Simulate user creating dialogue with manual AnswerIds")

        # User creates dialogue and manually assigns some AnswerIds
        assignments = [
            ("start_dialogue", 0, "Hello", 1),
            ("npc_greeting", 0, "Greetings!", None),  # Auto-assign
            ("player_choices", 0, "Ask quest", 2),
            ("player_choices", 1, "Just looking", 3),
            ("quest_accept", 0, "Sure!", 2),  # Conflict with player_choices[0]
            ("quest_refuse", 0, "Maybe later", 3),  # Conflict with player_choices[1]
            ("merchant", 0, "Buy items", 4),
            ("ending", 0, "Goodbye", 99)
        ]

        for node_id, choice_idx, text, answer_id in assignments:
            if answer_id is None:
                assigned_id = manager.assign_answer_id(node_id, choice_idx, text)
                print(f"   Auto-assigned: {node_id}[{choice_idx}] = {assigned_id}")
            else:
                success = manager.assign_manual_id(node_id, choice_idx, answer_id, text)
                print(f"   Manual: {node_id}[{choice_idx}] = {answer_id} {'✅' if success else '❌'}")

        print("\n🔍 Step 2: Detect conflicts")
        conflicts = manager.validate_uniqueness()
        print(f"   Found {len(conflicts)} conflicts:")

        for i, conflict in enumerate(conflicts, 1):
            print(f"     {i}. AnswerId {conflict.answer_id}: {', '.join(conflict.step_ids)}")

        print("\n🔧 Step 3: Resolve conflicts automatically")
        if conflicts:
            resolved_count = manager.resolve_conflicts("keep_first")
            print(f"   Resolved {resolved_count} conflicting assignments")
        else:
            print("   No conflicts to resolve")

        print("\n✅ Step 4: Verify no conflicts remain")
        final_conflicts = manager.validate_uniqueness()

        if len(final_conflicts) == 0:
            print("   ✅ All conflicts resolved!")

            print("\n📊 Final AnswerId assignments:")
            for step_id, assignments in sorted(manager.assignments.items()):
                for assignment in assignments:
                    auto_text = "Auto" if assignment.auto_assigned else "Manual"
                    print(f"   {step_id}[{assignment.choice_index}] = {assignment.answer_id} ({auto_text})")

            return True
        else:
            print(f"   ❌ Still have {len(final_conflicts)} conflicts")
            return False

    except Exception as e:
        print(f"❌ Real-world test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all conflict detection and resolution tests"""
    print("⚡ Fixed AnswerId Conflict Detection & Resolution Test Suite")
    print("=" * 80)

    success = True

    # Run tests
    detection_success, conflicts = test_conflict_detection()
    success &= detection_success

    success &= test_conflict_resolution()
    success &= test_resolution_strategies()
    success &= test_real_world_workflow()

    # Summary
    print("\n" + "=" * 80)
    if success:
        print("🎉 ALL CONFLICT TESTS PASSED! 🎉")
        print("\n✅ Fixed Conflict Management Features:")
        print("   ✅ Conflict detection now works correctly")
        print("   ✅ Manual assignment allows duplicates for detection")
        print("   ✅ Three resolution strategies implemented:")
        print("       - keep_first: Keep first assignment, reassign others")
        print("       - keep_last: Keep last assignment, reassign others")
        print("       - reassign_all: Reassign all conflicting assignments")
        print("   ✅ Automatic conflict resolution with user choice")
        print("   ✅ Real-world workflow compatibility")

        print("\n🔧 Conflict Resolution Workflow:")
        print("   1. Allow duplicate AnswerId assignments")
        print("   2. Detect conflicts using validate_uniqueness()")
        print("   3. Present resolution options to user")
        print("   4. Resolve using chosen strategy")
        print("   5. Update dialogue data accordingly")

    else:
        print("❌ SOME CONFLICT TESTS FAILED")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)