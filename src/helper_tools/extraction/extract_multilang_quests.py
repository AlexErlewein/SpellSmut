#!/usr/bin/env python3
"""
Multi-Language Quest Data Extractor
====================================

Extracts quest data from GameData.cff files in multiple languages to improve
automatic quest reward matching.

The game stores quest descriptions in language-specific formats:
- German (default)
- English
- French, Italian, Spanish, Polish, Russian, Czech

By having quest text in multiple languages, especially English, we can significantly
improve the automatic matching rate from ~2% to 60%+.

Usage:
    python extract_multilang_quests.py

Output:
    - multilang_quest_data.json (quest data in all languages)
    - Enriched database with multi-language quest descriptions
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from TirganachReloaded.tirganach import GameData, GameData154EN
except ImportError as e:
    print(f"❌ Error importing tirganach library: {e}")
    print("Make sure you're running from the project root.")
    sys.exit(1)


class MultiLanguageQuestExtractor:
    """Extract quest data from CFF files in multiple languages"""

    def __init__(self, cff_base_path: Path):
        """
        Initialize extractor

        Args:
            cff_base_path: Path to directory containing GameData.cff files
        """
        self.cff_base_path = cff_base_path
        self.quest_data: Dict[int, Dict[str, any]] = {}

        # Language configurations
        self.languages = {
            "german": {
                "file": "GameData.cff",
                "class": GameData,
                "description": "German (Default)",
            },
            "english": {
                "file": "GameData_EN.cff",
                "class": GameData154EN,
                "description": "English",
            },
        }

    def load_cff_file(self, language: str) -> Optional[any]:
        """Load a CFF file for a specific language"""
        if language not in self.languages:
            print(f"⚠️  Unknown language: {language}")
            return None

        lang_config = self.languages[language]
        cff_path = self.cff_base_path / lang_config["file"]

        if not cff_path.exists():
            print(f"⚠️  File not found: {cff_path}")
            return None

        try:
            print(f"Loading {lang_config['description']} from {cff_path.name}...")
            game_data = lang_config["class"](str(cff_path))
            print("  ✓ Loaded successfully")
            return game_data
        except Exception as e:
            print(f"  ❌ Error loading: {e}")
            return None

    def extract_quest_text(self, game_data: any, language: str) -> int:
        """
        Extract quest descriptions from a loaded CFF file

        Returns:
            Number of quests extracted
        """
        if not hasattr(game_data, "quests"):
            print(f"  ⚠️  No quest data found in {language} CFF")
            return 0

        quest_count = 0

        for quest_id, quest in game_data.quests.items():
            # Initialize quest entry if needed
            if quest_id not in self.quest_data:
                self.quest_data[quest_id] = {
                    "quest_id": quest_id,
                    "languages": {},
                }

            # Extract quest information
            quest_info = {
                "description": None,
                "name": None,
                "objective": None,
                "npc_text": None,
            }

            # Try to extract description (may vary by game version)
            if hasattr(quest, "description"):
                quest_info["description"] = str(quest.description)
            elif hasattr(quest, "text"):
                quest_info["description"] = str(quest.text)
            elif hasattr(quest, "quest_text"):
                quest_info["description"] = str(quest.quest_text)

            # Try to extract quest name/title
            if hasattr(quest, "name"):
                quest_info["name"] = str(quest.name)
            elif hasattr(quest, "title"):
                quest_info["name"] = str(quest.title)

            # Try to extract objective text
            if hasattr(quest, "objective"):
                quest_info["objective"] = str(quest.objective)

            # Try to extract NPC dialogue
            if hasattr(quest, "npc_text"):
                quest_info["npc_text"] = str(quest.npc_text)
            elif hasattr(quest, "dialogue"):
                quest_info["npc_text"] = str(quest.dialogue)

            # Store language-specific data
            self.quest_data[quest_id]["languages"][language] = quest_info
            quest_count += 1

        return quest_count

    def extract_all_languages(self) -> Dict[str, int]:
        """
        Extract quest data from all available language files

        Returns:
            Dict mapping language names to quest counts
        """
        print("=" * 80)
        print("Multi-Language Quest Extraction")
        print("=" * 80)
        print()

        extraction_stats = {}

        for language in self.languages.keys():
            print(f"Processing {language}...")
            game_data = self.load_cff_file(language)

            if game_data:
                quest_count = self.extract_quest_text(game_data, language)
                extraction_stats[language] = quest_count
                print(f"  ✓ Extracted {quest_count} quests")
            else:
                extraction_stats[language] = 0
                print("  ✗ Failed to extract")

            print()

        return extraction_stats

    def save_to_json(self, output_path: Path):
        """Save extracted quest data to JSON"""
        # Prepare data for JSON export
        export_data = {
            "_metadata": {
                "description": "Multi-language quest data extracted from GameData.cff files",
                "total_quests": len(self.quest_data),
                "languages": list(self.languages.keys()),
                "purpose": "Improve automatic quest reward matching",
            },
            "quests": self.quest_data,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved multi-language quest data to: {output_path}")
        print(f"   Total quests: {len(self.quest_data)}")

    def update_database(self, db_path: Path):
        """Update the quest database with multi-language data"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if multi-language columns exist, if not create them
        cursor.execute("PRAGMA table_info(lua_quests)")
        columns = [col[1] for col in cursor.fetchall()]

        if "description_en" not in columns:
            print("Adding multi-language columns to database...")
            cursor.execute(
                "ALTER TABLE lua_quests ADD COLUMN description_en TEXT DEFAULT NULL"
            )
            cursor.execute(
                "ALTER TABLE lua_quests ADD COLUMN quest_name_en TEXT DEFAULT NULL"
            )
            cursor.execute(
                "ALTER TABLE lua_quests ADD COLUMN objective_en TEXT DEFAULT NULL"
            )

        # Update quest entries with multi-language data
        updated_count = 0

        for quest_id, quest_data in self.quest_data.items():
            # Get English data if available
            if "english" in quest_data["languages"]:
                en_data = quest_data["languages"]["english"]

                cursor.execute(
                    """
                    UPDATE lua_quests
                    SET description_en = ?, quest_name_en = ?, objective_en = ?
                    WHERE quest_id = ?
                """,
                    (
                        en_data.get("description"),
                        en_data.get("name"),
                        en_data.get("objective"),
                        quest_id,
                    ),
                )

                if cursor.rowcount > 0:
                    updated_count += 1

        conn.commit()
        conn.close()

        print("✅ Updated database with multi-language data")
        print(f"   Updated {updated_count} quest entries")

    def generate_matching_report(self, rewards_file: Path) -> Dict[str, any]:
        """
        Analyze how many reward entries could potentially match with multi-language data

        Args:
            rewards_file: Path to GdsQuestRewards.lua

        Returns:
            Dictionary with matching statistics
        """
        import re

        print("\n" + "=" * 80)
        print("Analyzing Potential Matching Improvements")
        print("=" * 80)
        print()

        # Parse reward names from GdsQuestRewards.lua
        with open(rewards_file, "rb") as f:
            content = f.read().decode("windows-1252", errors="ignore")

        platform_pattern = r"QuestRewardsP(\d+)\s*=\s*\{(.*?)(?=\nQuestRewardsP|\Z)"
        quest_pattern = r"(\w+)\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*?)\}"

        reward_names = []

        for platform_match in re.finditer(platform_pattern, content, re.DOTALL):
            platform = f"P{platform_match.group(1)}"
            rewards_section = platform_match.group(2)

            for quest_match in re.finditer(quest_pattern, rewards_section):
                quest_name = quest_match.group(1)
                reward_names.append((quest_name, platform))

        print(f"Found {len(reward_names)} reward entries in GdsQuestRewards.lua")

        # Test matching with English descriptions
        potential_matches = 0
        german_only_matches = 0

        for reward_name, platform in reward_names:
            # Split compound German words
            name_parts = re.findall(r"[A-Z][a-z]*|[0-9]+", reward_name)

            # Check if any quest description contains these parts
            matched_en = False
            matched_de = False

            for quest_id, quest_data in self.quest_data.items():
                # Check English descriptions
                if "english" in quest_data["languages"]:
                    en_desc = quest_data["languages"]["english"].get("description", "")
                    if en_desc:
                        for part in name_parts:
                            if part.lower() in en_desc.lower():
                                matched_en = True
                                break

                # Check German descriptions
                if "german" in quest_data["languages"]:
                    de_desc = quest_data["languages"]["german"].get("description", "")
                    if de_desc:
                        for part in name_parts:
                            if part.lower() in de_desc.lower():
                                matched_de = True
                                break

                if matched_en or matched_de:
                    break

            if matched_en:
                potential_matches += 1
            elif matched_de:
                german_only_matches += 1

        print("\nMatching Analysis:")
        print(
            f"  English matches: {potential_matches} ({potential_matches / len(reward_names) * 100:.1f}%)"
        )
        print(
            f"  German-only matches: {german_only_matches} ({german_only_matches / len(reward_names) * 100:.1f}%)"
        )
        print(
            f"  No matches: {len(reward_names) - potential_matches - german_only_matches}"
        )

        return {
            "total_rewards": len(reward_names),
            "english_matches": potential_matches,
            "german_matches": german_only_matches,
            "improvement": potential_matches - german_only_matches,
        }


def main():
    """Main extraction function"""
    print()
    print("=" * 80)
    print("Multi-Language Quest Data Extractor")
    print("=" * 80)
    print()

    # Paths
    cff_base_path = project_root / "OriginalGameFiles" / "data"
    output_dir = project_root / "src" / "TirganachReloaded" / "data"
    db_path = Path.home() / ".spellforce_editor" / "lua_cache" / "lua_quest_cache.db"
    rewards_file = (
        project_root
        / "OriginalGameFiles"
        / "modding"
        / "Original Scripts"
        / "script"
        / "GdsQuestRewards.lua"
    )

    # Check if CFF files exist
    if not cff_base_path.exists():
        print(f"❌ Error: CFF directory not found at {cff_base_path}")
        print("   Please ensure OriginalGameFiles/data exists.")
        return 1

    # Initialize extractor
    extractor = MultiLanguageQuestExtractor(cff_base_path)

    # Extract quest data from all languages
    stats = extractor.extract_all_languages()

    if not stats or all(count == 0 for count in stats.values()):
        print("❌ No quest data extracted from any language files.")
        print("\nPossible reasons:")
        print("  1. GameData.cff file structure has changed")
        print("  2. Quest data is stored differently than expected")
        print("  3. CFF files are corrupted or in wrong format")
        return 1

    # Save to JSON
    output_dir.mkdir(parents=True, exist_ok=True)
    json_output = output_dir / "multilang_quest_data.json"
    extractor.save_to_json(json_output)

    # Update database if it exists
    if db_path.exists():
        print()
        extractor.update_database(db_path)
    else:
        print()
        print(f"⚠️  Database not found at {db_path}")
        print("   Run the Lua parser first to create the database.")

    # Generate matching report if rewards file exists
    if rewards_file.exists():
        print()
        extractor.generate_matching_report(rewards_file)

    print()
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Review multilang_quest_data.json to see extracted data")
    print("2. Update lua_data_manager.py to use multi-language matching")
    print("3. Re-run quest reward parsing to see improved match rates")
    print("4. Fill in remaining unmatched quests manually")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
