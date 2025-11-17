#!/usr/bin/env python3
"""
LUA Quest Exporter
==================

Exports quest data from the Quest Editor to SpellForce-compatible LUA scripts.

Features:
- Quest logic export (OnOneTimeEvent blocks)
- Reward system export (GdsQuestRewards format)
- Dialogue tree export
- Condition/flag export
- Full SpellForce format compatibility

Author: Quest Editor Development Team
Date: November 17, 2025
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json


class LuaExporter:
    """
    Main LUA export engine for quest data.

    Converts Quest Editor data structures into SpellForce-compatible LUA scripts.
    """

    def __init__(self):
        self.indent_level = 0
        self.indent_char = "\t"

    def _indent(self, level: Optional[int] = None) -> str:
        """Get indentation string for current or specified level."""
        if level is None:
            level = self.indent_level
        return self.indent_char * level

    def _lua_bool(self, value: bool) -> str:
        """Convert Python bool to LUA boolean."""
        return "TRUE" if value else "FALSE"

    def _lua_string(self, value: str) -> str:
        """Convert Python string to LUA string with proper escaping."""
        # Escape special characters
        value = value.replace("\\", "\\\\")
        value = value.replace('"', '\\"')
        value = value.replace("\n", "\\n")
        value = value.replace("\t", "\\t")
        return f'"{value}"'

    def _lua_table_entry(self, key: str, value: Any, indent: int = 1) -> str:
        """Format a single table entry."""
        ind = self._indent(indent)

        if isinstance(value, bool):
            return f"{ind}{key} = {self._lua_bool(value)}"
        elif isinstance(value, (int, float)):
            return f"{ind}{key} = {value}"
        elif isinstance(value, str):
            return f"{ind}{key} = {self._lua_string(value)}"
        elif isinstance(value, list):
            return f"{ind}{key} = {{{', '.join(str(v) for v in value)}}}"
        elif isinstance(value, dict):
            return f"{ind}{key} = {self._lua_table(value, indent + 1)}"
        else:
            return f"{ind}{key} = nil"

    def _lua_table(self, data: Dict[str, Any], base_indent: int = 0) -> str:
        """Convert Python dict to LUA table."""
        if not data:
            return "{}"

        lines = ["{"]
        for key, value in data.items():
            lines.append(self._lua_table_entry(key, value, base_indent + 1) + ",")
        lines.append(self._indent(base_indent) + "}")

        return "\n".join(lines)

    # ========================================================================
    # CONDITION EXPORT
    # ========================================================================

    def export_condition(self, condition: Dict[str, Any], indent: int = 2) -> str:
        """
        Export a single condition to LUA format.

        Args:
            condition: Condition data from condition builder
            indent: Indentation level

        Returns:
            LUA condition string
        """
        cond_type = condition.get("type", "")
        negated = condition.get("negated", False)

        # Build the condition string
        lua_cond = ""

        if cond_type == "QuestState":
            quest_id = condition.get("quest_id", 0)
            state = condition.get("state", "StateActive")
            lua_cond = f"QuestState{{QuestId = {quest_id}, State = {state}}}"

        elif cond_type == "GlobalFlag":
            flag_name = condition.get("flag_name", "")
            flag_state = condition.get("flag_state", True)
            if flag_state:
                lua_cond = f"IsGlobalFlagTrue{{Name = {self._lua_string(flag_name)}}}"
            else:
                lua_cond = f"IsGlobalFlagFalse{{Name = {self._lua_string(flag_name)}}}"

        elif cond_type == "ItemFlag":
            flag_name = condition.get("flag_name", "")
            flag_state = condition.get("flag_state", True)
            if flag_state:
                lua_cond = f"IsPlayerFlagTrue{{Name = {self._lua_string(flag_name)}}}"
            else:
                lua_cond = f"IsPlayerFlagFalse{{Name = {self._lua_string(flag_name)}}}"

        elif cond_type == "NpcFlag":
            flag_name = condition.get("flag_name", "")
            flag_state = condition.get("flag_state", True)
            if flag_state:
                lua_cond = f"IsNpcFlagTrue{{Name = {self._lua_string(flag_name)}}}"
            else:
                lua_cond = f"IsNpcFlagFalse{{Name = {self._lua_string(flag_name)}}}"

        elif cond_type == "TimeDay":
            lua_cond = "IsDay{}"

        elif cond_type == "TimeNight":
            lua_cond = "IsNight{}"

        elif cond_type == "FigureDead":
            npc_id = condition.get("npc_id", 0)
            lua_cond = f"FigureDead{{NpcId = {npc_id}}}"

        elif cond_type == "PlayerHasItem":
            item_id = condition.get("item_id", 0)
            quantity = condition.get("quantity", 1)
            if quantity > 1:
                lua_cond = f"PlayerHasItem{{ItemId = {item_id}, Amount = {quantity}}}"
            else:
                lua_cond = f"PlayerHasItem{{ItemId = {item_id}}}"

        # Apply negation if needed
        if negated and lua_cond:
            lua_cond = f"Negated({lua_cond})"

        return lua_cond

    def export_condition_group(
        self, group: Dict[str, Any], indent: int = 2
    ) -> List[str]:
        """
        Export a condition group (UND/ODER) to LUA format.

        Args:
            group: Condition group data
            indent: Indentation level

        Returns:
            List of LUA condition strings
        """
        conditions = []
        operator = group.get("operator", "UND")
        children = group.get("children", [])

        if not children:
            return []

        # For single condition, just export it
        if len(children) == 1:
            child = children[0]
            if child.get("is_group"):
                return self.export_condition_group(child, indent)
            else:
                return [self.export_condition(child, indent)]

        # For multiple conditions with UND, just list them
        if operator == "UND":
            for child in children:
                if child.get("is_group"):
                    # Nested group needs ODER/UND wrapper
                    nested = self.export_condition_group(child, indent)
                    conditions.extend(nested)
                else:
                    conditions.append(self.export_condition(child, indent))

        # For ODER, wrap in ODER() function
        elif operator == "ODER":
            oder_conditions = []
            for child in children:
                if child.get("is_group"):
                    nested = self.export_condition_group(child, indent + 1)
                    oder_conditions.extend(nested)
                else:
                    oder_conditions.append(self.export_condition(child, indent + 1))

            # Build ODER wrapper
            if oder_conditions:
                oder_block = ["ODER("]
                for i, cond in enumerate(oder_conditions):
                    comma = "," if i < len(oder_conditions) - 1 else ""
                    oder_block.append(f"{self._indent(indent + 1)}{cond}{comma}")
                oder_block.append(f"{self._indent(indent)})")
                conditions.append("\n".join(oder_block))

        return conditions

    # ========================================================================
    # QUEST LOGIC EXPORT
    # ========================================================================

    def export_quest_begin(self, quest_data: Dict[str, Any]) -> str:
        """
        Export quest initialization block.

        Args:
            quest_data: Quest data from editor

        Returns:
            LUA OnOneTimeEvent block for quest initialization
        """
        quest_id = quest_data.get("quest_id", 0)
        quest_name = quest_data.get("internal_name", f"Quest{quest_id}")

        lines = [
            f"-- Initialize Quest: {quest_name}",
            "OnOneTimeEvent",
            "{",
            f"{self._indent(1)}Conditions = {{",
            f"{self._indent(2)}QuestState{{QuestId = {quest_id}, State = StateUnknown}}",
            f"{self._indent(1)}}},",
            f"{self._indent(1)}Actions = {{",
            f"{self._indent(2)}QuestBegin{{QuestId = {quest_id}}}",
        ]

        # Add child quests if any
        child_quests = quest_data.get("child_quests", [])
        for child_id in child_quests:
            lines.append(f"{self._indent(2)}QuestBegin{{QuestId = {child_id}}},")

        lines.append(f"{self._indent(1)}}}")
        lines.append("}")

        return "\n".join(lines)

    def export_quest_objective(
        self,
        quest_data: Dict[str, Any],
        objective: Dict[str, Any],
        objective_index: int,
    ) -> str:
        """
        Export a single quest objective as OnOneTimeEvent.

        Args:
            quest_data: Quest data from editor
            objective: Objective data
            objective_index: Index of this objective

        Returns:
            LUA OnOneTimeEvent block for objective completion
        """
        quest_id = quest_data.get("quest_id", 0)
        quest_name = quest_data.get("internal_name", f"Quest{quest_id}")
        obj_type = objective.get("type", "Custom")

        lines = [
            f"-- Quest: {quest_name} - Objective {objective_index + 1}: {obj_type}",
            "OnOneTimeEvent",
            "{",
            f"{self._indent(1)}Conditions = {{",
            f"{self._indent(2)}QuestState{{QuestId = {quest_id}, State = StateActive}},",
        ]

        # Add objective-specific conditions
        if obj_type == "Kill Target":
            target_id = objective.get("target_id", 0)
            quantity = objective.get("quantity", 1)
            if quantity == 1:
                lines.append(f"{self._indent(2)}FigureDead{{NpcId = {target_id}}}")
            else:
                # For multiple kills, use counter system
                lines.append(
                    f'{self._indent(2)}IsGlobalCounter{{Name = "KillCount_{quest_id}_{objective_index}", Operator = IsGreaterOrEqual, Value = {quantity}}}'
                )

        elif obj_type == "Gather Items":
            item_id = objective.get("target_id", 0)
            quantity = objective.get("quantity", 1)
            lines.append(
                f"{self._indent(2)}PlayerHasItem{{ItemId = {item_id}, Amount = {quantity}}}"
            )

        elif obj_type == "Talk to NPC":
            flag_name = f"Talked_{quest_id}_Objective_{objective_index}"
            lines.append(
                f"{self._indent(2)}IsPlayerFlagTrue{{Name = {self._lua_string(flag_name)}}}"
            )

        elif obj_type == "Explore Location":
            location = objective.get("location", "")
            flag_name = f"Explored_{location}"
            lines.append(
                f"{self._indent(2)}IsGlobalFlagTrue{{Name = {self._lua_string(flag_name)}}}"
            )

        elif obj_type == "Escort NPC":
            npc_id = objective.get("target_id", 0)
            destination = objective.get("destination", "")
            flag_name = f"Escorted_{npc_id}_To_{destination}"
            lines.append(
                f"{self._indent(2)}IsGlobalFlagTrue{{Name = {self._lua_string(flag_name)}}}"
            )

        elif obj_type == "Custom Objective":
            # Custom objectives use player flags
            flag_name = f"CustomObj_{quest_id}_{objective_index}"
            lines.append(
                f"{self._indent(2)}IsPlayerFlagTrue{{Name = {self._lua_string(flag_name)}}}"
            )

        lines.append(f"{self._indent(1)}}},")
        lines.append(f"{self._indent(1)}Actions = {{")

        # Set objective complete flag
        obj_flag = f"Objective_{quest_id}_{objective_index}_Complete"
        lines.append(
            f"{self._indent(2)}SetPlayerFlagTrue{{Name = {self._lua_string(obj_flag)}}}"
        )

        lines.append(f"{self._indent(1)}}}")
        lines.append("}")

        return "\n".join(lines)

    def export_quest_complete(self, quest_data: Dict[str, Any]) -> str:
        """
        Export quest completion block.

        Args:
            quest_data: Quest data from editor

        Returns:
            LUA OnOneTimeEvent block for quest completion
        """
        quest_id = quest_data.get("quest_id", 0)
        quest_name = quest_data.get("internal_name", f"Quest{quest_id}")
        objectives = quest_data.get("objectives", [])

        lines = [
            f"-- Quest Complete: {quest_name}",
            "OnOneTimeEvent",
            "{",
            f"{self._indent(1)}Conditions = {{",
            f"{self._indent(2)}QuestState{{QuestId = {quest_id}, State = StateActive}},",
        ]

        # Add conditions for all objectives being complete
        for i, obj in enumerate(objectives):
            obj_flag = f"Objective_{quest_id}_{i}_Complete"
            lines.append(
                f"{self._indent(2)}IsPlayerFlagTrue{{Name = {self._lua_string(obj_flag)}}},"
            )

        # Add custom conditions if any
        conditions = quest_data.get("conditions", {})
        if conditions and conditions.get("children"):
            custom_conditions = self.export_condition_group(conditions, indent=2)
            for cond in custom_conditions:
                lines.append(f"{self._indent(2)}{cond},")

        lines.append(f"{self._indent(1)}}},")
        lines.append(f"{self._indent(1)}Actions = {{")
        lines.append(f"{self._indent(2)}QuestSolve{{QuestId = {quest_id}}}")

        # Activate next quest if specified
        next_quest_id = quest_data.get("next_quest_id")
        if next_quest_id:
            lines.append(f"{self._indent(2)}QuestBegin{{QuestId = {next_quest_id}}},")

        lines.append(f"{self._indent(1)}}}")
        lines.append("}")

        return "\n".join(lines)

    def export_quest_logic(self, quest_data: Dict[str, Any]) -> str:
        """
        Export complete quest logic including all events.

        Args:
            quest_data: Complete quest data from editor

        Returns:
            Complete LUA script for quest
        """
        blocks = []

        # Header comment
        quest_id = quest_data.get("quest_id", 0)
        quest_name = quest_data.get("name", "Unknown Quest")
        internal_name = quest_data.get("internal_name", f"Quest{quest_id}")

        blocks.append("-- " + "=" * 70)
        blocks.append(f"-- Quest ID: {quest_id}")
        blocks.append(f"-- Name: {quest_name}")
        blocks.append(f"-- Internal Name: {internal_name}")
        blocks.append("-- " + "=" * 70)
        blocks.append("")

        # Quest initialization
        blocks.append(self.export_quest_begin(quest_data))
        blocks.append("")

        # Objective events
        objectives = quest_data.get("objectives", [])
        for i, objective in enumerate(objectives):
            blocks.append(self.export_quest_objective(quest_data, objective, i))
            blocks.append("")

        # Quest completion
        if objectives:  # Only add completion if there are objectives
            blocks.append(self.export_quest_complete(quest_data))
            blocks.append("")

        return "\n".join(blocks)

    # ========================================================================
    # REWARD EXPORT
    # ========================================================================

    def export_quest_rewards(self, quest_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export quest rewards in GdsQuestRewards format.

        Args:
            quest_data: Quest data from editor

        Returns:
            Dict with reward data in SpellForce format
        """
        internal_name = quest_data.get(
            "internal_name", f"Quest{quest_data.get('quest_id', 0)}"
        )
        rewards = quest_data.get("rewards", {})

        reward_entry = {}

        # XP rewards
        xp = rewards.get("xp", 0)
        if xp > 0:
            reward_entry["XP"] = [xp]

        # Money rewards
        money = rewards.get("money", {})
        gold = money.get("gold", 0)
        silver = money.get("silver", 0)
        copper = money.get("copper", 0)

        if gold > 0 or silver > 0 or copper > 0:
            reward_entry["Money"] = {}
            if gold > 0:
                reward_entry["Money"]["Gold"] = gold
            if silver > 0:
                reward_entry["Money"]["Silver"] = silver
            if copper > 0:
                reward_entry["Money"]["Copper"] = copper

        # Item rewards
        items = rewards.get("items", [])
        if items:
            item_ids = [item.get("id", 0) for item in items if item.get("id", 0) > 0]
            if item_ids:
                reward_entry["Items"] = item_ids

        return {internal_name: reward_entry} if reward_entry else {}

    def export_rewards_table(
        self, quests: List[Dict[str, Any]], platform_id: int = 1
    ) -> str:
        """
        Export rewards table for multiple quests.

        Args:
            quests: List of quest data dicts
            platform_id: Platform/map ID (default: 1 = Liannon)

        Returns:
            Complete LUA rewards table
        """
        lines = [
            "-- Quest Rewards",
            f"-- Generated by Quest Editor",
            f"-- Platform: P{platform_id}",
            "",
            f"QuestRewardsP{platform_id} = {{",
        ]

        for quest in quests:
            reward_data = self.export_quest_rewards(quest)
            if not reward_data:
                continue

            internal_name, rewards = next(iter(reward_data.items()))

            # Build reward entry
            parts = []
            if "XP" in rewards:
                xp_val = rewards["XP"][0]
                parts.append(f"XP = {{{xp_val}}}")

            if "Money" in rewards:
                money_parts = []
                if "Gold" in rewards["Money"]:
                    money_parts.append(f"Gold = {rewards['Money']['Gold']}")
                if "Silver" in rewards["Money"]:
                    money_parts.append(f"Silver = {rewards['Money']['Silver']}")
                if "Copper" in rewards["Money"]:
                    money_parts.append(f"Copper = {rewards['Money']['Copper']}")
                parts.append(f"Money = {{{', '.join(money_parts)}}}")

            if "Items" in rewards:
                item_list = ", ".join(str(i) for i in rewards["Items"])
                parts.append(f"Items = {{{item_list}}}")

            reward_str = ", ".join(parts)
            lines.append(
                f"{self._indent(1)}{internal_name} = {{ {reward_str} }}, -- {quest.get('name', '')}"
            )

        lines.append("}")
        lines.append("")

        return "\n".join(lines)

    # ========================================================================
    # FULL EXPORT
    # ========================================================================

    def export_quest_script(
        self,
        quest_data: Dict[str, Any],
        include_rewards: bool = True,
        platform_id: int = 1,
    ) -> str:
        """
        Export complete quest script including logic and rewards.

        Args:
            quest_data: Quest data from editor
            include_rewards: Include reward table (default: True)
            platform_id: Platform/map ID

        Returns:
            Complete LUA script
        """
        blocks = []

        # File header
        blocks.append("-- SpellForce Quest Script")
        blocks.append("-- Generated by TirganachReloaded Quest Editor")
        blocks.append("-- https://github.com/yourusername/quest-editor")
        blocks.append("")
        blocks.append(f"-- Platform: P{platform_id}")
        blocks.append(f"-- Quest: {quest_data.get('name', 'Unknown')}")
        blocks.append("")

        # Quest logic
        blocks.append(self.export_quest_logic(quest_data))

        # Rewards (if requested)
        if include_rewards:
            blocks.append("")
            blocks.append(self.export_rewards_table([quest_data], platform_id))

        return "\n".join(blocks)

    def export_multiple_quests(
        self,
        quests: List[Dict[str, Any]],
        platform_id: int = 1,
        output_dir: Optional[Path] = None,
    ) -> Dict[str, str]:
        """
        Export multiple quests to separate files.

        Args:
            quests: List of quest data dicts
            platform_id: Platform/map ID
            output_dir: Output directory (optional)

        Returns:
            Dict mapping quest_id to file content
        """
        exports = {}

        for quest in quests:
            quest_id = quest.get("quest_id", 0)
            script = self.export_quest_script(
                quest, include_rewards=False, platform_id=platform_id
            )

            filename = f"quest_{quest_id}.lua"
            exports[filename] = script

            # Write to file if output_dir provided
            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                (output_dir / filename).write_text(script, encoding="utf-8")

        # Export rewards table
        rewards_script = self.export_rewards_table(quests, platform_id)
        exports["quest_rewards.lua"] = rewards_script

        if output_dir:
            (output_dir / "quest_rewards.lua").write_text(
                rewards_script, encoding="utf-8"
            )

        return exports


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def export_quest_to_lua(
    quest_data: Dict[str, Any], output_path: Optional[Path] = None
) -> str:
    """
    Convenience function to export a single quest.

    Args:
        quest_data: Quest data from editor
        output_path: Optional output file path

    Returns:
        LUA script content
    """
    exporter = LuaExporter()
    script = exporter.export_quest_script(quest_data)

    if output_path:
        output_path.write_text(script, encoding="utf-8")

    return script


def export_quests_batch(
    quests: List[Dict[str, Any]], output_dir: Path, platform_id: int = 1
) -> int:
    """
    Batch export multiple quests.

    Args:
        quests: List of quest data dicts
        output_dir: Output directory
        platform_id: Platform/map ID

    Returns:
        Number of quests exported
    """
    exporter = LuaExporter()
    exports = exporter.export_multiple_quests(quests, platform_id, output_dir)
    return len(exports) - 1  # Subtract 1 for rewards file


if __name__ == "__main__":
    # Test with sample data
    sample_quest = {
        "quest_id": 999,
        "name": "Test Quest",
        "internal_name": "TestQuest",
        "objectives": [
            {
                "type": "Kill Target",
                "target_id": 1234,
                "target_name": "Goblin Chief",
                "quantity": 1,
                "description": "Defeat the Goblin Chief",
            },
            {
                "type": "Gather Items",
                "target_id": 626,
                "target_name": "Simple Metal Helmet",
                "quantity": 3,
                "description": "Collect 3 helmets",
            },
        ],
        "rewards": {
            "xp": 500,
            "money": {"gold": 5, "silver": 10, "copper": 0},
            "items": [{"id": 626, "name": "Simple Metal Helmet"}],
        },
    }

    exporter = LuaExporter()
    script = exporter.export_quest_script(sample_quest)
    print(script)
