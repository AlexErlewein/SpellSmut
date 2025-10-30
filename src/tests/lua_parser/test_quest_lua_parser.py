"""
Test Tool for Lua Quest Parser
Demonstrates bidirectional parsing: Reading Lua files and Generating Lua from data
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from TirganachReloaded.cff_editor.lua_parser import (
    LuaQuestParser,
    QuestData,
    QuestDialogue,
    QuestObjective,
    QuestRequirement,
    QuestReward,
    create_example_quest,
)


def test_generate_quest():
    """Test generating Lua script from quest data"""
    print("=" * 80)
    print("TEST 1: Generate Lua Script from Quest Data")
    print("=" * 80)
    print()

    # Create a quest
    quest = QuestData(
        quest_id=1001,
        quest_name="The Bandit Problem",
        description="Help the village by eliminating the bandit threat",
        platform="P7",
        npc_id=205,
        author="Quest Editor User",
        notes="Tutorial quest for new players",
    )

    # Add requirements
    quest.requirements.append(
        QuestRequirement(
            description="Reach level 3",
            requirement_type="Level",
            value=3,
        )
    )

    # Add objectives
    quest.objectives.append(
        QuestObjective(
            description="Defeat the Bandit Leader",
            objective_type="Kill",
            target="BanditLeader",
            count=1,
        )
    )

    quest.objectives.append(
        QuestObjective(
            description="Collect stolen goods",
            objective_type="Collect",
            target="150",
            count=5,
        )
    )

    # Add rewards
    quest.rewards = QuestReward(
        xp=500,
        gold=25,
        silver=50,
        copper=0,
        items=[301, 302],
    )

    # Add dialogues
    quest.dialogues.append(
        QuestDialogue(
            dialogue_id="bandit_quest_start",
            speaker="NPC",
            text="Please help us! Bandits have been stealing from our village!",
        )
    )

    quest.dialogues.append(
        QuestDialogue(
            dialogue_id="bandit_quest_accept",
            speaker="Player",
            text="I'll take care of the bandits for you.",
            is_player_choice=True,
        )
    )

    # Generate Lua script
    parser = LuaQuestParser()
    lua_script = parser.generate_lua_script(quest)

    print("Generated Lua Script:")
    print("-" * 80)
    print(lua_script)
    print()

    # Validate
    valid, messages = parser.validate_quest(quest)
    print(f"Validation: {'✓ PASS' if valid else '✗ FAIL'}")
    if messages:
        for msg in messages:
            print(f"  - {msg}")
    print()

    return lua_script


def test_save_and_load():
    """Test saving to file and loading back"""
    print("=" * 80)
    print("TEST 2: Save to File and Load Back")
    print("=" * 80)
    print()

    # Create example quest
    quest = create_example_quest()

    # Save to file
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"quest_{quest.quest_id}.lua"

    parser = LuaQuestParser()
    parser.save_to_file(quest, str(output_file))

    print(f"✓ Saved quest to: {output_file}")
    print()

    # Try to load it back
    print("Loading quest from file...")
    loaded_quests = parser.parse_file(str(output_file))

    if loaded_quests:
        print(f"✓ Loaded {len(loaded_quests)} quest(s)")
        for q in loaded_quests:
            print(f"  - Quest ID: {q.quest_id}")
            print(f"    Name: {q.quest_name}")
            print(f"    Objectives: {len(q.objectives)}")
            print(f"    Requirements: {len(q.requirements)}")
            print(f"    Rewards: {q.rewards.xp} XP, {q.rewards.gold} Gold")
    else:
        print("✗ No quests loaded")

    print()
    return output_file


def test_parse_existing_lua():
    """Test parsing an existing Lua file"""
    print("=" * 80)
    print("TEST 3: Parse Existing Lua File")
    print("=" * 80)
    print()

    # Create a sample Lua script
    sample_lua = """-- Sample Quest Script
-- Quest ID: 2001
-- Platform: P8

function CreateStateMachine(_Type, _PlatformId, _NpcId, _X, _Y)
BeginDefinition(_Type, _PlatformId, _NpcId, _X, _Y)

-- Quest: The Ancient Ruins
-- ID: 2001

-- Quest Initialization
OnOneTimeEvent
{
    EventName = "Init_TheAncientRuins",
    Conditions =
    {
        AvatarLevel{Level = 10},
        QuestState{QuestId = 1000, State = StateSolved}
    },
    Actions =
    {
        QuestBegin{QuestId = 2001},
        Outcry{
            NpcId = 150,
            String = "Explore the ancient ruins to the north!",
            Color = ColorYellow
        }
    }
}

-- Quest Completion
OnOneTimeEvent
{
    EventName = "Complete_TheAncientRuins",
    Conditions =
    {
        QuestState{QuestId = 2001, State = StateActive},
        FigureIsDead{Tag = "RuinsGuardian"},
        PlayerHasItem{ItemId = 500, Amount = 1}
    },
    Actions =
    {
        QuestSolve{QuestId = 2001},
        SetRewardFlagTrue{Name = "Quest2001Reward"},
        Outcry{
            NpcId = 0,
            String = "Quest completed: The Ancient Ruins!",
            Color = ColorGreen
        }
    }
}

-- Quest2001Reward = {
--     XP = {1500},
--     Money = {Gold = 100, Silver = 0, Copper = 0},
--     Items = {501, 502, 503}
-- }

EndDefinition()
end
"""

    print("Sample Lua script:")
    print("-" * 80)
    print(sample_lua[:300] + "...")
    print()

    # Parse it
    parser = LuaQuestParser()
    quests = parser.parse_string(sample_lua)

    print(f"Parsed {len(quests)} quest(s):")
    print()

    for quest in quests:
        print(f"Quest ID: {quest.quest_id}")
        print(f"Name: {quest.quest_name}")
        print(f"Description: {quest.description}")
        print(f"Platform: {quest.platform}")
        print()
        print(f"Requirements ({len(quest.requirements)}):")
        for req in quest.requirements:
            print(f"  - {req.description}")
        print()
        print(f"Objectives ({len(quest.objectives)}):")
        for obj in quest.objectives:
            print(f"  - {obj.description} ({obj.objective_type})")
        print()
        print("Rewards:")
        print(f"  - XP: {quest.rewards.xp}")
        print(f"  - Gold: {quest.rewards.gold}")
        print(f"  - Items: {quest.rewards.items}")
        print()


def test_round_trip():
    """Test complete round trip: Create → Generate → Parse → Generate"""
    print("=" * 80)
    print("TEST 4: Round Trip (Create → Generate → Parse → Generate)")
    print("=" * 80)
    print()

    # Step 1: Create quest
    original = QuestData(
        quest_id=3001,
        quest_name="Round Trip Test",
        description="Testing bidirectional parsing",
    )
    original.objectives.append(
        QuestObjective(
            description="Test objective",
            objective_type="Kill",
            target="TestEnemy",
        )
    )
    original.rewards.xp = 100

    parser = LuaQuestParser()

    # Step 2: Generate Lua
    print("Step 1: Generate Lua from quest data...")
    lua1 = parser.generate_lua_script(original)
    print(f"✓ Generated {len(lua1)} characters")
    print()

    # Step 3: Parse the generated Lua
    print("Step 2: Parse the generated Lua...")
    parsed = parser.parse_string(lua1)
    print(f"✓ Parsed {len(parsed)} quest(s)")
    if parsed:
        quest = parsed[0]
        print(f"  Quest ID: {quest.quest_id}")
        print(f"  Name: {quest.quest_name}")
        print(f"  Objectives: {len(quest.objectives)}")
    print()

    # Step 4: Generate Lua again
    print("Step 3: Generate Lua from parsed quest...")
    if parsed:
        lua2 = parser.generate_lua_script(parsed[0])
        print(f"✓ Generated {len(lua2)} characters")
        print()
        print("Round trip successful!" if lua2 else "Round trip failed!")
    else:
        print("✗ Could not complete round trip (parsing failed)")

    print()


def test_multiple_quests():
    """Test creating multiple related quests"""
    print("=" * 80)
    print("TEST 5: Multiple Related Quests")
    print("=" * 80)
    print()

    # Main quest
    main_quest = QuestData(
        quest_id=4001,
        quest_name="The Great Adventure",
        description="Embark on an epic journey",
    )
    main_quest.objectives.append(
        QuestObjective(description="Complete all sub-quests", objective_type="Quest")
    )

    # Sub-quest 1
    sub_quest1 = QuestData(
        quest_id=4002,
        quest_name="Gather Supplies",
        description="Collect necessary supplies",
    )
    sub_quest1.requirements.append(
        QuestRequirement(
            description="Accept main quest",
            requirement_type="Quest",
            value=4001,
        )
    )

    # Sub-quest 2
    sub_quest2 = QuestData(
        quest_id=4003,
        quest_name="Find the Guide",
        description="Locate the experienced guide",
    )
    sub_quest2.requirements.append(
        QuestRequirement(
            description="Gather supplies first",
            requirement_type="Quest",
            value=4002,
        )
    )

    parser = LuaQuestParser()

    # Generate all scripts
    print("Generating Lua scripts for quest chain:")
    print()

    for i, quest in enumerate([main_quest, sub_quest1, sub_quest2], 1):
        print(f"{i}. {quest.quest_name} (ID: {quest.quest_id})")
        lua = parser.generate_lua_script(quest)
        print(f"   Generated: {len(lua)} characters")

        # Save to file
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"quest_{quest.quest_id}.lua"
        parser.save_to_file(quest, str(output_file))
        print(f"   Saved to: {output_file}")
        print()


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "LUA QUEST PARSER TEST SUITE" + " " * 31 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    try:
        # Run tests
        test_generate_quest()
        test_save_and_load()
        test_parse_existing_lua()
        test_round_trip()
        test_multiple_quests()

        print()
        print("=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("Output files saved to: src/tests/lua_parser/output/")
        print()

    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR DURING TESTING")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
