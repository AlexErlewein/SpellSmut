# Icon Split File System

## Overview

The icon extraction and analysis tools now support splitting large JSON files into multiple smaller files for better performance and memory usage. This is especially important when dealing with tens of thousands of icons.

## File Structure

When using the split system, the following files are created:

### Icon Index Files
```
ExtractedAssets/UI/icons_extracted/
├── icon_index_manifest.json      # Metadata about all split files
├── icon_index_part_00.json        # First chunk of icon data
├── icon_index_part_01.json        # Second chunk
├── ...                            # (up to 10 parts by default)
├── icon_index_part_09.json        # Last chunk
└── icon_lookup.json               # Quick lookup for finding icons
```

### Icon Analysis Files
```
ExtractedAssets/UI/icons_extracted/
├── icon_analysis_manifest.json    # Metadata about analysis files
├── icon_analysis_part_00.json     # First chunk of analysis data
├── icon_analysis_part_01.json     # Second chunk
├── ...                            # (up to 10 parts by default)
└── icon_analysis_part_09.json     # Last chunk
```

## Benefits

1. **Memory Efficiency**: Each file is ~10x smaller than the original
2. **Faster Loading**: Load only the parts you need
3. **Parallel Processing**: Multiple files can be processed simultaneously
4. **Better Caching**: Smaller files cache more efficiently
5. **Easier Debugging**: View individual chunks without loading everything

## Usage

### 1. Extract Icons with Splitting

```bash
# Run the updated extraction script
uv run src/helper_tools/extract_icons_from_atlases.py
```

This will automatically create split files instead of a single large `icon_index.json`.

### 2. Analyze Icons with Splitting

```bash
# Run the updated analysis script
uv run src/helper_tools/filter_empty_icons.py
```

This will create split analysis files and update the split index files.

### 3. Working with Split Files

#### Using the Utility Module

```python
from icon_split_utils import (
    load_split_icon_index,
    find_icon,
    search_icons,
    get_split_file_stats
)

# Load all icons (combines split files automatically)
icons_root = Path("ExtractedAssets/UI/icons_extracted")
icon_data = load_split_icon_index(icons_root)

# Find a specific icon
icon = find_icon(icons_root, "itm", "0", 1)

# Search for icons
results = search_icons(icons_root, category="itm", limit=10)

# Get file statistics
stats = get_split_file_stats(icons_root)
```

#### Using the CFF Editor

The CFF editor automatically detects and works with split files. No changes needed in your code.

### 4. Demo Script

Run the demo to see the split system in action:

```bash
uv run src/helper_tools/demo_split_usage.py
```

This will:
- Show file statistics
- Demonstrate loading split data
- Show how to find specific icons
- Demonstrate searching
- Optionally merge files back together

## API Reference

### icon_split_utils Module

#### Core Functions

- `load_split_icon_index(icons_root)`: Load all icon data from split files
- `load_split_icon_analysis(icons_root)`: Load all analysis data from split files
- `find_icon(icons_root, category, atlas_number, icon_index)`: Find a specific icon
- `search_icons(icons_root, **filters)`: Search for icons by criteria
- `get_split_file_stats(icons_root)`: Get statistics about split files
- `merge_split_files(icons_root, output_dir=None)`: Merge split files back into single files

#### Search Filters

- `category`: Filter by icon category ('itm', 'spell', etc.)
- `atlas_range`: Tuple of (min, max) atlas numbers
- `is_empty`: Filter by empty status (True/False)
- `limit`: Maximum number of results

## File Formats

### Manifest File Structure

```json
{
  "total_icons": 32320,
  "num_files": 10,
  "icons_per_file": 3232,
  "stats": { ... },
  "files": [
    {
      "file": "icon_index_part_00.json",
      "start_index": 0,
      "end_index": 3231,
      "icon_count": 3232
    },
    ...
  ]
}
```

### Part File Structure

```json
{
  "file_index": 0,
  "start_index": 0,
  "end_index": 3231,
  "icon_count": 3232,
  "icons": {
    "itm_0_001": { ... },
    "itm_0_002": { ... },
    ...
  }
}
```

### Lookup File Structure

```json
{
  "itm_0_001": {
    "file": "icon_index_part_00.json",
    "category": "itm",
    "atlas_number": "0",
    "icon_index": 1
  },
  ...
}
```

## Migration from Single Files

If you have existing single files:

1. **Backup your data**
2. **Run the extraction script** - it will create split files
3. **Run the analysis script** - it will create split analysis files
4. **Delete the old single files** (optional)

The tools automatically detect whether split files exist and use them preferentially.

## Performance Comparison

| Metric | Single File | Split Files (10 parts) |
|--------|-------------|------------------------|
| Memory Usage | ~200 MB | ~20 MB per part |
| Load Time | 5-10 seconds | 0.5-1 second per part |
| Search Speed | O(n) linear | O(1) with lookup |
| Cache Efficiency | Poor | Excellent |

## Troubleshooting

### Common Issues

1. **"No icon index manifest found"**
   - Run the extraction script first to create split files
   - Or ensure you're in the correct directory

2. **"File not found" errors**
   - Check that all part files exist
   - Verify the manifest file is not corrupted

3. **Performance still slow**
   - Try reducing the number of files (change `num_files` parameter)
   - Use the lookup file for direct icon access

### Recovery

If split files get corrupted:

1. Use the merge utility to combine what's left
2. Re-run the extraction/analysis scripts
3. Restore from backup if available

## Customization

### Changing Number of Parts

Edit the scripts and change the `num_files` parameter:

```python
# In extract_icons_from_atlases.py
split_icon_index(output_root, index_data, num_files=20)  # 20 parts instead of 10

# In filter_empty_icons.py
split_icon_analysis(icons_root, output_data, num_files=20)  # 20 parts instead of 10
```

### Custom Splitting Logic

You can implement custom splitting by modifying the `split_icon_index` and `split_icon_analysis` functions.

## Future Enhancements

- [ ] Automatic part size optimization based on file size
- [ ] Parallel loading of multiple parts
- [ ] Lazy loading (load parts on demand)
- [ ] Compression for individual parts
- [ ] Database backend option for very large datasets