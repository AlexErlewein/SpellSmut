# Armor Creation System Plan
## 🛡️ The Armor Forge

## Overview

The **Armor Creation System** allows users to create custom armor pieces (helmets, chest armor, legs, boots, shields, rings) with full stat customization. Similar to the Weapon Forge, users can create new armor, edit existing pieces, and save under new IDs. The system includes material integration, set bonuses, and visual customization.

**Status**: 🟡 Planning Phase  
**Priority**: High  
**Dependencies**: ID Management System, Weapon Forge (for architecture reference)

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

## Wizard Steps

```
Step 1: Mode & ID Assignment
  ├─ Create New / Edit Existing / Duplicate
  ├─ ID Assignment (via ID Manager)
  │   └─ Range: 20000-29999 (10,000 capacity)
  └─ Armor Browser (if Edit mode)

Step 2: Basic Properties
  ├─ Armor Name
  ├─ Armor Slot (Head/Chest/Legs/Feet/Ring/Shield)
  ├─ Armor Type (Cloth/Leather/Chain/Plate)
  ├─ Material (Leather, Iron, Steel, Mithril, etc.)
  └─ Description

Step 3: Stat Bonuses
  ├─ Primary Stats (Str/Sta/Agi/Dex/Int/Wis/Cha)
  ├─ Derived Stats (Health/Mana/Armor)
  ├─ Resistances (Fire/Ice/Black/Mind)
  └─ Speed Modifiers (Run/Fight/Cast)

Step 4: Requirements & Value
  ├─ Stat Requirements (level, class restrictions)
  ├─ Economic Value (sell/buy)
  ├─ Rarity (Common → Legendary)
  └─ Item Set (optional)

Step 5: Visual & Effects
  ├─ Icon Assignment (browse extracted icons)
  ├─ 3D Model (armor mesh)
  ├─ Texture (armor appearance)
  └─ Special Effects (glow, particles)

Step 6: Review & Export
  ├─ Stat Summary
  ├─ Balance Rating
  ├─ Validation
  └─ Export to CFF + Savefile
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

**Week 1**: Core wizard + ID Manager integration  
**Week 2**: Stat system + edit existing feature  
**Week 3**: Material system + armor sets  
**Week 4**: Visual/icon assignment  
**Week 5**: CFF export + validation  
**Week 6**: Testing + polish

---

## Success Criteria

- ✅ Create new armor in < 20 minutes
- ✅ Edit existing armor pieces
- ✅ Armor sets work with bonuses
- ✅ Armor works in-game without errors
- ✅ ID Manager prevents conflicts

---

## Related Documents

- [Weapon Creator](WEAPON_CREATION_PLAN.md) - Similar architecture
- [ID Management System](ID_MANAGEMENT_SYSTEM.md) - Shared component
- Armor Data: `src/TirganachReloaded/enhanced_armor.json`

---

**Document Version**: 1.0  
**Created**: 2025-10-27  
**Status**: 🟡 Planning Complete - Ready for Implementation
