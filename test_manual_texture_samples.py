#!/usr/bin/env python3
"""
Test script to manually trigger texture loading and sample display
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from TirganachReloaded.map_viewer.map_viewer_window import MapViewerWindow

def test_texture_samples_manual():
    """Manually test texture samples by triggering texture loading"""
    app = QApplication(sys.argv)
    
    # Create window
    window = MapViewerWindow()
    window.show()
    
    # Manually trigger texture manager initialization (this normally happens when opening a map)
    print("Manually initializing texture manager...")
    window.viewer._init_texture_manager()
    
    # Force texture preview update
    print("Updating texture preview...")
    window.viewer._update_texture_preview()
    
    print("Window should now show texture samples in the left panel")
    print("Close the window to exit...")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_texture_samples_manual()