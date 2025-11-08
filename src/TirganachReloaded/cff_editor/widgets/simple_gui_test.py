#!/usr/bin/env python3
"""
Simple GUI Test - Just Get Window Working

This bypasses all data loading to test if the GUI window will appear.
"""

import sys
from pathlib import Path

# Add src directory to Python path
script_path = Path(__file__).resolve()
widgets_dir = script_path.parent
src_dir = widgets_dir.parent.parent.parent  # widgets -> cff_editor -> TirganachReloaded -> src
sys.path.insert(0, str(src_dir))

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QWidget,
        QPushButton, QLabel, QMessageBox
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
except ImportError as e:
    print(f"Error: PySide6 not found: {e}")
    print("Please install PySide6: pip install PySide6")
    sys.exit(1)

class SimpleTestWindow(QMainWindow):
    """Simple test window to verify GUI works"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple GUI Test")
        self.setMinimumSize(400, 300)
        
        print("DEBUG: Creating simple test window...")
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title_label = QLabel("GUI Test Window")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Test button
        test_btn = QPushButton("Test Button")
        test_btn.setStyleSheet(
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
        test_btn.clicked.connect(self.on_test_click)
        layout.addWidget(test_btn)
        
        # Status
        status_label = QLabel("GUI is working! ✅")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("color: #27ae60; font-size: 16px; margin-top: 20px;")
        layout.addWidget(status_label)
        
        layout.addStretch()
        
        print("DEBUG: Simple test window setup completed")
    
    def on_test_click(self):
        """Handle test button click"""
        QMessageBox.information(
            self, 
            "Test Success!", 
            "The GUI is working perfectly! 🎉\n\n"
            "Your PySide6 installation is fine.\n"
            "The issue must be in the data loading code."
        )
        self.statusBar().showMessage("Test button clicked!")


def main():
    """Main test function"""
    print("Starting simple GUI test...")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Simple GUI Test")
    
    # Create and show test window
    window = SimpleTestWindow()
    window.show()
    
    # Force window to front
    window.raise_()
    window.activateWindow()
    
    print("Simple test window shown - should be visible now!")
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)