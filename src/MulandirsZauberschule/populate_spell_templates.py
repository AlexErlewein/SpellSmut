"""
Populate custom_spells with template spells

This script loads spell templates from TirganachReloaded and saves them
to the custom_spells directory so they appear in the spell browser.
"""

import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

import json
from pathlib import Path
import sys

try:
    from TirganachReloaded.cff_editor.models.spell_templates import (
        FireballTemplate,
        IceBlastTemplate,
        HolyHealTemplate,
        ChainLightningTemplate,
        RegenerationAuraTemplate,
        SummonWolfTemplate
    )
    from TirganachReloaded.cff_editor.models.spell_creation_data import SpellCreationData
except ImportError as e:
    print(f"Error importing templates: {e}")
    sys.exit(1)


def populate_template_spells():
    """Create template spells and save to custom_spells directory"""
    print("="*60)
    print("    POPULATING SPELL TEMPLATES")
    print("="*60)

    # Create custom_spells directory
    spells_dir = Path(__file__).parent / 'custom_spells'
    spells_dir.mkdir(exist_ok=True)

    individual_dir = spells_dir / 'individual'
    individual_dir.mkdir(exist_ok=True)

    # Create all template spells
    templates = [
        ("Fireball", FireballTemplate()),
        ("Ice Blast", IceBlastTemplate()),
        ("Holy Heal", HolyHealTemplate()),
        ("Chain Lightning", ChainLightningTemplate()),
        ("Regeneration Aura", RegenerationAuraTemplate()),
        ("Summon Wolf", SummonWolfTemplate()),
    ]

    all_spells = []

    for name, template in templates:
        print(f"\nCreating template: {name}")
        spell = template.create_spell()

        # Convert to dict
        spell_dict = spell.to_dict()

        # Show stats
        print(f"  ID: {spell.spell_line_id}")
        print(f"  School: {spell.magic_school.name}")
        print(f"  Type: {spell.spell_type.value}")
        print(f"  Levels: {spell.num_levels}")
        if spell.levels:
            print(f"  Level 1 DPS: {spell.levels[0].dps:.1f}")
            print(f"  Level {spell.num_levels} DPS: {spell.levels[-1].dps:.1f}")

        all_spells.append(spell_dict)

        # Save individual file
        safe_name = spell.internal_name.lower().replace(" ", "_")
        individual_file = individual_dir / f"spell_{spell.spell_line_id}_{safe_name}.json"

        with open(individual_file, 'w', encoding='utf-8') as f:
            json.dump(spell_dict, f, indent=2)

        print(f"  ✓ Saved to {individual_file.name}")

    # Load and add original game spells from extracted CFF data
    print(f"\nLoading original game spells from CFF extraction...")
    cff_spells_dir = Path(__file__).parent.parent.parent / "extracted_spells"  # Changed to match actual location
    
    if cff_spells_dir.exists():
        # Load the all_cff_spells.json file
        all_cff_spells_file = cff_spells_dir / "all_cff_spells.json"
        if all_cff_spells_file.exists():
            with open(all_cff_spells_file, 'r', encoding='utf-8') as f:
                cff_spells = json.load(f)
            
            print(f"  Found {len(cff_spells)} original game spells from CFF extraction")
            
            # Add CFF spells to all_spells list (with IDs adjusted to start from 1000 to avoid conflicts)
            for spell_data in cff_spells:
                # Create a SpellCreationData object from the CFF spell data
                cff_spell = SpellCreationData.from_dict(spell_data)
                
                # Adjust ID to avoid conflicts with template spells (300+) and custom spells
                # Use original CFF ID if it's in the game range (1-999), otherwise keep it
                if 1 <= cff_spell.spell_line_id <= 999:
                    cff_spell.spell_line_id += 1000  # Shift to 1000+ range to avoid conflicts
                
                # Update the spell data
                cff_spell_dict = cff_spell.to_dict()
                
                # Add to all spells
                all_spells.append(cff_spell_dict)
                
                # Save individual file for CFF spell
                safe_name = cff_spell.internal_name.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
                individual_file = individual_dir / f"spell_{cff_spell.spell_line_id}_{safe_name}.json"

                with open(individual_file, 'w', encoding='utf-8') as f:
                    json.dump([cff_spell_dict], f, indent=2)  # Save as single-element array for consistency

                print(f"  ✓ Added CFF spell: {cff_spell.spell_name} (ID: {cff_spell.spell_line_id})")
        else:
            print(f"  Warning: {all_cff_spells_file} not found. Original game spells will not be loaded.")
    else:
        print(f"  Warning: CFF extracted spells directory not found at {cff_spells_dir}. Original game spells will not be loaded.")

    # Save all spells to main file
    spells_file = spells_dir / 'spells.json'

    with open(spells_file, 'w', encoding='utf-8') as f:
        json.dump(all_spells, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✓ Successfully created {len(all_spells)} total spells")
    print(f"✓ Saved to {spells_file}")
    print(f"{'='*60}")

    # Show summary table
    print("\nTemplate Spells Summary:")
    print(f"{'ID':<6} {'Name':<25} {'School':<12} {'Type':<12} {'Max DPS':<10}")
    print("-"*70)

    for spell_dict in sorted(all_spells, key=lambda x: x['spell_line_id'])[:10]:  # Show first 10 spells
        spell_id = spell_dict['spell_line_id']
        name = spell_dict['spell_name']
        school = spell_dict['magic_school']
        spell_type = spell_dict['spell_type']

        # Calculate DPS from last level
        max_dps = 0
        if spell_dict['levels']:
            last_level = spell_dict['levels'][-1]
            avg_damage = (last_level['damage_min'] + last_level['damage_max']) / 2
            effective_cast_time = last_level['cast_time'] + last_level['cooldown']
            max_dps = avg_damage / effective_cast_time if effective_cast_time > 0 else 0

        school_names = {0: 'WHITE', 1: 'FIRE', 2: 'ICE', 3: 'BLACK', 4: 'MENTAL', 5: 'EARTH'}
        school_name = school_names.get(school, str(school))

        print(f"{spell_id:<6} {name:<25} {school_name:<12} {spell_type:<12} {max_dps:<10.1f}")

    if len(all_spells) > 10:
        print(f"... and {len(all_spells) - 10} more spells")
    
    print("-"*70)
    print(f"\nTotal spells available: {len(all_spells)}")
    print("You can now browse all spells (templates + original game) in the Spell Forge!")
    print("Run: python spell_forge_wizard.py")


if __name__ == "__main__":
    try:
        populate_template_spells()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
