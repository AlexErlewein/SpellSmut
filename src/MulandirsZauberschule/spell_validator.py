"""
Spell Validation System

This module provides validation for spell data to ensure consistency,
balance, and correctness before export.
"""

from typing import List, Tuple

try:
    from TirganachReloaded.cff_editor.models.spell_creation_data import SpellCreationData
    from TirganachReloaded.cff_editor.models.spell_enums import SpellType
except ImportError:
    print("Error: Could not import spell models from TirganachReloaded")


class SpellValidator:
    """Validates spell data for consistency and balance"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate(self, spell: SpellCreationData) -> Tuple[List[str], List[str]]:
        """
        Validate a spell and return errors and warnings

        Returns:
            Tuple of (errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Basic validation
        self._validate_basic_properties(spell)
        self._validate_mechanics(spell)
        self._validate_level_progression(spell)
        self._validate_balance(spell)
        self._validate_effects(spell)

        return self.errors, self.warnings

    def _validate_basic_properties(self, spell: SpellCreationData):
        """Validate basic spell properties"""
        # Name validation
        if not spell.spell_name or len(spell.spell_name.strip()) == 0:
            self.errors.append("Spell name cannot be empty")
        elif len(spell.spell_name) > 50:
            self.warnings.append(f"Spell name is very long ({len(spell.spell_name)} characters)")

        # Internal name validation
        if not spell.internal_name or len(spell.internal_name.strip()) == 0:
            self.errors.append("Internal name cannot be empty")
        elif " " in spell.internal_name:
            self.errors.append("Internal name cannot contain spaces")

        # ID validation
        if spell.spell_line_id < 300:
            self.warnings.append(f"Spell ID {spell.spell_line_id} is below 300 (recommended range for custom spells)")
        elif spell.spell_line_id > 9999:
            self.warnings.append(f"Spell ID {spell.spell_line_id} is very high")

    def _validate_mechanics(self, spell: SpellCreationData):
        """Validate spell mechanics"""
        # Range validation
        if spell.base_range < 0:
            self.errors.append("Base range cannot be negative")
        elif spell.base_range == 0 and spell.target_type.value != 'self':
            self.warnings.append("Base range is 0 but target type is not 'self'")
        elif spell.base_range > 100:
            self.warnings.append(f"Base range ({spell.base_range}) is very high")

        # AOE validation
        if spell.aoe_radius < 0:
            self.errors.append("AOE radius cannot be negative")
        elif spell.aoe_radius > 50:
            self.warnings.append(f"AOE radius ({spell.aoe_radius}) is very large")

        # Duration validation
        if spell.duration < 0:
            self.errors.append("Duration cannot be negative")
        elif spell.duration > 300:
            self.warnings.append(f"Duration ({spell.duration}s) is very long (over 5 minutes)")

        # Projectile validation
        if spell.has_projectile:
            if spell.projectile_count < 1:
                self.errors.append("Projectile count must be at least 1 if spell has projectile")
            elif spell.projectile_count > 20:
                self.warnings.append(f"Projectile count ({spell.projectile_count}) is very high")

            if spell.projectile_speed <= 0:
                self.errors.append("Projectile speed must be positive")

    def _validate_level_progression(self, spell: SpellCreationData):
        """Validate spell level progression"""
        # Number of levels
        if spell.num_levels < 1 or spell.num_levels > 15:
            self.errors.append(f"Number of levels must be between 1-15, got {spell.num_levels}")

        # Check if we have levels defined
        if not spell.levels:
            self.errors.append("Spell has no levels defined")
            return

        if len(spell.levels) != spell.num_levels:
            self.errors.append(f"Number of levels ({spell.num_levels}) doesn't match actual levels ({len(spell.levels)})")

        # Validate each level
        for i, level in enumerate(spell.levels):
            level_num = i + 1

            # Damage validation
            if level.damage_min < 0:
                self.errors.append(f"Level {level_num}: Minimum damage cannot be negative")
            if level.damage_max < level.damage_min:
                self.errors.append(f"Level {level_num}: Maximum damage ({level.damage_max}) is less than minimum damage ({level.damage_min})")

            # Mana cost validation
            if level.mana_cost < 0:
                self.errors.append(f"Level {level_num}: Mana cost cannot be negative")
            elif level.mana_cost == 0:
                self.warnings.append(f"Level {level_num}: Mana cost is 0 (free spell)")
            elif level.mana_cost > 1000:
                self.warnings.append(f"Level {level_num}: Mana cost ({level.mana_cost}) is very high")

            # Cooldown validation
            if level.cooldown < 0:
                self.errors.append(f"Level {level_num}: Cooldown cannot be negative")
            elif level.cooldown == 0:
                self.warnings.append(f"Level {level_num}: Cooldown is 0 (instant recast)")
            elif level.cooldown > 60:
                self.warnings.append(f"Level {level_num}: Cooldown ({level.cooldown}s) is very long")

            # Cast time validation
            if level.cast_time < 0:
                self.errors.append(f"Level {level_num}: Cast time cannot be negative")
            elif level.cast_time > 10:
                self.warnings.append(f"Level {level_num}: Cast time ({level.cast_time}s) is very long")

        # Check for logical progression
        if len(spell.levels) > 1:
            first_level = spell.levels[0]
            last_level = spell.levels[-1]

            # Damage should generally increase
            if last_level.damage_max <= first_level.damage_max:
                self.warnings.append("Spell damage doesn't increase with levels")

            # Mana cost progression check
            if last_level.mana_cost < first_level.mana_cost:
                self.warnings.append("Mana cost decreases with levels (unusual)")

    def _validate_balance(self, spell: SpellCreationData):
        """Validate spell balance"""
        if not spell.levels:
            return

        # Check balance at max level
        max_level = spell.levels[-1]

        # Damage per mana ratio
        if max_level.mana_cost > 0:
            dpm = max_level.damage_per_mana
            if dpm > 10:
                self.warnings.append(f"Very high damage per mana ratio ({dpm:.1f}) - spell may be overpowered")
            elif dpm < 0.5:
                self.warnings.append(f"Very low damage per mana ratio ({dpm:.1f}) - spell may be underpowered")

        # DPS check
        dps = max_level.dps
        if dps > 100:
            self.warnings.append(f"Very high DPS ({dps:.1f}) at max level - spell may be overpowered")
        elif dps < 5 and spell.spell_type == SpellType.ATTACK:
            self.warnings.append(f"Very low DPS ({dps:.1f}) for an attack spell - may be underpowered")

        # Effective cast time
        ect = max_level.effective_cast_time
        if ect < 1.0:
            self.warnings.append(f"Very short effective cast time ({ect:.1f}s) - spell can be spammed")
        elif ect > 20.0:
            self.warnings.append(f"Very long effective cast time ({ect:.1f}s) - spell is slow to use")

        # Get overall balance metrics
        metrics = spell.get_balance_metrics()
        if metrics:
            power_rating = metrics.get('power_rating', 0)
            balance_category = metrics.get('balance_category', 'Unknown')

            if balance_category == 'Overpowered':
                self.warnings.append(f"Spell is rated as '{balance_category}' (power rating: {power_rating:.1f})")
            elif balance_category == 'Weak':
                self.warnings.append(f"Spell is rated as '{balance_category}' (power rating: {power_rating:.1f})")

    def _validate_effects(self, spell: SpellCreationData):
        """Validate visual and sound effects"""
        # Check if attack spells have appropriate effects
        if spell.spell_type == SpellType.ATTACK:
            if not spell.vfx_cast and not spell.vfx_projectile and not spell.vfx_resolve:
                self.warnings.append("Attack spell has no visual effects defined")
            if not spell.sfx_cast and not spell.sfx_hit:
                self.warnings.append("Attack spell has no sound effects defined")

        # Projectile effects
        if spell.has_projectile:
            if not spell.vfx_projectile:
                self.warnings.append("Spell has projectile but no projectile visual effect")
            if not spell.sfx_projectile:
                self.warnings.append("Spell has projectile but no projectile sound effect")

        # Aura validation
        if spell.has_aura:
            if spell.aura_radius <= 0:
                self.errors.append("Spell has aura but aura radius is 0 or negative")
            if spell.aura_duration <= 0:
                self.warnings.append("Spell has aura but aura duration is 0 or negative")


def validate_spell(spell: SpellCreationData) -> Tuple[List[str], List[str]]:
    """
    Convenience function to validate a spell

    Returns:
        Tuple of (errors, warnings)
    """
    validator = SpellValidator()
    return validator.validate(spell)
