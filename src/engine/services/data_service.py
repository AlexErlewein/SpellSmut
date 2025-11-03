"""Data Service following C# SFEngine patterns adapted for Python"""

import logging
from typing import Any, Dict, Optional

from ..game_data.models import GameDataModel


class DataService:
    """
    Service for loading, managing, and accessing game data.
    Follows C# SFEngine data management patterns adapted for Python.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._data_cache: Dict[str, Any] = {}
        self._loaded_categories: Dict[str, bool] = {}

    def load_category(self, category_name: str, source_path: str = "") -> bool:
        """
        Load a data category following C# SFEngine patterns.

        Args:
            category_name: Name of the category to load (e.g., 'items', 'spells', 'quests')
            source_path: Path to data source (default: use configured path)

        Returns:
            True if successfully loaded, False otherwise
        """
        try:
            self.logger.info(f"Loading category: {category_name}")

            # In a real implementation, this would load from CFF files or other sources
            # For now, we'll simulate the loading process
            if category_name not in self._loaded_categories:
                self._loaded_categories[category_name] = True
                self._data_cache[category_name] = {}
                self.logger.info(f"Successfully loaded category: {category_name}")
                return True
            else:
                self.logger.info(f"Category already loaded: {category_name}")
                return True

        except Exception as e:
            self.logger.error(f"Failed to load category {category_name}: {e}")
            return False

    def get_entry(self, category_name: str, entry_id: int) -> Optional[GameDataModel]:
        """
        Get a specific data entry by category and ID.

        Args:
            category_name: Name of the data category
            entry_id: ID of the specific entry

        Returns:
            GameDataModel instance or None if not found
        """
        if category_name in self._data_cache:
            category_data = self._data_cache[category_name]
            return category_data.get(entry_id)
        return None

    def add_entry(
        self, category_name: str, entry_id: int, entry_data: GameDataModel
    ) -> bool:
        """
        Add or update a data entry in the cache.

        Args:
            category_name: Name of the data category
            entry_id: ID of the entry to add/update
            entry_data: The GameDataModel instance to store

        Returns:
            True if successfully added, False otherwise
        """
        try:
            if category_name not in self._data_cache:
                self._data_cache[category_name] = {}

            self._data_cache[category_name][entry_id] = entry_data
            self.logger.debug(
                f"Added/updated entry {entry_id} in category {category_name}"
            )
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to add entry {entry_id} in category {category_name}: {e}"
            )
            return False

    def get_category_entries(self, category_name: str) -> Dict[int, GameDataModel]:
        """
        Get all entries in a specific category.

        Args:
            category_name: Name of the data category

        Returns:
            Dictionary mapping IDs to GameDataModel instances
        """
        return self._data_cache.get(category_name, {})

    def clear_cache(self, category_name: Optional[str] = None):
        """
        Clear the data cache, optionally for a specific category only.

        Args:
            category_name: Name of category to clear, or None for all categories
        """
        if category_name:
            if category_name in self._data_cache:
                del self._data_cache[category_name]
                if category_name in self._loaded_categories:
                    del self._loaded_categories[category_name]
                self.logger.info(f"Cleared cache for category: {category_name}")
        else:
            self._data_cache.clear()
            self._loaded_categories.clear()
            self.logger.info("Cleared entire data cache")

    def is_category_loaded(self, category_name: str) -> bool:
        """
        Check if a category has been loaded.

        Args:
            category_name: Name of the category to check

        Returns:
            True if category is loaded, False otherwise
        """
        return self._loaded_categories.get(category_name, False)

    def get_loaded_categories(self) -> list:
        """
        Get list of all currently loaded categories.

        Returns:
            List of category names that are currently loaded
        """
        return list(self._loaded_categories.keys())
