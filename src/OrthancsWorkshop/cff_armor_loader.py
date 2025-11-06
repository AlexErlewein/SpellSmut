"""
CFF-based Armor Loader for Orthanc's Workshop
================================================

This module provides functionality to load armor data directly from CFF files,
ensuring access to the most complete and up-to-date armor information.

Based on the existing armor_loader.py from TirganachReloaded.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, Signal

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
import sys

sys.path.insert(0, str(project_root))

try:
    from TirganachReloaded.tirganach import GameData
except ImportError:
    GameData = None
    print("Warning: Tirganach library not available. Armor data will be limited.")


class CFFArmorLoader(QObject):
    """Load armor data directly from CFF files"""

    # Signal for progress updates
    progress_updated = Signal(int, str)  # (percentage, message)
    loading_complete = Signal(int)  # (total_armor_loaded)

    def __init__(self, gamedata_path: Optional[str] = None):
        super().__init__()
        self.gamedata_path = gamedata_path or str(
            project_root / "OriginalGameFiles/data/GameData.cff"
        )
        self.gamedata = None

    def load_all_armor(self) -> Dict[int, Dict[str, Any]]:
        """Load all armor from CFF file"""
        armor = {}

        # Try to load from GameData.cff for complete stats
        if GameData and Path(self.gamedata_path).exists():
            try:
                self.progress_updated.emit(10, "Loading GameData.cff...")
                self.gamedata = GameData(self.gamedata_path)

                # Get all armor directly from the armor table
                all_armor = (
                    self.gamedata.armor.all()
                    if hasattr(self.gamedata.armor, "all")
                    else []
                )

                total_armor = len(all_armor)

                for i, armor_entry in enumerate(all_armor):
                    armor_data = self._convert_armor_from_gamedata(armor_entry)
                    armor_id = armor_data["id"]
                    armor[armor_id] = armor_data

                    # Update progress
                    progress = int((i + 1) / total_armor * 90) + 10  # 10-100%
                    self.progress_updated.emit(
                        progress, f"Loading armor {i + 1}/{total_armor}"
                    )

                self.progress_updated.emit(
                    100, f"Loaded {len(armor)} armor pieces from CFF"
                )
                self.loading_complete.emit(len(armor))

            except Exception as e:
                print(f"Error loading from GameData: {e}")
                # Fall back to enhanced_armor.json if CFF loading fails
                armor = self._load_from_enhanced_json()
        else:
            # If GameData.cff doesn't exist or Tirganach is not available, fall back to JSON
            armor = self._load_from_enhanced_json()

        return armor

    def _convert_armor_from_gamedata(self, item) -> Dict[str, Any]:
        """Convert from GameData Item entity to standard dict format"""

        # Get the related item through the relation
        item = getattr(armor, "item", None)
        item_name = "Armor"
        item_sell_value = 0
        item_buy_value = 0
        if item:
            item_name = getattr(item, "name", f"Armor {getattr(armor, 'item_id', 0)}")
            item_sell_value = getattr(item, "selling_price", 0)
            item_buy_value = getattr(item, "buying_price", 0)

        # Initialize basic data structure
        armor_data = {
            "id": getattr(armor, "item_id", 0),
            "armor_id": getattr(armor, "item_id", 0),
            "name": item_name,
            "display_name": item_name,
            "description": getattr(armor, "description", ""),
            "slot": self._map_slot_from_subtype(0),  # Armor doesn't have item_subtype
            "armor_type": "Unknown",  # Will be determined differently
            "material": "Unknown",  # Will be determined differently
            "tier": "Common",  # Will be inferred
            "level_requirement": 1,
            "class_restriction": "None",
            # Stats from the armor table structure
            "strength": getattr(armor, "strength", 0),
            "stamina": getattr(armor, "stamina", 0),
            "agility": getattr(armor, "agility", 0),
            "dexterity": getattr(armor, "dexterity", 0),
            "intelligence": getattr(armor, "intelligence", 0),
            "wisdom": getattr(armor, "wisdom", 0),
            "charisma": getattr(armor, "charisma", 0),
            "health": getattr(armor, "health", 0),
            "mana": getattr(armor, "mana", 0),
            # Armor values
            "armor_value": getattr(armor, "armor", 0),
            # Resistances
            "resist_fire": getattr(armor, "resist_fire", 0),
            "resist_ice": getattr(armor, "resist_ice", 0),
            "resist_black": getattr(armor, "resist_black", 0),
            "resist_mind": getattr(armor, "resist_mind", 0),
            # Speed modifiers from the armor table
            "run_speed": getattr(armor, "speed_run", 0),
            "fight_speed": getattr(armor, "speed_fight", 0),
            "cast_speed": getattr(armor, "speed_cast", 0),
            # Other properties (these don't exist in the armor table structure)
            "stealth_bonus": 0,
            "swimming_speed": 0,
            "jump_height": 0,
            "icon_id": 0,
            "model_ref": "",
            "texture": "",
            "normal_map": "",
            "set_id": None,
            "set_bonus": {},
            "special_abilities": [],
            "enchantment_slots": 0,
            "stat_balance_rating": 0.0,
            # Economy from item relation
            "buy_value": item_buy_value,
            "sell_value": item_sell_value,
            "rarity": "Common",
        }

        # Set requirements to a structured format (armor doesn't directly have requirements)
        requirements = getattr(armor, "requirements", [])
        if requirements:
            reqs = (
                requirements[0]
                if isinstance(requirements, list) and len(requirements) > 0
                else requirements
            )
            armor_data["requirements"] = {
                "strength": getattr(reqs, "strength", 0),
                "dexterity": getattr(reqs, "dexterity", 0),
                "intelligence": getattr(reqs, "intelligence", 0),
                "level": getattr(reqs, "level", 1),
            }
        else:
            armor_data["requirements"] = {
                "strength": armor_data["strength"],
                "dexterity": armor_data["dexterity"],
                "intelligence": armor_data["intelligence"],
                "level": 1,
            }

        return armor_data

    def _map_slot_from_subtype(self, subtype: int) -> str:
        """Map item_subtype to slot name"""
        slot_map = {
            1: "Head",  # In SpellForce, different subtypes represent different slots
            2: "Chest",
            3: "Shield",  # This is likely the offhand slot
            4: "Hands",
            5: "Legs",
            6: "Feet",
            7: "Cloak",
            8: "Belt",
            9: "Ring",
            10: "Amulet",
        }

        # Default to "Unknown" if subtype not in map, but return the number as string if it's not known
        return slot_map.get(subtype, f"Slot {subtype}")

    def _load_from_enhanced_json(self) -> Dict[int, Dict[str, Any]]:
        """Fallback to load from enhanced_armor.json"""
        armor_file = project_root / "src" / "TirganachReloaded" / "enhanced_armor.json"
        armor = {}

        if armor_file.exists():
            try:
                self.progress_updated.emit(20, "Loading from enhanced_armor.json...")
                with open(armor_file, "r", encoding="utf-8") as f:
                    armor_data = json.load(f)

                # Get the list of armor items from the JSON structure
                armor_items = (
                    armor_data.get("armors", [])
                    if isinstance(armor_data, dict)
                    else armor_data
                )

                for armor_item in armor_items:
                    armor_id = armor_item.get("id") or armor_item.get("item_id")
                    if armor_id:
                        # Normalize the armor data to match what the UI expects
                        normalized_armor = {
                            "id": armor_id,
                            "armor_id": armor_id,
                            "armor_name": armor_item.get(
                                "display_name",
                                armor_item.get("name", f"Armor {armor_id}"),
                            ),
                            "name": armor_item.get("name", f"Armor {armor_id}"),
                            "display_name": armor_item.get(
                                "display_name",
                                armor_item.get("name", f"Armor {armor_id}"),
                            ),
                            "description": armor_item.get("description", ""),
                            "slot": self._get_armor_slot_name(
                                armor_item.get("slot", 0)
                            ),
                            "armor_type": armor_item.get("armor_type", "Unknown"),
                            "tier": armor_item.get("tier", "Unknown"),
                            "material_name": armor_item.get("material", "Unknown"),
                            "base_armor": armor_item.get(
                                "armor_value", armor_item.get("base_armor", 0)
                            ),
                            "magic_resistance": armor_item.get(
                                "magic_resist", armor_item.get("magic_resistance", 0)
                            ),
                            "physical_resistance": armor_item.get(
                                "physical_resist",
                                armor_item.get("physical_resistance", 0),
                            ),
                            "move_speed_bonus": armor_item.get(
                                "run_speed", armor_item.get("move_speed_bonus", 0)
                            ),
                            "health_bonus": armor_item.get(
                                "health", armor_item.get("health_bonus", 0)
                            ),
                            "mana_bonus": armor_item.get(
                                "mana", armor_item.get("mana_bonus", 0)
                            ),
                            "requirements": {
                                "strength": armor_item.get("strength", 0),
                                "dexterity": armor_item.get("dexterity", 0),
                                "intelligence": armor_item.get("intelligence", 0),
                                "level": armor_item.get(
                                    "level_requirement", armor_item.get("level", 1)
                                ),
                            },
                            "sell_value": armor_item.get(
                                "sell_value", armor_item.get("sell_value", 0)
                            ),
                            "buy_value": armor_item.get(
                                "buy_value", armor_item.get("buy_value", 0)
                            ),
                            "rarity": armor_item.get("rarity", "Unknown"),
                            "level_requirement": armor_item.get("level_requirement", 1),
                            "class_restriction": armor_item.get(
                                "class_restriction", "None"
                            ),
                            "resist_fire": armor_item.get("resist_fire", 0),
                            "resist_ice": armor_item.get("resist_ice", 0),
                            "resist_black": armor_item.get("resist_black", 0),
                            "resist_mind": armor_item.get("resist_mind", 0),
                            "critical_resist": armor_item.get("critical_resist", 0),
                            "fight_speed": armor_item.get("fight_speed", 0),
                            "cast_speed": armor_item.get("cast_speed", 0),
                            "stealth_bonus": armor_item.get("stealth_bonus", 0),
                            "swimming_speed": armor_item.get("swimming_speed", 0),
                            "jump_height": armor_item.get("jump_height", 0),
                            "icon_id": armor_item.get("icon_id", 0),
                            "model_ref": armor_item.get("model_ref", ""),
                            "texture": armor_item.get("texture", ""),
                            "normal_map": armor_item.get("normal_map", ""),
                            "set_id": armor_item.get("set_id", None),
                            "set_bonus": armor_item.get("set_bonus", {}),
                            "special_abilities": armor_item.get(
                                "special_abilities", []
                            ),
                            "enchantment_slots": armor_item.get("enchantment_slots", 0),
                            "stat_balance_rating": armor_item.get(
                                "stat_balance_rating", 0.0
                            ),
                        }

                        armor[armor_id] = normalized_armor

                self.progress_updated.emit(
                    100, f"Loaded {len(armor)} armor pieces from JSON"
                )
                self.loading_complete.emit(len(armor))

            except Exception as e:
                print(f"Error loading from enhanced_armor.json: {e}")
        else:
            self.progress_updated.emit(100, "No armor data file found")
            self.loading_complete.emit(0)

        return armor

    def _get_armor_slot_name(self, slot_id: int) -> str:
        """Convert armor slot ID to human-readable name"""
        slot_names = {
            0: "Unknown",
            1: "Head",
            2: "Chest",
            3: "Shield",  # This is likely the offhand slot
            4: "Hands",
            5: "Legs",
            6: "Feet",
            7: "Cloak",
            8: "Belt",
            9: "Ring",
            10: "Amulet",
        }
        return slot_names.get(slot_id, f"Slot {slot_id}")


def main():
    """Main function for testing the loader"""
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Initialize the armor loader
    loader = CFFArmorLoader()

    # Connect signals for progress updates
    loader.progress_updated.connect(lambda p, msg: print(f"Progress: {p}% - {msg}"))
    loader.loading_complete.connect(
        lambda count: print(f"Loading complete: {count} armor loaded")
    )

    # Load armor
    armor = loader.load_all_armor()

    print(f"Loaded {len(armor)} armor pieces")
    if armor:
        # Show sample of first armor piece
        first_armor_id = next(iter(armor))
        first_armor = armor[first_armor_id]
        print(f"Sample armor data: {first_armor}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
