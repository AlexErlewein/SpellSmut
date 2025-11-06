"""
CFF Export for Armor

This module handles exporting armor data to CFF (Configuration File Format) format
for use in the game.
"""

import os
from typing import Dict, Any

# Import Armor class from the dedicated model file
try:
    from .armor_model import Armor
except ImportError:
    # For direct execution
    from cff_editor.systems.armor_system.armor_model import Armor


def export_armor_to_cff(armor: Armor, output_dir: str = "./cff_export") -> str:
    """
    Export a single armor piece to CFF format
    
    Args:
        armor: The armor object to export
        output_dir: Directory to save the CFF file
        
    Returns:
        Path to the exported file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct the CFF content
    cff_content = f"""[ITEM_{armor.id}]
Name={armor.name}
DisplayName={armor.display_name}
Description={armor.description}
ItemType=Armor
Slot={armor.slot if armor.slot is not None else 0}
ArmorType={armor.armor_type or "Unknown"}
Material={armor.material or "Unknown"}
Tier={armor.tier}
LevelRequirement={armor.level_requirement}
ClassRestriction={armor.class_restriction}

# Stat Bonuses
Strength={armor.strength}
Stamina={armor.stamina}
Agility={armor.agility}
Dexterity={armor.dexterity}
Intelligence={armor.intelligence}
Wisdom={armor.wisdom}
Charisma={armor.charisma}
Health={armor.health}
Mana={armor.mana}
ArmorValue={armor.armor_value}

# Resistances
ResistFire={armor.resist_fire}
ResistIce={armor.resist_ice}
ResistBlack={armor.resist_black}
ResistMind={armor.resist_mind}
PhysicalResist={armor.physical_resist}
MagicResist={armor.magic_resist}
CriticalResist={armor.critical_resist}

# Speed Modifiers
RunSpeed={armor.run_speed}
FightSpeed={armor.fight_speed}
CastSpeed={armor.cast_speed}
StealthBonus={armor.stealth_bonus}
SwimmingSpeed={armor.swimming_speed}
JumpHeight={armor.jump_height}

# Visual Properties
IconID={armor.icon_id}
ModelRef={armor.model_ref}
Texture={armor.texture}
NormalMap={armor.normal_map}

# Advanced Features
SetID={armor.set_id or "None"}
EnchantmentSlots={armor.enchantment_slots}
StatBalanceRating={armor.stat_balance_rating}
"""
    
    # Write the CFF file
    file_path = os.path.join(output_dir, f"armor_{armor.id:05d}_{armor.name.replace(' ', '_')}.cff")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cff_content)
    
    return file_path


def export_armors_to_cff(armors: Dict[int, Armor], output_dir: str = "./cff_export") -> Dict[int, str]:
    """
    Export multiple armor pieces to CFF format
    
    Args:
        armors: Dictionary of armor objects to export
        output_dir: Directory to save the CFF files
        
    Returns:
        Dictionary mapping armor IDs to exported file paths
    """
    exported_files = {}
    for armor_id, armor in armors.items():
        try:
            file_path = export_armor_to_cff(armor, output_dir)
            exported_files[armor_id] = file_path
        except Exception as e:
            print(f"Failed to export armor {armor_id}: {e}")
    
    return exported_files