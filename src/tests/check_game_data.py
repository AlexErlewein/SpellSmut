#!/usr/bin/env python3
"""
Check Game Data Tables
======================

Simple script to check what tables are available in the loaded game data.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def check_game_data():
    """Check what tables are available in game data"""
    try:
        from TirganachReloaded.cff_editor.data_model import CFFDataModel

        # Initialize data model
        data_model = CFFDataModel()

        # Load game data
        data_path = Path("OriginalGameFiles/data/GameData.cff")
        if not data_path.exists():
            print(f"Game data not found at: {data_path}")
            return False

        print(f"Loading game data from: {data_path}")
        if data_model.load_file(str(data_path)):
            print("✓ Successfully loaded game data")
        else:
            print("✗ Failed to load game data")
            return False

        if data_model.game_data:
            print(f"\nGame data loaded successfully!")
            tables = data_model.game_data.tables()
            print(f"Number of tables: {len(tables)}")
            print("\nAvailable tables:")
            for table_name in tables:
                table = data_model.game_data.get_table(table_name)
                if table:
                    print(f"  - {table_name}: {len(table)} entries")
                else:
                    print(f"  - {table_name}: (empty)")
        else:
            print("No game data available")
            return False

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_game_data()