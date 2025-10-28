"""
SpellForce Spell Creation System - Pre-built Spell Templates
"""

from typing import Dict, Any
from ..models import (
    SpellCreationData, MagicSchool, SpellType, TargetType, ScalingMode,
    SpellLevel
)


class SpellTemplate:
    """Pre-configured spell template"""

    def __init__(self, name: str, description: str, template_type: SpellType):
        self.name = name
        self.description = description
        self.template_type = template_type
        self.config = {}

    def create_spell(self) -> SpellCreationData:
        """Create a SpellCreationData instance from this template"""
        raise NotImplementedError("Subclasses must implement create_spell()")


class FireballTemplate(SpellTemplate):
    """Classic fireball spell template"""

    def __init__(self):
        super().__init__(
            "🔥 Fireball",
            "Classic fireball projectile that explodes on impact, dealing fire damage",
            SpellType.ATTACK
        )

    def create_spell(self) -> SpellCreationData:
        # Create 15 levels with exponential scaling
        levels = []
        for level in range(1, 16):
            # Exponential scaling for damage
            damage_min = int(15 + level * 8 * (1.1 ** (level / 3)))
            damage_max = int(20 + level * 10 * (1.1 ** (level / 3)))

            levels.append(SpellLevel(
                level=level,
                damage_min=damage_min,
                damage_max=damage_max,
                mana_cost=10 + level * 2,
                cooldown=3.0,
                cast_time=1.5,
                range=20.0 + level * 0.5,
                aoe_radius=0.0,
                duration=0.0
            ))

        return SpellCreationData(
            spell_name="Fireball",
            internal_name="Fireball",
            magic_school=MagicSchool.FIRE,
            spell_type=SpellType.ATTACK,
            description="Hurls a ball of fire at the target, dealing fire damage on impact",
            target_type=TargetType.SINGLE,
            has_projectile=True,
            base_range=20.0,
            aoe_radius=0.0,
            duration=0.0,
            special_effects=["burn"],
            num_levels=15,
            levels=levels,
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
            created_date="",
            author="Spell Wizard Template"
        )


class IceBlastTemplate(SpellTemplate):
    """Ice blast spell template"""

    def __init__(self):
        super().__init__(
            "❄️ Ice Blast",
            "Freezing projectile that shatters on impact, dealing ice damage and slowing",
            SpellType.ATTACK
        )

    def create_spell(self) -> SpellCreationData:
        levels = []
        for level in range(1, 16):
            damage_min = int(12 + level * 6 * (1.08 ** (level / 4)))
            damage_max = int(18 + level * 8 * (1.08 ** (level / 4)))

            levels.append(SpellLevel(
                level=level,
                damage_min=damage_min,
                damage_max=damage_max,
                mana_cost=12 + level * 2,
                cooldown=3.5,
                cast_time=1.8,
                range=18.0 + level * 0.4,
                aoe_radius=0.0,
                duration=0.0
            ))

        return SpellCreationData(
            spell_name="Ice Blast",
            internal_name="IceBlast",
            magic_school=MagicSchool.ICE,
            spell_type=SpellType.ATTACK,
            description="Launches a shard of ice that shatters on impact, dealing ice damage",
            target_type=TargetType.SINGLE,
            has_projectile=True,
            base_range=18.0,
            aoe_radius=0.0,
            duration=0.0,
            special_effects=["slow"],
            num_levels=15,
            levels=levels,
            scaling_mode=ScalingMode.EXPONENTIAL,
            vfx_cast="CastIce",
            vfx_projectile="ProjectileIceShard",
            vfx_resolve="ResolveIceShatter",
            vfx_target="TargetFreeze",
            vfx_overtime="",
            sfx_cast="spell_ice_cast",
            sfx_projectile="",
            sfx_resolve="spell_hit_iceburst",
            sfx_hit="spell_hit_freeze",
            spell_line_id=302,
            created_date="",
            author="Spell Wizard Template"
        )


class HolyHealTemplate(SpellTemplate):
    """Holy healing spell template"""

    def __init__(self):
        super().__init__(
            "✨ Holy Heal",
            "Instant healing spell that restores health to a single target",
            SpellType.HEAL
        )

    def create_spell(self) -> SpellCreationData:
        levels = []
        for level in range(1, 16):
            # Healing uses linear scaling (more predictable)
            heal_min = 25 + level * 12
            heal_max = 35 + level * 15

            levels.append(SpellLevel(
                level=level,
                damage_min=heal_min,  # Using damage fields for healing
                damage_max=heal_max,
                mana_cost=15 + level * 3,
                cooldown=5.0,
                cast_time=2.0,
                range=25.0 + level * 0.3,
                aoe_radius=0.0,
                duration=0.0
            ))

        return SpellCreationData(
            spell_name="Holy Heal",
            internal_name="HolyHeal",
            magic_school=MagicSchool.WHITE,
            spell_type=SpellType.HEAL,
            description="Channels holy energy to heal a single target's wounds",
            target_type=TargetType.SINGLE,
            has_projectile=False,  # Instant cast
            base_range=25.0,
            aoe_radius=0.0,
            duration=0.0,
            special_effects=[],
            num_levels=15,
            levels=levels,
            scaling_mode=ScalingMode.LINEAR,
            vfx_cast="CastWhite",
            vfx_projectile="",
            vfx_resolve="ResolveHolyFlash",
            vfx_target="TargetHealGlow",
            vfx_overtime="",
            sfx_cast="spell_white_cast",
            sfx_projectile="",
            sfx_resolve="spell_hit_healing",
            sfx_hit="spell_hit_heal",
            spell_line_id=303,
            created_date="",
            author="Spell Wizard Template"
        )


class ChainLightningTemplate(SpellTemplate):
    """Chain lightning spell template"""

    def __init__(self):
        super().__init__(
            "⚡ Chain Lightning",
            "Lightning bolt that jumps between multiple targets in a chain",
            SpellType.ATTACK
        )

    def create_spell(self) -> SpellCreationData:
        levels = []
        for level in range(1, 16):
            # Chain lightning has lower base damage but hits multiple targets
            damage_min = int(20 + level * 4 * (1.05 ** level))
            damage_max = int(30 + level * 6 * (1.05 ** level))

            levels.append(SpellLevel(
                level=level,
                damage_min=damage_min,
                damage_max=damage_max,
                mana_cost=25 + level * 4,
                cooldown=8.0,
                cast_time=2.5,
                range=15.0 + level * 0.2,  # Shorter range
                aoe_radius=8.0 + level * 0.3,  # Chain distance
                duration=0.0
            ))

        return SpellCreationData(
            spell_name="Chain Lightning",
            internal_name="ChainLightning",
            magic_school=MagicSchool.EARTH,  # Lightning is often earth/air elemental
            spell_type=SpellType.AOE,
            description="Summons a bolt of lightning that arcs between nearby enemies",
            target_type=TargetType.CHAIN,
            has_projectile=True,
            base_range=15.0,
            aoe_radius=8.0,  # Chain distance
            duration=0.0,
            special_effects=["stun"],
            num_levels=15,
            levels=levels,
            scaling_mode=ScalingMode.EXPONENTIAL,
            vfx_cast="CastLightning",
            vfx_projectile="ProjectileLightningBolt",
            vfx_resolve="ResolveLightningStrike",
            vfx_target="TargetShock",
            vfx_overtime="",
            sfx_cast="spell_mental_cast",  # Reusing mental cast for now
            sfx_projectile="",
            sfx_resolve="spell_hit_lightning",
            sfx_hit="spell_hit_shock",
            spell_line_id=304,
            created_date="",
            author="Spell Wizard Template"
        )


class RegenerationAuraTemplate(SpellTemplate):
    """Regeneration buff spell template"""

    def __init__(self):
        super().__init__(
            "💚 Regeneration Aura",
            "Places a healing aura on target that restores health over time",
            SpellType.BUFF
        )

    def create_spell(self) -> SpellCreationData:
        levels = []
        for level in range(1, 16):
            # Buff spells have lower immediate impact but longer duration
            heal_per_second = 3 + level * 1

            levels.append(SpellLevel(
                level=level,
                damage_min=heal_per_second,  # Healing per second
                damage_max=heal_per_second,
                mana_cost=20 + level * 3,
                cooldown=15.0,
                cast_time=2.0,
                range=20.0,
                aoe_radius=0.0,
                duration=20.0 + level * 2  # 20-50 seconds
            ))

        return SpellCreationData(
            spell_name="Regeneration Aura",
            internal_name="RegenerationAura",
            magic_school=MagicSchool.WHITE,
            spell_type=SpellType.BUFF,
            description="Surrounds the target with healing energy that restores health over time",
            target_type=TargetType.SINGLE,
            has_projectile=False,
            base_range=20.0,
            aoe_radius=0.0,
            duration=20.0,
            special_effects=[],
            num_levels=15,
            levels=levels,
            scaling_mode=ScalingMode.LINEAR,
            vfx_cast="CastWhite",
            vfx_projectile="",
            vfx_resolve="ResolveHolyFlash",
            vfx_target="TargetHealGlow",
            vfx_overtime="OvertimeRegeneration",
            sfx_cast="spell_white_cast",
            sfx_projectile="",
            sfx_resolve="spell_hit_healing",
            sfx_hit="spell_hit_aura_white",
            spell_line_id=305,
            created_date="",
            author="Spell Wizard Template"
        )


class SummonWolfTemplate(SpellTemplate):
    """Summon creature spell template"""

    def __init__(self):
        super().__init__(
            "🐺 Summon Wolf",
            "Summons a loyal wolf companion to fight alongside you",
            SpellType.SUMMON
        )

    def create_spell(self) -> SpellCreationData:
        levels = []
        for level in range(1, 16):
            # Summon spells scale duration and "strength"
            summon_strength = level  # Represents creature level/power

            levels.append(SpellLevel(
                level=level,
                damage_min=summon_strength,  # Creature level
                damage_max=summon_strength,
                mana_cost=30 + level * 5,
                cooldown=60.0,  # Long cooldown for summons
                cast_time=3.0,
                range=10.0,  # Summon in front of caster
                aoe_radius=0.0,
                duration=45.0 + level * 5  # 45-120 seconds
            ))

        return SpellCreationData(
            spell_name="Summon Wolf",
            internal_name="SummonWolf",
            magic_school=MagicSchool.BLACK,  # Necromancy/summoning
            spell_type=SpellType.SUMMON,
            description="Calls forth a spectral wolf to aid you in battle",
            target_type=TargetType.SELF,
            has_projectile=False,
            base_range=10.0,
            aoe_radius=0.0,
            duration=45.0,
            special_effects=[],
            num_levels=15,
            levels=levels,
            scaling_mode=ScalingMode.LINEAR,
            vfx_cast="CastBlack",
            vfx_projectile="",
            vfx_resolve="ResolveSummon",
            vfx_target="",
            vfx_overtime="OvertimeSummonGlow",
            sfx_cast="spell_black_cast",
            sfx_projectile="",
            sfx_resolve="spell_summon",
            sfx_hit="",
            spell_line_id=306,
            created_date="",
            author="Spell Wizard Template"
        )


class SpellTemplateLibrary:
    """Library of available spell templates"""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, SpellTemplate]:
        """Load all available templates"""
        return {
            "fireball": FireballTemplate(),
            "ice_blast": IceBlastTemplate(),
            "holy_heal": HolyHealTemplate(),
            "chain_lightning": ChainLightningTemplate(),
            "regeneration_aura": RegenerationAuraTemplate(),
            "summon_wolf": SummonWolfTemplate(),
        }

    def get_template(self, template_id: str) -> SpellTemplate | None:
        """Get a template by ID"""
        return self.templates.get(template_id)

    def get_all_templates(self) -> Dict[str, SpellTemplate]:
        """Get all available templates"""
        return self.templates

    def get_templates_by_type(self, spell_type: SpellType) -> Dict[str, SpellTemplate]:
        """Get templates filtered by spell type"""
        return {
            tid: template
            for tid, template in self.templates.items()
            if template.template_type == spell_type
        }

    def get_template_display_list(self) -> list:
        """Get templates formatted for display"""
        return [
            {
                "id": tid,
                "name": template.name,
                "description": template.description,
                "type": template.template_type.value
            }
            for tid, template in self.templates.items()
        ]


# Global template library instance
template_library = SpellTemplateLibrary()


def get_spell_template(template_id: str) -> SpellCreationData:
    """Convenience function to get a spell from template"""
    template = template_library.get_template(template_id)
    if template:
        return template.create_spell()
    return None


def get_available_templates() -> list:
    """Get list of available templates for UI"""
    return template_library.get_template_display_list()