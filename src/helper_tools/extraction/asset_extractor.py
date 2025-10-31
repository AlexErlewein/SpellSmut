#!/usr/bin/env python3
"""
SpellForce Asset Extractor with Diff Comparison

This tool extracts game assets from PAK files and provides diff comparison
functionality to track changes between different versions.

Features:
1. Extract assets using QuickBMS
2. Organize assets in structured directory layout
3. Create reference snapshots of original files
4. Compare extracted assets with reference to show changes
5. Generate detailed reports of additions, deletions, and modifications

Author: SpellSmut Modding Project
Date: October 31, 2025
"""

import os
import sys
import subprocess
import hashlib
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
import argparse


@dataclass
class AssetInfo:
    """Information about an asset file"""
    path: str
    size: int
    checksum: str
    modified_time: float


@dataclass
class ExtractionSnapshot:
    """Snapshot of extracted assets"""
    timestamp: str
    game_version: str
    assets: Dict[str, AssetInfo]


class AssetExtractor:
    """Main asset extraction and comparison tool"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tools_dir = project_root / "ModdingTools"
        self.quickbms_dir = self.tools_dir / "quickbms"
        self.extraction_scripts_dir = project_root / "src" / "helper_tools" / "extraction"
        self.original_files_dir = project_root / "OriginalGameFiles"
        self.extracted_assets_dir = project_root / "ExtractedAssets"
        self.reference_dir = project_root / "ReferenceAssets"
        
        # Detect platform and use appropriate executable
        import platform
        if platform.system() == "Windows":
            self.quickbms_exe = self.quickbms_dir / "quickbms.exe"
        else:
            self.quickbms_exe = self.quickbms_dir / "quickbms"  # macOS/Linux

    def ensure_quickbms(self) -> bool:
        """Ensure QuickBMS is available"""
        if self.quickbms_exe.exists():
            print(f"[OK] QuickBMS found at: {self.quickbms_exe}")
            return True
            
        print("[ERROR] QuickBMS not found. Please run bulk_extract_paks.py first to install it.")
        return False

    def get_pak_files(self) -> List[Path]:
        """Get list of all PAK files to extract"""
        pak_dir = self.original_files_dir / "pak"
        if not pak_dir.exists():
            print(f"[ERROR] PAK directory not found: {pak_dir}")
            return []

        pak_files = sorted(pak_dir.glob("*.pak"))
        return pak_files

    def extract_assets(self, output_dir: Path = None, force: bool = False) -> bool:
        """
        Extract all game assets using the existing bulk extraction script
        
        Args:
            output_dir: Directory to extract to (uses default if None)
            force: Force re-extraction even if files exist
            
        Returns:
            True if successful, False otherwise
        """
        print("Starting asset extraction...")
        
        # Use the existing bulk extraction script
        bulk_extract_script = self.extraction_scripts_dir / "bulk_extract_paks.py"
        if not bulk_extract_script.exists():
            print(f"[ERROR] Bulk extraction script not found: {bulk_extract_script}")
            return False
            
        # Run the script with auto-proceed flag
        cmd = [sys.executable, str(bulk_extract_script), "--auto"]
        
        try:
            print("Running bulk extraction...")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("[OK] Asset extraction completed successfully")
                print(result.stdout)
                return True
            else:
                print("[ERROR] Asset extraction failed")
                print(f"Return code: {result.returncode}")
                print(f"Stdout: {result.stdout}")
                print(f"Stderr: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to run bulk extraction: {e}")
            return False

    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"Warning: Could not calculate checksum for {file_path}: {e}")
            return ""

    def create_asset_info(self, file_path: Path, base_dir: Path) -> AssetInfo:
        """Create AssetInfo for a file"""
        try:
            stat = file_path.stat()
            relative_path = file_path.relative_to(base_dir).as_posix()
            checksum = self.calculate_file_checksum(file_path)
            
            return AssetInfo(
                path=relative_path,
                size=stat.st_size,
                checksum=checksum,
                modified_time=stat.st_mtime
            )
        except Exception as e:
            print(f"Warning: Could not create asset info for {file_path}: {e}")
            return None

    def create_snapshot(self, assets_dir: Path, snapshot_name: str = None) -> ExtractionSnapshot:
        """
        Create a snapshot of the current extracted assets
        
        Args:
            assets_dir: Directory containing extracted assets
            snapshot_name: Name for the snapshot (defaults to timestamp)
            
        Returns:
            ExtractionSnapshot object
        """
        import datetime
        
        if snapshot_name is None:
            snapshot_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
        print(f"Creating snapshot: {snapshot_name}")
        
        # Collect asset information
        assets = {}
        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                file_path = Path(root) / file
                asset_info = self.create_asset_info(file_path, assets_dir)
                if asset_info:
                    assets[asset_info.path] = asset_info
                    
        # Create snapshot
        snapshot = ExtractionSnapshot(
            timestamp=snapshot_name,
            game_version="SpellForce Platinum Edition",  # Could be enhanced to detect version
            assets=assets
        )
        
        return snapshot

    def save_snapshot(self, snapshot: ExtractionSnapshot, snapshot_file: Path):
        """Save snapshot to JSON file"""
        # Convert to dictionary for JSON serialization
        snapshot_dict = {
            "timestamp": snapshot.timestamp,
            "game_version": snapshot.game_version,
            "assets": {path: asdict(info) for path, info in snapshot.assets.items()}
        }
        
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot_dict, f, indent=2)
            
        print(f"Snapshot saved to: {snapshot_file}")

    def load_snapshot(self, snapshot_file: Path) -> ExtractionSnapshot:
        """Load snapshot from JSON file"""
        try:
            with open(snapshot_file, 'r') as f:
                snapshot_dict = json.load(f)
                
            # Convert back to objects
            assets = {
                path: AssetInfo(**info) 
                for path, info in snapshot_dict["assets"].items()
            }
            
            snapshot = ExtractionSnapshot(
                timestamp=snapshot_dict["timestamp"],
                game_version=snapshot_dict["game_version"],
                assets=assets
            )
            
            return snapshot
        except Exception as e:
            print(f"Warning: Could not load snapshot from {snapshot_file}: {e}")
            return None

    def compare_snapshots(self, snapshot1: ExtractionSnapshot, snapshot2: ExtractionSnapshot) -> Dict:
        """
        Compare two snapshots and return differences
        
        Returns:
            Dictionary with added, removed, and modified files
        """
        assets1 = set(snapshot1.assets.keys())
        assets2 = set(snapshot2.assets.keys())
        
        # Find differences
        added = assets2 - assets1
        removed = assets1 - assets2
        common = assets1 & assets2
        
        # Check for modifications in common files
        modified = set()
        for path in common:
            asset1 = snapshot1.assets[path]
            asset2 = snapshot2.assets[path]
            
            # Compare by checksum or size
            if asset1.checksum != asset2.checksum:
                modified.add(path)
            elif asset1.size != asset2.size:
                modified.add(path)
                
        return {
            "added": sorted(list(added)),
            "removed": sorted(list(removed)),
            "modified": sorted(list(modified)),
            "stats": {
                "added_count": len(added),
                "removed_count": len(removed),
                "modified_count": len(modified),
                "total_files_snapshot1": len(assets1),
                "total_files_snapshot2": len(assets2)
            }
        }

    def generate_diff_report(self, diff_result: Dict, report_file: Path):
        """Generate a detailed diff report"""
        with open(report_file, 'w') as f:
            f.write("# Asset Extraction Diff Report\n\n")
            
            f.write("## Summary\n")
            f.write(f"- Added files: {diff_result['stats']['added_count']}\n")
            f.write(f"- Removed files: {diff_result['stats']['removed_count']}\n")
            f.write(f"- Modified files: {diff_result['stats']['modified_count']}\n")
            f.write(f"- Total files (before): {diff_result['stats']['total_files_snapshot1']}\n")
            f.write(f"- Total files (after): {diff_result['stats']['total_files_snapshot2']}\n\n")
            
            if diff_result['added']:
                f.write("## Added Files\n")
                for path in diff_result['added']:
                    f.write(f"- {path}\n")
                f.write("\n")
                
            if diff_result['removed']:
                f.write("## Removed Files\n")
                for path in diff_result['removed']:
                    f.write(f"- {path}\n")
                f.write("\n")
                
            if diff_result['modified']:
                f.write("## Modified Files\n")
                for path in diff_result['modified']:
                    f.write(f"- {path}\n")
                f.write("\n")
                
        print(f"Diff report saved to: {report_file}")

    def create_reference_snapshot(self, force: bool = False) -> bool:
        """
        Create a reference snapshot of the original game files
        
        Args:
            force: Force creation even if reference exists
            
        Returns:
            True if successful, False otherwise
        """
        reference_snapshot_file = self.reference_dir / "reference_snapshot.json"
        
        if reference_snapshot_file.exists() and not force:
            print(f"[OK] Reference snapshot already exists: {reference_snapshot_file}")
            print("Use --force to recreate reference snapshot")
            return True
            
        print("Creating reference snapshot of original game files...")
        
        # Ensure reference directory exists
        self.reference_dir.mkdir(parents=True, exist_ok=True)
        
        # Create snapshot
        snapshot = self.create_snapshot(self.extracted_assets_dir, "reference")
        self.save_snapshot(snapshot, reference_snapshot_file)
        
        print("[OK] Reference snapshot created successfully")
        return True

    def compare_with_reference(self) -> bool:
        """
        Compare current extracted assets with reference snapshot
        
        Returns:
            True if successful, False otherwise
        """
        reference_snapshot_file = self.reference_dir / "reference_snapshot.json"
        
        if not reference_snapshot_file.exists():
            print(f"[ERROR] Reference snapshot not found: {reference_snapshot_file}")
            print("Please create a reference snapshot first using --create-reference")
            return False
            
        print("Comparing current assets with reference...")
        
        # Load reference snapshot
        reference_snapshot = self.load_snapshot(reference_snapshot_file)
        if not reference_snapshot:
            print("[ERROR] Failed to load reference snapshot")
            return False
            
        # Create current snapshot
        current_snapshot = self.create_snapshot(self.extracted_assets_dir, "current")
        
        # Compare snapshots
        diff_result = self.compare_snapshots(reference_snapshot, current_snapshot)
        
        # Generate report
        report_file = self.extracted_assets_dir / "diff_report.md"
        self.generate_diff_report(diff_result, report_file)
        
        # Print summary
        print("\n" + "=" * 50)
        print("DIFF COMPARISON RESULTS")
        print("=" * 50)
        print(f"Added files:     {diff_result['stats']['added_count']}")
        print(f"Removed files:   {diff_result['stats']['removed_count']}")
        print(f"Modified files:  {diff_result['stats']['modified_count']}")
        print(f"Total files (reference): {diff_result['stats']['total_files_snapshot1']}")
        print(f"Total files (current):   {diff_result['stats']['total_files_snapshot2']}")
        print("=" * 50)
        print(f"Full report saved to: {report_file}")
        
        return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="SpellForce Asset Extractor with Diff Comparison")
    parser.add_argument("--extract", action="store_true", help="Extract game assets")
    parser.add_argument("--create-reference", action="store_true", help="Create reference snapshot")
    parser.add_argument("--compare", action="store_true", help="Compare with reference snapshot")
    parser.add_argument("--force", action="store_true", help="Force operations (re-extract, recreate reference)")
    parser.add_argument("--output-dir", help="Output directory for extraction")
    
    args = parser.parse_args()
    
    # Set up paths
    project_root = Path(__file__).parent.parent.parent.parent
    extractor = AssetExtractor(project_root)
    
    # Ensure QuickBMS is available
    if not extractor.ensure_quickbms():
        return 1
        
    success = True
    
    # Handle operations
    if args.extract:
        output_dir = Path(args.output_dir) if args.output_dir else None
        success = extractor.extract_assets(output_dir, args.force)
        
    if args.create_reference:
        success = extractor.create_reference_snapshot(args.force) and success
        
    if args.compare:
        success = extractor.compare_with_reference() and success
        
    # If no operations specified, show help
    if not any([args.extract, args.create_reference, args.compare]):
        parser.print_help()
        return 0
        
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())