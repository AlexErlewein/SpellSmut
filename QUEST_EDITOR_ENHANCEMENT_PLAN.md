# Quest Editor Enhancement Plan

## Objective
Enhance the **existing Tirganach GUI Quest Editor (Qt/PySide6)** to display comprehensive quest information extracted from our Amra & Lea quest analysis, including:
- Dialogues from Lua scripts
- Quest rewards and XP
- Map locations
- File references
- Extended story context

**Technology Stack**: PySide6 (Qt for Python)  
**Target File**: `src/TirganachReloaded/cff_editor/widgets/quest_details_viewer.py`  
**Approach**: Modify existing Qt widgets and add new sections

## Current State Analysis

### Existing Components
1. **`quest_details_viewer.py`** - Main quest details display widget
   - Already has sections for: Basic Info, Quest Giver, Requirements, Objectives, Rewards, Dialogues, Relationships
   - Has platform/map name mappings (but incomplete)
   - Currently shows CFF data only with warnings about Lua data

2. **`quest_lua_parser.py`** - Lua script parser
   - Likely handles dialogue extraction from Lua files

3. **Data Files Available**:
   - `quest_reward_mappings.json` - Quest reward data
   - `lua_quest_cache.db` - Cached Lua quest data
   - Our new files: `quest_descriptions_complete.json`, `quest_maps_and_descriptions.json`

### Current Limitations
- Only shows CFF data (basic metadata)
- Lua data (dialogues, rewards, objectives) not integrated
- Map locations incomplete
- No file references shown
- No extended story context

---

## Enhancement Plan - Phase by Phase

### Phase 1: Data Integration Layer ✅ (Preparation)
**Goal**: Create a unified data service that combines CFF + Lua + our extracted data

**Tasks**:
1. Create `quest_data_service.py` - Central data access layer
2. Load and merge data from:
   - CFF files (existing)
   - `quest_descriptions_complete.json` (our extraction)
   - `quest_maps_and_descriptions.json` (map data)
   - `quest_reward_mappings.json` (existing rewards)
3. Provide unified API for quest details

**Output**: Service class that returns complete quest data

**Testing**: Unit test with Quest 379-391 to verify data merging

---

### Phase 2: Map Locations Display 🗺️
**Goal**: Show accurate map locations for each quest

**Tasks**:
1. Update `PLATFORM_NAMES` dictionary in `quest_details_viewer.py` with correct mappings:
   ```python
   "P1": "Liannon",
   "P6": "Wildland Pass / Greyfell area",
   "P7": "Ice Gate",
   "P15": "Desert / Burning Sands",
   "P25": "Godmark / Mountains",
   "P63": "Greyfell",
   ```

2. Add new section in `quest_details_viewer.py`:
   - **"Map Locations"** section
   - Display all maps where quest is active
   - Show map code + name
   - Highlight primary location

3. Update `load_quest_data()` to pull map data from service

**Output**: Map locations visible in quest details

**Testing**: 
- Load Quest 379 - should show P15 (Desert), P63 (Greyfell)
- Load Quest 380 - should show P63 (Greyfell)
- Load Quest 390 - should show P25 (Godmark), P7 (Ice Gate)

---

### Phase 3: Dialogues Enhancement 💬
**Goal**: Display all extracted dialogues with context

**Tasks**:
1. Enhance dialogues section to show:
   - Dialogue text (German)
   - English translation (if available)
   - Source file path
   - Dialogue type (Say, Answer, Outcry, Dialog)

2. Add expandable "Extended Story Dialogues" subsection:
   - Show narrative context dialogues
   - Display with translations

3. Format dialogues in tree structure:
   ```
   📁 Dialogues (12 found)
     ├── 📄 From script/P15/n0.lua
     │   ├── "Öffnet das Tor!" (Outcry)
     │   └── "Lasst die Horde ausrücken!" (Outcry)
     └── 📄 From script/P63/n2896.lua
         └── "Was soll es sein?" (Dialog)
   ```

**Output**: Rich dialogue display with context

**Testing**:
- Quest 379 - should show 3 dialogues from 2 files
- Quest 380 - should show extended story dialogues with translations

---

### Phase 4: Rewards Display 💰
**Goal**: Show quest rewards and XP

**Tasks**:
1. Update rewards section to display:
   - XP amount
   - Reward flag name (e.g., "AmraUndLea1Liannon1")
   - Items (if available)
   - Gold (if available)

2. Format as clear list:
   ```
   🎁 Quest Rewards
   ├── XP: 200
   ├── Reward Flag: AmraUndLea1Liannon1
   └── Source: GdsQuestRewards.lua
   ```

3. Handle multiple rewards (e.g., Quest 391 has 2 rewards)

**Output**: Complete reward information

**Testing**:
- Quest 380 - should show 200 XP
- Quest 391 - should show 800 XP + 1200 XP (2 rewards)

---

### Phase 5: File References 📁
**Goal**: Show which Lua files reference this quest

**Tasks**:
1. Add new section: **"Technical References"**
2. Display:
   - List of all Lua files that reference this quest
   - Number of references per file
   - File paths (clickable if possible)

3. Format as expandable tree:
   ```
   📂 Technical References (74 total references in 2 files)
   ├── script/p1/n1390.lua (73 references)
   └── script/P63/n2896.lua (1 reference)
   ```

**Output**: Developer-friendly file reference list

**Testing**:
- Quest 380 - should show 74 references in 2 files
- Quest 381 - should show 1,154 references in 2 files

---

### Phase 6: Quest Statistics 📊
**Goal**: Add summary statistics section

**Tasks**:
1. Add new section at top: **"Quest Statistics"**
2. Display:
   - Total dialogues found
   - Total Lua files involved
   - Total quest references
   - XP reward
   - Number of maps

3. Format as info cards:
   ```
   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
   │ 💬 Dialogues: 3 │  │ 📁 Files: 2     │  │ 🗺️ Maps: 2      │
   └─────────────────┘  └─────────────────┘  └─────────────────┘
   ```

**Output**: Quick overview stats

**Testing**: Verify stats match our extracted data

---

### Phase 7: Quest Chain Visualization 🔗
**Goal**: Show quest relationships visually

**Tasks**:
1. Enhance relationships section to show:
   - Parent quest (with name)
   - All subquests (with names)
   - Quest order index
   - Visual tree structure

2. Add navigation buttons:
   - "Go to Parent Quest"
   - "Go to Subquest" (for each subquest)

**Output**: Interactive quest chain navigation

**Testing**:
- Quest 379 - should show all 13 subquests
- Quest 380 - should show parent (379) and siblings

---

## Qt/PySide6 Implementation Details

### Existing Qt Widgets Used
The current `quest_details_viewer.py` already uses:
- `QGroupBox` - For section containers
- `QVBoxLayout`, `QHBoxLayout` - For layouts
- `QLabel` - For text display
- `QTextEdit` - For multi-line text
- `QScrollArea` - For scrollable content
- `QTreeWidget`, `QTreeWidgetItem` - For hierarchical data
- `QListWidget` - For lists

### New Qt Components We'll Add
1. **Statistics Cards** - Custom `QFrame` widgets with styled layouts
2. **Map Badges** - Styled `QLabel` or custom `QPushButton` widgets
3. **Dialogue Items** - `QGroupBox` with nested layouts for German/English text
4. **File Reference List** - `QListWidget` with custom item delegates
5. **Navigation Buttons** - `QPushButton` with signals to navigate quests

### Qt Styling Approach
```python
# Example: Statistics card styling
stat_card = QFrame()
stat_card.setStyleSheet("""
    QFrame {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 #667eea, stop:1 #764ba2);
        border-radius: 8px;
        padding: 15px;
    }
""")
```

### Signal/Slot Connections
- **Navigation buttons** → `quest_selected` signal to load parent/sibling quests
- **File references** → Optional: `file_clicked` signal to open Lua files
- **Expandable sections** → `toggled` signal for collapsible groups

---

## Implementation Strategy

### Step-by-Step Approach

1. **Create Data Service** (1-2 hours)
   - Write `quest_data_service.py`
   - Test data loading and merging
   - Verify with Amra & Lea quests

2. **Update Map Display** (30 mins)
   - Update platform names
   - Add map section
   - Test with sample quests

3. **Enhance Dialogues** (1 hour)
   - Update dialogue section
   - Add tree structure
   - Add translations

4. **Add Rewards** (30 mins)
   - Update rewards section
   - Format display
   - Test with various quests

5. **Add File References** (45 mins)
   - Create technical section
   - Display file list
   - Add reference counts

6. **Add Statistics** (30 mins)
   - Create stats section
   - Calculate metrics
   - Format display

7. **Enhance Relationships** (1 hour)
   - Update relationship display
   - Add navigation
   - Test quest chain

### Testing Plan

#### Unit Tests
- Test data service with known quest IDs
- Verify data merging logic
- Check edge cases (quests without rewards, etc.)

#### Integration Tests
- Load Quest 379 (main quest)
- Load Quest 380 (first subquest)
- Load Quest 390 (Craig's quest with multiple maps)
- Load Quest 391 (quest with multiple rewards)

#### UI Tests
- Check all sections display correctly
- Verify scrolling works
- Test with different window sizes
- Check performance with large quest chains

---

## Data Structure

### Quest Data Service API

```python
class QuestDataService:
    def get_quest_details(self, quest_id: int) -> QuestDetails:
        """Get complete quest information"""
        pass
    
    def get_quest_dialogues(self, quest_id: int) -> List[Dialogue]:
        """Get all dialogues for quest"""
        pass
    
    def get_quest_rewards(self, quest_id: int) -> QuestRewards:
        """Get quest rewards"""
        pass
    
    def get_quest_maps(self, quest_id: int) -> List[MapLocation]:
        """Get map locations"""
        pass
    
    def get_quest_files(self, quest_id: int) -> List[FileReference]:
        """Get Lua file references"""
        pass
    
    def get_quest_statistics(self, quest_id: int) -> QuestStatistics:
        """Get quest statistics"""
        pass
```

### Data Models

```python
@dataclass
class QuestDetails:
    quest_id: int
    name: str
    description: str
    parent_id: int
    order_index: int
    name_id: int
    description_id: int

@dataclass
class Dialogue:
    text: str
    translation: str | None
    source_file: str
    dialogue_type: str  # Say, Answer, Outcry, Dialog

@dataclass
class QuestRewards:
    xp: int
    reward_flags: List[str]
    items: List[str]
    gold: int

@dataclass
class MapLocation:
    code: str  # P1, P6, etc.
    name: str  # Liannon, Wildland Pass, etc.

@dataclass
class FileReference:
    path: str
    reference_count: int

@dataclass
class QuestStatistics:
    total_dialogues: int
    total_files: int
    total_references: int
    total_maps: int
    xp_reward: int
```

---

## Files to Modify

1. **New Files**:
   - `src/TirganachReloaded/cff_editor/services/quest_data_service.py`
   - `src/TirganachReloaded/cff_editor/models/quest_models.py`

2. **Modify**:
   - `src/TirganachReloaded/cff_editor/widgets/quest_details_viewer.py`
   - Update sections and add new ones

3. **Data Files to Use**:
   - `/Users/alex/Desktop/code/Others/SpellSmut/quest_descriptions_complete.json`
   - `/Users/alex/Desktop/code/Others/SpellSmut/quest_maps_and_descriptions.json`
   - Existing reward mappings

---

## Success Criteria

### Phase Completion Checklist

- [ ] Phase 1: Data service loads and merges all data sources
- [ ] Phase 2: Map locations display correctly for all quests
- [ ] Phase 3: Dialogues show with translations and context
- [ ] Phase 4: Rewards display with XP and flags
- [ ] Phase 5: File references list all Lua files
- [ ] Phase 6: Statistics show accurate counts
- [ ] Phase 7: Quest chain navigation works

### Final Validation

Test with complete Amra & Lea quest chain (379-391, 393):
- ✅ All 14 quests load without errors
- ✅ All sections populated with correct data
- ✅ UI remains responsive
- ✅ Data matches our extracted documentation
- ✅ Navigation between quests works

---

## Next Steps

**Immediate Action**: 
1. Review this plan
2. Confirm approach
3. Start with Phase 1 (Data Service)
4. Test incrementally after each phase

**Questions to Answer**:
1. Should we copy our JSON files to `src/TirganachReloaded/data/`?
2. Do we want clickable file paths that open Lua files?
3. Should dialogues be editable or read-only?
4. Do we want export functionality (export quest details to markdown)?

---

*Plan created: 2025-11-02*  
*Target quests: Amra and Lea chain (379-391, 393)*  
*Estimated total time: 5-7 hours*
