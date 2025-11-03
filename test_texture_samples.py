#!/usr/bin/env python3
"""
Test script to verify texture sample viewer functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from TirganachReloaded.map_viewer.simple_texture_manager import SimpleTextureManager

def test_texture_samples():
    """Test texture sample viewer functionality"""
    app = QApplication(sys.argv)
    
    # Create texture manager
    texture_manager = SimpleTextureManager()
    texture_manager.load_available_textures("ExtractedAssets")
    
    # Create a simple window to test texture samples
    window = QMainWindow()
    window.setWindowTitle("Texture Samples Test")
    window.setGeometry(100, 100, 400, 600)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add title
    title = QLabel("Texture Samples Test")
    title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
    layout.addWidget(title)
    
    # Add info
    info = QLabel(f"Found {len(texture_manager.texture_files)} texture files")
    layout.addWidget(info)
    
    # Try to load a few textures
    from PySide6.QtGui import QPixmap, QImage
    from PySide6.QtCore import Qt
    
    samples_shown = 0
    max_samples = 12
    
    for texture_id, texture_path in list(texture_manager.texture_files.items())[:max_samples]:
        try:
            # Load texture
            texture_data = texture_manager.get_texture(texture_id)
            if texture_data is not None:
                height, width = texture_data.shape[:2]
                
                # Create QImage from numpy array
                if len(texture_data.shape) == 3:
                    q_image = QImage(texture_data.tobytes(), width, height, QImage.Format.Format_RGBA8888)
                else:
                    q_image = QImage(texture_data.tobytes(), width, height, QImage.Format.Format_Grayscale8)
                
                # Scale to thumbnail
                thumbnail = q_image.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                
                # Create label
                thumbnail_label = QLabel()
                thumbnail_label.setPixmap(QPixmap.fromImage(thumbnail))
                thumbnail_label.setStyleSheet("""
                    QLabel {
                        border: 1px solid #555;
                        border-radius: 4px;
                        padding: 2px;
                        background-color: #333;
                    }
                """)
                thumbnail_label.setToolTip(f"Texture ID: {texture_id}\nSize: {width}x{height}")
                
                layout.addWidget(thumbnail_label)
                samples_shown += 1
                
                print(f"✓ Created thumbnail for texture {texture_id} ({width}x{height})")
            else:
                print(f"✗ Failed to load texture {texture_id}")
                
        except Exception as e:
            print(f"✗ Error creating thumbnail for texture {texture_id}: {e}")
    
    # Add summary
    summary = QLabel(f"Showing {samples_shown} texture samples")
    summary.setStyleSheet("color: #666; font-style: italic; margin: 10px;")
    layout.addWidget(summary)
    
    window.show()
    print(f"Test window launched with {samples_shown} texture samples")
    print("Close the window to exit...")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_texture_samples()