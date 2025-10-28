import json
from ..models.weapon_creation_data import WeaponCreationData

class WeaponLoader:
    """Load and save weapon data"""
    
    @staticmethod
    def load_weapon(weapon_id: int) -> WeaponCreationData:
        """Load existing weapon by ID"""
        # Load from enhanced_weapons.json
        with open("src/TirganachReloaded/enhanced_weapons.json", 'r') as f:
            weapons = json.load(f)
        
        weapon_data = next((w for w in weapons if w['item_id'] == weapon_id), None)
        if not weapon_data:
            raise ValueError(f"Weapon ID {weapon_id} not found")
        
        # Convert to WeaponCreationData
        return WeaponCreationData(
            weapon_id=weapon_data['item_id'],
            creation_mode="edit",
            source_weapon_id=weapon_data['item_id'],
            weapon_name=weapon_data['name'],
            weapon_type_id=weapon_data.get('weapon_type_id', 4),
            weapon_type_name=weapon_data.get('weapon_type_name', ''),
            weapon_material_id=weapon_data.get('weapon_material_id', 5),
            weapon_material_name=weapon_data.get('weapon_material_name', ''),
            min_damage=weapon_data.get('min_damage', 10),
            max_damage=weapon_data.get('max_damage', 15),
            attack_speed=weapon_data.get('weapon_speed', 100),
            min_range=weapon_data.get('min_range', 0),
            max_range=weapon_data.get('max_range', 2),
            sell_value=weapon_data.get('sell_value', 50),
            buy_value=weapon_data.get('buy_value', 100),
            # ... map other fields
        )
    
    @staticmethod
    def save_weapon(weapon_data: WeaponCreationData, export_path: str):
        """Save weapon to JSON file"""
        weapon_dict = {
            "item_id": weapon_data.weapon_id,
            "name": weapon_data.weapon_name,
            "weapon_type_id": weapon_data.weapon_type_id,
            "weapon_material_id": weapon_data.weapon_material_id,
            "min_damage": weapon_data.min_damage,
            "max_damage": weapon_data.max_damage,
            "weapon_speed": weapon_data.attack_speed,
            "min_range": weapon_data.min_range,
            "max_range": weapon_data.max_range,
            "sell_value": weapon_data.sell_value,
            "buy_value": weapon_data.buy_value,
            "rarity": weapon_data.rarity.value,
            "icon_handle": weapon_data.icon_handle,
            "requirements": {
                "strength": weapon_data.requirements.strength,
                "dexterity": weapon_data.requirements.dexterity,
                "intelligence": weapon_data.requirements.intelligence,
                "level": weapon_data.requirements.level
            },
            "effects": [
                {
                    "effect_id": effect.effect_id,
                    "effect_name": effect.effect_name,
                    "value": effect.value,
                    "duration": effect.duration
                }
                for effect in weapon_data.effects
            ],
            "created_date": weapon_data.created_date,
            "modified_date": weapon_data.modified_date,
            "author": weapon_data.author,
            "version": weapon_data.version
        }
        
        with open(export_path, 'w') as f:
            json.dump(weapon_dict, f, indent=2)
