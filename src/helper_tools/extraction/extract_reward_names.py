#!/usr/bin/env python3
"""
Extract Quest Reward Names from GdsQuestRewards.lua

This script parses the GdsQuestRewards.lua file and generates a comprehensive
mapping template to help manually map reward script names to quest IDs.

Usage:
    python extract_reward_names.py

Output:
    - quest_reward_mappings_template.json (comprehensive template)
    - reward_names_by_platform.txt (readable list for reference)
"""

import json
import re
from pathlib import Path


def parse_rewards_file(file_path: Path) -> dict:
    """Parse GdsQuestRewards.lua and extract all reward entries by platform"""

    with open(file_path, "rb") as f:
        content = f.read().decode("windows-1252", errors="ignore")

    print(f"Reading {file_path.name}...")
    print(f"File size: {len(content)} characters\n")

    # Parse each platform's rewards
    platform_pattern = r"QuestRewardsP(\d+)\s*=\s*\{(.*?)(?=\nQuestRewardsP|\Z)"

    rewards_by_platform = {}

    for platform_match in re.finditer(platform_pattern, content, re.DOTALL):
        platform_num = platform_match.group(1)
        platform = f"P{platform_num}"
        rewards_section = platform_match.group(2)

        print(f"Processing {platform}...")

        # Parse individual quest rewards
        # Format: QuestName = { XP = {25}, Items = {626}, Money = {Gold = 1} }
        quest_pattern = r"(\w+)\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*?)\}"

        platform_rewards = {}

        for quest_match in re.finditer(quest_pattern, rewards_section):
            quest_name = quest_match.group(1)
            reward_data = quest_match.group(2)

            # Extract reward details for reference
            xp_match = re.search(r"XP\s*=\s*\{?\s*(\d+)\s*\}?", reward_data)
            xp = int(xp_match.group(1)) if xp_match else 0

            gold_match = re.search(r"Gold\s*=\s*(\d+)", reward_data)
            gold = int(gold_match.group(1)) if gold_match else 0

            silver_match = re.search(r"Silver\s*=\s*(\d+)", reward_data)
            silver = int(silver_match.group(1)) if silver_match else 0

            copper_match = re.search(r"Copper\s*=\s*(\d+)", reward_data)
            copper = int(copper_match.group(1)) if copper_match else 0

            items_match = re.search(r"Items\s*=\s*\{([^}]+)\}", reward_data)
            items = []
            if items_match:
                items_str = items_match.group(1)
                items = [
                    int(x.strip()) for x in items_str.split(",") if x.strip().isdigit()
                ]

            # Extract comments (often contain useful info)
            comment_match = re.search(r"--\s*(.+)", reward_data)
            comment = comment_match.group(1).strip() if comment_match else ""

            platform_rewards[quest_name] = {
                "quest_id": None,
                "xp": xp,
                "gold": gold,
                "silver": silver,
                "copper": copper,
                "items": items,
                "comment": comment,
            }

        rewards_by_platform[platform] = platform_rewards
        print(f"  Found {len(platform_rewards)} reward entries")

    return rewards_by_platform


def generate_mapping_template(rewards_by_platform: dict, output_path: Path):
    """Generate a JSON template for manual mapping"""

    template = {
        "_readme": {
            "description": "Manual mapping file for quest rewards",
            "format": "Map reward script names from GdsQuestRewards.lua to quest IDs",
            "usage": "Fill in the 'quest_id' field for each reward entry",
            "workflow": [
                "1. Look at the reward name and associated data (XP, items, comment)",
                "2. Search for matching quest in the CFF editor or database",
                "3. Fill in the quest_id field",
                "4. The parser will use these manual mappings when loading data",
            ],
            "note": "Comments from the original file are included to help with identification",
        }
    }

    # Platform names (known ones)
    platform_names = {
        "P63": "Greyfell",
        "P1": "Greydusk Vale",
        "P2": "Greydusk Vale (continued)",
        "P4": "The Whisper",
        "P5": "The Whisper (continued)",
        "P6": "The Shiel",
        "P7": "Mulandir",
        "P9": "Sevenkeeps",
        "P10": "The Gorge",
        "P11": "Dun Mora",
        "P12": "Dun Mora (continued)",
        "P15": "Shal",
        "P16": "Shal (continued)",
        "P17": "The Shattered Wastes",
        "P19": "The Magnet Stones",
        "P21": "Tirganach",
        "P23": "Siege of Mulandir",
        "P25": "Shadow Pass",
        "P27": "The Undergound",
        "P30": "Crystal Wastes",
    }

    # Sort platforms numerically
    sorted_platforms = sorted(rewards_by_platform.keys(), key=lambda x: int(x[1:]))

    for platform in sorted_platforms:
        rewards = rewards_by_platform[platform]
        platform_name = platform_names.get(platform, f"Platform {platform[1:]}")

        template[platform] = {
            "_platform_name": platform_name,
            "_count": len(rewards),
            "rewards": rewards,
        }

    # Write template
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved mapping template to: {output_path}")


def generate_readable_list(rewards_by_platform: dict, output_path: Path):
    """Generate a readable text file listing all rewards"""

    lines = []
    lines.append("=" * 80)
    lines.append("QUEST REWARD NAMES BY PLATFORM")
    lines.append("Extracted from GdsQuestRewards.lua")
    lines.append("=" * 80)
    lines.append("")

    # Sort platforms numerically
    sorted_platforms = sorted(rewards_by_platform.keys(), key=lambda x: int(x[1:]))

    total_rewards = 0

    for platform in sorted_platforms:
        rewards = rewards_by_platform[platform]
        total_rewards += len(rewards)

        lines.append(f"\n{'=' * 80}")
        lines.append(f"PLATFORM {platform} - {len(rewards)} rewards")
        lines.append(f"{'=' * 80}\n")

        for quest_name, data in sorted(rewards.items()):
            lines.append(f"  {quest_name}")

            reward_parts = []
            if data["xp"] > 0:
                reward_parts.append(f"XP: {data['xp']}")
            if data["gold"] > 0:
                reward_parts.append(f"Gold: {data['gold']}")
            if data["silver"] > 0:
                reward_parts.append(f"Silver: {data['silver']}")
            if data["copper"] > 0:
                reward_parts.append(f"Copper: {data['copper']}")
            if data["items"]:
                reward_parts.append(f"Items: {data['items']}")

            if reward_parts:
                lines.append(f"    → {', '.join(reward_parts)}")

            if data["comment"]:
                lines.append(f"    💬 {data['comment']}")

            lines.append("")

    lines.append(f"\n{'=' * 80}")
    lines.append(
        f"SUMMARY: {total_rewards} total reward entries across {len(rewards_by_platform)} platforms"
    )
    lines.append(f"{'=' * 80}")

    # Write file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Saved readable list to: {output_path}")


def main():
    """Main extraction function"""

    print("Quest Reward Name Extractor")
    print("=" * 80)
    print()

    # Find the GdsQuestRewards.lua file
    script_dir = Path(__file__).parent.parent.parent.parent
    rewards_file = (
        script_dir
        / "OriginalGameFiles"
        / "modding"
        / "Original Scripts"
        / "script"
        / "GdsQuestRewards.lua"
    )

    if not rewards_file.exists():
        print("❌ Error: Could not find GdsQuestRewards.lua at:")
        print(f"   {rewards_file}")
        print("\nPlease ensure the OriginalGameFiles directory is in the project root.")
        return 1

    # Parse the rewards file
    rewards_by_platform = parse_rewards_file(rewards_file)

    print(f"\n{'=' * 80}")
    print(
        f"Extracted {sum(len(r) for r in rewards_by_platform.values())} total rewards"
    )
    print(f"from {len(rewards_by_platform)} platforms")
    print(f"{'=' * 80}\n")

    # Generate output files
    output_dir = script_dir / "TirganachReloaded" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    template_file = output_dir / "quest_reward_mappings_template.json"
    readable_file = output_dir / "reward_names_by_platform.txt"

    generate_mapping_template(rewards_by_platform, template_file)
    generate_readable_list(rewards_by_platform, readable_file)

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Review reward_names_by_platform.txt to see all reward entries")
    print("2. Open quest_reward_mappings_template.json")
    print("3. For each reward, find the matching quest ID from:")
    print("   - The CFF editor quest browser")
    print("   - The database query tools")
    print("   - In-game testing")
    print("4. Fill in the quest_id field for each reward")
    print("5. Save as quest_reward_mappings.json")
    print("6. The parser will automatically use your manual mappings")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit(main())
