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

---

## 11. IMPORT/BI-DIRECTIONAL CONVERSION STRATEGY

**Updated:** 2025-10-18
**Goal:** Enable importing JSON/CSV data back into GameData.cff format for creating custom weapons, items, and game data.

### 11.1 Import Architecture

#### Import Flow
```
JSON/CSV Files
    ↓
Parse & Validate
    ↓
Resolve Foreign Keys
    ↓
Create Category Structs
    ↓
Build SFGameDataNew
    ↓
Save to GameData.cff
```

#### Key Challenges

1. **Foreign Key Validation**
   - All NameID/TextID references must exist in Category 2016
   - Item references must exist in Category 2003
   - Spell references must exist in Category 2002
   - Unit references must exist in Category 2024/2005
   - etc.

2. **ID Assignment**
   - New items need unique IDs that don't conflict with existing data
   - Auto-increment from highest existing ID, or
   - Allow user to specify ID ranges

3. **Multi-Valued Categories**
   - JSON arrays → multiple sub-items in CategoryBaseMultiple
   - Must generate correct sub-IDs (EquipmentIndex, EffectIndex, etc.)

4. **Dependency Resolution**
   - Import order matters (see Section 11.3)
   - Circular dependencies (Items ← → Units)
   - Missing dependencies must be created or error

5. **Data Validation**
   - Type checking (ushort ranges, byte limits)
   - Required fields
   - Valid enum values
   - Text encoding (Windows-1252, 1250, 1251)

6. **Encoding Issues**
   - Category 2016 text uses legacy encodings
   - Fixed-size byte arrays (50, 512 chars)
   - Null-terminated strings

---

### 11.2 Import Data Models

#### JSON Input Format for Weapons

```json
{
  "weapons": [
    {
      "id": null,  // null = auto-assign
      "name": {
        "english": "Legendary Sword of Doom",
        "german": "Legendäres Schwert des Untergangs",
        "russian": "Легендарный Меч Гибели"
      },
      "type": "1H Sword",  // lookup by name in Category 2063
      "material": "Adamantium",  // lookup by name in Category 2064
      "damage": {
        "min": 50,
        "max": 75
      },
      "range": {
        "min": 0,
        "max": 1
      },
      "speed": 120,
      "value": {
        "sell": 5000,
        "buy": 10000
      },
      "stats": {  // optional
        "strength": 5,
        "agility": 3,
        "resistFire": 10
      },
      "effects": [  // optional
        {
          "effectName": "Fire Damage",  // lookup by spell name
          "effectId": null  // or specify ID directly
        }
      ],
      "requirements": [  // optional
        {
          "skillMajor": "Sword Mastery",
          "skillMinor": "One-Handed",
          "level": 10
        }
      ],
      "ui": {  // optional
        "handle": "icon_sword_legendary",
        "scaledDown": false
      }
    }
  ]
}
```

#### CSV Input Format for Weapons

```csv
WeaponID,Name_EN,Name_DE,Name_RU,Type,Material,MinDamage,MaxDamage,MinRange,MaxRange,Speed,SellValue,BuyValue,Strength,Agility,UIHandle
,Legendary Sword of Doom,Legendäres Schwert des Untergangs,Легендарный Меч Гибели,1H Sword,Adamantium,50,75,0,1,120,5000,10000,5,3,icon_sword_legendary
```

**Note:** CSV format is more limited - cannot handle multi-valued fields (effects, requirements) easily.

---

### 11.3 Import Dependency Order

To safely import custom data, categories must be imported in dependency order:

**Phase 1: Foundational Data**
1. ✅ **Category 2016** - Text entries (names, descriptions)
   - Create text entries for all custom item names
   - Generate unique TextIDs

**Phase 2: Lookup Tables**
2. ✅ **Category 2063** - Weapon types (if creating new type)
3. ✅ **Category 2064** - Weapon materials (if creating new material)
4. ✅ **Category 2039** - Skills (if creating new skill requirements)
5. ✅ **Category 2054** - Spell lines (if creating new spell lines)

**Phase 3: Core Entities**
6. ✅ **Category 2002** - Spells (if weapon effects reference new spells)
7. ✅ **Category 2003** - Items (base item entries)

**Phase 4: Item Extensions**
8. ✅ **Category 2015** - Weapon data (for weapons from 2003)
9. ✅ **Category 2004** - Item stats (optional, for items with bonuses)
10. ✅ **Category 2012** - Item UI (optional, for custom icons)
11. ✅ **Category 2014** - Weapon effects (optional, for magical weapons)
12. ✅ **Category 2017** - Item requirements (optional, for skill-locked items)

---

### 11.4 Import Implementation

#### Importer Architecture

```csharp
public class GameDataImporter
{
    private SFGameDataNew gamedata;
    private Dictionary<string, ushort> textIdMap;  // name → TextID
    private Dictionary<string, ushort> weaponTypeMap;  // type name → TypeID
    private Dictionary<string, ushort> weaponMaterialMap;  // material name → MaterialID
    private ushort nextItemId;
    private ushort nextTextId;

    public GameDataImporter(SFGameDataNew existingGameData)
    {
        gamedata = existingGameData;
        BuildLookupMaps();
    }

    public void ImportWeapons(string jsonPath)
    {
        // 1. Parse JSON
        var weaponsJson = File.ReadAllText(jsonPath);
        var weapons = JsonSerializer.Deserialize<List<WeaponData>>(weaponsJson);

        // 2. Validate and assign IDs
        foreach (var weapon in weapons)
        {
            if (weapon.Id == null)
            {
                weapon.Id = nextItemId++;
            }
            ValidateWeapon(weapon);
        }

        // 3. Create text entries (Category 2016)
        foreach (var weapon in weapons)
        {
            CreateTextEntries(weapon);
        }

        // 4. Create lookup entries if needed (Categories 2063, 2064)
        foreach (var weapon in weapons)
        {
            EnsureWeaponTypExists(weapon.Type);
            EnsureWeaponMaterialExists(weapon.Material);
        }

        // 5. Create item entries (Category 2003)
        foreach (var weapon in weapons)
        {
            CreateItemEntry(weapon);
        }

        // 6. Create weapon data (Category 2015)
        foreach (var weapon in weapons)
        {
            CreateWeaponDataEntry(weapon);
        }

        // 7. Create optional extensions
        foreach (var weapon in weapons)
        {
            if (weapon.Stats != null)
                CreateItemStatsEntry(weapon);
            if (weapon.Effects != null && weapon.Effects.Count > 0)
                CreateWeaponEffects(weapon);
            if (weapon.Requirements != null && weapon.Requirements.Count > 0)
                CreateItemRequirements(weapon);
            if (weapon.UI != null)
                CreateItemUIEntry(weapon);
        }
    }

    private void CreateTextEntries(WeaponData weapon)
    {
        ushort textId = nextTextId++;

        // English
        var enText = new Category2016Item();
        enText.TextID = textId;
        enText.LanguageID = 0;  // English
        SetTextContent(enText, weapon.Name.English);
        gamedata.c2016.AddSubItem(..., enText);

        // German (if provided)
        if (!string.IsNullOrEmpty(weapon.Name.German))
        {
            var deText = new Category2016Item();
            deText.TextID = textId;
            deText.LanguageID = 1;  // German
            SetTextContent(deText, weapon.Name.German);
            gamedata.c2016.AddSubItem(..., deText);
        }

        // Russian (if provided)
        if (!string.IsNullOrEmpty(weapon.Name.Russian))
        {
            var ruText = new Category2016Item();
            ruText.TextID = textId;
            ruText.LanguageID = 5;  // Russian
            SetTextContent(ruText, weapon.Name.Russian, Encoding.GetEncoding(1251));
            gamedata.c2016.AddSubItem(..., ruText);
        }

        textIdMap[weapon.Name.English] = textId;
    }

    private unsafe void SetTextContent(Category2016Item item, string text, Encoding encoding = null)
    {
        if (encoding == null)
            encoding = Encoding.GetEncoding(1252);

        byte[] bytes = encoding.GetBytes(text);
        if (bytes.Length > 512)
            throw new Exception($"Text content too long: {text}");

        fixed (byte* dest = item.Content)
        {
            for (int i = 0; i < bytes.Length; i++)
                dest[i] = bytes[i];
            // Null-terminate
            if (bytes.Length < 512)
                dest[bytes.Length] = 0;
        }
    }

    private void CreateItemEntry(WeaponData weapon)
    {
        var item = new Category2003Item();
        item.ItemID = weapon.Id.Value;
        item.ItemType1 = 1;  // Weapon type (verify correct value)
        item.ItemType2 = 0;
        item.NameID = textIdMap[weapon.Name.English];
        item.SellValue = weapon.Value.Sell;
        item.BuyValue = weapon.Value.Buy;
        // ... other fields

        gamedata.c2003.AddItem(..., item);
    }

    private void CreateWeaponDataEntry(WeaponData weapon)
    {
        var weaponData = new Category2015Item();
        weaponData.ItemID = weapon.Id.Value;
        weaponData.MinDamage = weapon.Damage.Min;
        weaponData.MaxDamage = weapon.Damage.Max;
        weaponData.MinRange = weapon.Range.Min;
        weaponData.MaxRange = weapon.Range.Max;
        weaponData.WeaponSpeed = weapon.Speed;
        weaponData.WeaponType = weaponTypeMap[weapon.Type];
        weaponData.WeaponMaterial = weaponMaterialMap[weapon.Material];

        gamedata.c2015.AddItem(..., weaponData);
    }

    private void CreateWeaponEffects(WeaponData weapon)
    {
        for (byte i = 0; i < weapon.Effects.Count; i++)
        {
            var effect = weapon.Effects[i];
            var effectItem = new Category2014Item();
            effectItem.ItemID = weapon.Id.Value;
            effectItem.EffectIndex = i;
            effectItem.EffectID = ResolveSpellId(effect.EffectName);

            gamedata.c2014.AddSubItem(..., effectItem);
        }
    }
}
```

---

### 11.5 Validation Rules

#### ID Validation
- `ushort` range: 0-65535
- `byte` range: 0-255
- IDs must be unique within category
- Cannot use ID 0 (reserved/invalid in many contexts)

#### Text Validation
- Name must not be empty
- Text content ≤ 512 bytes (after encoding)
- Handle strings ≤ 50 bytes (after encoding)
- Valid encoding for language

#### Weapon Validation
- MinDamage ≤ MaxDamage
- MinRange ≤ MaxRange
- Speed > 0
- Valid weapon type (exists in 2063 or will be created)
- Valid material (exists in 2064 or will be created)

#### Foreign Key Validation
- All referenced TextIDs must exist
- All referenced weapon types must exist
- All referenced materials must exist
- All referenced effect/spell IDs must exist

---

### 11.6 Conflict Resolution Strategies

#### Strategy 1: Merge Mode
- Import data merges with existing GameData
- New IDs assigned automatically
- Existing items untouched
- **Use case:** Adding new weapons to existing game

#### Strategy 2: Replace Mode
- Import data replaces specific category
- Can overwrite existing items with same ID
- **Use case:** Modifying existing weapons

#### Strategy 3: ID Range Reservation
- Reserve ID ranges for custom content (e.g., 50000-60000)
- Prevents conflicts with base game content
- **Use case:** Large mods with many custom items

---

### 11.7 Error Handling

#### Validation Errors
- Report all validation errors before import
- Don't partially import (all-or-nothing)
- Generate detailed error report:
  ```
  Error: Weapon "Legendary Sword of Doom"
  - MinDamage (100) exceeds MaxDamage (75)
  - Weapon type "Triple-Bladed Axe" does not exist
  - Effect "Super Fire" references non-existent spell ID
  ```

#### Missing Dependencies
- Option 1: **Fail fast** - abort import if dependencies missing
- Option 2: **Auto-create** - create stub entries for missing lookups
- Option 3: **Interactive** - prompt user to provide missing data

#### ID Conflicts
- Detect ID conflicts before import
- Options:
  - Auto-reassign conflicting IDs
  - Prompt user to resolve
  - Abort import

---

### 11.8 Testing Strategy

#### Unit Tests
- Text encoding/decoding
- ID assignment
- Foreign key resolution
- Multi-valued field handling

#### Integration Tests
- Import weapon → export → verify JSON matches
- Import weapon → save GameData.cff → load in game
- Import with missing dependencies
- Import with ID conflicts
- Import multi-language text

#### Test Data Sets
- **Minimal Weapon** - Only required fields
- **Full Weapon** - All optional fields populated
- **Multi-Effect Weapon** - Multiple effects
- **High-Requirement Weapon** - Multiple skill requirements
- **Invalid Weapon** - Various validation failures

---

### 11.9 CLI Interface for Import

```bash
# Import weapons from JSON (merge mode)
SpellforceGameDataExporter.exe --import "custom_weapons.json" --gamedata "Gamedata.cff" --output "Gamedata_modified.cff" --mode merge

# Import weapons with ID range reservation
SpellforceGameDataExporter.exe --import "custom_weapons.json" --gamedata "Gamedata.cff" --output "Gamedata_modified.cff" --id-range 50000-60000

# Validate without importing
SpellforceGameDataExporter.exe --validate "custom_weapons.json" --gamedata "Gamedata.cff"

# Import with dependency auto-creation
SpellforceGameDataExporter.exe --import "custom_weapons.json" --gamedata "Gamedata.cff" --output "Gamedata_modified.cff" --auto-create-deps

# Interactive import (prompts for missing dependencies)
SpellforceGameDataExporter.exe --import "custom_weapons.json" --gamedata "Gamedata.cff" --output "Gamedata_modified.cff" --interactive
```

---

### 11.10 GUI Integration for Import

**SpelllforceCFFEditor** menu additions:
- **File → Import → Weapons from JSON...**
- **File → Import → Items from JSON...**
- **File → Import → Units from JSON...**
- **File → Import → Spells from JSON...**

**Import Dialog:**
- File selector (JSON/CSV)
- Mode selection (merge/replace)
- ID assignment strategy
- Dependency handling options
- Validation results preview
- Conflict resolution UI

---

### 11.11 Round-Trip Testing

**Goal:** Ensure export → import → export produces identical data

**Test Process:**
1. Export weapons from vanilla GameData.cff to JSON
2. Import the exported JSON into a new GameData.cff
3. Export weapons again from new GameData.cff
4. Compare JSON files - should be identical (allowing for formatting)

**Potential Issues:**
- Floating-point precision
- Text encoding inconsistencies
- Field ordering
- Default value handling

---

### 11.12 Advanced Import Features

#### Batch Import
- Import multiple JSON files in sequence
- Combine weapons, armor, items into one GameData

#### Template System
- Define weapon templates (e.g., "Iron Weapon", "Legendary Weapon")
- Inherit properties from templates
- Override specific fields

```json
{
  "templates": {
    "IronWeapon": {
      "material": "Iron",
      "value": { "sell": 50, "buy": 100 }
    }
  },
  "weapons": [
    {
      "template": "IronWeapon",
      "name": "Iron Sword",
      "type": "1H Sword",
      "damage": { "min": 10, "max": 15 }
    }
  ]
}
```

#### Scripted Generation
- Use C# scripting to generate items programmatically
- Useful for creating item sets, progression curves

```csharp
// Generate 10 iron swords with increasing damage
for (int i = 1; i <= 10; i++)
{
    var weapon = new WeaponData {
        Name = $"Iron Sword +{i}",
        Damage = { Min = 10 + i*2, Max = 15 + i*2 },
        // ...
    };
    importer.ImportWeapon(weapon);
}
```

---

### 11.13 Import Implementation Phases

**Phase 1: Weapon Import (MVP)**
- Import JSON → GameData.cff
- Categories: 2003, 2015, 2016, 2063, 2064
- Basic validation
- Merge mode only

**Phase 2: Extended Weapon Import**
- Add Categories: 2004, 2012, 2014, 2017
- Multi-valued fields (effects, requirements)
- CSV support

**Phase 3: Other Entity Types**
- Units (2024, 2005, 2025, 2026)
- Spells (2002, 2054)
- Buildings (2029, 2030, 2031)

**Phase 4: Advanced Features**
- Replace mode
- ID range reservation
- Template system
- Batch import
- GUI integration

---

### 11.14 Import Deliverables

1. ✅ `GameDataImporter.cs` - Core importer class
2. ✅ `WeaponImporter.cs` - Weapon-specific importer
3. ✅ `ForeignKeyResolver.cs` - Dependency resolution
4. ✅ `ValidationEngine.cs` - Data validation
5. ✅ CLI argument parsing for `--import`
6. ✅ Import dialog form (GUI)
7. ✅ Documentation - Import JSON schema
8. ✅ Unit tests
9. ✅ Integration tests
10. ✅ Example JSON files

---

### 11.15 Import Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Corrupt existing GameData | **CRITICAL** | Always backup original, validate before save |
| ID conflicts | High | Auto-detect conflicts, provide resolution options |
| Missing dependencies | Medium | Validate before import, auto-create option |
| Invalid data types | Medium | Strong validation, type checking |
| Encoding issues | Low | Test with all language sets, proper encoding handling |
| Game crashes from bad data | **CRITICAL** | Extensive testing, validate against game constraints |

---

### 11.16 Next Steps for Import

1. **Implement basic weapon importer** (Category 2003, 2015, 2016)
2. **Create validation framework**
3. **Test with simple weapon import**
4. **Load modified GameData in actual game** - verify it works!
5. **Extend to multi-valued categories** (effects, requirements)
6. **Add GUI dialog**
7. **Implement other entity importers**

---

## 12. ASSET INTEGRATION & RELATIONAL DATABASE STRATEGY

**Updated:** 2025-10-18
**Goal:** Include all asset references (icons, models, textures, sounds) in the export and design a comprehensive relational database where all relationships can be queried.

---

### 12.1 Asset System Architecture Analysis

#### PAK File System Overview

SpellForce stores all game assets in numbered PAK archives with **priority loading** (higher numbers override lower):

**Asset Type → PAK File Mapping:**

| Asset Type | File Extensions | PAK Files | Resource Path |
|------------|----------------|-----------|---------------|
| **Textures** | `.dds`, `.tga` | sf0, sf1, sf22, sf25, sf32, sf35 | `texture/` |
| **3D Models** | `.msb` | sf8, sf22, sf32 | `mesh/` |
| **Animations** | `.bob` | sf5, sf22, sf32 | `animation/` |
| **Skeletons** | `.bor` | sf4, sf22, sf32 | `animation/` |
| **Skins** | `.msb` | sf8, sf22, sf32 | `skinning/b20/` |
| **Bone Indices** | `.bsi` | sf8, sf22, sf32 | `skinning/b20/` |
| **Music** | `.mp3` | sf3, sf20, sf30 | `sound/` |
| **Sound Effects** | `.wav` | sf2, sf20, sf30 | `sound/` |
| **Speech (Battle)** | `.wav` | sf2, sf23, sf33 | `sound/speech/battle/` |
| **Speech (NPC)** | `.mp3` | sf10, sf20, sf23, sf33 | `sound/speech/` |
| **Speech (Player)** | `.mp3` | sf10, sf23, sf33 | `sound/speech/male/`, `sound/speech/female/` |

**Access Methods:**
- `SFUnPak.LoadFileFind(filename, pakfiles)` - Load asset by name from PAK
- `SFResourceManager.<Type>.Get(name)` - Load and cache typed resources
- `SFUnPak.ListAllWithExtension(path, ext, pak_filter)` - List all assets of type

---

### 12.2 Asset References in CFF Categories

#### Item/Weapon Assets

| Category | Field Name | Asset Type | Resolution Method |
|----------|------------|------------|-------------------|
| **2012** | `UIHandle` (64 bytes) | **Icon texture** | `texture/ui/` + UIHandle + `.tga` or `.dds` |
| **2024** | `Handle` (40 bytes) | **Unit 3D model** | `mesh/` + Handle + `.msb` |
| **2050** | `Handle` (40 bytes) | **Object 3D model** | `mesh/` + Handle + `.msb` |
| **2054** | `UIHandle` (40 bytes) | **Spell icon** | `texture/ui/` + UIHandle + `.tga` or `.dds` |

**Icon Naming Conventions:**
- Item icons: `figure_item_<type>_<name>` (e.g., `figure_item_sword_iron`)
- Spell icons: `figure_spell_<school>_<name>` (e.g., `figure_spell_fire_fireball`)
- UI icons: `ui_<category>_<name>` (e.g., `ui_button_attack`)

**3D Model Handles:**
- Units: `figure_<race>_<type>` (e.g., `figure_human_warrior`)
- Objects: `object_<category>_<name>` (e.g., `object_building_tower`)
- Weapons: Not directly stored; visual is part of unit equipment rendering

---

### 12.3 Complete Entity Relationship Map

#### Core Entity Types

```
┌─────────────────────────────────────────────────────────────┐
│                       GAME DATABASE                         │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    ITEMS     │◄───►│    WEAPONS   │     │    ARMOR     │
│  (Cat 2003)  │     │  (Cat 2015)  │     │  (Cat 2004)  │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │ NameID             │ ItemID             │ ItemID
       ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────┐
│                    TEXT DATABASE                         │
│                    (Category 2016)                       │
│  TextID + LanguageID → Localized String                 │
└──────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   ITEM UI    │     │ WEAPON TYPES │     │  MATERIALS   │
│  (Cat 2012)  │     │  (Cat 2063)  │     │  (Cat 2064)  │
│  UIHandle ───┼────►│   (Icons)    │     │   (Lookup)   │
└──────────────┘     └──────────────┘     └──────────────┘
       │
       │ UIHandle
       ▼
┌──────────────────────────────────────────────────────────┐
│                  TEXTURE ASSETS (PAK)                    │
│          texture/ui/<UIHandle>.tga or .dds              │
└──────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ WEAPON EFFECTS│    │    SPELLS    │     │  SPELL LINES │
│  (Cat 2014)  │────►│  (Cat 2002)  │◄────│  (Cat 2047)  │
│  EffectID    │     │   SpellID    │     │ SpellLineID  │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                            │ UIHandle
                            ▼
                     ┌──────────────┐
                     │  SPELL UI    │
                     │  (Cat 2054)  │
                     │  (Icons)     │
                     └──────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    UNITS     │◄───►│  UNIT STATS  │     │ UNIT EQUIP   │
│  (Cat 2024)  │     │  (Cat 2005)  │     │  (Cat 2025)  │
│   Handle ────┼─┐   │              │◄────│  ItemID      │
└──────────────┘ │   └──────────────┘     └──────────────┘
                 │
                 │ Handle
                 ▼
        ┌──────────────────────────────────────┐
        │      3D MODEL ASSETS (PAK)          │
        │    mesh/<Handle>.msb + .bor         │
        └──────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  BUILDINGS   │     │BUILDING STATS│     │BUILDING COSTS│
│  (Cat 2029)  │────►│  (Cat 2030)  │     │  (Cat 2031)  │
│              │     │              │     │ ResourceType │
└──────────────┘     └──────────────┘     └──────────────┘

┌──────────────┐     ┌──────────────┐
│  MERCHANTS   │────►│ MERCHANT INV │
│  (Cat 2041)  │     │  (Cat 2042)  │
│              │     │   ItemID ────┼───► ITEMS (2003)
└──────────────┘     └──────────────┘

┌──────────────┐     ┌──────────────┐
│    RACES     │────►│  RACE DATA   │
│  (Cat 2022)  │     │  (Cat 2023)  │
│              │     │  (Bonuses)   │
└──────────────┘     └──────────────┘

┌──────────────┐
│   OBJECTS    │
│  (Cat 2050)  │
│  Handle ─────┼───► 3D MODELS (PAK)
└──────────────┘
```

---

### 12.4 Relational Database Schema Design

#### Database Technology Options

**Option A: SQLite** (Recommended for MVP)
- **Pros:** Serverless, portable, single file, fast queries, full SQL support
- **Cons:** Single writer (fine for export use case)
- **Use Case:** Export GameData.cff → single `.sqlite` database file

**Option B: PostgreSQL / MySQL**
- **Pros:** Multi-user, advanced queries, materialized views
- **Cons:** Requires server setup, more complex
- **Use Case:** Central mod database, web API backend

**Option C: JSON + Search Index**
- **Pros:** Human-readable, easy to version control
- **Cons:** Slower queries, no native JOIN operations
- **Use Case:** Documentation, wiki generation

**Recommendation:** **SQLite for local use** + **JSON for sharing/documentation**

---

#### Schema Design (SQL DDL)

```sql
-- ============================================================
-- TEXT DATABASE (multilingual strings)
-- ============================================================
CREATE TABLE texts (
    text_id INTEGER NOT NULL,
    language_id INTEGER NOT NULL,
    language_name TEXT,
    content TEXT NOT NULL,
    PRIMARY KEY (text_id, language_id)
);

CREATE INDEX idx_texts_content ON texts(content);

-- ============================================================
-- ITEMS (base item data)
-- ============================================================
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY,
    name_text_id INTEGER,
    item_type_1 INTEGER,
    item_type_2 INTEGER,
    sell_value INTEGER,
    buy_value INTEGER,
    item_set_id INTEGER,
    -- Add all fields from Category2003
    FOREIGN KEY (name_text_id) REFERENCES texts(text_id)
);

CREATE TABLE item_names (
    item_id INTEGER NOT NULL,
    language_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (item_id, language_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

CREATE INDEX idx_items_type ON items(item_type_1, item_type_2);

-- ============================================================
-- WEAPON DATA
-- ============================================================
CREATE TABLE weapon_types (
    weapon_type_id INTEGER PRIMARY KEY,
    name_text_id INTEGER,
    sharpness INTEGER,
    FOREIGN KEY (name_text_id) REFERENCES texts(text_id)
);

CREATE TABLE weapon_materials (
    material_id INTEGER PRIMARY KEY,
    name_text_id INTEGER,
    FOREIGN KEY (name_text_id) REFERENCES texts(text_id)
);

CREATE TABLE weapons (
    item_id INTEGER PRIMARY KEY,
    min_damage INTEGER,
    max_damage INTEGER,
    min_range INTEGER,
    max_range INTEGER,
    weapon_speed INTEGER,
    weapon_type_id INTEGER,
    weapon_material_id INTEGER,
    FOREIGN KEY (item_id) REFERENCES items(item_id),
    FOREIGN KEY (weapon_type_id) REFERENCES weapon_types(weapon_type_id),
    FOREIGN KEY (weapon_material_id) REFERENCES weapon_materials(material_id)
);

-- ============================================================
-- ITEM STATS (bonuses)
-- ============================================================
CREATE TABLE item_stats (
    item_id INTEGER PRIMARY KEY,
    strength INTEGER DEFAULT 0,
    stamina INTEGER DEFAULT 0,
    agility INTEGER DEFAULT 0,
    dexterity INTEGER DEFAULT 0,
    health INTEGER DEFAULT 0,
    charisma INTEGER DEFAULT 0,
    intelligence INTEGER DEFAULT 0,
    wisdom INTEGER DEFAULT 0,
    mana INTEGER DEFAULT 0,
    armor INTEGER DEFAULT 0,
    resist_fire INTEGER DEFAULT 0,
    resist_ice INTEGER DEFAULT 0,
    resist_black INTEGER DEFAULT 0,
    resist_mind INTEGER DEFAULT 0,
    speed_walk INTEGER DEFAULT 0,
    speed_fight INTEGER DEFAULT 0,
    speed_cast INTEGER DEFAULT 0,
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

-- ============================================================
-- ITEM UI (icons, visuals)
-- ============================================================
CREATE TABLE item_ui (
    item_id INTEGER NOT NULL,
    ui_index INTEGER NOT NULL,
    ui_handle TEXT NOT NULL,
    is_scaled_down BOOLEAN,
    icon_path TEXT,  -- Resolved: texture/ui/<ui_handle>.tga
    PRIMARY KEY (item_id, ui_index),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

CREATE INDEX idx_item_ui_handle ON item_ui(ui_handle);

-- ============================================================
-- WEAPON EFFECTS
-- ============================================================
CREATE TABLE weapon_effects (
    item_id INTEGER NOT NULL,
    effect_index INTEGER NOT NULL,
    effect_id INTEGER NOT NULL,
    effect_name TEXT,
    PRIMARY KEY (item_id, effect_index),
    FOREIGN KEY (item_id) REFERENCES weapons(item_id),
    FOREIGN KEY (effect_id) REFERENCES spells(spell_id)
);

-- ============================================================
-- SPELLS
-- ============================================================
CREATE TABLE spells (
    spell_id INTEGER PRIMARY KEY,
    name_text_id INTEGER,
    spell_line_id INTEGER,
    mana_cost INTEGER,
    cast_time INTEGER,
    cooldown INTEGER,
    -- Add all fields from Category2002
    FOREIGN KEY (name_text_id) REFERENCES texts(text_id),
    FOREIGN KEY (spell_line_id) REFERENCES spell_lines(spell_line_id)
);

CREATE TABLE spell_lines (
    spell_line_id INTEGER PRIMARY KEY,
    name_text_id INTEGER,
    ui_handle TEXT,
    icon_path TEXT,
    FOREIGN KEY (name_text_id) REFERENCES texts(text_id)
);

CREATE TABLE spell_ui (
    spell_line_id INTEGER PRIMARY KEY,
    ui_handle TEXT,
    icon_path TEXT,  -- Resolved: texture/ui/<ui_handle>.tga
    FOREIGN KEY (spell_line_id) REFERENCES spell_lines(spell_line_id)
);

-- ============================================================
-- UNITS
-- ============================================================
CREATE TABLE units (
    unit_id INTEGER PRIMARY KEY,
    name_text_id INTEGER,
    stats_id INTEGER,
    handle TEXT NOT NULL,
    experience_gain INTEGER,
    copper_loot INTEGER,
    armor INTEGER,
    model_path TEXT,  -- Resolved: mesh/<handle>.msb
    FOREIGN KEY (name_text_id) REFERENCES texts(text_id),
    FOREIGN KEY (stats_id) REFERENCES unit_stats(stats_id)
);

CREATE TABLE unit_stats (
    stats_id INTEGER PRIMARY KEY,
    health INTEGER,
    mana INTEGER,
    strength INTEGER,
    agility INTEGER,
    -- Add all stat fields from Category2005
);

CREATE TABLE unit_equipment (
    unit_id INTEGER NOT NULL,
    equipment_index INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    PRIMARY KEY (unit_id, equipment_index),
    FOREIGN KEY (unit_id) REFERENCES units(unit_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

CREATE TABLE unit_spells (
    unit_id INTEGER NOT NULL,
    spell_index INTEGER NOT NULL,
    spell_id INTEGER NOT NULL,
    PRIMARY KEY (unit_id, spell_index),
    FOREIGN KEY (unit_id) REFERENCES units(unit_id),
    FOREIGN KEY (spell_id) REFERENCES spells(spell_id)
);

-- ============================================================
-- BUILDINGS
-- ============================================================
CREATE TABLE buildings (
    building_id INTEGER PRIMARY KEY,
    name_text_id INTEGER,
    -- Add fields from Category2029
    FOREIGN KEY (name_text_id) REFERENCES texts(text_id)
);

CREATE TABLE building_costs (
    building_id INTEGER NOT NULL,
    cost_index INTEGER NOT NULL,
    resource_type INTEGER,
    resource_amount INTEGER,
    PRIMARY KEY (building_id, cost_index),
    FOREIGN KEY (building_id) REFERENCES buildings(building_id)
);

-- ============================================================
-- MERCHANTS
-- ============================================================
CREATE TABLE merchants (
    merchant_id INTEGER PRIMARY KEY,
    name_text_id INTEGER,
    FOREIGN KEY (name_text_id) REFERENCES texts(text_id)
);

CREATE TABLE merchant_inventory (
    merchant_id INTEGER NOT NULL,
    inventory_index INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER,
    PRIMARY KEY (merchant_id, inventory_index),
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

-- ============================================================
-- ASSETS (resolved from PAK files)
-- ============================================================
CREATE TABLE assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_type TEXT NOT NULL,  -- 'texture', 'model', 'sound', 'animation'
    asset_name TEXT NOT NULL,
    pak_file TEXT,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    UNIQUE(asset_type, asset_name)
);

CREATE INDEX idx_assets_name ON assets(asset_name);
CREATE INDEX idx_assets_type ON assets(asset_type);

-- Link items to their icon assets
CREATE TABLE item_assets (
    item_id INTEGER NOT NULL,
    asset_id INTEGER NOT NULL,
    asset_role TEXT,  -- 'icon', 'model', etc.
    FOREIGN KEY (item_id) REFERENCES items(item_id),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

-- Link units to their model/animation assets
CREATE TABLE unit_assets (
    unit_id INTEGER NOT NULL,
    asset_id INTEGER NOT NULL,
    asset_role TEXT,  -- 'model', 'skeleton', 'animation'
    FOREIGN KEY (unit_id) REFERENCES units(unit_id),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

-- ============================================================
-- VIEWS (convenient queries)
-- ============================================================

-- Complete weapon view with all related data
CREATE VIEW v_weapons_full AS
SELECT
    w.item_id,
    in_en.name AS name_english,
    in_de.name AS name_german,
    in_ru.name AS name_russian,
    wt.weapon_type_id,
    wt_en.content AS weapon_type,
    wm.material_id,
    wm_en.content AS weapon_material,
    w.min_damage,
    w.max_damage,
    w.min_range,
    w.max_range,
    w.weapon_speed,
    i.sell_value,
    i.buy_value,
    s.strength,
    s.agility,
    s.armor,
    ui.ui_handle,
    ui.icon_path,
    a.file_path AS icon_file_path
FROM weapons w
INNER JOIN items i ON w.item_id = i.item_id
LEFT JOIN item_names in_en ON i.item_id = in_en.item_id AND in_en.language_id = 0
LEFT JOIN item_names in_de ON i.item_id = in_de.item_id AND in_de.language_id = 1
LEFT JOIN item_names in_ru ON i.item_id = in_ru.item_id AND in_ru.language_id = 5
LEFT JOIN weapon_types wt ON w.weapon_type_id = wt.weapon_type_id
LEFT JOIN texts wt_en ON wt.name_text_id = wt_en.text_id AND wt_en.language_id = 0
LEFT JOIN weapon_materials wm ON w.weapon_material_id = wm.material_id
LEFT JOIN texts wm_en ON wm.name_text_id = wm_en.text_id AND wm_en.language_id = 0
LEFT JOIN item_stats s ON w.item_id = s.item_id
LEFT JOIN item_ui ui ON w.item_id = ui.item_id AND ui.ui_index = 0
LEFT JOIN item_assets ia ON w.item_id = ia.item_id AND ia.asset_role = 'icon'
LEFT JOIN assets a ON ia.asset_id = a.asset_id;

-- Units with all equipment
CREATE VIEW v_units_with_equipment AS
SELECT
    u.unit_id,
    u_en.content AS name,
    u.handle,
    u.model_path,
    ue.equipment_index,
    i.item_id,
    i_en.content AS item_name,
    w.min_damage,
    w.max_damage
FROM units u
LEFT JOIN texts u_en ON u.name_text_id = u_en.text_id AND u_en.language_id = 0
LEFT JOIN unit_equipment ue ON u.unit_id = ue.unit_id
LEFT JOIN items i ON ue.item_id = i.item_id
LEFT JOIN texts i_en ON i.name_text_id = i_en.text_id AND i_en.language_id = 0
LEFT JOIN weapons w ON i.item_id = w.item_id;

-- Merchants with their inventory
CREATE VIEW v_merchant_inventory AS
SELECT
    m.merchant_id,
    m_en.content AS merchant_name,
    mi.inventory_index,
    i.item_id,
    i_en.content AS item_name,
    i.sell_value,
    i.buy_value
FROM merchants m
INNER JOIN texts m_en ON m.name_text_id = m_en.text_id AND m_en.language_id = 0
INNER JOIN merchant_inventory mi ON m.merchant_id = mi.merchant_id
INNER JOIN items i ON mi.item_id = i.item_id
INNER JOIN texts i_en ON i.name_text_id = i_en.text_id AND i_en.language_id = 0;
```

---

### 12.5 Asset Extraction & Database Population

#### Asset Extraction Process

```csharp
public class AssetExtractor
{
    private SQLiteConnection db;
    private Dictionary<string, int> assetCache = new Dictionary<string, int>();

    public void ExtractAllAssets()
    {
        // 1. Scan PAK files for all assets
        LogInfo("Extracting textures...");
        ExtractAssetType("texture", ".tga|.dds", new[] {"sf0.pak", "sf1.pak", "sf22.pak", "sf32.pak"});

        LogInfo("Extracting 3D models...");
        ExtractAssetType("model", ".msb", new[] {"sf8.pak", "sf22.pak", "sf32.pak"});

        LogInfo("Extracting sounds...");
        ExtractAssetType("sound", ".wav|.mp3", new[] {"sf2.pak", "sf3.pak", "sf20.pak", "sf30.pak"});

        LogInfo("Extracting animations...");
        ExtractAssetType("animation", ".bob", new[] {"sf5.pak", "sf22.pak", "sf32.pak"});
    }

    private void ExtractAssetType(string assetType, string extensions, string[] pakFiles)
    {
        foreach (string ext in extensions.Split('|'))
        {
            var files = SFUnPak.ListAllWithExtension("", ext, pakFiles);
            foreach (string file in files)
            {
                string assetName = Path.GetFileNameWithoutExtension(file);
                string pakFile = FindPakContainingFile(file, pakFiles);

                // Insert into database
                using (var cmd = db.CreateCommand())
                {
                    cmd.CommandText = @"
                        INSERT OR IGNORE INTO assets (asset_type, asset_name, pak_file, file_path)
                        VALUES (@type, @name, @pak, @path)
                    ";
                    cmd.Parameters.AddWithValue("@type", assetType);
                    cmd.Parameters.AddWithValue("@name", assetName);
                    cmd.Parameters.AddWithValue("@pak", pakFile);
                    cmd.Parameters.AddWithValue("@path", file);
                    cmd.ExecuteNonQuery();
                }
            }
        }
    }

    public int ResolveAssetID(string assetType, string assetName)
    {
        string key = $"{assetType}:{assetName}";
        if (assetCache.TryGetValue(key, out int assetId))
            return assetId;

        using (var cmd = db.CreateCommand())
        {
            cmd.CommandText = "SELECT asset_id FROM assets WHERE asset_type = @type AND asset_name = @name";
            cmd.Parameters.AddWithValue("@type", assetType);
            cmd.Parameters.AddWithValue("@name", assetName);
            var result = cmd.ExecuteScalar();
            if (result != null)
            {
                assetId = Convert.ToInt32(result);
                assetCache[key] = assetId;
                return assetId;
            }
        }
        return -1;  // Asset not found
    }

    public void LinkItemAssets()
    {
        // Link item icons from Category 2012
        var itemUICategory = SFCategoryManager.gamedata.c2012;
        for (int i = 0; i < itemUICategory.GetNumOfItems(); i++)
        {
            var uiItem = itemUICategory[i];
            string uiHandle = uiItem.GetHandleString().TrimEnd('\0');

            if (string.IsNullOrEmpty(uiHandle))
                continue;

            // Try to find icon in texture assets
            int assetId = ResolveAssetID("texture", uiHandle);
            if (assetId == -1)
            {
                // Try with ui/ prefix
                assetId = ResolveAssetID("texture", $"ui/{uiHandle}");
            }

            if (assetId != -1)
            {
                LinkAsset(uiItem.ItemID, assetId, "icon");
            }
        }
    }

    public void LinkUnitAssets()
    {
        // Link unit models from Category 2024
        var unitCategory = SFCategoryManager.gamedata.c2024;
        for (int i = 0; i < unitCategory.GetNumOfItems(); i++)
        {
            var unit = unitCategory[i];
            string handle = unit.GetHandleString().TrimEnd('\0');

            if (string.IsNullOrEmpty(handle))
                continue;

            // Find 3D model
            int modelAssetId = ResolveAssetID("model", handle);
            if (modelAssetId != -1)
            {
                LinkUnitAsset(unit.UnitID, modelAssetId, "model");
            }

            // Find skeleton
            int skelAssetId = ResolveAssetID("animation", handle);
            if (skelAssetId != -1)
            {
                LinkUnitAsset(unit.UnitID, skelAssetId, "skeleton");
            }
        }
    }

    private void LinkAsset(int itemId, int assetId, string role)
    {
        using (var cmd = db.CreateCommand())
        {
            cmd.CommandText = @"
                INSERT OR REPLACE INTO item_assets (item_id, asset_id, asset_role)
                VALUES (@item_id, @asset_id, @role)
            ";
            cmd.Parameters.AddWithValue("@item_id", itemId);
            cmd.Parameters.AddWithValue("@asset_id", assetId);
            cmd.Parameters.AddWithValue("@role", role);
            cmd.ExecuteNonQuery();
        }
    }

    private void LinkUnitAsset(int unitId, int assetId, string role)
    {
        using (var cmd = db.CreateCommand())
        {
            cmd.CommandText = @"
                INSERT OR REPLACE INTO unit_assets (unit_id, asset_id, asset_role)
                VALUES (@unit_id, @asset_id, @role)
            ";
            cmd.Parameters.AddWithValue("@unit_id", unitId);
            cmd.Parameters.AddWithValue("@asset_id", assetId);
            cmd.Parameters.AddWithValue("@role", role);
            cmd.ExecuteNonQuery();
        }
    }
}
```

---

### 12.6 Enhanced Export Formats with Assets

#### JSON Export with Asset Links

```json
{
  "weapons": [
    {
      "id": 123,
      "name": {
        "english": "Iron Sword",
        "german": "Eisenschwert",
        "russian": "Железный Меч"
      },
      "type": "1H Sword",
      "material": "Iron",
      "damage": { "min": 10, "max": 15 },
      "range": { "min": 0, "max": 1 },
      "speed": 100,
      "value": { "sell": 50, "buy": 100 },
      "stats": {
        "strength": 0,
        "agility": 2
      },
      "assets": {
        "icon": {
          "handle": "figure_item_sword_iron",
          "path": "texture/ui/figure_item_sword_iron.tga",
          "pak_file": "sf1.pak",
          "url": "file://extracted/texture/ui/figure_item_sword_iron.tga"
        }
      }
    }
  ]
}
```

#### SQLite Query Examples

```sql
-- Find all weapons with fire damage effects
SELECT
    w.item_id,
    in_en.name,
    w.min_damage,
    w.max_damage,
    s_en.content AS effect_name
FROM weapons w
INNER JOIN item_names in_en ON w.item_id = in_en.item_id AND in_en.language_id = 0
INNER JOIN weapon_effects we ON w.item_id = we.item_id
INNER JOIN spells s ON we.effect_id = s.spell_id
INNER JOIN texts s_en ON s.name_text_id = s_en.text_id AND s_en.language_id = 0
WHERE s_en.content LIKE '%Fire%';

-- Find all items without icons
SELECT
    i.item_id,
    in_en.name
FROM items i
LEFT JOIN item_names in_en ON i.item_id = in_en.item_id AND in_en.language_id = 0
LEFT JOIN item_assets ia ON i.item_id = ia.item_id AND ia.asset_role = 'icon'
WHERE ia.asset_id IS NULL;

-- List all units that can equip a specific weapon type
SELECT DISTINCT
    u.unit_id,
    u_en.content AS unit_name,
    i_en.content AS weapon_name
FROM units u
INNER JOIN texts u_en ON u.name_text_id = u_en.text_id AND u_en.language_id = 0
INNER JOIN unit_equipment ue ON u.unit_id = ue.unit_id
INNER JOIN items i ON ue.item_id = i.item_id
INNER JOIN texts i_en ON i.name_text_id = i_en.text_id AND i_en.language_id = 0
INNER JOIN weapons w ON i.item_id = w.item_id
INNER JOIN weapon_types wt ON w.weapon_type_id = wt.weapon_type_id
INNER JOIN texts wt_en ON wt.name_text_id = wt_en.text_id AND wt_en.language_id = 0
WHERE wt_en.content = '1H Sword';

-- Calculate average damage by weapon type
SELECT
    wt_en.content AS weapon_type,
    COUNT(*) AS count,
    AVG((w.min_damage + w.max_damage) / 2.0) AS avg_damage,
    MIN(w.min_damage) AS min_dmg,
    MAX(w.max_damage) AS max_dmg
FROM weapons w
INNER JOIN weapon_types wt ON w.weapon_type_id = wt.weapon_type_id
INNER JOIN texts wt_en ON wt.name_text_id = wt_en.text_id AND wt_en.language_id = 0
GROUP BY wt_en.content
ORDER BY avg_damage DESC;
```

---

### 12.7 Export Tool Enhancements

#### CLI Extensions

```bash
# Export to SQLite database with all assets
SpellforceGameDataExporter.exe --input "Gamedata.cff" --game-dir "H:\SpellSmut\OriginalGameFiles" --output "gamedata.db" --format sqlite --include-assets

# Export only specific tables to JSON
SpellforceGameDataExporter.exe --input "gamedata.db" --output "weapons.json" --tables weapons,weapon_effects --format json

# Extract assets referenced by items
SpellforceGameDataExporter.exe --input "gamedata.db" --output "extracted_assets/" --extract-assets --filter "type=texture,role=icon"

# Generate data dictionary (schema documentation)
SpellforceGameDataExporter.exe --input "gamedata.db" --output "schema.html" --generate-docs
```

**New CLI Arguments:**
- `--game-dir <path>` - Game directory for PAK file access
- `--include-assets` - Scan PAK files and link assets
- `--extract-assets` - Extract asset files to disk
- `--tables <list>` - Export specific tables only
- `--generate-docs` - Generate schema documentation

---

### 12.8 Asset Browser Integration

#### Web-Based Database Explorer

Create a simple web interface to browse the exported database:

**Technology Stack:**
- **Backend:** ASP.NET Core minimal API OR Python Flask
- **Database:** SQLite (read-only)
- **Frontend:** HTML + JavaScript (Vue.js/React optional)

**Features:**
- Search items/weapons by name
- Filter by type, damage range, value
- View all relationships (weapon → effects → spells)
- Display icons inline (served from extracted assets)
- Export filtered results to JSON/CSV
- Compare weapons side-by-side
- Visualize item stat distributions (charts)

**Example Routes:**
```
GET  /api/weapons              - List all weapons
GET  /api/weapons/{id}         - Get weapon details with all relations
GET  /api/items/search?q=sword - Search items
GET  /api/units/{id}/equipment - Get unit equipment
GET  /assets/icons/{handle}    - Serve icon image
GET  /                         - Web UI
```

---

### 12.9 Implementation Phases (Extended)

**Phase 1: Database Schema & Basic Export** ✅ (Weeks 1-2)
1. Create SQLite schema
2. Implement category → table exporters
3. Export items, weapons, spells, units
4. Test data integrity

**Phase 2: Asset Scanning & Linking** (Weeks 3-4)
1. Implement PAK file scanning
2. Populate `assets` table
3. Link items to icons (Category 2012)
4. Link units to models (Category 2024)
5. Link spells to icons (Category 2054)

**Phase 3: Advanced Queries & Views** (Week 5)
1. Create SQL views for common queries
2. Implement full-text search on names/descriptions
3. Add query performance indexes
4. Test complex JOINs

**Phase 4: Asset Extraction** (Week 6)
1. Extract referenced assets to disk
2. Convert textures to web-friendly formats (TGA → PNG)
3. Generate thumbnails
4. Create asset manifest

**Phase 5: Web Interface** (Weeks 7-8)
1. Create REST API
2. Build web UI
3. Implement search/filter
4. Add icon display
5. Deploy locally

**Phase 6: Documentation & Tools** (Week 9)
1. Generate schema documentation
2. Create SQL query cookbook
3. Write modding guide using database
4. Add import validation against DB

---

### 12.10 Database Export Benefits

#### For Modders
- **Query capabilities:** Find all items with specific stats
- **Data mining:** Analyze game balance (damage curves, price/performance)
- **Validation:** Check for orphaned references before import
- **Documentation:** Auto-generate item/spell wikis

#### For Developers
- **Testing:** Query database for test cases
- **Balance tools:** Analyze stat distributions
- **Asset audit:** Find missing/unused assets
- **Migration:** Easy conversion to other formats

#### For Community
- **Wiki generation:** Auto-populate game wikis
- **Build calculators:** Character/equipment optimizer tools
- **Lore research:** Extract all text for translation/analysis
- **Mod compatibility:** Detect ID conflicts between mods

---

### 12.11 Asset Export Deliverables

1. ✅ **SQLite schema definition** (SQL DDL)
2. ✅ **Database exporter** (CFF → SQLite)
3. ✅ **Asset scanner** (PAK → assets table)
4. ✅ **Asset linker** (items/units → assets)
5. ✅ **Asset extractor** (PAK → disk files)
6. ✅ **SQL query examples** (cookbook)
7. ✅ **Web API** (REST endpoints)
8. ✅ **Web UI** (browser interface)
9. ✅ **Schema documentation** (auto-generated)
10. ✅ **Example queries** (modding cookbook)

---

### 12.12 Comprehensive Testing Strategy

**Testing Philosophy:** Every component must be tested either with automated unit tests OR manual testing before proceeding to the next phase. No untested code should advance.

---

#### 12.12.1 Unit Testing Framework Setup

**Test Framework:** xUnit or NUnit for .NET 8.0

**Project Structure:**
```
SpellforceGameDataExporter.Tests/
├── CategoryExport/
│   ├── WeaponExporterTests.cs
│   ├── ItemExporterTests.cs
│   ├── SpellExporterTests.cs
│   └── UnitExporterTests.cs
├── AssetManagement/
│   ├── AssetExtractorTests.cs
│   ├── AssetLinkerTests.cs
│   └── PakScannerTests.cs
├── Database/
│   ├── SchemaTests.cs
│   ├── QueryTests.cs
│   └── DataIntegrityTests.cs
├── Import/
│   ├── WeaponImporterTests.cs
│   ├── ValidationTests.cs
│   └── ForeignKeyResolverTests.cs
├── Fixtures/
│   ├── TestGameData.cff (small test file)
│   ├── TestPakFile.pak (minimal PAK)
│   └── TestDatabaseFactory.cs
└── SpellforceGameDataExporter.Tests.csproj
```

**Dependencies:**
- `xUnit` (or `NUnit`)
- `FluentAssertions` (for readable assertions)
- `Moq` (for mocking dependencies)
- `System.Data.SQLite` (for database tests)

---

#### 12.12.2 Phase 1 Testing: Basic Category Export

**MUST PASS BEFORE PROCEEDING TO PHASE 2**

##### Unit Tests (Automated)

**Test: `CategoryLoading_Tests.cs`**
```csharp
[Fact]
public void LoadGameDataCFF_ValidFile_ReturnsGameData()
{
    // Arrange
    string testFile = "Fixtures/TestGameData.cff";

    // Act
    var result = SFCategoryManager.LoadCFF(testFile);

    // Assert
    result.Should().NotBeNull();
    result.c2003.Should().NotBeNull(); // Items category
}

[Fact]
public void LoadGameDataCFF_InvalidFile_ThrowsException()
{
    // Arrange
    string testFile = "nonexistent.cff";

    // Act & Assert
    Assert.Throws<FileNotFoundException>(() => SFCategoryManager.LoadCFF(testFile));
}

[Fact]
public void Category2016_TextResolution_ReturnsCorrectText()
{
    // Arrange
    LoadTestGameData();
    ushort testTextId = 1; // Known text ID in test data

    // Act
    string text = SFCategoryManager.GetTextByLanguage(testTextId, 0); // English

    // Assert
    text.Should().NotBeNullOrEmpty();
}
```

**Test: `WeaponExporter_Tests.cs`**
```csharp
[Fact]
public void ExportWeapons_ToJSON_ValidStructure()
{
    // Arrange
    LoadTestGameData();
    var exporter = new WeaponExporter(ExportFormat.JSON);

    // Act
    string json = exporter.Export();
    var weapons = JsonSerializer.Deserialize<List<WeaponData>>(json);

    // Assert
    weapons.Should().NotBeEmpty();
    weapons.First().Name.Should().NotBeNullOrEmpty();
    weapons.First().MinDamage.Should().BeGreaterThanOrEqualTo(0);
    weapons.First().MaxDamage.Should().BeGreaterThanOrEqualTo(weapons.First().MinDamage);
}

[Fact]
public void ExportWeapons_CrossCategoryLookup_ResolvesWeaponType()
{
    // Arrange
    LoadTestGameData();
    var exporter = new WeaponExporter(ExportFormat.JSON);

    // Act
    var weapons = exporter.ExportToModel();

    // Assert
    weapons.Where(w => w.WeaponTypeId > 0)
           .All(w => !string.IsNullOrEmpty(w.Type))
           .Should().BeTrue("All weapons with type ID should resolve to type name");
}

[Fact]
public void ExportWeapons_TextResolution_AllLanguages()
{
    // Arrange
    LoadTestGameData();
    var exporter = new WeaponExporter(ExportFormat.JSON);

    // Act
    var weapons = exporter.ExportToModel();
    var firstWeapon = weapons.First();

    // Assert
    firstWeapon.Name.English.Should().NotBeNullOrEmpty();
    // German and Russian may be null if not in test data, that's OK
}
```

**Test: `CSV_Export_Tests.cs`**
```csharp
[Fact]
public void ExportWeapons_ToCSV_ValidFormat()
{
    // Arrange
    LoadTestGameData();
    var exporter = new WeaponExporter(ExportFormat.CSV);

    // Act
    string csv = exporter.Export();

    // Assert
    csv.Should().Contain("WeaponID,Name,Type,Material"); // Header
    csv.Split('\n').Should().HaveCountGreaterThan(1); // At least header + 1 row
}

[Fact]
public void ExportWeapons_ToCSV_NoEscapingIssues()
{
    // Arrange
    LoadTestGameData();
    var exporter = new WeaponExporter(ExportFormat.CSV);

    // Act
    string csv = exporter.Export();

    // Assert
    // Names with commas should be quoted
    csv.Should().NotContain("\",\"\""); // Improper escaping
}
```

##### Manual Tests (Checklist)

**MANUAL TEST 1: Export Full GameData.cff**
- [ ] Export weapons from real `Gamedata.cff` to JSON
- [ ] Verify file is created
- [ ] Open JSON in text editor - confirm valid JSON syntax
- [ ] Check first 5 weapons have:
  - [ ] Valid name (not null/empty)
  - [ ] MinDamage ≤ MaxDamage
  - [ ] Weapon type resolved to name (not just ID)
  - [ ] Material resolved to name

**MANUAL TEST 2: Export to CSV**
- [ ] Export weapons to CSV
- [ ] Open in Excel/LibreOffice
- [ ] Verify columns aligned correctly
- [ ] Check for data corruption (encoding issues, garbled text)
- [ ] Verify Russian/German text displays correctly

**MANUAL TEST 3: Cross-Reference with Game**
- [ ] Pick 3 random weapons from export
- [ ] Launch SpellForce game
- [ ] Find those weapons in-game
- [ ] Verify stats match (damage, speed, name)

---

#### 12.12.3 Phase 2 Testing: Asset Scanning & Linking

**MUST PASS BEFORE PROCEEDING TO PHASE 3**

##### Unit Tests (Automated)

**Test: `PakScanner_Tests.cs`**
```csharp
[Fact]
public void ScanPakFile_ValidPak_ReturnsAssetList()
{
    // Arrange
    var scanner = new PakScanner();
    string[] pakFiles = { "sf1.pak" };

    // Act
    var assets = scanner.ScanPakForAssets("texture", ".tga", pakFiles);

    // Assert
    assets.Should().NotBeEmpty();
    assets.All(a => a.AssetType == "texture").Should().BeTrue();
    assets.All(a => a.FilePath.EndsWith(".tga")).Should().BeTrue();
}

[Fact]
public void ListAllWithExtension_MultipleExtensions_ReturnsAll()
{
    // Arrange
    var scanner = new PakScanner();

    // Act
    var textures = scanner.ListAllWithExtension("texture/ui", ".tga|.dds", new[] {"sf1.pak"});

    // Assert
    textures.Should().Contain(t => t.EndsWith(".tga"));
    textures.Should().Contain(t => t.EndsWith(".dds"));
}
```

**Test: `AssetLinker_Tests.cs`**
```csharp
[Fact]
public void LinkItemAssets_ValidUIHandle_FindsIcon()
{
    // Arrange
    LoadTestGameData();
    var db = CreateTestDatabase();
    var linker = new AssetLinker(db);

    // Populate test assets
    InsertTestAsset("texture", "figure_item_sword_iron", "texture/ui/figure_item_sword_iron.tga");

    // Act
    linker.LinkItemAssets();

    // Assert
    var links = db.Query("SELECT * FROM item_assets WHERE asset_role = 'icon'");
    links.Should().NotBeEmpty();
}

[Fact]
public void LinkItemAssets_MissingIcon_DoesNotCrash()
{
    // Arrange
    LoadTestGameData();
    var db = CreateTestDatabase();
    var linker = new AssetLinker(db);

    // Act (no assets in database)
    Action act = () => linker.LinkItemAssets();

    // Assert
    act.Should().NotThrow();
}

[Fact]
public void ResolveAssetID_CachedLookup_UsesCache()
{
    // Arrange
    var db = CreateTestDatabase();
    var linker = new AssetLinker(db);
    InsertTestAsset("texture", "test_icon", "texture/test.tga");

    // Act
    int firstCall = linker.ResolveAssetID("texture", "test_icon");
    int secondCall = linker.ResolveAssetID("texture", "test_icon");

    // Assert
    firstCall.Should().Be(secondCall);
    // Verify cache was used (could mock database to ensure only 1 query)
}
```

**Test: `AssetExtractor_Tests.cs`**
```csharp
[Fact]
public void ExtractAsset_FromPak_CreatesFile()
{
    // Arrange
    var extractor = new AssetExtractor();
    string outputPath = Path.GetTempFileName();

    // Act
    int result = extractor.ExtractAsset("sf1.pak", "texture/ui/test.tga", outputPath);

    // Assert
    result.Should().Be(0);
    File.Exists(outputPath).Should().BeTrue();

    // Cleanup
    File.Delete(outputPath);
}
```

##### Manual Tests (Checklist)

**MANUAL TEST 4: Asset Scanning**
- [ ] Run asset scanner on real PAK files
- [ ] Verify console output shows progress
- [ ] Check `assets` table in database:
  - [ ] Contains textures from sf1.pak
  - [ ] Contains models from sf8.pak
  - [ ] Contains sounds from sf2.pak
- [ ] Verify asset counts match expected (compare to game file browser)

**MANUAL TEST 5: Asset Linking**
- [ ] Run asset linker
- [ ] Query `item_assets` table:
  - [ ] At least 50% of items have icon links
  - [ ] No NULL asset_id values
- [ ] Query `unit_assets` table:
  - [ ] Major units have model links
- [ ] Check for orphaned assets (assets with no links) - log count

**MANUAL TEST 6: Asset Extraction**
- [ ] Extract 5 item icons to disk
- [ ] Verify TGA files open in image viewer
- [ ] Check file sizes are reasonable (not 0 bytes)
- [ ] Verify icons match in-game appearance

---

#### 12.12.4 Phase 3 Testing: Database Schema & Queries

**MUST PASS BEFORE PROCEEDING TO PHASE 4**

##### Unit Tests (Automated)

**Test: `DatabaseSchema_Tests.cs`**
```csharp
[Fact]
public void CreateSchema_ValidSQL_NoErrors()
{
    // Arrange
    var db = new SQLiteConnection(":memory:");
    db.Open();

    // Act
    var schemaSQL = File.ReadAllText("schema.sql");
    Action act = () => db.ExecuteNonQuery(schemaSQL);

    // Assert
    act.Should().NotThrow();
}

[Fact]
public void Schema_AllTables_Exist()
{
    // Arrange
    var db = CreateTestDatabase();

    // Act
    var tables = db.Query("SELECT name FROM sqlite_master WHERE type='table'");

    // Assert
    tables.Should().Contain("items");
    tables.Should().Contain("weapons");
    tables.Should().Contain("weapon_effects");
    tables.Should().Contain("spells");
    tables.Should().Contain("units");
    tables.Should().Contain("assets");
    tables.Should().Contain("item_assets");
}

[Fact]
public void Schema_AllViews_Exist()
{
    // Arrange
    var db = CreateTestDatabase();

    // Act
    var views = db.Query("SELECT name FROM sqlite_master WHERE type='view'");

    // Assert
    views.Should().Contain("v_weapons_full");
    views.Should().Contain("v_units_with_equipment");
    views.Should().Contain("v_merchant_inventory");
}

[Fact]
public void Schema_ForeignKeys_Enforced()
{
    // Arrange
    var db = CreateTestDatabase();
    db.ExecuteNonQuery("PRAGMA foreign_keys = ON");

    // Act & Assert - inserting item with invalid text_id should fail
    Action act = () => db.ExecuteNonQuery(@"
        INSERT INTO items (item_id, name_text_id) VALUES (1, 99999)
    ");

    act.Should().Throw<SQLiteException>()
       .WithMessage("*FOREIGN KEY constraint failed*");
}
```

**Test: `QueryTests.cs`**
```csharp
[Fact]
public void Query_WeaponsFull_JoinsCorrectly()
{
    // Arrange
    var db = CreateAndPopulateTestDatabase();

    // Act
    var weapons = db.Query("SELECT * FROM v_weapons_full");

    // Assert
    weapons.Should().NotBeEmpty();
    weapons.First()["name_english"].Should().NotBeNullOrEmpty();
    weapons.First()["weapon_type"].Should().NotBeNullOrEmpty();
}

[Fact]
public void Query_FindWeaponsWithFireDamage_ReturnsMatches()
{
    // Arrange
    var db = CreateAndPopulateTestDatabase();

    // Act
    var query = @"
        SELECT w.item_id, in_en.name
        FROM weapons w
        INNER JOIN item_names in_en ON w.item_id = in_en.item_id
        INNER JOIN weapon_effects we ON w.item_id = we.item_id
        WHERE we.effect_name LIKE '%Fire%'
    ";
    var results = db.Query(query);

    // Assert
    results.Should().NotBeEmpty();
}

[Fact]
public void Query_AverageDamageByType_CalculatesCorrectly()
{
    // Arrange
    var db = CreateAndPopulateTestDatabase();
    InsertTestWeapon(1, "1H Sword", 10, 15);
    InsertTestWeapon(2, "1H Sword", 12, 18);

    // Act
    var query = @"
        SELECT weapon_type, AVG((min_damage + max_damage) / 2.0) as avg_dmg
        FROM v_weapons_full
        GROUP BY weapon_type
    ";
    var results = db.Query(query);

    // Assert
    var swordRow = results.First(r => r["weapon_type"] == "1H Sword");
    swordRow["avg_dmg"].Should().BeApproximately(13.75, 0.1);
}
```

**Test: `DataIntegrity_Tests.cs`**
```csharp
[Fact]
public void DataIntegrity_NoOrphanedWeapons_AllHaveItems()
{
    // Arrange
    var db = CreateAndPopulateTestDatabase();

    // Act
    var orphans = db.Query(@"
        SELECT w.item_id FROM weapons w
        LEFT JOIN items i ON w.item_id = i.item_id
        WHERE i.item_id IS NULL
    ");

    // Assert
    orphans.Should().BeEmpty("All weapons must have corresponding item entries");
}

[Fact]
public void DataIntegrity_NoInvalidTextReferences()
{
    // Arrange
    var db = CreateAndPopulateTestDatabase();

    // Act
    var invalid = db.Query(@"
        SELECT i.item_id FROM items i
        WHERE i.name_text_id NOT IN (SELECT DISTINCT text_id FROM texts)
    ");

    // Assert
    invalid.Should().BeEmpty("All name_text_id must reference existing texts");
}

[Fact]
public void DataIntegrity_WeaponDamageLogical()
{
    // Arrange
    var db = CreateAndPopulateTestDatabase();

    // Act
    var invalid = db.Query(@"
        SELECT item_id FROM weapons
        WHERE min_damage > max_damage OR min_damage < 0
    ");

    // Assert
    invalid.Should().BeEmpty("MinDamage must be ≤ MaxDamage and ≥ 0");
}
```

##### Manual Tests (Checklist)

**MANUAL TEST 7: Database Export**
- [ ] Export full GameData.cff to SQLite
- [ ] Verify .db file is created
- [ ] Open in DB Browser for SQLite
- [ ] Check table counts:
  - [ ] `items` table has 1000+ rows
  - [ ] `weapons` table has 200+ rows
  - [ ] `texts` table has 5000+ rows
  - [ ] `assets` table has 10000+ rows

**MANUAL TEST 8: Query Performance**
- [ ] Run `v_weapons_full` view - should complete in < 1 second
- [ ] Run complex JOIN queries - verify results
- [ ] Test search query on item names - should be fast

**MANUAL TEST 9: Data Accuracy**
- [ ] Query 5 random weapons from database
- [ ] Cross-reference with original CFF file (open in editor)
- [ ] Verify all stats match exactly

---

#### 12.12.5 Phase 4 Testing: Import & Validation

**MUST PASS BEFORE PROCEEDING TO PHASE 5**

##### Unit Tests (Automated)

**Test: `WeaponImporter_Tests.cs`**
```csharp
[Fact]
public void ImportWeapon_ValidJSON_CreatesEntries()
{
    // Arrange
    var db = CreateTestDatabase();
    var importer = new WeaponImporter(db);
    var json = @"{
        ""name"": {""english"": ""Test Sword""},
        ""damage"": {""min"": 10, ""max"": 15},
        ""type"": ""1H Sword"",
        ""material"": ""Iron""
    }";

    // Act
    int itemId = importer.ImportFromJSON(json);

    // Assert
    itemId.Should().BeGreaterThan(0);

    var weapon = db.QuerySingle("SELECT * FROM weapons WHERE item_id = @id", itemId);
    weapon.Should().NotBeNull();
    weapon["min_damage"].Should().Be(10);
}

[Fact]
public void ImportWeapon_InvalidData_ThrowsValidationException()
{
    // Arrange
    var db = CreateTestDatabase();
    var importer = new WeaponImporter(db);
    var json = @"{
        ""name"": {""english"": ""Bad Weapon""},
        ""damage"": {""min"": 100, ""max"": 50}
    }";

    // Act & Assert
    Action act = () => importer.ImportFromJSON(json);
    act.Should().Throw<ValidationException>()
       .WithMessage("*MinDamage cannot exceed MaxDamage*");
}

[Fact]
public void ImportWeapon_MissingDependency_CreatesOrFails()
{
    // Arrange
    var db = CreateTestDatabase();
    var importer = new WeaponImporter(db, autoCreateDeps: false);
    var json = @"{
        ""name"": {""english"": ""Mythril Sword""},
        ""material"": ""Mythril""
    }";

    // Act & Assert
    Action act = () => importer.ImportFromJSON(json);
    act.Should().Throw<ValidationException>()
       .WithMessage("*Material 'Mythril' does not exist*");
}
```

**Test: `ValidationEngine_Tests.cs`**
```csharp
[Fact]
public void ValidateWeapon_AllFieldsValid_PassesValidation()
{
    // Arrange
    var validator = new ValidationEngine();
    var weapon = new WeaponData {
        Name = new MultilingualText { English = "Test" },
        MinDamage = 10,
        MaxDamage = 15,
        Speed = 100
    };

    // Act
    var errors = validator.Validate(weapon);

    // Assert
    errors.Should().BeEmpty();
}

[Fact]
public void ValidateWeapon_EmptyName_FailsValidation()
{
    // Arrange
    var validator = new ValidationEngine();
    var weapon = new WeaponData {
        Name = new MultilingualText { English = "" },
        MinDamage = 10,
        MaxDamage = 15
    };

    // Act
    var errors = validator.Validate(weapon);

    // Assert
    errors.Should().Contain(e => e.Contains("Name is required"));
}

[Fact]
public void ValidateWeapon_DamageInverted_FailsValidation()
{
    // Arrange
    var validator = new ValidationEngine();
    var weapon = new WeaponData {
        Name = new MultilingualText { English = "Test" },
        MinDamage = 50,
        MaxDamage = 10
    };

    // Act
    var errors = validator.Validate(weapon);

    // Assert
    errors.Should().Contain(e => e.Contains("MinDamage"));
}
```

**Test: `RoundTrip_Tests.cs`**
```csharp
[Fact]
public void RoundTrip_ExportThenImport_DataMatches()
{
    // Arrange
    var originalDb = CreateAndPopulateTestDatabase();
    var exporter = new WeaponExporter(originalDb);

    // Act - Export
    string json = exporter.ExportToJSON();

    // Import into new database
    var newDb = CreateTestDatabase();
    var importer = new WeaponImporter(newDb);
    importer.ImportFromJSON(json);

    // Assert - Query both databases
    var originalWeapons = originalDb.Query("SELECT * FROM v_weapons_full ORDER BY item_id");
    var importedWeapons = newDb.Query("SELECT * FROM v_weapons_full ORDER BY item_id");

    originalWeapons.Count().Should().Be(importedWeapons.Count());

    for (int i = 0; i < originalWeapons.Count(); i++)
    {
        var orig = originalWeapons[i];
        var imported = importedWeapons[i];

        imported["name_english"].Should().Be(orig["name_english"]);
        imported["min_damage"].Should().Be(orig["min_damage"]);
        imported["max_damage"].Should().Be(orig["max_damage"]);
    }
}
```

##### Manual Tests (Checklist)

**MANUAL TEST 10: JSON Import**
- [ ] Create test JSON with 3 custom weapons
- [ ] Import using CLI tool
- [ ] Verify weapons appear in database
- [ ] Check all fields populated correctly
- [ ] Verify text entries created in all languages

**MANUAL TEST 11: Validation**
- [ ] Try importing weapon with MinDamage > MaxDamage - should fail with error
- [ ] Try importing weapon with empty name - should fail
- [ ] Try importing weapon with invalid type - should fail
- [ ] Verify error messages are clear and helpful

**MANUAL TEST 12: Import Into Game**
- [ ] Import custom weapon into GameData.cff
- [ ] Save modified GameData.cff
- [ ] Copy to game directory
- [ ] Launch SpellForce
- [ ] Use console/editor to spawn custom weapon
- [ ] Verify weapon works in-game (CRITICAL!)

---

#### 12.12.6 Phase 5 Testing: Web Interface

**MUST PASS BEFORE PROCEEDING TO PHASE 6**

##### Automated Tests

**Test: `API_Tests.cs`**
```csharp
[Fact]
public async Task API_GetWeapons_ReturnsJSON()
{
    // Arrange
    var client = CreateTestAPIClient();

    // Act
    var response = await client.GetAsync("/api/weapons");

    // Assert
    response.StatusCode.Should().Be(HttpStatusCode.OK);
    response.Content.Headers.ContentType.MediaType.Should().Be("application/json");
}

[Fact]
public async Task API_GetWeaponByID_ReturnsWeapon()
{
    // Arrange
    var client = CreateTestAPIClient();

    // Act
    var response = await client.GetAsync("/api/weapons/123");
    var weapon = await response.Content.ReadAsAsync<WeaponData>();

    // Assert
    response.StatusCode.Should().Be(HttpStatusCode.OK);
    weapon.Id.Should().Be(123);
}

[Fact]
public async Task API_SearchWeapons_FiltersCorrectly()
{
    // Arrange
    var client = CreateTestAPIClient();

    // Act
    var response = await client.GetAsync("/api/items/search?q=sword");
    var items = await response.Content.ReadAsAsync<List<ItemData>>();

    // Assert
    items.Should().NotBeEmpty();
    items.All(i => i.Name.ToLower().Contains("sword")).Should().BeTrue();
}
```

##### Manual Tests (Checklist)

**MANUAL TEST 13: Web UI**
- [ ] Launch web server
- [ ] Open browser to http://localhost:5000
- [ ] Home page loads without errors
- [ ] Search for "sword" - results appear
- [ ] Click on a weapon - detail page loads
- [ ] Verify icon displays (if available)
- [ ] Test pagination (if implemented)

**MANUAL TEST 14: API Endpoints**
- [ ] GET /api/weapons - returns JSON array
- [ ] GET /api/weapons/123 - returns single weapon
- [ ] GET /api/items/search?q=iron - returns filtered results
- [ ] GET /api/units/1/equipment - returns unit equipment
- [ ] GET /assets/icons/figure_item_sword - serves image

**MANUAL TEST 15: Cross-Browser Testing**
- [ ] Test in Chrome - works correctly
- [ ] Test in Firefox - works correctly
- [ ] Test in Edge - works correctly
- [ ] Responsive design on mobile (optional)

---

#### 12.12.7 Integration Testing: End-to-End

**FINAL TESTS BEFORE RELEASE**

##### Manual Integration Tests

**INTEGRATION TEST 1: Full Export Pipeline**
- [ ] Start with vanilla GameData.cff
- [ ] Export to SQLite database with assets
- [ ] Verify database contains:
  - [ ] All items (compare count to CFF)
  - [ ] All weapons with stats
  - [ ] All spells
  - [ ] All units
  - [ ] Asset links
- [ ] Export subset to JSON
- [ ] Verify JSON is valid and complete

**INTEGRATION TEST 2: Full Import Pipeline**
- [ ] Create custom weapons in JSON
- [ ] Import into new GameData.cff
- [ ] Export back to JSON
- [ ] Compare original JSON to exported JSON - should match
- [ ] Load modified GameData.cff in game
- [ ] Verify custom weapons work

**INTEGRATION TEST 3: Asset Extraction Pipeline**
- [ ] Export database with assets
- [ ] Extract all weapon icons to folder
- [ ] Verify 200+ icon files created
- [ ] Random sample 10 icons - open in viewer
- [ ] Check file sizes reasonable

**INTEGRATION TEST 4: Web Interface Full Flow**
- [ ] Export database
- [ ] Launch web server
- [ ] Search for weapon
- [ ] View weapon details
- [ ] Export weapon to JSON via UI
- [ ] Modify JSON
- [ ] Import modified weapon
- [ ] Refresh database
- [ ] Verify changes appear in UI

---

#### 12.12.8 Performance Testing

##### Performance Benchmarks

**BENCHMARK TEST 1: Export Speed**
- [ ] Export full GameData.cff to JSON
- [ ] Measure time - should complete in < 30 seconds
- [ ] Export to SQLite - should complete in < 60 seconds
- [ ] Export with asset scanning - should complete in < 5 minutes

**BENCHMARK TEST 2: Import Speed**
- [ ] Import 100 weapons from JSON
- [ ] Measure time - should complete in < 10 seconds
- [ ] Import 1000 items - should complete in < 60 seconds

**BENCHMARK TEST 3: Query Performance**
- [ ] Run complex JOIN query (v_weapons_full)
- [ ] Should return results in < 500ms
- [ ] Search query by name - should complete in < 100ms

---

#### 12.12.9 Testing Checklist by Phase

**Phase 1: Basic Export**
- [ ] All unit tests pass (CategoryLoading, WeaponExporter, CSV_Export)
- [ ] MANUAL TEST 1 completed
- [ ] MANUAL TEST 2 completed
- [ ] MANUAL TEST 3 completed
- ✅ **Approved to proceed to Phase 2**

**Phase 2: Asset Scanning**
- [ ] All unit tests pass (PakScanner, AssetLinker, AssetExtractor)
- [ ] MANUAL TEST 4 completed
- [ ] MANUAL TEST 5 completed
- [ ] MANUAL TEST 6 completed
- ✅ **Approved to proceed to Phase 3**

**Phase 3: Database Schema**
- [ ] All unit tests pass (DatabaseSchema, QueryTests, DataIntegrity)
- [ ] MANUAL TEST 7 completed
- [ ] MANUAL TEST 8 completed
- [ ] MANUAL TEST 9 completed
- ✅ **Approved to proceed to Phase 4**

**Phase 4: Import & Validation**
- [ ] All unit tests pass (WeaponImporter, ValidationEngine, RoundTrip)
- [ ] MANUAL TEST 10 completed
- [ ] MANUAL TEST 11 completed
- [ ] MANUAL TEST 12 completed ⚠️ **CRITICAL: Must work in-game!**
- ✅ **Approved to proceed to Phase 5**

**Phase 5: Web Interface**
- [ ] All unit tests pass (API_Tests)
- [ ] MANUAL TEST 13 completed
- [ ] MANUAL TEST 14 completed
- [ ] MANUAL TEST 15 completed
- ✅ **Approved to proceed to Phase 6**

**Phase 6: Final Release**
- [ ] INTEGRATION TEST 1 completed
- [ ] INTEGRATION TEST 2 completed
- [ ] INTEGRATION TEST 3 completed
- [ ] INTEGRATION TEST 4 completed
- [ ] BENCHMARK TEST 1 completed
- [ ] BENCHMARK TEST 2 completed
- [ ] BENCHMARK TEST 3 completed
- [ ] All documentation complete
- ✅ **APPROVED FOR RELEASE**

---

#### 12.12.10 Test Data Management

**Test Fixtures Required:**

1. **TestGameData.cff** (100 KB)
   - 50 items (weapons, armor, consumables)
   - 10 spells
   - 10 units
   - Text entries in English, German, Russian
   - Should be minimal but representative

2. **TestPakFile.pak** (1 MB)
   - 10 texture assets (item icons)
   - 5 model assets (.msb files)
   - 5 sound files
   - Should include items referenced in TestGameData.cff

3. **TestDatabase.db**
   - Pre-populated SQLite database
   - 100 items, 50 weapons, 20 spells, 20 units
   - Used for query testing

**Test Data Setup:**
```csharp
public class TestDataFactory
{
    public static SQLiteConnection CreateTestDatabase()
    {
        var db = new SQLiteConnection(":memory:");
        db.Open();

        // Load schema
        var schema = File.ReadAllText("schema.sql");
        db.ExecuteNonQuery(schema);

        // Populate with test data
        PopulateTestData(db);

        return db;
    }

    private static void PopulateTestData(SQLiteConnection db)
    {
        // Insert test texts
        db.ExecuteNonQuery(@"
            INSERT INTO texts (text_id, language_id, language_name, content)
            VALUES
                (1, 0, 'English', 'Iron Sword'),
                (1, 1, 'German', 'Eisenschwert'),
                (2, 0, 'English', '1H Sword')
        ");

        // Insert test items
        db.ExecuteNonQuery(@"
            INSERT INTO items (item_id, name_text_id, sell_value, buy_value)
            VALUES (100, 1, 50, 100)
        ");

        // Insert test weapons
        db.ExecuteNonQuery(@"
            INSERT INTO weapons (item_id, min_damage, max_damage, weapon_type_id)
            VALUES (100, 10, 15, 1)
        ");
    }
}
```

---

#### 12.12.11 Continuous Testing Strategy

**During Development:**
- Run unit tests after every code change
- Use Test-Driven Development (TDD) where possible:
  1. Write failing test
  2. Implement feature
  3. Test passes
  4. Refactor

**Before Committing:**
- [ ] All unit tests pass
- [ ] Code coverage > 70%
- [ ] No compiler warnings

**Before Merging to Main:**
- [ ] All unit tests pass
- [ ] Relevant manual tests completed
- [ ] Code reviewed
- [ ] Documentation updated

---

### 12.13 Future Enhancements

#### Advanced Asset Features
- **3D model preview** in web UI (Three.js)
- **Sound playback** inline
- **Texture preview** with transparency
- **Animation viewer** (skeleton + animation)

#### Data Analysis Tools
- **Balance analyzer:** Detect overpowered items
- **Price calculator:** Suggest balanced sell/buy values
- **Stat distribution charts:** Visualize item progression
- **Mod conflict detector:** Check ID overlaps

#### Integration with Game
- **Live reload:** Export → reimport → test in-game
- **Hot reloading:** Modify database, apply changes without restart
- **In-game console:** Query database from game

---

**End of Plan**
