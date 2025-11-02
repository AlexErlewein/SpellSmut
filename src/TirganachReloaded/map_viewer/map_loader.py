"""
SpellForce Map Loader
Reads and parses SpellForce .map files (binary chunk format)

Based on the C# implementation in spellforce_data_editor/SFEngine/SFMap
"""

import struct
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
        self._read_chunks()

    def _read_chunks(self):
        """Read all chunks from the file"""
        try:
            while True:
                # Read chunk header
                chunk_header = self.file.read(8)
                if len(chunk_header) < 8:
                    break

                chunk_id, chunk_size = struct.unpack("<II", chunk_header)

                # Read chunk data
                chunk_data = self.file.read(chunk_size)

                if len(chunk_data) < chunk_size:
                    logger.warning(
                        f"Incomplete chunk {chunk_id}: expected {chunk_size}, got {len(chunk_data)}"
                    )
                    break

                self.chunks[chunk_id] = chunk_data
                logger.debug(f"Read chunk {chunk_id} with {chunk_size} bytes")

        except Exception as e:
            logger.error(f"Error reading chunks: {e}")

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
        chunk_data = self.chunk_reader.get_chunk(1)
        if not chunk_data:
            raise ValueError("Map header chunk (1) not found")

        # Parse header - adjust based on actual format
        if len(chunk_data) >= 16:
            version, width, height, chunk_count = struct.unpack(
                "<IIII", chunk_data[:16]
            )
            self.header = MapHeader(version, width, height, chunk_count)
            logger.debug(f"Map header: {width}x{height}, version {version}")
        else:
            raise ValueError(f"Invalid header chunk size: {len(chunk_data)}")

    def _load_heightmap(self):
        """Load heightmap data from chunk 2"""
        chunk_data = self.chunk_reader.get_chunk(2)
        if not chunk_data:
            logger.warning("Heightmap chunk (2) not found, using flat terrain")
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

            # Read grid dimensions if present
            if len(chunk_data) >= 8:
                grid_width, grid_height = struct.unpack(
                    "<II", chunk_data[offset : offset + 8]
                )
                offset += 8

                if grid_width != width or grid_height != height:
                    logger.warning(
                        f"Grid size mismatch: header={width}x{height}, grid={grid_width}x{grid_height}"
                    )

            # Read height values (assuming 2-byte signed integers or 4-byte floats)
            heights = []
            bytes_per_value = 2  # Could be 4 for floats

            for y in range(height):
                row = []
                for x in range(width):
                    if offset + bytes_per_value <= len(chunk_data):
                        if bytes_per_value == 2:
                            value = struct.unpack(
                                "<h", chunk_data[offset : offset + 2]
                            )[0]
                            height_value = float(value) / 10.0  # Scale factor
                        else:
                            height_value = struct.unpack(
                                "<f", chunk_data[offset : offset + 4]
                            )[0]
                        offset += bytes_per_value
                    else:
                        height_value = 0.0
                    row.append(height_value)
                heights.append(row)

            self.heightmap = HeightmapData(width=width, height=height, heights=heights)
            logger.debug(f"Loaded heightmap: {width}x{height}")

        except Exception as e:
            logger.error(f"Error loading heightmap: {e}")
            # Fallback to flat terrain
            self.heightmap = HeightmapData(
                width=self.header.width,
                height=self.header.height,
                heights=[[0.0] * self.header.width for _ in range(self.header.height)],
            )

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
