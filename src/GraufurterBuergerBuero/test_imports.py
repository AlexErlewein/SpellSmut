#!/usr/bin/env python3
"""Quick test to verify the app loads correctly"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
print("Testing imports...")
try:
    from npc_loader import load_all_npcs, save_npc, delete_npc
    print("✓ npc_loader imports OK")
except Exception as e:
    print(f"✗ npc_loader import failed: {e}")
    sys.exit(1)

try:
    from npc_creation_data import NpcCreationData
    print("✓ npc_creation_data imports OK")
except Exception as e:
    print(f"✗ npc_creation_data import failed: {e}")
    sys.exit(1)

try:
    from id_manager import IDManager, ContentType
    print("✓ id_manager imports OK")
except Exception as e:
    print(f"✗ id_manager import failed: {e}")
    sys.exit(1)

# Test loading NPCs
print("\nTesting NPC loading...")
try:
    npcs = load_all_npcs()
    print(f"✓ Loaded {len(npcs)} NPCs")
except Exception as e:
    print(f"✗ Failed to load NPCs: {e}")
    sys.exit(1)

# Test ID manager
print("\nTesting ID manager...")
try:
    id_mgr = IDManager()
    test_id = id_mgr.allocate_id(ContentType.NPC)
    print(f"✓ Allocated test NPC ID: {test_id}")
    id_mgr.release_id(ContentType.NPC, test_id)
    print(f"✓ Released test NPC ID: {test_id}")
except Exception as e:
    print(f"✗ ID manager failed: {e}")
    sys.exit(1)

print("\n✅ All basic tests passed!")
print("\nTo run the full application:")
print("  uv run graufurter_buerger_buero.py")
