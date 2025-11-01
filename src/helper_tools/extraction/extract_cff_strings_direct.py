#!/usr/bin/env python3
"""
Direct CFF String Extractor
============================

Extracts readable strings directly from GameData.cff binary files without
using the tirganach library. This is useful for extracting quest descriptions
and other text in multiple languages.

This tool:
1. Reads CFF files as binary data
2. Extracts all readable strings (sequences of printable characters)
3. Identifies potential quest text based on patterns
4. Exports strings to JSON for multi-language matching

Usage:
    python extract_cff_strings_direct.py

Output:
    - cff_strings_german.json (strings from German GameData.cff)
    - cff_strings_english.json (strings from English GameData.cff if available)
    - cff_quest_strings.txt (human-readable quest strings)
"""

import json
import re
from pathlib import Path
from typing import Dict, List


class DirectCFFStringExtractor:
    """Extract strings directly from CFF binary files"""

    def __init__(self):
        self.min_string_length = 10  # Minimum length for a valid string
        self.max_string_length = 500  # Maximum length to avoid binary garbage

    def extract_strings_from_binary(
        self, file_path: Path, encoding="cp1252"
    ) -> List[str]:
        """
        Extract all readable strings from a binary file

        Args:
            file_path: Path to CFF file
            encoding: Text encoding (cp1252/windows-1252 for German, latin1 for English)

        Returns:
            List of extracted strings
        """
        print(f"Reading {file_path.name}...")

        with open(file_path, "rb") as f:
            data = f.read()

        print(f"  File size: {len(data):,} bytes")

        strings = []
        current_string = bytearray()

        # Extract sequences of printable characters
        for byte in data:
            # Check if byte is printable (or common whitespace)
            if (32 <= byte <= 126) or byte in [
                9,
                10,
                13,
            ]:  # Printable ASCII + tab/newline
                current_string.append(byte)
            else:
                # End of string sequence
                if len(current_string) >= self.min_string_length:
                    try:
                        text = current_string.decode(encoding, errors="ignore").strip()
                        if (
                            len(text) >= self.min_string_length
                            and len(text) <= self.max_string_length
                        ):
                            # Filter out strings that are mostly special characters
                            alpha_ratio = sum(
                                c.isalpha() or c.isspace() for c in text
                            ) / len(text)
                            if alpha_ratio > 0.5:  # At least 50% letters/spaces
                                strings.append(text)
                    except:
                        pass
                current_string = bytearray()

        # Don't forget the last string
        if len(current_string) >= self.min_string_length:
            try:
                text = current_string.decode(encoding, errors="ignore").strip()
                if (
                    len(text) >= self.min_string_length
                    and len(text) <= self.max_string_length
                ):
                    alpha_ratio = sum(c.isalpha() or c.isspace() for c in text) / len(
                        text
                    )
                    if alpha_ratio > 0.5:
                        strings.append(text)
            except:
                pass

        # Deduplicate while preserving order
        seen = set()
        unique_strings = []
        for s in strings:
            if s not in seen:
                seen.add(s)
                unique_strings.append(s)

        print(f"  Extracted {len(unique_strings):,} unique strings")
        return unique_strings

    def identify_quest_strings(self, strings: List[str]) -> List[Dict[str, str]]:
        """
        Identify strings that are likely quest-related

        Returns:
            List of dicts with quest strings and metadata
        """
        quest_strings = []

        # Quest-related keywords (German and English)
        quest_keywords = [
            # German
            "quest",
            "aufgabe",
            "mission",
            "sucht",
            "findet",
            "sprecht",
            "bringt",
            "sammelt",
            "tötet",
            "geht zu",
            "kehrt zurück",
            # English
            "find",
            "talk",
            "bring",
            "collect",
            "kill",
            "go to",
            "return",
            "speak",
            "gather",
            "defeat",
            "retrieve",
            "deliver",
            # Common quest NPCs
            "darius",
            "rohen",
            "lya",
            "dunhan",
            "jared",
            "uram",
        ]

        for string in strings:
            string_lower = string.lower()

            # Check if string contains quest keywords
            is_quest = False
            matched_keywords = []

            for keyword in quest_keywords:
                if keyword in string_lower:
                    is_quest = True
                    matched_keywords.append(keyword)

            # Also check for quest patterns
            if not is_quest:
                # Questions often indicate quests
                if "?" in string or string.endswith("!"):
                    is_quest = True
                    matched_keywords.append("question/exclamation")

                # Multi-sentence text
                if string.count(".") >= 2 or string.count("!") >= 2:
                    is_quest = True
                    matched_keywords.append("multi-sentence")

            if is_quest and len(string) >= 20:  # Meaningful quest text
                quest_strings.append(
                    {
                        "text": string,
                        "length": len(string),
                        "keywords": matched_keywords,
                    }
                )

        return quest_strings

    def match_with_rewards(
        self, quest_strings: List[str], rewards_file: Path, language: str
    ) -> Dict:
        """
        Attempt to match quest strings with reward names from GdsQuestRewards.lua

        Returns:
            Dictionary with matching statistics and potential matches
        """
        print(f"\nMatching {language} strings with reward names...")

        # Parse reward names
        with open(rewards_file, "rb") as f:
            content = f.read().decode("windows-1252", errors="ignore")

        platform_pattern = r"QuestRewardsP(\d+)\s*=\s*\{(.*?)(?=\nQuestRewardsP|\Z)"
        quest_pattern = r"(\w+)\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*?)\}"

        reward_entries = []

        for platform_match in re.finditer(platform_pattern, content, re.DOTALL):
            platform = f"P{platform_match.group(1)}"
            rewards_section = platform_match.group(2)

            for quest_match in re.finditer(quest_pattern, rewards_section):
                quest_name = quest_match.group(1)
                reward_data = quest_match.group(2)

                # Extract XP for priority
                xp_match = re.search(r"XP\s*=\s*\{?\s*(\d+)\s*\}?", reward_data)
                xp = int(xp_match.group(1)) if xp_match else 0

                reward_entries.append(
                    {"name": quest_name, "platform": platform, "xp": xp}
                )

        print(f"  Found {len(reward_entries)} reward entries")

        # Try to match
        potential_matches = []

        for reward in reward_entries:
            # Split compound German words
            name_parts = re.findall(r"[A-Z][a-z]*|[0-9]+", reward["name"])

            # Search for strings containing these parts
            for quest_string in quest_strings:
                matches = 0
                matched_parts = []

                for part in name_parts:
                    if len(part) >= 3:  # Ignore very short parts
                        if part.lower() in quest_string.lower():
                            matches += 1
                            matched_parts.append(part)

                # If we matched multiple parts, this is likely a match
                if matches >= 2 or (matches >= 1 and len(name_parts) == 1):
                    potential_matches.append(
                        {
                            "reward_name": reward["name"],
                            "platform": reward["platform"],
                            "xp": reward["xp"],
                            "quest_text": quest_string[:150]
                            + ("..." if len(quest_string) > 150 else ""),
                            "matched_parts": matched_parts,
                            "confidence": matches / max(len(name_parts), 1),
                        }
                    )

        print(f"  Found {len(potential_matches)} potential matches")

        return {
            "total_rewards": len(reward_entries),
            "total_quest_strings": len(quest_strings),
            "potential_matches": len(potential_matches),
            "matches": potential_matches,
        }

    def export_to_json(self, strings: List[str], output_path: Path, language: str):
        """Export extracted strings to JSON"""

        # Categorize strings
        quest_strings = self.identify_quest_strings(strings)

        export_data = {
            "_metadata": {
                "language": language,
                "total_strings": len(strings),
                "quest_strings": len(quest_strings),
                "min_length": self.min_string_length,
                "max_length": self.max_string_length,
            },
            "quest_strings": quest_strings,
            "all_strings": strings[
                :5000
            ],  # Limit to first 5000 to keep file manageable
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Exported to {output_path}")
        print(f"   Total strings: {len(strings):,}")
        print(f"   Quest strings: {len(quest_strings):,}")

    def export_readable_list(
        self, quest_strings: List[Dict], output_path: Path, language: str
    ):
        """Export quest strings to readable text file"""

        lines = []
        lines.append("=" * 80)
        lines.append(f"QUEST STRINGS EXTRACTED FROM {language.upper()} CFF")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Total quest-related strings: {len(quest_strings)}")
        lines.append("")

        # Sort by length (longer strings first, likely more important)
        sorted_strings = sorted(quest_strings, key=lambda x: x["length"], reverse=True)

        for idx, entry in enumerate(sorted_strings[:200], 1):  # Top 200
            lines.append(f"\n{'-' * 80}")
            lines.append(
                f"String #{idx} (Length: {entry['length']}, Keywords: {', '.join(entry['keywords'])})"
            )
            lines.append(f"{'-' * 80}")
            lines.append(entry["text"])

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"✅ Exported readable list to {output_path}")


def main():
    """Main extraction function"""

    print()
    print("=" * 80)
    print("Direct CFF String Extractor")
    print("=" * 80)
    print()

    # Setup paths
    project_root = Path(__file__).parent.parent.parent.parent
    cff_dir = project_root / "OriginalGameFiles" / "data"
    output_dir = project_root / "src" / "TirganachReloaded" / "data"
    rewards_file = (
        project_root
        / "OriginalGameFiles"
        / "modding"
        / "Original Scripts"
        / "script"
        / "GdsQuestRewards.lua"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize extractor
    extractor = DirectCFFStringExtractor()

    # Process German CFF (default)
    german_cff = cff_dir / "GameData.cff"
    if german_cff.exists():
        print("Processing German GameData.cff...")
        print("-" * 80)

        german_strings = extractor.extract_strings_from_binary(
            german_cff, encoding="cp1252"
        )
        quest_strings_de = extractor.identify_quest_strings(german_strings)

        # Export
        extractor.export_to_json(
            german_strings, output_dir / "cff_strings_german.json", "German"
        )

        extractor.export_readable_list(
            quest_strings_de, output_dir / "cff_quest_strings_german.txt", "German"
        )

        # Match with rewards
        if rewards_file.exists():
            match_results_de = extractor.match_with_rewards(
                [s["text"] for s in quest_strings_de], rewards_file, "German"
            )

            # Save match results
            with open(
                output_dir / "quest_matches_german.json", "w", encoding="utf-8"
            ) as f:
                json.dump(match_results_de, f, indent=2, ensure_ascii=False)

            print("\n📊 German Matching Results:")
            print(f"   Potential matches: {match_results_de['potential_matches']}")
            print(
                f"   Match rate: {match_results_de['potential_matches'] / match_results_de['total_rewards'] * 100:.1f}%"
            )

        print()

    # Process English CFF if available
    english_cff = cff_dir / "GameData_EN.cff"
    if english_cff.exists():
        print("Processing English GameData_EN.cff...")
        print("-" * 80)

        english_strings = extractor.extract_strings_from_binary(
            english_cff, encoding="latin1"
        )
        quest_strings_en = extractor.identify_quest_strings(english_strings)

        # Export
        extractor.export_to_json(
            english_strings, output_dir / "cff_strings_english.json", "English"
        )

        extractor.export_readable_list(
            quest_strings_en, output_dir / "cff_quest_strings_english.txt", "English"
        )

        # Match with rewards
        if rewards_file.exists():
            match_results_en = extractor.match_with_rewards(
                [s["text"] for s in quest_strings_en], rewards_file, "English"
            )

            # Save match results
            with open(
                output_dir / "quest_matches_english.json", "w", encoding="utf-8"
            ) as f:
                json.dump(match_results_en, f, indent=2, ensure_ascii=False)

            print("\n📊 English Matching Results:")
            print(f"   Potential matches: {match_results_en['potential_matches']}")
            print(
                f"   Match rate: {match_results_en['potential_matches'] / match_results_en['total_rewards'] * 100:.1f}%"
            )

        print()
    else:
        print("⚠️  English CFF not found - skipping English extraction")
        print(f"   Looking for: {english_cff}")
        print()

    print("=" * 80)
    print("SUMMARY & NEXT STEPS")
    print("=" * 80)
    print()
    print("✅ Extracted strings from CFF file(s)")
    print("✅ Identified quest-related text")
    print("✅ Generated matching analysis")
    print()
    print("Review the generated files:")
    print("  • cff_strings_*.json - All extracted strings")
    print("  • cff_quest_strings_*.txt - Human-readable quest text")
    print("  • quest_matches_*.json - Potential reward matches")
    print()
    print("Next steps:")
    print("  1. Review the quest strings to see quality")
    print("  2. Use high-confidence matches to improve automatic matching")
    print("  3. Update lua_data_manager.py to use multi-language matching")
    print("  4. Manually map remaining unmatched quests")
    print()
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit(main())
