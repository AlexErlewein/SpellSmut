"""
Armor Validation and Balance Calculator
"""

from typing import List, Dict, Any
from ..models.armor_creation_data import ArmorCreationData, ArmorType, ArmorTier


class ArmorValidator:
    """Validate armor data"""

    def __init__(self):
        pass

    def validate(self, armor_data: ArmorCreationData) -> tuple[List[str], List[str]]:
        """
        Validate armor data

        Returns:
            (errors, warnings)
        """
        errors = []
        warnings = []

        # Check required fields
        if not armor_data.armor_name.strip():
            errors.append("Armor name is required")

        if len(armor_data.armor_name.strip()) < 3:
            warnings.append("Armor name is very short (less than 3 characters)")

        # Check armor values
        if armor_data.base_armor < 0:
            errors.append("Base armor cannot be negative")

        if armor_data.health_bonus < 0:
            errors.append("Health bonus cannot be negative")

        if armor_data.mana_bonus < 0:
            errors.append("Mana bonus cannot be negative")

        # Check resistances
        for resist_name, resist_value in [
            ("Fire resistance", armor_data.resist_fire),
            ("Ice resistance", armor_data.resist_ice),
            ("Black magic resistance", armor_data.resist_black),
            ("Mind magic resistance", armor_data.resist_mind)
        ]:
            if resist_value < 0 or resist_value > 100:
                errors.append(f"{resist_name} must be between 0% and 100%")
            elif resist_value > 75:
                warnings.append(f"{resist_name} of {resist_value}% is very high")

        # Check speed modifiers (reasonable bounds)
        for speed_name, speed_value in [
            ("Run speed", armor_data.run_speed_modifier),
            ("Fight speed", armor_data.fight_speed_modifier),
            ("Cast speed", armor_data.cast_speed_modifier)
        ]:
            if speed_value < -75 or speed_value > 75:
                errors.append(f"{speed_name} modifier must be between -75% and +75%")
            elif abs(speed_value) > 50:
                warnings.append(f"{speed_name} modifier of {speed_value}% is extreme")

        # Check special bonuses
        if armor_data.stealth_bonus < 0 or armor_data.stealth_bonus > 100:
            errors.append("Stealth bonus must be between 0% and 100%")

        if armor_data.swimming_speed < -50 or armor_data.swimming_speed > 100:
            errors.append("Swimming speed modifier must be between -50% and +100%")

        if armor_data.jump_height < -50 or armor_data.jump_height > 100:
            errors.append("Jump height modifier must be between -50% and +100%")

        # Check balance
        balance_rating = armor_data.calculate_balance_rating()
        if balance_rating > 95:
            warnings.append(f"Armor may be overpowered (balance rating: {balance_rating}/100)")
        elif balance_rating < 5:
            warnings.append(f"Armor may be underpowered (balance rating: {balance_rating}/100)")

        # Type-specific validation
        if armor_data.armor_type == ArmorType.MAGIC:
            if armor_data.base_armor > 10:
                warnings.append("Magic armor typically has low physical defense (focus on magical stats)")
            if armor_data.intelligence == 0 and armor_data.wisdom == 0 and armor_data.mana_bonus == 0:
                warnings.append("Magic armor should provide magical benefits (intelligence, wisdom, or mana)")
        elif armor_data.armor_type in [ArmorType.PLATE, ArmorType.CHAIN]:
            if armor_data.base_armor < 20:
                warnings.append(f"{armor_data.armor_type.value.title()} armor should provide substantial physical defense")
        elif armor_data.armor_type == ArmorType.CLOTH:
            if armor_data.base_armor > 15:
                warnings.append("Cloth armor typically has low physical defense")

        # Slot-specific validation
        if armor_data.slot.name == "LEFT_HAND":  # Shield
            if armor_data.base_armor < 10:
                warnings.append("Shields should provide meaningful physical defense")

        # Check for conflicting properties
        total_speed_penalty = (armor_data.run_speed_modifier + armor_data.fight_speed_modifier +
                              armor_data.cast_speed_modifier)
        if armor_data.armor_type == ArmorType.PLATE and total_speed_penalty > -20:
            warnings.append("Plate armor should typically reduce movement speed")

        # Check icon
        if not armor_data.icon_handle.strip():
            warnings.append("No icon assigned (armor will appear as placeholder in-game)")

        # Check material
        if not armor_data.material_name.strip():
            warnings.append("No material specified (consider adding one for immersion)")

        return errors, warnings


class ArmorBalanceCalculator:
    """Calculate armor balance metrics"""

    @staticmethod
    def calculate_defense_rating(armor_data: ArmorCreationData) -> float:
        """Calculate overall defense rating (0-100)"""
        return armor_data.calculate_defense_rating()

    @staticmethod
    def calculate_effective_power(armor_data: ArmorCreationData) -> float:
        """Calculate effective power accounting for requirements"""
        defense_rating = armor_data.calculate_defense_rating()

        # Reduce effectiveness if high requirements (harder to get)
        total_req = armor_data.get_total_stat_bonuses()
        req_penalty = total_req / 300.0  # Reduce by up to 50% for very high requirements

        return defense_rating * (1 - req_penalty)

    @staticmethod
    def compare_to_similar(armor_data: ArmorCreationData,
                          all_armor: List[ArmorCreationData]) -> Dict[str, Any]:
        """Compare armor to similar pieces"""

        # Find similar armor (same slot and type)
        similar = [a for a in all_armor
                  if a.slot == armor_data.slot and a.armor_type == armor_data.armor_type
                  and a != armor_data]  # Exclude self if editing

        if not similar:
            return {"similar_count": 0, "comparison": "No similar armor found"}

        # Calculate averages
        avg_defense = sum(a.calculate_defense_rating() for a in similar) / len(similar)
        avg_stats = sum(a.get_total_stat_bonuses() for a in similar) / len(similar)

        current_defense = armor_data.calculate_defense_rating()
        current_stats = armor_data.get_total_stat_bonuses()

        # Determine relative strength
        defense_percentile = (sum(1 for a in similar if a.calculate_defense_rating() < current_defense)
                            / len(similar)) * 100

        stats_percentile = (sum(1 for a in similar if a.get_total_stat_bonuses() < current_stats)
                          / len(similar)) * 100

        # Generate rating
        if defense_percentile >= 80 and stats_percentile >= 80:
            rating = "Exceptional"
            color = "green"
        elif defense_percentile >= 60 and stats_percentile >= 60:
            rating = "Strong"
            color = "blue"
        elif defense_percentile >= 40 and stats_percentile >= 40:
            rating = "Balanced"
            color = "black"
        elif defense_percentile >= 20 and stats_percentile >= 20:
            rating = "Below Average"
            color = "orange"
        else:
            rating = "Weak"
            color = "red"

        return {
            "similar_count": len(similar),
            "avg_defense": avg_defense,
            "avg_stats": avg_stats,
            "defense_percentile": defense_percentile,
            "stats_percentile": stats_percentile,
            "rating": rating,
            "color": color,
            "comparison": f"{rating} compared to {len(similar)} similar {armor_data.armor_type.value} {armor_data.slot.name.lower()} pieces"
        }

    @staticmethod
    def get_balance_recommendations(armor_data: ArmorCreationData) -> List[str]:
        """Get balance recommendations for the armor"""
        recommendations = []

        balance_rating = armor_data.calculate_balance_rating()
        defense_rating = armor_data.calculate_defense_rating()

        if balance_rating > 90:
            recommendations.append("⚠️ Consider reducing armor stats - this piece may be overpowered")
        elif balance_rating < 10:
            recommendations.append("💡 Consider increasing armor effectiveness - this piece may be underpowered")

        # Type-specific recommendations
        if armor_data.armor_type == ArmorType.PLATE:
            if defense_rating < 60:
                recommendations.append("💡 Plate armor should typically provide strong physical defense")
            if armor_data.run_speed_modifier > -10:
                recommendations.append("💡 Consider adding movement speed penalty for realistic plate armor")
        elif armor_data.armor_type == ArmorType.CLOTH:
            if defense_rating > 30:
                recommendations.append("💡 Cloth armor typically has low physical defense")
            if armor_data.run_speed_modifier < 5:
                recommendations.append("💡 Consider adding movement speed bonus for cloth armor")
        elif armor_data.armor_type == ArmorType.MAGIC:
            if armor_data.intelligence + armor_data.wisdom + armor_data.mana_bonus < 10:
                recommendations.append("💡 Magic armor should provide meaningful magical benefits")

        # Slot-specific recommendations
        if "RING" in armor_data.slot.name:
            total_bonuses = (armor_data.get_total_stat_bonuses() +
                           armor_data.health_bonus + armor_data.mana_bonus)
            if total_bonuses > 15:
                recommendations.append("⚠️ Rings are typically weaker than other armor pieces")

        return recommendations

    @staticmethod
    def calculate_tier_appropriateness(armor_data: ArmorCreationData) -> Dict[str, Any]:
        """Check if armor tier matches its power level"""
        defense_rating = armor_data.calculate_defense_rating()

        # Expected defense ranges by tier
        tier_ranges = {
            ArmorTier.COMMON: (0, 25),
            ArmorTier.UNCOMMON: (15, 40),
            ArmorTier.RARE: (30, 60),
            ArmorTier.EPIC: (50, 80),
            ArmorTier.LEGENDARY: (70, 95),
            ArmorTier.UNIQUE: (80, 100)
        }

        expected_min, expected_max = tier_ranges[armor_data.tier]

        if defense_rating < expected_min:
            status = "Underpowered for tier"
            color = "orange"
        elif defense_rating > expected_max:
            status = "Overpowered for tier"
            color = "red"
        else:
            status = "Appropriate for tier"
            color = "green"

        return {
            "current_tier": armor_data.tier.value.title(),
            "defense_rating": defense_rating,
            "expected_range": f"{expected_min}-{expected_max}",
            "status": status,
            "color": color
        }