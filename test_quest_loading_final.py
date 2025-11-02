#!/usr/bin/env python3
"""
Test quest loading performance after optimization
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger
from TirganachReloaded.cff_editor.data_model import CFFDataModel
from TirganachReloaded.cff_editor.widgets.quest_hierarchy_tree import QuestHierarchyTreeWidget

def test_quest_loading_performance():
    """Test quest loading performance end-to-end"""
    logger.info("Testing quest loading performance after optimization...")
    
    # Initialize data model and load file
    logger.info("1. Loading GameData.cff...")
    start_time = time.time()
    data_model = CFFDataModel()
    file_path = data_model.get_default_file_path()
    success = data_model.load_file(file_path)
    load_time = time.time() - start_time
    logger.info(f"   Load time: {load_time:.3f}s")
    logger.info(f"   Load success: {success}")
    
    if success:
        # Test quest hierarchy tree loading
        logger.info("2. Loading quest hierarchy tree...")
        start_time = time.time()
        quest_tree = QuestHierarchyTreeWidget(data_model)
        quest_tree.load_quests()
        tree_time = time.time() - start_time
        logger.info(f"   Tree load time: {tree_time:.3f}s")
        logger.info(f"   Quests loaded: {len(quest_tree.quest_nodes)}")
        
        # Test quest selection
        logger.info("3. Testing quest selection...")
        start_time = time.time()
        quests = data_model.get_elements("quests")
        if quests:
            first_quest = quests[0]
            quest_id = getattr(first_quest, "quest_id", None)
            logger.info(f"   Selected quest ID: {quest_id}")
        selection_time = time.time() - start_time
        logger.info(f"   Selection time: {selection_time:.6f}s")
        
        total_time = load_time + tree_time
        logger.info("=== PERFORMANCE SUMMARY ===")
        logger.info(f"GameData loading: {load_time:.3f}s")
        logger.info(f"Quest tree loading: {tree_time:.3f}s")
        logger.info(f"Total quest loading: {total_time:.3f}s")
        
        return total_time < 2.0  # Should be under 2 seconds
    
    return False

if __name__ == "__main__":
    success = test_quest_loading_performance()
    logger.info(f"{'✅ Quest loading performance EXCELLENT' if success else '❌ Quest loading still slow'}")