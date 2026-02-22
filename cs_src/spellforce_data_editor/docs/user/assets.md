# Asset Management Guide

The Asset Viewer allows you to browse, preview, and extract game assets from PAK archives.

## Table of Contents

1. [Overview](#overview)
2. [Asset Types](#asset-types)
3. [Browsing Assets](#browsing-assets)
4. [Extracting Assets](#extracting-assets)
5. [Asset Reference](#asset-reference)

## Overview

The Asset Manager provides access to all game files stored in PAK archives.

### Supported Asset Types

| Type | Extension | Description |
|------|-----------|-------------|
| Models | .msb | 3D geometry |
| Textures | .dds, .tga | Images |
| Animations | .bob | Animation data |
| Skeletons | .bor | Bone hierarchies |
| Sounds | .wav | Audio effects |
| Music | .mp3 | Background music |
| Scripts | .lua | Game scripts |

### Opening Asset Viewer

1. Click **"Asset Viewer"** on main window
2. Wait for PAK file indexing
3. Browse to asset category

## Asset Types

### 3D Models (.msb)

**Contains**:
- Vertex positions
- Normals
- UV coordinates
- Colors
- Triangle indices
- Optional skeleton reference

**Categories**:
- `mesh/units/` - Unit models
- `mesh/buildings/` - Buildings
- `mesh/items/` - Items
- `mesh/effects/` - Effects

**Viewing**:
- 3D preview with rotation
- Wireframe toggle
- Bounding box display

### Textures

**DDS Format**:
- Compressed textures (DXT1, DXT5)
- Mipmaps included
- Used for most game textures

**TGA Format**:
- Uncompressed textures
- Used for UI elements
- RGB or RGBA format

**Categories**:
- `texture/terrain/` - Ground textures
- `texture/unit/` - Unit skins
- `texture/ui/` - Interface elements

### Animations (.bob)

**Contains**:
- Bone transformations
- Keyframe data
- Animation duration
- Loop information

**Categories**:
- `animation/units/` - Unit animations
- `animation/buildings/` - Building animations
- `animation/effects/` - Effect animations

### Skeletons (.bor)

**Contains**:
- Bone hierarchy
- Bone names
- Parent-child relationships
- Bind pose

**Categories**:
- `animation/` - Character skeletons
- `figure*.bor` - Hero/rare unit skeletons

### Audio

**WAV Files**:
- Sound effects
- UI sounds
- Unit responses

**MP3 Files**:
- Background music
- Ambient tracks
- Cutscene audio

**Categories**:
- `sound/sfx/` - Effects
- `sound/speech/` - Dialogue
- `sound/music/` - Music

## Browsing Assets

### Navigation

**Tree View**:
- Folders on left
- Files on right
- Filter by name

**Preview Panel**:
- Shows selected asset
- 3D models: Rotating preview
- Textures: Image preview
- Audio: Playback controls

### Filtering

**By Extension**:
```
Filter: *.dds
Shows: All DDS textures
```

**By Name**:
```
Filter: *sword*
Shows: All files with "sword" in name
```

**By Path**:
```
Filter: mesh/units/*
Shows: All unit models
```

## Extracting Assets

### Single File Extraction

1. Browse to file
2. Right-click file
3. Select **"Extract"**
4. Choose destination
5. File is extracted

### Batch Extraction

1. Select folder or multiple files
2. Right-click
3. Select **"Extract All"**
4. Choose destination folder
5. All files extracted

### Extract with Structure

To preserve folder structure:
1. Right-click folder
2. Select **"Extract with Structure"**
3. Choose root destination
4. Files extracted maintaining paths

## Asset Reference

### Model File Format

The `.msb` format contains:

```c
struct MSBHeader {
    char magic[4];      // "MSB\x01"
    uint version;
    uint flags;
    uint submesh_count;
}

struct SubMesh {
    uint vertex_count;
    uint triangle_count;
    uint vertex_offset;
    uint index_offset;
}
```

### Texture File Format

**DDS Structure**:
```
[DDS Header: 124 bytes]
[Pixel Data: compressed]
```

**Compression Types**:
- DXT1: 4:1 compression, no alpha
- DXT5: 4:1 compression, with alpha
- RGB8: No compression, 24-bit
- RGBA8: No compression, 32-bit

### Animation File Format

The `.bob` format stores:
- Duration (seconds)
- FPS (frames per second)
- Keyframe count
- Bone transformations per keyframe

## Using Extracted Assets

### Editing Models

Extracted models can be:
- Imported into 3D software (Blender, Maya)
- Modified and exported back to .msb
- **Note**: The editor can only read .msb, not write

### Editing Textures

Extracted textures can be:
- Edited in image software (GIMP, Photoshop)
- Saved as DDS with same format
- Replaced in PAK files

**DDS Plugins**:
- GIMP: DDS plugin
- Photoshop: NVIDIA Texture Tools

### Editing Audio

Extracted audio can be:
- Modified in audio software
- Re-encoded (must match format)
- Replaced in PAK files

**Format Requirements**:
- WAV: 16-bit PCM, 44.1kHz or 22.05kHz
- MP3: 128-192 kbps bitrate

## Advanced Features

### Searching for Assets

**By Model Reference**:
Find all models used by a specific unit:
1. Select unit in Category 2024
2. Note ModelID field
3. Search for model with that ID

**By Texture Reference**:
Find all textures used by a model:
1. Open model in viewer
2. View material info
3. Lists all textures

### Asset Dependencies

Models reference:
- Textures (by name)
- Skeletons (by name)
- Animations (by skeleton)

To check dependencies:
1. Open asset viewer
2. Select model
3. Click "Show Dependencies"

### Batch Operations

**Extract All Models**:
1. Navigate to `mesh/`
2. Ctrl+A to select all
3. Extract to destination

**Extract by Type**:
1. Use filter: `*.dds`
2. Ctrl+A to select all
3. Extract

## Modding with Assets

### Adding Custom Assets

**New Models**:
1. Create model in 3D software
2. Export to compatible format
3. Convert to .msb (requires custom tool)
4. Place in PAK file

**New Textures**:
1. Create texture (power of 2 dimensions)
2. Save as DDS
3. Replace existing texture
4. Or add new texture to PAK

### Asset Replacement

To replace an asset:
1. Extract original asset
2. Use as template (dimensions, format)
3. Create replacement
4. Place in PAK file at same location

**Important**: Maintain exact format and dimensions.

## Performance

### Caching

Assets are cached after first load:
- Models: Stored in memory
- Textures: GPU memory
- Audio: Streamed on demand

**Cache Size**:
- Models: ~100-500MB
- Textures: ~200MB-1GB
- Total: Up to 2GB for full cache

### Memory Management

To free memory:
```csharp
SFResourceManager.DisposeAll();
SFResourceManager.InitContainerPaks();
```

Or close and reopen the asset viewer.

## Tips and Tricks

### 1. Quick Preview

Double-click any asset for quick preview (no extraction needed).

### 2. Drag and Drop

Drag assets from viewer to:
- File explorer (extracts)
- Image editor (opens file)

### 3. Recent Files

The viewer maintains a recent files list:
- Click "Recent" in toolbar
- Select previously viewed asset

### 4. Bookmarks

Mark frequently used assets:
1. Right-click asset
2. Select "Add to Bookmarks"
3. Access from "Bookmarks" menu

## Troubleshooting

### "Asset Failed to Load"

**Possible causes**:
- Corrupted PAK file
- Unsupported format
- Missing dependencies

**Solutions**:
1. Verify PAK file integrity
2. Check game directory is correct
3. View `UserLog.txt` for details

### "Texture Appears Corrupted"

**Possible causes**:
- Unsupported compression
- Wrong dimensions

**Solutions**:
1. Update graphics drivers
2. Verify DDS format compatibility
3. Try extracting and viewing externally

### "Model Preview is Empty"

**Possible causes**:
- Missing skeleton
- Corrupted vertex data
- Unsupported format version

**Solutions**:
1. Check console for errors
2. Verify model dependencies
3. Try extracting and inspecting with hex editor

## Best Practices

### 1. Organize Extracted Assets

```
extracted/
├── models/
│   ├── units/
│   ├── buildings/
│   └── items/
├── textures/
│   ├── terrain/
│   └── units/
└── audio/
    ├── music/
    └── sfx/
```

### 2. Keep Originals

Always keep original assets:
```
sword_original.dds
sword_edit.dds
```

### 3. Document Changes

Keep notes on modifications:
```
sword.dds: Changed blade from steel to gold
Increased contrast by 20%
```

### 4. Test Incrementally

After replacing assets:
1. Test in-game
2. Verify visual appearance
3. Check for performance impact

## Next Steps

- [Game Data Editor](gamedata-editor.md) - Edit game data
- [Map Editor](map-editor.md) - Edit maps
- [Script Editing](scripts.md) - Edit game scripts

---

**Related**: [Getting Started Guide](README.md), [Development: Resource Management](../development/README.md)
