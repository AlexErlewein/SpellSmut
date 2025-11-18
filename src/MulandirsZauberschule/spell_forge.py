"""
The Spell Forge - Standalone Spell Creation System

This module implements a multi-phase spell creation system allowing users to create
custom spells with full customization including schools, levels, visual effects,
and browser capabilities.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import spell models from TirganachReloaded
try:
    from TirganachReloaded.cff_editor.models.spell_templates import (
        FireballTemplate,
        IceBlastTemplate,
        HolyHealTemplate,
        ChainLightningTemplate,
        RegenerationAuraTemplate,
        SummonWolfTemplate
    )
except ImportError as e:
    print(f"Error importing templates: {e}")
    sys.exit(1)

# Import validator
try:
    from spell_validator import SpellValidator
except ImportError:
    print("Warning: Could not import spell validator")
    SpellValidator = None


class SpellForge:
    """
    The Spell Forge - Multi-Phase Spell Creation System
    """

    def __init__(self):
        self.spells_file = Path(__file__).parent / 'custom_spells' / 'spells.json'
        self.spells_file.parent.mkdir(exist_ok=True)
        self.spells = self.load_spells()

    def load_spells(self) -> Dict[int, SpellCreationData]:
        """Load existing spells from the spells.json file"""
        spells = {}
        if self.spells_file.exists():
            try:
                with open(self.spells_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for spell_data in data:
                        spell = SpellCreationData.from_dict(spell_data)
                        spells[spell.spell_line_id] = spell
            except Exception as e:
                print(f"Error loading spells: {e}")
        return spells

    def save_spells(self):
        """Save all spells to the spells.json file"""
        try:
            spells_list = [spell.to_dict() for spell in self.spells.values()]
            with open(self.spells_file, 'w', encoding='utf-8') as f:
                json.dump(spells_list, f, indent=2)
        except Exception as e:
            print(f"Error saving spells: {e}")

    def get_available_id(self) -> int:
        """Get the next available ID in the spell range (300+)"""
        if not self.spells:
            return 300
        max_id = max(self.spells.keys())
        return max_id + 1

    def create_new_spell(self) -> SpellCreationData:
        """Phase 1: Create a new spell with auto-assigned ID"""
        new_id = self.get_available_id()
        spell = SpellCreationData(spell_line_id=new_id)
        return spell

    def edit_existing_spell(self, spell_id: int) -> Optional[SpellCreationData]:
        """Phase 1: Load an existing spell for editing"""
        return self.spells.get(spell_id)

    def duplicate_spell(self, spell_id: int) -> Optional[SpellCreationData]:
        """Phase 1: Create a duplicate of an existing spell"""
        original = self.spells.get(spell_id)
        if original:
            new_id = self.get_available_id()
            # Create a copy with new ID
            spell_dict = original.to_dict()
            spell_dict['spell_line_id'] = new_id
            spell_dict['spell_name'] = f"{original.spell_name} (Copy)"
            new_spell = SpellCreationData.from_dict(spell_dict)
            return new_spell
        return None

    def browse_spells(self, filter_school: Optional[str] = None, filter_type: Optional[str] = None, search_name: Optional[str] = None) -> Optional[int]:
        """
        Browse available spells with advanced filtering

        Args:
            filter_school: Filter by magic school name
            filter_type: Filter by spell type
            search_name: Search by spell name (partial match)
        """
        if not self.spells:
            print("\nNo spells available to browse.")
            return None

        # Apply filters
        filtered_spells = {}
        for spell_id, spell in self.spells.items():
            # School filter
            if filter_school:
                school_name = spell.magic_school.name if hasattr(spell.magic_school, 'name') else str(spell.magic_school)
                if filter_school.upper() not in school_name.upper():
                    continue

            # Type filter
            if filter_type:
                spell_type = spell.spell_type.value if hasattr(spell.spell_type, 'value') else str(spell.spell_type)
                if filter_type.upper() not in spell_type.upper():
                    continue

            # Name search
            if search_name:
                if search_name.lower() not in spell.spell_name.lower():
                    continue

            filtered_spells[spell_id] = spell

        if not filtered_spells:
            print("\nNo spells match the current filters.")
            return None

        print("\n" + "="*80)
        print("                          SPELL BROWSER")
        if filter_school or filter_type or search_name:
            filters = []
            if filter_school:
                filters.append(f"School: {filter_school}")
            if filter_type:
                filters.append(f"Type: {filter_type}")
            if search_name:
                filters.append(f"Name: {search_name}")
            print(f"                    Filters: {', '.join(filters)}")
        print("="*80)
        print(f"\n{'ID':<6} {'Name':<30} {'School':<15} {'Type':<12} {'Levels':<8} {'DPS':<8}")
        print("-"*80)

        for spell_id, spell in sorted(filtered_spells.items()):
            school_name = spell.magic_school.name if hasattr(spell.magic_school, 'name') else str(spell.magic_school)
            spell_type = spell.spell_type.value if hasattr(spell.spell_type, 'value') else str(spell.spell_type)
            max_dps = spell.levels[-1].dps if spell.levels else 0
            print(f"{spell_id:<6} {spell.spell_name[:28]:<30} {school_name[:13]:<15} {spell_type[:10]:<12} {spell.num_levels:<8} {max_dps:<8.1f}")

        print("-"*80)
        print(f"Total: {len(filtered_spells)} spells")
        print("\nOptions:")
        print("  - Enter spell ID to select")
        print("  - Type 'filter' to change filters")
        print("  - Type 'clear' to clear filters")
        print("  - Type 'back' to cancel")

        while True:
            try:
                choice = input("\nYour choice: ").strip()

                if choice.lower() == 'back':
                    return None

                elif choice.lower() == 'filter':
                    # Interactive filter menu
                    print("\n--- Filter Options ---")
                    new_school = input("Filter by School (or Enter to skip): ").strip() or None
                    new_type = input("Filter by Type (or Enter to skip): ").strip() or None
                    new_search = input("Search by Name (or Enter to skip): ").strip() or None
                    return self.browse_spells(new_school, new_type, new_search)

                elif choice.lower() == 'clear':
                    return self.browse_spells()

                else:
                    spell_id = int(choice)
                    if spell_id in filtered_spells:
                        # Show spell details before selection
                        self.show_spell_details(filtered_spells[spell_id])
                        confirm = input("\nSelect this spell? (y/n): ").strip().lower()
                        if confirm == 'y':
                            return spell_id
                    else:
                        print(f"Spell ID {spell_id} not found in filtered results. Please try again.")

            except ValueError:
                print("Invalid input. Please enter a numeric ID or a valid command.")

    def show_spell_details(self, spell: SpellCreationData):
        """Display detailed information about a spell"""
        print("\n" + "="*60)
        print(f"  {spell.spell_name} (ID: {spell.spell_line_id})")
        print("="*60)
        print(f"School: {spell.magic_school.name}")
        print(f"Type: {spell.spell_type.value}")
        print(f"Target: {spell.target_type.value}")
        print(f"Range: {spell.base_range}")
        print(f"Projectile: {'Yes' if spell.has_projectile else 'No'}")
        print(f"AOE Radius: {spell.aoe_radius}")
        print(f"Levels: {spell.num_levels}")

        if spell.levels:
            print(f"\nLevel 1: Damage {spell.levels[0].damage_min}-{spell.levels[0].damage_max}, "
                  f"Mana {spell.levels[0].mana_cost}, DPS {spell.levels[0].dps:.1f}")
            if len(spell.levels) > 1:
                max_lvl = spell.levels[-1]
                print(f"Level {spell.num_levels}: Damage {max_lvl.damage_min}-{max_lvl.damage_max}, "
                      f"Mana {max_lvl.mana_cost}, DPS {max_lvl.dps:.1f}")

        print(f"\nDescription: {spell.description or 'No description'}")
        print("="*60)

    def phase1_mode_selection(self) -> tuple[str, int, Optional[SpellCreationData]]:
        """
        Phase 1: Mode Selection & ID Assignment

        Returns:
            - mode: 'create_new', 'edit_existing', or 'duplicate'
            - chosen_id: selected ID for the spell
            - spell: the spell object to work with
        """
        print("\n" + "="*60)
        print("              THE SPELL FORGE - PHASE 1")
        print("            Mode Selection & ID Assignment")
        print("="*60)

        print("\nChoose an operation mode:")
        print("1. Create New Spell")
        print("2. Edit Existing Spell")
        print("3. Duplicate Existing Spell")
        print("4. Browse Spells")

        while True:
            try:
                choice = input("\nEnter your choice (1-4): ").strip()
                if choice in ['1', '2', '3', '4']:
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, 3, or 4.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return None, None, None

        if choice == '1':
            # Create new spell
            spell = self.create_new_spell()
            print(f"\nNew spell created with ID: {spell.spell_line_id}")
            return 'create_new', spell.spell_line_id, spell

        elif choice == '2':
            # Edit existing spell
            spell_id = self.browse_spells()
            if spell_id is None:
                return None, None, None

            spell = self.edit_existing_spell(spell_id)
            if spell:
                print(f"Editing spell: {spell.spell_name} (ID: {spell.spell_line_id})")
                return 'edit_existing', spell_id, spell
            else:
                print(f"No spell found with ID {spell_id}")
                return None, None, None

        elif choice == '3':
            # Duplicate existing spell
            spell_id = self.browse_spells()
            if spell_id is None:
                return None, None, None

            spell = self.duplicate_spell(spell_id)
            if spell:
                print(f"Duplicating spell: {self.spells[spell_id].spell_name}")
                print(f"New spell created with ID: {spell.spell_line_id}")
                return 'duplicate', spell.spell_line_id, spell
            else:
                print(f"No spell found with ID {spell_id}")
                return None, None, None

        elif choice == '4':
            # Just browse
            self.browse_spells()
            return self.phase1_mode_selection()

        return None, None, None

    def phase2_basic_properties(self, spell: SpellCreationData) -> SpellCreationData:
        """
        Phase 2: Basic Properties & Classification
        """
        print("\n" + "="*60)
        print("              THE SPELL FORGE - PHASE 2")
        print("         Basic Properties & Classification")
        print("="*60)

        # Naming & Identity
        spell.spell_name = input(f"\nSpell Name (current: '{spell.spell_name}'): ").strip() or spell.spell_name
        spell.internal_name = input(f"Internal Name (no spaces) (current: '{spell.internal_name}'): ").strip() or spell.internal_name
        spell.description = input(f"Description (current: '{spell.description}'): ").strip() or spell.description

        # Magic School
        print(f"\nCurrent Magic School: {spell.magic_school.name}")
        print("\nSelect Magic School:")
        schools = list(MagicSchool)
        for i, school in enumerate(schools, 1):
            print(f"{i}. {school.name} ({school.value})")

        while True:
            try:
                school_choice = input(f"\nEnter school number (1-{len(schools)}, or press Enter to keep current): ").strip()
                if school_choice == '':
                    break
                school_choice = int(school_choice)
                if 1 <= school_choice <= len(schools):
                    spell.magic_school = schools[school_choice - 1]
                    break
                else:
                    print(f"Invalid choice. Please enter 1-{len(schools)}.")
            except ValueError:
                print(f"Invalid choice. Please enter 1-{len(schools)}.")

        # Spell Type
        print(f"\nCurrent Spell Type: {spell.spell_type.value}")
        print("\nSelect Spell Type:")
        types = list(SpellType)
        for i, stype in enumerate(types, 1):
            print(f"{i}. {stype.value.capitalize()}")

        while True:
            try:
                type_choice = input(f"\nEnter type number (1-{len(types)}, or press Enter to keep current): ").strip()
                if type_choice == '':
                    break
                type_choice = int(type_choice)
                if 1 <= type_choice <= len(types):
                    spell.spell_type = types[type_choice - 1]
                    break
                else:
                    print(f"Invalid choice. Please enter 1-{len(types)}.")
            except ValueError:
                print(f"Invalid choice. Please enter 1-{len(types)}.")

        return spell

    def phase3_mechanics(self, spell: SpellCreationData) -> SpellCreationData:
        """
        Phase 3: Target & Mechanics
        """
        print("\n" + "="*60)
        print("              THE SPELL FORGE - PHASE 3")
        print("               Target & Mechanics")
        print("="*60)

        # Target Type
        print(f"\nCurrent Target Type: {spell.target_type.value}")
        print("\nSelect Target Type:")
        targets = list(TargetType)
        for i, target in enumerate(targets, 1):
            print(f"{i}. {target.value.capitalize()}")

        while True:
            try:
                target_choice = input(f"\nEnter target type (1-{len(targets)}, or press Enter to keep current): ").strip()
                if target_choice == '':
                    break
                target_choice = int(target_choice)
                if 1 <= target_choice <= len(targets):
                    spell.target_type = targets[target_choice - 1]
                    break
                else:
                    print(f"Invalid choice. Please enter 1-{len(targets)}.")
            except ValueError:
                print(f"Invalid choice. Please enter 1-{len(targets)}.")

        # Projectile
        has_proj = input(f"\nHas Projectile? (y/n, current: {'y' if spell.has_projectile else 'n'}): ").strip().lower()
        if has_proj in ['y', 'n']:
            spell.has_projectile = (has_proj == 'y')

        # Range
        while True:
            try:
                range_input = input(f"\nBase Range (current: {spell.base_range}): ").strip()
                if range_input == '':
                    break
                spell.base_range = float(range_input)
                break
            except ValueError:
                print("Invalid value. Please enter a number.")

        # AOE Radius
        while True:
            try:
                aoe_input = input(f"\nAOE Radius (0 for single target, current: {spell.aoe_radius}): ").strip()
                if aoe_input == '':
                    break
                spell.aoe_radius = float(aoe_input)
                break
            except ValueError:
                print("Invalid value. Please enter a number.")

        # Duration (for buffs/debuffs)
        while True:
            try:
                dur_input = input(f"\nDuration in seconds (0 for instant, current: {spell.duration}): ").strip()
                if dur_input == '':
                    break
                spell.duration = float(dur_input)
                break
            except ValueError:
                print("Invalid value. Please enter a number.")

        return spell

    def phase4_level_progression(self, spell: SpellCreationData) -> SpellCreationData:
        """
        Phase 4: Level Progression & Scaling
        """
        print("\n" + "="*60)
        print("              THE SPELL FORGE - PHASE 4")
        print("           Level Progression & Scaling")
        print("="*60)

        # Number of levels
        while True:
            try:
                num_levels = input(f"\nNumber of Levels (1-15, current: {spell.num_levels}): ").strip()
                if num_levels == '':
                    break
                num_levels = int(num_levels)
                if 1 <= num_levels <= 15:
                    spell.num_levels = num_levels
                    spell.initialize_levels()
                    break
                else:
                    print("Number of levels must be between 1-15.")
            except ValueError:
                print("Invalid value. Please enter a number.")

        # Configure level 1 base stats
        print(f"\n--- Configuring Level 1 Base Stats ---")
        base_level = spell.levels[0]

        while True:
            try:
                min_dmg = input(f"Minimum Damage (current: {base_level.damage_min}): ").strip()
                if min_dmg == '':
                    break
                base_level.damage_min = int(min_dmg)
                break
            except ValueError:
                print("Invalid value. Please enter a number.")

        while True:
            try:
                max_dmg = input(f"Maximum Damage (current: {base_level.damage_max}): ").strip()
                if max_dmg == '':
                    break
                base_level.damage_max = int(max_dmg)
                break
            except ValueError:
                print("Invalid value. Please enter a number.")

        while True:
            try:
                mana = input(f"Mana Cost (current: {base_level.mana_cost}): ").strip()
                if mana == '':
                    break
                base_level.mana_cost = int(mana)
                break
            except ValueError:
                print("Invalid value. Please enter a number.")

        while True:
            try:
                cooldown = input(f"Cooldown (seconds, current: {base_level.cooldown}): ").strip()
                if cooldown == '':
                    break
                base_level.cooldown = float(cooldown)
                break
            except ValueError:
                print("Invalid value. Please enter a number.")

        while True:
            try:
                cast = input(f"Cast Time (seconds, current: {base_level.cast_time}): ").strip()
                if cast == '':
                    break
                base_level.cast_time = float(cast)
                break
            except ValueError:
                print("Invalid value. Please enter a number.")

        # Scaling mode
        print(f"\nCurrent Scaling Mode: {spell.scaling_mode.value}")
        print("\nSelect Scaling Mode:")
        modes = list(ScalingMode)
        for i, mode in enumerate(modes, 1):
            print(f"{i}. {mode.value.capitalize()}")

        while True:
            try:
                mode_choice = input(f"\nEnter scaling mode (1-{len(modes)}, or press Enter to keep current): ").strip()
                if mode_choice == '':
                    break
                mode_choice = int(mode_choice)
                if 1 <= mode_choice <= len(modes):
                    spell.scaling_mode = modes[mode_choice - 1]
                    break
                else:
                    print(f"Invalid choice. Please enter 1-{len(modes)}.")
            except ValueError:
                print(f"Invalid choice. Please enter 1-{len(modes)}.")

        # Apply scaling
        if spell.scaling_mode != ScalingMode.CUSTOM:
            spell.apply_scaling()
            print(f"\nScaling applied! Level {spell.num_levels} stats:")
            max_level = spell.levels[-1]
            print(f"  Damage: {max_level.damage_min} - {max_level.damage_max}")
            print(f"  Mana: {max_level.mana_cost}")
            print(f"  Cooldown: {max_level.cooldown:.1f}s")
            print(f"  DPS: {max_level.dps:.1f}")

        return spell

    def phase5_visual_effects(self, spell: SpellCreationData) -> SpellCreationData:
        """
        Phase 5: Visual Effects
        """
        print("\n" + "="*60)
        print("              THE SPELL FORGE - PHASE 5")
        print("                Visual Effects")
        print("="*60)

        print("\nEnter visual effect names (press Enter to keep current):")

        vfx_cast = input(f"Cast Effect (current: '{spell.vfx_cast}'): ").strip()
        if vfx_cast:
            spell.vfx_cast = vfx_cast

        vfx_proj = input(f"Projectile Effect (current: '{spell.vfx_projectile}'): ").strip()
        if vfx_proj:
            spell.vfx_projectile = vfx_proj

        vfx_resolve = input(f"Resolve Effect (current: '{spell.vfx_resolve}'): ").strip()
        if vfx_resolve:
            spell.vfx_resolve = vfx_resolve

        vfx_target = input(f"Target Effect (current: '{spell.vfx_target}'): ").strip()
        if vfx_target:
            spell.vfx_target = vfx_target

        vfx_overtime = input(f"Over Time Effect (current: '{spell.vfx_overtime}'): ").strip()
        if vfx_overtime:
            spell.vfx_overtime = vfx_overtime

        return spell

    def phase6_sound_effects(self, spell: SpellCreationData) -> SpellCreationData:
        """
        Phase 6: Sound Effects
        """
        print("\n" + "="*60)
        print("              THE SPELL FORGE - PHASE 6")
        print("                Sound Effects")
        print("="*60)

        print("\nEnter sound effect names (press Enter to keep current):")

        sfx_cast = input(f"Cast Sound (current: '{spell.sfx_cast}'): ").strip()
        if sfx_cast:
            spell.sfx_cast = sfx_cast

        sfx_proj = input(f"Projectile Sound (current: '{spell.sfx_projectile}'): ").strip()
        if sfx_proj:
            spell.sfx_projectile = sfx_proj

        sfx_resolve = input(f"Resolve Sound (current: '{spell.sfx_resolve}'): ").strip()
        if sfx_resolve:
            spell.sfx_resolve = sfx_resolve

        sfx_hit = input(f"Hit Sound (current: '{spell.sfx_hit}'): ").strip()
        if sfx_hit:
            spell.sfx_hit = sfx_hit

        return spell

    def phase7_review_export(self, spell: SpellCreationData) -> SpellCreationData:
        """
        Phase 7: Review & Export
        """
        print("\n" + "="*60)
        print("              THE SPELL FORGE - PHASE 7")
        print("                Review & Export")
        print("="*60)

        # Display spell summary
        print(f"\n--- Spell Summary ---")
        print(f"ID: {spell.spell_line_id}")
        print(f"Name: {spell.spell_name}")
        print(f"Internal Name: {spell.internal_name}")
        print(f"School: {spell.magic_school.name}")
        print(f"Type: {spell.spell_type.value}")
        print(f"Target: {spell.target_type.value}")
        print(f"Projectile: {'Yes' if spell.has_projectile else 'No'}")
        print(f"Range: {spell.base_range}")
        print(f"AOE Radius: {spell.aoe_radius}")
        print(f"Duration: {spell.duration}s")
        print(f"Levels: {spell.num_levels}")
        print(f"Scaling: {spell.scaling_mode.value}")

        # Show level 1 and max level stats
        if spell.levels:
            print(f"\n--- Level 1 Stats ---")
            lvl1 = spell.levels[0]
            print(f"Damage: {lvl1.damage_min}-{lvl1.damage_max}")
            print(f"Mana: {lvl1.mana_cost}")
            print(f"Cooldown: {lvl1.cooldown}s")
            print(f"Cast Time: {lvl1.cast_time}s")
            print(f"DPS: {lvl1.dps:.1f}")

            if len(spell.levels) > 1:
                print(f"\n--- Level {spell.num_levels} Stats ---")
                lvlmax = spell.levels[-1]
                print(f"Damage: {lvlmax.damage_min}-{lvlmax.damage_max}")
                print(f"Mana: {lvlmax.mana_cost}")
                print(f"Cooldown: {lvlmax.cooldown}s")
                print(f"Cast Time: {lvlmax.cast_time}s")
                print(f"DPS: {lvlmax.dps:.1f}")

        # Balance metrics
        metrics = spell.get_balance_metrics()
        if metrics:
            print(f"\n--- Balance Metrics ---")
            print(f"Damage per Mana: {metrics.get('damage_per_mana', 0):.2f}")
            print(f"Damage per Second: {metrics.get('damage_per_second', 0):.2f}")
            print(f"Power Rating: {metrics.get('power_rating', 0):.1f}")
            print(f"Balance Category: {metrics.get('balance_category', 'Unknown')}")

        # Visual/Sound Effects
        print(f"\n--- Effects ---")
        print(f"VFX Cast: {spell.vfx_cast}")
        print(f"VFX Projectile: {spell.vfx_projectile}")
        print(f"VFX Resolve: {spell.vfx_resolve}")
        print(f"SFX Cast: {spell.sfx_cast}")
        print(f"SFX Hit: {spell.sfx_hit}")

        # Validation
        if SpellValidator:
            print(f"\n--- Validation Results ---")
            validator = SpellValidator()
            errors, warnings = validator.validate(spell)

            if not errors and not warnings:
                print("✓ Spell is valid and ready for export!")
            else:
                if errors:
                    print(f"\n❌ Errors ({len(errors)}):")
                    for error in errors:
                        print(f"  - {error}")

                if warnings:
                    print(f"\n⚠️  Warnings ({len(warnings)}):")
                    for warning in warnings:
                        print(f"  - {warning}")

                if errors:
                    print("\n⚠️  Fix errors before exporting!")

        return spell

    def create_spell(self):
        """
        Main method to create a spell through all phases
        """
        # Phase 1: Mode Selection & ID Assignment
        mode, spell_id, spell = self.phase1_mode_selection()

        if spell is None:
            print("Operation cancelled.")
            return None

        # Phase 2: Basic Properties & Classification
        spell = self.phase2_basic_properties(spell)

        # Phase 3: Target & Mechanics
        spell = self.phase3_mechanics(spell)

        # Phase 4: Level Progression & Scaling
        spell = self.phase4_level_progression(spell)

        # Phase 5: Visual Effects
        spell = self.phase5_visual_effects(spell)

        # Phase 6: Sound Effects
        spell = self.phase6_sound_effects(spell)

        # Phase 7: Review & Export
        spell = self.phase7_review_export(spell)

        # Add to spells dictionary
        self.spells[spell.spell_line_id] = spell

        # Save to file
        self.save_spells()

        # Export individual spell file
        self.export_spell_to_json(spell)

        print("\n" + "="*60)
        print(f"     SPELL FORGE COMPLETE: {spell.spell_name} (ID: {spell.spell_line_id})")
        print("="*60)
        metrics = spell.get_balance_metrics()
        print(f"Balance Category: {metrics.get('balance_category', 'Unknown')}")
        print(f"Power Rating: {metrics.get('power_rating', 0):.1f}")
        print("Spell has been saved to spells.json")

        return spell

    def export_spell_to_json(self, spell: SpellCreationData):
        """Export a single spell to its own JSON file"""
        try:
            # Create export directory
            export_dir = Path(__file__).parent / 'custom_spells' / 'individual'
            export_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in spell.spell_name)
            safe_name = safe_name.replace(" ", "_").lower()
            filename = f"spell_{spell.spell_line_id}_{safe_name}.json"
            filepath = export_dir / filename

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(spell.to_dict(), f, indent=2)

            print(f"Spell exported to: {filepath}")

        except Exception as e:
            print(f"Error exporting spell: {e}")


def run_spell_forge():
    """
    Main function to run the spell forge
    """
    print("\n" + "="*60)
    print("                    THE SPELL FORGE")
    print("         A Multi-Phase Spell Creation System")
    print("="*60)

    forge = SpellForge()

    while True:
        spell = forge.create_spell()

        if spell:
            print(f"\nSuccessfully created spell: {spell.spell_name} (ID: {spell.spell_line_id})")
        else:
            print("\nSpell creation cancelled.")

        # Ask if user wants to create another
        another = input("\nCreate another spell? (y/n): ").strip().lower()
        if another != 'y':
            break

    print("\nThank you for using The Spell Forge!")


if __name__ == "__main__":
    run_spell_forge()
