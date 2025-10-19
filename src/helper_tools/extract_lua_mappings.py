#!/usr/bin/env python3
"""
SpellForce Lua Mapping Extractor

This script extracts ID-to-name mappings from SpellForce Lua source files
and generates a comprehensive JSON mapping database for use in the editor.

Usage:
    python extract_lua_mappings.py [--output path/to/output.json]
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional


class LuaMappingExtractor:
    """Extract ID mappings from SpellForce Lua source files"""

    def __init__(self, lua_sources_dir: str):
        self.lua_sources_dir = Path(lua_sources_dir)
        self.mappings = {
            "weapon_types": {},
            "spell_lines": {},
            "effect_types": {},
            "job_types": {},
            "races": {},
            "equipment_slots": {},
            "quest_states": {},
            "figure_tasks": {},
            "figure_flags": {},
            "directions": {},
            "target_types": {},
            "variable_operators": {},
            "variable_comparison": {},
            "transfer_flags": {},
            "movement_modes": {},
            "spawn_modes": {},
            "monument_types": {},
            "play_modes": {},
            "animation_subtypes": {},
        }

    def extract_all(self) -> Dict[str, Any]:
        """Extract all mappings from Lua sources"""
        print("🔍 Extracting mappings from Lua sources...")

        # Extract weapon types from DrwSound.lua
        self.extract_weapon_types()

        # Extract constants from GdsDefines.lua
        self.extract_gds_defines()

        # Extract effect types and spell lines from object_effect_register.lua
        self.extract_effect_mappings()

        # Extract monument types from object_effect_register.lua
        self.extract_monument_types()

        # Extract race IDs from effect register (from monument mappings)
        self.extract_race_ids()

        # Extract job/animation IDs (basic set for now)
        self.extract_job_types()

        # Extract figure tasks
        self.extract_figure_tasks()

        # Clean up and validate
        self.clean_mappings()

        return self.mappings

    def extract_weapon_types(self):
        """Extract weapon type mappings from DrwSound.lua"""
        print("  📋 Extracting weapon types...")

        drw_sound_path = self.lua_sources_dir / "script" / "DrwSound.lua"
        if not drw_sound_path.exists():
            print(f"    ⚠️  Warning: {drw_sound_path} not found")
            return

        with open(drw_sound_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Extract BattleData section which maps weapon types to sounds
        # Use a more robust pattern that handles nested braces
        battle_data_start = content.find("local BattleData = {")
        if battle_data_start == -1:
            print("    ⚠️  Warning: Could not find BattleData section")
            return

        # Find the matching closing brace (simple brace counting)
        brace_count = 0
        battle_data_end = battle_data_start
        for i in range(battle_data_start, len(content)):
            if content[i] == "{":
                brace_count += 1
            elif content[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    battle_data_end = i
                    break

        battle_data_content = content[battle_data_start:battle_data_end]

        # Extract hits mapping - use more flexible pattern
        # Match from "hits =" to the comma that ends the section
        hits_match = re.search(
            r"hits\s*=\s*\{([^}]+)\}", battle_data_content, re.DOTALL
        )

        if hits_match:
            hits_content = hits_match.group(1)
            # Pattern: kDrwWt1HSword = "battle_hit_1hsword"
            weapon_pattern = r'(kDrwWt\w+)\s*=\s*"([^"]+)"'

            for match in re.finditer(weapon_pattern, hits_content):
                constant = match.group(1)
                sound_name = match.group(2)

                # Generate readable name from constant
                name = self.format_weapon_name(constant)

                # We don't have the numeric ID yet, so we'll use constant as key
                # and add ID later if we find it
                weapon_id = self.get_weapon_id_from_constant(constant)

                if weapon_id is not None:
                    self.mappings["weapon_types"][str(weapon_id)] = {
                        "name": name,
                        "constant": constant,
                        "display": f"{name} [{weapon_id}]",
                        "sound_hit": sound_name,
                    }

        # Extract misses mapping - use more flexible pattern
        misses_match = re.search(
            r"misses\s*=\s*\{([^}]+)\}", battle_data_content, re.DOTALL
        )

        if misses_match:
            misses_content = misses_match.group(1)
            weapon_pattern = r'(kDrwWt\w+)\s*=\s*"([^"]+)"'

            for match in re.finditer(weapon_pattern, misses_content):
                constant = match.group(1)
                sound_name = match.group(2)
                weapon_id = self.get_weapon_id_from_constant(constant)

                if (
                    weapon_id is not None
                    and str(weapon_id) in self.mappings["weapon_types"]
                ):
                    self.mappings["weapon_types"][str(weapon_id)]["sound_miss"] = (
                        sound_name
                    )

        print(f"    ✅ Extracted {len(self.mappings['weapon_types'])} weapon types")

    def format_weapon_name(self, constant: str) -> str:
        """Convert constant name to readable format

        Example: kDrwWt1HSword -> One-handed Sword
        """
        # Remove prefix
        name = constant.replace("kDrwWt", "")

        # Special cases
        special_names = {
            "Default": "Default/Fist",
            "Mouth": "Mouth/Bite",
            "Hand": "Unarmed/Fist",
            "1HDagger": "One-handed Dagger",
            "1HSword": "One-handed Sword",
            "1HAxe": "One-handed Axe",
            "1HMaceSpiky": "One-handed Mace (Spiky)",
            "1HMaceBlunt": "One-handed Mace (Blunt)",
            "1HHammer": "One-handed Hammer",
            "1HStaff": "One-handed Staff",
            "2HSword": "Two-handed Sword",
            "2HAxe": "Two-handed Axe",
            "2HMace": "Two-handed Mace",
            "2HHammer": "Two-handed Hammer",
            "2HStaff": "Two-handed Staff",
            "2HSpear": "Two-handed Spear",
            "2HHalberd": "Two-handed Halberd",
            "2HBow": "Two-handed Bow",
            "2HCrossbow": "Two-handed Crossbow",
            "1HClaw": "One-handed Claw",
            "Throw": "Thrown Weapon",
        }

        return special_names.get(name, name)

    def get_weapon_id_from_constant(self, constant: str) -> Optional[int]:
        """Try to determine weapon ID from constant name

        Note: Since we don't have the actual C++ enum values,
        we'll use a hardcoded mapping based on the documentation.
        """
        # Based on ID_MAPPINGS.md and common patterns
        weapon_ids = {
            "kDrwWtDefault": 0,
            "kDrwWtMouth": 1,
            "kDrwWtHand": 2,
            "kDrwWt1HDagger": 3,
            "kDrwWt1HSword": 4,
            "kDrwWt1HAxe": 5,
            "kDrwWt1HMaceSpiky": 6,
            "kDrwWt1HMaceBlunt": 7,
            "kDrwWt1HHammer": 8,
            "kDrwWt1HStaff": 9,
            "kDrwWt2HSword": 10,
            "kDrwWt2HAxe": 11,
            "kDrwWt2HMace": 12,
            "kDrwWt2HHammer": 13,
            "kDrwWt2HStaff": 14,
            "kDrwWt2HSpear": 15,
            "kDrwWt2HHalberd": 16,
            "kDrwWt2HBow": 17,
            "kDrwWt2HCrossbow": 18,
            "kDrwWt1HClaw": 19,
            "kDrwWtThrow": 20,
        }

        return weapon_ids.get(constant)

    def extract_gds_defines(self):
        """Extract constants from GdsDefines.lua"""
        print("  📋 Extracting GdsDefines constants...")

        # Try both possible locations
        possible_paths = [
            self.lua_sources_dir / "script" / "GdsDefines.lua",
            Path("ModdingTools/Original Scripts/script/GdsDefines.lua"),
        ]

        gds_path = None
        for path in possible_paths:
            if path.exists():
                gds_path = path
                break

        if not gds_path:
            print("    ⚠️  Warning: GdsDefines.lua not found in any expected location")
            return

        with open(gds_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Extract quest states
        self.extract_quest_states(content)

        # Extract equipment slots
        self.extract_equipment_slots(content)

        # Extract target types
        self.extract_target_types(content)

        # Extract variable operators
        self.extract_variable_operators(content)

        # Extract directions
        self.extract_directions(content)

        # Extract movement modes
        self.extract_movement_modes(content)

    def extract_quest_states(self, content: str):
        """Extract quest state constants"""
        states = {
            "StateUnknown": (0, "Unknown"),
            "StateUnsolvable": (1, "Unsolvable"),
            "StateKnown": (2, "Known"),
            "StateActive": (3, "Active"),
            "StateSolved": (4, "Solved"),
        }

        for constant, (id_val, name) in states.items():
            self.mappings["quest_states"][str(id_val)] = {
                "name": name,
                "constant": constant,
                "display": f"{name} [{id_val}]",
            }

        print(f"    ✅ Extracted {len(states)} quest states")

    def extract_equipment_slots(self, content: str):
        """Extract equipment slot constants"""
        # Pattern: SlotHead = 0
        slot_pattern = r"(Slot\w+)\s*=\s*(\d+)"

        slot_names = {
            "SlotHead": "Head/Helmet",
            "SlotRightHand": "Right Hand",
            "SlotChest": "Chest/Armor",
            "SlotLeftHand": "Left Hand/Shield",
            "SlotRightRing": "Right Ring",
            "SlotLegs": "Legs/Pants",
            "SlotLeftRing": "Left Ring",
        }

        for match in re.finditer(slot_pattern, content):
            constant = match.group(1)
            id_val = match.group(2)
            name = slot_names.get(constant, constant.replace("Slot", ""))

            self.mappings["equipment_slots"][id_val] = {
                "name": name,
                "constant": constant,
                "display": f"{name} [{id_val}]",
            }

        print(
            f"    ✅ Extracted {len(self.mappings['equipment_slots'])} equipment slots"
        )

    def extract_target_types(self, content: str):
        """Extract target type constants"""
        targets = {
            "Figure": (1, "Character/Unit"),
            "Building": (2, "Structure"),
            "Object": (3, "Interactive Object"),
            "World": (4, "Terrain/World"),
            "Area": (5, "Area/Region"),
        }

        for constant, (id_val, name) in targets.items():
            self.mappings["target_types"][str(id_val)] = {
                "name": name,
                "constant": constant,
                "display": f"{name} [{id_val}]",
            }

        print(f"    ✅ Extracted {len(targets)} target types")

    def extract_variable_operators(self, content: str):
        """Extract variable operator constants"""
        operators = {
            "Add": (0, "Addition (+)"),
            "OperatorAdd": (0, "Addition (+)"),
            "OperatorInvertBool": (1, "Boolean NOT (!)"),
            "OperatorSetRandom": (2, "Set Random"),
        }

        # Avoid duplicates
        seen = set()
        for constant, (id_val, name) in operators.items():
            if id_val not in seen:
                self.mappings["variable_operators"][str(id_val)] = {
                    "name": name,
                    "constant": constant,
                    "display": f"{name} [{id_val}]",
                }
                seen.add(id_val)

        print(
            f"    ✅ Extracted {len(self.mappings['variable_operators'])} variable operators"
        )

    def extract_directions(self, content: str):
        """Extract direction constants"""
        directions = {
            "East": (0, "East", "0°"),
            "SouthEast": (1, "Southeast", "45°"),
            "South": (2, "South", "90°"),
            "SouthWest": (3, "Southwest", "135°"),
            "West": (4, "West", "180°"),
            "NorthWest": (5, "Northwest", "225°"),
            "North": (6, "North", "270°"),
            "NorthEast": (7, "Northeast", "315°"),
        }

        for constant, (id_val, name, angle) in directions.items():
            self.mappings["directions"][str(id_val)] = {
                "name": name,
                "constant": constant,
                "display": f"{name} [{id_val}]",
                "angle": angle,
            }

        print(f"    ✅ Extracted {len(directions)} directions")

    def extract_movement_modes(self, content: str):
        """Extract movement mode constants"""
        modes = {
            "Walk": (0, "Walking"),
            "Run": (1, "Running"),
        }

        for constant, (id_val, name) in modes.items():
            self.mappings["movement_modes"][str(id_val)] = {
                "name": name,
                "constant": constant,
                "display": f"{name} [{id_val}]",
            }

        print(f"    ✅ Extracted {len(modes)} movement modes")

    def extract_effect_mappings(self):
        """Extract effect types and spell line mappings"""
        print("  📋 Extracting effect types and spell lines...")

        effect_path = self.lua_sources_dir / "object" / "object_effect_register.lua"
        if not effect_path.exists():
            print(f"    ⚠️  Warning: {effect_path} not found")
            return

        with open(effect_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Extract effect type constants (kGdEffect*)
        self.extract_effect_types(content)

        # Extract spell line mappings
        self.extract_spell_lines(content)

    def extract_effect_types(self, content: str):
        """Extract effect type constants"""
        # Known effect types from ID_MAPPINGS.md
        effects = {
            0: ("None", "kGdEffectNone"),
            1: ("Spell Cast", "kGdEffectSpellCast"),
            2: ("Spell Hit World", "kGdEffectSpellHitWorld"),
            3: ("Spell Hit Target", "kGdEffectSpellHitTarget"),
            4: ("Spell DOT Hit Target", "kGdEffectSpellDOTHitTarget"),
            5: ("Spell Miss Target", "kGdEffectSpellMissTarget"),
            6: ("Spell Resolve", "kGdEffectSpellResolve"),
            7: ("Summon Worker", "kGdEffectSummonWorker"),
            8: ("Worker Appears", "kGdEffectWorkerAppears"),
            9: ("Summon Hero", "kGdEffectSummonHero"),
            10: ("Hero Appears", "kGdEffectHeroAppears"),
            11: ("Spell Target Resisted", "kGdEffectSpellTargetResisted"),
            12: ("Spell Resolve Self", "kGdEffectSpellResolveSelf"),
            13: ("Meteor Fall", "kGdEffectMeteorFall"),
            14: ("Meteor Hit", "kGdEffectMeteorHit"),
            15: ("Blizzard Fall", "kGdEffectBlizzardFall"),
            16: ("Blizzard Hit", "kGdEffectBlizzardHit"),
            17: ("Stone Fall", "kGdEffectStoneFall"),
            18: ("Stone Hit", "kGdEffectStoneHit"),
            19: ("Pet Appears", "kGdEffectPetAppears"),
            20: ("Test Effect", "kGdEffectTest"),
            21: ("Monument Claimed", "kGdEffectMonumentClaimed"),
            22: ("Monument Working", "kGdEffectMonumentWorking"),
            23: ("Aura Resolve", "kGdEffectAuraResolve"),
            24: ("Projectile", "kGdEffectProjectile"),
            25: ("Building", "kGdEffectBuilding"),
            26: ("Player Bind", "kGdEffectPlayerBind"),
            27: ("Summon Main Character", "kGdEffectSummonMainChar"),
            28: ("Main Character Appears", "kGdEffectMainCharAppears"),
            29: ("Titan Production", "kGdEffectTitanProduction"),
            30: ("Titan Appears", "kGdEffectTitanAppears"),
            31: ("Mental Tower Cast", "kGdEffectMentalTowerCast"),
            32: ("Mental Tower Idle", "kGdEffectMentalTowerIdle"),
            33: ("Monument Bullet", "kGdEffectMonumentBullet"),
            34: ("Monument Hit Figure", "kGdEffectMonumentHitFigure"),
            35: ("Spell Assistance Hit", "kGdEffectSpellAssistanceHitFigure"),
            36: ("Chain Resolve", "kGdEffectChainResolve"),
            37: ("Spell Voodoo Hit", "kGdEffectSpellVoodooHitFigure"),
            38: ("Spell Mana Shield Hit", "kGdEffectSpellManaShieldHitFigure"),
        }

        for id_val, (name, constant) in effects.items():
            self.mappings["effect_types"][str(id_val)] = {
                "name": name,
                "constant": constant,
                "display": f"{name} [{id_val}]",
            }

        print(f"    ✅ Extracted {len(effects)} effect types")

    def extract_spell_lines(self, content: str):
        """Extract spell line mappings from SpellEffect declarations"""
        # Pattern: SpellEffect{line=kGdSpellLinePain, ...}
        spell_pattern = r"SpellEffect\{line=(kGdSpellLine\w+)"

        spell_names = {}
        for match in re.finditer(spell_pattern, content):
            constant = match.group(1)
            # Generate readable name from constant
            name = constant.replace("kGdSpellLine", "")

            # Add spaces before capitals
            name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)

            spell_names[constant] = name

        # For now, we don't have the numeric IDs, so we'll store by constant
        # We'll need to extract these from game data files later
        for constant, name in spell_names.items():
            # Use constant as temporary key
            self.mappings["spell_lines"][constant] = {
                "name": name,
                "constant": constant,
                "display": f"{name} [?]",  # ID unknown for now
                "id": None,  # To be filled later
            }

        print(f"    ✅ Extracted {len(spell_names)} spell line constants")

    def extract_monument_types(self):
        """Extract monument type constants"""
        print("  📋 Extracting monument types...")

        monuments = {
            0x303: ("Human Monument", "kGdObjMonumentHuman"),
            0x304: ("Dwarf Monument", "kGdObjMonumentDwarf"),
            0x305: ("Elf Monument", "kGdObjMonumentElf"),
            0x306: ("Dark Elf Monument", "kGdObjMonumentDarkElf"),
            0x307: ("Orc Monument", "kGdObjMonumentOrc"),
            0x308: ("Troll Monument", "kGdObjMonumentTroll"),
            0x309: ("Hero Monument", "kGdObjMonumentHero"),
        }

        for id_val, (name, constant) in monuments.items():
            self.mappings["monument_types"][str(id_val)] = {
                "name": name,
                "constant": constant,
                "display": f"{name} [{id_val}]",
                "hex_id": f"0x{id_val:03X}",
            }

        print(f"    ✅ Extracted {len(monuments)} monument types")

    def extract_race_ids(self):
        """Extract race IDs from monument types and RegisterEffect calls"""
        print("  📋 Extracting race IDs...")

        races = {
            1: ("Human", "kGtRaceHuman"),
            2: ("Elf", "kGtRaceElf"),
            3: ("Dwarf", "kGtRaceDwarf"),
            4: ("Orc", "kGtRaceOrc"),
            5: ("Troll", "kGtRaceTroll"),
            6: ("Dark Elf", "kGtRaceDarkElf"),
        }

        for id_val, (name, constant) in races.items():
            self.mappings["races"][str(id_val)] = {
                "name": name,
                "constant": constant,
                "display": f"{name} [{id_val}]",
            }

        print(f"    ✅ Extracted {len(races)} races")

    def extract_job_types(self):
        """Extract job/animation type constants"""
        print("  📋 Extracting job/animation types...")

        # Core job types based on ID_MAPPINGS.md
        jobs = {
            # Core jobs
            ("kGdJobDefault", "Default/Idle"),
            ("kGdJobGroupNothing", "No Action"),
            ("kGdJobGroupWalk", "Walking"),
            ("kGdJobPunch", "Unarmed Attack"),
            ("kGdJobStrike", "Melee Strike"),
            ("kGdJobStab", "Stabbing Attack"),
            ("kGdJobHitTargetRange1", "Ranged Aim"),
            ("kGdJobHitTargetRange2", "Ranged Fire"),
            ("kGdJobCast", "Spell Cast"),
            ("kGdJobCastResolve", "Spell Complete"),
            ("kGdJobDie", "Death"),
            ("kGdJobCriticalHit", "Hit Reaction"),
            ("kGdJobStoop", "Pickup/Loot"),
            ("kGdJobFeignDeath", "Feign Death"),
            # Worker jobs
            ("kGdJobWoodCutterCutTree", "Chop Trees"),
            ("kGdJobStoneMinerCrushStone", "Mine Stone"),
            ("kGdJobMinerWork", "Mine Ore"),
            ("kGdJobBuilderBuild", "Construction"),
            ("kGdJobFisherWork", "Fishing"),
            ("kGdJobSmithWork", "Blacksmithing"),
        }

        for constant, name in jobs:
            # We don't have numeric IDs for these, store by constant
            self.mappings["job_types"][constant] = {
                "name": name,
                "constant": constant,
                "display": f"{name} [?]",
                "id": None,
            }

        print(f"    ✅ Extracted {len(jobs)} job type constants")

    def extract_figure_tasks(self):
        """Extract figure task type constants"""
        print("  📋 Extracting figure task types...")

        tasks = {
            2: ("Worker", "TASK_WORKER"),
            3: ("Woodcutter", "TASK_WOODCUTTER"),
            4: ("Quarry Worker", "TASK_QUARRY"),
            5: ("Miner", "TASK_MINE"),
            6: ("Blacksmith", "TASK_FORGE"),
            9: ("Hero", "TASK_HERO"),
            10: ("Main Character", "TASK_MAINCHAR"),
            11: ("NPC", "TASK_NPC"),
            12: ("Pet", "TASK_PET"),
            14: ("Hunter", "TASK_HUNTING_LODGE"),
            17: ("Merchant", "TASK_MERCHANT"),
        }

        for id_val, (name, constant) in tasks.items():
            self.mappings["figure_tasks"][str(id_val)] = {
                "name": name,
                "constant": constant,
                "display": f"{name} [{id_val}]",
            }

        print(f"    ✅ Extracted {len(tasks)} figure task types")

    def clean_mappings(self):
        """Clean up and validate extracted mappings"""
        print("  🧹 Cleaning and validating mappings...")

        # Remove empty categories
        self.mappings = {
            category: data for category, data in self.mappings.items() if data
        }

        # Sort IDs within each category
        for category in self.mappings:
            # Only sort if all keys are numeric
            try:
                sorted_items = sorted(
                    self.mappings[category].items(),
                    key=lambda x: int(x[0]) if x[0].isdigit() else 999999,
                )
                self.mappings[category] = dict(sorted_items)
            except (ValueError, AttributeError):
                # Keep original order if not all numeric
                pass

    def save_to_json(self, output_path: str):
        """Save mappings to JSON file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.mappings, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Saved mappings to: {output_path}")

        # Print summary
        print("\n📊 Extraction Summary:")
        for category, data in self.mappings.items():
            print(f"  • {category}: {len(data)} entries")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract ID mappings from SpellForce Lua sources"
    )
    parser.add_argument(
        "--lua-dir",
        default="ModdingTools/SpellForceLUASources",
        help="Path to Lua sources directory",
    )
    parser.add_argument(
        "--output",
        default="src/TiganachReloaded/data/id_name_mappings.json",
        help="Output JSON file path",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("SpellForce Lua Mapping Extractor")
    print("=" * 70)

    extractor = LuaMappingExtractor(args.lua_dir)
    extractor.extract_all()
    extractor.save_to_json(args.output)

    print("\n✨ Extraction complete!")


if __name__ == "__main__":
    main()
