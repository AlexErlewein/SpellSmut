"""
The Armor Forge - 7-Phase Armor Creation System

This module implements the 7-phase armor creation system allowing users to create
custom armor pieces with full stat customization, material integration, set bonuses,
and visual customization.
"""

import json
import os
from typing import Dict, List, Any, Optional

# Import from existing modules
try:
    from ....tirganach import GameData
    from ....shared.id_manager import IDManager, ContentType
    from .armor_model import Armor, ARMOR_TYPES, MATERIAL_CATEGORIES, QUALITY_TIERS, CLASS_RESTRICTIONS, SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_FEET, SLOT_RIGHT_RING, SLOT_LEFT_RING, SLOT_LEFT_HAND
    from .armor_sets import ArmorSetManager
    from .cff_armor_export import export_armor_to_cff
except ImportError:
    # For direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
    try:
        from TirganachReloaded.tirganach import GameData
        from TirganachReloaded.cff_editor.shared.id_manager import IDManager, ContentType
        from TirganachReloaded.cff_editor.systems.armor_system.armor_model import Armor, ARMOR_TYPES, MATERIAL_CATEGORIES, QUALITY_TIERS, CLASS_RESTRICTIONS, SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_FEET, SLOT_RIGHT_RING, SLOT_LEFT_RING, SLOT_LEFT_HAND
        from TirganachReloaded.cff_editor.systems.armor_system.armor_sets import ArmorSetManager
        from TirganachReloaded.cff_editor.systems.armor_system.cff_armor_export import export_armor_to_cff
    except ImportError:
        from tirganach import GameData
        from cff_editor.shared.id_manager import IDManager, ContentType
        from armor_system.armor_model import Armor, ARMOR_TYPES, MATERIAL_CATEGORIES, QUALITY_TIERS, CLASS_RESTRICTIONS, SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_FEET, SLOT_RIGHT_RING, SLOT_LEFT_RING, SLOT_LEFT_HAND
        from armor_system.armor_sets import ArmorSetManager
        from armor_system.cff_armor_export import export_armor_to_cff



class ArmorForge:
    """
    The 7-Phase Armor Creation System
    """
    
    def __init__(self):
        self.id_manager = IDManager()
        self.enhanced_armor_file = os.path.join(
            os.path.dirname(__file__), 'enhanced_armor.json'
        )
        self.armors = self.load_armors()
        self.set_manager = ArmorSetManager(self.enhanced_armor_file)
        
    def load_armors(self) -> Dict[int, Armor]:
        """Load existing armors from the enhanced_armor.json file"""
        armors = {}
        if os.path.exists(self.enhanced_armor_file):
            try:
                with open(self.enhanced_armor_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Check if the data is structured with 'armors' and 'sets' keys
                    if isinstance(data, dict) and 'armors' in data:
                        # New format: { "armors": [...], "sets": [...] }
                        for armor_data in data.get('armors', []):
                            armor = Armor.from_dict(armor_data)
                            armors[armor.id] = armor
                    else:
                        # Old format: list of armor objects
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

    def save_armors(self):
        """Save all armors to the enhanced_armor.json file"""
        try:
            # Load existing data to preserve other entries
            existing_data = []
            if os.path.exists(self.enhanced_armor_file):
                with open(self.enhanced_armor_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # Convert our armors to old format for compatibility
            armors_in_old_format = []
            for armor in self.armors.values():
                old_format = self._convert_new_format_to_old(armor.to_dict())
                armors_in_old_format.append(old_format)
            
            # Write the data in the old format to maintain compatibility
            with open(self.enhanced_armor_file, 'w', encoding='utf-8') as f:
                json.dump(armors_in_old_format, f, indent=2)
        except Exception as e:
            print(f"Error saving armors: {e}")

    def _convert_new_format_to_old(self, new_data: Dict) -> Dict:
        """Convert new format to old format for compatibility"""
        # Map new fields back to old ones
        old_data = {
            'item_id': new_data['id'],
            'name': new_data['name'],
            'name_id': 0,  # Not sure what this was in the original
            'item_type': 'EQUIPMENT',
            'item_subtype': self._infer_subtype_from_slot(new_data['slot']),
            
            # Core stats
            'strength': new_data['strength'],
            'stamina': new_data['stamina'],
            'agility': new_data['agility'],
            'dexterity': new_data['dexterity'],
            'intelligence': new_data['intelligence'],
            'wisdom': new_data['wisdom'],
            'charisma': new_data['charisma'],
            'health': new_data['health'],
            'mana': new_data['mana'],
            'armor': new_data['armor_value'],
            
            # Resists
            'resist_fire': new_data['resist_fire'],
            'resist_ice': new_data['resist_ice'],
            'resist_black': new_data['resist_black'],
            'resist_mind': new_data['resist_mind'],
            
            # Speed modifiers
            'speed_run': new_data['run_speed'],
            'speed_fight': new_data['fight_speed'],
            'speed_cast': new_data['cast_speed']
        }
        return old_data

    def _infer_subtype_from_slot(self, slot: int) -> str:
        """Infer item subtype from slot ID"""
        slot_map = {
            SLOT_HEAD: 'HELMET',
            SLOT_CHEST: 'UPPER',
            SLOT_LEGS: 'LOWER',
            SLOT_FEET: 'BOOTS',
            SLOT_RIGHT_RING: 'RING',
            SLOT_LEFT_RING: 'RING',  # Treat left ring same as right
            SLOT_LEFT_HAND: 'SHIELD'
        }
        return slot_map.get(slot, 'ARMOR')

    def get_available_id(self) -> int:
        """Get the next available ID in the armor range"""
        return self.id_manager.get_next_id(ContentType.ARMOR)

    def create_new_armor(self) -> Armor:
        """Phase 1: Create a new armor with auto-assigned ID"""
        new_id = self.get_available_id()
        return Armor(new_id)

    def edit_existing_armor(self, armor_id: int) -> Optional[Armor]:
        """Phase 1: Load an existing armor for editing"""
        return self.armors.get(armor_id)

    def duplicate_armor(self, armor_id: int) -> Optional[Armor]:
        """Phase 1: Create a duplicate of an existing armor"""
        original = self.armors.get(armor_id)
        if original:
            new_id = self.get_available_id()
            # Create a copy with new ID
            new_armor = Armor.from_dict(original.to_dict())
            new_armor.id = new_id
            new_armor.name = f"{original.name} (Copy)"
            return new_armor
        return None

    def phase1_mode_selection(self) -> tuple[str, int, Optional[Armor]]:
        """
        Phase 1: Mode Selection & ID Assignment
        
        Returns:
            - mode: 'create_new', 'edit_existing', or 'duplicate'
            - chosen_id: selected ID for the armor
            - armor: the armor object to work with
        """
        print("\n" + "="*60)
        print("              THE ARMOR FORGE - PHASE 1")
        print("            Mode Selection & ID Assignment")
        print("="*60)
        
        print("\nChoose an operation mode:")
        print("1. Create New Armor")
        print("2. Edit Existing Armor")
        print("3. Duplicate Existing Armor")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                if choice in ['1', '2', '3']:
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return None, None, None
        
        if choice == '1':
            # Create new armor
            armor = self.create_new_armor()
            print(f"\nNew armor created with ID: {armor.id}")
            return 'create_new', armor.id, armor
            
        elif choice == '2':
            # Edit existing armor
            print("\nCurrent armor IDs in system:")
            for armor_id in sorted(self.armors.keys()):
                armor = self.armors[armor_id]
                print(f"  ID: {armor_id} - Name: {armor.name}")
            
            while True:
                try:
                    edit_id = int(input("\nEnter the ID of the armor to edit: ").strip())
                    armor = self.edit_existing_armor(edit_id)
                    if armor:
                        print(f"Editing armor: {armor.name} (ID: {armor.id})")
                        return 'edit_existing', edit_id, armor
                    else:
                        print(f"No armor found with ID {edit_id}")
                except ValueError:
                    print("Invalid ID. Please enter a number.")
                    
        elif choice == '3':
            # Duplicate existing armor
            print("\nCurrent armor IDs in system:")
            for armor_id in sorted(self.armors.keys()):
                armor = self.armors[armor_id]
                print(f"  ID: {armor_id} - Name: {armor.name}")
            
            while True:
                try:
                    dup_id = int(input("\nEnter the ID of the armor to duplicate: ").strip())
                    armor = self.duplicate_armor(dup_id)
                    if armor:
                        print(f"Duplicating armor: {self.armors[dup_id].name}")
                        print(f"New armor created with ID: {armor.id}")
                        return 'duplicate', armor.id, armor
                    else:
                        print(f"No armor found with ID {dup_id}")
                except ValueError:
                    print("Invalid ID. Please enter a number.")
        
        return None, None, None

    def phase2_basic_properties(self, armor: Armor) -> Armor:
        """
        Phase 2: Basic Properties & Classification
        """
        print("\n" + "="*60)
        print("              THE ARMOR FORGE - PHASE 2")
        print("         Basic Properties & Classification")
        print("="*60)
        
        # Naming & Identity
        armor.name = input(f"\nArmor Name (current: '{armor.name}'): ").strip() or armor.name
        armor.display_name = input(f"Display Name (tooltip) (current: '{armor.display_name}'): ").strip() or armor.display_name
        armor.description = input(f"Description (flavor text) (current: '{armor.description}'): ").strip() or armor.description
        
        # Slot Classification
        print(f"\nCurrent Armor Slot: {armor.slot}")
        print("\nSelect Equipment Slot:")
        slots = {
            '0': ('Head/Helmet', SLOT_HEAD),
            '2': ('Chest/Armor', SLOT_CHEST),
            '5': ('Legs/Pants', SLOT_LEGS),
            '7': ('Boots/Feet', SLOT_FEET),
            '4': ('Right Ring', SLOT_RIGHT_RING),
            '6': ('Left Ring', SLOT_LEFT_RING),
            '3': ('Left Hand/Shield', SLOT_LEFT_HAND)
        }
        
        for key, (name, _) in slots.items():
            print(f"{key}. {name}")
        
        while True:
            slot_choice = input(f"\nEnter slot number (0-7, current: {armor.slot}): ").strip()
            if slot_choice in slots:
                armor.slot = slots[slot_choice][1]
                break
            elif slot_choice == '':
                break
            else:
                print("Invalid choice. Please enter 0, 2, 3, 4, 5, 6, or 7.")
        
        # Armor Type
        print(f"\nCurrent Armor Type: {armor.armor_type}")
        print("\nSelect Armor Type:")
        for i, armor_type in enumerate(ARMOR_TYPES, 1):
            print(f"{i}. {armor_type}")
        
        while True:
            try:
                type_choice = input(f"\nEnter type number (1-{len(ARMOR_TYPES)}, current: {armor.armor_type}): ").strip()
                if type_choice == '':
                    break
                type_choice = int(type_choice)
                if 1 <= type_choice <= len(ARMOR_TYPES):
                    armor.armor_type = ARMOR_TYPES[type_choice - 1]
                    break
                else:
                    print(f"Invalid choice. Please enter 1-{len(ARMOR_TYPES)}.")
            except ValueError:
                print(f"Invalid choice. Please enter 1-{len(ARMOR_TYPES)}.")
        
        # Material Category
        print(f"\nCurrent Material: {armor.material}")
        print("\nSelect Material Category:")
        for i, material in enumerate(MATERIAL_CATEGORIES, 1):
            print(f"{i}. {material}")
        
        while True:
            try:
                mat_choice = input(f"\nEnter material number (1-{len(MATERIAL_CATEGORIES)}, current: {armor.material}): ").strip()
                if mat_choice == '':
                    break
                mat_choice = int(mat_choice)
                if 1 <= mat_choice <= len(MATERIAL_CATEGORIES):
                    armor.material = MATERIAL_CATEGORIES[mat_choice - 1]
                    break
                else:
                    print(f"Invalid choice. Please enter 1-{len(MATERIAL_CATEGORIES)}.")
            except ValueError:
                print(f"Invalid choice. Please enter 1-{len(MATERIAL_CATEGORIES)}.")
        
        # Quality & Rarity
        print(f"\nCurrent Tier: {armor.tier}")
        print("\nSelect Quality Tier:")
        for i, tier in enumerate(QUALITY_TIERS, 1):
            print(f"{i}. {tier}")
        
        while True:
            try:
                tier_choice = input(f"\nEnter tier number (1-{len(QUALITY_TIERS)}, current: {armor.tier}): ").strip()
                if tier_choice == '':
                    break
                tier_choice = int(tier_choice)
                if 1 <= tier_choice <= len(QUALITY_TIERS):
                    armor.tier = QUALITY_TIERS[tier_choice - 1]
                    break
                else:
                    print(f"Invalid choice. Please enter 1-{len(QUALITY_TIERS)}.")
            except ValueError:
                print(f"Invalid choice. Please enter 1-{len(QUALITY_TIERS)}.")
        
        # Level requirement
        while True:
            try:
                level_req = input(f"\nLevel Requirement (current: {armor.level_requirement}): ").strip()
                if level_req == '':
                    break
                armor.level_requirement = int(level_req)
                if armor.level_requirement < 1:
                    print("Level requirement must be at least 1.")
                    continue
                break
            except ValueError:
                print("Invalid value. Please enter a number.")
        
        # Class restriction
        print(f"\nCurrent Class Restriction: {armor.class_restriction}")
        print("\nSelect Class Restriction:")
        for i, cls in enumerate(CLASS_RESTRICTIONS, 1):
            print(f"{i}. {cls}")
        
        while True:
            try:
                cls_choice = input(f"\nEnter class number (1-{len(CLASS_RESTRICTIONS)}, current: {armor.class_restriction}): ").strip()
                if cls_choice == '':
                    break
                cls_choice = int(cls_choice)
                if 1 <= cls_choice <= len(CLASS_RESTRICTIONS):
                    armor.class_restriction = CLASS_RESTRICTIONS[cls_choice - 1]
                    break
                else:
                    print(f"Invalid choice. Please enter 1-{len(CLASS_RESTRICTIONS)}.")
            except ValueError:
                print(f"Invalid choice. Please enter 1-{len(CLASS_RESTRICTIONS)}.")

        return armor

    def phase3_core_stats(self, armor: Armor) -> Armor:
        """
        Phase 3: Core Stat Bonuses
        """
        print("\n" + "="*60)
        print("              THE ARMOR FORGE - PHASE 3")
        print("                 Core Stat Bonuses")
        print("="*60)
        
        print(f"\nCurrent stats for {armor.name} (ID: {armor.id}):")
        
        # Primary stats
        stats = {
            'strength': 'Strength',
            'stamina': 'Stamina',
            'agility': 'Agility',
            'dexterity': 'Dexterity',
            'intelligence': 'Intelligence',
            'wisdom': 'Wisdom',
            'charisma': 'Charisma'
        }
        
        for attr, name in stats.items():
            current_value = getattr(armor, attr)
            while True:
                try:
                    new_value = input(f"{name} (current: {current_value}): ").strip()
                    if new_value == '':
                        break
                    setattr(armor, attr, int(new_value))
                    break
                except ValueError:
                    print("Invalid value. Please enter a number.")
        
        # Derived stats
        derived_stats = {
            'health': 'Health Bonus',
            'mana': 'Mana Bonus',
            'armor_value': 'Base Armor Value'
        }
        
        for attr, name in derived_stats.items():
            current_value = getattr(armor, attr)
            while True:
                try:
                    new_value = input(f"{name} (current: {current_value}): ").strip()
                    if new_value == '':
                        break
                    setattr(armor, attr, int(new_value))
                    break
                except ValueError:
                    print("Invalid value. Please enter a number.")
        
        return armor

    def phase4_resistances(self, armor: Armor) -> Armor:
        """
        Phase 4: Resistance & Defense Systems
        """
        print("\n" + "="*60)
        print("              THE ARMOR FORGE - PHASE 4")
        print("            Resistance & Defense Systems")
        print("="*60)
        
        print(f"\nCurrent resistances for {armor.name} (ID: {armor.id}):")
        
        # Elemental resistances
        resists = {
            'resist_fire': 'Fire Resistance (%)',
            'resist_ice': 'Ice Resistance (%)',
            'resist_black': 'Black Magic Resistance (%)',
            'resist_mind': 'Mind Magic Resistance (%)'
        }
        
        for attr, name in resists.items():
            current_value = getattr(armor, attr)
            while True:
                try:
                    new_value = input(f"{name} (current: {current_value}%): ").strip()
                    if new_value == '':
                        break
                    new_value = int(new_value)
                    if -100 <= new_value <= 100:  # Reasonable limits
                        setattr(armor, attr, new_value)
                        break
                    else:
                        print("Value must be between -100% and 100%.")
                except ValueError:
                    print("Invalid value. Please enter a number.")
        
        # Defense mechanics
        defense_stats = {
            'physical_resist': 'Physical Damage Reduction (%)',
            'magic_resist': 'Magic Damage Reduction (%)',
            'critical_resist': 'Critical Hit Reduction (%)'
        }
        
        for attr, name in defense_stats.items():
            current_value = getattr(armor, attr)
            while True:
                try:
                    new_value = input(f"{name} (current: {current_value}%): ").strip()
                    if new_value == '':
                        break
                    new_value = int(new_value)
                    if -100 <= new_value <= 100:  # Reasonable limits
                        setattr(armor, attr, new_value)
                        break
                    else:
                        print("Value must be between -100% and 100%.")
                except ValueError:
                    print("Invalid value. Please enter a number.")
        
        return armor

    def phase5_speed_modifiers(self, armor: Armor) -> Armor:
        """
        Phase 5: Speed & Mobility Modifiers
        """
        print("\n" + "="*60)
        print("              THE ARMOR FORGE - PHASE 5")
        print("            Speed & Mobility Modifiers")
        print("="*60)
        
        print(f"\nCurrent speed modifiers for {armor.name} (ID: {armor.id}):")
        
        # Speed modifiers
        speed_mods = {
            'run_speed': 'Run Speed (% change)',
            'fight_speed': 'Fight Speed (% change)',
            'cast_speed': 'Cast Speed (% change)'
        }
        
        for attr, name in speed_mods.items():
            current_value = getattr(armor, attr)
            while True:
                try:
                    new_value = input(f"{name} (current: {current_value}%): ").strip()
                    if new_value == '':
                        break
                    new_value = int(new_value)
                    if -100 <= new_value <= 100:  # Reasonable limits
                        setattr(armor, attr, new_value)
                        break
                    else:
                        print("Value must be between -100% and 100%.")
                except ValueError:
                    print("Invalid value. Please enter a number.")
        
        # Special movement bonuses
        special_movements = {
            'stealth_bonus': 'Stealth Bonus',
            'swimming_speed': 'Swimming Speed',
            'jump_height': 'Jump Height'
        }
        
        for attr, name in special_movements.items():
            current_value = getattr(armor, attr)
            while True:
                try:
                    new_value = input(f"{name} (current: {current_value}): ").strip()
                    if new_value == '':
                        break
                    setattr(armor, attr, int(new_value))
                    break
                except ValueError:
                    print("Invalid value. Please enter a number.")
        
        return armor

    def phase6_visual_properties(self, armor: Armor) -> Armor:
        """
        Phase 6: Visual Properties & Materials
        """
        print("\n" + "="*60)
        print("              THE ARMOR FORGE - PHASE 6")
        print("         Visual Properties & Materials")
        print("="*60)
        
        print(f"\nVisual properties for {armor.name} (ID: {armor.id}):")
        
        # Icon selection
        current_icon = getattr(armor, 'icon_id', 0)
        while True:
            try:
                new_icon = input(f"Icon ID (current: {current_icon}): ").strip()
                if new_icon == '':
                    break
                setattr(armor, 'icon_id', int(new_icon))
                break
            except ValueError:
                print("Invalid value. Please enter a number.")
        
        # 3D model reference
        current_model = getattr(armor, 'model_ref', '')
        new_model = input(f"3D Model Reference (current: '{current_model}'): ").strip()
        if new_model != '':
            setattr(armor, 'model_ref', new_model)
        
        # Texture assignment
        current_texture = getattr(armor, 'texture', '')
        new_texture = input(f"Texture (current: '{current_texture}'): ").strip()
        if new_texture != '':
            setattr(armor, 'texture', new_texture)
        
        # Normal map
        current_normal = getattr(armor, 'normal_map', '')
        new_normal = input(f"Normal Map (current: '{current_normal}'): ").strip()
        if new_normal != '':
            setattr(armor, 'normal_map', new_normal)
        
        # Material properties
        current_material_name = getattr(armor, 'material', '')
        new_material_name = input(f"Material Name (current: '{current_material_name}'): ").strip()
        if new_material_name != '':
            setattr(armor, 'material', new_material_name)
        
        return armor

    def phase7_advanced_features(self, armor: Armor) -> Armor:
        """
        Phase 7: Advanced Features & Export
        """
        print("\n" + "="*60)
        print("              THE ARMOR FORGE - PHASE 7")
        print("          Advanced Features & Export")
        print("="*60)
        
        print(f"\nAdvanced features for {armor.name} (ID: {armor.id}):")
        
        # Item set assignment
        current_set = getattr(armor, 'set_id', None)
        print(f"\nCurrent sets in system:")
        for set_id, armor_set in self.set_manager.sets.items():
            print(f"  Set {set_id}: {armor_set.name}")
        
        set_input = input(f"\nSet ID (current: {current_set}, or 'none' to not assign to a set): ").strip()
        if set_input.lower() == 'none' or set_input == '':
            if current_set is not None and current_set in self.set_manager.sets:
                # Remove armor from the current set
                self.set_manager.remove_armor_from_set(armor.id, current_set)
            setattr(armor, 'set_id', None)
            armor.set_id = None
        else:
            try:
                new_set_id = int(set_input)
                if new_set_id in self.set_manager.sets:
                    # Add to existing set
                    self.set_manager.add_armor_to_set(armor.id, new_set_id)
                    setattr(armor, 'set_id', new_set_id)
                    print(f"Armor added to set '{self.set_manager.sets[new_set_id].name}'")
                else:
                    # Option to create new set
                    create_new = input(f"Set ID {new_set_id} doesn't exist. Create new set? (y/n): ").strip().lower()
                    if create_new == 'y':
                        set_name = input(f"Enter name for the new set: ").strip()
                        self.set_manager.create_set(new_set_id, set_name)
                        self.set_manager.add_armor_to_set(armor.id, new_set_id)
                        setattr(armor, 'set_id', new_set_id)
                        print(f"Created new set '{set_name}' and added armor to it")
            except ValueError:
                print("Invalid set ID. Keeping current value.")
        
        # Enchantment slots
        current_slots = getattr(armor, 'enchantment_slots', 0)
        while True:
            try:
                new_slots = input(f"Enchantment Slots (current: {current_slots}): ").strip()
                if new_slots == '':
                    break
                new_slots = int(new_slots)
                if new_slots >= 0:
                    setattr(armor, 'enchantment_slots', new_slots)
                    break
                else:
                    print("Enchantment slots must be 0 or more.")
            except ValueError:
                print("Invalid value. Please enter a number.")
        
        # Calculate stat balance rating (simplified)
        total_positive_stats = (
            armor.strength + armor.stamina + armor.agility + armor.dexterity +
            armor.intelligence + armor.wisdom + armor.charisma +
            armor.health + armor.mana + armor.armor_value +
            max(0, armor.resist_fire) + max(0, armor.resist_ice) +
            max(0, armor.resist_black) + max(0, armor.resist_mind) +
            max(0, armor.physical_resist) + max(0, armor.magic_resist) +
            max(0, armor.run_speed) + max(0, armor.fight_speed) + max(0, armor.cast_speed)
        )
        
        total_negative_stats = (
            abs(min(0, armor.resist_fire)) + abs(min(0, armor.resist_ice)) +
            abs(min(0, armor.resist_black)) + abs(min(0, armor.resist_mind)) +
            abs(min(0, armor.physical_resist)) + abs(min(0, armor.magic_resist)) +
            abs(min(0, armor.run_speed)) + abs(min(0, armor.fight_speed)) + abs(min(0, armor.cast_speed))
        )
        
        # Calculate effective stat value considering requirements
        effective_stats = total_positive_stats - total_negative_stats
        
        # Consider level requirement as a balancing factor
        # Higher level requirement allows for more powerful items
        if armor.level_requirement > 0:
            effective_value = effective_stats / armor.level_requirement * 5  # Arbitrary scaling factor
        else:
            effective_value = effective_stats
            
        # Calculate a more nuanced balance rating
        # Base rating on effective value but capped to reasonable levels
        if armor.tier == "Common":
            max_expected_value = 100
        elif armor.tier == "Uncommon":
            max_expected_value = 200
        elif armor.tier == "Rare":
            max_expected_value = 400
        elif armor.tier == "Epic":
            max_expected_value = 700
        elif armor.tier == "Legendary":
            max_expected_value = 1200
        else:  # Unique
            max_expected_value = 2000
            
        balance_rating = min(100.0, (effective_value / max_expected_value) * 100 if max_expected_value > 0 else 0)
        setattr(armor, 'stat_balance_rating', round(balance_rating, 2))
        
        print(f"\nStat Balance Rating: {balance_rating:.2f}%")
        
        return armor

    def create_armor(self):
        """
        Main method to create an armor through all 7 phases
        """
        # Phase 1: Mode Selection & ID Assignment
        mode, armor_id, armor = self.phase1_mode_selection()
        
        if armor is None:
            print("Operation cancelled.")
            return None
        
        # Phase 2: Basic Properties & Classification
        armor = self.phase2_basic_properties(armor)
        
        # Phase 3: Core Stat Bonuses
        armor = self.phase3_core_stats(armor)
        
        # Phase 4: Resistance & Defense Systems
        armor = self.phase4_resistances(armor)
        
        # Phase 5: Speed & Mobility Modifiers
        armor = self.phase5_speed_modifiers(armor)
        
        # Phase 6: Visual Properties & Materials
        armor = self.phase6_visual_properties(armor)
        
        # Phase 7: Advanced Features & Export
        armor = self.phase7_advanced_features(armor)
        
        # Add to armors dictionary
        self.armors[armor.id] = armor
        
        # Calculate and store stat balance rating
        armor.stat_balance_rating = self.calculate_stat_balance(armor)
        
        # Save to file
        self.save_armors()
        
        # Export to CFF
        cff_path = export_armor_to_cff(armor)
        
        print("\n" + "="*60)
        print(f"     ARMOR FORGE COMPLETE: {armor.name} (ID: {armor.id})")
        print("="*60)
        print(f"Stat Balance Rating: {armor.stat_balance_rating:.2f}%")
        print("Armor has been saved to enhanced_armor.json")
        print(f"CFF file exported to: {cff_path}")
        
        return armor

    def calculate_stat_balance(self, armor: Armor) -> float:
        """
        Calculate a simple balance rating based on the total stats
        """
        total_positive_stats = (
            armor.strength + armor.stamina + armor.agility + armor.dexterity +
            armor.intelligence + armor.wisdom + armor.charisma +
            armor.health + armor.mana + armor.armor_value +
            max(0, armor.resist_fire) + max(0, armor.resist_ice) +
            max(0, armor.resist_black) + max(0, armor.resist_mind) +
            max(0, armor.physical_resist) + max(0, armor.magic_resist) +
            max(0, armor.run_speed) + max(0, armor.fight_speed) + max(0, armor.cast_speed)
        )
        
        total_negative_stats = (
            abs(min(0, armor.resist_fire)) + abs(min(0, armor.resist_ice)) +
            abs(min(0, armor.resist_black)) + abs(min(0, armor.resist_mind)) +
            abs(min(0, armor.physical_resist)) + abs(min(0, armor.magic_resist)) +
            abs(min(0, armor.run_speed)) + abs(min(0, armor.fight_speed)) + abs(min(0, armor.cast_speed))
        )
        
        # Calculate effective stat value considering requirements
        effective_stats = total_positive_stats - total_negative_stats
        
        # Consider level requirement as a balancing factor
        # Higher level requirement allows for more powerful items
        if armor.level_requirement > 0:
            effective_value = effective_stats / armor.level_requirement * 5  # Arbitrary scaling factor
        else:
            effective_value = effective_stats
        
        # Calculate a more nuanced balance rating
        # Base rating on effective value but capped to reasonable levels
        if armor.tier == "Common":
            max_expected_value = 100
        elif armor.tier == "Uncommon":
            max_expected_value = 200
        elif armor.tier == "Rare":
            max_expected_value = 400
        elif armor.tier == "Epic":
            max_expected_value = 700
        elif armor.tier == "Legendary":
            max_expected_value = 1200
        else:  # Unique
            max_expected_value = 2000
            
        balance_rating = min(100.0, (effective_value / max_expected_value) * 100 if max_expected_value > 0 else 0)
        return round(balance_rating, 2)


def run_armor_forge():
    """
    Main function to run the armor forge
    """
    print("\n" + "="*60)
    print("                    THE ARMOR FORGE")
    print("            A 7-Phase Armor Creation System")
    print("="*60)
    
    forge = ArmorForge()
    armor = forge.create_armor()
    
    if armor:
        print(f"\nSuccessfully created armor: {armor.name} (ID: {armor.id})")
    else:
        print("\nArmor creation cancelled.")


if __name__ == "__main__":
    run_armor_forge()