# Mod Packaging / Export UI Spec

## Goals
- Export quests as installable mod packages with metadata, dependencies, and versioning.
- Support dependency resolution and compatibility checking.

## Mod Package Structure

### Package Contents
- **Lua Scripts**: Generated quest Lua files (n*.lua)
- **CFF Diffs**: Changes to GameData.cff (additive changes only)
- **Localization Files**: Quest name/description/dialogue strings
- **Metadata**: mod.json with name, version, author, dependencies, description
- **Manifest**: List of all files and their checksums

### Package Format
- **Archive**: ZIP file with standardized structure
- **Naming**: `[ModName]_v[Version].zip`
- **Structure**:
  ```
  [ModName]_v1.0.0.zip
  ├── mod.json
  ├── manifest.txt
  ├── script/
  │   └── [Campaign]/
  │       ├── n9001.lua
  │       └── n9002.lua
  ├── data/
  │   └── GameData.cff.patch
  └── localization/
      ├── en/
      ├── de/
      └── fr/
  ```

## Metadata (mod.json)

### Required Fields
- **name**: Mod name
- **version**: Semantic version (e.g., "1.0.0")
- **author**: Author name
- **description**: Mod description
- **questIds**: List of quest IDs included
- **dependencies**: List of required mods (name, version range)

### Optional Fields
- **homepage**: Mod homepage URL
- **license**: License type
- **compatibility**: Game version compatibility
- **changelog**: Version history

## Dependency Management

### Dependency Resolution
- Check for required mods before installation
- Verify version compatibility (semantic versioning)
- Detect conflicts (overlapping quest IDs, conflicting CFF changes)
- Provide dependency installation suggestions

### Compatibility Checking
- Quest ID range conflicts
- CFF field conflicts
- Localization key conflicts
- Lua script name conflicts
## Export UI

### Package Configuration
- **Mod Name**: Text input
- **Version**: Semantic version input (major.minor.patch)
- **Author**: Text input
- **Description**: Multi-line text area
- **Dependencies**: List with add/remove, version range selector
- **Quest Selection**: Multi-select list of quests to include

### Export Flow
1. **Validation**: Run full quest validation, check for errors
2. **Dependency Check**: Verify dependencies are available
3. **Conflict Detection**: Check for ID conflicts, CFF conflicts
4. **Package Generation**: Create ZIP with all required files
5. **Manifest Generation**: Create manifest with file list and checksums
6. **Summary**: Show package contents, size, dependency status

### Export Options
- **Include CFF Changes**: Checkbox to include CFF patch
- **Include Localization**: Checkbox to include localization files
- **Include Lua Scripts**: Checkbox to include Lua files (always included)
- **Compression Level**: Select compression level for ZIP

## Acceptance Criteria
- Users can export quests as installable mod packages
- Package includes all required files and metadata
- Dependency resolution works correctly
- Conflict detection prevents incompatible mods
- Generated packages can be installed by mod manager

## Implementation Notes
- Use standard ZIP format for compatibility
- Implement semantic versioning parser for dependency resolution
- Create mod manager integration API for installation
- Provide package validation tools for testing

## Installation Structure
- Mods installed to `mods/` directory
- Each mod in separate subdirectory: `mods/[ModName]/`
- Mod manager handles loading order based on dependencies
- CFF patches applied in dependency order
