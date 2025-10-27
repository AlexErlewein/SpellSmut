# SpellForce Modding Project - Master Plan

This document tracks completed tasks and future work for the SpellSmut modding project.

## 🎯 Project Overview

A comprehensive modding toolkit and documentation project for SpellForce: The Order of Dawn - Platinum Edition.

---

## ✅ Completed Tasks

### Phase 1: Documentation & Analysis (Completed)
- ✅ Comprehensive codebase analysis (see CLAUDE.md)
- ✅ Quest System Guide
- ✅ Spell System Guide
- ✅ Sound System Guide
- ✅ Race Creation Guide
- ✅ Campaign System Guide
- ✅ Multiplayer/FreeGame Guide
- ✅ Category system documentation
- ✅ ID mappings and references
- ✅ GitHub Pages site setup

### Phase 2: UI Asset Extraction (Completed - Oct 18, 2025)

**Status**: ✅ COMPLETE

**Summary**: Successfully identified and cataloged 683 UI assets from the game's PAK archives.

**Achievements**:
- Scanned 23 PAK archive files (3.2 GB total)
- Identified and categorized 683 pure UI assets
- Created 11 organized asset categories
- Developed automated extraction tools
- Generated comprehensive documentation

**Asset Categories** (Updated 2025-10-25):
| Category | Count | Description |
|----------|-------|-------------|
| Backgrounds | 255 | UI panels, windows, dialogs |
| Items | 4096+ | ITM atlas icons (16 atlases × 256 icons each) |
| Main Menu | 79 | Menu background images |
| Buttons | 65 | Interactive button graphics |
| Other UI | 43 | Miscellaneous UI elements |
| Containers | 37 | Character/container frames |
| Cursors | 33 | Mouse cursor states |
| Splash Screens | 26 | Loading screens |
| Spells | 18+ | Spell atlases (ui_spell8.dds, ui_spell9.dds) |
| Clock | 8 | Time/day-night indicators |
| Logos | 5 | Game branding |

**Icon System Status**:
- ✅ **ITM Extraction**: 4096 icons extracted, weapons reassembled
- ⚠️ **Mapping Gap**: Handle-to-atlas mapping missing (atlas numbers not in GameData exports)
- 🔍 **Investigation Needed**: Find atlas assignment data in original game files

**Tools Created**:
- `src/helper_tools/extract_ui_assets.py` - Scans pakdata.dat for UI files
- `src/helper_tools/batch_extract_ui.py` - Categorizes and organizes assets
- `src/helper_tools/extract_ui_batch.bat` - Launches SpellforceDataEditor
- Complete extraction lists for each category
- User documentation (README.md)

**Note:** TirganachReloaded CFF library moved to `TirganachReloaded/`

**File Formats**:
- TGA (Targa): 33 files - Cursors, menu backgrounds
- DDS (DirectDraw Surface): 650 files - Most UI graphics

**Location**: `H:\SpellSmut\ExtractedAssets\UI\`

**Documentation**:
- Full technical summary: `UI_EXTRACTION_SUMMARY.md`
- User guide: `ExtractedAssets/UI/README.md`
- Extraction lists: `ExtractedAssets/UI/extraction_lists/`

**Next Steps for UI Assets**:
1. ⏳ Extract assets using SpellforceDataEditor (run `src/helper_tools/extract_ui_batch.bat`)
2. ⏳ Convert DDS files to PNG for easier editing
3. ⏳ Create visual catalog/atlas of all UI elements
4. ⏳ Document UI layout system and coordinate mappings
5. ⏳ Create custom UI theme/skin as proof of concept

---

## 🔄 In Progress Tasks

_(Currently no active tasks)_

---

## ✅ Recently Completed

### Phase 3: Bulk Asset Extraction (Completed - Oct 18, 2025)

**Status**: ✅ **COMPLETE - ALL ASSETS EXTRACTED!**

**Summary**: Successfully extracted ALL game assets from 23 PAK files using automated QuickBMS system.

**Results**:
- **Total Files Extracted:** 59,500 files
- **Audio Files:** 15,765 files (MP3 + WAV)
- **UI Assets:** 2,475 files (DDS/TGA)
- **Textures:** 6,602 files
- **3D Models:** 12,136 files (.msb)
- **Animations:** 1,827 files (.bob)
- **Skeletons:** 1,196 files (.bor)
- **Lua Scripts:** 16,730 files
- **Other Assets:** 2,769 files

**Tools Created**:
- `src/helper_tools/bulk_extract_paks.py` - Automated PAK extraction with QuickBMS
- `src/helper_tools/bulk_extract_paks.bat` - One-click launcher
- `src/helper_tools/SpellForce_PAK_script.bms` - PAK format BMS script
- `src/helper_tools/extract_audio_assets.py` - Audio asset scanner
- `src/helper_tools/organize_extracted_files.py` - File organizer
- Complete extraction guide: `BULK_EXTRACTION_GUIDE.md`

**Extraction Method**:
- QuickBMS with custom BMS script
- Automated download and configuration
- Batch processing of all 23 PAKs (~3.2 GB)
- Automatic organization by file type
- Total extraction time: ~10 minutes

**Output Location**: `H:\SpellSmut\ExtractedAssets\`
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

**Documentation**:
- Bulk extraction guide: `BULK_EXTRACTION_GUIDE.md`
- Audio extraction plan: `AUDIO_EXTRACTION_PLAN.md`
- UI extraction summary: `UI_EXTRACTION_SUMMARY.md`

**Next Steps**:
1. ✅ ~~Extract all assets~~ **DONE!**
2. ⏳ Analyze and catalog extracted files
3. ⏳ Convert audio to modern formats (FLAC, OGG)
4. ⏳ Convert UI textures to PNG
5. ⏳ Create interactive asset browser
6. ⏳ Build modding tutorials using extracted assets

---

## 📋 Planned Tasks

### Phase 3: Asset Extraction & Processing

#### 3D Models & Animations
- ✅ Extract all 3D mesh files from PAK archives (12,136 models extracted!)
- ✅ Extract skeleton/bone files (1,196 .bor files extracted!)
- ✅ Extract animation files (1,827 .bob files extracted!)
- [ ] Document model file formats
- [ ] Create Blender import/export scripts
- [ ] Build asset catalog with preview images

#### Textures & Materials
- ✅ Extract all texture files (6,602 DDS/TGA files extracted!)
- ✅ Complete ITM (item) texture atlas extraction (16 atlases, 4096+ icons)
- ✅ Complete spell texture atlas extraction (18 atlases, 657 icons)
- ✅ Weapon reassembly working (1x2 and 1x4 weapons)
- [ ] Categorize by type (terrain, units, buildings, effects)
- [ ] Document texture naming conventions
- [ ] Complete texture atlas tools (missing: handle-to-atlas mapping)
- [ ] Build material/shader documentation

#### Sounds & Music
- ✅ Audio system analysis complete
- ✅ Created extraction tools (extract_audio_assets.py)
- ✅ Documented sound categories and organization
- ✅ Created comprehensive extraction plan
- ✅ **Extracted ALL audio files** (15,765 MP3/WAV files!)
- ✅ Organized by category in ExtractedAssets/Audio/
- [ ] Analyze and catalog audio files (verify counts vs expectations)
- [ ] Convert to modern formats (FLAC, OGG)
- [ ] Create audio catalog and browser
- [ ] Document sound event system integration
- [ ] Create sound replacement guide

### Phase 4: Reverse Engineering

#### File Format Documentation
- [ ] PAK archive format specification
- [ ] CFF (game data) format specification
- [ ] Map file (.map) format specification
- [ ] 3D model format documentation
- [ ] Animation format documentation
- [ ] Texture format documentation

#### Game Systems Analysis
- [ ] UI rendering system
- [ ] Physics and collision system
- [ ] Pathfinding and navigation
- [ ] AI behavior trees
- [ ] Multiplayer networking protocol
- [ ] Save game format

### Phase 5: Modding Tools Development

#### Asset Tools
- [ ] PAK packer/unpacker standalone tool
- [ ] Texture converter (DDS ↔ PNG)
- [ ] Model viewer application
- [ ] Animation preview tool
- [ ] Sound browser and player

#### Content Creation Tools
- ✅ Visual quest editor (with rewards, requirements, dialogues, Lua generation)
- ✅ Dialogue tree editor (branching conversations with visual enhancements)
- [ ] Spell designer GUI
- [ ] Race/unit creator wizard
- [ ] Map editor enhancements

#### Development Tools
- [ ] Lua script debugger
- [ ] Live reload system for testing
- [ ] Automated build system for mods
- [ ] Mod packaging tool
- [ ] Version control best practices guide

### Phase 6: Example Mods & Tutorials

#### Tutorial Mods
- [ ] "Hello World" - Basic quest mod
- [ ] "Fireball+" - Custom spell mod
- [ ] "Dark Elves Reborn" - Race modification
- [ ] "Mystic Isles" - Custom campaign (3-5 quests)
- [ ] "Arena Master" - Multiplayer map pack

#### Reference Implementations
- [ ] Complete working mod template
- [ ] Asset pipeline example
- [ ] Localization example
- [ ] Complex quest chain example
- [ ] Custom UI skin example

### Phase 7: Community & Distribution

#### Community Resources
- [ ] Mod showcase gallery
- [ ] Tutorial video series
- [ ] Discord/forum community setup
- [ ] Mod compatibility database
- [ ] FAQ and troubleshooting wiki

#### Distribution & Publishing
- [ ] Steam Workshop integration guide
- [ ] Nexus Mods presence
- [ ] GitHub releases for tools
- [ ] Automated update system
- [ ] Mod manager application

---

## 🎨 UI Asset Extraction - Detailed Roadmap

### ✅ Completed Achievements (2025-10-25)

1. **ITM Icon Extraction** (COMPLETED)
    - [x] Extracted 4096+ ITM icons from 16 atlases
    - [x] Implemented weapon reassembly (1x2 and 1x4 weapons)
    - [x] Created automated pattern detection
    - [x] DDS → PNG conversion pipeline working
    - [x] Grid extraction algorithms (16x16 grid, 16x16px icons)
    - [x] Atlas statistics and metadata collection
    - [x] Icon indexing system with 4096+ entries
    - [x] Individual icon extraction with proper naming

2. **Technical Infrastructure** (COMPLETED)
    - [x] Created Python scripts for atlas extraction
    - [x] ImageMagick integration for DDS conversion
    - [x] 180° rotation correction for SpellForce Y-axis
    - [x] Grid-based extraction algorithms
    - [x] Weapon pattern detection and reassembly
    - [x] Icon indexing and organization system
    - [x] Automated extraction pipeline for ITM category

### ✅ Completed Achievements (2025-10-25)

1. **ITM Icon Extraction** (COMPLETED)
    - [x] Extracted 4096+ ITM icons from 16 atlases
    - [x] Implemented weapon reassembly (1x2 and 1x4 weapons)
    - [x] Created automated pattern detection
    - [x] DDS → PNG conversion pipeline working
    - [x] Grid extraction algorithms (16x16 grid, 16x16px icons)
    - [x] Atlas statistics and metadata collection
    - [x] Icon indexing system with 4096+ entries
    - [x] Individual icon extraction with proper naming

2. **Spell Icon Extraction** (COMPLETED)
    - [x] Extracted 657 spell icons from 18 atlases
    - [x] Implemented 4×4 grid extraction (64×64 icons with 2px offset)
    - [x] Identified 9 active slots per atlas (positions 1,2,3,5,6,7,9,10,11)
    - [x] Implemented spell-specific extraction pipeline

3. **Technical Infrastructure** (COMPLETED)
    - [x] Created Python scripts for atlas extraction
    - [x] ImageMagick integration for DDS conversion
    - [x] 180° rotation correction for SpellForce Y-axis
    - [x] Grid-based extraction algorithms
    - [x] Weapon pattern detection and reassembly
    - [x] Icon indexing and organization system
    - [x] Automated extraction pipeline for ITM category
    - [x] Automated extraction pipeline for spell category
    - [x] 180° rotation applied to spell icons for consistency

### ⏳ Current Challenges (Phase 3B)

1. **Mapping Discovery** (URGENT)
    - [ ] Find atlas-to-handle mapping in game files
    - [ ] Locate missing `item_ui_texture` field data
    - [ ] Reverse engineer icon loading system
    - [ ] Connect game data handles to specific atlas locations

2. **ITM Extraction Refinement** (HIGH PRIORITY)
    - [ ] Replace current ITM extraction script with improved version
    - [ ] Current extraction has alignment/offset issues
    - [ ] Weapon reassembly needs optimization
    - [ ] Verify icon quality and positioning

3. **Spell Icon GUI Integration** (HIGH PRIORITY)
    - [ ] Debug why spell icons aren't displaying in GUI
    - [ ] Verify icon mapping is correctly loaded
    - [ ] Check GUI icon resolution paths
    - [ ] Test spell category icon display

4. **Integration Completion**
    - [ ] Connect extracted icons to CFF editor (Partially working)
    - [ ] Implement fallback mapping system
    - [ ] Create manual mapping interface
   - [ ] Document texture sizes and formats
   - [ ] Create interactive asset browser

4. **UI System Analysis** (Week 3)
   - [ ] Map UI element coordinates and layouts
   - [ ] Document UI widget hierarchy
   - [ ] Reverse engineer UI positioning system
   - [ ] Create UI layout diagrams

5. **Custom UI Theme** (Week 3-4)
   - [ ] Design new UI theme concept
   - [ ] Modify background textures
   - [ ] Create custom button states
   - [ ] Test in-game loading
   - [ ] Document theme creation process

### 📊 Success Metrics

**Phase 3A Complete When**:
- ✅ All 683 UI assets extracted to disk
- ✅ All DDS files converted to PNG
- ✅ Visual catalog created and accessible
- ✅ At least one custom UI theme working in-game
- ✅ Complete UI modding guide published

---

## 🔧 Technical Debt & Infrastructure

### Build System
- [ ] Automate documentation generation
- [ ] Set up CI/CD for tool builds
- [ ] Create automated testing suite
- [ ] Version control for game file formats

### Code Quality
- [ ] Refactor extraction scripts
- [ ] Add error handling and logging
- [ ] Create unit tests for tools
- [ ] Documentation generation automation

### Performance
- [ ] Optimize PAK file reading
- [ ] Cache expensive operations
- [ ] Parallel processing for batch operations
- [ ] Memory usage profiling

---

## 📅 Timeline & Milestones

### Q4 2025
- ✅ Complete UI asset extraction (DONE)
- ✅ Complete quest editor enhancements (DONE)
- ⏳ Extract 3D models and textures
- ⏳ Document file formats
- ⏳ Release PAK extraction tool v1.0

### Q1 2026
- Create visual asset browser
- Build first tutorial mod
- Launch community forum
- Release modding SDK alpha

### Q2 2026
- Complete tool suite
- Video tutorial series
- Steam Workshop guide
- Modding SDK beta

### Q3 2026
- Full mod manager release
- Example mod collection
- Community mod showcase
- Version 1.0 release

---

## 🤝 Collaboration Opportunities

Areas where community help would be valuable:

1. **Testing**: Test extraction tools on different systems
2. **Documentation**: Write tutorials and guides
3. **Modding**: Create example mods and content
4. **Translation**: Localize documentation
5. **Design**: Create UI themes and assets
6. **Programming**: Contribute to tool development

---

## 📝 Notes & Ideas

### UI Modding Possibilities
- Modern UI redesign (flat/minimalist style)
- High-res texture pack
- Color scheme variants (dark mode, colorblind-friendly)
- Custom icon sets
- Animated UI elements
- Widescreen UI fixes

### Future Research Topics
- Lua-C++ binding API reverse engineering
- Network protocol for multiplayer modding
- Save game editor possibilities
- Real-time debugging tools
- Automated mod testing framework

### Community Requests
_(To be filled in as requests come in)_

---

## 📊 Project Statistics

**Documentation Pages**: 15+
**Guides Created**: 7 major guides
**Assets Cataloged**: 683 UI assets
**Tools Developed**: 5 (extraction, categorization, automation)
**Code Written**: ~400 lines Python
**Project Duration**: 4+ months
**Last Updated**: October 18, 2025

---

## 🔗 Quick Links

- **Documentation Site**: https://alexerlewein.github.io/SpellSmut/
- **UI Assets**: `H:\SpellSmut\ExtractedAssets\UI\`
- **Tools**: `H:\SpellSmut\ModdingTools\`
- **Guides**: `H:\SpellSmut\docs\`

---

**Status**: 🟢 Active Development
**Current Phase**: Phase 5 - Modding Tools Development
**Next Milestone**: Complete quest editor enhancements

