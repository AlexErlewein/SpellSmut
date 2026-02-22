# File Format Specifications

This document describes the binary file formats used by SpellForce games. Understanding these formats is essential for extending the editor or working with game files directly.

## Table of Contents

1. [Chunk File Format](#chunk-file-format)
2. [GameData.cff Format](#gamedatacff-format)
3. [Map File Format](#map-file-format)
4. [PAK Archive Format](#pak-archive-format)
5. [Lua Bytecode Format](#lua-bytecode-format)
6. [Model Format (.msb)](#model-format-msb)
7. [Texture Formats](#texture-formats)

## Chunk File Format

The chunk file format is the foundation for all SpellForce binary files.

### File Header

```
Offset | Size | Type    | Description
-------|------|---------|-------------------
0x00   | 4    | int     | Magic: 0xDD5E5E12 (-579674862)
0x04   | 4    | int     | Format version (varies by type)
0x08   | 4    | int     | Type (1=map, 0=gamedata, 2=save)
0x0C   | 4    | int     | Version (usually 0)
0x10   | 4    | int     | Checksum (usually 0)
```

**Total Header Size**: 20 bytes

### Chunk Structure

After the header, chunks are stored sequentially:

```
Offset | Size | Type    | Description
-------|------|---------|-------------------
0x00   | 2    | short   | Chunk ID (identifies data type)
0x02   | 2    | short   | Occurrence ID (for multiple chunks with same ID)
0x04   | 2    | short   | Flags (bit 0: is_compressed)
0x06   | 4    | int     | Data size (uncompressed)
0x0A   | 2    | short   | Data type (category-specific)
+0x0C  | varies | -      | Data (compressed or raw)
```

**If compressed** (Format version 3):
- Additional 2 bytes: compressed size
- 2 bytes: Adler-32 checksum
- Compression: DEFLATE (RFC 1951)

### Implementation

See: `SFEngine/SFChunk/SFChunkFile.cs`

## GameData.cff Format

The `GameData.cff` file contains the master game database with 66+ categories.

### File Properties

- **Format Version**: 2
- **Type**: 0 (gamedata)
- **Compression**: Yes (most chunks)

### Category Chunks

Each category has a unique ID:

| ID   | Name                          | Type | Description |
|------|-------------------------------|------|-------------|
| 2001 | Army building requirements    | 3    | Building prerequisites |
| 2002 | Spell data                    | 3    | Spells and effects |
| 2003 | Items (general)               | 3    | Base item data |
| 2004 | Item types                    | 2    | Item categorization |
| 2005 | Unit stats                    | 3    | Unit attributes |
| 2006 | Player avatars                | 2    | Character data |
| 2012 | Item sets                     | 2    | Item sets |
| 2013 | Item armor data               | 3    | Armor stats |
| 2014 | Item shield data              | 3    | Shield stats |
| 2015 | Item weapon data              | 3    | Weapon stats |
| 2016 | Text data                     | 3    | Localized strings |
| 2017 | Item spell data               | 3    | Spell items |
| 2018 | Item potion data              | 3    | Potion items |
| 2022 | Race data                     | 2    | Race definitions |
| 2023 | Buildings - requirements      | 3    | Building requirements |
| 2024 | Unit types                    | 3    | Unit templates |
| 2025 | Unit equipment                | 3    | Starting equipment |
| 2028 | Interactive objects           | 3    | Object definitions |
| 2029 | Buildings                     | 3    | Building types |
| 2030 | Building commands             | 3    | Building actions |
| 2031 | Building upgrades             | 3    | Upgrade paths |
| 2032 | Quest information             | 3    | Quest data |
| 2036 | Spell descriptions            | 3    | Spell tooltips |
| 2039 | Skills                        | 3    | Skill definitions |
| 2040 | Item projectile               | 3    | Projectile items |
| 2041 | Merchants                     | 3    | Shop data |
| 2042 | Spell info                    | 3    | Spell metadata |
| 2044 | Building hero spawn           | 3    | Hero spawn data |
| 2047 | Item ammo                     | 3    | Ammunition items |
| 2048 | Building worker               | 3    | Worker units |
| 2049 | Item bound weapon             | 3    | Bound weapons |
| 2050 | Objects                       | 3    | Placeable objects |
| 2051 | Spell buttons                 | 3    | UI spell buttons |
| 2052 | Maps                          | 3    | Map information |
| 2053 | Spell cooldown                | 3    | Cooldown data |
| 2054 | Spell lines                   | 3    | Spell progression |
| 2055 | Building maps                 | 3    | Building placements |
| 2056 | Spell auto-cast               | 3    | Auto-cast settings |
| 2057 | Worker commands               | 3    | Worker actions |
| 2058 | Descriptions                  | 3    | Text descriptions |
| 2059 | Spell requirements            | 3    | Spell prerequisites |
| 2061 | Item gen data                 | 3    | Generic items |
| 2062 | Spell attack types            | 3    | Attack bonuses |
| 2063 | Spell info 2                  | 3    | More spell data |
| 2064 | Spell radius                  | 3    | Area spells |
| 2065 | Spell aura                    | 3    | Aura spells |
| 2067 | Worker workers                | 3    | Worker counts |
| 2072 | Building construction          | 3    | Build times |

### Data Types

Categories use one of two data types:

**Type 2**: Single item per ID
```
[Item1 struct]
[Item2 struct]
...
```

**Type 3**: Multiple items per ID
```
[Item1-SubItem1 struct]
[Item1-SubItem2 struct]
[Item2-SubItem1 struct]
...
```

### Implementation

See: `SFEngine/SFCFF/SFGameDataNew.cs`

## Map File Format

Map files use Format Version 3 and contain terrain, entities, and metadata.

### File Properties

- **Format Version**: 3
- **Type**: 1 (map)
- **Compression**: Yes (all chunks)

### Map Chunks

| ID | Name                     | Description |
|----|--------------------------|-------------|
| 2  | Tile data                | Terrain type per tile |
| 3  | Tile definitions         | Texture/property data |
| 4  | Texture IDs              | Texture assignments |
| 6  | Heightmap rows           | Elevation data (one per row) |
| 11 | Buildings                | Placed buildings |
| 12 | Units                    | Placed units |
| 29 | Objects                  | Interactive objects |
| 30 | Interactive objects      | Special objects |
| 31 | Decal assignments        | Decoration placement |
| 32 | Decal groups             | Decoration definitions |
| 35 | Portals                  | Map portals |
| 40 | Lakes                    | Water bodies |
| 42 | Movement flags           | Blocked tiles |
| 44 | Weather                  | Weather settings |
| 46 | Unit groups              | Unit groupings |
| 53 | Team compositions        | Multiplayer teams |
| 55 | Player spawns            | Spawn points |
| 56 | Vision flags             | Fog of war |
| 59 | Coop spawn params        | Coop settings |
| 60 | Additional flags         | More flag data |

### Terrain Data

**Chunk 2** - Tile Data:
```
Size (int16)
Padding (byte)
Tiles (byte[size * size])
```

**Chunk 6** - Heightmap:
- One chunk per map row
- Contains `size * 2` bytes (uint16 per tile)
- Elevation in units above/below 0

### Entity Data

**Buildings** (Chunk 11):
```
X (int16)
Y (int16)
Angle (int16)
NPC ID (int16)
Building Type (byte)
Level (byte)
Race ID (byte)
```

**Units** (Chunk 12):
```
X (int16)
Y (int16)
Flags (int16)
Unit ID (int16)
NPC ID (uint16)
Unknown (uint16)
Group (byte)
Unknown2 (byte)
```

**Objects** (Chunk 29):
```
X (int16)
Y (int16)
Object ID (int16)
Angle (int16)
NPC ID (uint16)
Unknown1 (uint16)
Spawn/Int Data (int32)
```

### Implementation

See: `SFEngine/SFMap/SFMap.cs`

## PAK Archive Format

PAK files are compressed archives containing game assets.

### File Structure

```
[File Entry 1]
  ├─ Hash (uint32)
  ├─ Offset (uint32)
  └─ Size (uint32)
[File Entry 2]
  ...
[Data Start Offset]
  ├─ File 1 data (compressed)
  ├─ File 2 data (compressed)
  └─ ...
```

### File Entry

```
Offset | Size  | Type    | Description
-------|-------|---------|-------------------
0x00   | 4     | uint    | Name hash (FNV-1)
0x04   | 4     | uint    | Data offset
0x08   | 4     | uint    | Compressed size
```

**Entry Size**: 12 bytes

### Hash Algorithm

```
hash = 0
for each byte c in filename:
    hash = (hash * 16777619) XOR c
```

### Compression

- Algorithm: ZLIB (RFC 1950)
- Most files are compressed
- Some small files are uncompressed

### Implementation

See: `SFEngine/SFUnPak/SFPakFileSystem.cs`

## Lua Bytecode Format

SpellForce uses Lua 4.01 bytecode for game scripts.

### File Structure

```
Header (12 bytes)
  ├─ Magic: 0x1B4C7561 ("Lua\x1B")
  ├─ Version: 0x34 (Lua 4.0)
  ├─ Format: 0
  └─ Endianness flag

Function Header
  ├─ Source name (string)
  ├─ Line defined (int)
  ├─ Last line defined (int)
  ├─ Number of upvalues (byte)
  ├─ Number of parameters (byte)
  ├─ Is vararg (byte)
  ├─ Max stack size (byte)

Code
  ├─ Instructions (bytecode array)
  ├─ Constants (numbers/strings)
  └─ Nested functions
```

### Instruction Format

```
[OpCode (byte)]
[Arguments (varies by opcode)]
```

### Common Opcodes

| OpCode | Name              | Description |
|--------|-------------------|-------------|
| 0      | OP_MOVE           | Copy register |
| 1      | OP_LOADK          | Load constant |
| 2      | OP_LOADBOOL       | Load boolean |
| 3      | OP_LOADNIL        | Load nil |
| 4      | OP_GETUPVAL       | Get upvalue |
| 5      | OP_GETGLOBAL      | Get global |
| 6      | OP_GETTABLE       | Get table field |
| 7      | OP_SETGLOBAL      | Set global |
| 8      | OP_SETUPVAL       | Set upvalue |
| 9      | OP_SETTABLE       | Set table field |
| 10     | OP_NEWTABLE       | Create table |
| 11     | OP_SELF           | Method call setup |
| 12     | OP_ADD            | Addition |
| 13     | OP_SUB            | Subtraction |
| 14     | OP_MUL            | Multiplication |
| 15     | OP_DIV            | Division |
| 16     | OP_POW            | Power |
| 17     | OP_UNM            | Unary minus |
| 18     | OP_NOT            | Logical NOT |
| 19     | OP_CONCAT         | String concatenation |
| 20     | OP_JMP            | Jump |
| 21     | OP_JMPNE          | Jump if not equal |
| 22     | OP_JMPEQ          | Jump if equal |
| ...    | ...              | ... |

### Implementation

See: `SFEngine/SFLua/LuaDecompiler/Decompiler.cs`

## Model Format (.msb)

The `.msb` format contains 3D model data.

### File Structure

```
Header
  ├─ Magic: "MSB\x01"
  ├─ Version
  └─ Flags

Submeshes
  ├─ Vertex count
  ├─ Triangle count
  ├─ Vertices (position, normal, UV, color)
  └─ Indices

Skeleton (optional)
  ├─ Bone count
  └─ Bone hierarchy
```

### Implementation

See: `SFEngine/SF3D/SFModel3D.cs`

## Texture Formats

### DDS Format

DirectDraw Surface format, used for most game textures.

**Structure**:
- DDS header (124 bytes)
- Pixel data (compressed: DXT1, DXT5, etc.)

### TGA Format

Targa format, used for some UI textures.

**Structure**:
- TGA header
- Pixel data (uncompressed: RGB, RGBA)

### Implementation

See: `SFEngine/SF3D/SFTexture.cs`

## Endianness

All multi-byte values are **little-endian**.

## Compression

- **GameData.cff**: DEFLATE (zlib)
- **Maps**: DEFLATE (zlib)
- **PAK files**: ZLIB

## Checksums

- **Chunk files**: Adler-32 (for compressed chunks)
- **PAK files**: None (hash-based lookup only)

## Tools

### Built-in Tools

The editor includes viewers/editors for:
- GameData.cff editor
- Map editor
- Asset viewer
- Lua decompiler

### External Tools

- **Hex Editor**: For inspecting binary files
- **DDS Viewer**: For viewing textures
- **3D Model Viewer**: For viewing .msb files

## References

- [DEFLATE Specification](https://tools.ietf.org/html/rfc1951)
- [ZLIB Specification](https://tools.ietf.org/html/rfc1950)
- [Lua 4.0 Manual](https://www.lua.org/manual/4.0/)

---

**Next**: See [Chunk Format Details](chunk-format.md) for in-depth chunk file documentation.
