# Weapon Creation System Plan
## ⚔️ The Weapon Forge

## Overview

This plan defines a comprehensive **Weapon Creation System** - a wizard-style interface for creating and editing custom SpellForce weapons. Users can create entirely new weapons, edit existing ones, define new weapon types, and manage weapon materials—all without writing code. The system includes an **ID Management System** to prevent conflicts across all game content (quests, spells, weapons).

**Status**: 🟡 Planning Phase  
**Priority**: High  
**Dependencies**: Quest Creator, Spell Creator (for ID Manager integration)

---

## System Goals

### Primary Objectives

1. **Weapon Forge Wizard**: 5-step guided weapon creation interface
2. **Edit Existing Weapons**: Load, modify, and save weapons under new IDs (719 weapons available)
3. **New Weapon Types**: Create custom weapon categories beyond the 20 base types
4. **Material System**: Define weapon materials (metal, wood, bone, crystal, etc.)
5. **ID Management System**: Centralized ID allocation for all content types ⭐ **NEW!**
6. **Export to CFF**: Generate GameData entries for weapons

### Secondary Objectives

- Weapon stat calculator (DPS, balance rating)
- Visual icon assignment (from extracted 4096+ item icons)
- Sound effect mapping (20 weapon types × hit/miss sounds)
- Weapon set support (matching equipment pieces)
- Import/Export weapon templates
- Batch edit multiple weapons

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Weapon Creation Workflow                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Weapon     │─▶│   Stats &    │─▶│   Visual &   │      │
│  │   Forge      │  │  Requirements│  │   Export     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│        │                  │                  │              │
│        ▼                  ▼                  ▼              │
│  Basic Info          Damage/Speed       Icon + Sounds       │
│  Type & Material     Requirements       CFF Export          │
│  New/Edit Mode       Rarity             ID Management       │
│        │                  │                  │              │
│        └──────────────────┴──────────────────┘              │
│                           │                                 │
│                           ▼                                 │
│                  ┌──────────────┐                           │
│                  │      ID      │                           │
│                  │   Manager    │ ⭐ SHARED SYSTEM         │
│                  └──────────────┘                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Weapon System Fundamentals

### Existing Weapon Types (20 Base Types)

| ID | Type | Hands | Category | Examples |
|----|------|-------|----------|----------|
| 0 | Default/Fist | Unarmed | Melee | Bare hands |
| 1 | Mouth/Bite | Natural | Melee | Beast attacks |
| 2 | Unarmed/Fist | Unarmed | Melee | Monk attacks |
| 3 | Dagger | 1H | Melee | Short blade, fast |
| 4 | Sword | 1H | Melee | Standard blade |
| 5 | Axe | 1H | Melee | Chopping weapon |
| 6 | Mace (Spiky) | 1H | Melee | Crushing + piercing |
| 7 | Mace (Blunt) | 1H | Melee | Pure crushing |
| 8 | Hammer | 1H | Melee | Heavy blunt |
| 9 | Staff | 1H | Melee | Magic focus |
| 10 | Sword | 2H | Melee | Longsword, greatsword |
| 11 | Axe | 2H | Melee | Battleaxe, greataxe |
| 12 | Mace | 2H | Melee | Warhammer variant |
| 13 | Hammer | 2H | Melee | Maul, sledgehammer |
| 14 | Staff | 2H | Magic | Wizard staff |
| 15 | Spear | 2H | Melee/Range | Piercing polearm |
| 16 | Halberd | 2H | Melee | Axe-spear hybrid |
| 17 | Bow | 2H | Ranged | Arrows |
| 18 | Crossbow | 2H | Ranged | Bolts |
| 19 | Claw | 1H | Melee | Beast claw |

**New Weapon Types We Can Add**:
- Katana (1H curved sword)
- Scimitar (1H curved blade)
- Rapier (1H piercing sword)
- Wand (1H magic focus)
- Throwing Knife (1H ranged)
- Whip (1H flexible)
- Scythe (2H reaper weapon)
- Lance (2H mounted)
- Glaive (2H polearm)
- Shield Bash (1H defensive weapon)
- Dual Wield (paired weapons)
- Chakram (1H throwing disc)

### Weapon Stats Structure

Every weapon has these core properties:

```json
{
  "item_id": 28,
  "name": "Flameblade Sword",
  "weapon_type_id": 4,        // 1H Sword
  "weapon_material_id": 5,    // Metal
  "min_damage": 12,
  "max_damage": 18,
  "weapon_speed": 100,        // Attack speed (lower = faster)
  "min_range": 0,             // Minimum attack range
  "max_range": 2,             // Maximum attack range
  "requirements": {
    "strength": 10,
    "dexterity": 5,
    "intelligence": 0,
    "level": 3
  },
  "effects": [],              // Special effects (poison, fire, etc.)
  "sell_value": 50,
  "buy_value": 100,
  "rarity": "RARE",
  "item_set_id": 0,           // Part of weapon set?
  "icon_handle": "ui_item_equip_weapon_sword_flame"
}
```

---

## Phase 1: ID Management System (SHARED ACROSS ALL CREATORS)

### 1.1 ID Manager Architecture

**IDManager Class** - Centralized ID allocation for all content types

```python
from enum import Enum
from typing import Dict, List, Optional, Set
import json

class ContentType(Enum):
    """Types of game content that need unique IDs"""
    QUEST = "quest"
    SPELL = "spell"
    WEAPON = "weapon"
    ARMOR = "armor"
    ITEM = "item"
    NPC = "npc"
    CREATURE = "creature"
    BUILDING = "building"

class IDRange:
    """ID range allocation for each content type"""
    
    # Official game ranges (DO NOT USE)
    OFFICIAL_QUESTS = (1, 299)
    OFFICIAL_SPELLS = (1, 299)
    OFFICIAL_WEAPONS = (1, 1000)
    OFFICIAL_ITEMS = (1, 5000)
    
    # Custom content ranges (SAFE TO USE)
    CUSTOM_QUESTS = (9000, 9999)
    CUSTOM_SPELLS = (300, 999)
    CUSTOM_WEAPONS = (10000, 19999)
    CUSTOM_ARMOR = (20000, 29999)
    CUSTOM_ITEMS = (30000, 39999)
    CUSTOM_NPCS = (40000, 49999)
    CUSTOM_CREATURES = (50000, 59999)
    CUSTOM_BUILDINGS = (60000, 69999)

class IDManager:
    """Manages unique ID allocation across all content types"""
    
    def __init__(self, project_file: str = "project_ids.json"):
        self.project_file = project_file
        self.allocated_ids: Dict[ContentType, Set[int]] = {}
        self.load()
    
    def load(self):
        """Load existing ID allocations from project file"""
        try:
            with open(self.project_file, 'r') as f:
                data = json.load(f)
                for content_type_str, id_list in data.items():
                    content_type = ContentType(content_type_str)
                    self.allocated_ids[content_type] = set(id_list)
        except FileNotFoundError:
            # Initialize empty allocation sets
            for content_type in ContentType:
                self.allocated_ids[content_type] = set()
    
    def save(self):
        """Save ID allocations to project file"""
        data = {}
        for content_type, id_set in self.allocated_ids.items():
            data[content_type.value] = sorted(list(id_set))
        
        with open(self.project_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_next_id(self, content_type: ContentType) -> int:
        """Get next available ID for content type"""
        
        # Get valid range for this content type
        id_range = self._get_range(content_type)
        start, end = id_range
        
        # Find first unused ID in range
        for candidate_id in range(start, end + 1):
            if candidate_id not in self.allocated_ids[content_type]:
                return candidate_id
        
        raise ValueError(f"No available IDs in range {start}-{end} for {content_type.value}")
    
    def allocate_id(self, content_type: ContentType, requested_id: Optional[int] = None) -> int:
        """
        Allocate an ID (auto-assign or use requested ID)
        
        Args:
            content_type: Type of content
            requested_id: Specific ID to use (optional)
        
        Returns:
            Allocated ID
        
        Raises:
            ValueError: If requested ID is already in use or out of range
        """
        
        if requested_id is None:
            # Auto-assign next available ID
            new_id = self.get_next_id(content_type)
        else:
            # Validate requested ID
            if not self.is_valid_id(content_type, requested_id):
                raise ValueError(f"ID {requested_id} is out of valid range for {content_type.value}")
            
            if self.is_id_used(content_type, requested_id):
                raise ValueError(f"ID {requested_id} is already in use for {content_type.value}")
            
            new_id = requested_id
        
        # Allocate the ID
        self.allocated_ids[content_type].add(new_id)
        self.save()
        return new_id
    
    def release_id(self, content_type: ContentType, item_id: int):
        """Release an ID back to the pool"""
        if item_id in self.allocated_ids[content_type]:
            self.allocated_ids[content_type].remove(item_id)
            self.save()
    
    def is_id_used(self, content_type: ContentType, item_id: int) -> bool:
        """Check if ID is already allocated"""
        return item_id in self.allocated_ids[content_type]
    
    def is_valid_id(self, content_type: ContentType, item_id: int) -> bool:
        """Check if ID is in valid range for content type"""
        id_range = self._get_range(content_type)
        start, end = id_range
        return start <= item_id <= end
    
    def get_used_ids(self, content_type: ContentType) -> List[int]:
        """Get list of all used IDs for content type"""
        return sorted(list(self.allocated_ids[content_type]))
    
    def get_available_count(self, content_type: ContentType) -> int:
        """Get count of available IDs"""
        id_range = self._get_range(content_type)
        total_range = id_range[1] - id_range[0] + 1
        used_count = len(self.allocated_ids[content_type])
        return total_range - used_count
    
    def _get_range(self, content_type: ContentType) -> tuple:
        """Get ID range for content type"""
        range_map = {
            ContentType.QUEST: IDRange.CUSTOM_QUESTS,
            ContentType.SPELL: IDRange.CUSTOM_SPELLS,
            ContentType.WEAPON: IDRange.CUSTOM_WEAPONS,
            ContentType.ARMOR: IDRange.CUSTOM_ARMOR,
            ContentType.ITEM: IDRange.CUSTOM_ITEMS,
            ContentType.NPC: IDRange.CUSTOM_NPCS,
            ContentType.CREATURE: IDRange.CUSTOM_CREATURES,
            ContentType.BUILDING: IDRange.CUSTOM_BUILDINGS,
        }
        return range_map.get(content_type, (0, 0))
    
    def get_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for all content types"""
        stats = {}
        for content_type in ContentType:
            id_range = self._get_range(content_type)
            total = id_range[1] - id_range[0] + 1
            used = len(self.allocated_ids[content_type])
            available = total - used
            
            stats[content_type.value] = {
                "range_start": id_range[0],
                "range_end": id_range[1],
                "total_capacity": total,
                "used": used,
                "available": available,
                "usage_percent": round((used / total) * 100, 1) if total > 0 else 0
            }
        
        return stats
```

### 1.2 ID Manager UI Widget

**IDManagerWidget** - Visual interface for ID management

```python
class IDManagerWidget(QWidget):
    """Visual ID manager interface"""
    
    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("ID Management System")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Stats table
        stats_group = QGroupBox("ID Usage Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_table = QTableWidget(8, 5)
        self.stats_table.setHorizontalHeaderLabels([
            "Content Type", "Range", "Used", "Available", "Usage %"
        ])
        self.update_stats_table()
        
        stats_layout.addWidget(self.stats_table)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # ID allocation section
        alloc_group = QGroupBox("Allocate New ID")
        alloc_layout = QFormLayout()
        
        self.content_type_combo = QComboBox()
        self.content_type_combo.addItems([ct.value.title() for ct in ContentType])
        alloc_layout.addRow("Content Type:", self.content_type_combo)
        
        self.auto_id_radio = QRadioButton("Auto-assign next available ID")
        self.manual_id_radio = QRadioButton("Manually specify ID")
        self.auto_id_radio.setChecked(True)
        alloc_layout.addRow(self.auto_id_radio)
        alloc_layout.addRow(self.manual_id_radio)
        
        self.manual_id_spin = QSpinBox()
        self.manual_id_spin.setRange(0, 99999)
        self.manual_id_spin.setEnabled(False)
        self.manual_id_radio.toggled.connect(lambda checked: self.manual_id_spin.setEnabled(checked))
        alloc_layout.addRow("Specific ID:", self.manual_id_spin)
        
        allocate_btn = QPushButton("Allocate ID")
        allocate_btn.clicked.connect(self.allocate_id)
        alloc_layout.addRow(allocate_btn)
        
        self.allocated_id_label = QLabel("")
        self.allocated_id_label.setStyleSheet("color: green; font-weight: bold;")
        alloc_layout.addRow("Allocated:", self.allocated_id_label)
        
        alloc_group.setLayout(alloc_layout)
        layout.addWidget(alloc_group)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Statistics")
        refresh_btn.clicked.connect(self.update_stats_table)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
    
    def update_stats_table(self):
        """Update statistics table"""
        stats = self.id_manager.get_stats()
        
        row = 0
        for content_type_str, stat_data in stats.items():
            self.stats_table.setItem(row, 0, QTableWidgetItem(content_type_str.title()))
            self.stats_table.setItem(row, 1, QTableWidgetItem(
                f"{stat_data['range_start']}-{stat_data['range_end']}"
            ))
            self.stats_table.setItem(row, 2, QTableWidgetItem(str(stat_data['used'])))
            self.stats_table.setItem(row, 3, QTableWidgetItem(str(stat_data['available'])))
            self.stats_table.setItem(row, 4, QTableWidgetItem(f"{stat_data['usage_percent']}%"))
            row += 1
        
        self.stats_table.resizeColumnsToContents()
    
    def allocate_id(self):
        """Allocate a new ID"""
        content_type_str = self.content_type_combo.currentText().lower()
        content_type = ContentType(content_type_str)
        
        try:
            if self.auto_id_radio.isChecked():
                # Auto-assign
                new_id = self.id_manager.allocate_id(content_type)
            else:
                # Manual ID
                requested_id = self.manual_id_spin.value()
                new_id = self.id_manager.allocate_id(content_type, requested_id)
            
            self.allocated_id_label.setText(f"✓ ID {new_id} allocated successfully!")
            self.allocated_id_label.setStyleSheet("color: green; font-weight: bold;")
            self.update_stats_table()
            
        except ValueError as e:
            self.allocated_id_label.setText(f"✗ Error: {str(e)}")
            self.allocated_id_label.setStyleSheet("color: red; font-weight: bold;")
```

### 1.3 Integration with Creators

**Each creator wizard (Quest, Spell, Weapon) will**:

1. **Initialize ID Manager** on startup
2. **Request ID** in first wizard step
3. **Show ID status** (auto-assigned or manual)
4. **Validate ID** before export
5. **Release ID** if creation canceled

**Example in Weapon Creator**:

```python
class WeaponForgeWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize ID Manager
        self.id_manager = IDManager("project_ids.json")
        
        # Request weapon ID
        self.weapon_id = None
        
        # Add pages...
        self.addPage(WeaponBasicsPage(self.id_manager))  # Pass ID manager
        # ...
    
    def done(self, result):
        """Override done to handle ID cleanup"""
        if result == QDialog.Rejected and self.weapon_id:
            # User canceled - release the allocated ID
            self.id_manager.release_id(ContentType.WEAPON, self.weapon_id)
        
        super().done(result)
```

---

## Phase 2: Weapon Forge Wizard Interface

### 2.1 Wizard Design

**Implementation**: Separate window (accessed via `Tools → Weapon Forge`)

**Wizard Steps**:

```
Step 1: Mode Selection & ID Assignment
  ├─ Creation Mode:
  │   ├─ Create New Weapon (blank slate)
  │   ├─ Edit Existing Weapon (load from 719 weapons)
  │   └─ Duplicate & Modify (copy existing, new ID)
  ├─ ID Assignment:
  │   ├─ Auto-assign next available ID (recommended)
  │   ├─ Manual ID entry (with validation)
  │   └─ ID Manager status (X available in range 10000-19999)
  └─ If Edit Mode: Select weapon from list

Step 2: Basic Properties
  ├─ Weapon Name (e.g., "Dragonslayer Greatsword")
  ├─ Weapon Type:
  │   ├─ Select from 20 existing types
  │   └─ Or: Create New Weapon Type...
  ├─ Weapon Material:
  │   ├─ Select from existing materials (Metal, Wood, Bone, etc.)
  │   └─ Or: Create New Material...
  ├─ Hands Required: 1H / 2H / Unarmed
  ├─ Damage Category: Melee / Ranged / Magic
  └─ Description (player-visible tooltip)

Step 3: Combat Stats
  ├─ Damage:
  │   ├─ Minimum Damage
  │   ├─ Maximum Damage
  │   └─ Damage Type (Slash/Pierce/Blunt)
  ├─ Speed:
  │   ├─ Attack Speed (1-200, lower = faster)
  │   └─ DPS Calculator (auto-calculates damage per second)
  ├─ Range:
  │   ├─ Minimum Range (melee = 0)
  │   ├─ Maximum Range (melee = 1-2, ranged = 15-30)
  │   └─ Attack Arc (degrees, for melee sweep)
  └─ Special Properties:
      ├─ Critical Hit Chance (%)
      ├─ Armor Penetration (%)
      └─ Knockback Chance (%)

Step 4: Requirements & Value
  ├─ Stat Requirements:
  │   ├─ Strength Required
  │   ├─ Dexterity Required
  │   ├─ Intelligence Required
  │   └─ Level Required
  ├─ Economic Value:
  │   ├─ Sell Value (gold)
  │   ├─ Buy Value (gold)
  │   └─ Rarity (Common/Uncommon/Rare/Epic/Legendary)
  ├─ Effects:
  │   ├─ Add Effect... (Fire damage, Poison, Life drain, etc.)
  │   └─ Effect List (multi-select)
  └─ Item Set:
      ├─ Part of Set? (Yes/No)
      └─ Set ID (if part of set)

Step 5: Visual & Audio
  ├─ Icon Assignment:
  │   ├─ Browse 4096+ extracted item icons
  │   ├─ Filter by weapon type
  │   ├─ Preview icon
  │   └─ Icon Handle (e.g., ui_item_equip_weapon_sword_flame)
  ├─ Sound Effects:
  │   ├─ Hit Sound (from 20 weapon type sounds)
  │   ├─ Miss Sound (swoosh sound)
  │   ├─ Equip Sound (optional)
  │   └─ Preview sounds
  ├─ 3D Model (optional):
  │   ├─ Browse extracted weapon models
  │   └─ Model file path
  └─ Visual Effects (optional):
      ├─ Trail Effect (for swing animations)
      └─ Impact Effect (on hit)

Step 6: Review & Export
  ├─ Weapon Summary (all configured data)
  ├─ Stats Display:
  │   ├─ DPS: X.X
  │   ├─ Balance Rating: X/100
  │   ├─ Power Level: Balanced/Strong/Overpowered
  │   └─ Comparison (vs similar weapons)
  ├─ Validation Results:
  │   ├─ ✓ Weapon ID unique (10523)
  │   ├─ ✓ All required fields filled
  │   ├─ ✓ Icon exists
  │   └─ ⚠ Warning: Very high DPS (50+)
  └─ Export Options:
      ├─ Export to CFF (GameData.cff)
      ├─ Export to JSON (for version control)
      └─ Create Test Item (spawn code)
```

### 2.2 Data Models

**Weapon Data Model**:

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class WeaponHands(Enum):
    ONE_HANDED = "1H"
    TWO_HANDED = "2H"
    UNARMED = "Unarmed"

class DamageCategory(Enum):
    MELEE = "melee"
    RANGED = "ranged"
    MAGIC = "magic"

class DamageType(Enum):
    SLASH = "slash"
    PIERCE = "pierce"
    BLUNT = "blunt"
    MIXED = "mixed"

class Rarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class WeaponRequirements:
    """Stat requirements to equip weapon"""
    strength: int = 0
    dexterity: int = 0
    intelligence: int = 0
    level: int = 1

@dataclass
class WeaponEffect:
    """Special effect on weapon"""
    effect_id: int
    effect_name: str  # "Fire Damage", "Poison", "Life Drain"
    value: float      # Effect strength
    duration: float   # Effect duration (if applicable)

@dataclass
class WeaponCreationData:
    """Complete weapon definition"""
    
    # Step 1: Mode & ID
    weapon_id: int                # Managed by ID Manager
    creation_mode: str            # "new", "edit", "duplicate"
    source_weapon_id: Optional[int] = None  # If edit/duplicate mode
    
    # Step 2: Basic Properties
    weapon_name: str = ""
    weapon_type_id: int = 4       # Default to 1H Sword
    weapon_type_name: str = ""
    weapon_material_id: int = 5   # Default to Metal
    weapon_material_name: str = ""
    hands: WeaponHands = WeaponHands.ONE_HANDED
    damage_category: DamageCategory = DamageCategory.MELEE
    description: str = ""
    
    # Step 3: Combat Stats
    min_damage: int = 10
    max_damage: int = 15
    damage_type: DamageType = DamageType.SLASH
    attack_speed: int = 100       # Lower = faster (50-200 range)
    min_range: int = 0
    max_range: int = 2
    attack_arc: int = 90          # Degrees for melee sweep
    critical_chance: float = 5.0  # Percentage
    armor_penetration: float = 0.0
    knockback_chance: float = 0.0
    
    # Step 4: Requirements & Value
    requirements: WeaponRequirements = None
    sell_value: int = 50
    buy_value: int = 100
    rarity: Rarity = Rarity.COMMON
    effects: List[WeaponEffect] = None
    item_set_id: int = 0
    
    # Step 5: Visual & Audio
    icon_handle: str = ""
    hit_sound: str = "battle_hit_1hsword"
    miss_sound: str = "battle_miss_sword"
    equip_sound: str = ""
    model_file: str = ""
    trail_effect: str = ""
    impact_effect: str = ""
    
    # Metadata
    created_date: str = ""
    modified_date: str = ""
    author: str = ""
    version: int = 1
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = WeaponRequirements()
        if self.effects is None:
            self.effects = []
    
    def calculate_dps(self) -> float:
        """Calculate damage per second"""
        avg_damage = (self.min_damage + self.max_damage) / 2
        attacks_per_second = 100 / self.attack_speed
        return avg_damage * attacks_per_second
    
    def get_balance_rating(self) -> int:
        """Calculate balance rating (0-100)"""
        # DPS-based rating
        dps = self.calculate_dps()
        
        # Adjust for requirements
        req_factor = (self.requirements.strength + 
                      self.requirements.dexterity + 
                      self.requirements.intelligence) / 100
        
        # Adjust for rarity
        rarity_multiplier = {
            Rarity.COMMON: 1.0,
            Rarity.UNCOMMON: 1.2,
            Rarity.RARE: 1.5,
            Rarity.EPIC: 2.0,
            Rarity.LEGENDARY: 3.0
        }[self.rarity]
        
        rating = (dps / rarity_multiplier) - req_factor
        return int(min(100, max(0, rating)))
```

---

## Phase 3: Edit Existing Weapons Feature

### 3.1 Weapon Browser

**WeaponBrowserDialog** - Browse and select from 719 existing weapons

```python
class WeaponBrowserDialog(QDialog):
    """Browse and select existing weapons"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Weapon to Edit")
        self.setModal(True)
        self.resize(800, 600)
        
        self.selected_weapon = None
        self.weapons = self.load_weapons()
        
        layout = QVBoxLayout()
        
        # Search/Filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_weapons)
        search_layout.addWidget(self.search_edit)
        
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types")
        self.type_filter.addItems([
            "Daggers", "Swords", "Axes", "Maces", "Hammers",
            "Staves", "Spears", "Halberds", "Bows", "Crossbows"
        ])
        self.type_filter.currentTextChanged.connect(self.filter_weapons)
        search_layout.addWidget(self.type_filter)
        
        layout.addLayout(search_layout)
        
        # Weapon table
        self.weapon_table = QTableWidget(0, 7)
        self.weapon_table.setHorizontalHeaderLabels([
            "ID", "Name", "Type", "Material", "Damage", "Speed", "Rarity"
        ])
        self.weapon_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.weapon_table.setSelectionMode(QTableWidget.SingleSelection)
        self.weapon_table.doubleClicked.connect(self.accept)
        self.populate_table()
        layout.addWidget(self.weapon_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Load Weapon")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_weapons(self) -> List[Dict]:
        """Load weapons from enhanced_weapons.json"""
        with open("src/TirganachReloaded/enhanced_weapons.json", 'r') as f:
            return json.load(f)
    
    def populate_table(self, weapons=None):
        """Populate weapon table"""
        if weapons is None:
            weapons = self.weapons
        
        self.weapon_table.setRowCount(len(weapons))
        
        for row, weapon in enumerate(weapons):
            self.weapon_table.setItem(row, 0, QTableWidgetItem(str(weapon['item_id'])))
            self.weapon_table.setItem(row, 1, QTableWidgetItem(weapon['name']))
            self.weapon_table.setItem(row, 2, QTableWidgetItem(weapon.get('weapon_type_name', 'Unknown')))
            self.weapon_table.setItem(row, 3, QTableWidgetItem(weapon.get('weapon_material_name', 'Unknown')))
            
            damage_str = f"{weapon.get('min_damage', 0)}-{weapon.get('max_damage', 0)}"
            self.weapon_table.setItem(row, 4, QTableWidgetItem(damage_str))
            self.weapon_table.setItem(row, 5, QTableWidgetItem(str(weapon.get('weapon_speed', 0))))
            self.weapon_table.setItem(row, 6, QTableWidgetItem(weapon.get('rarity', 'Common')))
        
        self.weapon_table.resizeColumnsToContents()
    
    def filter_weapons(self):
        """Filter weapons by search text and type"""
        search_text = self.search_edit.text().lower()
        type_filter = self.type_filter.currentText()
        
        filtered = []
        for weapon in self.weapons:
            # Text search
            if search_text and search_text not in weapon['name'].lower():
                continue
            
            # Type filter
            if type_filter != "All Types":
                weapon_type = weapon.get('weapon_type_name', '')
                if type_filter.lower() not in weapon_type.lower():
                    continue
            
            filtered.append(weapon)
        
        self.populate_table(filtered)
    
    def get_selected_weapon(self) -> Optional[Dict]:
        """Get selected weapon data"""
        selected_rows = self.weapon_table.selectedIndexes()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        weapon_id = int(self.weapon_table.item(row, 0).text())
        
        for weapon in self.weapons:
            if weapon['item_id'] == weapon_id:
                return weapon
        
        return None
```

### 3.2 Load & Save Weapons

```python
class WeaponLoader:
    """Load and save weapon data"""
    
    @staticmethod
    def load_weapon(weapon_id: int) -> WeaponCreationData:
        """Load existing weapon by ID"""
        # Load from enhanced_weapons.json
        with open("src/TirganachReloaded/enhanced_weapons.json", 'r') as f:
            weapons = json.load(f)
        
        weapon_data = next((w for w in weapons if w['item_id'] == weapon_id), None)
        if not weapon_data:
            raise ValueError(f"Weapon ID {weapon_id} not found")
        
        # Convert to WeaponCreationData
        return WeaponCreationData(
            weapon_id=weapon_data['item_id'],
            creation_mode="edit",
            source_weapon_id=weapon_data['item_id'],
            weapon_name=weapon_data['name'],
            weapon_type_id=weapon_data.get('weapon_type_id', 4),
            weapon_type_name=weapon_data.get('weapon_type_name', ''),
            weapon_material_id=weapon_data.get('weapon_material_id', 5),
            weapon_material_name=weapon_data.get('weapon_material_name', ''),
            min_damage=weapon_data.get('min_damage', 10),
            max_damage=weapon_data.get('max_damage', 15),
            attack_speed=weapon_data.get('weapon_speed', 100),
            min_range=weapon_data.get('min_range', 0),
            max_range=weapon_data.get('max_range', 2),
            sell_value=weapon_data.get('sell_value', 50),
            buy_value=weapon_data.get('buy_value', 100),
            # ... map other fields
        )
    
    @staticmethod
    def save_weapon(weapon_data: WeaponCreationData, export_path: str):
        """Save weapon to JSON file"""
        weapon_dict = {
            "item_id": weapon_data.weapon_id,
            "name": weapon_data.weapon_name,
            "weapon_type_id": weapon_data.weapon_type_id,
            "weapon_material_id": weapon_data.weapon_material_id,
            "min_damage": weapon_data.min_damage,
            "max_damage": weapon_data.max_damage,
            "weapon_speed": weapon_data.attack_speed,
            "min_range": weapon_data.min_range,
            "max_range": weapon_data.max_range,
            "sell_value": weapon_data.sell_value,
            "buy_value": weapon_data.buy_value,
            "rarity": weapon_data.rarity.value,
            "icon_handle": weapon_data.icon_handle,
            "requirements": {
                "strength": weapon_data.requirements.strength,
                "dexterity": weapon_data.requirements.dexterity,
                "intelligence": weapon_data.requirements.intelligence,
                "level": weapon_data.requirements.level
            },
            "effects": [
                {
                    "effect_id": effect.effect_id,
                    "effect_name": effect.effect_name,
                    "value": effect.value,
                    "duration": effect.duration
                }
                for effect in weapon_data.effects
            ],
            "created_date": weapon_data.created_date,
            "modified_date": weapon_data.modified_date,
            "author": weapon_data.author,
            "version": weapon_data.version
        }
        
        with open(export_path, 'w') as f:
            json.dump(weapon_dict, f, indent=2)
```

---

## Phase 4: New Weapon Types Feature

### 4.1 Custom Weapon Type Creator

**NewWeaponTypeDialog** - Create entirely new weapon categories

```python
class NewWeaponTypeDialog(QDialog):
    """Create a new weapon type"""
    
    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Weapon Type")
        self.setModal(True)
        self.id_manager = id_manager
        
        layout = QFormLayout()
        
        # Type ID (auto-assigned from 20+)
        self.type_id_label = QLabel("Auto-assigned: 20")
        layout.addRow("Type ID:", self.type_id_label)
        
        # Type name
        self.type_name_edit = QLineEdit()
        self.type_name_edit.setPlaceholderText("e.g., Katana, Scimitar, Wand")
        layout.addRow("Type Name:", self.type_name_edit)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Melee", "Ranged", "Magic"])
        layout.addRow("Category:", self.category_combo)
        
        # Hands
        self.hands_combo = QComboBox()
        self.hands_combo.addItems(["1H", "2H", "Unarmed"])
        layout.addRow("Hands:", self.hands_combo)
        
        # Damage type
        self.damage_type_combo = QComboBox()
        self.damage_type_combo.addItems(["Slash", "Pierce", "Blunt", "Mixed"])
        layout.addRow("Damage Type:", self.damage_type_combo)
        
        # Base weapon (for sounds/animations)
        self.base_weapon_combo = QComboBox()
        self.base_weapon_combo.addItems([
            "Dagger", "Sword", "Axe", "Mace", "Hammer",
            "Staff", "Spear", "Halberd", "Bow", "Crossbow", "Claw"
        ])
        layout.addRow("Base Weapon (for animations):", self.base_weapon_combo)
        
        # Sounds
        sound_group = QGroupBox("Sound Effects")
        sound_layout = QFormLayout()
        
        self.hit_sound_combo = QComboBox()
        self.populate_hit_sounds()
        sound_layout.addRow("Hit Sound:", self.hit_sound_combo)
        
        self.miss_sound_combo = QComboBox()
        self.populate_miss_sounds()
        sound_layout.addRow("Miss Sound:", self.miss_sound_combo)
        
        sound_group.setLayout(sound_layout)
        layout.addRow(sound_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create Type")
        create_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        self.setLayout(layout)
    
    def populate_hit_sounds(self):
        """Populate hit sound dropdown"""
        hit_sounds = [
            "battle_hit_1hdagger",
            "battle_hit_1hsword",
            "battle_hit_1haxe",
            "battle_hit_1hmacespiky",
            "battle_hit_1hmaceblunt",
            "battle_hit_1hhammer",
            "battle_hit_1hstaff",
            "battle_hit_2hsword",
            "battle_hit_2haxe",
            "battle_hit_2hmace",
            "battle_hit_2hhammer",
            "battle_hit_2hstaff",
            "battle_hit_2hspear",
            "battle_hit_2hhalberd",
            "battle_hit_2hbow",
            "battle_hit_2hcrossbow",
            "battle_hit_claw",
            "battle_hit_fist",
            "battle_hit_mouth"
        ]
        self.hit_sound_combo.addItems(hit_sounds)
    
    def populate_miss_sounds(self):
        """Populate miss sound dropdown"""
        miss_sounds = [
            "battle_miss_sword",
            "battle_miss_hammer",
            "battle_miss_staff",
            "battle_miss_bow",
            "battle_miss_fist"
        ]
        self.miss_sound_combo.addItems(miss_sounds)
    
    def get_weapon_type_data(self) -> Dict:
        """Get new weapon type data"""
        return {
            "type_id": 20,  # Start from 20 (after official 0-19)
            "type_name": self.type_name_edit.text(),
            "category": self.category_combo.currentText().lower(),
            "hands": self.hands_combo.currentText(),
            "damage_type": self.damage_type_combo.currentText().lower(),
            "base_weapon": self.base_weapon_combo.currentText().lower(),
            "hit_sound": self.hit_sound_combo.currentText(),
            "miss_sound": self.miss_sound_combo.currentText()
        }
```

---

## (Continuing in next message due to length...)

I'll create the rest of the plan and then update all existing plans with ID Manager integration. Would you like me to continue with:
- Phase 5: Material System
- Phase 6: CFF Export
- Phase 7: Weapon Validation & Balance
- Then update Quest/Spell plans with ID Manager?
---

## Phase 5: Material System

### 5.1 Existing Materials

**Materials in SpellForce**:
- Metal (ID 5)
- Wood (ID 1)
- Bone (ID 2)
- Stone (ID 3)
- Crystal (ID 4)
- Leather (ID 6)
- Cloth (ID 7)
- Obsidian (ID 8)

### 5.2 New Material Creator

**NewMaterialDialog** - Create custom weapon materials

```python
class NewMaterialDialog(QDialog):
    """Create a new weapon material"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Material")
        
        layout = QFormLayout()
        
        # Material ID (auto-assigned from 10+)
        self.material_id_label = QLabel("Auto-assigned: 10")
        layout.addRow("Material ID:", self.material_id_label)
        
        # Material name
        self.material_name_edit = QLineEdit()
        self.material_name_edit.setPlaceholderText("e.g., Mithril, Adamantium, Dragonbone")
        layout.addRow("Material Name:", self.material_name_edit)
        
        # Material properties
        self.hardness_spin = QSpinBox()
        self.hardness_spin.setRange(1, 100)
        self.hardness_spin.setValue(50)
        layout.addRow("Hardness (1-100):", self.hardness_spin)
        
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0.1, 10.0)
        self.weight_spin.setValue(1.0)
        self.weight_spin.setSuffix(" kg")
        layout.addRow("Weight:", self.weight_spin)
        
        self.durability_spin = QSpinBox()
        self.durability_spin.setRange(10, 1000)
        self.durability_spin.setValue(100)
        layout.addRow("Durability:", self.durability_spin)
        
        # Visual properties
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.choose_color)
        layout.addRow("Material Color:", self.color_btn)
        
        self.texture_edit = QLineEdit()
        self.texture_edit.setPlaceholderText("Optional texture file")
        layout.addRow("Texture File:", self.texture_edit)
        
        # Stat modifiers
        mod_group = QGroupBox("Stat Modifiers")
        mod_layout = QFormLayout()
        
        self.damage_mod_spin = QSpinBox()
        self.damage_mod_spin.setRange(-50, 50)
        self.damage_mod_spin.setSuffix("%")
        mod_layout.addRow("Damage Modifier:", self.damage_mod_spin)
        
        self.speed_mod_spin = QSpinBox()
        self.speed_mod_spin.setRange(-50, 50)
        self.speed_mod_spin.setSuffix("%")
        mod_layout.addRow("Speed Modifier:", self.speed_mod_spin)
        
        self.value_mod_spin = QSpinBox()
        self.value_mod_spin.setRange(-50, 200)
        self.value_mod_spin.setSuffix("%")
        mod_layout.addRow("Value Modifier:", self.value_mod_spin)
        
        mod_group.setLayout(mod_layout)
        layout.addRow(mod_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create Material")
        create_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        self.setLayout(layout)
    
    def choose_color(self):
        """Choose material color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background-color: {color.name()};")
```

---

## Phase 6: CFF Export System

### 6.1 CFF Exporter

**WeaponCFFExporter** - Export weapons to GameData.cff format

```python
class WeaponCFFExporter:
    """Export weapon to CFF format"""
    
    def export_weapon(self, weapon_data: WeaponCreationData) -> Dict[str, bytes]:
        """
        Export weapon to CFF categories
        
        Returns:
            Dict mapping category IDs to binary data
        """
        
        exports = {}
        
        # Category 2003: Item General Info
        exports[2003] = self.export_item_general(weapon_data)
        
        # Category 2015: Weapon Combat Data
        exports[2015] = self.export_weapon_data(weapon_data)
        
        # Category 2016: Text entries (name, description)
        exports[2016] = self.export_text_entries(weapon_data)
        
        # Category 2063: Weapon Type (if new type)
        if weapon_data.weapon_type_id >= 20:
            exports[2063] = self.export_weapon_type(weapon_data)
        
        # Category 2064: Material (if new material)
        if weapon_data.weapon_material_id >= 10:
            exports[2064] = self.export_material(weapon_data)
        
        # Category 2014: Effects (if any)
        if weapon_data.effects:
            exports[2014] = self.export_weapon_effects(weapon_data)
        
        return exports
    
    def export_item_general(self, weapon_data: WeaponCreationData) -> bytes:
        """Export to Category 2003 (Item General Info)"""
        # Structure:
        # - ItemID (ushort)
        # - NameID (ushort)
        # - ItemType (byte) - EQUIPMENT
        # - ItemSubtype (byte) - WEAPON
        # - SellValue (uint)
        # - BuyValue (uint)
        # - Option (byte)
        # - ItemSetID (ushort)
        
        import struct
        
        data = struct.pack('<HHBBIIBxH',
            weapon_data.weapon_id,          # ItemID
            weapon_data.weapon_id + 20000,  # NameID (arbitrary offset)
            1,                               # ItemType: EQUIPMENT
            2,                               # ItemSubtype: WEAPON
            weapon_data.sell_value,
            weapon_data.buy_value,
            0,                               # Option
            weapon_data.item_set_id
        )
        
        return data
    
    def export_weapon_data(self, weapon_data: WeaponCreationData) -> bytes:
        """Export to Category 2015 (Weapon Combat Data)"""
        # Structure:
        # - ItemID (ushort) - Foreign key to 2003
        # - MinDamage (ushort)
        # - MaxDamage (ushort)
        # - MinRange (ushort)
        # - MaxRange (ushort)
        # - WeaponSpeed (ushort)
        # - WeaponType (ushort) - Foreign key to 2063
        # - WeaponMaterial (ushort) - Foreign key to 2064
        
        import struct
        
        data = struct.pack('<HHHHHHHH',
            weapon_data.weapon_id,
            weapon_data.min_damage,
            weapon_data.max_damage,
            weapon_data.min_range,
            weapon_data.max_range,
            weapon_data.attack_speed,
            weapon_data.weapon_type_id,
            weapon_data.weapon_material_id
        )
        
        return data
    
    def export_text_entries(self, weapon_data: WeaponCreationData) -> List[bytes]:
        """Export to Category 2016 (Text Strings)"""
        # Two entries:
        # 1. Weapon name
        # 2. Weapon description
        
        name_id = weapon_data.weapon_id + 20000
        desc_id = weapon_data.weapon_id + 20001
        
        entries = []
        
        # Name entry
        name_entry = self.create_text_entry(
            name_id,
            weapon_data.weapon_name
        )
        entries.append(name_entry)
        
        # Description entry
        if weapon_data.description:
            desc_entry = self.create_text_entry(
                desc_id,
                weapon_data.description
            )
            entries.append(desc_entry)
        
        return entries
    
    def create_text_entry(self, text_id: int, text: str) -> bytes:
        """Create a text entry"""
        import struct
        
        # Encode text as UTF-16LE (SpellForce text format)
        text_bytes = text.encode('utf-16le')
        text_length = len(text_bytes)
        
        # Structure:
        # - TextID (uint)
        # - TextLength (ushort)
        # - Text (UTF-16LE string)
        
        return struct.pack(f'<IH{text_length}s',
            text_id,
            text_length,
            text_bytes
        )
    
    def save_to_cff(self, exports: Dict[int, bytes], output_file: str):
        """Save exported data to CFF file"""
        # This would integrate with the existing CFF library
        # For now, save to JSON for testing
        
        output_data = {
            "weapon_exports": {}
        }
        
        for category_id, data in exports.items():
            output_data["weapon_exports"][f"category_{category_id}"] = {
                "size": len(data),
                "hex": data.hex()
            }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
```

---

## Phase 7: Weapon Validation & Balance

### 7.1 Weapon Validator

**WeaponValidator** - Validate weapon data before export

```python
class WeaponValidator:
    """Validate weapon data"""
    
    def __init__(self, id_manager: IDManager):
        self.id_manager = id_manager
    
    def validate(self, weapon_data: WeaponCreationData) -> tuple[List[str], List[str]]:
        """
        Validate weapon data
        
        Returns:
            (errors, warnings)
        """
        errors = []
        warnings = []
        
        # Check weapon name
        if not weapon_data.weapon_name:
            errors.append("Weapon name is required")
        elif len(weapon_data.weapon_name) < 3:
            warnings.append("Weapon name is very short")
        
        # Check ID
        if not self.id_manager.is_valid_id(ContentType.WEAPON, weapon_data.weapon_id):
            errors.append(f"Weapon ID {weapon_data.weapon_id} is out of valid range")
        
        # Check damage
        if weapon_data.min_damage > weapon_data.max_damage:
            errors.append("Minimum damage cannot be greater than maximum damage")
        
        if weapon_data.max_damage == 0:
            warnings.append("Weapon has no damage (decorative only?)")
        
        # Check range
        if weapon_data.damage_category == DamageCategory.RANGED:
            if weapon_data.max_range < 10:
                warnings.append("Ranged weapon has very short range")
        else:
            if weapon_data.max_range > 5:
                warnings.append("Melee weapon has unusually long range")
        
        # Check speed
        if weapon_data.attack_speed < 20:
            warnings.append("Attack speed is extremely fast (may be unbalanced)")
        elif weapon_data.attack_speed > 200:
            warnings.append("Attack speed is very slow")
        
        # Check requirements
        total_req = (weapon_data.requirements.strength + 
                     weapon_data.requirements.dexterity + 
                     weapon_data.requirements.intelligence)
        
        if total_req > 150:
            warnings.append("Very high stat requirements (few players can use)")
        
        # Check balance
        balance_rating = weapon_data.get_balance_rating()
        if balance_rating > 80:
            warnings.append("Weapon may be overpowered (balance rating > 80)")
        
        # Check DPS
        dps = weapon_data.calculate_dps()
        if dps > 100:
            warnings.append(f"Very high DPS ({dps:.1f}) - may be overpowered")
        elif dps < 5:
            warnings.append(f"Very low DPS ({dps:.1f}) - weapon is weak")
        
        # Check icon
        if not weapon_data.icon_handle:
            warnings.append("No icon assigned (weapon will appear as placeholder)")
        
        return errors, warnings
```

### 7.2 Balance Calculator

**WeaponBalanceCalculator** - Calculate weapon balance metrics

```python
class WeaponBalanceCalculator:
    """Calculate weapon balance metrics"""
    
    @staticmethod
    def calculate_dps(weapon_data: WeaponCreationData) -> float:
        """Calculate damage per second"""
        return weapon_data.calculate_dps()
    
    @staticmethod
    def calculate_effective_damage(weapon_data: WeaponCreationData) -> float:
        """Calculate effective damage accounting for requirements"""
        base_dps = weapon_data.calculate_dps()
        
        # Reduce effectiveness if high requirements
        req_penalty = (weapon_data.requirements.strength + 
                       weapon_data.requirements.dexterity + 
                       weapon_data.requirements.intelligence) / 200
        
        return base_dps * (1 - req_penalty)
    
    @staticmethod
    def compare_to_similar(weapon_data: WeaponCreationData, 
                          all_weapons: List[WeaponCreationData]) -> Dict:
        """Compare weapon to similar weapons"""
        
        # Find similar weapons (same type)
        similar = [w for w in all_weapons 
                   if w.weapon_type_id == weapon_data.weapon_type_id]
        
        if not similar:
            return {"similar_count": 0}
        
        # Calculate percentiles
        dps_values = [w.calculate_dps() for w in similar]
        dps_values.sort()
        
        weapon_dps = weapon_data.calculate_dps()
        percentile = (sum(1 for dps in dps_values if dps < weapon_dps) / len(dps_values)) * 100
        
        return {
            "similar_count": len(similar),
            "dps_percentile": percentile,
            "average_dps": sum(dps_values) / len(dps_values),
            "min_dps": min(dps_values),
            "max_dps": max(dps_values),
            "rating": "Weak" if percentile < 25 else 
                     "Below Average" if percentile < 40 else
                     "Average" if percentile < 60 else
                     "Above Average" if percentile < 75 else
                     "Strong"
        }
```

---

## Implementation Timeline

### Week 1: Foundation & ID Manager (Phase 1)
- ☐ Create `IDManager` class (shared system)
- ☐ Build `IDManagerWidget` UI
- ☐ Integrate with project file system
- ☐ Test ID allocation/release
- ☐ Create documentation

### Week 2: Weapon Forge Wizard (Phase 2)
- ☐ Create `WeaponForgeWizard` class
- ☐ Implement 6 wizard pages
- ☐ Build `WeaponCreationData` model
- ☐ Add menu integration
- ☐ Test basic workflow

### Week 3: Edit Existing Weapons (Phase 3)
- ☐ Build `WeaponBrowserDialog`
- ☐ Implement `WeaponLoader` class
- ☐ Add duplicate & modify mode
- ☐ Test loading 719 existing weapons
- ☐ Test save under new ID

### Week 4: New Types & Materials (Phase 4-5)
- ☐ Build `NewWeaponTypeDialog`
- ☐ Build `NewMaterialDialog`
- ☐ Test creating custom types
- ☐ Test material modifiers
- ☐ Document new type/material workflow

### Week 5: Export & Validation (Phase 6-7)
- ☐ Build `WeaponCFFExporter`
- ☐ Implement CFF category exports
- ☐ Build `WeaponValidator`
- ☐ Implement `WeaponBalanceCalculator`
- ☐ Test full export workflow

### Week 6: Polish & Testing
- ☐ Icon browser integration
- ☐ Sound preview system
- ☐ Create weapon templates
- ☐ User documentation
- ☐ **First weapon tested in-game!**

---

## Technical Requirements

### Dependencies

**Python Packages**:
- PySide6 - ✅ Already installed
- dataclasses - ✅ Python stdlib
- struct (for binary CFF export) - ✅ Python stdlib
- json - ✅ Python stdlib

**Data Files**:
- Read: `src/TirganachReloaded/enhanced_weapons.json` (719 weapons)
- Read: Extracted UI icons (4096+ icons)
- Read: Extracted audio files (weapon sounds)
- Write: `project_ids.json` (ID tracking)
- Write: Custom weapon exports (CFF + JSON)

### File Structure

```
src/TirganachReloaded/cff_editor/
├── shared/
│   ├── id_manager.py                 # NEW: ID Management System ⭐
│   └── id_manager_widget.py          # NEW: ID Manager UI
├── widgets/
│   ├── weapon_forge_wizard.py        # NEW: Main wizard
│   ├── weapon_browser_dialog.py      # NEW: Browse existing weapons
│   ├── new_weapon_type_dialog.py     # NEW: Create weapon types
│   ├── new_material_dialog.py        # NEW: Create materials
│   └── weapon_validation.py          # NEW: Validator
├── models/
│   ├── weapon_creation_data.py       # NEW: Weapon data model
│   ├── weapon_requirements.py        # NEW: Requirements model
│   └── weapon_effect.py              # NEW: Effect model
├── exporters/
│   ├── weapon_cff_exporter.py        # NEW: CFF export
│   └── weapon_loader.py              # NEW: Load/save weapons
└── data/
    └── project_ids.json               # NEW: ID tracking file
```

---

## Success Metrics

### Phase 1 Success (ID Manager)
- ✅ ID Manager tracks all content types
- ✅ Can allocate/release IDs
- ✅ Prevents duplicate IDs
- ✅ Shows usage statistics

### Phase 2-3 Success (Wizard + Edit)
- ✅ All 6 wizard pages functional
- ✅ Can create new weapons
- ✅ Can load existing 719 weapons
- ✅ Can save under new ID
- ✅ Duplicate & modify works

### Phase 4-5 Success (Types + Materials)
- ✅ Can create new weapon types (20+)
- ✅ Can create new materials (10+)
- ✅ New types work in-game

### Phase 6-7 Success (Export + Validation)
- ✅ Exports valid CFF data
- ✅ Validation catches errors
- ✅ Balance calculator works
- ✅ DPS calculations accurate

### Final Success Criteria
- ✅ **Non-programmer creates weapon in < 30 minutes**
- ✅ **Can edit existing weapons and save under new ID**
- ✅ **Can create entirely new weapon types**
- ✅ **Weapon works in-game without errors**
- ✅ **ID Manager prevents conflicts across Quest/Spell/Weapon**
- ✅ **No ID collisions with official content**

---

## Integration with Other Creators

### Shared ID Manager

All three creators (Quest, Spell, Weapon) share the **same ID Manager instance**:

```python
# In main application
class ModdingToolsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize shared ID Manager
        self.id_manager = IDManager("project_ids.json")
        
        # Pass to all creators
        self.quest_creator = QuestCreatorWizard(self.id_manager)
        self.spell_creator = SpellCreatorWizard(self.id_manager)
        self.weapon_creator = WeaponForgeWizard(self.id_manager)
```

**Benefits**:
- ✅ Single source of truth for all IDs
- ✅ Prevents conflicts across content types
- ✅ Centralized statistics
- ✅ Consistent ID ranges
- ✅ Easy project-wide ID management

---

## Risks & Mitigations

### Risk 1: ID Conflicts with Official Content
**Issue**: Custom IDs might conflict with future official content  
**Mitigation**:
- Use high ID ranges (10000+ for weapons)
- Document official ID ranges clearly
- Validate against known official IDs
- Provide ID remapping tool if conflicts occur

### Risk 2: CFF Export Complexity
**Issue**: CFF binary format is complex and error-prone  
**Mitigation**:
- Export to JSON first for testing
- Validate binary data structure
- Use struct module for safe packing
- Test with small datasets first
- Provide rollback mechanism

### Risk 3: Balance Issues
**Issue**: Custom weapons may be overpowered  
**Mitigation**:
- Provide balance calculator
- Show warnings for extreme values
- Compare to similar weapons
- Suggest stat adjustments
- Document balance guidelines

### Risk 4: Editing Official Weapons
**Issue**: Accidentally overwriting official weapons  
**Mitigation**:
- ALWAYS require new ID when saving edits
- Show clear "Save As New Weapon" prompt
- Prevent saving with ID < 10000
- Backup system for safety

---

## Future Enhancements

### Post-V1 Features

1. **Weapon Sets**:
   - Create matched weapon/armor sets
   - Set bonuses when wearing multiple pieces
   - Visual set editor

2. **Enchantment System**:
   - Add temporary/permanent enchantments
   - Enchantment templates
   - Visual enchantment effects

3. **Legendary Weapons**:
   - Unique weapon creator
   - Special abilities
   - Quest-linked legendary weapons

4. **Batch Operations**:
   - Edit multiple weapons at once
   - Bulk stat adjustments
   - Material replacement

5. **3D Preview**:
   - View weapon model in 3D
   - Test animations
   - Preview in-hand appearance

---

## Related Documentation

- **Quest Creator**: [QUEST_CREATION_PLAN.md](QUEST_CREATION_PLAN.md)
- **Spell Creator**: [SPELL_CREATION_PLAN.md](SPELL_CREATION_PLAN.md)
- **ID Mappings**: [../../docs/Project/ID_MAPPINGS.md](../../docs/Project/ID_MAPPINGS.md)
- **Weapon Data**: `src/TirganachReloaded/enhanced_weapons.json`
- **Sound System**: [../../docs/Guides/SOUND_SYSTEM_GUIDE.md](../../docs/Guides/SOUND_SYSTEM_GUIDE.md)

---

**Document Version**: 1.0  
**Created**: 2025-10-27  
**Author**: SpellSmut Development Team  
**Status**: 🟡 Planning Complete - Ready for Implementation  
**Key Innovation**: ⭐ Shared ID Management System across all creators!
