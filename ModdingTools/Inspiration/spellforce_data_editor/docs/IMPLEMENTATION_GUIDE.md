# SpellForce Data Editor - Implementation Guide

**Generated:** 2025-10-21  
**Purpose:** Practical guide for implementing common modding tasks

---

## Table of Contents

1. [Quick Start Examples](#quick-start-examples)
2. [Reading Game Data](#reading-game-data)
3. [Modifying Game Data](#modifying-game-data)
4. [Creating New Content](#creating-new-content)
5. [Working with Relationships](#working-with-relationships)
6. [Advanced Patterns](#advanced-patterns)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start Examples

### Load and Display All Weapons

```csharp
using SFEngine.SFCFF;
using SFEngine.SFCFF.CTG;

// Load GameData
SFGameDataNew gamedata = new SFGameDataNew();
int result = gamedata.Load("path/to/Gamedata.cff");
if (result != 0)
{
    Console.WriteLine("Failed to load GameData");
    return;
}

// Set up category manager for text lookups
SFCategoryManager.Set(gamedata);

// Get weapon category
var weaponCat = gamedata.c2015;
var itemCat = gamedata.c2003;

Console.WriteLine($"Found {weaponCat.GetNumOfItems()} weapons");

// Iterate through all weapons
for (int i = 0; i < weaponCat.GetNumOfItems(); i++)
{
    var weapon = weaponCat[i];
    
    // Get weapon name from item category
    string name = SFCategoryManager.GetItemName(weapon.ItemID);
    
    Console.WriteLine($"Weapon: {name}");
    Console.WriteLine($"  ID: {weapon.ItemID}");
    Console.WriteLine($"  Damage: {weapon.MinDamage}-{weapon.MaxDamage}");
    Console.WriteLine($"  Speed: {weapon.WeaponSpeed}");
    Console.WriteLine();
}
```

### Find Specific Item by Name

```csharp
// Search for items containing "sword" in their name
string searchTerm = "sword";
List<int> foundItems = new List<int>();

var itemCat = gamedata.c2003;
var textCat = gamedata.c2016;

for (int i = 0; i < itemCat.GetNumOfItems(); i++)
{
    var item = itemCat[i];
    string itemName = SFCategoryManager.GetItemName(item.ItemID);
    
    if (itemName.ToLower().Contains(searchTerm.ToLower()))
    {
        foundItems.Add(i);
        Console.WriteLine($"Found: {itemName} (ID: {item.ItemID})");
    }
}
```

### Modify Weapon Damage

```csharp
// Find weapon by ID
ushort weaponID = 123;
if (weaponCat.GetItemIndex(weaponID, out int index))
{
    // Get current weapon data
    var weapon = weaponCat[index];
    
    Console.WriteLine($"Old damage: {weapon.MinDamage}-{weapon.MaxDamage}");
    
    // Modify damage
    weapon.MinDamage = 50;
    weapon.MaxDamage = 75;
    
    // Write back (structs are value types!)
    weaponCat.SetItem(index, weapon);
    
    Console.WriteLine($"New damage: {weapon.MinDamage}-{weapon.MaxDamage}");
}
else
{
    Console.WriteLine($"Weapon {weaponID} not found");
}
```

---

## Reading Game Data

### Accessing Categories

```csharp
// Direct access via SFGameDataNew
var spells = gamedata.c2002;      // Spells
var items = gamedata.c2003;       // Items (general)
var itemStats = gamedata.c2004;   // Item stats/bonuses
var units = gamedata.c2024;       // Units
var unitStats = gamedata.c2005;   // Unit stats
var weapons = gamedata.c2015;     // Weapon data
var text = gamedata.c2016;        // Text/translations

// Iterate all categories
foreach (var category in gamedata.GetCategories())
{
    Console.WriteLine($"{category.GetName()}: {category.GetNumOfItems()} items");
}
```

### Reading Single-Value Categories

```csharp
// Category 2015: Weapon Data (one entry per weapon)
var weaponCat = gamedata.c2015;

// Get item by index
var weapon = weaponCat[5];

// Find item by ID
if (weaponCat.GetItemIndex(123, out int index))
{
    var weapon = weaponCat[index];
    // Use weapon data
}

// Get all items
for (int i = 0; i < weaponCat.GetNumOfItems(); i++)
{
    var weapon = weaponCat[i];
    // Process weapon
}
```

### Reading Multi-Value Categories

```csharp
// Category 2016: Text Data (multiple languages per text ID)
var textCat = gamedata.c2016;

ushort textID = 1234;
if (textCat.GetItemIndex(textID, out int index))
{
    // Get number of translations
    int translationCount = textCat.GetItemSubItemNum(index);
    
    Console.WriteLine($"Text {textID} has {translationCount} translations:");
    
    // Iterate all translations
    for (int i = 0; i < translationCount; i++)
    {
        var textItem = textCat[index, i];
        string languageName = GetLanguageName(textItem.LanguageID);
        string content = textItem.GetContentString();
        
        Console.WriteLine($"  [{languageName}]: {content}");
    }
}

string GetLanguageName(byte langID)
{
    return langID switch
    {
        0 => "English",
        1 => "German",
        2 => "French",
        5 => "Russian",
        6 => "Polish",
        _ => $"Unknown ({langID})"
    };
}
```

### Resolving Foreign Keys

```csharp
// Get complete weapon information with resolved references
ushort weaponID = 123;

if (weaponCat.GetItemIndex(weaponID, out int weaponIndex))
{
    var weapon = weaponCat[weaponIndex];
    
    // Get item general info
    if (itemCat.GetItemIndex(weaponID, out int itemIndex))
    {
        var item = itemCat[itemIndex];
        
        // Resolve weapon name
        string name = SFCategoryManager.GetItemName(weaponID);
        
        // Resolve weapon type
        string typeName = "";
        if (gamedata.c2063.GetItemIndex(weapon.WeaponType, out int typeIndex))
        {
            var weaponType = gamedata.c2063[typeIndex];
            typeName = SFCategoryManager.GetTextByLanguage(weaponType.NameID, 0);
        }
        
        // Resolve weapon material
        string materialName = "";
        if (gamedata.c2064.GetItemIndex(weapon.WeaponMaterial, out int matIndex))
        {
            var material = gamedata.c2064[matIndex];
            materialName = SFCategoryManager.GetTextByLanguage(material.NameID, 0);
        }
        
        Console.WriteLine($"Weapon: {name}");
        Console.WriteLine($"  Type: {typeName}");
        Console.WriteLine($"  Material: {materialName}");
        Console.WriteLine($"  Damage: {weapon.MinDamage}-{weapon.MaxDamage}");
        Console.WriteLine($"  Value: {item.SellValue} copper");
    }
}
```

---

## Modifying Game Data

### Simple Field Modification

```csharp
// Without undo/redo (direct modification)
if (weaponCat.GetItemIndex(123, out int index))
{
    var weapon = weaponCat[index];
    weapon.MinDamage = 50;
    weapon.MaxDamage = 75;
    weaponCat.SetItem(index, weapon);  // Must call SetItem!
}

// With undo/redo support
UndoRedoQueue urq = new UndoRedoQueue();
weaponCat.EnableUndoRedo(urq);

weaponCat.SetField(index, "MinDamage", (ushort)50);
weaponCat.SetField(index, "MaxDamage", (ushort)75);

// Can undo
urq.Undo();  // Reverts both changes

// Can redo
urq.Redo();  // Re-applies both changes
```

### Batch Modifications

```csharp
// Modify multiple fields atomically
urq.OpenCluster();

weaponCat.SetField(index, "MinDamage", (ushort)50);
weaponCat.SetField(index, "MaxDamage", (ushort)75);
weaponCat.SetField(index, "WeaponSpeed", (ushort)120);

urq.CloseCluster();  // All changes undo/redo together
```

### Modifying Text

```csharp
// Modify existing text
ushort textID = 1234;
byte languageID = 0;  // English

if (textCat.GetItemSubItemIndex(textID, languageID, out int itemIndex))
{
    var textItem = textCat[itemIndex];
    
    // Create new text item with modified content
    var newTextItem = textItem;
    SetTextContent(ref newTextItem, "New text content");
    
    // Find which main index and sub-index this is
    if (textCat.GetItemIndex(textID, out int mainIndex))
    {
        // Find sub-index
        int subItemCount = textCat.GetItemSubItemNum(mainIndex);
        for (int i = 0; i < subItemCount; i++)
        {
            if (textCat[mainIndex, i].LanguageID == languageID)
            {
                textCat.SetSubItem(mainIndex, i, newTextItem);
                break;
            }
        }
    }
}

unsafe void SetTextContent(ref Category2016Item item, string text)
{
    Encoding encoding = Encoding.GetEncoding(1252);
    byte[] bytes = encoding.GetBytes(text);
    
    if (bytes.Length > 512)
        throw new Exception("Text too long");
    
    fixed (byte* dest = item.Content)
    {
        for (int i = 0; i < bytes.Length && i < 512; i++)
            dest[i] = bytes[i];
        if (bytes.Length < 512)
            dest[bytes.Length] = 0;  // Null terminate
    }
}
```

---

## Creating New Content

### Adding a New Weapon

```csharp
// 1. Find unused ID
weaponCat.GetFirstUnusedID(out int newWeaponID, out int insertIndex);

Console.WriteLine($"Creating weapon with ID {newWeaponID}");

// 2. Create weapon data
Category2015Item newWeapon = new Category2015Item
{
    ItemID = (ushort)newWeaponID,
    MinDamage = 20,
    MaxDamage = 30,
    MinRange = 0,
    MaxRange = 1,
    WeaponSpeed = 100,
    WeaponType = 1,      // 1H Sword
    WeaponMaterial = 2   // Steel
};

// 3. Add to weapon category
weaponCat.AddItem(insertIndex, newWeapon);

// 4. Create item general info
itemCat.GetFirstUnusedID(out int itemID, out int itemInsertIndex);

Category2003Item newItem = new Category2003Item
{
    ItemID = (ushort)newWeaponID,  // Same ID as weapon
    ItemType1 = 1,  // Weapon type
    ItemType2 = 0,
    NameID = 0,     // Will set after creating text
    SellValue = 100,
    BuyValue = 200
};

itemCat.AddItem(itemInsertIndex, newItem);

// 5. Create text entry for weapon name
ushort newTextID = CreateTextEntry("Custom Steel Sword");

// 6. Update item with text ID
newItem.NameID = newTextID;
itemCat.SetItem(itemInsertIndex, newItem);

Console.WriteLine("Weapon created successfully!");
```

### Creating Text Entries

```csharp
ushort CreateTextEntry(string englishText, string germanText = null)
{
    // Find unused text ID
    textCat.GetFirstUnusedID(out int newTextID, out int insertIndex);
    
    // Create English entry
    Category2016Item englishItem = new Category2016Item
    {
        TextID = (ushort)newTextID,
        LanguageID = 0,  // English
        Mode = 0
    };
    SetTextContent(ref englishItem, englishText);
    
    textCat.AddItem(insertIndex, englishItem);
    
    // Add German translation if provided
    if (germanText != null)
    {
        Category2016Item germanItem = new Category2016Item
        {
            TextID = (ushort)newTextID,
            LanguageID = 1,  // German
            Mode = 0
        };
        SetTextContent(ref germanItem, germanText);
        
        // Add as sub-item
        textCat.AddSubItem(insertIndex, 1, germanItem);
    }
    
    return (ushort)newTextID;
}
```

### Adding Item Stats/Bonuses

```csharp
// Add stat bonuses to an item
Category2004Item itemStats = new Category2004Item
{
    ItemID = (ushort)newWeaponID,
    Strength = 5,
    Agility = 3,
    Dexterity = 2,
    Armor = 0,
    ResistFire = 10,
    // ... other stats default to 0
};

itemStatsCat.CalculateNewItemIndex(newWeaponID, out int statsInsertIndex);
itemStatsCat.AddItem(statsInsertIndex, itemStats);
```

### Adding Weapon Effects

```csharp
// Add fire damage effect to weapon
Category2014Item weaponEffect = new Category2014Item
{
    ItemID = (ushort)newWeaponID,
    EffectIndex = 0,  // First effect
    EffectID = 147    // Fire damage spell ID
};

// Find insert position
if (gamedata.c2014.CalculateNewItemIndex(newWeaponID, out int effectInsertIndex))
{
    gamedata.c2014.AddItem(effectInsertIndex, weaponEffect);
}
else
{
    // Item already has effects, add as sub-item
    gamedata.c2014.GetItemIndex(newWeaponID, out int mainIndex);
    int subIndex = gamedata.c2014.GetItemSubItemNum(mainIndex);
    weaponEffect.EffectIndex = (byte)subIndex;
    gamedata.c2014.AddSubItem(mainIndex, subIndex, weaponEffect);
}
```

---

## Working with Relationships

### Finding All Items Equipped by a Unit

```csharp
ushort unitID = 456;

if (gamedata.c2025.GetItemIndex(unitID, out int index))
{
    int equipmentCount = gamedata.c2025.GetItemSubItemNum(index);
    
    Console.WriteLine($"Unit {unitID} equipment:");
    
    for (int i = 0; i < equipmentCount; i++)
    {
        var equipment = gamedata.c2025[index, i];
        string itemName = SFCategoryManager.GetItemName(equipment.ItemID);
        
        Console.WriteLine($"  Slot {equipment.EquipmentIndex}: {itemName}");
    }
}
```

### Finding All Units That Can Equip an Item

```csharp
ushort itemID = 123;
List<ushort> unitsWithItem = new List<ushort>();

// Iterate all units
for (int i = 0; i < gamedata.c2025.GetNumOfItems(); i++)
{
    gamedata.c2025.GetID(i, out int unitID);
    
    int equipmentCount = gamedata.c2025.GetItemSubItemNum(i);
    for (int j = 0; j < equipmentCount; j++)
    {
        var equipment = gamedata.c2025[i, j];
        if (equipment.ItemID == itemID)
        {
            unitsWithItem.Add((ushort)unitID);
            break;
        }
    }
}

Console.WriteLine($"Item {itemID} is equipped by {unitsWithItem.Count} units");
```

### Finding All Weapons of a Specific Type

```csharp
ushort weaponTypeID = 1;  // 1H Sword
List<ushort> weaponsOfType = new List<ushort>();

for (int i = 0; i < weaponCat.GetNumOfItems(); i++)
{
    var weapon = weaponCat[i];
    if (weapon.WeaponType == weaponTypeID)
    {
        weaponsOfType.Add(weapon.ItemID);
    }
}

Console.WriteLine($"Found {weaponsOfType.Count} weapons of type {weaponTypeID}");
```

---

## Advanced Patterns

### Bulk Operations with Progress Reporting

```csharp
void IncreaseAllWeaponDamage(int percentage, IProgress<int> progress)
{
    int totalWeapons = weaponCat.GetNumOfItems();
    
    urq.OpenCluster();  // Batch all changes
    
    for (int i = 0; i < totalWeapons; i++)
    {
        var weapon = weaponCat[i];
        
        ushort newMinDamage = (ushort)(weapon.MinDamage * (100 + percentage) / 100);
        ushort newMaxDamage = (ushort)(weapon.MaxDamage * (100 + percentage) / 100);
        
        weaponCat.SetField(i, "MinDamage", newMinDamage);
        weaponCat.SetField(i, "MaxDamage", newMaxDamage);
        
        // Report progress
        if (i % 10 == 0)
            progress?.Report((i * 100) / totalWeapons);
    }
    
    urq.CloseCluster();
    progress?.Report(100);
}

// Usage
var progress = new Progress<int>(percent => 
{
    Console.WriteLine($"Progress: {percent}%");
});

IncreaseAllWeaponDamage(10, progress);  // +10% damage to all weapons
```

### Searching with Complex Criteria

```csharp
// Find all weapons with damage > 50 and speed > 100
List<int> FindWeapons(Func<Category2015Item, bool> predicate)
{
    List<int> results = new List<int>();
    
    for (int i = 0; i < weaponCat.GetNumOfItems(); i++)
    {
        var weapon = weaponCat[i];
        if (predicate(weapon))
        {
            results.Add(i);
        }
    }
    
    return results;
}

// Usage
var powerfulFastWeapons = FindWeapons(w => 
    w.MaxDamage > 50 && w.WeaponSpeed > 100
);

Console.WriteLine($"Found {powerfulFastWeapons.Count} powerful fast weapons");
```

### Cloning Items

```csharp
ushort CloneWeapon(ushort sourceWeaponID)
{
    // 1. Find source weapon
    if (!weaponCat.GetItemIndex(sourceWeaponID, out int sourceIndex))
        throw new Exception("Source weapon not found");
    
    // 2. Get new ID
    weaponCat.GetFirstUnusedID(out int newID, out int insertIndex);
    
    // 3. Copy weapon data
    var sourceWeapon = weaponCat[sourceIndex];
    var newWeapon = sourceWeapon;
    newWeapon.ItemID = (ushort)newID;
    weaponCat.AddItem(insertIndex, newWeapon);
    
    // 4. Copy item general info
    if (itemCat.GetItemIndex(sourceWeaponID, out int sourceItemIndex))
    {
        var sourceItem = itemCat[sourceItemIndex];
        var newItem = sourceItem;
        newItem.ItemID = (ushort)newID;
        
        // Create new text entry for name
        string originalName = SFCategoryManager.GetItemName(sourceWeaponID);
        ushort newTextID = CreateTextEntry($"{originalName} (Copy)");
        newItem.NameID = newTextID;
        
        itemCat.CalculateNewItemIndex(newID, out int itemInsertIndex);
        itemCat.AddItem(itemInsertIndex, newItem);
    }
    
    // 5. Copy stats if present
    if (itemStatsCat.GetItemIndex(sourceWeaponID, out int sourceStatsIndex))
    {
        var sourceStats = itemStatsCat[sourceStatsIndex];
        var newStats = sourceStats;
        newStats.ItemID = (ushort)newID;
        
        itemStatsCat.CalculateNewItemIndex(newID, out int statsInsertIndex);
        itemStatsCat.AddItem(statsInsertIndex, newStats);
    }
    
    // 6. Copy effects if present
    if (gamedata.c2014.GetItemIndex(sourceWeaponID, out int effectMainIndex))
    {
        int effectCount = gamedata.c2014.GetItemSubItemNum(effectMainIndex);
        
        for (int i = 0; i < effectCount; i++)
        {
            var sourceEffect = gamedata.c2014[effectMainIndex, i];
            var newEffect = sourceEffect;
            newEffect.ItemID = (ushort)newID;
            
            if (i == 0)
            {
                gamedata.c2014.CalculateNewItemIndex(newID, out int effectInsertIndex);
                gamedata.c2014.AddItem(effectInsertIndex, newEffect);
            }
            else
            {
                gamedata.c2014.GetItemIndex(newID, out int newEffectMainIndex);
                gamedata.c2014.AddSubItem(newEffectMainIndex, i, newEffect);
            }
        }
    }
    
    return (ushort)newID;
}
```

---

## Troubleshooting

### Common Issues

#### 1. "Item not found" when ID exists

**Problem:** Using wrong category or ID type mismatch.

```csharp
// WRONG: Looking for weapon in item category
if (itemCat.GetItemIndex(weaponID, out int index))
{
    var weapon = itemCat[index];  // This is an item, not weapon data!
}

// CORRECT: Use weapon category for weapon data
if (weaponCat.GetItemIndex(weaponID, out int index))
{
    var weapon = weaponCat[index];  // Correct!
}
```

#### 2. Modified struct not saving

**Problem:** Structs are value types - must call SetItem after modification.

```csharp
// WRONG: Modification lost
var weapon = weaponCat[index];
weapon.MinDamage = 50;  // Modifies local copy only!

// CORRECT: Write back to category
var weapon = weaponCat[index];
weapon.MinDamage = 50;
weaponCat.SetItem(index, weapon);  // Must call this!
```

#### 3. Text encoding issues

**Problem:** Wrong encoding for language.

```csharp
// WRONG: Using default encoding for Russian
Encoding encoding = Encoding.GetEncoding(1252);  // Wrong for Russian!

// CORRECT: Use language-specific encoding
Encoding encoding = languageID == 5 
    ? Encoding.GetEncoding(1251)  // Russian
    : Encoding.GetEncoding(1252); // Default
```

#### 4. Multi-valued category confusion

**Problem:** Treating multi-valued category like single-valued.

```csharp
// WRONG: Accessing text like single-value category
var text = textCat[index];  // This is the FIRST sub-item only!

// CORRECT: Iterate sub-items
int subItemCount = textCat.GetItemSubItemNum(index);
for (int i = 0; i < subItemCount; i++)
{
    var text = textCat[index, i];  // Access each sub-item
}
```

#### 5. Foreign key not resolved

**Problem:** Referenced ID doesn't exist.

```csharp
// Check if foreign key exists before using
if (gamedata.c2063.GetItemIndex(weapon.WeaponType, out int typeIndex))
{
    var weaponType = gamedata.c2063[typeIndex];
    // Use weapon type
}
else
{
    Console.WriteLine($"Warning: Weapon type {weapon.WeaponType} not found");
}
```

### Validation Checklist

Before saving modified GameData:

```csharp
bool ValidateGameData(SFGameDataNew gamedata)
{
    bool valid = true;
    
    // 1. Check all items have valid text IDs
    for (int i = 0; i < gamedata.c2003.GetNumOfItems(); i++)
    {
        var item = gamedata.c2003[i];
        if (!gamedata.c2016.GetItemIndex(item.NameID, out _))
        {
            Console.WriteLine($"Error: Item {item.ItemID} has invalid NameID {item.NameID}");
            valid = false;
        }
    }
    
    // 2. Check all weapons reference valid items
    for (int i = 0; i < gamedata.c2015.GetNumOfItems(); i++)
    {
        var weapon = gamedata.c2015[i];
        if (!gamedata.c2003.GetItemIndex(weapon.ItemID, out _))
        {
            Console.WriteLine($"Error: Weapon {weapon.ItemID} has no item entry");
            valid = false;
        }
    }
    
    // 3. Check weapon types exist
    for (int i = 0; i < gamedata.c2015.GetNumOfItems(); i++)
    {
        var weapon = gamedata.c2015[i];
        if (!gamedata.c2063.GetItemIndex(weapon.WeaponType, out _))
        {
            Console.WriteLine($"Error: Weapon {weapon.ItemID} has invalid type {weapon.WeaponType}");
            valid = false;
        }
    }
    
    // Add more validation as needed...
    
    return valid;
}

// Usage
if (ValidateGameData(gamedata))
{
    gamedata.Save("ModifiedGamedata.cff");
    Console.WriteLine("GameData saved successfully");
}
else
{
    Console.WriteLine("Validation failed - not saving");
}
```

---

## Performance Tips

### 1. Cache Lookups

```csharp
// BAD: Repeated lookups
for (int i = 0; i < 1000; i++)
{
    string name = SFCategoryManager.GetItemName(itemID);  // Slow!
}

// GOOD: Cache result
string name = SFCategoryManager.GetItemName(itemID);
for (int i = 0; i < 1000; i++)
{
    // Use cached name
}
```

### 2. Use Binary Search

```csharp
// BAD: Linear search
int FindItemIndex(ushort itemID)
{
    for (int i = 0; i < itemCat.GetNumOfItems(); i++)
    {
        if (itemCat[i].ItemID == itemID)
            return i;
    }
    return -1;
}

// GOOD: Use built-in binary search
if (itemCat.GetItemIndex(itemID, out int index))
{
    // Found at index
}
```

### 3. Batch Operations

```csharp
// BAD: Individual saves
for (int i = 0; i < 100; i++)
{
    ModifyWeapon(i);
    gamedata.Save("temp.cff");  // Very slow!
}

// GOOD: Batch modifications
for (int i = 0; i < 100; i++)
{
    ModifyWeapon(i);
}
gamedata.Save("final.cff");  // Save once
```

---

**This guide covers the most common implementation patterns. For more details, see CODEBASE_ARCHITECTURE.md and BINARY_FORMAT_SPECIFICATION.md.**
