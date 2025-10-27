from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class WeaponHands(Enum):
    ONE_HANDED = "1H"
    TWO_HANDED = "2H"
    UNARMED = "Unarmed"

class DamageCategory(Enum):
    MELEE = "melee"
    RANGED = "ranged"
    MAGIC = "magic"

class DamageType(Enum):
    SLASH = "slash"
    PIERCE = "pierce"
    BLUNT = "blunt"
    MIXED = "mixed"

class Rarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class WeaponRequirements:
    """Stat requirements to equip weapon"""
    strength: int = 0
    dexterity: int = 0
    intelligence: int = 0
    level: int = 1

@dataclass
class WeaponEffect:
    """Special effect on weapon"""
    effect_id: int
    effect_name: str  # "Fire Damage", "Poison", "Life Drain"
    value: float      # Effect strength
    duration: float   # Effect duration (if applicable)

@dataclass
class WeaponCreationData:
    """Complete weapon definition"""
    
    # Step 1: Mode & ID
    weapon_id: int                # Managed by ID Manager
    creation_mode: str            # "new", "edit", "duplicate"
    source_weapon_id: Optional[int] = None  # If edit/duplicate mode
    
    # Step 2: Basic Properties
    weapon_name: str = ""
    weapon_type_id: int = 4       # Default to 1H Sword
    weapon_type_name: str = ""
    weapon_material_id: int = 5   # Default to Metal
    weapon_material_name: str = ""
    hands: WeaponHands = WeaponHands.ONE_HANDED
    damage_category: DamageCategory = DamageCategory.MELEE
    description: str = ""
    
    # Step 3: Combat Stats
    min_damage: int = 10
    max_damage: int = 15
    damage_type: DamageType = DamageType.SLASH
    attack_speed: int = 100       # Lower = faster (50-200 range)
    min_range: int = 0
    max_range: int = 2
    attack_arc: int = 90          # Degrees for melee sweep
    critical_chance: float = 5.0  # Percentage
    armor_penetration: float = 0.0
    knockback_chance: float = 0.0
    
    # Step 4: Requirements & Value
    requirements: WeaponRequirements = field(default_factory=WeaponRequirements)
    sell_value: int = 50
    buy_value: int = 100
    rarity: Rarity = Rarity.COMMON
    effects: List[WeaponEffect] = field(default_factory=list)
    item_set_id: int = 0
    
    # Step 5: Visual & Audio
    icon_handle: str = ""
    hit_sound: str = "battle_hit_1hsword"
    miss_sound: str = "battle_miss_sword"
    equip_sound: str = ""
    model_file: str = ""
    trail_effect: str = ""
    impact_effect: str = ""
    
    # Metadata
    created_date: str = ""
    modified_date: str = ""
    author: str = ""
    version: int = 1
    
    def calculate_dps(self) -> float:
        """Calculate damage per second"""
        if self.attack_speed == 0:
            return 0.0
        avg_damage = (self.min_damage + self.max_damage) / 2
        attacks_per_second = 100 / self.attack_speed
        return avg_damage * attacks_per_second
    
    def get_balance_rating(self) -> int:
        """Calculate balance rating (0-100)"""
        # DPS-based rating
        dps = self.calculate_dps()
        
        # Adjust for requirements
        req_factor = (self.requirements.strength + 
                      self.requirements.dexterity + 
                      self.requirements.intelligence) / 100
        
        # Adjust for rarity
        rarity_multiplier = {
            Rarity.COMMON: 1.0,
            Rarity.UNCOMMON: 1.2,
            Rarity.RARE: 1.5,
            Rarity.EPIC: 2.0,
            Rarity.LEGENDARY: 3.0
        }[self.rarity]
        
        rating = (dps / rarity_multiplier) - req_factor
        return int(min(100, max(0, rating)))
