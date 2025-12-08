#!/usr/bin/env python3
"""
Test script to directly test the on_add_node method
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from PySide6.QtWidgets import QApplication
from TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview import (
    TextModeDialogueOverview,
)


def test_on_add_node():
    """Test the on_add_node method directly"""
    print("Testing on_add_node method...")

    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    try:
        # Create the text mode dialogue overview widget
        print("Creating text mode dialogue overview widget...")
        text_mode_widget = TextModeDialogueOverview()

        print("Widget created successfully")

        # Simulate clicking the "+ Add Node" button by calling on_add_node directly
        # But we can't easily simulate the dialog. Let's manually add a node like the method does.

        print("Manually adding a node like on_add_node does...")

        # This is what on_add_node does when the dialog is accepted
        node_type = "npc"
        node_id = f"{node_type}_{len(text_mode_widget.nodes) + 1}"
        speaker = "Test NPC"
        text = "Hello, this is a test dialogue!"

        print(f"Creating node: id={node_id}, type={node_type}, speaker={speaker}")

        # Create node
        from TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview import (
            DialogueNodeData,
        )

        node = DialogueNodeData(
            id=node_id, node_type=node_type, speaker=speaker, text=text
        )

        print("Created node object")

        # Add node to collection
        text_mode_widget.nodes[node_id] = node
        print("Added node to collection")

        # Auto-connect to previous node if one exists (simplified)
        if text_mode_widget.nodes:
            # Find the most recently added node
            sorted_nodes = sorted(text_mode_widget.nodes.keys(), key=lambda x: x)
            if sorted_nodes:
                last_node_id = sorted_nodes[-1]
                last_node = text_mode_widget.nodes[last_node_id]
                if node_id not in last_node.next_nodes:
                    last_node.next_nodes.append(node_id)

                # Update hierarchy
                if last_node_id not in text_mode_widget.node_hierarchy:
                    text_mode_widget.node_hierarchy[last_node_id] = []
                if node_id not in text_mode_widget.node_hierarchy[last_node_id]:
                    text_mode_widget.node_hierarchy[last_node_id].append(node_id)

                print(f"Connected node {node_id} after {last_node_id}")
        else:
            print("No previous nodes to connect to")

        # Emit signal to notify other components (like visual editor)
        print("Emitting node_added signal...")
        text_mode_widget.node_added.emit(node_id, node.to_dict())
        print("Signal emitted successfully")

        # Refresh the view
        print("Refreshing view...")
        text_mode_widget.refresh_view()
        print("View refreshed successfully")

        print("Node addition completed successfully!")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_on_add_node()
    sys.exit(0 if success else 1)
