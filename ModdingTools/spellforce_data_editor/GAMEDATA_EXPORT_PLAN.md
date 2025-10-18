# GameData.cff Export Implementation Plan

**Date:** 2025-10-18
**Goal:** Extract and export GameData.cff file contents to human-readable formats (JSON, CSV, or both)

---

## 1. Analysis Findings

### 1.1 GameData.cff File Structure

The `Gamedata.cff` file is a **binary chunk file format** that contains all game data for SpellForce. Key characteristics:

- **Format:** Custom chunk-based binary format (handled by `SFChunk.SFChunkFile`)
- **Categories:** 50+ category classes (numbered 2001-2072 with gaps)
- **Organization:** Each category contains structured data for different game systems
- **Binary Serialization:** Uses `StructLayout(LayoutKind.Sequential, Pack = 1)` for efficient packing

### 1.2 Category System Architecture

Each category implements the `ICategory` interface:
- **Load/Save:** Binary serialization from/to chunk files
- **Items:** Stored in `List<T>` where T is a struct implementing `ICategoryItem`
- **IDs:** Each item has a unique ID (accessed via `GetID()`/`SetID()`)
- **Two Types:**
  - `CategoryBaseSingle<T>`: Single ID per item (most common)
  - `CategoryBaseMultiple<T>`: ID + SubID per item (for one-to-many relationships)

### 1.3 Weapon-Related Data Categories

Weapon data is distributed across **multiple categories**:

| Category | Description | Key Fields |
|----------|-------------|------------|
| **2003** | Item general info | ItemID, ItemType1/2, NameID, SellValue, BuyValue, ItemSetID |
| **2004** | Item armor/stats data | ItemID, Strength, Stamina, Agility, Dexterity, Health, Armor, Resistances |
| **2012** | Item UI data | ItemID, UIIndex, UIHandle (icon name), IsScaledDown |
| **2013** | Spell scroll links | ItemID, InstalledScrollItemID |
| **2014** | Weapon effects | ItemID, EffectIndex, EffectID (multiple effects per weapon) |
| **2015** | **Weapon combat data** | ItemID, MinDamage, MaxDamage, MinRange, MaxRange, WeaponSpeed, WeaponType, WeaponMaterial |
| **2063** | Weapon types lookup | WeaponTypeID, NameID, Sharpness |
| **2064** | Weapon materials lookup | WeaponMaterialID, NameID |
| **2016** | Text database | TextID, LanguageID, Content (multilingual strings) |

**Relationships:**
- Category 2003 contains ALL items (weapons, armor, consumables, etc.)
  - `ItemType1 == ?` identifies weapons (need to verify exact value)
- Category 2015 only contains entries for weapon items (subset of 2003)
- Weapon names are in Category 2016 (referenced via `NameID`)
- Weapon types/materials are lookups (2063/2064)

### 1.4 Helper Infrastructure

`SFCategoryManager` provides high-level access:
- `GetTextByLanguage(text_id, lang_id)` - Resolve text references
- `GetItemName(item_id)` - Get item name
- `gamedata.cXXXX` - Direct access to each category instance

Example usage:
```csharp
// Access weapon data
var weaponData = SFCategoryManager.gamedata.c2015;
for (int i = 0; i < weaponData.GetNumOfItems(); i++)
{
    var weapon = weaponData[i];
    ushort itemId = weapon.ItemID;
    string name = SFCategoryManager.GetItemName(itemId);
    // weapon.MinDamage, weapon.MaxDamage, etc.
}
```

### 1.5 Existing Export Mechanisms

**Finding:** ❌ **No existing export functionality**

- Categories only support binary Load/Save to chunk files
- No JSON/CSV/XML serialization infrastructure
- The application can read and display data, but cannot export it

---

## 2. Implementation Options

### Option A: Standalone Console Application (Recommended)
**Pros:**
- Independent of GUI
- Easy to run in batch mode
- Can be used by other tools/scripts
- Simpler testing

**Cons:**
- Separate executable to maintain

### Option B: Integrated Export in Existing Tool
**Pros:**
- Centralized in one application
- Uses existing UI infrastructure
- Direct access to loaded gamedata

**Cons:**
- More complex UI integration
- Requires modifying existing forms

### ✅ **Recommendation:** Start with **Option A**, then optionally add **Option B** later

---

## 3. Proposed Implementation

### 3.1 Standalone Exporter Application

**Project Structure:**
```
SpellforceGameDataExporter/
├── Program.cs                    # Entry point, CLI parsing
├── Exporters/
│   ├── IExporter.cs             # Interface for exporters
│   ├── JSONExporter.cs          # JSON export implementation
│   ├── CSVExporter.cs           # CSV export implementation
│   └── CategoryExporter.cs      # Base exporter logic
├── Models/
│   ├── WeaponData.cs            # Combined weapon data model
│   ├── ItemData.cs              # Combined item data model
│   └── ... (other data models)
└── SpellforceGameDataExporter.csproj
```

**Dependencies:**
- Reference `SFEngine` project (for category access)
- `System.Text.Json` (for JSON serialization)
- `CsvHelper` NuGet package (for CSV export)

### 3.2 Export Format Design

#### JSON Format (Hierarchical)
```json
{
  "weapons": [
    {
      "id": 123,
      "name": "Iron Sword",
      "type": "1H Sword",
      "material": "Iron",
      "damage": {
        "min": 10,
        "max": 15
      },
      "range": {
        "min": 0,
        "max": 1
      },
      "speed": 100,
      "value": {
        "sell": 50,
        "buy": 100
      },
      "stats": {
        "strength": 0,
        "agility": 2,
        "dexterity": 1
        // ... other stats
      },
      "effects": [
        {
          "index": 0,
          "effectId": 456,
          "effectName": "Fire Damage"
        }
      ],
      "ui": {
        "handle": "icon_sword_iron",
        "scaledDown": false
      }
    }
  ]
}
```

#### CSV Format (Flat)
```csv
WeaponID,Name,Type,Material,MinDamage,MaxDamage,MinRange,MaxRange,Speed,SellValue,BuyValue,Strength,Agility,Dexterity,UIHandle
123,Iron Sword,1H Sword,Iron,10,15,0,1,100,50,100,0,2,1,icon_sword_iron
```

**Note:** CSV format will have one row per weapon, with effects in separate CSV or as pipe-delimited values.

### 3.3 Command-Line Interface

```bash
# Export all weapons to JSON
SpellforceGameDataExporter.exe --input "Gamedata.cff" --output "weapons.json" --category weapons --format json

# Export all items to CSV
SpellforceGameDataExporter.exe --input "Gamedata.cff" --output "items.csv" --category items --format csv

# Export specific categories
SpellforceGameDataExporter.exe --input "Gamedata.cff" --output "export/" --category 2015 --format json

# Export all categories (full database dump)
SpellforceGameDataExporter.exe --input "Gamedata.cff" --output "full_export/" --all --format json
```

**CLI Arguments:**
- `--input <path>` - Path to Gamedata.cff file (required)
- `--output <path>` - Output file/directory path (required)
- `--category <name|id>` - Category to export (weapons, items, spells, units, or category ID)
- `--format <json|csv>` - Export format (default: json)
- `--all` - Export all categories
- `--language <id>` - Language ID for text fields (default: 1 = English)

### 3.4 Code Architecture

#### Main Export Flow
```csharp
// Program.cs
1. Parse command-line arguments
2. Load Gamedata.cff using SFCategoryManager
3. Determine export target (category/all)
4. Create appropriate exporter (JSON/CSV)
5. Execute export
6. Save to file
7. Report success/errors
```

#### Category Exporter Base Class
```csharp
public abstract class CategoryExporter
{
    protected SFGameDataNew gamedata;
    protected int languageId;

    public abstract void Export(string outputPath);

    protected string GetText(ushort textId)
    {
        return SFCategoryManager.GetTextByLanguage(textId, languageId);
    }
}
```

#### Weapon Exporter Example
```csharp
public class WeaponExporter : CategoryExporter
{
    public override void Export(string outputPath)
    {
        var weapons = new List<WeaponData>();

        // Iterate through weapon category (2015)
        for (int i = 0; i < gamedata.c2015.GetNumOfItems(); i++)
        {
            var weaponItem = gamedata.c2015[i];
            ushort weaponId = weaponItem.ItemID;

            // Get general item info (category 2003)
            if (!gamedata.c2003.GetItemIndex(weaponId, out int itemIndex))
                continue;
            var generalItem = gamedata.c2003[itemIndex];

            // Build combined weapon data
            var weapon = new WeaponData
            {
                Id = weaponId,
                Name = GetText(generalItem.NameID),
                MinDamage = weaponItem.MinDamage,
                MaxDamage = weaponItem.MaxDamage,
                // ... map all fields
            };

            // Get weapon type name
            if (gamedata.c2063.GetItemIndex(weaponItem.WeaponType, out int typeIndex))
            {
                weapon.Type = GetText(gamedata.c2063[typeIndex].NameID);
            }

            // Get weapon material name
            if (gamedata.c2064.GetItemIndex(weaponItem.WeaponMaterial, out int matIndex))
            {
                weapon.Material = GetText(gamedata.c2064[matIndex].NameID);
            }

            // Get stats (category 2004)
            if (gamedata.c2004.GetItemIndex(weaponId, out int statsIndex))
            {
                var stats = gamedata.c2004[statsIndex];
                weapon.Stats = new ItemStats
                {
                    Strength = stats.Strength,
                    Agility = stats.Agility,
                    // ... map all stat fields
                };
            }

            // Get effects (category 2014 - multiple per item)
            weapon.Effects = new List<WeaponEffect>();
            // Iterate through all items in c2014 with matching ItemID
            // (This is a CategoryBaseMultiple with ItemID + EffectIndex)

            weapons.Add(weapon);
        }

        // Serialize and save
        if (format == ExportFormat.JSON)
        {
            var json = JsonSerializer.Serialize(weapons, jsonOptions);
            File.WriteAllText(outputPath, json);
        }
        else if (format == ExportFormat.CSV)
        {
            // Use CsvHelper to write weapons list
        }
    }
}
```

### 3.5 Data Models

```csharp
// Models/WeaponData.cs
public class WeaponData
{
    public ushort Id { get; set; }
    public string Name { get; set; }
    public string Type { get; set; }
    public string Material { get; set; }
    public ushort MinDamage { get; set; }
    public ushort MaxDamage { get; set; }
    public ushort MinRange { get; set; }
    public ushort MaxRange { get; set; }
    public ushort Speed { get; set; }
    public uint SellValue { get; set; }
    public uint BuyValue { get; set; }
    public ItemStats Stats { get; set; }
    public List<WeaponEffect> Effects { get; set; }
    public WeaponUI UI { get; set; }
}

public class ItemStats
{
    public short Strength { get; set; }
    public short Stamina { get; set; }
    public short Agility { get; set; }
    public short Dexterity { get; set; }
    public short Health { get; set; }
    public short Charisma { get; set; }
    public short Intelligence { get; set; }
    public short Wisdom { get; set; }
    public short Mana { get; set; }
    public short Armor { get; set; }
    public short ResistFire { get; set; }
    public short ResistIce { get; set; }
    public short ResistBlack { get; set; }
    public short ResistMind { get; set; }
    public short SpeedWalk { get; set; }
    public short SpeedFight { get; set; }
    public short SpeedCast { get; set; }
}

public class WeaponEffect
{
    public byte Index { get; set; }
    public ushort EffectId { get; set; }
    public string EffectName { get; set; }
}

public class WeaponUI
{
    public string Handle { get; set; }
    public bool IsScaledDown { get; set; }
}
```

---

## 4. Implementation Steps

### Phase 1: Standalone Exporter Prototype (Basic Weapons Export)
1. ✅ **Create new console application project** in solution
   - Add to `SpellforceDataEditor.sln`
   - Reference `SFEngine` project
   - Add NuGet packages: `System.Text.Json`, `CsvHelper`

2. ✅ **Implement basic CLI parsing**
   - Parse `--input`, `--output`, `--format` arguments
   - Validate input file exists

3. ✅ **Load Gamedata.cff**
   - Use `SFCategoryManager.Set(gamedata)` after loading
   - Handle loading errors gracefully

4. ✅ **Implement WeaponExporter**
   - Create `WeaponData` model class
   - Implement JSON serialization
   - Combine data from categories 2003, 2015, 2063, 2064, 2004

5. ✅ **Test with actual Gamedata.cff**
   - Verify all weapon data is exported correctly
   - Check name resolution works
   - Validate JSON structure

### Phase 2: Expand Export Categories
6. ✅ **Add CSV export support**
   - Implement `CSVExporter` class
   - Handle multi-value fields (effects)

7. ✅ **Add more exporters**
   - Items (all items, not just weapons)
   - Spells (Category 2002, 2054)
   - Units (Category 2024, 2005)
   - Buildings (Category 2029)

8. ✅ **Implement `--all` option**
   - Export all categories to separate files
   - Generate index/manifest file

### Phase 3: Integration into Main Application (Optional)
9. ✅ **Add Export menu to SpelllforceCFFEditor**
   - Create export dialog form
   - Add "Export Category..." menu item
   - Reuse exporter classes from standalone app

10. ✅ **Add export buttons to category controls**
    - Each Control1-Control49 gets an "Export" button
    - Exports currently displayed category

---

## 5. Testing Plan

### Unit Tests
- ✅ Category data loading
- ✅ Text resolution
- ✅ Cross-category lookups (weapon type, material)
- ✅ JSON serialization/deserialization
- ✅ CSV formatting

### Integration Tests
- ✅ Full weapon export with real Gamedata.cff
- ✅ Verify exported data matches in-game values
- ✅ Test with different languages
- ✅ Test with modded Gamedata.cff files

### Manual Testing Checklist
- [ ] Export weapons to JSON
- [ ] Export weapons to CSV
- [ ] Verify weapon names are correct
- [ ] Verify weapon stats match game
- [ ] Verify damage values are correct
- [ ] Verify weapon types/materials resolve correctly
- [ ] Test with missing data (graceful handling)

---

## 6. Future Enhancements

### Advanced Export Features
- **Filtering:** Export only specific weapon types or ID ranges
- **Relationships:** Export related data (e.g., spells with their spell lines)
- **Localization:** Export all languages simultaneously
- **Diff Export:** Export only differences between two Gamedata.cff files
- **Import:** Allow importing from JSON/CSV back to Gamedata.cff

### Performance Optimization
- **Parallel Processing:** Export multiple categories concurrently
- **Streaming:** For very large datasets
- **Caching:** Cache text lookups

### Additional Formats
- **XML:** For compatibility with other tools
- **SQLite:** For queryable database export
- **Excel:** Direct XLSX export

---

## 7. Technical Considerations

### Category Identification
**Question:** How to identify weapon items in Category 2003?
- **Approach 1:** Items present in Category 2015 are weapons
- **Approach 2:** Check `ItemType1` or `ItemType2` fields
- **Recommendation:** Use Approach 1 (iterate c2015, lookup in c2003)

### Multi-value Fields
Some items have multiple entries in certain categories:
- Category 2014 (weapon effects): Multiple effects per weapon
- Category 2012 (UI data): Multiple UI representations

**Solution:** Use `CategoryBaseMultiple.GetItemSubItemIndex()` to find all entries for a given ItemID

### Text Encoding
Category 2016 text content uses **Windows-1252 encoding** (fixed byte arrays).
- Already handled in existing code via `Encoding.GetEncoding(1252)`

### Error Handling
**Missing Data Scenarios:**
- Item has no name (NameID = 0 or missing in c2016)
- Weapon type/material not found in lookup tables
- Stats data missing for an item

**Strategy:**
- Use fallback values (e.g., "Unknown", 0, null)
- Log warnings to console
- Continue export (don't fail entire export for one bad item)

---

## 8. Estimated Effort

| Task | Effort | Priority |
|------|--------|----------|
| Phase 1: Basic weapon exporter | 4-6 hours | **High** |
| Phase 2: Multi-category export | 3-4 hours | Medium |
| Phase 3: GUI integration | 2-3 hours | Low |
| Testing & refinement | 2-3 hours | High |
| **Total** | **11-16 hours** | |

---

## 9. Deliverables

### Minimum Viable Product (MVP)
1. ✅ Standalone console application
2. ✅ Export weapons to JSON
3. ✅ Export weapons to CSV
4. ✅ Command-line interface
5. ✅ Documentation (README)

### Full Feature Set
6. ✅ Export all major categories (items, spells, units, buildings)
7. ✅ GUI integration in main application
8. ✅ Multiple language support
9. ✅ Comprehensive testing

---

## 10. Next Steps

1. **Create new console application project** (`SpellforceGameDataExporter`)
2. **Set up project structure** (folders, references)
3. **Implement basic CLI and Gamedata loading**
4. **Build WeaponData model and WeaponExporter**
5. **Test with real Gamedata.cff file**
6. **Iterate based on findings**

---

## Appendix: Category Reference

**Full list of categories and their purposes** (for future export implementation):

| ID | Name | Description |
|----|------|-------------|
| 2001 | Abilities | Character abilities |
| 2002 | Effects | Spell effects |
| 2003 | Items (general) | Item metadata |
| 2004 | Items (stats) | Item stat bonuses |
| 2005 | Unit stats | Unit statistics |
| 2006 | Unit data | Unit metadata |
| 2012 | Item UI | Item icons and UI |
| 2013 | Spell scrolls | Spell scroll links |
| 2014 | Weapon effects | Weapon-triggered effects |
| 2015 | Weapon data | Weapon combat stats |
| 2016 | Text | Multilingual text database |
| 2017 | Item descriptions | Item description text IDs |
| 2018 | Item requirements | Item equip requirements |
| 2022 | Races | Race definitions |
| 2023 | Race data | Race stats and bonuses |
| 2024 | Units | Unit definitions |
| 2025 | Unit equipment | Unit starting equipment |
| 2026 | Unit spells | Unit starting spells |
| 2028 | Unit requirements | Unit build requirements |
| 2029 | Buildings | Building definitions |
| 2030 | Building stats | Building HP and armor |
| 2031 | Building costs | Building resource costs |
| 2039 | Skills | Skill definitions |
| 2040 | Interactables | Interactive objects |
| 2041 | Merchants | Merchant definitions |
| 2042 | Merchant inventory | Items sold by merchants |
| 2047 | Spell lines | Spell progression lines |
| 2050 | Objects | Map object definitions |
| 2054 | Spell line data | Spell line metadata |
| 2056 | Spell requirements | Spell learning requirements |
| 2063 | Weapon types | Weapon type lookup |
| 2064 | Weapon materials | Weapon material lookup |
| ... | ... | (and more) |

---

**End of Plan**
