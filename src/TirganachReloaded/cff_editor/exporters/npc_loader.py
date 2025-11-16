"""
NPC Loader - Load and save NPC data from JSON
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from ..models.npc_creation_data import (
    NpcCreationData, NpcType, CharacterClass, VoiceType,
    NpcStats, NpcCombatStats, NpcEquipment, NpcAppearance,
    NpcBehavior, NpcRewards
)


class NpcLoader:
    """Load and save NPC data"""

    NPC_DATA_FILE = "data/npcs/custom_npcs.json"

    @staticmethod
    def ensure_directory():
        """Ensure NPC data directory exists"""
        os.makedirs(os.path.dirname(NpcLoader.NPC_DATA_FILE), exist_ok=True)

    @staticmethod
    def load_all_npcs() -> Dict[int, Dict[str, Any]]:
        """Load all NPCs from JSON file"""
        try:
            NpcLoader.ensure_directory()
            if not os.path.exists(NpcLoader.NPC_DATA_FILE):
                return {}

            with open(NpcLoader.NPC_DATA_FILE, 'r') as f:
                npc_list = json.load(f)

            # Convert list to dict indexed by npc_id
            return {npc['npc_id']: npc for npc in npc_list}

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading NPCs: {e}")
            return {}

    @staticmethod
    def load_npc(npc_id: int) -> Optional[NpcCreationData]:
        """Load specific NPC by ID"""
        try:
            all_npcs = NpcLoader.load_all_npcs()
            npc_data = all_npcs.get(npc_id)

            if not npc_data:
                return None

            # Convert from dict to NpcCreationData
            return NpcCreationData.from_dict(npc_data)

        except Exception as e:
            print(f"Error loading NPC {npc_id}: {e}")
            return None

    @staticmethod
    def save_npc(npc: NpcCreationData) -> bool:
        """Save NPC to JSON file"""
        try:
            NpcLoader.ensure_directory()

            # Load existing NPCs
            all_npcs = NpcLoader.load_all_npcs()

            # Update or add this NPC
            all_npcs[npc.npc_id] = npc.to_dict()

            # Convert dict back to list for JSON
            npc_list = list(all_npcs.values())

            # Save to file
            with open(NpcLoader.NPC_DATA_FILE, 'w') as f:
                json.dump(npc_list, f, indent=2)

            print(f"Saved NPC {npc.npc_id} ({npc.name}) to {NpcLoader.NPC_DATA_FILE}")
            return True

        except Exception as e:
            print(f"Error saving NPC {npc.npc_id}: {e}")
            return False

    @staticmethod
    def delete_npc(npc_id: int) -> bool:
        """Delete NPC from JSON file"""
        try:
            NpcLoader.ensure_directory()

            # Load existing NPCs
            all_npcs = NpcLoader.load_all_npcs()

            if npc_id not in all_npcs:
                print(f"NPC {npc_id} not found")
                return False

            # Remove NPC
            del all_npcs[npc_id]

            # Convert dict back to list for JSON
            npc_list = list(all_npcs.values())

            # Save to file
            with open(NpcLoader.NPC_DATA_FILE, 'w') as f:
                json.dump(npc_list, f, indent=2)

            print(f"Deleted NPC {npc_id} from {NpcLoader.NPC_DATA_FILE}")
            return True

        except Exception as e:
            print(f"Error deleting NPC {npc_id}: {e}")
            return False

    @staticmethod
    def get_npc_list() -> List[Dict[str, Any]]:
        """Get list of all NPCs with basic info"""
        all_npcs = NpcLoader.load_all_npcs()
        return [
            {
                "npc_id": npc_data["npc_id"],
                "name": npc_data.get("name", "Unnamed NPC"),
                "title": npc_data.get("title", ""),
                "npc_type": npc_data.get("npc_type", "friendly"),
                "character_class": npc_data.get("character_class", "warrior"),
                "level": npc_data.get("level", 1)
            }
            for npc_data in all_npcs.values()
        ]
