"""
CFF-based NPC Loader for Graufurter Bürger Büro
================================================

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
    from TirganachReloaded.tirganach.entities import Language
except ImportError:
    GameData = None
    Language = None
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

    def load_all_npcs(self, cff_file_path: Optional[str] = None, language: str = "GERMAN") -> Dict[int, Dict[str, Any]]:
        """Load all NPCs from CFF file
        
        Args:
            cff_file_path: Optional path to CFF file (uses default if not provided)
            language: Language for localization (default: GERMAN)
        """
        npcs = {}

        # Use custom CFF file path if provided, otherwise use default
        gamedata_path = cff_file_path or self.gamedata_path

        # Try to load from GameData.cff
        if GameData and Path(gamedata_path).exists():
            try:
                file_name = Path(gamedata_path).name
                self.progress_updated.emit(10, f"Loading {file_name}...")
                self.gamedata = GameData(gamedata_path)

                # Get all creatures (NPCs are stored in the creatures table)
                all_creatures = list(self.gamedata.creatures)
                total_creatures = len(all_creatures)

                print(f"Found {total_creatures} creatures in CFF file")

                for i, creature in enumerate(all_creatures):
                    # Only process NPC-type creatures (not buildings, etc.)
                    if self._is_npc_creature(creature):
                        npc_data = self._convert_npc_from_gamedata(creature, language)
                        npc_id = npc_data["npc_id"]
                        npcs[npc_id] = npc_data

                    # Update progress
                    progress = int((i + 1) / total_creatures * 90) + 10  # 10-100%
                    if i % 100 == 0:  # Update every 100 items to avoid spam
                        self.progress_updated.emit(
                            progress, f"Processing creatures {i + 1}/{total_creatures}"
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

    def _is_npc_creature(self, creature) -> bool:
        """Check if a creature is an NPC (not a building, summon, etc.)"""
        try:
            # Get creature ID
            creature_id = getattr(creature, "creature_id", 0)

            # Filter out invalid IDs
            if creature_id <= 0 or creature_id >= 30000:
                return False

            # Check if it has a name_id (for localization)
            name_id = getattr(creature, "name_id", 0)
            if name_id <= 0:
                return False

            # Check if it has stats reference
            stats_id = getattr(creature, "stats_id", 0)
            if stats_id <= 0:
                return False

            return True

        except Exception as e:
            return False

    def _convert_npc_from_gamedata(self, creature, language: str = "GERMAN") -> Dict[str, Any]:
        """Convert from GameData Creature entity to NPC dict format
        
        Implements TODO-007 through TODO-010:
        - Load head IDs from creature data
        - Load equipment from creature_equipment table
        - Load localized names via name_id
        - Load skills and spells
        """

        creature_id = getattr(creature, "creature_id", 0)
        name_id = getattr(creature, "name_id", 0)
        
        # TODO-009: Load Localized Names
        name = getattr(creature, "name", f"Creature {creature_id}")
        if name_id > 0 and hasattr(self.gamedata, "localisation") and Language:
            try:
                lang_enum = getattr(Language, language, Language.GERMAN)
                loc_entries = [
                    loc for loc in self.gamedata.localisation
                    if loc.text_id == name_id and loc.language == lang_enum
                ]
                if loc_entries:
                    name = loc_entries[0].text
            except Exception as e:
                print(f"Warning: Could not load localized name for creature {creature_id}: {e}")

        # Try to determine NPC type (default to friendly for now)
        npc_type = "friendly"

        # Get stats if available
        stats_id = getattr(creature, "stats_id", 0)
        
        # TODO-007: Load Head IDs
        # Note: Heads in SpellForce are typically stored at race/gender level, not per-creature
        # For now, we use default head_id from creature (if it exists)
        head_id = getattr(creature, "head_id", 0)
        
        # TODO-008: Load Equipment Data
        equipment_dict = {
            "helmet_item_id": None,
            "chest_item_id": None,
            "legs_item_id": None,
            "right_hand_item_id": None,
            "left_hand_item_id": None,
            "right_ring_item_id": None,
            "left_ring_item_id": None
        }
        
        if hasattr(self.gamedata, "creature_equipment"):
            try:
                equipment_items = [
                    eq for eq in self.gamedata.creature_equipment
                    if eq.creature_id == creature_id
                ]
                
                # Map equipment slots to our format
                slot_mapping = {
                    "HEAD": "helmet_item_id",
                    "CHEST": "chest_item_id",
                    "LEGS": "legs_item_id",
                    "RIGHT_HAND": "right_hand_item_id",
                    "LEFT_HAND": "left_hand_item_id",
                    "RIGHT_RING": "right_ring_item_id",
                    "LEFT_RING": "left_ring_item_id"
                }
                
                for eq in equipment_items:
                    slot_name = str(eq.equipment_slot).split(".")[-1]  # Extract enum name
                    if slot_name in slot_mapping:
                        equipment_dict[slot_mapping[slot_name]] = eq.item_id
                        
            except Exception as e:
                print(f"Warning: Could not load equipment for creature {creature_id}: {e}")
        
        # TODO-010: Load Skills and Spells
        skills_list = []
        spells_list = []
        
        # Load skills (linked via stats_id)
        if stats_id > 0 and hasattr(self.gamedata, "creature_skills"):
            try:
                skill_items = [
                    sk for sk in self.gamedata.creature_skills
                    if sk.stats_id == stats_id
                ]
                
                for skill in skill_items:
                    skill_school = str(skill.skill_school).split(".")[-1]  # Extract enum name
                    skills_list.append({
                        "school": skill_school,
                        "level": skill.skill_level
                    })
                    
            except Exception as e:
                print(f"Warning: Could not load skills for creature {creature_id}: {e}")
        
        # Load spells (linked via creature_id)
        if hasattr(self.gamedata, "creature_spells"):
            try:
                spell_items = [
                    sp for sp in self.gamedata.creature_spells
                    if sp.creature_id == creature_id
                ]
                
                for spell in spell_items:
                    spells_list.append({
                        "spell_id": spell.spell_id,
                        "position": spell.spell_position
                    })
                    
            except Exception as e:
                print(f"Warning: Could not load spells for creature {creature_id}: {e}")
        
        # Basic NPC data structure matching our NpcCreationData format
        npc_data = {
            "npc_id": creature_id,
            "creation_mode": "game",  # Mark as game NPC
            "source_npc_id": None,
            "name": name,
            "title": "",
            "description": f"Game creature from GameData.cff",
            "npc_type": npc_type,
            "character_class": "warrior",  # Default
            "level": 1,  # Default
            "faction": "NEUTRAL",  # Default

            # Base stats (simplified - we'd need to lookup via stats_id)
            "base_stats": {
                "strength": 10,
                "stamina": 10,
                "agility": 10,
                "dexterity": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10,
            },

            # Derived stats
            "derived_stats": {
                "health": 100,
                "mana": 50,
                "melee_attack": 10,
                "ranged_attack": 0,
                "magic_attack": 0,
                "physical_defense": getattr(creature, "armor", 5),
                "magic_defense": 5,
                "fire_resistance": 0,
                "ice_resistance": 0,
                "black_resistance": 0,
                "mind_resistance": 0,
            },

            # Appearance (TODO-007: head_id loaded)
            "appearance": {
                "head_id": head_id,
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

            # Equipment (TODO-008: loaded from game data)
            "equipment": equipment_dict,

            # Rewards
            "rewards": {
                "experience": getattr(creature, "experience", 0),
                "gold": getattr(creature, "money_copper", 0),
                "items": []
            },

            "special_abilities": [],
            
            # TODO-010: Skills and Spells loaded
            "skills": skills_list,
            "spells": spells_list
        }

        return npc_data
