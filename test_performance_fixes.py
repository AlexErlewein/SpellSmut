#!/usr/bin/env python3
"""
Test script for performance and texture fixes
"""

import sys
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent, QKeyEvent
from PySide6.QtCore import Qt
from unittest.mock import Mock

# Add src to path
sys.path.append('src')

# Initialize Qt application
app = QApplication(sys.argv if sys.argv else ['test'])

from TirganachReloaded.map_viewer.map_viewer_window import MapViewerWidget
from TirganachReloaded.map_viewer.camera import Camera

def test_texture_enabled_by_default():
    """Test that textures are enabled by default"""
    print("Testing texture default state...")
    
    widget = MapViewerWidget()
    assert widget.use_textures == True, f"Textures should be enabled by default, got {widget.use_textures}"
    print("✓ Textures are enabled by default")

def test_single_update_call():
    """Test that only one update() call happens per frame"""
    print("Testing single update optimization...")
    
    widget = MapViewerWidget()
    widget.gl_initialized = True
    widget.camera = Camera()
    
    # Mock the update method to count calls
    update_count = 0
    original_update = widget.update
    def mock_update():
        nonlocal update_count
        update_count += 1
    
    widget.update = mock_update
    
    # Simulate multiple inputs in one frame
    w_key = Mock(spec=QKeyEvent)
    w_key.key.return_value = Qt.Key.Key_W
    q_key = Mock(spec=QKeyEvent)
    q_key.key.return_value = Qt.Key.Key_Q
    
    widget.keyPressEvent(w_key)
    widget.keyPressEvent(q_key)
    
    # Simulate frame update
    widget.update_frame()
    
    # Should only call update once
    assert update_count == 1, f"Expected 1 update call, got {update_count}"
    print(f"✓ Single update call per frame: {update_count}")
    
    # Restore original method
    widget.update = original_update

def test_terrain_smoothing_performance():
    """Test that terrain smoothing doesn't impact performance"""
    print("Testing terrain smoothing performance...")
    
    camera = Camera()
    camera.terrain_following = True
    
    # Time multiple elevation updates
    start_time = time.time()
    for i in range(1000):
        camera.set_elevation(100.0, 50.0 + i * 0.1)
    end_time = time.time()
    
    elapsed = end_time - start_time
    assert elapsed < 0.1, f"Terrain smoothing too slow: {elapsed:.3f}s for 1000 updates"
    print(f"✓ Terrain smoothing performance: {elapsed:.3f}s for 1000 updates")

def test_camera_mode_performance():
    """Test camera mode switching performance"""
    print("Testing camera mode performance...")
    
    camera = Camera()
    
    # Time multiple mode toggles
    start_time = time.time()
    for i in range(100):
        result = camera.toggle_terrain_following()
        assert isinstance(result, bool), f"Toggle should return bool, got {type(result)}"
    end_time = time.time()
    
    elapsed = end_time - start_time
    assert elapsed < 0.01, f"Camera mode toggle too slow: {elapsed:.3f}s for 100 toggles"
    print(f"✓ Camera mode toggle performance: {elapsed:.3f}s for 100 toggles")

def test_movement_speed():
    """Test that movement speed is properly increased"""
    print("Testing movement speed...")
    
    camera = Camera()
    assert camera.movement_speed == 120.0, f"Expected 120.0 units/sec, got {camera.movement_speed}"
    print(f"✓ Movement speed: {camera.movement_speed} units/second")

def main():
    """Run all performance and texture tests"""
    print("=== Testing Performance & Texture Fixes ===\n")
    
    try:
        test_texture_enabled_by_default()
        test_single_update_call()
        test_terrain_smoothing_performance()
        test_camera_mode_performance()
        test_movement_speed()
        
        print("\n🎉 All performance and texture tests passed!")
        print("\nFixes Applied:")
        print("- ✅ Textures enabled by default (was False)")
        print("- ✅ Single update() call per frame (was multiple)")
        print("- ✅ Terrain smoothing optimized for performance")
        print("- ✅ Camera mode toggle is fast")
        print("- ✅ Movement speed increased to 120 units/second")
        
        print("\nExpected Results:")
        print("- FPS should return to 60+ (from 4.5)")
        print("- Textures should be visible by default")
        print("- Smooth camera movement without bumpiness")
        print("- F key toggles terrain following/fixed altitude")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())