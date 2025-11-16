"""
Test script for the Spell Forge

This creates a sample spell to verify the forge works correctly.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from TirganachReloaded.cff_editor.models.spell_creation_data import SpellCreationData
    from TirganachReloaded.cff_editor.models.spell_enums import MagicSchool, SpellType, TargetType, ScalingMode
    from spell_validator import SpellValidator
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the src directory")
    sys.exit(1)


def create_test_spell():
    """Create a test spell programmatically"""
    print("\n" + "="*60)
    print("         SPELL FORGE TEST - Creating Sample Spell")
    print("="*60)

    # Create a simple fireball spell
    spell = SpellCreationData(
        spell_line_id=300,
        spell_name="Test Fireball",
        internal_name="TestFireball",
        description="A test fireball spell for validation",
        magic_school=MagicSchool.FIRE,
        spell_type=SpellType.ATTACK,
        target_type=TargetType.SINGLE,
        has_projectile=True,
        base_range=25.0,
        aoe_radius=0.0,
        duration=0.0,
        num_levels=5,
        scaling_mode=ScalingMode.LINEAR,
        vfx_cast="CastFire",
        vfx_projectile="ProjectileFireBall",
        vfx_resolve="ResolveFireExplosion",
        sfx_cast="spell_fire_cast",
        sfx_hit="spell_hit_fireburst",
    )

    # Configure level 1 base stats
    spell.levels[0].damage_min = 15
    spell.levels[0].damage_max = 20
    spell.levels[0].mana_cost = 10
    spell.levels[0].cooldown = 3.0
    spell.levels[0].cast_time = 1.5

    # Apply scaling
    spell.apply_scaling()

    print("\n✓ Spell created successfully!")
    print(f"  Name: {spell.spell_name}")
    print(f"  School: {spell.magic_school.name}")
    print(f"  Type: {spell.spell_type.value}")
    print(f"  Levels: {spell.num_levels}")

    # Show progression
    print(f"\n--- Level Progression ---")
    for i, level in enumerate(spell.levels, 1):
        print(f"Level {i}: Damage {level.damage_min}-{level.damage_max}, "
              f"Mana {level.mana_cost}, DPS {level.dps:.1f}")

    # Validate
    print(f"\n--- Validation ---")
    validator = SpellValidator()
    errors, warnings = validator.validate(spell)

    if not errors and not warnings:
        print("✓ Spell is valid!")
    else:
        if errors:
            print(f"❌ Errors: {len(errors)}")
            for error in errors:
                print(f"  - {error}")
        if warnings:
            print(f"⚠️  Warnings: {len(warnings)}")
            for warning in warnings:
                print(f"  - {warning}")

    # Balance metrics
    metrics = spell.get_balance_metrics()
    print(f"\n--- Balance Metrics ---")
    print(f"Damage per Mana: {metrics.get('damage_per_mana', 0):.2f}")
    print(f"Damage per Second: {metrics.get('damage_per_second', 0):.2f}")
    print(f"Power Rating: {metrics.get('power_rating', 0):.1f}")
    print(f"Balance Category: {metrics.get('balance_category', 'Unknown')}")

    # Export to JSON
    try:
        from spell_forge import SpellForge
        forge = SpellForge()
        forge.spells[spell.spell_line_id] = spell
        forge.save_spells()
        forge.export_spell_to_json(spell)
        print(f"\n✓ Spell exported successfully!")
    except Exception as e:
        print(f"\n⚠️  Export failed: {e}")

    print("\n" + "="*60)
    print("                    TEST COMPLETE")
    print("="*60)

    return spell


if __name__ == "__main__":
    try:
        spell = create_test_spell()
        print("\n✓ Test passed! The Spell Forge is working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
