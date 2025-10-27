#!/usr/bin/env python3
"""
Test script for the SpellForce Spell Creation System
"""

import sys
import os

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_spell_creation_system():
    """Test the complete spell creation workflow"""

    print("🧙 Testing SpellForce Spell Creation System")
    print("=" * 50)

    try:
        # Import our modules
        from TirganachReloaded.cff_editor.models import (
            SpellCreationData, MagicSchool, SpellType, TargetType, ScalingMode, SpellLevel
        )
        from TirganachReloaded.cff_editor.exporters.spell_lua_exporter import SpellLuaExporter, SpellValidator

        print("✅ Imports successful")

        # Create a test spell
        print("\n📝 Creating test spell...")

        spell_data = SpellCreationData(
            spell_name="Test Inferno Blast",
            internal_name="TestInfernoBlast",
            magic_school=MagicSchool.FIRE,
            spell_type=SpellType.ATTACK,
            description="A powerful fireball that burns enemies",
            target_type=TargetType.SINGLE,
            has_projectile=True,
            base_range=25.0,
            aoe_radius=0.0,
            duration=0.0,
            special_effects=["burn", "stun"],
            num_levels=10,
            scaling_mode=ScalingMode.EXPONENTIAL,
            vfx_cast="CastFire",
            vfx_projectile="ProjectileFireBall",
            vfx_resolve="ResolveFireExplosion",
            vfx_target="TargetBurn",
            vfx_overtime="",
            sfx_cast="spell_fire_cast",
            sfx_projectile="",
            sfx_resolve="spell_hit_fireburst",
            sfx_hit="spell_hit_explosion",
            spell_line_id=301,
            created_date="2025-01-01 12:00:00",
            author="Spell Wizard Test"
        )

        print(f"✅ Created spell: {spell_data.spell_name}")
        print(f"   Internal name: {spell_data.internal_name}")
        print(f"   School: {spell_data.magic_school.name}")
        print(f"   Type: {spell_data.spell_type.value}")

        # Apply scaling
        print("\n📊 Applying level scaling...")
        spell_data.apply_scaling()

        print("✅ Scaling applied. Level stats:")
        for i, level in enumerate(spell_data.levels[:5]):  # Show first 5 levels
            print(f"   Level {level.level}: {level.damage_min}-{level.damage_max} dmg, {level.mana_cost} mana")

        if len(spell_data.levels) > 5:
            last_level = spell_data.levels[-1]
            print(f"   ... Level {last_level.level}: {last_level.damage_min}-{last_level.damage_max} dmg, {last_level.mana_cost} mana")

        # Validate spell
        print("\n🔍 Validating spell...")
        validator = SpellValidator()
        errors, warnings = validator.validate(spell_data)

        print(f"✅ Validation complete:")
        print(f"   Errors: {len(errors)}")
        for error in errors:
            print(f"     ❌ {error}")

        print(f"   Warnings: {len(warnings)}")
        for warning in warnings:
            print(f"     ⚠️  {warning}")

        # Get balance score
        balance = validator.get_balance_score(spell_data)
        print("\n⚖️  Balance analysis:")
        print(f"   Damage per Mana: {balance['damage_per_mana']}")
        print(f"   Damage per Second: {balance['damage_per_second']}")
        print(f"   Power Rating: {balance['power_rating']} ({balance['balance_category']})")

        # Export to Lua
        print("\n💾 Exporting to Lua scripts...")
        exporter = SpellLuaExporter("test_spell_export")
        exported_files = exporter.export_to_files(spell_data)

        print(f"✅ Export complete. Generated {len(exported_files)} files:")
        for file_path in exported_files:
            file_size = os.path.getsize(file_path)
            print(f"   📄 {os.path.basename(file_path)} ({file_size} bytes)")

        # Show sample content
        print("\n📖 Sample generated content:")
        if exported_files:
            sample_file = exported_files[0]  # First file
            print(f"\n--- Content of {os.path.basename(sample_file)} ---")
            with open(sample_file, 'r') as f:
                lines = f.readlines()[:10]  # First 10 lines
                for line in lines:
                    print(line.rstrip())
            if len(lines) == 10:
                print("... (truncated)")
            print("--- End sample ---\n")

        print("🎉 Spell creation test completed successfully!")
        print("\nNext steps:")
        print("1. Integrate the wizard into the main application")
        print("2. Add visual effects page with templates")
        print("3. Add sound effects browser")
        print("4. Test with actual SpellForce game files")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_components():
    """Test GUI components (requires display)"""
    print("\n🖥️  GUI Component Test")
    print("-" * 30)

    try:
        # Only test if we have a display
        if os.environ.get('DISPLAY') or sys.platform == 'win32':
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)

            # Test imports
            from TirganachReloaded.cff_editor.widgets.spell_creator_wizard import SpellCreatorWizard
            from TirganachReloaded.cff_editor.widgets.level_editor_dialog import LevelEditorDialog

            print("✅ GUI imports successful")
            print("✅ Wizard and dialog classes available")

            # Don't actually show GUI in automated test
            print("ℹ️  GUI components ready (not displayed in automated test)")

        else:
            print("ℹ️  No display available, skipping GUI test")

        return True

    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False


if __name__ == "__main__":
    print("SpellForce Spell Creation System - Test Suite")
    print("=" * 55)

    success = True

    # Test core functionality
    success &= test_spell_creation_system()

    # Test GUI components
    success &= test_gui_components()

    print("\n" + "=" * 55)
    if success:
        print("🎊 ALL TESTS PASSED! Spell creation system is ready.")
        sys.exit(0)
    else:
        print("💥 SOME TESTS FAILED. Please check the errors above.")
        sys.exit(1)