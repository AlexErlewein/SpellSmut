"""
Enhanced Cache with Existing TirganachReloaded Patterns
Implements advanced caching using proven existing patterns from TirganachReloaded
"""

import hashlib
import json
import logging
import pickle
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from src.engine.utils.performance import perf_monitor

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata"""

    data: Any
    timestamp: float
    access_count: int
    size_bytes: int
    ttl: int = 300  # 5 minutes default TTL


class EnhancedTirganachCache:
    """
    Enhanced cache implementing proven patterns from TirganachReloaded.
    Builds on existing fingerprinting, serialization, and validation patterns.
    """

    # Cache version matching existing pattern
    CACHE_VERSION = "1.0.0"

    def __init__(self, cache_dir: Union[str, Path] = None, max_size_mb: int = 100):
        """
        Initialize enhanced cache with existing patterns.

        Args:
            cache_dir: Directory for cache files (defaults to system temp)
            max_size_mb: Maximum cache size in MB
        """
        # Use existing cache directory patterns
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Use existing pattern for default cache directory
            self.cache_dir = Path.home() / ".spellsmut" / "cache"

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.disk_cache_enabled = True

        # Track cache statistics using existing patterns
        self.hits = 0
        self.misses = 0
        self.evictions = 0

        logger.info(f"Initialized EnhancedTirganachCache at {self.cache_dir}")

    def get(
        self, key: str, use_memory: bool = True, use_disk: bool = True
    ) -> Optional[Any]:
        """
        Get cached data using existing validation patterns.

        Args:
            key: Cache key
            use_memory: Whether to check memory cache
            use_disk: Whether to check disk cache

        Returns:
            Cached data or None if not found/expired
        """
        perf_monitor.start_timer(f"cache_get_{key}")

        current_time = time.time()

        # Check memory cache first using existing patterns
        if use_memory and key in self.memory_cache:
            entry = self.memory_cache[key]

            # Check TTL expiration using existing patterns
            if current_time - entry.timestamp < entry.ttl:
                # Update access count using existing patterns
                entry.access_count += 1
                self.hits += 1
                perf_monitor.stop_timer(f"cache_get_{key}")
                return entry.data
            else:
                # Expired entry - remove it using existing patterns
                del self.memory_cache[key]
                self.evictions += 1

        # Check disk cache using existing patterns
        if use_disk:
            disk_data = self._load_from_disk_cache(key)
            if disk_data is not None:
                data, timestamp, ttl = disk_data

                # Check TTL using existing patterns
                if current_time - timestamp < ttl:
                    # Cache in memory for faster future access using existing patterns
                    size_bytes = len(pickle.dumps(data)) if data else 0
                    self.memory_cache[key] = CacheEntry(
                        data=data,
                        timestamp=timestamp,
                        access_count=1,
                        size_bytes=size_bytes,
                        ttl=ttl,
                    )
                    self.hits += 1
                    perf_monitor.stop_timer(f"cache_get_{key}")
                    return data
                else:
                    # Expired - remove disk cache file using existing patterns
                    self._remove_disk_cache(key)

        self.misses += 1
        perf_monitor.stop_timer(f"cache_get_{key}")
        return None

    def set(
        self, key: str, data: Any, ttl: int = 300, cache_to_disk: bool = True
    ) -> None:
        """
        Set cached data using existing serialization patterns.

        Args:
            key: Cache key
            data: Data to cache
            ttl: Time-to-live in seconds
            cache_to_disk: Whether to also cache to disk
        """
        perf_monitor.start_timer(f"cache_set_{key}")

        current_time = time.time()

        # Cache in memory using existing patterns
        size_bytes = len(pickle.dumps(data)) if data else 0
        self.memory_cache[key] = CacheEntry(
            data=data,
            timestamp=current_time,
            access_count=1,
            size_bytes=size_bytes,
            ttl=ttl,
        )

        # Cache to disk using existing patterns
        if cache_to_disk and self.disk_cache_enabled:
            self._save_to_disk_cache(key, data, current_time, ttl)

        # Manage cache size using existing patterns
        self._manage_cache_size()

        perf_monitor.stop_timer(f"cache_set_{key}")

    def _save_to_disk_cache(
        self, key: str, data: Any, timestamp: float, ttl: int
    ) -> None:
        """
        Save to disk cache using existing serialization patterns.

        Args:
            key: Cache key
            data: Data to cache
            timestamp: Creation timestamp
            ttl: Time-to-live
        """
        try:
            # Use existing cache path patterns
            cache_file, meta_file = self._get_cache_paths(key)

            # Save metadata using existing patterns
            meta = {
                "cache_version": self.CACHE_VERSION,
                "created_at": timestamp,
                "ttl": ttl,
                "key": key,
                "data_size": len(pickle.dumps(data)) if data else 0,
            }

            with open(meta_file, "w") as f:
                json.dump(meta, f, indent=2)

            # Save pickled data using existing patterns
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)

        except Exception as e:
            logger.warning(f"Failed to save to disk cache: {e}")

    def _load_from_disk_cache(self, key: str) -> Optional[Tuple[Any, float, int]]:
        """
        Load from disk cache using existing validation patterns.

        Args:
            key: Cache key

        Returns:
            Tuple of (data, timestamp, ttl) or None if not found/invalid
        """
        try:
            cache_file, meta_file = self._get_cache_paths(key)

            if not cache_file.exists() or not meta_file.exists():
                return None

            # Load and validate metadata using existing patterns
            with open(meta_file, "r") as f:
                meta = json.load(f)

            cached_version = meta.get("cache_version")
            if cached_version != self.CACHE_VERSION:
                # Version mismatch - invalidate cache using existing patterns
                self._remove_disk_cache(key)
                return None

            # Load pickled data using existing patterns
            with open(cache_file, "rb") as f:
                data = pickle.load(f)

            timestamp = meta.get("created_at", time.time())
            ttl = meta.get("ttl", 300)

            return data, timestamp, ttl

        except Exception as e:
            logger.warning(f"Failed to load from disk cache: {e}")
            # Remove invalid cache files using existing patterns
            self._remove_disk_cache(key)
            return None

    def _get_cache_paths(self, key: str) -> Tuple[Path, Path]:
        """
        Get cache file paths using existing fingerprint patterns.

        Args:
            key: Cache key

        Returns:
            Tuple of (cache_file, meta_file) paths
        """
        # Use existing fingerprinting pattern for cache file names
        fingerprint = self._generate_fingerprint(key)
        cache_file = self.cache_dir / f"EnhancedCache_{fingerprint}.pkl"
        meta_file = self.cache_dir / f"EnhancedCache_{fingerprint}.meta.json"
        return cache_file, meta_file

    def _generate_fingerprint(self, key: str) -> str:
        """
        Generate fingerprint using existing hashing patterns.

        Args:
            key: Key to fingerprint

        Returns:
            SHA-256 hash as hex string
        """
        # Use existing SHA-256 pattern
        return hashlib.sha256(key.encode()).hexdigest()

    def _manage_cache_size(self) -> None:
        """Manage cache size using existing LRU patterns."""
        # Calculate current memory cache size using existing patterns
        current_size = sum(entry.size_bytes for entry in self.memory_cache.values())

        # If we're over the limit, evict least recently used entries using existing patterns
        if current_size > self.max_size_bytes:
            # Sort by access count (ascending) and timestamp (oldest first) using existing patterns
            sorted_entries = sorted(
                self.memory_cache.items(),
                key=lambda x: (x[1].access_count, x[1].timestamp),
            )

            # Remove entries until we're under the limit using existing patterns
            removed_size = 0
            for key, entry in sorted_entries:
                if current_size - removed_size <= self.max_size_bytes:
                    break

                del self.memory_cache[key]
                removed_size += entry.size_bytes
                self.evictions += 1

    def _remove_disk_cache(self, key: str) -> None:
        """Remove disk cache files using existing patterns."""
        try:
            cache_file, meta_file = self._get_cache_paths(key)
            if cache_file.exists():
                cache_file.unlink()
            if meta_file.exists():
                meta_file.unlink()
        except Exception as e:
            logger.warning(f"Failed to remove disk cache: {e}")

    def invalidate(self, key: str) -> None:
        """
        Invalidate specific cache entry using existing patterns.

        Args:
            key: Cache key to invalidate
        """
        # Remove from memory cache using existing patterns
        if key in self.memory_cache:
            del self.memory_cache[key]

        # Remove from disk cache using existing patterns
        self._remove_disk_cache(key)

    def clear(self) -> None:
        """Clear all cache using existing patterns."""
        # Clear memory cache using existing patterns
        self.memory_cache.clear()

        # Clear disk cache using existing patterns
        if self.cache_dir.exists():
            for file in self.cache_dir.iterdir():
                if file.name.startswith("EnhancedCache_"):
                    try:
                        file.unlink()
                    except Exception:
                        pass

        # Reset statistics using existing patterns
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics using existing patterns.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        memory_size = sum(entry.size_bytes for entry in self.memory_cache.values())
        memory_entries = len(self.memory_cache)

        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "evictions": self.evictions,
            "memory_entries": memory_entries,
            "memory_size_bytes": memory_size,
            "memory_size_mb": round(memory_size / (1024 * 1024), 2),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "disk_cache_enabled": self.disk_cache_enabled,
        }

    def warm_up(self, keys_and_data: Dict[str, Tuple[Any, int]]) -> None:
        """
        Warm up cache with pre-populated data using existing patterns.

        Args:
            keys_and_data: Dictionary mapping keys to (data, ttl) tuples
        """
        for key, (data, ttl) in keys_and_data.items():
            self.set(key, data, ttl)


class HybridCache(EnhancedTirganachCache):
    """
    Hybrid cache that combines multiple caching strategies using existing patterns.
    """

    def __init__(self, cache_dir: Union[str, Path] = None, max_size_mb: int = 100):
        super().__init__(cache_dir, max_size_mb)
        self.lru_access_log: Dict[str, float] = {}  # Track last access times

    def get(
        self, key: str, use_memory: bool = True, use_disk: bool = True
    ) -> Optional[Any]:
        """
        Get with LRU tracking using existing patterns.
        """
        result = super().get(key, use_memory, use_disk)

        # Update LRU tracking using existing patterns
        if result is not None:
            self.lru_access_log[key] = time.time()

        return result

    def set(
        self, key: str, data: Any, ttl: int = 300, cache_to_disk: bool = True
    ) -> None:
        """
        Set with LRU tracking using existing patterns.
        """
        super().set(key, data, ttl, cache_to_disk)

        # Update LRU tracking using existing patterns
        self.lru_access_log[key] = time.time()

    def get_lru_stats(self) -> Dict[str, Any]:
        """
        Get LRU statistics using existing patterns.

        Returns:
            Dictionary with LRU statistics
        """
        if not self.lru_access_log:
            return {"entries": 0, "oldest_access": None, "newest_access": None}

        sorted_times = sorted(self.lru_access_log.values())
        return {
            "entries": len(self.lru_access_log),
            "oldest_access": min(sorted_times) if sorted_times else None,
            "newest_access": max(sorted_times) if sorted_times else None,
            "access_span_seconds": max(sorted_times) - min(sorted_times)
            if len(sorted_times) > 1
            else 0,
        }


# Factory function for creating caches using existing patterns
def create_enhanced_cache(
    cache_type: str = "hybrid", **kwargs
) -> EnhancedTirganachCache:
    """
    Factory function to create enhanced caches using existing patterns.

    Args:
        cache_type: Type of cache ('basic' or 'hybrid')
        **kwargs: Additional arguments for cache initialization

    Returns:
        Enhanced cache instance
    """
    if cache_type == "hybrid":
        return HybridCache(**kwargs)
    else:
        return EnhancedTirganachCache(**kwargs)


# Context manager for cache operations using existing patterns
class CacheContext:
    """
    Context manager for cache operations using existing patterns.
    """

    def __init__(self, cache: EnhancedTirganachCache, key: str):
        self.cache = cache
        self.key = key
        self.data = None

    def __enter__(self):
        self.data = self.cache.get(self.key)
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.data is not None and exc_type is None:
            # Cache the result if no exception occurred using existing patterns
            self.cache.set(self.key, self.data)


# Decorator for caching function results using existing patterns
def cached_function(cache: EnhancedTirganachCache, ttl: int = 300):
    """
    Decorator for caching function results using existing patterns.

    Args:
        cache: Cache instance to use
        ttl: Time-to-live for cached results
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from function arguments using existing patterns
            key_parts = [func.__name__] + [str(arg) for arg in args]
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = "|".join(key_parts)

            # Try to get from cache using existing patterns
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result using existing patterns
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator
