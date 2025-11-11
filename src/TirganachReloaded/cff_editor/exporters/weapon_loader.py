import json
from pathlib import Path
from typing import Optional

from TirganachReloaded.tirganach import GameData
from ..models.weapon_creation_data import (
    DamageCategory,
    DamageType,
    Rarity,
    WeaponCreationData,
    WeaponEffect,
    WeaponHands,
    WeaponRequirements,
    SchoolRequirement,
)


class WeaponLoader:
    """Load and save weapon data"""

    @staticmethod
    def load_weapon(
        weapon_id: int, gamedata_path: Optional[str] = None
    ) -> WeaponCreationData:
        """Load existing weapon by ID from GameData.cff"""

        # Try to load from GameData.cff first for full stats
        if gamedata_path and Path(gamedata_path).exists():
            try:
                gd = GameData(gamedata_path)
                weapons = gd.weapons.where(item_id=weapon_id)

                if weapons:
                    weapon = weapons[0]
                    return WeaponLoader._convert_from_gamedata(weapon, gd)
            except Exception as e:
                print(f"Warning: Could not load from GameData: {e}")
                # Fall back to JSON

        # Fallback to enhanced_weapons.json (basic info only)
        current_file = Path(__file__)
        weapons_file = current_file.parent.parent.parent / "enhanced_weapons.json"

        if not weapons_file.exists():
            raise FileNotFoundError(f"Weapons file not found at: {weapons_file}")

        with open(weapons_file, "r") as f:
            weapons = json.load(f)

        weapon_data = next((w for w in weapons if w["item_id"] == weapon_id), None)
        if not weapon_data:
            raise ValueError(f"Weapon ID {weapon_id} not found")

        # Convert to WeaponCreationData with defaults
        return WeaponCreationData(
            weapon_id=weapon_data["item_id"],
            creation_mode="edit",
            source_weapon_id=weapon_data["item_id"],
            weapon_name=weapon_data["name"],
            weapon_type_id=weapon_data.get("weapon_type_id", 4),
            weapon_type_name=weapon_data.get("weapon_type_name", ""),
            weapon_material_id=weapon_data.get("weapon_material_id", 5),
            weapon_material_name=weapon_data.get("weapon_material_name", ""),
            hands=WeaponLoader._determine_hands_from_type(
                weapon_data.get("weapon_type_name", "")
            ),
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
            icon_handle="",  # Will be populated from UI data
            hit_sound="battle_hit_1hsword",
            miss_sound="battle_miss_sword",
            equip_sound="",
            model_file="",  # Would need to be populated from model mapping
            trail_effect="",
            impact_effect="",
        )

    @staticmethod
    def _convert_from_gamedata(weapon, gd) -> WeaponCreationData:
        """Convert from GameData Weapon entity to WeaponCreationData"""

        # Get related item data
        item = weapon.item
        item_ui = None
        icon_handle = ""

        # Try to get UI data for icon
        try:
            item_uis = gd.item_ui.where(item_id=weapon.item_id)
            if item_uis:
                item_ui = item_uis[0]
                icon_handle = (
                    item_ui.item_ui_handle.strip() if item_ui.item_ui_handle else ""
                )
        except:
            pass

        # Get type and material names
        weapon_type_name = ""
        weapon_material_name = ""

        try:
            type_names = gd.weapon_type_names.where(weapon_type_id=weapon.weapon_type)
            if type_names:
                weapon_type_name = type_names[0].name
        except:
            pass

        try:
            material_names = gd.weapon_material_names.where(
                weapon_material_id=weapon.material
            )
            if material_names:
                weapon_material_name = material_names[0].name
        except:
            pass

        # Determine damage type based on weapon type
        damage_type = WeaponLoader._determine_damage_type(
            weapon.weapon_type, weapon_type_name
        )

        # Determine hands and category
        hands = WeaponLoader._determine_hands_from_type(weapon_type_name)
        damage_category = WeaponLoader._damage_category_from_range(weapon.max_range)

        # Get requirements from item if available
        requirements = WeaponRequirements()
        try:
            if hasattr(item, "requirements") and item.requirements:
                # Handle school requirements
                school_requirements = []

                for req in item.requirements:
                    # Convert school requirement
                    if hasattr(req, "requirement_school") and req.requirement_school:
                        school_req = SchoolRequirement(
                            school_name=req.requirement_school.name, level=req.level
                        )
                        school_requirements.append(school_req)

                # Get stat requirements (if available)
                reqs = (
                    item.requirements[0]
                    if isinstance(item.requirements, list)
                    else item.requirements
                )
                requirements = WeaponRequirements(
                    strength=getattr(reqs, "strength", 0),
                    dexterity=getattr(reqs, "dexterity", 0),
                    intelligence=getattr(reqs, "intelligence", 0),
                    level=getattr(reqs, "level", 1),
                    school_requirements=school_requirements,
                )
        except Exception as e:
            print(f"Warning: Could not load requirements: {e}")
            pass

        return WeaponCreationData(
            weapon_id=weapon.item_id,
            creation_mode="edit",
            source_weapon_id=weapon.item_id,
            weapon_name=item.name if item else f"Weapon {weapon.item_id}",
            weapon_type_id=weapon.weapon_type,
            weapon_type_name=weapon_type_name,
            weapon_material_id=weapon.material,
            weapon_material_name=weapon_material_name,
            hands=hands,
            damage_category=damage_category,
            description="",  # Would need to get from descriptions table
            min_damage=weapon.min_damage,
            max_damage=weapon.max_damage,
            damage_type=damage_type,
            attack_speed=weapon.speed,
            min_range=weapon.min_range,
            max_range=weapon.max_range,
            attack_arc=90,  # Default melee arc
            critical_chance=5.0,  # Default crit chance
            armor_penetration=0.0,
            knockback_chance=0.0,
            requirements=requirements,
            sell_value=item.selling_price if item else 0,
            buy_value=item.buying_price if item else 0,
            rarity=Rarity.COMMON,  # Default rarity
            effects=[],  # Would need to populate from weapon.effects
            item_set_id=item.item_set_id if item else 0,
            icon_handle=icon_handle,
            hit_sound="battle_hit_1hsword",
            miss_sound="battle_miss_sword",
            equip_sound="",
            model_file="",
            trail_effect="",
            impact_effect="",
        )

    @staticmethod
    def _determine_hands_from_type(weapon_type_name: str) -> WeaponHands:
        """Determine if weapon is one-handed or two-handed based on type name"""
        weapon_type_lower = weapon_type_name.lower()

        if any(
            two_hand in weapon_type_lower
            for two_hand in [
                "2h",
                "twoh",
                "twohanded",
                "two-handed",
                "great",
                "polearm",
            ]
        ):
            return WeaponHands.TWO_HANDED
        elif "1h" in weapon_type_lower or "oneh" in weapon_type_lower:
            return WeaponHands.ONE_HANDED
        elif any(ranged in weapon_type_lower for ranged in ["bow", "crossbow", "xbow"]):
            return WeaponHands.TWO_HANDED  # Most ranged weapons are two-handed
        else:
            return WeaponHands.ONE_HANDED  # Default assumption

    @staticmethod
    def _determine_damage_type(
        weapon_type_id: int, weapon_type_name: str
    ) -> DamageType:
        """Determine damage type based on weapon type"""
        type_lower = weapon_type_name.lower()

        if any(
            slash in type_lower
            for slash in ["sword", "blade", "axe", "dagger", "cleaver"]
        ):
            return DamageType.SLASH
        elif any(pierce in type_lower for pierce in ["spear", "pike", "bolt", "arrow"]):
            return DamageType.PIERCE
        elif any(crush in type_lower for crush in ["hammer", "mace", "club", "staff"]):
            return DamageType.CRUSH
        else:
            return DamageType.SLASH  # Default

    @staticmethod
    def _damage_category_from_range(max_range: int) -> DamageCategory:
        """Determine if weapon is melee or ranged based on range"""
        if max_range > 5:  # Arbitrary threshold for "ranged"
            return DamageCategory.RANGED
        else:
            return DamageCategory.MELEE

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
