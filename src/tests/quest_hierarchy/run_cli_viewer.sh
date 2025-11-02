#!/bin/bash
# Launcher script for Quest Hierarchy CLI Viewer

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

echo "Starting Quest Hierarchy CLI Viewer..."
echo "======================================="
echo ""

# Check if a CFF file path was provided as argument
if [ $# -eq 1 ]; then
    echo "Loading CFF file: $1"
    echo ""
    python quest_hierarchy_cli.py "$1"
else
    echo "Loading default CFF file..."
    echo ""
    python quest_hierarchy_cli.py
fi
