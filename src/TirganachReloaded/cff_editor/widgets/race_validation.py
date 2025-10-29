"""Race Validation System

This module provides validation for race data created in the Race Creator Wizard.
"""

from typing import List, Tuple
from ..models.race_creation_data import RaceCreationData
from ..shared.id_manager import IDManager, ContentType


class RaceValidator:
    """Validate race data to ensure it meets SpellForce requirements"""
    
    def __init__(self, id_manager: IDManager):
        self.id_manager = id_manager
        self.errors = []
        self.warnings = []
    
    def validate(self, race_data: RaceCreationData) -> Tuple[List[str], List[str]]:
        """Validate race data and return errors/warnings"""
        self.errors = []
        self.warnings = []
        
        # Check race name
        if not race_data.race_name or not race_data.race_name.strip():
            self.errors.append("Race name is required")
        elif len(race_data.race_name.strip()) < 3:
            self.warnings.append("Race name is very short")
        
        # Check race ID
        if not self.id_manager.is_valid_id(ContentType.RACE, race_data.race_id):
            self.errors.append(f"Race ID {race_data.race_id} is out of valid range")
        elif not self.id_manager.is_id_used(ContentType.RACE, race_data.race_id):
            # This is just a warning since they might be creating a new race ID
            self.warnings.append(f"Race ID {race_data.race_id} is not currently in use")
        
        # Check equipment scaling range
        if race_data.equipment_scaling < 100 or race_data.equipment_scaling > 180:
            self.errors.append(f"Equipment scaling must be between 100-180%, got {race_data.equipment_scaling}%")
        elif race_data.equipment_scaling > 150:
            self.warnings.append(f"Equipment scaling of {race_data.equipment_scaling}% may make race overpowered")
        
        # Check shadow size range
        if race_data.shadow_size < 0.8 or race_data.shadow_size > 2.0:
            self.errors.append(f"Shadow size must be between 0.8-2.0, got {race_data.shadow_size}")
        
        # Validate units
        self._validate_units(race_data.units)
        
        # Validate buildings
        self._validate_buildings(race_data.buildings)
        
        # Check for required files/paths
        if not race_data.animation_library:
            self.warnings.append("No animation library specified")
        
        if not race_data.sound_prefix:
            self.warnings.append("No sound prefix specified")
        
        if not race_data.asset_paths.get("models"):
            self.warnings.append("No 3D model path specified")
        
        if not race_data.asset_paths.get("textures"):
            self.warnings.append("No texture path specified")
        
        if not race_data.asset_paths.get("sounds"):
            self.warnings.append("No sound path specified")
        
        # Check if race has the minimum required units (at least worker, fighter, ranged, mage)
        required_types = {"worker", "fighter", "ranged", "mage"}
        actual_types = {unit.unit_type.value for unit in race_data.units}
        missing_types = required_types - actual_types
        
        if missing_types:
            self.errors.append(f"Missing required unit types: {', '.join(missing_types).title()}")
        
        # Check if race has the minimum required buildings (at least HQ, resource, barracks)
        required_buildings = {"HQ", "resource", "barracks"}
        actual_buildings = {building.building_type for building in race_data.buildings}
        missing_buildings = required_buildings - actual_buildings
        
        if missing_buildings:
            self.errors.append(f"Missing required building types: {', '.join(missing_buildings)}")
        
        return self.errors, self.warnings
    
    def _validate_units(self, units: List) -> None:
        """Validate the list of units"""
        if not units:
            self.errors.append("Race must have at least one unit defined")
            return
        
        if len(units) < 7:  # Minimum: worker, fighter, ranged, mage, siege, titan, swarm
            self.warnings.append(f"Race has only {len(units)} units, but typically needs 7+ units")
        
        unit_names = []
        for i, unit in enumerate(units):
            # Check unit name
            if not unit.name or not unit.name.strip():
                self.errors.append(f"Unit {i+1} has no name")
            else:
                unit_names.append(unit.name.strip().lower())
            
            # Check stats are reasonable
            if unit.stats.strength < 1 or unit.stats.strength > 50:
                self.warnings.append(f"Unit {unit.name}: Strength value {unit.stats.strength} seems unusual")
            
            if unit.stats.dexterity < 1 or unit.stats.dexterity > 50:
                self.warnings.append(f"Unit {unit.name}: Dexterity value {unit.stats.dexterity} seems unusual")
            
            if unit.stats.intelligence < 1 or unit.stats.intelligence > 50:
                self.warnings.append(f"Unit {unit.name}: Intelligence value {unit.stats.intelligence} seems unusual")
            
            # Check combat stats
            if unit.combat.health < 1 or unit.combat.health > 10000:
                self.warnings.append(f"Unit {unit.name}: Health value {unit.combat.health} seems unusual")
            
            if unit.combat.damage_min < 0 or unit.combat.damage_min > 5000:
                self.warnings.append(f"Unit {unit.name}: Min damage {unit.combat.damage_min} seems unusual")
            
            if unit.combat.damage_max < 0 or unit.combat.damage_max > 5000:
                self.warnings.append(f"Unit {unit.name}: Max damage {unit.combat.damage_max} seems unusual")
            
            if unit.combat.damage_min > unit.combat.damage_max:
                self.errors.append(f"Unit {unit.name}: Min damage exceeds max damage")
        
        # Check for duplicate unit names
        if len(unit_names) != len(set(unit_names)):
            self.errors.append("Duplicate unit names found")
    
    def _validate_buildings(self, buildings: List) -> None:
        """Validate the list of buildings"""
        if not buildings:
            self.errors.append("Race must have at least one building defined")
            return
        
        if len(buildings) < 5:  # Minimum for a functional race
            self.warnings.append(f"Race has only {len(buildings)} buildings, but typically needs 5+ buildings")
        
        building_names = []
        for i, building in enumerate(buildings):
            # Check building name
            if not building.name or not building.name.strip():
                self.errors.append(f"Building {i+1} has no name")
            else:
                building_names.append(building.name.strip().lower())
            
            # Check HP is reasonable
            if building.hp < 1 or building.hp > 50000:
                self.warnings.append(f"Building {building.name}: HP value {building.hp} seems unusual")
            
            # Check build time is reasonable
            if building.build_time < 1 or building.build_time > 1000:
                self.warnings.append(f"Building {building.name}: Build time {building.build_time}s seems unusual")
        
        # Check for duplicate building names
        if len(building_names) != len(set(building_names)):
            self.errors.append("Duplicate building names found")
    
    def get_race_balance_score(self, race_data: RaceCreationData) -> dict:
        """Calculate a balance score for the race"""
        score = 0
        details = {
            "unit_count": len(race_data.units),
            "building_count": len(race_data.buildings),
            "avg_unit_health": 0,
            "avg_unit_damage": 0,
            "avg_building_hp": 0,
            "equipment_scaling": race_data.equipment_scaling
        }
        
        # Calculate average unit stats
        if race_data.units:
            total_health = sum(unit.combat.health for unit in race_data.units)
            details["avg_unit_health"] = total_health / len(race_data.units)
            
            total_damage = sum((unit.combat.damage_min + unit.combat.damage_max) / 2 for unit in race_data.units)
            details["avg_unit_damage"] = total_damage / len(race_data.units)
        
        # Calculate average building stats
        if race_data.buildings:
            total_hp = sum(building.hp for building in race_data.buildings)
            details["avg_building_hp"] = total_hp / len(race_data.buildings)
        
        # Calculate a basic score
        # Higher scores are not necessarily better - we want balanced races
        unit_score = min(len(race_data.units) * 5, 50)  # Up to 50 points for units
        building_score = min(len(race_data.buildings) * 3, 30)  # Up to 30 points for buildings
        
        # Equipment scaling affects score (around 100-150 is balanced)
        if 100 <= race_data.equipment_scaling <= 130:
            scaling_score = 15  # Max points for balanced scaling
        elif 130 < race_data.equipment_scaling <= 150:
            scaling_score = 10  # Still reasonable
        else:
            scaling_score = max(0, 15 - abs(race_data.equipment_scaling - 125) / 5)  # Lower points for extremes
        
        # Health and damage balance
        health_score = min(details["avg_unit_health"] / 10, 20) if details["avg_unit_health"] else 0
        damage_score = min(details["avg_unit_damage"] / 5, 20) if details["avg_unit_damage"] else 0
        
        score = unit_score + building_score + scaling_score + health_score + damage_score
        details["score"] = min(100, int(score))
        
        return details