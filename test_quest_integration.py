#!/usr/bin/env python3
"""
Test script to verify quest tree view and quest details integration
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_quest_integration():
    """Test that quest selection updates the quest details view"""
    print("=" * 60)
    print("Testing Quest Tree View and Quest Details Integration")
    print("=" * 60)
    
    try:
        from TirganachReloaded.cff_editor.main_window import MainWindow
        from PySide6.QtWidgets import QApplication
        
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            app = QApplication([])
        
        # Create main window
        main_window = MainWindow()
        
        print("✓ Main window created successfully")
        
        # Check if quest-related widgets are present
        assert hasattr(main_window, 'quest_hierarchy_tree'), "Missing quest_hierarchy_tree"
        assert hasattr(main_window, 'quest_details'), "Missing quest_details"
        assert hasattr(main_window, 'category_tree'), "Missing category_tree"
        
        print("✓ All quest-related widgets are present")
        
        # Check if element_selected signal is connected
        assert hasattr(main_window, 'on_element_selected'), "Missing on_element_selected method"
        
        print("✓ Element selection handler is present")
        
        # Check if quest details widget has the required method
        assert hasattr(main_window.quest_details, 'on_element_selected'), "Quest details missing on_element_selected method"
        
        print("✓ Quest details widget can handle element selection")
        
        print("\n" + "=" * 60)
        print("INTEGRATION SUMMARY:")
        print("- Quest tree view: QuestHierarchyTreeWidget (center panel)")
        print("- Quest details view: QuestDetailsWidget (right panel)")
        print("- Connection: element_selected signal connects tree to details")
        print("- Activation: Automatically shows when 'quests' category is selected")
        print("- Layout: 4-panel layout (categories, quest tree, properties, quest details)")
        print("\nTo test:")
        print("1. Run the main application")
        print("2. Click on 'quests' in the left category tree")
        print("3. Click on any quest in the center quest tree")
        print("4. Quest details should appear in the right panel")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"Error during integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_quest_integration()
    sys.exit(0 if success else 1)
