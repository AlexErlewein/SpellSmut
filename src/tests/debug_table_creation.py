#!/usr/bin/env python3
"""
Debug Table Creation
====================

Debug script to understand how to properly work with existing tables.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def debug_table_creation():
    """Debug table creation approach"""
    try:
        from TirganachReloaded.cff_editor.data_model import CFFDataModel
        from TirganachReloaded.tirganach.entities import Localisation, Language

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

        print(f"\nGame data type: {type(data_model.game_data)}")
        print(f"Game data tables: {data_model.game_data.tables()}")

        # Try to access localisation table directly as attribute
        print(f"\nDirect attribute access:")
        print(f"  - game_data.localisation: {getattr(data_model.game_data, 'localisation', 'NOT FOUND')}")
        print(f"  - Type: {type(getattr(data_model.game_data, 'localisation', None))}")

        # Try get_table method
        print(f"\nget_table method:")
        localisation_table = data_model.game_data.get_table(Localisation)
        print(f"  - get_table(Localisation): {localisation_table}")
        print(f"  - Type: {type(localisation_table)}")

        # Try different approaches
        print(f"\nTrying different approaches:")

        # Approach 1: Access as attribute
        loc_attr = data_model.game_data.localisation
        print(f"  - Attribute access: {loc_attr} (type: {type(loc_attr)})")

        if loc_attr is not None:
            print(f"  - Can append: {hasattr(loc_attr, 'append')}")
            print(f"  - Length: {len(loc_attr)}")

            # Try to create a test entry
            try:
                test_entry = Localisation()
                test_entry.text_id = 50001
                test_entry.language = Language.GERMAN
                test_entry.text = "Test Quest Name"

                loc_attr.append(test_entry)
                print(f"  - Successfully added test entry, new length: {len(loc_attr)}")
                print(f"  - First entry: {loc_attr[0]}")

            except Exception as e:
                print(f"  - Failed to add entry: {e}")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_table_creation()