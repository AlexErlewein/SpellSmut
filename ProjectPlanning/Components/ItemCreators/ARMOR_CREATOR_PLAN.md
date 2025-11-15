# Armor Creation System Plan
## 🛡️ The Armor Forge

## Overview

The **Armor Creation System** allows users to create custom armor pieces (helmets, chest armor, legs, boots, shields, rings) with full stat customization. Similar to the Weapon Forge, users can create new armor, edit existing pieces, and save under new IDs. The system includes material integration, set bonuses, visual customization, and **school requirements** support.

**Status**: ✅ **IMPLEMENTED**  
**Priority**: High  
**Dependencies**: ID Management System, Weapon Forge (for architecture reference)

**Latest Updates**:
- ✅ Armor model now supports school requirements (Nov 2025)
- ✅ Enhanced armor browser displays school requirements
- ✅ Requirements preserved during duplication
- ✅ Full integration with CFFArmorLoader

---

## Key Features

### 1. Armor Slots (7 Equipment Slots)

| Slot ID | Slot Name | Constant | Examples |
|---------|-----------|----------|----------|
| 0 | Head/Helmet | `SlotHead` | Helmets, crowns, hoods |
| 2 | Chest/Armor | `SlotChest` | Breastplates, robes, tunics |
| 5 | Legs/Pants | `SlotLegs` | Greaves, pants, leggings |
| 7 | Boots/Feet | `SlotFeet` | Boots, shoes, sandals |
| 4 | Right Ring | `SlotRightRing` | Rings, bands |
| 6 | Left Ring | `SlotLeftRing` | Rings, bands |
| 3 | Left Hand/Shield | `SlotLeftHand` | Shields, bucklers |

### 2. Armor Stats

Every armor piece can modify:

**Primary Stats**:
- Strength
- Stamina
- Agility
- Dexterity
- Intelligence
- Wisdom
- Charisma

**Derived Stats**:
- Health (HP)
- Mana (MP)
- Armor (physical defense)
- Resist Fire
- Resist Ice
- Resist Black (dark magic)
- Resist Mind (mental magic)

**Speed Modifiers**:
- Run Speed
- Fight Speed (attack speed)
- Cast Speed (spell casting)

### 3. Edit Existing Armor

**Feature**: Load from `enhanced_armor.json`, modify, save under new ID

**Use Cases**:
- Create upgraded versions ("Iron Helmet" → "Iron Helmet +1")
- Change materials
- Adjust stat bonuses
- Create set pieces

---

## The 7-Phase Armor Forge

### Phase 1: Mode Selection & ID Assignment
```
Mode Options:
  ├─ Create New Armor
  ├─ Edit Existing Armor (from `enhanced_armor.json`)
  └─ Duplicate Existing Armor
  
ID Assignment:
  ├─ Auto-assign next available (via ID Manager)
  ├─ Manual override allowed (validated by ID Manager)
  └─ Range: 20000-29999 (10,000 capacity)
  
Armor Browser (for Edit/Duplicate modes):
  ├─ Filter by slot, type, material
  ├─ Search by name
  └─ Preview selected armor
```

### Phase 2: Basic Properties & Classification
```
Naming & Identity:
  ├─ Armor Name (max 32 chars)
  ├─ Display Name (for tooltips)
  └─ Description (flavor text)

Slot & Type Classification:
  ├─ Equipment Slot (Head/Chest/Legs/Feet/Ring/Shield)
  ├─ Armor Type (Cloth/Leather/Chain/Plate/Magic)
  └─ Material Category (Leather/Iron/Steel/Mithril/etc.)

Quality & Rarity:
  ├─ Tier (Common/Rare/Epic/Legendary/Unique)
  ├─ Base Level Requirement
  ├─ Class Restrictions (optional)
  └─ School Requirements (elemental/white/black magic schools)
```

### Phase 3: Core Stat Bonuses
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
  ├─ Health Bonus (+HP)
  ├─ Mana Bonus (+MP)
  ├─ Base Armor Value (physical defense)
  └─ Additional Stats (Speed, etc.)
```

### Phase 4: Resistance & Defense Systems
```
Elemental Resistances:
  ├─ Fire Resistance (%)
  ├─ Ice Resistance (%)
  ├─ Black Magic Resistance (%)
  └─ Mind Magic Resistance (%)

Defense Mechanics:
  ├─ Physical Damage Reduction (%)
  ├─ Magic Damage Reduction (%)
  └─ Critical Hit Reduction (%)
```

### Phase 5: Speed & Mobility Modifiers
```
Speed Modifiers:
  ├─ Run Speed (% change)
  ├─ Fight Speed (% change)
  ├─ Cast Speed (% change)
  └─ Movement Speed Cap (can't exceed 100%)

Special Movement Bonuses:
  ├─ Stealth Bonus (harder to detect)
  ├─ Swimming Speed (if applicable)
  └─ Jump Height (if applicable)
```

### Phase 6: Visual Properties & Materials
```
Visual Components:
  ├─ Icon Selection (from ExtractedAssets/UI/)
  ├─ 3D Model Reference (mesh file)
  ├─ Texture Assignment (diffuse map)
  └─ Normal Map (for lighting)

Material Properties:
  ├─ Material Name (for crafting)
  ├─ Visual Appearance (color/shininess)
  ├─ Sound Effects (equip/unequip)
  └─ Special Effects (glow, particles)
```

### Phase 7: Advanced Features & Export
```
Advanced Features:
  ├─ Item Set Assignment (create/join sets)
  ├─ Set Bonuses (for 2/3/4-piece bonuses)
  ├─ Special Abilities (passive effects)
  └─ Enchantment Slots (if applicable)

Export & Validation:
  ├─ Stat Balance Rating (0-100%)
  ├─ Game Compatibility Check
  ├─ Export to CFF format
  ├─ Save to .armor file
  └─ Add to ID Manager registry
```

---

## Armor Sets

**Feature**: Create matching armor sets with bonuses

**Example**:
```
Dragon Scale Set:
  - Dragon Scale Helmet (ID 20001)
  - Dragon Scale Chest (ID 20002)
  - Dragon Scale Legs (ID 20003)
  - Dragon Scale Boots (ID 20004)
  
Set Bonuses:
  - 2 pieces: +10% Fire Resist
  - 4 pieces: +20% Fire Resist, +5 Strength
```

---

## Implementation Timeline

**Week 1**: Phases 1-2 (Mode selection, basic properties) + ID Manager integration  
**Week 2**: Phases 3-4 (Stat system, resistances) + edit existing feature  
**Week 3**: Phases 5-6 (Speed modifiers, visual properties) + material system  
**Week 4**: Phase 7 (Advanced features) + armor sets implementation  
**Week 5**: CFF export + validation + savefile system integration  
**Week 6**: Testing + polish

---

## Success Criteria

- ✅ Create new armor in < 20 minutes
- ✅ Edit existing armor pieces
- ✅ Duplicate armor with all properties preserved (including school requirements)
- ✅ Armor sets work with bonuses
- ✅ School requirements displayed and preserved
- ✅ Armor works in-game without errors
- ✅ ID Manager prevents conflicts
- ✅ Browser shows requirements in details panel

---

## Implementation Status

### ✅ Completed Features
- **Armor Model**: Requirements field added with school requirements support
- **Enhanced Armor Browser**: 
  - Uses CFFArmorLoader for complete data loading
  - Displays school requirements in details panel
  - Preserves requirements during duplication
- **CFFArmorLoader Integration**: Full requirements loading from `item_requirements` table
- **Localization**: Multi-language support for armor names and properties

### 🔄 In Progress
- Export to CFF format with requirements
- Advanced armor set creation UI

### 📋 Planned
- Visual properties customization
- Enhanced material system
- Special abilities system

---

## Related Documents

- [Weapon Creator](WEAPON_CREATION_PLAN.md) - Similar architecture
- [ID Management System](ID_MANAGEMENT_SYSTEM.md) - Shared component
- Armor Data: `src/TirganachReloaded/enhanced_armor.json`

---

**Document Version**: 1.2  
**Created**: 2025-10-27  
**Last Updated**: 2025-11-15  
**Status**: ✅ Core System Implemented - School Requirements Support Added
