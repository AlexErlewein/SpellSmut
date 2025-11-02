#!/usr/bin/env python3
"""
Quick test of Simple Quest Viewer GUI
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path('.') / 'src'))

from PySide6.QtWidgets import QApplication
from TirganachReloaded.cff_editor.simple_quest_viewer import SimpleQuestViewer

def main():
    app = QApplication(sys.argv)
    viewer = SimpleQuestViewer()
    viewer.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())