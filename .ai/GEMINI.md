# Gemini Code Assistant Context

## 📍 File Location Notice

**This file is located at:** `.ai/GEMINI.md`

**Purpose:** Instructions specifically for Gemini CLI / Google's Gemini AI assistant

**Note:** Other AI assistants have their own instruction files:
- Claude Code → `.ai/CLAUDE.md`
- Qwen → `.ai/QWEN.md`
- Crush → `.ai/CRUSH.md`

All AI instruction files are in the `.ai/` hidden folder, separate from user documentation.

---

This document provides a comprehensive overview of the SpellSmut project, a modding toolkit for **SpellForce: The Order of Dawn - Platinum Edition**.

## Project Overview

SpellSmut is a Python-based project that provides tools and documentation for modding the SpellForce game. The core of the project is **TirganachReloaded**, a GUI application built with **PySide6** for editing the game's `GameData.cff` file. This file contains a wide range of game data, including spells, items, quests, and more.

The project also includes an extensive set of documentation, asset extraction tools, and other resources to support the modding community.

### Key Components

*   **TirganachReloaded (CFF Editor):** A powerful GUI tool for editing `GameData.cff` files. It features:
    *   A 3-panel layout for navigating categories, elements, and properties.
    *   Multi-language support for viewing and editing game data.
    *   A dark theme for improved usability.
    *   An integrated Quest Editor for creating and modifying quests.
*   **Asset Extraction System:** A suite of Python scripts for extracting game assets (icons, textures, etc.) from the game's PAK archives.
*   **Icon System:** A system for extracting and mapping over 32,000 game icons to their corresponding items and spells.
*   **Documentation:** A comprehensive set of guides and tutorials covering all aspects of SpellForce modding.

## Building and Running

This project uses `uv` for dependency management and `hatchling` for building.

### Prerequisites

*   Python 3.9+
*   `uv` package manager (`pip install uv`)

### Installation

1.  **Install dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

### Running the CFF Editor

To run the CFF Editor GUI application:

```bash
uv run python src/TirganachReloaded/run_cff_editor.py
```

### Running Helper Tools

The project includes several helper tools in the `src/helper_tools` directory. You can run them using `uv run`:

*   **Interactive Icon Mapper:**
    ```bash
    uv run python src/helper_tools/interactive_icon_mapper.py
    ```
*   **Icon Extractor:**
    ```bash
    uv run python src/helper_tools/extract_icons_from_atlases.py
    ```

## Development Conventions

*   **Code Style:** The project uses **Black** for code formatting and **isort** for import sorting.
*   **Type Checking:** **mypy** is used for static type checking.
*   **Testing:** **pytest** is the testing framework of choice. Tests are located in the `src/tests` directory.

### Configuration Files

*   `pyproject.toml`: Defines project metadata, dependencies, and build settings.
*   `uv.lock`: Locks the versions of all project dependencies.
*   `pytest.ini`: Configures the pytest testing framework.

## Project Structure

```
/
├── docs/                  # Modding documentation and guides
├── ExtractedAssets/       # Game assets extracted by the tools
├── ModdedGameFiles/       # Modified game files created by the CFF Editor
├── OriginalGameFiles/     # Original game files for reference
├── ProjectPlanning/       # Project planning and overview documents
├── src/                   # Source code for the CFF Editor and helper tools
│   ├── TirganachReloaded/ # The main CFF Editor application
│   ├── helper_tools/      # Additional scripts and tools
│   └── tests/             # Unit and integration tests
├── .gitignore             # Git ignore file
├── GEMINI.md              # This file
├── pyproject.toml         # Python project configuration
└── README.md              # Project README
```
