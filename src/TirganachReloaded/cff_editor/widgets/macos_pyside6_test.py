#!/usr/bin/env python3
"""
PySide6 macOS Fixed Launcher

Proper PySide6 setup for macOS to ensure GUI windows display.
"""

import sys
import os
import argparse
from pathlib import Path

# Fix macOS display issues
if sys.platform == 'darwin':
    os.environ['QT_MAC_WANTS_LAYER'] = '1'

# Add src directory to Python path
script_path = Path(__file__).resolve()
widgets_dir = script_path.parent
src_dir = widgets_dir.parent.parent.parent
project_root = src_dir.parent

print(f"Platform: {sys.platform}")
print(f"Script path: {script_path}")
print(f"Src dir: {src_dir}")
print(f"Project root: {project_root}")

sys.path.insert(0, str(src_dir))

# Test PySide6 imports first
print("Testing PySide6 imports...")
try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QFont
    print("✓ PySide6 imports successful")
except ImportError as e:
    print(f"✗ PySide6 import failed: {e}")
    print("Please install PySide6: pip install PySide6")
    sys.exit(1)

# Simple test window
class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 macOS Test")
        self.setGeometry(100, 100, 400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("PySide6 Test Window")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        layout.addWidget(title)
        
        # Status
        status = QLabel("PySide6 is working on macOS! ✅")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("color: #27ae60; font-size: 14px; margin: 20px;")
        layout.addWidget(status)
        
        # Test button
        btn = QPushButton("Test Click")
        btn.setStyleSheet(
            "QPushButton {"
            "   background-color: #3498db;"
            "   color: white;"
            "   padding: 10px 20px;"
            "   border-radius: 5px;"
            "   font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #2980b9;"
            "}"
        )
        btn.clicked.connect(self.on_click)
        layout.addWidget(btn)
        
        layout.addStretch()
        
        print("Test window created")
    
    def on_click(self):
        QMessageBox.information(self, "Success!", "PySide6 is working perfectly! 🎉")


def create_app():
    """Create Qt application with proper settings"""
    print("Creating Qt application...")
    
    # Set application attributes for macOS
    app = QApplication(sys.argv)
    app.setApplicationName("PySide6 macOS Test")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Test")
    
    # macOS specific settings
    if sys.platform == 'darwin':
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        print("Set macOS high DPI attributes")
    
    return app


def main():
    """Main function"""
    print("Starting PySide6 macOS test...")
    
    # Parse args
    parser = argparse.ArgumentParser(description="PySide6 macOS Test")
    parser.add_argument("--debug", action="store_true", help="Enable debug")
    args = parser.parse_args()
    
    if args.debug:
        print("Debug mode enabled")
    
    # Create application
    app = create_app()
    
    # Create and show window
    print("Creating test window...")
    window = TestWindow()
    
    print("Showing window...")
    window.show()
    
    # macOS specific window activation
    if sys.platform == 'darwin':
        window.raise_()
        window.activateWindow()
        QTimer.singleShot(100, window.raise_)
        QTimer.singleShot(200, window.activateWindow)
        print("Activated window for macOS")
    
    # Force UI update
    app.processEvents()
    print("Forced UI update")
    
    print("Starting event loop...")
    print("Window should be visible now!")
    
    # Run event loop
    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)