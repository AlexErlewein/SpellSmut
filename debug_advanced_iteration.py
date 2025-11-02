#!/usr/bin/env python3
"""
Debug what's slow in advanced descriptions iteration
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger
from TirganachReloaded.cff_editor.data_model import CFFDataModel

def debug_advanced_descriptions_iteration():
    """Debug what's slow in advanced descriptions"""
    logger.info("Debugging advanced descriptions iteration...")
    
    # Initialize data model
    data_model = CFFDataModel()
    
    file_path = data_model.get_default_file_path()
    fingerprint = data_model._generate_fingerprint(file_path)
    
    # Load cache manually
    cached_data, _ = data_model._load_from_cache(fingerprint)
    if cached_data:
        data_model.game_data = cached_data
        
        descriptions_table = data_model.get_table("advanced_descriptions")
        if descriptions_table:
            logger.info(f"Table type: {type(descriptions_table)}")
            logger.info(f"Table length: {len(descriptions_table)}")
            
            # Test just iterating
            logger.info("Testing iteration speed...")
            start_time = time.time()
            count = 0
            for entry in descriptions_table:
                count += 1
            iteration_time = time.time() - start_time
            logger.info(f"Iteration only: {iteration_time:.3f}s for {count} entries")
            
            # Test accessing attributes
            logger.info("Testing attribute access...")
            start_time = time.time()
            for entry in descriptions_table:
                description_id = getattr(entry, "description_id", None)
                text = getattr(entry, "text", "")
            attr_time = time.time() - start_time
            logger.info(f"Attribute access: {attr_time:.3f}s")
            
            # Test building dict
            logger.info("Testing dict building...")
            start_time = time.time()
            test_dict = {}
            for entry in descriptions_table:
                description_id = getattr(entry, "description_id", None)
                text = getattr(entry, "text", "")
                if description_id is not None:
                    test_dict[description_id] = text
            dict_time = time.time() - start_time
            logger.info(f"Dict building: {dict_time:.3f}s")
            
            # Test comprehension
            logger.info("Testing comprehension...")
            start_time = time.time()
            test_dict2 = {
                getattr(entry, "description_id", None): getattr(entry, "text", "")
                for entry in descriptions_table
                if getattr(entry, "description_id", None) is not None
            }
            comp_time = time.time() - start_time
            logger.info(f"Comprehension: {comp_time:.3f}s")
            
            logger.info(f"Dict sizes: {len(test_dict)} vs {len(test_dict2)}")
    
if __name__ == "__main__":
    debug_advanced_descriptions_iteration()