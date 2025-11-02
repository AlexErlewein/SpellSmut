# Quick Start Guide - SpellForce Map Viewer

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
- **W** or **↑** - Move forward
- **S** or **↓** - Move backward  
- **A** or **←** - Move left
- **D** or **→** - Move right

### Camera Rotation
- **Middle Mouse + Drag** - Free look (rotate camera)
- **Home** - Rotate left
- **End** - Rotate right
- **Page Up** - Tilt camera up
- **Page Down** - Tilt camera down

### Zoom
- **Mouse Wheel** - Zoom in/out
- **Insert** - Zoom in (alternative)
- **Delete** - Zoom out (alternative)

### UI
- **Open Map** - Load a map file
- **Reset Camera** - Return to center of map

## What You'll See

- **Green Terrain** - The heightmap (elevation data)
- **Gray Grid** - Positioning reference lines (every 10 units)
- **Blue Cubes** - Unit placements
- **Brown Cubes** - Building placements
- **RGB Axes** - Coordinate system (Red=X, Green=Y, Blue=Z)

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

### Map doesn't load
- Verify it's a valid `.map` file
- Check console output for error messages
- See `map_viewer.log` for detailed logs

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

**Q: Why are units shown as cubes?**  
A: 3D model loading is planned for Phase 3. Cubes are placeholders.

**Q: Can I edit maps?**  
A: Not yet. Editing features are planned for Phase 4.

**Q: Does this work on Mac/Linux?**  
A: Yes! Unlike the C# version, this is fully cross-platform.

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

## What's Coming Next

### Phase 2: Visual Fidelity
- ✨ Terrain textures with blending
- 💡 Proper lighting (sun + ambient)
- 🌑 Shadow mapping
- 🎨 Better visual quality

### Phase 3: Assets
- 🧊 3D model loading
- 🏃 Animated units
- 🎮 Game-accurate appearance

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