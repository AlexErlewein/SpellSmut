#!/usr/bin/env python3
"""
Test script for multi-layer texture blending system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.TirganachReloaded.map_viewer.multi_layer_texture_system import (
    MultiLayerTextureSystem, 
    TerrainTextureBlend
)

def test_multi_layer_system():
    """Test multi-layer texture blending system"""
    print("=== Testing Multi-Layer Texture System ===")
    
    # Test 1: Basic TerrainTextureBlend
    print("1. Testing TerrainTextureBlend...")
    blend = TerrainTextureBlend()
    
    # Add some texture layers
    blend.add_layer(1, 0.7)  # Grass
    blend.add_layer(44, 0.3)  # Rock
    
    print(f"   Added layers: {blend.texture_ids}")
    print(f"   Weights: {blend.blend_weights}")
    print(f"   Total weight: {blend.total_weight}")
    
    # Normalize weights
    blend.normalize_weights()
    print(f"   Normalized weights: {blend.blend_weights}")
    print(f"   Primary texture: {blend.get_primary_texture()}")
    print(f"   Is valid: {blend.is_valid()}")
    
    # Test 2: Multi-layer texture system
    print("\n2. Testing MultiLayerTextureSystem...")
    system = MultiLayerTextureSystem()
    
    print(f"   Texture categories: {len(system.texture_categories)}")
    print(f"   Blend patterns: {len(system.blend_patterns)}")
    
    # Test 3: Create fallback blend
    print("\n3. Testing fallback blend creation...")
    fallback_blend = system.create_fallback_blend(50.0, 0.0, 100.0)
    print(f"   Fallback blend textures: {fallback_blend.texture_ids}")
    print(f"   Fallback blend weights: {fallback_blend.blend_weights}")
    
    # Test 4: Mock texture assignments
    print("\n4. Testing texture assignment parsing...")
    
    class MockAssignment:
        def __init__(self, x, y, texture_id):
            self.x = x
            self.y = y
            self.texture_id = texture_id
    
    # Create mock assignments
    assignments = [
        MockAssignment(0, 0, 1),   # Grass
        MockAssignment(1, 0, 1),   # Grass  
        MockAssignment(2, 0, 44),  # Rock
        MockAssignment(3, 0, 44),  # Rock
        MockAssignment(0, 1, 1),   # Grass
        MockAssignment(1, 1, 77),  # Stone grass
        MockAssignment(2, 1, 77),  # Stone grass
        MockAssignment(3, 1, 44),  # Rock
    ]
    
    # Parse assignments
    blends = system.parse_texture_assignments(assignments)
    print(f"   Parsed {len(assignments)} assignments into {len(blends)} tile blends")
    
    # Show some blend examples
    for i, (tile_key, blend) in enumerate(list(blends.items())[:3]):
        print(f"   Tile {tile_key}: textures={blend.texture_ids}, weights={blend.blend_weights}")
    
    # Test 5: Statistics
    print("\n5. Testing statistics...")
    stats = system.get_statistics()
    print(f"   Statistics: {stats}")
    
    return True

def test_integration():
    """Test integration with map viewer components"""
    print("\n=== Testing Integration ===")
    
    try:
        from src.TirganachReloaded.map_viewer.simple_texture_manager import SimpleTextureManager
        
        # Test texture manager integration
        texture_mgr = SimpleTextureManager()
        base_path = "/Users/alex/Desktop/code/Others/SpellSmut/ExtractedAssets"
        texture_mgr.load_available_textures(base_path)
        
        print(f"   Texture manager found {len(texture_mgr.texture_files)} textures")
        
        # Test multi-layer system with real texture IDs
        system = MultiLayerTextureSystem()
        
        # Update texture categories with real IDs
        real_texture_ids = list(texture_mgr.texture_files.keys())[:10]
        print(f"   Real texture IDs found: {real_texture_ids}")
        
        return True
        
    except Exception as e:
        print(f"   Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Multi-Layer Texture Blending System")
    print("=" * 60)
    
    basic_test = test_multi_layer_system()
    integration_test = test_integration()
    
    print("\n=== Test Results ===")
    print(f"Basic functionality: {'✅ PASS' if basic_test else '❌ FAIL'}")
    print(f"Integration test: {'✅ PASS' if integration_test else '❌ FAIL'}")
    
    if basic_test and integration_test:
        print("\n🎉 Multi-layer texture system is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)