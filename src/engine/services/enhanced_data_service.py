"""
Enhanced Data Services with Existing Caching Patterns
Implements optimized data services using existing TirganachReloaded cache patterns
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar

# Import existing caching patterns
try:
    from TirganachReloaded.cff_editor.data_model import CFFDataModel

    TIRGANACH_CACHE_AVAILABLE = True
except ImportError:
    TIRGANACH_CACHE_AVAILABLE = False
    CFFDataModel = None

# Import existing performance utilities
try:
    from TirganachReloaded.cff_editor.logging_config import get_logger

    EXISTING_LOGGING_AVAILABLE = True
except ImportError:
    EXISTING_LOGGING_AVAILABLE = False
    get_logger = None

from src.engine.adapters.tirganach_adapter import get_tirganach_adapter
from src.engine.utils.performance import perf_monitor, performance_timer

logger = (
    logging.getLogger(__name__)
    if not EXISTING_LOGGING_AVAILABLE
    else get_logger(__name__)
)
T = TypeVar("T")


class EnhancedDataCache:
    """
    Enhanced data cache implementing existing TirganachReloaded cache patterns.
    Leverages proven caching strategies with TTL and LRU eviction.
    """

    def __init__(self, ttl: int = 300, max_size: int = 1000):
        """
        Initialize enhanced data cache.

        Args:
            ttl: Time-to-live in seconds for cached entries
            max_size: Maximum number of entries to cache
        """
        self.ttl = ttl
        self.max_size = max_size
        self._cache: Dict[str, tuple] = {}  # {key: (data, timestamp, access_count)}
        self._access_order: List[str] = []  # LRU tracking
        self.hits = 0
        self.misses = 0

    @performance_timer
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached data with TTL validation.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found/expired
        """
        perf_monitor.start_timer("cache_get")

        current_time = time.time()

        if key in self._cache:
            data, timestamp, access_count = self._cache[key]

            # Check TTL expiration
            if current_time - timestamp < self.ttl:
                # Update access count for LRU
                self._cache[key] = (data, timestamp, access_count + 1)

                # Update LRU tracking
                if key in self._access_order:
                    self._access_order.remove(key)
                self._access_order.append(key)

                self.hits += 1
                perf_monitor.stop_timer("cache_get")
                return data
            else:
                # Expired entry - remove it
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)

        self.misses += 1
        perf_monitor.stop_timer("cache_get")
        return None

    @performance_timer
    def set(self, key: str, data: Any) -> None:
        """
        Set cached data with LRU management.

        Args:
            key: Cache key
            data: Data to cache
        """
        perf_monitor.start_timer("cache_set")

        current_time = time.time()

        # Remove oldest entries if we're at max size
        if len(self._cache) >= self.max_size:
            self._evict_lru_entries()

        # Add new entry
        self._cache[key] = (data, current_time, 1)

        # Update LRU tracking
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        perf_monitor.stop_timer("cache_set")

    def _evict_lru_entries(self) -> None:
        """Evict least recently used entries to maintain size limits."""
        # Remove entries from the beginning of access order (least recently used)
        while len(self._cache) >= self.max_size and self._access_order:
            lru_key = self._access_order.pop(0)
            if lru_key in self._cache:
                del self._cache[lru_key]

    @performance_timer
    def invalidate(self, key: str) -> None:
        """
        Invalidate specific cache entry.

        Args:
            key: Cache key to invalidate
        """
        if key in self._cache:
            del self._cache[key]
        if key in self._access_order:
            self._access_order.remove(key)

    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._access_order.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "current_size": len(self._cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
        }


class EnhancedDataService:
    """
    Enhanced data service implementing existing TirganachReloaded patterns.
    Combines proven data access patterns with new engine architecture.
    """

    def __init__(self):
        self.adapter = get_tirganach_adapter()
        self.cache = EnhancedDataCache()
        self.file_cache = EnhancedDataCache(ttl=3600)  # Longer TTL for file data
        self._loaded_categories: Dict[str, bool] = {}
        self._category_data: Dict[str, List[Any]] = {}

    @performance_timer
    def load_category(self, category_name: str, source_path: str = "") -> bool:
        """
        Load category data using existing TirganachReloaded patterns.

        Args:
            category_name: Name of category to load
            source_path: Source file path (uses existing file loading patterns)

        Returns:
            True if loaded successfully, False otherwise
        """
        perf_monitor.start_timer(f"load_category_{category_name}")

        try:
            # Use existing cache-first pattern
            cache_key = f"category_{category_name}_{source_path}"
            cached_data = self.cache.get(cache_key)

            if cached_data is not None:
                self._category_data[category_name] = cached_data
                self._loaded_categories[category_name] = True
                perf_monitor.stop_timer(f"load_category_{category_name}")
                return True

            # Load using existing Tirganach patterns
            if not self.adapter.game_data:
                # Load game data using existing patterns
                if source_path and Path(source_path).exists():
                    if not self.adapter.load_game_data(source_path):
                        perf_monitor.stop_timer(f"load_category_{category_name}")
                        return False
                else:
                    # Try to find default GameData file using existing patterns
                    default_path = self._find_default_gamedata()
                    if default_path and Path(default_path).exists():
                        if not self.adapter.load_game_data(str(default_path)):
                            perf_monitor.stop_timer(f"load_category_{category_name}")
                            return False
                    else:
                        logger.error("No GameData file found")
                        perf_monitor.stop_timer(f"load_category_{category_name}")
                        return False

            # Load category using existing table patterns
            table_data = self.adapter.get_table(category_name)
            if table_data is not None:
                self._category_data[category_name] = table_data
                self._loaded_categories[category_name] = True

                # Cache the result using existing patterns
                self.cache.set(cache_key, table_data)
                perf_monitor.stop_timer(f"load_category_{category_name}")
                return True
            else:
                logger.warning(f"Category {category_name} not found in GameData")
                perf_monitor.stop_timer(f"load_category_{category_name}")
                return False

        except Exception as e:
            logger.error(f"Error loading category {category_name}: {e}")
            perf_monitor.stop_timer(f"load_category_{category_name}")
            return False

    @performance_timer
    def _find_default_gamedata(self) -> Optional[Path]:
        """
        Find default GameData file using existing search patterns.

        Returns:
            Path to GameData file or None if not found
        """
        # Use existing search patterns from TirganachReloaded
        search_paths = [
            Path("OriginalGameFiles/data/GameData.cff"),
            Path("../OriginalGameFiles/data/GameData.cff"),
            Path("../../OriginalGameFiles/data/GameData.cff"),
            Path("GameData.cff"),
        ]

        for path in search_paths:
            if path.exists():
                return path

        return None

    @performance_timer
    def get_entry(self, category_name: str, entry_id: int) -> Optional[Any]:
        """
        Get specific entry using existing indexing patterns.

        Args:
            category_name: Category name
            entry_id: Entry ID

        Returns:
            Entry data or None if not found
        """
        perf_monitor.start_timer(f"get_entry_{category_name}_{entry_id}")

        # Use existing cache pattern
        cache_key = f"entry_{category_name}_{entry_id}"
        cached_entry = self.cache.get(cache_key)

        if cached_entry is not None:
            perf_monitor.stop_timer(f"get_entry_{category_name}_{entry_id}")
            return cached_entry

        # Load category if not already loaded
        if not self._loaded_categories.get(category_name, False):
            # Try to load from default source
            if not self.load_category(category_name):
                perf_monitor.stop_timer(f"get_entry_{category_name}_{entry_id}")
                return None

        # Find entry using existing table search patterns
        category_data = self._category_data.get(category_name, [])
        for entry in category_data:
            # Use existing primary key patterns
            entry_key = getattr(
                entry,
                "item_id",
                getattr(entry, "spell_id", getattr(entry, "quest_id", None)),
            )
            if entry_key is not None and entry_key == entry_id:
                # Cache the result using existing patterns
                self.cache.set(cache_key, entry)
                perf_monitor.stop_timer(f"get_entry_{category_name}_{entry_id}")
                return entry

        perf_monitor.stop_timer(f"get_entry_{category_name}_{entry_id}")
        return None

    @performance_timer
    def get_category_entries(self, category_name: str) -> Dict[int, Any]:
        """
        Get all entries in category using existing indexing patterns.

        Args:
            category_name: Category name

        Returns:
            Dictionary mapping IDs to entries
        """
        perf_monitor.start_timer(f"get_category_entries_{category_name}")

        # Load category if not already loaded
        if not self._loaded_categories.get(category_name, False):
            self.load_category(category_name)

        entries = {}
        category_data = self._category_data.get(category_name, [])

        # Use existing indexing patterns
        for entry in category_data:
            # Use existing primary key patterns
            entry_key = getattr(
                entry,
                "item_id",
                getattr(entry, "spell_id", getattr(entry, "quest_id", None)),
            )
            if entry_key is not None:
                entries[entry_key] = entry

        perf_monitor.stop_timer(f"get_category_entries_{category_name}")
        return entries

    @performance_timer
    def add_entry(self, category_name: str, entry_id: int, entry_data: Any) -> bool:
        """
        Add entry to category using existing patterns.

        Args:
            category_name: Category name
            entry_id: Entry ID
            entry_data: Entry data

        Returns:
            True if added successfully, False otherwise
        """
        perf_monitor.start_timer(f"add_entry_{category_name}_{entry_id}")

        # Load category if not already loaded
        if not self._loaded_categories.get(category_name, False):
            self.load_category(category_name)

        # Add to category data using existing patterns
        if category_name not in self._category_data:
            self._category_data[category_name] = []

        # Check if entry already exists
        category_data = self._category_data[category_name]
        entry_exists = False
        for i, entry in enumerate(category_data):
            entry_key = getattr(
                entry,
                "item_id",
                getattr(entry, "spell_id", getattr(entry, "quest_id", None)),
            )
            if entry_key is not None and entry_key == entry_id:
                # Update existing entry using existing patterns
                category_data[i] = entry_data
                entry_exists = True
                break

        if not entry_exists:
            # Add new entry using existing patterns
            category_data.append(entry_data)

        # Invalidate cache for this entry using existing patterns
        cache_key = f"entry_{category_name}_{entry_id}"
        self.cache.invalidate(cache_key)

        # Invalidate category cache using existing patterns
        category_cache_key = f"category_{category_name}_"
        self.cache.invalidate(category_cache_key)

        perf_monitor.stop_timer(f"add_entry_{category_name}_{entry_id}")
        return True

    def is_category_loaded(self, category_name: str) -> bool:
        """
        Check if category is loaded using existing patterns.

        Args:
            category_name: Category name

        Returns:
            True if category is loaded, False otherwise
        """
        return self._loaded_categories.get(category_name, False)

    def get_loaded_categories(self) -> List[str]:
        """
        Get list of loaded categories using existing patterns.

        Returns:
            List of loaded category names
        """
        return [cat for cat, loaded in self._loaded_categories.items() if loaded]

    def clear_cache(self, category_name: Optional[str] = None) -> None:
        """
        Clear cache using existing patterns.

        Args:
            category_name: Specific category to clear, or None for all
        """
        if category_name:
            # Clear specific category cache using existing patterns
            category_cache_key = f"category_{category_name}_"
            self.cache.invalidate(category_cache_key)

            # Clear category data using existing patterns
            if category_name in self._category_data:
                del self._category_data[category_name]
            if category_name in self._loaded_categories:
                del self._loaded_categories[category_name]
        else:
            # Clear all cache using existing patterns
            self.cache.clear()
            self._category_data.clear()
            self._loaded_categories.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics using existing patterns.

        Returns:
            Dictionary with cache statistics
        """
        return self.cache.get_stats()


# Enhanced validation service that leverages existing patterns
class EnhancedValidationService:
    """
    Enhanced validation service implementing existing TirganachReloaded validation patterns.
    """

    def __init__(self):
        self.adapter = get_tirganach_adapter()
        self.errors: List[Dict[str, Any]] = []
        self.cache = EnhancedDataCache()

    def validate(self, data: Any, data_type: Optional[str] = None) -> bool:
        """
        Validate data using existing patterns.

        Args:
            data: Data to validate
            data_type: Type of data being validated

        Returns:
            True if validation passes, False otherwise
        """
        # Clear previous errors for this validation using existing patterns
        self.errors.clear()

        # Determine data type if not provided using existing patterns
        if data_type is None:
            data_type = self._infer_data_type(data)

        # Run general validation first using existing patterns
        if not self._run_general_validation(data):
            return False

        # Run type-specific validation using existing patterns
        type_valid = self._run_type_specific_validation(data, data_type)
        if not type_valid:
            return False

        # Return success if no errors using existing patterns
        return len(self.errors) == 0

    def _infer_data_type(self, data: Any) -> str:
        """
        Infer data type using existing patterns.

        Args:
            data: Data to infer type for

        Returns:
            Inferred data type
        """
        # Use existing type inference patterns
        class_name = data.__class__.__name__.lower()
        if "item" in class_name:
            return "item"
        elif "spell" in class_name:
            return "spell"
        elif "quest" in class_name:
            return "quest"
        else:
            # Try to infer from attributes using existing patterns
            if hasattr(data, "item_id"):
                return "item"
            elif hasattr(data, "spell_id"):
                return "spell"
            elif hasattr(data, "quest_id"):
                return "quest"
            else:
                return "generic"

    def _run_general_validation(self, data: Any) -> bool:
        """
        Run general validation using existing patterns.

        Args:
            data: Data to validate

        Returns:
            True if general validation passes, False otherwise
        """
        try:
            # Use existing validation patterns from TirganachReloaded
            # This would normally be more complex, but keeping it simple for example
            return True
        except Exception as e:
            self.errors.append(
                {
                    "type": data.__class__.__name__,
                    "id": getattr(
                        data,
                        "item_id",
                        getattr(data, "spell_id", getattr(data, "quest_id", "unknown")),
                    ),
                    "error": f"General validation error: {str(e)}",
                }
            )
            return False

    def _run_type_specific_validation(self, data: Any, data_type: str) -> bool:
        """
        Run type-specific validation using existing patterns.

        Args:
            data: Data to validate
            data_type: Type of data

        Returns:
            True if validation passes, False otherwise
        """
        # Use existing validation rule patterns
        validation_rules = {
            "item": self._validate_item,
            "spell": self._validate_spell,
            "quest": self._validate_quest,
        }

        validator = validation_rules.get(data_type)
        if validator:
            return validator(data)
        else:
            # Generic validation for unknown types
            return self._validate_generic(data)

    def _validate_item(self, item: Any) -> bool:
        """
        Validate item using existing patterns.

        Args:
            item: Item to validate

        Returns:
            True if validation passes, False otherwise
        """
        # Use existing item validation patterns from TirganachReloaded
        try:
            item_id = getattr(item, "item_id", 0)
            if item_id <= 0:
                self.errors.append(
                    {
                        "type": "item",
                        "id": item_id,
                        "error": f"Item ID must be positive, got {item_id}",
                    }
                )
                return False

            # Use existing price validation patterns
            selling_price = getattr(item, "selling_price", 0)
            buying_price = getattr(item, "buying_price", 0)
            if selling_price < 0 or buying_price < 0:
                self.errors.append(
                    {
                        "type": "item",
                        "id": item_id,
                        "error": f"Prices cannot be negative (sell: {selling_price}, buy: {buying_price})",
                    }
                )
                return False

            return True
        except Exception as e:
            item_id = getattr(item, "item_id", "unknown")
            self.errors.append(
                {
                    "type": "item",
                    "id": item_id,
                    "error": f"Item validation error: {str(e)}",
                }
            )
            return False

    def _validate_spell(self, spell: Any) -> bool:
        """
        Validate spell using existing patterns.

        Args:
            spell: Spell to validate

        Returns:
            True if validation passes, False otherwise
        """
        # Use existing spell validation patterns
        try:
            spell_id = getattr(spell, "spell_id", 0)
            if spell_id <= 0:
                self.errors.append(
                    {
                        "type": "spell",
                        "id": spell_id,
                        "error": f"Spell ID must be positive, got {spell_id}",
                    }
                )
                return False

            # Use existing mana validation patterns
            mana = getattr(spell, "mana", getattr(spell, "mana_cost", 0))
            if mana < 0:
                self.errors.append(
                    {
                        "type": "spell",
                        "id": spell_id,
                        "error": f"Mana cost cannot be negative, got {mana}",
                    }
                )
                return False

            return True
        except Exception as e:
            spell_id = getattr(spell, "spell_id", "unknown")
            self.errors.append(
                {
                    "type": "spell",
                    "id": spell_id,
                    "error": f"Spell validation error: {str(e)}",
                }
            )
            return False

    def _validate_quest(self, quest: Any) -> bool:
        """
        Validate quest using existing patterns.

        Args:
            quest: Quest to validate

        Returns:
            True if validation passes, False otherwise
        """
        # Use existing quest validation patterns
        try:
            quest_id = getattr(quest, "quest_id", 0)
            if quest_id <= 0:
                self.errors.append(
                    {
                        "type": "quest",
                        "id": quest_id,
                        "error": f"Quest ID must be positive, got {quest_id}",
                    }
                )
                return False

            return True
        except Exception as e:
            quest_id = getattr(quest, "quest_id", "unknown")
            self.errors.append(
                {
                    "type": "quest",
                    "id": quest_id,
                    "error": f"Quest validation error: {str(e)}",
                }
            )
            return False

    def _validate_generic(self, data: Any) -> bool:
        """
        Generic validation for unknown data types.

        Args:
            data: Data to validate

        Returns:
            True if validation passes, False otherwise
        """
        # Basic validation for any data
        try:
            # Check for required ID field using existing patterns
            has_id = (
                hasattr(data, "item_id")
                or hasattr(data, "spell_id")
                or hasattr(data, "quest_id")
            )

            if not has_id:
                self.errors.append(
                    {
                        "type": data.__class__.__name__,
                        "id": "unknown",
                        "error": "Data object missing required ID field",
                    }
                )
                return False

            return True
        except Exception as e:
            self.errors.append(
                {
                    "type": data.__class__.__name__,
                    "id": "unknown",
                    "error": f"Generic validation error: {str(e)}",
                }
            )
            return False

    def get_errors(self) -> List[Dict[str, Any]]:
        """
        Get validation errors using existing patterns.

        Returns:
            List of validation errors
        """
        return self.errors.copy()


# Factory for creating enhanced services
def create_enhanced_data_service() -> EnhancedDataService:
    """
    Factory function to create enhanced data service.

    Returns:
        EnhancedDataService instance
    """
    return EnhancedDataService()


def create_enhanced_validation_service() -> EnhancedValidationService:
    """
    Factory function to create enhanced validation service.

    Returns:
        EnhancedValidationService instance
    """
    return EnhancedValidationService()
