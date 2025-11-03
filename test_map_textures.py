#!/usr/bin/env python3
"""
Test texture toggle with actual map loading
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}", level="DEBUG")

def test_map_with_textures():
    """Test loading a map and toggling textures"""
    logger.info("Testing map loading with texture toggle...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from TirganachReloaded.map_viewer.map_viewer_window import MapViewerWindow
        from TirganachReloaded.map_viewer.simple_map_loader import SimpleMapLoader
        
        app = QApplication([])
        
        # Create window and viewer
        window = MapViewerWindow()
        viewer = window.viewer
        
        # Test with a small map
        map_path = Path("OriginalGameFiles/map/lanfreegame/Coop_01_rpg.map")
        if not map_path.exists():
            logger.error(f"Test map not found: {map_path}")
            return False
            
        # Load map
        logger.info(f"Loading map: {map_path}")
        success = viewer.load_map(map_path)
        
        if not success:
            logger.error("Failed to load map")
            return False
            
        logger.info("✓ Map loaded successfully")
        
        # Test texture toggle
        logger.info(f"Initial texture state: {'ON' if viewer.use_textures else 'OFF'}")
        logger.info(f"Textures loaded: {viewer.textures_loaded}")
        logger.info(f"Texture IDs available: {len(viewer.texture_ids)}")
        logger.info(f"Texture ID mappings: {len(viewer.texture_id_map)}")
        
        # Toggle textures
        viewer.toggle_textures()
        logger.info(f"After toggle: {'ON' if viewer.use_textures else 'OFF'}")
        
        # Toggle back
        viewer.toggle_textures()
        logger.info(f"After toggle back: {'ON' if viewer.use_textures else 'OFF'}")
        
        logger.info("✅ Map loading with texture toggle test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_map_with_textures()
    sys.exit(0 if success else 1)