"""
CFF-based Armor Loader for Orthancs Schmiede
===========================================

This module provides functionality to load armor data directly from CFF files,
ensuring access to the most complete and up-to-date armor information.

Based on the existing armor_loader.py from TirganachReloaded.
"""

import json
import subprocess
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
    print("Warning: Tirganach library not available. Armor data will be limited.")


CACHE_FILE = Path(__file__).parent / "armor_cache.json"
RUST_TOOL_PATH = project_root / "rust_src" / "target" / "release" / "cff-tool.exe"
DEFAULT_CFF = project_root / "OriginalGameFiles" / "data" / "GameData.cff"


class CFFArmorLoader(QObject):
    """Load armor data directly from CFF files"""

    # Signal for progress updates
    progress_updated = Signal(int, str)  # (percentage, message)
    loading_complete = Signal(int)  # (total_armor_loaded)

    def __init__(self, gamedata_path: Optional[str] = None):
        super().__init__()
        self.gamedata_path = gamedata_path or str(DEFAULT_CFF)
        self.gamedata = None

    def load_all_armor(
        self, cff_file_path: Optional[str] = None, force_rebuild: bool = False
    ) -> Dict[int, Dict[str, Any]]:
        """Load all armor from CFF file"""
        armor = {}

        # Use custom CFF file path if provided, otherwise use default
        gamedata_path = cff_file_path or self.gamedata_path

        # Try cache first
        if not force_rebuild and CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    armor = {int(k): v for k, v in data.items()}
                    if armor:
                        self.progress_updated.emit(
                            100, f"Loaded {len(armor)} armor from cache"
                        )
                        self.loading_complete.emit(len(armor))
                        return armor
            except Exception as e:
                print(f"Failed to load armor cache: {e}")

        # Try Rust first
        armor = self._load_from_rust(gamedata_path)
        if armor:
            # Save to cache
            try:
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(armor, f)
            except Exception as e:
                print(f"Failed to save armor cache: {e}")
            self.progress_updated.emit(100, f"Loaded {len(armor)} armor from Rust")
            self.loading_complete.emit(len(armor))
            return armor

        # Fall back to Python/Tirganach
        print("Rust tool failed, falling back to Python/Tirganach...")
        armor = self._load_from_python(gamedata_path)

        return armor

    def _load_from_rust(self, gamedata_path: str) -> Dict[int, Dict[str, Any]]:
        """Load armor using the Rust CLI tool (much faster)"""
        armor = {}

        # Check if Rust tool exists
        if not RUST_TOOL_PATH.exists():
            print("Rust tool not found, building...")
            try:
                result = subprocess.run(
                    ["cargo", "build", "--release"],
                    cwd=str(project_root / "rust_src"),
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if result.returncode != 0:
                    print(f"Failed to build Rust tool: {result.stderr}")
                    return {}
            except Exception as e:
                print(f"Failed to build Rust tool: {e}")
                return {}

        if not RUST_TOOL_PATH.exists():
            return {}

        try:
            self.progress_updated.emit(10, "Loading armor from Rust...")
            result = subprocess.run(
                [str(RUST_TOOL_PATH), gamedata_path, "armor"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                print(f"Rust tool error: {result.stderr}")
                return {}

            # Parse JSON output
            stdout = result.stdout
            json_start = stdout.find("{")
            data = {}
            if json_start >= 0:
                json_str = stdout[json_start:]
                data = json.loads(json_str)

            armor_list = data.get("armor", [])

            for armor_item in armor_list:
                armor_id = armor_item.get("item_id", 0)
                if armor_id == 0:
                    continue

                armor[armor_id] = {
                    "item_id": armor_id,
                    "armor_id": armor_id,
                    "name": armor_item.get("name", f"Armor {armor_id}"),
                    "armor_name": armor_item.get("name", f"Armor {armor_id}"),
                    "name_id": armor_item.get("name_id", 0),
                    "item_type": "EQUIPMENT",
                    "item_subtype": "UNKNOWN",
                    # Stats from Rust
                    "strength": armor_item.get("strength", 0),
                    "stamina": armor_item.get("stamina", 0),
                    "agility": armor_item.get("agility", 0),
                    "dexterity": armor_item.get("dexterity", 0),
                    "health": armor_item.get("health", 0),
                    "charisma": armor_item.get("charisma", 0),
                    "intelligence": armor_item.get("intelligence", 0),
                    "wisdom": armor_item.get("wisdom", 0),
                    "mana": armor_item.get("mana", 0),
                    "armor_value": armor_item.get("armor_value", 0),
                    "base_armor": armor_item.get("armor_value", 0),
                    "resist_fire": armor_item.get("resist_fire", 0),
                    "resist_ice": armor_item.get("resist_ice", 0),
                    "resist_black": armor_item.get("resist_black", 0),
                    "resist_mind": armor_item.get("resist_mind", 0),
                    "run_speed": armor_item.get("speed_run", 0),
                    "fight_speed": armor_item.get("speed_fight", 0),
                    "cast_speed": armor_item.get("speed_cast", 0),
                    "move_speed_bonus": armor_item.get("speed_run", 0),
                    "fight_speed_bonus": armor_item.get("speed_fight", 0),
                    "cast_speed_bonus": armor_item.get("speed_cast", 0),
                    "health_bonus": armor_item.get("health", 0),
                    "mana_bonus": armor_item.get("mana", 0),
                    "magic_resistance": armor_item.get("resist_black", 0),
                    "physical_resistance": armor_item.get("armor_value", 0),
                    "sell_value": 0,
                    "buy_value": 0,
                    "rarity": "Common",
                    "requirements": {
                        "strength": 0,
                        "dexterity": 0,
                        "intelligence": 0,
                        "level": 1,
                        "school_requirements": [],
                    },
                    "effects": [],
                    "icon_handle": "",
                    "slot": "Unknown",
                    "armor_type": "Unknown",
                    "tier": "Common",
                }

            print(f"Loaded {len(armor)} armor from Rust")

        except subprocess.TimeoutExpired:
            print("Rust tool timed out")
            return {}
        except Exception as e:
            print(f"Error running Rust tool: {e}")
            return {}

        return armor

    def _load_from_python(self, gamedata_path: str) -> Dict[int, Dict[str, Any]]:
        """Load armor using Python/Tirganach (slower fallback)"""
        armor = {}

    def _convert_armor_from_gamedata(self, armor) -> Dict[str, Any]:
        """Convert from GameData Armor entity to standard dict format"""

        # Get the related item through the armor's item relation
        item = getattr(armor, "item", None)

        armor_name = f"Armor {armor.item_id}"
        sell_value = 0
        buy_value = 0
        item_set_id = 0
        item_type = "EQUIPMENT"
        item_subtype = "UNKNOWN"
        name_id = 0
        unit_stats_id = 0
        army_unit_id = 0
        building_id = 0
        unknown1 = 0

        if item:
            armor_name = getattr(item, "name", armor_name)
            sell_value = getattr(item, "selling_price", 0)
            buy_value = getattr(item, "buying_price", 0)
            item_set_id = getattr(item, "item_set_id", 0)
            item_type = getattr(item, "item_type", "EQUIPMENT")
            item_subtype = getattr(item, "item_subtype", "UNKNOWN")
            name_id = getattr(item, "name_id", 0)
            unit_stats_id = getattr(item, "unit_stats_id", 0)
            army_unit_id = getattr(item, "army_unit_id", 0)
            building_id = getattr(item, "building_id", 0)
            unknown1 = getattr(item, "unknown1", 0)

        # Initialize basic data structure with all available CFF fields
        armor_data = {
            "item_id": armor.item_id,
            "armor_id": armor.item_id,
            "name": armor_name,
            "armor_name": armor_name,  # Add for compatibility
            "name_id": name_id,
            "item_type": item_type,
            "item_subtype": item_subtype,
            "unit_stats_id": unit_stats_id,
            "army_unit_id": army_unit_id,
            "building_id": building_id,
            "unknown1": unknown1,
            "item_set_id": item_set_id,
            # Armor stats from CFF
            "strength": getattr(armor, "strength", 0),
            "stamina": getattr(armor, "stamina", 0),
            "agility": getattr(armor, "agility", 0),
            "dexterity": getattr(armor, "dexterity", 0),
            "health": getattr(armor, "health", 0),
            "charisma": getattr(armor, "charisma", 0),
            "intelligence": getattr(armor, "intelligence", 0),
            "wisdom": getattr(armor, "wisdom", 0),
            "mana": getattr(armor, "mana", 0),
            # UI field mapping - provide both names for compatibility
            "armor_value": getattr(armor, "armor", 0),
            "base_armor": getattr(armor, "armor", 0),  # UI expects "base_armor"
            # Special properties - map to UI expected fields
            "health_bonus": getattr(armor, "health", 0),  # UI expects "health_bonus"
            "mana_bonus": getattr(armor, "mana", 0),  # UI expects "mana_bonus"
            "move_speed_bonus": getattr(
                armor, "speed_run", 0
            ),  # UI expects "move_speed_bonus"
            "fight_speed_bonus": getattr(
                armor, "speed_fight", 0
            ),  # UI expects "fight_speed_bonus"
            "cast_speed_bonus": getattr(
                armor, "speed_cast", 0
            ),  # UI expects "cast_speed_bonus"
            # Resistances - map to UI expected fields
            "resist_fire": getattr(armor, "resist_fire", 0),
            "resist_ice": getattr(armor, "resist_ice", 0),
            "resist_black": getattr(armor, "resist_black", 0),
            "resist_mind": getattr(armor, "resist_mind", 0),
            "magic_resistance": getattr(
                armor, "resist_black", 0
            ),  # UI expects "magic_resistance"
            "physical_resistance": getattr(
                armor, "armor", 0
            ),  # UI expects "physical_resistance" - use armor value as approximation
            # Speed modifiers (keep original names for CFF data section)
            "run_speed": getattr(armor, "speed_run", 0),
            "fight_speed": getattr(armor, "speed_fight", 0),
            "cast_speed": getattr(armor, "speed_cast", 0),
            # Economy
            "sell_value": sell_value,
            "buy_value": buy_value,
            "rarity": "Common",  # Default rarity
        }

        # Determine armor slot from item_subtype
        armor_data["slot"] = self._map_slot_from_subtype(item_subtype)

        # Get requirements from item_requirements table
        try:
            if hasattr(self.gamedata, "item_requirements"):
                item_reqs = self.gamedata.item_requirements.where(item_id=armor.item_id)
                if item_reqs:
                    armor_data["requirements"] = {
                        "strength": 0,
                        "dexterity": 0,
                        "intelligence": 0,
                        "level": max([req.level for req in item_reqs])
                        if item_reqs
                        else 1,
                        "school_requirements": [
                            {
                                "requirement_number": req.requirement_number,
                                "requirement_school": str(req.requirement_school),
                                "level": req.level,
                            }
                            for req in item_reqs
                        ],
                    }
                else:
                    armor_data["requirements"] = {
                        "strength": 0,
                        "dexterity": 0,
                        "intelligence": 0,
                        "level": 1,
                        "school_requirements": [],
                    }
            else:
                armor_data["requirements"] = {
                    "strength": 0,
                    "dexterity": 0,
                    "intelligence": 0,
                    "level": 1,
                    "school_requirements": [],
                }
        except Exception:
            armor_data["requirements"] = {
                "strength": 0,
                "dexterity": 0,
                "intelligence": 0,
                "level": 1,
                "school_requirements": [],
            }

        # Get UI handle for icons
        try:
            if hasattr(self.gamedata, "item_ui"):
                item_uis = self.gamedata.item_ui.where(item_id=armor.item_id)
                if item_uis and item_uis[0].item_ui_handle:
                    armor_data["icon_handle"] = item_uis[0].item_ui_handle.strip()
                else:
                    armor_data["icon_handle"] = ""
            else:
                armor_data["icon_handle"] = ""
        except Exception:
            armor_data["icon_handle"] = ""

        # Get item effects
        try:
            if hasattr(self.gamedata, "item_effects"):
                item_effects = self.gamedata.item_effects.where(item_id=armor.item_id)
                armor_data["effects"] = [
                    {"effect_index": eff.effect_index, "effect_id": eff.effect_id}
                    for eff in item_effects
                ]
            else:
                armor_data["effects"] = []
        except Exception:
            armor_data["effects"] = []

        # Determine armor type based on slot and stats
        armor_data["armor_type"] = self._determine_armor_type(
            armor_data["slot"], armor_data["armor_value"]
        )
        armor_data["tier"] = self._determine_tier(armor_data["armor_value"])
        armor_data["material"] = "Unknown"  # Would need material mapping table

        return armor_data

    def _map_slot_from_subtype(self, subtype) -> str:
        """Map item_subtype to slot name"""
        # Handle both string and integer subtypes
        if isinstance(subtype, str):
            subtype_map = {
                "EquipmentType.HELMET": "Head",
                "EquipmentType.UPPER": "Chest",
                "EquipmentType.LOWER": "Legs",
                "EquipmentType.BOOTS": "Feet",
                "EquipmentType.GLOVES": "Hands",
                "EquipmentType.SHIELD": "Shield",
                "EquipmentType.RING": "Ring",
                "EquipmentType.AMULET": "Amulet",
                "EquipmentType.BELT": "Belt",
                "EquipmentType.CLOAK": "Cloak",
            }
            return subtype_map.get(subtype, f"Slot {subtype}")
        else:
            # Handle numeric subtypes
            slot_map = {
                1: "Head",
                2: "Chest",
                3: "Shield",
                4: "Hands",
                5: "Legs",
                6: "Feet",
                7: "Cloak",
                8: "Belt",
                9: "Ring",
                10: "Amulet",
            }
            return slot_map.get(subtype, f"Slot {subtype}")

    def _determine_armor_type(self, slot: str, armor_value: int) -> str:
        """Determine armor type based on slot and armor value"""
        if slot == "Shield":
            return "Shield"
        elif armor_value >= 50:
            return "Heavy"
        elif armor_value >= 25:
            return "Medium"
        else:
            return "Light"

    def _determine_tier(self, armor_value: int) -> str:
        """Determine tier based on armor value"""
        if armor_value >= 70:
            return "Epic"
        elif armor_value >= 50:
            return "Rare"
        elif armor_value >= 30:
            return "Uncommon"
        else:
            return "Common"

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

    QApplication(sys.argv)  # Initialize Qt application

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
