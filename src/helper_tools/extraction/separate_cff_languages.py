#!/usr/bin/env python3
"""
Multi-Language Separator for CFF Strings
=========================================

Separates the extracted strings from GameData.cff by language and performs
matching for each language separately. The single CFF file contains multiple
languages (German, English, Italian, French, etc.) interleaved.

This script:
1. Loads extracted strings from cff_strings_german.json (contains all languages)
2. Detects language of each string using linguistic patterns
3. Separates strings by language
4. Performs reward matching for each language
5. Combines results for maximum coverage

Usage:
    python separate_cff_languages.py

Output:
    - cff_strings_by_language.json (strings organized by language)
    - quest_matches_multilang.json (combined matches from all languages)
    - language_analysis_report.txt (detailed analysis)
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


class LanguageDetector:
    """Detect the language of text strings"""

    def __init__(self):
        # Language indicators (most distinctive words/patterns)
        self.language_patterns = {
            "German": {
                "chars": ["ä", "ö", "ü", "ß"],
                "words": [
                    "der",
                    "die",
                    "das",
                    "und",
                    "ist",
                    "mit",
                    "von",
                    "für",
                    "auf",
                    "dem",
                    "den",
                    "des",
                    "eine",
                    "einen",
                    "einem",
                    "wird",
                    "werden",
                    "wurde",
                    "sich",
                    "nicht",
                    "auch",
                ],
                "quest_words": [
                    "findet",
                    "sprecht",
                    "bringt",
                    "sammelt",
                    "tötet",
                    "geht zu",
                    "kehrt zurück",
                    "aufgabe",
                ],
            },
            "English": {
                "chars": [],
                "words": [
                    "the",
                    "and",
                    "you",
                    "your",
                    "have",
                    "will",
                    "can",
                    "with",
                    "from",
                    "that",
                    "this",
                    "they",
                    "would",
                    "there",
                    "their",
                    "about",
                ],
                "quest_words": [
                    "find",
                    "talk",
                    "bring",
                    "collect",
                    "kill",
                    "go to",
                    "return",
                    "speak",
                    "quest",
                ],
            },
            "Italian": {
                "chars": ["à", "è", "é", "ì", "ò", "ù"],
                "words": [
                    "gli",
                    "una",
                    "sono",
                    "hanno",
                    "quello",
                    "della",
                    "nella",
                    "alla",
                    "degli",
                    "anche",
                    "come",
                    "tutto",
                ],
                "quest_words": ["trova", "parla", "porta", "uccidi", "torna"],
            },
            "French": {
                "chars": ["é", "è", "ê", "ë", "à", "â", "ç", "œ"],
                "words": [
                    "les",
                    "des",
                    "une",
                    "dans",
                    "pour",
                    "avec",
                    "vous",
                    "qui",
                    "est",
                    "sont",
                    "cette",
                    "tout",
                ],
                "quest_words": [
                    "trouve",
                    "parle",
                    "apporte",
                    "collecte",
                    "tue",
                    "retour",
                ],
            },
            "Spanish": {
                "chars": ["á", "é", "í", "ó", "ú", "ñ"],
                "words": [
                    "los",
                    "las",
                    "una",
                    "del",
                    "para",
                    "con",
                    "que",
                    "está",
                    "son",
                    "todo",
                    "también",
                ],
                "quest_words": [
                    "encuentra",
                    "habla",
                    "trae",
                    "mata",
                    "regresa",
                ],
            },
            "Polish": {
                "chars": ["ą", "ć", "ę", "ł", "ń", "ó", "ś", "ź", "ż"],
                "words": [
                    "jest",
                    "się",
                    "nie",
                    "może",
                    "który",
                    "jego",
                    "można",
                    "tego",
                ],
                "quest_words": ["znajdź", "mów", "przynieś", "zbierz", "zabij"],
            },
        }

    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect the language of a text string

        Returns:
            Tuple of (language_name, confidence_score)
        """
        text_lower = text.lower()
        scores = defaultdict(float)

        for lang, patterns in self.language_patterns.items():
            # Check for special characters (very reliable)
            char_score = sum(10 for char in patterns["chars"] if char in text_lower)
            scores[lang] += char_score

            # Check for common words (reliable with word boundaries)
            for word in patterns["words"]:
                # Use word boundaries to avoid false matches
                if re.search(rf"\b{word}\b", text_lower):
                    scores[lang] += 2

            # Check for quest-specific words (bonus points)
            for word in patterns["quest_words"]:
                if word in text_lower:
                    scores[lang] += 3

        # Normalize scores
        if not scores:
            return ("Unknown", 0.0)

        best_lang = max(scores.items(), key=lambda x: x[1])
        total_score = sum(scores.values())

        if total_score == 0:
            return ("Unknown", 0.0)

        confidence = best_lang[1] / total_score

        # Require minimum confidence
        if confidence < 0.4:
            return ("Unknown", confidence)

        return (best_lang[0], confidence)


class MultiLanguageSeparator:
    """Separate and organize CFF strings by language"""

    def __init__(self, input_file: Path):
        self.input_file = input_file
        self.detector = LanguageDetector()
        self.strings_by_language: Dict[str, List[Dict]] = defaultdict(list)
        self.quest_strings_by_language: Dict[str, List[Dict]] = defaultdict(list)

    def load_and_separate(self):
        """Load strings and separate by language"""
        print("Loading extracted strings...")
        with open(self.input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"Total strings: {data['_metadata']['total_strings']:,}")
        print(f"Quest strings: {data['_metadata']['quest_strings']:,}")
        print("\nDetecting languages...")

        # Process quest strings (higher priority)
        for quest_string in data["quest_strings"]:
            lang, confidence = self.detector.detect_language(quest_string["text"])

            quest_string["language"] = lang
            quest_string["language_confidence"] = confidence

            self.quest_strings_by_language[lang].append(quest_string)

        # Show statistics
        print("\nLanguage Distribution in Quest Strings:")
        print("=" * 60)

        total_quest = sum(len(v) for v in self.quest_strings_by_language.values())
        for lang in sorted(
            self.quest_strings_by_language.keys(),
            key=lambda x: len(self.quest_strings_by_language[x]),
            reverse=True,
        ):
            count = len(self.quest_strings_by_language[lang])
            print(f"  {lang:12} {count:5,} ({count / total_quest * 100:5.1f}%)")

        return self.quest_strings_by_language

    def match_rewards_multilang(self, rewards_file: Path) -> Dict[str, Dict[str, any]]:
        """
        Match quest rewards using all languages

        Returns:
            Combined matching results from all languages
        """
        print("\n" + "=" * 60)
        print("Multi-Language Reward Matching")
        print("=" * 60)

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

                # Extract XP
                xp_match = re.search(r"XP\s*=\s*\{?\s*(\d+)\s*\}?", reward_data)
                xp = int(xp_match.group(1)) if xp_match else 0

                # Extract items
                items_match = re.search(r"Items\s*=\s*\{([^}]+)\}", reward_data)
                items = []
                if items_match:
                    items_str = items_match.group(1)
                    items = [
                        int(x.strip())
                        for x in items_str.split(",")
                        if x.strip().isdigit()
                    ]

                reward_entries.append(
                    {"name": quest_name, "platform": platform, "xp": xp, "items": items}
                )

        print(f"\nTotal reward entries: {len(reward_entries)}")

        # Match using each language
        all_matches = defaultdict(list)
        match_stats = {}

        for lang, quest_strings in self.quest_strings_by_language.items():
            if lang == "Unknown":
                continue

            print(f"\nMatching with {lang} strings ({len(quest_strings)} strings)...")

            matches = self._match_language(
                reward_entries, [qs["text"] for qs in quest_strings], lang
            )

            match_stats[lang] = {
                "total_matches": len(matches),
                "high_confidence": len([m for m in matches if m["confidence"] >= 0.7]),
            }

            # Store matches by reward name
            for match in matches:
                all_matches[match["reward_name"]].append(match)

            print(
                f"  Found {len(matches)} matches ({match_stats[lang]['high_confidence']} high-confidence)"
            )

        # Deduplicate and keep best match for each reward
        best_matches = {}
        for reward_name, matches in all_matches.items():
            # Sort by confidence, keep highest
            best = max(matches, key=lambda x: x["confidence"])
            best_matches[reward_name] = best

        print("\n" + "=" * 60)
        print(f"Combined Results: {len(best_matches)} unique reward matches")
        print("=" * 60)

        return {
            "match_statistics": match_stats,
            "best_matches": best_matches,
            "all_matches": dict(all_matches),
        }

    def _match_language(
        self, reward_entries: List[Dict], quest_strings: List[str], language: str
    ) -> List[Dict]:
        """Match rewards with quest strings for a specific language"""
        matches = []

        for reward in reward_entries:
            # Split compound words
            name_parts = re.findall(r"[A-Z][a-z]*|[0-9]+", reward["name"])

            # Search for matches
            for quest_string in quest_strings:
                matched_parts = []
                match_score = 0

                for part in name_parts:
                    if len(part) >= 3:  # Ignore very short parts
                        if part.lower() in quest_string.lower():
                            matched_parts.append(part)
                            match_score += 1

                # Calculate confidence
                if matched_parts:
                    confidence = match_score / max(len(name_parts), 1)

                    # Bonus for matching more parts
                    if match_score >= 2:
                        confidence = min(confidence * 1.2, 1.0)

                    matches.append(
                        {
                            "reward_name": reward["name"],
                            "platform": reward["platform"],
                            "xp": reward["xp"],
                            "items": reward["items"],
                            "quest_text": quest_string[:150]
                            + ("..." if len(quest_string) > 150 else ""),
                            "matched_parts": matched_parts,
                            "confidence": confidence,
                            "language": language,
                        }
                    )

        return matches

    def export_results(
        self, output_dir: Path, match_results: Dict, language_stats: Dict
    ):
        """Export separated strings and match results"""

        # Export strings by language
        strings_by_lang_file = output_dir / "cff_strings_by_language.json"

        export_data = {
            "_metadata": {
                "description": "CFF strings separated by detected language",
                "total_languages": len(self.quest_strings_by_language),
                "total_quest_strings": sum(
                    len(v) for v in self.quest_strings_by_language.values()
                ),
            },
            "languages": {
                lang: {
                    "count": len(strings),
                    "quest_strings": strings[:100],  # Sample for size
                }
                for lang, strings in self.quest_strings_by_language.items()
            },
        }

        with open(strings_by_lang_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Saved language-separated strings to: {strings_by_lang_file}")

        # Export match results
        matches_file = output_dir / "quest_matches_multilang.json"

        match_export = {
            "_metadata": {
                "description": "Quest reward matches using multi-language extraction",
                "languages_used": list(match_results["match_statistics"].keys()),
                "total_unique_matches": len(match_results["best_matches"]),
            },
            "statistics": match_results["match_statistics"],
            "best_matches": list(match_results["best_matches"].values()),
            "all_matches_by_reward": match_results["all_matches"],
        }

        with open(matches_file, "w", encoding="utf-8") as f:
            json.dump(match_export, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved multi-language matches to: {matches_file}")

        # Export analysis report
        self._generate_report(output_dir, match_results, language_stats)

    def _generate_report(self, output_dir: Path, match_results: Dict, language_stats):
        """Generate detailed analysis report"""

        report_file = output_dir / "language_analysis_report.txt"

        lines = []
        lines.append("=" * 80)
        lines.append("MULTI-LANGUAGE CFF ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Language distribution
        lines.append("LANGUAGE DISTRIBUTION:")
        lines.append("-" * 80)
        total = sum(len(v) for v in self.quest_strings_by_language.values())
        for lang in sorted(
            self.quest_strings_by_language.keys(),
            key=lambda x: len(self.quest_strings_by_language[x]),
            reverse=True,
        ):
            count = len(self.quest_strings_by_language[lang])
            lines.append(
                f"  {lang:12} {count:5,} quest strings ({count / total * 100:5.1f}%)"
            )

        # Matching statistics
        lines.append("")
        lines.append("=" * 80)
        lines.append("MATCHING STATISTICS BY LANGUAGE:")
        lines.append("-" * 80)

        for lang, stats in match_results["match_statistics"].items():
            lines.append(f"\n{lang}:")
            lines.append(f"  Total matches:        {stats['total_matches']:,}")
            lines.append(
                f"  High-confidence (≥0.7): {stats['high_confidence']:,} ({stats['high_confidence'] / stats['total_matches'] * 100:.1f}%)"
            )

        # Best matches examples
        lines.append("")
        lines.append("=" * 80)
        lines.append("TOP 20 HIGH-CONFIDENCE MATCHES:")
        lines.append("-" * 80)

        sorted_matches = sorted(
            match_results["best_matches"].values(),
            key=lambda x: (x["confidence"], x["xp"]),
            reverse=True,
        )

        for i, match in enumerate(sorted_matches[:20], 1):
            lines.append(f"\n{i}. {match['reward_name']} ({match['platform']})")
            lines.append(f"   Language: {match['language']}")
            lines.append(f"   XP: {match['xp']}, Confidence: {match['confidence']:.0%}")
            lines.append(f"   Matched: {', '.join(match['matched_parts'])}")
            lines.append(f"   Text: {match['quest_text']}")

        # Summary
        lines.append("")
        lines.append("=" * 80)
        lines.append("SUMMARY:")
        lines.append("-" * 80)
        total_rewards = 522  # From GdsQuestRewards.lua
        unique_matches = len(match_results["best_matches"])
        high_conf_matches = len(
            [
                m
                for m in match_results["best_matches"].values()
                if m["confidence"] >= 0.7
            ]
        )

        lines.append(f"Total rewards in GdsQuestRewards.lua: {total_rewards}")
        lines.append(f"Unique matches found: {unique_matches}")
        lines.append(f"High-confidence matches (≥0.7): {high_conf_matches}")
        lines.append(
            f"Match rate: {unique_matches / total_rewards * 100:.1f}% ({high_conf_matches / total_rewards * 100:.1f}% high-confidence)"
        )
        lines.append(f"Remaining unmatched: {total_rewards - unique_matches}")
        lines.append("")
        lines.append("=" * 80)

        with open(report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"✅ Saved analysis report to: {report_file}")


def main():
    """Main execution function"""

    print()
    print("=" * 80)
    print("Multi-Language CFF String Separator")
    print("=" * 80)
    print()

    # Setup paths
    project_root = Path(__file__).parent.parent.parent.parent
    data_dir = project_root / "TirganachReloaded" / "data"
    input_file = data_dir / "cff_strings_german.json"  # Contains all languages
    rewards_file = (
        project_root
        / "OriginalGameFiles"
        / "modding"
        / "Original Scripts"
        / "script"
        / "GdsQuestRewards.lua"
    )

    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        print("   Run extract_cff_strings_direct.py first!")
        return 1

    # Initialize separator
    separator = MultiLanguageSeparator(input_file)

    # Separate by language
    language_stats = separator.load_and_separate()

    # Match rewards using all languages
    if rewards_file.exists():
        match_results = separator.match_rewards_multilang(rewards_file)

        # Export results
        separator.export_results(data_dir, match_results, language_stats)
    else:
        print(f"\n⚠️  Rewards file not found: {rewards_file}")

    print()
    print("=" * 80)
    print("COMPLETE!")
    print("=" * 80)
    print("Review the generated files:")
    print("  • cff_strings_by_language.json - Strings organized by language")
    print("  • quest_matches_multilang.json - Combined matches from all languages")
    print("  • language_analysis_report.txt - Detailed analysis")
    print()
    print("Next: Integrate high-confidence matches into lua_data_manager.py")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    exit(main())
