#!/usr/bin/env python3
"""
Liannon Quest Viewer - Launcher Script
======================================

Convenience launcher for the Liannon Quest Viewer application.

Usage:
    python run_viewer.py [--debug] [--rebuild-cache]

Features:
    - Browse all SpellForce quests
    - Search by ID, name, or description
    - Filter by platform/location and quest giver
    - Export quests to JSON or Markdown
    - View detailed quest information
    - Dark theme interface

Location:
    This launcher is in: src/LiannonQuestViewer/
    Main application: ./simple_quest_viewer.py
    Uses cache from: src/TirganachReloaded/data/cache/
"""

import sys
from pathlib import Path

# Get the directory where this script is located
viewer_dir = Path(__file__).parent

# Add the main script directory to path
sys.path.insert(0, str(viewer_dir))

# Import and run the viewer
if __name__ == "__main__":
    import simple_quest_viewer

    sys.exit(simple_quest_viewer.main())
