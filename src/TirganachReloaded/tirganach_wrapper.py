#!/usr/bin/env python3
"""
Wrapper script for TirganachReloaded
"""

# Import and run the main function
try:
    from .cff_editor.main import main as tirganach_main
except ImportError:
    from cff_editor.main import main as tirganach_main

def main():
    """Main entry point for the wrapper"""
    tirganach_main()

if __name__ == "__main__":
    main()