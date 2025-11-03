"""
Adapters for existing TirganachReloaded data models
Integrates existing optimized components with new engine architecture
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

# Import existing TirganachReloaded components
try:
    from TirganachReloaded.tirganach import GameData
    from TirganachReloaded.tirganach.entities import (
        AdvancedDescription,
        Armor,
        Description,
        Item,
        Localisation,
        Quest,
        Spell,
        Weapon,
    )
    from TirganachReloaded.tirganach.types import Language

    TIRGANACH_AVAILABLE = True
except ImportError:
    TIRGANACH_AVAILABLE = False
    GameData = None
    Item = None
    Spell = None
    Quest = None
    Weapon = None
    Armor = None
    Localisation = None
    Description = None
    AdvancedDescription = None
    Language = None

# Import our new engine models for compatibility
from src.engine.game_data.models import ItemDataModel, QuestDataModel, SpellDataModel

logger = logging.getLogger(__name__)
T = TypeVar("T")


class TirganachDataAdapter:
    """
    Adapter that bridges existing TirganachReloaded data models with new engine architecture.
    Leverages existing optimizations while providing clean interface for new components.
    """

    def __init__(self):
        self.game_data: Optional[GameData] = None
        self.localisation_index: Dict[Language, Dict[int, str]] = {}
        self.current_language = Language.ENGLISH if Language else None
        self._cache: Dict[str, Any] = {}

    def load_game_data(self, file_path: str) -> bool:
        """
        Load GameData using existing optimized loader with caching.

        Args:
            file_path: Path to GameData.cff file

        Returns:
            True if loaded successfully, False otherwise
        """
        if not TIRGANACH_AVAILABLE:
            logger.error("TirganachReloaded library not available")
            return False

        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.error(f"GameData file not found: {file_path}")
                return False

            # Use existing optimized loader
            self.game_data = GameData(str(file_path_obj))
            logger.info(f"Successfully loaded GameData from {file_path}")

            # Build localisation index for fast lookups (existing optimization)
            self._build_localisation_index()

            # Clear cache for new data
            self._cache.clear()

            return True

        except Exception as e:
            logger.exception(f"Failed to load GameData: {e}")
            return False

    def _build_localisation_index(self):
        """Build optimized index for localisation lookups (existing pattern)"""
        if not self.game_data:
            return

        try:
            # Build index: {language: {text_id: text}} for O(1) lookups
            self.localisation_index = {}

            localisation_table = getattr(self.game_data, "localisation", [])
            if not localisation_table:
                return

            for entry in localisation_table:
                language = getattr(entry, "language", None)
                text_id = getattr(entry, "text_id", None)
                text = getattr(entry, "text", "")

                if language is not None and text_id is not None:
                    if language not in self.localisation_index:
                        self.localisation_index[language] = {}
                    self.localisation_index[language][text_id] = text

        except Exception as e:
            logger.error(f"Error building localisation index: {e}")

    def get_localised_text(
        self, text_id: int, language: Optional[Language] = None
    ) -> Optional[str]:
        """
        Get localized text using existing optimized lookup pattern.

        Args:
            text_id: Text ID to look up
            language: Language to use (defaults to current_language)

        Returns:
            Localized text or None if not found
        """
        if not self.game_data:
            return None

        language = language or self.current_language

        # Use existing indexing optimization
        if (
            language in self.localisation_index
            and text_id in self.localisation_index[language]
        ):
            return self.localisation_index[language][text_id]

        return None

    def get_table(self, table_name: str) -> Optional[List[Any]]:
        """
        Get table data using existing table access patterns.

        Args:
            table_name: Name of table to retrieve

        Returns:
            List of table entries or None if not found
        """
        if not self.game_data:
            return None

        try:
            # Use existing table access pattern
            return getattr(self.game_data, table_name, None)
        except Exception as e:
            logger.error(f"Error accessing table {table_name}: {e}")
            return None

    def convert_to_engine_model(self, entity: Any, model_type: Type[T]) -> Optional[T]:
        """
        Convert existing TirganachReloaded entities to new engine models.

        Args:
            entity: Existing entity to convert
            model_type: Target engine model type

        Returns:
            Converted engine model or None if conversion failed
        """
        try:
            if model_type == ItemDataModel and hasattr(entity, "item_id"):
                return self._convert_item_to_model(entity)
            elif model_type == SpellDataModel and hasattr(entity, "spell_id"):
                return self._convert_spell_to_model(entity)
            elif model_type == QuestDataModel and hasattr(entity, "quest_id"):
                return self._convert_quest_to_model(entity)

        except Exception as e:
            logger.error(f"Error converting {type(entity)} to {model_type}: {e}")

        return None

    def _convert_item_to_model(self, item: Any) -> Optional[ItemDataModel]:
        """Convert Item entity to ItemDataModel"""
        try:
            # Get localized name using existing pattern
            name = getattr(item, "name", f"Item {item.item_id}")
            if not name and hasattr(item, "name_id"):
                name = self.get_localised_text(item.name_id) or f"Item {item.item_id}"

            # Create model with existing data
            return ItemDataModel(
                id=item.item_id,
                name=name or f"Item {item.item_id}",
                description=getattr(item, "description", ""),
                type=getattr(item, "item_type", "").name
                if hasattr(item, "item_type")
                else "",
                value=getattr(item, "selling_price", 0),
                required_level=getattr(item, "req_level", 1),
            )
        except Exception as e:
            logger.error(
                f"Error converting item {getattr(item, 'item_id', 'unknown')}: {e}"
            )
            return None

    def _convert_spell_to_model(self, spell: Any) -> Optional[SpellDataModel]:
        """Convert Spell entity to SpellDataModel"""
        try:
            # Get localized name using existing pattern
            name = getattr(spell, "name", f"Spell {spell.spell_id}")
            if not name and hasattr(spell, "spell_name_id"):
                name = (
                    self.get_localised_text(spell.spell_name_id)
                    or f"Spell {spell.spell_id}"
                )

            # Create model with existing data
            return SpellDataModel(
                id=spell.spell_id,
                name=name or f"Spell {spell.spell_id}",
                description=getattr(spell, "description", ""),
                school=getattr(spell, "magic_type", ""),
                level=getattr(spell, "level", 1),
                mana_cost=getattr(spell, "mana", 0),
                range=float(getattr(spell, "max_range", 0.0)),
            )
        except Exception as e:
            logger.error(
                f"Error converting spell {getattr(spell, 'spell_id', 'unknown')}: {e}"
            )
            return None

    def _convert_quest_to_model(self, quest: Any) -> Optional[QuestDataModel]:
        """Convert Quest entity to QuestDataModel"""
        try:
            # Get localized name using existing pattern
            name = getattr(quest, "name", f"Quest {quest.quest_id}")
            if not name and hasattr(quest, "name_id"):
                name = (
                    self.get_localised_text(quest.name_id) or f"Quest {quest.quest_id}"
                )

            # Create model with existing data
            return QuestDataModel(
                id=quest.quest_id,
                name=name or f"Quest {quest.quest_id}",
                description=getattr(quest, "description", ""),
                quest_type="sub"
                if getattr(quest, "parent_quest_id", 0) > 0
                else "main",
                required_level=getattr(quest, "req_level", 1),
                parent_quest_id=getattr(quest, "parent_quest_id", None),
                experience_reward=getattr(quest, "xp_reward", 0),
            )
        except Exception as e:
            logger.error(
                f"Error converting quest {getattr(quest, 'quest_id', 'unknown')}: {e}"
            )
            return None

    def get_items(self, cache: bool = True) -> List[ItemDataModel]:
        """
        Get all items using existing optimized access patterns.

        Args:
            cache: Whether to use cached results

        Returns:
            List of ItemDataModel instances
        """
        cache_key = "items"
        if cache and cache_key in self._cache:
            return self._cache[cache_key]

        items = []
        try:
            # Use existing table access pattern
            item_table = self.get_table("items")
            if item_table:
                for item in item_table:
                    item_model = self.convert_to_engine_model(item, ItemDataModel)
                    if item_model:
                        items.append(item_model)

            if cache:
                self._cache[cache_key] = items

        except Exception as e:
            logger.error(f"Error loading items: {e}")

        return items

    def get_spells(self, cache: bool = True) -> List[SpellDataModel]:
        """
        Get all spells using existing optimized access patterns.

        Args:
            cache: Whether to use cached results

        Returns:
            List of SpellDataModel instances
        """
        cache_key = "spells"
        if cache and cache_key in self._cache:
            return self._cache[cache_key]

        spells = []
        try:
            # Use existing table access pattern
            spell_table = self.get_table("spells")
            if spell_table:
                for spell in spell_table:
                    spell_model = self.convert_to_engine_model(spell, SpellDataModel)
                    if spell_model:
                        spells.append(spell_model)

            if cache:
                self._cache[cache_key] = spells

        except Exception as e:
            logger.error(f"Error loading spells: {e}")

        return spells

    def get_quests(self, cache: bool = True) -> List[QuestDataModel]:
        """
        Get all quests using existing optimized access patterns.

        Args:
            cache: Whether to use cached results

        Returns:
            List of QuestDataModel instances
        """
        cache_key = "quests"
        if cache and cache_key in self._cache:
            return self._cache[cache_key]

        quests = []
        try:
            # Use existing table access pattern
            quest_table = self.get_table("quests")
            if quest_table:
                for quest in quest_table:
                    quest_model = self.convert_to_engine_model(quest, QuestDataModel)
                    if quest_model:
                        quests.append(quest_model)

            if cache:
                self._cache[cache_key] = quests

        except Exception as e:
            logger.error(f"Error loading quests: {e}")

        return quests


# Singleton instance for easy access
adapter_instance = None


def get_tirganach_adapter() -> TirganachDataAdapter:
    """
    Get singleton instance of TirganachDataAdapter.

    Returns:
        TirganachDataAdapter instance
    """
    global adapter_instance
    if adapter_instance is None:
        adapter_instance = TirganachDataAdapter()
    return adapter_instance
