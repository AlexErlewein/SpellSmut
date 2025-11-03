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
from dataclasses import dataclass
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
    """Terrain texture assignment for a tile"""

    x: int
    y: int
    texture_id: int
    blend_weights: List[float]  # For multi-texture blending


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
        """Parse chunk 3 - Terrain texture assignments"""
        logger.debug(f"Parsing terrain texture chunk (size: {len(data)})")

        texture_assignments = []

        # Enhanced parsing based on C# SFEngine patterns
        try:
            # Parse as a 255-entry table with 14 bytes per entry
            # Each entry: [ind1][ind2][ind3][weight1][weight2][weight3][padding]
            expected_entries = 255
            entry_size = 14  # 3 indices + 3 weights + 8 padding bytes
            total_expected_size = expected_entries * entry_size

            if len(data) >= total_expected_size:
                logger.debug("Parsing Chunk 3 as 255-entry texture assignment table")

                for i in range(expected_entries):
                    offset = i * entry_size

                    # Extract texture indices (3 bytes)
                    ind1 = data[offset] if offset < len(data) else 0
                    ind2 = data[offset + 1] if offset + 1 < len(data) else 0
                    ind3 = data[offset + 2] if offset + 2 < len(data) else 0

                    # Extract blend weights (3 bytes, 0-255 scale)
                    weight1 = data[offset + 3] if offset + 3 < len(data) else 0
                    weight2 = data[offset + 4] if offset + 4 < len(data) else 0
                    weight3 = data[offset + 5] if offset + 5 < len(data) else 0

                    # Convert weights to 0.0-1.0 scale
                    weights = [weight1 / 255.0, weight2 / 255.0, weight3 / 255.0]

                    # Create texture assignments for non-zero weights
                    indices = [ind1, ind2, ind3]
                    for j, (idx, weight) in enumerate(zip(indices, weights)):
                        if weight > 0.01:  # Threshold to ignore negligible weights
                            assignment = TerrainTextureAssignment(
                                x=i % 16 * 16,  # Distribute across map grid
                                y=i // 16 * 16,
                                texture_id=idx,
                                blend_weights=[weight],
                            )
                            texture_assignments.append(assignment)

                logger.info(
                    f"Successfully parsed {len(texture_assignments)} texture assignments from Chunk 3"
                )
            else:
                logger.warning(
                    f"Chunk 3 data size mismatch: expected {total_expected_size}, got {len(data)}. "
                    f"Trying alternative parsing methods."
                )

                # Fallback parsing methods
                offset = 0
                while offset + 6 <= len(
                    data
                ):  # Need at least 6 bytes for (x,y,idx,w1,w2,w3)
                    try:
                        # Try to parse as individual texture assignments
                        x = struct.unpack("<H", data[offset : offset + 2])[0]
                        y = struct.unpack("<H", data[offset + 2 : offset + 4])[0]
                        texture_id = struct.unpack("<H", data[offset + 4 : offset + 6])[
                            0
                        ]

                        # Validate reasonable values
                        if x < 1024 and y < 1024 and texture_id < 256:
                            assignment = TerrainTextureAssignment(
                                x=x,
                                y=y,
                                texture_id=texture_id,
                                blend_weights=[1.0],  # Single texture for now
                            )
                            texture_assignments.append(assignment)
                            offset += 6
                        else:
                            offset += 1  # Skip one byte and try again
                    except Exception:
                        offset += 1  # Skip one byte and try again

                logger.info(
                    f"Fallback parsing found {len(texture_assignments)} texture assignments"
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
