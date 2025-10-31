import json
from pathlib import Path

from ..models.weapon_creation_data import (
    DamageCategory,
    DamageType,
    Rarity,
    WeaponCreationData,
    WeaponEffect,
    WeaponHands,
    WeaponRequirements,
)


class WeaponLoader:
    """Load and save weapon data"""

    @staticmethod
    def load_weapon(weapon_id: int) -> WeaponCreationData:
        """Load existing weapon by ID"""
        # Load from enhanced_weapons.json using absolute path
        current_file = Path(__file__)
        weapons_file = current_file.parent.parent.parent / "enhanced_weapons.json"
        
        if not weapons_file.exists():
            raise FileNotFoundError(f"Weapons file not found at: {weapons_file}")
        
        with open(weapons_file, "r") as f:
            weapons = json.load(f)

        weapon_data = next((w for w in weapons if w["item_id"] == weapon_id), None)
        if not weapon_data:
            raise ValueError(f"Weapon ID {weapon_id} not found")

        # Convert to WeaponCreationData
        return WeaponCreationData(
            weapon_id=weapon_data["item_id"],
            creation_mode="edit",
            source_weapon_id=weapon_data["item_id"],
            weapon_name=weapon_data["name"],
            weapon_type_id=weapon_data.get("weapon_type_id", 4),
            weapon_type_name=weapon_data.get("weapon_type_name", ""),
            weapon_material_id=weapon_data.get("weapon_material_id", 5),
            weapon_material_name=weapon_data.get("weapon_material_name", ""),
            hands=WeaponHands.ONE_HANDED,  # Default, can be updated based on weapon type
            damage_category=DamageCategory.MELEE,  # Default, can be updated based on weapon type
            description=weapon_data.get("description", ""),
            min_damage=weapon_data.get("min_damage", 10),
            max_damage=weapon_data.get("max_damage", 15),
            damage_type=DamageType.SLASH,  # Default, can be updated based on weapon type
            attack_speed=weapon_data.get("weapon_speed", 100),
            min_range=weapon_data.get("min_range", 0),
            max_range=weapon_data.get("max_range", 2),
            attack_arc=90,  # Default melee arc
            critical_chance=5.0,  # Default crit chance
            armor_penetration=0.0,
            knockback_chance=0.0,
            requirements=WeaponRequirements(),  # Use defaults
            sell_value=weapon_data.get("sell_value", 50),
            buy_value=weapon_data.get("buy_value", 100),
            rarity=Rarity.COMMON,  # Default rarity
            effects=[],  # No effects by default
            item_set_id=weapon_data.get("item_set_id", 0),
            icon_handle="",  # Would need to be populated from icon mapping
            hit_sound="battle_hit_1hsword",
            miss_sound="battle_miss_sword",
            equip_sound="",
            model_file="",  # Would need to be populated from model mapping
            trail_effect="",
            impact_effect=""
        )

    @staticmethod
    def save_weapon(weapon_data: WeaponCreationData, export_path: str):
        """Save weapon to JSON file"""
        weapon_dict = {
            "item_id": weapon_data.weapon_id,
            "name": weapon_data.weapon_name,
            "weapon_type_id": weapon_data.weapon_type_id,
            "weapon_material_id": weapon_data.weapon_material_id,
            "min_damage": weapon_data.min_damage,
            "max_damage": weapon_data.max_damage,
            "weapon_speed": weapon_data.attack_speed,
            "min_range": weapon_data.min_range,
            "max_range": weapon_data.max_range,
            "sell_value": weapon_data.sell_value,
            "buy_value": weapon_data.buy_value,
            "rarity": weapon_data.rarity.value,
            "icon_handle": weapon_data.icon_handle,
            "requirements": {
                "strength": weapon_data.requirements.strength,
                "dexterity": weapon_data.requirements.dexterity,
                "intelligence": weapon_data.requirements.intelligence,
                "level": weapon_data.requirements.level,
            },
            "effects": [
                {
                    "effect_id": effect.effect_id,
                    "effect_name": effect.effect_name,
                    "value": effect.value,
                    "duration": effect.duration,
                }
                for effect in weapon_data.effects
            ],
            "created_date": weapon_data.created_date,
            "modified_date": weapon_data.modified_date,
            "author": weapon_data.author,
            "version": weapon_data.version,
        }

        with open(export_path, "w") as f:
            json.dump(weapon_dict, f, indent=2)

    @staticmethod
    def load_weapon_from_file(file_path: str) -> WeaponCreationData:
        """Load weapon from exported JSON file"""
        with open(file_path, "r") as f:
            weapon_dict = json.load(f)

        # Reconstruct WeaponRequirements
        requirements = WeaponRequirements(
            strength=weapon_dict.get("requirements", {}).get("strength", 0),
            dexterity=weapon_dict.get("requirements", {}).get("dexterity", 0),
            intelligence=weapon_dict.get("requirements", {}).get("intelligence", 0),
            level=weapon_dict.get("requirements", {}).get("level", 1),
        )

        # Reconstruct effects
        effects = []
        for effect_data in weapon_dict.get("effects", []):
            effects.append(
                WeaponEffect(
                    effect_id=effect_data.get("effect_id", 0),
                    effect_name=effect_data.get("effect_name", ""),
                    value=effect_data.get("value", 0.0),
                    duration=effect_data.get("duration", 0.0),
                )
            )

        # Create WeaponCreationData
        weapon = WeaponCreationData(
            weapon_id=weapon_dict["item_id"],
            creation_mode=weapon_dict.get("creation_mode", "new"),
            weapon_name=weapon_dict["name"],
            weapon_type_id=weapon_dict.get("weapon_type_id", 4),
            weapon_type_name=weapon_dict.get("weapon_type_name", ""),
            weapon_material_id=weapon_dict.get("weapon_material_id", 5),
            weapon_material_name=weapon_dict.get("weapon_material_name", ""),
            min_damage=weapon_dict.get("min_damage", 10),
            max_damage=weapon_dict.get("max_damage", 15),
            attack_speed=weapon_dict.get("weapon_speed", 100),
            min_range=weapon_dict.get("min_range", 0),
            max_range=weapon_dict.get("max_range", 2),
            sell_value=weapon_dict.get("sell_value", 50),
            buy_value=weapon_dict.get("buy_value", 100),
            rarity=Rarity(weapon_dict.get("rarity", "common")),
            icon_handle=weapon_dict.get("icon_handle", ""),
            requirements=requirements,
            effects=effects,
            created_date=weapon_dict.get("created_date", ""),
            modified_date=weapon_dict.get("modified_date", ""),
            author=weapon_dict.get("author", ""),
            version=weapon_dict.get("version", 1),
        )

        return weapon
