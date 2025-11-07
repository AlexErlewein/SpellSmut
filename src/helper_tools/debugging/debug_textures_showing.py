#!/usr/bin/env python3
"""
Debug script to check why textures aren't showing
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
        viewer.textures_loaded
        and viewer.use_textures
        and len(viewer.texture_ids) > 0
    )
    
    print("\n=== Texture Mapping Condition ===")
    print(f"viewer.textures_loaded: {viewer.textures_loaded}")
    print(f"viewer.use_textures: {viewer.use_textures}")
    print(f"len(viewer.texture_ids) > 0: {len(viewer.texture_ids) > 0 if viewer.texture_ids else False}")
    print(f"Final has_texture_mapping: {has_texture_mapping}")
    
    print("\n=== Issues Found ===")
    if not viewer.texture_manager:
        print("❌ Texture manager not initialized")
    elif not viewer.textures_loaded:
        print("❌ Textures not loaded to OpenGL")
    elif not viewer.use_textures:
        print("❌ Textures disabled")
    elif len(viewer.texture_ids) == 0:
        print("❌ No texture IDs generated")
    else:
        print("✅ All texture conditions should be met")
        
    # Try to initialize OpenGL context to check texture upload
    print("\n=== Trying to initialize OpenGL ===")
    viewer.show()  # This should trigger OpenGL initialization
    app.processEvents()  # Process events to ensure OpenGL is ready
    
    print(f"After OpenGL init - textures_loaded: {viewer.textures_loaded}")
    print(f"After OpenGL init - texture_ids: {len(viewer.texture_ids) if viewer.texture_ids else 0}")
    
    if viewer.texture_ids:
        print(f"First few texture IDs: {viewer.texture_ids[:3]}")
    
    print("\n=== Debug Complete ===")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
