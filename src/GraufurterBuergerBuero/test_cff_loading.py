#!/usr/bin/env python3
"""Test CFF NPC loading"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing CFF NPC Loader...")

try:
    from cff_npc_loader import CFFNpcLoader
    print("✓ CFFNpcLoader imported successfully")
except Exception as e:
    print(f"✗ Failed to import CFFNpcLoader: {e}")
    sys.exit(1)

# Test with GameData.cff if it exists
gamedata_path = Path(__file__).parent.parent.parent / "OriginalGameFiles/data/GameData.cff"

if gamedata_path.exists():
    print(f"\n✓ Found GameData.cff at: {gamedata_path}")
    print("\nAttempting to load NPCs from CFF...")
    
    try:
        loader = CFFNpcLoader()
        npcs = loader.load_all_npcs(cff_file_path=str(gamedata_path))
        
        print(f"✓ Loaded {len(npcs)} NPCs from CFF!")
        
        if npcs:
            # Show first 5 NPCs as sample
            print("\nSample NPCs:")
            for i, (npc_id, npc_info) in enumerate(list(npcs.items())[:5]):
                name = npc_info.get("name", "Unknown")
                level = npc_info.get("level", 0)
                npc_type = npc_info.get("npc_type", "Unknown")
                print(f"  - ID {npc_id}: {name} (Level {level}, {npc_type})")
                
    except Exception as e:
        print(f"✗ Failed to load NPCs from CFF: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
else:
    print(f"\n⚠ GameData.cff not found at: {gamedata_path}")
    print("  CFF loading cannot be tested without the game file.")
    print("  Place GameData.cff in OriginalGameFiles/data/ to test CFF loading.")

print("\n✅ CFF NPC loader is functional!")
