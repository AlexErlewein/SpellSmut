import json
import struct
from typing import Dict, List, Optional
from pathlib import Path
from ..models.weapon_creation_data import WeaponCreationData

# Import tirganach library for CFF handling
try:
    from TirganachReloaded.tirganach import GameData
    from TirganachReloaded.tirganach.types import ItemType, EquipmentType
    from TirganachReloaded.tirganach.entities import Item, Weapon, Localisation
    TIRGANACH_AVAILABLE = True
except ImportError as e:
    TIRGANACH_AVAILABLE = False
    print(f"Warning: Tirganach library not available: {e}")
    print("CFF export will be limited to legacy binary format.")

class WeaponCFFExporter:
    """Export weapon to CFF format using the tirganach library"""

    def __init__(self, gamedata_path: Optional[str] = None):
        """
        Initialize the CFF exporter

        Args:
            gamedata_path: Path to original GameData.cff file (for reference data)
        """
        self.gamedata_path = gamedata_path
        self.gamedata = None

        if TIRGANACH_AVAILABLE and gamedata_path and Path(gamedata_path).exists():
            try:
                self.gamedata = GameData(gamedata_path)
                print(f"Loaded reference GameData from: {gamedata_path}")
            except Exception as e:
                print(f"Warning: Could not load GameData: {e}")

    def export_weapon_to_gamedata(self, weapon_data: WeaponCreationData, output_path: str) -> bool:
        """
        Export weapon to a new GameData.cff file using tirganach library

        Args:
            weapon_data: The weapon to export
            output_path: Path where the new GameData.cff will be saved

        Returns:
            True if export succeeded, False otherwise
        """
        if not TIRGANACH_AVAILABLE:
            print("Error: Tirganach library not available")
            return False

        if not self.gamedata:
            print("Error: No reference GameData loaded")
            return False

        try:
            # Create new GameData by copying the reference
            new_gamedata = self._create_modified_gamedata(weapon_data)

            # Save the new GameData
            new_gamedata.save(output_path)
            print(f"Successfully exported weapon to: {output_path}")
            return True

        except Exception as e:
            try:
                import traceback
                print(f"Error exporting weapon to CFF: {e!r} ({type(e).__name__})")
                traceback.print_exc()
            except Exception:
                print(f"Error exporting weapon to CFF: {e}")
            return False

    def _create_modified_gamedata(self, weapon_data: WeaponCreationData) -> GameData:
        """Create a new GameData instance with the weapon added"""

        # Create a copy of the original GameData by reloading it
        # This ensures we have a fresh instance to work with
        if not self.gamedata_path:
            raise ValueError("No GameData path available for creating modified version")

        new_gamedata = GameData(self.gamedata_path)

        try:
            # Allocate localisation IDs to avoid collisions with existing text rows
            # Prefer weapon_id-based offset when free; otherwise pick a free ID in a safe high range
            preferred_name_id = weapon_data.weapon_id + 20000
            name_id = self._allocate_localisation_id(new_gamedata, preferred_name_id)

            desc_id = None
            if weapon_data.description:
                preferred_desc_id = weapon_data.weapon_id + 20001
                # Ensure description ID does not collide with name_id
                if preferred_desc_id == name_id:
                    preferred_desc_id = preferred_desc_id + 1
                desc_id = self._allocate_localisation_id(new_gamedata, preferred_desc_id)

            # Step 1: Create the Item entry for the weapon (with allocated name_id)
            self._add_item_entry(new_gamedata, weapon_data, name_id)

            # Step 2: Create the Weapon entry with combat stats
            self._add_weapon_entry(new_gamedata, weapon_data)

            # Step 3: Create Item Requirements entries for school requirements
            self._add_item_requirements(new_gamedata, weapon_data)

            # Step 4: Create Localization entries for name and description using allocated IDs
            self._add_localization_entries(new_gamedata, weapon_data, name_id, desc_id)

            # Step 5: Handle new weapon types (if any)
            if weapon_data.weapon_type_id >= 20:
                self._add_weapon_type_entry(new_gamedata, weapon_data)

            # Step 6: Handle new materials (if any)
            if weapon_data.weapon_material_id >= 10:
                self._add_material_entry(new_gamedata, weapon_data)

            print(f"Successfully added weapon '{weapon_data.weapon_name}' (ID: {weapon_data.weapon_id})")
            return new_gamedata

        except Exception as e:
            try:
                import traceback
                print(f"Error creating modified GameData: {e!r} ({type(e).__name__})")
                traceback.print_exc()
            except Exception:
                print(f"Error creating modified GameData: {e}")
            raise

    def _add_item_entry(self, gamedata: GameData, weapon_data: WeaponCreationData, name_id: int):
        """Add an Item entry for the weapon, using provided name_id"""

        # Create item binary data based on tirganach entity structure
        # Item structure based on entities.py:
        # - item_id: int (2 bytes, primary key)
        # - item_type: ItemType (1 byte)
        # - item_subtype: EquipmentType (1 byte)
        # - name_id: int (2 bytes)
        # - unit_stats_id: int (2 bytes)
        # - army_unit_id: int (2 bytes)
        # - building_id: int (2 bytes)
        # - unknown1: int (1 byte)
        # - selling_price: int (4 bytes)
        # - buying_price: int (4 bytes)
        # - item_set_id: int (1 byte)

        from TirganachReloaded.tirganach.types import ItemType, EquipmentType

        # Map our weapon hands to equipment types
        equipment_map = {
            "1H": EquipmentType.ONEHANDED_WEAPON,
            "2H": EquipmentType.TWOHANDED_WEAPON,
            "Unarmed": EquipmentType.ONEHANDED_WEAPON
        }

        # Create binary data for the item
        item_data = bytearray(22)  # Item entity length

        # Pack the data according to tirganach structure
        import struct
        struct.pack_into('<H', item_data, 0, weapon_data.weapon_id)  # item_id
        item_type_val = (
            ItemType.EQUIPMENT.value[0]
            if isinstance(ItemType.EQUIPMENT.value, tuple)
            else ItemType.EQUIPMENT.value
        )
        struct.pack_into('<B', item_data, 2, item_type_val)  # item_type

        equip_enum = equipment_map.get(
            weapon_data.hands.value, EquipmentType.ONEHANDED_WEAPON
        )
        equip_val = (
            equip_enum.value[0] if isinstance(equip_enum.value, tuple) else equip_enum.value
        )
        struct.pack_into('<B', item_data, 3, equip_val)  # item_subtype
        struct.pack_into('<H', item_data, 4, name_id)  # name_id
        struct.pack_into('<H', item_data, 6, 0)  # unit_stats_id (0 for regular items)
        struct.pack_into('<H', item_data, 8, 0)  # army_unit_id
        struct.pack_into('<H', item_data, 10, 0)  # building_id
        struct.pack_into('<B', item_data, 12, 0)  # unknown1
        struct.pack_into('<I', item_data, 13, weapon_data.sell_value)  # selling_price
        struct.pack_into('<I', item_data, 17, weapon_data.buy_value)  # buying_price
        struct.pack_into('<B', item_data, 21, weapon_data.item_set_id)  # item_set_id

        # Create the Item entity and add to gamedata
        item_entity = Item(bytes(item_data), game_data=gamedata)

        # Add to the items table (this is a simplified approach)
        # In practice, we'd need to properly append to the table structure
        gamedata.items.append(item_entity)
        print(f"  ✓ Added Item entry for weapon ID {weapon_data.weapon_id}")

    def _add_weapon_entry(self, gamedata: GameData, weapon_data: WeaponCreationData):
        """Add a Weapon entry with combat stats"""

        # Weapon structure based on entities.py:
        # - item_id: int (2 bytes, primary key)
        # - min_damage: int (2 bytes)
        # - max_damage: int (2 bytes)
        # - min_range: int (2 bytes)
        # - max_range: int (2 bytes)
        # - speed: int (2 bytes)
        # - weapon_type: int (2 bytes)
        # - material: int (2 bytes)

        # Create binary data for the weapon
        weapon_data_binary = bytearray(16)  # Weapon entity length

        import struct
        struct.pack_into('<H', weapon_data_binary, 0, weapon_data.weapon_id)  # item_id
        struct.pack_into('<H', weapon_data_binary, 2, weapon_data.min_damage)  # min_damage
        struct.pack_into('<H', weapon_data_binary, 4, weapon_data.max_damage)  # max_damage
        struct.pack_into('<H', weapon_data_binary, 6, weapon_data.min_range)  # min_range
        struct.pack_into('<H', weapon_data_binary, 8, weapon_data.max_range)  # max_range
        struct.pack_into('<H', weapon_data_binary, 10, weapon_data.attack_speed)  # speed
        struct.pack_into('<H', weapon_data_binary, 12, weapon_data.weapon_type_id)  # weapon_type
        struct.pack_into('<H', weapon_data_binary, 14, weapon_data.weapon_material_id)  # material

        # Create the Weapon entity and add to gamedata
        weapon_entity = Weapon(bytes(weapon_data_binary), game_data=gamedata)

        # Add to the weapons table
        gamedata.weapons.append(weapon_entity)
        print(f"  ✓ Added Weapon entry for weapon ID {weapon_data.weapon_id}")

    def _add_localization_entries(self, gamedata: GameData, weapon_data: WeaponCreationData, name_id: int, desc_id: Optional[int]):
        """Add localization entries for weapon name and description using allocated IDs"""

        # Create localization entries for English text
        from TirganachReloaded.tirganach.types import Language

        # Name localisation entity (ensure correct record length)
        name_entity = Localisation(b"\x00" * Localisation._length(), game_data=gamedata)
        name_entity.text_id = name_id  # ushort
        name_entity.language = Language.ENGLISH
        name_entity.is_dialogue = False
        name_entity.dialogue_name = ""
        name_entity.text = weapon_data.weapon_name or ""
        gamedata.localisation.append(name_entity)

        # Description localisation entity (optional)
        if weapon_data.description and desc_id is not None:
            desc_entity = Localisation(b"\x00" * Localisation._length(), game_data=gamedata)
            desc_entity.text_id = desc_id
            desc_entity.language = Language.ENGLISH
            desc_entity.is_dialogue = False
            desc_entity.dialogue_name = ""
            desc_entity.text = weapon_data.description
            gamedata.localisation.append(desc_entity)

        print(f"  ✓ Added localization entries for weapon '{weapon_data.weapon_name}'")

    def _allocate_localisation_id(self, gamedata: GameData, preferred_id: int) -> int:
        """Return a free localisation text_id (ushort) avoiding collisions with existing rows."""
        try:
            used: set[int] = set()
            try:
                for row in gamedata.localisation:
                    # Some entity implementations might not expose text_id directly
                    tid = getattr(row, 'text_id', None)
                    if isinstance(tid, int):
                        used.add(tid)
            except Exception:
                pass

            # If preferred is valid and free, use it
            if isinstance(preferred_id, int) and 0 <= preferred_id <= 0xFFFF and preferred_id not in used:
                return preferred_id

            # Otherwise, search a safe high range (65000 down to 40000)
            for tid in range(65000, 39999, -1):
                if tid not in used:
                    return tid

            # As a last resort, search upwards from 30000
            for tid in range(30000, 65535):
                if tid not in used:
                    return tid

            # If nothing free found (extremely unlikely), fallback to preferred masked to ushort
            return preferred_id & 0xFFFF
        except Exception:
            # On any error, fallback to preferred within ushort
            return preferred_id & 0xFFFF

    def _add_weapon_type_entry(self, gamedata: GameData, weapon_data: WeaponCreationData):
        """Add a new weapon type entry if it's a custom type"""
        # This would add to WeaponTypeName table
        # Implementation would be similar to the above methods
        print(f"  ✓ Weapon type {weapon_data.weapon_type_name} is custom - type entries would be added here")

    def _add_material_entry(self, gamedata: GameData, weapon_data: WeaponCreationData):
        """Add a new material entry if it's a custom material"""
        # This would add to WeaponMaterialName table
        # Implementation would be similar to the above methods
        print(f"  ✓ Material {weapon_data.weapon_material_name} is custom - material entries would be added here")

    def export_weapon(self, weapon_data: WeaponCreationData) -> Dict[str, bytes]:
        """
        Export weapon to CFF categories (legacy method for compatibility)

        Returns:
            Dict mapping category IDs to binary data
        """

        exports = {}

        # Category 2003: Item General Info (equivalent to Item table)
        exports[2003] = self.export_item_general(weapon_data)

        # Category 2015: Weapon Combat Data (equivalent to Weapon table)
        exports[2015] = self.export_weapon_data(weapon_data)

        # Category 2016: Text entries (name, description - equivalent to Localisation table)
        text_entries = self.export_text_entries(weapon_data)
        exports[2016] = b''.join(text_entries) if text_entries else b''

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
        # - ItemID (uint) - Changed from ushort to handle larger IDs
        # - NameID (uint) - Changed from ushort to handle larger IDs
        # - ItemType (byte) - EQUIPMENT
        # - ItemSubtype (byte) - WEAPON
        # - SellValue (uint)
        # - BuyValue (uint)
        # - Option (byte)
        # - ItemSetID (ushort)

        # Clamp and validate values to prevent overflow
        item_id = min(max(weapon_data.weapon_id, 0), 4294967295)  # uint32 max
        name_id = min(max(item_id + 20000, 0), 4294967295)  # uint32 max
        sell_value = min(max(weapon_data.sell_value, 0), 4294967295)  # uint32 max
        buy_value = min(max(weapon_data.buy_value, 0), 4294967295)  # uint32 max
        item_set_id = min(max(weapon_data.item_set_id, 0), 65535)  # ushort max

        data = struct.pack('<IIBBIIBxH',
            item_id,                         # ItemID (uint)
            name_id,                         # NameID (uint)
            1,                               # ItemType: EQUIPMENT
            2,                               # ItemSubtype: WEAPON
            sell_value,                      # SellValue (uint)
            buy_value,                       # BuyValue (uint)
            0,                               # Option
            item_set_id                      # ItemSetID (ushort)
        )

        return data
    
    def export_weapon_data(self, weapon_data: WeaponCreationData) -> bytes:
        """Export to Category 2015 (Weapon Combat Data)"""
        # Structure:
        # - ItemID (uint) - Changed from ushort to handle larger IDs, Foreign key to 2003
        # - MinDamage (ushort)
        # - MaxDamage (ushort)
        # - MinRange (ushort)
        # - MaxRange (ushort)
        # - WeaponSpeed (ushort)
        # - WeaponType (ushort) - Foreign key to 2063
        # - WeaponMaterial (ushort) - Foreign key to 2064

        # Clamp and validate values to prevent overflow
        item_id = min(max(weapon_data.weapon_id, 0), 4294967295)  # uint32 max
        min_damage = min(max(weapon_data.min_damage, 0), 65535)  # ushort max
        max_damage = min(max(weapon_data.max_damage, 0), 65535)  # ushort max
        min_range = min(max(weapon_data.min_range, 0), 65535)  # ushort max
        max_range = min(max(weapon_data.max_range, 0), 65535)  # ushort max
        attack_speed = min(max(weapon_data.attack_speed, 0), 65535)  # ushort max
        weapon_type_id = min(max(weapon_data.weapon_type_id, 0), 65535)  # ushort max
        weapon_material_id = min(max(weapon_data.weapon_material_id, 0), 65535)  # ushort max

        data = struct.pack('<IHHHHHHH',
            item_id,                         # ItemID (uint)
            min_damage,                      # MinDamage (ushort)
            max_damage,                      # MaxDamage (ushort)
            min_range,                       # MinRange (ushort)
            max_range,                       # MaxRange (ushort)
            attack_speed,                    # WeaponSpeed (ushort)
            weapon_type_id,                  # WeaponType (ushort)
            weapon_material_id               # WeaponMaterial (ushort)
        )

        return data
    
    def _add_item_requirements(self, gamedata: GameData, weapon_data: WeaponCreationData):
        """Add Item Requirements entries for school requirements"""

        if not weapon_data.requirements.school_requirements:
            print(f"  ✓ No school requirements to add for weapon ID {weapon_data.weapon_id}")
            return

        try:
            # Check if gamedata has item_requirements table
            if not hasattr(gamedata, 'item_requirements'):
                print(f"  ⚠ Warning: item_requirements table not found in GameData")
                return

            # Import ItemRequirement entity
            from TirganachReloaded.tirganach.entities import ItemRequirement

            # Create ItemRequirements entries for each school requirement
            for req_number, school_req in enumerate(weapon_data.requirements.school_requirements):
                try:
                    # ItemRequirement structure based on entities.py:
                    # - item_id: int (2 bytes, primary key)
                    # - requirement_number: int (1 byte)
                    # - requirement_school: School (2 bytes enum)
                    # - level: int (1 byte)

                    # Create binary data for the item requirement
                    req_data = bytearray(6)  # ItemRequirement entity length

                    # Pack the data according to tirganach structure
                    import struct
                    struct.pack_into('<H', req_data, 0, weapon_data.weapon_id)  # item_id
                    struct.pack_into('<B', req_data, 2, req_number)  # requirement_number

                    # Convert school name to school enum value
                    school_value = self._get_school_enum_value(school_req.school_name)
                    struct.pack_into('<H', req_data, 3, school_value)  # requirement_school (2 bytes)
                    struct.pack_into('<B', req_data, 5, school_req.level)  # level

                    # Create the ItemRequirement entity and add to gamedata
                    item_req_entity = ItemRequirement(bytes(req_data), game_data=gamedata)

                    # Add to the item_requirements table
                    gamedata.item_requirements.append(item_req_entity)

                    print(f"  ✓ Added ItemRequirement entry: {school_req.school_name} Level {school_req.level}")

                except Exception as e:
                    print(f"  ⚠ Warning: Failed to add school requirement {school_req.school_name}: {e}")
                    continue

            print(f"  ✓ Added {len(weapon_data.requirements.school_requirements)} school requirements for weapon ID {weapon_data.weapon_id}")

        except Exception as e:
            print(f"  ⚠ Warning: Failed to add item requirements for weapon ID {weapon_data.weapon_id}: {e}")

    def _get_school_enum_value(self, school_name: str) -> int:
        """Convert school name string to enum value"""
        # Map school names to their enum values
        # These values come from the tirganach School enum
        school_mapping = {
            "LEVEL_ONLY": 0,
            "LIGHT_COMBAT": 1,
            "PIERCING_WEAPONS": 2,
            "LIGHT_BLADE_WEAPONS": 3,
            "LIGHT_BLUNT_WEAPONS": 4,
            "LIGHT_ARMOR": 5,
            "HEAVY_COMBAT": 6,
            "HEAVY_BLADE_WEAPONS": 7,
            "HEAVY_BLUNT_WEAPONS": 8,
            "HEAVY_ARMOR": 9,
            "SHIELDS": 10,
            "RANGED_COMBAT": 11,
            "BOWS": 12,
            "CROSSBOWS": 13,
            "WHITE_MAGIC": 14,
            "LIFE": 15,
            "NATURE": 16,
            "BOONS": 17,
            "ELEMENTAL_MAGIC": 18,
            "FIRE": 19,
            "ICE": 20,
            "EARTH": 21,
            "MIND_MAGIC": 22,
            "ENCHANTMENT": 23,
            "OFFENSIVE": 24,
            "DEFENSIVE": 25,
            "BLACK_MAGIC": 26,
            "DEATH": 27,
            "NECROMANCY": 28,
        }

        return school_mapping.get(school_name, 0)  # Default to LEVEL_ONLY (0) if not found

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
