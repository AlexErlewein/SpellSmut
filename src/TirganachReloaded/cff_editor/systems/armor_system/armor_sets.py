"""
Armor Sets System

This module handles the creation and management of armor sets with bonuses
for different numbers of pieces worn.
"""

import json
import os
from typing import Dict, List, Any

# Import Armor class from the dedicated model file
try:
    from .armor_model import Armor
except ImportError:
    # For direct execution
    from cff_editor.systems.armor_system.armor_model import Armor


class ArmorSet:
    """
    Represents an armor set with associated bonuses
    """
    def __init__(self, set_id: int, name: str):
        self.id = set_id
        self.name = name
        self.description = ""
        self.pieces = []  # List of armor IDs that are part of this set
        self.bonuses = {}  # Dict like {2: bonus_stats, 3: bonus_stats, 4: bonus_stats}

    def add_piece(self, armor: Armor):
        """Add an armor piece to the set"""
        if armor.id not in self.pieces:
            self.pieces.append(armor.id)

    def remove_piece(self, armor_id: int):
        """Remove an armor piece from the set"""
        if armor_id in self.pieces:
            self.pieces.remove(armor_id)

    def add_bonus(self, num_pieces: int, bonus_stats: Dict[str, Any]):
        """Add a bonus for wearing a certain number of pieces"""
        self.bonuses[num_pieces] = bonus_stats

    def get_bonus(self, num_pieces: int) -> Dict[str, Any]:
        """Get the bonus for wearing a certain number of pieces"""
        return self.bonuses.get(num_pieces, {})

    def get_pieces_count(self) -> int:
        """Get the total number of pieces in the set"""
        return len(self.pieces)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'pieces': self.pieces,
            'bonuses': self.bonuses
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary"""
        armor_set = cls(
            set_id=data['id'],
            name=data.get('name', 'Unknown Set')
        )
        armor_set.description = data.get('description', '')
        armor_set.pieces = data.get('pieces', [])
        armor_set.bonuses = data.get('bonuses', {})
        return armor_set


class ArmorSetManager:
    """
    Manages armor sets and their bonuses
    """
    def __init__(self, armor_data_file: str = None):
        if armor_data_file:
            self.armor_data_file = armor_data_file
        else:
            self.armor_data_file = os.path.join(
                os.path.dirname(__file__), 'enhanced_armor.json'
            )
        
        self.sets = self.load_sets()
        self.armors = self.load_armors()

    def load_armors(self) -> Dict[int, Armor]:
        """Load armors from the armor data file"""
        armors = {}
        if os.path.exists(self.armor_data_file):
            try:
                with open(self.armor_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Check if the data is structured with 'armors' and 'sets' keys
                    if isinstance(data, dict) and 'armors' in data:
                        # New format: { "armors": [...], "sets": [...] }
                        for armor_data in data.get('armors', []):
                            armor = Armor.from_dict(armor_data)
                            armors[armor.id] = armor
                    else:
                        # Old format: list of armor objects
                        # We'll need to define the conversion here directly
                        for armor_data in data:
                            # Convert old format to new format
                            new_armor_data = self._convert_old_format_to_new(armor_data)
                            armor = Armor.from_dict(new_armor_data)
                            armors[armor.id] = armor
            except Exception as e:
                print(f"Error loading armors: {e}")
        return armors

    def _convert_old_format_to_new(self, old_data: Dict) -> Dict:
        """Convert the old format of armor data to new format"""
        # Map old fields to new ones
        new_data = {
            'id': old_data.get('item_id', 0),
            'name': old_data.get('name', ''),
            'display_name': old_data.get('name', ''),  # Using name as display name in old format
            'description': '',  # Old format doesn't have description
            
            # Classification
            'slot': self._convert_subtype_to_slot(old_data.get('item_subtype', '')),
            'armor_type': self._infer_armor_type(old_data.get('item_subtype', '')),
            'material': 'Unknown',
            'tier': 'Common',
            'level_requirement': 1,
            'class_restriction': 'None',
            
            # Core stats
            'strength': old_data.get('strength', 0),
            'stamina': old_data.get('stamina', 0),
            'agility': old_data.get('agility', 0),
            'dexterity': old_data.get('dexterity', 0),
            'intelligence': old_data.get('intelligence', 0),
            'wisdom': old_data.get('wisdom', 0),
            'charisma': old_data.get('charisma', 0),
            'health': old_data.get('health', 0),
            'mana': old_data.get('mana', 0),
            'armor_value': old_data.get('armor', 0),
            
            # Resists
            'resist_fire': old_data.get('resist_fire', 0),
            'resist_ice': old_data.get('resist_ice', 0),
            'resist_black': old_data.get('resist_black', 0),
            'resist_mind': old_data.get('resist_mind', 0),
            'physical_resist': 0,  # Not in old format
            'magic_resist': 0,     # Not in old format
            'critical_resist': 0,  # Not in old format
            
            # Speed modifiers
            'run_speed': old_data.get('speed_run', 0),
            'fight_speed': old_data.get('speed_fight', 0),
            'cast_speed': old_data.get('speed_cast', 0),
            'stealth_bonus': 0,
            'swimming_speed': 0,
            'jump_height': 0,
            
            # Visual properties
            'icon_id': 0,
            'model_ref': '',
            'texture': '',
            'normal_map': '',
            
            # Advanced features
            'set_id': None,
            'set_bonus': {},
            'special_abilities': [],
            'enchantment_slots': 0,
            'stat_balance_rating': 0.0
        }
        return new_data

    def _convert_subtype_to_slot(self, subtype: str) -> int:
        """Convert item subtype to armor slot"""
        # Define slot constants locally
        SLOT_HEAD = 0
        SLOT_CHEST = 2
        SLOT_LEGS = 5
        SLOT_FEET = 7
        SLOT_RIGHT_RING = 4
        SLOT_LEFT_RING = 6
        SLOT_LEFT_HAND = 3  # Shield slot
        
        subtype_map = {
            'HELMET': SLOT_HEAD,
            'UPPER': SLOT_CHEST,
            'LOWER': SLOT_LEGS,
            'BOOTS': SLOT_FEET,
            'RING': SLOT_RIGHT_RING,
            'SHIELD': SLOT_LEFT_HAND
        }
        return subtype_map.get(subtype, 0)

    def _infer_armor_type(self, subtype: str) -> str:
        """Infer armor type from item subtype"""
        if subtype in ['HELMET', 'UPPER', 'LOWER', 'BOOTS']:
            return 'Plate' if 'Plate' in subtype else 'Unknown'
        elif subtype == 'SHIELD':
            return 'Shield'
        elif subtype == 'RING':
            return 'Jewelry'
        return 'Unknown'

    def load_sets(self) -> Dict[int, ArmorSet]:
        """Load armor sets from the armor data file"""
        sets = {}
        if os.path.exists(self.armor_data_file):
            try:
                with open(self.armor_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Check if the data is structured with 'armors' and 'sets' keys
                    if isinstance(data, dict) and 'sets' in data:
                        # New format: { "armors": [...], "sets": [...] }
                        for set_data in data.get('sets', []):
                            armor_set = ArmorSet.from_dict(set_data)
                            sets[armor_set.id] = armor_set
                    # If using old format, no sets are loaded
            except Exception as e:
                print(f"Error loading sets: {e}")
        return sets

    def save_sets(self):
        """Save armor sets to the data file"""
        try:
            # Reload armors to ensure we have the latest
            self.armors = self.load_armors()
            
            # Prepare data for saving
            set_list = [armor_set.to_dict() for armor_set in self.sets.values()]
            armor_list = [armor.to_dict() for armor in self.armors.values()]
            
            data = {
                'sets': set_list,
                'armors': armor_list,
                'last_updated': '2025-10-28'  # Update timestamp
            }
            
            with open(self.armor_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving sets: {e}")

    def create_set(self, set_id: int, name: str) -> ArmorSet:
        """Create a new armor set"""
        armor_set = ArmorSet(set_id, name)
        self.sets[set_id] = armor_set
        return armor_set

    def get_set(self, set_id: int) -> ArmorSet:
        """Get an armor set by ID"""
        return self.sets.get(set_id)

    def add_armor_to_set(self, armor_id: int, set_id: int):
        """Add an armor piece to an existing set"""
        armor = self.armors.get(armor_id)
        if not armor:
            print(f"Armor with ID {armor_id} not found.")
            return False

        armor_set = self.get_set(set_id)
        if not armor_set:
            print(f"Set with ID {set_id} not found.")
            return False

        armor.set_id = set_id  # Update the armor's set ID
        armor_set.add_piece(armor)
        self.armors[armor_id] = armor  # Update the armor in our collection
        return True

    def remove_armor_from_set(self, armor_id: int, set_id: int):
        """Remove an armor piece from a set"""
        armor_set = self.get_set(set_id)
        if not armor_set:
            print(f"Set with ID {set_id} not found.")
            return False

        armor_set.remove_piece(armor_id)
        # Also update the armor object to remove set reference
        armor = self.armors.get(armor_id)
        if armor and armor.set_id == set_id:
            armor.set_id = None
        return True

    def add_set_bonus(self, set_id: int, num_pieces: int, bonus_stats: Dict[str, Any]):
        """Add a bonus to a set for wearing a specific number of pieces"""
        armor_set = self.get_set(set_id)
        if not armor_set:
            print(f"Set with ID {set_id} not found.")
            return False

        armor_set.add_bonus(num_pieces, bonus_stats)
        return True

    def get_set_bonus(self, set_id: int, num_pieces: int) -> Dict[str, Any]:
        """Get the bonus for wearing a certain number of pieces from a set"""
        armor_set = self.get_set(set_id)
        if not armor_set:
            return {}

        return armor_set.get_bonus(num_pieces)

    def get_equipped_set_bonus(self, equipped_armor_ids: List[int]) -> Dict[str, Any]:
        """Calculate bonuses from all sets that have pieces equipped"""
        total_bonus = {}
        
        # Group equipped armor by set
        set_pieces = {}
        for armor_id in equipped_armor_ids:
            armor = self.armors.get(armor_id)
            if armor and armor.set_id is not None:
                set_id = armor.set_id
                if set_id not in set_pieces:
                    set_pieces[set_id] = []
                set_pieces[set_id].append(armor_id)

        # For each set that has equipped pieces, calculate bonuses
        for set_id, pieces in set_pieces.items():
            armor_set = self.get_set(set_id)
            if not armor_set:
                continue

            num_equipped = len(pieces)
            # Get bonuses for all possible piece counts up to what's equipped
            for count in sorted(armor_set.bonuses.keys(), reverse=True):
                if count <= num_equipped:
                    bonus = armor_set.get_bonus(count)
                    # Add this bonus to the total
                    for stat, value in bonus.items():
                        if stat in total_bonus:
                            total_bonus[stat] += value
                        else:
                            total_bonus[stat] = value
                    break

        return total_bonus

    def get_set_stats(self, set_id: int) -> Dict[str, Any]:
        """Get comprehensive stats about a set"""
        armor_set = self.get_set(set_id)
        if not armor_set:
            return {}

        # Get all armor pieces in the set
        set_armors = [self.armors[pid] for pid in armor_set.pieces if pid in self.armors]
        
        stats = {
            'id': armor_set.id,
            'name': armor_set.name,
            'description': armor_set.description,
            'total_pieces': len(set_armors),
            'bonuses': armor_set.bonuses,
            'pieces_info': [
                {
                    'id': armor.id,
                    'name': armor.name,
                    'slot': armor.slot,
                    'tier': armor.tier
                } for armor in set_armors
            ]
        }

        return stats