#!/bin/bash

# TirganachReloaded Quest Viewer Launcher
# This script launches the quest viewer with the Quest Creation Wizard

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory and launch the quest viewer
cd "$SCRIPT_DIR"
exec uv run python src/TirganachReloaded/cff_editor/simple_quest_viewer.py "$@"