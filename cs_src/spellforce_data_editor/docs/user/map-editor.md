# Map Editor Guide

The Map Editor provides visual editing of SpellForce maps with real-time 3D preview.

## Table of Contents

1. [Interface Overview](#interface-overview)
2. [Navigation](#navigation)
3. [Terrain Editing](#terrain-editing)
4. [Entity Placement](#entity-placement)
5. [Map Properties](#map-properties)
6. [Save/Load](#saveload)

## Interface Overview

### Main Editor Window

```
┌─────────────────────────────────────────────────────────┐
│ Map Editor                                     [Save] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│                   3D Viewport                           │
│                 (Interactive)                           │
│                                                          │
├──────────────┬──────────────────────────────────────────┤
│ Tools        │ Entity List                             │
│              │                                          │
│ - Select     │ Buildings: 25                            │
│ - Terrain    │ Units: 150                               │
│ - Buildings  │ Objects: 75                              │
│ - Units      │ Portals: 3                               │
│ - Objects    │                                          │
│ - Decor      │                                          │
└──────────────┴──────────────────────────────────────────┘
```

### Controls

**3D Viewport Controls**:
- **Left Mouse**: Rotate camera
- **Right Mouse**: Pan camera
- **Scroll Wheel**: Zoom in/out
- **Middle Mouse**: Tilt camera

**Toolbar**:
- **Select**: Select and move entities
- **Raise/Lower**: Modify terrain height
- **Paint**: Apply terrain textures
- **Place**: Add entities
- **Delete**: Remove selected

## Navigation

### Camera Controls

| Input | Action |
|-------|--------|
| Left Drag | Orbit around selection |
| Right Drag | Pan camera |
| Scroll | Zoom in/out |
| Middle Drag | Tilt camera |
| F | Focus on selection |
| Home | Reset camera |

### Moving the View

**To pan**:
- Hold right mouse and drag
- Or use arrow keys

**To zoom**:
- Mouse scroll wheel
- Or Page Up/Down keys

**To rotate**:
- Hold left mouse and drag around center

## Terrain Editing

### Modifying Height

1. Select **Raise/Lower** tool
2. Adjust brush size (1-20 tiles)
3. Click and drag on terrain
4. Height changes by ~100 units per second

**Options**:
- **Brush Size**: 1-20 tiles
- **Strength**: Low/Medium/High
- **Smooth**: Blurs height differences

### Changing Terrain Type

1. Select **Paint** tool
2. Choose terrain type from dropdown
3. Paint on terrain

**Terrain Types**:
- Grass, Dirt, Stone, Sand
- Snow, Swamp, Lava
- Water (shallow/deep)
- Road, Forest tiles

### Setting Flags

**Movement Flags** (blocks units):
1. Right-click tile
2. Toggle "Blocks Movement"

**Vision Flags** (blocks sight):
1. Right-click tile
2. Toggle "Blocks Vision"

Both flags can be set independently.

## Entity Placement

### Placing Buildings

1. Select **Buildings** tool
2. Choose building type
3. Click on map to place

**Building Properties**:
- Type ID (building template)
- Position (X, Y)
- Rotation (0-360 degrees)
- NPC ID (script reference)
- Level (1-5 for upgradeables)
- Race ID (owner)

### Placing Units

1. Select **Units** tool
2. Choose unit type
3. Click on map to place

**Unit Properties**:
- Type ID (unit template)
- Position
- Flags (state, alliance)
- NPC ID (script reference)
- Group (unit group)

### Placing Objects

1. Select **Objects** tool
2. Choose object type
3. Click on map to place

**Object Properties**:
- Type ID (object template)
- Position
- Rotation
- NPC ID (script reference)
- Unknown1 (data field)

### Decorations

Decorations (decals) are automatically placed based on terrain types.

To manually adjust:
1. Select **Decor** tool
2. Paint decorations
3. Or use "Clear" to remove

## Map Properties

### Map Information

**Size**: 16-256 tiles (square)
- Campaign maps: 128-256
- Multiplayer maps: 64-128
- Coop maps: 64-128

**Type**:
- Campaign: Single player
- Multiplayer: PvP
- Coop: Team vs AI

### Player Spawns

**Setting Spawns**:
1. Select **Spawns** tool
2. Click on bindstone
3. Set spawn properties

**Spawn Properties**:
- Position (must be at bindstone)
- Text ID (player name)
- Team assignment

### Portals

**Adding Portals**:
1. Select **Portals** tool
2. Choose portal type
3. Click to place

**Portal Properties**:
- Type ID (destination)
- Position
- Rotation

### Weather

**Weather Settings**:
- Clear
- Rain
- Snow
- Fog
- Storm

## Advanced Features

### Heightmap Import

Import heightmap from image:
1. Select **File → Import Heightmap**
2. Choose grayscale image
3. Adjust scaling
4. Apply

**Requirements**:
- Image must be square
- Grayscale values determine height
- Resolution = map size

### Texture Painting

Paint multiple terrain textures:
1. Select **Paint** tool
2. Choose primary texture
3. Hold Shift for secondary texture
4. Paint blends between them

### Entity Selection

**Select Multiple**:
- Hold Ctrl and click
- Or drag selection rectangle

**Group Operations**:
- Move all selected
- Rotate all selected
- Delete all selected

### Undo/Redo

Map editor supports unlimited undo:
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo
- Undo history persists until save

## Save/Load

### Loading a Map

1. Click **File → Open**
2. Navigate to `maps/` folder
3. Select `.map` file
4. Wait for load (2-5 seconds for large maps)

### Saving a Map

**First Save**:
1. Click **File → Save As**
2. Choose location and name
3. Wait for save
4. Test in-game

**Subsequent Saves**:
- Click **File → Save**
- Overwrites existing file

### Auto-Save

The editor does **not** auto-save. Save frequently!

## Best Practices

### 1. Test in Small Increments

```
1. Make a few changes
2. Save map
3. Test in-game
4. Verify changes
5. Continue editing
```

### 2. Use Snap to Grid

Entities snap to tile grid by default. For precise placement:
1. Disable snap
2. Place entity
3. Re-enable snap

### 3. Check Pathfinding

After editing terrain:
1. Place test units
2. Verify they can navigate
3. Check movement flags

### 4. Validate Multiplayer Maps

For multiplayer/coop maps:
1. Verify spawn points
2. Test team compositions
3. Check resource distribution

### 5. Keep Backups

Always keep original maps:
```batch
copy mymap.map mymap_backup.map
```

## Troubleshooting

### Editor Crashes on Load

**Possible causes**:
- Corrupted map file
- Missing game directory
- Incompatible chunk version

**Solutions**:
1. Check `UserLog.txt` for errors
2. Verify game directory is set
3. Try loading a different map

### 3D View is Black

**Possible causes**:
- Graphics driver issues
- OpenGL version too old
- Missing terrain data

**Solutions**:
1. Update graphics drivers
2. Verify OpenGL 3.0+ support
3. Reload the map

### Entities Not Appearing

**Possible causes**:
- Below terrain
- Wrong rotation
- Missing model

**Solutions**:
1. Check entity height (Z position)
2. Verify rotation angle
3. Ensure model exists in PAK files

### Performance Issues

Large maps (>128 tiles) may be slow:
1. Reduce view distance
2. Disable shadows
3. Close other applications

## Tips and Tricks

### 1. Use Templates

Create a map template with:
- Pre-placed spawn points
- Standard terrain setup
- Common entities

Use as starting point for new maps.

### 2. Height Map Shortcuts

**Flatten terrain**:
- Select area
- Use "Smooth" tool repeatedly

**Create mountains**:
- Use "Raise" tool
- Then "Smooth" to blend

**Create valleys**:
- Lower terrain
- Paint river/water type

### 3. Entity Placement Shortcuts

**Quick duplicate**:
- Select entity
- Hold Ctrl, drag to copy

**Quick rotate**:
- Select entity
- Press R to rotate 45°
- Shift+R for -45°

### 4. Map Size Considerations

| Map Size | Tiles | Use Case |
|----------|-------|----------|
| 32 | 1024 | Skirmish |
| 64 | 4096 | Small scenario |
| 128 | 16384 | Medium campaign |
| 256 | 65536 | Large campaign |

Larger maps = longer load times.

## Next Steps

- [Game Data Editor](gamedata-editor.md) - Edit game data
- [Asset Management](assets.md) - View game assets
- [Script Editing](scripts.md) - Modify game scripts

---

**Related**: [Getting Started Guide](README.md), [Architecture: Map System](../architecture/map-system.md)
