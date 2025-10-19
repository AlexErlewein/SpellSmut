# SpellSmut Project Instructions for AI Assistants

## Project Overview

This is a **SpellForce Platinum Edition** modding and analysis project. SpellForce is a fantasy real-time strategy/RPG hybrid from 2005 that uses a **C++ engine** with **Lua 4.0 scripting** for game logic.

## Technology Stack

- **Core Engine**: C++ (Windows executable)
- **Scripting**: Lua 4.0 (NOT modern Lua 5.x)
- **Video**: Bink Video Technology
- **Audio**: Miles Sound System
- **Assets**: Custom PAK archive format
- **Target Platform**: Windows (DirectX 9)

## Code Style Guidelines

### General Rules
- Use **4 spaces** for indentation (never tabs)
- Keep lines under **100 characters** when possible
- Use **descriptive variable names**
- Comment complex logic and engine interactions
- Ensure final newline at end of files
- Remove trailing whitespace

### Lua Conventions (Lua 4.0)

**Important**: This project uses **Lua 4.0**, which has different syntax than modern Lua:

```lua
-- Lua 4.0 syntax (USE THIS):
getn(table)              -- NOT #table
tremove(table, index)    -- Table removal
tinsert(table, value)    -- Table insertion
globals()                -- Access global table

-- Upvalues use % syntax:
function MyFunc()
    return %globalVariable
end

-- No ipairs/pairs in Lua 4.0, use for i,v in table do
```

**Naming Conventions**:
- **Global functions**: PascalCase → `FindAnim()`, `GetSoundFile()`, `FindBones()`
- **Local variables**: snake_case → `local mod_dir`, `local sound_file`
- **Tables/data**: lowercase → `local data = {}`, `local sounds = {}`
- **Constants**: UPPER_SNAKE_CASE → `local MAX_SOUNDS = 100`

**C++ Engine Bindings** (exposed to Lua):
These functions are provided by the C++ engine and should not be redefined:

```lua
-- File I/O
dir_readdirectory(path)
readfile(path)
doscript(path)

-- String manipulation
strsplit(delimiter, string)
gsub(string, pattern, replace)
strfind(string, pattern)
strsub(string, start, end)
strlen(string)
strjoin(separator, array)

-- List operations
list_concat(list1, list2)
list_converttoset(list)
list_insert(list, item)
tremove(list, index)
getn(list)
tkeys(table)
tinsert(table, value)
sort(list)

-- Game-specific objects
UtlMod:GetInstalledModCount()
UtlMod:GetInstalledModDirectory(index)
ObjectLibrary:GetSoundLibrary()
SoundLibrary:AddSound(id, type, weapon, flags)

-- Global tables (engine-provided)
DrwSoundId
SndDrwEventSamples
ObjectLibrary
```

### Markdown Conventions
- Use **2 spaces** for indentation
- Keep lines under **80 characters** for documentation
- Use clear section headers with proper hierarchy
- Include code examples in fenced code blocks with language tags

## Project Structure

```
SpellSmut/
├── OriginalGameFiles/          # Original game files (NEVER MODIFY)
│   ├── pak/                    # Compressed asset archives (.pak)
│   ├── script/                 # Lua game logic scripts
│   │   ├── DrwFiles.lua        # Asset loading system
│   │   └── DrwSound.lua        # Sound event definitions
│   ├── texture/                # Font textures (TGA format)
│   ├── videos/                 # Bink video cinematics
│   └── *.exe, *.dll            # Game executables and libraries
├── ProjectPlanning/            # Planning & strategy documents
├── docs/                       # User-facing documentation & guides
│   ├── AITools/                # AI assistant guides
│   ├── AssetsExtraction/       # Asset extraction documentation
│   ├── CFFExtraction/          # CFF file modding documentation
│   ├── img/                    # Documentation images
│   ├── assets/                 # Jekyll/GitHub Pages assets
│   └── _layouts/               # Jekyll templates
├── src/                        # Source code & utilities
│   ├── helper_tools/           # Standalone helper scripts
│   ├── luas/                   # Lua scripts and modifications
│   └── TiganachReloaded/       # CFF editing library and tools
├── ExtractedAssets/            # Assets extracted from PAK files
│   ├── UI/                     # User interface assets
│   ├── Audio/                  # Sound effects, music, voice
│   └── ...                     # Additional asset types
├── ModdingTools/               # Third-party modding tools
├── ModdedGameFiles/            # Modified game files & custom mods
└── .zed/                       # Zed IDE project settings
```

## 📁 File Organization Rules

**CRITICAL**: Follow these file organization conventions strictly.

### 1. Planning & Strategy Files → `ProjectPlanning/`

**What goes here:**
- Project planning documents
- Development roadmaps
- Strategy documents
- Architecture planning
- Editor planning documents
- Modding plans

**Examples:**
- `MODDING_PLAN.md`
- `EDITOR_PLANNING.md`
- Future planning documents

**Rule:** All planning/strategy files MUST be placed in `ProjectPlanning/` folder.

### 2. Documentation Files → `docs/`

**What goes here:**
- User-facing documentation
- Modding guides
- System documentation
- Reference materials
- Tutorials and walkthroughs

**Subfolder Structure:**
- `docs/AssetsExtraction/` - Asset extraction guides and documentation
- `docs/CFFExtraction/` - CFF file modding documentation
- `docs/img/` - Documentation images
- `docs/assets/` - Jekyll/GitHub Pages assets
- `docs/_layouts/` - Jekyll templates

**Examples:**
- `docs/index.md` - Main documentation index
- `docs/SpellForce_Quest_System_Guide.md` - Quest system guide
- `docs/SOUND_SYSTEM_GUIDE.md` - Sound system guide
- `docs/CFFExtraction/CFF_MODDING_GUIDE.md` - CFF modding guide
- `docs/AssetsExtraction/BULK_EXTRACTION_GUIDE.md` - Extraction guide

**Rule:** All documentation MUST be placed in `docs/` folder. Use or create appropriate subfolders for better structure when possible.

### 3. Source Code → `src/`

**What goes here:**
- Python scripts and modules
- Helper tools
- Modding utilities
- Core application code
- Active development libraries (TiganachReloaded, etc.)

**Subfolder Structure:**
- `src/helper_tools/` - Standalone helper scripts
- `src/luas/` - Lua scripts and modifications
- `src/TiganachReloaded/` - CFF editing library and tools
- Additional subdirectories as needed for different modules

### 4. Extracted Assets → `ExtractedAssets/`

**What goes here:**
- Assets extracted from game PAK files
- UI elements
- Audio files (future)
- Textures (future)
- Models (future)

**Subfolder Structure:**
- `ExtractedAssets/UI/` - User interface assets
- `ExtractedAssets/Audio/` - Sound effects, music, voice
- Additional subdirectories as needed

### 5. Modding Tools → `ModdingTools/`

**What goes here:**
- Third-party modding tools
- External utilities
- Reference materials

**Note:** Active development tools and libraries have been moved to `src/`

### 6. Original Game Files → `OriginalGameFiles/`

**What goes here:**
- Untouched original game files
- Reference copies
- Source PAK files
- Game executables and scripts

**Rule:** NEVER modify files in this directory. Keep as pristine reference.

### 7. Modded Game Files → `ModdedGameFiles/`

**What goes here:**
- Modified game files
- Custom mods
- Testing versions

### 🎯 Quick Reference Table

| File Type | Location | Use Subfolders? |
|-----------|----------|-----------------|
| Planning documents | `ProjectPlanning/` | No |
| Documentation/Guides | `docs/` | **Yes** - organize by topic |
| Source code | `src/` | **Yes** - organize by purpose |
| Extracted assets | `ExtractedAssets/` | **Yes** - organize by type |
| Modding tools | `ModdingTools/` | **Yes** - one per tool |
| Original game files | `OriginalGameFiles/` | Maintain game structure |
| Modded files | `ModdedGameFiles/` | Mirror game structure |

### 📝 File Organization Best Practices

#### Documentation
1. Always use markdown (`.md`) format
2. Include clear headings and table of contents
3. Cross-reference related documents
4. Keep the main `docs/index.md` updated when adding new guides
5. Use descriptive filenames (e.g., `CFF_MODDING_GUIDE.md` not `guide.md`)

#### Planning Documents
1. Include dates in planning documents
2. Keep project status up-to-date
3. Reference related documentation in `docs/`

#### Code Organization
1. Use descriptive module/script names
2. Keep related functionality together in subfolders
3. Add README files in subdirectories when needed

#### Asset Management
1. Maintain clear folder hierarchy for extracted assets
2. Include README files explaining asset organization
3. Don't mix original and modified assets

### 🔄 When Adding New Content

#### Adding a New Guide
1. Create the `.md` file in `docs/` (or appropriate subfolder)
2. Update `docs/index.md` to include the new guide
3. Add cross-references in related guides
4. If creating a new topic category, consider creating a new subfolder

#### Adding a New Plan
1. Create the `.md` file in `ProjectPlanning/`
2. Use a descriptive name with context (e.g., `UI_REDESIGN_PLAN.md`)
3. Include date and version information

#### Adding New Tools/Scripts
1. Place in `src/` or `src/helper_tools/`
2. Document usage in appropriate `docs/` guide
3. Update relevant planning documents if needed

### ⚠️ Common File Organization Mistakes to Avoid

❌ **Don't:**
- Mix planning docs and user documentation
- Put documentation files in the root directory
- Create documentation without updating the index
- Use vague filenames like `notes.md` or `temp.md`
- Modify files in `OriginalGameFiles/`

✅ **Do:**
- Follow the folder structure consistently
- Use subfolders to maintain organization
- Keep documentation and planning separate
- Use clear, descriptive names
- Update index files when adding content

## Important Technical Details

### Asset System
- **PAK files**: Custom compressed archives containing game assets (models, textures, sounds, etc.)
- **Asset loading**: Dual-source (directory + manifest file), merged and deduplicated
- **Modding system**: Non-destructive asset merging from mod directories

### Audio System
- **Sound events**: Defined in `DrwSound.lua` with properties (Volume, FallOffMin, FallOffMax)
- **3D positional audio**: Uses falloff distances for spatial sound
- **Random variation**: Multiple sound files per event to avoid repetition
- **Categories**: Combat, magic, environmental, work sounds

### Magic System
- **8 Schools**: White, Black, Fire, Ice, Earth, Air, Mental, Elemental
- **Spell mechanics**: Cast → Resolve → Hit/Miss → Resist checks
- **Sound events**: Separate sounds for cast, resolve, hit, DOT, summon, resist

### Combat System
- **19 weapon types**: Each with unique sounds and animations
- **6 playable races**: Human, Orc, Elf, Dark Elf, Dwarf, Troll
- **Unit types**: Main character, heroes, race units, titans, NPCs
- **Sound events**: Screams, attacks, deaths (gender-specific, multiple variations)

## Common Tasks & Guidelines

### When Analyzing Original Code
1. **Respect Lua 4.0 syntax** - Don't suggest modern Lua features
2. **Document C++ bindings** - Note when functions are engine-provided
3. **Understand the architecture** - Engine (C++) + Logic (Lua) separation
4. **Preserve compatibility** - Original game must still work

### When Creating New Code
1. **Follow existing patterns** - Match style of `DrwFiles.lua` and `DrwSound.lua`
2. **Use engine functions** - Leverage existing C++ bindings
3. **Test asset loading** - Ensure mod system compatibility
4. **Add comments** - Explain complex logic and engine interactions

### When Writing Documentation
1. **Be comprehensive** - Include examples and use cases
2. **Explain context** - Why something works the way it does
3. **Provide references** - Link to related files or documentation
4. **Use consistent formatting** - Follow established markdown style

### When Suggesting Improvements
1. **Don't break compatibility** - Original game must function
2. **Consider performance** - Game runs on older hardware
3. **Document changes** - Explain what and why
4. **Provide rollback** - How to undo if needed

## File Types & Extensions

- `.lua` - Lua scripts (Lua 4.0 syntax)
- `.pak` - Compressed asset archives (binary, don't parse)
- `.bik` - Bink video files (binary)
- `.tga` - Targa image files (font atlases)
- `.bor` - Bone rig files (skeletal animation data)
- `.wav` - Audio files
- `.txt` - Text manifests (asset lists)
- `.md` - Markdown documentation

## Excluded Files (Don't Process)

Binary files that should not be read or analyzed:
- `**/*.pak` - Game archives
- `**/*.bik` - Videos
- `**/*.tga` - Textures
- `**/*.dll` - Libraries
- `**/*.exe` - Executables
- `**/*.ico` - Icons
- `**/*.dat` - Binary data

## Git Workflow

- **Main branch**: Stable, working code
- **Feature branches**: `feature/description`
- **Hotfix branches**: `hotfix/description`
- **Experimental branches**: `experimental/description`
- **Mod branches**: `mod/mod-name`

Consider using **git worktrees** for parallel development (see `docs/AITools/git-worktrees-with-claude.md`).

## Testing Guidelines

1. **Manual testing**: Run the game after changes
2. **Script validation**: Check Lua syntax (remember Lua 4.0!)
3. **Asset verification**: Ensure resources load correctly
4. **Mod compatibility**: Test with mod system
5. **Documentation updates**: Keep docs in sync with code

## References & Resources

- **Project Documentation**: See `docs/` folder
- **CLAUDE.md**: Comprehensive codebase analysis
- **Original Scripts**: `OriginalGameFiles/script/` for reference implementations
- **AI Tools Guide**: `docs/AITools/` for workflow documentation

## Communication Style

When working on this project:
- **Be specific**: Reference exact file paths and line numbers
- **Explain rationale**: Why a change is being made
- **Provide examples**: Show before/after code
- **Consider context**: Game is from 2005, respect that era's practices
- **Ask questions**: If unsure about game mechanics or engine behavior

## Common Pitfalls to Avoid

1. ❌ Using modern Lua 5.x syntax → Use Lua 4.0
2. ❌ Hardcoding paths with forward slashes → Use backslashes for Windows
3. ❌ Assuming hash tables → Lua 4.0 has limited table features
4. ❌ Breaking mod compatibility → Always test mod loading
5. ❌ Ignoring performance → Game runs on old hardware
6. ❌ Removing original files → Keep originals intact
7. ❌ Using undefined globals → Check engine bindings first

## Quality Checklist

Before considering a task complete:
- [ ] Code follows Lua 4.0 syntax
- [ ] Naming conventions are consistent
- [ ] Comments explain complex logic
- [ ] Documentation is updated
- [ ] Original game functionality preserved
- [ ] Mod system compatibility maintained
- [ ] No trailing whitespace
- [ ] Final newline present
- [ ] Line length under 100 characters (where reasonable)

## Getting Help

If you need clarification on:
- **Game mechanics**: Refer to `CLAUDE.md` codebase analysis
- **Lua 4.0 syntax**: Check original scripts for patterns
- **Engine functions**: Look at how existing scripts use them
- **Project workflow**: See `docs/AITools/` guides

---

**Project Goal**: Analyze, document, and potentially enhance the SpellForce Platinum Edition game while preserving its original functionality and supporting the modding community.

**Approach**: Respectful analysis, careful documentation, and thoughtful enhancement suggestions that honor the original design while enabling modern development practices.

*Last Updated: 2025-10-18*