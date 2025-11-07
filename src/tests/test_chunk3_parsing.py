#!/usr/bin/env python3
"""
Test script for enhanced Chunk 3 texture parsing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from src.TirganachReloaded.map_viewer.simple_map_loader import SimpleMapLoader

def test_chunk_3_parsing():
    """Test enhanced Chunk 3 parsing with multi-layer support"""
    print("=== Testing Enhanced Chunk 3 Parsing ===")
    
    # Try to load a real map file
    map_file = "/Users/alex/Desktop/code/Others/SpellSmut/OriginalGameFiles/data/GameData.cff"
    
    if not os.path.exists(map_file):
        print(f"Map file not found: {map_file}")
        return False
        
    try:
        loader = SimpleMapLoader()
        success = loader.load(Path(map_file))
        
        if not success:
            print("Failed to load map")
            return False
            
        print(f"✅ Map loaded successfully")
        print(f"   Heightmap: {loader.heightmap.width}x{loader.heightmap.height}")
        print(f"   Texture assignments: {len(loader.terrain_textures)}")
        
        # Analyze texture assignments
        if loader.terrain_textures:
            print(f"\n=== Texture Assignment Analysis ===")
            
            # Count layers per assignment
            layer_counts = {}
            texture_usage = {}
            
            for assignment in loader.terrain_textures[:10]:  # Sample first 10
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
            for tex_id, usage in sorted(texture_usage.items())[:10]:
                print(f"   Texture {tex_id}: {usage} uses")
                
        return True
        
    except Exception as e:
        print(f"❌ Error testing Chunk 3 parsing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Enhanced Chunk 3 Texture Parsing")
    print("=" * 50)
    
    success = test_chunk_3_parsing()
    
    print(f"\n=== Test Results ===")
    if success:
        print("🎉 Enhanced Chunk 3 parsing: ✅ PASS")
        sys.exit(0)
    else:
        print("❌ Enhanced Chunk 3 parsing: ❌ FAIL")
        sys.exit(1)