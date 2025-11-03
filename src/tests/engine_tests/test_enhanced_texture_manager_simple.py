"""
Simple tests for Enhanced Texture Manager core logic (without any texture loading)
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.engine.textures.enhanced_texture_manager import (
    EnhancedTextureManager,
    TextureLoadingContext,
    cached_texture_load,
    create_enhanced_texture_manager,
)


class TestEnhancedTextureManagerCoreLogic:
    """Test enhanced texture manager core logic without any texture loading"""

    @pytest.fixture
    def texture_manager(self):
        """Fixture providing texture manager instance"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tm = EnhancedTextureManager(assets_path=temp_dir)
            yield tm

    def test_texture_manager_creation(self):
        """Test texture manager can be created"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tm = EnhancedTextureManager(assets_path=temp_dir)
            assert tm is not None
            assert tm.assets_path == Path(temp_dir)

    def test_get_texture_stats(self, texture_manager):
        """Test getting texture statistics"""
        # Get initial stats
        stats = texture_manager.get_texture_stats()
        assert isinstance(stats, dict)
        assert "total_loads" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "hit_rate" in stats
        assert "cache_size_bytes" in stats
        assert "cached_textures" in stats
        assert "failed_loads" in stats

        # Check initial values
        assert stats["total_loads"] == 0
        assert stats["cache_hits"] == 0
        assert stats["cache_misses"] == 0
        assert stats["hit_rate"] == 0
        assert stats["cache_size_bytes"] == 0
        assert stats["cached_textures"] == 0
        assert stats["failed_loads"] == 0

    def test_clear_cache(self, texture_manager):
        """Test clearing texture cache"""
        # Add some data to cache
        mock_texture = np.random.rand(256, 256, 4).astype(np.uint8)
        texture_path = Path("test_texture.dds")
        texture_manager.texture_cache[str(texture_path)] = (mock_texture, 0)
        texture_manager.texture_stats[str(texture_path)] = {
            "size_bytes": mock_texture.nbytes
        }
        texture_manager.failed_loads[str(texture_path)] = "test error"

        # Verify cache has data
        assert len(texture_manager.texture_cache) == 1
        assert len(texture_manager.texture_stats) == 1
        assert len(texture_manager.failed_loads) == 1

        # Clear cache
        texture_manager.clear_cache()

        # Verify cache is empty
        assert len(texture_manager.texture_cache) == 0
        assert len(texture_manager.texture_stats) == 0
        assert len(texture_manager.failed_loads) == 0

    def test_factory_function(self):
        """Test texture manager factory function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tm = create_enhanced_texture_manager(temp_dir)
            assert isinstance(tm, EnhancedTextureManager)
            assert tm.assets_path == Path(temp_dir)

    def test_texture_search_paths(self, texture_manager):
        """Test texture search paths are properly set up"""
        assert len(texture_manager.search_paths) > 0
        for path in texture_manager.search_paths:
            assert isinstance(path, Path)

    def test_context_manager_creation(self, texture_manager):
        """Test context manager can be created"""
        texture_path = Path("test_texture.dds")
        context = TextureLoadingContext(texture_manager, texture_path)
        assert context is not None
        assert context.texture_manager == texture_manager
        assert context.texture_path == texture_path

    def test_cached_texture_load_decorator(self, texture_manager):
        """Test cached texture load decorator can be created"""
        # Test decorator creation
        decorator = cached_texture_load(texture_manager, ttl=300)
        assert decorator is not None

        # Test that it returns a function
        def test_func():
            return "test"

        decorated_func = decorator(test_func)
        assert decorated_func is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
