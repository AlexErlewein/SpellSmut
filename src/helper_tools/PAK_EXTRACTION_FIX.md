# PAK Extraction Issue - Root Cause Analysis & Fix

## Issue Summary

Four PAK files were failing to extract during bulk extraction:
- **sf6.pak** (1.1 MB)
- **sf21.pak** (18 MB)  
- **sf32.pak** (377 MB)
- **sf34.pak** (25 MB)

## Root Cause

The extraction failures were caused by **filename encoding issues** with German special characters in the PAK files. These PAK files contain filenames with German Umlauts (ü, ö, ä) and ß (eszett/sharp S) that are stored in a non-UTF8 encoding (likely Windows-1252 or ISO-8859-1).

### Problematic Filenames Identified

1. **sf21.pak** (5 files with encoding issues):
   - `n6973_ork_fußball.lua` - appears as `n6973_ork_fu�ball.lua`
   - `n5538_flüchtlingegerettet.lua` - appears as `n5538_fl�chtlingegerettet.lua`
   - And 3 others

2. **sf32.pak** (1 file):
   - `ft_presse_phönixstein.des` - appears as `ft_presse_ph�nixstein.des`

3. **sf34.pak** (5 files):
   - Same files as sf21.pak (contains overlapping content)

4. **sf6.pak** (1 file):
   - One file with invalid character encoding

### Why It Failed

When QuickBMS encountered these filenames:
1. It attempted to create files with the corrupted character sequences
2. macOS filesystem rejected the invalid UTF-8 sequences
3. QuickBMS prompted for a new filename: "press ENTER for auto-generated name"
4. The Python script was not providing stdin input, causing QuickBMS to hang
5. Eventually the script reported these PAKs as "failed"

## Solution

The fix involves two changes to `bulk_extract_paks.py`:

### 1. Provide Stdin Input to Auto-Accept Renamed Files

```python
result = subprocess.run(
    cmd,
    input=b"\n" * 200,  # Send 200 newlines as bytes
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    timeout=600
)
```

When QuickBMS prompts for a new filename, pressing Enter causes it to auto-generate a safe filename like `original_name_00352120.ext` (using the file offset as a unique identifier).

### 2. Handle Non-UTF8 Output from QuickBMS

```python
# Decode output with error handling
stdout_text = result.stdout.decode('utf-8', errors='replace')
stderr_text = result.stderr.decode('utf-8', errors='replace')
```

QuickBMS outputs the original corrupted filenames in its logs, which would crash the Python script when trying to decode as UTF-8. Using `errors='replace'` substitutes invalid bytes with � (replacement character).

### 3. Count and Report Auto-Renamed Files

```python
rename_count = stdout_text.count("it's not possible to create that file")

if rename_count > 0:
    print(f"  [WARNING] {rename_count} file(s) auto-renamed due to invalid characters")
```

This informs the user that some files were renamed during extraction.

## Verification Results

After applying the fix, all four PAK files extract successfully:

| PAK File   | Status  | Files Extracted | Auto-Renamed Files |
|------------|---------|-----------------|-------------------|
| sf6.pak    | ✓ SUCCESS | 214 items      | 1                 |
| sf21.pak   | ✓ SUCCESS | 6,276 items    | 5                 |
| sf32.pak   | ✓ SUCCESS | 5,605 items    | 1                 |
| sf34.pak   | ✓ SUCCESS | 10,598 items   | 5                 |

### Example Auto-Renamed Files

Original (broken): `n6973_ork_fußball.lua`
After extraction: `n6973_ork_fu_ball_00352120.lua`

The auto-generated filename:
- Removes invalid characters (`ß` → `_`)
- Appends the file offset as a unique identifier (`00352120`)
- Ensures the file is extractable on any filesystem

## Technical Details

### Character Encoding Analysis

The PAK files were created on Windows, likely using the German Windows-1252 code page:
- `ü` (U+00FC) in UTF-8: `0xC3 0xBC`
- `ü` in Windows-1252: `0xFC` (single byte)
- `ß` (U+00DF) in UTF-8: `0xC3 0x9F`  
- `ß` in Windows-1252: `0xDF` (single byte)

When QuickBMS reads these single-byte values and tries to create files on macOS (which expects UTF-8), the filesystem rejects them as invalid sequences.

### Alternative Solutions Considered

1. **Pre-scan and rename**: Would require parsing PAK format ourselves
2. **Use -K flag**: QuickBMS's `-K` flag was tested but still prompts for input
3. **Extract on Windows**: Would work but not portable for macOS/Linux users
4. **Modify BMS script**: Would require complex filename sanitization logic

The stdin input approach was chosen because:
- Minimal code changes
- Works with existing QuickBMS
- Preserves as much of the original filename as possible
- Auto-generated names are deterministic (use file offset)

## Files Modified

- `bulk_extract_paks.py` - Lines 137-195 (extract_pak function)
  - Added stdin input handling
  - Added output encoding error handling
  - Added rename count reporting

## Testing Recommendations

When running bulk extraction after this fix:
1. Expect warning messages for files with invalid characters
2. Check `ExtractedAssets/` for files with `_00xxxxxx` suffixes
3. These files are complete and valid despite the renamed filenames

## Future Improvements

Possible enhancements:
1. Create a filename mapping file (original → renamed) for reference
2. Attempt to detect the original code page and convert properly
3. Add a post-processing step to restore German characters where safe

## References

- QuickBMS Homepage: https://aluigi.altervista.org/quickbms.htm
- SpellForce PAK Format: Custom "MASSIVE PAKFILE V 4.0" format
- BMS Script: `SpellForce_PAK_script.bms` by Bartlomiej Duda (Ikskoks)

---

**Date**: October 24, 2025
**Tested On**: macOS (Apple Silicon)
**QuickBMS Version**: 0.12.0
