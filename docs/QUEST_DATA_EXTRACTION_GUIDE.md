# Quest Data Extraction Technical Guide

## Overview

This guide explains how to extract comprehensive quest data from SpellForce game files, including rewards, dialogues, objectives, and metadata.

---

## Data Sources

### 1. GameData.cff
**Location**: `OriginalGameFiles/data/GameData.cff`

**Contains**:
- Quest hierarchy (parent-child relationships)
- Quest names (German, localized)
- Quest descriptions (German text)
- Quest IDs and order indices
- Text reference IDs (name_id, description_id)

**Accessed via**: `CFFDataModel` class

```python
from TirganachReloaded.cff_editor.data_model import CFFDataModel

data_model = CFFDataModel()
data_model.load_file("OriginalGameFiles/data/GameData.cff")

# Get all quests
quests = data_model.get_elements("quests")

# Get localized name
name = data_model.get_localised_text(quest, "name")
```

---

### 2. GdsQuestRewards.lua
**Location**: `ModdingTools/SpellForceLUASources/script/GdsQuestRewards.lua`

**Contains**:
- XP rewards for quests
- Item rewards (item IDs)
- Money rewards (Gold, Silver, Copper)
- Reward flags (quest completion flags)
- Platform organization (P1, P63, etc.)

**Format**:
```lua
QuestRewardsP1 = {
    GeistInDerMine = { 
        XP = {35}, 
        Money = {Silver = 2, Copper = 50}
    },
    WegNachEloni1Snarf = { 
        XP = {25}, 
        Items = {626}  -- Simple Metal Helmet
    },
}
```

**Extraction Script**: `src/helper_tools/quest_extraction/extract_gds_quest_rewards.py`

**Statistics** (from GdsQuestRewards.lua):
- Total rewards: 450
- Platforms covered: 47
- With XP: 449 quests
- With items: 47 quests
- With money: 21 quests

---

### 3. Lua Quest Scripts
**Location**: `ModdingTools/SpellForceLUASources/script/p*/`

**Contains**:
- Quest objectives (Kill X, Collect Y)
- Quest requirements (level, previous quests)
- Quest giver assignments (NPC IDs)
- Dialogue branching logic
- Quest state management

**Accessed via**: `LuaDataManager` class (cached in SQLite)

```python
from TirganachReloaded.cff_editor.lua_parser.lua_data_manager import LuaDataManager

lua_manager = LuaDataManager(cache_dir="path/to/cache")
quest_data = lua_manager.get_quest_data(quest_id)

# Access objectives, requirements, dialogues, etc.
objectives = quest_data.objectives
rewards = quest_data.rewards
```

---

## Extraction Tools

### 1. Extract Quest Rewards (Complete)

**Script**: `src/helper_tools/quest_extraction/extract_gds_quest_rewards.py`

**Purpose**: Parse GdsQuestRewards.lua to extract all reward data

**Usage**:
```bash
python src/helper_tools/quest_extraction/extract_gds_quest_rewards.py
```

**Output Files**:
1. `quest_rewards_complete.json` - Structured JSON for QuestDataService
2. `quest_rewards_complete.csv` - Human-readable CSV for review

**JSON Structure**:
```json
{
  "rewards_by_quest_id": {
    "357": {
      "xp": 30,
      "gold": 0,
      "silver": 0,
      "copper": 0,
      "items": [],
      "flags": ["WundtinkturValdis"],
      "platform": "P63"
    }
  },
  "rewards_without_quest_id": [
    {
      "reward_name": "UnmappedReward",
      "platform": "P1",
      "xp": 100,
      "items": [532]
    }
  ],
  "statistics": {
    "total_rewards": 450,
    "with_quest_id": 197,
    "without_quest_id": 253
  }
}
```

**Key Features**:
- Handles nested braces in Lua tables
- Supports multiple encodings (UTF-8, Latin-1, CP1252)
- Maps reward names to quest IDs using existing mappings
- Merges multiple rewards for same quest
- Provides detailed statistics

---

### 2. Quest Description Extraction

**Script**: `src/helper_tools/quest_extraction/extract_quest_descriptions.py`

**Purpose**: Extract quest descriptions and dialogues from Lua files

**Usage**:
```bash
python src/helper_tools/quest_extraction/extract_quest_descriptions.py
```

**Output**: `quest_descriptions_complete.json`

---

### 3. Map Location Extraction

**Script**: `src/helper_tools/quest_extraction/extract_map_and_descriptions.py`

**Purpose**: Extract quest map/platform locations

**Output**: `quest_maps_and_descriptions.json`

---

## Data Integration

### QuestDataService

**Purpose**: Centralized service for accessing enhanced quest data

**Location**: `src/TirganachReloaded/cff_editor/services/quest_data_service.py`

**Usage**:
```python
from TirganachReloaded.cff_editor.services.quest_data_service import QuestDataService

service = QuestDataService(project_root)

# Get enhanced quest data
quest_data = service.get_enhanced_quest_data(
    quest_id=380,
    cff_data=cff_quest_dict
)

# Access merged data
print(f"XP: {quest_data.rewards.xp}")
print(f"Items: {quest_data.rewards.items}")
print(f"Dialogues: {len(quest_data.dialogues)}")
print(f"Maps: {quest_data.map_locations}")
```

**Data Sources** (loaded in priority order):
1. `quest_rewards_complete.json` - Full reward data with items/money
2. `quest_maps_and_descriptions.json` - Map locations
3. `quest_descriptions_complete.json` - Lua dialogue references
4. Hardcoded special dialogues (Amra & Lea quests)

---

## Data Models

### QuestReward
```python
@dataclass
class QuestReward:
    xp: int = 0
    gold: int = 0
    silver: int = 0
    copper: int = 0
    items: List[str] = field(default_factory=list)
    reward_flags: List[str] = field(default_factory=list)
    source: str = "script/GdsQuestRewards.lua"
```

### Dialogue
```python
@dataclass
class Dialogue:
    text: str  # German text
    translation: Optional[str] = None  # English
    source_file: str = ""
    dialogue_type: str = "Standard"  # or "Story"
```

### MapLocation
```python
@dataclass
class MapLocation:
    code: str  # e.g., "P1", "P63"
    name: str  # e.g., "Liannon", "Greyfell"
```

### EnhancedQuestData
```python
@dataclass
class EnhancedQuestData:
    quest_id: int
    name: str
    description: str
    parent_id: int = 0
    order_index: int = 0
    
    # Enhanced data
    map_locations: List[MapLocation]
    dialogues: List[Dialogue]
    rewards: Optional[QuestReward]
    file_references: List[FileReference]
    statistics: Optional[QuestStatistics]
```

---

## Mapping Reward Names to Quest IDs

### Challenge
The GdsQuestRewards.lua file uses reward names (e.g., "GeistInDerMine") but doesn't directly reference quest IDs. We need to map these names to quest IDs.

### Current Mapping Status
- **Mapped**: 197 rewards (43.8%)
- **Unmapped**: 253 rewards (56.2%)

### Mapping Sources

**1. FINAL_REWARD_WITH_QUEST_IDS.csv**
```csv
Reward_Name,Platform,Quest_ID,XP,Items,Confidence,Language
"GeistInDerMine","P1",36,35,"[]",0.900,"German"
```

**2. Manual Mapping Required**
For unmapped rewards, use:
- `quest_rewards_complete.csv` - Review unmapped entries
- Quest descriptions in CFF - Match reward names to quest text
- Lua dialogue files - Find reward calls in quest scripts

### Mapping Strategy

**Semi-Automated Approach**:
1. Extract quest descriptions from CFF
2. Tokenize reward names (split CamelCase)
3. Match tokens to quest description text
4. Calculate confidence score
5. Manual review of low-confidence matches

**Example**:
```
Reward Name: "GeistInDerMine"
Tokens: ["Geist", "In", "Der", "Mine"]
Quest Description: "...Geist eines Menschen in der Mine..."
Match: HIGH confidence → Quest ID 36
```

---

## Advanced Extraction

### Extract Objectives from Lua

Objectives are defined in Lua quest scripts, not in reward tables.

**Pattern to Find**:
```lua
-- In quest script files
Quest_Objectives = {
    Objective1 = "Kill 5 Orcs",
    Objective2 = "Collect 3 Items",
}
```

**TODO**: Create extraction script for quest objectives

---

### Extract Requirements

Requirements are also in Lua scripts:

```lua
Quest_Requirements = {
    MinLevel = 10,
    PreviousQuest = 123,
    RequiredItem = 456,
}
```

**TODO**: Create extraction script for requirements

---

### Extract NPC Assignments

Quest givers are assigned in NPC dialogue scripts:

```lua
-- In NPC script (e.g., p1/n1234.lua)
GiveQuest("GeistInDerMine")
```

**TODO**: Create extraction script to map NPCs to quests

---

## Data Quality & Completeness

### Current Coverage

| Data Type | Source | Coverage | Status |
|-----------|--------|----------|--------|
| Quest Names | CFF | 1040 (100%) | ✅ Complete |
| Quest Descriptions | CFF | 1040 (100%) | ✅ Complete |
| Quest Hierarchy | CFF | 1040 (100%) | ✅ Complete |
| XP Rewards | Lua | 449 (43%) | ✅ Extracted |
| Item Rewards | Lua | 47 (4.5%) | ✅ Extracted |
| Money Rewards | Lua | 21 (2%) | ✅ Extracted |
| Reward Mappings | Manual | 197 (43.8%) | 🔶 Partial |
| Dialogues | Lua | ~50 special | 🔶 Partial |
| Objectives | Lua | 0 (0%) | ❌ Not extracted |
| Requirements | Lua | 0 (0%) | ❌ Not extracted |
| NPC Assignments | Lua | 0 (0%) | ❌ Not extracted |

---

## Best Practices

### 1. Always Backup
Before running extraction scripts, backup existing data files:
```bash
cp quest_rewards_complete.json quest_rewards_complete.json.bak
```

### 2. Use Debug Mode
Run scripts with debug output to diagnose issues:
```python
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    main()
```

### 3. Validate Extracted Data
After extraction, verify:
- Total count matches expectations
- No duplicate entries
- All required fields are present
- Data types are correct

### 4. Cache Results
Large extractions should be cached:
- Use pickle for Python objects
- Use JSON for human-readable data
- Include timestamp and version info

---

## Troubleshooting

### Issue: UnicodeDecodeError
**Symptom**: Can't read Lua files
**Solution**: Try multiple encodings
```python
encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
for encoding in encodings:
    try:
        with open(file, "r", encoding=encoding) as f:
            content = f.read()
        break
    except UnicodeDecodeError:
        continue
```

### Issue: Regex Not Matching
**Symptom**: Extraction returns 0 results
**Solution**: Test regex patterns interactively
```python
import re
test_line = 'RewardName = { XP = {100}, Items = {532}}'
pattern = r'(\w+)\s*=\s*\{(.+)\}\s*,?'
match = re.match(pattern, test_line)
print(match.groups() if match else "NO MATCH")
```

### Issue: Missing Quest IDs
**Symptom**: Many rewards show "UNMAPPED"
**Solution**: Update reward mapping CSV file
1. Review `quest_rewards_complete.csv`
2. Match reward names to quest descriptions
3. Add mappings to `FINAL_REWARD_WITH_QUEST_IDS.csv`
4. Re-run extraction script

---

## Future Enhancements

### Priority 1: Complete Reward Mappings
- **Goal**: Map all 253 unmapped rewards to quest IDs
- **Method**: Text matching + manual review
- **Impact**: 100% reward data coverage

### Priority 2: Extract Objectives
- **Goal**: Parse Lua files for quest objectives
- **Method**: Pattern matching in quest scripts
- **Impact**: Show "Kill X, Collect Y" in viewer

### Priority 3: Extract Requirements
- **Goal**: Get quest prerequisites (level, previous quests)
- **Method**: Parse Lua requirement tables
- **Impact**: Show quest availability conditions

### Priority 4: Item Name Lookup
- **Goal**: Convert item IDs to item names
- **Method**: Parse item database from CFF
- **Impact**: Show "Steel Sword" instead of "Item 626"

---

## References

### File Locations
- CFF File: `OriginalGameFiles/data/GameData.cff`
- Reward Script: `ModdingTools/SpellForceLUASources/script/GdsQuestRewards.lua`
- Quest Scripts: `ModdingTools/SpellForceLUASources/script/p*/`
- Data Output: `src/TirganachReloaded/data/`
- Extraction Tools: `src/helper_tools/quest_extraction/`

### Key Classes
- `CFFDataModel`: CFF file access
- `LuaDataManager`: Lua cache management
- `QuestDataService`: Enhanced quest data
- `GdsQuestRewardsParser`: Reward extraction

### Documentation
- `QUEST_VIEWER_COMPLETE_V2.md`: User guide
- `QUEST_DATA_EXTRACTION_GUIDE.md`: This file
- `README.md`: Project overview

---

## Conclusion

The quest data extraction system provides comprehensive access to SpellForce quest information from multiple sources. With proper tooling and methodology, we can extract and integrate nearly all quest-related data for use in the quest viewer and other tools.

**Current Status**: ✅ Core data extraction complete, enhancements ongoing
**Next Steps**: Complete reward mappings, extract objectives and requirements