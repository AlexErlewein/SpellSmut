#!/usr/bin/env python3
"""
Profile what happens after cache loading
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger
from TirganachReloaded.cff_editor.data_model import CFFDataModel

def profile_post_cache_loading():
    """Profile operations after cache loading"""
    logger.info("Profiling post-cache loading operations...")
    
    # Initialize data model
    data_model = CFFDataModel()
    
    file_path = data_model.get_default_file_path()
    fingerprint = data_model._generate_fingerprint(file_path)
    
    # Load cache manually
    logger.info("1. Loading cache...")
    start_time = time.time()
    cached_data, cache_failure_reason = data_model._load_from_cache(fingerprint)
    cache_time = time.time() - start_time
    logger.info(f"   Cache load: {cache_time:.3f}s")
    
    if cached_data:
        data_model.game_data = cached_data
        data_model.file_path = file_path
        data_model.modified = False
        
        # Profile each operation
        logger.info("2. Loading weapon names...")
        start_time = time.time()
        data_model._load_weapon_names()
        weapon_time = time.time() - start_time
        logger.info(f"   Weapon names: {weapon_time:.3f}s")
        
        logger.info("3. Loading armor names...")
        start_time = time.time()
        data_model._load_armor_names()
        armor_time = time.time() - start_time
        logger.info(f"   Armor names: {armor_time:.3f}s")
        
        logger.info("4. Building localisation index...")
        start_time = time.time()
        data_model._build_localisation_index()
        loc_time = time.time() - start_time
        logger.info(f"   Localisation index: {loc_time:.3f}s")
        
        logger.info("5. Building advanced descriptions index...")
        start_time = time.time()
        data_model._build_advanced_descriptions_index()
        desc_time = time.time() - start_time
        logger.info(f"   Advanced descriptions: {desc_time:.3f}s")
        
        total_post_cache = weapon_time + armor_time + loc_time + desc_time
        logger.info(f"Total post-cache time: {total_post_cache:.3f}s")
        logger.info(f"Cache load time: {cache_time:.3f}s")
        logger.info(f"Total estimated: {cache_time + total_post_cache:.3f}s")
        
        return total_post_cache < 2.0
    
    return False

if __name__ == "__main__":
    success = profile_post_cache_loading()
    logger.info(f"{'✅ Post-cache loading OK' if success else '❌ Post-cache loading too slow'}")