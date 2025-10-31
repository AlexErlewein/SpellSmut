#!/usr/bin/env python3
"""
Test QPixmap loading with icon files
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap
from TirganachReloaded.cff_editor.data_model import CFFDataModel


def main():
    """Test pixmap loading"""
    app = QApplication(sys.argv)
    
    # Create data model
    data_model = CFFDataModel()
    
    # Test loading a few icons
    icons = data_model.icon_index.get('icons', {})
    test_keys = list(icons.keys())[:3]
    
    for key in test_keys:
        icon_info = icons[key]
        icon_path = data_model.icons_root / icon_info['path']
        
        print(f"Testing: {key}")
        print(f"  Path: {icon_path}")
        print(f"  Exists: {icon_path.exists()}")
        
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            print(f"  Pixmap loaded: {not pixmap.isNull()}")
            if not pixmap.isNull():
                print(f"  Size: {pixmap.width()}x{pixmap.height()}")
                
                # Test scaling
                scaled = pixmap.scaled(32, 32)
                print(f"  Scaled: {scaled.width()}x{scaled.height()}")
            else:
                print(f"  Failed to load pixmap")
        print()


if __name__ == "__main__":
    main()