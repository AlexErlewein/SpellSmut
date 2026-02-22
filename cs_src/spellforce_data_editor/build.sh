#!/bin/bash
# Build Script for SpellForce Data Editor
# Builds the application and copies the exe to the SpellforceDataEditor directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/SpellforceDataEditor"
OUTPUT_DIR="$PROJECT_DIR/bin/Release/net8.0-windows10.0.17763.0"
TARGET_DIR="$PROJECT_DIR"

echo -e "${CYAN}=== SpellForce Data Editor Build Script ===${NC}"
echo ""
echo -e "${GRAY}Project Directory: $PROJECT_DIR${NC}"
echo -e "${GRAY}Output Directory: $OUTPUT_DIR${NC}"
echo -e "${GRAY}Target Directory: $TARGET_DIR${NC}"
echo ""

# Check if dotnet is available
if ! command -v dotnet &> /dev/null; then
    echo -e "${RED}✗ .NET SDK not found. Please install .NET 8.0 SDK.${NC}"
    exit 1
fi

DOTNET_VERSION=$(dotnet --version)
echo -e "${GREEN}✓ Found dotnet SDK: $DOTNET_VERSION${NC}"
echo ""

# Restore packages
echo -e "${YELLOW}Restoring NuGet packages...${NC}"
dotnet restore "SpellforceDataEditor.sln" --no-build 2>/dev/null
echo -e "${GREEN}✓ Packages restored${NC}"
echo ""

# Build the project
echo -e "${YELLOW}Building Release configuration...${NC}"
dotnet build "SpellforceDataEditor.sln" -c Release -p:Platform=x86 --no-restore
echo -e "${GREEN}✓ Build completed successfully${NC}"
echo ""

# Copy the exe to the target directory
EXE_SOURCE="$OUTPUT_DIR/SpellforceDataEditor.exe"
EXE_TARGET="$TARGET_DIR/SpellforceDataEditor.exe"

echo -e "${YELLOW}Copying exe to target directory...${NC}"

if [ -f "$EXE_SOURCE" ]; then
    # Remove old exe if exists
    if [ -f "$EXE_TARGET" ]; then
        rm -f "$EXE_TARGET"
        echo -e "${GRAY}  Removed old exe${NC}"
    fi

    # Copy new exe
    cp "$EXE_SOURCE" "$EXE_TARGET"
    echo -e "${GREEN}✓ Copied SpellforceDataEditor.exe to: $TARGET_DIR${NC}"

    # Get file info
    FILE_SIZE=$(du -h "$EXE_TARGET" | cut -f1)
    echo -e "${GRAY}  Size: $FILE_SIZE${NC}"
else
    echo -e "${RED}✗ exe not found at: $EXE_SOURCE${NC}"
    exit 1
fi

# Also copy required DLLs if they don't exist
echo ""
echo -e "${YELLOW}Checking required dependencies...${NC}"

REQUIRED_FILES=("OpenTK.dll" "OpenTK.WinForms.dll" "NAudio.dll")

for file in "${REQUIRED_FILES[@]}"; do
    SOURCE_FILE="$OUTPUT_DIR/$file"
    TARGET_FILE="$TARGET_DIR/$file"

    if [ ! -f "$TARGET_FILE" ]; then
        if [ -f "$SOURCE_FILE" ]; then
            cp "$SOURCE_FILE" "$TARGET_FILE"
            echo -e "${GREEN}  ✓ Copied $file${NC}"
        else
            echo -e "${YELLOW}  ⚠ Warning: $file not found${NC}"
        fi
    fi
done

echo ""
echo -e "${GREEN}=== Build Complete! ===${NC}"
echo -e "${CYAN}You can now run the editor from: $EXE_TARGET${NC}"
