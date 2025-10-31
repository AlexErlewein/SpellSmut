#!/usr/bin/env python3
"""
Chunk large UI icon mapping JSON files to keep them under 100MB.

This script processes large JSON mapping files and splits them into 
manageable chunks to avoid performance issues with very large files.
"""

import json
import math
from pathlib import Path


def chunk_large_json(input_path: Path, output_dir: Path, chunk_size_mb: float = 50.0):
    """
    Split a large JSON file containing an object with many keys into chunks.
    
    Args:
        input_path: Path to the large JSON file
        output_dir: Directory to save chunked files
        chunk_size_mb: Maximum size of each chunk in MB (default 50MB to be safe)
    """
    print(f"Processing: {input_path.name}")
    print(f"Target chunk size: {chunk_size_mb}MB")
    
    # Load the large JSON file
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # The icon mapping has a specific structure with item_to_icons
    if "item_to_icons" not in data:
        print("  No 'item_to_icons' key found, nothing to chunk")
        return
    
    items = data["item_to_icons"]
    total_items = len(items)
    print(f"Total items to chunk: {total_items}")
    
    if total_items == 0:
        print("  No items to chunk")
        return
    
    # Calculate target items per chunk
    target_size_bytes = int(chunk_size_mb * 1024 * 1024)
    
    # Sample a few items to estimate size
    sample_size = min(50, total_items)
    sample_items = dict(list(items.items())[:sample_size])
    sample_subset = {"item_to_icons": sample_items}
    
    sample_json = json.dumps(sample_subset)
    estimated_size_per_item = len(sample_json.encode('utf-8')) / sample_size
    
    # Calculate how many items per chunk to stay under target
    items_per_chunk = max(1, int(target_size_bytes / estimated_size_per_item * 0.5))  # Half to be very safe
    total_chunks = math.ceil(total_items / items_per_chunk)
    
    print(f"Estimated {estimated_size_per_item:.2f} bytes per item")
    print(f"Will use {items_per_chunk} items per chunk")
    print(f"Creating {total_chunks} total chunks")
    
    # Prepare manifest
    manifest = {
        "description": "Chunked UI icon mapping manifest",
        "original_file": input_path.name,
        "total_items": total_items,
        "total_chunks": total_chunks,
        "target_chunk_size_mb": chunk_size_mb,
        "files": []
    }
    
    # Get list of items to chunk
    item_list = list(items.items())
    
    # Create chunks
    for chunk_idx in range(total_chunks):
        start_idx = chunk_idx * items_per_chunk
        end_idx = min(start_idx + items_per_chunk, total_items)
        
        # Extract chunk of items
        chunk_items = dict(item_list[start_idx:end_idx])
        
        # Create chunk data
        chunk_data = {
            "chunk_index": chunk_idx,
            "total_chunks": total_chunks,
            "total_items_in_chunk": len(chunk_items),
            "item_to_icons": chunk_items
        }
        
        # Write chunk
        chunk_filename = f"ui_icon_mapping_chunk_{chunk_idx:03d}.json"
        chunk_path = output_dir / chunk_filename
        
        with open(chunk_path, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=2)
        
        # Add to manifest
        manifest["files"].append({
            "filename": chunk_filename,
            "start_index": start_idx,
            "end_index": end_idx,
            "item_count": len(chunk_items)
        })
        
        print(f"  Chunk {chunk_idx + 1}/{total_chunks}: {len(chunk_items)} items -> {chunk_filename}")
    
    # Write manifest
    manifest_path = output_dir / "ui_icon_mapping_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✓ Chunking complete!")
    print(f"  Manifest: {manifest_path.name}")
    print(f"  Total chunks: {total_chunks}")
    

def combine_chunked_json(manifest_path: Path) -> dict:
    """
    Combine chunked JSON files back into a single mapping based on manifest.
    
    Args:
        manifest_path: Path to the manifest file
        
    Returns:
        Combined data dictionary
    """
    print(f"Combining chunked files from manifest: {manifest_path.name}")
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    combined_data = {"item_to_icons": {}}
    
    for file_info in manifest["files"]:
        chunk_path = manifest_path.parent / file_info["filename"]
        print(f"Loading chunk: {file_info['filename']}")
        
        with open(chunk_path, 'r', encoding='utf-8') as f:
            chunk_data = json.load(f)
        
        combined_data["item_to_icons"].update(chunk_data["item_to_icons"])
    
    print(f"✓ Combined {len(manifest['files'])} chunks with total {len(combined_data['item_to_icons'])} items")
    return combined_data


def main():
    """Main function to run the chunking tool."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Chunk large UI icon mapping JSON files to keep them under specified size"
    )
    parser.add_argument(
        "input_path",
        help="Path to the large JSON file to chunk (e.g., ui_icon_mapping.json)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory for chunked files (default: same as input file)",
        default=None
    )
    parser.add_argument(
        "-s", "--size",
        type=float,
        default=50.0,
        help="Target chunk size in MB (default: 50.0)"
    )
    parser.add_argument(
        "--combine",
        action="store_true",
        help="Combine chunked files back instead of chunking"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_path)
    
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        return 1
    
    # Set output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = input_path.parent
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.combine:
        # Combine files from manifest
        if input_path.name != "ui_icon_mapping_manifest.json":
            print("Error: For combine operation, input should be the manifest file")
            return 1
            
        combined = combine_chunked_json(input_path)
        
        # Write combined file
        output_path = input_path.parent / "ui_icon_mapping_combined.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(combined, f, indent=2)
        
        print(f"Combined mapping saved to: {output_path}")
    else:
        # Chunk the file
        chunk_large_json(input_path, output_dir, args.size)


if __name__ == "__main__":
    main()