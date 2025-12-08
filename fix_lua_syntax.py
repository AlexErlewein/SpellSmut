#!/usr/bin/env python3
"""
Automated fix for SpellForce Lua syntax errors.
Fixes UND and ODER function calls that are split across multiple lines.
"""

import os
import re
import glob
from pathlib import Path


def fix_lua_syntax(file_path):
    """Fix UND and ODER function calls in a Lua file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        original_content = content

        # Fix UND function calls split across lines
        # Pattern: UND\n(\n    ...parameters...\n)
        content = re.sub(r"UND\s*\n\s*\(\s*\n", "UND(", content, flags=re.MULTILINE)

        # Fix ODER function calls split across lines
        # Pattern: ODER\n(\n    ...parameters...\n)
        content = re.sub(r"ODER\s*\n\s*\(\s*\n", "ODER(", content, flags=re.MULTILINE)

        # Additional pattern: UND\n( without newline after (
        content = re.sub(r"UND\s*\n\s*\(", "UND(", content, flags=re.MULTILINE)

        # Additional pattern: ODER\n( without newline after (
        content = re.sub(r"ODER\s*\n\s*\(", "ODER(", content, flags=re.MULTILINE)

        # Only write if content changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def find_lua_files(base_path):
    """Find all Lua files in the ModdingTools/SpellForceLUASources directory."""
    lua_files = []

    # Look specifically in the script subdirectories
    script_path = os.path.join(base_path, "script")
    if os.path.exists(script_path):
        for root, dirs, files in os.walk(script_path):
            for file in files:
                if file.endswith(".lua"):
                    lua_files.append(os.path.join(root, file))

    return lua_files


def main():
    """Main function to fix all Lua files."""
    # Base path to the SpellForce Lua sources
    base_path = "/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/ModdingTools/SpellForceLUASources"

    print("Finding Lua files to fix...")
    lua_files = find_lua_files(base_path)

    print(f"Found {len(lua_files)} Lua files to check")

    fixed_files = []
    error_files = []

    for file_path in lua_files:
        print(f"Processing: {file_path}")
        if fix_lua_syntax(file_path):
            fixed_files.append(file_path)
            print(f"  ✓ Fixed")
        else:
            print(f"  - No changes needed")

    print(f"\nSummary:")
    print(f"Files fixed: {len(fixed_files)}")
    print(f"Files with errors: {len(error_files)}")

    if fixed_files:
        print(f"\nFixed files:")
        for file_path in fixed_files:
            print(f"  {file_path}")


if __name__ == "__main__":
    main()
