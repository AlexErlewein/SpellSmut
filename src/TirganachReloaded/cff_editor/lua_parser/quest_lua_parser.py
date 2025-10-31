"""
Lua Quest Script Parser
Bidirectional parser for SpellForce quest Lua scripts
Can READ existing quest Lua files and WRITE new ones
"""

import re
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple


@dataclass
class QuestObjective:
    """Quest objective/goal"""

    description: str
    objective_type: str = "Unknown"  # Kill, Collect, Talk, Escort, etc.
    target: Optional[str] = None
    count: int = 1
    lua_condition: Optional[str] = None  # Raw Lua condition if complex


@dataclass
class QuestRequirement:
    """Requirement to accept quest"""

    description: str
    requirement_type: str = "Unknown"  # Level, Quest, Item, Flag, etc.
    value: Optional[Any] = None
    lua_condition: Optional[str] = None  # Raw Lua condition


@dataclass
class QuestReward:
    """Quest reward"""

    xp: int = 0
    gold: int = 0
    silver: int = 0
    copper: int = 0
    items: List[int] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)


@dataclass
class QuestDialogue:
    """Quest dialogue node"""

    dialogue_id: str
    speaker: str = "NPC"  # NPC or Player
    text: str = ""
    is_player_choice: bool = False
    conditions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    next_dialogues: List[str] = field(default_factory=list)


@dataclass
class QuestData:
    """Complete quest data structure"""

    quest_id: int
    quest_name: str
    description: str = ""
    platform: str = "P7"
    npc_id: Optional[int] = None

    # Quest flow
    objectives: List[QuestObjective] = field(default_factory=list)
    requirements: List[QuestRequirement] = field(default_factory=list)
    rewards: QuestReward = field(default_factory=QuestReward)

    # Dialogues
    dialogues: List[QuestDialogue] = field(default_factory=list)

    # Raw Lua sections (for advanced users)
    init_event: Optional[str] = None
    complete_event: Optional[str] = None
    custom_events: List[str] = field(default_factory=list)

    # Metadata
    author: str = ""
    notes: str = ""


class LuaQuestParser:
    """Bidirectional Lua quest script parser"""

    def __init__(self):
        self.current_quest: Optional[QuestData] = None

    def parse_file(self, lua_file_path: str) -> List[QuestData]:
        """Parse a Lua quest file and extract all quests"""
        # Try multiple encodings (German characters in SpellForce files)
        encodings = ["utf-8", "windows-1252", "latin-1", "iso-8859-1"]
        lua_content = None

        for encoding in encodings:
            try:
                with open(lua_file_path, "r", encoding=encoding) as f:
                    lua_content = f.read()
                break
            except (UnicodeDecodeError, LookupError):
                continue

        if lua_content is None:
            # Last resort: read as binary and ignore errors
            with open(lua_file_path, "r", encoding="utf-8", errors="ignore") as f:
                lua_content = f.read()

        return self.parse_string(lua_content)

    def parse_string(self, lua_content: str) -> List[QuestData]:
        """Parse Lua script string and extract quest data"""
        quests = []

        # Find all quest definitions
        # Look for QuestBegin or quest ID patterns
        quest_id_pattern = r"QuestId\s*=\s*(\d+)"
        quest_ids = set(re.findall(quest_id_pattern, lua_content))

        for quest_id_str in quest_ids:
            quest_id = int(quest_id_str)
            quest_data = self._extract_quest_data(lua_content, quest_id)
            if quest_data:
                quests.append(quest_data)

        return quests

    def _extract_quest_data(
        self, lua_content: str, quest_id: int
    ) -> Optional[QuestData]:
        """Extract data for a specific quest from Lua content"""
        quest = QuestData(quest_id=quest_id, quest_name=f"Quest {quest_id}")

        # Extract quest name from comments or strings
        name_patterns = [
            rf"-- Quest: (.+)\n.*?QuestId\s*=\s*{quest_id}",
            rf"QuestId\s*=\s*{quest_id}.*?--\s*(.+)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, lua_content, re.IGNORECASE)
            if match:
                quest.quest_name = match.group(1).strip()
                break

        # Extract description from Outcry or comments
        desc_pattern = rf'QuestId\s*=\s*{quest_id}.*?String\s*=\s*["\']([^"\']+)["\']'
        desc_match = re.search(desc_pattern, lua_content, re.DOTALL)
        if desc_match:
            quest.description = desc_match.group(1)

        # Extract init event
        quest.init_event = self._extract_event(
            lua_content, f"Init.*?QuestId\\s*=\\s*{quest_id}"
        )

        # Extract complete event
        quest.complete_event = self._extract_event(
            lua_content, f"Complete.*?QuestId\\s*=\\s*{quest_id}"
        )

        # Extract objectives from completion conditions
        quest.objectives = self._extract_objectives(lua_content, quest_id)

        # Extract requirements from init conditions
        quest.requirements = self._extract_requirements(lua_content, quest_id)

        # Extract rewards
        quest.rewards = self._extract_rewards(lua_content, quest_id)

        # Extract dialogues
        quest.dialogues = self._extract_dialogues(lua_content, quest_id)

        return quest

    def _extract_event(self, lua_content: str, event_pattern: str) -> Optional[str]:
        """Extract a complete OnOneTimeEvent block"""
        pattern = rf"OnOneTimeEvent\s*{{[^}}]*{event_pattern}.*?EndEvent\s*}}"
        match = re.search(pattern, lua_content, re.DOTALL | re.IGNORECASE)
        return match.group(0) if match else None

    def _extract_objectives(
        self, lua_content: str, quest_id: int
    ) -> List[QuestObjective]:
        """Extract quest objectives from completion conditions"""
        objectives = []

        # Limit search to reasonable chunk size to prevent hanging
        if len(lua_content) > 500000:  # 500KB
            # Only search in relevant sections
            quest_pattern = rf"QuestId\s*=\s*{quest_id}"
            matches = list(re.finditer(quest_pattern, lua_content))
            if matches:
                # Search in 10KB around each match
                for match in matches[:5]:  # Limit to first 5 occurrences
                    start = max(0, match.start() - 5000)
                    end = min(len(lua_content), match.end() + 5000)
                    chunk = lua_content[start:end]
                    objectives.extend(self._extract_objectives_from_chunk(chunk, quest_id))
                return objectives
            else:
                return []

        # Find all OnOneTimeEvent blocks related to this quest
        # Simplified pattern to avoid catastrophic backtracking
        objectives.extend(self._extract_objectives_from_chunk(lua_content, quest_id))
        return objectives

    def _extract_objectives_from_chunk(
        self, lua_content: str, quest_id: int
    ) -> List[QuestObjective]:
        """Extract objectives from a chunk of Lua content"""
        objectives = []

        # Simple pattern - just look for conditions near QuestSolve
        solve_pattern = rf"QuestSolve\s*{{\s*QuestId\s*=\s*{quest_id}"

        for match in re.finditer(solve_pattern, lua_content):
            # Look backwards for Conditions block (up to 2000 chars)
            start_pos = max(0, match.start() - 2000)
            preceding_text = lua_content[start_pos:match.start()]

            # Find the last Conditions block before this QuestSolve
            conditions_match = re.search(r"Conditions\s*=\s*\{([^}]{0,1000})\}", preceding_text)
            if not conditions_match:
                continue

            conditions = conditions_match.group(1)

            # FigureIsDead - Kill objectives (with NpcId)
            kill_pattern = r"FigureIsDead\s*{{\s*NpcId\s*=\s*(\d+)"
            for kill_match in re.finditer(kill_pattern, conditions):
                npc_id = kill_match.group(1)
                objectives.append(
                    QuestObjective(
                        description=f"Defeat NPC {npc_id}",
                        objective_type="Kill",
                        target=f"NPC {npc_id}",
                    )
                )

            # FigureIsDead with Tag
            kill_tag_pattern = r'FigureIsDead\s*{{\s*Tag\s*=\s*["\']([^"\']+)["\']'
            for kill_match in re.finditer(kill_tag_pattern, conditions):
                objectives.append(
                    QuestObjective(
                        description=f"Defeat {kill_match.group(1)}",
                        objective_type="Kill",
                        target=kill_match.group(1),
                    )
                )

            # PlayerHasItem - Collection objectives
            item_pattern = r"PlayerHasItem\s*{{\s*ItemId\s*=\s*(\d+)"
            for item_match in re.finditer(item_pattern, conditions):
                item_id = item_match.group(1)
                # Try to extract amount
                amount = 1
                amount_match = re.search(
                    rf"ItemId\s*=\s*{item_id}.*?Amount\s*=\s*(\d+)",
                    conditions,
                    re.DOTALL,
                )
                if amount_match:
                    amount = int(amount_match.group(1))

                objectives.append(
                    QuestObjective(
                        description=f"Collect item {item_id}",
                        objective_type="Collect",
                        target=item_id,
                        count=amount,
                    )
                )

            # FigureIsInRange - Reach location objectives
            range_pattern = r'FigureIsInRange\s*{{\s*Tag\s*=\s*["\']([^"\']+)["\'].*?Range\s*=\s*(\d+)'
            for range_match in re.finditer(range_pattern, conditions):
                objectives.append(
                    QuestObjective(
                        description=f"Reach {range_match.group(1)}",
                        objective_type="Reach",
                        target=range_match.group(1),
                    )
                )

        return objectives

    def _extract_requirements(
        self, lua_content: str, quest_id: int
    ) -> List[QuestRequirement]:
        """Extract quest requirements from init conditions"""
        requirements = []

        # Limit search scope to prevent hanging
        quest_begin_pattern = rf"QuestBegin\s*{{\s*QuestId\s*=\s*{quest_id}"

        for match in re.finditer(quest_begin_pattern, lua_content):
            # Look backwards for Conditions (up to 1000 chars)
            start_pos = max(0, match.start() - 1000)
            preceding_text = lua_content[start_pos:match.start()]

            conditions_match = re.search(r"Conditions\s*=\s*\{([^}]{0,500})\}", preceding_text)
            if not conditions_match:
                continue

            conditions = conditions_match.group(1)

            # QuestState - Prerequisite quest
            quest_pattern = r"QuestState\s*{{\s*QuestId\s*=\s*(\d+).*?State\s*=\s*(\w+)"
            for quest_match in re.finditer(quest_pattern, conditions):
                requirements.append(
                    QuestRequirement(
                        description=f"Complete Quest {quest_match.group(1)}",
                        requirement_type="Quest",
                        value=int(quest_match.group(1)),
                    )
                )

            # AvatarLevel - Level requirement
            level_pattern = r"AvatarLevel\s*{{\s*Level\s*=\s*(\d+)"
            level_match = re.search(level_pattern, conditions)
            if level_match:
                requirements.append(
                    QuestRequirement(
                        description=f"Reach level {level_match.group(1)}",
                        requirement_type="Level",
                        value=int(level_match.group(1)),
                    )
                )

        return requirements

    def _extract_rewards(self, lua_content: str, quest_id: int) -> QuestReward:
        """Extract quest rewards"""
        reward = QuestReward()

        # Look for reward definition (simplified pattern)
        reward_pattern = rf"Quest{quest_id}Reward\s*=\s*\{{([^}}]{{0,500}})\}}"
        match = re.search(reward_pattern, lua_content)

        if match:
            reward_def = match.group(1)

            # XP
            xp_match = re.search(r"XP\s*=\s*(\d+)", reward_def)
            if xp_match:
                reward.xp = int(xp_match.group(1))

            # Gold
            gold_match = re.search(r"Gold\s*=\s*(\d+)", reward_def)
            if gold_match:
                reward.gold = int(gold_match.group(1))

            # Silver
            silver_match = re.search(r"Silver\s*=\s*(\d+)", reward_def)
            if silver_match:
                reward.silver = int(silver_match.group(1))

            # Copper
            copper_match = re.search(r"Copper\s*=\s*(\d+)", reward_def)
            if copper_match:
                reward.copper = int(copper_match.group(1))

            # Items
            items_match = re.search(r"Items\s*=\s*{([^}]+)}", reward_def)
            if items_match:
                items_str = items_match.group(1)
                reward.items = [
                    int(i.strip()) for i in items_str.split(",") if i.strip().isdigit()
                ]

        return reward

    def _extract_dialogues(
        self, lua_content: str, quest_id: int
    ) -> List[QuestDialogue]:
        """Extract quest dialogues (simplified - full dialogue parsing is complex)"""
        dialogues = []

        # Look for dialogue definitions related to this quest
        # This is a simplified extraction - real dialogue parsing would need
        # to handle the complex dialogue state machine in SpellForce

        dialogue_pattern = (
            r'OnOneTimeEvent\s*{{\s*EventName\s*=\s*["\']([^"\']*[Dd]ialog[^"\']*)["\']'
        )
        for match in re.finditer(dialogue_pattern, lua_content):
            dialogue_id = match.group(1)
            dialogues.append(QuestDialogue(dialogue_id=dialogue_id, speaker="NPC"))

        return dialogues

    # ========================================================================
    # GENERATION METHODS - Create Lua from QuestData
    # ========================================================================

    def generate_lua_script(self, quest: QuestData) -> str:
        """Generate complete Lua script from quest data"""
        script_parts = []

        # Header
        script_parts.append(self._generate_header(quest))

        # State machine wrapper
        script_parts.append(self._generate_state_machine_start(quest))

        # Init event
        script_parts.append(self._generate_init_event(quest))

        # Objective events (if needed)
        for i, objective in enumerate(quest.objectives):
            if objective.objective_type in ["Kill", "Collect"]:
                script_parts.append(self._generate_objective_event(quest, objective, i))

        # Complete event
        script_parts.append(self._generate_complete_event(quest))

        # Reward definition
        script_parts.append(self._generate_reward_definition(quest))

        # Dialogue section
        if quest.dialogues:
            script_parts.append(self._generate_dialogue_section(quest))

        # Footer
        script_parts.append(self._generate_footer())

        return "\n\n".join(script_parts)

    def _generate_header(self, quest: QuestData) -> str:
        """Generate Lua script header"""
        return f"""-- Generated Quest Script: {quest.quest_name}
-- Quest ID: {quest.quest_id}
-- Platform: {quest.platform}
{f"-- Author: {quest.author}" if quest.author else ""}
{f"-- Notes: {quest.notes}" if quest.notes else ""}
--
-- This script was generated by the SpellForce CFF Editor
-- Generated on: {self._get_timestamp()}
"""

    def _generate_state_machine_start(self, quest: QuestData) -> str:
        """Generate state machine function start"""
        return f"""function CreateStateMachine(_Type, _PlatformId, _NpcId, _X, _Y)
BeginDefinition(_Type, _PlatformId, _NpcId, _X, _Y)

--------------------------------------------------------------------------
-- QUEST: {quest.quest_name.upper()}
-- ID: {quest.quest_id}
--------------------------------------------------------------------------"""

    def _generate_init_event(self, quest: QuestData) -> str:
        """Generate quest initialization event"""
        event_name = quest.quest_name.replace(" ", "")

        # Build conditions
        conditions = []
        for req in quest.requirements:
            if req.lua_condition:
                conditions.append(f"        {req.lua_condition}")
            elif req.requirement_type == "Quest":
                conditions.append(
                    f"        QuestState{{QuestId = {req.value}, State = StateSolved}}"
                )
            elif req.requirement_type == "Level":
                conditions.append(f"        AvatarLevel{{Level = {req.value}}}")
            else:
                conditions.append(f"        -- TODO: {req.description}")

        if not conditions:
            conditions.append("        -- No prerequisites")

        # Build actions
        actions = [
            f"        QuestBegin{{QuestId = {quest.quest_id}}}",
        ]

        if quest.description:
            desc_escaped = quest.description.replace('"', '\\"')
            actions.append(f"""        Outcry{{
            NpcId = {quest.npc_id or 0},
            String = "{desc_escaped[:100]}",
            Color = ColorYellow
        }}""")

        return f"""-- Quest Initialization
OnOneTimeEvent
{{
    EventName = "Init_{event_name}",
    Conditions =
    {{
{chr(10).join(conditions)}
    }},
    Actions =
    {{
{chr(10).join(actions)}
    }}
}}"""

    def _generate_objective_event(
        self, quest: QuestData, objective: QuestObjective, index: int
    ) -> str:
        """Generate event for tracking objective completion"""
        event_name = quest.quest_name.replace(" ", "")

        return f"""-- Objective {index + 1}: {objective.description}
OnOneTimeEvent
{{
    EventName = "{event_name}_Objective{index + 1}",
    Conditions =
    {{
        QuestState{{QuestId = {quest.quest_id}, State = StateActive}},
        -- TODO: Add specific condition for: {objective.description}
    }},
    Actions =
    {{
        Outcry{{
            NpcId = 0,
            String = "Objective completed: {objective.description}",
            Color = ColorGreen
        }}
    }}
}}"""

    def _generate_complete_event(self, quest: QuestData) -> str:
        """Generate quest completion event"""
        event_name = quest.quest_name.replace(" ", "")

        # Build conditions from objectives
        conditions = [
            f"        QuestState{{QuestId = {quest.quest_id}, State = StateActive}}"
        ]

        for obj in quest.objectives:
            if obj.lua_condition:
                conditions.append(f"        {obj.lua_condition}")
            elif obj.objective_type == "Kill" and obj.target:
                conditions.append(f'        FigureIsDead{{Tag = "{obj.target}"}}')
            elif obj.objective_type == "Collect" and obj.target:
                conditions.append(
                    f"        PlayerHasItem{{ItemId = {obj.target}, Amount = {obj.count}}}"
                )
            else:
                conditions.append(f"        -- TODO: {obj.description}")

        # Build actions
        actions = [
            f"        QuestSolve{{QuestId = {quest.quest_id}}}",
            f'        SetRewardFlagTrue{{Name = "Quest{quest.quest_id}Reward"}}',
        ]

        if quest.objectives:
            actions.append(f"""        Outcry{{
            NpcId = 0,
            String = "Quest completed: {quest.quest_name}!",
            Color = ColorGreen
        }}""")

        return f"""-- Quest Completion
OnOneTimeEvent
{{
    EventName = "Complete_{event_name}",
    Conditions =
    {{
{chr(10).join(conditions)}
    }},
    Actions =
    {{
{chr(10).join(actions)}
    }}
}}"""

    def _generate_reward_definition(self, quest: QuestData) -> str:
        """Generate quest reward definition"""
        reward = quest.rewards

        items_str = ", ".join(str(i) for i in reward.items) if reward.items else ""

        return f"""-- Quest Rewards (typically in GdsQuestRewards.lua)
-- Quest{quest.quest_id}Reward = {{
--     XP = {{{reward.xp}}},
--     Money = {{Gold = {reward.gold}, Silver = {reward.silver}, Copper = {reward.copper}}},
--     Items = {{{items_str}}}
-- }}"""

    def _generate_dialogue_section(self, quest: QuestData) -> str:
        """Generate dialogue section"""
        return f"""--------------------------------------------------------------------------
-- DIALOGUE SECTION
--------------------------------------------------------------------------
-- Dialogues for this quest:
{chr(10).join(f"-- - {d.dialogue_id}" for d in quest.dialogues)}
--
-- Note: Detailed dialogue branching should be defined separately
"""

    def _generate_footer(self) -> str:
        """Generate script footer"""
        return """
EndDefinition()
end
"""

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def save_to_file(self, quest: QuestData, output_path: str):
        """Generate Lua script and save to file"""
        lua_script = self.generate_lua_script(quest)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(lua_script)

    def validate_quest(self, quest: QuestData) -> Tuple[bool, List[str]]:
        """Validate quest data and return errors/warnings"""
        errors = []
        warnings = []

        if not quest.quest_name:
            errors.append("Quest name is required")

        if quest.quest_id <= 0:
            errors.append("Quest ID must be positive")

        if not quest.objectives:
            warnings.append("Quest has no objectives defined")

        if (
            quest.rewards.xp == 0
            and quest.rewards.gold == 0
            and not quest.rewards.items
        ):
            warnings.append("Quest has no rewards defined")

        return (len(errors) == 0, errors + warnings)


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================


def parse_quest_file(lua_file_path: str) -> List[QuestData]:
    """Convenience function to parse a quest Lua file"""
    parser = LuaQuestParser()
    return parser.parse_file(lua_file_path)


def generate_quest_file(quest: QuestData, output_path: str):
    """Convenience function to generate a quest Lua file"""
    parser = LuaQuestParser()
    parser.save_to_file(quest, output_path)


def create_example_quest() -> QuestData:
    """Create an example quest for testing"""
    quest = QuestData(
        quest_id=1001,
        quest_name="The Lost Sword",
        description="Find the legendary sword in the ancient ruins",
        platform="P7",
        npc_id=100,
    )

    quest.requirements.append(
        QuestRequirement(description="Reach level 5", requirement_type="Level", value=5)
    )

    quest.objectives.append(
        QuestObjective(
            description="Defeat the Guardian", objective_type="Kill", target="Guardian"
        )
    )

    quest.objectives.append(
        QuestObjective(
            description="Collect the Ancient Sword",
            objective_type="Collect",
            target="101",
            count=1,
        )
    )

    quest.rewards.xp = 1000
    quest.rewards.gold = 50
    quest.rewards.items = [201, 202]

    return quest


if __name__ == "__main__":
    # Example usage
    print("Creating example quest...")
    quest = create_example_quest()

    parser = LuaQuestParser()
    lua_script = parser.generate_lua_script(quest)

    print("Generated Lua Script:")
    print("=" * 80)
    print(lua_script)
