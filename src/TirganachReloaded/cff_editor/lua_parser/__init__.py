"""
Lua Parser Package
Bidirectional parsers for SpellForce Lua scripts
"""

from .lua_data_manager import (
    LuaDataManager,
    get_lua_data_manager,
    get_quest_lua_data,
    parse_lua_scripts,
)
from .quest_lua_parser import (
    LuaQuestParser,
    QuestData,
    QuestDialogue,
    QuestObjective,
    QuestRequirement,
    QuestReward,
    create_example_quest,
    generate_quest_file,
    parse_quest_file,
)

__all__ = [
    # Quest Parser
    "LuaQuestParser",
    "parse_quest_file",
    "generate_quest_file",
    "create_example_quest",
    # Data Structures
    "QuestData",
    "QuestObjective",
    "QuestRequirement",
    "QuestReward",
    "QuestDialogue",
    # Data Manager
    "LuaDataManager",
    "get_lua_data_manager",
    "get_quest_lua_data",
    "parse_lua_scripts",
]

__version__ = "1.0.0"
