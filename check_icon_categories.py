#!/usr/bin/env python3
"""
Check what icon categories exist in the data
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from TirganachReloaded.cff_editor.data_model import CFFDataModel


def main():
    """Check icon categories"""
    data_model = CFFDataModel()
    
    icons = data_model.icon_index.get('icons', {})
    
    # Count categories
    categories = {}
    for icon_key, icon_info in icons.items():
        category = icon_info.get('category', 'unknown')
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    print("=== Icon Categories ===")
    for category, count in sorted(categories.items()):
        print(f"{category}: {count} icons")
    
    print(f"\nTotal: {sum(categories.values())} icons")
    
    # Show some examples from each category
    print("\n=== Sample Icons by Category ===")
    category_examples = {}
    
    for icon_key, icon_info in icons.items():
        category = icon_info.get('category', 'unknown')
        if category not in category_examples and len(category_examples) < 10:
            category_examples[category] = icon_key
    
    for category, icon_key in sorted(category_examples.items()):
        icon_info = icons[icon_key]
        print(f"\n{category}:")
        print(f"  Key: {icon_key}")
        print(f"  Path: {icon_info.get('path', '')}")
        print(f"  Atlas: {icon_info.get('atlas_number', '')}")


if __name__ == "__main__":
    main()