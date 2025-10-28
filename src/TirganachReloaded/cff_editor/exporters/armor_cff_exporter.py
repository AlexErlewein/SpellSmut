"""
Armor CFF Exporter - Export armor to GameData.cff format
"""

import struct
from typing import Dict, List, Any
from ..models.armor_creation_data import ArmorCreationData


class ArmorCFFExporter:
    """Export armor to CFF format"""

    def export_armor(self, armor_data: ArmorCreationData) -> Dict[int, bytes]:
        """
        Export armor to CFF categories

        Returns:
            Dict mapping category IDs to binary data
        """

        exports = {}

        # Category 2003: Item General Info
        exports[2003] = self.export_item_general(armor_data)

        # Category 2004: Item Stats (armor-specific stats)
        exports[2004] = self.export_item_stats(armor_data)

        # Category 2016: Text entries (name, description)
        exports[2016] = self.export_text_entries(armor_data)

        # Category 2014: Effects (if any special effects)
        if armor_data.special_abilities or armor_data.set_bonuses:
            exports[2014] = self.export_effects(armor_data)

        return exports

    def export_item_general(self, armor_data: ArmorCreationData) -> bytes:
        """Export to Category 2003 (Item General Info)"""
        # Structure based on SpellForce CFF format
        # This is a simplified version - actual format may vary

        try:
            # Pack basic item info
            # ItemID (uint16), NameID (uint16), Type (byte), SubType (byte), etc.
            data = struct.pack('<HHBBIIBH',
                armor_data.armor_id,          # ItemID
                armor_data.armor_id + 20000,  # NameID (offset for text)
                1,                            # ItemType: EQUIPMENT
                self._get_slot_subtype(armor_data),  # SubType based on slot
                0,                            # Sell value (placeholder)
                0,                            # Buy value (placeholder)
                0,                            # Option flags
                0                             # Item set ID (placeholder)
            )

            return data

        except struct.error as e:
            raise ValueError(f"Failed to pack item general data: {e}")

    def export_item_stats(self, armor_data: ArmorCreationData) -> bytes:
        """Export to Category 2004 (Item Stats)"""
        # Armor-specific stats
        try:
            # Structure: ItemID + various stat bonuses
            data = struct.pack('<Hiiiiiiiiiiiiii',
                armor_data.armor_id,      # Foreign key to item
                armor_data.strength,      # Strength bonus
                armor_data.stamina,       # Stamina bonus
                armor_data.agility,       # Agility bonus
                armor_data.dexterity,     # Dexterity bonus
                armor_data.intelligence,  # Intelligence bonus
                armor_data.wisdom,        # Wisdom bonus
                armor_data.charisma,      # Charisma bonus
                armor_data.health_bonus,  # Health bonus
                armor_data.mana_bonus,    # Mana bonus
                armor_data.base_armor,    # Base armor value
                int(armor_data.resist_fire * 100),   # Fire resist (as int percentage)
                int(armor_data.resist_ice * 100),    # Ice resist
                int(armor_data.resist_black * 100),  # Black resist
                int(armor_data.resist_mind * 100)    # Mind resist
            )

            return data

        except struct.error as e:
            raise ValueError(f"Failed to pack item stats: {e}")

    def export_text_entries(self, armor_data: ArmorCreationData) -> List[bytes]:
        """Export to Category 2016 (Text Strings)"""
        entries = []

        try:
            # Name entry
            name_id = armor_data.armor_id + 20000
            name_entry = self._create_text_entry(name_id, armor_data.armor_name)
            entries.append(name_entry)

            # Description entry (if provided)
            if armor_data.description.strip():
                desc_id = armor_data.armor_id + 20001
                desc_entry = self._create_text_entry(desc_id, armor_data.description)
                entries.append(desc_entry)

            # Display name entry (if different from name)
            if armor_data.display_name.strip() and armor_data.display_name != armor_data.armor_name:
                display_id = armor_data.armor_id + 20002
                display_entry = self._create_text_entry(display_id, armor_data.display_name)
                entries.append(display_entry)

        except (UnicodeEncodeError, struct.error) as e:
            raise ValueError(f"Failed to create text entries: {e}")

        return entries

    def export_effects(self, armor_data: ArmorCreationData) -> bytes:
        """Export to Category 2014 (Effects)"""
        # Placeholder for effects system
        # This would need to be implemented based on actual CFF effects format
        try:
            # Simple placeholder - just item ID for now
            data = struct.pack('<H', armor_data.armor_id)
            return data
        except struct.error as e:
            raise ValueError(f"Failed to pack effects: {e}")

    def _get_slot_subtype(self, armor_data: ArmorCreationData) -> int:
        """Get the subtype byte for the armor slot"""
        # Map armor slots to SpellForce item subtypes
        slot_map = {
            'HEAD': 0,      # Helmet
            'CHEST': 1,     # Chest armor
            'LEGS': 2,      # Leg armor
            'FEET': 3,      # Boots
            'RIGHT_RING': 4, # Right ring
            'LEFT_RING': 5,  # Left ring
            'LEFT_HAND': 6   # Shield
        }

        slot_name = armor_data.slot.name
        return slot_map.get(slot_name, 1)  # Default to chest armor

    def _create_text_entry(self, text_id: int, text: str) -> bytes:
        """Create a text entry in CFF format"""
        # Encode text as UTF-16LE (SpellForce standard)
        text_bytes = text.encode('utf-16le')
        text_length = len(text_bytes) // 2  # Length in UTF-16 code units

        # Structure: TextID (uint), Length (ushort), Text (UTF-16LE bytes)
        return struct.pack(f'<HI{text_length}s',
            text_id,
            text_length,
            text_bytes
        )

    def save_to_json(self, exports: Dict[int, Any], output_file: str):
        """Save exported data to JSON for testing/debugging"""
        import json
        import os

        # Convert binary data to hex strings for JSON storage
        json_data = {
            "armor_exports": {},
            "metadata": {
                "export_categories": list(exports.keys()),
                "format_version": "1.0"
            }
        }

        for category_id, data in exports.items():
            if isinstance(data, list):
                # Multiple entries (like text entries)
                json_data["armor_exports"][f"category_{category_id}"] = [
                    {"size": len(entry), "hex": entry.hex()} for entry in data
                ]
            else:
                # Single binary blob
                json_data["armor_exports"][f"category_{category_id}"] = {
                    "size": len(data),
                    "hex": data.hex()
                }

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

    def validate_export(self, armor_data: ArmorCreationData) -> List[str]:
        """Validate that armor can be exported"""
        issues = []

        if armor_data.armor_id <= 0:
            issues.append("Armor ID must be positive")

        if not armor_data.armor_name.strip():
            issues.append("Armor name is required for export")

        if len(armor_data.armor_name) > 32:
            issues.append("Armor name too long (max 32 characters)")

        return issues