#!/usr/bin/env python3
"""Diagnostic script to see what quest_viewer_standalone.py would display"""

import sys
from pathlib import Path

# Add src to path (same as quest_viewer_standalone.py)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.data_model import CFFDataModel
from TirganachReloaded.cff_editor.logging_config import configure_logging, get_logger
from TirganachReloaded.cff_editor.lua_parser.lua_data_manager import LuaDataManager

print("=" * 80)
print("DIAGNOSTIC: What quest_viewer_standalone.py would display")
print("=" * 80)

# Configure logging
configure_logging()
logger = get_logger("diagnostic")

# Initialize data model (same as simple_quest_viewer.py)
data_model = CFFDataModel()

# Load GameData.cff file (same path as simple_quest_viewer.py)
cff_file = Path("OriginalGameFiles/data/GameData.cff")
if not cff_file.exists():
    print(f"❌ GameData.cff not found at: {cff_file}")
    sys.exit(1)

print(f"✅ Loading CFF file: {cff_file}")
if not data_model.load_file(str(cff_file)):
    print("❌ Failed to load GameData.cff")
    sys.exit(1)

# Initialize Lua data manager (same as quest_viewer_standalone.py)
# Use absolute cache path to avoid creating duplicate cache directories
cache_dir = project_root / "src" / "TirganachReloaded" / "data" / "cache"
lua_manager = LuaDataManager(cache_dir=cache_dir)

# Load quest data from CFF (EXACTLY as quest_viewer_standalone.py does)
quest_data = {}

quests = data_model.get_elements("quests")
if not quests:
    print("❌ No quests found in CFF file")
    sys.exit(1)

print(f"✅ Found {len(quests)} quests in CFF file")

# Extract quest information (EXACTLY as simple_quest_viewer.py does)
for quest in quests:
    quest_id = getattr(quest, "quest_id", None)
    if quest_id is None:
        continue

    # Get quest name (try localized first)
    name = data_model.get_localised_text(quest, "name")
    if not name:
        name = getattr(quest, "name", f"Quest {quest_id}")

    # Get description
    description = data_model.get_localised_text(quest, "description")
    if not description:
        description = getattr(quest, "description", "")

    # Get parent ID and order
    parent_id = getattr(quest, "parent_quest_id", None)
    order_index = getattr(quest, "order_index", 0)

    # Store quest data
    quest_data[quest_id] = {
        "id": quest_id,
        "name": name,
        "description": description,
        "parent_id": parent_id,
        "order_index": order_index,
    }

print(f"✅ Loaded {len(quest_data)} quests")

# Now enhance with Lua data (same as simple_quest_viewer.py)
if lua_manager:
    if not lua_manager.cache_loaded:
        lua_manager.preload_cache()

    quest_ids = lua_manager.get_all_quest_ids()
    print(f"✅ Found {len(quest_ids)} quests in Lua cache")

    lua_enhanced_count = 0
    for quest_id in quest_ids:
        quest_data_obj = lua_manager.get_quest_data(quest_id)
        if quest_data_obj and quest_id in quest_data:
            # Enhance existing quest data (don't overwrite name!)
            quest_data[quest_id].update(
                {
                    "platform": quest_data_obj.platform,
                    "npc_id": quest_data_obj.npc_id,
                    "objectives": quest_data_obj.objectives,
                    "requirements": quest_data_obj.requirements,
                    "rewards": quest_data_obj.rewards,
                    "dialogues": quest_data_obj.dialogues,
                }
            )
            lua_enhanced_count += 1

    print(f"✅ Enhanced {lua_enhanced_count} quests with Lua data")

# Show what would be displayed in the tree
print("\n" + "=" * 80)
print("TREE VIEW DATA (First 30 quests)")
print("=" * 80)
print(f"{'Quest ID':<12} | {'Name'}")
print("-" * 80)

for quest_id in sorted(quest_data.keys())[:30]:
    name = quest_data[quest_id]["name"]
    parent_id = quest_data[quest_id]["parent_id"]
    indent = "  " if parent_id else ""
    print(f"{indent}{quest_id:<12} | {name}")

# Statistics
print("\n" + "=" * 80)
print("STATISTICS")
print("=" * 80)

names_count = sum(
    1 for q in quest_data.values() if q["name"] and not q["name"].startswith("Quest ")
)
generic_names = sum(1 for q in quest_data.values() if q["name"].startswith("Quest "))
no_names = sum(1 for q in quest_data.values() if not q["name"])

print(f"Total quests: {len(quest_data)}")
print(f"Quests with proper names: {names_count}")
print(f"Quests with generic names: {generic_names}")
print(f"Quests with no names: {no_names}")

if generic_names > 0:
    print(f"\n⚠️  WARNING: {generic_names} quests have generic names!")
    print("Sample quests with generic names:")
    count = 0
    for quest_id, quest_info in sorted(quest_data.items()):
        if quest_info["name"].startswith("Quest ") and count < 10:
            print(f"  Quest {quest_id}: {quest_info['name']}")
            count += 1
else:
    print(f"\n✅ SUCCESS: All {names_count} quests have proper names!")
