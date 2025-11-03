# SpellForce Map Viewer - Phase 2 Texture Analysis

## Document Information
- **Version**: 1.0.0
- **Created**: 2024-11-03
- **Phase**: Phase 2, Week 1
- **Status**: Analysis Complete ✅
- **Purpose**: Document texture format findings from C# code analysis

---

## Executive Summary

**Status**: ✅ Texture format successfully reverse-engineered from C# source code

**Key Findings**:
1. Textures stored in **Chunk 3** (tile definitions) and **Chunk 4** (texture IDs)
2. 255 tile definitions with **3-layer blending** (ind1/ind2/ind3 + weights)
3. Texture files are **DDS format** stored in PAK archives
4. Naming convention: `landscape_island_XXX_*.dds` where XXX is 001-119
5. 32 base textures used per map (from pool of 119 available)

**Next Steps**: 
- ✅ Format documented
- 🔄 Implement DDS texture loader (Week 2)
- 📋 Implement chunk-based map reader (Week 2)
- 📋 Implement texture blending (Week 3)

---

## Table of Contents

1. [Texture File Format](#texture-file-format)
2. [Map Chunk Structure](#map-chunk-structure)
3. [Texture Manager Architecture](#texture-manager-architecture)
4. [Tile Blending System](#tile-blending-system)
5. [Texture Loading Process](#texture-loading-process)
6. [Implementation Plan](#implementation-plan)
7. [Code Examples](#code-examples)

---

## Texture File Format

### Texture Naming Convention

**Pattern**: `landscape_island_XXX_[description][d].dds`

**Components**:
- **Prefix**: `landscape_island_`
- **ID**: `XXX` = 001 to 119 (three-digit zero-padded)
- **Description**: Texture type (e.g., `grass`, `stone`, `mud`, `snow`)
- **Suffix**: `d` = diffuse/color texture (optional)

**Examples**:
```
landscape_island_000_worldd.dds       # Base world texture (ID 0)
landscape_island_001_grassd.dds       # Grass texture (ID 1)
landscape_island_050_stoned.dds       # Stone texture (ID 50)
landscape_island_100_snowd.dds        # Snow texture (ID 100)
```

### Texture Specifications

**Format**: DDS (DirectDraw Surface)
**Compression**: BC1 (DXT1) or BC3 (DXT5)
**Dimensions**: 256×256 pixels (confirmed from C# code)
**Color Space**: sRGB
**Mipmaps**: Yes (8 levels)

### Texture Storage

**Location**: PAK archives (specifically `sf1.pak`)
**Path in PAK**: `texture/landscape_island_XXX_*.dds`

**Total Available**: 119 terrain textures + 1 base world texture

---

## Map Chunk Structure

### Overview

SpellForce map files use a **chunk-based format** (not simple header + ZLIB as we initially thought for heightmaps).

**File Structure**:
```
┌─────────────────────────────────────┐
│ Chunk File Header                   │
├─────────────────────────────────────┤
│ Chunk 1: Unknown                    │
├─────────────────────────────────────┤
│ Chunk 2: Heightmap                  │ ← We already parse this
│  - Width, Height                    │
│  - ZLIB compressed height data      │
├─────────────────────────────────────┤
│ Chunk 3: Tile Definitions           │ ← NEW: Texture blending data
│  - 255 tiles × 14 bytes each        │
│  - 3,570 bytes total                │
├─────────────────────────────────────┤
│ Chunk 4: Texture IDs                │ ← NEW: Base texture assignments
│  - 63 bytes (texture ID array)      │
├─────────────────────────────────────┤
│ Chunk 5+: Other data                │
│  - Entities, objects, etc.          │
└─────────────────────────────────────┘
```

### Chunk 3: Tile Definitions

**Purpose**: Defines texture blending for all 255 possible tiles

**Structure**: 255 entries × 14 bytes = 3,570 bytes

**Per-Tile Format** (14 bytes):
```
Offset | Size | Type  | Name              | Description
-------|------|-------|-------------------|---------------------------
0x00   | 1    | byte  | ind1              | Base texture 1 index (0-31)
0x01   | 1    | byte  | ind2              | Base texture 2 index (0-31)
0x02   | 1    | byte  | ind3              | Base texture 3 index (0-31)
0x03   | 1    | byte  | weight1           | Blend weight 1 (0-255)
0x04   | 1    | byte  | weight2           | Blend weight 2 (0-255)
0x05   | 1    | byte  | weight3           | Blend weight 3 (0-255)
0x06   | 1    | byte  | reindex_data      | Unknown/unused
0x07   | 1    | byte  | reindex_index     | Unknown/unused
0x08   | 1    | byte  | unknown1          | Padding/unused
0x09   | 1    | byte  | unknown2          | Padding/unused
0x0A   | 1    | byte  | material_property | Material type ID
0x0B   | 1    | byte  | unknown3          | Padding/unused
0x0C   | 1    | byte  | blocks_movement   | Movement blocking flag
0x0D   | 1    | byte  | blocks_vision     | Vision blocking flag
```

**Blending Logic**:
- **ind1, ind2, ind3**: Indices into the 32 base textures (chunk 4)
- **weight1, weight2, weight3**: Blend weights (0-255)
- Weights are normalized: `final_weight = weight / (weight1 + weight2 + weight3)`
- If all indices are 0, tile is unused/undefined

**Example**:
```
Tile 50:
  ind1=5, ind2=8, ind3=12
  weight1=200, weight2=30, weight3=25
  
Interpretation: 
  - 78.4% texture 5 (grass)
  - 11.8% texture 8 (dirt)
  -  9.8% texture 12 (stone)
```

### Chunk 4: Texture IDs

**Purpose**: Maps the 32 base textures used in this map to global texture IDs

**Structure**: 63 bytes (byte array)

**Layout**:
```
Index  | Purpose
-------|--------------------------------------------------
0      | Base world texture ID (always texture 0)
1-31   | "Far" texture IDs (used for distant terrain LOD)
32-62  | "Near" texture IDs (actual terrain textures)
```

**Note**: The C# code indicates:
- Indices 1-31 are "far textures" (lower resolution for distant viewing)
- Indices 32-62 are "near textures" (full resolution)
- In practice, `near_texture_id = far_texture_id + 119`
- Exception: Index 0 is always texture 0 (base world)

**Example**:
```
texture_id[0]  = 0    # Base world texture
texture_id[1]  = 5    # Far texture: grass
texture_id[32] = 124  # Near texture: grass (5 + 119)
texture_id[2]  = 12   # Far texture: stone
texture_id[33] = 131  # Near texture: stone (12 + 119)
...
```

---

## Texture Manager Architecture

### C# Implementation Overview

From `SFMapTerrainTextureManager.cs`:

```csharp
public class SFMapTerrainTextureManager
{
    // Constants
    public const int MAX_TEXTURES = 63;           // Total texture slots
    public const int MAX_USED_TEXTURES = 32;      // Actually used (0 + 31)
    public const int MAX_TILES = 255;             // Tile definitions
    public const int TEXTURES_AVAILABLE = 119;    // Global texture pool
    
    // Data structures
    public byte[] texture_id;                     // 63 bytes from Chunk 4
    public SFMapTerrainTextureTileData[] texture_tiledata;  // 255 tiles from Chunk 3
    public SFTexture[] base_texture_bank;         // 32 loaded textures
    public SFTexture[] tile_texture_bank;         // 255 mixed textures
    
    // Tile definition structure
    public struct SFMapTerrainTextureTileData
    {
        public byte ind1, ind2, ind3;             // Texture indices
        public byte weight1, weight2, weight3;    // Blend weights
        public byte reindex_data, reindex_index;  // Unused
        public byte material_property;            // Material type
        public bool blocks_movement, blocks_vision;  // Collision flags
    }
}
```

### Tile Indexing System

**Tile Index Range**: 0-254 (255 total)

**Tile Categories**:
```
0-31    : Base textures (direct mapping to base_texture_bank[0-31])
32-223  : Mixed tiles (3-layer blended textures)
224-254 : Base textures again (mapping to base_texture_bank[1-31])
```

**Usage in Heightmap**:
- Each terrain cell has a tile index (0-254)
- Tile 0 = base world texture (usually ocean/water)
- Tiles 1-31 = pure base textures
- Tiles 32-223 = custom blended tiles
- Tiles 224-254 = another way to reference base textures

**Why Two Ranges for Base Textures?**
- Performance optimization in game engine
- Tiles 1-31: Used for "far" terrain rendering (LOD)
- Tiles 224-254: Used for "near" terrain rendering (full detail)

---

## Tile Blending System

### 3-Layer Blending

**Algorithm** (from C# code):

```csharp
// Pseudo-code for texture blending
void MixUncompressed(
    SFTexture tex1, byte weight1,
    SFTexture tex2, byte weight2,
    SFTexture tex3, byte weight3,
    ref SFTexture output)
{
    int total_weight = weight1 + weight2 + weight3;
    
    for each pixel (x, y):
        Color c1 = tex1.GetPixel(x, y);
        Color c2 = tex2.GetPixel(x, y);
        Color c3 = tex3.GetPixel(x, y);
        
        float w1 = weight1 / (float)total_weight;
        float w2 = weight2 / (float)total_weight;
        float w3 = weight3 / (float)total_weight;
        
        output.SetPixel(x, y,
            c1.r * w1 + c2.r * w2 + c3.r * w3,
            c1.g * w1 + c2.g * w2 + c3.g * w3,
            c1.b * w1 + c2.b * w2 + c3.b * w3,
            c1.a * w1 + c2.a * w2 + c3.a * w3
        );
}
```

**Shader Implementation** (for GPU):

```glsl
// Fragment shader pseudo-code
uniform sampler2DArray terrainTextures;  // 255 texture layers
uniform vec4 tileColors[255];            // Average colors for minimap

in vec2 texCoord;
in float tileIndex;

out vec4 fragColor;

void main()
{
    // Sample from texture array
    vec3 color = texture(terrainTextures, vec3(texCoord, tileIndex)).rgb;
    fragColor = vec4(color, 1.0);
}
```

**Optimization Notes**:
- Pre-blend textures on CPU (C# approach)
  - Pros: Simple shader, good for many unique blends
  - Cons: Memory intensive (255 textures × 256×256 × 4 bytes = 64 MB)
  
- Blend in shader on GPU (modern approach)
  - Pros: Less memory, more flexible
  - Cons: More complex shader, need to pass blend weights per-cell

---

## Texture Loading Process

### C# Loading Sequence

From `SFMapTerrainTextureManager.Init()`:

```
1. LoadTextureNames()
   - Query PAK archives for available textures
   - Build list of 119 texture filenames
   - Sort by ID (001-119)

2. Load 32 Base Textures
   for i in 0..31:
       texture_id_index = (i == 0) ? 0 : i + 31
       filename = GetTextureNameByID(texture_id[texture_id_index])
       base_texture_bank[i] = LoadFromPAK(filename)
       base_texture_bank[i].Uncompress()  // DXT → RGBA

3. Generate 192 Mixed Tiles (32-223)
   for i in 32..223:
       if tile_defined[i]:
           tile_texture_bank[i] = MixUncompressed(
               base_texture_bank[tiledata[i].ind1], tiledata[i].weight1,
               base_texture_bank[tiledata[i].ind2], tiledata[i].weight2,
               base_texture_bank[tiledata[i].ind3], tiledata[i].weight3
           )

4. Upload to GPU
   - Create OpenGL 2D texture array (256×256×255)
   - Upload all 255 textures as layers
   - Generate mipmaps
   - Set filtering (trilinear + anisotropic)

5. Create Uniform Buffer
   - Store average color per tile (for minimap)
   - Bind to shader uniform block
```

### Python Implementation Strategy

**Option A: Pre-blend on CPU** (C# approach)
```python
# Advantages:
- Simple to implement
- Matches C# behavior exactly
- Works with OpenGL 2.1

# Disadvantages:
- High memory usage (64 MB for textures)
- Slower initial load time
- Less flexible for editing
```

**Option B: Dynamic blending in shader** (modern approach)
```python
# Advantages:
- Lower memory usage (only 32 base textures)
- Faster load time
- More flexible (can change blend weights dynamically)

# Disadvantages:
- More complex shader code
- Requires OpenGL 3.3+ (GLSL 330)
- Need to pass per-cell blend data to GPU
```

**Recommendation**: Start with **Option A** (pre-blend on CPU) for Phase 2 to match C# behavior and work with OpenGL 2.1. Upgrade to **Option B** in Phase 3 when moving to modern OpenGL.

---

## Implementation Plan

### Week 2: Texture Loading (Nov 11-17)

#### Task 1: Chunk-Based Map Reader
**Goal**: Parse Chunks 3 and 4 from map files

**Implementation**:
```python
class ChunkMapLoader:
    """Load map files with chunk-based format"""
    
    def load_map(self, filepath):
        """
        Load map with texture data
        
        Returns:
            heightmap: numpy array
            width, height: map dimensions
            texture_ids: 63-byte array
            tile_data: 255 tile definitions
        """
        with open(filepath, 'rb') as f:
            chunks = self.parse_chunk_file(f)
            
            # Chunk 2: Heightmap (already implemented)
            heightmap, width, height = self.parse_chunk_2(chunks[2])
            
            # Chunk 3: Tile definitions (NEW)
            tile_data = self.parse_chunk_3(chunks[3])
            
            # Chunk 4: Texture IDs (NEW)
            texture_ids = self.parse_chunk_4(chunks[4])
            
        return heightmap, width, height, texture_ids, tile_data
    
    def parse_chunk_3(self, chunk_data):
        """Parse 255 tile definitions"""
        tile_data = []
        for i in range(255):
            offset = i * 14
            tile = {
                'ind1': chunk_data[offset + 0],
                'ind2': chunk_data[offset + 1],
                'ind3': chunk_data[offset + 2],
                'weight1': chunk_data[offset + 3],
                'weight2': chunk_data[offset + 4],
                'weight3': chunk_data[offset + 5],
                'reindex_data': chunk_data[offset + 6],
                'reindex_index': chunk_data[offset + 7],
                'material_property': chunk_data[offset + 10],
                'blocks_movement': (chunk_data[offset + 12] % 2) == 1,
                'blocks_vision': (chunk_data[offset + 13] % 2) == 1
            }
            tile_data.append(tile)
        return tile_data
    
    def parse_chunk_4(self, chunk_data):
        """Parse 63 texture IDs"""
        return list(chunk_data[:63])
```

**Estimated Time**: 2 days

#### Task 2: DDS Texture Loader
**Goal**: Load DDS textures and decompress to RGBA

**Dependencies**: 
- `Pillow` library with DDS support, or
- `imageio` with DDS plugin, or
- Custom DDS parser

**Implementation**:
```python
from PIL import Image
import numpy as np

class DDSTextureLoader:
    """Load DDS textures from PAK archives"""
    
    def load_texture(self, pak_path, texture_name):
        """
        Load a DDS texture from PAK
        
        Args:
            pak_path: Path to PAK archive
            texture_name: e.g., "landscape_island_050_stoned.dds"
        
        Returns:
            numpy array: RGBA texture data (256×256×4)
        """
        # Extract from PAK
        dds_data = self.extract_from_pak(pak_path, texture_name)
        
        # Load DDS
        image = Image.open(io.BytesIO(dds_data))
        
        # Convert to RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Resize if needed
        if image.size != (256, 256):
            image = image.resize((256, 256), Image.LANCZOS)
        
        # Convert to numpy array
        texture_data = np.array(image, dtype=np.uint8)
        
        return texture_data
```

**Estimated Time**: 2 days (including PAK extraction)

#### Task 3: Texture Manager
**Goal**: Manage base textures and tile blending

**Implementation**:
```python
class TextureManager:
    """Manage terrain textures and blending"""
    
    def __init__(self):
        self.texture_names = []        # 119 texture filenames
        self.texture_ids = None        # 63-byte array from map
        self.tile_data = None          # 255 tile definitions
        self.base_textures = {}        # 32 loaded RGBA textures
        self.tile_textures = {}        # 255 blended textures
    
    def load_texture_names(self, pak_path):
        """Query PAK for available texture filenames"""
        # Get list of all landscape_island_*.dds files
        all_files = self.list_pak_contents(pak_path)
        terrain_files = [f for f in all_files if 'landscape_island_' in f]
        
        # Sort by ID (001-119)
        self.texture_names = self.sort_by_id(terrain_files)
    
    def load_base_textures(self, pak_path, texture_ids):
        """Load 32 base textures for this map"""
        self.texture_ids = texture_ids
        
        for i in range(32):
            # Get texture ID
            if i == 0:
                tex_id = texture_ids[0]  # Base world
            else:
                tex_id = texture_ids[i + 31]  # Near textures
            
            # Get filename
            filename = self.texture_names[tex_id]
            
            # Load texture
            self.base_textures[i] = self.loader.load_texture(pak_path, filename)
    
    def generate_tile_textures(self, tile_data):
        """Pre-blend all 255 tile textures"""
        self.tile_data = tile_data
        
        # Tiles 0-31: Direct base textures
        for i in range(32):
            self.tile_textures[i] = self.base_textures[i]
        
        # Tiles 32-223: Mixed textures
        for i in range(32, 224):
            tile = tile_data[i]
            if tile['ind1'] == 0 and tile['ind2'] == 0 and tile['ind3'] == 0:
                continue  # Undefined tile
            
            # Blend 3 textures
            self.tile_textures[i] = self.blend_textures(
                self.base_textures[tile['ind1']], tile['weight1'],
                self.base_textures[tile['ind2']], tile['weight2'],
                self.base_textures[tile['ind3']], tile['weight3']
            )
        
        # Tiles 224-254: Base textures again
        for i in range(224, 255):
            base_idx = i - 223
            self.tile_textures[i] = self.base_textures[base_idx]
    
    def blend_textures(self, tex1, w1, tex2, w2, tex3, w3):
        """Blend 3 textures with weights"""
        total = w1 + w2 + w3
        if total == 0:
            return tex1  # Fallback
        
        # Normalize weights
        w1_norm = w1 / total
        w2_norm = w2 / total
        w3_norm = w3 / total
        
        # Blend pixels
        result = (tex1.astype(np.float32) * w1_norm +
                  tex2.astype(np.float32) * w2_norm +
                  tex3.astype(np.float32) * w3_norm)
        
        return result.astype(np.uint8)
```

**Estimated Time**: 2 days

#### Task 4: Test with Real Maps
**Goal**: Verify texture loading works

**Test Cases**:
1. Load Coop_01_rpg.map texture data
2. Verify 63 texture IDs parsed correctly
3. Verify 255 tile definitions parsed correctly
4. Load 32 base textures from PAK
5. Generate 255 blended tiles
6. Verify memory usage (<100 MB)

**Estimated Time**: 1 day

**Total Week 2**: 7 days

---

### Week 3: Texture Rendering (Nov 18-24)

#### Task 1: Generate Texture Coordinates
**Goal**: Map terrain cells to texture coordinates

**Implementation**:
```python
def generate_terrain_with_textures(self, heightmap, tile_indices):
    """
    Generate terrain mesh with texture coordinates
    
    Args:
        heightmap: height data
        tile_indices: per-cell tile index (0-254)
    
    Returns:
        vertices, texcoords, tile_ids
    """
    vertices = []
    texcoords = []
    tile_ids = []
    
    for z in range(height):
        for x in range(width):
            h = heightmap[z, x]
            tile_id = tile_indices[z, x]
            
            # Vertex position
            vertices.append([x, h, z])
            
            # Texture coordinate (world-space UVs)
            u = x / width
            v = z / height
            texcoords.append([u, v])
            
            # Tile index for this cell
            tile_ids.append(tile_id)
    
    return vertices, texcoords, tile_ids
```

#### Task 2: Upload Textures to GPU
**Goal**: Create OpenGL texture array

**Implementation**:
```python
def upload_textures_to_gpu(self):
    """Create OpenGL 2D texture array"""
    # Generate texture
    self.texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture_id)
    
    # Allocate storage for 255 layers
    glTexImage3D(
        GL_TEXTURE_2D_ARRAY,
        0,                    # Level
        GL_RGBA8,             # Internal format
        256, 256, 255,        # Width, height, layers
        0,                    # Border
        GL_RGBA,              # Format
        GL_UNSIGNED_BYTE,     # Type
        None                  # Data (allocated, not filled yet)
    )
    
    # Upload each layer
    for i, texture_data in self.tile_textures.items():
        glTexSubImage3D(
            GL_TEXTURE_2D_ARRAY,
            0,                # Level
            0, 0, i,          # Offset (x, y, layer)
            256, 256, 1,      # Size (width, height, depth)
            GL_RGBA,          # Format
            GL_UNSIGNED_BYTE, # Type
            texture_data      # Data
        )
    
    # Set filtering
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT)
    
    # Generate mipmaps
    glGenerateMipmap(GL_TEXTURE_2D_ARRAY)
```

**Note**: This requires OpenGL 3.0+ for `glTexImage3D`. For OpenGL 2.1, we'll need to use separate 2D textures or a texture atlas.

#### Task 3: Render Textured Terrain
**Goal**: Display terrain with textures

**OpenGL 2.1 Approach** (immediate mode):
```python
def render_textured_terrain(self):
    """Render terrain with textures (OpenGL 2.1)"""
    # Enable texturing
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, self.current_tile_texture)
    
    # Render terrain
    glBegin(GL_TRIANGLE_STRIP)
    for vertex, texcoord, tile_id in zip(vertices, texcoords, tile_ids):
        # Switch texture if tile changed
        if tile_id != self.current_tile:
            glEnd()
            glBindTexture(GL_TEXTURE_2D, self.tile_textures_gl[tile_id])
            glBegin(GL_TRIANGLE_STRIP)
            self.current_tile = tile_id
        
        glTexCoord2f(texcoord[0], texcoord[1])
        glVertex3f(vertex[0], vertex[1], vertex[2])
    glEnd()
```

**Performance Note**: This approach requires many texture switches. For better performance, sort triangles by tile ID, or upgrade to modern OpenGL with texture arrays.

**Estimated Time**: 3 days

---

## Code Examples

### Complete Tile Parsing Example

```python
import struct
import numpy as np

def parse_map_with_textures(filepath):
    """
    Complete example: Parse map file with textures
    """
    with open(filepath, 'rb') as f:
        # Read magic number
        magic = struct.unpack('<I', f.read(4))[0]
        if magic != 0xDD72DD12:
            raise ValueError("Invalid map file")
        
        # Read version
        version = struct.unpack('<I', f.read(4))[0]
        
        # Skip to chunk data (offset 36)
        f.seek(36)
        
        # Decompress heightmap (Chunk 2)
        compressed_data = f.read()
        heightmap_data = zlib.decompress(compressed_data)
        
        # TODO: Parse chunk structure properly
        # For now, this is pseudo-code
        
    return heightmap, texture_ids, tile_data

def blend_three_textures(tex1, w1, tex2, w2, tex3, w3):
    """
    Blend three 256x256 RGBA textures
    
    Args:
        tex1, tex2, tex3: numpy arrays (256, 256, 4) uint8
        w1, w2, w3: weights (0-255)
    
    Returns:
        numpy array: blended texture (256, 256, 4) uint8
    """
    total = w1 + w2 + w3
    if total == 0:
        return tex1  # Fallback to first texture
    
    # Normalize weights to 0-1
    w1_norm = w1 / total
    w2_norm = w2 / total
    w3_norm = w3 / total
    
    # Blend (convert to float, blend, convert back to uint8)
    result = (
        tex1.astype(np.float32) * w1_norm +
        tex2.astype(np.float32) * w2_norm +
        tex3.astype(np.float32) * w3_norm
    )
    
    return np.clip(result, 0, 255).astype(np.uint8)

# Example usage
tex1 = np.random.randint(0, 255, (256, 256, 4), dtype=np.uint8)  # Grass
tex2 = np.random.randint(0, 255, (256, 256, 4), dtype=np.uint8)  # Dirt
tex3 = np.random.randint(0, 255, (256, 256, 4), dtype=np.uint8)  # Stone

# Blend: 70% grass, 20% dirt, 10% stone
blended = blend_three_textures(
    tex1, 178,  # 70% → weight = 178 (out of 255)
    tex2, 51,   # 20% → weight = 51
    tex3, 26    # 10% → weight = 26
)
```

---

## Next Steps

### Immediate (This Week)
1. ✅ **Document texture format** (this document)
2. 🔄 **Locate test map files** with texture data
3. 🔄 **Set up PAK extraction** for accessing texture files

### Week 2 (Nov 11-17)
1. Implement chunk-based map parser
2. Implement DDS texture loader
3. Implement texture manager
4. Test with real maps

### Week 3 (Nov 18-24)
1. Generate texture coordinates
2. Upload textures to GPU
3. Render textured terrain
4. Performance optimization

---

## References

### C# Source Files Analyzed
- `SFEngine/SFMap/SFMapTerrainTextureManager.cs` - Texture management
- `SFEngine/SFMap/SFMap.cs` - Map loading, chunk parsing
- `SFMap/map_dialog/MapModifyTextureSet.cs` - Texture