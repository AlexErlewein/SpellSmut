#!/usr/bin/env python3
"""
Test script to verify texture loading and rendering
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}", level="INFO")

def test_texture_loading():
    """Test that textures are loaded correctly"""
    logger.info("Testing texture loading...")
    
    try:
        from TirganachReloaded.map_viewer.simple_texture_manager import SimpleTextureManager
        
        # Create texture manager
        tm = SimpleTextureManager()
        
        # Try to load from ExtractedAssets
        assets_path = Path("ExtractedAssets")
        if not assets_path.exists():
            assets_path = Path("../../ExtractedAssets")
        
        if not assets_path.exists():
            logger.error(f"ExtractedAssets not found at {assets_path}")
            return False
            
        # Load available textures
        count = tm.load_available_textures(str(assets_path))
        logger.info(f"Found {count} terrain textures")
        
        if count == 0:
            logger.error("No terrain textures found!")
            return False
            
        # Try to load a few textures
        test_ids = sorted(tm.texture_files.keys())[:5]
        for tid in test_ids:
            texture = tm.get_texture(tid)
            if texture is not None:
                logger.info(f"✓ Loaded texture {tid}: shape={texture.shape}")
            else:
                logger.error(f"✗ Failed to load texture {tid}")
                return False
                
        # Get statistics
        stats = tm.get_statistics()
        logger.info(f"Statistics: {stats}")
        
        logger.info("✅ Texture loading test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_texture_loading()
    sys.exit(0 if success else 1)