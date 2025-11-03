#!/usr/bin/env python3
"""
Debug why cache is not being used for GameData loading
"""

import sys
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from TirganachReloaded.cff_editor.data_model import CFFDataModel

def debug_cache_usage():
    """Debug why cache is not being used"""
    print("Debugging cache usage...")
    
    # Initialize data model
    data_model = CFFDataModel()
    
    # Check file path and fingerprint
    file_path = data_model.get_default_file_path()
    print(f"File path: {file_path}")
    
    fingerprint = data_model._generate_fingerprint(file_path)
    print(f"Fingerprint: {fingerprint}")
    
    # Check cache files
    cache_file, meta_file = data_model._get_cache_paths(fingerprint)
    print(f"Cache file: {cache_file}")
    print(f"Meta file: {meta_file}")
    print(f"Cache exists: {cache_file.exists()}")
    print(f"Meta exists: {meta_file.exists()}")
    
    if meta_file.exists():
        with open(meta_file, "r") as f:
            meta = json.load(f)
        print(f"Cache metadata: {meta}")
        
        # Check cache version
        from TirganachReloaded.cff_editor.data_model import CACHE_VERSION
        print(f"Current cache version: {CACHE_VERSION}")
        print(f"Cached version: {meta.get('cache_version')}")
        print(f"Version match: {meta.get('cache_version') == CACHE_VERSION}")
    
    # Test cache loading
    print("\nTesting cache loading...")
    start_time = time.time()
    cached_data, cache_failure_reason = data_model._load_from_cache(fingerprint)
    cache_time = time.time() - start_time
    
    print(f"Cache load time: {cache_time:.3f}s")
    print(f"Cache data loaded: {cached_data is not None}")
    print(f"Cache failure reason: {cache_failure_reason}")
    
    # Test full loading with timing
    print("\nTesting full file loading...")
    start_time = time.time()
    success = data_model.load_file(file_path)
    full_time = time.time() - start_time
    
    print(f"Full load time: {full_time:.3f}s")
    print(f"Load success: {success}")
    
    return cached_data is not None

if __name__ == "__main__":
    cache_works = debug_cache_usage()
    print(f"\n{'✅ Cache working' if cache_works else '❌ Cache not working'}")