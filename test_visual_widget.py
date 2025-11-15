#!/usr/bin/env python3
"""
Test script to check visual dialogue widget initialization
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from PySide6.QtWidgets import QApplication
from TirganachReloaded.cff_editor.widgets.visual_dialogue_widget import (
    VisualDialogueWidget,
)


def test_visual_widget():
    """Test visual dialogue widget initialization"""
    print("Testing visual dialogue widget initialization...")

    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    try:
        print("Creating visual dialogue widget...")
        visual_widget = VisualDialogueWidget()
        print("Visual widget created successfully")

        print("Checking VISUAL_EDITOR_COMPONENTS_AVAILABLE...")
        from TirganachReloaded.cff_editor.widgets.visual_dialogue_widget import (
            VISUAL_EDITOR_COMPONENTS_AVAILABLE,
        )

        print(
            f"VISUAL_EDITOR_COMPONENTS_AVAILABLE = {VISUAL_EDITOR_COMPONENTS_AVAILABLE}"
        )

        print("Checking widget attributes...")
        print(
            f"graphics_view: {hasattr(visual_widget, 'graphics_view') and visual_widget.graphics_view is not None}"
        )
        print(
            f"tree_widget: {hasattr(visual_widget, 'tree_widget') and visual_widget.tree_widget is not None}"
        )

        if hasattr(visual_widget, "graphics_view") and visual_widget.graphics_view:
            print(f"graphics_view type: {type(visual_widget.graphics_view)}")
            print(
                f"graphics_view has add_node: {hasattr(visual_widget.graphics_view, 'add_node')}"
            )

        if hasattr(visual_widget, "tree_widget") and visual_widget.tree_widget:
            print(f"tree_widget type: {type(visual_widget.tree_widget)}")
            print(
                f"tree_widget has set_nodes: {hasattr(visual_widget.tree_widget, 'set_nodes')}"
            )

        print("Testing set_dialogue_data with empty data...")
        visual_widget.set_dialogue_data({})
        print("Empty data test passed")

        print("Testing set_dialogue_data with node data...")
        test_data = {
            "nodes": [
                {
                    "id": "test_node_1",
                    "type": "npc",
                    "speaker": "Test NPC",
                    "text": "Hello, this is a test dialogue!",
                }
            ],
            "connections": [],
        }
        visual_widget.set_dialogue_data(test_data)
        print("Node data test passed")

        print("Visual widget test completed successfully!")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_visual_widget()
    sys.exit(0 if success else 1)
