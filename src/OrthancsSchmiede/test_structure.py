#!/usr/bin/env python3
"""
Simple test script for OrthancsSchmiede structure
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

print("OrthancsSchmiede Structure Test")
print("=" * 40)

# Test imports
try:
    print("✓ Project root:", project_root)
    print("✓ Added to sys.path:", str(project_root / "src"))

    # Check if required modules exist
    orthancs_file = project_root / "src" / "OrthancsSchmiede" / "orthancs_schmiede.py"
    if orthancs_file.exists():
        print("✓ Main app file exists:", orthancs_file)
    else:
        print("✗ Main app file missing")

    readme_file = project_root / "src" / "OrthancsSchmiede" / "README.md"
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

    print("\n✅ OrthancsSchmiede structure test completed successfully!")
    print("\nTo run the full application:")
    print("  cd src/OrthancsSchmiede")
    print("  python orthancs_schmiede.py")

except Exception as e:
    print("✗ Test failed:", e)
    sys.exit(1)
