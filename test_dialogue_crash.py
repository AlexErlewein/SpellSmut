#!/usr/bin/env python3
"""
Test script to reproduce the dialogue node addition crash
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from PySide6.QtWidgets import QApplication
from TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview import (
    TextModeDialogueOverview,
)


def test_add_node_crash():
    """Test adding a node to reproduce the crash"""
    print("Testing dialogue node addition...")

    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    try:
        # Create the text mode dialogue overview widget
        widget = TextModeDialogueOverview()

        # Try to add a node programmatically (simulating the button click)
        print("Adding a test node...")

        # Create a simple node
        from TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview import (
            DialogueNodeData,
        )

        node = DialogueNodeData(
            id="test_node_1",
            node_type="npc",
            speaker="Test NPC",
            text="Hello, this is a test dialogue!",
        )

        # Add node to collection (simulating what on_add_node does)
        widget.nodes[node.id] = node

        # Emit signal (simulating what on_add_node does)
        widget.node_added.emit(node.id, node.to_dict())

        # Refresh view (simulating what on_add_node does)
        widget.refresh_view()

        print("Node added successfully!")

        # Try adding another node
        print("Adding a second test node...")
        node2 = DialogueNodeData(
            id="test_node_2", node_type="player", speaker="Player", text="Hello back!"
        )

        widget.nodes[node2.id] = node2
        widget.node_added.emit(node2.id, node2.to_dict())
        widget.refresh_view()

        print("Second node added successfully!")
        print("Test completed without crash!")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = test_add_node_crash()
    sys.exit(0 if success else 1)
