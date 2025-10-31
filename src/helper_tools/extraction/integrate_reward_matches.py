#!/usr/bin/env python3
"""
Quest Reward Match Integrator
==============================

Integrates multi-language quest reward matches into the database.

This script:
1. Loads quest matches from quest_matches_multilang.json
2. Connects to the lua_quest_cache.db database
3. Updates quest_rewards table with matched XP, gold, and items
4. Applies matches based on confidence thresholds
5. Reports on success/failure statistics

Usage:
    python integrate_reward_matches.py [--min-confidence 0.7] [--dry-run]

Arguments:
    --min-confidence: Minimum confidence threshold (default: 0.7)
    --dry-run: Show what would be updated without making changes
    --force: Apply even medium-confidence matches
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Tuple


class RewardMatchIntegrator:
    """Integrate quest reward matches into database"""

    def __init__(self, db_path: Path, matches_file: Path):
        self.db_path = db_path
        self.matches_file = matches_file
        self.matches = None
        self.stats = {
            "total_matches": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "applied": 0,
            "skipped": 0,
            "failed": 0,
        }

    def load_matches(self):
        """Load quest matches from JSON file"""
        print(f"Loading matches from {self.matches_file.name}...")

        with open(self.matches_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # best_matches is stored as a list in the JSON
        self.matches = data["best_matches"]
        self.stats["total_matches"] = len(self.matches)

        # Count by confidence
        for match in self.matches:
            if match["confidence"] >= 0.7:
                self.stats["high_confidence"] += 1
            elif match["confidence"] >= 0.5:
                self.stats["medium_confidence"] += 1
            else:
                self.stats["low_confidence"] += 1

        print(f"✓ Loaded {self.stats['total_matches']} matches")
        print(f"  High confidence (≥0.70): {self.stats['high_confidence']}")
        print(f"  Medium confidence (0.50-0.69): {self.stats['medium_confidence']}")
        print(f"  Low confidence (<0.50): {self.stats['low_confidence']}")

    def find_quest_id(
        self, cursor, reward_name: str, platform: str, quest_text: str
    ) -> int | None:
        """
        Find quest ID by matching reward name and platform

        Args:
            cursor: Database cursor
            reward_name: Reward script name
            platform: Platform (e.g., P63)
            quest_text: Quest text snippet from match

        Returns:
            Quest ID if found, None otherwise
        """
        # Strategy 1: Try to match using quest text snippet
        # Extract a distinctive phrase from the quest text
        if len(quest_text) > 20:
            # Get first 50 chars as search term
            search_term = quest_text[:50].strip()

            cursor.execute(
                """
                SELECT quest_id FROM lua_quests
                WHERE platform = ?
                AND description LIKE ?
                LIMIT 1
            """,
                (platform, f"%{search_term}%"),
            )

            result = cursor.fetchone()
            if result:
                return result[0]

        # Strategy 2: Split reward name and search for parts
        import re

        name_parts = re.findall(r"[A-Z][a-z]*|[0-9]+", reward_name)
        name_parts = [p for p in name_parts if len(p) >= 3]

        if name_parts:
            # Build query that checks for all parts
            conditions = " AND ".join(["description LIKE ?" for _ in name_parts])
            params = [platform]
            for part in name_parts:
                params.append(f"%{part}%")

            query = f"""
                SELECT quest_id FROM lua_quests
                WHERE platform = ? AND {conditions}
                LIMIT 1
            """

            cursor.execute(query, params)
            result = cursor.fetchone()
            if result:
                return result[0]

        return None

    def apply_matches(
        self, min_confidence: float = 0.7, dry_run: bool = False
    ) -> Tuple[int, int, int]:
        """
        Apply reward matches to database

        Args:
            min_confidence: Minimum confidence threshold
            dry_run: If True, don't actually update database

        Returns:
            Tuple of (applied, skipped, failed)
        """
        print(f"\n{'DRY RUN: ' if dry_run else ''}Applying matches...")
        print(f"Minimum confidence threshold: {min_confidence:.2f}")
        print("=" * 80)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        applied = 0
        skipped = 0
        failed = 0

        # Sort by confidence (highest first) and XP (for priority)
        sorted_matches = sorted(
            self.matches,
            key=lambda x: (x["confidence"], x["xp"]),
            reverse=True,
        )

        for i, match in enumerate(sorted_matches, 1):
            # Check confidence threshold
            if match["confidence"] < min_confidence:
                skipped += 1
                continue

            # Find quest ID
            quest_id = self.find_quest_id(
                cursor, match["reward_name"], match["platform"], match["quest_text"]
            )

            if not quest_id:
                print(
                    f"  ⚠️  [{i}/{len(sorted_matches)}] Could not find quest for {match['reward_name']} ({match['platform']})"
                )
                failed += 1
                continue

            # Convert items list to JSON string
            items_json = json.dumps(match["items"]) if match["items"] else "[]"

            # Update quest rewards
            if not dry_run:
                cursor.execute(
                    """
                    UPDATE quest_rewards
                    SET xp = ?, items = ?
                    WHERE quest_id = ?
                """,
                    (match["xp"], items_json, quest_id),
                )

                if cursor.rowcount > 0:
                    applied += 1
                    if applied <= 10 or match["xp"] >= 1000:  # Show first 10 or high XP
                        print(
                            f"  ✓ [{i}/{len(sorted_matches)}] {match['reward_name']:30} (Q{quest_id}) → {match['xp']:5} XP | Conf: {match['confidence']:.0%} | Lang: {match['language']}"
                        )
                else:
                    failed += 1
            else:
                # Dry run - just show what would be updated
                applied += 1
                if applied <= 10 or match["xp"] >= 1000:
                    print(
                        f"  [DRY] [{i}/{len(sorted_matches)}] {match['reward_name']:30} (Q{quest_id}) → {match['xp']:5} XP | Conf: {match['confidence']:.0%}"
                    )

        if not dry_run:
            conn.commit()

        conn.close()

        return applied, skipped, failed

    def verify_updates(self) -> Dict[str, int]:
        """Verify that updates were applied correctly"""
        print("\nVerifying updates...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count quests with non-zero rewards
        cursor.execute(
            """
            SELECT COUNT(*) FROM quest_rewards
            WHERE xp > 0 OR gold > 0 OR items != '[]'
        """
        )
        quests_with_rewards = cursor.fetchone()[0]

        # Count quests with zero rewards
        cursor.execute(
            """
            SELECT COUNT(*) FROM quest_rewards
            WHERE xp = 0 AND gold = 0 AND items = '[]'
        """
        )
        quests_without_rewards = cursor.fetchone()[0]

        # Get sample of updated quests
        cursor.execute(
            """
            SELECT q.quest_id, q.quest_name, q.platform, r.xp, r.items
            FROM quest_rewards r
            JOIN lua_quests q ON r.quest_id = q.quest_id
            WHERE r.xp > 0
            ORDER BY r.xp DESC
            LIMIT 5
        """
        )
        samples = cursor.fetchall()

        conn.close()

        return {
            "with_rewards": quests_with_rewards,
            "without_rewards": quests_without_rewards,
            "samples": samples,
        }

    def generate_report(self, verification: Dict):
        """Generate final report"""
        print("\n" + "=" * 80)
        print("INTEGRATION REPORT")
        print("=" * 80)

        print("\nMatches Loaded:")
        print(f"  Total matches:          {self.stats['total_matches']}")
        print(f"  High confidence (≥0.7): {self.stats['high_confidence']}")
        print(f"  Medium confidence:      {self.stats['medium_confidence']}")
        print(f"  Low confidence:         {self.stats['low_confidence']}")

        print("\nApplication Results:")
        print(f"  Successfully applied:   {self.stats['applied']}")
        print(f"  Skipped (low conf):     {self.stats['skipped']}")
        print(f"  Failed (not found):     {self.stats['failed']}")

        print("\nDatabase Status:")
        print(f"  Quests with rewards:    {verification['with_rewards']}")
        print(f"  Quests without rewards: {verification['without_rewards']}")

        if verification["samples"]:
            print("\nSample Updated Quests (Top 5 by XP):")
            for quest_id, name, platform, xp, items in verification["samples"]:
                items_count = len(json.loads(items)) if items != "[]" else 0
                items_str = f", {items_count} items" if items_count > 0 else ""
                print(f"  Quest {quest_id} ({platform}): {xp} XP{items_str}")

        print("\n" + "=" * 80)
        success_rate = (
            self.stats["applied"] / (self.stats["applied"] + self.stats["failed"]) * 100
            if (self.stats["applied"] + self.stats["failed"]) > 0
            else 0
        )
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 80)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Integrate quest reward matches into database"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.7,
        help="Minimum confidence threshold (default: 0.7)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Apply medium-confidence matches (≥0.5 instead of ≥0.7)",
    )

    args = parser.parse_args()

    print()
    print("=" * 80)
    print("Quest Reward Match Integrator")
    print("=" * 80)
    print()

    # Paths
    project_root = Path(__file__).parent.parent.parent.parent
    db_path = Path.home() / ".spellforce_editor" / "lua_cache" / "lua_quest_cache.db"
    matches_file = (
        project_root / "TirganachReloaded" / "data" / "quest_matches_multilang.json"
    )

    # Check files exist
    if not db_path.exists():
        print(f"❌ Error: Database not found at {db_path}")
        print("   Run the Lua parser first to create the database.")
        return 1

    if not matches_file.exists():
        print(f"❌ Error: Matches file not found at {matches_file}")
        print("   Run separate_cff_languages.py first!")
        return 1

    # Adjust confidence threshold if --force is used
    min_confidence = 0.5 if args.force else args.min_confidence

    # Initialize integrator
    integrator = RewardMatchIntegrator(db_path, matches_file)

    # Load matches
    integrator.load_matches()

    # Apply matches
    print()
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made to the database")
        print()

    applied, skipped, failed = integrator.apply_matches(
        min_confidence=min_confidence, dry_run=args.dry_run
    )

    integrator.stats["applied"] = applied
    integrator.stats["skipped"] = skipped
    integrator.stats["failed"] = failed

    # Verify updates (skip if dry run)
    if not args.dry_run:
        verification = integrator.verify_updates()
        integrator.generate_report(verification)

        print()
        print("✅ Integration complete!")
        print()
        print("Next steps:")
        print("  1. Review medium-confidence matches with review_medium_confidence.py")
        print("  2. Re-run Lua parser to refresh quest data in editor")
        print("  3. Open CFF editor to see updated quest rewards")
    else:
        print("\n⚠️  DRY RUN COMPLETE - No changes were made")
        print("Run without --dry-run to apply changes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
