# SpellForce Binary Format Specification

**Generated:** 2025-10-21  
**Purpose:** Detailed specification of SpellForce's binary file formats

---

## Table of Contents

1. [Chunk File Format](#chunk-file-format)
2. [GameData.cff Structure](#gamedatacff-structure)
3. [Map File Format](#map-file-format)
4. [PAK Archive Format](#pak-archive-format)
5. [Data Type Specifications](#data-type-specifications)
6. [Encoding & Text Handling](#encoding--text-handling)

---

## Chunk File Format

SpellForce uses a custom chunk-based binary format for GameData, Maps, and Save files.

### File Header (20 bytes)

```
Offset | Size | Type  | Name     | Description
-------|------|-------|----------|----------------------------------
0x00   | 4    | int32 | Magic    | File signature: 0xDD5E5E12 (-579674862)
0x04   | 4    | int32 | Format   | Format version (3 for maps, varies)
0x08   | 4    | int32 | Type     | File type (0=GameData, 1=Map, 2=Save)
0x0C   | 4    | int32 | Version  | File version (usually 0)
0x10   | 4    | int32 | Checksum | Checksum (usually 0, not validated)
```

**Magic Number Validation:**
```csharp
public bool IsValid() { return Magic == -579674862; }
```

### Chunk Structure

Each chunk follows this format:

```
Offset | Size | Type   | Name            | Description
-------|------|--------|-----------------|----------------------------------
0x00   | 2    | int16  | ChunkID         | Category ID (e.g., 2015 for weapons)
0x02   | 2    | int16  | ChunkOccurrence | Occurrence index (usually 0)
0x04   | 1    | bool   | IsCompressed    | Compression flag (0=raw, 1=zlib)
0x05   | 2    | int16  | ChunkDataType   | Category type (2=single, 3=multiple)
0x07   | 4    | int32  | ChunkDataSize   | Size of data in bytes
0x0B   | N    | byte[] | ChunkData       | Raw or compressed data
```

**Total Chunk Header Size:** 11 bytes

### Chunk Data Layout

For uncompressed chunks, data is a raw array of structs:

```
[Struct 1: N bytes]
[Struct 2: N bytes]
[Struct 3: N bytes]
...
```

**Item Count Calculation:**
```csharp
int item_count = ChunkDataSize / sizeof(T);
```

### Compression

When `IsCompressed == true`, `ChunkData` contains zlib-compressed data:

```csharp
// Decompression
using (var compressedStream = new MemoryStream(compressedData))
using (var zlibStream = new ZLibStream(compressedStream, CompressionMode.Decompress))
{
    zlibStream.Read(decompressedBuffer, 0, decompressedSize);
}
```

### File Layout Example

```
[File Header: 20 bytes]
[Chunk 1: Category 2001]
  - Header: 11 bytes
  - Data: 240 bytes (15 items × 16 bytes)
[Chunk 2: Category 2002]
  - Header: 11 bytes
  - Data: 12800 bytes (200 items × 64 bytes)
[Chunk 3: Category 2003]
  - Header: 11 bytes
  - Data: 51200 bytes (3200 items × 16 bytes)
...
[EOF]
```

---

## GameData.cff Structure

### File Metadata

- **Type:** 0 (GameData)
- **Format:** Varies by game version
- **Typical Size:** 2-5 MB
- **Chunk Count:** 40-50 chunks (one per category)

### Category Chunk IDs

| Chunk ID | Category Name           | Type | Struct Size | Typical Count |
|----------|-------------------------|------|-------------|---------------|
| 2001     | Army Unit Building Req  | 3    | 16          | 50-100        |
| 2002     | Spells                  | 2    | 64          | 200-300       |
| 2003     | Items (General)         | 2    | 16          | 2000-3000     |
| 2004     | Item Stats              | 2    | 34          | 500-1000      |
| 2005     | Unit Stats              | 2    | 48          | 300-500       |
| 2012     | Item UI                 | 3    | 66          | 2000-3000     |
| 2014     | Weapon Effects          | 3    | 6           | 100-200       |
| 2015     | Weapon Data             | 2    | 16          | 500-800       |
| 2016     | Text Data               | 3    | 566         | 5000-10000    |
| 2024     | Units                   | 2    | 52          | 300-500       |
| 2029     | Buildings               | 2    | 32          | 100-200       |
| 2063     | Weapon Types            | 2    | 6           | 20-30         |
| 2064     | Weapon Materials        | 2    | 4           | 10-20         |

### Struct Packing

All structs use `Pack = 1` (no padding):

```csharp
[StructLayout(LayoutKind.Sequential, Pack = 1)]
public unsafe struct Category2015Item
{
    public ushort ItemID;        // 2 bytes
    public ushort MinDamage;     // 2 bytes
    public ushort MaxDamage;     // 2 bytes
    public ushort MinRange;      // 2 bytes
    public ushort MaxRange;      // 2 bytes
    public ushort WeaponSpeed;   // 2 bytes
    public ushort WeaponType;    // 2 bytes
    public ushort WeaponMaterial;// 2 bytes
}
// Total: 16 bytes (no padding)
```

---

## Map File Format

### File Metadata

- **Type:** 1 (Map)
- **Format:** 3
- **Typical Size:** 500 KB - 10 MB
- **Chunk Count:** 10-20 chunks

### Map Chunk IDs

| Chunk ID | Name                    | Description                          |
|----------|-------------------------|--------------------------------------|
| 2        | Heightmap               | Terrain elevation data               |
| 3        | Terrain Textures        | Texture blend weights (255 layers)  |
| 4        | Units                   | Unit placement data                  |
| 5        | Buildings               | Building placement data              |
| 6        | Objects                 | Interactive object placement         |
| 7        | Decorations             | Decoration placement                 |
| 8        | Portals                 | Portal definitions                   |
| 9        | Lakes                   | Water body definitions               |
| 10       | Weather                 | Weather settings                     |
| 11       | Metadata                | Map name, description, player count  |

### Heightmap Data (Chunk 2)

```
[Map Width: 4 bytes (uint32)]
[Map Height: 4 bytes (uint32)]
[Tile Data: Width × Height × 2 bytes]
  - Each tile: uint16 elevation value (0-65535)
  - Row-major order (left-to-right, top-to-bottom)
```

**Example:**
```
Map: 128×128
Data size: 4 + 4 + (128 × 128 × 2) = 32,776 bytes
```

### Terrain Texture Data (Chunk 3)

```
[Texture Count: 1 byte (always 255)]
For each texture (255 entries):
  [Texture ID: 2 bytes (uint16)]
  [Blend Weights: Width × Height bytes]
    - Each tile: uint8 blend weight (0-255)
```

**Total Size:**
```
1 + (255 × (2 + Width × Height))
```

### Entity Placement Data

Units, buildings, objects, decorations use similar structure:

```
[Entity Count: 4 bytes (uint32)]
For each entity:
  [Entity ID: 2 bytes (uint16)]
  [Position X: 4 bytes (float)]
  [Position Y: 4 bytes (float)]
  [Position Z: 4 bytes (float)]
  [Rotation: 4 bytes (float)]
  [Additional Data: varies by entity type]
```

---

## PAK Archive Format

### Overview

PAK files are custom archive format containing game assets (textures, models, sounds, animations).

### File Structure

```
[Header]
  - Magic: "PAK\0" (4 bytes)
  - Version: uint32
  - File Count: uint32
  - Index Offset: uint32 (offset to file index)

[File Data]
  - Concatenated file contents

[File Index]
  For each file:
    - File Path: null-terminated string
    - File Offset: uint32
    - File Size: uint32
    - Compression: uint8 (0=none, 1=zlib)
```

### PAK Priority System

Multiple PAK files can exist, with higher numbers overriding lower:

```
sf0.pak  - Base textures
sf1.pak  - Additional textures
sf2.pak  - Sound effects
sf3.pak  - Music
sf8.pak  - 3D models
sf22.pak - Expansion content (overrides sf0-sf8)
sf32.pak - Patch content (overrides all)
```

**Loading Order:**
1. Scan all PAK files in `/pak` directory
2. Build file index with highest PAK number winning
3. Cache index in `pakdata.dat` for fast subsequent loads

### pakdata.dat Format

Binary cache of PAK file structure:

```
[Version: 4 bytes]
[PAK Count: 4 bytes]
For each PAK:
  [PAK Filename: null-terminated string]
  [File Count: 4 bytes]
  For each file:
    [File Path: null-terminated string]
    [File Offset: 4 bytes]
    [File Size: 4 bytes]
    [Compression: 1 byte]
```

**Purpose:** Avoid re-scanning PAK files on each application launch (scanning takes 10-30 seconds).

---

## Data Type Specifications

### Primitive Types

| C# Type  | Size | Range                    | Usage                          |
|----------|------|--------------------------|--------------------------------|
| `byte`   | 1    | 0-255                    | Flags, small IDs, percentages  |
| `sbyte`  | 1    | -128 to 127              | Signed small values            |
| `ushort` | 2    | 0-65535                  | IDs, damage, stats             |
| `short`  | 2    | -32768 to 32767          | Signed stats, bonuses          |
| `uint`   | 4    | 0-4294967295             | Large values, timestamps       |
| `int`    | 4    | -2147483648 to 2147483647| Signed large values            |
| `float`  | 4    | IEEE 754                 | Positions, rotations           |

### Fixed Buffers

Used for strings and arrays:

```csharp
public fixed byte Handle[50];    // 50-byte string buffer
public fixed byte Content[512];  // 512-byte text content
```

**Null-Termination:**
Strings are null-terminated within the buffer:
```
"Hello\0\0\0\0\0..." (remaining bytes are garbage or zeros)
```

### Encoding

Text uses legacy Windows code pages:

| Language ID | Encoding      | Code Page | Usage                    |
|-------------|---------------|-----------|--------------------------|
| 0           | Windows-1252  | 1252      | English, German, French  |
| 5           | Windows-1251  | 1251      | Russian, Cyrillic        |
| 6           | Windows-1250  | 1250      | Polish, Central European |

**Decoding Example:**
```csharp
Encoding encoding = languageID switch
{
    5 => Encoding.GetEncoding(1251),
    6 => Encoding.GetEncoding(1250),
    _ => Encoding.GetEncoding(1252)
};

fixed (byte* ptr = buffer)
{
    string text = encoding.GetString(ptr, bufferSize);
    // Trim null terminator
    int nullIndex = text.IndexOf('\0');
    if (nullIndex >= 0)
        text = text.Substring(0, nullIndex);
}
```

---

## Encoding & Text Handling

### Category 2016: Text Data

Most complex category due to variable encoding:

```csharp
[StructLayout(LayoutKind.Sequential, Pack = 1)]
public unsafe struct Category2016Item
{
    public ushort TextID;        // 2 bytes - Primary ID
    public byte LanguageID;      // 1 byte  - Sub-ID (language)
    public byte Mode;            // 1 byte  - Text mode/format
    public fixed byte Handle[50];   // 50 bytes - Text identifier
    public fixed byte Content[512]; // 512 bytes - Actual text
}
// Total: 566 bytes
```

### Language IDs

| ID | Language           | Encoding      |
|----|--------------------|---------------|
| 0  | English            | Windows-1252  |
| 1  | German             | Windows-1252  |
| 2  | French             | Windows-1252  |
| 3  | Spanish            | Windows-1252  |
| 4  | Italian            | Windows-1252  |
| 5  | Russian            | Windows-1251  |
| 6  | Polish             | Windows-1250  |

### Text Extraction

```csharp
public string GetContentString()
{
    Encoding encoding;
    switch (LanguageID)
    {
        case 5:
            encoding = Encoding.GetEncoding(1251);  // Russian
            break;
        case 6:
            encoding = Encoding.GetEncoding(1250);  // Polish
            break;
        default:
            encoding = Encoding.GetEncoding(1252);  // Western European
            break;
    }

    fixed (byte* s = Content)
    {
        string text = encoding.GetString(s, 512);
        // Find null terminator
        int nullIndex = text.IndexOf('\0');
        if (nullIndex >= 0)
            return text.Substring(0, nullIndex);
        return text;
    }
}
```

### Text Insertion

```csharp
public unsafe void SetContentString(string text, byte languageID)
{
    Encoding encoding = GetEncodingForLanguage(languageID);
    byte[] bytes = encoding.GetBytes(text);
    
    if (bytes.Length > 512)
        throw new Exception("Text too long (max 512 bytes)");
    
    fixed (byte* dest = Content)
    {
        // Copy text bytes
        for (int i = 0; i < bytes.Length; i++)
            dest[i] = bytes[i];
        
        // Null-terminate
        if (bytes.Length < 512)
            dest[bytes.Length] = 0;
    }
}
```

### Handle vs Content

- **Handle:** Short identifier (max 50 bytes), used for lookups
- **Content:** Actual text content (max 512 bytes), displayed to user

**Example:**
```
Handle:  "item_sword_iron"
Content: "Iron Sword"
```

---

## Binary Reading/Writing Examples

### Reading a Category

```csharp
public bool Load(SFChunkFile file)
{
    // 1. Find chunk by category ID
    if(!file.GetChunkSpanByID(GetCategoryID(), out int type, out int start, out int length))
        return true;  // Category not present
    
    // 2. Validate chunk type
    if(type != GetCategoryType())
        return false;
    
    // 3. Calculate item count
    int item_count;
    unsafe { item_count = length / sizeof(T); }
    
    // 4. Resize list
    CollectionsMarshal.SetCount(Items, item_count);
    
    // 5. Get memory span
    Span<T> items_span = CollectionsMarshal.AsSpan(Items);
    Span<byte> items_span_raw = MemoryMarshal.Cast<T, byte>(items_span);
    
    // 6. Read directly into memory
    file.stream.Position = start;
    file.stream.Read(items_span_raw);
    
    return true;
}
```

### Writing a Category

```csharp
public bool Save(SFChunkFile sfcf)
{
    if(Items.Count == 0)
        return true;  // Skip empty categories
    
    // 1. Get memory span
    Span<T> items_span = CollectionsMarshal.AsSpan(Items);
    ReadOnlySpan<byte> items_span_raw = MemoryMarshal.Cast<T, byte>(items_span);
    
    // 2. Add chunk to file
    sfcf.AddChunk(
        chunkID: GetCategoryID(),
        occurrence: 0,
        compressed: false,
        dataType: GetCategoryType(),
        data: items_span_raw
    );
    
    return true;
}
```

---

## Validation & Integrity

### Checksum

The file header contains a checksum field, but it's **not validated** by the game or editor:

```csharp
public int Checksum;  // Usually 0, not checked
```

### Magic Number

Only validation performed:

```csharp
if (header.Magic != -579674862)
{
    LogUtils.Log.Error("Invalid file format");
    return -3;
}
```

### Struct Size Validation

Ensure chunk data size is a multiple of struct size:

```csharp
if (chunkDataSize % sizeof(T) != 0)
{
    LogUtils.Log.Error("Chunk data size mismatch");
    return false;
}
```

---

## Performance Characteristics

### Load Performance

| Operation              | Time (typical) | Notes                          |
|------------------------|----------------|--------------------------------|
| Open file              | < 1 ms         | File handle acquisition        |
| Parse header           | < 1 ms         | 20 bytes                       |
| Load all categories    | 100-500 ms     | ~50 categories, 50K items      |
| Build lookup indices   | 50-100 ms      | Multi-valued categories        |
| **Total Load Time**    | **< 1 second** | For typical GameData.cff       |

### Save Performance

| Operation              | Time (typical) | Notes                          |
|------------------------|----------------|--------------------------------|
| Serialize categories   | 100-300 ms     | Memory → byte spans            |
| Write to disk          | 200-500 ms     | Depends on disk speed          |
| **Total Save Time**    | **< 1 second** | For typical GameData.cff       |

### Memory Usage

| Component              | Memory         | Notes                          |
|------------------------|----------------|--------------------------------|
| GameData.cff (loaded)  | 10-20 MB       | All categories in memory       |
| Undo/redo queue        | 1-5 MB         | Depends on edit history        |
| UI controls            | 5-10 MB        | WinForms overhead              |
| **Total Application**  | **50-100 MB**  | Typical working set            |

---

## Appendix: Hex Dump Examples

### GameData.cff Header

```
Offset  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  ASCII
------  -----------------------------------------------  ----------------
0x0000  12 5E 5E DD 03 00 00 00 00 00 00 00 00 00 00 00  .^^.............
0x0010  00 00 00 00                                      ....
```

**Decoded:**
- Magic: `0xDD5E5E12` (little-endian)
- Format: `0x00000003` (3)
- Type: `0x00000000` (GameData)
- Version: `0x00000000` (0)
- Checksum: `0x00000000` (0)

### Category 2015 Chunk Header

```
Offset  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  ASCII
------  -----------------------------------------------  ----------------
0x0014  DF 07 00 00 00 02 00 00 10 00                    ..........
```

**Decoded:**
- ChunkID: `0x07DF` (2015)
- Occurrence: `0x0000` (0)
- Compressed: `0x00` (false)
- DataType: `0x0002` (2 = single)
- DataSize: `0x00001000` (4096 bytes = 256 items × 16 bytes)

### Category 2015 Item Data

```
Offset  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  ASCII
------  -----------------------------------------------  ----------------
0x001E  7B 00 0A 00 0F 00 00 00 01 00 64 00 01 00 01 00  {.........d.....
```

**Decoded (Category2015Item):**
- ItemID: `0x007B` (123)
- MinDamage: `0x000A` (10)
- MaxDamage: `0x000F` (15)
- MinRange: `0x0000` (0)
- MaxRange: `0x0001` (1)
- WeaponSpeed: `0x0064` (100)
- WeaponType: `0x0001` (1)
- WeaponMaterial: `0x0001` (1)

---

**This specification provides the foundation for implementing custom tools to read, write, and manipulate SpellForce binary files.**
