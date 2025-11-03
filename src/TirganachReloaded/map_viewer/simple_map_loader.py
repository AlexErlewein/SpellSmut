"""
Simple SpellForce Map Loader
Loads heightmap-only data from actual SpellForce .map files

Based on reverse engineering of Coop_02_dark.map:
- 36 byte header
- ZLIB compressed heightmap data
- Decompressed format: small header + WIDTHxHEIGHT bytes
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
    Simplified map loader for SpellForce .map files

    Format discovered:
    1. 36-byte header with magic, version, size info
    2. ZLIB compressed data starting at offset 36
    3. Decompressed data = small header + heightmap bytes
    """

    def __init__(self):
        self.header: Optional[SimpleMapHeader] = None
        self.heightmap: Optional[SimpleHeightmap] = None
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

            # Parse heightmap
            if not self._parse_heightmap():
                return False

            logger.info(
                f"Map loaded successfully: {self.heightmap.width}x{self.heightmap.height}"
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

    def _parse_heightmap(self) -> bool:
        """Parse heightmap from decompressed data"""
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
            logger.exception(f"Failed to parse heightmap: {e}")
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
