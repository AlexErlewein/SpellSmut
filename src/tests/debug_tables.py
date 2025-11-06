#!/usr/bin/env python3
"""
Debug Table Access
==================

Debug script to see what get_table returns for empty tables.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def debug_tables():
    """Debug table access"""
    try:
        from TirganachReloaded.cff_editor.data_model import CFFDataModel

        # Initialize data model
        data_model = CFFDataModel()

        # Load game data
        data_path = Path("OriginalGameFiles/data/GameData.cff")
        print(f"Loading game data from: {data_path}")
        if data_model.load_file(str(data_path)):
            print("✓ Successfully loaded game data")
        else:
            print("✗ Failed to load game data")
            return False

        # Test table access
        tables_to_test = ['localisation', 'advanced_descriptions', 'quests']

        for table_name in tables_to_test:
            print(f"\nTesting table: {table_name}")
            table = data_model.game_data.get_table(table_name)
            print(f"  - Type: {type(table)}")
            print(f"  - Value: {table}")
            print(f"  - Is None: {table is None}")
            print(f"  - Length: {len(table) if table else 'N/A'}")
            print(f"  - Truthiness: {bool(table)}")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_tables()