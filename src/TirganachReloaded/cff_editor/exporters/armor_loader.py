"""
Armor Loader - Load and save armor data
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

from ..models.armor_creation_data import ArmorCreationData, ArmorSlot, ArmorType, ArmorTier


class ArmorLoader:
    """Load and save armor data"""

    @staticmethod
    def load_armor(armor_id: int) -> Optional[ArmorCreationData]:
        """Load existing armor by ID"""
        try:
            with open("src/TirganachReloaded/enhanced_armor.json", 'r') as f:
                armor_list = json.load(f)

            armor_data = next((a for a in armor_list if a['item_id'] == armor_id), None)
            if not armor_data:
                return None

            # Convert to ArmorCreationData
            return ArmorCreationData(
                armor_id=armor_data['item_id'],
                creation_mode="edit",
                source_armor_id=armor_data['item_id'],
                armor_name=armor_data.get('name', ''),
                # Map slot from item_subtype
                slot=ArmorLoader._map_slot_from_subtype(armor_data.get('item_subtype', 'CHEST')),
                # Infer armor type from stats
                armor_type=ArmorLoader._infer_armor_type(armor_data),
                material_name=armor_data.get('material_name', ''),
                # Infer tier from stats
                tier=ArmorLoader._infer_tier(armor_data),
                # Basic stats
                strength=armor_data.get('strength', 0),
                stamina=armor_data.get('stamina', 0),
                agility=armor_data.get('agility', 0),
                dexterity=armor_data.get('dexterity', 0),
                intelligence=armor_data.get('intelligence', 0),
                wisdom=armor_data.get('wisdom', 0),
                charisma=armor_data.get('charisma', 0),
                health_bonus=armor_data.get('health', 0),
                mana_bonus=armor_data.get('mana', 0),
                base_armor=armor_data.get('armor', 0),
                # Resistances
                resist_fire=armor_data.get('resist_fire', 0.0),
                resist_ice=armor_data.get('resist_ice', 0.0),
                resist_black=armor_data.get('resist_black', 0.0),
                resist_mind=armor_data.get('resist_mind', 0.0),
                # Speed modifiers
                run_speed_modifier=armor_data.get('speed_run', 0.0),
                fight_speed_modifier=armor_data.get('speed_fight', 0.0),
                cast_speed_modifier=armor_data.get('speed_cast', 0.0),
                # Other fields with defaults
                icon_handle=armor_data.get('icon_handle', ''),
                created_date=armor_data.get('created_date', datetime.now().isoformat()),
                modified_date=datetime.now().isoformat(),
                author=armor_data.get('author', ''),
                version=armor_data.get('version', 1)
            )

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading armor {armor_id}: {e}")
            return None

    @staticmethod
    def _map_slot_from_subtype(subtype: str) -> ArmorSlot:
        """Map item_subtype to ArmorSlot"""
        subtype_map = {
            'HEAD': ArmorSlot.HEAD,
            'CHEST': ArmorSlot.CHEST,
            'LEGS': ArmorSlot.LEGS,
            'FEET': ArmorSlot.FEET,
            'RIGHT_RING': ArmorSlot.RIGHT_RING,
            'LEFT_RING': ArmorSlot.LEFT_RING,
            'SHIELD': ArmorSlot.LEFT_HAND
        }
        return subtype_map.get(subtype, ArmorSlot.CHEST)

    @staticmethod
    def _infer_armor_type(armor_data: dict) -> ArmorType:
        """Infer armor type from armor stats"""
        armor_value = armor_data.get('armor', 0)

        if armor_value >= 50:
            return ArmorType.PLATE
        elif armor_value >= 30:
            return ArmorType.CHAIN
        elif armor_value >= 15:
            return ArmorType.LEATHER
        elif armor_value >= 5:
            return ArmorType.CLOTH
        else:
            # Check for magic stats
            magic_stats = (armor_data.get('intelligence', 0) +
                          armor_data.get('wisdom', 0) +
                          armor_data.get('mana', 0))
            if magic_stats > 0:
                return ArmorType.MAGIC
            return ArmorType.CLOTH

    @staticmethod
    def _infer_tier(armor_data: dict) -> ArmorTier:
        """Infer armor tier from stats"""
        armor_value = armor_data.get('armor', 0)
        total_stats = (armor_data.get('strength', 0) + armor_data.get('stamina', 0) +
                      armor_data.get('agility', 0) + armor_data.get('dexterity', 0) +
                      armor_data.get('intelligence', 0) + armor_data.get('wisdom', 0) +
                      armor_data.get('charisma', 0))

        # Simple tier inference
        if armor_value >= 60 or total_stats >= 20:
            return ArmorTier.EPIC
        elif armor_value >= 40 or total_stats >= 10:
            return ArmorTier.RARE
        elif armor_value >= 20 or total_stats >= 5:
            return ArmorTier.UNCOMMON
        else:
            return ArmorTier.COMMON

    @staticmethod
    def save_armor(armor_data: ArmorCreationData, export_path: Optional[str] = None) -> str:
        """Save armor to JSON file"""
        if export_path is None:
            # Default path
            os.makedirs("exports/armor", exist_ok=True)
            export_path = f"exports/armor/armor_{armor_data.armor_id}.json"

        # Update modified date
        armor_data.modified_date = datetime.now().isoformat()

        # Convert to dict
        armor_dict = armor_data.to_dict()

        # Add some metadata
        armor_dict['export_date'] = datetime.now().isoformat()
        armor_dict['export_version'] = '1.0'

        # Ensure directory exists
        os.makedirs(os.path.dirname(export_path), exist_ok=True)

        with open(export_path, 'w') as f:
            json.dump(armor_dict, f, indent=2)

        return export_path

    @staticmethod
    def load_all_armor() -> list:
        """Load all armor from enhanced_armor.json"""
        try:
            with open("src/TirganachReloaded/enhanced_armor.json", 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def get_armor_count() -> int:
        """Get total number of armor pieces"""
        return len(ArmorLoader.load_all_armor())

    @staticmethod
    def find_armor_by_name(name: str) -> list:
        """Find armor pieces by name (partial match)"""
        all_armor = ArmorLoader.load_all_armor()
        name_lower = name.lower()
        return [a for a in all_armor if name_lower in a.get('name', '').lower()]

    @staticmethod
    def validate_armor_data(armor_data: ArmorCreationData) -> tuple[list[str], list[str]]:
        """Validate armor data and return (errors, warnings)"""
        errors = []
        warnings = []

        # Check required fields
        if not armor_data.armor_name.strip():
            errors.append("Armor name is required")

        if armor_data.base_armor < 0:
            errors.append("Base armor cannot be negative")

        if armor_data.health_bonus < 0:
            errors.append("Health bonus cannot be negative")

        if armor_data.mana_bonus < 0:
            errors.append("Mana bonus cannot be negative")

        # Check resistances
        for resist_name, resist_value in [
            ("Fire resistance", armor_data.resist_fire),
            ("Ice resistance", armor_data.resist_ice),
            ("Black magic resistance", armor_data.resist_black),
            ("Mind magic resistance", armor_data.resist_mind)
        ]:
            if resist_value < 0 or resist_value > 100:
                errors.append(f"{resist_name} must be between 0% and 100%")

        # Check speed modifiers (reasonable bounds)
        for speed_name, speed_value in [
            ("Run speed", armor_data.run_speed_modifier),
            ("Fight speed", armor_data.fight_speed_modifier),
            ("Cast speed", armor_data.cast_speed_modifier)
        ]:
            if speed_value < -50 or speed_value > 50:
                warnings.append(f"{speed_name} modifier of {speed_value}% seems extreme")

        # Check balance
        balance_rating = armor_data.calculate_balance_rating()
        if balance_rating > 90:
            warnings.append(f"Armor may be overpowered (balance rating: {balance_rating}/100)")
        elif balance_rating < 10:
            warnings.append(f"Armor may be underpowered (balance rating: {balance_rating}/100)")

        # Check for empty but required fields for certain armor types
        if armor_data.armor_type == ArmorType.MAGIC and armor_data.base_armor > 0:
            warnings.append("Magic armor typically has 0 base armor (focus on magical stats)")

        return errors, warnings