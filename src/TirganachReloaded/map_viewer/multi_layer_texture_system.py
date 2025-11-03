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
        """Create a texture blend for a single tile from its assignments"""
        blend = TerrainTextureBlend()
        
        # Count texture frequencies in this tile
        texture_counts: Dict[int, int] = {}
        for assignment in assignments:
            texture_counts[assignment.texture_id] = texture_counts.get(assignment.texture_id, 0) + 1
            
        # Convert counts to weights
        total_assignments = len(assignments)
        for texture_id, count in texture_counts.items():
            weight = count / total_assignments
            blend.add_layer(texture_id, weight)
            
        # Apply intelligent blending based on texture categories
        self._apply_intelligent_blending(blend)
        
        # Normalize weights
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
        
    def get_blend_for_position(self, world_x: float, world_z: float) -> Optional[TerrainTextureBlend]:
        """Get the texture blend for a world position"""
        # Convert world coordinates to tile coordinates
        tile_x = int(world_x) // 4
        tile_y = int(world_z) // 4
        return self.get_blend_for_tile(tile_x, tile_y)
        
    def create_fallback_blend(self, height: float, min_height: float, max_height: float) -> TerrainTextureBlend:
        """Create a fallback texture blend based on height when no map data is available"""
        blend = TerrainTextureBlend()
        
        # Height-based texture selection
        height_range = max_height - min_height
        if height_range <= 0:
            height_range = 1.0
            
        normalized_height = (height - min_height) / height_range
        
        if normalized_height < 0.3:
            # Low elevation: primarily grass
            blend.add_layer(1, 0.8)  # Grass texture
            blend.add_layer(77, 0.2)  # Some stone grass
        elif normalized_height < 0.7:
            # Mid elevation: grass and rock mix
            blend.add_layer(1, 0.6)  # Grass
            blend.add_layer(77, 0.3)  # Stone grass  
            blend.add_layer(44, 0.1)  # Some rock
        else:
            # High elevation: primarily rock
            blend.add_layer(44, 0.7)  # Rock
            blend.add_layer(77, 0.2)  # Stone grass
            blend.add_layer(1, 0.1)  # Some grass
            
        blend.normalize_weights()
        return blend
        
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