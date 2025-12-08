#!/usr/bin/env python3
"""
Launcher script for Graufurter Bürger Büro (NPC Creation Suite)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from graufurter_buerger_buero import main

if __name__ == "__main__":
    main()
