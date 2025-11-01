#!/usr/bin/env python3
"""
Medium-Confidence Match Reviewer
=================================

Interactive tool to review medium-confidence quest reward matches (0.5-0.69).

This tool:
1. Loads matches from quest_matches_multilang.json
2. Filters for medium-confidence matches (0.50-0.69)
3. Presents each match with context for review
4. Allows user to accept/reject/skip matches
5. Saves approved matches for integration

Usage:
    python review_medium_confidence.py [--batch-size 50]

Controls:
    y/yes   - Accept this match
    n/no    - Reject this match
    s/skip  - Skip for now
    q/quit  - Save and quit
    i/info  - Show more details
    b/back  - Go back to previous match
    ?/help  - Show help

Output:
    - approved_medium_matches.json (matches approved for integration)
    - review_session_TIMESTAMP.txt (review log)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


class MediumConfidenceReviewer:
    """Interactive reviewer for medium-confidence matches"""

    def __init__(self, matches_file: Path, output_dir: Path):
        self.matches_file = matches_file
        self.output_dir = output_dir
        self.matches = []
        self.current_index = 0
        self.session_log = []

        # Statistics
        self.stats = {
            "total": 0,
            "reviewed": 0,
            "approved": 0,
            "rejected": 0,
            "skipped": 0,
        }

        self.approved_matches = []
        self.rejected_matches = []

    def load_matches(self):
        """Load and filter medium-confidence matches"""
        print("Loading matches...")

        with open(self.matches_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Filter for medium confidence (0.5 - 0.69)
        # best_matches is stored as a list in the JSON
        all_matches = data["best_matches"]
        self.matches = [m for m in all_matches if 0.5 <= m["confidence"] < 0.7]

        # Sort by confidence (highest first) then XP
        self.matches.sort(key=lambda x: (x["confidence"], x["xp"]), reverse=True)

        self.stats["total"] = len(self.matches)

        print(f"✓ Loaded {self.stats['total']} medium-confidence matches")
        print("  Confidence range: 0.50 - 0.69")
        print()

    def display_match(self, match: Dict, index: int):
        """Display a match for review"""
        print()
        print("=" * 80)
        print(f"MATCH {index + 1} of {self.stats['total']}")
        print("=" * 80)
        print()

        print(f"Reward Name:  {match['reward_name']}")
        print(f"Platform:     {match['platform']}")
        print(f"XP:           {match['xp']}")
        print(f"Items:        {match['items'] if match['items'] else 'None'}")
        print(f"Confidence:   {match['confidence']:.0%} ({match['confidence']:.3f})")
        print(f"Language:     {match['language']}")
        print()

        print("Matched Parts:")
        print(f"  {', '.join(match['matched_parts'])}")
        print()

        print("Quest Text:")
        print("-" * 80)
        # Wrap text for readability
        text = match["quest_text"]
        words = text.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 > 78:
                print(f"  {line}")
                line = word
            else:
                line = line + " " + word if line else word
        if line:
            print(f"  {line}")
        print("-" * 80)

    def display_help(self):
        """Display help information"""
        print()
        print("COMMANDS:")
        print("  y / yes  - Accept this match (will be applied to database)")
        print("  n / no   - Reject this match (will be skipped)")
        print("  s / skip - Skip for now (can review later)")
        print("  i / info - Show additional details")
        print("  b / back - Go back to previous match")
        print("  q / quit - Save progress and quit")
        print("  ? / help - Show this help")
        print()

    def display_info(self, match: Dict):
        """Display additional match information"""
        print()
        print("ADDITIONAL INFORMATION:")
        print("-" * 80)
        print(f"Full Reward Name: {match['reward_name']}")

        # Show name breakdown
        import re

        name_parts = re.findall(r"[A-Z][a-z]*|[0-9]+", match["reward_name"])
        print(f"Name Parts: {' + '.join(name_parts)}")

        print(f"Platform: {match['platform']}")
        print(f"Language Detected: {match['language']}")
        print(f"Confidence Score: {match['confidence']:.5f}")
        print()
        print("Rewards:")
        print(f"  XP: {match['xp']}")
        if match["items"]:
            print(f"  Items: {match['items']}")
        else:
            print("  Items: None")
        print()
        print("Full Quest Text:")
        print(f"  {match['quest_text']}")
        print("-" * 80)

    def prompt_decision(self, match: Dict, index: int) -> str:
        """Prompt user for decision"""
        print()
        print(
            f"Progress: {self.stats['reviewed']}/{self.stats['total']} reviewed "
            f"({self.stats['approved']} approved, {self.stats['rejected']} rejected)"
        )
        print()

        while True:
            response = input("Decision [y/n/s/i/b/q/?]: ").strip().lower()

            if response in ["y", "yes"]:
                return "approve"
            elif response in ["n", "no"]:
                return "reject"
            elif response in ["s", "skip"]:
                return "skip"
            elif response in ["i", "info"]:
                self.display_info(match)
                continue
            elif response in ["b", "back"]:
                return "back"
            elif response in ["q", "quit"]:
                return "quit"
            elif response in ["?", "help"]:
                self.display_help()
                continue
            else:
                print("Invalid input. Type ? for help.")

    def log_decision(self, match: Dict, decision: str):
        """Log a review decision"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "reward_name": match["reward_name"],
            "platform": match["platform"],
            "xp": match["xp"],
            "confidence": match["confidence"],
            "decision": decision,
        }
        self.session_log.append(log_entry)

    def review_all(self):
        """Main review loop"""
        print()
        print("=" * 80)
        print("INTERACTIVE REVIEW SESSION")
        print("=" * 80)
        print()
        print("You will review each medium-confidence match.")
        print("Type ? for help on available commands.")
        print()
        input("Press ENTER to start...")

        while self.current_index < len(self.matches):
            match = self.matches[self.current_index]

            # Display match
            self.display_match(match, self.current_index)

            # Get decision
            decision = self.prompt_decision(match, self.current_index)

            if decision == "approve":
                self.approved_matches.append(match)
                self.stats["approved"] += 1
                self.stats["reviewed"] += 1
                self.log_decision(match, "approved")
                print("✓ Approved")
                self.current_index += 1

            elif decision == "reject":
                self.rejected_matches.append(match)
                self.stats["rejected"] += 1
                self.stats["reviewed"] += 1
                self.log_decision(match, "rejected")
                print("✗ Rejected")
                self.current_index += 1

            elif decision == "skip":
                self.stats["skipped"] += 1
                self.log_decision(match, "skipped")
                print("⊘ Skipped")
                self.current_index += 1

            elif decision == "back":
                if self.current_index > 0:
                    self.current_index -= 1
                    # Remove last review from stats
                    if self.session_log:
                        last_decision = self.session_log[-1]["decision"]
                        if last_decision == "approved":
                            self.stats["approved"] -= 1
                            self.stats["reviewed"] -= 1
                            self.approved_matches.pop()
                        elif last_decision == "rejected":
                            self.stats["rejected"] -= 1
                            self.stats["reviewed"] -= 1
                            self.rejected_matches.pop()
                        elif last_decision == "skipped":
                            self.stats["skipped"] -= 1
                        self.session_log.pop()
                    print("↶ Going back...")
                else:
                    print("Already at first match")

            elif decision == "quit":
                print()
                print("Saving progress and quitting...")
                break

    def save_results(self):
        """Save review results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save approved matches
        if self.approved_matches:
            approved_file = self.output_dir / "approved_medium_matches.json"

            export_data = {
                "_metadata": {
                    "description": "Medium-confidence matches approved during review",
                    "review_date": datetime.now().isoformat(),
                    "total_approved": len(self.approved_matches),
                    "min_confidence": min(
                        m["confidence"] for m in self.approved_matches
                    ),
                    "max_confidence": max(
                        m["confidence"] for m in self.approved_matches
                    ),
                },
                "approved_matches": self.approved_matches,
            }

            with open(approved_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            print(f"✓ Saved {len(self.approved_matches)} approved matches to:")
            print(f"  {approved_file}")

        # Save session log
        log_file = self.output_dir / f"review_session_{timestamp}.txt"

        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("MEDIUM-CONFIDENCE REVIEW SESSION LOG\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total matches reviewed: {self.stats['reviewed']}\n")
            f.write(f"Approved: {self.stats['approved']}\n")
            f.write(f"Rejected: {self.stats['rejected']}\n")
            f.write(f"Skipped: {self.stats['skipped']}\n\n")

            f.write("=" * 80 + "\n")
            f.write("REVIEW LOG\n")
            f.write("=" * 80 + "\n\n")

            for entry in self.session_log:
                f.write(f"[{entry['timestamp']}]\n")
                f.write(f"  {entry['reward_name']} ({entry['platform']})\n")
                f.write(f"  XP: {entry['xp']}, Confidence: {entry['confidence']:.3f}\n")
                f.write(f"  Decision: {entry['decision'].upper()}\n\n")

        print("✓ Saved session log to:")
        print(f"  {log_file}")

    def generate_report(self):
        """Generate final report"""
        print()
        print("=" * 80)
        print("REVIEW SESSION COMPLETE")
        print("=" * 80)
        print()

        print("Statistics:")
        print(f"  Total matches:      {self.stats['total']}")
        print(
            f"  Reviewed:           {self.stats['reviewed']} ({self.stats['reviewed'] / self.stats['total'] * 100:.1f}%)"
        )
        print(f"  Approved:           {self.stats['approved']}")
        print(f"  Rejected:           {self.stats['rejected']}")
        print(f"  Skipped:            {self.stats['skipped']}")
        print(f"  Remaining:          {self.stats['total'] - self.stats['reviewed']}")
        print()

        if self.approved_matches:
            # Calculate total XP from approved matches
            total_xp = sum(m["xp"] for m in self.approved_matches)
            print("Approved Matches Summary:")
            print(f"  Total XP:           {total_xp:,}")
            print(f"  Average XP:         {total_xp / len(self.approved_matches):.0f}")
            print(
                f"  Confidence range:   {min(m['confidence'] for m in self.approved_matches):.3f} - {max(m['confidence'] for m in self.approved_matches):.3f}"
            )
            print()

        print("Next Steps:")
        if self.approved_matches:
            print("  1. Run integrate_reward_matches.py with approved matches")
            print("     python integrate_reward_matches.py --min-confidence 0.5")
        if self.stats["skipped"] > 0:
            print(f"  2. Review {self.stats['skipped']} skipped matches later")
        if self.stats["total"] - self.stats["reviewed"] > 0:
            print(
                f"  3. Continue reviewing {self.stats['total'] - self.stats['reviewed']} remaining matches"
            )
        print()


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Review medium-confidence quest reward matches"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=0,
        help="Review only N matches (default: all)",
    )

    args = parser.parse_args()

    print()
    print("=" * 80)
    print("Medium-Confidence Match Reviewer")
    print("=" * 80)
    print()

    # Paths
    project_root = Path(__file__).parent.parent.parent.parent
    data_dir = project_root / "src" / "TirganachReloaded" / "data"
    matches_file = data_dir / "quest_matches_multilang.json"

    if not matches_file.exists():
        print(f"❌ Error: Matches file not found at {matches_file}")
        print("   Run separate_cff_languages.py first!")
        return 1

    # Initialize reviewer
    reviewer = MediumConfidenceReviewer(matches_file, data_dir)

    # Load matches
    reviewer.load_matches()

    if reviewer.stats["total"] == 0:
        print("No medium-confidence matches to review!")
        return 0

    # Limit batch size if requested
    if args.batch_size > 0 and args.batch_size < len(reviewer.matches):
        reviewer.matches = reviewer.matches[: args.batch_size]
        reviewer.stats["total"] = len(reviewer.matches)
        print(f"Limiting review to first {args.batch_size} matches")
        print()

    # Review matches
    try:
        reviewer.review_all()
    except KeyboardInterrupt:
        print()
        print()
        print("⚠️  Review interrupted by user")
        print()

    # Save results
    reviewer.save_results()

    # Generate report
    reviewer.generate_report()

    return 0


if __name__ == "__main__":
    sys.exit(main())
