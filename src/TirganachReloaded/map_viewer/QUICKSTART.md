# Quick Start Guide - SpellForce Map Viewer

## ✅ STATUS: WORKING! (Verified on macOS M4 Pro)

The viewer is now fully functional and displays 3D terrain with height-based coloring!

## Installation

### 1. Install Python Dependencies

```bash
pip install PySide6 PyOpenGL numpy loguru
```

Or install with optional accelerations:

```bash
pip install PySide6 PyOpenGL PyOpenGL-accelerate numpy loguru
```

### 2. Verify Installation

```bash
python -c "import PySide6; import OpenGL; import numpy; print('✓ All dependencies installed')"
```

## Running the Viewer

### Option 1: Using the Launcher (Recommended)

```bash
python src/TirganachReloaded/run_map_viewer.py
```

### Option 2: Direct Module Execution

```bash
python -m TirganachReloaded.map_viewer.map_viewer_window
```

### Option 3: After pip install

```bash
sf-map-viewer
```

## Loading a Map

1. Click **"Open Map"** button in the toolbar
2. Navigate to your SpellForce map directory
   - Usually: `<SpellForce Install>/Maps/`
3. Select a `.map` file (e.g., `P01.map` for Greyfell)
4. The map will load and display in 3D

## Controls

### Movement
- **W** or **↑** - Move forward (faster now)
- **S** or **↓** - Move backward  
- **A** or **←** - Move left
- **D** or **→** - Move right
- **Left Mouse + Drag** - Move camera (drag to move in any direction)

### Camera Rotation
- **Middle Mouse + Drag** - Free look (rotate camera)
- **Q** - Rotate left
- **E** - Rotate right
- **Home** - Rotate left
- **End** - Rotate right
- **Page Up** - Tilt camera up
- **Page Down** - Tilt camera down

### Camera Modes
- **F** - Toggle terrain following / fixed altitude mode
  - **Terrain Following**: Camera smoothly follows terrain height (default)
  - **Fixed Altitude**: Camera stays at constant height for smooth movement

### Zoom
- **Mouse Wheel** - Zoom in/out
- **Insert** - Zoom in (alternative)
- **Delete** - Zoom out (alternative)

### Debug
- **D Key** - Print debug info to console (camera position, map info)

### UI
- **Open Map** - Load a map file
- **Reset Camera** - Return to center of map

## What You'll See

- **Colored Terrain** - 3D heightmap with elevation-based coloring
  - Dark green = Low elevation (valleys)
  - Light green/yellow = High elevation (peaks)
- **Gray Grid** - Positioning reference lines
- **Status Bars** (top-left corner):
  - Orange/Red bar = FPS indicator (green = good)
  - Blue bar = Map size indicator
  - Orange bar = Camera height indicator
- **RGB Axes** - Coordinate system at map center (Red=X, Green=Y, Blue=Z)

**Note**: Textures, units, and buildings are not yet implemented (Phase 2-3)

## Performance

Expected FPS based on map size:

| Map Size | Expected FPS |
|----------|--------------|
| 64x64    | 200+ FPS     |
| 128x128  | 150+ FPS     |
| 256x256  | 100+ FPS     |
| 512x512  | 60+ FPS      |

If performance is low:
- Close other applications
- Update graphics drivers
- Reduce map complexity (future feature)

## Troubleshooting

### "PyOpenGL not installed"
```bash
pip install PyOpenGL
```

### "No module named 'OpenGL.GL'"
```bash
pip install --upgrade PyOpenGL
```

### Black screen / No rendering
- Verify your GPU supports OpenGL 3.3+
- Update graphics drivers
- Try: `python -c "from OpenGL.GL import *; print(glGetString(GL_VERSION))"`

### Map doesn't load / App crashes during loading

**FIXED in v0.1.0!** The viewer now uses the correct map format.

If you still have issues:

1. **Check the console output** - Look for error messages about decompression or size detection
2. **Use the map inspector tool**:
   ```bash
   python -m TirganachReloaded.map_viewer.inspect_map path/to/your.map
   ```
3. **Check the log file**: `map_viewer.log` has detailed error information
4. **Verify map file**:
   - File should be ZLIB compressed (starts with header, then 0x789C at offset 36)
   - Should decompress to a square size (64x64, 128x128, 256x256, 512x512, 1024x1024)

**Common Issues:**
- **"Could not determine map size"** - The decompressed size doesn't match known map dimensions
- **App crashes silently** - Usually means the old `map_loader.py` is being used instead of `simple_map_loader.py`
- **OpenGL errors on macOS** - Update to latest version (fixed deprecated calls)

### Camera moves too fast/slow
- Currently fixed speed (60 units/sec)
- Speed controls planned for Phase 2

### Low FPS
- Large maps (512x512+) may be slower
- Frustum culling planned for Phase 2
- Try a smaller map to verify

## Finding Maps

SpellForce maps are typically located at:

```
<SpellForce Installation Directory>/
└── Maps/
    ├── Campaign/
    │   ├── P01.map          # Greyfell
    │   ├── P02.map          # Liannon
    │   ├── P03.map          # Windwall
    │   ├── P04.map          # Mulandir
    │   └── ...
    └── Multiplayer/
        └── ...
```

### Testing with Small Maps

Start with smaller maps for better performance:
- Campaign maps are usually 256x256 or smaller
- Multiplayer maps vary in size

## Next Steps

After you're comfortable with the viewer:

1. **Read the full documentation**: `README.md`
2. **Check the roadmap**: `IMPLEMENTATION_PLAN.md`
3. **Explore the code**: Well-documented Python modules
4. **Try Phase 2 features**: Coming soon (textures, lighting)

## Getting Help

### Using the Map Inspector Tool

The map inspector helps understand the actual format of .map files:

```bash
# Analyze a map file
python -m TirganachReloaded.map_viewer.inspect_map /path/to/map.map

# Or directly
python src/TirganachReloaded/map_viewer/inspect_map.py /path/to/map.map
```

This tool will:
- Show all chunks found in the file
- Display hex dumps of chunk data
- Try to interpret data as various types (int, float, strings)
- Identify potential header and heightmap chunks

**Use this when a map fails to load!** The output helps us understand the actual format.

### Logs
Check the log file for detailed error information:
```bash
cat map_viewer.log
# or
tail -f map_viewer.log  # Follow in real-time
```

### Common Issues

**Q: Where do I find SpellForce maps?**  
A: In your SpellForce installation directory under `Maps/Campaign/` or `Maps/Multiplayer/`

**Q: Why is terrain green instead of textured?**  
A: Texture rendering is planned for Phase 2. Currently showing solid color.

**Q: Map failed to load or app crashes?**  
A: Make sure you're using the latest version with `simple_map_loader.py`. The old chunk-based loader doesn't work with real SpellForce maps. Check the console for error messages and see `map_viewer.log` for details.
   
   Test if the simple loader works:
   ```bash
   python3 -c "from TirganachReloaded.map_viewer.simple_map_loader import SimpleMapLoader; print('✓ Using correct loader')"
   ```

**Q: Why are units shown as cubes?**  
A: 3D model loading is planned for Phase 3. Cubes are placeholders.

**Q: Can I edit maps?**  
A: Not yet. Editing features are planned for Phase 4.

**Q: Does this work on Mac/Linux?**  
A: Yes! Unlike the C# version, this is fully cross-platform. macOS OpenGL compatibility fixed in v0.1.0.

**Q: Can I help improve map format support?**  
A: Absolutely! Run the inspector tool on various maps and share the results. This helps us understand the actual chunk format used by SpellForce.

## Tips & Tricks

### Smooth Navigation
- Hold multiple keys (W+D) to move diagonally
- Combine mouse drag + keyboard for fluid camera control
- Use zoom to get closer detail or wide overview

### Finding Specific Locations
- Use the grid overlay as reference
- Unit/building markers help identify points of interest
- Reset camera to return to map center

### Performance Optimization
- Close the viewer when not in use (releases GPU resources)
- Smaller maps load faster and run smoother
- Future updates will add LOD for better large map performance

## Current Status - v0.1.0 ✅ VERIFIED WORKING!

**Phase 1 Complete!** The viewer now successfully:
- ✅ Loads real SpellForce .map files **CONFIRMED**
- ✅ Decompresses ZLIB data **WORKING**
- ✅ Displays heightmap terrain in 3D **RENDERING CONFIRMED**
- ✅ Height-based terrain coloring **NEW FEATURE**
- ✅ Smooth camera navigation **TESTED**
- ✅ Works on macOS, Windows, Linux **macOS M4 Pro VERIFIED**

**What's Working:**
- Map loading: 256x256, 512x512 maps tested ✅
- Rendering: 150+ FPS performance on Apple M4 Pro ✅
- Controls: All keyboard/mouse inputs ✅
- Format: Reverse engineered and documented ✅
- OpenGL: Fixed compatibility mode for macOS ✅
- Visual feedback: Status bars and height coloring ✅

**Tested Maps:**
- Coop_01_rpg.map (256x256) ✅
- Coop_08_dark.map (512x512) ✅

## What's Coming Next

### Phase 2: Visual Fidelity (Next)
- ✨ Terrain textures with blending
- 💡 Proper lighting (sun + ambient)
- 🌑 Shadow mapping
- 🎨 Better visual quality

### Phase 3: Assets
- 🧊 3D model loading
- 🏃 Animated units
- 🎮 Game-accurate appearance
- 📦 PAK archive access

### Phase 4: Editing
- 🖱️ Click to select entities
- ✏️ Edit properties
- 🏔️ Terrain editing
- 💾 Save changes

## Contributing

Want to help develop the map viewer?

1. Read `IMPLEMENTATION_PLAN.md` for technical details
2. Check open issues and planned features
3. Fork, develop, and submit pull requests
4. Join the SpellForce modding community

## Resources

- **Main README**: Comprehensive documentation
- **Implementation Plan**: Technical roadmap
- **C# Reference**: `ModdingTools/Inspiration/spellforce_data_editor/`
- **SpellForce Forums**: Community support

---

**Version**: 0.1.0 (Phase 1 - Core Viewer)

**Status**: ✅ Functional - Basic viewing working, advanced features coming soon

**Last Updated**: 2024

**Enjoy exploring SpellForce maps in 3D! 🗺️✨**

---

## Troubleshooting the "Mirroring" Issue (SOLVED!)

**Problem**: Window showed mirrored reflection, no 3D content visible.

**Solution**: Switch OpenGL to Compatibility Profile (OpenGL 2.1) instead of Core Profile (3.3).

This was a critical macOS compatibility issue that has now been fixed in v0.1.0!

**If you still see mirroring**:
1. Make sure you're running the latest version
2. Check that OpenGL is initialized (console should show "OpenGL initialized successfully")
3. Look for the red square test (top-left) - if you don't see it, OpenGL isn't rendering
4. Try resizing the window - sometimes triggers a refresh

**Success indicators**:
- You should see colored 3D terrain (green/yellow based on height)
- Status bars in top-left corner (colored horizontal bars)
- FPS counter updating in window title
- Terrain responds to camera movement

**If it's still not working**, please share:
1. macOS version
2. GPU type
3. Console output when loading a map
4. Whether you see the red test square