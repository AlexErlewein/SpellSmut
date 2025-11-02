#!/usr/bin/env python3
"""Quick test to see if CFF loads and what's in it"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.tirganach import GameData

cff_file = project_root / "OriginalGameFiles" / "data" / "GameData.cff"

print(f"Loading: {cff_file}")
game_data = GameData(cff_file)

print("\n=== GameData Structure ===")
for attr in sorted(dir(game_data)):
    if not attr.startswith('_'):
        try:
            value = getattr(game_data, attr)
            if not callable(value):
                if hasattr(value, '__len__'):
                    print(f"{attr}: {type(value).__name__} (length: {len(value)})")
                    if attr == 'quests' and len(value) > 0:
                        print(f"  First quest attributes: {[a for a in dir(value[0]) if not a.startswith('_')][:10]}")
                else:
                    print(f"{attr}: {type(value).__name__}")
        except Exception as e:
            print(f"{attr}: Error - {e}")

# Try to find quest 379
if hasattr(game_data, 'quests'):
    print(f"\n=== Searching for Quest 379 ===")
    for i, quest in enumerate(game_data.quests):
        try:
            qid = getattr(quest, 'id', None) or getattr(quest, 'quest_id', None)
            if qid == 379:
                print(f"Found at index {i}!")
                print("Attributes:")
                for attr in sorted(dir(quest)):
                    if not attr.startswith('_'):
                        try:
                            val = getattr(quest, attr)
                            if not callable(val):
                                print(f"  {attr} = {val}")
                        except:
                            pass
                break
        except:
            continue
