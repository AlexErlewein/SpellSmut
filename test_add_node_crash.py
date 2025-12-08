#!/usr/bin/env python3
"""
Test script to reproduce the crash when adding a dialogue node in the quest editor
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


def test_add_node_crash():
    """Test adding a node to reproduce the crash"""
    print("Testing dialogue node addition crash...")

    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    try:
        # Create both widgets
        print("Creating text mode dialogue overview widget...")
        text_mode_widget = TextModeDialogueOverview()

        print("Creating visual dialogue widget...")
        visual_widget = VisualDialogueWidget()

        # Connect the signal like the unified quest editor does
        print("Connecting signals...")
        text_mode_widget.node_added.connect(
            lambda node_id, node_data: on_text_node_added(
                text_mode_widget, visual_widget, node_id, node_data
            )
        )

        print("Widgets created and connected successfully")

        # Create a test node directly (simulating the dialog)
        from TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview import (
            DialogueNodeData,
        )

        node = DialogueNodeData(
            id="test_node_1",
            node_type="npc",
            speaker="Test NPC",
            text="Hello, this is a test dialogue that should cause a crash!",
        )

        print("Created test node")

        # Simulate what happens when the dialog is accepted
        print("Simulating node addition process...")

        # Add node to collection (what on_add_node does)
        text_mode_widget.nodes[node.id] = node
        print("Added node to collection")

        # Emit signal to notify other components (like visual editor)
        print("Emitting node_added signal...")
        try:
            text_mode_widget.node_added.emit(node.id, node.to_dict())
            print("Signal emitted successfully")
        except Exception as e:
            print(f"ERROR: Failed to emit signal: {e}")
            import traceback

            traceback.print_exc()
            return False

        # Refresh the view
        print("Refreshing view...")
        try:
            text_mode_widget.refresh_view()
            print("View refreshed successfully")
        except Exception as e:
            print(f"ERROR: Failed to refresh view: {e}")
            import traceback

            traceback.print_exc()
            return False

        print("Node addition completed successfully!")
        return True

    except Exception as e:
        print(f"ERROR: Crash occurred: {e}")
        import traceback

        traceback.print_exc()
        return False


def on_text_node_added(text_widget, visual_widget, node_id, node_data):
    """Simulate the _on_text_mode_node_added method from unified quest editor"""
    print(f"Syncing node {node_id} to visual widget...")

    try:
        # Sync to visual editor if available
        if visual_widget:
            print("Getting dialogue data from text widget...")
            dialogue_data = text_widget.get_dialogue_data()
            print(f"Got dialogue data: {len(dialogue_data.get('nodes', []))} nodes")

            print("Setting dialogue data on visual widget...")
            visual_widget.set_dialogue_data(dialogue_data)
            print(f"Synced node {node_id} to visual widget")
        else:
            print("No visual widget available")
    except Exception as e:
        print(f"ERROR: Failed to sync to visual widget: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    success = test_add_node_crash()
    sys.exit(0 if success else 1)
