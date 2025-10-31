#!/usr/bin/env python3
"""
Split large JSON files into smaller chunks
"""
import json
import math
from pathlib import Path


def split_json_file(input_file: Path, max_size_mb: int = 100):
    """Split a JSON array into multiple files"""
    
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    print(f"Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError("This tool only works with JSON arrays")
    
    total_items = len(data)
    print(f"Total items: {total_items}")
    
    # Calculate max items per chunk based on size
    max_size_bytes = max_size_mb * 1024 * 1024
    file_size = input_file.stat().st_size
    avg_item_size = file_size / total_items
    max_items_per_chunk = math.ceil(max_size_bytes / avg_item_size)
    
    print(f"File size: {file_size / (1024*1024):.1f} MB")
    print(f"Average item size: {avg_item_size:.0f} bytes")
    print(f"Max items per chunk: {max_items_per_chunk}")
    
    num_chunks = math.ceil(total_items / max_items_per_chunk)
    print(f"Will create {num_chunks} chunks")
    
    # Split the data
    output_dir = input_file.parent / f"{input_file.stem}_chunks"
    output_dir.mkdir(exist_ok=True)
    
    for chunk_idx in range(num_chunks):
        start_idx = chunk_idx * max_items_per_chunk
        end_idx = min(start_idx + max_items_per_chunk, total_items)
        chunk_data = data[start_idx:end_idx]
        
        chunk_filename = f"{input_file.stem}_part_{chunk_idx:02d}.json"
        chunk_path = output_dir / chunk_filename
        
        print(f"Writing chunk {chunk_idx + 1}/{num_chunks}: items {start_idx} to {end_idx - 1}")
        
        with open(chunk_path, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)
        
        print(f"  -> {chunk_path} ({chunk_path.stat().st_size / (1024*1024):.1f} MB)")
    
    print(f"\nAll chunks saved to: {output_dir}")
    
    # Create an index file for easy reference
    index_data = {
        "total_items": total_items,
        "num_chunks": num_chunks,
        "max_items_per_chunk": max_items_per_chunk,
        "chunks": [
            {
                "chunk_index": i,
                "filename": f"{input_file.stem}_part_{i:02d}.json",
                "start_index": i * max_items_per_chunk,
                "end_index": min((i + 1) * max_items_per_chunk, total_items),
                "item_count": min(max_items_per_chunk, total_items - (i * max_items_per_chunk))
            }
            for i in range(num_chunks)
        ]
    }
    
    index_path = output_dir / f"{input_file.stem}_index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"Index file created: {index_path}")
    return output_dir, index_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Split large JSON files into smaller chunks")
    parser.add_argument("input_file", help="Input JSON file path")
    parser.add_argument("--max-size", type=int, default=100, help="Max chunk size in MB (default: 100)")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    split_json_file(input_path, args.max_size)