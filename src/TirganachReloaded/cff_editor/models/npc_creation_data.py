from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, field


class NpcType(Enum):
    FRIENDLY = "friendly"
    MERCHANT = "merchant"
    GUARD = "guard"
    HOSTILE = "hostile"


class CharacterClass(Enum):
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    MULTI_CLASS = "multi_class"


class VoiceType(Enum):
    MAIN_CHARACTER_MALE = "main_male"
    MAIN_CHARACTER_FEMALE = "main_female"
    HERO_MALE_1 = "hero_male_1"
    HERO_MALE_2 = "hero_male_2"
    HERO_MALE_3 = "hero_male_3"
    HERO_MALE_4 = "hero_male_4"
    HERO_MALE_5 = "hero_male_5"
    HERO_FEMALE_1 = "hero_female_1"
    HERO_FEMALE_2 = "hero_female_2"
    HERO_FEMALE_3 = "hero_female_3"
    HERO_FEMALE_4 = "hero_female_4"
    HERO_FEMALE_5 = "hero_female_5"
    CREATURE_BEAR = "bear"
    CREATURE_DEMON = "demon"
    CREATURE_DRAGON = "dragon"
    CREATURE_GOBLIN = "goblin"
    CREATURE_OGRE = "ogre"
    CREATURE_SKELETON = "skeleton"
    CREATURE_WOLF = "wolf"
    CREATURE_ZOMBIE = "zombie"


@dataclass
class NpcStats:
    """Base stats for NPC"""
    strength: int = 10
    stamina: int = 10
    agility: int = 10
    dexterity: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10


@dataclass
class NpcCombatStats:
    """Combat-related stats"""
    health: int = 100
    mana: int = 50
    melee_attack: int = 10
    ranged_attack: int = 0
    magic_attack: int = 0
    physical_defense: int = 5
    magic_defense: int = 5
    fire_resistance: int = 0
    ice_resistance: int = 0
    black_resistance: int = 0
    mind_resistance: int = 0


@dataclass
class NpcEquipment:
    """Equipment assigned to NPC"""
    helmet_item_id: Optional[int] = None
    chest_item_id: Optional[int] = None
    legs_item_id: Optional[int] = None
    right_hand_item_id: Optional[int] = None
    left_hand_item_id: Optional[int] = None
    right_ring_item_id: Optional[int] = None
    left_ring_item_id: Optional[int] = None


@dataclass
class NpcAppearance:
    """Visual appearance settings"""
    head_id: int = 0  # 0-31 available
    race: str = "HUMANS"  # Race enum value
    gender: str = "MALE"  # Gender enum value
    voice_type: VoiceType = VoiceType.MAIN_CHARACTER_MALE


@dataclass
class NpcBehavior:
    """AI and behavior settings"""
    movement_type: str = "stationary"  # stationary, patrol, wander
    interaction_radius: int = 5
    spawn_location: Optional[Tuple[int, int]] = None  # (x, y) coordinates
    spawn_conditions: Dict[str, Any] = field(default_factory=dict)  # time, quest state, etc.


@dataclass
class NpcRewards:
    """Quest rewards when NPC is defeated or completes objective"""
    experience: int = 0
    gold: int = 0
    items: List[Dict[str, int]] = field(default_factory=list)  # [{"item_id": 123, "quantity": 1}]


@dataclass
class NpcCreationData:
    """Complete NPC definition for creation wizard"""

    # Phase 1: Mode Selection & ID Assignment
    npc_id: int                           # Managed by ID Manager (40000-49999)
    creation_mode: str                    # "new", "edit", "duplicate"
    source_npc_id: Optional[int] = None   # If edit/duplicate mode

    # Phase 2: Basic Identity & Classification
    name: str = ""
    title: str = ""
    description: str = ""
    npc_type: NpcType = NpcType.FRIENDLY
    character_class: CharacterClass = CharacterClass.WARRIOR
    level: int = 1
    faction: str = "HUMANS"  # Race/faction for AI behavior

    # Phase 3: Base Statistics
    base_stats: NpcStats = field(default_factory=NpcStats)
    derived_stats: NpcCombatStats = field(default_factory=NpcCombatStats)

    # Phase 4: Combat & Skills (Future: detailed skill system)
    # For now, combat stats are in derived_stats above

    # Phase 5: Appearance & Voice
    appearance: NpcAppearance = field(default_factory=NpcAppearance)

    # Phase 6: Behavior & Interaction
    behavior: NpcBehavior = field(default_factory=NpcBehavior)

    # Phase 7: Advanced Features & Export
    equipment: NpcEquipment = field(default_factory=NpcEquipment)
    rewards: NpcRewards = field(default_factory=NpcRewards)
    special_abilities: List[str] = field(default_factory=list)  # Future: spell/ability system


@dataclass
class NpcValidationResult:
    """Result of NPC validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []