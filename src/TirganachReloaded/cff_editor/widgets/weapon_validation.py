from typing import List, Dict
from ..models.weapon_creation_data import WeaponCreationData, DamageCategory
from ..shared.id_manager import IDManager, ContentType

class WeaponValidator:
    """Validate weapon data"""
    
    def __init__(self, id_manager: IDManager):
        self.id_manager = id_manager
    
    def validate(self, weapon_data: WeaponCreationData) -> tuple[List[str], List[str]]:
        """
        Validate weapon data
        
        Returns:
            (errors, warnings)
        """
        errors = []
        warnings = []
        
        # Check weapon name
        if not weapon_data.weapon_name:
            errors.append("Weapon name is required")
        elif len(weapon_data.weapon_name) < 3:
            warnings.append("Weapon name is very short")
        
        # Check ID
        if not self.id_manager.is_valid_id(ContentType.WEAPON, weapon_data.weapon_id):
            errors.append(f"Weapon ID {weapon_data.weapon_id} is out of valid range")
        
        # Check damage
        if weapon_data.min_damage > weapon_data.max_damage:
            errors.append("Minimum damage cannot be greater than maximum damage")
        
        if weapon_data.max_damage == 0:
            warnings.append("Weapon has no damage (decorative only?)")
        
        # Check range
        if weapon_data.damage_category == DamageCategory.RANGED:
            if weapon_data.max_range < 10:
                warnings.append("Ranged weapon has very short range")
        else:
            if weapon_data.max_range > 5:
                warnings.append("Melee weapon has unusually long range")
        
        # Check speed
        if weapon_data.attack_speed < 20:
            warnings.append("Attack speed is extremely fast (may be unbalanced)")
        elif weapon_data.attack_speed > 200:
            warnings.append("Attack speed is very slow")
        
        # Check requirements
        total_req = (weapon_data.requirements.strength + 
                     weapon_data.requirements.dexterity + 
                     weapon_data.requirements.intelligence)
        
        if total_req > 150:
            warnings.append("Very high stat requirements (few players can use)")
        
        # Check balance
        balance_rating = weapon_data.get_balance_rating()
        if balance_rating > 80:
            warnings.append("Weapon may be overpowered (balance rating > 80)")
        
        # Check DPS
        dps = weapon_data.calculate_dps()
        if dps > 100:
            warnings.append(f"Very high DPS ({dps:.1f}) - may be overpowered")
        elif dps < 5:
            warnings.append(f"Very low DPS ({dps:.1f}) - weapon is weak")
        
        # Check icon
        if not weapon_data.icon_handle:
            warnings.append("No icon assigned (weapon will appear as placeholder)")
        
        return errors, warnings

class WeaponBalanceCalculator:
    """Calculate weapon balance metrics"""
    
    @staticmethod
    def calculate_dps(weapon_data: WeaponCreationData) -> float:
        """Calculate damage per second"""
        return weapon_data.calculate_dps()
    
    @staticmethod
    def calculate_effective_damage(weapon_data: WeaponCreationData) -> float:
        """Calculate effective damage accounting for requirements"""
        base_dps = weapon_data.calculate_dps()
        
        # Reduce effectiveness if high requirements
        req_penalty = (weapon_data.requirements.strength + 
                       weapon_data.requirements.dexterity + 
                       weapon_data.requirements.intelligence) / 200
        
        return base_dps * (1 - req_penalty)
    
    @staticmethod
    def compare_to_similar(weapon_data: WeaponCreationData, 
                          all_weapons: List[WeaponCreationData]) -> Dict:
        """Compare weapon to similar weapons"""
        
        # Find similar weapons (same type)
        similar = [w for w in all_weapons 
                   if w.weapon_type_id == weapon_data.weapon_type_id]
        
        if not similar:
            return {"similar_count": 0}
        
        # Calculate percentiles
        dps_values = [w.calculate_dps() for w in similar]
        dps_values.sort()
        
        weapon_dps = weapon_data.calculate_dps()
        percentile = (sum(1 for dps in dps_values if dps < weapon_dps) / len(dps_values)) * 100
        
        return {
            "similar_count": len(similar),
            "dps_percentile": percentile,
            "average_dps": sum(dps_values) / len(dps_values),
            "min_dps": min(dps_values),
            "max_dps": max(dps_values),
            "rating": "Weak" if percentile < 25 else 
                     "Below Average" if percentile < 40 else
                     "Average" if percentile < 60 else
                     "Above Average" if percentile < 75 else
                     "Strong"
        }
