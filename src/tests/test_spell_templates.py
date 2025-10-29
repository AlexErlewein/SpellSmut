#!/usr/bin/env python3
"""
Test script for Spell Template System
"""

import os
import sys
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Define test output directory
TEST_OUTPUT_DIR = Path(__file__).parent / "test_outputs" / "test_template_export"


def test_spell_templates():
    """Test the spell template system"""

    print("🧙 Testing SpellForce Spell Templates")
    print("=" * 45)

    try:
        # Import our modules
        from TirganachReloaded.cff_editor.exporters.spell_lua_exporter import (
            SpellLuaExporter,
        )
        from TirganachReloaded.cff_editor.models.spell_templates import (
            SpellTemplateLibrary,
            get_available_templates,
            get_spell_template,
        )

        print("✅ Template imports successful")

        # Test template library
        print("\n📚 Testing template library...")
        library = SpellTemplateLibrary()
        templates = library.get_all_templates()

        print(f"✅ Loaded {len(templates)} spell templates:")
        for template_id, template in templates.items():
            print(f"   • {template.name} ({template.template_type.value})")

        # Test getting available templates for UI
        print("\n📋 Available templates for UI:")
        available = get_available_templates()
        for template in available:
            print(f"   • {template['name']}: {template['description']}")

        # Test creating a spell from template
        print("\n🔥 Testing Fireball template...")
        fireball_spell = get_spell_template("fireball")

        if fireball_spell:
            print("✅ Created fireball spell from template:")
            print(f"   Name: {fireball_spell.spell_name}")
            print(f"   School: {fireball_spell.magic_school.name}")
            print(f"   Type: {fireball_spell.spell_type.value}")
            print(f"   Levels: {fireball_spell.num_levels}")

            # Show level 1 and max level stats
            level_1 = fireball_spell.levels[0]
            level_15 = fireball_spell.levels[-1]
            print(
                f"   Level 1: {level_1.damage_min}-{level_1.damage_max} dmg, {level_1.mana_cost} mana"
            )
            print(
                f"   Level 15: {level_15.damage_min}-{level_15.damage_max} dmg, {level_15.mana_cost} mana"
            )

            # Export the template spell
            print("\n💾 Exporting template spell...")
            # Ensure output directory exists
            TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            exporter = SpellLuaExporter(str(TEST_OUTPUT_DIR))
            exported_files = exporter.export_to_files(fireball_spell)

            print(
                f"✅ Template export complete. Generated {len(exported_files)} files:"
            )
            for file_path in exported_files:
                file_size = os.path.getsize(file_path)
                print(f"   📄 {os.path.basename(file_path)} ({file_size} bytes)")

        else:
            print("❌ Failed to create fireball spell from template")
            return False

        # Test another template
        print("\n💚 Testing Regeneration Aura template...")
        regen_spell = get_spell_template("regeneration_aura")

        if regen_spell:
            print("✅ Created regeneration aura from template:")
            print(f"   Name: {regen_spell.spell_name}")
            print(f"   Type: {regen_spell.spell_type.value}")
            print(f"   Duration: {regen_spell.duration} seconds")

            level_10 = regen_spell.levels[9]  # Level 10
            print(
                f"   Level 10: {level_10.damage_min} HP/sec regen, {level_10.mana_cost} mana, {level_10.duration}s duration"
            )

        # Test template filtering
        print("\n🔍 Testing template filtering...")
        attack_templates = library.get_templates_by_type(fireball_spell.spell_type)
        print(f"✅ Found {len(attack_templates)} attack spell templates")

        heal_templates = library.get_templates_by_type(regen_spell.spell_type)
        print(f"✅ Found {len(heal_templates)} buff spell templates")

        print("\n🎉 Template system test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Template test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("SpellForce Spell Templates - Test Suite")
    print("=" * 42)

    success = test_spell_templates()

    print("\n" + "=" * 42)
    if success:
        print("🎊 TEMPLATE TESTS PASSED!")
    else:
        print("💥 TEMPLATE TESTS FAILED!")
        sys.exit(1)
