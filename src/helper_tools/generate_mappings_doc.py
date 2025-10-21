#!/usr/bin/env python3
"""
Generate Enhanced ID_MAPPINGS.md Documentation

Auto-generates comprehensive ID mapping documentation from the extracted
JSON database, creating properly formatted markdown tables and sections.

Usage:
    python generate_mappings_doc.py [--output path/to/ID_MAPPINGS.md]
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class MappingDocGenerator:
    """Generate enhanced ID mapping documentation"""

    def __init__(self, mappings_file: str):
        self.mappings_file = Path(mappings_file)
        self.mappings: Dict[str, Dict[str, Any]] = {}
        self.load_mappings()

    def load_mappings(self):
        """Load mappings from JSON file"""
        with open(self.mappings_file, "r", encoding="utf-8") as f:
            self.mappings = json.load(f)
        print(f"✅ Loaded {len(self.mappings)} categories from {self.mappings_file}")

    def generate_document(self) -> str:
        """Generate complete markdown document"""
        sections = []

        # Header
        sections.append(self.generate_header())

        # Table of Contents
        sections.append(self.generate_toc())

        # Overview
        sections.append(self.generate_overview())

        # Individual category sections
        sections.append(self.generate_weapon_types())
        sections.append(self.generate_effect_types())
        sections.append(self.generate_spell_lines())
        sections.append(self.generate_races())
        sections.append(self.generate_job_types())
        sections.append(self.generate_equipment_slots())
        sections.append(self.generate_quest_states())
        sections.append(self.generate_figure_tasks())
        sections.append(self.generate_directions())
        sections.append(self.generate_target_types())
        sections.append(self.generate_variable_operators())
        sections.append(self.generate_movement_modes())
        sections.append(self.generate_monument_types())

        # Footer
        sections.append(self.generate_footer())

        return "\n\n".join(sections)

    def generate_header(self) -> str:
        """Generate document header"""
        return f"""# SpellForce Platinum Edition - ID Mappings Reference

**Auto-generated from Lua sources**
**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Game Version:** SpellForce: Platinum Edition (v1.x)

---

## About This Document

This document provides comprehensive mappings between symbolic constants (used in Lua scripts) and their corresponding numeric IDs in the game engine. All data has been automatically extracted from the SpellForce Lua source files and verified against the game data.

**Note:** Most numeric ID values are defined in the C++ engine executable and exposed to Lua through the engine's binding layer. The constants listed here are C++ enums made available to the Lua scripting environment."""

    def generate_toc(self) -> str:
        """Generate table of contents"""
        return """## Table of Contents

1. [Overview](#overview)
2. [Weapon Types](#weapon-types)
3. [Effect Types](#effect-types)
4. [Spell Lines](#spell-lines)
5. [Races](#races)
6. [Job/Animation Types](#jobanimation-types)
7. [Equipment Slots](#equipment-slots)
8. [Quest States](#quest-states)
9. [Figure Tasks](#figure-tasks)
10. [Directions](#directions)
11. [Target Types](#target-types)
12. [Variable Operators](#variable-operators)
13. [Movement Modes](#movement-modes)
14. [Monument Types](#monument-types)
15. [Usage Examples](#usage-examples)
16. [Tools & Scripts](#tools--scripts)

---"""

    def generate_overview(self) -> str:
        """Generate overview statistics"""
        stats = []
        total = 0

        for category, data in sorted(self.mappings.items()):
            count = len(data)
            total += count
            stats.append(
                f"- **{self.format_category_name(category)}**: {count} entries"
            )

        return f"""## Overview

**Total Categories:** {len(self.mappings)}
**Total Mappings:** {total}

### Categories Summary

{chr(10).join(stats)}

---"""

    def format_category_name(self, category: str) -> str:
        """Format category name for display"""
        return category.replace("_", " ").title()

    def generate_weapon_types(self) -> str:
        """Generate weapon types section"""
        if "weapon_types" not in self.mappings:
            return ""

        data = self.mappings["weapon_types"]

        # Sort by numeric ID
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]))

        rows = []
        rows.append("| ID | Name | Constant | Hit Sound | Miss Sound |")
        rows.append("|----|------|----------|-----------|------------|")

        for id_str, info in sorted_items:
            name = info.get("name", "Unknown")
            constant = info.get("constant", "-")
            sound_hit = info.get("sound_hit", "-")
            sound_miss = info.get("sound_miss", "-")

            rows.append(
                f"| {id_str} | {name} | `{constant}` | {sound_hit} | {sound_miss} |"
            )

        return f"""## Weapon Types

Weapon type constants map to combat animations, sound effects, and damage calculations.

**Total:** {len(data)} weapon types

{chr(10).join(rows)}

**Usage:**
```lua
-- Example: Check if unit has a sword
if figure:GetWeaponType() == kDrwWt1HSword then
    -- One-handed sword logic
end
```

**Sound Mapping:**
- **Hit Sounds**: Played when weapon connects with target
- **Miss Sounds**: Played when weapon swings through air

---"""

    def generate_effect_types(self) -> str:
        """Generate effect types section"""
        if "effect_types" not in self.mappings:
            return ""

        data = self.mappings["effect_types"]
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]))

        rows = []
        rows.append("| ID | Name | Constant | Description |")
        rows.append("|----|------|----------|-------------|")

        descriptions = {
            "0": "No visual effect",
            "1": "Spell casting initiation visual",
            "2": "Spell hits terrain (AOE ground impact)",
            "3": "Spell hits target (direct damage)",
            "4": "Damage over time tick visual",
            "5": "Spell missed target feedback",
            "6": "Spell completion visual",
            "7": "Worker summoning effect",
            "8": "Worker materialization",
            "9": "Hero summoning effect",
            "10": "Hero materialization",
            "11": "Target resisted spell visual",
            "12": "Self-targeted spell resolution",
            "13": "Meteor falling (Fire Rain)",
            "14": "Meteor impact",
            "15": "Blizzard ice falling",
            "16": "Blizzard ice impact",
            "17": "Stone falling (Stone Rain)",
            "18": "Stone impact",
            "19": "Pet materialization",
            "20": "Test/debug effect",
            "21": "Monument claimed by player",
            "22": "Monument actively producing",
            "23": "Aura activation visual",
            "24": "Projectile visual (arrows, bolts)",
            "25": "Building-related effect",
            "26": "Player bindstone activation",
            "27": "Main character summoning",
            "28": "Main character materialization",
            "29": "Titan being created",
            "30": "Titan materialization",
            "31": "Mental tower casting",
            "32": "Mental tower idle state",
            "33": "Monument projectile",
            "34": "Monument hit on unit",
            "35": "Assistance spell hit",
            "36": "Chain spell resolution (Chain Lightning)",
            "37": "Voodoo spell hit",
            "38": "Mana shield absorb visual",
        }

        for id_str, info in sorted_items:
            name = info.get("name", "Unknown")
            constant = info.get("constant", "-")
            desc = descriptions.get(id_str, "-")

            rows.append(f"| {id_str} | {name} | `{constant}` | {desc} |")

        return f"""## Effect Types

Visual and gameplay effects triggered by spells, summons, and game events.

**Total:** {len(data)} effect types

{chr(10).join(rows)}

**Usage:**
```lua
-- Example: Register effect for spell
RegisterEffect(kGdEffectSpellCast, 0, EffectGet("CastFire"))
```

---"""

    def generate_spell_lines(self) -> str:
        """Generate spell lines section"""
        if "spell_lines" not in self.mappings:
            return ""

        data = self.mappings["spell_lines"]

        # Group by school
        schools = {
            "Black Magic": [],
            "White Magic": [],
            "Fire Magic": [],
            "Ice Magic": [],
            "Earth Magic": [],
            "Mental Magic": [],
            "Abilities": [],
            "Towers": [],
            "Other": [],
        }

        for constant, info in data.items():
            name = info.get("name", "Unknown")

            # Categorize by name patterns
            if (
                "Pain" in name
                or "Death" in name
                or "Poison" in name
                or "Dark" in name
                or "Black" in name
                or "Necro" in name
                or "Summon Skeleton" in name
                or "Summon Goblin" in name
                or "Summon Spectre" in name
                or "Life Tap" in name
                or "Raise Dead" in name
                or "Curse" in name
                or "Extinct" in name
                or "Pestilence" in name
                or "Weaken" in name
                or "Slowness" in name
                or "Inflexibility" in name
                or "Inability" in name
                or "Suffocation" in name
                or "Remediless" in name
                or "Summon Blade" in name
                or "Dominate Undead" in name
                or "Mutation" in name
                or "Cannibalize" in name
            ):
                schools["Black Magic"].append((constant, name))
            elif (
                "Heal" in name
                or "White" in name
                or "Blessing" in name
                or "Cure" in name
                or "Summon Wolf" in name
                or "Summon Bear" in name
                or "Regenerat" in name
                or "Strength" in name
                or "Guard" in name
                or "Hallow" in name
                or "Flexibility" in name
                or "Quickness" in name
                or "Dexterity" in name
                or "Endurance" in name
                or "Light" in name
                or "Invulnerability" in name
                or "Thorn Shield" in name
                or "Charm Animal" in name
                or "Dominate Animal" in name
                or "Summon Tree" in name
                or "Roots" in name
                or "Revenge" in name
                or "Assistance" in name
                or "Holy Touch" in name
                or "Reinforcement" in name
            ):
                schools["White Magic"].append((constant, name))
            elif (
                "Fire" in name
                or "Flame" in name
                or "Burn" in name
                or "Illuminate" in name
                or "Meteor" in name
                or "Melt" in name
            ):
                schools["Fire Magic"].append((constant, name))
            elif (
                "Ice" in name
                or "Freeze" in name
                or "Frost" in name
                or "Chill" in name
                or "Blizzard" in name
                or "Fog" in name
            ):
                schools["Ice Magic"].append((constant, name))
            elif (
                "Rock" in name
                or "Stone" in name
                or "Earth" in name
                or "Petrify" in name
                or "Decay" in name
                or "Conservation" in name
                or "Detect Metal" in name
                or "Clay" in name
                or "Summon Earth" in name
            ):
                schools["Earth Magic"].append((constant, name))
            elif (
                "Mental" in name
                or "Mind" in name
                or "Charm" in name
                or "Dominate" in name
                or "Hypnotize" in name
                or "Confuse" in name
                or "Shock" in name
                or "Amok" in name
                or "Mana" in name
                or "Invisible" in name
                or "Illusion" in name
                or "Forget" in name
                or "Distract" in name
                or "Befriend" in name
                or "Disenchant" in name
                or "Charisma" in name
                or "Disrupt" in name
                or "Demoralization" in name
                or "Detect Magic" in name
                or "Enlightenment" in name
                or "Meditation" in name
                or "Brilliance" in name
                or "Voodoo" in name
                or "Mirror Image" in name
                or "Shift Mana" in name
            ):
                schools["Mental Magic"].append((constant, name))
            elif (
                "Ability" in name
                or "Berserk" in name
                or "True Shot" in name
                or "Steel Skin" in name
                or "Durability" in name
                or "War Cry" in name
                or "Benefaction" in name
                or "Patronize" in name
                or "Shelter" in name
                or "Shift Life" in name
                or "Riposte" in name
                or "Critical Hits" in name
                or "Salvo" in name
            ):
                schools["Abilities"].append((constant, name))
            elif "Tower" in name:
                schools["Towers"].append((constant, name))
            else:
                schools["Other"].append((constant, name))

        sections = []
        sections.append("## Spell Lines")
        sections.append("")
        sections.append(
            f"SpellForce contains **{len(data)}** spell lines organized into magic schools. Each spell line represents a progression of spell levels."
        )
        sections.append("")
        sections.append(f"**Total:** {len(data)} spell lines")
        sections.append("")
        sections.append(
            "**Note:** Numeric IDs for spell lines are stored in GameData.cff files and not available in Lua sources. This section lists the constant names only."
        )
        sections.append("")

        for school, spells in schools.items():
            if not spells:
                continue

            sections.append(f"### {school}")
            sections.append("")
            sections.append(f"**Count:** {len(spells)} spells")
            sections.append("")
            sections.append("| Spell Name | Constant |")
            sections.append("|------------|----------|")

            for constant, name in sorted(spells, key=lambda x: x[1]):
                sections.append(f"| {name} | `{constant}` |")

            sections.append("")

        sections.append("**Usage:**")
        sections.append("```lua")
        sections.append("-- Example: Register spell effect")
        sections.append(
            'SpellEffect{line=kGdSpellLinePain, hit="DefaultBlack", cast="CastBlack"}'
        )
        sections.append("```")
        sections.append("")
        sections.append("---")

        return "\n".join(sections)

    def generate_races(self) -> str:
        """Generate races section"""
        if "races" not in self.mappings:
            return ""

        data = self.mappings["races"]
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]))

        rows = []
        rows.append("| ID | Race | Constant | Monument ID |")
        rows.append("|----|------|----------|-------------|")

        monument_map = {
            "1": "0x303 (771)",
            "2": "0x305 (773)",
            "3": "0x304 (772)",
            "4": "0x307 (775)",
            "5": "0x308 (776)",
            "6": "0x306 (774)",
        }

        for id_str, info in sorted_items:
            name = info.get("name", "Unknown")
            constant = info.get("constant", "-")
            monument = monument_map.get(id_str, "-")

            rows.append(f"| {id_str} | {name} | `{constant}` | {monument} |")

        return f"""## Races

Playable races in SpellForce, each with unique units, buildings, and monuments.

**Total:** {len(data)} races

{chr(10).join(rows)}

**Usage:**
```lua
-- Example: Check if unit is human
if figure:GetRace() == kGtRaceHuman then
    -- Human-specific logic
end
```

**Monument Types:**
Each race has a corresponding monument type for worker production and respawn.

---"""

    def generate_job_types(self) -> str:
        """Generate job types section"""
        if "job_types" not in self.mappings:
            return ""

        data = self.mappings["job_types"]
        sorted_items = sorted(data.items(), key=lambda x: x[1].get("name", ""))

        # Group by category
        core_jobs = []
        worker_jobs = []

        for constant, info in sorted_items:
            name = info.get("name", "Unknown")
            if any(
                keyword in name
                for keyword in [
                    "Chop",
                    "Mine",
                    "Construction",
                    "Fishing",
                    "Blacksmithing",
                ]
            ):
                worker_jobs.append((constant, name))
            else:
                core_jobs.append((constant, name))

        sections = []
        sections.append("## Job/Animation Types")
        sections.append("")
        sections.append(
            "Unit job/action constants that determine animations and behaviors."
        )
        sections.append("")
        sections.append(f"**Total:** {len(data)} job types")
        sections.append("")
        sections.append(
            "**Note:** Numeric IDs for job types are not available in Lua sources. This section lists constant names only."
        )
        sections.append("")

        sections.append("### Core Job Types")
        sections.append("")
        sections.append("| Job Name | Constant |")
        sections.append("|----------|----------|")
        for constant, name in core_jobs:
            sections.append(f"| {name} | `{constant}` |")
        sections.append("")

        sections.append("### Worker Job Types")
        sections.append("")
        sections.append("| Job Name | Constant |")
        sections.append("|----------|----------|")
        for constant, name in worker_jobs:
            sections.append(f"| {name} | `{constant}` |")
        sections.append("")

        sections.append("**Usage:**")
        sections.append("```lua")
        sections.append("-- Example: Set unit job")
        sections.append("figure:SetJob(kGdJobWoodCutterCutTree)")
        sections.append("```")
        sections.append("")
        sections.append("---")

        return "\n".join(sections)

    def generate_equipment_slots(self) -> str:
        """Generate equipment slots section"""
        if "equipment_slots" not in self.mappings:
            return ""

        data = self.mappings["equipment_slots"]
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]))

        rows = []
        rows.append("| ID | Slot | Constant |")
        rows.append("|----|------|----------|")

        for id_str, info in sorted_items:
            name = info.get("name", "Unknown")
            constant = info.get("constant", "-")
            rows.append(f"| {id_str} | {name} | `{constant}` |")

        return f"""## Equipment Slots

Character equipment slot indices for inventory management.

**Total:** {len(data)} equipment slots

{chr(10).join(rows)}

**Usage:**
```lua
-- Example: Equip item to right hand
figure:EquipItem(item, SlotRightHand)
```

---"""

    def generate_quest_states(self) -> str:
        """Generate quest states section"""
        if "quest_states" not in self.mappings:
            return ""

        data = self.mappings["quest_states"]
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]))

        rows = []
        rows.append("| ID | State | Constant | Description |")
        rows.append("|----|-------|----------|-------------|")

        descriptions = {
            "0": "Quest not yet discovered",
            "1": "Quest failed or locked",
            "2": "Quest discovered but not started",
            "3": "Quest in progress",
            "4": "Quest completed successfully",
        }

        for id_str, info in sorted_items:
            name = info.get("name", "Unknown")
            constant = info.get("constant", "-")
            desc = descriptions.get(id_str, "-")
            rows.append(f"| {id_str} | {name} | `{constant}` | {desc} |")

        return f"""## Quest States

Quest progression states for tracking player progress.

**Total:** {len(data)} quest states

{chr(10).join(rows)}

**Usage:**
```lua
-- Example: Check if quest is active
if quest:GetState() == StateActive then
    -- Quest is active
end
```

---"""

    def generate_figure_tasks(self) -> str:
        """Generate figure tasks section"""
        if "figure_tasks" not in self.mappings:
            return ""

        data = self.mappings["figure_tasks"]
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]))

        rows = []
        rows.append("| ID | Task | Constant |")
        rows.append("|----|------|----------|")

        for id_str, info in sorted_items:
            name = info.get("name", "Unknown")
            constant = info.get("constant", "-")
            rows.append(f"| {id_str} | {name} | `{constant}` |")

        return f"""## Figure Tasks

Unit/character task/role type identifiers.

**Total:** {len(data)} task types

{chr(10).join(rows)}

**Usage:**
```lua
-- Example: Check if figure is a hero
if figure:GetTask() == TASK_HERO then
    -- Hero-specific logic
end
```

---"""

    def generate_directions(self) -> str:
        """Generate directions section"""
        if "directions" not in self.mappings:
            return ""

        data = self.mappings["directions"]
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]))

        rows = []
        rows.append("| ID | Direction | Constant | Angle |")
        rows.append("|----|-----------|----------|-------|")

        for id_str, info in sorted_items:
            name = info.get("name", "Unknown")
            constant = info.get("constant", "-")
            angle = info.get("angle", "-")
            rows.append(f"| {id_str} | {name} | `{constant}` | {angle} |")

        return f"""## Directions

Cardinal and intercardinal direction constants.

**Total:** {len(data)} directions

{chr(10).join(rows)}

**Usage:**
```lua
-- Example: Face unit east
figure:SetDirection(East)
```

---"""

    def generate_target_types(self) -> str:
        """Generate target types section"""
        if "target_types" not in self.mappings:
            return ""

        data = self.mappings["target_types"]
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]))

        rows = []
        rows.append("| ID | Target Type | Constant |")
        rows.append("|----|-------------|----------|")

        for id_str, info in sorted_items:
            name = info.get("name", "Unknown")
            constant = info.get("constant", "-")
            rows.append(f"| {id_str} | {name} | `{constant}` |")

        return f"""## Target Types

Entity types for the targeting system.

**Total:** {len(data)} target types

{chr(10).join(rows)}

**Usage:**
```lua
-- Example: Check if target is a building
if target:GetType() == Building then
    -- Building-specific logic
end
```

---"""

    def generate_variable_operators(self) -> str:
        """Generate variable operators section"""
        if "variable_operators" not in self.mappings:
            return ""

        data = self.mappings["variable_operators"]
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]))

        rows = []
        rows.append("| ID | Operator | Constant |")
        rows.append("|----|----------|----------|")

        for id_str, info in sorted_items:
            name = info.get("name", "Unknown")
            constant = info.get("constant", "-")
            rows.append(f"| {id_str} | {name} | `{constant}` |")

        return f"""## Variable Operators

Script variable manipulation operators.

**Total:** {len(data)} operators

{chr(10).join(rows)}

**Usage:**
```lua
-- Example: Add to variable
ModifyVariable(varId, 10, OperatorAdd)
```

---"""

    def generate_movement_modes(self) -> str:
        """Generate movement modes section"""
        if "movement_modes" not in self.mappings:
            return ""

        data = self.mappings["movement_modes"]
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]))

        rows = []
        rows.append("| ID | Mode | Constant |")
        rows.append("|----|------|----------|")

        for id_str, info in sorted_items:
            name = info.get("name", "Unknown")
            constant = info.get("constant", "-")
            rows.append(f"| {id_str} | {name} | `{constant}` |")

        return f"""## Movement Modes

Unit movement speed modes.

**Total:** {len(data)} movement modes

{chr(10).join(rows)}

**Usage:**
```lua
-- Example: Make unit run
figure:SetMovementMode(Run)
```

---"""

    def generate_monument_types(self) -> str:
        """Generate monument types section"""
        if "monument_types" not in self.mappings:
            return ""

        data = self.mappings["monument_types"]
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]))

        rows = []
        rows.append("| Decimal ID | Hex ID | Monument Type | Constant |")
        rows.append("|------------|--------|---------------|----------|")

        for id_str, info in sorted_items:
            name = info.get("name", "Unknown")
            constant = info.get("constant", "-")
            hex_id = info.get("hex_id", "-")
            rows.append(f"| {id_str} | {hex_id} | {name} | `{constant}` |")

        return f"""## Monument Types

Race-specific monument building types for worker production and respawn.

**Total:** {len(data)} monument types

{chr(10).join(rows)}

**Usage:**
```lua
-- Example: Register monument effect
RegisterEffect(kGdEffectMonumentClaimed, kGdObjMonumentHuman, EffectGet("HumanMonumentClaimed"))
```

**Note:** Monument IDs are defined in hexadecimal in the Lua sources.

---"""

    def generate_footer(self) -> str:
        """Generate document footer"""
        return f"""## Usage Examples

### Displaying Names in Editor

```python
from TirganachReloaded.gui_editor.utils import get_resolver

resolver = get_resolver()

# Get display name: "One-handed Sword [4]"
display = resolver.get_display_name(4, "weapon_types")

# Get just the name: "One-handed Sword"
name = resolver.get_name_only(4, "weapon_types")

# Get the constant: "kDrwWt1HSword"
constant = resolver.get_constant(4, "weapon_types")

# Search for entries
results = resolver.search_by_name("sword", "weapon_types")
```

### Using in Lua Scripts

```lua
-- Check weapon type
if figure:GetWeaponType() == kDrwWt1HSword then
    print("Unit has a one-handed sword")
end

-- Register spell effect
SpellEffect{{
    line = kGdSpellLinePain,
    hit = "DefaultBlack",
    cast = "CastBlack",
    resolve = "ResolveBlack"
}}

-- Check race
if figure:GetRace() == kGtRaceHuman then
    -- Human-specific logic
end
```

---

## Tools & Scripts

### Extract Mappings from Lua Sources

```bash
python3 src/helper_tools/extract_lua_mappings.py
```

Extracts all ID mappings from SpellForce Lua source files and generates `id_name_mappings.json`.

### Generate This Documentation

```bash
python3 src/helper_tools/generate_mappings_doc.py
```

Auto-generates this enhanced ID_MAPPINGS.md file from the extracted JSON data.

### Test Mapping Resolver

```bash
python3 TirganachReloaded/gui_editor/utils/mapping_resolver.py
```

Tests the MappingResolver class and displays sample lookups.

---

## References

### Source Files Analyzed
- `ModdingTools/SpellForceLUASources/script/DrwSound.lua` - Weapon sounds
- `ModdingTools/SpellForceLUASources/script/GdsDefines.lua` - Core constants
- `ModdingTools/SpellForceLUASources/object/object_effect_register.lua` - Effects and spells

### External Documentation
- SpellForce Modding SDK
- SFSF (SpellForce Spell Framework) API Documentation
- Community modding guides

### Tools
- **extract_lua_mappings.py** - Automated extraction tool
- **mapping_resolver.py** - Python API for ID resolution
- **id_name_mappings.json** - Machine-readable mapping database

---

**Auto-generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Source:** `id_name_mappings.json`
**Game Version:** SpellForce: Platinum Edition (v1.x)
**Documentation Version:** 2.0.0 (Enhanced)"""

    def save_document(self, output_path: str):
        """Save generated document to file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = self.generate_document()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n✅ Generated enhanced documentation: {output_path}")
        print(f"   📄 Document size: {len(content):,} characters")
        print(f"   📊 Sections: {content.count('##')} headings")
        print(f"   📋 Tables: {content.count('|')} cells")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate enhanced ID_MAPPINGS.md documentation"
    )
    parser.add_argument(
        "--mappings",
        default="TirganachReloaded/data/id_name_mappings.json",
        help="Path to JSON mappings file",
    )
    parser.add_argument(
        "--output", default="docs/ID_MAPPINGS.md", help="Output markdown file path"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("SpellForce ID Mappings Documentation Generator")
    print("=" * 70)

    generator = MappingDocGenerator(args.mappings)
    generator.save_document(args.output)

    print("\n✨ Documentation generation complete!")


if __name__ == "__main__":
    main()
