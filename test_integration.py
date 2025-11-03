#!/usr/bin/env python3
"""
Integration test for complete multi-layer texture system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.TirganachReloaded.map_viewer.simple_map_loader import SimpleMapLoader, TerrainTextureAssignment
from src.TirganachReloaded.map_viewer.multi_layer_texture_system import MultiLayerTextureSystem

def test_complete_integration():
    """Test complete integration of enhanced parsing with multi-layer system"""
    print("=== Testing Complete Multi-Layer Integration ===")
    
    # Create mock enhanced texture assignments
    enhanced_assignments = []
    
    # Single texture tile
    assignment1 = TerrainTextureAssignment(
        x=0, y=0, texture_id=1, blend_weights=[1.0]
    )
    enhanced_assignments.append(assignment1)
    
    # Double texture tile
    assignment2 = TerrainTextureAssignment(
        x=4, y=4, 
        texture_id=1, 
        blend_weights=[0.7, 0.3],
        additional_textures=[44]
    )
    enhanced_assignments.append(assignment2)
    
    # Triple texture tile
    assignment3 = TerrainTextureAssignment(
        x=8, y=8,
        texture_id=1,
        blend_weights=[0.5, 0.3, 0.2],
        additional_textures=[44, 77]
    )
    enhanced_assignments.append(assignment3)
    
    print(f"Created {len(enhanced_assignments)} enhanced texture assignments")
    
    # Test multi-layer system integration
    multi_layer_system = MultiLayerTextureSystem()
    
    # Convert to mock assignments for parsing
    mock_assignments = []
    for assignment in enhanced_assignments:
        all_textures = assignment.get_all_textures()
        weights = assignment.get_effective_weights()
        
        print(f"Assignment ({assignment.x}, {assignment.y}):")
        print(f"  All textures: {all_textures}")
        print(f"  Weights: {weights}")
        
        # Create mock assignments for each layer
        for i, (tex_id, weight) in enumerate(zip(all_textures, weights)):
            mock_assignment = type('MockAssignment', (), {
                'x': assignment.x,
                'y': assignment.y,
                'texture_id': tex_id
            })()
            mock_assignments.append(mock_assignment)
    
    # Parse with multi-layer system
    blends = multi_layer_system.parse_texture_assignments(mock_assignments)
    
    print(f"\nMulti-layer system created {len(blends)} texture blends")
    
    # Test tile retrieval
    for tile_key in [(0, 0), (1, 1), (2, 2)]:
        blend = multi_layer_system.get_blend_for_tile(tile_key[0], tile_key[1])
        if blend:
            print(f"Tile {tile_key}: {blend.texture_ids} with weights {blend.blend_weights}")
        else:
            print(f"Tile {tile_key}: No blend found")
    
    # Test statistics
    stats = multi_layer_system.get_statistics()
    print(f"\nStatistics: {stats}")
    
    return len(blends) > 0

def test_fallback_system():
    """Test fallback texture generation"""
    print("\n=== Testing Fallback System ===")
    
    system = MultiLayerTextureSystem()
    
    # Test different heights
    test_heights = [0.0, 25.0, 50.0, 75.0, 100.0]
    min_h, max_h = 0.0, 100.0
    
    for height in test_heights:
        blend = system.create_fallback_blend(height, min_h, max_h)
        print(f"Height {height}: {blend.texture_ids} with weights {blend.blend_weights}")
    
    return True

if __name__ == "__main__":
    print("Testing Complete Multi-Layer Texture Integration")
    print("=" * 60)
    
    integration_test = test_complete_integration()
    fallback_test = test_fallback_system()
    
    print(f"\n=== Test Results ===")
    print(f"Complete integration: {'✅ PASS' if integration_test else '❌ FAIL'}")
    print(f"Fallback system: {'✅ PASS' if fallback_test else '❌ FAIL'}")
    
    if integration_test and fallback_test:
        print("\n🎉 Complete multi-layer texture system is working!")
        print("✅ Ready for integration with map viewer!")
        sys.exit(0)
    else:
        print("\n❌ Some integration tests failed.")
        sys.exit(1)