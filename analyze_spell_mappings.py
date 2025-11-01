#!/usr/bin/env python3
"""
Script to specifically analyze spell-related mappings in the ui_icon_mapping.json file.
"""

import json
import gzip
from pathlib import Path

def analyze_spell_mappings():
    mapping_path = Path("src/TirganachReloaded/data/ui_icon_mapping.json")
    
    if not mapping_path.exists():
        print(f"Mapping file not found: {mapping_path}")
        return
    
    print("Analyzing spell mappings...")
    
    # Since the file is too large to load entirely, let's try streaming it
    # and look for spell-related entries
    spell_mappings = []
    
    with open(mapping_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Find spell-related mappings
        # Look for entries that map to handles starting with "ui_spell_"
        import re
        
        # Pattern to match spell-related entries
        # We're looking for patterns like "handle": "ui_spell_..." 
        spell_handle_pattern = r'"handle"\s*:\s*"([^"]*ui_spell_[^"]*)"'
        matches = re.findall(spell_handle_pattern, content)
        
        print(f"Found {len(matches)} spell-related handles in mapping")
        print("First 20 spell handles:", matches[:20])
        
        # Also look for item IDs that have spell mappings
        # Pattern to find ID mappings that contain spell handles
        item_id_pattern = r'"(\d+)"\s*:\s*\[([^\]]*ui_spell_[^\]]*)\]'
        id_matches = re.findall(item_id_pattern, content)
        
        print(f"\nFound {len(id_matches)} item IDs that have spell mappings")
        print("First 10 ID mappings:", id_matches[:10])
        
        # Now let's create a sample mapping file with spell data to see the structure
        # Extract first few spell mappings to understand structure
        if matches:
            print(f"\nAnalyzing structure based on found spell handles...")
            
            # Let's try to extract a small sample of the mapping
            # Find complete entries that include spell handles
            import re
            
            # Look for complete id -> icon mappings that include a spell handle
            complex_pattern = r'"(\d+)"\s*:\s*\[([^{]*\{[^}]*"handle"[^}]*"ui_spell_[^}]*\}[^]]*)\]'
            detailed_matches = re.findall(complex_pattern, content)
            
            print(f"\nDetailed matches with spell mappings: {len(detailed_matches)}")
            if detailed_matches:
                print("Sample of detailed mapping (first 3):")
                for i, (item_id, mapping_data) in enumerate(detailed_matches[:3]):
                    print(f"  ID {item_id}: {mapping_data[:200]}...")
    
    print("\nAnalysis complete.")

def extract_spell_mappings_to_file():
    """Extract spell-related mappings to a smaller file for detailed analysis."""
    
    mapping_path = Path("src/TirganachReloaded/data/ui_icon_mapping.json")
    output_path = Path("spell_mappings_sample.json")
    
    if not mapping_path.exists():
        print(f"Mapping file not found: {mapping_path}")
        return
    
    print("Extracting spell mappings to separate file...")
    
    spell_mappings = {}
    
    with open(mapping_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        import re
        
        # Find all occurrences of item ID mappings that contain spell handles
        id_pattern = r'"(\d+)"\s*:\s*\[([^{]*\{[^}]*"handle"[^}]*"ui_spell_[^}]*\}[^]]*)\]'
        matches = re.findall(id_pattern, content)
        
        # Extract a sample to understand the structure
        sample_matches = matches[:50]  # First 50 entries
        
        # Reconstruct as valid JSON
        sample_data = {"spell_mappings": {}}
        for item_id, mapping_str in sample_matches:
            # We need to fix the mapping_str to be valid JSON
            # Add back the outer brackets and structure
            full_mapping = f"[{mapping_str}]"
            # This is still not properly formatted, so let's try a different approach
            
        # Write the sample data to file
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write("{\n")
            out_f.write('  "note": "Sample of spell-related mappings from ui_icon_mapping.json",\n')
            out_f.write('  "total_spell_mappings_found": ' + str(len(matches)) + ',\n')
            out_f.write('  "sample_spell_mappings": {\n')
            
            for i, (item_id, mapping_str) in enumerate(matches[:10]):
                if i > 0:
                    out_f.write(',\n')
                out_f.write(f'    "{item_id}": [/* mapping data with spell handle */]')
            
            out_f.write('\n  }\n')
            out_f.write("}\n")
    
    print(f"Sample written to {output_path}")

if __name__ == "__main__":
    analyze_spell_mappings()
    extract_spell_mappings_to_file()