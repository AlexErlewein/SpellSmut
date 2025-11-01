#!/usr/bin/env python3
"""
TirganachReloaded launcher script
"""

import sys
from pathlib import Path

# Add src directory to Python path for imports
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))


def main():
    # Add project root to Python path (since src/ is in root)
    src_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(src_dir))

    # Import and run the main function
    from TirganachReloaded.cff_editor.main import main as app_main

    # Pass command line arguments to the main function
    app_main()


if __name__ == "__main__":
    main()
