# Asset Extraction Component

## Overview
Complete asset extraction pipeline for SpellForce game files, converting PAK archives into usable assets for modding and development.

## Current Status: ✅ COMPLETE

### ✅ Phase 1: Documentation & Analysis ✅ COMPLETE
- Comprehensive codebase analysis
- Asset format documentation
- Extraction method research

### ✅ Phase 2: UI Asset Extraction ✅ COMPLETE
- 683 UI assets identified and categorized
- Automated extraction tools developed
- Comprehensive documentation created

### ✅ Phase 3: Bulk Asset Extraction ✅ COMPLETE
- **59,500+ files extracted** from 23 PAK archives
- **15,765 audio files** (MP3 + WAV)
- **2,475 UI assets** (DDS/TGA)
- **6,602 textures**
- **12,136 3D models** (.msb)
- **1,827 animations** (.bob)
- **1,196 skeletons** (.bor)
- **16,730 Lua scripts**

## Extraction Pipeline

### Tools and Methods
- **QuickBMS**: Industry-standard game asset extraction tool
- **Custom BMS Script**: SpellForce PAK format specification
- **Automated Processing**: Batch extraction of all 23 PAK files
- **File Organization**: Automatic categorization by type and extension

### Output Structure
```
ExtractedAssets/
├── Audio/extracted/        # 15,765 audio files
├── UI/extracted/           # 2,475 UI files
├── Textures/               # 6,602 texture files
├── Models/                 # 12,136 model files
├── Animations/             # 1,827 animation files
├── Skeletons/              # 1,196 skeleton files
├── Scripts/                # 16,730 Lua scripts
└── Other/                  # 2,769 misc files
```

## Technical Infrastructure

### Build System Migration
- **UV Package Manager**: Adopted as project standard
- **Dependency Management**: Consistent Python environment across platforms
- **Installation Commands**: `uv pip install <package>` (replacing pip)
- **Script Execution**: `uv run <script.py>` (replacing python)

### Performance Optimizations
- **Parallel Processing**: Multi-threaded extraction where possible
- **Caching**: Intermediate results cached to avoid re-processing
- **Memory Management**: Efficient handling of large file sets
- **Progress Tracking**: Real-time progress indicators for long operations

## Asset Categories and Statistics

### Audio Assets (15,765 files)
- **MP3 Format**: Compressed audio for music and sound effects
- **WAV Format**: Uncompressed audio for high-quality effects
- **Organization**: Categorized by game context (battle, ambient, UI, etc.)
- **Future Plans**: Convert to modern formats (FLAC, OGG)

### UI Assets (2,475 files)
- **DDS Format**: DirectDraw Surface textures (primary)
- **TGA Format**: Targa images for specific UI elements
- **Categories**: Backgrounds, buttons, cursors, icons, menus
- **Post-Processing**: PNG conversion and rotation correction

### 3D Assets (12,136 models + 1,827 animations + 1,196 skeletons)
- **MSB Format**: 3D mesh data for models
- **BOB Format**: Bone-based animation data
- **BOR Format**: Skeletal rig definitions
- **Usage**: Characters, buildings, terrain, effects

### Script Assets (16,730 files)
- **Lua 4.0**: Game logic and behavior scripts
- **Organization**: Preserved directory structure from PAK files
- **Analysis**: Foundation for understanding game mechanics

## Tools Developed

### Core Extraction Tools
- `bulk_extract_paks.py` - Automated PAK extraction with QuickBMS
- `bulk_extract_paks.bat` - Windows automation script
- `SpellForce_PAK_script.bms` - PAK format specification

### Specialized Extractors
- `extract_ui_assets.py` - UI asset scanner and categorizer
- `batch_extract_ui.py` - UI asset batch processing
- `extract_audio_assets.py` - Audio asset scanner

### Utility Scripts
- `organize_extracted_files.py` - File organization and cleanup
- `convert_ui_textures.py` - DDS to PNG conversion
- `rotate_ui_pngs.py` - Y-axis rotation correction

## Documentation Created
- `BULK_EXTRACTION_GUIDE.md` - Complete extraction walkthrough
- `AUDIO_EXTRACTION_PLAN.md` - Audio-specific extraction guide
- `UI_EXTRACTION_SUMMARY.md` - UI asset documentation
- `EXTRACTION_SUCCESS.md` - Success metrics and verification

## Future Plans

### Phase 4: Asset Processing
- **Audio Conversion**: MP3/WAV → FLAC/OGG for modern compatibility
- **UI Optimization**: PNG optimization and atlas generation
- **Model Processing**: Blender import/export script development
- **Animation Tools**: Preview and editing capabilities

### Phase 5: Asset Management
- **Catalog System**: Interactive asset browser
- **Search/Indexing**: Fast asset lookup and filtering
- **Metadata**: Asset information and usage tracking
- **Integration**: Direct links to game data references

## Success Metrics
- ✅ **Complete Coverage**: All 23 PAK files extracted successfully
- ✅ **File Integrity**: No corruption or data loss during extraction
- ✅ **Organization**: Automatic categorization and naming preservation
- ✅ **Performance**: Reasonable extraction times (10-30 minutes total)
- ✅ **Documentation**: Comprehensive guides for all extraction processes

## Dependencies and Requirements
- **QuickBMS**: Game asset extraction tool
- **ImageMagick**: Image format conversion
- **UV**: Python package management
- **Python 3.8+**: Script execution environment
- **Storage**: ~5GB free space for extracted assets

## Files Consolidated From
- `Internal/DATA_EXTRACTION_PLAN.md`
- `Internal/UV_MIGRATION_SUMMARY.md`
- Related extraction status and planning documents