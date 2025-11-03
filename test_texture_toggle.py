#!/usr/bin/env python3
"""
Test script to verify texture toggle functionality
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}", level="INFO")

def test_texture_toggle():
    """Test that texture toggle functionality works"""
    logger.info("Testing texture toggle functionality...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from TirganachReloaded.map_viewer.map_viewer_window import MapViewerWidget
        
        app = QApplication([])
        
        # Create viewer widget
        viewer = MapViewerWidget()
        
        # Test initial state
        logger.info(f"Initial texture state: {'ON' if viewer.use_textures else 'OFF'}")
        
        # Test toggle method exists
        assert hasattr(viewer, 'toggle_textures'), "toggle_textures method not found"
        logger.info("✓ toggle_textures method exists")
        
        # Test toggle functionality
        initial_state = viewer.use_textures
        viewer.toggle_textures()
        new_state = viewer.use_textures
        
        assert new_state != initial_state, f"Texture state didn't change: {initial_state} -> {new_state}"
        logger.info(f"✓ Texture toggle works: {initial_state} -> {new_state}")
        
        # Test toggle back
        viewer.toggle_textures()
        back_state = viewer.use_textures
        assert back_state == initial_state, f"Texture toggle didn't return to original: {initial_state} -> {back_state}"
        logger.info(f"✓ Texture toggle back works: {new_state} -> {back_state}")
        
        logger.info("✅ All texture toggle tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_texture_toggle()
    sys.exit(0 if success else 1)