"""
NPC CFF Exporter - Export NPCs to GameData.cff format
"""

import struct
from typing import Dict, List, Any
from npc_creation_data import NpcCreationData, NpcType, CharacterClass


class NpcCFFExporter:
    """Export NPCs to CFF format"""

    def export_npc(self, npc_data: NpcCreationData) -> Dict[int, bytes]:
        """
        Export NPC to CFF categories

        Returns:
            Dict mapping category IDs to binary data
        """

        exports = {}

        # Category 3001: NPC General Info
        exports[3001] = self.export_npc_general(npc_data)

        # Category 3002: NPC Stats
        exports[3002] = self.export_npc_stats(npc_data)

        # Category 3003: NPC Combat Stats
        exports[3003] = self.export_npc_combat(npc_data)

        # Category 3004: NPC Equipment
        exports[3004] = self.export_npc_equipment(npc_data)

        # Category 3005: NPC Behavior
        exports[3005] = self.export_npc_behavior(npc_data)

        # Category 2016: Text entries (name, title, description)
        text_entries = self.export_text_entries(npc_data)
        exports[2016] = b''.join(text_entries) if text_entries else b''

        return exports

    def export_npc_general(self, npc_data: NpcCreationData) -> bytes:
        """Export to Category 3001 (NPC General Info)"""
        try:
            # Pack basic NPC info
            # NPCID (uint16), NameID (uint16), Type (byte), Class (byte), Level (byte),
            # FactionID (byte), HeadID (byte), Race (byte), Gender (byte), VoiceType (byte)

            npc_type_map = {
                NpcType.FRIENDLY: 0,
                NpcType.MERCHANT: 1,
                NpcType.GUARD: 2,
                NpcType.HOSTILE: 3
            }

            class_type_map = {
                CharacterClass.WARRIOR: 0,
                CharacterClass.MAGE: 1,
                CharacterClass.ROGUE: 2,
                CharacterClass.MULTI_CLASS: 3
            }

            # Calculate CFF-safe NPC ID and name ID (must be <= 65535)
            if npc_data.npc_id is None:
                cff_npc_id = 1001  # Default ID for NPCs with null ID
            else:
                cff_npc_id = npc_data.npc_id % 65535  # Ensure NPC ID fits in unsigned short
                if cff_npc_id == 0:
                    cff_npc_id = 1  # Avoid ID 0 which might be reserved
            name_id = (cff_npc_id % 35000) + 1000  # Keep it in safe range

            data = struct.pack('<HHBBBBBBBB',
                cff_npc_id,                                        # NPC ID (adjusted for CFF format)
                name_id,                                           # Name ID (safe range)
                npc_type_map.get(npc_data.npc_type, 0),           # NPC Type
                class_type_map.get(npc_data.character_class, 0),  # Character Class
                npc_data.level,                                    # Level
                0,                                                 # Faction ID (placeholder)
                npc_data.appearance.head_id,                      # Head ID
                0,                                                 # Race ID (placeholder)
                1 if npc_data.appearance.gender == "FEMALE" else 0, # Gender (0=male, 1=female)
                0                                                  # Voice Type (placeholder)
            )

            return data

        except struct.error as e:
            raise ValueError(f"Failed to pack NPC general data: {e}")

    def export_npc_stats(self, npc_data: NpcCreationData) -> bytes:
        """Export to Category 3002 (NPC Base Stats)"""
        try:
            # Calculate CFF-safe NPC ID
            if npc_data.npc_id is None:
                cff_npc_id = 1001  # Default ID for NPCs with null ID
            else:
                cff_npc_id = npc_data.npc_id % 65535
                if cff_npc_id == 0:
                    cff_npc_id = 1

            # Structure: NPCID + base stats (STR, STA, AGI, DEX, INT, WIS, CHA)
            data = struct.pack('<Hiiiiiiii',
                cff_npc_id,
                npc_data.base_stats.strength,
                npc_data.base_stats.stamina,
                npc_data.base_stats.agility,
                npc_data.base_stats.dexterity,
                npc_data.base_stats.intelligence,
                npc_data.base_stats.wisdom,
                npc_data.base_stats.charisma,
                0  # Padding
            )

            return data

        except struct.error as e:
            raise ValueError(f"Failed to pack NPC stats: {e}")

    def export_npc_combat(self, npc_data: NpcCreationData) -> bytes:
        """Export to Category 3003 (NPC Combat Stats)"""
        try:
            # Calculate CFF-safe NPC ID
            if npc_data.npc_id is None:
                cff_npc_id = 1001  # Default ID for NPCs with null ID
            else:
                cff_npc_id = npc_data.npc_id % 65535
                if cff_npc_id == 0:
                    cff_npc_id = 1

            # Structure: NPCID + combat stats
            data = struct.pack('<Hiiiiiiiiiiii',
                cff_npc_id,
                npc_data.derived_stats.health,
                npc_data.derived_stats.mana,
                npc_data.derived_stats.melee_attack,
                npc_data.derived_stats.ranged_attack,
                npc_data.derived_stats.magic_attack,
                npc_data.derived_stats.physical_defense,
                npc_data.derived_stats.magic_defense,
                npc_data.derived_stats.fire_resistance,
                npc_data.derived_stats.ice_resistance,
                npc_data.derived_stats.black_resistance,
                npc_data.derived_stats.mind_resistance,
                0  # Padding
            )

            return data

        except struct.error as e:
            raise ValueError(f"Failed to pack NPC combat stats: {e}")

    def export_npc_equipment(self, npc_data: NpcCreationData) -> bytes:
        """Export to Category 3004 (NPC Equipment)"""
        try:
            # Calculate CFF-safe NPC ID
            if npc_data.npc_id is None:
                cff_npc_id = 1001  # Default ID for NPCs with null ID
            else:
                cff_npc_id = npc_data.npc_id % 65535
                if cff_npc_id == 0:
                    cff_npc_id = 1

            # Structure: NPCID + equipment item IDs (7 slots)
            data = struct.pack('<HHHHHHHH',
                cff_npc_id,
                npc_data.equipment.helmet_item_id or 0,
                npc_data.equipment.chest_item_id or 0,
                npc_data.equipment.legs_item_id or 0,
                npc_data.equipment.right_hand_item_id or 0,
                npc_data.equipment.left_hand_item_id or 0,
                npc_data.equipment.right_ring_item_id or 0,
                npc_data.equipment.left_ring_item_id or 0
            )

            return data

        except struct.error as e:
            raise ValueError(f"Failed to pack NPC equipment: {e}")

    def export_npc_behavior(self, npc_data: NpcCreationData) -> bytes:
        """Export to Category 3005 (NPC Behavior)"""
        try:
            # Structure: NPCID + behavior settings
            movement_type_map = {
                "stationary": 0,
                "patrol": 1,
                "wander": 2
            }

            spawn_x = npc_data.behavior.spawn_location[0] if npc_data.behavior.spawn_location else 0
            spawn_y = npc_data.behavior.spawn_location[1] if npc_data.behavior.spawn_location else 0

            # Calculate CFF-safe NPC ID
            if npc_data.npc_id is None:
                cff_npc_id = 1001  # Default ID for NPCs with null ID
            else:
                cff_npc_id = npc_data.npc_id % 65535
                if cff_npc_id == 0:
                    cff_npc_id = 1

            data = struct.pack('<HBHhh',
                cff_npc_id,
                movement_type_map.get(npc_data.behavior.movement_type, 0),
                npc_data.behavior.interaction_radius,
                spawn_x,
                spawn_y
            )

            return data

        except struct.error as e:
            raise ValueError(f"Failed to pack NPC behavior: {e}")

    def export_text_entries(self, npc_data: NpcCreationData) -> List[bytes]:
        """Export to Category 2016 (Text Strings)"""
        entries = []

        try:
            # Calculate CFF-safe NPC ID
            if npc_data.npc_id is None:
                cff_npc_id = 1001  # Default ID for NPCs with null ID
            else:
                cff_npc_id = npc_data.npc_id % 65535
                if cff_npc_id == 0:
                    cff_npc_id = 1

            # Name entry
            name_id = cff_npc_id + 30000
            name_entry = self._create_text_entry(name_id, npc_data.name)
            entries.append(name_entry)

            # Title entry (if provided)
            if npc_data.title.strip():
                title_id = cff_npc_id + 30001
                title_entry = self._create_text_entry(title_id, npc_data.title)
                entries.append(title_entry)

            # Description entry (if provided)
            if npc_data.description.strip():
                desc_id = cff_npc_id + 30002
                desc_entry = self._create_text_entry(desc_id, npc_data.description)
                entries.append(desc_entry)

        except (UnicodeEncodeError, struct.error) as e:
            raise ValueError(f"Failed to create text entries: {e}")

        return entries

    def _create_text_entry(self, text_id: int, text: str) -> bytes:
        """Create a text entry in CFF format"""
        # Encode text as UTF-16LE (SpellForce standard)
        text_bytes = text.encode('utf-16le')
        text_length = len(text_bytes) // 2  # Length in UTF-16 code units

        # Structure: TextID (uint), Length (ushort), Text (UTF-16LE bytes)
        header = struct.pack('<IH', text_id, text_length)
        return header + text_bytes
