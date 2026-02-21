# SFEngine Overview

This document provides an overview of the folders and files within the `SFEngine` directory.

## Folders

### SFCFF
This folder seems to contain the logic for handling SpellForce's CFF (GameData) files.
- **CTG:** This subfolder contains numerous files named `Category...cs`, suggesting that each file represents a specific data category within the CFF file format. These classes likely handle the reading, writing, and manipulation of data for things like items, units, spells, etc.
- `ICategory.cs`: An interface for the category classes.
- `SFCategoryManager.cs`: Manages all the different data categories.
- `SFGameDataNew.cs`: Represents the entire `GameData.cff` file, holding all the categories.

### SFChunk
This folder contains code to handle chunk-based file formats. It's likely used for proprietary SpellForce file types that are structured in chunks of data.
- `SFChunkFile.cs`: Represents a chunked file.
- `SFChunkFileChunk.cs`: Represents a single chunk within the file.

### SFLua
This folder is dedicated to handling Lua scripts, which SpellForce uses for game logic, quests, and AI.
- **LuaDecompiler:** Contains a full Lua decompiler, used to convert Lua bytecode back into human-readable script.
- **LuaParser:** Contains a parser to understand the structure of Lua scripts.
- **LuaTokenizer:** Contains a tokenizer, which is the first step in parsing, breaking the script into individual tokens.
- **lua_sql:** A specialized component for handling SQL-like data structures and queries within Lua, likely for game database interactions.
- Other files like `SFLuaDialog.cs` and `SFLuaEnvironment.cs` manage the Lua scripting environment and game dialogs.

### SFMap
This folder contains all the logic for loading, saving, and managing SpellForce maps.
- **MapGen:** Contains tools for procedural map generation.
- `SFMap.cs`: The main class representing a game map.
- The various `SFMap...Manager.cs` files (e.g., `SFMapBuildingManager.cs`, `SFMapUnitManager.cs`, `SFMapDecorationManager.cs`) are responsible for managing specific types of objects and data on the map.
- Other files like `SFMapHeightMap.cs`, `SFMapTerrainTextureManager.cs`, and `SFMapOcean.cs` handle the physical terrain and appearance of the map.

### SFResources
This folder contains a generic resource management system.
- `SFResourceManager.cs`: Manages loading and unloading of game resources.
- `SFResource.cs` & `SFResourceContainer.cs`: Represent individual resources and their containers.

### SFSound
This folder handles the sound and audio engine.
- `SFSoundEngine.cs`: The main class for managing and playing sounds.
- `StreamResource.cs`: Likely handles streaming audio from files.

### SFUnPak
This folder contains tools for unpacking SpellForce's `.pak` files, which are archives containing game assets.
- `SFUnPak.cs`: The main class for unpacking `.pak` files.
- `SFPakFileSystem.cs`: Provides a file system interface for accessing files within the `.pak` archives.
- `SFPakMap.cs`: Manages the mapping of files within a `.pak` archive.

## Root Files
- `SFEngine.csproj`: The C# project file for the SFEngine library.
- `StringUtils.cs`: Contains utility functions for string manipulation.
- `Utility.cs`: Contains other general-purpose utility functions.
