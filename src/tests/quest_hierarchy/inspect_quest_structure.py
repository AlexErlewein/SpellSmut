"""
Inspect Quest Data Structure
Examines quest elements in CFF to see what fields are actually available
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from TirganachReloaded.cff_editor.data_model import CFFDataModel


def inspect_quest_structure(cff_path):
    """Inspect the structure of quest data in CFF"""

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
    print()

    # Analyze first quest in detail
    print("DETAILED ANALYSIS OF FIRST QUEST")
    print("=" * 80)
    first_quest = quests[0]

    print("All attributes found on quest object:")
    print()

    attributes = {}
    for attr in dir(first_quest):
        if not attr.startswith("_"):
            try:
                value = getattr(first_quest, attr, None)
                if not callable(value):
                    attributes[attr] = value
                    value_type = type(value).__name__
                    value_str = str(value)
                    if len(value_str) > 60:
                        value_str = value_str[:60] + "..."
                    print(f"  {attr:30s} [{value_type:15s}] = {value_str}")
            except Exception as e:
                print(f"  {attr:30s} [ERROR] = {str(e)}")

    print()
    print(f"Total attributes: {len(attributes)}")
    print()

    # Sample multiple quests
    print("SAMPLE OF MULTIPLE QUESTS")
    print("=" * 80)

    sample_size = min(5, len(quests))
    print(f"Showing {sample_size} quests:\n")

    for i in range(sample_size):
        quest = quests[i]
        quest_id = getattr(quest, "quest_id", "Unknown")
        name = data_model.get_localised_text(quest, "name")
        if not name:
            name = getattr(quest, "name", "No name")

        print(f"Quest {i + 1}:")
        print(f"  ID: {quest_id}")
        print(f"  Name: {name}")

        # Show key fields
        for field in [
            "parent_quest_id",
            "quest_giver_id",
            "npc_id",
            "min_level",
            "required_quest_id",
            "xp_reward",
            "gold_reward",
            "name_id",
            "description_id",
            "order_index",
        ]:
            value = getattr(quest, field, None)
            if value is not None:
                print(f"  {field}: {value}")

        print()

    # Check for quest-related tables
    print("CHECKING FOR RELATED TABLES")
    print("=" * 80)

    related_tables = [
        "quest_objectives",
        "quest_requirements",
        "quest_rewards",
        "quest_dialogues",
        "quest_dialogs",
        "quest_npcs",
        "quest_items",
        "objectives",
        "requirements",
        "rewards",
    ]

    print("Looking for these tables:")
    for table_name in related_tables:
        elements = data_model.get_elements(table_name)
        if elements:
            print(f"  ✓ {table_name}: {len(elements)} entries")
        else:
            print(f"  ✗ {table_name}: Not found")

    print()

    # Check all available tables
    print("ALL AVAILABLE TABLES IN CFF")
    print("=" * 80)

    if hasattr(data_model, "game_data"):
        game_data = data_model.game_data
        print("Tables found:")
        for attr in dir(game_data):
            if not attr.startswith("_"):
                try:
                    table = getattr(game_data, attr, None)
                    if hasattr(table, "__len__"):
                        print(f"  - {attr:30s} ({len(table)} entries)")
                except:
                    pass
    print()

    # Analyze quest field patterns
    print("QUEST FIELD USAGE ANALYSIS")
    print("=" * 80)

    field_usage = {}
    common_fields = [
        "quest_id",
        "name",
        "name_id",
        "description_id",
        "parent_quest_id",
        "quest_giver_id",
        "npc_id",
        "min_level",
        "max_level",
        "required_quest_id",
        "xp_reward",
        "experience",
        "gold_reward",
        "silver_reward",
        "copper_reward",
        "item_rewards",
        "objectives",
        "requirements",
        "map",
        "platform",
        "location",
        "order_index",
        "quest_type",
        "is_main_quest",
        "is_optional",
        "repeatable",
    ]

    for field in common_fields:
        count = 0
        has_value = 0
        for quest in quests:
            if hasattr(quest, field):
                count += 1
                value = getattr(quest, field, None)
                if value is not None and value != "" and value != 0:
                    has_value += 1

        if count > 0:
            field_usage[field] = {"exists": count, "has_value": has_value}

    print("Field usage across all quests:")
    print()
    for field, usage in sorted(field_usage.items()):
        exists = usage["exists"]
        has_value = usage["has_value"]
        percent = (has_value / len(quests)) * 100
        print(
            f"  {field:25s} exists: {exists:4d}/{len(quests):4d}  has_value: {has_value:4d}/{len(quests):4d} ({percent:5.1f}%)"
        )

    print()

    # Check dialogue relationships
    print("DIALOGUE-QUEST RELATIONSHIP ANALYSIS")
    print("=" * 80)

    localisation_table = data_model.get_elements("localisation")
    if localisation_table:
        print(f"Found {len(localisation_table)} localisation entries")

        # Check dialogue entries
        dialogue_count = 0
        dialogue_with_quest_ref = 0

        for entry in localisation_table:
            if getattr(entry, "is_dialogue", False):
                dialogue_count += 1
                dialogue_name = getattr(entry, "dialogue_name", "")

                # Check if dialogue references a quest
                for quest in quests[:10]:  # Sample first 10 quests
                    quest_id = getattr(quest, "quest_id", None)
                    if quest_id and (
                        str(quest_id) in dialogue_name
                        or f"q{quest_id}" in dialogue_name.lower()
                    ):
                        dialogue_with_quest_ref += 1
                        break

        print(f"Total dialogues: {dialogue_count}")
        print(f"Dialogues referencing quests (sample): {dialogue_with_quest_ref}")
        print()

        # Sample dialogue structure
        print("Sample dialogue entry structure:")
        for entry in localisation_table:
            if getattr(entry, "is_dialogue", False):
                print("Dialogue entry attributes:")
                for attr in dir(entry):
                    if not attr.startswith("_"):
                        try:
                            value = getattr(entry, attr, None)
                            if not callable(value):
                                print(f"  {attr}: {type(value).__name__}")
                        except:
                            pass
                break
    else:
        print("No localisation table found")

    print()
    print("✓ Inspection complete")


def main():
    """Run the inspector"""

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
            print("Usage: python inspect_quest_structure.py <path_to_cff_file>")
            print()
            print("Or place spellforce.cff in: ~/Desktop/code/Others/SpellSmut/data/")
            return 1

    inspect_quest_structure(cff_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
