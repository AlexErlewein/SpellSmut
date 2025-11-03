#!/usr/bin/env python3
"""
Quick test to check texture samples functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from TirganachReloaded.map_viewer.map_viewer_window import MapViewerWindow

def quick_test():
    """Quick test of texture samples"""
    app = QApplication(sys.argv)
    
    # Create window
    window = MapViewerWindow()
    window.show()
    
    # Initialize textures after window is shown
    QTimer.singleShot(1000, lambda: window.viewer._init_texture_manager())
    
    # Update texture preview after textures are loaded
    QTimer.singleShot(2000, lambda: window.viewer._update_texture_preview())
    
    # Update texture samples after preview is updated
    QTimer.singleShot(2500, lambda: window.update_texture_samples())
    
    # Exit after 3 seconds
    QTimer.singleShot(3000, app.quit)
    
    print("Test running... Check for texture samples in the left panel")
    sys.exit(app.exec())

if __name__ == "__main__":
    quick_test()