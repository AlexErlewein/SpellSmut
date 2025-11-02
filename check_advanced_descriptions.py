#!/usr/bin/env python3
"""
Check how many advanced descriptions exist
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger
from TirganachReloaded.cff_editor.data_model import CFFDataModel

def check_advanced_descriptions():
    """Check advanced descriptions table size"""
    logger.info("Checking advanced descriptions...")
    
    # Initialize data model
    data_model = CFFDataModel()
    
    file_path = data_model.get_default_file_path()
    fingerprint = data_model._generate_fingerprint(file_path)
    
    # Load cache manually
    cached_data, _ = data_model._load_from_cache(fingerprint)
    if cached_data:
        data_model.game_data = cached_data
        
        # Check table size
        descriptions_table = data_model.get_table("advanced_descriptions")
        if descriptions_table:
            logger.info(f"Advanced descriptions count: {len(descriptions_table)}")
            
            # Time the index building
            start_time = time.time()
            data_model._build_advanced_descriptions_index()
            index_time = time.time() - start_time
            logger.info(f"Index building time: {index_time:.3f}s")
            
            if data_model.advanced_descriptions_index:
                logger.info(f"Index size: {len(data_model.advanced_descriptions_index)}")
        else:
            logger.warning("No advanced descriptions table found")
    
if __name__ == "__main__":
    check_advanced_descriptions()