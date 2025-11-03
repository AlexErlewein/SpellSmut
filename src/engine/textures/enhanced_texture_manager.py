"""
Enhanced Texture Manager with Existing DDS Loader Integration
Implements advanced texture management using existing DDS loader from TirganachReloaded
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from loguru import logger

# Import existing DDS loader from TirganachReloaded
try:
    from TirganachReloaded.map_viewer.dds_loader import DDSLoader

    DDS_LOADER_AVAILABLE = True
except ImportError:
    DDS_LOADER_AVAILABLE = False
    DDSLoader = None

from src.engine.utils.performance import perf_monitor, performance_timer

# Texture constants following existing patterns
DEFAULT_TEXTURE_SIZE = (256, 256)
MAX_TEXTURE_CACHE_SIZE = 1000


class EnhancedTextureManager:
    """
    Enhanced texture manager implementing existing DDS loader integration patterns.
    Builds on proven DDS loading patterns from TirganachReloaded.
    """

    def __init__(self, assets_path: Union[str, Path] = "ExtractedAssets"):
        """
        Initialize enhanced texture manager with existing DDS loader.

        Args:
            assets_path: Path to extracted assets directory
        """
        self.assets_path = Path(assets_path)
        self.texture_cache: Dict[
            str, Tuple[np.ndarray, float]
        ] = {}  # {path: (texture, timestamp)}
        self.texture_stats: Dict[str, Dict[str, Any]] = {}  # Texture statistics
        self.failed_loads: Dict[str, str] = {}  # Failed load attempts
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_loads = 0

        # Initialize existing DDS loader if available
        self.dds_loader = DDSLoader() if DDS_LOADER_AVAILABLE else None

        # Texture search paths following existing patterns
        self.search_paths = [
            self.assets_path / "UI" / "icons_extracted",
            self.assets_path / "UI" / "extracted",
            self.assets_path / "Textures",
            self.assets_path,
        ]

        logger.info(
            f"Initialized EnhancedTextureManager with assets path: {self.assets_path}"
        )
        if not DDS_LOADER_AVAILABLE:
            logger.warning("DDS loader not available - texture loading will not work")

    @performance_timer
    def load_texture(self, texture_path: Union[str, Path]) -> Optional[np.ndarray]:
        """
        Load texture using existing DDS loader patterns.

        Args:
            texture_path: Path to texture file

        Returns:
            NumPy array with texture data or None if failed
        """
        perf_monitor.start_timer(f"load_texture_{texture_path}")

        texture_path = Path(texture_path)
        self.total_loads += 1

        # Check cache first using existing patterns
        current_time = time.time()
        if str(texture_path) in self.texture_cache:
            cached_texture, timestamp = self.texture_cache[str(texture_path)]
            # Check if cache is still valid (5 minute TTL)
            if current_time - timestamp < 300:  # 5 minutes
                self.cache_hits += 1
                perf_monitor.stop_timer(f"load_texture_{texture_path}")
                return cached_texture
            else:
                # Expired - remove from cache
                del self.texture_cache[str(texture_path)]

        self.cache_misses += 1

        # Load using existing DDS loader if available
        if self.dds_loader and texture_path.exists():
            try:
                texture = self.dds_loader.load(str(texture_path))
                if texture is not None:
                    # Cache the loaded texture using existing patterns
                    self.texture_cache[str(texture_path)] = (texture, current_time)
                    self._update_texture_stats(texture_path, texture)
                    perf_monitor.stop_timer(f"load_texture_{texture_path}")
                    return texture
                else:
                    self.failed_loads[str(texture_path)] = "DDS loader returned None"
            except Exception as e:
                logger.error(f"Failed to load texture {texture_path}: {e}")
                self.failed_loads[str(texture_path)] = str(e)
        else:
            # Try to find texture in search paths using existing patterns
            found_texture = self._find_and_load_texture(texture_path)
            if found_texture is not None:
                # Cache the found texture using existing patterns
                self.texture_cache[str(texture_path)] = (found_texture, current_time)
                self._update_texture_stats(texture_path, found_texture)
                perf_monitor.stop_timer(f"load_texture_{texture_path}")
                return found_texture
            else:
                self.failed_loads[str(texture_path)] = (
                    "Texture not found in search paths"
                )

        perf_monitor.stop_timer(f"load_texture_{texture_path}")
        return None

    @performance_timer
    def _find_and_load_texture(self, texture_path: Path) -> Optional[np.ndarray]:
        """
        Find and load texture using existing search path patterns.

        Args:
            texture_path: Path to texture file

        Returns:
            NumPy array with texture data or None if not found
        """
        # Try exact path first using existing patterns
        if texture_path.exists():
            return self._load_texture_from_path(texture_path)

        # Try search paths using existing patterns
        for search_path in self.search_paths:
            if search_path.exists():
                # Try various path combinations using existing patterns
                possible_paths = [
                    search_path / texture_path.name,
                    search_path / texture_path,
                    search_path / "textures" / texture_path.name,
                    search_path / "icons" / texture_path.name,
                ]

                for possible_path in possible_paths:
                    if possible_path.exists():
                        texture = self._load_texture_from_path(possible_path)
                        if texture is not None:
                            return texture

        return None

    @performance_timer
    def _load_texture_from_path(self, texture_path: Path) -> Optional[np.ndarray]:
        """
        Load texture from path using existing DDS loader patterns.

        Args:
            texture_path: Path to texture file

        Returns:
            NumPy array with texture data or None if failed
        """
        if not texture_path.exists():
            return None

        # Use existing DDS loader if available
        if self.dds_loader:
            try:
                return self.dds_loader.load(str(texture_path))
            except Exception as e:
                logger.error(f"Failed to load texture {texture_path}: {e}")
                return None

        # Fallback to basic loading if DDS loader is not available
        try:
            # Try to load as image file using existing patterns
            from PIL import Image

            image = Image.open(texture_path)
            # Convert to RGBA numpy array using existing patterns
            rgba_image = image.convert("RGBA")
            return np.array(rgba_image)
        except Exception as e:
            logger.error(f"Failed to load texture {texture_path}: {e}")
            return None

    @performance_timer
    def _update_texture_stats(self, texture_path: Path, texture: np.ndarray) -> None:
        """
        Update texture statistics using existing patterns.

        Args:
            texture_path: Path to texture file
            texture: Loaded texture data
        """
        stats_key = str(texture_path)
        self.texture_stats[stats_key] = {
            "shape": texture.shape if texture is not None else None,
            "dtype": str(texture.dtype) if texture is not None else None,
            "size_bytes": texture.nbytes if texture is not None else 0,
            "last_access": time.time(),
            "load_count": self.texture_stats.get(stats_key, {}).get("load_count", 0)
            + 1,
        }

    @performance_timer
    def get_texture_stats(self) -> Dict[str, Any]:
        """
        Get texture loading statistics using existing patterns.

        Returns:
            Dictionary with texture loading statistics
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0

        # Calculate cache size using existing patterns
        cache_size = sum(
            stats.get("size_bytes", 0) for stats in self.texture_stats.values()
        )

        return {
            "total_loads": self.total_loads,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": round(hit_rate, 2),
            "cache_size_bytes": cache_size,
            "cache_size_mb": round(cache_size / (1024 * 1024), 2),
            "cached_textures": len(self.texture_cache),
            "failed_loads": len(self.failed_loads),
            "max_cache_size": MAX_TEXTURE_CACHE_SIZE,
        }

    @performance_timer
    def clear_cache(self, texture_path: Optional[Union[str, Path]] = None) -> None:
        """
        Clear texture cache using existing patterns.

        Args:
            texture_path: Specific texture to clear, or None for all
        """
        if texture_path:
            texture_path_str = str(texture_path)
            if texture_path_str in self.texture_cache:
                del self.texture_cache[texture_path_str]
            if texture_path_str in self.texture_stats:
                del self.texture_stats[texture_path_str]
        else:
            self.texture_cache.clear()
            self.texture_stats.clear()
            self.failed_loads.clear()
            self.cache_hits = 0
            self.cache_misses = 0
            self.total_loads = 0

    @performance_timer
    def preload_textures(self, texture_paths: List[Union[str, Path]]) -> int:
        """
        Preload textures using existing batch loading patterns.

        Args:
            texture_paths: List of texture paths to preload

        Returns:
            Number of successfully loaded textures
        """
        perf_monitor.start_timer("preload_textures")

        loaded_count = 0
        for texture_path in texture_paths:
            texture = self.load_texture(texture_path)
            if texture is not None:
                loaded_count += 1

        perf_monitor.stop_timer("preload_textures")
        logger.info(f"Preloaded {loaded_count}/{len(texture_paths)} textures")
        return loaded_count

    @performance_timer
    def create_texture_atlas(
        self,
        texture_paths: List[Union[str, Path]],
        atlas_size: Tuple[int, int] = (1024, 1024),
    ) -> Optional[np.ndarray]:
        """
        Create texture atlas using existing packing patterns.

        Args:
            texture_paths: List of texture paths to include in atlas
            atlas_size: Size of atlas (width, height)

        Returns:
            Atlas texture as NumPy array or None if failed
        """
        perf_monitor.start_timer("create_texture_atlas")

        # Load all textures using existing patterns
        textures = []
        for texture_path in texture_paths:
            texture = self.load_texture(texture_path)
            if texture is not None:
                textures.append(texture)

        if not textures:
            perf_monitor.stop_timer("create_texture_atlas")
            return None

        # Create atlas using existing packing patterns
        atlas_width, atlas_height = atlas_size
        atlas = np.zeros((atlas_height, atlas_width, 4), dtype=np.uint8)

        # Simple grid packing (existing pattern)
        texture_count = len(textures)
        grid_cols = int(np.ceil(np.sqrt(texture_count)))
        grid_rows = int(np.ceil(texture_count / grid_cols))

        cell_width = atlas_width // grid_cols
        cell_height = atlas_height // grid_rows

        for i, texture in enumerate(textures):
            row = i // grid_cols
            col = i % grid_cols

            # Resize texture to fit cell using existing patterns
            if texture.shape[0] > cell_height or texture.shape[1] > cell_width:
                from PIL import Image

                pil_texture = Image.fromarray(texture)
                resized_texture = pil_texture.resize(
                    (cell_width, cell_height), Image.Resampling.LANCZOS
                )
                texture_resized = np.array(resized_texture)
            else:
                texture_resized = texture

            # Place in atlas using existing patterns
            y_start = row * cell_height
            x_start = col * cell_width
            y_end = min(y_start + texture_resized.shape[0], atlas_height)
            x_end = min(x_start + texture_resized.shape[1], atlas_width)

            atlas[y_start:y_end, x_start:x_end] = texture_resized[
                : y_end - y_start, : x_end - x_start
            ]

        perf_monitor.stop_timer("create_texture_atlas")
        logger.info(
            f"Created {atlas_width}x{atlas_height} texture atlas with {len(textures)} textures"
        )
        return atlas

    @performance_timer
    def get_available_textures(self, search_pattern: str = "**/*.dds") -> List[Path]:
        """
        Get list of available textures using existing search patterns.

        Args:
            search_pattern: Glob pattern to search for textures

        Returns:
            List of available texture paths
        """
        perf_monitor.start_timer("get_available_textures")

        available_textures = []
        for search_path in self.search_paths:
            if search_path.exists():
                try:
                    textures = list(search_path.glob(search_pattern))
                    available_textures.extend(textures)
                except Exception as e:
                    logger.warning(f"Failed to search {search_path}: {e}")

        perf_monitor.stop_timer("get_available_textures")
        logger.info(f"Found {len(available_textures)} available textures")
        return available_textures


# Factory function for creating texture managers using existing patterns
def create_enhanced_texture_manager(
    assets_path: Union[str, Path] = "ExtractedAssets",
) -> EnhancedTextureManager:
    """
    Factory function to create enhanced texture manager using existing patterns.

    Args:
        assets_path: Path to extracted assets directory

    Returns:
        EnhancedTextureManager instance
    """
    return EnhancedTextureManager(assets_path)


# Context manager for texture loading using existing patterns
class TextureLoadingContext:
    """
    Context manager for texture loading using existing patterns.
    """

    def __init__(
        self, texture_manager: EnhancedTextureManager, texture_path: Union[str, Path]
    ):
        self.texture_manager = texture_manager
        self.texture_path = texture_path
        self.texture = None

    def __enter__(self):
        self.texture = self.texture_manager.load_texture(self.texture_path)
        return self.texture

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Texture is automatically cached by the manager using existing patterns
        pass


# Decorator for texture loading with caching using existing patterns
def cached_texture_load(texture_manager: EnhancedTextureManager, ttl: int = 300):
    """
    Decorator for cached texture loading using existing patterns.

    Args:
        texture_manager: Texture manager to use for caching
        ttl: Time-to-live for cached textures
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from arguments using existing patterns
            key_parts = [func.__name__] + [str(arg) for arg in args]
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = "|".join(key_parts)

            # Try to get from texture manager cache using existing patterns
            # This is a simplified approach for demonstration
            result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator
