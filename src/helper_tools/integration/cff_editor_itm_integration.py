#!/usr/bin/env python3
"""
CFF Editor ITM Icon Integration
================================

This module provides complete ITM icon integration for the CFF editor.
It handles loading GameData.cff files, extracting ITM mappings, and calculating
texture coordinates for icon display.

Features:
- Load Items and ItemUI tables from GameData.cff
- Extract ITM indices from UI handles using regex patterns
- Calculate texture coordinates for ITM atlas display
- Support both original and modded GameData files
- Complete mapping with fallback handling
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from src.TirganachReloaded.tirganach.structure import GameData


@dataclass
class ITMMapping:
    """Represents a complete ITM mapping with texture coordinates."""
    item_id: int
    item_name: Optional[str]
    ui_handle: str
    itm_index: Optional[int]
    ui_index: int
    scaled_down: int
    texture_coords: Optional[Tuple[int, int, int, int]]  # (x, y, width, height)
    atlas_file: Optional[str]


class ITMIconMapper:
    """Handles ITM icon mapping from GameData.cff files."""
    
    # ITM texture atlas configuration
    ICON_SIZE = 16
    GRID_SIZE = 16
    ATLAS_SIZE = 256
    
    # Regex patterns for ITM index extraction (in priority order)
    ITM_PATTERNS = [
        (r'ui_itm_equip_(\d+)', 'Direct ITM equipment index'),
        (r'itm_(\d+)', 'Fallback ITM index'),
        (r'equip.*?(\d{4})', 'Equipment 4-digit index'),
    ]
    
    def __init__(self, game_data_path: str):
        """Initialize the mapper with a GameData.cff file."""
        self.game_data_path = Path(game_data_path)
        self.game_data = None
        self.item_lookup = {}
        self.itm_mappings = []
        
        self._load_game_data()
        self._build_item_lookup()
        self._extract_itm_mappings()
    
    def _load_game_data(self):
        """Load the GameData.cff file."""
        if not self.game_data_path.exists():
            raise FileNotFoundError(f"GameData file not found: {self.game_data_path}")
        
        print(f"Loading GameData from: {self.game_data_path}")
        self.game_data = GameData(str(self.game_data_path))
        print(f"Loaded {len(self.game_data.items)} items and {len(self.game_data.item_ui)} UI entries")
    
    def _build_item_lookup(self):
        """Build efficient item_id -> Item mapping."""
        self.item_lookup = {item.item_id: item for item in self.game_data.items}
        print(f"Built item lookup with {len(self.item_lookup)} entries")
    
    def _extract_itm_mappings(self):
        """Extract all ITM mappings from ItemUI table."""
        self.itm_mappings = []
        
        for ui_entry in self.game_data.item_ui:
            # Get item name (may be None for UI-only entries)
            item = self.item_lookup.get(ui_entry.item_id)
            item_name = item.name_id if item else None
            
            # Extract ITM index using patterns
            itm_index = self._extract_itm_index(ui_entry.item_ui_handle)
            
            # Calculate texture coordinates if ITM index found
            texture_coords = None
            atlas_file = None
            if itm_index is not None:
                texture_coords, atlas_file = self._calculate_texture_coordinates(itm_index)
            
            mapping = ITMMapping(
                item_id=ui_entry.item_id,
                item_name=item_name,
                ui_handle=ui_entry.item_ui_handle,
                itm_index=itm_index,
                ui_index=ui_entry.item_ui_index,
                scaled_down=ui_entry.scaled_down,
                texture_coords=texture_coords,
                atlas_file=atlas_file
            )
            
            self.itm_mappings.append(mapping)
        
        # Filter to only ITM mappings
        self.itm_mappings = [m for m in self.itm_mappings if m.itm_index is not None]
        print(f"Found {len(self.itm_mappings)} ITM mappings")
    
    def _extract_itm_index(self, ui_handle: str) -> Optional[int]:
        """Extract ITM index from UI handle using regex patterns."""
        for pattern, description in self.ITM_PATTERNS:
            match = re.search(pattern, ui_handle, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        return None
    
    def _calculate_texture_coordinates(self, itm_index: int) -> Tuple[Tuple[int, int, int, int], str]:
        """Calculate texture coordinates and atlas file for ITM index."""
        # Determine atlas file (0-97 based on index range)
        atlas_num = itm_index // (self.GRID_SIZE * self.GRID_SIZE)
        local_index = itm_index % (self.GRID_SIZE * self.GRID_SIZE)
        
        # Calculate grid position
        row = local_index // self.GRID_SIZE
        col = local_index % self.GRID_SIZE
        
        # Calculate pixel coordinates
        x = col * self.ICON_SIZE
        y = row * self.ICON_SIZE
        
        texture_coords = (x, y, self.ICON_SIZE, self.ICON_SIZE)
        atlas_file = f"atlas_{atlas_num}.png"
        
        return texture_coords, atlas_file
    
    def get_itm_mapping(self, item_id: int) -> Optional[ITMMapping]:
        """Get ITM mapping for a specific item ID."""
        for mapping in self.itm_mappings:
            if mapping.item_id == item_id:
                return mapping
        return None
    
    def get_all_itm_mappings(self) -> List[ITMMapping]:
        """Get all ITM mappings."""
        return self.itm_mappings
    
    def get_itm_mappings_by_atlas(self, atlas_num: int) -> List[ITMMapping]:
        """Get ITM mappings for a specific atlas file."""
        return [m for m in self.itm_mappings if m.atlas_file == f"atlas_{atlas_num}.png"]
    
    def print_summary(self):
        """Print a summary of ITM mappings."""
        print(f"\n=== ITM Mapping Summary ===")
        print(f"Total ITM mappings: {len(self.itm_mappings)}")
        
        if self.itm_mappings:
            itm_indices = [m.itm_index for m in self.itm_mappings]
            print(f"ITM index range: {min(itm_indices)} - {max(itm_indices)}")
            print(f"Unique ITM indices: {len(set(itm_indices))}")
            
            # Show mappings by pattern type
            pattern_counts = {}
            for mapping in self.itm_mappings:
                for pattern, desc in self.ITM_PATTERNS:
                    if re.search(pattern, mapping.ui_handle, re.IGNORECASE):
                        pattern_counts[desc] = pattern_counts.get(desc, 0) + 1
                        break
            
            print("Mappings by pattern:")
            for pattern, count in pattern_counts.items():
                print(f"  {pattern}: {count}")
            
            print(f"\nSample mappings:")
            for i, mapping in enumerate(self.itm_mappings[:5]):
                item_info = f"'{mapping.item_name}'" if mapping.item_name else "No item data"
                print(f"  {i+1}. Item {mapping.item_id} ({item_info}) -> ITM {mapping.itm_index}")
                print(f"     Handle: {mapping.ui_handle}")
                print(f"     Atlas: {mapping.atlas_file}, Coords: {mapping.texture_coords}")


class CFFEditorITMIntegration:
    """Complete CFF editor integration for ITM icons."""
    
    def __init__(self, original_gamedata: str, modded_gamedata: str = None):
        """Initialize with original and optionally modded GameData files."""
        self.original_mapper = ITMIconMapper(original_gamedata)
        self.modded_mapper = ITMIconMapper(modded_gamedata) if modded_gamedata else None
        
        # ITM icon directory (from extraction)
        self.itm_icon_dir = Path("ExtractedAssets/UI/icons_extracted/itm/")
        
    def get_icon_path(self, mapping: ITMMapping, use_modded: bool = False) -> Optional[Path]:
        """Get the actual icon file path for a mapping."""
        mapper = self.modded_mapper if use_modded and self.modded_mapper else self.original_mapper
        
        if not mapping.atlas_file or not mapping.texture_coords:
            return None
        
        # Try to find the extracted icon file
        atlas_num = int(mapping.atlas_file.replace('atlas_', '').replace('.png', ''))
        icon_index = mapping.itm_index
        
        # Look for individual icon file
        icon_file = self.itm_icon_dir / f"atlas_{atlas_num}" / f"icon_{icon_index:03d}.png"
        
        if icon_file.exists():
            return icon_file
        
        # Fallback to atlas file
        atlas_file = self.itm_icon_dir / mapping.atlas_file
        return atlas_file if atlas_file.exists() else None
    
    def compare_original_vs_modded(self):
        """Compare ITM mappings between original and modded GameData."""
        if not self.modded_mapper:
            print("No modded GameData provided for comparison")
            return
        
        original_mappings = {m.item_id: m for m in self.original_mapper.get_all_itm_mappings()}
        modded_mappings = {m.item_id: m for m in self.modded_mapper.get_all_itm_mappings()}
        
        original_only = set(original_mappings.keys()) - set(modded_mappings.keys())
        modded_only = set(modded_mappings.keys()) - set(original_mappings.keys())
        common = set(original_mappings.keys()) & set(modded_mappings.keys())
        
        print(f"\n=== Original vs Modded Comparison ===")
        print(f"Original ITM mappings: {len(original_mappings)}")
        print(f"Modded ITM mappings: {len(modded_mappings)}")
        print(f"Common mappings: {len(common)}")
        print(f"Original only: {len(original_only)}")
        print(f"Modded only: {len(modded_only)}")
        
        if original_only:
            print(f"\nItems only in original: {sorted(list(original_only))}")
        if modded_only:
            print(f"\nItems only in modded: {sorted(list(modded_only))}")
        
        # Check for differences in common mappings
        differences = []
        for item_id in common:
            orig = original_mappings[item_id]
            mod = modded_mappings[item_id]
            if orig.itm_index != mod.itm_index or orig.ui_handle != mod.ui_handle:
                differences.append(item_id)
        
        if differences:
            print(f"\nItems with different mappings: {len(differences)}")
            for item_id in differences[:10]:  # Show first 10
                orig = original_mappings[item_id]
                mod = modded_mappings[item_id]
                print(f"  Item {item_id}:")
                print(f"    Original: {orig.ui_handle} -> ITM {orig.itm_index}")
                print(f"    Modded:   {mod.ui_handle} -> ITM {mod.itm_index}")


def main():
    """Demonstrate the ITM integration system."""
    print("CFF Editor ITM Integration Demo")
    print("=" * 40)
    
    # Initialize with original GameData
    original_path = "OriginalGameFiles/data/GameData.cff"
    modded_path = "ModdedGameFiles/GameData_MyCustomMod_20251019_100557.cff"
    
    if not Path(original_path).exists():
        print(f"Original GameData not found: {original_path}")
        return
    
    integration = CFFEditorITMIntegration(original_path, modded_path)
    
    # Show original mappings
    print("\nORIGINAL GAME DATA:")
    integration.original_mapper.print_summary()
    
    # Show comparison if modded data available
    if Path(modded_path).exists():
        print("\nMODDED GAME DATA:")
        integration.modded_mapper.print_summary()
        
        integration.compare_original_vs_modded()
    
    # Test icon path resolution
    print(f"\n=== Icon Path Resolution Test ===")
    mappings = integration.original_mapper.get_all_itm_mappings()
    if mappings:
        test_mapping = mappings[0]
        icon_path = integration.get_icon_path(test_mapping)
        print(f"Test mapping: Item {test_mapping.item_id} -> ITM {test_mapping.itm_index}")
        print(f"Icon path: {icon_path}")
        print(f"Icon exists: {icon_path.exists() if icon_path else False}")


if __name__ == "__main__":
    main()