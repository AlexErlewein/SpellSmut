import json
import struct
from typing import Dict, List
from ..models.weapon_creation_data import WeaponCreationData

class WeaponCFFExporter:
    """Export weapon to CFF format"""
    
    def export_weapon(self, weapon_data: WeaponCreationData) -> Dict[str, bytes]:
        """
        Export weapon to CFF categories
        
        Returns:
            Dict mapping category IDs to binary data
        """
        
        exports = {}
        
        # Category 2003: Item General Info
        exports[2003] = self.export_item_general(weapon_data)
        
        # Category 2015: Weapon Combat Data
        exports[2015] = self.export_weapon_data(weapon_data)
        
        # Category 2016: Text entries (name, description)
        exports[2016] = self.export_text_entries(weapon_data)
        
        # Category 2063: Weapon Type (if new type)
        if weapon_data.weapon_type_id >= 20:
            exports[2063] = self.export_weapon_type(weapon_data)
        
        # Category 2064: Material (if new material)
        if weapon_data.weapon_material_id >= 10:
            exports[2064] = self.export_material(weapon_data)
        
        # Category 2014: Effects (if any)
        if weapon_data.effects:
            exports[2014] = self.export_weapon_effects(weapon_data)
        
        return exports
    
    def export_item_general(self, weapon_data: WeaponCreationData) -> bytes:
        """Export to Category 2003 (Item General Info)"""
        # Structure:
        # - ItemID (ushort)
        # - NameID (ushort)
        # - ItemType (byte) - EQUIPMENT
        # - ItemSubtype (byte) - WEAPON
        # - SellValue (uint)
        # - BuyValue (uint)
        # - Option (byte)
        # - ItemSetID (ushort)
        
        data = struct.pack('<HHBBIIBxH',
            weapon_data.weapon_id,          # ItemID
            weapon_data.weapon_id + 20000,  # NameID (arbitrary offset)
            1,                               # ItemType: EQUIPMENT
            2,                               # ItemSubtype: WEAPON
            weapon_data.sell_value,
            weapon_data.buy_value,
            0,                               # Option
            weapon_data.item_set_id
        )
        
        return data
    
    def export_weapon_data(self, weapon_data: WeaponCreationData) -> bytes:
        """Export to Category 2015 (Weapon Combat Data)"""
        # Structure:
        # - ItemID (ushort) - Foreign key to 2003
        # - MinDamage (ushort)
        # - MaxDamage (ushort)
        # - MinRange (ushort)
        # - MaxRange (ushort)
        # - WeaponSpeed (ushort)
        # - WeaponType (ushort) - Foreign key to 2063
        # - WeaponMaterial (ushort) - Foreign key to 2064
        
        data = struct.pack('<HHHHHHHH',
            weapon_data.weapon_id,
            weapon_data.min_damage,
            weapon_data.max_damage,
            weapon_data.min_range,
            weapon_data.max_range,
            weapon_data.attack_speed,
            weapon_data.weapon_type_id,
            weapon_data.weapon_material_id
        )
        
        return data
    
    def export_text_entries(self, weapon_data: WeaponCreationData) -> List[bytes]:
        """Export to Category 2016 (Text Strings)"""
        # Two entries:
        # 1. Weapon name
        # 2. Weapon description
        
        name_id = weapon_data.weapon_id + 20000
        desc_id = weapon_data.weapon_id + 20001
        
        entries = []
        
        # Name entry
        name_entry = self.create_text_entry(
            name_id,
            weapon_data.weapon_name
        )
        entries.append(name_entry)
        
        # Description entry
        if weapon_data.description:
            desc_entry = self.create_text_entry(
                desc_id,
                weapon_data.description
            )
            entries.append(desc_entry)
        
        return entries
    
    def create_text_entry(self, text_id: int, text: str) -> bytes:
        """Create a text entry"""
        # Encode text as UTF-16LE (SpellForce text format)
        text_bytes = text.encode('utf-16le')
        text_length = len(text_bytes)
        
        # Structure:
        # - TextID (uint)
        # - TextLength (ushort)
        # - Text (UTF-16LE string)
        
        return struct.pack(f'<IH{text_length}s',
            text_id,
            text_length,
            text_bytes
        )

    def export_weapon_type(self, weapon_data: WeaponCreationData) -> bytes:
        # This is a placeholder implementation
        return b''

    def export_material(self, weapon_data: WeaponCreationData) -> bytes:
        # This is a placeholder implementation
        return b''

    def export_weapon_effects(self, weapon_data: WeaponCreationData) -> bytes:
        # This is a placeholder implementation
        return b''

    def save_to_cff(self, exports: Dict[int, bytes], output_file: str):
        """Save exported data to CFF file"""
        # This would integrate with the existing CFF library
        # For now, save to JSON for testing
        
        output_data = {
            "weapon_exports": {}
        }
        
        for category_id, data in exports.items():
            output_data["weapon_exports"][f"category_{category_id}"] = {
                "size": len(data),
                "hex": data.hex()
            }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
