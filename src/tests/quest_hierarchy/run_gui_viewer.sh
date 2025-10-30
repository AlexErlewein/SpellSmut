#!/bin/bash
# Launcher script for Quest Hierarchy GUI Viewer

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

echo "Starting Quest Hierarchy Tree Viewer..."
echo "=========================================="
echo ""

# Check if a CFF file path was provided as argument
if [ $# -eq 1 ]; then
    echo "Loading CFF file: $1"
    python test_quest_tree_view.py "$1"
else
    echo "Loading default CFF file..."
    python test_quest_tree_view.py
fi
