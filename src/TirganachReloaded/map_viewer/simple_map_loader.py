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
        self.terrain_textures: Optional[List[TerrainTextureAssignment]] = None
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
        if all_heights:
            min_h = min(all_heights)
            max_h = max(all_heights)
            avg_h = sum(all_heights) / len(all_heights)
            logger.info(
                f"Heightmap stats: min={min_h:.2f}, max={max_h:.2f}, avg={avg_h:.2f}"
            )

    def _parse_chunk_3_terrain_textures(self, data: bytes):
        """Parse chunk 3 - Terrain texture assignments"""
        logger.debug(f"Parsing terrain texture chunk (size: {len(data)})")

        # The exact format of terrain texture assignments isn't known yet
        # This would contain mappings of (x, y) -> texture_id
        # For now, we'll try to decode it based on common patterns

        texture_assignments = []
        offset = 0

        # Try to parse as a sequence of (x, y, texture_id) or similar structure
        # This is speculative based on common game formats
        try:
            # If data looks like a grid format (width*height entries), try that
            if self.heightmap:
                expected_size = (
                    self.heightmap.width * self.heightmap.height * 2
                )  # Assuming 2 bytes per tile
                if len(data) >= expected_size:
                    logger.debug("Attempting grid-based texture parsing")
                    for y in range(self.heightmap.height):
                        for x in range(self.heightmap.width):
                            idx = (y * self.heightmap.width + x) * 2
                            if idx + 2 <= len(data):
                                texture_id = struct.unpack("<H", data[idx : idx + 2])[0]
                                if texture_id > 0:  # Only add if not default/background
                                    assignment = TerrainTextureAssignment(
                                        x=x,
                                        y=y,
                                        texture_id=texture_id,
                                        blend_weights=[1.0],
                                    )
                                    texture_assignments.append(assignment)
                else:
                    logger.debug(
                        "Data size doesn't match grid format, trying alternative parsing"
                    )
                    # Try parsing as a sequence of records
                    while offset + 4 <= len(
                        data
                    ):  # At least x, y, texture_id (2 bytes each)
                        record_x = struct.unpack("<H", data[offset : offset + 2])[0]
                        record_y = struct.unpack("<H", data[offset + 2 : offset + 4])[0]

                        # Check if values are reasonable for map dimensions
                        if self.heightmap is None or (
                            record_x < self.heightmap.width
                            and record_y < self.heightmap.height
                        ):
                            # Get texture ID (might be 1 or 2 bytes)
                            if offset + 6 <= len(data):
                                texture_id = struct.unpack(
                                    "<H", data[offset + 4 : offset + 6]
                                )[0]
                                offset += 6
                            else:
                                texture_id = (
                                    struct.unpack("<B", data[offset + 4 : offset + 5])[
                                        0
                                    ]
                                    if offset + 5 <= len(data)
                                    else 0
                                )
                                offset += 5

                            assignment = TerrainTextureAssignment(
                                x=record_x,
                                y=record_y,
                                texture_id=texture_id,
                                blend_weights=[1.0],
                            )
                            texture_assignments.append(assignment)
                        else:
                            offset += 2  # Skip this value and continue

        except Exception as e:
            logger.warning(f"Error parsing terrain textures: {e}")

        self.terrain_textures = texture_assignments
        logger.info(f"Parsed {len(texture_assignments)} terrain texture assignments")

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
        import math

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
