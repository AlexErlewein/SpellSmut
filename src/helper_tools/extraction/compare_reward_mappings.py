#!/usr/bin/env python3
"""
Reward Mapping Comparison Tool
===============================

Compares old and new quest reward mappings to show improvements and changes.

This script:
1. Loads old reward mappings (REWARD_TO_QUEST_ID_MASTER_MAP.json)
2. Loads new Lua scan mappings (lua_reward_mappings_complete.json)
3. Compares and analyzes differences
4. Generates detailed reports showing:
   - New mappings discovered
   - Confirmed mappings (same in both)
   - Changed mappings (conflicts)
   - Coverage improvements

Usage:
    python compare_reward_mappings.py [--verbose] [--output-dir OUTPUT_DIR]
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, Tuple


class RewardMappingComparison:
    """Compare old and new reward mappings"""

    def __init__(self, old_file: Path, new_file: Path, verbose: bool = False):
        self.old_file = old_file
        self.new_file = new_file
        self.verbose = verbose

        self.old_mappings: Dict[str, str] = {}
        self.new_mappings: Dict[str, str] = {}

        self.new_discoveries: Dict[str, str] = {}
        self.confirmed: Dict[str, str] = {}
        self.conflicts: Dict[str, Tuple[str, str]] = {}
        self.lost: Dict[str, str] = {}

    def load_old_mappings(self):
        """Load old reward mappings"""
        print(f"Loading old mappings from {self.old_file.name}...")

        if not self.old_file.exists():
            print("  ⚠️  Old mappings file not found, skipping comparison")
            return

        with open(self.old_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Old format can be:
        # 1. {"mappings": {"reward": quest_id, ...}, "total": N}
        # 2. {"reward": quest_id, ...}
        if isinstance(data, dict):
            if "mappings" in data:
                # Nested format - convert quest IDs to "Q123" format
                raw_mappings = data["mappings"]
                self.old_mappings = {
                    k: f"Q{v}" if isinstance(v, int) else v
                    for k, v in raw_mappings.items()
                    if v
                }
            else:
                # Flat format
                self.old_mappings = {k: v for k, v in data.items() if v}

        print(f"  ✓ Loaded {len(self.old_mappings)} old mappings")

    def load_new_mappings(self):
        """Load new reward mappings from comprehensive scan"""
        print(f"Loading new mappings from {self.new_file.name}...")

        with open(self.new_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # New format has mappings as a list
        if "mappings" in data:
            # Build a mapping dict, preferring first occurrence
            mappings_dict = {}
            for mapping in data["mappings"]:
                reward_name = mapping["reward_name"]
                quest_id = mapping["quest_id"]

                # Skip UNKNOWN quest IDs
                if quest_id == "UNKNOWN":
                    continue

                # Use first occurrence or keep existing
                if reward_name not in mappings_dict:
                    mappings_dict[reward_name] = quest_id

            self.new_mappings = mappings_dict

        print(f"  ✓ Loaded {len(self.new_mappings)} new mappings")

    def compare_mappings(self):
        """Compare old and new mappings"""
        print("\nComparing mappings...")

        old_rewards = set(self.old_mappings.keys())
        new_rewards = set(self.new_mappings.keys())

        # New discoveries: in new but not in old
        new_reward_names = new_rewards - old_rewards
        self.new_discoveries = {
            name: self.new_mappings[name] for name in new_reward_names
        }

        # Lost: in old but not in new
        lost_reward_names = old_rewards - new_rewards
        self.lost = {name: self.old_mappings[name] for name in lost_reward_names}

        # Check overlapping rewards for conflicts or confirmation
        overlapping = old_rewards & new_rewards
        for name in overlapping:
            old_quest = self.old_mappings[name]
            new_quest = self.new_mappings[name]

            if old_quest == new_quest:
                self.confirmed[name] = old_quest
            else:
                self.conflicts[name] = (old_quest, new_quest)

        print("  ✓ Analysis complete")

    def generate_summary(self) -> Dict:
        """Generate comparison summary"""
        total_old = len(self.old_mappings)
        total_new = len(self.new_mappings)

        improvement = total_new - total_old
        improvement_pct = (improvement / total_old * 100) if total_old > 0 else 0

        return {
            "old_count": total_old,
            "new_count": total_new,
            "improvement": improvement,
            "improvement_pct": improvement_pct,
            "new_discoveries": len(self.new_discoveries),
            "confirmed": len(self.confirmed),
            "conflicts": len(self.conflicts),
            "lost": len(self.lost),
        }

    def print_report(self):
        """Print detailed comparison report"""
        summary = self.generate_summary()

        print("\n" + "=" * 80)
        print("REWARD MAPPING COMPARISON REPORT")
        print("=" * 80)

        print("\n📊 Summary:")
        print(f"  Old mappings:       {summary['old_count']:4}")
        print(f"  New mappings:       {summary['new_count']:4}")
        print(
            f"  Improvement:        {summary['improvement']:+4} ({summary['improvement_pct']:+.1f}%)"
        )
        print()
        print(f"  New discoveries:    {summary['new_discoveries']:4} ✨")
        print(f"  Confirmed matches:  {summary['confirmed']:4} ✓")
        print(f"  Conflicts:          {summary['conflicts']:4} ⚠️")
        print(f"  Lost mappings:      {summary['lost']:4} ❌")

        # Show sample new discoveries
        if self.new_discoveries:
            print("\n🆕 Sample New Discoveries (first 20):")
            for i, (name, quest_id) in enumerate(
                list(self.new_discoveries.items())[:20], 1
            ):
                print(f"  {i:2}. {name:40} → {quest_id}")

        # Show conflicts if any
        if self.conflicts:
            print(f"\n⚠️  Conflicts Found ({len(self.conflicts)}):")
            for name, (old_id, new_id) in list(self.conflicts.items())[:20]:
                print(f"  {name:40} | Old: {old_id:8} → New: {new_id:8}")

            if len(self.conflicts) > 20:
                print(f"  ... and {len(self.conflicts) - 20} more")

        # Show lost mappings if significant
        if self.lost and len(self.lost) > 5:
            print(f"\n❌ Lost Mappings ({len(self.lost)}):")
            for name, quest_id in list(self.lost.items())[:10]:
                print(f"  {name:40} → {quest_id}")

            if len(self.lost) > 10:
                print(f"  ... and {len(self.lost) - 10} more")

        print("\n" + "=" * 80)

    def save_reports(self, output_dir: Path):
        """Save detailed reports to files"""
        output_dir.mkdir(parents=True, exist_ok=True)

        summary = self.generate_summary()

        # 1. Save summary as JSON
        summary_file = output_dir / "mapping_comparison_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "summary": summary,
                    "new_discoveries": self.new_discoveries,
                    "confirmed": self.confirmed,
                    "conflicts": self.conflicts,
                    "lost": self.lost,
                },
                f,
                indent=2,
            )
        print(f"\n✓ Saved summary to {summary_file.name}")

        # 2. Save new discoveries as CSV
        if self.new_discoveries:
            new_disc_file = output_dir / "new_discoveries.csv"
            with open(new_disc_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["reward_name", "quest_id"])
                for name, quest_id in sorted(self.new_discoveries.items()):
                    writer.writerow([name, quest_id])
            print(
                f"✓ Saved {len(self.new_discoveries)} new discoveries to {new_disc_file.name}"
            )

        # 3. Save conflicts report
        if self.conflicts:
            conflicts_file = output_dir / "mapping_conflicts.csv"
            with open(conflicts_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["reward_name", "old_quest_id", "new_quest_id", "note"])
                for name, (old_id, new_id) in sorted(self.conflicts.items()):
                    writer.writerow([name, old_id, new_id, "Review needed"])
            print(f"✓ Saved {len(self.conflicts)} conflicts to {conflicts_file.name}")

        # 4. Create merged/best mapping
        merged = {}

        # Start with confirmed matches
        merged.update(self.confirmed)

        # Add new discoveries
        merged.update(self.new_discoveries)

        # For conflicts, prefer new mappings (from comprehensive scan)
        for name, (old_id, new_id) in self.conflicts.items():
            merged[name] = new_id  # Prefer new scan results

        merged_file = output_dir / "reward_to_quest_merged.json"
        with open(merged_file, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, sort_keys=True)
        print(f"✓ Saved {len(merged)} merged mappings to {merged_file.name}")

        # 5. Create detailed text report
        report_file = output_dir / "comparison_report.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("Reward Mapping Comparison Report\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Old mappings: {summary['old_count']}\n")
            f.write(f"New mappings: {summary['new_count']}\n")
            f.write(
                f"Improvement:  {summary['improvement']:+} ({summary['improvement_pct']:+.1f}%)\n\n"
            )

            f.write(f"New discoveries: {summary['new_discoveries']}\n")
            f.write(f"Confirmed:       {summary['confirmed']}\n")
            f.write(f"Conflicts:       {summary['conflicts']}\n")
            f.write(f"Lost:            {summary['lost']}\n\n")

            if self.new_discoveries:
                f.write("\nNew Discoveries:\n")
                f.write("-" * 80 + "\n")
                for name, quest_id in sorted(self.new_discoveries.items()):
                    f.write(f"{name:50} → {quest_id}\n")

            if self.conflicts:
                f.write("\n\nConflicts (Old → New):\n")
                f.write("-" * 80 + "\n")
                for name, (old_id, new_id) in sorted(self.conflicts.items()):
                    f.write(f"{name:50} | {old_id:8} → {new_id:8}\n")

            if self.lost:
                f.write("\n\nLost Mappings:\n")
                f.write("-" * 80 + "\n")
                for name, quest_id in sorted(self.lost.items()):
                    f.write(f"{name:50} → {quest_id}\n")

        print(f"✓ Saved detailed report to {report_file.name}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Compare old and new reward mappings")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for reports (default: TirganachReloaded/data)",
    )

    args = parser.parse_args()

    # Paths
    project_root = Path(__file__).parent.parent.parent.parent
    data_dir = project_root / "TirganachReloaded" / "data"

    old_file = data_dir / "REWARD_TO_QUEST_ID_MASTER_MAP.json"
    new_file = data_dir / "lua_reward_mappings_complete.json"

    # Check if new file exists
    if not new_file.exists():
        print(f"❌ Error: New mappings file not found at {new_file}")
        print("   Run scan_all_reward_flags.py first!")
        return 1

    # Set output directory
    output_dir = args.output_dir or data_dir

    print("=" * 80)
    print("Reward Mapping Comparison Tool")
    print("=" * 80)
    print()

    # Initialize comparison
    comparison = RewardMappingComparison(old_file, new_file, verbose=args.verbose)

    # Load data
    comparison.load_old_mappings()
    comparison.load_new_mappings()

    # Compare
    comparison.compare_mappings()

    # Print report
    comparison.print_report()

    # Save reports
    comparison.save_reports(output_dir)

    print(f"\n✅ Comparison complete! Reports saved to: {output_dir}")
    print("\nNext steps:")
    print("  1. Review mapping_conflicts.csv for any conflicts")
    print("  2. Use reward_to_quest_merged.json as your new master mapping")
    print("  3. Update your database with the new mappings")
    print("  4. Celebrate the improvement! 🎉")

    return 0


if __name__ == "__main__":
    sys.exit(main())
