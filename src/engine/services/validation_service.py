"""Validation Service following C# SFEngine patterns adapted for Python"""

import logging
from typing import Any, Callable, Dict, List, Optional

from ..game_data.models import GameDataModel


class ValidationService:
    """
    Service for validating game data following C# SFEngine patterns.
    Provides validation functions for different data types and cross-references.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._validation_rules: Dict[str, List[Callable]] = {}
        self._errors: List[Dict[str, Any]] = []

    def add_validation_rule(self, data_type: str, rule_func: Callable):
        """
        Add a validation rule for a specific data type.

        Args:
            data_type: Type of data to validate (e.g., 'item', 'spell', 'quest')
            rule_func: Function that takes a GameDataModel and returns (bool, str)
        """
        if data_type not in self._validation_rules:
            self._validation_rules[data_type] = []
        self._validation_rules[data_type].append(rule_func)
        self.logger.debug(f"Added validation rule for type: {data_type}")

    def validate(self, data: GameDataModel, data_type: Optional[str] = None) -> bool:
        """
        Validate a single data model instance.

        Args:
            data: GameDataModel instance to validate
            data_type: Type of data (if not provided, inferred from class name)

        Returns:
            True if validation passes, False otherwise
        """
        # Clear previous errors for this validation
        self._errors.clear()

        # Determine data type if not provided
        if data_type is None:
            data_type = data.__class__.__name__.lower().replace("datamodel", "")

        # Run general validation first
        if not self._run_general_validation(data):
            return False

        # Run type-specific validation rules
        if data_type in self._validation_rules:
            for rule_func in self._validation_rules[data_type]:
                try:
                    is_valid, error_msg = rule_func(data)
                    if not is_valid:
                        self._errors.append(
                            {"type": data_type, "id": data.id, "error": error_msg}
                        )
                        self.logger.warning(
                            f"Validation failed for {data_type} ID {data.id}: {error_msg}"
                        )
                except Exception as e:
                    self.logger.error(
                        f"Validation rule failed for {data_type} ID {data.id}: {e}"
                    )
                    self._errors.append(
                        {
                            "type": data_type,
                            "id": data.id,
                            "error": f"Validation rule error: {str(e)}",
                        }
                    )

        # Return success if no errors
        return len(self._errors) == 0

    def validate_category(self, data_list: List[GameDataModel], data_type: str) -> bool:
        """
        Validate multiple data instances of the same type.

        Args:
            data_list: List of GameDataModel instances to validate
            data_type: Type of data being validated

        Returns:
            True if all items pass validation, False otherwise
        """
        self._errors.clear()

        for data in data_list:
            if not self.validate(data, data_type):
                # Don't return immediately, validate all items but return overall status
                self.logger.warning(f"Validation failed for {data_type} ID {data.id}")

        return len(self._errors) == 0

    def get_errors(self) -> List[Dict[str, Any]]:
        """
        Get list of validation errors from last validation run.

        Returns:
            List of error dictionaries with type, id, and error message
        """
        return self._errors.copy()

    def validate_cross_references(
        self, data_sets: Dict[str, List[GameDataModel]]
    ) -> bool:
        """
        Validate cross-references between different data types.
        For example: spell requirements reference valid items or spells.

        Args:
            data_sets: Dictionary mapping data type names to their data lists

        Returns:
            True if all cross-references are valid, False otherwise
        """
        self._errors.clear()

        # Example validation rules for cross-references:
        # - Quest prerequisites exist
        # - Spell reagents exist
        # - Item recipes reference valid components

        for data_type, data_list in data_sets.items():
            for data in data_list:
                cross_errors = self._check_cross_references(data, data_sets)
                for error in cross_errors:
                    self._errors.append(error)
                    self.logger.warning(f"Cross-reference error: {error}")

        return len(self._errors) == 0

    def _run_general_validation(self, data: GameDataModel) -> bool:
        """Run general validation checks common to all data types."""
        try:
            # This will trigger the validation in the data model itself
            # Since all models inherit from GameDataModel which has _validate()
            # called in __post_init__, we just need to make sure no exceptions occurred
            return True
        except Exception as e:
            self._errors.append(
                {
                    "type": data.__class__.__name__,
                    "id": data.id,
                    "error": f"General validation error: {str(e)}",
                }
            )
            self.logger.error(
                f"General validation failed for {data.__class__.__name__} ID {data.id}: {e}"
            )
            return False

    def _check_cross_references(
        self, data: GameDataModel, data_sets: Dict[str, List[GameDataModel]]
    ) -> List[Dict[str, Any]]:
        """Check cross-references for a single data item."""
        errors = []

        # This is where we would implement specific cross-reference checks
        # based on the type of data model

        # Example: If it's a quest, check if parent quest exists
        if hasattr(data, "parent_quest_id") and data.parent_quest_id is not None:
            if "quests" in data_sets:
                quest_exists = any(
                    q.id == data.parent_quest_id for q in data_sets["quests"]
                )
                if not quest_exists:
                    errors.append(
                        {
                            "type": "quest",
                            "id": data.id,
                            "error": f"Parent quest ID {data.parent_quest_id} does not exist",
                        }
                    )

        return errors

    def register_default_validators(self):
        """
        Register default validation rules following C# SFEngine patterns.
        This is where we would add common validation rules for different data types.
        """

        # Item validators
        def validate_item_value(item):
            if hasattr(item, "value") and item.value < 0:
                return False, f"Item value cannot be negative: {item.value}"
            return True, ""

        # Spell validators
        def validate_spell_level(spell):
            if hasattr(spell, "level") and (spell.level < 1 or spell.level > 15):
                return False, f"Spell level must be between 1-15: {spell.level}"
            return True, ""

        # Quest validators
        def validate_quest_requirements(quest):
            if hasattr(quest, "required_level") and quest.required_level < 1:
                return (
                    False,
                    f"Quest required level must be at least 1: {quest.required_level}",
                )
            return True, ""

        self.add_validation_rule("item", validate_item_value)
        self.add_validation_rule("spell", validate_spell_level)
        self.add_validation_rule("quest", validate_quest_requirements)

        self.logger.info("Registered default validators following C# patterns")
