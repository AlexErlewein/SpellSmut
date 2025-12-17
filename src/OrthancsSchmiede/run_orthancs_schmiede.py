#!/usr/bin/env python3
"""
Orthancs Schmiede - Launcher Script
===================================

Convenience launcher for the Orthancs Schmiede application.

Usage:
    python run_orthancs_schmiede.py [--debug]

Features:
    - Browse all SpellForce weapons and armor
    - Search by ID, name, or properties
    - Filter by category and type
    - View detailed item information
    - Dark theme interface

Location:
    This launcher is in: src/OrthancsSchmiede/
    Main application: ./orthancs_schmiede.py
"""

import sys
from pathlib import Path

# Get the directory where this script is located
app_dir = Path(__file__).parent

# Add the main script directory to path
sys.path.insert(0, str(app_dir))

# Import and run the application
if __name__ == "__main__":
    import orthancs_schmiede

    sys.exit(orthancs_schmiede.main())
