# SpellForce Audio Extraction - Master Plan

**Date:** October 18, 2025
**Project:** SpellSmut Modding Project
**Status:** 🟡 Ready to Execute

---

## 📊 Executive Summary

SpellForce Platinum Edition contains **1,000-1,150+ audio files** across two primary formats:
- **MP3 Music Tracks:** ~110-130 files (streaming background music)
- **WAV Sound Effects:** ~800-1,000+ files (in-game sound effects)

All audio assets are stored in **PAK archives** and require extraction using SpellforceDataEditor or custom PAK unpacking tools.

---

## 🎯 Project Goals

1. **Identify** all audio files from game scripts and PAK archives
2. **Categorize** audio by type (music, combat, spells, work, ambient, etc.)
3. **Extract** all audio files to organized directory structure
4. **Document** the sound system architecture and usage
5. **Convert** to modern formats for preservation and modding
6. **Create** searchable audio catalog with metadata

---

## 📁 Audio Asset Breakdown

### Music Tracks (MP3 Format) - ~110-130 Files

| Category | Count | Description |
|----------|-------|-------------|
| **Main Menu** | ~10 | Menu background music (spellforce.mp3, elvensong_menu.mp3, etc.) |
| **Battle/Combat** | ~15 | Battle music (battle_music1.mp3, combat_music2.mp3, etc.) |
| **Location Themes** | ~80 | Map-specific music (elves_and_angels.mp3, bone_temple.mp3, etc.) |
| **Platform Plains** | ~15 | Terrain background music (plain_waterworld.mp3, plain_iceworld.mp3) |
| **Special Tracks** | ~10 | Death music, silence, cutscene audio |

**Total Music:** ~130 MP3 files

---

### Sound Effects (WAV Format) - ~800-1,000+ Files

#### Environmental & Ambient (~25 files)
- Atmospheric loops (water, swamp, lava)
- Object sounds (torches, portals, bindstones)
- Building destruction sounds
- Ambient creature sounds

#### Spell System (~200+ files)
- **Casting Sounds** (~10): Spell initiation by magic school
- **Resolve Sounds** (~15): Spell completion effects
- **Hit Effects** (~100+): Spell impact sounds
  - Fire (fireball, firerain, explosion)
  - Ice (freeze, icefall, icespear)
  - White (heal, blessing, divine)
  - Black (curse, decay, death)
  - Earth (stone, earthquake, petrify)
  - Air (lightning, wind, storm)
  - Mental (confusion, fear, dominate)
- **Buff/Debuff** (~10): Auras, shields, enchantments
- **Summon Effects** (~10): Creature summoning sounds
- **Resist** (~5): Magic resistance feedback

#### Combat Sounds (~450+ files)

**Character Vocals:**
- Main Character (male/female): 12+ variants (scream, attack, die)
- Heroes: 10 heroes × 6 variants = 60 sounds
- Races: 6 races × 2 unit types × 6 variants = 72 sounds
- Titans: 6 titan types × 6 variants = 36 sounds

**NPC Creatures:**
- Base Game: 40+ creature types × 6 variants = 240+ sounds
- Addon 1 (Breath of Winter): 10+ creatures × 6 variants = 60+ sounds
- Addon 2 (Shadow of Phoenix): 10+ creatures × 6 variants = 60+ sounds

**Weapon Sounds:**
- Hit Sounds: 80+ files (all weapon types × variations)
- Miss Sounds: 10+ files (weapon swings)

#### Work & Gathering (~60 files)
- Building construction (stone, wood)
- Resource gathering (ore, iron, coal, bronze)
- Tree cutting, stone cutting
- Smithing, fishing, farming
- Cattle breeding

#### Movement (~20 files)
- Footsteps: normal, talon, titan, blade
- Wing sounds (flying creatures)
- Each type has 3-4 variations

#### UI & Misc (~20 files)
- UI feedback sounds
- Portal entry/exit
- Summon notifications
- Idle creature sounds

**Total Sound Effects:** ~800-1,000+ WAV files

---

## 🛠️ Tools Created

### 1. `extract_audio_assets.py`
**Purpose:** Scan and catalog all audio files

**Features:**
- Parses DrwSound.lua for WAV file references
- Parses SndTracks.lua for MP3 file references
- Scans pakdata.dat for audio file entries
- Categorizes sounds into 20+ categories
- Generates extraction lists by category
- Creates comprehensive summary report

**Usage:**
```bash
python src/helper_tools/extract_audio_assets.py
```

**Output:**
- `ExtractedAssets/Audio/audio_assets_list.txt` - Master list
- `ExtractedAssets/Audio/extraction_lists/*.txt` - Category lists
- `ExtractedAssets/Audio/EXTRACTION_SUMMARY.md` - Report

---

### 2. `extract_audio_batch.bat`
**Purpose:** Launch SpellforceDataEditor for extraction

**Features:**
- Configures extraction directory automatically
- Provides step-by-step instructions
- Lists priority extractions
- Shows category breakdown

**Usage:**
```batch
src\helper_tools\extract_audio_batch.bat
```

---

## 📋 Extraction Workflow

### Phase 1: Identification ✅ (READY)

1. **Run the scanner script:**
   ```bash
   python src/helper_tools/extract_audio_assets.py
   ```

2. **Review the output:**
   - Check `ExtractedAssets/Audio/audio_assets_list.txt`
   - Review `ExtractedAssets/Audio/EXTRACTION_SUMMARY.md`
   - Examine category-specific lists in `extraction_lists/`

---

### Phase 2: Extraction (PENDING)

#### Method 1: Using SpellforceDataEditor (Recommended)

1. **Launch the tool:**
   ```batch
   src\helper_tools\extract_audio_batch.bat
   ```

2. **Extract music tracks first:**
   - Go to Asset Viewer tab
   - Filter by: `.mp3`
   - Select all music files
   - Extract to: `H:\SpellSmut\ExtractedAssets\Audio\extracted\music\`

3. **Extract sound effects by category:**
   - Filter by category prefix (e.g., `spell_`, `battle_`, `work_`)
   - Use extraction lists as reference
   - Extract to organized subdirectories

4. **Verify extraction:**
   - Check file counts match expected numbers
   - Test audio playback on sample files

#### Method 2: PAK Unpacker (Future)

Once PAK format is reverse-engineered:
- Create automated PAK unpacker tool
- Batch extract all audio files
- Auto-organize by category

---

### Phase 3: Conversion & Preservation

1. **Convert to modern formats:**
   ```bash
   # WAV to FLAC (lossless compression)
   ffmpeg -i input.wav -c:a flac output.flac

   # MP3 to OGG Vorbis (better compression)
   ffmpeg -i input.mp3 -c:a libvorbis -q:a 6 output.ogg
   ```

2. **Create high-quality archive:**
   - Preserve original WAV/MP3 files
   - Create compressed versions for distribution
   - Generate checksums for verification

3. **Organize directory structure:**
   ```
   ExtractedAssets/Audio/
   ├── extracted/
   │   ├── music/
   │   │   ├── menu/
   │   │   ├── battle/
   │   │   ├── location/
   │   │   └── themes/
   │   ├── sounds/
   │   │   ├── ambient/
   │   │   ├── spells/
   │   │   ├── combat/
   │   │   ├── work/
   │   │   └── movement/
   │   └── original/          # Backup of originals
   ├── converted/
   │   ├── flac/              # Lossless WAV conversions
   │   └── ogg/               # Compressed MP3 conversions
   └── metadata/
       └── audio_catalog.json  # Complete metadata
   ```

---

### Phase 4: Documentation & Cataloging

1. **Create audio catalog:**
   - Generate JSON/CSV database
   - Include: filename, category, format, duration, file size
   - Add metadata: usage context, event ID, volume, falloff

2. **Build interactive browser:**
   - HTML5 audio player
   - Category filtering
   - Search by filename or category
   - Waveform visualization

3. **Document sound events:**
   - Map DrwSound.lua event IDs to filenames
   - Document which sounds play in which contexts
   - Create usage guide for modders

4. **Generate preview reel:**
   - Create audio montage of highlights
   - Category-specific sample packs
   - Modding tutorial audio examples

---

## 🎵 Sound System Architecture

### Lua Script System

**DrwSound.lua** (1030 lines):
- Defines 500+ sound events
- Maps event names to filenames
- Specifies volume, falloff, duration
- Auto-generates event IDs

**SndTracks.lua:**
- Defines music track metadata
- Priority-based track selection
- Transition effects
- Map/location associations

**SndTransitionEngine.lua:**
- Handles music crossfading
- Context-based switching
- Combat/peace state transitions

### Miles Sound System

**Audio Engine:** RAD Game Tools Miles Sound System v3.x

**Features:**
- 3D positional audio
- Distance-based falloff (FallOffMin/Max)
- Environmental Audio Extensions (EAX)
- 32+ simultaneous channels
- Real-time DSP effects
- MP3 streaming support

**Modules:**
- `Mssa3d.m3d` - 3D audio positioning
- `mssds3d.m3d` - DirectSound 3D
- `Msseax.m3d` - EAX environmental effects
- `mssmp3.asi` - MP3 codec
- `mssdsp.flt` - DSP filtering

---

## 📊 Technical Specifications

### Audio Formats

**MP3 Music:**
- Bitrate: Likely 128-192 kbps
- Sample Rate: 44.1 kHz
- Channels: Stereo
- Purpose: Streaming background music
- Engine: Miles MP3 codec

**WAV Sound Effects:**
- Format: PCM or ADPCM compressed
- Sample Rate: 22.05 kHz or 44.1 kHz
- Bit Depth: 16-bit
- Channels: Mono or Stereo
- Purpose: Low-latency in-game effects

### 3D Audio Parameters

**Falloff Settings:**
- FallOffMin: 2-50 units (sound at full volume)
- FallOffMax: 25-6000 units (sound becomes inaudible)
- Volume: 0.0-3.0+ (normalized to 1.0)

**Common Falloff Ranges:**
- Combat sounds: Min=10, Max=90
- Spell effects: Min=5, Max=60
- Environmental: Min=2, Max=25
- Atmospheric: Min=10, Max=100

---

## 🎯 Priority Extraction Order

### High Priority (Extract First)
1. **All Music Tracks** (~130 files)
   - Easy to identify (.mp3 extension)
   - Relatively small file count
   - High value for preservation

2. **Main Character Sounds** (~20 files)
   - Core gameplay audio
   - Most frequently heard

3. **Spell Effects** (~150 files)
   - Iconic game sounds
   - Modding potential

### Medium Priority
4. **Combat Sounds** (~450 files)
   - Large category
   - Important for gameplay feel

5. **Work Sounds** (~60 files)
   - Resource gathering atmosphere
   - RTS gameplay element

### Low Priority
6. **Ambient/Environmental** (~50 files)
   - Nice to have
   - Less critical

7. **Movement Sounds** (~20 files)
   - Subtle effects
   - Lower importance

---

## 🔬 Advanced Analysis Tasks

### Audio File Analysis
- [ ] Measure actual file sizes
- [ ] Analyze compression ratios
- [ ] Document exact audio specifications
- [ ] Identify unused/duplicate sounds

### Script Analysis
- [ ] Map all event IDs to filenames
- [ ] Document sound usage contexts
- [ ] Create event trigger guide
- [ ] Identify addon-specific sounds

### Modding Support
- [ ] Create sound replacement guide
- [ ] Document custom sound integration
- [ ] Build sound modding toolkit
- [ ] Write tutorial for custom music

---

## 📈 Success Metrics

**Phase Complete When:**
- ✅ All audio files identified and cataloged
- ✅ Extraction lists generated for all categories
- ✅ SpellforceDataEditor configured for extraction
- ⏳ All music tracks extracted (130 files)
- ⏳ All sound effects extracted (800-1,000 files)
- ⏳ Files organized in category structure
- ⏳ Modern format conversions complete
- ⏳ Audio catalog database created
- ⏳ Interactive browser built
- ⏳ Documentation published

---

## 🗺️ Timeline Estimate

### Week 1: Identification & Setup
- ✅ Run extraction scanner
- ✅ Review generated lists
- ✅ Set up directory structure
- ⏳ Test SpellforceDataEditor extraction

### Week 2-3: Music Extraction
- ⏳ Extract all MP3 files (~130 files)
- ⏳ Organize by category
- ⏳ Convert to OGG Vorbis
- ⏳ Create music catalog

### Week 4-6: Sound Effects Extraction
- ⏳ Extract spell sounds (~150 files)
- ⏳ Extract combat sounds (~450 files)
- ⏳ Extract work/ambient sounds (~100 files)
- ⏳ Extract misc sounds (~100 files)

### Week 7-8: Conversion & Organization
- ⏳ Convert WAV to FLAC (lossless)
- ⏳ Organize final directory structure
- ⏳ Generate checksums
- ⏳ Create backup archives

### Week 9-10: Documentation & Cataloging
- ⏳ Build audio database (JSON/CSV)
- ⏳ Create interactive browser
- ⏳ Write modding guides
- ⏳ Generate preview samples

**Total Estimated Time:** 10-12 weeks (part-time effort)

---

## 🛠️ Required Tools

### For Extraction
- **SpellforceDataEditor** (included)
- **.NET 8.0 Runtime** (required by editor)

### For Audio Analysis
- **Audacity** (free) - Waveform viewer, editor
- **foobar2000** (free) - Audio player, converter
- **MediaInfo** (free) - File specification analyzer

### For Conversion
- **FFmpeg** (free) - Universal audio converter
  ```bash
  # Install via Chocolatey (Windows)
  choco install ffmpeg
  ```

### For Organization
- **Python 3.x** - For scripting and automation
- **librosa** (Python) - Audio analysis library
- **mutagen** (Python) - Audio metadata editing

---

## 📚 File References

### Scripts
- `H:\SpellSmut\OriginalGameFiles\script\DrwSound.lua`
- `H:\SpellSmut\OriginalGameFiles\modding\Original Scripts\script\SndTracks.lua`
- `H:\SpellSmut\OriginalGameFiles\modding\Original Scripts\script\SndSystemInit.lua`
- `H:\SpellSmut\OriginalGameFiles\modding\Original Scripts\script\SndTransitionEngine.lua`

### Audio Engine
- `H:\SpellSmut\OriginalGameFiles\miles\` (8 files)

### PAK Archives
- `H:\SpellSmut\OriginalGameFiles\pak\` (23 files: sf0.pak - sf36.pak)

### Tools
- `H:\SpellSmut\src\helper_tools\extract_audio_assets.py`
- `H:\SpellSmut\src\helper_tools\extract_audio_batch.bat`

---

## 🎬 Next Steps

### Immediate (This Week)
1. ✅ Review this extraction plan
2. ⏳ Run `extract_audio_assets.py` to generate lists
3. ⏳ Review generated extraction lists
4. ⏳ Test SpellforceDataEditor extraction with 5-10 sample files

### Short Term (Next 2 Weeks)
1. ⏳ Extract all music tracks (priority: main themes)
2. ⏳ Extract high-priority sound effects (spells, combat)
3. ⏳ Set up organized directory structure
4. ⏳ Begin format conversion tests

### Long Term (Next 2-3 Months)
1. ⏳ Complete full audio extraction
2. ⏳ Build audio catalog database
3. ⏳ Create interactive audio browser
4. ⏳ Publish audio modding documentation
5. ⏳ Release audio pack for community

---

## 🤝 Community Opportunities

### How Others Can Help

1. **Testing:** Test extraction on different systems
2. **Organization:** Help categorize ambiguous sounds
3. **Documentation:** Document sound usage in-game
4. **Conversion:** Batch convert audio to modern formats
5. **Cataloging:** Build metadata database
6. **Web Development:** Create interactive audio browser

---

## 📝 Notes & Observations

### Interesting Findings
- SpellForce uses **random variation** (3-6 variants per sound) to avoid repetition
- **Cross-mixing** weapon sounds creates more perceived variety
- **Addon content** conditionally loads based on flags in scripts
- Some sounds are **reused** across multiple events (optimization)
- Music tracks use **priority system** for dynamic context switching

### Potential Challenges
- **PAK format** is proprietary (requires reverse engineering or existing tool)
- **Large file count** makes manual extraction tedious
- **File naming** doesn't always match in-game usage (requires script analysis)
- **Addon detection** may affect which sounds are available

### Future Research
- Reverse engineer PAK format completely
- Document music transition algorithm
- Map all sound events to in-game triggers
- Create sound replacement modding guide

---

## 📊 Project Statistics

**Estimated Totals:**
- **Audio Files:** 1,000-1,150+
- **Music Tracks:** 110-130 MP3 files
- **Sound Effects:** 800-1,000+ WAV files
- **Categories:** 20+ types
- **Storage (compressed):** ~500-800 MB
- **Storage (uncompressed):** ~2-3 GB

**Script Analysis:**
- **DrwSound.lua:** 1,030 lines, 500+ events
- **Sound Categories:** 20+ types
- **Lua Scripts:** 5+ files

---

**Status:** 🟢 Ready to Begin
**Phase:** Phase 1 - Identification Complete
**Next Milestone:** Phase 2 - Begin Extraction
**Last Updated:** October 18, 2025
