# NPC Creation System Plan
## 👤 The NPC Workshop

## Overview

The **NPC Creation System** allows users to create custom non-player characters with full stat customization, dialogue trees, and behavior scripting. The system includes features for editing existing NPCs from the game and saving them under new IDs. A research flag is included regarding character appearance customization possibilities in SpellForce.

**Status**: ✅ Planning Complete  
**Priority**: Medium  
**Dependencies**: ID Management System, Quest Creator (for dialogue integration)

---

## Key Features

### 1. Basic NPC Properties
- Name, title, and description
- Character class and level
- Factions and relationship settings
- Base stats and abilities

### 2. Appearance System
**RESEARCH FLAG**: Current research needed to determine extent of character appearance customization possible in SpellForce
  - Head model selection (if supported)
  - Clothing/armor customization
  - Voice selection from available options
  - Inventory/starting equipment
  - Research task: Document whether new character models can be created or if only existing ones can be reused with new IDs.

### 3. Stat System
**Base Stats**:
- Strength, Stamina, Agility, Dexterity
- Intelligence, Wisdom, Charisma

**Combat Stats**:
- Health (HP), Mana (MP)
- Attack power, defense
- Resistances (Fire, Ice, Black, Mind)

**Skill Ratings**:
- Combat skills (Melee, Ranged, Magic)
- Crafting abilities
- Trade and barter skills

### 4. Behavior & AI
- Default behavior patterns
- Dialogue activation conditions
- Combat engagement triggers
- Movement and patrol routes

### 5. Dialogue & Quest Integration
- Embedded dialogue trees (using Quest Creator system)
- Quest giver/receiver functionality
- Response to player actions
- Reputation and relationship tracking

### 6. Edit Existing NPCs
**Feature**: Load existing NPCs, modify, save under new ID
- Access to all existing NPCs from game files
- Modify stats, appearance, behavior
- Adjust dialogue and quest connections
- Create variants of existing NPCs

---

## The 7-Phase NPC Workshop

### Phase 1: Mode Selection & ID Assignment
```
Mode Options:
  ├─ Create New NPC
  ├─ Edit Existing NPC (from game files)
  └─ Duplicate Existing NPC

ID Assignment:
  ├─ Auto-assign next available (via ID Manager)
  ├─ Manual override allowed (validated by ID Manager)
  └─ Range: 40000-49999 (10,000 capacity)
  
NPC Browser (for Edit/Duplicate modes):
  ├─ Filter by class, faction, location
  ├─ Search by name
  └─ Preview selected NPC
```

### Phase 2: Basic Identity & Classification
```
Naming & Identity:
  ├─ NPC Name (max 32 chars)
  ├─ Title/Class Display
  └─ Description (flavor text)

Classification:
  ├─ NPC Type (Friendly/Merchant/Guard/Hostile)
  ├─ Character Class (Warrior/Mage/Rogue/Multi-class)
  ├─ Level Range (1-100)
  └─ Faction Assignment (Alchemist, Bandit, etc.)
```

### Phase 3: Base Statistics
```
Primary Stats:
  ├─ Strength
  ├─ Stamina
  ├─ Agility
  ├─ Dexterity
  ├─ Intelligence
  ├─ Wisdom
  └─ Charisma

Derived Stats:
  ├─ Health Points (HP)
  ├─ Mana Points (MP)
  ├─ Base Armor Class
  └─ Carry Weight Capacity
```

### Phase 4: Combat & Skills
```
Combat Stats:
  ├─ Melee Attack Rating
  ├─ Ranged Attack Rating
  ├─ Magic Attack Rating
  ├─ Physical Defense
  └─ Magic Defense

Skills & Abilities:
  ├─ Weapon Specializations
  ├─ Magic School Ratings
  ├─ Crafting Skills
  └─ Non-combat Abilities
```

### Phase 5: Appearance & Voice
```
Visual Properties:
  ├─ Base Character Model (research needed)
  ├─ Head Selection (if available)
  ├─ Hair Style & Color (if customizable)
  └─ Skin Tone (if customizable)

Audio Properties:
  ├─ Voice Set Selection
  └─ Sound Effects (if applicable)

RESEARCH TASK: Document appearance customization limits in SpellForce
```

### Phase 6: Behavior & Interaction
```
Behavior Patterns:
  ├─ Default AI Settings
  ├─ Movement Type (stationary/patrol/wander)
  ├─ Combat Engagement Triggers
  └─ Interaction Radius

Quest & Dialogue Integration:
  ├─ Quest Giver Status
  ├─ Dialogue Tree Connection
  ├─ Special Abilities Access
  └─ Reputation Impact Settings
```

### Phase 7: Advanced Features & Export
```
Advanced Features:
  ├─ Inventory Contents
  ├─ Spawn Location (X/Y coordinates)
  ├─ Spawn Conditions (time, quest state, etc.)
  └─ Special Abilities/Spells

Export & Validation:
  ├─ Balance Rating (0-100%)
  ├─ Game Compatibility Check
  ├─ Export to CFF format
  ├─ Save to .npc file
  └─ Add to ID Manager registry
```

---

## Research Requirements

**RESEARCH FLAG**: Determine the full extent of character appearance customization possible in SpellForce:

1. Can new character models be created, or only existing ones reused?
2. What aspects of appearance (hair, skin color, facial features) are customizable?
3. Are there limitations on assigning different armor/visuals to NPCs?
4. What voice options are available, and can custom voices be added?

**Research Task**: Create a comprehensive document outlining character customization possibilities before Phase 5 implementation.

---

## Implementation Timeline

**Week 1**: Phases 1-2 (Mode selection, identity) + ID Manager integration  
**Week 2**: Phases 3-4 (Stats, combat) + edit existing feature  
**Week 3**: Research phase for appearance system, basic Phase 5  
**Week 4**: Phases 6-7 (Behavior, advanced features)  
**Week 5**: CFF export + validation + savefile system integration  
**Week 6**: Testing + polish

---

## Success Criteria

- ✅ Create new NPCs in < 30 minutes
- ✅ Edit existing NPCs successfully
- ✅ NPCs behave correctly in-game
- ✅ All stats accurately reflected in-game
- ✅ ID Manager prevents conflicts
- ✅ Research document completed for appearance system

---

## Related Documents

- [Quest Creator](QUEST_CREATION_PLAN.md) - Dialogue integration
- [ID Management System](ID_MANAGEMENT_SYSTEM.md) - Shared component
- [Character Creation Research](../Research/CHARACTER_APPEARANCE_RESEARCH.md) - NEW

---

**Document Version**: 1.0  
**Created**: 2025-10-27  
**Status**: ✅ Planning Complete - Ready for Implementation