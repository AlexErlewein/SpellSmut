#!/usr/bin/env python3
"""
Test AnswerId Assignment and Editing Workflow

Test the complete workflow of assigning and editing AnswerIds in dialogue.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_assignment_workflow():
    """Test the basic AnswerId assignment workflow"""
    print("🔄 Testing Basic Assignment Workflow")
    print("=" * 60)

    try:
        from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager

        manager = AnswerIdManager(start_id=1, quest_name="Workflow Test")

        print("📝 Step 1: Create dialogue nodes")
        dialogue_data = {
            "nodes": [
                {
                    "id": "npc_guard",
                    "node_type": "npc",
                    "speaker": "Guard",
                    "text": "Halt! Who goes there?",
                    "choices": [
                        {"text": "I'm a traveler.", "answer_id": None},
                        {"text": "None of your business.", "answer_id": None},
                        {"text": "[Show pass]", "answer_id": None}
                    ]
                },
                {
                    "id": "guard_response",
                    "node_type": "npc",
                    "speaker": "Guard",
                    "text": "State your business.",
                    "answer_id": 1  # Response to choice with AnswerId=1
                }
            ]
        }

        print(f"   Created {len(dialogue_data['nodes'])} dialogue nodes")

        print("\n🏷️ Step 2: Assign AnswerIds to choices")
        for node in dialogue_data["nodes"]:
            node_id = node["id"]
            choices = node.get("choices", [])

            for i, choice in enumerate(choices):
                if choice.get("answer_id") is None:
                    # Auto-assign AnswerId
                    answer_id = manager.assign_answer_id(node_id, i, choice["text"])
                    choice["answer_id"] = answer_id
                    print(f"   {node_id}[{i}]: Assigned AnswerId {answer_id} - '{choice['text'][:30]}...'")

        print("\n📊 Step 3: Assignment Summary")
        for step_id, assignments in manager.assignments.items():
            print(f"   Node {step_id}:")
            for assignment in assignments:
                print(f"     Choice {assignment.choice_index}: AnswerId {assignment.answer_id}")

        print("\n✅ Step 4: Validate assignments")
        conflicts = manager.validate_uniqueness()
        if len(conflicts) == 0:
            print("   ✅ No conflicts detected")
        else:
            print(f"   ⚠️  Found {len(conflicts)} conflicts")

        print("\n🔗 Step 5: Update dialogue data")
        updated_nodes = 0
        for node in dialogue_data["nodes"]:
            for i, choice in enumerate(node.get("choices", [])):
                if choice.get("answer_id") is not None:
                    updated_nodes += 1

        print(f"   Updated {updated_nodes} choices with AnswerIds")

        return len(conflicts) == 0 and updated_nodes > 0

    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def test_manual_assignment_workflow():
    """Test manual AnswerId assignment workflow"""
    print("\n✏️ Testing Manual Assignment Workflow")
    print("=" * 60)

    try:
        from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager

        manager = AnswerIdManager(start_id=100, quest_name="Manual Test")

        print("📋 Step 1: Define manual AnswerId plan")
        # AnswerId plan matching game conventions
        assignment_plan = [
            ("start_node", 0, "Begin dialogue", 1),      # Start dialogue
            ("npc_greeting", 0, "Friendly greeting", 10), # Response to AnswerId=1
            ("player_choice_1", 0, "Ask for quest", 2),   # First player choice
            ("player_choice_1", 1, "Just passing", 3),    # Second player choice
            ("quest_accept", 0, "Accept quest!", 2),      # Response to AnswerId=2
            ("quest_refuse", 0, "Maybe later", 3),       # Response to AnswerId=3
        ]

        print("   Planned assignments:")
        for node_id, choice_idx, choice_text, answer_id in assignment_plan:
            print(f"     {node_id}[{choice_idx}] = AnswerId {answer_id} ('{choice_text}')")

        print("\n✏️ Step 2: Execute manual assignments")
        successful_assignments = []
        failed_assignments = []

        for node_id, choice_idx, choice_text, answer_id in assignment_plan:
            success = manager.assign_manual_id(node_id, choice_idx, answer_id, choice_text)
            if success:
                successful_assignments.append((node_id, choice_idx, answer_id))
                print(f"   ✅ {node_id}[{choice_idx}] = {answer_id}")
            else:
                failed_assignments.append((node_id, choice_idx, answer_id))
                print(f"   ❌ {node_id}[{choice_idx}] = {answer_id} (conflict)")

        print("\n🔍 Step 3: Validate manual assignments")
        conflicts = manager.validate_uniqueness()
        print(f"   Found {len(conflicts)} conflicts")

        print("\n📊 Step 4: Assignment results")
        print(f"   Successful: {len(successful_assignments)}")
        print(f"   Failed: {len(failed_assignments)}")
        print(f"   Conflicts: {len(conflicts)}")

        return len(failed_assignments) == 0  # Should have no failed assignments in this test

    except Exception as e:
        print(f"❌ Manual assignment test failed: {e}")
        return False

def test_editing_workflow():
    """Test editing existing AnswerId assignments"""
    print("\n✏️ Testing Editing Workflow")
    print("=" * 60)

    try:
        from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager

        manager = AnswerIdManager(start_id=1, quest_name="Editing Test")

        print("📝 Step 1: Create initial assignments")
        # Create some initial assignments
        initial_assignments = [
            ("dialogue_001", 0, "Hello", 1),
            ("dialogue_001", 1, "Goodbye", 2),
            ("dialogue_002", 0, "Response to hello", 1),
            ("dialogue_003", 0, "Response to goodbye", 2)
        ]

        for node_id, choice_idx, text, answer_id in initial_assignments:
            manager.assign_manual_id(node_id, choice_idx, answer_id, text)

        print("   Initial assignments created")

        print("\n✏️ Step 2: Edit an assignment")
        # Change AnswerId for dialogue_003 from 2 to 3
        old_answer_id = manager.get_answer_id("dialogue_003", 0)
        print(f"   Current: dialogue_003[0] = {old_answer_id}")

        # Remove old assignment
        manager.remove_assignment("dialogue_003", 0)
        # Assign new AnswerId
        new_answer_id = manager.assign_manual_id("dialogue_003", 0, 3, "Response to goodbye (updated)")
        print(f"   Updated: dialogue_003[0] = {new_answer_id}")

        print("\n🔍 Step 3: Validate after edit")
        conflicts = manager.validate_uniqueness()
        print(f"   Conflicts after edit: {len(conflicts)}")

        print("\n📊 Step 4: Verify assignment chain")
        assignments_to_check = [
            ("dialogue_001", 0, 1),
            ("dialogue_001", 1, 2),
            ("dialogue_002", 0, 1),
            ("dialogue_003", 0, 3)  # This should be the changed one
        ]

        all_correct = True
        for node_id, choice_idx, expected_answer_id in assignments_to_check:
            actual_answer_id = manager.get_answer_id(node_id, choice_idx)
            if actual_answer_id == expected_answer_id:
                print(f"   ✅ {node_id}[{choice_idx}] = {actual_answer_id}")
            else:
                print(f"   ❌ {node_id}[{choice_idx}] = {actual_answer_id} (expected {expected_answer_id})")
                all_correct = False

        return len(conflicts) == 0 and all_correct

    except Exception as e:
        print(f"❌ Editing workflow test failed: {e}")
        return False

def test_integration_with_dialogue_data():
    """Test integration with dialogue data format"""
    print("\n🔗 Testing Integration with Dialogue Data")
    print("=" * 60)

    try:
        from TirganachReloaded.cff_editor.widgets.answer_id_manager import AnswerIdManager

        manager = AnswerIdManager(start_id=1, quest_name="Integration Test")

        # Sample dialogue data in the format used by the editor
        dialogue_data = {
            "nodes": [
                {
                    "id": "start_dialogue",
                    "node_type": "start",
                    "text": "Dialogue begins",
                    "choices": []
                },
                {
                    "id": "npc_merchant",
                    "node_type": "npc",
                    "speaker": "Merchant",
                    "text": "Welcome to my shop!",
                    "choices": [
                        {"text": "What do you sell?", "answer_id": None},
                        {"text": "I'm just looking.", "answer_id": None}
                    ]
                },
                {
                    "id": "merchant_wares",
                    "node_type": "npc",
                    "speaker": "Merchant",
                    "text": "I have weapons and armor.",
                    "answer_id": 1  # Response to AnswerId=1
                },
                {
                    "id": "merchant_goodbye",
                    "node_type": "npc",
                    "speaker": "Merchant",
                    "text": "Come back anytime!",
                    "answer_id": 2  # Response to AnswerId=2
                }
            ],
            "connections": [
                {"from": "start_dialogue", "to": "npc_merchant"},
                {"from": "npc_merchant", "to": "merchant_wares"},
                {"from": "npc_merchant", "to": "merchant_goodbye"}
            ]
        }

        print("📋 Step 1: Process dialogue data")
        total_choices = 0
        unassigned_choices = 0

        for node in dialogue_data["nodes"]:
            choices = node.get("choices", [])
            total_choices += len(choices)
            unassigned += sum(1 for choice in choices if choice.get("answer_id") is None)

        print(f"   Total choices: {total_choices}")
        print(f"   Unassigned choices: {unassigned}")

        print("\n🏷️ Step 2: Auto-assign missing AnswerIds")
        assigned_count = 0

        for node in dialogue_data["nodes"]:
            node_id = node["id"]
            choices = node.get("choices", [])

            for i, choice in enumerate(choices):
                if choice.get("answer_id") is None:
                    answer_id = manager.assign_answer_id(node_id, i, choice["text"])
                    choice["answer_id"] = answer_id
                    assigned_count += 1
                    print(f"   {node_id}[{i}]: Assigned {answer_id} - '{choice['text'][:25]}...'")

        print(f"\n✅ Step 3: Assignment complete")
        print(f"   Assigned {assigned_count} AnswerIds")

        print("\n🔗 Step 4: Update connections based on AnswerIds")
        # In a real system, we would update connections to match AnswerId responses
        print("   Connection mapping:")
        for node in dialogue_data["nodes"]:
            node_answer_id = node.get("answer_id")
            if node_answer_id is not None:
                print(f"     Node '{node['id']}' responds to AnswerId {node_answer_id}")

        print("\n📊 Step 5: Final validation")
        conflicts = manager.validate_uniqueness()
        if len(conflicts) == 0:
            print("   ✅ All AnswerIds are unique")
        else:
            print(f"   ⚠️  Found {len(conflicts)} conflicts")

        print("\n💾 Step 6: Export updated dialogue data")
        # Show the updated dialogue data with AnswerIds
        print("   Updated nodes:")
        for node in dialogue_data["nodes"]:
            node_id = node["id"]
            if node.get("answer_id") is not None:
                print(f"     {node_id}: [AnswerId={node['answer_id']}] '{node.get('text', '')[:30]}...'")
            else:
                choices = node.get("choices", [])
                for i, choice in enumerate(choices):
                    if choice.get("answer_id") is not None:
                        print(f"     {node_id}[{i}]: [AnswerId={choice['answer_id']}] '{choice['text'][:25]}...'")

        return len(conflicts) == 0 and assigned_count > 0

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all assignment workflow tests"""
    print("🔄 AnswerId Assignment Workflow Test Suite")
    print("=" * 80)

    success = True

    # Run tests
    success &= test_basic_assignment_workflow()
    success &= test_manual_assignment_workflow()
    success &= test_editing_workflow()
    success &= test_integration_with_dialogue_data()

    # Summary
    print("\n" + "=" * 80)
    if success:
        print("🎉 ALL ASSIGNMENT WORKFLOW TESTS PASSED! 🎉")
        print("\n✅ Workflow Features Confirmed:")
        print("   ✅ Basic auto-assignment of AnswerIds")
        print("   ✅ Manual AnswerId assignment")
        print("   ✅ Assignment editing and modification")
        print("   ✅ Integration with dialogue data format")
        print("   ✅ Conflict prevention and detection")
        print("   ✅ Validation and consistency checks")

        print("\n🔄 Complete Workflow:")
        print("   1. Load dialogue structure")
        print("   2. Auto-assign missing AnswerIds")
        print("   3. Manually adjust specific assignments")
        print("   4. Validate for conflicts")
        print("   5. Resolve any issues")
        print("   6. Export updated dialogue data")

    else:
        print("❌ SOME ASSIGNMENT WORKFLOW TESTS FAILED")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)