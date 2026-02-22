# Map System (SFMap)

The SFMap system handles loading, editing, and saving game map files. It integrates with the 3D engine to provide a visual map editing experience.

## Table of Contents

1. [Overview](#overview)
2. [Map Structure](#map-structure)
3. [Managers](#managers)
4. [Editing Operations](#editing-operations)
5. [3D Visualization](#3d-visualization)
6. [Save/Load](#saveload)

## Overview

A SpellForce map consists of:

- **Terrain**: Heightmap, textures, movement/visibility flags
- **Entities**: Buildings, units, objects, decorations
- **Metadata**: Spawns, portals, weather, multiplayer settings
- **Environment**: Lakes, boundaries

### Map Properties

| Property | Type | Range | Description |
|----------|------|-------|-------------|
| Width/Height | int | 16-256 | Map dimensions (tiles) |
| Tile Size | float | 4.0 units | World space per tile |
| Max Height | ushort | 0-65535 | Elevation range |

## Map Structure

### SFMap Class

```csharp
public class SFMap
{
    // Dimensions
    public int width { get; private set; }
    public int height { get; private set; }

    // Components
    public SFMapHeightMap heightmap;
    public SFMapBuildingManager building_manager;
    public SFMapUnitManager unit_manager;
    public SFMapObjectManager object_manager;
    public SFMapInteractiveObjectManager int_object_manager;
    public SFMapDecorationManager decoration_manager;
    public SFMapPortalManager portal_manager;
    public SFMapLakeManager lake_manager;
    public SFMapWeatherManager weather_manager;
    public SFMapMetaData metadata;
    public SFMapOcean ocean;

    // Platform ID (for map identification)
    public uint PlatformID;
}
```

### Coordinate System

**Grid Coordinates (SFCoord)**:
```
(0, 0) is top-left
(width-1, height-1) is bottom-right
X increases to the right
Y increases downward
```

**World Coordinates**:
```
(x * 4.0, y * 4.0, height)
```

## Managers

### SFMapHeightMap

Handles terrain elevation and textures:

```csharp
public class SFMapHeightMap
{
    // Elevation data
    public ushort[] height_data;

    // Terrain types
    public byte[] tile_data;

    // Textures
    public SFMapTerrainTextureManager texture_manager;

    // Flags
    public bool IsFlagSet(SFCoord pos, SFMapHeightMapFlag flag);
    public void SetFlag(SFCoord pos, SFMapHeightMapFlag flag, bool value);
}
```

**Height Flags**:
- `FLAG_MOVEMENT` - Blocks unit movement
- `FLAG_VISION` - Blocks line of sight
- `FLAG_ENTITY_BUILDING` - Building present
- `FLAG_ENTITY_UNIT` - Unit present
- `FLAG_ENTITY_OBJECT` - Object present

### SFMapBuildingManager

Manages placed buildings:

```csharp
public class SFMapBuildingManager
{
    public List<SFMapBuilding> buildings;

    public int AddBuilding(int type_id, SFCoord pos, int angle,
                          int npc_id, int level, int race_id);
    public void RemoveBuilding(int index);
    public SFMapBuilding FindBuilding(SFCoord pos);
}
```

**Building Data**:
```
Type ID - Building template ID
Position - Grid coordinates
Angle - Rotation (0-360)
NPC ID - Script reference
Level - Building level
Race ID - Owner race
```

### SFMapUnitManager

Manages placed units:

```csharp
public class SFMapUnitManager
{
    public List<SFMapUnit> units;

    public int AddUnit(int unit_id, SFCoord pos, int flags,
                      int npc_id, int unknown, int group, int unknown2);
    public void RemoveUnit(int index);
    public SFMapUnit FindUnit(SFCoord pos);
}
```

### SFMapObjectManager

Manages interactive objects:

```csharp
public class SFMapObjectManager
{
    public List<SFMapObject> objects;

    public int AddObject(int object_id, SFCoord pos, int angle,
                       int npc_id, int unknown1);
    public void RemoveObject(int index);
    public SFMapObject FindObjectApprox(SFCoord pos);
}
```

**Special Objects**:
- ID 2541 - Coop spawn point
- ID 65-67 - Editor-only markers

### SFMapPortalManager

Manages map portals:

```csharp
public class SFMapPortalManager
{
    public List<SFMapPortal> portals;

    public int AddPortal(int portal_id, SFCoord pos, int angle);
    public void RemovePortal(int index);
}
```

### SFMapDecorationManager

Manages ground decorations (decals):

```csharp
public class SFMapDecorationManager
{
    // 1024x1024 assignment array (one per tile quadrant)
    public byte[] dec_assignment;

    // 255 decoration groups
    public SFMapDecorationGroup[] dec_groups;

    public void GenerateDecorations();
}
```

### SFMapLakeManager

Manages water bodies:

```csharp
public class SFMapLakeManager
{
    public List<SFMapLake> lakes;

    public int AddLake(SFCoord pos, ushort level, byte type,
                       int index, List<SFMapLake> consumed,
                       List<int> consumed_indices);
}
```

**Lake Properties**:
- Surface level (elevation)
- Type (water, lava, etc.)
- Connected tiles

### SFMapMetaData

Contains map metadata:

```csharp
public class SFMapMetaData
{
    // Map type
    public SFMapType map_type; // CAMPAIGN, MULTIPLAYER, COOP

    // Spawns
    public List<SFMapSpawn> spawns;
    public int player_count;

    // Multiplayer teams
    public List<SFMapMultiplayerTeamComposition> multi_teams;

    // Coop settings
    public List<SFMapCoopAISpawn> coop_spawns;
    public SFMapCoopSpawnParam[] coop_spawn_params;

    // Minimap
    public SFMapMinimap original_minimap;
}
```

## Editing Operations

### Adding a Building

```csharp
// Using the manager
building_manager.AddBuilding(
    type_id: 29,        // Farm
    pos: new SFCoord(50, 50),
    angle: 0,
    npc_id: 0,
    level: 1,
    race_id: 1          // Human
);

// Update heightmap flags
heightmap.SetFlag(new SFCoord(50, 50),
                 SFMapHeightMapFlag.FLAG_ENTITY_BUILDING,
                 true);
```

### Removing an Entity

```csharp
// Get index
int index = building_manager.buildings.FindIndex(
    b => b.grid_position == new SFCoord(50, 50)
);

if (index >= 0)
{
    // Clear flags
    heightmap.SetFlag(new SFCoord(50, 50),
                     SFMapHeightMapFlag.FLAG_ENTITY_BUILDING,
                     false);

    // Remove
    building_manager.RemoveBuilding(index);
}
```

### Modifying Terrain

```csharp
// Change elevation
heightmap.SetHeight(new SFCoord(x, y), 5000);

// Change terrain type
heightmap.SetTile(new SFCoord(x, y), terrain_type_id);

// Update flags
heightmap.SetFlag(new SFCoord(x, y),
                 SFMapHeightMapFlag.FLAG_MOVEMENT,
                 true);
```

### Adding a Lake

```csharp
// Lake will automatically expand to connected tiles
// with elevation at or below the specified level
lake_manager.AddLake(
    pos: new SFCoord(100, 100),
    level: 100,        // Low elevation
    type: 0,           // Water
    index: Utility.NO_INDEX,
    consumed: new List<SFMapLake>(),
    consumed_indices: new List<int>()
);
```

## 3D Visualization

### Scene Creation

When a map is loaded, the editor creates a 3D scene:

```csharp
// Create terrain mesh
SFModel3D terrain_mesh = heightmap.GenerateTerrainMesh();
SceneNode terrain_node = scene.AddSceneNodeSimple(
    scene.RootNode,
    "terrain",
    "terrain_node"
);
terrain_node.Mesh = terrain_mesh;

// Create building models
foreach (SFMapBuilding building in building_manager.buildings)
{
    string mesh_name = GetBuildingMesh(building.game_id);
    SFModel3D mesh = SFResourceManager.Models.Get(mesh_name);

    SceneNode node = scene.AddSceneNode(
        scene.RootNode,
        mesh_name,
        "building_" + building.game_id
    );
    node.Mesh = mesh;
    node.Position = new Vector3(
        building.grid_position.x * 4.0f,
        building.height,
        building.grid_position.y * 4.0f
    );
}
```

### Heightmap Generation

```csharp
public SFModel3D GenerateTerrainMesh()
{
    // Generate vertices from heightmap
    List<Vector3> vertices = new List<Vector3>();
    List<Vector3> normals = new List<Vector3>();
    List<Vector2> uvs = new List<Vector2>();
    List<uint> indices = new List<uint>();

    for (int y = 0; y < height - 1; y++)
    {
        for (int x = 0; x < width - 1; x++)
        {
            // Create quad (2 triangles)
            int i = vertices.Count;

            vertices.Add(new Vector3(x * 4, GetZ(x, y), y * 4));
            vertices.Add(new Vector3((x + 1) * 4, GetZ(x + 1, y), y * 4));
            vertices.Add(new Vector3(x * 4, GetZ(x, y + 1), (y + 1) * 4));
            vertices.Add(new Vector3((x + 1) * 4, GetZ(x + 1, y + 1), (y + 1) * 4));

            indices.AddRange(new uint[] {
                (uint)(i + 0), (uint)(i + 2), (uint)(i + 1),
                (uint)(i + 1), (uint)(i + 2), (uint)(i + 3)
            });
        }
    }

    // Create model
    SFModel3D model = new SFModel3D();
    model.CreateRaw(vertices, uvs, null, normals, indices);
    return model;
}
```

## Save/Load

### Loading a Map

```csharp
SFMap map = new SFMap();
int result = map.Load("maps/mymap.map");

if (result != 0)
{
    LogUtils.Log.Error(LogUtils.LogSource.SFMap,
                      $"Failed to load map: {result}");
}
```

**Load Process**:
1. Open chunk file
2. Read header
3. Load chunks sequentially:
   - Chunk 2: Tile data
   - Chunk 3: Tile definitions
   - Chunk 4: Texture IDs
   - Chunk 6: Heightmap (one per row)
   - Chunk 11: Buildings
   - Chunk 12: Units
   - Chunk 29: Objects
   - Chunk 30: Interactive objects
   - Chunk 31: Decorations
   - Chunk 32: Decoration groups
   - Chunk 35: Portals
   - Chunk 40: Lakes
   - Chunk 42/56/60: Flags
   - Chunk 44: Weather
   - Chunk 53: Multiplayer teams
   - Chunk 55: Spawns
   - Chunk 59: Coop settings
4. Generate 3D meshes
5. Create scene graph

### Saving a Map

```csharp
int result = map.Save("maps/mymap_edited.map");

if (result != 0)
{
    LogUtils.Log.Error(LogUtils.LogSource.SFMap,
                      $"Failed to save map: {result}");
}
```

**Save Process**:
1. Create new chunk file
2. Write header
3. Serialize all managers to chunks
4. Close file

### Creating a New Map

```csharp
SFMap map = new SFMap();
int result = map.CreateDefault(
    size: 128,
    generator: null  // Use flat terrain
);

if (result != 0)
{
    LogUtils.Log.Error(LogUtils.LogSource.SFMap,
                      $"Failed to create map: {result}");
}
```

### Unloading a Map

```csharp
map.Unload();

// This releases:
// - 3D meshes
// - Textures
// - Scene nodes
// - Manager data
```

## Implementation Reference

| File | Description |
|------|-------------|
| `SFEngine/SFMap/SFMap.cs` | Main map container |
| `SFEngine/SFMap/SFMapHeightMap.cs` | Terrain system |
| `SFEngine/SFMap/SFMapBuildingManager.cs` | Buildings |
| `SFEngine/SFMap/SFMapUnitManager.cs` | Units |
| `SFEngine/SFMap/SFMapObjectManager.cs` | Objects |
| `SFEngine/SFMap/SFMapMetaData.cs` | Metadata |

---

**Related**: [Format Specifications](../formats/README.md), [User Guide: Map Editor](../user/map-editor.md)
