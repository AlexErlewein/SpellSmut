#!/bin/bash
# Quest Viewer Launcher Script
# Usage: ./run_quest_viewer.sh [--debug] [--rebuild-cache]

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to project directory
cd "$SCRIPT_DIR"

# Check if UV is available
if command -v uv &> /dev/null; then
    # Use UV for proper dependency management
    uv run python quest_viewer.py "$@"
else
    # Fallback to system Python
    python3 quest_viewer.py "$@"
fi