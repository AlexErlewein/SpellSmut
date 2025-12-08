#!/usr/bin/env python3
"""
Simple test to check if the visual dialogue widget has the new methods
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_imports():
    """Test that we can import the visual dialogue widget"""
    try:
        print("Testing imports...")
        from TirganachReloaded.cff_editor.widgets.visual_dialogue_widget import (
            VisualDialogueWidget,
            VISUAL_EDITOR_COMPONENTS_AVAILABLE,
            NodeType,
        )

        print("✓ Imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_methods_exist():
    """Test that the new methods exist on the class"""
    try:
        print("Testing method existence...")
        from TirganachReloaded.cff_editor.widgets.visual_dialogue_widget import (
            VisualDialogueWidget,
        )

        # Check if the new methods exist
        methods_to_check = [
            "add_response_to_selected",
            "add_choice_to_selected",
            "update_toolbar_actions",
        ]

        for method_name in methods_to_check:
            if hasattr(VisualDialogueWidget, method_name):
                print(f"✓ Method {method_name} exists")
            else:
                print(f"✗ Method {method_name} missing")
                return False

        print("✓ All required methods exist")
        return True
    except Exception as e:
        print(f"✗ Method check failed: {e}")
        return False


def test_node_creation():
    """Test node creation logic without GUI"""
    try:
        print("Testing node creation logic...")
        from TirganachReloaded.cff_editor.widgets.visual_dialogue_widget import (
            DialogueNode,
            NodeType,
        )

        # Test creating a node
        node = DialogueNode(
            id="test_node",
            node_type=NodeType.NPC,
            speaker="Test NPC",
            text="Hello world",
            position=(100, 100),
        )

        print(f"✓ Created node: {node.id}, type: {node.node_type}")
        print(f"✓ Node has position: {node.position}")
        print(f"✓ Node has next_nodes: {node.next_nodes}")

        # Test to_dict method
        node_dict = node.to_dict()
        print(f"✓ Node to_dict: {node_dict}")

        return True
    except Exception as e:
        print(f"✗ Node creation test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Running simple visual dialogue widget tests...\n")

    tests = [
        test_imports,
        test_methods_exist,
        test_node_creation,
    ]

    results = []
    for test in tests:
        print(f"\n--- {test.__name__} ---")
        result = test()
        results.append(result)

    print("\n=== Test Results ===")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
