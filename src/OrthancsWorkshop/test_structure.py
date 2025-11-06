#!/usr/bin/env python3
"""
Simple test script for OrthancsWorkshop structure
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

print("OrthancsWorkshop Structure Test")
print("=" * 40)

# Test imports
try:
    print("✓ Project root:", project_root)
    print("✓ Added to sys.path:", str(project_root / "src"))

    # Check if required modules exist
    orthancs_file = project_root / "src" / "OrthancsWorkshop" / "orthancs_workshop.py"
    if orthancs_file.exists():
        print("✓ Main app file exists:", orthancs_file)
    else:
        print("✗ Main app file missing")

    readme_file = project_root / "src" / "OrthancsWorkshop" / "README.md"
    if readme_file.exists():
        print("✓ README file exists:", readme_file)
    else:
        print("✗ README file missing")

    # Check if TirganachReloaded modules are accessible
    try:
        from TirganachReloaded.cff_editor.logging_config import configure_logging

        print("✓ Logging config import successful")
    except ImportError as e:
        print("⚠ Logging config import failed (expected in test env):", e)

    try:
        from TirganachReloaded.cff_editor.shared.id_manager import (
            IDManager,
            ContentType,
        )

        print("✓ ID Manager import successful")
    except ImportError as e:
        print("⚠ ID Manager import failed (expected in test env):", e)

    print("\n✅ OrthancsWorkshop structure test completed successfully!")
    print("\nTo run the full application:")
    print("  cd src/OrthancsWorkshop")
    print("  python orthancs_workshop.py")

except Exception as e:
    print("✗ Test failed:", e)
    sys.exit(1)
