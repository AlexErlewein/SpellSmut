#!/usr/bin/env python3
"""
Test script to verify T key texture toggle in map viewer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

from src.TirganachReloaded.map_viewer.map_viewer_window import MapViewerWindow

def test_t_key_functionality():
    """Test T key texture toggle functionality"""
    print("=== Testing T Key Texture Toggle ===")
    
    app = QApplication(sys.argv)
    window = MapViewerWindow()
    
    # Show window (but don't exec the app)
    window.show()
    
    # Allow window to initialize
    QApplication.processEvents()
    
    # Check initial state
    initial_state = window.viewer.use_textures
    print(f"Initial texture state: {'ON' if initial_state else 'OFF'}")
    
    # Test texture checkbox
    window.texture_checkbox.setChecked(True)
    texture_on_state = window.viewer.use_textures
    print(f"After checkbox ON: {'ON' if texture_on_state else 'OFF'}")
    
    window.texture_checkbox.setChecked(False)
    texture_off_state = window.viewer.use_textures
    print(f"After checkbox OFF: {'ON' if texture_off_state else 'OFF'}")
    
    # Test T key simulation
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtCore import QEvent
    
    # Simulate T key press
    key_event = QKeyEvent(QEvent.KeyPress, Qt.Key.Key_T, Qt.KeyboardModifier.NoModifier)
    app.postEvent(window, key_event)
    QApplication.processEvents()
    
    t_key_state1 = window.viewer.use_textures
    print(f"After first T key: {'ON' if t_key_state1 else 'OFF'}")
    
    # Simulate T key press again
    key_event2 = QKeyEvent(QEvent.KeyPress, Qt.Key.Key_T, Qt.KeyboardModifier.NoModifier)
    app.postEvent(window, key_event2)
    QApplication.processEvents()
    
    t_key_state2 = window.viewer.use_textures
    print(f"After second T key: {'ON' if t_key_state2 else 'OFF'}")
    
    # Check texture preview panel
    preview_text = window.texture_preview_label.text()
    print(f"Texture preview text: {preview_text}")
    
    # Test texture loading status
    textures_loaded = len(window.viewer.base_textures) if window.viewer.base_textures else 0
    print(f"Textures loaded in viewer: {textures_loaded}")
    
    # Check texture manager status
    if window.viewer.texture_manager:
        texture_files_found = len(window.viewer.texture_manager.texture_files)
        print(f"Texture files found by manager: {texture_files_found}")
    else:
        print("Texture manager not initialized")
    
    window.close()
    
    # Verify functionality
    success = (
        not initial_state and  # Should start OFF
        texture_on_state and  # Checkbox should turn ON
        not texture_off_state and  # Checkbox should turn OFF
        t_key_state1 and  # T key should turn ON
        not t_key_state2  # T key should turn OFF
    )
    
    return success

if __name__ == "__main__":
    print("Testing T Key Texture Toggle Functionality")
    print("=" * 50)
    
    try:
        success = test_t_key_functionality()
        
        print("\n=== Test Results ===")
        if success:
            print("🎉 T key texture toggle: ✅ PASS")
            print("✅ All texture toggle functionality working correctly!")
            sys.exit(0)
        else:
            print("❌ T key texture toggle: ❌ FAIL")
            print("❌ Some functionality is not working correctly.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)