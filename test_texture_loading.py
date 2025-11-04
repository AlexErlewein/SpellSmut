#!/usr/bin/env python3
"""
Test script to check texture loading and binding
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from TirganachReloaded.map_viewer.simple_texture_manager import SimpleTextureManager
    from TirganachReloaded.map_viewer.dds_loader import DDSLoader
    print("✅ Texture imports successful")
    
    # Test DDS loader
    dds_loader = DDSLoader()
    print("✅ DDS loader initialized")
    
    # Test texture manager
    texture_manager = SimpleTextureManager()
    print("✅ Texture manager initialized")
    
    # Load available textures
    texture_manager.load_available_textures("ExtractedAssets")
    print(f"✅ Found {len(texture_manager.texture_files)} available textures")
    
    # Try to load a specific texture
    if texture_manager.texture_files:
        first_texture_id = list(texture_manager.texture_files.keys())[0]
        texture_path = texture_manager.texture_files[first_texture_id]
        print(f"✅ First texture: ID {first_texture_id} -> {texture_path}")
        
        # Try to load the texture data
        if os.path.exists(texture_path):
            texture_data = dds_loader.load_from_file(texture_path)
            if texture_data is not None:
                print(f"✅ Successfully loaded texture: shape={texture_data.shape}, dtype={texture_data.dtype}")
            else:
                print("❌ Failed to load texture data")
        else:
            print(f"❌ Texture file not found: {texture_path}")
    else:
        print("❌ No textures found")
    
    print("\n🎉 Texture loading test completed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()