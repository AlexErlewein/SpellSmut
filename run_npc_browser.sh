#!/bin/bash
# Launch script for NPC Browser Test

cd "$(dirname "$0")"

echo "============================================================"
echo "NPC Browser Test Launcher"
echo "============================================================"
echo ""

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "✓ Using uv to run..."
    uv run test_npc_browser.py
else
    echo "⚠ uv not found, trying python3..."
    
    # Check for virtual environment
    if [ -d ".venv" ]; then
        echo "✓ Activating virtual environment..."
        source .venv/bin/activate
        python3 test_npc_browser.py
    else
        echo "✗ No virtual environment found"
        echo ""
        echo "Please install dependencies first:"
        echo "  pip install -r requirements.txt"
        echo ""
        echo "Or use uv:"
        echo "  uv sync"
        echo "  uv run test_npc_browser.py"
    fi
fi
