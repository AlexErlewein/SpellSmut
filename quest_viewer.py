#!/usr/bin/env python3
"""
Quest Viewer Launcher
======================

Simple launcher for the standalone quest viewer application.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.quest_viewer_app import main

if __name__ == "__main__":
    sys.exit(main())