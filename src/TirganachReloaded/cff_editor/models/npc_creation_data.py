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

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export"""
        return {
            "strength": self.strength,
            "stamina": self.stamina,
            "agility": self.agility,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NpcStats':
        """Create from dictionary"""
        return cls(**data)


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

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export"""
        return {
            "health": self.health,
            "mana": self.mana,
            "melee_attack": self.melee_attack,
            "ranged_attack": self.ranged_attack,
            "magic_attack": self.magic_attack,
            "physical_defense": self.physical_defense,
            "magic_defense": self.magic_defense,
            "fire_resistance": self.fire_resistance,
            "ice_resistance": self.ice_resistance,
            "black_resistance": self.black_resistance,
            "mind_resistance": self.mind_resistance
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NpcCombatStats':
        """Create from dictionary"""
        return cls(**data)


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

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export"""
        return {
            "helmet_item_id": self.helmet_item_id,
            "chest_item_id": self.chest_item_id,
            "legs_item_id": self.legs_item_id,
            "right_hand_item_id": self.right_hand_item_id,
            "left_hand_item_id": self.left_hand_item_id,
            "right_ring_item_id": self.right_ring_item_id,
            "left_ring_item_id": self.left_ring_item_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NpcEquipment':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class NpcAppearance:
    """Visual appearance settings"""
    head_id: int = 0  # 0-31 available
    race: str = "HUMANS"  # Race enum value
    gender: str = "MALE"  # Gender enum value
    voice_type: VoiceType = VoiceType.MAIN_CHARACTER_MALE

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export"""
        return {
            "head_id": self.head_id,
            "race": self.race,
            "gender": self.gender,
            "voice_type": self.voice_type.value
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NpcAppearance':
        """Create from dictionary"""
        data_copy = data.copy()
        data_copy['voice_type'] = VoiceType(data.get('voice_type', 'main_male'))
        return cls(**data_copy)


@dataclass
class NpcBehavior:
    """AI and behavior settings"""
    movement_type: str = "stationary"  # stationary, patrol, wander
    interaction_radius: int = 5
    spawn_location: Optional[Tuple[int, int]] = None  # (x, y) coordinates
    spawn_conditions: Dict[str, Any] = field(default_factory=dict)  # time, quest state, etc.

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export"""
        return {
            "movement_type": self.movement_type,
            "interaction_radius": self.interaction_radius,
            "spawn_location": list(self.spawn_location) if self.spawn_location else None,
            "spawn_conditions": self.spawn_conditions
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NpcBehavior':
        """Create from dictionary"""
        data_copy = data.copy()
        if data.get('spawn_location'):
            data_copy['spawn_location'] = tuple(data['spawn_location'])
        return cls(**data_copy)


@dataclass
class NpcRewards:
    """Quest rewards when NPC is defeated or completes objective"""
    experience: int = 0
    gold: int = 0
    items: List[Dict[str, int]] = field(default_factory=list)  # [{"item_id": 123, "quantity": 1}]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export"""
        return {
            "experience": self.experience,
            "gold": self.gold,
            "items": self.items
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NpcRewards':
        """Create from dictionary"""
        return cls(**data)


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

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export"""
        return {
            "npc_id": self.npc_id,
            "creation_mode": self.creation_mode,
            "source_npc_id": self.source_npc_id,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "npc_type": self.npc_type.value,
            "character_class": self.character_class.value,
            "level": self.level,
            "faction": self.faction,
            "base_stats": self.base_stats.to_dict(),
            "derived_stats": self.derived_stats.to_dict(),
            "appearance": self.appearance.to_dict(),
            "behavior": self.behavior.to_dict(),
            "equipment": self.equipment.to_dict(),
            "rewards": self.rewards.to_dict(),
            "special_abilities": self.special_abilities
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NpcCreationData':
        """Create from dictionary"""
        data_copy = data.copy()

        # Convert enums
        data_copy['npc_type'] = NpcType(data.get('npc_type', 'friendly'))
        data_copy['character_class'] = CharacterClass(data.get('character_class', 'warrior'))

        # Convert nested objects
        data_copy['base_stats'] = NpcStats.from_dict(data.get('base_stats', {}))
        data_copy['derived_stats'] = NpcCombatStats.from_dict(data.get('derived_stats', {}))
        data_copy['appearance'] = NpcAppearance.from_dict(data.get('appearance', {}))
        data_copy['behavior'] = NpcBehavior.from_dict(data.get('behavior', {}))
        data_copy['equipment'] = NpcEquipment.from_dict(data.get('equipment', {}))
        data_copy['rewards'] = NpcRewards.from_dict(data.get('rewards', {}))

        return cls(**data_copy)


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