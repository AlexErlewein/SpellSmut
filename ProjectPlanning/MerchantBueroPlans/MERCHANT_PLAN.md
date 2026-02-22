# Merchant Section for GraufurterBuergerBuero - Implementation Plan

## Overview

This plan outlines adding a **Merchant Section** to the GraufurterBuergerBuero NPC creation tool. The enhancement allows users to:
1. Create NPCs configured as merchants with inventory
2. Export merchant data to CFF format (categories 2041, 2042, 2047)
3. Place these merchant NPCs on maps using the SpellForce MapEditor

**Status**: ✅ Planning Complete  
**Priority**: High  
**Dependencies**: Existing NPC Creation System, Item Loader

---

## Background: SpellForce Merchant Data Structure

The SpellForce game uses **three CFF categories** to define merchants:

| Category | ID | Name | Fields | Description |
|----------|-----|------|--------|-------------|
| **2041** | `c2041` | Merchant Definition | `MerchantID`, `UnitID` | Links merchant to an NPC/Unit |
| **2042** | `c2042` | Merchant Inventory | `MerchantID`, `ItemID`, `Stock` | Items the merchant sells |
| **2047** | `c2047` | Buy/Sell Rates | `MerchantID`, `ItemType`, `PriceMultiplier` | Price adjustments by item type |

### Relationship Flow
```
NPC (Unit) → Category 2041 (MerchantID ← UnitID link)
                ↓
         Category 2042 (items sold by this MerchantID)
                ↓
         Category 2047 (price modifiers for this MerchantID)
```

### Current Issue: Map Placement
The user noted: *"currently the newly created NPCs are not placeable on the map via the MapEditor"*

**Root Cause**: New NPCs created in GraufurterBuergerBuero exist as JSON but lack the required CFF category entries (especially category 2000/unit data) needed for the MapEditor to recognize them.

**Solution**: This implementation will export proper CFF binary data that can be merged into GameData.cff.

---

## User Requirements (Clarified)

| # | Requirement | Decision |
|---|-------------|----------|
| 1 | Merchant ID Range | Use NPC range (40000-49999) - shared with regular NPCs |
| 2 | Item Loader | Create new item loader, reuse code from OrthancsSchmiede |
| 3 | Price Multipliers | Include Category 2047 (buy/sell rates) |
| 4 | Map Placement | Workflow: Create in GBB → Export CFF → Merge → Place via MapEditor using Unit ID |

---

## Implementation Plan

### Phase 1: Data Model Updates

#### 1.1 Update `npc_creation_data.py`
Add new dataclasses:

```python
@dataclass
class MerchantItem:
    """Individual item in merchant inventory"""
    item_id: int
    stock: int = 1  # Quantity available (0 = unlimited)

@dataclass
class MerchantPriceModifier:
    """Price multiplier for item types"""
    item_type: int  # 1=Equipment, 2=Inventory Rune, etc.
    multiplier: int = 100  # 100 = normal price

@dataclass
class MerchantData:
    """Complete merchant configuration"""
    merchant_id: int  # Same as NPC ID (40000+)
    linked_npc_id: int  # Reference to the NPC/Unit
    inventory: List[MerchantItem] = field(default_factory=list)
    price_modifiers: List[MerchantPriceModifier] = field(default_factory=list)
```

Add field to `NpcCreationData`:
```python
@dataclass
class NpcCreationData:
    # ... existing fields ...
    merchant_data: Optional[MerchantData] = None
```

---

### Phase 2: Item Loader

#### 2.1 Create `item_loader.py` in GraufurterBuergerBuero
- **Location**: `src/GraufurterBuergerBuero/item_loader.py`
- **Purpose**: Load all items from CFF category 2009 for merchant inventory selection
- **Reuse**: Adapt code from `OrthancsSchmiede/cff_weapon_loader.py` and `cff_armor_loader.py`

```python
class ItemLoader:
    """Loads items from CFF category 2009"""
    
    def load_all_items() -> Dict[int, Dict]:
        """Returns {item_id: {name, type, price, slot, etc.}}"""
    
    def get_items_by_type(item_type: str) -> Dict[int, Dict]:
        """Filter items by type (Equipment, Rune, etc.)"""
    
    def search_items(query: str) -> List[Tuple[int, str]]:
        """Search items by name"""
```

#### 2.2 Item Types Reference (from C# Control31.cs)
```python
ITEM_TYPES = {
    0: "Unknown",
    1: "Equipment",
    2: "Inventory Rune",
    3: "Installed Rune",
    # ... more types
}
```

---

### Phase 3: NPC Creator Wizard Enhancement

#### 3.1 Add MerchantPage Wizard Step

**Trigger**: Only appears when `npc_type` = "merchant" (in BasicIdentityPage)

**Layout**:
```
+-------------------------------------------------------------+
| MERCHANT CONFIGURATION                                      |
+-------------------------------------------------------------+
| Merchant Settings:                                           |
|   [Merchant ID: ___________] [Auto-Allocate] ✓             |
|   (Linked to NPC ID: 40001)                                |
+-------------------------------------------------------------+
| INVENTORY                                                    |
| +---------------------------------------------------------+ |
| | Item ID | Stock | Item Name                    | Actions| |
| +---------+-------+--------------------------------+--------+ |
| | 1234    | 5     | Iron Sword                    | [Edit] | |
| | 5678    | 10    | Health Potion                 | [X]    | |
| | ...     | ...   | ...                           | ...    | |
| +---------------------------------------------------------+ |
| [+ Add Item]                                                |
+-------------------------------------------------------------+
| PRICE MODIFIERS (Optional)                                 |
|   Equipment: [100]% (normal)                               |
|   Inventory Rune: [100]%                                    |
|   [Save Changes]                                            |
+-------------------------------------------------------------+
```

#### 3.2 Item Selector Dialog
- Searchable list of all items from ItemLoader
- Filter by item type
- Shows: Item ID, Name, Type, Price
- Multi-select support

#### 3.3 Update collect_npc_data()
Add merchant data collection from MerchantPage to `NpcCreationData`

---

### Phase 4: CFF Exporter Updates

#### 4.1 Update `npc_cff_exporter.py`

Add export functions for merchant categories:

```python
def export_merchant_to_cff(npc_data: NpcCreationData) -> Dict[int, bytes]:
    """
    Export merchant data to CFF binary format
    
    Returns:
        {
            2041: bytes,  # Merchant Definition
            2042: bytes,  # Merchant Inventory  
            2047: bytes,  # Price Modifiers (optional)
        }
    """
```

#### 4.2 Binary Format Reference (from C# Category structures)

**Category 2041** (Merchant Definition):
```csharp
struct Category2041Item {
    ushort MerchantID;  // 2 bytes
    ushort UnitID;      // 2 bytes
    // Total: 4 bytes per record
}
```

**Category 2042** (Inventory):
```csharp
struct Category2042Item {
    ushort MerchantID;  // 2 bytes
    ushort ItemID;      // 2 bytes  
    ushort Stock;       // 2 bytes
    // Total: 6 bytes per record
}
```

**Category 2047** (Price Modifiers):
```csharp
struct Category2047Item {
    ushort MerchantID;      // 2 bytes
    byte   ItemType;        // 1 byte
    ushort PriceMultiplier; // 2 bytes
    // Total: 5 bytes per record
}
```

---

### Phase 5: UI Integration

#### 5.1 Update Main Window (`graufurter_buerger_buero.py`)

Add Merchant section to NPC Details display:

```python
# In show_npc_details() method, add:
if npc_info.get("npc_type") == "merchant":
    merchant_group = QGroupBox("MERCHANT DATA")
    # Display:
    # - Merchant ID
    # - Linked NPC ID  
    # - Inventory table (Item ID | Name | Stock)
    # - Price modifiers
```

#### 5.2 Update NPC Tree Filtering
Allow filtering by "Merchant" type in tree view

---

### Phase 6: Testing & Validation

#### 6.1 Test Cases
- [ ] Create merchant with inventory, export to CFF
- [ ] Edit existing merchant, modify inventory
- [ ] Verify CFF categories 2041, 2042, 2047 are correctly generated
- [ ] Test item search in selector dialog
- [ ] Test price modifier UI
- [ ] Verify exported data can be merged into GameData.cff

#### 6.2 Validation Checklist
- [ ] Merchant ID auto-allocation works
- [ ] Item IDs are validated (exist in category 2009)
- [ ] Stock values are in valid range (0-65535)
- [ ] Price multipliers are valid (0-65535)

---

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `npc_creation_data.py` | Modify | Add MerchantItem, MerchantPriceModifier, MerchantData classes |
| `item_loader.py` | Create | New item loader from CFF category 2009 |
| `npc_creator_wizard.py` | Modify | Add MerchantPage, integrate into wizard flow |
| `npc_cff_exporter.py` | Modify | Add export functions for categories 2041, 2042, 2047 |
| `graufurter_buerger_buero.py` | Modify | Add merchant display in NPC details |
| `npc_loader.py` | Modify | Support loading merchant data from JSON |

---

## Workflow Summary

### Creating a Merchant NPC
```
1. Open GraufurterBuergerBuero
2. Click "Create NPC"
3. Select NPC Type = "Merchant"
4. Fill in Basic Identity (name, class, etc.)
5. Configure stats, appearance, equipment (optional)
6. NEW: Merchant Page appears
   - Auto-allocates Merchant ID (same as NPC ID)
   - Add items to inventory via item selector
   - Set price modifiers (optional)
7. Review & Export
8. Export creates:
   - NPC CFF categories (2000, 2001, etc.)
   - Merchant categories (2041, 2042, 2047)
```

### Placing Merchant on Map
```
1. Merge exported CFF into GameData.cff
2. Open SpellForce MapEditor
3. Add Unit
4. Set Unit ID to the NPC ID (e.g., 40001)
5. Merchant functionality works automatically
   (Category 2041 links UnitID -> MerchantID)
```

---

## Open Questions / Future Enhancements

1. **Item Icons**: Add icon preview in item selector (requires icon system integration)
2. **Bulk Import**: Import inventory from CSV/template
3. **Template Merchants**: Pre-configured merchant templates (Blacksmith, Alchemist, etc.)
4. **Guild Stores**: Multiple merchants with shared inventory

---

## References

- C# Category Files: `cs_src/spellforce_data_editor/SFEngine/SFCFF/CTG/Category204*.cs`
- C# Category UI: `cs_src/spellforce_data_editor/SpellforceDataEditor/SFCFF/category forms/Control29-31.cs`
- Existing NPC Plan: `ProjectPlanning/Components/EntityCreators/NPC_CREATOR_PLAN.md`
- OrthancsSchmiede Loaders: `src/OrthancsSchmiede/cff_*_loader.py`

---

*Document created: 2026-02-22*  
*For implementation in: GraufurterBuergerBuero*
