#!/usr/bin/env python3
"""
Clean PySide6 Test for macOS

Fixed imports and syntax for proper GUI testing.
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to Python path
script_path = Path(__file__).resolve()
widgets_dir = script_path.parent
src_dir = widgets_dir.parent.parent.parent
project_root = src_dir.parent

sys.path.insert(0, str(src_dir))

print(f"Platform: {sys.platform}")
print(f"Script path: {script_path}")
print(f"Project root: {project_root}")

# Import PySide6 properly
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, 
        QLabel, QPushButton, QMessageBox
    )
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QFont
    print("✓ PySide6 imports successful")
except ImportError as e:
    print(f"✗ PySide6 import failed: {e}")
    sys.exit(1)


class CleanTestWindow(QMainWindow):
    """Clean test window for macOS"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clean PySide6 Test")
        self.setGeometry(200, 200, 400, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("PySide6 GUI Test")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        layout.addWidget(title)
        
        # Status
        status = QLabel("✅ GUI is working!\n✅ Window visible!\n✅ Click button below:")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("color: #27ae60; font-size: 14px; margin: 10px;")
        layout.addWidget(status)
        
        # Test button
        btn = QPushButton("Test PySide6")
        btn.setStyleSheet(
            "QPushButton {"
            "   background-color: #3498db;"
            "   color: white;"
            "   padding: 12px 25px;"
            "   border-radius: 6px;"
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
        """Handle button click"""
        QMessageBox.information(
            self, 
            "Success!", 
            "🎉 PySide6 is working perfectly on macOS!\n\n"
            "Your GUI environment is ready for the enhanced\n"
            "quest creation system."
        )


def main():
    """Main function"""
    print("Starting clean PySide6 test...")
    
    # Create app
    app = QApplication(sys.argv)
    app.setApplicationName("Clean PySide6 Test")
    
    # Create window
    print("Creating test window...")
    window = CleanTestWindow()
    
    # Show window
    print("Showing window...")
    window.show()
    
    # macOS specific activation
    if sys.platform == 'darwin':
        window.raise_()
        window.activateWindow()
    
    print("Window should be visible now!")
    
    # Run app
    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)