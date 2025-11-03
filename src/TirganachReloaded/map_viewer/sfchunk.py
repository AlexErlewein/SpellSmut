"""
SpellForce Chunk File Parser
Based on C# SFChunkFile implementation from spellforce_data_editor

Chunk file format:
- 20-byte header (magic, format, type, version, checksum)
- Multiple chunks, each with 12-byte header:
  - ChunkID: 2 bytes (short)
  - ChunkOccurence: 2 bytes (short)
  - ChunkIsPacked: 2 bytes (short) - 0=unpacked, 1=packed
  - ChunkDataLength: 4 bytes (int)
  - ChunkDataType: 2 bytes (short)

If packed (ChunkIsPacked != 0):
  - unpacked_data_length: 4 bytes (int)
  - padding: 2 bytes
  - DEFLATE compressed data

The heightmap chunk (2) is packed with DEFLATE.
Texture chunks (3, 4) may be unpacked.
"""

import struct
import zlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from loguru import logger


@dataclass
class ChunkFileHeader:
    """20-byte chunk file header"""

    magic: int  # 4 bytes
    format: int  # 4 bytes (format version)
    type: int  # 4 bytes
    version: int  # 4 bytes
    checksum: int  # 4 bytes

    @classmethod
    def read(cls, data: bytes) -> "ChunkFileHeader":
        """Read header from first 20 bytes"""
        values = struct.unpack("<5I", data[:20])
        return cls(
            magic=values[0],
            format=values[1],
            type=values[2],
            version=values[3],
            checksum=values[4],
        )


@dataclass
class ChunkHeader:
    """12-byte chunk header"""

    chunk_id: int  # 2 bytes (short)
    chunk_occurence: int  # 2 bytes (short)
    chunk_is_packed: int  # 2 bytes (short) - 0=no, 1=yes
    chunk_data_length: int  # 4 bytes (int)
    chunk_data_type: int  # 2 bytes (short)

    @classmethod
    def read(cls, data: bytes, offset: int = 0) -> Tuple["ChunkHeader", int]:
        """Read chunk header and return (header, new_offset)"""
        values = struct.unpack("<3hIh", data[offset : offset + 12])
        header = cls(
            chunk_id=values[0],
            chunk_occurence=values[1],
            chunk_is_packed=values[2],
            chunk_data_length=values[3],
            chunk_data_type=values[4],
        )
        return header, offset + 12


@dataclass
class Chunk:
    """A chunk with header and data"""

    header: ChunkHeader
    data: bytes
    unpacked_length: Optional[int] = None

    def get_data(self) -> bytes:
        """Get chunk data (decompressed if packed)"""
        if self.header.chunk_is_packed == 0:
            # Not compressed
            return self.data
        else:
            # Compressed with DEFLATE
            # Data format: unpacked_length (4 bytes) + padding (2 bytes) + deflate data
            if len(self.data) < 6:
                logger.error(f"Packed chunk too small: {len(self.data)} bytes")
                return b""

            unpacked_length = struct.unpack("<I", self.data[0:4])[0]
            # Skip padding (2 bytes), then decompress
            deflate_data = self.data[6:]

            try:
                # Use DEFLATE decompression (not ZLIB)
                decompressed = zlib.decompress(deflate_data, -zlib.MAX_WBITS)

                if len(decompressed) != unpacked_length:
                    logger.warning(
                        f"Decompressed size mismatch: expected {unpacked_length}, got {len(decompressed)}"
                    )

                return decompressed
            except Exception as e:
                logger.error(f"Failed to decompress chunk: {e}")
                return b""


class ChunkFile:
    """
    SpellForce chunk file reader

    Usage:
        cf = ChunkFile()
        cf.open(filepath)
        chunk2 = cf.get_chunk(2)  # Get heightmap
        chunk3 = cf.get_chunk(3)  # Get tile definitions
        chunk4 = cf.get_chunk(4)  # Get texture IDs
    """

    def __init__(self):
        self.header: Optional[ChunkFileHeader] = None
        self.chunks: Dict[Tuple[int, int], Chunk] = {}  # (chunk_id, occurence) -> Chunk

    def open(self, filepath: str) -> bool:
        """Open and parse a chunk file"""
        try:
            logger.info(f"Opening chunk file: {filepath}")

            with open(filepath, "rb") as f:
                data = f.read()

            # Read file header
            if len(data) < 20:
                logger.error("File too small for chunk header")
                return False

            self.header = ChunkFileHeader.read(data)
            logger.info(
                f"Chunk file header: magic=0x{self.header.magic:08X}, "
                f"format={self.header.format}, type={self.header.type}, "
                f"version={self.header.version}"
            )

            # Parse chunks
            offset = 20  # Start after header
            chunk_count = 0

            while offset < len(data):
                # Check if we have enough data for chunk header
                if offset + 12 > len(data):
                    logger.debug(f"Reached end of file at offset {offset}")
                    break

                # Read chunk header
                chunk_header, offset = ChunkHeader.read(data, offset)

                # Check if chunk data fits
                if offset + chunk_header.chunk_data_length > len(data):
                    logger.warning(
                        f"Chunk {chunk_header.chunk_id} extends beyond file, stopping"
                    )
                    break

                # Read chunk data
                chunk_data = data[offset : offset + chunk_header.chunk_data_length]
                offset += chunk_header.chunk_data_length

                # Store chunk
                chunk = Chunk(header=chunk_header, data=chunk_data)
                key = (chunk_header.chunk_id, chunk_header.chunk_occurence)
                self.chunks[key] = chunk

                chunk_count += 1

                logger.debug(
                    f"Chunk {chunk_header.chunk_id} (occ={chunk_header.chunk_occurence}): "
                    f"packed={chunk_header.chunk_is_packed}, "
                    f"length={chunk_header.chunk_data_length}, "
                    f"type={chunk_header.chunk_data_type}"
                )

            logger.info(f"Parsed {chunk_count} chunks")

            return True

        except Exception as e:
            logger.exception(f"Failed to open chunk file: {e}")
            return False

    def get_chunk(self, chunk_id: int, occurence: int = 0) -> Optional[Chunk]:
        """Get a chunk by ID and occurence"""
        key = (chunk_id, occurence)
        return self.chunks.get(key)

    def get_chunk_data(self, chunk_id: int, occurence: int = 0) -> Optional[bytes]:
        """Get decompressed chunk data by ID"""
        chunk = self.get_chunk(chunk_id, occurence)
        if chunk:
            return chunk.get_data()
        return None

    def list_chunks(self) -> List[Tuple[int, int, int, int]]:
        """List all chunks as (chunk_id, occurence, is_packed, data_length)"""
        result = []
        for (chunk_id, occurence), chunk in sorted(self.chunks.items()):
            result.append(
                (
                    chunk_id,
                    occurence,
                    chunk.header.chunk_is_packed,
                    chunk.header.chunk_data_length,
                )
            )
        return result


# Convenience function
def load_chunk_file(filepath: str) -> Optional[ChunkFile]:
    """Load a chunk file"""
    cf = ChunkFile()
    if cf.open(filepath):
        return cf
    return None
