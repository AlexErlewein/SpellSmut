#!/usr/bin/env python3
"""
Simple Quest Viewer Launcher
============================

Simple launcher for the standalone simple quest viewer application.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.simple_quest_viewer import main

if __name__ == "__main__":
    sys.exit(main())