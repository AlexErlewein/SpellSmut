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

SpellSmut is a mature, Python-based project that provides a full suite of tools and documentation for modding the SpellForce game. While the core of the project is **TirganachReloaded**, a GUI application for editing the game's `GameData.cff` file, it has expanded to include a wide range of content creation wizards, asset management systems, and a 3D map viewer.

The project uses **beads** for task tracking.

### Key Components

*   **TirganachReloaded (CFF Editor):** A powerful GUI tool for editing `GameData.cff` files. It features a 3-panel layout, multi-language support, a dark theme, and an integrated Quest Editor. The data layer has been significantly accelerated with a cache/DB backend to improve performance.
*   **Content Creator Suite:** A collection of wizard-style tools that enable users to create complex game content without writing code. All creators are integrated with a shared **ID Management System** to prevent conflicts. Completed creators include:
    *   Quest Creator
    *   Spell Wizard
    *   Weapon Forge
    *   Armor Forge
    *   NPC Workshop
    *   Race Creator
*   **Map Viewer:** An in-progress 3D map viewer built with PyOpenGL capable of rendering game maps. Core rendering, camera controls, and basic texture support are implemented.
*   **Asset Extraction System:** A suite of Python scripts for extracting over 59,500 game assets (icons, textures, models, audio, etc.) from the game's PAK archives.
*   **Icon System:** A system for extracting and mapping over 32,000 game icons. While technical extraction is complete, a critical blocker remains in mapping item handles from game data to the correct texture atlases.
*   **Universal Savefile System:** A plan for standardized `.quest`, `.spell`, `.weapon` file formats for sharing work-in-progress content.
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

The editor now has a convenient entry point. To run the GUI application:

```bash
uv run tirganach
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
*   **Testing:** **pytest** is the testing framework. Tests are located in the `src/tests` directory.
*   **Task Tracking:** The project uses **beads** for task and issue tracking.

### Configuration Files

*   `pyproject.toml`: Defines project metadata, dependencies, and build settings.
*   `uv.lock`: Locks the versions of all project dependencies.
*   `pytest.ini`: Configures the pytest testing framework.
*   `.beads/`: Contains task tracking data.

## Project Structure

The project has been reorganized for clarity and maintainability.

```
/
├── docs/                  # Modding documentation and guides
├── ExtractedAssets/       # Game assets extracted by the tools
├── ModdedGameFiles/       # Modified game files created by the CFF Editor
├── OriginalGameFiles/     # Original game files for reference
├── ProjectPlanning/       # Development plans, status reports, and architecture docs
├── src/                   # All Python source code
│   ├── TirganachReloaded/ # The main CFF Editor application and its components
│   ├── helper_tools/      # Standalone scripts and utilities
│   └── tests/             # Unit and integration tests
├── .beads/                # Task tracking data
├── .gitignore             # Git ignore file
├── .ai/                   # AI assistant context files
│   └── GEMINI.md          # This file
├── pyproject.toml         # Python project configuration
└── README.md              # Project README
```
