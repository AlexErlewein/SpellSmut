"""
Organize extracted PAK files by category.
Run this after bulk_extract_paks.py completes extraction.
"""

import os
import shutil
from pathlib import Path

# Import the organize function from the main script
import sys
sys.path.insert(0, str(Path(__file__).parent))

from bulk_extract_paks import organize_extracted_files, EXTRACTED_DIR

if __name__ == "__main__":
    raw_output = EXTRACTED_DIR / "_raw_extraction"

    if not raw_output.exists():
        print(f"ERROR: Raw extraction directory not found: {raw_output}")
        print("Please run bulk_extract_paks.py first.")
        sys.exit(1)

    print("Organizing extracted files...")
    organize_extracted_files(raw_output)
    print("\nDone! Files organized into categories.")
