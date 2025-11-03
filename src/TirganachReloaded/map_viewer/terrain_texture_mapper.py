"""
Terrain Texture Mapper for SpellForce maps

Maps terrain textures to different parts of the heightmap based on:
1. Height-based assignment (different textures at different elevations)
2. Slope-based assignment (grass on flat areas, rock on steep slopes)
3. Biome-based assignment (using procedural generation)
"""

from typing import Dict, List, Tuple

from loguru import logger


class TerrainTextureMapper:
    """
    Maps terrain textures to different parts of the heightmap
    Uses height, slope, and distance from water to determine texture
    """

    def __init__(self):
        self.texture_assignments = {}  # Maps tile coordinates to texture IDs
        self.texture_weights = {}  # Maps tile coordinates to blending weights
        self.tile_size = 4  # Size of each terrain tile for texture assignment

    def create_texture_map(
        self, heightmap: "SimpleHeightmap", texture_ids: List[int], texture_manager
    ) -> Dict[Tuple[int, int], Dict[int, float]]:
        """
        Create a texture assignment map for the heightmap

        Args:
            heightmap: The heightmap to create texture map for
            texture_ids: Available texture IDs to use
            texture_manager: Texture manager for texture properties

        Returns:
            Dictionary mapping (tile_x, tile_y) -> {texture_id: weight}
        """
        texture_map = {}

        # Determine texture based on height and slope
        for y in range(0, heightmap.height, self.tile_size):
            for x in range(0, heightmap.width, self.tile_size):
                # Calculate average height in this tile
                tile_height_sum = 0
                tile_count = 0
                for ty in range(self.tile_size):
                    for tx in range(self.tile_size):
                        if y + ty < heightmap.height and x + tx < heightmap.width:
                            tile_height_sum += heightmap.get_height(x + tx, y + ty)
                            tile_count += 1

                if tile_count > 0:
                    avg_height = tile_height_sum / tile_count
                else:
                    continue

                # Calculate slope (steepness) in this tile
                slope = self._calculate_tile_slope(heightmap, x, y, self.tile_size)

                # Determine texture based on height and slope
                texture_assignment = self._assign_texture_by_height_slope(
                    avg_height, slope, texture_ids
                )

                # Store in texture map
                tile_coords = (x // self.tile_size, y // self.tile_size)
                texture_map[tile_coords] = texture_assignment

        # Log some statistics
        texture_counts = {}
        for tile_assignment in texture_map.values():
            for tex_id in tile_assignment.keys():
                texture_counts[tex_id] = texture_counts.get(tex_id, 0) + 1

        logger.info(f"Texture map created: {len(texture_map)} tiles")
        logger.info(f"Texture usage: {texture_counts}")

        return texture_map

    def _calculate_tile_slope(
        self, heightmap: "SimpleHeightmap", x: int, y: int, size: int
    ) -> float:
        """Calculate average slope in a tile area"""
        slope_sum = 0.0
        slope_count = 0

        for ty in range(size):
            for tx in range(size):
                px, py = x + tx, y + ty
                if px < heightmap.width - 1 and py < heightmap.height - 1:
                    # Calculate gradient using neighboring points
                    dx = (
                        heightmap.get_height(px + 1, py)
                        - heightmap.get_height(px - 1, py)
                        if px > 0
                        else 0
                    )
                    dy = (
                        heightmap.get_height(px, py + 1)
                        - heightmap.get_height(px, py - 1)
                        if py > 0
                        else 0
                    )
                    slope = (abs(dx) + abs(dy)) / 2.0
                    slope_sum += slope
                    slope_count += 1

        return slope_sum / slope_count if slope_count > 0 else 0.0

    def _assign_texture_by_height_slope(
        self, height: float, slope: float, texture_ids: List[int]
    ) -> Dict[int, float]:
        """
        Assign textures based on height and slope

        Basic assignment logic:
        - Low height, low slope: grass/water
        - Mid height, low slope: grass/forest
        - Mid height, high slope: rock/stone
        - High height, high slope: snow/ice
        """
        assignment = {}

        if not texture_ids:
            return assignment

        # Height ranges
        low_height = 5.0
        high_height = 20.0

        # Slope ranges
        low_slope = 0.5
        high_slope = 2.0

        # Based on height and slope, assign texture
        if height < low_height:
            # Low elevation - likely water/coastal areas
            if slope < low_slope:
                # Low, flat - probably grassy
                assignment[texture_ids[0]] = 0.8  # Use first texture (grass)
                if len(texture_ids) > 1:
                    assignment[texture_ids[1]] = 0.2  # Mix with some other
            else:
                # Low, steep - rocky coast
                assignment[texture_ids[2]] = (
                    0.7 if len(texture_ids) > 2 else 1.0
                )  # rock
                if len(texture_ids) > 3:
                    assignment[texture_ids[3]] = 0.3

        elif height < high_height:
            # Mid elevation
            if slope < low_slope:
                # Mid elevation, flat - grass, forest
                assignment[texture_ids[0]] = 0.5  # grass
                if len(texture_ids) > 1:
                    assignment[texture_ids[1]] = 0.5  # mix
            elif slope < high_slope:
                # Mid elevation, moderate slope - rock/grass mix
                assignment[texture_ids[0]] = 0.3  # grass
                assignment[texture_ids[2]] = (
                    0.7 if len(texture_ids) > 2 else 0.7
                )  # rock
            else:
                # Mid elevation, steep - mostly rock
                assignment[texture_ids[2]] = (
                    0.8 if len(texture_ids) > 2 else 1.0
                )  # rock
                if len(texture_ids) > 4:
                    assignment[texture_ids[4]] = 0.2  # add some variety

        else:
            # High elevation
            if slope < high_slope:
                # High, flat - snow/dirt
                assignment[texture_ids[5] if len(texture_ids) > 5 else 0] = (
                    1.0  # snow or high texture
                )
            else:
                # High, steep - snow/rock mix
                assignment[texture_ids[5] if len(texture_ids) > 5 else 2] = (
                    0.7  # snow/rock
                )
                assignment[texture_ids[2] if len(texture_ids) > 2 else 0] = 0.3  # rock

        # Normalize weights to sum to 1.0
        total_weight = sum(assignment.values())
        if total_weight > 0:
            for texture_id in assignment:
                assignment[texture_id] /= total_weight

        return assignment

    def get_texture_for_position(
        self, x: float, y: float, texture_map: Dict[Tuple[int, int], Dict[int, float]]
    ) -> Dict[int, float]:
        """
        Get texture assignment for a specific world position

        Args:
            x: X coordinate
            y: Y coordinate
            texture_map: Precomputed texture map

        Returns:
            Dictionary mapping texture_id -> weight
        """
        # Convert world coordinates to tile coordinates
        tile_x = int(x) // self.tile_size
        tile_y = int(y) // self.tile_size

        # Get texture assignment for this tile
        tile_key = (tile_x, tile_y)
        if tile_key in texture_map:
            return texture_map[tile_key]
        else:
            # Default to first available texture
            return {0: 1.0} if texture_map else {}

    def create_simple_height_based_map(
        self, heightmap: "SimpleHeightmap", texture_ids: List[int]
    ) -> Dict[Tuple[int, int], Dict[int, float]]:
        """
        Create a simple height-based texture map (easier implementation)
        """
        texture_map = {}

        for y in range(0, heightmap.height, self.tile_size):
            for x in range(0, heightmap.width, self.tile_size):
                # Calculate average height in this tile
                heights = []
                for ty in range(min(self.tile_size, heightmap.height - y)):
                    for tx in range(min(self.tile_size, heightmap.width - x)):
                        heights.append(heightmap.get_height(x + tx, y + ty))

                if not heights:
                    continue

                avg_height = sum(heights) / len(heights)
                tile_coords = (x // self.tile_size, y // self.tile_size)

                # Simple height-based assignment
                if avg_height < 8:
                    # Low - grass
                    tex_id = texture_ids[0] if texture_ids else 0
                    texture_map[tile_coords] = {tex_id: 1.0}
                elif avg_height < 15:
                    # Mid - mix of grass and other
                    if len(texture_ids) >= 2:
                        texture_map[tile_coords] = {
                            texture_ids[0]: 0.6,  # grass
                            texture_ids[1]: 0.4,  # other
                        }
                    else:
                        texture_map[tile_coords] = {
                            texture_ids[0] if texture_ids else 0: 1.0
                        }
                else:
                    # High - rock or stone
                    tex_id = (
                        texture_ids[2]
                        if len(texture_ids) >= 3
                        else (texture_ids[0] if texture_ids else 0)
                    )
                    texture_map[tile_coords] = {tex_id: 1.0}

        return texture_map


def create_default_texture_mapper():
    """Create a default texture mapper instance"""
    return TerrainTextureMapper()
