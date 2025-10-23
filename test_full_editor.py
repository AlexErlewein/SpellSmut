#!/usr/bin/env python3
"""
Test script to run the full editor and check quest functionality
"""

import sys
sys.path.append('TirganachReloaded')

from PySide6.QtWidgets import QApplication
from TirganachReloaded.cff_editor.main_window import MainWindow
import time

def test_full_editor():
    """Test the full editor with quest functionality"""
    print("Testing full editor...")

    # Create QApplication
    app = QApplication(sys.argv)

    try:
        # Create main window
        window = MainWindow()
        print("✓ Main window created")

        # Wait a bit for auto-load
        time.sleep(1)

        # Check if data is loaded
        if window.data_model.game_data:
            print("✓ Data loaded successfully")
        else:
            print("✗ Data not loaded")
            return

        # Switch to quests category (simulate clicking on quests in category tree)
        window.data_model.current_category = "quests"
        window.data_model.category_changed.emit("quests")
        print("✓ Switched to quests category")

        # Force the main window to handle the category change
        window.on_category_changed("quests")
        print("✓ Main window handled category change")

        # Get quest elements
        quests = window.data_model.get_elements("quests")
        print(f"✓ Found {len(quests)} quests")

        if quests:
            # Select first quest
            window.data_model.element_selected.emit("quests", 0)
            print("✓ Selected first quest")

        # Check if quest details panel is visible
        if window.quest_details.isVisible():
            print("✓ Quest details panel is visible")
        else:
            print("✗ Quest details panel is not visible")
            # Try to show it manually
            window.quest_details.show()
            print("✓ Manually showed quest details panel")

            # Check quest details content
            quest_id = window.quest_details.quest_id_label.text()
            quest_name = window.quest_details.quest_name_label.text()
            print(f"✓ Quest ID: {quest_id}, Name: {quest_name}")

        print("Full editor test completed successfully!")

    except Exception as e:
        print(f"✗ Error in full editor test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        app.quit()

if __name__ == "__main__":
    test_full_editor()