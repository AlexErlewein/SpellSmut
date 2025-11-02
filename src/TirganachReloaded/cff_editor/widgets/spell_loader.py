import json
from pathlib import Path
from typing import Dict, Optional, Any
from ..models import SpellCreationData, MagicSchool, SpellType, TargetType, ScalingMode

class SpellLoader:
    """Load and convert spell data from various sources"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.game_script_path = Path(__file__).parent.parent.parent.parent.parent / "ModdingTools" / "SpellForceLUASources" / "script" / "sql_spellline.lua"
    
    def load_spell_from_data(self, spell_info: Dict) -> Optional[SpellCreationData]:
        """Load spell data from browser selection"""
        if spell_info['source'] == 'template':
            return self.load_template_spell(spell_info['file_path'])
        elif spell_info['source'] == 'game':
            return self.convert_game_spell(spell_info['full_data'])
        
        return None
    
    def load_template_spell(self, file_path: str) -> Optional[SpellCreationData]:
        """Load spell from template JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                spell_data = json.load(f)
            
            return self.convert_template_to_spell_data(spell_data)
            
        except Exception as e:
            print(f"Error loading template spell from {file_path}: {e}")
            return None
    
    def convert_template_to_spell_data(self, template_data: Dict) -> SpellCreationData:
        """Convert template JSON to SpellCreationData"""
        spell = SpellCreationData()
        
        # Basic info
        spell.spell_name = template_data.get('name', 'Unknown Spell')
        spell.internal_name = template_data.get('internal_name', spell.spell_name.replace(' ', ''))
        spell.description = template_data.get('description', '')
        
        # School and type
        school_map = {
            'White': MagicSchool.WHITE,
            'Fire': MagicSchool.FIRE,
            'Ice': MagicSchool.ICE,
            'Black': MagicSchool.BLACK,
            'Mental': MagicSchool.MENTAL,
            'Earth': MagicSchool.EARTH
        }
        
        type_map = {
            'Attack': SpellType.ATTACK,
            'Heal': SpellType.HEAL,
            'Buff': SpellType.BUFF,
            'Debuff': SpellType.DEBUFF,
            'Summon': SpellType.SUMMON,
            'Area': SpellType.AOE,
            'Aura': SpellType.AOE
        }
        
        spell.magic_school = school_map.get(template_data.get('school', 'Fire'), MagicSchool.FIRE)
        spell.spell_type = type_map.get(template_data.get('type', 'Attack'), SpellType.ATTACK)
        
        # Target type
        target_map = {
            'Self': TargetType.SELF,
            'Single': TargetType.SINGLE,
            'Area': TargetType.AOE,
            'Cone': TargetType.CONE,
            'Chain': TargetType.CHAIN
        }
        spell.target_type = target_map.get(template_data.get('target_type', 'Single'), TargetType.SINGLE)
        
        # Scaling
        scaling_map = {
            'Linear': ScalingMode.LINEAR,
            'Exponential': ScalingMode.EXPONENTIAL,
            'Logarithmic': ScalingMode.LOGARITHMIC,
            'Custom': ScalingMode.CUSTOM
        }
        spell.scaling_mode = scaling_map.get(template_data.get('scaling_mode', 'Linear'), ScalingMode.LINEAR)
        
        # Base values (from level 1 or first level)
        levels = template_data.get('levels', {})
        if levels:
            first_level_key = sorted(levels.keys())[0]
            first_level = levels[first_level_key]
            
            spell.base_range = first_level.get('range', 20.0)
            spell.aoe_radius = first_level.get('radius', 0.0)
            spell.duration = first_level.get('duration', 0.0)
            spell.has_projectile = template_data.get('has_projectile', False)
        
        # Visual and audio
        spell.vfx_cast = template_data.get('cast_effect', '')
        spell.vfx_resolve = template_data.get('hit_effect', '')
        spell.vfx_target = template_data.get('impact_effect', '')
        spell.vfx_projectile = template_data.get('projectile_effect', '')
        spell.vfx_overtime = template_data.get('area_effect', '')
        spell.sfx_cast = template_data.get('cast_sound', '')
        spell.sfx_hit = template_data.get('hit_sound', '')
        spell.sfx_resolve = template_data.get('impact_sound', '')
        
        # Special effects
        spell.special_effects = template_data.get('special_effects', [])
        
        # Level progression (convert all levels)
        from ..models.spell_level import SpellLevel
        spell.levels = []
        for level_key, level_data in levels.items():
            try:
                level_num = int(level_key)
                spell_level = SpellLevel(
                    level=level_num,
                    damage_min=level_data.get('damage', 0),
                    damage_max=level_data.get('damage', 0) + 5,
                    mana_cost=level_data.get('mana_cost', 50),
                    range=level_data.get('range', 20.0),
                    cooldown=level_data.get('cooldown', 1.0)
                )
                spell.levels.append(spell_level)
            except (ValueError, TypeError):
                continue
        
        # Ensure we have all levels up to num_levels
        spell.num_levels = len(spell.levels) if spell.levels else 15
        
        return spell
    
    def convert_game_spell(self, game_data: Dict) -> SpellCreationData:
        """Convert game spell data to SpellCreationData"""
        spell = SpellCreationData()
        
        # Basic info from game data
        spell.spell_name = game_data.get('name', 'Unknown Spell')
        spell.internal_name = spell.spell_name.replace(' ', '')
        spell.description = f"Original game spell: {spell.spell_name}"
        
        # Default values for game spells (since we only have basic info)
        spell.magic_school = MagicSchool.FIRE  # Default
        spell.spell_type = SpellType.ATTACK  # Default
        spell.target_type = TargetType.SINGLE
        spell.scaling_mode = ScalingMode.LINEAR
        
        # Conservative defaults
        spell.base_range = 20.0
        spell.aoe_radius = 0.0
        spell.duration = 0.0
        spell.has_projectile = True
        
        # Default effects
        spell.vfx_cast = 'spell_cast_fire'
        spell.vfx_resolve = 'spell_hit_fire'
        spell.vfx_target = 'spell_impact_fire'
        spell.vfx_projectile = 'projectile_fireball'
        spell.vfx_overtime = ''
        spell.sfx_cast = 'spell_cast_fire'
        spell.sfx_hit = 'spell_hit_fire'
        spell.sfx_resolve = 'spell_impact_fire'
        
        # Special effects
        spell.special_effects = []
        
        # Generate basic level progression
        from ..models.spell_level import SpellLevel
        spell.levels = []
        for level in range(1, 16):
            spell_level = SpellLevel(
                level=level,
                damage_min=10 * level,
                damage_max=15 * level,
                mana_cost=50 + (level - 1) * 5,
                range=20.0 + (level - 1) * 2,
                cooldown=1.0
            )
            spell.levels.append(spell_level)
        
        spell.num_levels = 15
        return spell
    
    def get_available_templates(self) -> list:
        """Get list of available template files"""
        templates = []
        if self.templates_dir.exists():
            for file_path in self.templates_dir.glob("*.json"):
                templates.append({
                    'name': file_path.stem.replace('_spell', '').title(),
                    'file_path': str(file_path)
                })
        return templates