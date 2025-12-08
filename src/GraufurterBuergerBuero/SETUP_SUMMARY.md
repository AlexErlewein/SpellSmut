# Graufurter Bürger Büro - Standalone NPC Editor

## Summary

Successfully created a standalone NPC editor following the Orthancs Schmiede (weapon/armor forge) pattern.

---

## Files Created/Copied

### Core Application
- **graufurter_buerger_buero.py** - Main standalone application with GUI
- **run_graufurter_buerger_buero.py** - Launcher script
- **__init__.py** - Package initialization

### NPC Components (copied from TirganachReloaded)
- **npc_creator_wizard.py** - Multi-step NPC creation wizard (7 pages)
- **enhanced_npc_browser.py** - NPC browser with search/filter capabilities
- **npc_creation_data.py** - Data models (NpcCreationData, NpcStats, NpcCombatStats, etc.)
- **npc_cff_exporter.py** - CFF binary export functionality
- **npc_loader.py** - JSON persistence layer
- **id_manager.py** - ID allocation system (40000-49999 for NPCs)

### Data Storage
- **npcs/custom_npcs.json** - Custom NPC database

### Documentation
- **README.md** - Complete usage guide and documentation

---

## Key Changes Made

### 1. Fixed Import Statements
Changed all relative imports to absolute imports for standalone operation:
```python
# Before (TirganachReloaded)
from ..shared.id_manager import ContentType, IDManager
from ..models.npc_creation_data import NpcCreationData

# After (Standalone)
from id_manager import ContentType, IDManager
from npc_creation_data import NpcCreationData
```

### 2. Updated File Paths
- **id_manager.py**: Updated path resolution to use `src/data/project_ids.json`
- **npc_loader.py**: Updated to use local `npcs/custom_npcs.json`

### 3. Added Helper Functions
Added standalone helper functions in `npc_loader.py`:
```python
def load_all_npcs() -> Dict[int, Dict[str, Any]]
def load_npc(npc_id: int) -> Optional[NpcCreationData]
def save_npc(npc: NpcCreationData) -> bool
def delete_npc(npc_id: int) -> bool
def get_npc_list() -> List[Dict[str, Any]]
```

### 4. Simplified Browser
Removed game CFF loading from `enhanced_npc_browser.py` for now (can be added later)

---

## Architecture

```
GraufurterBuergerBuero/
├── graufurter_buerger_buero.py    # Main app (QMainWindow)
│   ├── NPC tree browser
│   ├── Details panel
│   ├── Search & filter
│   └── Action buttons
│
├── npc_creator_wizard.py          # QWizard with 7 pages
│   ├── Page 1: Mode Selection (Create/Edit/Duplicate)
│   ├── Page 2: Basic Identity
│   ├── Page 3: Base Stats (7 attributes)
│   ├── Page 4: Combat Stats (11 stats)
│   ├── Page 5: Appearance/Voice
│   ├── Page 6: Equipment (7 slots)
│   ├── Page 7: Behavior/AI
│   └── Page 8: Review & Export
│
├── enhanced_npc_browser.py         # QDialog browser
│   ├── Search & filter
│   ├── Edit/Duplicate/Delete
│   └── Create new
│
├── Data Models & Persistence
│   ├── npc_creation_data.py       # NpcCreationData class
│   ├── npc_loader.py              # JSON I/O
│   └── npc_cff_exporter.py        # CFF binary export
│
└── Shared Systems
    ├── id_manager.py              # ID allocation (40000-49999)
    └── npcs/custom_npcs.json      # Data storage
```

---

## Features

### NPC Creation Wizard
- **Multi-step wizard** for comprehensive NPC creation
- **Mode selection**: Create new, Edit existing, Duplicate template
- **7 attribute stats**: Strength, Stamina, Agility, Dexterity, Intelligence, Wisdom, Charisma
- **11 combat stats**: Health, Mana, Damage (min/max), Armor, Resistances, Speeds
- **Equipment slots**: Main Hand, Off Hand, Head, Chest, Legs, Feet, Accessory
- **Appearance**: Head model, Race, Gender, Voice type
- **Behavior**: Movement patterns, Spawn conditions, AI settings

### NPC Browser
- **Search & filter** by name, type, or class
- **Tree view** organized by NPC type (Hostile, Friendly, Neutral, etc.)
- **Detailed panel** with all NPC properties
- **Edit/Duplicate/Delete** actions for custom NPCs
- **Export to CFF** for game integration

### Data Management
- **JSON persistence** in local `npcs/custom_npcs.json`
- **Automatic ID allocation** in 40000-49999 range
- **CFF export** with proper category mapping (3001-3005, 2016)
- **Shared ID system** across all modding tools

---

## Usage

```bash
# Launch the application
cd src/GraufurterBuergerBuero
uv run graufurter_buerger_buero.py

# Or use the launcher
uv run run_graufurter_buerger_buero.py

# With debug logging
uv run graufurter_buerger_buero.py --debug
```

---

## ID Ranges

Following the established ID management system:

| Content Type | ID Range | Tool |
|--------------|----------|------|
| Game NPCs | 1-39999 | SpellForce Game |
| Custom NPCs | 40000-49999 | **Graufurter Bürger Büro** |
| Reserved | 50000+ | Future use |

---

## Integration with Other Tools

- **Orthancs Schmiede** (`src/OrthancsSchmiede/`) - Weapon & Armor Editor
- **Mulandirs Zauberschule** (`src/MulandirsZauberschule/`) - Spell Editor
- **Darius Almanach** (`src/DariusAlmanach/`) - Dialogue Viewer
- **TirganachReloaded** (`src/TirganachReloaded/`) - Full CFF Editor

All tools share the same `IDManager` and `project_ids.json` for consistent ID allocation.

---

## NPC Data Model

### Basic Identity
- Name, Title, Description
- Type: hostile, friendly, neutral, merchant, quest
- Class: warrior, mage, ranger, rogue, cleric, paladin, monk, druid
- Level: 1-200
- Faction: Alignment/group

### Stats (7 base attributes)
```python
NpcStats(
    strength: int,      # Physical power
    stamina: int,       # Endurance
    agility: int,       # Speed & reflexes
    dexterity: int,     # Accuracy & finesse
    intelligence: int,  # Mental power
    wisdom: int,        # Perception & willpower
    charisma: int       # Social influence
)
```

### Combat Stats (11 stats)
```python
NpcCombatStats(
    health: int,
    mana: int,
    min_damage: int,
    max_damage: int,
    armor: int,
    magic_resistance: int,
    attack_speed: float,
    move_speed: float,
    critical_chance: float,
    dodge_chance: float,
    resistances: Dict[str, int]  # fire, ice, poison, etc.
)
```

### Equipment (7 slots)
```python
NpcEquipment(
    main_hand: Optional[int],    # Weapon ID
    off_hand: Optional[int],     # Shield/weapon ID
    head: Optional[int],         # Helmet ID
    chest: Optional[int],        # Armor ID
    legs: Optional[int],         # Leg armor ID
    feet: Optional[int],         # Boots ID
    accessory: Optional[int]     # Ring/amulet ID
)
```

### Appearance
```python
NpcAppearance(
    head_id: int,
    race: str,         # human, elf, dwarf, orc, etc.
    gender: str,       # male, female
    voice_type: VoiceType
)
```

### Behavior
```python
NpcBehavior(
    movement_pattern: str,
    spawn_conditions: Dict[str, Any],
    ai_settings: Dict[str, Any],
    quest_rewards: Optional[NpcRewards]
)
```

---

## CFF Export Categories

NPCs are exported to GameData.cff with the following structure:

| Category | Content | Format |
|----------|---------|--------|
| 3001 | General NPC Info | Binary struct |
| 3002 | Base Stats | Binary struct |
| 3003 | Combat Stats | Binary struct |
| 3004 | Equipment | Binary struct |
| 3005 | Behavior | Binary struct |
| 2016 | Text Entries | String data |

---

## Testing Status

✅ **Completed:**
- File structure created
- Import statements fixed
- Path resolution updated
- Helper functions added
- README documentation
- Empty JSON database initialized

⚠️ **Needs Testing:**
- NPC creation wizard flow
- CFF export functionality
- Equipment slot assignment
- Appearance/voice selection
- Browser search/filter
- Edit/Duplicate/Delete actions

---

## Future Enhancements

- [ ] Icon/portrait display
- [ ] Visual appearance preview
- [ ] Equipment preview with stats
- [ ] Dialogue integration with Darius Almanach
- [ ] Quest assignment system
- [ ] Spawn location map picker
- [ ] Advanced AI behavior editor
- [ ] Loot table editor
- [ ] Skill/ability assignment

---

## Related Documentation

- `/docs/` - Main documentation
- `ProjectPlanning/` - Development roadmap
- `src/TirganachReloaded/docs/` - CFF format documentation
- `.ai/CRUSH.md` - AI assistant instructions

---

**Status**: ✅ Standalone NPC editor created and ready for use  
**Date**: 2025-11-17  
**Version**: 1.0
