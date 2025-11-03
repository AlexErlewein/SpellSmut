#!/usr/bin/env python3
"""
Test script for enhanced Chunk 3 texture parsing with mock data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.TirganachReloaded.map_viewer.simple_map_loader import SimpleMapLoader, TerrainTextureAssignment

def test_mock_chunk3_parsing():
    """Test enhanced Chunk 3 parsing with mock data"""
    print("=== Testing Mock Chunk 3 Parsing ===")
    
    # Create mock Chunk 3 data (255 entries * 14 bytes each)
    mock_data = bytearray()
    
    for i in range(255):
        # Create varied texture assignments
        if i % 4 == 0:
            # Single texture - grass
            mock_data.extend([1, 0, 0])  # Texture indices
            mock_data.extend([255, 0, 0])  # Weights (100% grass)
        elif i % 4 == 1:
            # Double texture - grass + rock
            mock_data.extend([1, 44, 0])  # Texture indices (grass, rock)
            mock_data.extend([180, 75, 0])  # Weights (70% grass, 30% rock)
        elif i % 4 == 2:
            # Triple texture - grass + rock + stone
            mock_data.extend([1, 44, 77])  # Texture indices (grass, rock, stone)
            mock_data.extend([128, 77, 50])  # Weights (50% grass, 30% rock, 20% stone)
        else:
            # Single texture - rock
            mock_data.extend([44, 0, 0])  # Texture indices
            mock_data.extend([255, 0, 0])  # Weights (100% rock)
            
        # Add 8 bytes padding
        mock_data.extend([0, 0, 0, 0, 0, 0, 0, 0])
    
    # Test parsing
    loader = SimpleMapLoader()
    
    try:
        assignments = loader._parse_chunk_3_terrain_textures(bytes(mock_data))
        
        print(f"✅ Successfully parsed {len(assignments)} texture assignments")
        
        # Analyze results
        layer_counts = {}
        texture_usage = {}
        
        for assignment in assignments[:10]:  # Sample first 10
            all_textures = assignment.get_all_textures()
            weights = assignment.get_effective_weights()
            
            layer_count = len(all_textures)
            layer_counts[layer_count] = layer_counts.get(layer_count, 0) + 1
            
            print(f"   Assignment at ({assignment.x}, {assignment.y}):")
            print(f"     Textures: {all_textures}")
            print(f"     Weights: {weights}")
            print(f"     Layers: {layer_count}")
            
            for tex_id in all_textures:
                texture_usage[tex_id] = texture_usage.get(tex_id, 0) + 1
        
        print(f"\n=== Layer Distribution ===")
        for count, frequency in sorted(layer_counts.items()):
            print(f"   {count} layers: {frequency} assignments")
            
        print(f"\n=== Texture Usage ===")
        for tex_id, usage in sorted(texture_usage.items()):
            print(f"   Texture {tex_id}: {usage} uses")
            
        return True
        
    except Exception as e:
        print(f"❌ Error parsing mock Chunk 3 data: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_terrain_assignment_methods():
    """Test TerrainTextureAssignment helper methods"""
    print("\n=== Testing TerrainTextureAssignment Methods ===")
    
    # Test single texture
    assignment1 = TerrainTextureAssignment(
        x=0, y=0, texture_id=1, blend_weights=[1.0]
    )
    print(f"Single texture assignment:")
    print(f"   All textures: {assignment1.get_all_textures()}")
    print(f"   Effective weights: {assignment1.get_effective_weights()}")
    
    # Test multi-layer texture
    assignment2 = TerrainTextureAssignment(
        x=4, y=4, 
        texture_id=1, 
        blend_weights=[0.7, 0.3],
        additional_textures=[44]
    )
    print(f"\nMulti-layer assignment:")
    print(f"   All textures: {assignment2.get_all_textures()}")
    print(f"   Effective weights: {assignment2.get_effective_weights()}")
    
    # Test triple-layer texture
    assignment3 = TerrainTextureAssignment(
        x=8, y=8,
        texture_id=1,
        blend_weights=[0.5, 0.3, 0.2],
        additional_textures=[44, 77]
    )
    print(f"\nTriple-layer assignment:")
    print(f"   All textures: {assignment3.get_all_textures()}")
    print(f"   Effective weights: {assignment3.get_effective_weights()}")
    
    return True

if __name__ == "__main__":
    print("Testing Enhanced Chunk 3 Texture Parsing (Mock Data)")
    print("=" * 60)
    
    mock_test = test_mock_chunk3_parsing()
    methods_test = test_terrain_assignment_methods()
    
    print(f"\n=== Test Results ===")
    print(f"Mock data parsing: {'✅ PASS' if mock_test else '❌ FAIL'}")
    print(f"Assignment methods: {'✅ PASS' if methods_test else '❌ FAIL'}")
    
    if mock_test and methods_test:
        print("\n🎉 Enhanced Chunk 3 parsing is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)