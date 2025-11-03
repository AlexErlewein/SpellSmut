"""
SpellForce Map Loader
Reads and parses SpellForce .map files (binary chunk format)

Based on the C# implementation in spellforce_data_editor/SFEngine/SFMap
"""

import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, List, Optional

from loguru import logger


@dataclass
class MapHeader:
    """Map file header information"""

    version: int
    width: int
    height: int
    chunk_count: int


@dataclass
class HeightmapData:
    """Heightmap terrain elevation data"""

    width: int
    height: int
    heights: List[List[float]]  # 2D array of elevation values

    def get_height(self, x: int, y: int) -> float:
        """Get height at grid position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.heights[y][x]
        return 0.0


@dataclass
class TextureLayer:
    """Texture layer information for terrain"""

    texture_id: int
    texture_name: str
    blend_mode: int


@dataclass
class TerrainTexture:
    """Terrain texture assignment for a tile"""

    x: int
    y: int
    layers: List[TextureLayer]
    weights: List[float]  # Blend weights for each layer


@dataclass
class MapUnit:
    """Unit placed on the map"""

    unit_id: int
    x: float
    y: float
    z: float
    angle: float
    stats_id: int


@dataclass
class MapBuilding:
    """Building placed on the map"""

    building_id: int
    x: float
    y: float
    z: float
    angle: float
    building_type: int


@dataclass
class MapObject:
    """Interactive object on the map"""

    object_id: int
    x: float
    y: float
    z: float
    angle: float
    object_type: str


@dataclass
class MapMetadata:
    """Map metadata information"""

    map_name: str = ""
    description: str = ""
    author: str = ""
    player_count: int = 1
    map_type: str = ""  # "Campaign", "Skirmish", etc.


class ChunkReader:
    """Helper class for reading binary chunk files"""

    def __init__(self, file: BinaryIO):
        self.file = file
        self.chunks = {}
        self.is_compressed = False
        self._read_chunks()

    def _read_chunks(self):
        """Read all chunks from the file"""
        try:
            # Read the entire file first
            self.file.seek(0)
            raw_data = self.file.read()

            # Check for ZLIB compression signature (0x78 0x9c or similar)
            # SpellForce maps appear to have a custom header before zlib data
            logger.info(f"File size: {len(raw_data)} bytes")
            logger.debug(f"First 16 bytes: {raw_data[:16].hex()}")

            # Look for zlib signature
            zlib_start = -1
            for i in range(min(100, len(raw_data) - 2)):
                # Check for zlib signatures: 0x789c (default), 0x78da (best), 0x7801 (fastest)
                if raw_data[i : i + 2] in [b"\x78\x9c", b"\x78\xda", b"\x78\x01"]:
                    zlib_start = i
                    logger.info(f"Found zlib signature at offset {i}")
                    break

            if zlib_start >= 0:
                # File is compressed
                self.is_compressed = True
                logger.info("Map file is ZLIB compressed")

                try:
                    # Decompress from zlib signature onwards
                    compressed_data = raw_data[zlib_start:]
                    decompressed_data = zlib.decompress(compressed_data)
                    logger.info(
                        f"Decompressed {len(compressed_data)} -> {len(decompressed_data)} bytes"
                    )

                    # Now parse chunks from decompressed data
                    self._parse_chunks_from_data(decompressed_data)

                except zlib.error as e:
                    logger.error(f"Zlib decompression failed: {e}")
                    # Try parsing raw data as fallback
                    logger.warning("Attempting to parse raw data as chunks")
                    self._parse_chunks_from_data(raw_data)
            else:
                # Not compressed, parse directly
                logger.info("Map file is not compressed")
                self._parse_chunks_from_data(raw_data)

        except Exception as e:
            logger.exception(f"Error reading chunks: {e}")

    def _parse_chunks_from_data(self, data: bytes):
        """Parse chunk structures from decompressed data"""
        chunk_list = []
        offset = 0

        while offset + 8 <= len(data):
            # Read chunk header
            chunk_id, chunk_size = struct.unpack("<II", data[offset : offset + 8])
            offset += 8

            # Sanity check
            if chunk_size > len(data) - offset or chunk_size > 100_000_000:
                logger.warning(
                    f"Suspicious chunk size {chunk_size} at offset {offset - 8}, stopping"
                )
                break

            # Read chunk data
            chunk_data = data[offset : offset + chunk_size]

            if len(chunk_data) < chunk_size:
                logger.warning(
                    f"Incomplete chunk {chunk_id}: expected {chunk_size}, got {len(chunk_data)}"
                )
                break

            self.chunks[chunk_id] = chunk_data
            chunk_list.append((chunk_id, chunk_size))
            logger.debug(f"Read chunk {chunk_id} with {chunk_size} bytes")

            offset += chunk_size

        # Log all chunks found
        logger.info(
            f"Found {len(self.chunks)} chunks: {[f'{cid}({size}b)' for cid, size in chunk_list]}"
        )

    def has_chunk(self, chunk_id: int) -> bool:
        """Check if chunk exists"""
        return chunk_id in self.chunks

    def get_chunk(self, chunk_id: int) -> Optional[bytes]:
        """Get chunk data by ID"""
        return self.chunks.get(chunk_id)


class MapLoader:
    """
    Loads SpellForce .map files

    Map files use a chunk-based binary format:
    - Chunk 1: Map header (version, size, etc.)
    - Chunk 2: Heightmap data
    - Chunk 3: Terrain textures
    - Chunk 4: Units
    - Chunk 5: Buildings
    - Chunk 6: Objects
    - Additional chunks for other map data
    """

    def __init__(self):
        self.header: Optional[MapHeader] = None
        self.heightmap: Optional[HeightmapData] = None
        self.textures: List[TerrainTexture] = []
        self.units: List[MapUnit] = []
        self.buildings: List[MapBuilding] = []
        self.objects: List[MapObject] = []
        self.metadata: MapMetadata = MapMetadata()
        self.chunk_reader: Optional[ChunkReader] = None

    def load(self, filepath: Path) -> bool:
        """
        Load a map file

        Args:
            filepath: Path to .map file

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Loading map: {filepath}")

            if not filepath.exists():
                logger.error(f"Map file not found: {filepath}")
                return False

            with open(filepath, "rb") as f:
                self.chunk_reader = ChunkReader(f)

            # Load chunks in order
            self._load_header()
            self._load_heightmap()
            self._load_textures()
            self._load_units()
            self._load_buildings()
            self._load_objects()
            self._load_metadata()

            logger.info(
                f"Map loaded successfully: {self.header.width}x{self.header.height}"
            )
            logger.info(
                f"  Units: {len(self.units)}, Buildings: {len(self.buildings)}, Objects: {len(self.objects)}"
            )

            return True

        except Exception as e:
            logger.exception(f"Failed to load map: {e}")
            return False

    def _load_header(self):
        """Load map header from chunk 1"""
        # First, let's see what chunks we actually have
        available_chunks = list(self.chunk_reader.chunks.keys())
        logger.info(f"Available chunk IDs: {sorted(available_chunks)}")

        # Try to find a header chunk - it might not be chunk 1
        chunk_data = None
        header_chunk_id = None

        # Try common chunk IDs for headers
        for possible_id in [1, 0, 2, 10, 100]:
            chunk_data = self.chunk_reader.get_chunk(possible_id)
            if chunk_data and len(chunk_data) >= 16:
                header_chunk_id = possible_id
                logger.info(f"Found potential header in chunk {possible_id}")
                break

        if not chunk_data:
            # Use first chunk as fallback
            if available_chunks:
                header_chunk_id = available_chunks[0]
                chunk_data = self.chunk_reader.get_chunk(header_chunk_id)
                logger.warning(f"Using first chunk ({header_chunk_id}) as header")
            else:
                raise ValueError("No chunks found in map file")

        # Parse header - adjust based on actual format
        if len(chunk_data) >= 16:
            # Try to parse as header
            try:
                version, width, height, chunk_count = struct.unpack(
                    "<IIII", chunk_data[:16]
                )
                # Sanity check
                if 16 <= width <= 1024 and 16 <= height <= 1024:
                    self.header = MapHeader(version, width, height, chunk_count)
                    logger.info(
                        f"Map header: {width}x{height}, version {version}, chunks {chunk_count}"
                    )
                else:
                    # Try different byte order or format
                    logger.warning(
                        f"Header values seem wrong: {width}x{height}, trying alternative format"
                    )
                    # Create a default small map for testing
                    self.header = MapHeader(1, 128, 128, len(available_chunks))
            except Exception as e:
                logger.error(f"Failed to parse header: {e}")
                # Create default header
                self.header = MapHeader(1, 128, 128, len(available_chunks))
        else:
            raise ValueError(f"Invalid header chunk size: {len(chunk_data)}")

    def _load_heightmap(self):
        """Load heightmap data from chunk 2"""
        # Try multiple possible chunk IDs for heightmap
        chunk_data = None
        for possible_id in [2, 3, 4, 5]:
            chunk_data = self.chunk_reader.get_chunk(possible_id)
            if chunk_data:
                logger.info(f"Found heightmap data in chunk {possible_id}")
                break

        if not chunk_data:
            logger.warning(
                "Heightmap chunk not found in expected locations, using flat terrain"
            )
            # Create flat heightmap
            self.heightmap = HeightmapData(
                width=self.header.width,
                height=self.header.height,
                heights=[[0.0] * self.header.width for _ in range(self.header.height)],
            )
            return

        try:
            # Parse heightmap format
            # Format depends on actual SpellForce map format
            # This is a simplified version
            offset = 0
            width = self.header.width
            height = self.header.height

            logger.debug(
                f"Parsing heightmap chunk: {len(chunk_data)} bytes for {width}x{height} grid"
            )

            # Read grid dimensions if present
            if len(chunk_data) >= 8:
                try:
                    grid_width, grid_height = struct.unpack(
                        "<II", chunk_data[offset : offset + 8]
                    )
                    # Sanity check
                    if 16 <= grid_width <= 1024 and 16 <= grid_height <= 1024:
                        offset += 8
                        if grid_width != width or grid_height != height:
                            logger.warning(
                                f"Grid size mismatch: header={width}x{height}, grid={grid_width}x{grid_height}"
                            )
                            # Use the grid dimensions from chunk
                            width, height = grid_width, grid_height
                    else:
                        logger.debug(
                            f"Grid dimensions invalid ({grid_width}x{grid_height}), skipping header"
                        )
                except:
                    logger.debug("Could not parse grid dimensions, using header values")

            # Calculate expected data size
            expected_values = width * height
            remaining_bytes = len(chunk_data) - offset

            # Determine bytes per value
            bytes_per_value = 2
            if remaining_bytes >= expected_values * 4:
                bytes_per_value = 4  # Likely floats
                logger.debug("Using 4 bytes per height value (float)")
            elif remaining_bytes >= expected_values * 2:
                bytes_per_value = 2  # Likely shorts
                logger.debug("Using 2 bytes per height value (short)")
            else:
                bytes_per_value = 1  # Bytes
                logger.debug("Using 1 byte per height value")

            # Read height values
            heights = []
            for y in range(height):
                row = []
                for x in range(width):
                    if offset + bytes_per_value <= len(chunk_data):
                        try:
                            if bytes_per_value == 4:
                                height_value = struct.unpack(
                                    "<f", chunk_data[offset : offset + 4]
                                )[0]
                            elif bytes_per_value == 2:
                                value = struct.unpack(
                                    "<h", chunk_data[offset : offset + 2]
                                )[0]
                                height_value = float(value) / 10.0  # Scale factor
                            else:
                                value = chunk_data[offset]
                                height_value = float(value) / 10.0
                            offset += bytes_per_value
                        except:
                            height_value = 0.0
                    else:
                        height_value = 0.0
                    row.append(height_value)
                heights.append(row)

            self.heightmap = HeightmapData(width=width, height=height, heights=heights)
            logger.info(
                f"Loaded heightmap: {width}x{height} ({len(heights) * len(heights[0])} vertices)"
            )

        except Exception as e:
            logger.exception(f"Error loading heightmap: {e}")
            # Fallback to flat terrain
            self.heightmap = HeightmapData(
                width=self.header.width,
                height=self.header.height,
                heights=[[0.0] * self.header.width for _ in range(self.header.height)],
            )
            logger.warning("Using flat terrain as fallback")

    def _load_textures(self):
        """Load terrain texture data from chunk 3"""
        chunk_data = self.chunk_reader.get_chunk(3)
        if not chunk_data:
            logger.warning("Texture chunk (3) not found")
            return

        try:
            # Parse texture assignments
            # Format depends on actual implementation
            offset = 0

            # This is a simplified placeholder
            # Real implementation would parse texture layers and blend weights
            logger.debug(f"Texture chunk size: {len(chunk_data)} bytes")

        except Exception as e:
            logger.error(f"Error loading textures: {e}")

    def _load_units(self):
        """Load unit placements from chunk 4"""
        chunk_data = self.chunk_reader.get_chunk(4)
        if not chunk_data:
            logger.debug("Unit chunk (4) not found")
            return

        try:
            offset = 0

            # Read unit count
            if len(chunk_data) >= 4:
                unit_count = struct.unpack("<I", chunk_data[offset : offset + 4])[0]
                offset += 4

                # Read each unit
                unit_size = 24  # Adjust based on actual format
                for i in range(unit_count):
                    if offset + unit_size <= len(chunk_data):
                        # Parse unit data
                        unit_id = struct.unpack("<I", chunk_data[offset : offset + 4])[
                            0
                        ]
                        x = struct.unpack("<f", chunk_data[offset + 4 : offset + 8])[0]
                        y = struct.unpack("<f", chunk_data[offset + 8 : offset + 12])[0]
                        z = struct.unpack("<f", chunk_data[offset + 12 : offset + 16])[
                            0
                        ]
                        angle = struct.unpack(
                            "<f", chunk_data[offset + 16 : offset + 20]
                        )[0]
                        stats_id = struct.unpack(
                            "<I", chunk_data[offset + 20 : offset + 24]
                        )[0]

                        unit = MapUnit(unit_id, x, y, z, angle, stats_id)
                        self.units.append(unit)
                        offset += unit_size

                logger.debug(f"Loaded {len(self.units)} units")

        except Exception as e:
            logger.error(f"Error loading units: {e}")

    def _load_buildings(self):
        """Load building placements from chunk 5"""
        chunk_data = self.chunk_reader.get_chunk(5)
        if not chunk_data:
            logger.debug("Building chunk (5) not found")
            return

        try:
            offset = 0

            if len(chunk_data) >= 4:
                building_count = struct.unpack("<I", chunk_data[offset : offset + 4])[0]
                offset += 4

                building_size = 24
                for i in range(building_count):
                    if offset + building_size <= len(chunk_data):
                        building_id = struct.unpack(
                            "<I", chunk_data[offset : offset + 4]
                        )[0]
                        x = struct.unpack("<f", chunk_data[offset + 4 : offset + 8])[0]
                        y = struct.unpack("<f", chunk_data[offset + 8 : offset + 12])[0]
                        z = struct.unpack("<f", chunk_data[offset + 12 : offset + 16])[
                            0
                        ]
                        angle = struct.unpack(
                            "<f", chunk_data[offset + 16 : offset + 20]
                        )[0]
                        building_type = struct.unpack(
                            "<I", chunk_data[offset + 20 : offset + 24]
                        )[0]

                        building = MapBuilding(
                            building_id, x, y, z, angle, building_type
                        )
                        self.buildings.append(building)
                        offset += building_size

                logger.debug(f"Loaded {len(self.buildings)} buildings")

        except Exception as e:
            logger.error(f"Error loading buildings: {e}")

    def _load_objects(self):
        """Load interactive objects from chunk 6"""
        chunk_data = self.chunk_reader.get_chunk(6)
        if not chunk_data:
            logger.debug("Object chunk (6) not found")
            return

        try:
            # Similar to units/buildings
            # Format depends on actual implementation
            logger.debug(f"Object chunk size: {len(chunk_data)} bytes")

        except Exception as e:
            logger.error(f"Error loading objects: {e}")

    def _load_metadata(self):
        """Load map metadata from various chunks"""
        # Metadata might be in chunk 7 or other chunks
        chunk_data = self.chunk_reader.get_chunk(7)
        if not chunk_data:
            logger.debug("Metadata chunk (7) not found")
            return

        try:
            # Parse metadata
            # This would include map name, description, etc.
            offset = 0

            # Example: read null-terminated strings
            def read_string(data, start):
                end = data.find(b"\x00", start)
                if end == -1:
                    return "", start
                return data[start:end].decode("utf-8", errors="ignore"), end + 1

            if len(chunk_data) > 0:
                self.metadata.map_name, offset = read_string(chunk_data, offset)
                logger.debug(f"Map name: {self.metadata.map_name}")

        except Exception as e:
            logger.error(f"Error loading metadata: {e}")

    def get_height_at(self, x: float, y: float) -> float:
        """
        Get terrain height at world position
        Uses bilinear interpolation for smooth height values
        """
        if not self.heightmap:
            return 0.0

        # Convert to grid coordinates
        grid_x = int(x)
        grid_y = int(y)

        # Get fractional parts for interpolation
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
