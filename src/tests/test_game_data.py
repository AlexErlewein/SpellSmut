#!/usr/bin/env python3
"""Simple test to check if we can load GameData.cff"""

import sys
import os

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_game_data_access():
    """Test if we can access GameData.cff"""
    print("Testing GameData.cff access...")

    try:
        from TirganachReloaded.tirganach import GameData

        print("✓ Successfully imported TirganachReloaded.tirganach.GameData")

        # Try to load game data
        cff_path = os.path.join(
            os.path.dirname(__file__), "OriginalGameFiles", "data", "GameData.cff"
        )
        gd = GameData(cff_path)
        print("✓ Successfully created GameData instance")

        # Check if we can access weapons
        try:
            weapons = list(gd.weapons)
            print(f"✓ Found {len(weapons)} weapons in GameData.cff")

            # Show first few weapons
            for i, weapon in enumerate(weapons[:3]):
                print(
                    f"  Weapon {i + 1}: ID={weapon.item_id}, Type={weapon.weapon_type}"
                )

            return True

        except Exception as e:
            print(f"✗ Error accessing weapons: {e}")
            return False

    except ImportError as e:
        print(f"✗ Error importing tirganach: {e}")
        return False
    except Exception as e:
        print(f"✗ Error loading GameData: {e}")
        return False

    except ImportError as e:
        print(f"✗ Error importing tirganach: {e}")
        return False
    except Exception as e:
        print(f"✗ Error loading GameData: {e}")
        return False


if __name__ == "__main__":
    print("=== GameData.cff Access Test ===")
    test_game_data_access()
    print("\n=== Test Complete ===")
