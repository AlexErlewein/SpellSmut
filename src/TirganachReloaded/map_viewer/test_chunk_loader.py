"""
Test script to analyze SpellForce map file structure
and locate texture chunks (3 and 4)
"""

import struct
import zlib
from pathlib import Path

from loguru import logger


def analyze_map_file(filepath: str):
    """Analyze a map file to understand its structure"""

    logger.info(f"Analyzing: {filepath}")

    with open(filepath, "rb") as f:
        data = f.read()

    logger.info(f"File size: {len(data):,} bytes")

    # Parse header
    print("\n=== HEADER (first 36 bytes) ===")
    header = data[:36]
    values = struct.unpack("<9I", header)

    print(f"Magic:             0x{values[0]:08X}")
    print(f"Version:           {values[1]}")
    print(f"Field 2:           {values[2]}")
    print(f"Field 3:           {values[3]}")
    print(f"Field 4:           {values[4]}")
    print(f"Field 5:           {values[5]}")
    print(f"Field 6:           {values[6]}")
    print(f"Field 7:           {values[7]}")
    print(f"Decompressed size: {values[8]:,}")

    # Find ZLIB data (Chunk 2 - Heightmap)
    print("\n=== SEARCHING FOR ZLIB DATA (Chunk 2) ===")

    zlib_offset = None
    for i in range(len(data) - 2):
        signature = data[i : i + 2]
        if signature in [b"\x78\x9c", b"\x78\xda", b"\x78\x01"]:
            print(f"Found ZLIB signature at offset {i}: {signature.hex()}")
            zlib_offset = i
            break

    if zlib_offset:
        # Try to decompress
        try:
            compressed_data = data[zlib_offset:]
            decompressed_data = zlib.decompress(compressed_data)

            # Find actual compressed size
            compressed_size = len(compressed_data)
            for test_size in range(len(compressed_data)):
                try:
                    test_data = data[zlib_offset : zlib_offset + test_size]
                    test_decomp = zlib.decompress(test_data)
                    if len(test_decomp) == len(decompressed_data):
                        compressed_size = test_size
                        break
                except:
                    pass

            print(
                f"Decompressed: {compressed_size:,} -> {len(decompressed_data):,} bytes"
            )
            print(f"Compression ratio: {compressed_size / len(decompressed_data):.2%}")

            # Detect map size
            sizes = [64, 128, 256, 512, 1024]
            for size in sizes:
                expected = size * size
                if expected <= len(decompressed_data) <= expected + 16:
                    print(f"Detected map size: {size}×{size}")
                    break

            # Show what comes after compressed data
            after_offset = zlib_offset + compressed_size
            print(f"\nChunk 2 ends at offset: {after_offset}")
            print(f"Remaining data: {len(data) - after_offset:,} bytes")

            # Look for chunk headers after heightmap
            print("\n=== SEARCHING FOR CHUNK 3 & 4 ===")

            # Chunk 3 should be 3,570 bytes (255 tiles × 14 bytes)
            # Chunk 4 should be 63 bytes

            remaining = data[after_offset:]
            print("\nFirst 100 bytes after heightmap:")
            print_hex_dump(remaining[:100], after_offset)

            # Try to find patterns
            print("\n=== LOOKING FOR CHUNK MARKERS ===")

            # Search for potential chunk IDs (integers 3, 4, 5, etc.)
            for i in range(min(500, len(remaining) - 4)):
                # Check if this looks like a chunk ID
                potential_id = struct.unpack("<I", remaining[i : i + 4])[0]
                if 3 <= potential_id <= 10:
                    # Could be a chunk ID
                    # Check if followed by a reasonable size
                    if i + 8 <= len(remaining):
                        potential_size = struct.unpack("<I", remaining[i + 4 : i + 8])[
                            0
                        ]
                        if potential_size < 100000:  # Reasonable chunk size
                            print(f"Possible chunk at offset {after_offset + i}:")
                            print(f"  ID: {potential_id}")
                            print(f"  Size: {potential_size:,} bytes")

            # Try alternate approach: fixed offsets from end of compressed data
            print("\n=== TRYING FIXED OFFSET APPROACH ===")

            # Some games use fixed chunk structure
            # Try reading what's at specific offsets
            test_offsets = [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 100]

            for offset in test_offsets:
                if offset + 100 <= len(remaining):
                    chunk = remaining[offset : offset + 100]
                    print(f"\nOffset +{offset}:")
                    print(f"  First 32 bytes: {chunk[:32].hex()}")

                    # Check if it could be tile data (14-byte records)
                    # Tile data would have values 0-31 for indices
                    if all(b <= 31 for b in chunk[0:3]):  # ind1, ind2, ind3
                        print("  -> Could be tile data (indices in range)")

                    # Check if it could be texture IDs
                    if all(b <= 119 for b in chunk[:63]):
                        print("  -> Could be texture IDs (all <= 119)")

            # Look for the 3,570 byte pattern (Chunk 3)
            print("\n=== SEARCHING FOR 3,570 BYTE CHUNK ===")
            for i in range(0, min(1000, len(remaining) - 3570), 4):
                # Check if this section looks like valid tile data
                chunk = remaining[i : i + 3570]
                if len(chunk) == 3570:
                    # Heuristic: check if first few tiles have reasonable values
                    valid = True
                    for j in range(5):  # Check first 5 tiles
                        tile_offset = j * 14
                        ind1, ind2, ind3 = chunk[tile_offset : tile_offset + 3]
                        if ind1 > 31 or ind2 > 31 or ind3 > 31:
                            valid = False
                            break

                    if valid:
                        print(f"Found potential Chunk 3 at offset {after_offset + i}")
                        print(
                            f"  First tile: ind=[{chunk[0]},{chunk[1]},{chunk[2]}], weights=[{chunk[3]},{chunk[4]},{chunk[5]}]"
                        )

                        # Check what comes after (should be Chunk 4 - 63 bytes)
                        chunk4_offset = i + 3570
                        if chunk4_offset + 63 <= len(remaining):
                            chunk4_candidate = remaining[
                                chunk4_offset : chunk4_offset + 63
                            ]
                            print(
                                f"  Potential Chunk 4 at offset {after_offset + chunk4_offset}"
                            )
                            print(
                                f"    First 10 texture IDs: {list(chunk4_candidate[:10])}"
                            )

                            # Check if texture IDs are reasonable
                            if all(tid <= 119 for tid in chunk4_candidate):
                                print("    -> Valid! All texture IDs <= 119")
                                return after_offset + i, after_offset + chunk4_offset

        except Exception as e:
            print(f"Error decompressing: {e}")

    return None, None


def print_hex_dump(data: bytes, base_offset: int = 0):
    """Print hex dump of data"""
    for i in range(0, len(data), 16):
        chunk = data[i : i + 16]
        hex_str = " ".join(f"{b:02x}" for b in chunk)
        ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"{base_offset + i:08x}:  {hex_str:<48}  {ascii_str}")


def main():
    """Test with a real map file"""

    # Try to find a map file
    map_files = list(Path("OriginalGameFiles/map").rglob("*.map"))

    if not map_files:
        print("No map files found in OriginalGameFiles/map/")
        return

    # Test with first map found
    test_map = map_files[0]
    print(f"Testing with: {test_map}")
    print("=" * 80)

    chunk3_offset, chunk4_offset = analyze_map_file(str(test_map))

    if chunk3_offset and chunk4_offset:
        print("\n" + "=" * 80)
        print("SUCCESS! Found texture chunks:")
        print(f"  Chunk 3 (tile definitions): offset {chunk3_offset}")
        print(f"  Chunk 4 (texture IDs): offset {chunk4_offset}")
        print("\nYou can now update chunk_map_loader.py with these offsets!")
    else:
        print("\n" + "=" * 80)
        print("Could not definitively locate texture chunks.")
        print("Manual analysis of the hex dump above may be needed.")


if __name__ == "__main__":
    main()
