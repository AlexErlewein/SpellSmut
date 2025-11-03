#!/usr/bin/env python3
"""
SpellForce Map Inspector
Analyzes .map files to understand their binary structure
"""

import struct
import sys
import zlib
from pathlib import Path
from typing import BinaryIO, List, Tuple


def read_chunks(file: BinaryIO) -> List[Tuple[int, int, bytes]]:
    """Read all chunks from a map file"""
    chunks = []
    file.seek(0)
    raw_data = file.read()

    print(f"File size: {len(raw_data)} bytes")
    print(f"First 16 bytes: {raw_data[:16].hex()}")

    # Check for ZLIB compression
    zlib_start = -1
    for i in range(min(100, len(raw_data) - 2)):
        if raw_data[i : i + 2] in [b"\x78\x9c", b"\x78\xda", b"\x78\x01"]:
            zlib_start = i
            print(f"\n✓ Found ZLIB signature at offset {i}")
            break

    if zlib_start >= 0:
        try:
            compressed_data = raw_data[zlib_start:]
            decompressed_data = zlib.decompress(compressed_data)
            print(
                f"✓ Decompressed {len(compressed_data)} -> {len(decompressed_data)} bytes"
            )
            print(
                f"Header before compression ({zlib_start} bytes): {raw_data[:zlib_start].hex()}"
            )

            # Parse decompressed data
            data = decompressed_data
        except zlib.error as e:
            print(f"✗ ZLIB decompression failed: {e}")
            print("Attempting to parse raw data...")
            data = raw_data
    else:
        print("\nNo ZLIB compression detected, parsing raw data")
        data = raw_data

    # Parse chunks from data
    offset = 0
    while offset + 8 <= len(data):
        chunk_id, chunk_size = struct.unpack("<II", data[offset : offset + 8])
        offset += 8

        # Sanity check
        if chunk_size > len(data) - offset or chunk_size > 100_000_000:
            print(
                f"\nWARNING: Suspicious chunk size {chunk_size} at offset {offset - 8}, stopping"
            )
            break

        chunk_data = data[offset : offset + chunk_size]
        if len(chunk_data) < chunk_size:
            print(
                f"WARNING: Incomplete chunk {chunk_id}: expected {chunk_size}, got {len(chunk_data)}"
            )
            break

        chunks.append((chunk_id, chunk_size, chunk_data))
        offset += chunk_size

    return chunks


def hexdump(data: bytes, length: int = 256, width: int = 16) -> str:
    """Create a hexdump string"""
    lines = []
    for i in range(0, min(length, len(data)), width):
        # Hex values
        hex_part = " ".join(f"{b:02x}" for b in data[i : i + width])
        # ASCII representation
        ascii_part = "".join(
            chr(b) if 32 <= b < 127 else "." for b in data[i : i + width]
        )
        lines.append(f"{i:08x}  {hex_part:<{width * 3}}  {ascii_part}")
    return "\n".join(lines)


def analyze_chunk_as_integers(data: bytes, count: int = 20) -> str:
    """Try to interpret chunk as various integer types"""
    results = []

    # Try as uint32
    if len(data) >= 4:
        results.append("As uint32 (little-endian):")
        values = []
        for i in range(0, min(count * 4, len(data)), 4):
            if i + 4 <= len(data):
                val = struct.unpack("<I", data[i : i + 4])[0]
                values.append(f"{val}")
        results.append("  " + ", ".join(values[:count]))

    # Try as int32
    if len(data) >= 4:
        results.append("\nAs int32 (little-endian):")
        values = []
        for i in range(0, min(count * 4, len(data)), 4):
            if i + 4 <= len(data):
                val = struct.unpack("<i", data[i : i + 4])[0]
                values.append(f"{val}")
        results.append("  " + ", ".join(values[:count]))

    # Try as float
    if len(data) >= 4:
        results.append("\nAs float (little-endian):")
        values = []
        for i in range(0, min(count * 4, len(data)), 4):
            if i + 4 <= len(data):
                try:
                    val = struct.unpack("<f", data[i : i + 4])[0]
                    values.append(f"{val:.2f}")
                except:
                    values.append("N/A")
        results.append("  " + ", ".join(values[:count]))

    # Try as uint16
    if len(data) >= 2:
        results.append("\nAs uint16 (little-endian):")
        values = []
        for i in range(0, min(count * 2, len(data)), 2):
            if i + 2 <= len(data):
                val = struct.unpack("<H", data[i : i + 2])[0]
                values.append(f"{val}")
        results.append("  " + ", ".join(values[:count]))

    return "\n".join(results)


def find_strings(data: bytes, min_length: int = 4) -> List[str]:
    """Find null-terminated strings in data"""
    strings = []
    current = []

    for byte in data:
        if 32 <= byte < 127:  # Printable ASCII
            current.append(chr(byte))
        elif byte == 0 and len(current) >= min_length:
            strings.append("".join(current))
            current = []
        else:
            current = []

    return strings[:20]  # Limit to first 20 strings


def analyze_map_file(filepath: Path):
    """Analyze a SpellForce map file"""
    print(f"\n{'=' * 80}")
    print(f"Analyzing: {filepath.name}")
    print(f"File size: {filepath.stat().st_size:,} bytes")
    print(f"{'=' * 80}\n")

    with open(filepath, "rb") as f:
        chunks = read_chunks(f)

    print(f"Found {len(chunks)} chunks:\n")

    # Summary table
    print(f"{'Chunk ID':<12} {'Size (bytes)':<15} {'Size (KB)':<12} {'% of file':<12}")
    print("-" * 60)

    total_size = sum(size for _, size, _ in chunks)
    for chunk_id, chunk_size, _ in chunks:
        percentage = (chunk_size / total_size * 100) if total_size > 0 else 0
        print(
            f"{chunk_id:<12} {chunk_size:<15,} {chunk_size / 1024:<12.2f} {percentage:<12.1f}%"
        )

    print("\n" + "=" * 80 + "\n")

    # Detailed analysis of each chunk
    for idx, (chunk_id, chunk_size, data) in enumerate(chunks):
        print(f"\nChunk {chunk_id} (#{idx + 1}) - {chunk_size:,} bytes")
        print("-" * 80)

        # Hexdump first 256 bytes
        print("\nFirst 256 bytes (hex dump):")
        print(hexdump(data, 256))

        # Try to interpret as various types
        print("\n\nPossible interpretations:")
        print(analyze_chunk_as_integers(data, count=16))

        # Look for strings
        strings = find_strings(data)
        if strings:
            print("\n\nStrings found:")
            for s in strings[:10]:
                print(f"  '{s}'")

        # Special analysis for likely header chunks
        if idx == 0 or chunk_id in [0, 1, 2]:
            print("\n\n--- POTENTIAL HEADER ANALYSIS ---")
            if len(data) >= 16:
                vals = struct.unpack("<IIII", data[:16])
                print(f"First 4 uint32s: {vals}")
                print(
                    f"  Could be: version={vals[0]}, width={vals[1]}, height={vals[2]}, count={vals[3]}"
                )

                # Check if width/height make sense
                if 16 <= vals[1] <= 1024 and 16 <= vals[2] <= 1024:
                    print("  ✓ Width and height look reasonable!")
                else:
                    print("  ✗ Width/height seem unusual")

        # Look for heightmap patterns (many repeated values in a range)
        if len(data) > 1000:
            print("\n\n--- HEIGHTMAP ANALYSIS ---")
            # Sample as int16
            samples = []
            for i in range(0, min(200, len(data) - 2), 2):
                val = struct.unpack("<h", data[i : i + 2])[0]
                samples.append(val)

            if samples:
                min_val = min(samples)
                max_val = max(samples)
                avg_val = sum(samples) / len(samples)
                print(f"As int16: min={min_val}, max={max_val}, avg={avg_val:.1f}")

                if -10000 < min_val < 10000 and -10000 < max_val < 10000:
                    print("  ✓ Values look like terrain heights!")

        print("\n" + "=" * 80)

        # Stop after first few chunks to avoid too much output
        if idx >= 5:
            remaining = len(chunks) - idx - 1
            if remaining > 0:
                print(f"\n... and {remaining} more chunks not shown ...")
            break


def main():
    if len(sys.argv) < 2:
        print("Usage: python inspect_map.py <map_file.map>")
        print(
            "\nThis tool analyzes SpellForce .map files to understand their structure."
        )
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    analyze_map_file(filepath)

    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("\nTips:")
    print("  - Look for chunks with reasonable width/height values (64-1024)")
    print("  - Heightmap chunks usually contain many int16 or float values")
    print("  - Look for strings that might be map names or metadata")
    print("  - First chunk is often (but not always) the header")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
