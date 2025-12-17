#!/usr/bin/env python3
"""
Mulandirs Zauberschule - Launcher Script
========================================

Convenience launcher for the Mulandirs Zauberschule application.

Usage:
    python run_mulandirs_zauberschule.py

Features:
    - Browse all SpellForce spells
    - Search and filter spells by name, school, or type
    - View detailed level progression data
    - Create custom spells using the Spell Forge
    - Export spells for use in the game
    - Dark theme interface

Location:
    This launcher is in: src/MulandirsZauberschule/
    Main application: ./spell_browser_launcher.py
"""

import sys
from pathlib import Path

# Get the directory where this script is located
app_dir = Path(__file__).parent

# Add the main script directory to path
sys.path.insert(0, str(app_dir))

# Import and run the application
if __name__ == "__main__":
    import spell_browser_launcher

    sys.exit(spell_browser_launcher.main())
