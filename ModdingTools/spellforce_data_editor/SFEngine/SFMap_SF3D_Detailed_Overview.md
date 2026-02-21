# SFEngine SF3D and SFMap Detailed Overview

This document provides a detailed overview of the `SF3D` and `SFMap` folders within the `SFEngine` directory.

## SF3D Folder

This folder contains the core 3D rendering engine and related functionalities.

### `Physics/`
Handles 3D physics calculations and primitives.
- **`BoundingBox.cs`**: Defines an axis-aligned bounding box (AABB) used for collision detection and culling.
- **`Frustum.cs`**: Represents a camera's view frustum, used for frustum culling (determining what is visible to the camera).
- **`Plane.cs`**: Defines a 2D plane in 3D space, used in frustum calculations.
- **`Ray.cs`**: Implements a ray for raycasting, used to detect intersections with 3D objects like bounding boxes and triangles.

### `SFRender/`
Manages the rendering process.
- **`FrameBuffer.cs`**: A wrapper for OpenGL Framebuffer Objects (FBOs), allowing for off-screen rendering and post-processing effects.
- **`SFRenderEngine.cs`**: The main rendering engine. It orchestrates the rendering passes, manages shaders, and handles the OpenGL state.
- **`SFShader.cs`**: A helper class for compiling and managing GLSL shaders, including shader parameters (uniforms) and preprocessor definitions.

### `SceneSynchro/`
Manages the scene graph and synchronization of scene objects.
- **`SFEffectManager.cs`**: Manages particle effects and other visual effects in the scene.
- **`SFScene.cs`**: Represents the entire 3D scene, holding all game objects, the camera, lighting information, and managing the game loop timing.
- **`SceneNode.cs`**: The base class for all objects in the scene graph. It implements a hierarchical structure with parent-child relationships and manages transformations (position, rotation, scale).

### `UI/`
Contains classes for rendering the user interface.
- **`UIFont.cs`**: Handles font rendering by processing font textures.
- **`UIManager.cs`**: Manages UI elements, organizing them into quad storages for efficient rendering.
- **`UIQuadStorage.cs`**: A storage for UI elements (quads) that share the same texture, optimizing draw calls.

### Root Files
- **`InterpolatedValue.cs`**: Provides classes for interpolating values (float, Vector3, Quaternion, Color) over time, essential for animations.
- **`Lighting.cs`**: Defines lighting properties, including ambient light, sun light, and atmospheric effects like fog.
- **`MeshCache.cs`**: A cache for 3D mesh data, optimizing memory usage and rendering performance by batching similar geometry.
- **`SFAnimation.cs`**: Handles skeletal animations, defining how bone transforms change over time.
- **`SFBoneIndex.cs`**: Manages the mapping of bones for skinned models, which are split into parts for rendering.
- **`SFMaterial.cs`**: Defines the material properties of a 3D model, such as texture, render mode, and transparency.
- **`SFModel3D.cs`**: Represents a static 3D model, containing geometry and material information.
- **`SFModelSkin.cs`**: Represents a skinned (animated) 3D model, which is composed of multiple chunks.
- **`SFSkeleton.cs`**: Defines the bone hierarchy (skeleton) for animated models.
- **`SFTexture.cs`**: A resource class for handling texture loading (DDS/TGA) and management in OpenGL.

## SFMap Folder

This folder is responsible for everything related to SpellForce maps, from generation to object management.

### `MapGen/`
Contains tools for procedural map generation.
- **`GradientMap.cs`**: A 2D map of floating-point values, used as a base for generating heightmaps and other features.
- **`LatticeKernel.cs`**: Defines kernels (e.g., Gaussian) for applying filters to gradient maps.
- **`MapGenerator.cs`**: The main class for generating maps procedurally.

### Root Files
- **`SFCoord.cs`**: A simple struct representing 2D coordinates on the map grid.
- **`SFMap.cs`**: The main class that represents a SpellForce map, holding all its components like heightmap, buildings, units, etc.
- **`SFMapBuildingManager.cs`**: Manages all building objects on the map.
- **`SFMapCollisionBoundary.cs`**: Defines the collision boundaries for objects like buildings.
- **`SFMapDecorationManager.cs`**: Manages decorative objects on the map.
- **`SFMapEntity.cs`**: A base class for all map entities (units, buildings, objects).
- **`SFMapHeightMap.cs`**: Manages the map's heightmap, including its geometry, textures, and flags (e.g., for movement blocking).
- **`SFMapInteractiveObjectManager.cs`**: Manages interactive objects like bindstones and monuments.
- **`SFMapLakeManager.cs`**: Manages lakes and other bodies of water on the map.
- **`SFMapMetaData.cs`**: Contains metadata about the map, such as spawn points and team compositions for multiplayer.
- **`SFMapObjectManager.cs`**: Manages static objects on the map.
- **`SFMapOcean.cs`**: Manages the ocean plane that surrounds island maps.
- **`SFMapPortalManager.cs`**: Manages portals on the map.
- **`SFMapTerrainTextureManager.cs`**: Manages the terrain textures and how they are blended on the heightmap.
- **`SFMapUnitManager.cs`**: Manages all unit objects on the map.
- **`SFMapWeatherManager.cs`**: Manages weather settings for the map.
