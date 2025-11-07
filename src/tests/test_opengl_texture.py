#!/usr/bin/env python3
"""
Debug script to check OpenGL texture rendering
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Try to import OpenGL
    from OpenGL.GL import *
    from OpenGL.GLU import *
    print("✅ OpenGL imports successful")
    
    # Check if we can create a simple texture
    texture_id = glGenTextures(1)
    print(f"✅ Generated texture ID: {texture_id}")
    
    # Create a simple test texture (2x2 red pixels)
    import numpy as np
    test_texture = np.array([
        [[255, 0, 0, 255], [255, 0, 0, 255]],  # Red row
        [[255, 0, 0, 255], [255, 0, 0, 255]]   # Red row
    ], dtype=np.uint8)
    
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 2, 2, 0, GL_RGBA, GL_UNSIGNED_BYTE, test_texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    
    print("✅ Created test texture successfully")
    
    # Check for OpenGL errors
    error = glGetError()
    if error != GL_NO_ERROR:
        print(f"❌ OpenGL error: {error}")
    else:
        print("✅ No OpenGL errors")
    
    print("\n🎉 OpenGL texture test completed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()