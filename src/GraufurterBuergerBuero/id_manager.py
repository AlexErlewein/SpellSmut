"""
ID Management System - Shared across all content creators
"""

import json
import os
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


def get_default_project_ids_path() -> str:
    """
    Get the default path for project_ids.json in the data directory.

    Returns:
        Absolute path to project_ids.json in the data directory
    """
    # Get path relative to this file (in GraufurterBuergerBuero)
    current_file = Path(__file__)
    # Navigate to src/data/
    data_dir = current_file.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    return str(data_dir / "project_ids.json")


class ContentType(Enum):
    """Types of game content that need unique IDs"""

    QUEST = "quest"
    SPELL = "spell"
    WEAPON = "weapon"
    ARMOR = "armor"
    ITEM = "item"
    NPC = "npc"
    CREATURE = "creature"
    BUILDING = "building"
    RACE = "race"


class IDRange:
    """ID range allocation for each content type"""

    # Official game ranges (DO NOT USE)
    OFFICIAL_QUESTS = (1, 299)
    OFFICIAL_SPELLS = (1, 299)
    OFFICIAL_WEAPONS = (1, 1000)
    OFFICIAL_ITEMS = (1, 5000)

    # Custom content ranges (SAFE TO USE)
    CUSTOM_QUESTS = (9000, 9999)
    CUSTOM_SPELLS = (300, 999)
    CUSTOM_WEAPONS = (10000, 19999)
    CUSTOM_ARMOR = (20000, 29999)
    CUSTOM_ITEMS = (30000, 39999)
    CUSTOM_NPCS = (40000, 49999)
    CUSTOM_CREATURES = (50000, 59999)
    CUSTOM_BUILDINGS = (60000, 69999)
    CUSTOM_RACES = (7, 99)  # Race IDs start from 7 (since 1-6 are official races)


class IDManager:
    """Manages unique ID allocation across all content types"""

    def __init__(self, project_file: Optional[str] = None):
        """
        Initialize ID Manager.

        Args:
            project_file: Path to project_ids.json file. If None, uses default location
                         in src/TirganachReloaded/data/project_ids.json
        """
        if project_file is None:
            self.project_file = get_default_project_ids_path()
        else:
            self.project_file = project_file
        self.allocated_ids: Dict[ContentType, Set[int]] = {}
        self.load()

    def load(self):
        """Load existing ID allocations from project file"""
        try:
            if os.path.exists(self.project_file):
                with open(self.project_file, "r") as f:
                    data = json.load(f)
                    for content_type_str, id_list in data.items():
                        content_type = ContentType(content_type_str)
                        self.allocated_ids[content_type] = set(id_list)
        except (FileNotFoundError, json.JSONDecodeError):
            # Initialize empty allocation sets
            pass

        # Ensure all content types are initialized
        for content_type in ContentType:
            if content_type not in self.allocated_ids:
                self.allocated_ids[content_type] = set()

    def save(self):
        """Save ID allocations to project file"""
        data = {}
        for content_type, id_set in self.allocated_ids.items():
            data[content_type.value] = sorted(list(id_set))

        # Ensure directory exists (only if there's a directory path)
        dir_path = os.path.dirname(self.project_file)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        with open(self.project_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_next_id(self, content_type: ContentType) -> int:
        """Get next available ID for content type"""

        # Get valid range for this content type
        id_range = self._get_range(content_type)
        start, end = id_range

        # Find first unused ID in range
        for candidate_id in range(start, end + 1):
            if candidate_id not in self.allocated_ids[content_type]:
                return candidate_id

        raise ValueError(
            f"No available IDs in range {start}-{end} for {content_type.value}"
        )

    def allocate_id(
        self, content_type: ContentType, requested_id: Optional[int] = None
    ) -> int:
        """
        Allocate an ID (auto-assign or use requested ID)

        Args:
            content_type: Type of content
            requested_id: Specific ID to use (optional)

        Returns:
            Allocated ID

        Raises:
            ValueError: If requested ID is already in use or out of range
        """

        if requested_id is None:
            # Auto-assign next available ID
            new_id = self.get_next_id(content_type)
        else:
            # Validate requested ID
            if not self.is_valid_id(content_type, requested_id):
                raise ValueError(
                    f"ID {requested_id} is out of valid range for {content_type.value}"
                )

            if self.is_id_used(content_type, requested_id):
                raise ValueError(
                    f"ID {requested_id} is already in use for {content_type.value}"
                )

            new_id = requested_id

        # Allocate the ID
        self.allocated_ids[content_type].add(new_id)
        self.save()
        return new_id

    def release_id(self, content_type: ContentType, item_id: int):
        """Release an ID back to the pool"""
        if item_id in self.allocated_ids[content_type]:
            self.allocated_ids[content_type].remove(item_id)
            self.save()

    def is_id_used(self, content_type: ContentType, item_id: int) -> bool:
        """Check if ID is already allocated"""
        return item_id in self.allocated_ids[content_type]

    def is_valid_id(self, content_type: ContentType, item_id: int) -> bool:
        """Check if ID is in valid range for content type"""
        id_range = self._get_range(content_type)
        start, end = id_range
        return start <= item_id <= end

    def get_used_ids(self, content_type: ContentType) -> List[int]:
        """Get list of all used IDs for content type"""
        return sorted(list(self.allocated_ids[content_type]))

    def get_available_count(self, content_type: ContentType) -> int:
        """Get count of available IDs"""
        id_range = self._get_range(content_type)
        total_range = id_range[1] - id_range[0] + 1
        used_count = len(self.allocated_ids[content_type])
        return total_range - used_count

    def get_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for all content types"""
        stats = {}
        for content_type in ContentType:
            id_range = self._get_range(content_type)
            total = id_range[1] - id_range[0] + 1
            used = len(self.allocated_ids[content_type])
            available = total - used

            stats[content_type.value] = {
                "range_start": id_range[0],
                "range_end": id_range[1],
                "total_capacity": total,
                "used": used,
                "available": available,
                "usage_percent": round((used / total) * 100, 1) if total > 0 else 0,
            }

        return stats

    def _get_range(self, content_type: ContentType) -> tuple:
        """Get ID range for content type"""
        range_map = {
            ContentType.QUEST: IDRange.CUSTOM_QUESTS,
            ContentType.SPELL: IDRange.CUSTOM_SPELLS,
            ContentType.WEAPON: IDRange.CUSTOM_WEAPONS,
            ContentType.ARMOR: IDRange.CUSTOM_ARMOR,
            ContentType.ITEM: IDRange.CUSTOM_ITEMS,
            ContentType.NPC: IDRange.CUSTOM_NPCS,
            ContentType.CREATURE: IDRange.CUSTOM_CREATURES,
            ContentType.BUILDING: IDRange.CUSTOM_BUILDINGS,
            ContentType.RACE: IDRange.CUSTOM_RACES,
        }
        return range_map.get(content_type, (0, 0))
