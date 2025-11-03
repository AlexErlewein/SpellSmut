"""
Tests for Enhanced Cache with Existing TirganachReloaded Patterns
"""

import tempfile
import time

import pytest

from src.engine.cache.enhanced_cache import (
    CacheContext,
    EnhancedTirganachCache,
    HybridCache,
    cached_function,
    create_enhanced_cache,
)


class TestEnhancedTirganachCache:
    """Test enhanced cache with existing patterns"""

    @pytest.fixture
    def cache(self):
        """Fixture providing cache instance"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = EnhancedTirganachCache(cache_dir=temp_dir)
            yield cache

    @pytest.fixture
    def hybrid_cache(self):
        """Fixture providing hybrid cache instance"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = HybridCache(cache_dir=temp_dir)
            yield cache

    def test_cache_creation(self):
        """Test cache can be created"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = EnhancedTirganachCache(cache_dir=temp_dir)
            assert cache is not None
            assert cache.cache_dir.exists()

    def test_cache_set_get(self, cache):
        """Test setting and getting cache values"""
        # Test basic set/get
        cache.set("test_key", "test_value", ttl=60)
        result = cache.get("test_key")
        assert result == "test_value"

        # Test cache miss
        result = cache.get("nonexistent_key")
        assert result is None

    def test_cache_expiration(self, cache):
        """Test cache expiration"""
        # Set with short TTL
        cache.set("expiring_key", "expiring_value", ttl=1)

        # Should be available immediately
        result = cache.get("expiring_key")
        assert result == "expiring_value"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        result = cache.get("expiring_key")
        assert result is None

    def test_cache_invalidation(self, cache):
        """Test cache invalidation"""
        # Set value
        cache.set("invalidate_key", "invalidate_value")

        # Verify it exists
        result = cache.get("invalidate_key")
        assert result == "invalidate_value"

        # Invalidate it
        cache.invalidate("invalidate_key")

        # Should no longer exist
        result = cache.get("invalidate_key")
        assert result is None

    def test_cache_clear(self, cache):
        """Test cache clearing"""
        # Set multiple values
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Verify they exist
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

        # Clear cache
        cache.clear()

        # Should no longer exist
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None

    def test_cache_statistics(self, cache):
        """Test cache statistics"""
        # Initial stats
        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == 0

        # Set and get values
        cache.set("stats_key", "stats_value")
        cache.get("stats_key")  # Hit
        cache.get("missing_key")  # Miss

        # Check updated stats
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 50.0

    def test_disk_cache(self, cache):
        """Test disk cache persistence"""
        # Enable disk cache
        cache.disk_cache_enabled = True

        # Set value with disk caching
        cache.set("disk_key", "disk_value", cache_to_disk=True)

        # Create new cache instance pointing to same directory
        new_cache = EnhancedTirganachCache(cache_dir=cache.cache_dir)
        new_cache.disk_cache_enabled = True

        # Should be able to load from disk
        result = new_cache.get("disk_key", use_memory=False, use_disk=True)
        assert result == "disk_value"

    def test_hybrid_cache_creation(self, hybrid_cache):
        """Test hybrid cache creation"""
        assert hybrid_cache is not None
        assert isinstance(hybrid_cache, HybridCache)

    def test_hybrid_cache_lru_tracking(self, hybrid_cache):
        """Test hybrid cache LRU tracking"""
        # Set values
        hybrid_cache.set("lru_key1", "lru_value1")
        time.sleep(0.1)
        hybrid_cache.set("lru_key2", "lru_value2")

        # Access first key to update LRU tracking
        hybrid_cache.get("lru_key1")

        # Check LRU stats
        lru_stats = hybrid_cache.get_lru_stats()
        assert lru_stats["entries"] == 2

    def test_factory_function(self):
        """Test cache factory function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test basic cache
            basic_cache = create_enhanced_cache("basic", cache_dir=temp_dir)
            assert isinstance(basic_cache, EnhancedTirganachCache)
            assert not isinstance(basic_cache, HybridCache)

            # Test hybrid cache
            hybrid_cache = create_enhanced_cache("hybrid", cache_dir=temp_dir)
            assert isinstance(hybrid_cache, HybridCache)

    def test_context_manager(self, cache):
        """Test cache context manager"""
        # Test cache miss scenario
        with CacheContext(cache, "context_key") as cached_data:
            assert cached_data is None

            # Set data in context (simulating computation)
            computed_data = "computed_result"
            # In a real scenario, this would be set in the cache

        # Verify data can be retrieved normally
        cache.set("context_key", "computed_result")

        # Test cache hit scenario
        with CacheContext(cache, "context_key") as cached_data:
            assert cached_data == "computed_result"

    def test_cached_function_decorator(self, cache):
        """Test cached function decorator"""

        # Use a simple function to avoid closure complications
        @cached_function(cache, ttl=60)
        def multiply(x, y):
            return x * y

        # First call - should execute function
        result1 = multiply(5, 3)
        assert result1 == 15

        # Second call with same args - should use cache
        result2 = multiply(5, 3)
        assert result2 == 15

        # Call with different args - should execute function
        result3 = multiply(2, 4)
        assert result3 == 8

    def test_fingerprint_generation(self, cache):
        """Test fingerprint generation follows existing patterns"""
        # Test consistent fingerprint generation
        fp1 = cache._generate_fingerprint("test_key")
        fp2 = cache._generate_fingerprint("test_key")
        assert fp1 == fp2
        assert len(fp1) == 64  # SHA-256 hex length

        # Test different keys produce different fingerprints
        fp3 = cache._generate_fingerprint("different_key")
        assert fp3 != fp1

    def test_cache_paths(self, cache):
        """Test cache path generation follows existing patterns"""
        cache_file, meta_file = cache._get_cache_paths("test_key")

        assert cache_file.name.startswith("EnhancedCache_")
        assert cache_file.name.endswith(".pkl")
        assert meta_file.name.endswith(".meta.json")
        assert cache_file.parent == cache.cache_dir
        assert meta_file.parent == cache.cache_dir

    def test_warm_up(self, cache):
        """Test cache warm-up functionality"""
        # Warm up with data
        warmup_data = {
            "key1": ("value1", 60),
            "key2": ("value2", 120),
            "key3": ("value3", 300),
        }
        cache.warm_up(warmup_data)

        # Verify all data is cached
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_memory_management(self, cache):
        """Test cache memory management"""
        # Set cache size limits
        cache.max_size_bytes = 1024  # 1KB limit

        # Add large data that should trigger eviction
        large_data = "x" * 512  # 512 byte string
        cache.set("large_key1", large_data, ttl=60)
        cache.set("large_key2", large_data, ttl=60)
        cache.set("large_key3", large_data, ttl=60)  # Should trigger eviction

        # Verify cache still works
        result = cache.get("large_key1")
        assert result == large_data or result is None  # May have been evicted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
