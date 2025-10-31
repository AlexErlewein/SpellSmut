#!/usr/bin/env python3
"""
Utility to automatically split large JSON files and manage weapon data
"""
import json
import math
from pathlib import Path


def should_split_file(file_path: Path, max_size_mb: int = 50) -> bool:
    """Check if file needs splitting"""
    if not file_path.exists():
        return False
    
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    return file_size_mb > max_size_mb


def auto_split_if_needed(file_path: Path, max_size_mb: int = 50):
    """Automatically split file if it's too large"""
    if not should_split_file(file_path, max_size_mb):
        return False
    
    print(f"File {file_path} is too large, splitting...")
    
    # Import the splitter
    scripts_dir = Path(__file__).parent
    split_script = scripts_dir / "split_json.py"
    
    if split_script.exists():
        import subprocess
        import sys
        
        result = subprocess.run([
            sys.executable, str(split_script), str(file_path), 
            "--max-size", str(max_size_mb)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("File split successfully!")
            return True
        else:
            print(f"Error splitting file: {result.stderr}")
            return False
    else:
        print(f"Split script not found at {split_script}")
        return False


def check_weapon_data_quality():
    """Check the quality of weapon data from different sources"""
    
    print("Checking weapon data quality...")
    
    # Check enhanced_weapons.json
    enhanced_file = Path(__file__).parent.parent / "enhanced_weapons.json"
    if enhanced_file.exists():
        with open(enhanced_file, 'r') as f:
            enhanced_weapons = json.load(f)
        
        weapons_with_stats = sum(1 for w in enhanced_weapons 
                              if w.get('min_damage', 0) > 0 or w.get('max_damage', 0) > 0)
        print(f"Enhanced weapons: {len(enhanced_weapons)} total, {weapons_with_stats} with stats")
    
    # Check GameData.cff
    gamedata_path = Path(__file__).parent.parent.parent / "OriginalGameFiles" / "data" / "GameData.cff"
    if gamedata_path.exists():
        try:
            import sys
            sys.path.append(str(Path(__file__).parent.parent))
            from tirganach import GameData
            
            gd = GameData(str(gamedata_path))
            weapons = gd.weapons
            weapons_with_stats = sum(1 for w in weapons if w.min_damage > 0 or w.max_damage > 0)
            print(f"GameData weapons: {len(weapons)} total, {weapons_with_stats} with stats")
            
            # Check UI handles
            item_ui = gd.item_ui
            weapons_with_ui = 0
            for weapon in weapons:
                ui_matches = [ui for ui in item_ui if ui.item_id == weapon.item_id]
                if ui_matches and ui_matches[0].item_ui_handle:
                    weapons_with_ui += 1
            print(f"GameData weapons with UI handles: {weapons_with_ui}")
            
        except Exception as e:
            print(f"Error checking GameData: {e}")


if __name__ == "__main__":
    # Check enhanced_weapons.json and split if needed
    enhanced_file = Path(__file__).parent.parent / "enhanced_weapons.json"
    auto_split_if_needed(enhanced_file)
    
    # Check data quality
    check_weapon_data_quality()