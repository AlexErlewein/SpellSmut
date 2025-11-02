"""
Quest Data Models
Data structures for enhanced quest information
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MapLocation:
    """Map location information"""
    code: str  # e.g., "P1", "P63"
    name: str  # e.g., "Liannon", "Greyfell"


@dataclass
class Dialogue:
    """Quest dialogue information"""
    text: str  # German text
    translation: Optional[str] = None  # English translation
    source_file: str = ""  # Lua file path
    dialogue_type: str = "Dialog"  # Say, Answer, Outcry, Dialog, OfferAnswer


@dataclass
class QuestReward:
    """Quest reward information"""
    xp: int = 0
    reward_flags: List[str] = field(default_factory=list)
    items: List[str] = field(default_factory=list)
    gold: int = 0
    source: str = "script/GdsQuestRewards.lua"


@dataclass
class FileReference:
    """Lua file reference information"""
    path: str
    reference_count: int


@dataclass
class QuestStatistics:
    """Quest statistics summary"""
    total_dialogues: int = 0
    total_files: int = 0
    total_references: int = 0
    total_maps: int = 0
    xp_reward: int = 0


@dataclass
class QuestRelationship:
    """Quest relationship information"""
    quest_id: int
    name: str
    relationship_type: str  # "parent", "sibling", "child"


@dataclass
class EnhancedQuestData:
    """Complete enhanced quest data"""
    # Basic CFF data
    quest_id: int
    name: str
    description: str = ""
    parent_id: int = 0
    order_index: int = 0
    name_id: int = 0
    description_id: int = 0
    
    # Enhanced data
    map_locations: List[MapLocation] = field(default_factory=list)
    dialogues: List[Dialogue] = field(default_factory=list)
    rewards: Optional[QuestReward] = None
    file_references: List[FileReference] = field(default_factory=list)
    statistics: Optional[QuestStatistics] = None
    relationships: List[QuestRelationship] = field(default_factory=list)
    
    # Additional metadata
    has_extended_dialogues: bool = False
    lua_files_count: int = 0
    total_lua_references: int = 0
