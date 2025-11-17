"""
CFF-based NPC Loader for Orthancs Schmiede
===========================================

This module provides functionality to load NPC data directly from CFF files,
showing all NPCs from the game alongside custom NPCs.
"""

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
    print("Warning: Tirganach library not available. NPC data will be limited.")


class CFFNpcLoader(QObject):
    """Load NPC data directly from CFF files"""

    # Signal for progress updates
    progress_updated = Signal(int, str)  # (percentage, message)
    loading_complete = Signal(int)  # (total_npcs_loaded)

    def __init__(self, gamedata_path: Optional[str] = None):
        super().__init__()
        self.gamedata_path = gamedata_path or str(
            project_root / "OriginalGameFiles/data/GameData.cff"
        )
        self.gamedata = None

    def load_all_npcs(self, cff_file_path: Optional[str] = None) -> Dict[int, Dict[str, Any]]:
        """Load all NPCs from CFF file"""
        npcs = {}

        # Use custom CFF file path if provided, otherwise use default
        gamedata_path = cff_file_path or self.gamedata_path

        # Try to load from GameData.cff
        if GameData and Path(gamedata_path).exists():
            try:
                file_name = Path(gamedata_path).name
                self.progress_updated.emit(10, f"Loading {file_name}...")
                self.gamedata = GameData(gamedata_path)

                # Get all units (NPCs are stored in the units table)
                all_units = list(self.gamedata.units)
                total_units = len(all_units)

                print(f"Found {total_units} units in CFF file")

                for i, unit in enumerate(all_units):
                    # Only process NPC-type units (not buildings, etc.)
                    if self._is_npc_unit(unit):
                        npc_data = self._convert_npc_from_gamedata(unit)
                        npc_id = npc_data["npc_id"]
                        npcs[npc_id] = npc_data

                    # Update progress
                    progress = int((i + 1) / total_units * 90) + 10  # 10-100%
                    if i % 100 == 0:  # Update every 100 items to avoid spam
                        self.progress_updated.emit(
                            progress, f"Processing units {i + 1}/{total_units}"
                        )

                self.progress_updated.emit(
                    100, f"Loaded {len(npcs)} NPCs from CFF"
                )
                self.loading_complete.emit(len(npcs))
                print(f"Successfully loaded {len(npcs)} NPCs from GameData.cff")

            except Exception as e:
                print(f"Error loading NPCs from GameData: {e}")
                import traceback
                traceback.print_exc()

        elif not GameData:
            print("Warning: Tirganach library not available")
        elif not Path(gamedata_path).exists():
            print(f"Warning: CFF file not found: {gamedata_path}")

        return npcs

    def _is_npc_unit(self, unit) -> bool:
        """Check if a unit is an NPC (not a building, army unit, etc.)"""
        try:
            # NPCs typically have unit_type_id in certain ranges
            # and have character-like properties
            unit_id = getattr(unit, "unit_id", 0)

            # Filter out invalid IDs
            if unit_id <= 0 or unit_id >= 30000:
                return False

            # Check if it has character stats (NPCs usually have these)
            has_stats = (
                hasattr(unit, "strength") or
                hasattr(unit, "dexterity") or
                hasattr(unit, "intelligence")
            )

            # Check if it has a name
            name = getattr(unit, "name", "")
            if not name or name.strip() == "":
                return False

            return has_stats

        except Exception as e:
            return False

    def _convert_npc_from_gamedata(self, unit) -> Dict[str, Any]:
        """Convert from GameData Unit entity to NPC dict format"""

        unit_id = getattr(unit, "unit_id", 0)
        name = getattr(unit, "name", f"NPC {unit_id}")

        # Try to determine NPC type from unit properties
        npc_type = "friendly"  # Default

        # Basic NPC data structure matching our NpcCreationData format
        npc_data = {
            "npc_id": unit_id,
            "creation_mode": "game",  # Mark as game NPC
            "source_npc_id": None,
            "name": name,
            "title": "",
            "description": f"Game NPC from GameData.cff",
            "npc_type": npc_type,
            "character_class": "warrior",  # Default, could be inferred
            "level": getattr(unit, "level", 1),
            "faction": "HUMANS",  # Default

            # Base stats
            "base_stats": {
                "strength": getattr(unit, "strength", 10),
                "stamina": getattr(unit, "stamina", 10),
                "agility": getattr(unit, "agility", 10),
                "dexterity": getattr(unit, "dexterity", 10),
                "intelligence": getattr(unit, "intelligence", 10),
                "wisdom": getattr(unit, "wisdom", 10),
                "charisma": getattr(unit, "charisma", 10),
            },

            # Derived stats
            "derived_stats": {
                "health": getattr(unit, "health", 100),
                "mana": getattr(unit, "mana", 50),
                "melee_attack": getattr(unit, "melee_damage", 10),
                "ranged_attack": getattr(unit, "ranged_damage", 0),
                "magic_attack": 0,
                "physical_defense": getattr(unit, "armor", 5),
                "magic_defense": 5,
                "fire_resistance": getattr(unit, "fire_resistance", 0),
                "ice_resistance": getattr(unit, "ice_resistance", 0),
                "black_resistance": getattr(unit, "black_magic_resistance", 0),
                "mind_resistance": getattr(unit, "mind_resistance", 0),
            },

            # Appearance
            "appearance": {
                "head_id": 0,
                "race": "HUMANS",
                "gender": "MALE",
                "voice_type": "main_male"
            },

            # Behavior
            "behavior": {
                "movement_type": "stationary",
                "interaction_radius": 5,
                "spawn_location": None,
                "spawn_conditions": {}
            },

            # Equipment (empty for game NPCs)
            "equipment": {
                "helmet_item_id": None,
                "chest_item_id": None,
                "legs_item_id": None,
                "right_hand_item_id": None,
                "left_hand_item_id": None,
                "right_ring_item_id": None,
                "left_ring_item_id": None
            },

            # Rewards
            "rewards": {
                "experience": getattr(unit, "experience_value", 0),
                "gold": 0,
                "items": []
            },

            "special_abilities": []
        }

        return npc_data
