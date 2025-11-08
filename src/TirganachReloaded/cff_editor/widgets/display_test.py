#!/usr/bin/env python3
"""
Display Test - Check what display server we're using
"""

import sys
import os
import subprocess
from pathlib import Path

print("=== Display Environment Test ===")
print(f"Platform: {sys.platform}")
print(f"Python: {sys.version}")

# Check display environment
display_vars = ['DISPLAY', 'WAYLAND_DISPLAY', 'QT_QPA_PLATFORM']
for var in display_vars:
    if var in os.environ:
        print(f"{var}: {os.environ[var]}")

# Check macOS display
if sys.platform == 'darwin':
    try:
        result = subprocess.run(['echo', $DISPLAY], shell=True, capture_output=True, text=True)
        if result.stdout:
            print(f"DISPLAY (macOS): {result.stdout.strip()}")
    except:
        pass
    
    # Check if we're in SSH session
    if 'SSH_CLIENT' in os.environ or 'SSH_CONNECTION' in os.environ:
        print("⚠️ Running in SSH session - GUI may not work")
    
    # Check if we're in tmux/screen
    if 'TMUX' in os.environ or 'STY' in os.environ:
        print("⚠️ Running in tmux/screen - GUI may not work")

# Test basic PySide6 without Qt app
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    
    print("\n=== PySide6 Test ===")
    print("Creating QApplication...")
    app = QApplication([])
    
    print(f"Available platforms: {', '.join(app.platforms())}")
    print(f"Platform name: {app.platformName()}")
    
    # Check display capabilities
    print(f"Desktop is available: {QApplication.desktop() is not None}")
    
    print("✓ Basic PySide6 test passed")
    
except Exception as e:
    print(f"✗ PySide6 test failed: {e}")

# Test window creation
print("\n=== Simple Window Test ===")
try:
    from PySide6.QtWidgets import QLabel, QWidget
    from PySide6.QtGui import QFont
    from PySide6.QtCore import QTimer
    
    # Create simple window
    app = QApplication([])
    widget = QWidget()
    widget.setWindowTitle("Display Test")
    widget.resize(300, 200)
    
    label = QLabel("If you see this, GUI works! 🎉")
    label.setFont(QFont("Arial", 14))
    label.setAlignment(Qt.AlignCenter)
    
    layout = QVBoxLayout(widget)
    layout.addWidget(label)
    
    # Show widget
    widget.show()
    
    # Auto-close after 3 seconds
    QTimer.singleShot(3000, app.quit)
    
    print("Window shown - should be visible for 3 seconds...")
    
    # Run
    app.exec()
    print("Window test completed")
    
except Exception as e:
    print(f"✗ Window test failed: {e}")

print("\n=== Recommendations ===")
print("If no GUI appeared:")
print("1. Make sure you're not in SSH/tmux/screen session")
print("2. Try running with: python script.py")
print("3. Check display server is running")