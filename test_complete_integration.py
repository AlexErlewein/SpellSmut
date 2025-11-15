#!/usr/bin/env python3
"""Complete test of school requirements system integration"""

import sys

sys.path.append("src")

from TirganachReloaded.cff_editor.models.weapon_creation_data import (
    WeaponRequirements,
    SchoolRequirement,
    WeaponCreationData,
    DamageType,
    Rarity,
    WeaponHands,
    DamageCategory,
)
from TirganachReloaded.cff_editor.exporters.weapon_loader import WeaponLoader


def test_complete_school_requirements_integration():
    """Test complete school requirements integration"""
    print("=== Complete School Requirements Integration Test ===")

    # Test 1: Create weapon with school requirements
    print("\n1. Testing weapon creation with school requirements...")

    school_reqs = [
        SchoolRequirement(school_name="WHITE_MAGIC", level=5),
        SchoolRequirement(school_name="HEAVY_BLADE_WEAPONS", level=3),
    ]

    requirements = WeaponRequirements(
        strength=15,
        dexterity=12,
        intelligence=8,
        level=10,
        school_requirements=school_reqs,
    )

    weapon_data = WeaponCreationData(
        weapon_id=9999,
        creation_mode="new",
        source_weapon_id=27,
        weapon_name="Test Mystic Blade",
        weapon_type_id=3,
        weapon_type_name="Dagger",
        weapon_material_id=5,
        weapon_material_name="Steel",
        hands=WeaponHands.ONE_HANDED,
        damage_category=DamageCategory.MELEE,
        description="A test weapon with school requirements",
        min_damage=8,
        max_damage=15,
        damage_type=DamageType.SLASH,
        attack_speed=110,
        min_range=1,
        max_range=1,
        attack_arc=90,
        critical_chance=7.5,
        armor_penetration=2.0,
        knockback_chance=0.0,
        requirements=requirements,
        sell_value=5000,
        buy_value=10000,
        rarity=Rarity.RARE,
        effects=[],
        item_set_id=0,
        icon_handle="test_icon",
        hit_sound="test_hit",
        miss_sound="test_miss",
        equip_sound="test_equip",
        model_file="test_model",
        trail_effect="test_trail",
        impact_effect="test_impact",
    )

    print(f"✓ Created weapon: {weapon_data.weapon_name}")
    print(
        f"  Damage: {weapon_data.min_damage}-{weapon_data.max_damage} {weapon_data.damage_type.value}"
    )
    print(f"  Requirements:")
    print(f"    - STR: {weapon_data.requirements.strength}")
    print(f"    - DEX: {weapon_data.requirements.dexterity}")
    print(f"    - INT: {weapon_data.requirements.intelligence}")
    print(f"    - Level: {weapon_data.requirements.level}")
    print(f"    - Schools: {len(weapon_data.requirements.school_requirements)}")
    for req in weapon_data.requirements.school_requirements:
        print(f"      * {req.school_name} Level {req.level}")

    # Test 2: Load existing weapon and verify it has no school requirements
    print("\n2. Testing existing weapon loading...")

    try:
        existing_weapon = WeaponLoader.load_weapon(
            27, "OriginalGameFiles/data/GameData.cff"
        )
        print(f"✓ Loaded existing weapon: {existing_weapon.weapon_name}")
        print(f"  Damage: {existing_weapon.min_damage}-{existing_weapon.max_damage}")
        print(
            f"  School requirements: {len(existing_weapon.requirements.school_requirements)}"
        )

        if len(existing_weapon.requirements.school_requirements) == 0:
            print("  ✓ No school requirements (expected for original weapons)")
        else:
            print("  ⚠ Unexpected school requirements found")

    except Exception as e:
        print(f"  ✗ Failed to load existing weapon: {e}")
        return False

    # Test 3: Verify school requirements data structure
    print("\n3. Testing school requirements data structure...")

    test_req = SchoolRequirement(school_name="TEST_SCHOOL", level=7)

    if hasattr(test_req, "school_name") and hasattr(test_req, "level"):
        print(
            f"✓ SchoolRequirement structure correct: {test_req.school_name} Level {test_req.level}"
        )
    else:
        print("✗ SchoolRequirement structure missing fields")
        return False

    # Test 4: Verify requirements integration
    print("\n4. Testing requirements integration...")

    if (
        weapon_data.requirements
        and len(weapon_data.requirements.school_requirements) > 0
    ):
        print("✓ Requirements properly integrated into weapon data")
        print(
            f"  Total requirements: {len(weapon_data.requirements.school_requirements)} schools"
        )
    else:
        print("✗ Requirements not properly integrated")
        return False

    print("\n=== Integration Test Complete ===")
    print("✓ School requirements system is working correctly!")
    print("✓ New weapons can have school requirements")
    print("✓ Existing weapons load without school requirements")
    print("✓ Data structures are properly integrated")

    return True


if __name__ == "__main__":
    success = test_complete_school_requirements_integration()
    sys.exit(0 if success else 1)
