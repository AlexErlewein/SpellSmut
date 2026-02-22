# SpellForce Data Editor - Codebase Architecture

**Generated:** 2025-10-21  
**Focus:** SFEngine and SFEngine/SFCFF implementation details

---

## Table of Contents

1. [Overview](#overview)
2. [Core Architecture Patterns](#core-architecture-patterns)
3. [SFEngine Library Structure](#sfengine-library-structure)
4. [SFCFF Category System Deep Dive](#sfcff-category-system-deep-dive)
5. [Binary Serialization & Performance](#binary-serialization--performance)
6. [Undo/Redo System](#undoredo-system)
7. [Data Flow & Lifecycle](#data-flow--lifecycle)
8. [Key Implementation Details](#key-implementation-details)
9. [Working with Categories](#working-with-categories)
10. [Common Patterns & Best Practices](#common-patterns--best-practices)

---

## Overview

The SpellForce Data Editor is a modding tool for SpellForce: Platinum Edition that provides comprehensive access to game data files. The codebase is structured around a clean separation between the engine library (SFEngine) and the UI application (SpellforceDataEditor).

### Technology Stack

- **Language:** C# (.NET 8.0)
- **Platform:** Windows (x86 for game compatibility)
- **UI Framework:** Windows Forms
- **Graphics:** OpenGL via OpenTK 4.8.2
- **Audio:** NAudio 2.2.1
- **Key Features:** Unsafe code blocks, fixed buffers, memory marshaling

---

## Core Architecture Patterns

### 1. Interface-Based Category System

All game data categories implement the `ICategory` interface, providing a uniform API for:
- Loading/saving binary data
- Managing items (add, remove, copy, search)
- Undo/redo support
- Merge/diff operations for modding

```csharp
public interface ICategory
{
    string GetName();
    short GetCategoryID();
    short GetCategoryType();
    int GetNumOfItems();
    bool Load(SFChunkFile file);
    bool Save(SFChunkFile file);
    bool MergeFrom(ICategory c1, ICategory c2);
    bool DiffFrom(ICategory c1, ICategory c2);
    // ... CRUD operations, search, undo/redo
}
```

### 2. Generic Base Classes

Two generic base classes handle the majority of category implementations:

#### CategoryBaseSingle<T>
For categories where each ID has exactly one entry (e.g., items, units, spells).

```csharp
public abstract class CategoryBaseSingle<T> : ICategory 
    where T : struct, ICategoryItem
{
    public List<T> Items = new List<T>();
    // Binary search for O(log n) lookups
    // Direct memory marshaling for fast I/O
}
```

#### CategoryBaseMultiple<T>
For categories where each ID can have multiple sub-items (e.g., text translations, unit equipment, weapon effects).

```csharp
public abstract class CategoryBaseMultiple<T> : ICategory 
    where T : struct, ICategorySubItem
{
    public List<T> Items = new List<T>();
    public List<int> Indices = new List<int>();  // Index of first sub-item for each ID
    // Supports one-to-many relationships
}
```

### 3. Struct-Based Data Items

All category items are defined as C# structs with `StructLayout(LayoutKind.Sequential, Pack = 1)` for direct binary compatibility with game files.

```csharp
[StructLayout(LayoutKind.Sequential, Pack = 1)]
public unsafe struct Category2015Item : ICategoryItem
{
    public ushort ItemID;
    public ushort MinDamage;
    public ushort MaxDamage;
    public ushort MinRange;
    public ushort MaxRange;
    public ushort WeaponSpeed;
    public ushort WeaponType;
    public ushort WeaponMaterial;

    public int GetID() => ItemID;
    public void SetID(int id) => ItemID = (ushort)id;
}
```

### 4. Chunk-Based File Format

SpellForce uses a custom chunk-based binary format for all data files:

```
[File Header: 20 bytes]
  - Magic: 0xDD5E5E12 (-579674862)
  - Format: 3 (for maps), varies for other types
  - Type: 1 (map), 0 (gamedata)
  - Version: 0
  - Checksum: 0

[Chunk 1]
  - ChunkID: short (e.g., 2015 for weapon data)
  - ChunkOccurrence: short (usually 0)
  - IsCompressed: bool
  - ChunkDataType: short (category type)
  - ChunkDataSize: int
  - Data: byte[] (raw struct array)

[Chunk 2]
...
```

---

## SFEngine Library Structure

### Namespace Organization

```
SFEngine/
├── SFCFF/                    # Game data (CFF) system
│   ├── ICategory.cs          # Core interfaces
│   ├── CategoryBase.cs       # Generic base implementations
│   ├── SFCategoryManager.cs  # High-level category access
│   ├── SFGameDataNew.cs      # Container for all categories
│   └── CTG/                  # Category implementations
│       ├── Category2001.cs   # Army unit building requirements
│       ├── Category2002.cs   # Spells
│       ├── Category2003.cs   # Items (general)
│       ├── Category2015.cs   # Weapons
│       ├── Category2016.cs   # Text (multilingual)
│       └── ... (50+ categories)
│
├── SFChunk/                  # Binary chunk file I/O
│   ├── SFChunkFile.cs        # Chunk file reader/writer
│   └── SFChunkFileChunk.cs   # Individual chunk representation
│
├── SFUnPak/                  # PAK archive system
│   ├── SFUnPak.cs            # PAK file manager
│   ├── SFPakMap.cs           # File location cache
│   └── SFPakFileSystem.cs    # Virtual file system
│
├── SFMap/                    # Map file handling
│   ├── SFMap.cs              # Map container
│   ├── SFMapHeightMap.cs     # Terrain elevation
│   ├── SFMapUnitManager.cs   # Unit placement
│   └── ... (managers for each map component)
│
├── SF3D/                     # 3D rendering
│   ├── SFRenderEngine.cs     # OpenGL rendering
│   ├── SFModel3D.cs          # 3D model loading
│   └── SceneSynchro/         # Scene management
│
├── SFLua/                    # Lua script handling
│   ├── LuaParser/            # Lua script parsing
│   ├── LuaDecompiler/        # Binary Lua decompilation
│   └── lua_sql/              # SQL script editing
│
├── SFResources/              # Resource management
│   ├── SFResourceManager.cs  # Asset caching
│   └── SFResourceContainer.cs
│
├── SFSound/                  # Audio playback
│   └── SFSoundEngine.cs
│
└── LogUtils/                 # Logging system
    └── Log.cs
```

---

## SFCFF Category System Deep Dive

### Category Lifecycle

```
1. Load GameData.cff
   ↓
2. SFChunkFile.OpenFile() - Parse chunk headers
   ↓
3. For each category:
   - ICategory.Load(SFChunkFile)
   - Find chunk by category ID
   - Memory-map chunk data to struct array
   - Calculate indices (for multi-valued categories)
   ↓
4. SFCategoryManager.Set(gamedata) - Register for lookups
   ↓
5. UI displays category data
   ↓
6. User edits data (undo/redo tracked)
   ↓
7. ICategory.Save(SFChunkFile) - Serialize back to binary
   ↓
8. SFChunkFile.Close() - Write to disk
```

### CategoryBaseSingle Implementation Details

#### Fast Binary Loading

Uses `CollectionsMarshal` and `MemoryMarshal` for zero-copy deserialization:

```csharp
public bool Load(SFChunkFile file)
{
    // Get chunk span (start position, length)
    if(!file.GetChunkSpanByID(GetCategoryID(), out int type, out int start, out int length))
        return true;  // Category not present in file
    
    // Calculate item count from byte size
    int item_count;
    unsafe { item_count = length / sizeof(T); }
    
    // Resize list to exact size
    CollectionsMarshal.SetCount(Items, item_count);
    
    // Get direct memory span
    Span<T> items_span = CollectionsMarshal.AsSpan(Items);
    Span<byte> items_span_raw = MemoryMarshal.Cast<T, byte>(items_span);
    
    // Read directly into struct array (zero-copy!)
    file.stream.Position = start;
    file.stream.Read(items_span_raw);
    
    return true;
}
```

**Performance:** Loads 10,000+ items in milliseconds.

#### Binary Search for Lookups

All items are kept sorted by ID for O(log n) lookups:

```csharp
public bool GetItemIndex(int id, out int index)
{
    int current_start = 0;
    int current_end = Items.Count - 1;
    int current_center;
    
    while (current_start <= current_end)
    {
        current_center = (current_start + current_end) / 2;
        int cur_id = Items[current_center].GetID();
        
        if (cur_id == id)
        {
            index = current_center;
            return true;
        }
        
        if (cur_id < id)
            current_start = current_center + 1;
        else
            current_end = current_center - 1;
    }
    
    index = Utility.NO_INDEX;
    return false;
}
```

### CategoryBaseMultiple Implementation Details

#### Index Management

Multi-valued categories maintain a separate index list pointing to the first sub-item for each ID:

```csharp
// Items: [ID=1,SubID=0], [ID=1,SubID=1], [ID=2,SubID=0], [ID=3,SubID=0], [ID=3,SubID=1], [ID=3,SubID=2]
// Indices: [0, 2, 3]  (positions where new IDs start)

void CalculateIndices()
{
    int cur_item_id = -1;
    for(int i = 0; i < Items.Count; i++)
    {
        int item_id = Items[i].GetID();
        if(item_id != cur_item_id)
        {
            cur_item_id = item_id;
            Indices.Add(i);  // Mark start of new ID group
        }
    }
}
```

#### Accessing Sub-Items

```csharp
// Get number of sub-items for an ID
public int GetItemSubItemNum(int index)
{
    if(index == Indices.Count-1)
        return Items.Count - Indices[index];  // Last ID group
    return Indices[index + 1] - Indices[index];
}

// Access specific sub-item
public T this[int index, int subindex]
{
    get
    {
        int item_index = Indices[index] + subindex;
        return Items[item_index];
    }
}
```

### Category Examples

#### Category 2015: Weapon Data (Single)

```csharp
public class Category2015 : CategoryBaseSingle<Category2015Item>
{
    public override string GetName() => "Item weapon data";
    public override short GetCategoryID() => 2015;
    public override short GetCategoryType() => 2;
}

// Usage:
var weaponCat = gamedata.c2015;
if(weaponCat.GetItemIndex(123, out int index))
{
    var weapon = weaponCat[index];
    Console.WriteLine($"Damage: {weapon.MinDamage}-{weapon.MaxDamage}");
}
```

#### Category 2016: Text Data (Multiple)

```csharp
public class Category2016 : CategoryBaseMultiple<Category2016Item>
{
    public override string GetName() => "Text data";
    public override short GetCategoryID() => 2016;
    public override short GetCategoryType() => 3;
    public override bool GetSubitemDiffBehavior() => true;  // Treat sub-items independently
}

// Usage:
var textCat = gamedata.c2016;
if(textCat.GetItemIndex(1234, out int index))
{
    // Get all translations for text ID 1234
    int subItemCount = textCat.GetItemSubItemNum(index);
    for(int i = 0; i < subItemCount; i++)
    {
        var textItem = textCat[index, i];
        Console.WriteLine($"Lang {textItem.LanguageID}: {textItem.GetContentString()}");
    }
}
```

---

## Binary Serialization & Performance

### Memory Layout

Structs use `Pack = 1` to match game's binary layout exactly:

```csharp
[StructLayout(LayoutKind.Sequential, Pack = 1)]
public unsafe struct Category2015Item
{
    public ushort ItemID;        // Offset: 0, Size: 2
    public ushort MinDamage;     // Offset: 2, Size: 2
    public ushort MaxDamage;     // Offset: 4, Size: 2
    public ushort MinRange;      // Offset: 6, Size: 2
    public ushort MaxRange;      // Offset: 8, Size: 2
    public ushort WeaponSpeed;   // Offset: 10, Size: 2
    public ushort WeaponType;    // Offset: 12, Size: 2
    public ushort WeaponMaterial;// Offset: 14, Size: 2
}
// Total size: 16 bytes
```

### Fixed Buffers for Strings

Text fields use fixed-size byte arrays:

```csharp
[StructLayout(LayoutKind.Sequential, Pack = 1)]
public unsafe struct Category2016Item
{
    public ushort TextID;
    public byte LanguageID;
    public byte Mode;
    public fixed byte Handle[50];    // Fixed 50-byte buffer
    public fixed byte Content[512];  // Fixed 512-byte buffer
    
    public string GetContentString()
    {
        Encoding encoding = GetEncodingForLanguage(LanguageID);
        fixed (byte* s = Content)
        {
            return encoding.GetString(s, 512);
        }
    }
}
```

### Unsafe Code for Performance

Direct pointer manipulation for fast field access:

```csharp
void QueryItemsFieldNumber<U>(int num, uint field_offset, bool as_flag, List<int> result)
{
    Span<T> items_span = CollectionsMarshal.AsSpan(Items);
    unsafe
    {
        fixed (T* ptr = items_span)
        {
            for (int i = 0; i < items_span.Length; i++)
            {
                U* ptr2 = (U*)(((byte*)(&ptr[i])) + field_offset);
                int cur_value = Convert.ToInt32(*ptr2);
                
                if (cur_value == num)
                    result.Add(i);
            }
        }
    }
}
```

---

## Undo/Redo System

### Architecture

The undo/redo system uses the Command pattern with a queue-based implementation:

```
UndoRedoQueue
├── List<IUndoRedo> queue
├── int current_index
└── UndoRedoCluster current_cluster (for batching)

IUndoRedo (Command Interface)
├── bool Init()    // Execute and validate
├── void Undo()    // Reverse operation
└── void Redo()    // Re-apply operation
```

### Command Types

#### Single-Value Category Commands

```csharp
// Add item
public class UndoRedoElementAddSingle<T> : IUndoRedo
{
    public CategoryBaseSingle<T> cat;
    public int index;
    public T item;
    
    public void Redo() => cat.Items.Insert(index, item);
    public void Undo() => cat.Items.RemoveAt(index);
}

// Remove item
public class UndoRedoElementRemoveSingle<T> : IUndoRedo
{
    public CategoryBaseSingle<T> cat;
    public int index;
    T previous_item;
    
    public bool Init()
    {
        previous_item = cat.Items[index];
        Redo();
        return true;
    }
    
    public void Redo() => cat.Items.RemoveAt(index);
    public void Undo() => cat.Items.Insert(index, previous_item);
}

// Modify field
public class UndoRedoElementSetFieldSingle<T, U> : IUndoRedo
{
    public CategoryBaseSingle<T> cat;
    public int index;
    public string field_name;
    public U value;
    T new_item;
    T previous_item;
    
    // Uses reflection to modify specific field
    // Supports array indexing: "FieldName[5]"
}
```

#### Multi-Value Category Commands

Similar structure but operates on sub-items:
- `UndoRedoElementAddMultiple<T>`
- `UndoRedoSubElementAddMultiple<T>`
- `UndoRedoSubElementRemoveMultiple<T>`
- etc.

### Clustering Operations

Batch multiple operations into a single undo/redo step:

```csharp
urq.OpenCluster();

// Multiple operations
cat.AddItem(index1, item1);
cat.AddItem(index2, item2);
cat.SetField(index3, "Damage", 100);

urq.CloseCluster();  // All operations undo/redo together
```

### Usage Pattern

```csharp
// Enable undo/redo for a category
UndoRedoQueue urq = new UndoRedoQueue();
category.EnableUndoRedo(urq);

// Make changes (automatically tracked)
category.SetField(5, "MinDamage", (ushort)50);

// Undo
urq.Undo();  // Reverts to previous value

// Redo
urq.Redo();  // Re-applies change
```

---

## Data Flow & Lifecycle

### Loading GameData.cff

```
User: Open File
    ↓
MainForm.LoadGameData()
    ↓
SFGameDataNew.Load(filename)
    ↓
SFChunkFile.OpenFile(filename)
    ↓
For each category in SFGameDataNew.GetCategories():
    category.Load(chunkFile)
        ↓
        Find chunk by category ID
        ↓
        Memory-map chunk data to struct array
        ↓
        (For multi-valued) Calculate indices
    ↓
SFCategoryManager.Set(gamedata)
    ↓
UI: Display category list
```

### Editing Data

```
User: Select category → Select item → Edit field
    ↓
Control.SetField(index, field_name, value)
    ↓
Category.SetField<U>(index, field_name, value)
    ↓
Create UndoRedoElementSetFieldSingle<T, U>
    ↓
IUndoRedo.Init()
    ↓
    Use reflection to find field
    ↓
    Get current value (for undo)
    ↓
    Set new value (redo)
    ↓
    Store both values in command
    ↓
UndoRedoQueue.Push(command)
    ↓
Category.OnElementModified callback
    ↓
UI: Refresh display
```

### Saving GameData.cff

```
User: Save File
    ↓
SFGameDataNew.Save(filename)
    ↓
SFChunkFile.CreateFile(filename, GAMEDATA)
    ↓
For each category in SFGameDataNew.GetCategories():
    category.Save(chunkFile)
        ↓
        Get struct array span
        ↓
        Cast to byte span
        ↓
        chunkFile.AddChunk(categoryID, type, data)
    ↓
SFChunkFile.Close()
    ↓
    Write header
    ↓
    Write all chunks sequentially
    ↓
    Flush to disk
```

---

## Key Implementation Details

### SFCategoryManager

High-level helper for common operations:

```csharp
public static class SFCategoryManager
{
    public static SFGameDataNew gamedata;
    
    // Resolve text by ID and language
    public static string GetTextByLanguage(ushort text_id, int lang_id)
    {
        if(!gamedata.c2016.GetItemIndex(text_id, out int index))
            return "";
        
        int subItemCount = gamedata.c2016.GetItemSubItemNum(index);
        for(int i = 0; i < subItemCount; i++)
        {
            var textItem = gamedata.c2016[index, i];
            if(textItem.LanguageID == lang_id)
                return textItem.GetContentString();
        }
        return "";
    }
    
    // Get item name (resolves NameID → text)
    public static string GetItemName(ushort item_id)
    {
        if(!gamedata.c2003.GetItemIndex(item_id, out int index))
            return "";
        
        var item = gamedata.c2003[index];
        return GetTextByLanguage(item.NameID, 0);  // English
    }
    
    // Similar helpers for units, spells, etc.
}
```

### SFGameDataNew

Container for all categories:

```csharp
public class SFGameDataNew
{
    public string fname;
    
    // All 50+ categories as public fields
    public Category2001 c2001 = new();
    public Category2002 c2002 = new();
    public Category2003 c2003 = new();
    // ... etc
    
    public IEnumerable<ICategory> GetCategories()
    {
        yield return c2001;
        yield return c2002;
        yield return c2003;
        // ... etc
    }
    
    public int Load(string filename) { /* ... */ }
    public int Save(string filename) { /* ... */ }
    public int Merge(SFGameDataNew gd1, SFGameDataNew gd2) { /* ... */ }
    public int Diff(SFGameDataNew gd1, SFGameDataNew gd2) { /* ... */ }
}
```

### Merge & Diff Operations

Used for modding - combine or compare two GameData files:

```csharp
// Merge: Combine two gamedatas (new overrides old)
public bool MergeFrom(ICategory c1, ICategory c2)
{
    // Double list ladder algorithm
    // For each ID:
    //   - If only in c1: add from c1
    //   - If only in c2: add from c2
    //   - If in both: add from c2 (newer wins)
}

// Diff: Extract only differences
public bool DiffFrom(ICategory c1, ICategory c2)
{
    // For each ID:
    //   - If only in c2: add (new item)
    //   - If in both but different: add from c2 (modified)
    //   - If only in c1: skip (removed)
}
```

### Search System

Query items by field value:

```csharp
// Search for items with specific field value
List<int> results = category.QueryItems(
    value: 100,
    field_name: "MinDamage",
    option: SearchOption.IS_NUMBER
);

// Search all fields
List<int> results = category.QueryItems(
    value: "sword",
    field_name: "",  // Empty = search all
    option: SearchOption.IS_STRING | SearchOption.IGNORE_CASE
);
```

---

## Working with Categories

### Creating a New Category

1. Define the struct:

```csharp
[StructLayout(LayoutKind.Sequential, Pack = 1)]
public unsafe struct Category2XXXItem : ICategoryItem
{
    public ushort ItemID;
    public ushort Field1;
    public uint Field2;
    // ... fields
    
    public int GetID() => ItemID;
    public void SetID(int id) => ItemID = (ushort)id;
}
```

2. Define the category class:

```csharp
public class Category2XXX : CategoryBaseSingle<Category2XXXItem>
{
    public override string GetName() => "My Category";
    public override short GetCategoryID() => 2XXX;
    public override short GetCategoryType() => 2;  // Usually 2 for single, 3 for multiple
}
```

3. Add to SFGameDataNew:

```csharp
public class SFGameDataNew
{
    public Category2XXX c2XXX = new();
    
    public IEnumerable<ICategory> GetCategories()
    {
        // ... existing categories
        yield return c2XXX;
    }
}
```

### Reading Category Data

```csharp
// Get category
var weaponCat = gamedata.c2015;

// Iterate all items
for(int i = 0; i < weaponCat.GetNumOfItems(); i++)
{
    var weapon = weaponCat[i];
    Console.WriteLine($"Weapon {weapon.ItemID}: {weapon.MinDamage}-{weapon.MaxDamage}");
}

// Find specific item
if(weaponCat.GetItemIndex(123, out int index))
{
    var weapon = weaponCat[index];
    // Use weapon data
}
```

### Modifying Category Data

```csharp
// With undo/redo
category.SetField(index, "MinDamage", (ushort)50);

// Without undo/redo (direct modification)
var item = category[index];
item.MinDamage = 50;
category.SetItem(index, item);  // Must set back (structs are value types)
```

### Adding/Removing Items

```csharp
// Add new item
category.GetFirstUnusedID(out int newID, out int insertIndex);
category.AddID(insertIndex, newID);

// Remove item
category.Remove(index);

// Copy item
category.Copy(fromIndex, toIndex);
```

---

## Common Patterns & Best Practices

### 1. Always Use Binary Search

Items are sorted by ID - use `GetItemIndex()` instead of linear search:

```csharp
// GOOD
if(category.GetItemIndex(itemID, out int index))
{
    var item = category[index];
}

// BAD
for(int i = 0; i < category.GetNumOfItems(); i++)
{
    if(category[i].GetID() == itemID)
    {
        var item = category[i];
        break;
    }
}
```

### 2. Resolve Foreign Keys via SFCategoryManager

```csharp
// Get weapon with resolved names
var weapon = weaponCat[index];
string weaponName = SFCategoryManager.GetItemName(weapon.ItemID);
string weaponType = SFCategoryManager.GetTextByLanguage(
    gamedata.c2063[typeIndex].NameID, 0
);
```

### 3. Handle Multi-Valued Categories Correctly

```csharp
// Get all sub-items for an ID
if(textCat.GetItemIndex(textID, out int index))
{
    int subItemCount = textCat.GetItemSubItemNum(index);
    for(int i = 0; i < subItemCount; i++)
    {
        var textItem = textCat[index, i];
        // Process sub-item
    }
}
```

### 4. Use Undo/Redo for User-Facing Operations

```csharp
// Enable undo/redo
UndoRedoQueue urq = new UndoRedoQueue();
category.EnableUndoRedo(urq);

// Batch operations
urq.OpenCluster();
category.SetField(index1, "Field1", value1);
category.SetField(index2, "Field2", value2);
urq.CloseCluster();
```

### 5. Handle Text Encoding Properly

```csharp
Encoding GetEncodingForLanguage(byte languageID)
{
    return languageID switch
    {
        5 => Encoding.GetEncoding(1251),  // Russian
        6 => Encoding.GetEncoding(1250),  // Polish
        _ => Encoding.GetEncoding(1252)   // Default (Western European)
    };
}
```

### 6. Validate IDs Before Operations

```csharp
// Check if ID exists before modifying
if(!category.GetItemIndex(itemID, out int index))
{
    LogUtils.Log.Error(LogSource.SFCFF, $"Item {itemID} not found");
    return;
}

// Check if new ID is available
if(!category.CalculateNewItemIndex(newID, out int insertIndex))
{
    LogUtils.Log.Error(LogSource.SFCFF, $"ID {newID} already exists");
    return;
}
```

### 7. Use Callbacks for UI Updates

```csharp
category.SetOnElementModifiedCallback((catID, index) =>
{
    // Refresh UI display
    RefreshListBox();
});
```

---

## Performance Considerations

### Memory Usage

- **Struct-based:** All items are value types, stored contiguously in memory
- **No boxing:** Direct memory access via spans and pointers
- **Cache-friendly:** Sequential access patterns

### Load Times

- **GameData.cff:** ~50 categories, ~50,000 items total
- **Load time:** < 1 second (memory-mapped I/O)
- **Save time:** < 1 second (direct binary write)

### Search Performance

- **Binary search:** O(log n) for ID lookups
- **Field search:** O(n) but uses unsafe pointers for speed
- **Text search:** O(n) with encoding overhead

### Optimization Tips

1. **Batch operations** using undo/redo clusters
2. **Cache foreign key lookups** (e.g., text translations)
3. **Use spans** instead of copying arrays
4. **Avoid boxing** value types
5. **Minimize reflection** (only used in SetField)

---

## Conclusion

The SpellForce Data Editor codebase demonstrates advanced C# techniques for high-performance binary data manipulation:

- **Zero-copy I/O** via memory marshaling
- **Generic programming** for code reuse
- **Unsafe code** for performance-critical paths
- **Command pattern** for undo/redo
- **Interface-based design** for extensibility

The SFCFF system provides a robust foundation for modding SpellForce game data, with clean separation between data structures (structs), business logic (categories), and UI (WinForms controls).

---

**For more information:**
- See `CATEGORIES_OVERVIEW.md` for detailed category descriptions
- See `CATEGORY_RELATIONSHIPS.md` for foreign key relationships
- See `GAMEDATA_EXPORT_PLAN.md` for export/import implementation details
