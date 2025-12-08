#!/usr/bin/env python3
"""
Test script to reproduce the dialogue node addition crash in the full quest editor context
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from PySide6.QtWidgets import QApplication
from TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview import (
    TextModeDialogueOverview,
)
from TirganachReloaded.cff_editor.widgets.visual_dialogue_widget import (
    VisualDialogueWidget,
)


def test_full_integration():
    """Test the full integration between text mode and visual dialogue widgets"""
    print("Testing full dialogue widget integration...")

    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    try:
        # Create both widgets
        print("Creating text mode widget...")
        text_widget = TextModeDialogueOverview()

        print("Creating visual dialogue widget...")
        visual_widget = VisualDialogueWidget()

        # Connect the signal like the unified quest editor does
        text_widget.node_added.connect(
            lambda node_id, node_data: on_text_node_added(
                text_widget, visual_widget, node_id, node_data
            )
        )

        # Simulate adding a node through text mode
        print("Simulating node addition through text mode...")

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

        # Simulate what on_add_node does
        text_widget.nodes[node.id] = node
        text_widget.node_added.emit(node.id, node.to_dict())
        text_widget.refresh_view()

        print("Node added successfully through text mode!")

        # Try adding another node
        print("Adding a second test node...")
        node2 = DialogueNodeData(
            id="test_node_2", node_type="player", speaker="Player", text="Hello back!"
        )

        text_widget.nodes[node2.id] = node2
        text_widget.node_added.emit(node2.id, node2.to_dict())
        text_widget.refresh_view()

        print("Second node added successfully!")
        print("Full integration test completed without crash!")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def on_text_node_added(text_widget, visual_widget, node_id, node_data):
    """Simulate the _on_text_mode_node_added method from unified quest editor"""
    print(f"Syncing node {node_id} to visual widget...")

    # Sync to visual editor if available
    if visual_widget:
        dialogue_data = text_widget.get_dialogue_data()
        visual_widget.set_dialogue_data(dialogue_data)
        print(f"Synced node {node_id} to visual widget")


if __name__ == "__main__":
    success = test_full_integration()
    sys.exit(0 if success else 1)
