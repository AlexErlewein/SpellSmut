"""
Simple Texture Manager for SpellForce terrain textures

Manages loading and caching of terrain textures from extracted DDS files.
For Phase 2 implementation - loads real textures from extracted assets.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from loguru import logger

from .dds_loader import DDSLoader


class SimpleTextureManager:
    """
    Manage terrain textures for map rendering

    Features:
    - Load textures from extracted asset directory
    - Cache loaded textures
    - Provide test textures as fallback
    - Support texture lookup by ID or name

    Usage:
        mgr = SimpleTextureManager()
        mgr.load_available_textures("ExtractedAssets")
        texture = mgr.get_texture(5)  # Get texture by ID
    """

    def __init__(self, texture_size: Tuple[int, int] = (256, 256)):
        """
        Initialize texture manager

        Args:
            texture_size: Target size for all textures (width, height)
        """
        self.texture_size = texture_size
        self.dds_loader = DDSLoader()

        # Storage
        self.texture_files: Dict[int, Path] = {}  # ID -> file path
        self.texture_cache: Dict[int, np.ndarray] = {}  # ID -> texture data
        self.texture_names: List[str] = []  # List of all available texture names

        # Statistics
        self.load_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def load_available_textures(self, base_path: str) -> int:
        """
        Scan for and load available terrain textures
        
        Args:
            base_path: Root directory to search (e.g., "ExtractedAssets")
            
        Returns:
            Number of texture files found
        """
        logger.info(f"Scanning for terrain textures in {base_path}")
        
        # Look for DDS files in the texture directory or directories
        texture_paths = []
        base_dir = Path(base_path)
        
        if base_dir.is_dir() and "sf" in base_dir.name:
            # Single sf directory
            texture_paths = [base_dir]
        else:
            # Search for all sf*/texture directories
            texture_paths = list(base_dir.glob("UI/raw_reextraction/sf*/texture"))
        
        all_dds_files = []
        
        for texture_dir in texture_paths:
            logger.debug(f"Searching in: {texture_dir}")
            # Search for landscape island textures
            pattern = "landscape_island_*.dds"
            dds_files = list(texture_dir.glob(pattern))
            all_dds_files.extend(dds_files)
        
        logger.info(f"Found {len(all_dds_files)} terrain texture files")
        
        # Parse texture IDs from filenames
        for dds_file in all_dds_files:
            # Extract texture ID from filename like "landscape_island_001_based.dds"
            try:
                parts = dds_file.stem.split("_")
                if len(parts) >= 3 and parts[2].isdigit():
                    texture_id = int(parts[2])
                    # Only keep the first occurrence of each texture ID
                    if texture_id not in self.texture_files:
                        self.texture_files[texture_id] = dds_file
                else:
                    logger.warning(f"Could not parse texture ID from: {dds_file.name}")
                    
            except (ValueError, IndexError):
                logger.warning(f"Could not parse texture ID from: {dds_file.name}")
        
        logger.info(f"Mapped {len(self.texture_files)} unique texture IDs")
        
        # Log some examples
        if self.texture_files:
            examples = sorted(self.texture_files.items())[:5]
            for tid, path in examples:
                logger.info(f"  Texture {tid:03d}: {path.name}")
        
        return len(self.texture_files)

    def get_texture(
        self, texture_id: int, use_cache: bool = True
    ) -> Optional[np.ndarray]:
        """
        Get a texture by ID

        Args:
            texture_id: Texture ID (0-119)
            use_cache: Whether to use cached texture if available

        Returns:
            numpy array (height, width, 4) uint8 RGBA, or None if not found
        """
        # Check cache first
        if use_cache and texture_id in self.texture_cache:
            self.cache_hits += 1
            return self.texture_cache[texture_id]

        self.cache_misses += 1

        # Check if we have this texture file
        if texture_id not in self.texture_files:
            logger.warning(f"Texture {texture_id} not found")
            return None

        # Load texture
        filepath = self.texture_files[texture_id]
        logger.debug(f"Loading texture {texture_id} from {filepath.name}")

        texture = self.dds_loader.load(filepath, target_size=self.texture_size)

        if texture is not None:
            # Cache it
            self.texture_cache[texture_id] = texture
            self.load_count += 1
            logger.debug(f"Loaded texture {texture_id}: shape={texture.shape}")
        else:
            logger.error(f"Failed to load texture {texture_id} from {filepath}")

        return texture

    def load_base_textures(
        self, texture_ids: List[int], count: int = 32
    ) -> Dict[int, np.ndarray]:
        """
        Load a set of base textures for a map

        Args:
            texture_ids: List of texture IDs to load
            count: Number of textures to load (default 32)

        Returns:
            Dictionary mapping index (0-31) -> texture data
        """
        logger.info(f"Loading {count} base textures")

        base_textures = {}

        for i in range(min(count, len(texture_ids))):
            texture_id = texture_ids[i]

            # Get texture
            texture = self.get_texture(texture_id)

            if texture is not None:
                base_textures[i] = texture
            else:
                # Create fallback texture
                logger.warning(
                    f"Using fallback texture for index {i} (ID {texture_id})"
                )
                base_textures[i] = self.create_fallback_texture(i)

        logger.info(f"Loaded {len(base_textures)} base textures")

        return base_textures

    def create_fallback_texture(self, index: int) -> np.ndarray:
        """
        Create a fallback test texture with distinct color

        Args:
            index: Texture index (used to determine color)

        Returns:
            numpy array (height, width, 4) uint8
        """
        # Generate distinct color based on index
        hue = (index * 360 / 32) % 360

        # Convert HSV to RGB
        h = hue / 60.0
        c = 200  # Slightly muted colors
        x = int(c * (1 - abs(h % 2 - 1)))

        if 0 <= h < 1:
            r, g, b = c, x, 0
        elif 1 <= h < 2:
            r, g, b = x, c, 0
        elif 2 <= h < 3:
            r, g, b = 0, c, x
        elif 3 <= h < 4:
            r, g, b = 0, x, c
        elif 4 <= h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return self.dds_loader.create_test_texture(self.texture_size, (r, g, b, 255))

    def create_test_texture_set(self, count: int = 32) -> Dict[int, np.ndarray]:
        """
        Create a set of test textures with distinct colors

        Args:
            count: Number of textures to create

        Returns:
            Dictionary mapping index -> texture data
        """
        logger.info(f"Creating {count} test textures")

        textures = {}
        for i in range(count):
            textures[i] = self.create_fallback_texture(i)

        return textures

    def get_statistics(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "available_textures": len(self.texture_files),
            "cached_textures": len(self.texture_cache),
            "load_count": self.load_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": (self.cache_hits / (self.cache_hits + self.cache_misses) * 100)
            if (self.cache_hits + self.cache_misses) > 0
            else 0,
        }

    def clear_cache(self):
        """Clear cached textures to free memory"""
        logger.info(f"Clearing texture cache ({len(self.texture_cache)} textures)")
        self.texture_cache.clear()

    def preload_all(self) -> int:
        """
        Preload all available textures into cache

        Returns:
            Number of textures successfully loaded
        """
        logger.info(f"Preloading all {len(self.texture_files)} textures")

        success_count = 0
        for texture_id in sorted(self.texture_files.keys()):
            texture = self.get_texture(texture_id, use_cache=False)
            if texture is not None:
                success_count += 1

        logger.info(f"Preloaded {success_count}/{len(self.texture_files)} textures")

        return success_count


# Convenience functions
def create_simple_texture_manager(
    assets_path: str = "ExtractedAssets",
) -> SimpleTextureManager:
    """
    Create and initialize a texture manager

    Args:
        assets_path: Path to extracted assets directory

    Returns:
        Initialized SimpleTextureManager
    """
    mgr = SimpleTextureManager()
    mgr.load_available_textures(assets_path)
    return mgr
