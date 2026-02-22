# 3D Rendering Engine (SF3D)

The SF3D engine is responsible for all 3D visualization in the SpellForce Data Editor, including map rendering, model viewing, and asset preview.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Rendering Pipeline](#rendering-pipeline)
4. [Scene Graph](#scene-graph)
5. [Shaders](#shaders)
6. [Materials](#materials)
7. [Performance](#performance)

## Overview

The SF3D engine is built on **OpenGL via OpenTK 4.8.2** and provides:

- 3D map visualization with terrain and entities
- Model and animation preview
- Scene management with transform hierarchy
- Material and lighting system
- Shadow mapping support

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Graphics API | OpenGL 3.0+ | Cross-platform rendering |
| Math Library | OpenTK.Mathematics | Vector/matrix math |
| Window | WinForms GLControl | Integration with UI |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   SFRenderEngine (Static)                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    SFScene (scene)                       │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │              SceneNode (Root)                        │ │ │
│  │  │  ┌──────────┬──────────┬──────────┬──────────────┐ │ │ │
│  │  │  │ Terrain  │ Buildings│ Units    │ Objects      │ │ │ │
│  │  │  └──────────┴──────────┴──────────┴──────────────┘ │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    UIManager (ui)                        │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   Renderer State                         │ │
│  │  - Camera                                               │ │
│  │  - Lighting                                             │ │
│  │  - Render passes                                        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Core Classes

| Class | Responsibility |
|-------|---------------|
| `SFRenderEngine` | Static renderer facade |
| `SFScene` | Scene graph container |
| `SceneNode` | Transform hierarchy node |
| `SFModel3D` | 3D model data |
| `SFMaterial` | Material properties |
| `SFShader` | GLSL shader programs |
| `SFCamera` | View/projection matrices |

## Rendering Pipeline

The renderer uses a multi-pass approach:

### Pass 1: Shadow Map Generation

```
For each light source:
  1. Bind shadow framebuffer
  2. Set light-space camera
  3. Render depth from light POV
  4. Store in shadow texture
```

### Pass 2: Scene Rendering

```
1. Bind main framebuffer
2. Set camera matrices
3. For each render batch:
   a. Bind shader
   b. Bind material
   c. Bind geometry
   d. Draw calls
4. Apply lighting and shadows
```

### Pass 3: Screen-Space Effects

```
1. Fog blending
2. Distance fade
3. Tone mapping (optional)
```

### Pass 4: UI Rendering

```
1. Switch to orthographic projection
2. Render UI elements
3. Render text
```

## Scene Graph

The scene graph organizes objects in a hierarchy:

### Node Types

**SceneNode** - Base node with transform
```
- Position (Vector3)
- Rotation (Quaternion)
- Scale (Vector3)
- Children (List<SceneNode>)
- Mesh (SFModel3D)
```

**SceneNodeSimple** - Simplified node
```
- Inherits SceneNode
- Additional flags (IsDecal, IsClickable, etc.)
```

### Building the Scene

```csharp
// Create root
SceneNode root = new SceneNode();

// Add terrain
SFRenderEngine.scene.AddSceneNodeSimple(
    root,
    "terrain",
    "terrain_node"
);

// Add building
SceneNode building = SFRenderEngine.scene.AddSceneNode(
    root,
    mesh_name,
    "building_" + id
);
building.Position = new Vector3(x, y, z);
building.Rotation = Quaternion.FromAxisAngle(Vector3.UnitY, angle);
```

### Updating the Scene

```csharp
// Update transform
node.Position = newPosition;
node.Rotation = newRotation;
node.Scale = newScale;

// Mark as dirty
SFRenderEngine.scene.MarkDirty();
```

## Shaders

The engine uses GLSL shaders for rendering.

### Vertex Shader

```glsl
#version 330 core

layout(location = 0) in vec3 aPosition;
layout(location = 1) in vec3 aNormal;
layout(location = 2) in vec2 aTexCoord;
layout(location = 3) in vec4 aColor;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;

out vec3 vNormal;
out vec2 vTexCoord;
out vec4 vColor;
out vec3 vWorldPos;

void main()
{
    mat4 mvp = uProjection * uView * uModel;
    gl_Position = mvp * vec4(aPosition, 1.0);

    vNormal = mat3(uModel) * aNormal;
    vTexCoord = aTexCoord;
    vColor = aColor;
    vWorldPos = (uModel * vec4(aPosition, 1.0)).xyz;
}
```

### Fragment Shader

```glsl
#version 330 core

in vec3 vNormal;
in vec2 vTexCoord;
in vec4 vColor;
in vec3 vWorldPos;

uniform sampler2D uTexture;
uniform vec3 uLightDir;
uniform vec4 uColor;

out vec4 FragColor;

void main()
{
    vec3 normal = normalize(vNormal);
    float diff = max(dot(normal, uLightDir), 0.0);

    vec4 texColor = texture(uTexture, vTexCoord);
    FragColor = texColor * vColor * uColor * (0.3 + 0.7 * diff);
}
```

## Materials

Materials define how objects are rendered:

### Material Properties

```csharp
public class SFMaterial
{
    public string Name;
    public Vector4 Color = Vector4.One;
    public float Specular = 0.5f;
    public float Shininess = 32.0f;

    // Textures
    public SFTexture DiffuseMap;
    public SFTexture NormalMap;
    public SFTexture SpecularMap;

    // Flags
    public bool CastShadow = true;
    public bool ReceiveShadow = true;
    public bool Transparent = false;
}
```

### Creating Materials

```csharp
SFMaterial mat = new SFMaterial
{
    Name = "stone_wall",
    Color = new Vector4(1, 1, 1, 1),
    DiffuseMap = SFResourceManager.Textures.Get("texture/wall.dds")
};
```

## Models

### Loading Models

```csharp
SFModel3D model = SFResourceManager.Models.Get("mesh/unit/hero.msb");
```

### Model Structure

```
SFModel3D
├── SubModels (List<SFSubModel3D>)
│   ├── Vertices (Vector3[])
│   ├── Normals (Vector3[])
│   ├── UVs (Vector2[])
│   ├── Colors (byte[])
│   └── Indices (uint[])
├── Bounds (AABB)
└── Skeleton (SFSkeleton) - optional
```

### Rendering Models

```csharp
// Get model
SFModel3D model = SFResourceManager.Models.Get(meshName);

// Create VAO/ VBO
int vao = GL.GenVertexArray();
GL.BindVertexArray(vao);

// Upload vertex data
int vbo = GL.GenBuffer();
GL.BindBuffer(BufferTarget.ArrayBuffer, vbo);
GL.BufferData(BufferTarget.ArrayBuffer, vertexData, BufferUsageHint.StaticDraw);

// Upload index data
int ebo = GL.GenBuffer();
GL.BindBuffer(BufferTarget.ElementArrayBuffer, ebo);
GL.BufferData(BufferTarget.ElementArrayBuffer, indexData, BufferUsageHint.StaticDraw);

// Draw
GL.DrawElements(PrimitiveType.Triangles, count, DrawElementsType.UnsignedInt, 0);
```

## Camera

### Camera Setup

```csharp
// Perspective projection
Matrix4 projection = Matrix4.CreatePerspectiveFieldOfView(
    fov: MathHelper.PiOver4,
    aspect: width / height,
    zNear: 0.1f,
    zFar: 1000.0f
);

// View matrix
Matrix4 view = Matrix4.LookAt(
    eye: cameraPosition,
    target: cameraTarget,
    up: Vector3.UnitY
);
```

### Camera Controls

The map editor implements:
- **Orbit camera** - Rotate around target
- **Pan camera** - Move in XZ plane
- **Zoom camera** - Adjust distance

## Performance

### Optimization Techniques

1. **Frustum Culling** - Skip off-screen objects
2. **Batch Rendering** - Group by material
3. **LOD System** - Simplify distant geometry
4. **Instancing** - Share identical meshes

### Profiling

```csharp
// Enable debug output
GL.Enable(EnableCap.DebugOutput);

// Log frame time
Stopwatch sw = Stopwatch.StartNew();
Render();
LogUtils.Log.Info($"Frame time: {sw.ElapsedMilliseconds}ms");
```

### Memory Management

```csharp
// Dispose unused resources
SFResourceManager.Models.Dispose(model);
SFResourceManager.Textures.Dispose(texture);

// Log memory usage
SFResourceManager.LogMemoryUsage();
```

## Implementation Reference

| File | Description |
|------|-------------|
| `SFEngine/SF3D/SFRender/SFRenderEngine.cs` | Main renderer |
| `SFEngine/SF3D/SFRender/SFScene.cs` | Scene graph |
| `SFEngine/SF3D/SFModel3D.cs` | Model loading |
| `SFEngine/SF3D/SFTexture.cs` | Texture loading |
| `SFEngine/SF3D/SFShader.cs` | Shader programs |
| `SFEngine/SF3D/SceneSynchro/` | Scene components |

---

**Related**: [Architecture Overview](../architecture/README.md)
