#!/bin/bash
# Launcher script for Tirganach GUI Editor
# Opens the GUI in a new terminal window on macOS

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Launch in new terminal window
open -a Terminal.app --new --args bash -c "cd '$SCRIPT_DIR' && uv run tirganach; echo 'Press Enter to close...'; read"
