"""
Armor Creation Data Model
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from datetime import datetime


class ArmorSlot(Enum):
    """Equipment slots for armor pieces"""
    HEAD = 0      # Helmet
    CHEST = 2     # Chest armor
    LEGS = 5      # Leg armor
    FEET = 7      # Boots
    RIGHT_RING = 4  # Right ring
    LEFT_RING = 6   # Left ring
    LEFT_HAND = 3   # Shield/off-hand


class ArmorType(Enum):
    """Armor material types"""
    CLOTH = "cloth"
    LEATHER = "leather"
    CHAIN = "chain"
    PLATE = "plate"
    MAGIC = "magic"


class ArmorTier(Enum):
    """Armor quality tiers"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    UNIQUE = "unique"


@dataclass
class ArmorRequirements:
    """Stat requirements to equip armor"""
    strength: int = 0
    stamina: int = 0
    agility: int = 0
    dexterity: int = 0
    intelligence: int = 0
    wisdom: int = 0
    charisma: int = 0
    level: int = 1


@dataclass
class ArmorCreationData:
    """Complete armor definition"""

    # Phase 1: Mode & ID
    armor_id: int = 0
    creation_mode: str = "new"  # "new", "edit", "duplicate"
    source_armor_id: Optional[int] = None  # If edit/duplicate mode

    # Phase 2: Basic Properties & Classification
    armor_name: str = ""
    display_name: str = ""
    description: str = ""
    slot: ArmorSlot = ArmorSlot.CHEST
    armor_type: ArmorType = ArmorType.CLOTH
    material_name: str = ""
    tier: ArmorTier = ArmorTier.COMMON
    class_restrictions: Optional[List[str]] = None  # Optional class restrictions

    # Phase 3: Core Stat Bonuses
    strength: int = 0
    stamina: int = 0
    agility: int = 0
    dexterity: int = 0
    intelligence: int = 0
    wisdom: int = 0
    charisma: int = 0
    health_bonus: int = 0
    mana_bonus: int = 0
    base_armor: int = 0

    # Phase 4: Resistance & Defense Systems
    resist_fire: float = 0.0
    resist_ice: float = 0.0
    resist_black: float = 0.0
    resist_mind: float = 0.0
    physical_reduction: float = 0.0
    magic_reduction: float = 0.0
    critical_reduction: float = 0.0

    # Phase 5: Speed & Mobility Modifiers
    run_speed_modifier: float = 0.0  # Percentage change
    fight_speed_modifier: float = 0.0
    cast_speed_modifier: float = 0.0
    stealth_bonus: float = 0.0
    swimming_speed: float = 0.0
    jump_height: float = 0.0

    # Phase 6: Visual Properties & Materials
    icon_handle: str = ""
    mesh_file: str = ""
    texture_file: str = ""
    normal_map: str = ""
    material_color: str = "#808080"  # Hex color
    equip_sound: str = ""
    special_effects: Optional[List[str]] = None

    # Phase 7: Advanced Features
    item_set_id: int = 0
    set_bonuses: Optional[List[dict]] = None  # [{"pieces": 2, "bonus": "Fire Resist +10%"}]
    special_abilities: Optional[List[str]] = None
    enchantment_slots: int = 0

    # Metadata
    created_date: str = ""
    modified_date: str = ""
    author: str = ""
    version: int = 1

    def __post_init__(self):
        """Initialize mutable defaults"""
        if self.class_restrictions is None:
            self.class_restrictions = []
        if self.special_effects is None:
            self.special_effects = []
        if self.set_bonuses is None:
            self.set_bonuses = []
        if self.special_abilities is None:
            self.special_abilities = []

        # Set creation date if not provided
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.modified_date:
            self.modified_date = datetime.now().isoformat()

    def calculate_defense_rating(self) -> float:
        """Calculate overall defense rating (0-100)"""
        # Base armor value
        rating = min(self.base_armor / 50.0, 40.0)  # Max 40 points from base armor

        # Resistance bonuses (max 30 points)
        resist_avg = (self.resist_fire + self.resist_ice +
                     self.resist_black + self.resist_mind) / 4.0
        resist_points = min(resist_avg / 10.0, 30.0)

        # Reduction bonuses (max 30 points)
        reduction_avg = (self.physical_reduction + self.magic_reduction +
                        self.critical_reduction) / 3.0
        reduction_points = min(reduction_avg / 5.0, 30.0)

        return rating + resist_points + reduction_points

    def calculate_balance_rating(self) -> int:
        """Calculate balance rating (0-100)"""
        defense_rating = self.calculate_defense_rating()

        # Adjust for requirements
        total_req = (self.strength + self.stamina + self.agility +
                    self.dexterity + self.intelligence + self.wisdom + self.charisma)
        req_penalty = total_req / 200.0  # Reduce rating by up to 50% for high requirements

        # Adjust for tier
        tier_multiplier = {
            ArmorTier.COMMON: 1.0,
            ArmorTier.UNCOMMON: 1.1,
            ArmorTier.RARE: 1.3,
            ArmorTier.EPIC: 1.6,
            ArmorTier.LEGENDARY: 2.0,
            ArmorTier.UNIQUE: 2.5
        }[self.tier]

        rating = (defense_rating / tier_multiplier) - req_penalty
        return int(max(0, min(100, rating)))

    def get_slot_name(self) -> str:
        """Get human-readable slot name"""
        slot_names = {
            ArmorSlot.HEAD: "Helmet",
            ArmorSlot.CHEST: "Chest Armor",
            ArmorSlot.LEGS: "Leg Armor",
            ArmorSlot.FEET: "Boots",
            ArmorSlot.RIGHT_RING: "Right Ring",
            ArmorSlot.LEFT_RING: "Left Ring",
            ArmorSlot.LEFT_HAND: "Shield"
        }
        return slot_names.get(self.slot, "Unknown")

    def get_total_stat_bonuses(self) -> int:
        """Get sum of all primary stat bonuses"""
        return (self.strength + self.stamina + self.agility + self.dexterity +
                self.intelligence + self.wisdom + self.charisma)

    def is_magic_armor(self) -> bool:
        """Check if this is primarily magic armor"""
        return self.armor_type == ArmorType.MAGIC or any([
            self.intelligence > 0,
            self.wisdom > 0,
            self.mana_bonus > 0,
            self.resist_black > 0,
            self.resist_mind > 0,
            self.cast_speed_modifier != 0
        ])

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export"""
        return {
            "armor_id": self.armor_id,
            "creation_mode": self.creation_mode,
            "source_armor_id": self.source_armor_id,
            "armor_name": self.armor_name,
            "display_name": self.display_name,
            "description": self.description,
            "slot": self.slot.value,
            "armor_type": self.armor_type.value,
            "material_name": self.material_name,
            "tier": self.tier.value,
            "class_restrictions": self.class_restrictions,
            "strength": self.strength,
            "stamina": self.stamina,
            "agility": self.agility,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
            "health_bonus": self.health_bonus,
            "mana_bonus": self.mana_bonus,
            "base_armor": self.base_armor,
            "resist_fire": self.resist_fire,
            "resist_ice": self.resist_ice,
            "resist_black": self.resist_black,
            "resist_mind": self.resist_mind,
            "physical_reduction": self.physical_reduction,
            "magic_reduction": self.magic_reduction,
            "critical_reduction": self.critical_reduction,
            "run_speed_modifier": self.run_speed_modifier,
            "fight_speed_modifier": self.fight_speed_modifier,
            "cast_speed_modifier": self.cast_speed_modifier,
            "stealth_bonus": self.stealth_bonus,
            "swimming_speed": self.swimming_speed,
            "jump_height": self.jump_height,
            "icon_handle": self.icon_handle,
            "mesh_file": self.mesh_file,
            "texture_file": self.texture_file,
            "normal_map": self.normal_map,
            "material_color": self.material_color,
            "equip_sound": self.equip_sound,
            "special_effects": self.special_effects,
            "item_set_id": self.item_set_id,
            "set_bonuses": self.set_bonuses,
            "special_abilities": self.special_abilities,
            "enchantment_slots": self.enchantment_slots,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "author": self.author,
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ArmorCreationData':
        """Create from dictionary"""
        # Convert slot and enums back
        data_copy = data.copy()
        data_copy['slot'] = ArmorSlot(data.get('slot', 2))
        data_copy['armor_type'] = ArmorType(data.get('armor_type', 'cloth'))
        data_copy['tier'] = ArmorTier(data.get('tier', 'common'))

        return cls(**data_copy)