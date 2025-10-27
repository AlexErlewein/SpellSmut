# Asset Extraction Component

## Overview

A complete asset extraction pipeline for SpellForce game files, converting 23 PAK archives into over 59,500 usable assets for modding and development.

## Current Status: ✅ COMPLETE

### Key Achievements
- **Comprehensive Extraction**: Successfully extracted 59,500+ files from all 23 PAK archives.
- **Automated Pipeline**: Developed a fully automated extraction process using QuickBMS and custom scripts.
- **Asset Categorization**: Automatically organized extracted files into logical categories (Audio, UI, Models, etc.).
- **Development Environment**: Standardized the project's development environment using the UV package manager.

## Roadmap

### Phase 4: Asset Processing (Future)
- **Objective**: Convert and optimize assets for modern use.
- **Tasks**:
  - 🎵 **Audio Conversion**: Convert MP3/WAV files to modern formats like FLAC or OGG.
  - 🖼️ **UI Optimization**: Optimize PNGs and generate texture atlases.
  - 🎨 **3D Model Pipeline**: Develop a Blender import/export script for MSB, BOB, and BOR files.

### Phase 5: Asset Management (Future)
- **Objective**: Create a user-friendly system for browsing and managing assets.
- **Tasks**:
  - catalog **Asset Catalog**: Build an interactive asset browser with search and filtering capabilities.
  - 🔗 **Data Integration**: Link assets directly to their corresponding game data references in the GUI editor.

## Extraction Pipeline

The extraction process is handled by a combination of industry-standard tools and custom scripts:
- **QuickBMS**: Extracts files from the PAK archives using a custom BMS script.
- **Python Scripts**: Automate the extraction, conversion, and organization of assets.
- **Output**: Extracted assets are organized into a clear directory structure within the `ExtractedAssets/` folder.

## Extracted Asset Summary

| Category | File Count | Formats |
|---|---|---|
| **Scripts** | 16,730 | Lua |
| **Audio** | 15,765 | MP3, WAV |
| **3D Models** | 12,136 | MSB |
| **Textures** | 6,602 | DDS, TGA |
| **UI Assets** | 2,475 | DDS, TGA |
| **Animations** | 1,827 | BOB |
| **Skeletons** | 1,196 | BOR |
| **Other** | 2,769 | Various |
| **Total** | **59,500+** | |

## Tools Developed

- `bulk_extract_paks.py`: The core script for automated PAK extraction.
- `SpellForce_PAK_script.bms`: The BMS script that defines the PAK file format for QuickBMS.
- **Specialized Extractors**: A suite of scripts for handling specific asset types (UI, Audio, etc.).
- **Utility Scripts**: Various helper scripts for file conversion, rotation, and organization.

## Success Metrics

- **Completeness**: 100% of files from all 23 PAK archives were extracted.
- **Integrity**: Extracted files are free from corruption and match the originals.
- **Efficiency**: The entire extraction process completes in a reasonable timeframe (10-30 minutes).
- **Organization**: All extracted assets are automatically sorted into a logical and usable directory structure.

## Dependencies
- **QuickBMS**: For PAK file extraction.
- **ImageMagick**: For DDS to PNG image conversion.
- **UV**: For Python package management.

## Files Consolidated From
- `Internal/DATA_EXTRACTION_PLAN.md`
- `Internal/UV_MIGRATION_SUMMARY.md`
- Related extraction status and planning documents