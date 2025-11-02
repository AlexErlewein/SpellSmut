#!/usr/bin/env python3
"""
Test script to demonstrate the improved logging in the Lua mapping extractor
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from TirganachReloaded.cff_editor.logging_config import configure_logging, get_logger
from helper_tools.extraction.extract_lua_mappings import LuaMappingExtractor

def test_normal_mode():
    """Test normal mode (INFO level and above only)"""
    print("=" * 60)
    print("Testing NORMAL MODE (INFO level and above)")
    print("=" * 60)
    
    # Configure logging in normal mode
    configure_logging(debug_mode=False)
    
    # Test the extractor (this will show minimal output)
    extractor = LuaMappingExtractor("ModdingTools/SpellForceLUASources", debug_mode=False)
    
    # Just test a small part to avoid long execution
    try:
        extractor.extract_weapon_types()
        print("\n✓ Normal mode test completed - you should see minimal output")
    except Exception as e:
        print(f"Note: {e}")

def test_debug_mode():
    """Test debug mode (DEBUG level and above)"""
    print("\n" + "=" * 60)
    print("Testing DEBUG MODE (DEBUG level and above)")
    print("=" * 60)
    
    # Configure logging in debug mode
    configure_logging(debug_mode=True)
    
    # Test the extractor (this will show verbose output)
    extractor = LuaMappingExtractor("ModdingTools/SpellForceLUASources", debug_mode=True)
    
    try:
        extractor.extract_weapon_types()
        print("\n✓ Debug mode test completed - you should see detailed debug output")
    except Exception as e:
        print(f"Note: {e}")

if __name__ == "__main__":
    test_normal_mode()
    test_debug_mode()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("- Normal mode: Shows only INFO, WARNING, ERROR messages")
    print("- Debug mode: Shows all DEBUG, INFO, WARNING, ERROR messages")
    print("- Use --debug flag when running the main application for verbose output")
    print("=" * 60)
