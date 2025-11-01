#!/usr/bin/env python3
"""
Debug script to test GUI startup
"""

import sys
from pathlib import Path

# Add src directory to Python path
script_dir = Path(__file__).parent
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

print("Starting GUI debug test...")

try:
    print("1. Testing basic imports...")
    from TirganachReloaded.cff_editor.logging_config import configure_logging
    print("   ✓ Logging config imported")
    
    print("2. Configuring logging...")
    configure_logging(debug_mode=True, project_root=script_dir)
    print("   ✓ Logging configured")
    
    print("3. Importing main window...")
    from TirganachReloaded.cff_editor.main_window import MainWindow
    print("   ✓ MainWindow imported")
    
    print("4. Creating QApplication...")
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    print("   ✓ QApplication created")
    
    print("5. Creating MainWindow...")
    window = MainWindow()
    print("   ✓ MainWindow created successfully")
    
    print("6. Testing window show...")
    window.show()
    print("   ✓ Window shown successfully")
    
    print("\n✓ GUI startup test completed successfully!")
    print("The application should be visible now.")
    
    # Run the event loop briefly to test
    app.processEvents()
    
except Exception as e:
    import traceback
    print(f"\n✗ Error during GUI startup: {e}")
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1)
