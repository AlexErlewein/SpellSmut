# Chunk File Format - Detailed Specification

This document provides in-depth technical details about the chunk-based binary file format used throughout SpellForce.

## Table of Contents

1. [Format Overview](#format-overview)
2. [File Header](#file-header)
3. [Chunk Structure](#chunk-structure)
4. [Compression](#compression)
5. [Chunk Types](#chunk-types)
6. [Parsing Implementation](#parsing-implementation)
7. [Writing Chunks](#writing-chunks)

## Format Overview

The chunk file format is a container format that stores multiple independent chunks of binary data. Each chunk has:
- A unique identifier (Chunk ID)
- An optional occurrence number (for duplicates)
- Compression flags
- Data type information
- Raw or compressed binary payload

### Format Versions

| Version | Usage | Chunk Header Size |
|---------|-------|-------------------|
| 2 | GameData.cff | 12 bytes |
| 3 | Map files | 12 or 16 bytes |

## File Header

### Header Fields

```
Offset | Size | Type   | Value | Description
-------|----- ---------|-------|-------------------
0x00   | 4    | int     | 0xDD5E5E12 | Magic number
0x04   | 4    | int     | 2 or 3 | Format version
0x08   | 4    | int     | 0, 1, 2 | File type
0x0C   | 4    | int     | 0 | Version
0x10   | 4    | int     | 0 | Checksum (unused)
```

### Magic Number

```
Decimal: -579674862
Hex: 0xDD5E5E12
Bytes: 0xDD 0x5E 0x5E 0x12 (little-endian)
```

### File Types

| Value | Type | Usage |
|-------|------|-------|
| 0 | GameData | GameData.cff files |
| 1 | Map | .map files |
| 2 | Save | Save game files |

## Chunk Structure

### Uncompressed Chunk (Format 2)

```
Offset | Size | Type   | Description
-------|------|--------|-------------------
0x00   | 2    | short  | Chunk ID
0x02   | 2    | short  | Chunk Occurrence
0x04   | 2    | short  | Flags (0 = uncompressed)
0x06   | 4    | int    | Data Length
0x0A   | 2    | short  | Data Type
0x0C   | N    | byte[] | Raw Data
```

**Total Header**: 12 bytes

### Compressed Chunk (Format 3)

```
Offset | Size | Type   | Description
-------|------|--------|-------------------
0x00   | 2    | short  | Chunk ID
0x02   | 2    | short  | Chunk Occurrence
0x04   | 2    | short  | Flags (1 = compressed)
0x06   | 4    | int    | Original Data Length
0x0A   | 2    | short  | Data Type
0x0C   | 4    | int    | Compressed Data Length
0x10   | 2    | byte   | ZLIB Header (120, 156)
0x12   | N-2  | byte[] | Compressed Data
0x0C+N | 4    | int    | Adler-32 Checksum
```

**Total Header**: 16 bytes

### Chunk Fields

**Chunk ID**: Short integer identifying the data type
- Categories: 2001-2072 (GameData.cff)
- Map chunks: 2-60, 8000+

**Chunk Occurrence**: Short integer for duplicate chunks
- Usually 0
- Used for multiple chunks with same ID (e.g., heightmap rows)

**Flags**: Bitfield
```
Bit 0: Is compressed (1 = compressed, 0 = raw)
```

**Data Length**: Size of uncompressed data in bytes

**Compressed Data Length**: Size of compressed payload (Format 3 only)

**Data Type**: Category-specific data format
- Varies by chunk ID
- Used for versioning within chunks

## Compression

### Algorithm

- **Method**: DEFLATE (RFC 1951)
- **Wrapper**: ZLIB (RFC 1950)
- **Header**: 0x78 0x9C (default compression)

### Compression Process

```
1. Generate raw binary data
2. Compress using DEFLATE
3. Prepend ZLIB header (0x78 0x9C)
4. Calculate Adler-32 checksum of original data
5. Append checksum (little-endian)
```

### Decompression Process

```
1. Read chunk header
2. Read compressed data (excluding checksum)
3. Verify Adler-32 checksum
4. Decompress using ZLIB inflater
5. Return original data
```

### Checksum

**Adler-32** of the original (uncompressed) data:
```
A = 1 + D1 + D2 + ... + DN (mod 65521)
B = 1 + A + (A+1) + ... + (A+N-1) (mod 65521)
Checksum = (B << 16) | A
```

Stored as little-endian uint32 after compressed data.

## Chunk Types

### GameData.cff Chunks

| ID | Category | Data Type | Item Size | Description |
|----|----------|-----------|-----------|-------------|
| 2001 | Army building requirements | 3 | varies | Building prereqs |
| 2002 | Spells | 3 | 60 | Spell definitions |
| 2003 | Items | 3 | varies | Base item data |
| 2015 | Weapons | 2 | 16 | Weapon stats |
| 2016 | Text | 3 | 563 | Localized strings |
| ... | ... | ... | ... | ... |

### Map Chunks

| ID | Name | Data Type | Description |
|----|------|-----------|-------------|
| 2 | Tiles | 6 | Terrain type per tile |
| 3 | Tile Defs | 3 | Tile properties |
| 4 | Textures | 4 | Texture assignments |
| 6 | Heightmap | 6 | Elevation data |
| 11 | Buildings | 3 | Placed buildings |
| 12 | Units | 5 | Placed units |
| 29 | Objects | 6-7 | Interactive objects |
| ... | ... | ... | ... |

### Data Types

Categories use one of two organizational patterns:

**Type 2**: Single item per ID (simple array)
```
[Item with ID 1]
[Item with ID 2]
[Item with ID 3]
...
```

**Type 3**: Multiple items per ID (indexed array)
```
[Item with ID 1, SubItem 0]
[Item with ID 1, SubItem 1]
[Item with ID 1, SubItem 2]
[Item with ID 2, SubItem 0]
...
```

## Parsing Implementation

### Reading the Header

```csharp
public class SFChunkFileHeader
{
    public int Magic;
    public int Format;
    public int Type;
    public int Version;
    public int Checksum;

    public bool IsValid()
    {
        return Magic == -579674862;
    }

    public void Read(BinaryReader br)
    {
        Magic = br.ReadInt32();
        Format = br.ReadInt32();
        Type = br.ReadInt32();
        Version = br.ReadInt32();
        Checksum = br.ReadInt32();
    }
}
```

### Building the Lookup Table

```csharp
public void GenerateLookupDict()
{
    lookup_dict = new Dictionary<SFChunkLookupKey, long>();
    br.BaseStream.Position = 20; // Skip header

    while (br.BaseStream.Position < br.BaseStream.Length)
    {
        long offset = br.BaseStream.Position;
        SFChunkFileChunkHeader header = ReadChunkHeader(br, false);

        // Validate chunk
        if ((header.ChunkDataLength < 0) ||
            (br.BaseStream.Position + header_size + header.ChunkDataLength > br.BaseStream.Length))
        {
            break; // Malformed chunk
        }

        lookup_dict.Add(new SFChunkLookupKey(header.ChunkID, header.ChunkOccurence), offset);

        // Skip to next chunk
        br.BaseStream.Position += header_size + header.ChunkDataLength;
    }
}
```

### Reading a Chunk

```csharp
public SFChunkFileChunk GetChunkByID(short id, short occ_id = 0)
{
    SFChunkLookupKey key = new SFChunkLookupKey(id, occ_id);
    if (!lookup_dict.ContainsKey(key))
    {
        return null;
    }

    br.BaseStream.Position = lookup_dict[key];
    SFChunkFileChunk chunk = new SFChunkFileChunk();
    chunk.Read(br);
    return chunk;
}
```

### Decompressing Chunk Data

```csharp
public byte[] GetData()
{
    byte[] data;
    if (header.IsCompressed)
    {
        // Skip ZLIB header (0x78 0x9C)
        MemoryStream compressed = new MemoryStream(compressed_data, 2, compressed_data.Length - 2);

        using (DeflateStream inflater = new DeflateStream(compressed, CompressionMode.Decompress))
        using (MemoryStream decompressed = new MemoryStream())
        {
            inflater.CopyTo(decompressed);
            data = decompressed.ToArray();
        }
    }
    else
    {
        data = raw_data;
    }
    return data;
}
```

## Writing Chunks

### Creating a New File

```csharp
public int CreateFile(string filename, SFChunkFileType type)
{
    stream = new FileStream(filename, FileMode.Create, FileAccess.Write);

    header = new SFChunkFileHeader();
    header.Magic = -579674862;
    header.Format = (type == SFChunkFileType.MAP) ? 3 : 2;
    header.Type = (int)type;
    header.Version = 0;
    header.Checksum = 0;

    header.Write(bw);
    return 0;
}
```

### Adding a Chunk

```csharp
public void AddChunk(short chunk_id, short occ_id, bool is_compressed,
                     short data_type, ReadOnlySpan<byte> raw_data)
{
    if (is_compressed)
    {
        // Compress data
        using (MemoryStream ms_dest = new MemoryStream())
        {
            using (var ms_src = new UnmanagedMemoryStream(raw_data))
            using (var ds = new DeflateStream(ms_dest, CompressionMode.Compress))
            {
                ms_src.CopyTo(ds);
            }
            compressed_data = ms_dest.ToArray();
        }

        // Calculate checksum
        byte[] checksum = BitConverter.GetBytes(
            Utility.CalculateAdler32Checksum(raw_data)
        ).Reverse().ToArray();

        // Write chunk
        bw.Write(chunk_id);
        bw.Write(occ_id);
        bw.Write((short)1); // compressed flag
        bw.Write(compressed_data.Length + 6);
        bw.Write(data_type);
        bw.Write(raw_data.Length);
        bw.Write((byte)120); // ZLIB header
        bw.Write((byte)156);
        bw.Write(compressed_data);
        bw.Write(checksum);
    }
    else
    {
        // Write uncompressed chunk
        bw.Write(chunk_id);
        bw.Write(occ_id);
        bw.Write((short)0); // uncompressed flag
        bw.Write(raw_data.Length);
        bw.Write(data_type);
        bw.Write(raw_data);
    }
}
```

## Common Patterns

### Chunk Lookup Key

```csharp
public struct SFChunkLookupKey
{
    public short ChunkID;
    public short ChunkOccurence;

    public SFChunkLookupKey(short id, short occ)
    {
        ChunkID = id;
        ChunkOccurence = occ;
    }

    public override bool Equals(object obj)
    {
        return (obj is SFChunkLookupKey) &&
               ((SFChunkLookupKey)obj).ChunkID == ChunkID &&
               ((SFChunkLookupKey)obj).ChunkOccurence == ChunkOccurence;
    }

    public override int GetHashCode()
    {
        return ((ChunkID << 16) + ChunkOccurence).GetHashCode();
    }
}
```

### Error Handling

```csharp
// Validate magic number
if (!header.IsValid())
{
    LogUtils.Log.Error(LogUtils.LogSource.SFChunkFile,
                      "Invalid file header");
    return -1;
}

// Validate chunk integrity
if (offset + size > file_length)
{
    LogUtils.Log.Warning(LogUtils.LogSource.SFChunkFile,
                        "Chunk exceeds file boundary");
    break;
}

// Validate compression
if (decompressed_size != expected_size)
{
    LogUtils.Log.Error(LogUtils.LogSource.SFChunkFile,
                      "Decompression size mismatch");
    return -1;
}
```

## Performance Considerations

### Lookup Table

Building a lookup table at load time enables O(1) chunk access:

```csharp
// Without lookup table: O(n) scan
// With lookup table: O(1) hash lookup
```

### Memory-Mapped Files

For large files, memory-mapping reduces memory usage:

```csharp
using (var mmf = MemoryMappedFile.CreateFromFile(filename))
{
    using (var accessor = mmf.CreateViewAccessor())
    {
        // Read chunks on demand
    }
}
```

### Lazy Decompression

Defer decompression until data is actually needed:

```csharp
private byte[] _decompressedData = null;

public byte[] Data
{
    get
    {
        if (_decompressedData == null)
        {
            _decompressedData = Decompress();
        }
        return _decompressedData;
    }
}
```

## Implementation Reference

| File | Description |
|------|-------------|
| `SFEngine/SFChunk/SFChunkFile.cs` | Main file parser |
| `SFEngine/SFChunk/SFChunkFileChunk.cs` | Chunk representation |
| `SFEngine/Utility.cs` | Checksum calculation |

---

**Related**: [File Format Specifications](README.md)
