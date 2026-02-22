# Spellforce Data Editor - Category Relationships Analysis

## Overview
This document analyzes all categories in the Spellforce Data Editor and their relationships, focusing on how different data types are linked through IDs. The analysis uses merchant NPCs as a primary example to demonstrate the complex web of relationships.

## Category Structure

### Core Categories (2000s range)

#### Military & Units
- **2001** - Army unit building requirements
  - Links: `ArmyUnitID` → Unit data, `BuildingID` → Building data
- **2005** - Unit/hero stats  
  - Links: `HeadID` → Visual data, `EquipmentMode` → Equipment rules

#### Items & Equipment
- **2003** - Item general info
  - Links: `NameID` → Text data, `UnitStatsID` → Unit stats, `ArmyUnitID` → Units, `BuildingID` → Buildings
- **2004** - Item armor data
  - Links: `ItemID` → Category2003
- **2012** - Item UI data
  - Links: `ItemID` → Category2003
- **2013** - Inventory spell scroll link with installed spell scroll
  - Links: `ItemID` → Category2003, `InstalledScrollItemID` → Category2003
- **2014** - Item weapon effects/inventory scroll link with spell
  - Links: `ItemID` → Category2003
- **2015** - Item weapon data
  - Links: `ItemID` → Category2003

#### Spells & Abilities
- **2002** - Spell data
  - Links: `SpellLineID` → Spell lines, `SkillReq[0-11]` → Skill requirements

#### Buildings & Resources
- **2030** - Building collision data
  - Links: `BuildingID` → Building general data
- **2031** - Building resource requirements
  - Links: `BuildingID` → Building general data, `ResourceID` → Resource data

#### NPCs & Merchants
- **2041** - Merchants link with unit general data
  - Links: `MerchantID` → Merchant inventory/pricing, `UnitID` → Unit data
- **2042** - Merchant inventory
  - Links: `MerchantID` → Category2041, `ItemID` → Category2003
- **2047** - Merchant sell/buy rate
  - Links: `MerchantID` → Category2041
- **2051** - NPC link with text data
  - Links: `NPCID` → NPC entities, `TextID` → Text/dialogue data

#### Skills & Progression
- **2006** - Hero/worker skills
  - Links: `UnitStatsID` → Category2005, `SkillMajorID`/`SkillMinorID` → Skill definitions

## Merchant NPC Relationship Example

### Complete Relationship Chain for a Merchant NPC

```
Merchant NPC (Category 2041)
├── UnitID → Unit/General Data (not yet explored)
├── MerchantID → Multiple linked categories:
│   ├── Category2042 (Merchant Inventory)
│   │   └── ItemID → Category2003 (Item General Info)
│   │       ├── NameID → Text Data (names/descriptions)
│   │       ├── UnitStatsID → Category2005 (Unit Stats) 
│   │       ├── ArmyUnitID → Category2001 (Army Requirements)
│   │       └── BuildingID → Building Data
│   │           ├── Category2030 (Building Collision)
│   │           └── Category2031 (Building Resources)
│   │
│   └── Category2047 (Merchant Pricing)
│       └── ItemType → Price multipliers by item type
│
└── If also an NPC: Category2051 (NPC Text Links)
    └── TextID → Dialogue/Text Data
```

### Detailed Merchant Data Flow

1. **Merchant Definition (2041)**
   - `MerchantID` (primary key)
   - `UnitID` (links to unit's general data)

2. **Merchant Inventory (2042)**
   - `MerchantID` (foreign key to 2041)
   - `ItemID` (foreign key to 2003)
   - `Stock` (quantity available)

3. **Item Details (2003)**
   - `ItemID` (primary key)
   - `NameID` (text data for item name)
   - `UnitStatsID` (if item affects unit stats)
   - `ArmyUnitID` (if item is related to specific units)
   - `BuildingID` (if item is building-related)
   - `SellValue`/`BuyValue` (base prices)

4. **Merchant Pricing (2047)**
   - `MerchantID` (foreign key to 2041)
   - `ItemType` (category of items)
   - `PriceMultiplier` (modifies base prices from 2003)

## ID Linking Patterns

### Primary ID Types
- **UnitID**: Links to unit/general data categories
- **ItemID**: Primary key for item system (2003, 2004, 2012, 2013, 2014, 2015)
- **BuildingID**: Links to building data (2001, 2030, 2031)
- **MerchantID**: Primary key for merchant system (2041, 2042, 2047)
- **NPCID**: Links to NPC text data (2051)
- **SpellID**: Primary key for spell system (2002)
- **StatsID**: Links to unit/hero stats (2005, 2006)

### Relationship Types
1. **One-to-One**: Single record relationships (e.g., 2041 → Unit data)
2. **One-to-Many**: Parent-child relationships (e.g., 2041 → multiple 2042 inventory entries)
3. **Many-to-Many**: Complex relationships (e.g., Items ↔ Units via ArmyUnitID)

## Category Types Analysis

### Single Item Categories (CategoryBaseSingle)
- Store one record per ID
- Examples: 2002 (Spells), 2003 (Items), 2004 (Item Armor), 2005 (Unit Stats)

### Multiple Item Categories (CategoryBaseMultiple) 
- Store multiple records per ID using sub-IDs
- Examples: 2001 (Army Requirements), 2006 (Skills), 2042 (Merchant Inventory), 2047 (Pricing)

### Custom Implementation Categories
- Specialized logic for complex data
- Example: 2030 (Building Collision) with coordinate data

## Data Integrity Dependencies

### Critical Link Chains
1. **Merchant System**: 2041 → 2042 → 2003 → Text/Stats/Building data
2. **Item System**: 2003 → 2004/2012/2013/2014/2015 (item details)
3. **Unit System**: 2005 → 2006 (skills), 2001 (building requirements)
4. **Building System**: Building ID → 2030 (collision), 2031 (resources)

### Referential Integrity Rules
- All ItemID references should exist in Category2003
- All MerchantID references should exist in Category2041
- All BuildingID references should point to valid building data
- Text IDs (NameID, TextID) should resolve to text/localization data

## Visualization Approach

### Recommended Tree Structure
```
Root Entity (Merchant/NPC/Unit/Item)
├── Core Attributes
├── Related Systems (Inventory/Skills/Buildings)
├── Text/Localization Data
└── Visual/UI Data
```

### Interactive Visualization Features
1. **Expandable nodes** for exploring relationship chains
2. **Color coding** by category type (military, economic, text, etc.)
3. **Hover tooltips** showing ID values and category descriptions
4. **Search functionality** to find entities across categories
5. **Dependency highlighting** when selecting related items

## Missing Categories to Investigate

Based on the analysis, several referenced categories weren't fully explored:
- Unit/General Data (referenced by UnitID in 2041)
- Text/Localization Data (referenced by NameID, TextID)
- Skill Definitions (referenced by SkillMajorID/MinorID)
- Resource Data (referenced by ResourceID in 2031)
- Spell Line Data (referenced by SpellLineID in 2002)

## Implementation Recommendations

### For Data Editor UI
1. **Relationship Panel**: Show all related categories when selecting an item
2. **Navigation Links**: Clickable IDs to jump between related records
3. **Dependency Validation**: Warn before deleting items with dependencies
4. **Bulk Operations**: Allow cascading updates across related categories

### For Data Analysis
1. **Graph Database**: Consider representing relationships as a graph for complex queries
2. **Impact Analysis**: Tools to see all entities affected by changes
3. **Data Validation**: Comprehensive integrity checking across all links
4. **Export/Import**: Preserve relationships during data transfer

## Conclusion

The Spellforce Data Editor uses a sophisticated ID-based relationship system where categories interconnect through foreign key references. The merchant NPC example demonstrates how a single entity can have relationships spanning dozens of categories, creating a complex web of dependencies that must be maintained for data integrity.

The most critical relationship chains involve:
- Items (2003) as a central hub connecting to equipment, stats, buildings, and text
- Merchants (2041) as a bridge between units and economic systems  
- Buildings as connectors between units, resources, and collision data

Understanding these relationships is essential for proper data management and for developing tools that can safely manipulate the game data while maintaining referential integrity.
