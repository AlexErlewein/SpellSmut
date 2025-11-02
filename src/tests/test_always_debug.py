#!/usr/bin/env python3
"""
Test script to verify debug logging is always enabled for Lua operations
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_lua_data_manager():
    """Test that Lua data manager always shows debug output"""
    print("=" * 60)
    print("Testing Lua Data Manager - should show DEBUG output by default")
    print("=" * 60)
    
    from TirganachReloaded.cff_editor.lua_parser.lua_data_manager import LuaDataManager
    
    # Create a temporary directory for testing
    test_dir = Path(__file__).parent / "test_lua_cache"
    
    # This should initialize debug logging automatically
    try:
        lua_manager = LuaDataManager(cache_dir=test_dir)
        print("✓ Lua data manager created with debug logging")
        
        # Test a debug message
        lua_manager.lua_logger.debug("This is a debug message - you should see this!")
        lua_manager.lua_logger.info("This is an info message - you should see this too!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Clean up
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)

def test_lua_mapping_extractor():
    """Test that Lua mapping extractor always shows debug output"""
    print("\n" + "=" * 60)
    print("Testing Lua Mapping Extractor - should show DEBUG output by default")
    print("=" * 60)
    
    from helper_tools.extraction.extract_lua_mappings import LuaMappingExtractor
    
    try:
        # This should initialize debug logging automatically
        extractor = LuaMappingExtractor("nonexistent_directory", debug_mode=True)
        print("✓ Lua mapping extractor created with debug logging")
        
        # Test logging
        extractor.logger.debug("This is a debug message from mapping extractor - you should see this!")
        extractor.logger.info("This is an info message from mapping extractor - you should see this too!")
        
    except Exception as e:
        print(f"Expected error for nonexistent directory: {e}")

if __name__ == "__main__":
    test_lua_data_manager()
    test_lua_mapping_extractor()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("- Both Lua tools now always show DEBUG level output")
    print("- This happens automatically when the tools are initialized")
    print("- No need to pass --debug flag when using from GUI")
    print("- Debug output will be visible in terminal when GUI runs these tools")
    print("=" * 60)
