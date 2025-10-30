"""
Find Quests with Player Dialogue Choices
Scans CFF file to identify quests that have player-choosable dialogue options
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from TirganachReloaded.cff_editor.data_model import CFFDataModel


def find_quests_with_player_choices(cff_path):
    """Find all quests that have player dialogue choices"""

    print(f"Loading: {cff_path}")
    print("=" * 80)

    data_model = CFFDataModel()

    if not data_model.load_file(cff_path):
        print("ERROR: Failed to load CFF file")
        return

    print("✓ CFF file loaded successfully")
    print()

    # Get all quests
    quests = data_model.get_elements("quests")
    if not quests:
        print("No quests found in CFF file")
        return

    print(f"Found {len(quests)} quests")
    print("Scanning for player dialogue choices...")
    print()

    # Get all localisation entries
    localisation_table = data_model.get_elements("localisation")
    if not localisation_table:
        print("No localisation data found")
        return

    # Build dialogue index
    print("Building dialogue index...")
    dialogues_by_name = {}
    player_dialogues = set()

    for entry in localisation_table:
        if getattr(entry, "is_dialogue", False):
            dialogue_name = getattr(entry, "dialogue_name", "")
            text = getattr(entry, "text", "")
            speaker = getattr(entry, "speaker", "NPC")
            language = getattr(entry, "language", None)

            if dialogue_name and text:
                if dialogue_name not in dialogues_by_name:
                    dialogues_by_name[dialogue_name] = []

                dialogues_by_name[dialogue_name].append(
                    {"text": text, "speaker": speaker, "language": language}
                )

                # Track player dialogues
                if speaker and "player" in speaker.lower():
                    player_dialogues.add(dialogue_name)

    print(f"Found {len(dialogues_by_name)} unique dialogues")
    print(f"Found {len(player_dialogues)} player dialogue choices")
    print()

    # Check each quest for player dialogues
    print("QUESTS WITH PLAYER DIALOGUE CHOICES")
    print("=" * 80)

    quests_with_choices = []

    for quest in quests:
        quest_id = getattr(quest, "quest_id", None)
        if quest_id is None:
            continue

        # Get quest name
        quest_name = data_model.get_localised_text(quest, "name")
        if not quest_name:
            quest_name = getattr(quest, "name", f"Quest {quest_id}")

        # Look for dialogues related to this quest
        quest_dialogues = []
        player_choices = []

        for dialogue_name in dialogues_by_name.keys():
            # Check if dialogue is related to this quest (heuristic)
            if (
                str(quest_id) in dialogue_name
                or f"q{quest_id}" in dialogue_name.lower()
                or f"quest{quest_id}" in dialogue_name.lower()
            ):
                quest_dialogues.append(dialogue_name)

                # Check if it's a player dialogue
                if dialogue_name in player_dialogues:
                    player_choices.append(dialogue_name)

        if player_choices:
            quests_with_choices.append(
                {
                    "quest_id": quest_id,
                    "quest_name": quest_name,
                    "total_dialogues": len(quest_dialogues),
                    "player_choices": player_choices,
                }
            )

    # Print results
    if quests_with_choices:
        print(
            f"Found {len(quests_with_choices)} quests with player dialogue choices:\n"
        )

        for quest_info in quests_with_choices:
            print(f"Quest ID: {quest_info['quest_id']}")
            print(f"Quest Name: {quest_info['quest_name']}")
            print(f"Total Dialogues: {quest_info['total_dialogues']}")
            print(f"Player Choices: {len(quest_info['player_choices'])}")
            print("Player Dialogue Names:")
            for choice in quest_info["player_choices"]:
                print(f"  - {choice}")
            print("-" * 80)
            print()
    else:
        print("No quests found with player dialogue choices.")
        print()
        print("This might mean:")
        print("- Player dialogues are not marked with a 'speaker' field")
        print("- Dialogue-quest relationships are defined differently")
        print("- No quests currently have branching dialogues")
        print()

    # Additional analysis
    print()
    print("ADDITIONAL ANALYSIS")
    print("=" * 80)
    print(f"Total quests: {len(quests)}")
    print(
        f"Quests with any dialogues: {len([q for q in quests if any(str(getattr(q, 'quest_id', 0)) in d for d in dialogues_by_name.keys())])}"
    )
    print(f"Quests with player choices: {len(quests_with_choices)}")
    print()

    # Show sample of all dialogues
    print("SAMPLE OF ALL DIALOGUES (first 20):")
    print("=" * 80)
    for i, (dialogue_name, entries) in enumerate(list(dialogues_by_name.items())[:20]):
        if entries:
            first_entry = entries[0]
            speaker = first_entry.get("speaker", "Unknown")
            text_preview = (
                first_entry.get("text", "")[:60] + "..."
                if len(first_entry.get("text", "")) > 60
                else first_entry.get("text", "")
            )
            print(f"{dialogue_name} [{speaker}]: {text_preview}")

    print()
    print(f"... and {len(dialogues_by_name) - 20} more dialogues")
    print()

    # Check dialogue structure
    print("DIALOGUE FIELD ANALYSIS")
    print("=" * 80)
    if localisation_table:
        sample_dialogue = None
        for entry in localisation_table:
            if getattr(entry, "is_dialogue", False):
                sample_dialogue = entry
                break

        if sample_dialogue:
            print("Sample dialogue entry has these fields:")
            for attr in dir(sample_dialogue):
                if not attr.startswith("_"):
                    value = getattr(sample_dialogue, attr, None)
                    if value is not None and not callable(value):
                        print(f"  - {attr}: {type(value).__name__}")
        else:
            print("No dialogue entries found in localisation table")

    print()
    print("✓ Analysis complete")


def main():
    """Run the quest scanner"""

    # Check for CFF file argument
    if len(sys.argv) > 1:
        cff_path = sys.argv[1]
    else:
        # Try default path
        default_path = (
            Path.home()
            / "Desktop"
            / "code"
            / "Others"
            / "SpellSmut"
            / "data"
            / "spellforce.cff"
        )
        if default_path.exists():
            cff_path = str(default_path)
        else:
            print("Usage: python find_quests_with_player_choices.py <path_to_cff_file>")
            print()
            print("Or place spellforce.cff in: ~/Desktop/code/Others/SpellSmut/data/")
            return 1

    find_quests_with_player_choices(cff_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
