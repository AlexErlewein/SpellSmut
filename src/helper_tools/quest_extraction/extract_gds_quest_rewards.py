#!/usr/bin/env python3
"""
Extract Quest Rewards from GdsQuestRewards.lua
==============================================

Parses the main quest rewards file to extract:
- XP rewards
- Item rewards (with item IDs)
- Money rewards (Gold, Silver, Copper)

Maps reward names to quest IDs using existing mapping files.

Usage:
    python extract_gds_quest_rewards.py
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class QuestReward:
    """Complete quest reward information"""

    quest_id: Optional[int] = None
    reward_name: str = ""
    platform: str = ""
    xp: int = 0
    gold: int = 0
    silver: int = 0
    copper: int = 0
    items: List[int] = None

    def __post_init__(self):
        if self.items is None:
            self.items = []


class GdsQuestRewardsParser:
    """Parser for GdsQuestRewards.lua file"""

    def __init__(self, lua_file: Path, project_root: Path):
        self.lua_file = lua_file
        self.project_root = project_root
        self.data_dir = project_root / "src" / "TirganachReloaded" / "data"
        self.rewards: List[QuestReward] = []

        # Load existing mappings (reward name -> quest ID)
        self.reward_to_quest_map = self._load_reward_mappings()

    def _load_reward_mappings(self) -> Dict[str, int]:
        """Load reward name to quest ID mappings"""
        mappings = {}

        # Try to load from CSV file
        csv_file = self.data_dir / "FINAL_REWARD_WITH_QUEST_IDS.csv"
        if csv_file.exists():
            import csv

            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    reward_name = row.get("Reward_Name", "").strip('"')
                    quest_id = row.get("Quest_ID", "").strip()
                    if quest_id and quest_id != "NOT_FOUND" and quest_id.isdigit():
                        mappings[reward_name] = int(quest_id)

        print(f"[INFO] Loaded {len(mappings)} reward-to-quest mappings")
        return mappings

    def parse(self) -> List[QuestReward]:
        """Parse the GdsQuestRewards.lua file"""
        print(f"[INFO] Parsing {self.lua_file}")

        if not self.lua_file.exists():
            print(f"[ERROR] File not found: {self.lua_file}")
            return []

        # Try different encodings
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        content = None

        for encoding in encodings:
            try:
                with open(self.lua_file, "r", encoding=encoding) as f:
                    content = f.read()
                print(f"[INFO] Successfully read file with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            print("[ERROR] Could not read file with any supported encoding")
            return []

        # Find all platform reward tables
        # Need to match nested braces, so use a more robust pattern
        platform_pattern = r"QuestRewardsP(\d+)\s*=\s*\{(.*?)\n\}\s*(?:\n|--)"
        platform_matches = re.finditer(platform_pattern, content, re.DOTALL)

        for match in platform_matches:
            platform_id = match.group(1)
            platform_code = f"P{platform_id}"
            table_content = match.group(2)

            # Parse individual rewards in this platform
            self._parse_platform_rewards(platform_code, table_content)

        print(f"[INFO] Extracted {len(self.rewards)} quest rewards")
        return self.rewards

    def _parse_platform_rewards(self, platform: str, content: str):
        """Parse rewards for a specific platform"""
        # Pattern to match reward entries like:
        # RewardName = { XP = {25}, Items = {626}, Money = {Gold = 2, Silver = 1, Copper = 50}}
        # Split by lines and parse each reward entry
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if not line or line.startswith("--"):
                continue

            # Match: RewardName = { ... }, or RewardName = { ... } -- comment
            # Need to handle nested braces, so match everything up to the final closing brace before comma or comment
            match = re.match(r"(\w+)\s*=\s*\{(.+)\}\s*,?\s*(?:--.*)?$", line)
            if not match:
                continue

            reward_name = match.group(1)
            reward_data = match.group(2)

            self._extract_reward_data(reward_name, reward_data, platform)

    def _extract_reward_data(self, reward_name: str, reward_data: str, platform: str):
        """Extract reward data from a single reward entry"""
        reward = QuestReward(reward_name=reward_name, platform=platform)

        # Extract XP
        xp_match = re.search(r"XP\s*=\s*\{(\d+)\}", reward_data)
        if xp_match:
            reward.xp = int(xp_match.group(1))

        # Extract Items (array of item IDs)
        items_match = re.search(r"Items\s*=\s*\{([^}]+)\}", reward_data)
        if items_match:
            items_str = items_match.group(1)
            item_ids = re.findall(r"\d+", items_str)
            reward.items = [int(item_id) for item_id in item_ids]

        # Extract Money
        money_match = re.search(r"Money\s*=\s*\{([^}]+)\}", reward_data)
        if money_match:
            money_str = money_match.group(1)

            # Extract Gold
            gold_match = re.search(r"Gold\s*=\s*(\d+)", money_str)
            if gold_match:
                reward.gold = int(gold_match.group(1))

            # Extract Silver
            silver_match = re.search(r"Silver\s*=\s*(\d+)", money_str)
            if silver_match:
                reward.silver = int(silver_match.group(1))

            # Extract Copper
            copper_match = re.search(r"Copper\s*=\s*(\d+)", money_str)
            if copper_match:
                reward.copper = int(copper_match.group(1))

        # Try to map to quest ID
        if reward_name in self.reward_to_quest_map:
            reward.quest_id = self.reward_to_quest_map[reward_name]

        self.rewards.append(reward)

    def get_stats(self) -> Dict:
        """Get statistics about extracted rewards"""
        total = len(self.rewards)
        with_quest_id = sum(1 for r in self.rewards if r.quest_id is not None)
        with_xp = sum(1 for r in self.rewards if r.xp > 0)
        with_items = sum(1 for r in self.rewards if r.items)
        with_money = sum(
            1 for r in self.rewards if r.gold > 0 or r.silver > 0 or r.copper > 0
        )

        platforms = set(r.platform for r in self.rewards)

        return {
            "total_rewards": total,
            "with_quest_id": with_quest_id,
            "without_quest_id": total - with_quest_id,
            "with_xp": with_xp,
            "with_items": with_items,
            "with_money": with_money,
            "platforms_covered": len(platforms),
            "platforms": sorted(platforms),
        }

    def export_to_json(self, output_file: Path):
        """Export rewards to JSON format"""
        # Convert to dictionary format suitable for QuestDataService
        rewards_by_quest_id = {}
        rewards_without_quest_id = []

        for reward in self.rewards:
            reward_dict = {
                "xp": reward.xp,
                "gold": reward.gold,
                "silver": reward.silver,
                "copper": reward.copper,
                "items": reward.items,
                "flags": [reward.reward_name],
                "platform": reward.platform,
            }

            if reward.quest_id is not None:
                quest_id_str = str(reward.quest_id)
                # If quest already has rewards, merge them
                if quest_id_str in rewards_by_quest_id:
                    existing = rewards_by_quest_id[quest_id_str]
                    # Add XP
                    existing["xp"] += reward.xp
                    # Add items
                    existing["items"].extend(reward.items)
                    # Add flags
                    existing["flags"].append(reward.reward_name)
                    # Keep highest money values
                    existing["gold"] = max(existing["gold"], reward.gold)
                    existing["silver"] = max(existing["silver"], reward.silver)
                    existing["copper"] = max(existing["copper"], reward.copper)
                else:
                    rewards_by_quest_id[quest_id_str] = reward_dict
            else:
                rewards_without_quest_id.append(
                    {
                        "reward_name": reward.reward_name,
                        "platform": reward.platform,
                        **reward_dict,
                    }
                )

        output_data = {
            "rewards_by_quest_id": rewards_by_quest_id,
            "rewards_without_quest_id": rewards_without_quest_id,
            "statistics": self.get_stats(),
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"[INFO] Exported rewards to {output_file}")

    def export_to_csv(self, output_file: Path):
        """Export rewards to CSV format"""
        import csv

        with open(output_file, "w", encoding="utf-8", newline="") as f:
            fieldnames = [
                "Quest_ID",
                "Reward_Name",
                "Platform",
                "XP",
                "Gold",
                "Silver",
                "Copper",
                "Items",
                "Item_Count",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for reward in self.rewards:
                writer.writerow(
                    {
                        "Quest_ID": reward.quest_id if reward.quest_id else "UNMAPPED",
                        "Reward_Name": reward.reward_name,
                        "Platform": reward.platform,
                        "XP": reward.xp,
                        "Gold": reward.gold,
                        "Silver": reward.silver,
                        "Copper": reward.copper,
                        "Items": ",".join(map(str, reward.items))
                        if reward.items
                        else "",
                        "Item_Count": len(reward.items),
                    }
                )

        print(f"[INFO] Exported rewards to {output_file}")

    def print_summary(self):
        """Print summary statistics"""
        stats = self.get_stats()

        print("\n" + "=" * 80)
        print("QUEST REWARDS EXTRACTION SUMMARY")
        print("=" * 80)
        print(f"Total Rewards Found:        {stats['total_rewards']}")
        print(f"  With Quest ID:            {stats['with_quest_id']}")
        print(f"  Without Quest ID:         {stats['without_quest_id']}")
        print()
        print(f"Rewards with XP:            {stats['with_xp']}")
        print(f"Rewards with Items:         {stats['with_items']}")
        print(f"Rewards with Money:         {stats['with_money']}")
        print()
        print(f"Platforms Covered:          {stats['platforms_covered']}")
        print()

        # Show some examples
        print("Example Rewards:")
        print("-" * 80)
        for reward in self.rewards[:10]:
            quest_info = f"Quest {reward.quest_id}" if reward.quest_id else "UNMAPPED"
            items_info = f", Items: {reward.items}" if reward.items else ""
            money_info = ""
            if reward.gold or reward.silver or reward.copper:
                money_info = (
                    f", Money: {reward.gold}g {reward.silver}s {reward.copper}c"
                )

            print(
                f"  {quest_info:15} | {reward.reward_name:30} | XP: {reward.xp:5}{items_info}{money_info}"
            )
        print("=" * 80 + "\n")


def main():
    """Main entry point"""
    # Get project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent.parent

    # Path to GdsQuestRewards.lua
    lua_file = (
        project_root
        / "ModdingTools"
        / "SpellForceLUASources"
        / "script"
        / "GdsQuestRewards.lua"
    )

    if not lua_file.exists():
        print(f"[ERROR] GdsQuestRewards.lua not found at: {lua_file}")
        print(
            "[INFO] Please ensure the SpellForce Lua sources are in ModdingTools/SpellForceLUASources/"
        )
        return 1

    # Parse rewards
    parser = GdsQuestRewardsParser(lua_file, project_root)
    rewards = parser.parse()

    if not rewards:
        print("[ERROR] No rewards extracted!")
        return 1

    # Print summary
    parser.print_summary()

    # Export to JSON (for QuestDataService)
    output_dir = project_root / "src" / "TirganachReloaded" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    json_file = output_dir / "quest_rewards_complete.json"
    parser.export_to_json(json_file)

    # Export to CSV (for manual review)
    csv_file = output_dir / "quest_rewards_complete.csv"
    parser.export_to_csv(csv_file)

    print("\n[SUCCESS] Quest rewards extraction complete!")
    print(f"[INFO] JSON output: {json_file}")
    print(f"[INFO] CSV output:  {csv_file}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
