"""
Multi-Layer Texture Blending System for SpellForce Map Viewer

Implements advanced terrain texturing with multiple texture layers and blend weights.
Based on SpellForce's terrain system which uses up to 3 texture layers per tile.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from loguru import logger


class TerrainTextureBlend:
    """
    Represents texture blending for a single terrain tile
    
    SpellForce uses up to 3 texture layers per tile:
    - Layer 0: Base terrain (grass, dirt, sand)
    - Layer 1: Secondary terrain (rock, stone paths)  
    - Layer 2: Detail/transition (snow, lava, special)
    
    Each layer has a blend weight (0.0-1.0) that determines visibility.
    """
    
    def __init__(self):
        self.texture_ids: List[int] = []  # Up to 3 texture IDs
        self.blend_weights: List[float] = []  # Corresponding blend weights
        self.total_weight: float = 0.0
        
    def add_layer(self, texture_id: int, weight: float):
        """Add a texture layer with blend weight"""
        if len(self.texture_ids) >= 3:
            logger.warning(f"Cannot add more than 3 texture layers, ignoring texture {texture_id}")
            return
            
        if weight <= 0.0:
            return  # Skip zero-weight layers
            
        self.texture_ids.append(texture_id)
        self.blend_weights.append(weight)
        self.total_weight += weight
        
    def normalize_weights(self):
        """Normalize blend weights so they sum to 1.0"""
        if self.total_weight > 0.0:
            self.blend_weights = [w / self.total_weight for w in self.blend_weights]
            self.total_weight = 1.0
            
    def get_primary_texture(self) -> Optional[int]:
        """Get the primary texture (highest weight)"""
        if not self.texture_ids:
            return None
        max_idx = np.argmax(self.blend_weights)
        return self.texture_ids[max_idx]
        
    def is_valid(self) -> bool:
        """Check if this blend has valid texture data"""
        return len(self.texture_ids) > 0 and self.total_weight > 0.0


class MultiLayerTextureSystem:
    """
    Manages multi-layer texture blending for terrain rendering
    
    Features:
    - Parse texture assignments from map data
    - Create blend weights based on terrain type and transitions
    - Support up to 3 texture layers per tile
    - Optimize for OpenGL rendering with texture combiners
    """
    
    def __init__(self):
        self.texture_blends: Dict[Tuple[int, int], TerrainTextureBlend] = {}
        self.texture_categories: Dict[int, str] = {}  # texture_id -> category
        self.blend_patterns: Dict[Tuple[str, ...], Dict[str, float]] = {}  # transition patterns
        
        # Initialize texture categories based on SpellForce terrain types
        self._initialize_texture_categories()
        self._initialize_blend_patterns()
        
    def _initialize_texture_categories(self):
        """Categorize textures by type for intelligent blending"""
        # Grass textures (base layer)
        grass_ids = [1, 2, 3, 4, 5, 60, 61, 68]  # landscape_island_00X_grass
        for tid in grass_ids:
            self.texture_categories[tid] = "grass"
            
        # Rock/stone textures (secondary layer)  
        rock_ids = [44, 47, 77]  # lava, stone, etc.
        for tid in rock_ids:
            self.texture_categories[tid] = "rock"
            
        # Dirt/soil textures
        dirt_ids = []  # Will be populated as we discover more
        for tid in dirt_ids:
            self.texture_categories[tid] = "dirt"
            
        # Snow textures (detail layer)
        snow_ids = []  # Winter/snow textures
        for tid in snow_ids:
            self.texture_categories[tid] = "snow"
            
        # Special textures (lava, magical, etc.)
        special_ids = []  # Lava, magical effects
        for tid in special_ids:
            self.texture_categories[tid] = "special"
            
        logger.info(f"Categorized {len(self.texture_categories)} textures")
        
    def _initialize_blend_patterns(self):
        """Initialize blend patterns for terrain transitions"""
        # Grass to rock transitions
        self.blend_patterns[("grass", "rock")] = {
            "grass": 0.7, "rock": 0.3
        }
        
        # Rock to snow transitions  
        self.blend_patterns[("rock", "snow")] = {
            "rock": 0.6, "snow": 0.4
        }
        
        # Grass to dirt transitions
        self.blend_patterns[("grass", "dirt")] = {
            "grass": 0.8, "dirt": 0.2
        }
        
        # Multi-way transitions (3-way blend)
        self.blend_patterns[("grass", "rock", "snow")] = {
            "grass": 0.5, "rock": 0.3, "snow": 0.2
        }
        
    def _category_ids(self, category: str) -> List[int]:
        """Return IDs known for a category."""
        return [tid for tid, cat in self.texture_categories.items() if cat == category]
    
    def _pick_from_category(self, category: str, tile_x: int, tile_y: int, fallback: int) -> int:
        """Deterministically pick a texture ID from a category based on tile coords."""
        ids = self._category_ids(category)
        if not ids:
            return fallback
        # Deterministic pseudo-random selection
        idx = ((tile_x * 73856093) ^ (tile_y * 19349663)) % len(ids)
        return ids[idx]
        
    def parse_texture_assignments(self, texture_assignments: List) -> Dict[Tuple[int, int], TerrainTextureBlend]:
        """
        Parse raw texture assignments into multi-layer blends
        
        Args:
            texture_assignments: List of texture assignment objects from map data
            
        Returns:
            Dictionary mapping tile coordinates to texture blends
        """
        logger.info(f"Parsing {len(texture_assignments)} texture assignments for multi-layer blending")
        
        # Group assignments by tile (4x4 blocks)
        tile_assignments: Dict[Tuple[int, int], List] = {}
        
        for assignment in texture_assignments:
            # Convert to tile coordinates (4x4 tiles)
            tile_x = assignment.x // 4
            tile_y = assignment.y // 4
            tile_key = (tile_x, tile_y)
            
            if tile_key not in tile_assignments:
                tile_assignments[tile_key] = []
            tile_assignments[tile_key].append(assignment)
            
        # Create blends for each tile
        for tile_key, assignments in tile_assignments.items():
            blend = self._create_tile_blend(assignments)
            if blend.is_valid():
                self.texture_blends[tile_key] = blend
                
        logger.info(f"Created {len(self.texture_blends)} multi-layer texture blends")
        return self.texture_blends
        
    def _create_tile_blend(self, assignments: List) -> TerrainTextureBlend:
        """Create a texture blend for a single tile from its assignments.
        Prefer explicit per-assignment weights if present; otherwise fall back to frequency counts."""
        # Accumulate weights per texture id
        weight_map: Dict[int, float] = {}

        for assignment in assignments:
            # Try to use explicit multi-layer data, else fallback to single-layer
            textures: List[int] = []
            weights: List[float] = []
            if hasattr(assignment, "get_all_textures") and hasattr(assignment, "get_effective_weights"):
                try:
                    textures = assignment.get_all_textures()
                    weights = assignment.get_effective_weights()
                except Exception:
                    textures = [getattr(assignment, "texture_id", -1)]
                    weights = [1.0]
            else:
                textures = [getattr(assignment, "texture_id", -1)]
                weights = [1.0]

            if not textures:
                continue

            # If weights length mismatches, pad or truncate
            if len(weights) < len(textures):
                weights = weights + [0.0] * (len(textures) - len(weights))
            elif len(weights) > len(textures):
                weights = weights[: len(textures)]

            for tid, w in zip(textures[:3], weights[:3]):
                if tid is None or tid <= 0:
                    continue
                weight_map[tid] = weight_map.get(tid, 0.0) + float(max(0.0, w))

        # If nothing accumulated, fallback to frequency-based
        if not weight_map:
            texture_counts: Dict[int, int] = {}
            for assignment in assignments:
                tid = getattr(assignment, "texture_id", -1)
                if tid and tid > 0:
                    texture_counts[tid] = texture_counts.get(tid, 0) + 1
            total = sum(texture_counts.values()) or 1
            for tid, count in texture_counts.items():
                weight_map[tid] = count / total

        # Build blend
        blend = TerrainTextureBlend()
        for tid, w in weight_map.items():
            blend.add_layer(int(tid), float(w))

        # Apply intelligent blending and normalize
        self._apply_intelligent_blending(blend)
        blend.normalize_weights()
        return blend
        
    def _apply_intelligent_blending(self, blend: TerrainTextureBlend):
        """Apply intelligent blending based on texture categories"""
        if len(blend.texture_ids) <= 1:
            return  # No blending needed for single texture
            
        # Get categories for this blend
        categories = []
        for tid in blend.texture_ids:
            category = self.texture_categories.get(tid, "unknown")
            categories.append(category)
            
        # Remove duplicates while preserving order
        unique_categories = []
        for cat in categories:
            if cat not in unique_categories and cat != "unknown":
                unique_categories.append(cat)
                
        # Apply blend pattern if available
        if len(unique_categories) >= 2:
            pattern_key = tuple(unique_categories[:3])  # Max 3 categories
            if pattern_key in self.blend_patterns:
                pattern = self.blend_patterns[pattern_key]
                
                # Update weights based on pattern
                new_weights = []
                for i, tid in enumerate(blend.texture_ids):
                    category = self.texture_categories.get(tid, "unknown")
                    if category in pattern:
                        new_weights.append(pattern[category])
                    else:
                        new_weights.append(blend.blend_weights[i])  # Keep original weight
                        
                blend.blend_weights = new_weights
                
    def get_blend_for_tile(self, tile_x: int, tile_y: int) -> Optional[TerrainTextureBlend]:
        """Get the texture blend for a specific tile"""
        tile_key = (tile_x, tile_y)
        return self.texture_blends.get(tile_key)
    
    def get_weight_for_tile_and_texture(self, tile_x: int, tile_y: int, texture_id: int) -> float:
        """Get the normalized weight for a specific texture on a given tile."""
        blend = self.get_blend_for_tile(tile_x, tile_y)
        if not blend or not blend.texture_ids:
            return 0.0
        for tid, w in zip(blend.texture_ids, blend.blend_weights):
            if tid == texture_id:
                try:
                    return float(max(0.0, min(1.0, w)))
                except Exception:
                    return 0.0
        return 0.0
        
    def get_blend_for_position(self, world_x: float, world_z: float) -> Optional[TerrainTextureBlend]:
        """Get the texture blend for a world position"""
        # Convert world coordinates to tile coordinates
        tile_x = int(world_x) // 4
        tile_y = int(world_z) // 4
        return self.get_blend_for_tile(tile_x, tile_y)
        
    def create_fallback_blend_for_tile(self, tile_x: int, tile_y: int, height: float, min_height: float, max_height: float) -> TerrainTextureBlend:
        """Create a richer fallback blend per tile using height and a deterministic variant pick."""
        blend = TerrainTextureBlend()
        
        # Height-based selection
        height_range = max_height - min_height
        if height_range <= 0:
            height_range = 1.0
        normalized_height = (height - min_height) / height_range
        
        # Choose category variants deterministically per tile
        grass_id = self._pick_from_category("grass", tile_x, tile_y, 1)
        rock_id = self._pick_from_category("rock", tile_x + 13, tile_y + 7, 44)
        
        if normalized_height < 0.3:
            # Mostly grass, little rock
            blend.add_layer(grass_id, 0.85)
            blend.add_layer(rock_id, 0.15)
        elif normalized_height < 0.7:
            # Mixed
            blend.add_layer(grass_id, 0.6)
            blend.add_layer(rock_id, 0.4)
        else:
            # Mostly rock
            blend.add_layer(rock_id, 0.75)
            blend.add_layer(grass_id, 0.25)
        
        blend.normalize_weights()
        return blend
    
    def smooth_blends(self, iterations: int = 1):
        """Apply simple neighbor averaging to smooth blend weights across tile boundaries."""
        if not self.texture_blends:
            return
        for _ in range(max(0, int(iterations))):
            new_blends: Dict[Tuple[int, int], TerrainTextureBlend] = {}
            keys = list(self.texture_blends.keys())
            for tx, ty in keys:
                center = self.texture_blends.get((tx, ty))
                if not center:
                    continue
                # Collect neighbor weights
                accum: Dict[int, float] = {}
                counts: Dict[int, int] = {}
                def add_weights(b: TerrainTextureBlend):
                    for tid, w in zip(b.texture_ids, b.blend_weights):
                        accum[tid] = accum.get(tid, 0.0) + w
                        counts[tid] = counts.get(tid, 0) + 1
                add_weights(center)
                for dx, dy in ((-1,0),(1,0),(0,-1),(0,1)):
                    nb = self.texture_blends.get((tx+dx, ty+dy))
                    if nb:
                        add_weights(nb)
                # Average
                averaged: Dict[int, float] = {tid: accum[tid]/counts[tid] for tid in accum}
                # Rebuild blend (limit to top 3 weights for safety)
                sorted_items = sorted(averaged.items(), key=lambda kv: kv[1], reverse=True)[:3]
                nb_blend = TerrainTextureBlend()
                for tid, w in sorted_items:
                    nb_blend.add_layer(tid, w)
                nb_blend.normalize_weights()
                new_blends[(tx, ty)] = nb_blend
            self.texture_blends = new_blends
        
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the texture blending system"""
        stats = {
            "total_tiles": len(self.texture_blends),
            "single_layer": 0,
            "double_layer": 0, 
            "triple_layer": 0,
            "categories_used": set()
        }
        
        for blend in self.texture_blends.values():
            layer_count = len(blend.texture_ids)
            if layer_count == 1:
                stats["single_layer"] += 1
            elif layer_count == 2:
                stats["double_layer"] += 1
            elif layer_count == 3:
                stats["triple_layer"] += 1
                
            # Track categories used
            for tid in blend.texture_ids:
                category = self.texture_categories.get(tid, "unknown")
                stats["categories_used"].add(category)
                
        stats["categories_used"] = len(stats["categories_used"])
        return stats