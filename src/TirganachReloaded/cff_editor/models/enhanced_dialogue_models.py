#!/usr/bin/env python3
"""
Enhanced Dialogue Models

Extended dialogue data models with conditions, actions, and consequences
for the quest editor. Integrates with existing condition and action systems.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json

try:
    from TirganachReloaded.cff_editor.widgets.condition_builder import Condition
    from TirganachReloaded.cff_editor.widgets.flag_manager import FlagDefinition
except ImportError:
    # Fallback if modules not available
    class Condition:
        def __init__(self, condition_type: str, params: Dict[str, Any] = None, negated: bool = False):
            self.condition_type = condition_type
            self.params = params or {}
            self.negated = negated

        def to_dict(self):
            return {"type": self.condition_type, "params": self.params, "negated": self.negated}

        def to_lua(self) -> str:
            return f"-- {self.condition_type} condition"


class DialogueConditionType(Enum):
    """Types of dialogue conditions"""

    # Quest conditions
    QUEST_STATE = "quest_state"
    QUEST_COMPLETE = "quest_complete"
    QUEST_ACTIVE = "quest_active"

    # Item conditions
    PLAYER_HAS_ITEM = "player_has_item"
    PLAYER_HAS_ITEM_COUNT = "player_has_item_count"
    PLAYER_EQUIPPED = "player_equipped"

    # Flag conditions
    GLOBAL_FLAG = "global_flag"
    NPC_FLAG = "npc_flag"
    ITEM_FLAG = "item_flag"

    # Stat conditions
    PLAYER_LEVEL = "player_level"
    PLAYER_GOLD = "player_gold"
    PLAYER_XP = "player_xp"

    # Time conditions
    TIME_DAY = "time_day"
    TIME_NIGHT = "time_night"
    GAME_TIME = "game_time"

    # Location conditions
    PLAYER_IN_AREA = "player_in_area"
    IN_BUILDING = "in_building"

    # NPC conditions
    NPC_ALIVE = "npc_alive"
    NPC_DEAD = "npc_dead"
    NPC_FRIENDLY = "npc_friendly"
    NPC_HOSTILE = "npc_hostile"

    # Custom conditions
    CUSTOM_LUA = "custom_lua"


class DialogueActionType(Enum):
    """Types of dialogue actions"""

    # Quest actions
    QUEST_BEGIN = "quest_begin"
    QUEST_COMPLETE = "quest_complete"
    QUEST_FAIL = "quest_fail"

    # Flag actions
    SET_GLOBAL_FLAG = "set_global_flag"
    CLEAR_GLOBAL_FLAG = "clear_global_flag"
    SET_NPC_FLAG = "set_npc_flag"
    SET_ITEM_FLAG = "set_item_flag"

    # Item actions
    GIVE_ITEM = "give_item"
    TAKE_ITEM = "take_item"
    EQUIP_ITEM = "equip_item"

    # Stat actions
    GIVE_XP = "give_xp"
    GIVE_GOLD = "give_gold"
    GIVE_SILVER = "give_silver"
    GIVE_COPPER = "give_copper"
    SET_LEVEL = "set_level"

    # Location actions
    TELEPORT_PLAYER = "teleport_player"
    SPAWN_NPC = "spawn_npc"
    SPAWN_BUILDING = "spawn_building"

    # Relationship actions
    CHANGE_FACTION = "change_faction"
    CHANGE_REPUTATION = "change_reputation"

    # Dialogue actions
    START_DIALOGUE = "start_dialogue"
    END_DIALOGUE = "end_dialogue"
    REMOVE_NPC = "remove_npc"

    # Custom actions
    CUSTOM_LUA = "custom_lua"
    PLAY_SOUND = "play_sound"
    PLAY_MUSIC = "play_music"
    SHOW_CUTSCENE = "show_cutscene"


@dataclass
class DialogueCondition:
    """Represents a condition for dialogue availability"""

    condition_type: DialogueConditionType
    params: Dict[str, Any] = field(default_factory=dict)
    negated: bool = False
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "condition_type": self.condition_type.value,
            "params": self.params,
            "negated": self.negated,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueCondition':
        """Create from dictionary"""
        return cls(
            condition_type=DialogueConditionType(data.get("condition_type", "global_flag")),
            params=data.get("params", {}),
            negated=data.get("negated", False),
            description=data.get("description", "")
        )

    def to_lua(self) -> str:
        """Generate LUA code"""
        if self.condition_type == DialogueConditionType.GLOBAL_FLAG:
            flag_name = self.params.get("flag_name", "")
            flag_value = self.params.get("value", True)
            func = "IsGlobalFlagTrue" if flag_value else "IsGlobalFlagFalse"
            lua_code = f'{func}{{Name = "{flag_name}"}}'

        elif self.condition_type == DialogueConditionType.QUEST_COMPLETE:
            quest_id = self.params.get("quest_id", 0)
            lua_code = f'QuestState{{QuestId = {quest_id}, State = StateSolved}}'

        elif self.condition_type == DialogueConditionType.PLAYER_HAS_ITEM:
            item_id = self.params.get("item_id", 0)
            count = self.params.get("count", 1)
            if count == 1:
                lua_code = f'PlayerHasItem{{ItemId = {item_id}}}'
            else:
                lua_code = f'PlayerHasItem{{ItemId = {item_id}, Count = {count}}}'

        elif self.condition_type == DialogueConditionType.PLAYER_LEVEL:
            level = self.params.get("level", 1)
            comparison = self.params.get("comparison", ">=")  # >=, >, ==, <, <=
            lua_code = f'PlayerLevel{{Comparison = "{comparison}", Level = {level}}}'

        elif self.condition_type == DialogueConditionType.NPC_DEAD:
            npc_id = self.params.get("npc_id", 0)
            lua_code = f'FigureDead{{FigureId = {npc_id}}}'

        elif self.condition_type == DialogueConditionType.CUSTOM_LUA:
            lua_code = self.params.get("lua_code", "-- Custom condition")

        else:
            lua_code = f"-- Unknown condition: {self.condition_type.value}"

        if self.negated:
            return f"Negated({lua_code})"

        return lua_code

    def get_display_text(self) -> str:
        """Get human-readable display text"""
        if self.description:
            return self.description

        # Auto-generate description
        if self.condition_type == DialogueConditionType.GLOBAL_FLAG:
            flag_name = self.params.get("flag_name", "")
            flag_value = self.params.get("value", True)
            state = "TRUE" if flag_value else "FALSE"
            text = f"Global flag '{flag_name}' is {state}"

        elif self.condition_type == DialogueConditionType.QUEST_COMPLETE:
            quest_id = self.params.get("quest_id", 0)
            text = f"Quest {quest_id} is complete"

        elif self.condition_type == DialogueConditionType.PLAYER_HAS_ITEM:
            item_id = self.params.get("item_id", 0)
            count = self.params.get("count", 1)
            text = f"Player has item {item_id}"
            if count > 1:
                text += f" (x{count})"

        elif self.condition_type == DialogueConditionType.PLAYER_LEVEL:
            level = self.params.get("level", 1)
            comparison = self.params.get("comparison", ">=")
            text = f"Player level {comparison} {level}"

        elif self.condition_type == DialogueConditionType.NPC_DEAD:
            npc_id = self.params.get("npc_id", 0)
            text = f"NPC {npc_id} is dead"

        else:
            text = f"Condition: {self.condition_type.value}"

        if self.negated:
            text = f"NOT ({text})"

        return text


@dataclass
class DialogueAction:
    """Represents an action that occurs as a result of dialogue"""

    action_type: DialogueActionType
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "action_type": self.action_type.value,
            "params": self.params,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueAction':
        """Create from dictionary"""
        return cls(
            action_type=DialogueActionType(data.get("action_type", "set_global_flag")),
            params=data.get("params", {}),
            description=data.get("description", "")
        )

    def to_lua(self) -> str:
        """Generate LUA code"""
        if self.action_type == DialogueActionType.SET_GLOBAL_FLAG:
            flag_name = self.params.get("flag_name", "")
            flag_value = self.params.get("value", True)
            func = "SetGlobalFlagTrue" if flag_value else "SetGlobalFlagFalse"
            return f'{func}{{Name = "{flag_name}"}}'

        elif self.action_type == DialogueActionType.CLEAR_GLOBAL_FLAG:
            flag_name = self.params.get("flag_name", "")
            return f'ClearGlobalFlag{{Name = "{flag_name}"}}'

        elif self.action_type == DialogueActionType.QUEST_BEGIN:
            quest_id = self.params.get("quest_id", 0)
            return f'QuestBegin{{QuestId = {quest_id}}}'

        elif self.action_type == DialogueActionType.QUEST_COMPLETE:
            quest_id = self.params.get("quest_id", 0)
            return f'QuestSolve{{QuestId = {quest_id}}}'

        elif self.action_type == DialogueActionType.GIVE_ITEM:
            item_id = self.params.get("item_id", 0)
            count = self.params.get("count", 1)
            if count == 1:
                return f'TransferItem{{GiveItem = {item_id}, Flag = Give}}'
            else:
                return f'-- Give {count}x item {item_id} (requires custom implementation)'

        elif self.action_type == DialogueActionType.TAKE_ITEM:
            item_id = self.params.get("item_id", 0)
            count = self.params.get("count", 1)
            if count == 1:
                return f'TransferItem{{TakeItem = {item_id}, Flag = Take}}'
            else:
                return f'-- Take {count}x item {item_id} (requires custom implementation)'

        elif self.action_type == DialogueActionType.GIVE_XP:
            xp_amount = self.params.get("amount", 0)
            return f'UpdateVariable{{Name = "PlayerXP", Value = {xp_amount}}}'

        elif self.action_type == DialogueActionType.GIVE_GOLD:
            gold_amount = self.params.get("amount", 0)
            return f'UpdateVariable{{Name = "PlayerGold", Value = {gold_amount}}}'

        elif self.action_type == DialogueActionType.PLAY_SOUND:
            sound_id = self.params.get("sound_id", 0)
            return f'PlaySound{{SoundID = {sound_id}}}'

        elif self.action_type == DialogueActionType.REMOVE_NPC:
            npc_id = self.params.get("npc_id", 0)
            return f'RemoveDialog{{NpcId = {npc_id}}}'

        elif self.action_type == DialogueActionType.CUSTOM_LUA:
            return self.params.get("lua_code", "-- Custom action")

        else:
            return f"-- Unknown action: {self.action_type.value}"

    def get_display_text(self) -> str:
        """Get human-readable display text"""
        if self.description:
            return self.description

        # Auto-generate description
        if self.action_type == DialogueActionType.SET_GLOBAL_FLAG:
            flag_name = self.params.get("flag_name", "")
            flag_value = self.params.get("value", True)
            state = "TRUE" if flag_value else "FALSE"
            text = f"Set global flag '{flag_name}' to {state}"

        elif self.action_type == DialogueActionType.QUEST_BEGIN:
            quest_id = self.params.get("quest_id", 0)
            text = f"Begin quest {quest_id}"

        elif self.action_type == DialogueActionType.QUEST_COMPLETE:
            quest_id = self.params.get("quest_id", 0)
            text = f"Complete quest {quest_id}"

        elif self.action_type == DialogueActionType.GIVE_ITEM:
            item_id = self.params.get("item_id", 0)
            count = self.params.get("count", 1)
            text = f"Give item {item_id}"
            if count > 1:
                text += f" (x{count})"

        elif self.action_type == DialogueActionType.GIVE_XP:
            xp_amount = self.params.get("amount", 0)
            text = f"Give {xp_amount} XP"

        elif self.action_type == DialogueActionType.PLAY_SOUND:
            sound_id = self.params.get("sound_id", 0)
            text = f"Play sound {sound_id}"

        else:
            text = f"Action: {self.action_type.value}"

        return text


@dataclass
class DialogueChoice:
    """Represents a player choice in dialogue"""

    choice_id: Optional[int] = None  # AnswerId for game integration
    text: str = ""
    next_node_id: str = ""
    conditions: List[DialogueCondition] = field(default_factory=list)
    actions: List[DialogueAction] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "choice_id": self.choice_id,
            "text": self.text,
            "next_node_id": self.next_node_id,
            "conditions": [cond.to_dict() for cond in self.conditions],
            "actions": [action.to_dict() for action in self.actions]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueChoice':
        """Create from dictionary"""
        return cls(
            choice_id=data.get("choice_id"),
            text=data.get("text", ""),
            next_node_id=data.get("next_node_id", ""),
            conditions=[DialogueCondition.from_dict(cond) for cond in data.get("conditions", [])],
            actions=[DialogueAction.from_dict(action) for action in data.get("actions", [])]
        )

    def is_available(self, context: Dict[str, Any] = None) -> bool:
        """Check if this choice is available based on conditions"""
        # This would be called during runtime to check conditions
        # For now, return True if no conditions
        if not self.conditions:
            return True

        # In a real implementation, this would evaluate conditions against game state
        return True


@dataclass
class DialogueNode:
    """Represents a single dialogue node"""

    node_id: str
    node_type: str = "npc"  # "npc", "player", "start", "end"
    speaker: str = ""
    text: str = ""
    answer_id: Optional[int] = None  # For response nodes
    choices: List[DialogueChoice] = field(default_factory=list)
    conditions: List[DialogueCondition] = field(default_factory=list)
    actions: List[DialogueAction] = field(default_factory=list)

    # Metadata
    tag: str = ""  # Localization tag
    sound_file: str = ""
    emote: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "speaker": self.speaker,
            "text": self.text,
            "answer_id": self.answer_id,
            "choices": [choice.to_dict() for choice in self.choices],
            "conditions": [cond.to_dict() for cond in self.conditions],
            "actions": [action.to_dict() for action in self.actions],
            "tag": self.tag,
            "sound_file": self.sound_file,
            "emote": self.emote
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueNode':
        """Create from dictionary"""
        return cls(
            node_id=data.get("node_id", ""),
            node_type=data.get("node_type", "npc"),
            speaker=data.get("speaker", ""),
            text=data.get("text", ""),
            answer_id=data.get("answer_id"),
            choices=[DialogueChoice.from_dict(choice) for choice in data.get("choices", [])],
            conditions=[DialogueCondition.from_dict(cond) for cond in data.get("conditions", [])],
            actions=[DialogueAction.from_dict(action) for action in data.get("actions", [])],
            tag=data.get("tag", ""),
            sound_file=data.get("sound_file", ""),
            emote=data.get("emote", "")
        )

    def to_lua(self) -> str:
        """Generate LUA code for this node"""
        lines = []
        lines.append(f"-- Dialogue Node: {self.node_id}")

        if self.conditions:
            lines.append("-- Node conditions:")
            for condition in self.conditions:
                lines.append(f"{condition.to_lua()},")

        if self.node_type == "npc" or self.node_type == "start":
            # NPC/Start node with choices
            if not self.choices:
                # Simple node without choices
                lines.append(f'Say{{Tag = "{self.tag}", String = "{self.text}"}}')
            else:
                # Node with choices
                lines.append('OnBeginDialog{')
                lines.append('    Conditions = {')
                for condition in self.conditions:
                    lines.append(f'        {condition.to_lua()},')
                lines.append('    },')
                lines.append('    Actions = {')
                lines.append(f'        Say{{Tag = "{self.tag}", String = "{self.text}"}},')
                for action in self.actions:
                    lines.append(f'        {action.to_lua()},')
                lines.append('    }')
                lines.append('}')

                # Add choices
                for i, choice in enumerate(self.choices):
                    choice_letter = chr(65 + i)  # A, B, C, etc.
                    lines.append(f'Answer{{Tag = "{self.tag}_choice_{choice_letter}", String = "{choice.text}", AnswerId = {choice.choice_id}}}')

        elif self.node_type == "response" and self.answer_id:
            # Response node
            lines.append(f'OnAnswer{{{self.answer_id};')
            lines.append('    Conditions = {')
            for condition in self.conditions:
                lines.append(f'        {condition.to_lua()},')
            lines.append('    },')
            lines.append('    Actions = {')
            lines.append('        Say{{Tag = "{}", String = "{}"}},'.format(self.tag, self.text))
            for action in self.actions:
                lines.append(f'        {action.to_lua()},')
            lines.append('    }')
            lines.append('}')

        return '\n'.join(lines)


@dataclass
class DialogueTree:
    """Represents a complete dialogue tree"""

    nodes: Dict[str, DialogueNode] = field(default_factory=dict)
    start_node_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "start_node_id": self.start_node_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueTree':
        """Create from dictionary"""
        tree = cls()
        tree.start_node_id = data.get("start_node_id", "")

        for node_id, node_data in data.get("nodes", {}).items():
            tree.nodes[node_id] = DialogueNode.from_dict(node_data)

        return tree

    def add_node(self, node: DialogueNode):
        """Add a node to the dialogue tree"""
        self.nodes[node.node_id] = node

    def get_node(self, node_id: str) -> Optional[DialogueNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)

    def validate(self) -> List[str]:
        """Validate the dialogue tree and return list of issues"""
        issues = []

        # Check start node
        if not self.start_node_id:
            issues.append("No start node specified")
        elif self.start_node_id not in self.nodes:
            issues.append(f"Start node '{self.start_node_id}' not found")

        # Check node connections
        for node_id, node in self.nodes.items():
            for choice in node.choices:
                if choice.next_node_id and choice.next_node_id not in self.nodes:
                    issues.append(f"Node '{node_id}' choice points to non-existent node '{choice.next_node_id}'")

        # Check AnswerIds
        used_answer_ids = {}
        for node_id, node in self.nodes.items():
            if node.answer_id:
                if node.answer_id in used_answer_ids:
                    issues.append(f"Duplicate AnswerId {node.answer_id} in nodes '{used_answer_ids[node.answer_id]}' and '{node_id}'")
                else:
                    used_answer_ids[node.answer_id] = node_id

            for choice in node.choices:
                if choice.choice_id:
                    if choice.choice_id in used_answer_ids:
                        issues.append(f"Duplicate AnswerId {choice.choice_id} in node '{used_answer_ids[choice.choice_id]}' and choice '{node_id}'")
                    else:
                        used_answer_ids[choice.choice_id] = f"{node_id}[choice]"

        return issues