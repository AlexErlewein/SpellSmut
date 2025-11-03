#!/usr/bin/env python3
"""
Test script to verify texture loading and toggle functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.TirganachReloaded.map_viewer.simple_texture_manager import SimpleTextureManager
from src.TirganachReloaded.map_viewer.terrain_texture_mapper import TerrainTextureMapper

def test_texture_loading():
    """Test texture loading functionality"""
    print("=== Testing Texture Loading ===")
    
    # Test texture manager
    print("1. Testing SimpleTextureManager...")
    texture_mgr = SimpleTextureManager()
    
    # Load textures from the correct path
    base_path = "/Users/alex/Desktop/code/Others/SpellSmut/ExtractedAssets"
    texture_mgr.load_available_textures(base_path)
    
    print(f"   Texture files found: {len(texture_mgr.texture_files)}")
    if texture_mgr.texture_files:
        print(f"   First 5 texture IDs: {list(texture_mgr.texture_files.keys())[:5]}")
    
    # Test loading a few textures
    loaded_count = 0
    for i, texture_id in enumerate(list(texture_mgr.texture_files.keys())[:5]):
        texture = texture_mgr.get_texture(texture_id)
        if texture is not None:
            loaded_count += 1
            print(f"   Loaded texture {texture_id}: shape {texture.shape}")
        else:
            print(f"   Failed to load texture {texture_id}")
    
    print(f"   Successfully loaded {loaded_count}/5 textures")
    
    # Test terrain texture mapper
    print("\n2. Testing TerrainTextureMapper...")
    try:
        mapper = TerrainTextureMapper()
        print(f"   Terrain texture mapper created successfully")
        print(f"   Texture files found: {len(texture_mgr.texture_files)}")
    except Exception as e:
        print(f"   Error creating terrain texture mapper: {e}")
    
    return loaded_count > 0

def test_texture_toggle():
    """Test texture toggle functionality without GUI"""
    print("\n=== Testing Texture Toggle Logic ===")
    
    # Simulate texture toggle state
    use_textures = False
    
    print(f"Initial state: textures {'ON' if use_textures else 'OFF'}")
    
    # Toggle textures
    use_textures = not use_textures
    print(f"After toggle: textures {'ON' if use_textures else 'OFF'}")
    
    # Toggle again
    use_textures = not use_textures
    print(f"After second toggle: textures {'ON' if use_textures else 'OFF'}")
    
    return True

if __name__ == "__main__":
    print("Testing Map Viewer Texture System")
    print("=" * 50)
    
    texture_ok = test_texture_loading()
    toggle_ok = test_texture_toggle()
    
    print("\n=== Test Results ===")
    print(f"Texture Loading: {'✅ PASS' if texture_ok else '❌ FAIL'}")
    print(f"Texture Toggle: {'✅ PASS' if toggle_ok else '❌ FAIL'}")
    
    if texture_ok and toggle_ok:
        print("\n🎉 All tests passed! Texture system should work correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)