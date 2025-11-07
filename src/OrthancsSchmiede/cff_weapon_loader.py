"""
CFF-based Weapon Loader for Orthancs Schmiede
=============================================

This module provides functionality to load weapon data directly from CFF files,
ensuring access to the most complete and up-to-date weapon information.

Based on the existing weapon_loader.py from TirganachReloaded.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, Signal

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent

sys.path.insert(0, str(project_root))

try:
    from TirganachReloaded.tirganach import GameData
except ImportError:
    GameData = None
    print("Warning: Tirganach library not available. Weapon data will be limited.")


class CFFWeaponLoader(QObject):
    """Load weapon data directly from CFF files"""

    # Signal for progress updates
    progress_updated = Signal(int, str)  # (percentage, message)
    loading_complete = Signal(int)  # (total_weapons_loaded)

    def __init__(self, gamedata_path: Optional[str] = None):
        super().__init__()
        self.gamedata_path = gamedata_path or str(
            project_root / "OriginalGameFiles/data/GameData.cff"
        )
        self.gamedata = None

    def load_all_weapons(self) -> Dict[int, Dict[str, Any]]:
        """Load all weapons from CFF file"""
        weapons = {}

        # Try to load from GameData.cff for complete stats
        if GameData and Path(self.gamedata_path).exists():
            try:
                self.progress_updated.emit(10, "Loading GameData.cff...")
                self.gamedata = GameData(self.gamedata_path)

                # Get all weapons from the GameData
                all_weapons = list(self.gamedata.weapons)  # Convert to list
                total_weapons = len(all_weapons)

                for i, weapon in enumerate(all_weapons):
                    weapon_data = self._convert_weapon_from_gamedata(weapon)
                    weapons[weapon_data["item_id"]] = weapon_data

                    # Update progress
                    progress = int((i + 1) / total_weapons * 90) + 10  # 10-100%
                    self.progress_updated.emit(
                        progress, f"Loading weapon {i + 1}/{total_weapons}"
                    )

            except Exception as e:
                print(f"Error loading from GameData: {e}")

        return weapons

    def _convert_weapon_from_gamedata(self, weapon) -> Dict[str, Any]:
        """Convert from GameData Weapon entity to standard dict format"""

        # Get the related item through the weapon's item relation
        item = getattr(weapon, "item", None)

        weapon_name = f"Weapon {weapon.item_id}"
        sell_value = 0
        buy_value = 0
        item_set_id = 0
        item_type = "WEAPON"
        item_subtype = "WEAPON"
        name_id = 0
        unit_stats_id = 0
        army_unit_id = 0
        building_id = 0
        unknown1 = 0
        
        if item:
            weapon_name = getattr(item, "name", weapon_name)
            sell_value = getattr(item, "selling_price", 0)
            buy_value = getattr(item, "buying_price", 0)
            item_set_id = getattr(item, "item_set_id", 0)
            item_type = getattr(item, "item_type", "WEAPON")
            raw_subtype = getattr(item, "item_subtype", "WEAPON")
            item_subtype = str(raw_subtype).strip()
            name_id = getattr(item, "name_id", 0)
            unit_stats_id = getattr(item, "unit_stats_id", 0)
            army_unit_id = getattr(item, "army_unit_id", 0)
            building_id = getattr(item, "building_id", 0)
            unknown1 = getattr(item, "unknown1", 0)

        # Initialize basic data structure with all available CFF fields
        weapon_data = {
            "item_id": weapon.item_id,
            "weapon_id": weapon.item_id,
            "name": weapon_name,
            "weapon_name": weapon_name,  # Add for compatibility
            "name_id": name_id,
            "weapon_type_id": getattr(weapon, "weapon_type", 0),
            "weapon_material_id": getattr(weapon, "material", 0),
            "min_damage": getattr(weapon, "min_damage", 0),
            "max_damage": getattr(weapon, "max_damage", 0),
            "attack_speed": getattr(weapon, "speed", 100),
            "weapon_speed": getattr(weapon, "speed", 100),  # Add alternative field name
            "min_range": getattr(weapon, "min_range", 0),
            "max_range": getattr(weapon, "max_range", 2),
            "attack_arc": 90,  # Default melee arc
            "critical_chance": 5.0,  # Default crit chance
            "armor_penetration": 0.0,
            "knockback_chance": 0.0,
            "sell_value": sell_value,
            "buy_value": buy_value,
            "item_type": item_type,
            "item_subtype": item_subtype,
            "unit_stats_id": unit_stats_id,
            "army_unit_id": army_unit_id,
            "building_id": building_id,
            "unknown1": unknown1,
            "item_set_id": item_set_id,
            "hands": "One-handed",  # Will be determined from weapon type
            "damage_category": "Melee",  # Will be determined from range
            "damage_type": "Slashing",  # Will be determined from weapon type
            "rarity": "Common",  # Default rarity
        }

        # Try to get more specific information if available
        try:
            # Get requirements from item_requirements table
            if hasattr(self.gamedata, 'item_requirements'):
                item_reqs = self.gamedata.item_requirements.where(item_id=weapon.item_id)
                if item_reqs:
                    # For SpellForce, requirements are school-based rather than stat-based
                    # We'll create a basic requirements structure
                    weapon_data["requirements"] = {
                        "strength": 0,
                        "dexterity": 0,
                        "intelligence": 0,
                        "level": max([req.level for req in item_reqs]) if item_reqs else 1,
                        "school_requirements": [
                            {
                                "requirement_number": req.requirement_number,
                                "requirement_school": str(req.requirement_school),
                                "level": req.level
                            } for req in item_reqs
                        ]
                    }
                else:
                    weapon_data["requirements"] = {
                        "strength": 0,
                        "dexterity": 0,
                        "intelligence": 0,
                        "level": 1,
                        "school_requirements": []
                    }
            else:
                weapon_data["requirements"] = {
                    "strength": 0,
                    "dexterity": 0,
                    "intelligence": 0,
                    "level": 1,
                    "school_requirements": []
                }
        except Exception:
            # If we can't get requirements data, continue with defaults
            weapon_data["requirements"] = {
                "strength": 0,
                "dexterity": 0,
                "intelligence": 0,
                "level": 1,
                "school_requirements": []
            }

        # Try to get weapon type name
        try:
            if hasattr(self.gamedata, "weapon_type_names"):
                type_results = self.gamedata.weapon_type_names.where(
                    weapon_type_id=weapon.weapon_type
                )
                if type_results:
                    type_name = type_results[0].name
                    weapon_data["weapon_type_name"] = type_name
                    weapon_data["weapon_type"] = type_name
                    weapon_data["hands"] = self._determine_hands_from_type(type_name)
                    weapon_data["damage_type"] = self._determine_damage_type(type_name)
        except Exception:
            weapon_data["weapon_type_name"] = f"Type {weapon_data['weapon_type_id']}"
            weapon_data["weapon_type"] = f"Type {weapon_data['weapon_type_id']}"

        # Try to get material name
        try:
            if hasattr(self.gamedata, "weapon_material_names"):
                material_results = self.gamedata.weapon_material_names.where(
                    weapon_material_id=weapon.material
                )
                if material_results:
                    material_name = material_results[0].name
                    weapon_data["weapon_material_name"] = material_name
        except Exception:
            weapon_data["weapon_material_name"] = (
                f"Material {weapon_data['weapon_material_id']}"
            )

        # Get UI handle for icons
        try:
            if hasattr(self.gamedata, 'item_ui'):
                item_uis = self.gamedata.item_ui.where(item_id=weapon.item_id)
                if item_uis and item_uis[0].item_ui_handle:
                    weapon_data["icon_handle"] = item_uis[0].item_ui_handle.strip()
                else:
                    weapon_data["icon_handle"] = ""
            else:
                weapon_data["icon_handle"] = ""
        except Exception:
            weapon_data["icon_handle"] = ""

        # Get item effects
        try:
            if hasattr(self.gamedata, 'item_effects'):
                item_effects = self.gamedata.item_effects.where(item_id=weapon.item_id)
                weapon_data["effects"] = [
                    {
                        "effect_index": eff.effect_index,
                        "effect_id": eff.effect_id
                    } for eff in item_effects
                ]
            else:
                weapon_data["effects"] = []
        except Exception:
            weapon_data["effects"] = []

        # Determine damage category based on range
        weapon_data["damage_category"] = self._damage_category_from_range(
            weapon_data["max_range"]
        )

        # Add item subtype based on the weapon type
        weapon_data["item_subtype"] = "WEAPON"

        return weapon_data

    def _determine_hands_from_type(self, weapon_type_name: str) -> str:
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
            return "Two-handed"
        elif "1h" in weapon_type_lower or "oneh" in weapon_type_lower:
            return "One-handed"
        elif any(ranged in weapon_type_lower for ranged in ["bow", "crossbow", "xbow"]):
            return "Two-handed"  # Most ranged weapons are two-handed
        else:
            return "One-handed"  # Default assumption

    def _determine_damage_type(self, weapon_type_name: str) -> str:
        """Determine damage type based on weapon type"""
        type_lower = weapon_type_name.lower()

        if any(
            slash in type_lower
            for slash in ["sword", "blade", "axe", "dagger", "cleaver"]
        ):
            return "Slashing"
        elif any(pierce in type_lower for pierce in ["spear", "pike", "bolt", "arrow"]):
            return "Piercing"
        elif any(crush in type_lower for crush in ["hammer", "mace", "club", "staff"]):
            return "Crushing"
        else:
            return "Slashing"  # Default

    def _damage_category_from_range(self, max_range: int) -> str:
        """Determine if weapon is melee or ranged based on range"""
        if max_range > 5:  # Arbitrary threshold for "ranged"
            return "Ranged"
        else:
            return "Melee"

    def _load_from_enhanced_json(self) -> Dict[int, Dict[str, Any]]:
        """Fallback to load from enhanced_weapons.json"""
        weapons_file = (
            project_root / "src" / "TirganachReloaded" / "enhanced_weapons.json"
        )
        weapons = {}

        if weapons_file.exists():
            try:
                self.progress_updated.emit(20, "Loading from enhanced_weapons.json...")
                with open(weapons_file, "r", encoding="utf-8") as f:
                    weapons_list = json.load(f)

                for weapon in weapons_list:
                    weapon_id = weapon.get("item_id")
                    if weapon_id:
                        # Add default values for fields that might not exist
                        weapon_data = {
                            "item_id": weapon_id,
                            "weapon_id": weapon_id,
                            "name": weapon.get("name", f"Weapon {weapon_id}"),
                            "name_id": weapon.get("name_id", 0),
                            "weapon_type_name": weapon.get(
                                "weapon_type_name",
                                weapon.get("item_subtype", "Unknown"),
                            ),
                            "item_subtype": weapon.get("item_subtype", "Unknown"),
                            "weapon_material_name": weapon.get(
                                "weapon_material_name", "Unknown"
                            ),
                            "weapon_material_id": weapon.get("weapon_material_id", 0),
                            "min_damage": weapon.get("min_damage", 0),
                            "max_damage": weapon.get("max_damage", 0),
                            "damage_type": weapon.get(
                                "damage_type", "Physical"
                            ),  # Default
                            "attack_speed": weapon.get(
                                "weapon_speed", weapon.get("attack_speed", 0)
                            ),  # weapon_speed is the actual field
                            "min_range": weapon.get("min_range", 0),
                            "max_range": weapon.get("max_range", 0),
                            "attack_arc": weapon.get("attack_arc", 90),  # Default
                            "critical_chance": weapon.get("critical_chance", 0),
                            "armor_penetration": weapon.get("armor_penetration", 0),
                            "knockback_chance": weapon.get("knockback_chance", 0),
                            "sell_value": weapon.get("sell_value", 0),
                            "buy_value": weapon.get("buy_value", 0),
                            "rarity": weapon.get("rarity", "Common"),
                            "weapon_speed": weapon.get("weapon_speed", 0),
                            "option": weapon.get("option", 0),
                            "item_set_id": weapon.get("item_set_id", 0),
                            "hands": weapon.get("hands", "One-handed"),  # Default
                            "damage_category": weapon.get(
                                "damage_category", "Melee"
                            ),  # Default
                        }

                        # Add requirements if they exist in the JSON
                        if "requirements" in weapon:
                            weapon_data["requirements"] = weapon["requirements"]
                        else:
                            weapon_data["requirements"] = {
                                "strength": weapon.get("strength_req", 0),
                                "dexterity": weapon.get("dexterity_req", 0),
                                "intelligence": weapon.get("intelligence_req", 0),
                                "level": weapon.get(
                                    "level_requirement", weapon.get("level", 1)
                                ),
                            }

                        weapons[weapon_id] = weapon_data

                self.progress_updated.emit(
                    100, f"Loaded {len(weapons)} weapons from JSON"
                )
                self.loading_complete.emit(len(weapons))

            except Exception as e:
                print(f"Error loading from enhanced_weapons.json: {e}")
        else:
            self.progress_updated.emit(100, "No weapon data file found")
            self.loading_complete.emit(0)

        return weapons


def main():
    """Main function for testing the loader"""
    import sys

    from PySide6.QtWidgets import QApplication

    QApplication(sys.argv)  # Initialize Qt application

    # Initialize the weapon loader
    loader = CFFWeaponLoader()

    # Connect signals for progress updates
    loader.progress_updated.connect(lambda p, msg: print(f"Progress: {p}% - {msg}"))
    loader.loading_complete.connect(
        lambda count: print(f"Loading complete: {count} weapons loaded")
    )

    # Load weapons
    weapons = loader.load_all_weapons()

    print(f"Loaded {len(weapons)} weapons")
    if weapons:
        # Show sample of first weapon
        first_weapon_id = next(iter(weapons))
        first_weapon = weapons[first_weapon_id]
        print(f"Sample weapon data: {first_weapon}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
