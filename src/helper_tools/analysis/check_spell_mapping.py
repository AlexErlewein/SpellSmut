#!/usr/bin/env python3
"""
Script to analyze the spell-to-icon mapping in the ui_icon_mapping.json file.
"""

import json
from pathlib import Path

def analyze_spell_mapping():
    mapping_path = Path("src/TirganachReloaded/data/ui_icon_mapping.json")
    
    if not mapping_path.exists():
        print(f"Mapping file not found: {mapping_path}")
        return
    
    print("Analyzing spell mapping...")
    
    # Count total items to get an idea of the file size
    with open(mapping_path, 'r') as f:
        # Read the beginning to identify the structure
        start = f.read(1000)
        print("Beginning of file:", start[:200])
    
    # Instead of loading the whole file, let's check for spell-related entries
    with open(mapping_path, 'r') as f:
        # Read in chunks to find spell entries
        content = f.read()
        
        # Look for spell-related entries
        spell_handles = []
        
        # Check if it's a JSON object with multiple keys
        try:
            # Try to load the first part to see the structure
            # Since the file is too large, we'll just look for spell patterns
            import re
            
            # Look for handles that contain "spell" 
            spell_pattern = r'"([^"]*spell[^"]*)"'
            matches = re.findall(spell_pattern, content[:10000])  # Check first 10k chars
            
            print("Found potential spell handles in first part:", [m for m in matches if 'spell' in m.lower()][:10])
            
        except Exception as e:
            print(f"Error parsing: {e}")
    
    print("Completed basic analysis of mapping file.")

if __name__ == "__main__":
    analyze_spell_mapping()