# SpellForce Map Viewer - 3-Layer Texture Blending Implementation
## Reading Real Texture Assignments from Map Files
**Date**: November 3, 2025  
**Status**: Ready for Implementation

---

## Executive Summary

This document outlines the implementation plan for 3-layer texture blending that reads real texture assignments from SpellForce map files (Chunk 3). This addresses the critical need to display authentic terrain textures instead of simulated ones.

**Goal**: Implement full 3-layer texture blending with real map data
**Timeline**: 2 weeks (Week 1: Implementation, Week 2: Testing & Optimization)

---

## 1. Current State Analysis

### What's Working Now
✅ **Basic Texture Rendering**: Single texture per tile using DDS loader
✅ **Heightmap Visualization**: 3D terrain with elevation data
✅ **Lighting System**: Directional sun light with surface normals
✅ **Camera Controls**: Full 3D navigation with mouse and keyboard
✅ **Performance**: 60+ FPS on all platforms
✅ **Cross-Platform**: Works on macOS, Linux, Windows

### What's Missing
❌ **Multi-layer Blending**: Only single texture per tile
❌ **Real Texture Assignments**: Using simulated instead of real data
❌ **Texture Weighting**: No blending weights from map files
❌ **Chunk 3 Parsing**: Not reading actual texture assignments

---

## 2. Implementation Objectives

### Primary Goals
✅ **Parse Chunk 3**: Read real terrain texture assignments from map files
✅ **3-Layer Blending**: Implement multi-texture blending per tile
✅ **Weighted Mixing**: Use actual blend weights from map data
✅ **Performance**: Maintain 60+ FPS with blending enabled
✅ **Compatibility**: Work with all existing map formats

### Secondary Goals
✅ **Fallback System**: Gracefully degrade to single texture when needed
✅ **Visual Quality**: High-quality texture blending algorithms
✅ **Memory Efficiency**: Optimize texture memory usage
✅ **Error Handling**: Robust handling of corrupt/missing data

---

## 3. Technical Implementation Plan

### Phase 1: Chunk 3 Parsing (Week 1, Days 1-3)

#### Task 1.1: Enhanced Map Loader
**Objective**: Parse Chunk 3 terrain texture assignments

```python
# Current SimpleMapLoader structure
class SimpleMapLoader:
    def load(self, filepath: Path) -> bool:
        # Parse header
        # Decompress data
        # Parse heightmap (Chunk 2)
        # Parse terrain textures (Chunk 3) ← NEW!
        pass

# New Chunk 3 parsing
def _parse_chunk_3_terrain_textures(self, data: bytes):
    """Parse terrain texture assignments from Chunk 3"""
    # Format: 255 tiles × 14 bytes each
    # Each tile: [ind1][ind2][ind3][weight1][weight2][weight3][padding]
    # ind1-3: texture indices (0-118)
    # weight1-3: blend weights (0-255)
    # padding: 2 unused bytes
    
    texture_assignments = []
    for i in range(255):
        offset = i * 14
        if offset + 14 <= len(data):
            ind1, ind2, ind3 = struct.unpack("<BBB", data[offset:offset+3])
            weight1, weight2, weight3 = struct.unpack("<BBB", data[offset+3:offset+6])
            # Skip 2 padding bytes
            assignment = TerrainTextureAssignment(
                tile_index=i,
                texture_indices=[ind1, ind2, ind3],
                blend_weights=[weight1/255.0, weight2/255.0, weight3/255.0]
            )
            texture_assignments.append(assignment)
    
    self.terrain_textures = texture_assignments
```

#### Task 1.2: Data Structures
**Objective**: Create structures for 3-layer texture assignments

```python
@dataclass
class TerrainTextureAssignment:
    """3-layer terrain texture assignment for a tile"""
    tile_index: int
    texture_indices: List[int]  # 3 texture indices (0-118)
    blend_weights: List[float]  # 3 blend weights (0.0-1.0)
    
    def get_active_textures(self) -> List[Tuple[int, float]]:
        """Get list of (texture_index, weight) for active textures"""
        return [(idx, weight) for idx, weight in zip(self.texture_indices, self.blend_weights) 
                if weight > 0.01]  # Threshold to ignore negligible weights
```

### Phase 2: 3-Layer Blending System (Week 1, Days 4-7)

#### Task 2.1: Blending Algorithm
**Objective**: Implement weighted texture blending

```python
class TextureBlender:
    """Handle 3-layer texture blending"""
    
    def blend_textures(self, textures: List[np.ndarray], weights: List[float]) -> np.ndarray:
        """Blend multiple textures with given weights
        
        Args:
            textures: List of (height, width, 4) RGBA texture arrays
            weights: List of blending weights (0.0-1.0)
            
        Returns:
            Blended texture as (height, width, 4) RGBA array
        """
        if not textures or not weights:
            return np.zeros((256, 256, 4), dtype=np.uint8)
            
        # Normalize weights to sum to 1.0
        total_weight = sum(weights)
        if total_weight == 0:
            return textures[0] if textures else np.zeros((256, 256, 4), dtype=np.uint8)
            
        normalized_weights = [w/total_weight for w in weights]
        
        # Start with first texture
        result = textures[0].astype(np.float32) * normalized_weights[0]
        
        # Blend remaining textures
        for i in range(1, min(len(textures), len(normalized_weights))):
            texture_float = textures[i].astype(np.float32)
            result += texture_float * normalized_weights[i]
            
        # Convert back to uint8
        return np.clip(result, 0, 255).astype(np.uint8)
```

#### Task 2.2: Enhanced Texture Manager
**Objective**: Manage blended textures efficiently

```python
class EnhancedTextureManager:
    """Manage 3-layer texture blending with caching"""
    
    def __init__(self):
        self.texture_cache: Dict[str, np.ndarray] = {}  # Blended textures
        self.blend_cache: Dict[str, np.ndarray] = {}    # Individual blends
        self.base_textures: Dict[int, np.ndarray] = {}  # Loaded base textures
        
    def get_blended_texture(self, assignment: TerrainTextureAssignment) -> np.ndarray:
        """Get blended texture for a tile assignment"""
        # Create cache key
        cache_key = f"blend_{assignment.tile_index}_{hash(tuple(assignment.texture_indices))}_{hash(tuple(assignment.blend_weights))}"
        
        # Check cache first
        if cache_key in self.texture_cache:
            return self.texture_cache[cache_key]
            
        # Get active textures
        active_textures = assignment.get_active_textures()
        if not active_textures:
            # Return default texture
            return self._get_default_texture()
            
        # Load base textures
        base_textures = []
        weights = []
        for texture_idx, weight in active_textures:
            texture = self._load_base_texture(texture_idx)
            if texture is not None:
                base_textures.append(texture)
                weights.append(weight)
                
        # Blend textures
        if base_textures:
            blender = TextureBlender()
            blended = blender.blend_textures(base_textures, weights)
            self.texture_cache[cache_key] = blended
            return blended
        else:
            return self._get_default_texture()
```

### Phase 3: OpenGL Integration (Week 2, Days 1-3)

#### Task 3.1: Blended Texture Upload
**Objective**: Upload blended textures to GPU efficiently

```python
class OpenGLTextureManager:
    """Manage OpenGL texture uploads with blending support"""
    
    def __init__(self):
        self.opengl_texture_ids: Dict[str, int] = {}
        self.texture_manager = EnhancedTextureManager()
        
    def upload_blended_texture(self, assignment: TerrainTextureAssignment) -> int:
        """Upload blended texture to OpenGL and return texture ID"""
        # Get blended texture
        blended_texture = self.texture_manager.get_blended_texture(assignment)
        
        # Create cache key
        cache_key = f"opengl_blend_{assignment.tile_index}"
        
        # Check if already uploaded
        if cache_key in self.opengl_texture_ids:
            return self.opengl_texture_ids[cache_key]
            
        # Generate new texture ID
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Upload texture data
        height, width = blended_texture.shape[:2]
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            width,
            height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            blended_texture
        )
        
        # Store texture ID
        self.opengl_texture_ids[cache_key] = texture_id
        return texture_id
```

#### Task 3.2: Rendering Integration
**Objective**: Integrate blending with existing rendering pipeline

```python
class MapViewerRenderer:
    """Enhanced map viewer renderer with 3-layer blending"""
    
    def __init__(self):
        self.opengl_manager = OpenGLTextureManager()
        self.map_loader = SimpleMapLoader()
        
    def render_terrain_tile(self, x: int, y: int, tile_index: int):
        """Render a single terrain tile with 3-layer blending"""
        # Get texture assignment for this tile
        if self.map_loader.terrain_textures and tile_index < len(self.map_loader.terrain_textures):
            assignment = self.map_loader.terrain_textures[tile_index]
            
            # Upload blended texture
            texture_id = self.opengl_manager.upload_blended_texture(assignment)
            
            # Bind texture and render
            glBindTexture(GL_TEXTURE_2D, texture_id)
            self._render_textured_quad(x, y)
        else:
            # Fallback to single texture
            self._render_single_texture_tile(x, y, tile_index)
```

---

## 4. Implementation Timeline

### Week 1: Core Implementation

#### Day 1-2: Chunk 3 Parsing
- [ ] Implement Chunk 3 parser in SimpleMapLoader
- [ ] Create TerrainTextureAssignment data structure
- [ ] Parse 255 tile definitions with 3-layer assignments
- [ ] Validate parsing with test maps

#### Day 3-4: Blending System
- [ ] Implement TextureBlender class
- [ ] Create EnhancedTextureManager with caching
- [ ] Implement 3-layer texture blending algorithm
- [ ] Add fallback handling for missing textures

#### Day 5-6: Texture Management
- [ ] Implement blended texture caching
- [ ] Add memory management for blended textures
- [ ] Implement efficient base texture loading
- [ ] Add performance monitoring

#### Day 7: Integration Testing
- [ ] Test Chunk 3 parsing with real maps
- [ ] Verify 3-layer blending accuracy
- [ ] Test caching performance
- [ ] Validate error handling

### Week 2: OpenGL Integration & Optimization

#### Day 1-2: OpenGL Integration
- [ ] Implement OpenGLTextureManager
- [ ] Add blended texture upload to GPU
- [ ] Integrate with existing rendering pipeline
- [ ] Test texture binding and rendering

#### Day 3-4: Performance Optimization
- [ ] Optimize texture blending algorithms
- [ ] Implement texture streaming for large maps
- [ ] Add memory usage monitoring
- [ ] Optimize cache eviction policies

#### Day 5-6: Quality Assurance
- [ ] Comprehensive testing with various maps
- [ ] Performance benchmarking
- [ ] Visual quality verification
- [ ] Cross-platform testing

#### Day 7: Documentation & Wrap-up
- [ ] Update documentation with new features
- [ ] Create usage examples
- [ ] Final performance report
- [ ] Prepare for integration

---

## 5. Success Metrics

### Technical Metrics
✅ **Chunk 3 Parsing**: Successfully parse 255 tile definitions from real maps
✅ **3-Layer Blending**: Implement proper weighted texture blending
✅ **Performance**: Maintain 60+ FPS with blending enabled
✅ **Memory Usage**: Efficient texture memory management
✅ **Compatibility**: Work with all existing map formats

### Quality Metrics
✅ **Visual Accuracy**: Match original game texture appearance
✅ **Blending Quality**: Smooth transitions between texture layers
✅ **Error Handling**: Graceful degradation for missing/corrupt data
✅ **User Experience**: Seamless integration with existing controls

### Test Results
✅ **Map Compatibility**: Work with Coop maps and campaign maps
✅ **Texture Variety**: Handle all 119 available terrain textures
✅ **Performance**: No significant FPS drop with blending
✅ **Stability**: No crashes or rendering issues

---

## 6. Risk Mitigation

### Technical Risks
**Risk**: Chunk 3 format may be more complex than expected
**Mitigation**: Start with simple parsing and gradually add complexity

**Risk**: 3-layer blending may impact performance
**Mitigation**: Implement efficient algorithms and caching

**Risk**: Some maps may not have Chunk 3 data
**Mitigation**: Maintain fallback to height-based assignment

### Implementation Risks
**Risk**: OpenGL integration may be challenging
**Mitigation**: Use existing patterns and incremental testing

**Risk**: Memory usage may increase significantly
**Mitigation**: Implement smart caching and eviction

---

## 7. Resources Required

### Development Time
- **Week 1**: 40 hours (Core implementation)
- **Week 2**: 40 hours (Integration and optimization)
- **Total**: 80 hours (2 weeks @ 40 hours/week)

### Technical Requirements
- **Python Libraries**: NumPy for texture blending
- **OpenGL**: PyOpenGL for texture rendering
- **Existing Components**: DDS loader, map loader, texture manager

### Testing Resources
- **Map Files**: Coop maps, campaign maps for testing
- **Hardware**: macOS, Linux, Windows for cross-platform testing
- **Performance Tools**: Profiling and benchmarking utilities

---

## 8. Next Steps

### Immediate Actions
1. **Create branch**: `3layer-texture-blending` for implementation
2. **Set up environment**: Prepare development and testing environments
3. **Baseline testing**: Test existing functionality before changes
4. **Start implementation**: Begin with Chunk 3 parsing

### Week 1 Kickoff
- **Monday**: Start Chunk 3 parsing implementation
- **Tuesday**: Complete data structures and basic parsing
- **Wednesday**: Test with real map files
- **Thursday**: Begin blending system implementation
- **Friday**: Complete TextureBlender class
- **Saturday**: Implement EnhancedTextureManager
- **Sunday**: Integration testing and bug fixes

---

**Project Lead**: [Development Team]  
**Implementation Manager**: [To Be Assigned]  
**Start Date**: Monday, November 4, 2025  
**Completion Date**: Sunday, November 17, 2025  
**Review Date**: Monday, November 18, 2025