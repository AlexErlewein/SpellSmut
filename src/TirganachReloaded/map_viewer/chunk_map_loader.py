"""
Chunk-Based SpellForce Map Loader
Loads maps with texture data from chunk-based format

Based on C# spellforce_data_editor analysis:
- Chunk 2: Heightmap (ZLIB compressed)
- Chunk 3: Tile definitions (255 tiles × 14 bytes)
- Chunk 4: Texture IDs (63 bytes)
"""

import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from loguru import logger


@dataclass
class TileDefinition:
    """Terrain tile with texture blending info"""

    ind1: int  # Base texture 1 index (0-31)
    ind2: int  # Base texture 2 index (0-31)
    ind3: int  # Base texture 3 index (0-31)
    weight1: int  # Blend weight 1 (0-255)
    weight2: int  # Blend weight 2 (0-255)
    weight3: int  # Blend weight 3 (0-255)
    reindex_data: int  # Unknown/unused
    reindex_index: int  # Unknown/unused
    material_property: int  # Material type ID
    blocks_movement: bool  # Movement blocking flag
    blocks_vision: bool  # Vision blocking flag

    def is_defined(self) -> bool:
        """Check if tile has any texture data"""
        return self.ind1 != 0 or self.ind2 != 0 or self.ind3 != 0

    def get_normalized_weights(self) -> Tuple[float, float, float]:
        """Get normalized blend weights (0.0-1.0)"""
        total = self.weight1 + self.weight2 + self.weight3
        if total == 0:
            return (1.0, 0.0, 0.0)  # Default to first texture

        return (self.weight1 / total, self.weight2 / total, self.weight3 / total)


@dataclass
class ChunkHeader:
    """Chunk file header"""

    chunk_id: int
    chunk_size: int
    chunk_offset: int


class ChunkMapLoader:
    """
    Load SpellForce maps with chunk-based format

    File structure:
    - Header (varies)
    - Chunk 1: Unknown
    - Chunk 2: Heightmap (ZLIB compressed)
    - Chunk 3: Tile definitions (255 × 14 bytes = 3,570 bytes)
    - Chunk 4: Texture IDs (63 bytes)
    - Chunk 5+: Other data (entities, objects, etc.)
    """

    def __init__(self):
        self.chunks: Dict[int, bytes] = {}
        self.heightmap: Optional[np.ndarray] = None
        self.width: int = 0
        self.height: int = 0
        self.texture_ids: Optional[List[int]] = None
        self.tile_definitions: Optional[List[TileDefinition]] = None

    def load_map(
        self, filepath: Path
    ) -> Tuple[
        Optional[np.ndarray],
        int,
        int,
        Optional[List[int]],
        Optional[List[TileDefinition]],
    ]:
        """
        Load map with texture data

        Args:
            filepath: Path to .map file

        Returns:
            Tuple of:
                - heightmap: numpy array (height × width) of float heights
                - width: map width in cells
                - height: map height in cells
                - texture_ids: list of 63 texture IDs
                - tile_definitions: list of 255 tile definitions
        """
        try:
            logger.info(f"Loading chunk-based map: {filepath}")

            with open(filepath, "rb") as f:
                file_data = f.read()

            # Parse chunk structure
            if not self._parse_chunks(file_data):
                logger.error("Failed to parse chunk structure")
                return None, 0, 0, None, None

            # Parse Chunk 2: Heightmap
            if 2 not in self.chunks:
                logger.error("Chunk 2 (heightmap) not found")
                return None, 0, 0, None, None

            if not self._parse_heightmap():
                logger.error("Failed to parse heightmap")
                return None, 0, 0, None, None

            # Parse Chunk 3: Tile definitions
            if 3 in self.chunks:
                self._parse_tile_definitions()
            else:
                logger.warning("Chunk 3 (tile definitions) not found")

            # Parse Chunk 4: Texture IDs
            if 4 in self.chunks:
                self._parse_texture_ids()
            else:
                logger.warning("Chunk 4 (texture IDs) not found")

            logger.info(
                f"Map loaded: {self.width}×{self.height}, "
                f"textures={'yes' if self.texture_ids else 'no'}"
            )

            return (
                self.heightmap,
                self.width,
                self.height,
                self.texture_ids,
                self.tile_definitions,
            )

        except Exception as e:
            logger.exception(f"Failed to load map: {e}")
            return None, 0, 0, None, None

    def _parse_chunks(self, data: bytes) -> bool:
        """
        Parse chunk file structure

        Note: SpellForce uses a custom chunk format.
        This is a simplified parser based on observed patterns.
        """
        try:
            # Check for magic number
            if len(data) < 4:
                return False

            magic = struct.unpack("<I", data[0:4])[0]
            logger.debug(f"File magic: 0x{magic:08X}")

            # Try to find chunks by looking for known patterns
            # Chunk 2 typically starts with ZLIB signature at offset 36+
            # We'll use a simple approach: assume standard offsets

            # For now, use the simple approach:
            # - Chunk 2 starts at offset 36 (heightmap)
            # - After decompressing heightmap, look for more data

            # Try to find ZLIB compressed data (Chunk 2)
            offset = 36  # Standard header size
            while offset < len(data) - 2:
                # Check for ZLIB signature
                signature = data[offset : offset + 2]
                if signature in [b"\x78\x9c", b"\x78\xda", b"\x78\x01"]:
                    # Found ZLIB data - this is chunk 2
                    try:
                        # Try to decompress to find chunk boundaries
                        remaining = data[offset:]
                        decompressed = zlib.decompress(remaining)
                        compressed_size = len(remaining) - len(
                            zlib.compress(decompressed, 9)
                        )

                        # Chunk 2: Heightmap
                        self.chunks[2] = data[
                            offset : offset + compressed_size + 100
                        ]  # Add buffer

                        # Look for additional chunks after compressed data
                        # In practice, chunks 3 and 4 might be embedded differently
                        # For now, we'll try a heuristic approach

                        logger.debug(f"Found Chunk 2 at offset {offset}")
                        break
                    except:
                        pass

                offset += 1

            # Attempt to find Chunk 3 and 4 by searching after heightmap
            # This is a best-effort approach - may need refinement with real files
            self._find_texture_chunks(data)

            return len(self.chunks) > 0

        except Exception as e:
            logger.error(f"Failed to parse chunks: {e}")
            return False

    def _find_texture_chunks(self, data: bytes):
        """
        Try to locate texture chunks (3 and 4)

        This is heuristic - may need adjustment based on actual file structure
        """
        try:
            # Chunk 3 should be 3,570 bytes (255 tiles × 14 bytes)
            # Chunk 4 should be 63 bytes

            # Look for a 3,570 byte section that could be chunk 3
            # Followed by a 63 byte section

            # For now, we'll implement a placeholder
            # Real implementation would need to understand the chunk header format

            logger.debug("Searching for texture chunks (placeholder)")

            # TODO: Implement proper chunk header parsing
            # This may require analyzing more sample files

        except Exception as e:
            logger.error(f"Error finding texture chunks: {e}")

    def _parse_heightmap(self) -> bool:
        """Parse heightmap from Chunk 2"""
        try:
            chunk_data = self.chunks[2]

            # Find ZLIB signature
            zlib_offset = 0
            for i in range(len(chunk_data) - 2):
                signature = chunk_data[i : i + 2]
                if signature in [b"\x78\x9c", b"\x78\xda", b"\x78\x01"]:
                    zlib_offset = i
                    break

            # Decompress
            compressed_data = chunk_data[zlib_offset:]
            decompressed_data = zlib.decompress(compressed_data)

            logger.debug(
                f"Decompressed {len(compressed_data)} -> {len(decompressed_data)} bytes"
            )

            # Detect map size and parse heightmap
            # Try common sizes: 64, 128, 256, 512, 1024
            sizes = [1024, 512, 256, 128, 64]

            for size in sizes:
                expected = size * size
                # Allow for small header (1-16 bytes)
                if expected <= len(decompressed_data) <= expected + 16:
                    self.width = size
                    self.height = size

                    # Skip header (if any)
                    header_size = len(decompressed_data) - expected
                    heightmap_data = decompressed_data[header_size:]

                    # Parse heightmap
                    heights = np.frombuffer(heightmap_data, dtype=np.uint8)
                    heights = heights.reshape((self.height, self.width))

                    # Convert to float (0-255 -> 0.0-100.0)
                    self.heightmap = heights.astype(np.float32) * (100.0 / 255.0)

                    logger.info(f"Parsed heightmap: {self.width}×{self.height}")
                    logger.info(
                        f"Height range: {self.heightmap.min():.2f} - {self.heightmap.max():.2f}"
                    )

                    return True

            logger.error(
                f"Could not determine map size from {len(decompressed_data)} bytes"
            )
            return False

        except Exception as e:
            logger.error(f"Failed to parse heightmap: {e}")
            return False

    def _parse_tile_definitions(self):
        """
        Parse 255 tile definitions from Chunk 3

        Each tile: 14 bytes
        Total: 255 × 14 = 3,570 bytes
        """
        try:
            chunk_data = self.chunks[3]

            if len(chunk_data) < 3570:
                logger.warning(
                    f"Chunk 3 too small: {len(chunk_data)} bytes (expected 3,570)"
                )
                return

            self.tile_definitions = []

            for i in range(255):
                offset = i * 14

                # Parse tile data
                ind1 = chunk_data[offset + 0]
                ind2 = chunk_data[offset + 1]
                ind3 = chunk_data[offset + 2]
                weight1 = chunk_data[offset + 3]
                weight2 = chunk_data[offset + 4]
                weight3 = chunk_data[offset + 5]
                reindex_data = chunk_data[offset + 6]
                reindex_index = chunk_data[offset + 7]
                # offset + 8, 9: padding/unknown
                material_property = chunk_data[offset + 10]
                # offset + 11: padding/unknown
                blocks_movement_byte = chunk_data[offset + 12]
                blocks_vision_byte = chunk_data[offset + 13]

                tile = TileDefinition(
                    ind1=ind1,
                    ind2=ind2,
                    ind3=ind3,
                    weight1=weight1,
                    weight2=weight2,
                    weight3=weight3,
                    reindex_data=reindex_data,
                    reindex_index=reindex_index,
                    material_property=material_property,
                    blocks_movement=(blocks_movement_byte % 2) == 1,
                    blocks_vision=(blocks_vision_byte % 2) == 1,
                )

                self.tile_definitions.append(tile)

            # Count defined tiles
            defined_count = sum(
                1 for tile in self.tile_definitions if tile.is_defined()
            )
            logger.info(f"Parsed {defined_count} defined tiles (out of 255)")

            # Log some examples
            if defined_count > 0:
                for i, tile in enumerate(self.tile_definitions):
                    if tile.is_defined():
                        logger.debug(
                            f"Tile {i}: indices=[{tile.ind1},{tile.ind2},{tile.ind3}], "
                            f"weights=[{tile.weight1},{tile.weight2},{tile.weight3}]"
                        )
                        if i >= 5:  # Only show first few
                            break

        except Exception as e:
            logger.error(f"Failed to parse tile definitions: {e}")

    def _parse_texture_ids(self):
        """
        Parse 63 texture IDs from Chunk 4

        Layout:
        - Index 0: Base world texture (always 0)
        - Indices 1-31: "Far" texture IDs
        - Indices 32-62: "Near" texture IDs
        """
        try:
            chunk_data = self.chunks[4]

            if len(chunk_data) < 63:
                logger.warning(
                    f"Chunk 4 too small: {len(chunk_data)} bytes (expected 63)"
                )
                return

            self.texture_ids = list(chunk_data[:63])

            logger.info(f"Parsed {len(self.texture_ids)} texture IDs")
            logger.debug(f"Texture IDs [0-9]: {self.texture_ids[:10]}")
            logger.debug(f"Texture IDs [32-41]: {self.texture_ids[32:42]}")

        except Exception as e:
            logger.error(f"Failed to parse texture IDs: {e}")


# Convenience function
def load_map_with_textures(
    filepath: str,
) -> Tuple[
    Optional[np.ndarray], int, int, Optional[List[int]], Optional[List[TileDefinition]]
]:
    """
    Convenience function to load a map with textures

    Args:
        filepath: Path to .map file

    Returns:
        Tuple of (heightmap, width, height, texture_ids, tile_definitions)
    """
    loader = ChunkMapLoader()
    return loader.load_map(Path(filepath))
