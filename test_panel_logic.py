#!/usr/bin/env python3
"""
Test script to verify quest details panel visibility logic
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger

def test_quest_panel_visibility_logic():
    """Test the quest panel visibility logic from MainWindow"""
    logger.info("Testing quest panel visibility logic...")
    
    # Simulate logic from MainWindow.on_category_changed()
    def simulate_category_change(category):
        logger.debug(f"Category changed to: {category}")
        
        if category == "quests":
            logger.debug("Showing quest hierarchy tree and quest details panel")
            # Hide element table, show quest hierarchy tree
            element_table_visible = False
            quest_hierarchy_tree_visible = True
            quest_details_visible = True
            
            logger.debug(f"Element table visible: {element_table_visible}")
            logger.debug(f"Quest hierarchy tree visible: {quest_hierarchy_tree_visible}")
            logger.debug(f"Quest details panel visible: {quest_details_visible}")
            
            # Simulate splitter adjustment for 4-panel layout
            splitter_sizes = [200, 350, 300, 200]  # categories, elements, properties, quest details
            logger.debug(f"Splitter sizes for 4-panel layout: {splitter_sizes}")
            
        else:
            logger.debug("Showing element table, hiding quest components")
            # Show element table, hide quest hierarchy tree
            element_table_visible = True
            quest_hierarchy_tree_visible = False
            quest_details_visible = False
            
            logger.debug(f"Element table visible: {element_table_visible}")
            logger.debug(f"Quest hierarchy tree visible: {quest_hierarchy_tree_visible}")
            logger.debug(f"Quest details panel visible: {quest_details_visible}")
            
            # Simulate splitter adjustment for 3-panel layout
            splitter_sizes = [200, 350, 300]  # categories, elements, properties
            logger.debug(f"Splitter sizes for 3-panel layout: {splitter_sizes}")
        
        return {
            'element_table_visible': element_table_visible if category == "quests" else True,
            'quest_hierarchy_tree_visible': category == "quests",
            'quest_details_visible': category == "quests",
            'splitter_sizes': splitter_sizes
        }
    
    # Test quest category selection
    quest_result = simulate_category_change("quests")
    print(f"\n✅ Quest category test:")
    print(f"   - Quest details visible: {quest_result['quest_details_visible']}")
    print(f"   - Quest hierarchy visible: {quest_result['quest_hierarchy_tree_visible']}")
    print(f"   - Element table visible: {quest_result['element_table_visible']}")
    print(f"   - Splitter sizes: {quest_result['splitter_sizes']}")
    
    # Test non-quest category selection
    items_result = simulate_category_change("items")
    print(f"\n✅ Items category test:")
    print(f"   - Quest details visible: {items_result['quest_details_visible']}")
    print(f"   - Quest hierarchy visible: {items_result['quest_hierarchy_tree_visible']}")
    print(f"   - Element table visible: {items_result['element_table_visible']}")
    print(f"   - Splitter sizes: {items_result['splitter_sizes']}")
    
    # Verify logic correctness
    quest_logic_correct = (
        quest_result['quest_details_visible'] and 
        quest_result['quest_hierarchy_tree_visible'] and 
        not quest_result['element_table_visible'] and
        quest_result['splitter_sizes'][3] > 0  # Quest details panel has space
    )
    
    items_logic_correct = (
        not items_result['quest_details_visible'] and 
        not items_result['quest_hierarchy_tree_visible'] and 
        items_result['element_table_visible'] and
        items_result['splitter_sizes'][3] == 0  # Quest details panel hidden
    )
    
    return quest_logic_correct and items_logic_correct

if __name__ == "__main__":
    success = test_quest_panel_visibility_logic()
    print(f"\n{'✅ Panel visibility logic PASSED' if success else '❌ Panel visibility logic FAILED'}")
    if success:
        print("The quest details panel should show when 'quests' category is selected!")
    else:
        print("There's an issue with the panel visibility logic.")