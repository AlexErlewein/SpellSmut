# SpellForce Map Viewer - Phase 2 Week 2 Action Plan

## Document Information
- **Week**: Week 2 of Phase 2 (Nov 11-17, 2024)
- **Focus**: Texture Loading Implementation
- **Status**: Ready to Start
- **Created**: 2024-11-03

---

## Week Overview

**Goal**: Implement texture loading system with chunk-based map parsing and DDS texture support.

**Deliverables**:
1. ✅ Chunk-based map parser (parse Chunks 3 & 4)
2. ✅ DDS texture loader
3. ✅ Texture manager with 3-layer blending
4. ✅ Working demo with textured terrain

**Success Criteria**:
- Load texture data from real map files
- Extract textures from PAK archives
- Generate 255 blended tile textures
- Display textured terrain (even if not perfect)

---

## Daily Breakdown

### Day 1-2: Chunk-Based Map Parser

**Goal**: Parse Chunks 3 & 4 from SpellForce map files

**Tasks**:
- [ ] Implement chunk file reader
- [ ] Parse Chunk 3 (tile definitions: 255 × 14 bytes)
- [ ] Parse Chunk 4 (texture IDs: 63 bytes)
- [ ] Test with Coop_01_rpg.map
- [ ] Validate data integrity

**Files to Create**:
- `src/TirganachReloaded/map_viewer/chunk_map_loader.py`

**Implementation**:
```python
class ChunkMapLoader:
    """Load SpellForce maps with chunk-based format"""
    
    def load_map_with_textures(self, filepath):
        """
        Load map with texture data
        
        Returns:
            heightmap: numpy array (width × height)
            width, height: map dimensions
            texture_ids: list of 63 texture IDs
            tile_data: list of 255 tile definitions
        """
        pass
    
    def parse_chunk_file(self, file_handle):
        """Parse chunk file structure"""
        pass
    
    def parse_chunk_3(self, chunk_data):
        """
        Parse 255 tile definitions
        
        Each tile: 14 bytes
        - ind1, ind2, ind3: texture indices (3 bytes)
        - weight1, weight2, weight3: blend weights (3 bytes)
        - reindex_data, reindex_index: unused (2 bytes)
        - padding: (2 bytes)
        - material_property: (1 byte)
        - padding: (1 byte)
        - blocks_movement, blocks_vision: flags (2 bytes)
        """
        pass
    
    def parse_chunk_4(self, chunk_data):
        """Parse 63 texture IDs"""
        pass
```

**Test Cases**:
```python
def test_parse_chunk_3():
    loader = ChunkMapLoader()
    tile_data = loader.load_map_with_textures("test.map")
    assert len(tile_data) == 255
    assert tile_data[0]['ind1'] >= 0 and tile_data[0]['ind1'] <= 31

def test_parse_chunk_4():
    loader = ChunkMapLoader()
    _, _, _, texture_ids, _ = loader.load_map_with_textures("test.map")
    assert len(texture_ids) == 63
    assert texture_ids[0] == 0  # Base world texture
```

**Reference**: 
- `MAP_VIEWER_PHASE2_TEXTURE_ANALYSIS.md` - Chunk format specs
- C# code: `SFEngine/SFMap/SFMap.cs` lines 70-120

---

### Day 3-4: DDS Texture Loader + PAK Extraction

**Goal**: Load DDS textures from PAK archives

**Tasks**:
- [ ] Investigate PAK extraction methods
- [ ] Implement DDS texture loader (Pillow or custom)
- [ ] Test loading landscape_island_001_grassd.dds
- [ ] Verify texture dimensions (256×256)
- [ ] Convert DDS to RGBA numpy array

**Files to Create/Modify**:
- `src/TirganachReloaded/map_viewer/dds_loader.py`
- `src/TirganachReloaded/map_viewer/pak_extractor.py` (optional)

**Dependencies**:
```bash
# Option 1: Pillow with DDS support
pip install Pillow

# Option 2: imageio with DDS plugin
pip install imageio imageio-ffmpeg

# Option 3: Use existing QuickBMS tools
# (already in ModdingTools/quickbms/)
```

**Implementation**:
```python
from PIL import Image
import numpy as np
import io

class DDSLoader:
    """Load DDS textures"""
    
    def load_dds(self, dds_data_or_path):
        """
        Load DDS texture
        
        Args:
            dds_data_or_path: bytes or file path
        
        Returns:
            numpy array: (256, 256, 4) RGBA uint8
        """
        if isinstance(dds_data_or_path, bytes):
            image = Image.open(io.BytesIO(dds_data_or_path))
        else:
            image = Image.open(dds_data_or_path)
        
        # Convert to RGBA
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Ensure 256×256
        if image.size != (256, 256):
            image = image.resize((256, 256), Image.LANCZOS)
        
        return np.array(image, dtype=np.uint8)

class PAKExtractor:
    """Extract files from SpellForce PAK archives"""
    
    def __init__(self, pak_path):
        self.pak_path = pak_path
        # TODO: Implement or use QuickBMS
    
    def extract_file(self, filename):
        """
        Extract a single file from PAK
        
        Args:
            filename: e.g., "landscape_island_050_stoned.dds"
        
        Returns:
            bytes: file data
        """
        pass
    
    def list_textures(self):
        """List all landscape_island_*.dds files"""
        pass
```

**Test Cases**:
```python
def test_load_dds():
    loader = DDSLoader()
    texture = loader.load_dds("test_texture.dds")
    assert texture.shape == (256, 256, 4)
    assert texture.dtype == np.uint8

def test_pak_extraction():
    extractor = PAKExtractor("OriginalGameFiles/pak/sf1.pak")
    dds_data = extractor.extract_file("landscape_island_001_grassd.dds")
    assert len(dds_data) > 0
```

**Fallback Strategy**:
If PAK extraction is complex, use pre-extracted textures:
```bash
# Use QuickBMS to extract all textures once
cd ModdingTools/quickbms
./quickbms -o spellforce.bms ../../OriginalGameFiles/pak/sf1.pak ../../ExtractedAssets/Textures/
```

---

### Day 5-6: Texture Manager

**Goal**: Manage base textures and 3-layer blending

**Tasks**:
- [ ] Implement texture manager class
- [ ] Load 119 texture filenames
- [ ] Load 32 base textures for a map
- [ ] Implement 3-layer texture blending
- [ ] Generate all 255 tile textures
- [ ] Calculate average colors (for minimap)

**Files to Create**:
- `src/TirganachReloaded/map_viewer/texture_manager.py`

**Implementation**:
```python
class TextureManager:
    """Manage terrain textures and blending"""
    
    def __init__(self):
        self.texture_names = []           # 119 filenames
        self.texture_ids = None           # 63 bytes from map
        self.tile_data = None             # 255 tile definitions
        self.base_textures = {}           # 32 RGBA textures
        self.tile_textures = {}           # 255 blended textures
        self.tile_average_colors = {}     # For minimap
        
        self.dds_loader = DDSLoader()
        self.pak_extractor = None
    
    def load_texture_names(self, pak_path_or_dir):
        """Query available texture filenames"""
        # Get list of landscape_island_XXX_*.dds
        # Sort by ID (001-119)
        pass
    
    def load_base_textures(self, texture_ids):
        """
        Load 32 base textures for this map
        
        Args:
            texture_ids: 63-byte array from Chunk 4
        """
        self.texture_ids = texture_ids
        
        for i in range(32):
            # Get texture ID
            if i == 0:
                tex_id = texture_ids[0]      # Base world
            else:
                tex_id = texture_ids[i + 31]  # Near textures
            
            # Get filename
            filename = self.texture_names[tex_id]
            
            # Load texture
            dds_data = self.pak_extractor.extract_file(filename)
            self.base_textures[i] = self.dds_loader.load_dds(dds_data)
    
    def generate_tile_textures(self, tile_data):
        """Pre-blend all 255 tile textures"""
        self.tile_data = tile_data
        
        # Tiles 0-31: Direct base textures
        for i in range(32):
            self.tile_textures[i] = self.base_textures[i]
            self.tile_average_colors[i] = self._calc_average_color(self.base_textures[i])
        
        # Tiles 32-223: Mixed textures
        for i in range(32, 224):
            tile = tile_data[i]
            
            # Check if tile is defined
            if tile['ind1'] == 0 and tile['ind2'] == 0 and tile['ind3'] == 0:
                continue  # Skip undefined tiles
            
            # Blend 3 textures
            self.tile_textures[i] = self._blend_textures(
                self.base_textures[tile['ind1']], tile['weight1'],
                self.base_textures[tile['ind2']], tile['weight2'],
                self.base_textures[tile['ind3']], tile['weight3']
            )
            self.tile_average_colors[i] = self._calc_average_color(self.tile_textures[i])
        
        # Tiles 224-254: Base textures again
        for i in range(224, 255):
            base_idx = i - 223
            if base_idx < len(self.base_textures):
                self.tile_textures[i] = self.base_textures[base_idx]
                self.tile_average_colors[i] = self.tile_average_colors[base_idx]
    
    def _blend_textures(self, tex1, w1, tex2, w2, tex3, w3):
        """
        Blend 3 textures with weights
        
        Args:
            tex1, tex2, tex3: (256, 256, 4) uint8 arrays
            w1, w2, w3: weights (0-255)
        
        Returns:
            (256, 256, 4) uint8 array
        """
        total = w1 + w2 + w3
        if total == 0:
            return tex1  # Fallback
        
        # Normalize weights
        w1_norm = w1 / total
        w2_norm = w2 / total
        w3_norm = w3 / total
        
        # Blend (convert to float, blend, convert back)
        result = (
            tex1.astype(np.float32) * w1_norm +
            tex2.astype(np.float32) * w2_norm +
            tex3.astype(np.float32) * w3_norm
        )
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def _calc_average_color(self, texture):
        """Calculate average RGB color for minimap"""
        avg = np.mean(texture[:, :, :3], axis=(0, 1))
        return tuple(avg.astype(np.uint8))
```

**Test Cases**:
```python
def test_texture_manager():
    mgr = TextureManager()
    mgr.load_texture_names("ExtractedAssets/Textures/")
    assert len(mgr.texture_names) == 119
    
    # Load base textures
    texture_ids = [0] + list(range(1, 63))
    mgr.load_base_textures(texture_ids)
    assert len(mgr.base_textures) == 32
    
    # Generate tiles
    tile_data = [...]  # From chunk parser
    mgr.generate_tile_textures(tile_data)
    assert len(mgr.tile_textures) > 32

def test_texture_blending():
    mgr = TextureManager()
    
    # Create test textures
    tex1 = np.full((256, 256, 4), [255, 0, 0, 255], dtype=np.uint8)  # Red
    tex2 = np.full((256, 256, 4), [0, 255, 0, 255], dtype=np.uint8)  # Green
    tex3 = np.full((256, 256, 4), [0, 0, 255, 255], dtype=np.uint8)  # Blue
    
    # Blend 50% red, 30% green, 20% blue
    result = mgr._blend_textures(tex1, 127, tex2, 76, tex3, 52)
    
    # Check result is roughly purple
    assert result[0, 0, 0] > 100  # Red component
    assert result[0, 0, 1] > 50   # Green component
    assert result[0, 0, 2] > 30   # Blue component
```

---

### Day 7: Integration & Testing

**Goal**: Test complete texture loading pipeline

**Tasks**:
- [ ] Integrate all components
- [ ] Test with Coop_01_rpg.map
- [ ] Verify memory usage (<100 MB)
- [ ] Create demo script
- [ ] Update documentation

**Integration Test**:
```python
def test_full_texture_pipeline():
    """Test complete texture loading"""
    
    # 1. Load map with textures
    loader = ChunkMapLoader()
    heightmap, width, height, texture_ids, tile_data = loader.load_map_with_textures(
        "OriginalGameFiles/map/Coop_01_rpg.map"
    )
    
    # 2. Initialize texture manager
    mgr = TextureManager()
    mgr.load_texture_names("ExtractedAssets/Textures/")
    
    # 3. Load base textures
    mgr.load_base_textures(texture_ids)
    assert len(mgr.base_textures) == 32
    
    # 4. Generate tile textures
    mgr.generate_tile_textures(tile_data)
    assert len(mgr.tile_textures) >= 32
    
    # 5. Check memory usage
    import sys
    total_size = sum(sys.getsizeof(tex) for tex in mgr.tile_textures.values())
    print(f"Total texture memory: {total_size / 1024 / 1024:.1f} MB")
    assert total_size < 100 * 1024 * 1024  # <100 MB
```

**Demo Script**:
```python
# demo_texture_loading.py
"""Demo: Load and display texture data from a map"""

from map_viewer.chunk_map_loader import ChunkMapLoader
from map_viewer.texture_manager import TextureManager
import matplotlib.pyplot as plt

# Load map
loader = ChunkMapLoader()
heightmap, width, height, texture_ids, tile_data = loader.load_map_with_textures(
    "OriginalGameFiles/map/Coop_01_rpg.map"
)

print(f"Map: {width}×{height}")
print(f"Texture IDs: {texture_ids[:10]}...")  # First 10

# Initialize texture manager
mgr = TextureManager()
mgr.load_texture_names("ExtractedAssets/Textures/")
print(f"Available textures: {len(mgr.texture_names)}")

# Load base textures
mgr.load_base_textures(texture_ids)
print(f"Loaded base textures: {len(mgr.base_textures)}")

# Generate tile textures
mgr.generate_tile_textures(tile_data)
print(f"Generated tile textures: {len(mgr.tile_textures)}")

# Display some textures
fig, axes = plt.subplots(2, 4, figsize=(12, 6))
for i, ax in enumerate(axes.flat):
    if i in mgr.tile_textures:
        ax.imshow(mgr.tile_textures[i])
        ax.set_title(f"Tile {i}")
        ax.axis('off')
plt.tight_layout()
plt.savefig("texture_samples.png")
print("Saved texture_samples.png")
```

---

## Deliverables Checklist

### Code
- [ ] `chunk_map_loader.py` - Chunk-based map parser
- [ ] `dds_loader.py` - DDS texture loader
- [ ] `pak_extractor.py` - PAK extraction (or use QuickBMS)
- [ ] `texture_manager.py` - Texture management and blending
- [ ] `demo_texture_loading.py` - Demo script

### Tests
- [ ] `test_chunk_parser.py` - Test chunk parsing
- [ ] `test_dds_loader.py` - Test DDS loading
- [ ] `test_texture_manager.py` - Test blending
- [ ] `test_integration.py` - Test full pipeline

### Documentation
- [ ] Update `MAP_VIEWER_STATUS.md` with Week 2 progress
- [ ] Update `PHASE2_PROGRESS.md` with findings
- [ ] Document any issues encountered

---

## Success Metrics

### Functional
- ✅ Parse Chunks 3 & 4 correctly
- ✅ Load DDS textures from disk/PAK
- ✅ Generate 255 blended tile textures
- ✅ Memory usage <100 MB

### Performance
- Load time: <2 seconds for 32 base textures
- Blend time: <5 seconds for 192 mixed tiles
- Total time: <10 seconds for complete texture loading

### Quality
- Textures are correct size (256×256)
- Blending produces smooth transitions
- No visual artifacts
- Code is well-documented

---

## Risk Mitigation

### Risk: PAK extraction too complex
**Mitigation**: Use QuickBMS to pre-extract textures
**Fallback**: Work with extracted textures directory

### Risk: DDS format not supported by Pillow
**Mitigation**: Try imageio or custom DDS parser
**Fallback**: Convert DDS to PNG offline

### Risk: Memory usage too high
**Mitigation**: Load textures on-demand, implement LRU cache
**Fallback**: Reduce number of pre-blended tiles

### Risk: Blending too slow
**Mitigation**: Use NumPy vectorization, pre-allocate arrays
**Fallback**: Blend only frequently-used tiles

---

## Notes

### Texture File Locations
- **Game Files**: `OriginalGameFiles/pak/sf1.pak`
- **Extracted**: `ExtractedAssets/Textures/` (if pre-extracted)
- **Naming**: `landscape_island_XXX_*.dds` where XXX = 001-119

### Chunk Format Reference
- **Chunk 2**: Heightmap (already implemented)
- **Chunk 3**: 255 tiles × 14 bytes = 3,570 bytes
- **Chunk 4**: 63 texture IDs × 1 byte = 63 bytes

### Useful C# Reference Lines
- Chunk parsing: `SFEngine/SFMap/SFMap.cs` lines 70-120
- Texture loading: `SFEngine/SFMap/SFMapTerrainTextureManager.cs` lines 83-280
- Blending: `SFEngine/SF3D/SFTexture.cs` MixUncompressed method

---

## Next Week Preview

**Week 3 (Nov 18-24): Texture Rendering**
- Generate texture coordinates for terrain
- Upload textures to GPU
- Render textured terrain
- Add lighting (if time permits)

---

**Status**: Ready to Begin  
**Start Date**: November 11, 2024  
**Target Completion**: November 17, 2024  
**Updated**: 2024-11-03