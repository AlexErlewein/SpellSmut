# ID Management System - Shared Component
## 🎯 Preventing ID Conflicts Across All Content Types

## Overview

The **ID Management System** is a centralized component shared across all content creators (Quest, Spell, Weapon, etc.). It ensures unique ID allocation, prevents conflicts, and provides project-wide ID tracking.

**Status**: 🟢 Core System Design Complete  
**Integration**: Required for all creators (Quest, Spell, Weapon, Armor, Item, NPC, etc.)  
**Priority**: Critical - Must be implemented first!

---

## Problem Statement

### The ID Conflict Problem

In SpellForce, every game content type needs a unique numeric ID:
- **Quests**: 1-999 (official), 9000-9999 (custom)
- **Spells**: 1-299 (official), 300-999 (custom)
- **Weapons**: 1-1000 (official), 10000-19999 (custom)
- **Items**: 1-5000 (official), 30000-39999 (custom)
- **NPCs**: Unknown official range, 40000-49999 (custom)

**Without centralized management**:
- ❌ User manually enters IDs → high risk of duplicates
- ❌ Different creators don't know about each other's IDs
- ❌ Editing existing content might reuse IDs
- ❌ No visibility into available ID ranges
- ❌ Hard to track which IDs are in use

**With ID Manager**:
- ✅ Auto-assign next available ID
- ✅ Validate manual ID entries
- ✅ Track all IDs across all content types
- ✅ Prevent duplicates automatically
- ✅ Show usage statistics
- ✅ Release IDs when content is deleted

---

## Architecture

### ID Manager Class

**Location**: `src/TirganachReloaded/cff_editor/shared/id_manager.py`

**Core Responsibilities**:
1. Track allocated IDs for each content type
2. Assign new IDs (auto or manual)
3. Validate ID ranges
4. Detect conflicts
5. Persist state to disk
6. Provide usage statistics

### Data Storage

**File**: `project_ids.json` (in project root)

**Format**:
```json
{
  "quest": [9000, 9001, 9005, 9010],
  "spell": [300, 301, 305, 310],
  "weapon": [10000, 10001, 10050],
  "armor": [20000, 20001],
  "item": [30000, 30001, 30002],
  "npc": [40000],
  "creature": [50000, 50001],
  "building": [60000]
}
```

**Benefits**:
- Human-readable (JSON)
- Version control friendly (Git)
- Easy to backup/restore
- Can manually edit if needed

---

## ID Ranges

### Official Game Content (DO NOT USE)

| Content Type | Official Range | Count | Notes |
|--------------|----------------|-------|-------|
| Quests | 1-299 | ~300 | Campaign + side quests |
| Spells | 1-299 | ~240 | All magic schools |
| Weapons | 1-1000 | ~719 | All weapon types |
| Items | 1-5000 | ~5000 | All consumables, materials, etc. |
| NPCs | Unknown | ? | All story NPCs |

### Custom Content Ranges (SAFE TO USE)

| Content Type | Custom Range | Capacity | Usage |
|--------------|--------------|----------|-------|
| **Quests** | 9000-9999 | 1,000 | Quest Creator |
| **Spells** | 300-999 | 700 | Spell Wizard |
| **Weapons** | 10000-19999 | 10,000 | Weapon Forge |
| **Armor** | 20000-29999 | 10,000 | Armor Creator (future) |
| **Items** | 30000-39999 | 10,000 | Item Creator (future) |
| **NPCs** | 40000-49999 | 10,000 | NPC Creator (future) |
| **Creatures** | 50000-59999 | 10,000 | Creature Creator (future) |
| **Buildings** | 60000-69999 | 10,000 | Building Creator (future) |

**Why these ranges?**:
- Far from official content (no conflicts)
- Easy to identify custom content (high IDs)
- Large capacity for mods
- Room for future expansions

---

## API Reference

### Core Methods

```python
class IDManager:
    """Centralized ID management for all content types"""
    
    def __init__(self, project_file: str = "project_ids.json"):
        """Initialize ID Manager with project file"""
    
    def allocate_id(self, content_type: ContentType, 
                    requested_id: Optional[int] = None) -> int:
        """
        Allocate a new ID
        
        Args:
            content_type: Type of content (quest, spell, weapon, etc.)
            requested_id: Specific ID to use (None = auto-assign)
        
        Returns:
            Allocated ID
        
        Raises:
            ValueError: If ID is invalid or already in use
        
        Examples:
            # Auto-assign next available ID
            quest_id = id_manager.allocate_id(ContentType.QUEST)
            # Returns: 9000 (if first quest)
            
            # Request specific ID
            spell_id = id_manager.allocate_id(ContentType.SPELL, 350)
            # Returns: 350 (if available)
            # Raises: ValueError (if 350 already used)
        """
    
    def release_id(self, content_type: ContentType, item_id: int):
        """
        Release an ID back to the pool
        
        Use when deleting content or canceling creation.
        
        Example:
            # User canceled quest creation
            id_manager.release_id(ContentType.QUEST, 9005)
        """
    
    def is_id_used(self, content_type: ContentType, item_id: int) -> bool:
        """
        Check if ID is already allocated
        
        Example:
            if id_manager.is_id_used(ContentType.WEAPON, 10050):
                print("Weapon ID 10050 already exists!")
        """
    
    def is_valid_id(self, content_type: ContentType, item_id: int) -> bool:
        """
        Check if ID is in valid range for content type
        
        Example:
            if not id_manager.is_valid_id(ContentType.SPELL, 150):
                print("ID 150 is in official spell range (1-299)")
        """
    
    def get_next_id(self, content_type: ContentType) -> int:
        """
        Get next available ID without allocating it
        
        Example:
            next_quest = id_manager.get_next_id(ContentType.QUEST)
            print(f"Next quest will be ID {next_quest}")
        """
    
    def get_stats(self) -> Dict[str, Dict[str, int]]:
        """
        Get usage statistics for all content types
        
        Returns:
            {
                "quest": {
                    "range_start": 9000,
                    "range_end": 9999,
                    "total_capacity": 1000,
                    "used": 15,
                    "available": 985,
                    "usage_percent": 1.5
                },
                "spell": { ... },
                ...
            }
        """
```

---

## Integration Examples

### Quest Creator Integration

**Step 1: Initialize ID Manager in Wizard**

```python
class QuestCreatorWizard(QWizard):
    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        self.quest_id = None  # Will be assigned in Step 1
        
        # Add pages...
        self.addPage(QuestBasicsPage(self.id_manager))
        # ...
```

**Step 2: Request ID in First Wizard Page**

```python
class QuestBasicsPage(QWizardPage):
    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        
        # ... other widgets ...
        
        # ID assignment section
        id_group = QGroupBox("Quest ID Assignment")
        id_layout = QVBoxLayout()
        
        # Auto-assign option (recommended)
        self.auto_id_radio = QRadioButton("Auto-assign next available ID")
        self.auto_id_radio.setChecked(True)
        id_layout.addWidget(self.auto_id_radio)
        
        # Manual ID option
        self.manual_id_radio = QRadioButton("Manually specify ID")
        id_layout.addWidget(self.manual_id_radio)
        
        self.manual_id_spin = QSpinBox()
        self.manual_id_spin.setRange(9000, 9999)
        self.manual_id_spin.setEnabled(False)
        self.manual_id_radio.toggled.connect(
            lambda checked: self.manual_id_spin.setEnabled(checked)
        )
        id_layout.addWidget(self.manual_id_spin)
        
        # Allocate button
        allocate_btn = QPushButton("Allocate Quest ID")
        allocate_btn.clicked.connect(self.allocate_quest_id)
        id_layout.addWidget(allocate_btn)
        
        # Status label
        self.id_status_label = QLabel("")
        id_layout.addWidget(self.id_status_label)
        
        id_group.setLayout(id_layout)
        # ... add to page layout ...
    
    def allocate_quest_id(self):
        """Allocate a quest ID"""
        try:
            if self.auto_id_radio.isChecked():
                # Auto-assign
                quest_id = self.id_manager.allocate_id(ContentType.QUEST)
            else:
                # Manual ID
                requested_id = self.manual_id_spin.value()
                quest_id = self.id_manager.allocate_id(
                    ContentType.QUEST, 
                    requested_id
                )
            
            self.quest_id = quest_id
            self.id_status_label.setText(
                f"✓ Quest ID {quest_id} allocated successfully!"
            )
            self.id_status_label.setStyleSheet("color: green;")
            
            # Enable next button
            self.completeChanged.emit()
            
        except ValueError as e:
            self.id_status_label.setText(f"✗ Error: {str(e)}")
            self.id_status_label.setStyleSheet("color: red;")
    
    def isComplete(self):
        """Page is complete when ID is allocated"""
        return self.quest_id is not None
```

**Step 3: Release ID if Canceled**

```python
class QuestCreatorWizard(QWizard):
    def done(self, result):
        """Override done to handle ID cleanup"""
        if result == QDialog.Rejected and self.quest_id:
            # User canceled - release the allocated ID
            self.id_manager.release_id(ContentType.QUEST, self.quest_id)
            print(f"Released quest ID {self.quest_id}")
        
        super().done(result)
```

### Spell Creator Integration

Same pattern as Quest Creator, but use `ContentType.SPELL` and range 300-999.

### Weapon Forge Integration

Same pattern, but use `ContentType.WEAPON` and range 10000-19999.

---

## UI Components

### ID Manager Widget (Standalone Tool)

**Access**: `Tools → ID Manager`

**Features**:
- View all allocated IDs across all content types
- See usage statistics (X/1000 used)
- Manually allocate/release IDs
- Search for specific IDs
- Export ID list
- Import ID list (for collaboration)

**Screenshot Mockup**:

```
┌─────────────────────────────────────────────────────────┐
│               ID Management System                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Content Type    Range          Used   Available  %     │
│  ───────────────────────────────────────────────────── │
│  Quests         9000-9999        15     985      1.5%   │
│  Spells         300-999          42     658      6.0%   │
│  Weapons        10000-19999     103    9897      1.0%   │
│  Armor          20000-29999       0   10000      0.0%   │
│  Items          30000-39999       5    9995      0.0%   │
│  NPCs           40000-49999       0   10000      0.0%   │
│  Creatures      50000-59999       0   10000      0.0%   │
│  Buildings      60000-69999       0   10000      0.0%   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Allocate New ID                                 │  │
│  │  Content Type: [Quests     ▼]                    │  │
│  │  ○ Auto-assign next available ID                 │  │
│  │  ○ Manually specify ID: [____]                   │  │
│  │  [Allocate ID]                                   │  │
│  │  Result: ✓ ID 9016 allocated successfully!      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  [Refresh]  [Export IDs...]  [Import IDs...]           │
└─────────────────────────────────────────────────────────┘
```

---

## Best Practices

### For Users

1. **Always use Auto-Assign** unless you have a specific reason
2. **Don't manually use official ID ranges** (1-299 for quests, etc.)
3. **Back up project_ids.json** regularly
4. **Check ID Manager statistics** before creating lots of content
5. **Release IDs** when deleting content

### For Developers

1. **Pass ID Manager to all creators** via constructor
2. **Allocate ID in first wizard step** (not later)
3. **Always release ID** if creation canceled
4. **Validate ID before saving** to CFF/database
5. **Show ID status** clearly in UI (green check/red X)
6. **Handle errors gracefully** (try/except on allocate_id)

---

## Testing Checklist

### Unit Tests

- ☐ Test ID allocation (auto-assign)
- ☐ Test ID allocation (manual)
- ☐ Test ID validation (valid ranges)
- ☐ Test ID validation (invalid ranges)
- ☐ Test duplicate ID prevention
- ☐ Test ID release
- ☐ Test save/load from JSON
- ☐ Test statistics calculation
- ☐ Test edge cases (full range, empty range)

### Integration Tests

- ☐ Quest Creator uses ID Manager
- ☐ Spell Creator uses ID Manager
- ☐ Weapon Forge uses ID Manager
- ☐ IDs persist across application restarts
- ☐ Multiple creators don't conflict
- ☐ Canceled creation releases IDs
- ☐ Export/Import works correctly

### User Acceptance Tests

- ☐ User can create quest with auto-assigned ID
- ☐ User can manually specify ID (if valid)
- ☐ User gets error if ID already used
- ☐ User sees clear ID status
- ☐ User can view ID statistics
- ☐ User can't use official ID ranges

---

## Migration Strategy

### For Existing Projects

If users already have quests/spells/weapons with IDs:

**Step 1: Scan Existing Content**

```python
def scan_existing_content(self):
    """Scan project for existing IDs"""
    
    # Scan quests
    quest_ids = self.scan_quest_files()
    for qid in quest_ids:
        self.id_manager.allocate_id(ContentType.QUEST, qid)
    
    # Scan spells
    spell_ids = self.scan_spell_files()
    for sid in spell_ids:
        self.id_manager.allocate_id(ContentType.SPELL, sid)
    
    # Scan weapons
    weapon_ids = self.scan_weapon_files()
    for wid in weapon_ids:
        self.id_manager.allocate_id(ContentType.WEAPON, wid)
    
    print(f"Imported {len(quest_ids)} quests, "
          f"{len(spell_ids)} spells, "
          f"{len(weapon_ids)} weapons")
```

**Step 2: Prompt User**

```
Project Migration
─────────────────
Found existing content:
  • 12 quests (IDs: 9000-9011)
  • 5 spells (IDs: 300-304)
  • 18 weapons (IDs: 10000-10017)

These IDs will be registered in the ID Manager.

[Continue]  [Cancel]
```

**Step 3: Save to project_ids.json**

Automatically done by ID Manager.

---

## Troubleshooting

### Issue: "No available IDs in range"

**Cause**: All IDs in range are used (e.g., all 1000 quest IDs allocated)

**Solution**:
1. Check ID Manager statistics
2. Delete unused content to free IDs
3. Or: Increase range (requires code change)

### Issue: "ID already in use"

**Cause**: Trying to manually allocate an ID that's already taken

**Solution**:
1. Use auto-assign instead
2. Or: Check ID Manager to find available IDs
3. Or: Delete content using that ID

### Issue: "project_ids.json corrupted"

**Cause**: Manual editing broke JSON format

**Solution**:
1. Restore from backup
2. Or: Regenerate by scanning project files
3. Or: Delete and start fresh (IDs will be re-allocated)

---

## Related Documentation

- **Quest Creator**: [QUEST_CREATION_PLAN.md](QUEST_CREATION_PLAN.md)
- **Spell Creator**: [SPELL_CREATION_PLAN.md](SPELL_CREATION_PLAN.md)
- **Weapon Forge**: [WEAPON_CREATION_PLAN.md](WEAPON_CREATION_PLAN.md)
- **ID Mappings**: [../../docs/Project/ID_MAPPINGS.md](../../docs/Project/ID_MAPPINGS.md)

---

**Document Version**: 1.0  
**Created**: 2025-10-27  
**Author**: SpellSmut Development Team  
**Status**: 🟢 Core System Design Complete  
**Implementation Priority**: 🔴 CRITICAL - Must be implemented first!
