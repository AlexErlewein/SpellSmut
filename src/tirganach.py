#!/usr/bin/env python3
"""
TirganachReloaded launcher script
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run the main function
from TirganachReloaded.cff_editor.main import main

if __name__ == "__main__":
    main()
