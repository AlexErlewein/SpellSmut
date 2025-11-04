#!/usr/bin/env python3
"""
Debug script to check texture loading issues
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from TirganachReloaded.map_viewer.map_viewer_window import MapViewerWidget
    from PySide6.QtWidgets import QApplication
    print("✅ Imports successful")
    
    # Create a minimal Qt application for testing
    app = QApplication([])
    
    # Create map viewer widget to test texture initialization
    viewer = MapViewerWidget()
    
    print("=== Texture Manager Debug ===")
    print(f"texture_manager: {viewer.texture_manager}")
    print(f"textures_loaded: {viewer.textures_loaded}")
    print(f"use_textures: {viewer.use_textures}")
    print(f"texture_ids: {len(viewer.texture_ids) if viewer.texture_ids else 0}")
    print(f"base_textures: {len(viewer.base_textures) if viewer.base_textures else 0}")
    print(f"texture_id_map: {len(viewer.texture_id_map) if viewer.texture_id_map else 0}")
    print(f"texture_map: {len(viewer.texture_map) if viewer.texture_map else 0}")
    
    # Check the condition that determines if textures are shown
    has_texture_mapping = bool(
        viewer.texture_map
        and viewer.textures_loaded
        and viewer.use_textures
        and len(viewer.texture_ids) > 0
    )
    
    print("\n=== Texture Mapping Condition ===")
    print(f"viewer.texture_map: {bool(viewer.texture_map)}")
    print(f"viewer.textures_loaded: {viewer.textures_loaded}")
    print(f"viewer.use_textures: {viewer.use_textures}")
    print(f"len(viewer.texture_ids) > 0: {len(viewer.texture_ids) > 0 if viewer.texture_ids else False}")
    print(f"Final has_texture_mapping: {has_texture_mapping}")
    
    # Check fallback condition
    fallback_condition = bool(
        viewer.textures_loaded
        and viewer.use_textures
        and len(viewer.texture_ids) > 0
    )
    
    print("\n=== Fallback Condition ===")
    print(f"viewer.textures_loaded: {viewer.textures_loaded}")
    print(f"viewer.use_textures: {viewer.use_textures}")
    print(f"len(viewer.texture_ids) > 0: {len(viewer.texture_ids) > 0 if viewer.texture_ids else False}")
    print(f"Final fallback_condition: {fallback_condition}")
    
    print("\n=== Issues Found ===")
    if not viewer.texture_manager:
        print("❌ Texture manager not initialized")
    elif not viewer.textures_loaded:
        print("❌ Textures not loaded to OpenGL")
    elif not viewer.use_textures:
        print("❌ Textures disabled")
    elif len(viewer.texture_ids) == 0:
        print("❌ No OpenGL texture IDs")
    elif not viewer.texture_map:
        print("⚠️  No texture mapping (will use fallback)")
    else:
        print("✅ All texture conditions satisfied")
    
    app.quit()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
