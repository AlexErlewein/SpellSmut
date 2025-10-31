# SpellForce Asset Extractor

This tool extracts game assets from SpellForce Platinum Edition PAK files and provides diff comparison functionality to track changes between different versions.

## Features

1. **Asset Extraction**: Extracts all game assets using QuickBMS
2. **Organization**: Automatically organizes assets in structured directory layout
3. **Reference System**: Creates reference snapshots of original files
4. **Diff Comparison**: Compares extracted assets with reference to show changes
5. **Detailed Reports**: Generates comprehensive reports of additions, deletions, and modifications

## Usage

### Extract Assets
```bash
python asset_extractor.py --extract
```

### Create Reference Snapshot
```bash
python asset_extractor.py --create-reference
```

### Compare with Reference
```bash
python asset_extractor.py --compare
```

### Combine Operations
```bash
python asset_extractor.py --extract --create-reference --compare
```

## Options

- `--force`: Force re-extraction or recreate reference snapshot
- `--output-dir DIR`: Specify custom output directory for extraction

## Workflow

1. **First-time setup**: Run `--extract --create-reference` to extract original game assets and create a reference
2. **After modding**: Run `--extract --compare` to see what changed
3. **Update reference**: Run `--create-reference --force` to update reference with current state

## Output

- **Extracted Assets**: Organized in `ExtractedAssets/` directory
- **Reference Snapshot**: Stored in `ReferenceAssets/reference_snapshot.json`
- **Diff Report**: Generated as `ExtractedAssets/diff_report.md`