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

**End of Plan**
