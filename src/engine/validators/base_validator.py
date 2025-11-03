"""Validation utilities following C# SFEngine patterns"""

import logging
from typing import Any, Dict, List

from ..game_data.models import GameDataModel


class BaseValidator:
    """
    Base validator class following C# SFEngine validation patterns.
    Provides common validation functionality for all validators.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def validate(self, data: Any) -> Dict[str, List[str]]:
        """
        Validate data and return any errors found.

        Args:
            data: Data to validate

        Returns:
            Dictionary mapping error categories to lists of error messages
        """
        raise NotImplementedError("Subclasses must implement validate method")


class GameDataValidator(BaseValidator):
    """
    Validator for GameDataModel instances following C# validation patterns.
    """

    def validate(self, data: GameDataModel) -> Dict[str, List[str]]:
        """
        Validate a GameDataModel instance.

        Args:
            data: GameDataModel instance to validate

        Returns:
            Dictionary mapping error categories to lists of error messages
        """
        errors = {"critical": [], "warning": [], "info": []}

        # Validate ID is positive
        if data.id <= 0:
            errors["critical"].append(f"ID must be positive, got {data.id}")

        # Validate name is not empty
        if not data.name or not data.name.strip():
            errors["warning"].append(f"Object with ID {data.id} has empty name")

        # Validate name length (not too long for UI)
        if len(data.name) > 100:
            errors["warning"].append(
                f"Name for ID {data.id} is too long ({len(data.name)} chars)"
            )

        # Validate description length (reasonable limit)
        if len(data.description) > 1000:
            errors["warning"].append(
                f"Description for ID {data.id} is very long ({len(data.description)} chars)"
            )

        # Log the validation results
        total_errors = sum(len(error_list) for error_list in errors.values())
        if total_errors == 0:
            self.logger.debug(
                f"Validation passed for {data.__class__.__name__} ID {data.id}"
            )
        else:
            self.logger.info(
                f"Validation found {total_errors} issues for {data.__class__.__name__} ID {data.id}"
            )

        return errors


class CrossReferenceValidator(BaseValidator):
    """
    Validator for cross-references between different data types.
    """

    def __init__(self):
        super().__init__()
        self._data_registry: Dict[str, Dict[int, GameDataModel]] = {}

    def register_data_set(self, data_type: str, data_items: List[GameDataModel]):
        """
        Register a set of data items to validate cross-references against.

        Args:
            data_type: Type of data (e.g., 'items', 'spells', 'quests')
            data_items: List of GameDataModel instances to register
        """
        self._data_registry[data_type] = {item.id: item for item in data_items}
        self.logger.debug(
            f"Registered {len(data_items)} {data_type} for cross-reference validation"
        )

    def validate(self, data: GameDataModel) -> Dict[str, List[str]]:
        """
        Validate cross-references in the provided data.

        Args:
            data: GameDataModel instance to validate for cross-references

        Returns:
            Dictionary mapping error categories to lists of error messages
        """
        errors = {"critical": [], "warning": [], "info": []}

        # Example cross-reference validations:
        # - Check if referenced IDs exist in other data sets
        # - Validate dependency chains
        # - Check prerequisite relationships

        # This would be expanded with specific validation logic for different
        # types of cross-references found in SpellForce data

        # For now, we'll just implement a simple check for quest parent references
        if hasattr(data, "parent_quest_id") and data.parent_quest_id is not None:
            if "quests" in self._data_registry:
                if data.parent_quest_id not in self._data_registry["quests"]:
                    errors["critical"].append(
                        f"Parent quest ID {data.parent_quest_id} does not exist"
                    )

        return errors


class DataIntegrityValidator(BaseValidator):
    """
    Validator for data integrity following C# SFEngine patterns.
    Checks for common data integrity issues in game data.
    """

    def validate(self, data: GameDataModel) -> Dict[str, List[str]]:
        """
        Validate data integrity for a GameDataModel instance.

        Args:
            data: GameDataModel instance to validate

        Returns:
            Dictionary mapping error categories to lists of error messages
        """
        errors = {"critical": [], "warning": [], "info": []}

        # Perform data integrity checks
        # This could include checks like:
        # - Range validation for numeric values
        # - Format validation for text fields
        # - Constraint validation for logical relationships

        # Example: Check for reasonable bounds on common numeric fields
        if hasattr(data, "value") and isinstance(data.value, int):
            if data.value > 1000000:  # Arbitrary high value check
                errors["warning"].append(f"Value {data.value} seems unusually high")

        if hasattr(data, "required_level") and isinstance(data.required_level, int):
            if data.required_level > 100:  # Max level in game
                errors["critical"].append(
                    f"Required level {data.required_level} exceeds game maximum"
                )

        return errors
