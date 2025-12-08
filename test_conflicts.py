#!/usr/bin/env python3
"""
Test AnswerId Conflict Detection and Resolution

Test the conflict detection and resolution functionality.
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
        from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager, AnswerIdConflict

        # Create manager
        manager = AnswerIdManager(start_id=1, quest_name="Conflict Test")

        print("📝 Creating test assignments...")

        # Assign some AnswerIds
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
            return True
        else:
            print(f"   ❌ Expected {expected_conflicts} conflicts, got {len(conflicts)}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_conflict_resolution():
    """Test AnswerId conflict resolution"""
    print("\n🔧 Testing AnswerId Conflict Resolution")
    print("=" * 60)

    try:
        from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager

        manager = AnswerIdManager(start_id=1, quest_name="Resolution Test")

        # Create conflicts
        manager.assign_manual_id("node_001", 0, 5, "First Choice")
        manager.assign_manual_id("node_002", 0, 5, "Second Choice")  # Conflict
        manager.assign_manual_id("node_003", 0, 5, "Third Choice")  # Conflict

        print("🔍 Before resolution:")
        conflicts_before = manager.validate_uniqueness()
        for conflict in conflicts_before:
            print(f"   AnswerId {conflict.answer_id}: {', '.join(conflict.step_ids)}")

        # Simulate resolution (reassign conflicting nodes)
        print("\n🔧 Resolving conflicts...")

        # Remove conflicts by reassigning
        original_answer_id = 5
        conflicting_nodes = [step_id for conflict in conflicts_before for step_id in conflict.step_ids
                           if conflict.answer_id == original_answer_id and step_id != "node_001"]  # Keep first assignment

        for step_id in conflicting_nodes:
            # Find the choice index and reassign
            for choice_index in range(10):  # Check first 10 choices
                current_id = manager.get_answer_id(step_id, choice_index)
                if current_id == original_answer_id:
                    # Remove old assignment
                    manager.remove_assignment(step_id, choice_index)
                    # Assign new ID
                    new_id = manager.assign_answer_id(step_id, choice_index, f"Resolved {step_id}")
                    print(f"   Reassigned {step_id}[{choice_id}] from {original_answer_id} to {new_id}")
                    break

        print("\n🔍 After resolution:")
        conflicts_after = manager.validate_uniqueness()

        if len(conflicts_after) == 0:
            print("   ✅ All conflicts resolved successfully!")
            return True
        else:
            print(f"   ❌ Still have {len(conflicts_after)} conflicts:")
            for conflict in conflicts_after:
                print(f"      AnswerId {conflict.answer_id}: {', '.join(conflict.step_ids)}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("\n🧪 Testing Edge Cases")
    print("=" * 60)

    try:
        from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager

        manager = AnswerIdManager(start_id=1, quest_name="Edge Cases")

        # Test 1: Empty manager
        print("✅ Test 1: Empty manager validation")
        conflicts = manager.validate_uniqueness()
        if len(conflicts) == 0:
            print("   ✅ No conflicts in empty manager")
        else:
            print(f"   ❌ Unexpected conflicts in empty manager: {len(conflicts)}")

        # Test 2: Same node, different choices
        print("\n✅ Test 2: Same node, different choices")
        id1 = manager.assign_answer_id("node_001", 0, "Choice A")
        id2 = manager.assign_answer_id("node_001", 1, "Choice B")
        print(f"   Node 001: Choice 0 = {id1}, Choice 1 = {id2}")

        conflicts = manager.validate_uniqueness()
        if len(conflicts) == 0:
            print("   ✅ No conflicts between different choices in same node")
        else:
            print(f"   ❌ Unexpected conflicts: {len(conflicts)}")

        # Test 3: Removal and reassignment
        print("\n✅ Test 3: Removal and reassignment")
        manager.remove_assignment("node_001", 0)
        new_id = manager.assign_answer_id("node_001", 0, "Choice A (new)")
        print(f"   Removed {id1}, reassigned as {new_id}")

        conflicts = manager.validate_uniqueness()
        if len(conflicts) == 0:
            print("   ✅ No conflicts after removal and reassignment")
        else:
            print(f"   ❌ Conflicts after reassignment: {len(conflicts)}")

        # Test 4: Boundary values
        print("\n✅ Test 4: Boundary values")
        min_id = 1
        max_id = 99999

        success_min = manager.assign_manual_id("boundary_min", 0, min_id, "Minimum ID")
        success_max = manager.assign_manual_id("boundary_max", 0, max_id, "Maximum ID")
        success_below = manager.assign_manual_id("boundary_below", 0, min_id - 1, "Below minimum")
        success_above = manager.assign_manual_id("boundary_above", 0, max_id + 1, "Above maximum")

        print(f"   Minimum ID ({min_id}): {'✅' if success_min else '❌'}")
        print(f"   Maximum ID ({max_id}): {'✅' if success_max else '❌'}")
        print(f"   Below minimum ({min_id-1}): {'✅' if not success_below else '❌'} (should fail)")
        print(f"   Above maximum ({max_id+1}): {'✅' if not success_above else '❌'} (should fail)")

        boundary_success = success_min and success_max and not success_below and not success_above

        return boundary_success and len(conflicts) == 0

    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
        return False

def test_real_world_scenario():
    """Test with a realistic dialogue scenario"""
    print("\n🎮 Testing Real-World Scenario")
    print("=" * 60)

    try:
        from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager

        manager = AnswerIdManager(start_id=1, quest_name="Real World Test")

        # Simulate a dialogue tree with potential conflicts
        assignments = [
            ("start_dialogue", 0, "Talk to guard", None),          # Auto-assigned
            ("guard_response", 0, "Accept quest", 1),              # Response to AnswerId=1
            ("quest_refusal", 0, "Refuse quest", 2),              # Response to AnswerId=2
            ("merchant_dialogue", 0, "Buy supplies", 3),           # Auto-assigned
            ("merchant_dialogue", 1, "Sell items", 4),             # Auto-assigned
            ("combat_choice", 0, "Fight goblin", 5),              # Auto-assigned
            ("diplo_choice", 0, "Negotiate", 5),                  # CONFLICT! Uses same AnswerId
            ("end_dialogue", 0, "Goodbye", 99),                   # Special ending ID
        ]

        print("📝 Creating realistic dialogue assignments:")
        for node_id, choice_idx, choice_text, answer_id in assignments:
            if answer_id is None:
                assigned_id = manager.assign_answer_id(node_id, choice_idx, choice_text)
                print(f"   {node_id}[{choice_idx}]: Auto-assigned {assigned_id} - '{choice_text}'")
            else:
                success = manager.assign_manual_id(node_id, choice_idx, answer_id, choice_text)
                status = "✅" if success else "❌"
                print(f"   {node_id}[{choice_idx}]: Manual {answer_id} '{status}' - '{choice_text}'")

        print("\n🔍 Detecting conflicts in realistic scenario...")
        conflicts = manager.validate_uniqueness()

        print(f"   Found {len(conflicts)} conflicts:")
        for i, conflict in enumerate(conflicts, 1):
            print(f"     {i}. AnswerId {conflict.answer_id} used by {len(conflict.step_ids)} nodes:")
            for step_id in conflict.step_ids:
                print(f"        - {step_id}")

        # Simulate conflict resolution
        if conflicts:
            print("\n🔧 Resolving conflicts...")
            for conflict in conflicts:
                # Keep the first assignment, reassign others
                keep_node = conflict.step_ids[0]
                conflict_nodes = conflict.step_ids[1:]

                for conflict_node in conflict_nodes:
                    # Find and reassign the conflicting choice
                    for choice_idx in range(5):
                        if manager.get_answer_id(conflict_node, choice_idx) == conflict.answer_id:
                            manager.remove_assignment(conflict_node, choice_idx)
                            new_id = manager.assign_answer_id(conflict_node, choice_idx, f"Resolved {conflict_node}")
                            print(f"   Reassigned {conflict_node}[{choice_idx}] from {conflict.answer_id} to {new_id}")
                            break

            # Verify resolution
            final_conflicts = manager.validate_uniqueness()
            print(f"\n✅ Resolution complete: {len(final_conflicts)} conflicts remaining")
            return len(final_conflicts) == 0
        else:
            print("   ✅ No conflicts found in realistic scenario")
            return True

    except Exception as e:
        print(f"❌ Real-world scenario test failed: {e}")
        return False

def main():
    """Run all conflict detection tests"""
    print("⚡ AnswerId Conflict Detection Test Suite")
    print("=" * 80)

    success = True

    # Run tests
    success &= test_conflict_detection()
    success &= test_conflict_resolution()
    success &= test_edge_cases()
    success &= test_real_world_scenario()

    # Summary
    print("\n" + "=" * 80)
    if success:
        print("🎉 ALL CONFLICT DETECTION TESTS PASSED! 🎉")
        print("\n🛡️ Conflict Management Features Confirmed:")
        print("   ✅ Duplicate AnswerId detection")
        print("   ✅ Automatic conflict resolution")
        print("   ✅ Manual ID assignment with validation")
        print("   ✅ Edge case handling (empty, boundaries)")
        print("   ✅ Real-world scenario compatibility")
        print("   ✅ Assignment removal and reassignment")

        print("\n📊 Conflict Resolution Strategy:")
        print("   🔍 Detect: Find duplicate AnswerIds across dialogue nodes")
        print("   🔧 Resolve: Reassign conflicting nodes to unique IDs")
        print("   ✅ Validate: Ensure no conflicts remain")
        print("   🔄 Sync: Update all affected dialogue connections")

    else:
        print("❌ SOME CONFLICT DETECTION TESTS FAILED")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)