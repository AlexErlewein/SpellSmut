# Project Organization Rules

This document outlines the file organization conventions for the SpellSmut (SpellForce Modding) project.

---

## 📁 File Organization Conventions

### 1. Planning & Strategy Files
**Location:** `ProjectPlanning/`

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

---

### 2. Documentation Files
**Location:** `docs/`

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

---

### 3. Source Code
**Location:** `src/`

**What goes here:**
- Python scripts and modules
- Helper tools
- Modding utilities
- Core application code
- Active development libraries (TirganachReloaded, etc.)

**Subfolder Structure:**
- `src/helper_tools/` - Standalone helper scripts
- `src/luas/` - Lua scripts and modifications
- `TirganachReloaded/` - CFF editing library and tools
- Additional subdirectories as needed for different modules

---

### 4. Extracted Assets
**Location:** `ExtractedAssets/`

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

---

### 5. Modding Tools
**Location:** `ModdingTools/`

**What goes here:**
- Third-party modding tools
- External utilities
- Reference materials

**Note:** Active development tools and libraries have been moved to `src/`

---

### 6. Original Game Files
**Location:** `OriginalGameFiles/`

**What goes here:**
- Untouched original game files
- Reference copies
- Source PAK files
- Game executables and scripts

**Rule:** NEVER modify files in this directory. Keep as pristine reference.

---

### 7. Modded Game Files
**Location:** `ModdedGameFiles/`

**What goes here:**
- Modified game files
- Custom mods
- Testing versions

---

## 🎯 Quick Reference

| File Type | Location | Use Subfolders? |
|-----------|----------|-----------------|
| Planning documents | `ProjectPlanning/` | No |
| Documentation/Guides | `docs/` | **Yes** - organize by topic |
| Source code | `src/` | **Yes** - organize by purpose |
| Extracted assets | `ExtractedAssets/` | **Yes** - organize by type |
| Modding tools | `ModdingTools/` | **Yes** - one per tool |
| Original game files | `OriginalGameFiles/` | Maintain game structure |
| Modded files | `ModdedGameFiles/` | Mirror game structure |

---

## 📝 Best Practices

### Documentation
1. Always use markdown (`.md`) format
2. Include clear headings and table of contents
3. Cross-reference related documents
4. Keep the main `docs/index.md` updated when adding new guides
5. Use descriptive filenames (e.g., `CFF_MODDING_GUIDE.md` not `guide.md`)

### Planning Documents
1. Include dates in planning documents
2. Keep project status up-to-date
3. Reference related documentation in `docs/`

### Code Organization
1. Use descriptive module/script names
2. Keep related functionality together in subfolders
3. Add README files in subdirectories when needed

### Asset Management
1. Maintain clear folder hierarchy for extracted assets
2. Include README files explaining asset organization
3. Don't mix original and modified assets

---

## 🔄 When Adding New Content

### Adding a New Guide
1. Create the `.md` file in `docs/` (or appropriate subfolder)
2. Update `docs/index.md` to include the new guide
3. Add cross-references in related guides
4. If creating a new topic category, consider creating a new subfolder

### Adding a New Plan
1. Create the `.md` file in `ProjectPlanning/`
2. Use a descriptive name with context (e.g., `UI_REDESIGN_PLAN.md`)
3. Include date and version information

### Adding New Tools/Scripts
1. Place in `src/` or `src/helper_tools/`
2. Document usage in appropriate `docs/` guide
3. Update relevant planning documents if needed

---

## ⚠️ Common Mistakes to Avoid

❌ **Don't:**
- Mix planning docs and user documentation
- Put documentation files in the root directory
- Create documentation without updating the index
- Use vague filenames like `notes.md` or `temp.md`

✅ **Do:**
- Follow the folder structure consistently
- Use subfolders to maintain organization
- Keep documentation and planning separate
- Use clear, descriptive names
- Update index files when adding content

---

**Last Updated:** October 2025
**Maintainers:** SpellSmut Development Team
