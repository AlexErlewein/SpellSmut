"""Python adaptation of C# game data models"""

import logging
from dataclasses import dataclass
from typing import Optional


@dataclass
class GameDataModel:
    """Base class for all game data models with C#-inspired validation"""

    id: int
    name: str = ""
    description: str = ""

    def __post_init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._validate()

    def _validate(self):
        """Basic validation pattern inspired by C# SFEngine"""
        if self.id <= 0:
            raise ValueError(f"ID must be positive, got {self.id}")
        if not self.name.strip():
            self.logger.warning(f"Object with ID {self.id} has empty name")

    def to_dict(self) -> dict:
        """Export to dictionary following C# serialization patterns"""
        return {"id": self.id, "name": self.name, "description": self.description}

    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary following C# deserialization patterns"""
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            description=data.get("description", ""),
        )


@dataclass
class ItemDataModel(GameDataModel):
    """Item model with C#-style validation and properties"""

    type: str = ""
    value: int = 0
    required_level: int = 1

    def _validate(self):
        """Extended validation for items"""
        super()._validate()
        if self.value < 0:
            raise ValueError(f"Item value cannot be negative, got {self.value}")
        if self.required_level < 1:
            raise ValueError(
                f"Required level must be at least 1, got {self.required_level}"
            )


@dataclass
class SpellDataModel(GameDataModel):
    """Spell model with C#-style validation and properties"""

    school: str = ""
    level: int = 1
    mana_cost: int = 0
    range: float = 0.0

    def _validate(self):
        """Extended validation for spells"""
        super()._validate()
        if self.level < 1 or self.level > 15:
            raise ValueError(f"Spell level must be between 1-15, got {self.level}")
        if self.mana_cost < 0:
            raise ValueError(f"Mana cost cannot be negative, got {self.mana_cost}")
        if self.range < 0:
            raise ValueError(f"Spell range cannot be negative, got {self.range}")


@dataclass
class QuestDataModel(GameDataModel):
    """Quest model with C#-style validation and properties"""

    quest_type: str = ""
    required_level: int = 1
    experience_reward: int = 0
    parent_quest_id: Optional[int] = None

    def _validate(self):
        """Extended validation for quests"""
        super()._validate()
        if self.required_level < 1:
            raise ValueError(
                f"Required level must be at least 1, got {self.required_level}"
            )
        if self.experience_reward < 0:
            raise ValueError(
                f"Experience reward cannot be negative, got {self.experience_reward}"
            )
        if self.parent_quest_id is not None and self.parent_quest_id <= 0:
            raise ValueError(
                f"Parent quest ID must be positive or None, got {self.parent_quest_id}"
            )
