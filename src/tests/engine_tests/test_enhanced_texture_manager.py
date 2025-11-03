"""
Tests for Enhanced Texture Manager with Existing DDS Loader Integration
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from src.engine.textures.enhanced_texture_manager import (
    EnhancedTextureManager,
    TextureLoadingContext,
    cached_texture_load,
    create_enhanced_texture_manager,
)


class TestEnhancedTextureManager:
    """Test enhanced texture manager with existing DDS loader integration"""

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

    def test_load_texture_cache_hit(self, texture_manager):
        """Test texture caching works correctly"""
        # Create mock texture
        mock_texture = np.random.rand(256, 256, 4).astype(np.uint8)

        # Mock DDS loader
        with patch.object(texture_manager, "dds_loader") as mock_loader:
            mock_loader.load.return_value = mock_texture

            # Load texture
            texture_path = Path("test_texture.dds")
            result1 = texture_manager.load_texture(texture_path)
            assert result1 is not None
            assert np.array_equal(result1, mock_texture)

            # Load same texture again (should be cache hit)
            result2 = texture_manager.load_texture(texture_path)
            assert result2 is not None
            assert np.array_equal(result2, mock_texture)

            # Cache should have 1 hit
            stats = texture_manager.get_texture_stats()
            assert stats["cache_hits"] == 1
            assert stats["cache_misses"] == 1  # First load was a miss

    def test_load_texture_cache_miss(self, texture_manager):
        """Test texture cache miss handling"""
        # Create two different mock textures
        mock_texture1 = np.random.rand(256, 256, 4).astype(np.uint8)
        mock_texture2 = np.random.rand(256, 256, 4).astype(np.uint8)

        # Mock DDS loader to return different textures
        with patch.object(texture_manager, "dds_loader") as mock_loader:
            mock_loader.load.side_effect = [mock_texture1, mock_texture2]

            # Load first texture
            texture_path1 = Path("test_texture1.dds")
            result1 = texture_manager.load_texture(texture_path1)
            assert result1 is not None
            assert np.array_equal(result1, mock_texture1)

            # Load second texture (should be cache miss)
            texture_path2 = Path("test_texture2.dds")
            result2 = texture_manager.load_texture(texture_path2)
            assert result2 is not None
            assert np.array_equal(result2, mock_texture2)

            # Cache should have 2 misses
            stats = texture_manager.get_texture_stats()
            assert stats["cache_misses"] == 2

    def test_find_and_load_texture(self, texture_manager):
        """Test texture search functionality"""
        # Create mock texture
        mock_texture = np.random.rand(256, 256, 4).astype(np.uint8)

        # Mock DDS loader
        with patch.object(texture_manager, "dds_loader") as mock_loader:
            mock_loader.load.return_value = mock_texture

            # Test finding texture in search paths
            texture_path = Path("test_texture.dds")
            result = texture_manager._find_and_load_texture(texture_path)
            # Should return None since file doesn't exist in search paths
            assert result is None

    def test_load_texture_from_path(self, texture_manager):
        """Test loading texture from specific path"""
        # Create mock texture
        mock_texture = np.random.rand(256, 256, 4).astype(np.uint8)

        # Mock DDS loader
        with patch.object(texture_manager, "dds_loader") as mock_loader:
            mock_loader.load.return_value = mock_texture

            # Try to load from non-existent path
            texture_path = Path("/non/existent/texture.dds")
            result = texture_manager._load_texture_from_path(texture_path)
            assert result is None  # Should return None for non-existent file

    def test_update_texture_stats(self, texture_manager):
        """Test texture statistics updating"""
        # Create mock texture
        mock_texture = np.random.rand(256, 256, 4).astype(np.uint8)
        texture_path = Path("test_texture.dds")

        # Update stats
        texture_manager._update_texture_stats(texture_path, mock_texture)

        # Check stats were updated
        stats_key = str(texture_path)
        assert stats_key in texture_manager.texture_stats
        stats = texture_manager.texture_stats[stats_key]
        assert stats["shape"] == mock_texture.shape
        assert stats["dtype"] == str(mock_texture.dtype)
        assert stats["size_bytes"] == mock_texture.nbytes

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

    def test_clear_specific_cache_entry(self, texture_manager):
        """Test clearing specific cache entry"""
        # Add two entries to cache
        mock_texture1 = np.random.rand(256, 256, 4).astype(np.uint8)
        mock_texture2 = np.random.rand(256, 256, 4).astype(np.uint8)

        texture_path1 = Path("test_texture1.dds")
        texture_path2 = Path("test_texture2.dds")

        texture_manager.texture_cache[str(texture_path1)] = (mock_texture1, 0)
        texture_manager.texture_cache[str(texture_path2)] = (mock_texture2, 0)

        # Clear one entry
        texture_manager.clear_cache(texture_path1)

        # Verify only one entry remains
        assert len(texture_manager.texture_cache) == 1
        assert str(texture_path2) in texture_manager.texture_cache
        assert str(texture_path1) not in texture_manager.texture_cache

    def test_preload_textures(self, texture_manager):
        """Test preloading textures"""
        # Create mock textures
        mock_texture = np.random.rand(256, 256, 4).astype(np.uint8)

        # Mock DDS loader
        with patch.object(texture_manager, "dds_loader") as mock_loader:
            mock_loader.load.return_value = mock_texture

            # Preload textures
            texture_paths = [Path("texture1.dds"), Path("texture2.dds")]
            loaded_count = texture_manager.preload_textures(texture_paths)

            # Should have loaded 2 textures
            assert loaded_count == 2

    def test_create_texture_atlas(self, texture_manager):
        """Test creating texture atlas"""
        # Create mock textures
        mock_texture1 = np.random.rand(64, 64, 4).astype(np.uint8)
        mock_texture2 = np.random.rand(64, 64, 4).astype(np.uint8)

        # Mock DDS loader
        with patch.object(texture_manager, "dds_loader") as mock_loader:
            mock_loader.load.side_effect = [mock_texture1, mock_texture2]

            # Create atlas
            texture_paths = [Path("texture1.dds"), Path("texture2.dds")]
            atlas = texture_manager.create_texture_atlas(
                texture_paths, atlas_size=(128, 128)
            )

            # Should have created atlas
            assert atlas is not None
            assert atlas.shape == (128, 128, 4)

    def test_get_available_textures(self, texture_manager):
        """Test getting available textures"""
        # Create some fake texture files in temp directory
        assets_dir = Path(texture_manager.assets_path)
        ui_dir = assets_dir / "UI" / "icons_extracted"
        ui_dir.mkdir(parents=True, exist_ok=True)

        # Create fake DDS files
        (ui_dir / "texture1.dds").touch()
        (ui_dir / "texture2.dds").touch()
        (ui_dir / "texture3.png").touch()  # Non-DDS file

        # Get available textures
        textures = texture_manager.get_available_textures()

        # Should find DDS files
        dds_textures = [t for t in textures if t.suffix.lower() == ".dds"]
        assert len(dds_textures) >= 2

    def test_factory_function(self):
        """Test texture manager factory function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tm = create_enhanced_texture_manager(temp_dir)
            assert isinstance(tm, EnhancedTextureManager)
            assert tm.assets_path == Path(temp_dir)

    def test_context_manager(self, texture_manager):
        """Test texture loading context manager"""
        # Create mock texture
        mock_texture = np.random.rand(256, 256, 4).astype(np.uint8)

        # Mock DDS loader
        with patch.object(texture_manager, "dds_loader") as mock_loader:
            mock_loader.load.return_value = mock_texture

            # Use context manager
            texture_path = Path("test_texture.dds")
            with TextureLoadingContext(texture_manager, texture_path) as texture:
                assert texture is not None
                assert np.array_equal(texture, mock_texture)

    def test_cached_texture_load_decorator(self, texture_manager):
        """Test cached texture load decorator"""
        # Create mock texture
        mock_texture = np.random.rand(256, 256, 4).astype(np.uint8)

        # Mock DDS loader
        with patch.object(texture_manager, "dds_loader") as mock_loader:
            mock_loader.load.return_value = mock_texture

            # Create decorated function
            @cached_texture_load(texture_manager)
            def load_test_texture(texture_path):
                return texture_manager.load_texture(texture_path)

            # Call decorated function
            texture_path = Path("test_texture.dds")
            result = load_test_texture(texture_path)
            assert result is not None
            assert np.array_equal(result, mock_texture)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
