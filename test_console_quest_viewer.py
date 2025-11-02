#!/usr/bin/env python3
"""
Test Simple Quest Viewer with Console Output
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path('.') / 'src'))

from PySide6.QtWidgets import QApplication
from TirganachReloaded.cff_editor.simple_quest_viewer import SimpleQuestViewer

def main():
    print("Starting Simple Quest Viewer...")
    
    app = QApplication(sys.argv)
    
    # Create viewer instance
    viewer = SimpleQuestViewer()
    
    print(f"Viewer created successfully")
    print(f"Quest data loaded: {len(viewer.quest_data)} quests")
    
    if viewer.quest_data:
        sample_ids = sorted(viewer.quest_data.keys())[:5]
        print(f"Sample quest IDs: {sample_ids}")
        for qid in sample_ids:
            qinfo = viewer.quest_data[qid]
            print(f"  - Quest {qid}: {qinfo['name']}")
    else:
        print("❌ No quest data loaded!")
    
    print("Showing viewer window...")
    viewer.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())