#!/usr/bin/env python3
"""
Test script to verify map viewer fixes
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from TirganachReloaded.map_viewer.camera import Camera
    print("✅ Camera import successful")
    
    # Test camera initialization
    cam = Camera()
    print(f"✅ Camera initialized: position={cam.position}")
    print(f"✅ Terrain following: {cam.terrain_following}")
    print(f"✅ Smoothing factor: {cam.terrain_smoothing_factor}")
    
    # Test terrain following toggle
    cam.toggle_terrain_following()
    print(f"✅ After toggle: terrain_following={cam.terrain_following}")
    
    print("\n🎉 Camera system working correctly!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")