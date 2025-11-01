#!/usr/bin/env python3
"""
Comprehensive Lua Quest Rewards Scanner
========================================

Scans ALL platform Lua scripts to find SetRewardFlagTrue calls and map them to quest IDs.

This script:
1. Recursively scans all platform folders (P1, P2, P63, etc.)
2. Searches for SetRewardFlagTrue() calls in Lua files
3. Extracts reward names and associated quest IDs
4. Builds a comprehensive reward-to-quest mapping
5. Outputs results to JSON and CSV files

The script looks for patterns like:
    State
    {
        StateName = "QuestState10",
        OnOneTimeEvent
        {
            Conditions = {...},
            Actions = {
                ...SetRewardFlagTrue{Name = "RewardName"}...
            }
        }
    }

Usage:
    python scan_all_reward_flags.py [--verbose] [--output-dir OUTPUT_DIR]
"""

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


class LuaRewardScanner:
    """Scans Lua scripts for reward flag mappings"""

    def __init__(self, script_root: Path, verbose: bool = False):
        self.script_root = script_root
        self.verbose = verbose
        self.mappings = []
        self.stats = {
            "files_scanned": 0,
            "files_with_rewards": 0,
            "total_mappings": 0,
            "platforms_found": set(),
            "unique_rewards": set(),
            "unique_quests": set(),
        }

    def find_platform_folders(self) -> List[Path]:
        """Find all platform folders (P1, p1, P63, etc.)"""
        platform_folders = []

        # Look for folders starting with P or p followed by numbers
        for item in self.script_root.iterdir():
            if item.is_dir():
                name = item.name
                # Match P1, p1, P63, p63, P102, p102, etc.
                if re.match(r"^[Pp]\d+$", name):
                    platform_folders.append(item)

        # Sort by platform number
        def get_platform_number(path: Path) -> int:
            match = re.search(r"\d+", path.name)
            return int(match.group()) if match else 0

        platform_folders.sort(key=get_platform_number)
        return platform_folders

    def extract_quest_id_from_filename(self, filepath: Path) -> str | None:
        """
        Extract quest ID from filename patterns like:
        - n1695.lua -> quest_id could be 1695
        - quest_p1_005.lua
        """
        match = re.search(r"n(\d+)", filepath.stem)
        if match:
            return f"Q{match.group(1)}"
        return None

    def extract_quest_state(self, content: str, position: int) -> str | None:
        """
        Extract the quest state name before a SetRewardFlagTrue call.
        Looks backward from position for StateName = "..."
        """
        # Look for StateName within 2000 chars before the position
        search_start = max(0, position - 2000)
        segment = content[search_start:position]

        # Find all StateName patterns
        state_matches = list(
            re.finditer(r'StateName\s*=\s*["\']([^"\']+)["\']', segment)
        )

        if state_matches:
            # Return the last (closest) one
            return state_matches[-1].group(1)

        return None

    def extract_quest_id_from_context(self, content: str, position: int) -> str | None:
        """
        Extract quest ID from context around SetRewardFlagTrue.
        Looks for patterns like QuestState("quest_name") or QuestId = xxx
        """
        # Look within 3000 chars before the position
        search_start = max(0, position - 3000)
        segment = content[search_start:position]

        # Pattern 1: QuestState("P1_QuestName")
        quest_state_match = re.search(
            r'QuestState\s*\(\s*["\']([^"\']+)["\']\s*\)', segment
        )
        if quest_state_match:
            return quest_state_match.group(1)

        # Pattern 2: QuestId = 123 or quest_id = 123
        quest_id_match = re.search(r"[Qq]uest[_\s]?[Ii]d\s*=\s*(\d+)", segment)
        if quest_id_match:
            return f"Q{quest_id_match.group(1)}"

        return None

    def scan_file(self, filepath: Path, platform: str) -> List[Dict]:
        """
        Scan a single Lua file for SetRewardFlagTrue calls.

        Returns list of mappings found in this file.
        """
        mappings = []

        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            if self.verbose:
                print(f"  ⚠️  Could not read {filepath.name}: {e}")
            return mappings

        # Find all SetRewardFlagTrue calls
        # Pattern: SetRewardFlagTrue{Name = "RewardName"}
        # or SetRewardFlagTrue { Name = "RewardName" }
        pattern = r'SetRewardFlagTrue\s*\{\s*Name\s*=\s*["\']([^"\']+)["\']\s*\}'

        for match in re.finditer(pattern, content):
            reward_name = match.group(1)
            position = match.start()

            # Extract context
            quest_state = self.extract_quest_state(content, position)
            quest_id_context = self.extract_quest_id_from_context(content, position)
            quest_id_filename = self.extract_quest_id_from_filename(filepath)

            # Determine best quest ID
            quest_id = quest_id_context or quest_id_filename or "UNKNOWN"

            mapping = {
                "reward_name": reward_name,
                "quest_id": quest_id,
                "quest_state": quest_state,
                "platform": platform,
                "file": filepath.name,
                "file_path": str(filepath.relative_to(self.script_root)),
            }

            mappings.append(mapping)

            if self.verbose:
                print(f"    ✓ {reward_name} → {quest_id} [{quest_state or 'no state'}]")

        return mappings

    def scan_platform(self, platform_folder: Path) -> List[Dict]:
        """Scan all Lua files in a platform folder"""
        platform = platform_folder.name.upper()

        print(f"\n📁 Scanning {platform}...")

        lua_files = list(platform_folder.glob("*.lua"))

        if not lua_files:
            print("  No Lua files found")
            return []

        print(f"  Found {len(lua_files)} Lua files")

        platform_mappings = []
        files_with_rewards = 0

        for lua_file in lua_files:
            self.stats["files_scanned"] += 1

            file_mappings = self.scan_file(lua_file, platform)

            if file_mappings:
                files_with_rewards += 1
                platform_mappings.extend(file_mappings)

                if not self.verbose:
                    # Show progress for files with results
                    print(f"  ✓ {lua_file.name}: {len(file_mappings)} rewards")

        self.stats["files_with_rewards"] += files_with_rewards
        print(
            f"  → {len(platform_mappings)} reward mappings in {files_with_rewards} files"
        )

        return platform_mappings

    def scan_all_platforms(self):
        """Scan all platform folders"""
        print("=" * 80)
        print("Comprehensive Lua Quest Rewards Scanner")
        print("=" * 80)

        platform_folders = self.find_platform_folders()

        print(f"\nFound {len(platform_folders)} platform folders:")
        for folder in platform_folders:
            print(f"  - {folder.name}")

        print("\nStarting scan...")

        all_mappings = []

        for platform_folder in platform_folders:
            self.stats["platforms_found"].add(platform_folder.name.upper())
            platform_mappings = self.scan_platform(platform_folder)
            all_mappings.extend(platform_mappings)

        self.mappings = all_mappings

        # Update stats
        self.stats["total_mappings"] = len(all_mappings)
        self.stats["unique_rewards"] = {m["reward_name"] for m in all_mappings}
        self.stats["unique_quests"] = {
            m["quest_id"] for m in all_mappings if m["quest_id"] != "UNKNOWN"
        }

    def generate_summary(self) -> Dict:
        """Generate summary statistics"""
        # Group by reward name
        rewards_by_name = defaultdict(list)
        for mapping in self.mappings:
            rewards_by_name[mapping["reward_name"]].append(mapping)

        # Group by quest ID
        quests_by_id = defaultdict(list)
        for mapping in self.mappings:
            quests_by_id[mapping["quest_id"]].append(mapping)

        # Find duplicates (same reward in multiple places)
        duplicates = {
            name: mappings
            for name, mappings in rewards_by_name.items()
            if len(mappings) > 1
        }

        # Find rewards with unknown quest IDs
        unknown_quests = [m for m in self.mappings if m["quest_id"] == "UNKNOWN"]

        return {
            "total_mappings": self.stats["total_mappings"],
            "unique_rewards": len(self.stats["unique_rewards"]),
            "unique_quests": len(self.stats["unique_quests"]),
            "platforms_scanned": len(self.stats["platforms_found"]),
            "files_scanned": self.stats["files_scanned"],
            "files_with_rewards": self.stats["files_with_rewards"],
            "rewards_by_name": dict(rewards_by_name),
            "quests_by_id": dict(quests_by_id),
            "duplicates": duplicates,
            "unknown_quests": unknown_quests,
        }

    def save_results(self, output_dir: Path):
        """Save results to JSON and CSV files"""
        output_dir.mkdir(parents=True, exist_ok=True)

        summary = self.generate_summary()

        # 1. Save complete mappings as JSON
        json_file = output_dir / "lua_reward_mappings_complete.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "summary": {
                        "total_mappings": summary["total_mappings"],
                        "unique_rewards": summary["unique_rewards"],
                        "unique_quests": summary["unique_quests"],
                        "platforms_scanned": summary["platforms_scanned"],
                        "files_scanned": summary["files_scanned"],
                        "files_with_rewards": summary["files_with_rewards"],
                    },
                    "mappings": self.mappings,
                    "platforms": sorted(list(self.stats["platforms_found"])),
                },
                f,
                indent=2,
            )
        print(f"\n✓ Saved complete mappings to {json_file.name}")

        # 2. Save as CSV for easy review
        csv_file = output_dir / "lua_reward_mappings.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "reward_name",
                    "quest_id",
                    "quest_state",
                    "platform",
                    "file",
                    "file_path",
                ],
            )
            writer.writeheader()
            writer.writerows(self.mappings)
        print(f"✓ Saved CSV to {csv_file.name}")

        # 3. Save simplified mapping (reward -> quest ID)
        simple_map = {}
        for mapping in self.mappings:
            reward_name = mapping["reward_name"]
            quest_id = mapping["quest_id"]

            if reward_name not in simple_map:
                simple_map[reward_name] = {
                    "quest_id": quest_id,
                    "platform": mapping["platform"],
                    "quest_state": mapping["quest_state"],
                }

        simple_json = output_dir / "reward_to_quest_map_simple.json"
        with open(simple_json, "w", encoding="utf-8") as f:
            json.dump(simple_map, f, indent=2, sort_keys=True)
        print(f"✓ Saved simple mapping to {simple_json.name}")

        # 4. Save duplicates report
        if summary["duplicates"]:
            dup_file = output_dir / "duplicate_rewards_report.txt"
            with open(dup_file, "w", encoding="utf-8") as f:
                f.write("Duplicate Reward Mappings Report\n")
                f.write("=" * 80 + "\n\n")
                f.write(
                    f"Found {len(summary['duplicates'])} rewards mapped in multiple locations\n\n"
                )

                for reward_name, mappings in sorted(summary["duplicates"].items()):
                    f.write(f"\n{reward_name}:\n")
                    for m in mappings:
                        f.write(
                            f"  - {m['platform']}/{m['file']} → {m['quest_id']} [{m['quest_state']}]\n"
                        )
            print(f"✓ Saved duplicates report to {dup_file.name}")

        # 5. Save unknown quests report
        if summary["unknown_quests"]:
            unknown_file = output_dir / "unknown_quest_ids_report.txt"
            with open(unknown_file, "w", encoding="utf-8") as f:
                f.write("Rewards with Unknown Quest IDs\n")
                f.write("=" * 80 + "\n\n")
                f.write(
                    f"Found {len(summary['unknown_quests'])} rewards without clear quest IDs\n\n"
                )

                for m in summary["unknown_quests"]:
                    f.write(f"- {m['reward_name']}\n")
                    f.write(f"  Platform: {m['platform']}\n")
                    f.write(f"  File: {m['file']}\n")
                    f.write(f"  State: {m['quest_state'] or 'N/A'}\n\n")
            print(f"✓ Saved unknown quests report to {unknown_file.name}")

    def print_report(self):
        """Print final report"""
        summary = self.generate_summary()

        print("\n" + "=" * 80)
        print("SCAN COMPLETE")
        print("=" * 80)

        print("\n📊 Summary Statistics:")
        print(f"  Platforms scanned:      {summary['platforms_scanned']}")
        print(f"  Files scanned:          {summary['files_scanned']}")
        print(f"  Files with rewards:     {summary['files_with_rewards']}")
        print(f"  Total mappings found:   {summary['total_mappings']}")
        print(f"  Unique rewards:         {summary['unique_rewards']}")
        print(f"  Unique quest IDs:       {summary['unique_quests']}")
        print(f"  Duplicate mappings:     {len(summary['duplicates'])}")
        print(f"  Unknown quest IDs:      {len(summary['unknown_quests'])}")

        # Show top platforms by reward count
        platform_counts = defaultdict(int)
        for mapping in self.mappings:
            platform_counts[mapping["platform"]] += 1

        print("\n📍 Top 10 Platforms by Reward Count:")
        for platform, count in sorted(
            platform_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]:
            print(f"  {platform:8} {count:4} rewards")

        # Show sample mappings
        print("\n📝 Sample Mappings (first 10):")
        for mapping in self.mappings[:10]:
            state = f" [{mapping['quest_state']}]" if mapping["quest_state"] else ""
            print(
                f"  {mapping['reward_name']:35} → {mapping['quest_id']:10} ({mapping['platform']}){state}"
            )

        if len(summary["duplicates"]) > 0:
            print(
                f"\n⚠️  Found {len(summary['duplicates'])} rewards with multiple mappings"
            )
            print("   Check duplicate_rewards_report.txt for details")

        if len(summary["unknown_quests"]) > 0:
            print(
                f"\n⚠️  Found {len(summary['unknown_quests'])} rewards with unknown quest IDs"
            )
            print("   Check unknown_quest_ids_report.txt for details")

        print("\n" + "=" * 80)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Scan all platform Lua scripts for quest reward mappings"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output with each reward found",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for results (default: TirganachReloaded/data)",
    )

    args = parser.parse_args()

    # Find script root
    project_root = Path(__file__).parent.parent.parent.parent
    script_root = project_root / "ModdingTools" / "SpellForceLUASources" / "script"

    if not script_root.exists():
        print(f"❌ Error: Script root not found at {script_root}")
        return 1

    # Set output directory
    output_dir = args.output_dir or (project_root / "TirganachReloaded" / "data")

    # Initialize scanner
    scanner = LuaRewardScanner(script_root, verbose=args.verbose)

    # Run scan
    scanner.scan_all_platforms()

    # Save results
    scanner.save_results(output_dir)

    # Print report
    scanner.print_report()

    print(f"\n✅ All results saved to: {output_dir}")
    print("\nNext steps:")
    print("  1. Review lua_reward_mappings.csv for all mappings")
    print("  2. Check duplicate_rewards_report.txt for conflicts")
    print("  3. Use reward_to_quest_map_simple.json to update your database")
    print("  4. Review unknown_quest_ids_report.txt for unmapped rewards")

    return 0


if __name__ == "__main__":
    sys.exit(main())
