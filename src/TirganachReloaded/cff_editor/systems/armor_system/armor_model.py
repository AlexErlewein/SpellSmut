"""
Armor Model Definition

This module defines the Armor class which is used across the Armor Forge modules.
"""

import json
from typing import Dict, List, Any, Optional


# Define armor slot constants
SLOT_HEAD = 0
SLOT_CHEST = 2
SLOT_LEGS = 5
SLOT_FEET = 7
SLOT_RIGHT_RING = 4
SLOT_LEFT_RING = 6
SLOT_LEFT_HAND = 3  # Shield slot

# Define armor types
ARMOR_TYPES = [
    "Cloth", "Leather", "Chain", "Plate", "Magic"
]

# Define material categories
MATERIAL_CATEGORIES = [
    "Leather", "Iron", "Steel", "Mithril", "Adamantite", "Dragon Scale",
    "Elven Chain", "Dwarven Steel", "Runed Metal", "Enchanted Cloth"
]

# Define quality tiers
QUALITY_TIERS = [
    "Common", "Uncommon", "Rare", "Epic", "Legendary", "Unique"
]

# Define class restrictions
CLASS_RESTRICTIONS = [
    "None", "Warrior", "Mage", "Rogue", "Cleric", "Ranger", "Paladin", "Necromancer"
]


class Armor:
    def __init__(self, armor_id: int, name: str = "", display_name: str = "", description: str = ""):
        self.id = armor_id
        self.name = name
        self.display_name = display_name
        self.description = description
        
        # Classification
        self.slot = None  # Head, Chest, Legs, Feet, Ring, Shield
        self.armor_type = None  # Cloth, Leather, Chain, Plate, Magic
        self.material = None  # Leather, Iron, Steel, etc.
        self.tier = "Common"  # Quality tier
        self.level_requirement = 1
        self.class_restriction = "None"
        
        # Core stats
        self.strength = 0
        self.stamina = 0
        self.agility = 0
        self.dexterity = 0
        self.intelligence = 0
        self.wisdom = 0
        self.charisma = 0
        self.health = 0
        self.mana = 0
        self.armor_value = 0  # Physical defense
        
        # Resists
        self.resist_fire = 0
        self.resist_ice = 0
        self.resist_black = 0
        self.resist_mind = 0
        self.physical_resist = 0
        self.magic_resist = 0
        self.critical_resist = 0
        
        # Speed modifiers
        self.run_speed = 0  # Percentage change
        self.fight_speed = 0  # Percentage change
        self.cast_speed = 0  # Percentage change
        self.stealth_bonus = 0
        self.swimming_speed = 0
        self.jump_height = 0
        
        # Visual properties
        self.icon_id = 0
        self.model_ref = ""
        self.texture = ""
        self.normal_map = ""
        
        # Advanced features
        self.set_id = None
        self.set_bonus = {}  # For 2/3/4-piece bonuses
        self.special_abilities = []
        self.enchantment_slots = 0
        self.stat_balance_rating = 0.0
        
        # Requirements (including school requirements)
        self.requirements = {
            "strength": 0,
            "dexterity": 0,
            "intelligence": 0,
            "level": 1,
            "school_requirements": []
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert armor object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            
            # Classification
            'slot': self.slot,
            'armor_type': self.armor_type,
            'material': self.material,
            'tier': self.tier,
            'level_requirement': self.level_requirement,
            'class_restriction': self.class_restriction,
            
            # Core stats
            'strength': self.strength,
            'stamina': self.stamina,
            'agility': self.agility,
            'dexterity': self.dexterity,
            'intelligence': self.intelligence,
            'wisdom': self.wisdom,
            'charisma': self.charisma,
            'health': self.health,
            'mana': self.mana,
            'armor_value': self.armor_value,
            
            # Resists
            'resist_fire': self.resist_fire,
            'resist_ice': self.resist_ice,
            'resist_black': self.resist_black,
            'resist_mind': self.resist_mind,
            'physical_resist': self.physical_resist,
            'magic_resist': self.magic_resist,
            'critical_resist': self.critical_resist,
            
            # Speed modifiers
            'run_speed': self.run_speed,
            'fight_speed': self.fight_speed,
            'cast_speed': self.cast_speed,
            'stealth_bonus': self.stealth_bonus,
            'swimming_speed': self.swimming_speed,
            'jump_height': self.jump_height,
            
            # Visual properties
            'icon_id': self.icon_id,
            'model_ref': self.model_ref,
            'texture': self.texture,
            'normal_map': self.normal_map,
            
            # Advanced features
            'set_id': self.set_id,
            'set_bonus': self.set_bonus,
            'special_abilities': self.special_abilities,
            'enchantment_slots': self.enchantment_slots,
            'stat_balance_rating': self.stat_balance_rating,
            
            # Requirements
            'requirements': self.requirements
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create armor object from dictionary"""
        armor = cls(
            armor_id=data['id'],
            name=data.get('name', ''),
            display_name=data.get('display_name', ''),
            description=data.get('description', '')
        )
        
        # Classification
        armor.slot = data.get('slot')
        armor.armor_type = data.get('armor_type')
        armor.material = data.get('material')
        armor.tier = data.get('tier', 'Common')
        armor.level_requirement = data.get('level_requirement', 1)
        armor.class_restriction = data.get('class_restriction', 'None')
        
        # Core stats
        armor.strength = data.get('strength', 0)
        armor.stamina = data.get('stamina', 0)
        armor.agility = data.get('agility', 0)
        armor.dexterity = data.get('dexterity', 0)
        armor.intelligence = data.get('intelligence', 0)
        armor.wisdom = data.get('wisdom', 0)
        armor.charisma = data.get('charisma', 0)
        armor.health = data.get('health', 0)
        armor.mana = data.get('mana', 0)
        armor.armor_value = data.get('armor_value', 0)
        
        # Resists
        armor.resist_fire = data.get('resist_fire', 0)
        armor.resist_ice = data.get('resist_ice', 0)
        armor.resist_black = data.get('resist_black', 0)
        armor.resist_mind = data.get('resist_mind', 0)
        armor.physical_resist = data.get('physical_resist', 0)
        armor.magic_resist = data.get('magic_resist', 0)
        armor.critical_resist = data.get('critical_resist', 0)
        
        # Speed modifiers
        armor.run_speed = data.get('run_speed', 0)
        armor.fight_speed = data.get('fight_speed', 0)
        armor.cast_speed = data.get('cast_speed', 0)
        armor.stealth_bonus = data.get('stealth_bonus', 0)
        armor.swimming_speed = data.get('swimming_speed', 0)
        armor.jump_height = data.get('jump_height', 0)
        
        # Visual properties
        armor.icon_id = data.get('icon_id', 0)
        armor.model_ref = data.get('model_ref', '')
        armor.texture = data.get('texture', '')
        armor.normal_map = data.get('normal_map', '')
        
        # Advanced features
        armor.set_id = data.get('set_id')
        armor.set_bonus = data.get('set_bonus', {})
        armor.special_abilities = data.get('special_abilities', [])
        armor.enchantment_slots = data.get('enchantment_slots', 0)
        armor.stat_balance_rating = data.get('stat_balance_rating', 0.0)
        
        # Requirements (preserve school requirements from CFF data)
        armor.requirements = data.get('requirements', {
            "strength": 0,
            "dexterity": 0,
            "intelligence": 0,
            "level": 1,
            "school_requirements": []
        })
        
        return armor