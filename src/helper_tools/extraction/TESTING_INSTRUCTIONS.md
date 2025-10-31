# Testing the Asset Extraction Tool

## Prerequisites

Before testing, ensure you have:

1. **Python environment set up** with PySide6 installed
2. **SpellForce Platinum Edition PAK files** copied to `OriginalGameFiles/pak/`
3. **QuickBMS installed** (will be installed automatically by `bulk_extract_paks.py`)
4. **Platform-specific requirements**:
   - **macOS**: Native QuickBMS executable is available
   - **Windows**: Windows QuickBMS executable will be installed

## Platform Compatibility

The tool works on multiple platforms:
- **macOS**: Native QuickBMS executable is available and working (verified)
- **Windows**: Windows QuickBMS executable
- **Linux**: May work with Wine or a Linux version of QuickBMS

## Testing the Command-Line Version

### 1. Basic Extraction Test
```bash
# Activate virtual environment
source /Users/alex/.venv/bin/activate

# Run extraction
python3 src/helper_tools/extraction/asset_extractor.py --extract
```

Expected output:
- Should show "Starting asset extraction..."
- Should display progress information
- Should end with "Asset extraction completed successfully"

### 2. Reference Creation Test
```bash
# Create reference snapshot
python3 src/helper_tools/extraction/asset_extractor.py --create-reference
```

Expected output:
- Should show "Creating reference snapshot of original game files..."
- Should end with "Reference snapshot created successfully"

### 3. Comparison Test
```bash
# Compare current assets with reference
python3 src/helper_tools/extraction/asset_extractor.py --compare
```

Expected output:
- Should show "Comparing current assets with reference..."
- Should display a summary of differences
- Should end with "Comparison completed successfully"

### 4. Combined Operations Test
```bash
# Run all operations together
python3 src/helper_tools/extraction/asset_extractor.py --extract --create-reference --compare
```

## Testing the GUI Version

### 1. Launch the GUI
```bash
# Activate virtual environment
source /Users/alex/.venv/bin/activate

# Run GUI
python3 src/helper_tools/extraction/asset_extractor_gui.py
```

### 2. Test Asset Extraction Tab
1. Click "Extract Assets" button
2. Observe:
   - Progress bar appears
   - Log area shows extraction progress
   - Status bar updates with current operation
   - Success dialog appears when complete

### 3. Test Reference Management Tab
1. Click "Create Reference Snapshot" button
2. Observe:
   - Progress bar appears
   - Reference information updates with snapshot details
   - Success dialog appears when complete

### 4. Test Diff Comparison Tab
1. Click "Compare with Reference" button
2. Observe:
   - Progress bar appears
   - Summary and details panels populate with comparison results
   - Success dialog appears when complete

## Error Handling Tests

### 1. Missing PAK Files Test
1. Temporarily rename or move PAK files from `OriginalGameFiles/pak/`
2. Try extraction
3. Expected behavior:
   - Clear error message explaining the issue
   - Guidance on how to fix it

### 2. Missing QuickBMS Test
1. Temporarily rename QuickBMS executable
2. Try extraction
3. Expected behavior:
   - Warning dialog about missing QuickBMS
   - Guidance on how to install it

### 3. Cross-Platform Specific Tests
1. **File permissions**: When copying PAK files from Windows to macOS, verify they have correct permissions
2. **Path compatibility**: Ensure paths work correctly on your platform
3. **QuickBMS execution**: Verify QuickBMS runs properly on your system

## Verification Steps

### 1. Check Output Files
After successful extraction, verify these files exist:
- `ExtractedAssets/` directory with organized assets
- `ReferenceAssets/reference_snapshot.json`
- `ExtractedAssets/diff_report.md`

### 2. Verify Functionality
- Reference snapshot should contain asset metadata
- Diff report should show accurate comparison results
- GUI should display all information correctly

## Troubleshooting

### Common Issues

1. **"PAK directory not found"**
   - Solution: Create `OriginalGameFiles/pak/` and copy PAK files

2. **"QuickBMS not found"**
   - Solution: Run `bulk_extract_paks.py` to install QuickBMS

3. **"No PAK files found"**
   - Solution: Verify PAK files are in `OriginalGameFiles/pak/`

4. **Permission errors**
   - Solution: Ensure read permissions on PAK files

5. **Platform-specific issues**
   - On macOS: Check that the QuickBMS executable has execute permissions
   - On Windows: Ensure no antivirus is blocking QuickBMS
   - On Linux: May require Wine or native QuickBMS

### Debugging Tips

1. **Platform-specific verification**:
   ```bash
   # Check QuickBMS executable
   /Users/alex/Desktop/code/Others/SpellSmut-asset-extraction-check/ModdingTools/quickbms/quickbms -h
   ```

2. **Check file permissions**:
   ```bash
   # Ensure PAK files have read permissions
   ls -la OriginalGameFiles/pak/
   ```

3. **Enable detailed logging**:
   ```bash
   # Add verbose output to see more details
   python3 src/helper_tools/extraction/asset_extractor.py --extract --verbose
   ```

4. **Check intermediate files**:
   - Look in `ExtractedAssets/_raw_extraction/` for raw extraction output
   - Check `ReferenceAssets/reference_snapshot.json` for reference data

5. **Test individual components**:
   - Run `bulk_extract_paks.py` directly to test QuickBMS functionality
   - Test asset extractor module independently