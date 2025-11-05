"""
Enhanced SpellForce Map Loader
Loads heightmap and texture assignment data from actual SpellForce .map files

Based on reverse engineering of map files:
- 36 byte header
- ZLIB compressed data containing multiple chunks
- Chunk 1: Header information
- Chunk 2: Heightmap data
- Chunk 3: Terrain texture assignments
- Chunk 4: Unit placements
- Chunk 5: Building placements
"""

import math
import struct
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from loguru import logger


@dataclass
class SimpleMapHeader:
    """Simplified map header"""

    magic: int
    version: int
    flags: int
    map_size_code: int
    decompressed_size: int


@dataclass
class TerrainTextureAssignment:
    """Terrain texture assignment for a tile with multi-layer support"""

    x: int
    y: int
    texture_id: int  # Primary texture ID
    blend_weights: List[float]  # Blend weights for all layers
    additional_textures: List[int] = field(default_factory=list)  # Additional texture layers (2nd, 3rd)
    
    def get_all_textures(self) -> List[int]:
        """Get all texture IDs for this assignment"""
        all_textures = [self.texture_id] + self.additional_textures
        return [tid for tid in all_textures if tid > 0]  # Filter out invalid IDs
        
    def get_effective_weights(self) -> List[float]:
        """Get effective blend weights (matching get_all_textures)"""
        if len(self.blend_weights) >= len(self.get_all_textures()):
            return self.blend_weights[:len(self.get_all_textures())]
        else:
            # Pad with zeros if needed
            weights = self.blend_weights.copy()
            while len(weights) < len(self.get_all_textures()):
                weights.append(0.0)
            return weights


@dataclass
class SimpleHeightmap:
    """Simple heightmap data structure"""

    width: int
    height: int
    heights: List[List[float]]

    def get_height(self, x: int, y: int) -> float:
        """Get height at grid position with bounds checking"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.heights[y][x]
        return 0.0


class SimpleMapLoader:
    """
    Enhanced map loader for SpellForce .map files

    Format structure:
    1. 36-byte header with magic, version, size info
    2. ZLIB compressed data starting at offset 36
    3. Decompressed data contains multiple chunks:
       - Chunk 1: Map header info
       - Chunk 2: Heightmap data
       - Chunk 3: Terrain texture assignments
       - Chunk 4: Unit placements
       - Chunk 5: Building placements
    """

    def __init__(self):
        self.header: Optional[SimpleMapHeader] = None
        self.heightmap: Optional[SimpleHeightmap] = None
        self.terrain_textures: List[TerrainTextureAssignment] = []
        self.raw_header: Optional[bytes] = None
        self.decompressed_data: Optional[bytes] = None

    def load(self, filepath: Path) -> bool:
        """Load a map file"""
        try:
            logger.info(f"Loading map: {filepath}")

            with open(filepath, "rb") as f:
                file_data = f.read()

            # Parse header
            if not self._parse_header(file_data):
                return False

            # Decompress data
            if not self._decompress_data(file_data):
                return False

            # Parse all chunks from decompressed data
            if not self._parse_chunks():
                return False

            logger.info(
                f"Map loaded successfully: {self.heightmap.width if self.heightmap else 0}x{self.heightmap.height if self.heightmap else 0}"
            )
            logger.info(
                f"Terrain textures: {len(self.terrain_textures) if self.terrain_textures else 0} assignments"
            )
            return True

        except Exception as e:
            logger.exception(f"Failed to load map: {e}")
            return False

    def _parse_header(self, data: bytes) -> bool:
        """Parse the 36-byte map header"""
        if len(data) < 36:
            logger.error("File too small to contain header")
            return False

        self.raw_header = data[:36]

        try:
            # Parse header fields
            values = struct.unpack("<9I", self.raw_header)

            self.header = SimpleMapHeader(
                magic=values[0],
                version=values[1],
                flags=values[2],
                map_size_code=values[3],
                decompressed_size=values[8],  # Last field is decompressed size
            )

            logger.info(
                f"Header: magic=0x{self.header.magic:08X}, version={self.header.version}, "
                f"size_code={self.header.map_size_code}, decompressed={self.header.decompressed_size}"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to parse header: {e}")
            return False

    def _decompress_data(self, data: bytes) -> bool:
        """Decompress ZLIB data starting at offset 36"""
        try:
            # Find ZLIB signature
            zlib_start = 36  # Typically at offset 36
            compressed_data = data[zlib_start:]

            # Verify ZLIB signature
            if len(compressed_data) < 2:
                logger.error("No compressed data found")
                return False

            signature = compressed_data[:2]
            if signature not in [b"\x78\x9c", b"\x78\xda", b"\x78\x01"]:
                logger.warning(
                    f"Unexpected ZLIB signature: 0x{signature.hex()}, trying anyway"
                )

            # Decompress
            self.decompressed_data = zlib.decompress(compressed_data)
            logger.info(
                f"Decompressed {len(compressed_data)} -> {len(self.decompressed_data)} bytes"
            )

            # Verify size matches header
            if len(self.decompressed_data) != self.header.decompressed_size:
                logger.warning(
                    f"Size mismatch: expected {self.header.decompressed_size}, "
                    f"got {len(self.decompressed_data)}"
                )

            return True

        except zlib.error as e:
            logger.error(f"ZLIB decompression failed: {e}")
            return False
        except Exception as e:
            logger.exception(f"Decompression error: {e}")
            return False

    def _parse_chunks(self) -> bool:
        """Parse all chunks from decompressed data"""
        try:
            if not self.decompressed_data:
                logger.error("No decompressed data available")
                return False

            logger.debug(f"Decompressed data size: {len(self.decompressed_data)} bytes")

            # Attempt to parse as chunk-based format first
            if self._parse_chunk_format():
                logger.info("Successfully parsed as chunk-based format")
                return True

            # Fallback to the original single-heightmap format
            logger.debug("Chunk format parsing failed, trying original format")
            return self._parse_original_format()

        except Exception as e:
            logger.exception(f"Failed to parse chunks: {e}")
            return False

    def _parse_chunk_format(self) -> bool:
        """Parse the map as a chunk-based format"""
        data = self.decompressed_data
        offset = 0

        # Parse chunks
        while offset + 8 <= len(data):
            chunk_id, chunk_size = struct.unpack("<II", data[offset : offset + 8])
            offset += 8

            # Sanity check
            if chunk_size > len(data) - offset or chunk_size > 100_000_000:
                logger.warning(
                    f"Suspicious chunk size {chunk_size} for chunk {chunk_id} at offset {offset - 8}, stopping"
                )
                break

            chunk_data = data[offset : offset + chunk_size]
            if len(chunk_data) < chunk_size:
                logger.warning(
                    f"Incomplete chunk {chunk_id}: expected {chunk_size}, got {len(chunk_data)}"
                )
                break

            logger.debug(f"Parsing chunk {chunk_id} of size {chunk_size}")

            # Process specific chunks
            if chunk_id == 1:
                self._parse_chunk_1_header(chunk_data)
            elif chunk_id == 2:
                self._parse_chunk_2_heightmap(chunk_data)
            elif chunk_id == 3:
                self._parse_chunk_3_terrain_textures(chunk_data)
            # Add more chunk types as needed

            offset += chunk_size

        # Check if we have the essential data
        if not self.heightmap:
            logger.warning("No heightmap found in chunk format")
            return False

        return True

    def _parse_chunk_1_header(self, data: bytes):
        """Parse chunk 1 - Map header information"""
        logger.debug(f"Parsing header chunk (size: {len(data)})")
        # This may contain additional metadata about the map
        # For now, we'll just log its presence

    def _parse_chunk_2_heightmap(self, data: bytes):
        """Parse chunk 2 - Heightmap data"""
        logger.debug(f"Parsing heightmap chunk (size: {len(data)})")

        # Determine map size from data size
        width, height = self._detect_map_size(len(data))

        if width == 0 or height == 0:
            logger.error(f"Could not determine heightmap size from {len(data)} bytes")
            return

        logger.info(f"Heightmap chunk size: {width}x{height}")

        # Parse heightmap as raw bytes (0-255 elevation)
        heights = []
        for y in range(height):
            row = []
            for x in range(width):
                idx = y * width + x
                if idx < len(data):
                    # Raw byte value as height
                    # Scale to reasonable range (0-25.5 units)
                    height_value = float(data[idx]) / 10.0
                    row.append(height_value)
                else:
                    logger.warning(f"Missing height data at ({x}, {y})")
                    row.append(0.0)
            heights.append(row)

        self.heightmap = SimpleHeightmap(width=width, height=height, heights=heights)

        # Calculate some stats
        all_heights = [h for row in heights for h in row]
        if not all_heights:
            return

        min_h = min(all_heights)
        max_h = max(all_heights)
        avg_h = sum(all_heights) / len(all_heights)
        logger.info(
            f"Heightmap stats: min={min_h:.2f}, max={max_h:.2f}, avg={avg_h:.2f}"
        )

    def _parse_chunk_3_terrain_textures(self, data: bytes):
        """Parse chunk 3 - Terrain texture assignments with multi-layer support"""
        logger.debug(f"Parsing terrain texture chunk (size: {len(data)})")

        texture_assignments = []

        # Enhanced parsing based on SpellForce terrain system
        try:
            # Determine tile grid from heightmap if available
            tile_cols = 16
            tile_rows = 16
            if self.heightmap:
                tile_cols = max(1, (self.heightmap.width + 3) // 4)
                tile_rows = max(1, (self.heightmap.height + 3) // 4)
            tile_count = tile_cols * tile_rows

            # Try to deduce entry size from chunk size and tile count
            entry_size = None
            if tile_count > 0 and len(data) % tile_count == 0:
                entry_size = len(data) // tile_count
                logger.debug(
                    f"Chunk 3: tile grid {tile_cols}x{tile_rows} ({tile_count}), per-tile size candidate: {entry_size}"
                )

            # Candidate per-tile formats (bytes)
            candidates = []
            if entry_size:
                candidates.append(entry_size)
            candidates.extend([6, 14, 8, 12])  # Try common sizes, will ignore if too large

            parsed_tiles = 0
            tile_grid = {}

            for cand in candidates:
                if cand <= 0:
                    continue
                if tile_count * cand > len(data):
                    continue  # Not enough data

                # Attempt parse with this candidate size (use first 6 bytes for core data)
                try:
                    temp_assignments = []
                    for i in range(tile_count):
                        offset = i * cand
                        # Extract first 6 bytes as (3 indices, 3 weights) in 0..255
                        b0 = data[offset] if offset < len(data) else 0
                        b1 = data[offset + 1] if offset + 1 < len(data) else 0
                        b2 = data[offset + 2] if offset + 2 < len(data) else 0
                        w0 = data[offset + 3] if offset + 3 < len(data) else 0
                        w1 = data[offset + 4] if offset + 4 < len(data) else 0
                        w2 = data[offset + 5] if offset + 5 < len(data) else 0

                        tex_indices = [b0, b1, b2]
                        raw_weights = [w0, w1, w2]

                        # Convert to 0..1 and normalize
                        weights = [float(w) / 255.0 for w in raw_weights]
                        total_w = sum(weights)
                        if total_w > 0:
                            weights = [w / total_w for w in weights]
                        else:
                            weights = [0.0, 0.0, 0.0]

                        # Tile position in grid
                        tile_x = i % tile_cols
                        tile_y = i // tile_cols
                        world_x = tile_x * 4
                        world_y = tile_y * 4

                        # Keep only valid layers
                        valid_layers = []
                        for tex_idx, weight in zip(tex_indices, weights):
                            if tex_idx > 0 and weight > 0.001:
                                valid_layers.append((int(tex_idx), float(weight)))

                        if valid_layers:
                            primary_texture = valid_layers[0][0]
                            all_weights = [layer[1] for layer in valid_layers]
                            additional_textures = [layer[0] for layer in valid_layers[1:]]

                            assignment = TerrainTextureAssignment(
                                x=world_x,
                                y=world_y,
                                texture_id=primary_texture,
                                blend_weights=all_weights,
                                additional_textures=additional_textures,
                            )
                            temp_assignments.append(assignment)
                            tile_grid[(tile_x, tile_y)] = {
                                'textures': [layer[0] for layer in valid_layers],
                                'weights': [layer[1] for layer in valid_layers],
                            }

                    # If we parsed a reasonable number of tiles, accept and stop trying
                    if len(temp_assignments) >= max(1, tile_count // 2):
                        texture_assignments = temp_assignments
                        parsed_tiles = len(tile_grid)
                        logger.info(
                            f"Parsed terrain textures using per-tile size {cand} bytes: {parsed_tiles} tiles, {len(texture_assignments)} assignments"
                        )
                        # Log a few examples
                        for (tx, ty), tile_data in list(tile_grid.items())[:5]:
                            logger.debug(
                                f"Tile ({tx},{ty}): textures={tile_data['textures']}, weights={tile_data['weights']}"
                            )
                        break
                except Exception as ex:
                    logger.debug(f"Candidate parse with size {cand} failed: {ex}")

            # If candidates failed and data length matches legacy 16x16 grid, try that
            if not texture_assignments:
                expected_entries = 255
                legacy_entry_size = 14
                total_expected_size = expected_entries * legacy_entry_size
                if len(data) >= total_expected_size:
                    logger.debug("Falling back to legacy 16x16 grid parse (14 bytes/entry)")
                    for i in range(expected_entries):
                        offset = i * legacy_entry_size
                        tex_indices = [
                            data[offset] if offset < len(data) else 0,
                            data[offset + 1] if offset + 1 < len(data) else 0,
                            data[offset + 2] if offset + 2 < len(data) else 0,
                        ]
                        raw_weights = [
                            data[offset + 3] if offset + 3 < len(data) else 0,
                            data[offset + 4] if offset + 4 < len(data) else 0,
                            data[offset + 5] if offset + 5 < len(data) else 0,
                        ]
                        weights = [w / 255.0 for w in raw_weights]
                        total_weight = sum(weights)
                        if total_weight > 0:
                            weights = [w / total_weight for w in weights]
                        else:
                            weights = [0.0, 0.0, 0.0]
                        tile_x = i % 16
                        tile_y = i // 16
                        world_x = tile_x * 4
                        world_y = tile_y * 4
                        valid_layers = []
                        for tex_idx, weight in zip(tex_indices, weights):
                            if tex_idx > 0 and weight > 0.01:
                                valid_layers.append((tex_idx, weight))
                        if valid_layers:
                            primary_texture = valid_layers[0][0]
                            all_weights = [layer[1] for layer in valid_layers]
                            additional_textures = [layer[0] for layer in valid_layers[1:]]
                            assignment = TerrainTextureAssignment(
                                x=world_x,
                                y=world_y,
                                texture_id=primary_texture,
                                blend_weights=all_weights,
                                additional_textures=additional_textures,
                            )
                            texture_assignments.append(assignment)
                    logger.info(
                        f"Legacy parse produced {len(texture_assignments)} assignments"
                    )
                else:
                    logger.warning(
                        f"Chunk 3 data size {len(data)} did not match any expected per-tile format; trying byte-scan fallback"
                    )

            # Final fallback: scan for (x,y,tid) triplets and create single-layer assignments
            if not texture_assignments:
                offset = 0
                while offset + 6 <= len(data):
                    try:
                        x = struct.unpack("<H", data[offset : offset + 2])[0]
                        y = struct.unpack("<H", data[offset + 2 : offset + 4])[0]
                        texture_id = struct.unpack("<H", data[offset + 4 : offset + 6])[0]
                        if x < 8192 and y < 8192 and texture_id < 1024:
                            assignment = TerrainTextureAssignment(
                                x=x,
                                y=y,
                                texture_id=texture_id,
                                blend_weights=[1.0],
                            )
                            texture_assignments.append(assignment)
                            offset += 6
                        else:
                            offset += 1
                    except Exception:
                        offset += 1
                logger.info(
                    f"Byte-scan fallback found {len(texture_assignments)} texture assignments"
                )

        except Exception as e:
            logger.error(f"Error parsing Chunk 3 terrain textures: {e}")
            logger.info("Using simulated texture assignments as fallback")

            # Fallback to simulated assignments if parsing fails
            if self.heightmap:
                # Create simulated assignments based on heightmap
                for y in range(0, self.heightmap.height, 16):
                    for x in range(0, self.heightmap.width, 16):
                        # Simulate 3-layer blending based on height
                        h = self.heightmap.get_height(x, y)
                        if h < 5:
                            # Low elevation - grass texture
                            assignment = TerrainTextureAssignment(
                                x=x, y=y, texture_id=0, blend_weights=[1.0]
                            )
                            texture_assignments.append(assignment)
                        elif h < 15:
                            # Mid elevation - mixed textures
                            assignment = TerrainTextureAssignment(
                                x=x, y=y, texture_id=1, blend_weights=[0.7]
                            )
                            texture_assignments.append(assignment)
                            assignment2 = TerrainTextureAssignment(
                                x=x, y=y, texture_id=2, blend_weights=[0.3]
                            )
                            texture_assignments.append(assignment2)
                        else:
                            # High elevation - rock texture
                            assignment = TerrainTextureAssignment(
                                x=x, y=y, texture_id=3, blend_weights=[1.0]
                            )
                            texture_assignments.append(assignment)

        self.terrain_textures = texture_assignments
        return texture_assignments

    def _parse_original_format(self) -> bool:
        """Parse the map using the original single heightmap format"""
        try:
            if not self.decompressed_data:
                logger.error("No decompressed data available")
                return False

            logger.debug(f"Decompressed data size: {len(self.decompressed_data)} bytes")

            # Determine map size from decompressed data size
            width, height = self._detect_map_size(len(self.decompressed_data))

            if width == 0 or height == 0:
                logger.error(
                    f"Could not determine map size from {len(self.decompressed_data)} bytes"
                )
                logger.error("This might be an unsupported map format")
                return False

            logger.info(f"Detected map size: {width}x{height}")

            # Skip small header in decompressed data (if present)
            # Most maps have 1-16 bytes of header
            header_size = len(self.decompressed_data) - (width * height)
            if header_size < 0:
                logger.error(
                    f"Data size mismatch: need {width * height}, have {len(self.decompressed_data)}"
                )
                return False

            if header_size > 16:
                logger.warning(f"Unusually large header: {header_size} bytes")

            logger.debug(f"Skipping {header_size} byte header in decompressed data")
            heightmap_data = self.decompressed_data[header_size:]

            if len(heightmap_data) < width * height:
                logger.error(
                    f"Insufficient heightmap data: need {width * height}, have {len(heightmap_data)}"
                )
                return False

            # Parse heightmap as raw bytes (0-255 elevation)
            heights = []
            for y in range(height):
                row = []
                for x in range(width):
                    idx = y * width + x
                    if idx < len(heightmap_data):
                        # Raw byte value as height
                        # Scale to reasonable range (0-25.5 units)
                        height_value = float(heightmap_data[idx]) / 10.0
                        row.append(height_value)
                    else:
                        logger.warning(f"Missing height data at ({x}, {y})")
                        row.append(0.0)
                heights.append(row)

            self.heightmap = SimpleHeightmap(
                width=width, height=height, heights=heights
            )

            # Calculate some stats
            all_heights = [h for row in heights for h in row]
            if not all_heights:
                logger.error("No height data loaded")
                return False

            min_h = min(all_heights)
            max_h = max(all_heights)
            avg_h = sum(all_heights) / len(all_heights)
            logger.info(
                f"Heightmap stats: min={min_h:.2f}, max={max_h:.2f}, avg={avg_h:.2f}"
            )

            return True

        except Exception as e:
            logger.exception(f"Failed to parse in original format: {e}")
            return False

    def _detect_map_size(self, data_size: int) -> Tuple[int, int]:
        """
        Detect map dimensions from data size

        Common sizes:
        - 256x256 = 65,536 bytes
        - 512x512 = 262,144 bytes
        - 1024x1024 = 1,048,576 bytes

        Data may have small header (1-16 bytes), so we allow some tolerance
        """
        logger.debug(f"Detecting map size from {data_size} bytes")

        # Try common sizes
        common_sizes = [
            (64, 64),  # 4,096
            (128, 128),  # 16,384
            (256, 256),  # 65,536
            (512, 512),  # 262,144
            (1024, 1024),  # 1,048,576
        ]

        for width, height in common_sizes:
            expected = width * height
            # Allow up to 16 bytes difference for header
            if abs(data_size - expected) <= 16:
                logger.debug(
                    f"Matched common size: {width}x{height} (expected {expected}, got {data_size})"
                )
                return width, height

        # Try to deduce from size
        # Assume square map
        # Try with small header offset (0-16 bytes)
        for header_offset in range(17):
            map_size = data_size - header_offset
            side = int(math.sqrt(map_size))
            if side * side == map_size and side >= 64 and (side & (side - 1)) == 0:
                # Perfect square and power of 2
                logger.debug(
                    f"Detected size: {side}x{side} (with {header_offset} byte header)"
                )
                return side, side

        # Try non-square maps with header offset
        for header_offset in range(17):
            map_size = data_size - header_offset
            # Try common aspect ratios
            for ratio in [(1, 1), (2, 1), (1, 2), (4, 3), (3, 4)]:
                for base in [64, 128, 256, 512, 1024]:
                    width = base * ratio[0]
                    height = base * ratio[1]
                    if width * height == map_size:
                        logger.debug(f"Detected non-square: {width}x{height}")
                        return width, height

        logger.warning(f"Could not determine map size from {data_size} bytes")
        logger.warning(f"Closest square root: {int(math.sqrt(data_size))}")
        return 0, 0

    def get_height_at(self, x: float, y: float) -> float:
        """
        Get terrain height at world position with bilinear interpolation
        """
        if not self.heightmap:
            return 0.0

        # Convert to grid coordinates
        grid_x = int(x)
        grid_y = int(y)

        # Get fractional parts
        frac_x = x - grid_x
        frac_y = y - grid_y

        # Get heights at four corners
        h00 = self.heightmap.get_height(grid_x, grid_y)
        h10 = self.heightmap.get_height(grid_x + 1, grid_y)
        h01 = self.heightmap.get_height(grid_x, grid_y + 1)
        h11 = self.heightmap.get_height(grid_x + 1, grid_y + 1)

        # Bilinear interpolation
        h0 = h00 * (1 - frac_x) + h10 * frac_x
        h1 = h01 * (1 - frac_x) + h11 * frac_x
        height = h0 * (1 - frac_y) + h1 * frac_y

        return height
