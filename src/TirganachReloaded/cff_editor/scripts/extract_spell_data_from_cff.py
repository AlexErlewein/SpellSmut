#!/usr/bin/env python3
"""
Extract spell data from SpellForce GameData.cff file and convert it to SpellForge format
"""

import sys
from pathlib import Path
import json

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from TirganachReloaded.tirganach import GameData
from TirganachReloaded.tirganach.types import School


def extract_spell_data_from_cff(cff_path: str):
    """
    Extract spell data from the CFF file
    
    Args:
        cff_path: Path to the GameData.cff file
    
    Returns:
        List of spell data in a format compatible with SpellForge
    """
    print(f"Loading CFF file: {cff_path}")
    
    # Load the CFF file
    game_data = GameData(cff_path)
    
    # Get all spells and spell names
    spells = list(game_data.spells)
    spell_names = list(game_data.spell_names)
    
    print(f"Found {len(spells)} spells and {len(spell_names)} spell names")
    
    # Create a mapping from spell_name_id to spell_name data
    spell_name_map = {}
    for spell_name in spell_names:
        spell_name_map[spell_name.spell_name_id] = spell_name
    
    # Convert CFF spell data to SpellForge-compatible format
    extracted_spells = []
    
    for spell in spells:
        # Get the corresponding spell name
        spell_name = spell_name_map.get(spell.spell_name_id)
        
        # Determine magic school based on the requirements in the spell
        magic_school = determine_magic_school(spell)
        
        # Determine spell type based on flags and properties
        spell_type = determine_spell_type(spell, spell_name)
        
        # Determine target type based on cast_type
        target_type = determine_target_type(spell.cast_type)
        
        # Map to SpellForge format
        spell_data = {
            "spell_line_id": spell.spell_id,
            "spell_name": getattr(spell_name, 'name', f"Unknown Spell {spell.spell_id}"),
            "internal_name": getattr(spell_name, 'name', f"Spell_{spell.spell_id}").replace(" ", ""),
            "description": getattr(spell_name, 'description', ''),
            "magic_school": magic_school,
            "spell_type": spell_type,
            "target_type": target_type,
            "has_projectile": has_projectile(spell, spell_name),  # Simple heuristic
            "base_range": spell.max_range if spell.max_range > 0 else 20.0,
            "aoe_radius": 0.0,  # Would need to analyze spell effects for this
            "duration": 0.0,  # Would need to analyze spell effects for this
            "special_effects": get_special_effects(spell),  # Would depend on effects
            "num_levels": 15,  # Default to 15 levels
            "levels": create_spell_levels(spell),  # Create levels based on spell parameters
            "scaling_mode": "linear",  # Default scaling mode
            "vfx_cast": "",  # Would need to parse effect names
            "vfx_projectile": "",
            "vfx_resolve": "",
            "vfx_target": "",
            "vfx_overtime": "",
            "sfx_cast": "",
            "sfx_projectile": "",
            "sfx_resolve": "",
            "sfx_hit": "",
            "triggered_effects": [],
            "has_aura": spell.cast_type == 258,  # 258 seems to indicate aura spells
            "aura_radius": 0.0,
            "aura_duration": 0.0,
            "aura_vfx": "",
            "aura_sfx": "",
            "projectile_count": 1,
            "projectile_spread": 0.0,
            "projectile_speed": 1.0,
            "projectile_gravity": 1.0,
            "projectile_bounce": False,
            "projectile_pierce": False,
            "custom_school_name": "",
            "custom_school_color": "",
            "custom_school_description": "",
            "created_date": "",
            "author": "CFF Extractor"
        }
        
        extracted_spells.append(spell_data)
        print(f"Extracted spell: {spell_data['spell_name']} (ID: {spell_data['spell_line_id']})")
    
    return extracted_spells


def determine_magic_school(spell) -> int:
    """
    Determine magic school from the spell's requirements.
    The req1_class, req2_class, req3_class fields contain School enum values.
    """
    # Get the primary class requirement
    primary_school = spell.req1_class
    
    # Map to SpellForge magic school values (these match the MagicSchool enum)
    school_mapping = {
        School.WHITE_MAGIC: 0,  # WHITE
        School.FIRE: 1,         # FIRE
        School.ICE: 2,          # ICE
        School.BLACK_MAGIC: 3,  # BLACK
        School.MIND_MAGIC: 4,   # MENTAL
        School.ELEMENTAL_MAGIC: 5,  # EARTH (in SpellForge, EARTH represents general elemental)
        School.LIFE: 0,         # WHITE
        School.NATURE: 0,       # WHITE
        School.BOONS: 0,        # WHITE
        School.DEATH: 3,        # BLACK
        School.NECROMANCY: 3,   # BLACK
        School.CURSE: 3,        # BLACK
        School.ENCHANTMENT: 4,  # MENTAL
        School.OFFENSIVE: 4,    # MENTAL
        School.DEFENSIVE: 4,    # MENTAL
    }
    
    return school_mapping.get(primary_school, 1)  # Default to FIRE


def determine_spell_type(spell, spell_name) -> str:
    """Determine spell type based on properties"""
    # Check if it's an aura spell
    if spell.cast_type == 258:
        return "buff"  # Auras are buffs
    
    # Check if it's an area spell
    if spell.cast_type == 1025:
        return "aoe"
    
    # Check name for healing indicators
    name = getattr(spell_name, 'name', '').lower()
    if any(heal_word in name for heal_word in ['heal', 'cure', 'restore', 'renew']):
        return "heal"
    
    # Check for summon indicators
    if any(summon_word in name for summon_word in ['summon', 'call', 'conjure', 'sum']):
        return "summon"
    
    # Check for buff/debuff indicators
    if any(buff_word in name for buff_word in ['aura', 'bless', 'enchant', 'buff']):
        return "buff"
    
    if any(debuff_word in name for debuff_word in ['curse', 'debuff', 'weak', 'slow']):
        return "debuff"
    
    # Default to attack for most offensive spells
    return "attack"


def determine_target_type(cast_type: int) -> str:
    """Determine target type based on cast type"""
    # Based on common patterns in SpellForce
    if cast_type == 258:  # aura spells
        return "self"
    elif cast_type == 1025:  # area spells
        return "aoe"
    else:
        return "single"


def has_projectile(spell, spell_name) -> bool:
    """Determine if spell has projectile based on name or properties"""
    name = getattr(spell_name, 'name', '').lower()
    # Heuristic: spells with certain names likely have projectiles
    projectile_names = ['ball', 'bolt', 'arrow', 'missile', 'dart', 'blast', 'fire', 'ice', 'lightning']
    return any(proj_name in name for proj_name in projectile_names)


def get_special_effects(spell) -> list:
    """Get special effects from spell effects"""
    # This would require analyzing the spell's effect list
    # For now, return empty list; could be expanded with more analysis
    return []


def create_spell_levels(spell) -> list:
    """
    Create spell level data based on the single spell entry.
    This creates 15 levels with scaling based on the base spell parameters.
    """
    base_damage = (spell.p1 + spell.p2) // 2 if spell.p1 > 0 or spell.p2 > 0 else 10
    
    levels = []
    for level in range(1, 16):
        # Simple scaling based on level
        level_damage = int(base_damage * (1 + (level - 1) * 0.15))  # 15% increase per level
        
        level_data = {
            "level": level,
            "damage_min": level_damage,
            "damage_max": level_damage,
            "mana_cost": int(spell.mana * (1 + (level - 1) * 0.05)),  # 5% increase per level
            "cooldown": spell.cooldown / 1000.0,  # Convert from milliseconds to seconds
            "cast_time": spell.cast_time / 1000.0,  # Convert from milliseconds to seconds
            "range": spell.max_range if spell.max_range > 0 else 20.0,
            "aoe_radius": 0.0,
            "duration": 0.0
        }
        
        levels.append(level_data)
    
    return levels


def save_extracted_spells(spells_data, output_dir: str = "extracted_spells"):
    """Save extracted spells to JSON files"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save all spells to one file
    all_spells_file = output_path / "all_cff_spells.json"
    with open(all_spells_file, 'w', encoding='utf-8') as f:
        json.dump(spells_data, f, indent=2)
    
    print(f"Saved all {len(spells_data)} spells to {all_spells_file}")
    
    # Save individual spells
    for spell_data in spells_data:
        spell_id = spell_data["spell_line_id"]
        spell_name = spell_data["spell_name"].replace(" ", "_").replace("/", "_").replace("\\", "_")
        spell_file = output_path / f"spell_{spell_id}_{spell_name.lower()}.json"
        
        with open(spell_file, 'w', encoding='utf-8') as f:
            json.dump([spell_data], f, indent=2)
    
    print(f"Saved {len(spells_data)} individual spell files to {output_path}")


def main():
    """Main function to extract spell data from CFF file"""
    # Default path for GameData.cff - adjust this as needed
    cff_file_path = Path(__file__).parent.parent.parent.parent.parent / "OriginalGameFiles" / "data" / "GameData.cff"
    
    if not cff_file_path.exists():
        print(f"GameData.cff file not found at: {cff_file_path}")
        print("Please place the GameData.cff file in the OriginalGameFiles/data/ directory")
        return
    
    try:
        print("Starting spell data extraction...")
        extracted_spells = extract_spell_data_from_cff(str(cff_file_path))
        
        print(f"\nExtraction complete! Extracted {len(extracted_spells)} spells.")
        
        # Save the extracted spells
        save_extracted_spells(extracted_spells)
        
        print("\nSpell data extraction completed successfully!")
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
