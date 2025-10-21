# Zed IDE Project-Specific Settings Guide

## Table of Contents
- [Overview](#overview)
- [Project Settings File](#project-settings-file)
- [Common Project Settings](#common-project-settings)
- [SpellSmut-Specific Configuration](#spellsmut-specific-configuration)
- [AI Assistant Configuration](#ai-assistant-configuration)
- [Language-Specific Settings](#language-specific-settings)
- [Advanced Configuration](#advanced-configuration)
- [Examples](#examples)

---

## Overview

Zed IDE allows you to configure project-specific settings that override your global user settings. This is useful for:

- **Team consistency**: Ensure all contributors use the same formatting
- **Project-specific rules**: Define rules for specific technologies (Lua, etc.)
- **AI behavior**: Configure Claude's behavior for this project
- **Language servers**: Project-specific LSP configurations
- **Formatting rules**: Project-specific code style

---

## Project Settings File

### Location

Zed looks for project settings in:

```
<project-root>/.zed/settings.json
```

For SpellSmut, this would be:
```
H:\SpellSmut\.zed\settings.json
```

### Creating the File

```bash
# From your project root
cd H:\SpellSmut
mkdir .zed
# Then create settings.json in that directory
```

Or you can use Zed's command palette:
1. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
2. Type "Open Project Settings"
3. Zed will create `.zed/settings.json` if it doesn't exist

---

## Common Project Settings

### Basic Template

```json
{
  "tab_size": 4,
  "hard_tabs": false,
  "soft_wrap": "editor_width",
  "formatter": "auto",
  "remove_trailing_whitespace_on_save": true,
  "ensure_final_newline_on_save": true
}
```

### Editor Settings

```json
{
  "tab_size": 4,
  "hard_tabs": false,
  "soft_wrap": "preferred_line_length",
  "preferred_line_length": 100,
  "show_whitespaces": "selection",
  "show_indent_guides": true,
  "indent_guides": {
    "enabled": true,
    "coloring": "indent_aware"
  },
  "scroll_beyond_last_line": "one_page",
  "vertical_scroll_margin": 3,
  "relative_line_numbers": false,
  "seed_search_query_from_cursor": "always"
}
```

### File Settings

```json
{
  "remove_trailing_whitespace_on_save": true,
  "ensure_final_newline_on_save": true,
  "format_on_save": "on",
  "autosave": "on_focus_change",
  "file_types": {
    "Lua": ["lua"],
    "Markdown": ["md"],
    "JSON": ["json"]
  }
}
```

### Git Integration

```json
{
  "git": {
    "enabled": true,
    "autoFetch": true,
    "autoFetchInterval": 300,
    "gutter": "tracked_files"
  },
  "project_panel": {
    "git_status": true
  }
}
```

---

## SpellSmut-Specific Configuration

### Recommended Settings for SpellSmut

```json
{
  "tab_size": 4,
  "hard_tabs": false,
  "soft_wrap": "preferred_line_length",
  "preferred_line_length": 100,
  "formatter": "auto",
  "remove_trailing_whitespace_on_save": true,
  "ensure_final_newline_on_save": true,
  
  "lsp": {
    "lua-language-server": {
      "settings": {
        "Lua.runtime.version": "Lua 5.4",
        "Lua.diagnostics.globals": [
          "UtlMod",
          "ObjectLibrary",
          "SoundLibrary",
          "DrwSoundId",
          "SndDrwEventSamples",
          "dir_readdirectory",
          "readfile",
          "doscript",
          "list_insert",
          "list_concat",
          "list_converttoset",
          "tkeys",
          "Find",
          "FindAnim",
          "FindBones",
          "FindMesh",
          "GetSoundFile"
        ],
        "Lua.workspace.library": [
          "${workspaceFolder}/OriginalGameFiles/script"
        ]
      }
    }
  },
  
  "languages": {
    "Lua": {
      "tab_size": 4,
      "hard_tabs": false,
      "format_on_save": "on",
      "formatter": "language_server"
    },
    "Markdown": {
      "tab_size": 2,
      "soft_wrap": "preferred_line_length",
      "preferred_line_length": 80
    }
  },
  
  "file_types": {
    "Lua": ["lua"],
    "Markdown": ["md"],
    "TGA": ["tga"],
    "PAK": ["pak"]
  },
  
  "excluded_files": [
    "**/*.pak",
    "**/*.bik",
    "**/*.tga",
    "**/*.dll",
    "**/*.exe"
  ],
  
  "git": {
    "enabled": true,
    "gutter": "tracked_files"
  }
}
```

---

## AI Assistant Configuration

### Claude-Specific Settings

Zed allows you to configure AI assistant behavior per-project:

```json
{
  "assistant": {
    "enabled": true,
    "default_model": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022"
    },
    "version": "2"
  },
  
  "context_servers": {
    "github": {
      "enabled": true
    }
  }
}
```

### Project Context for AI

You can provide context through a `.zed/project-instructions.md` file (see below).

---

## Language-Specific Settings

### Lua Configuration

```json
{
  "languages": {
    "Lua": {
      "tab_size": 4,
      "hard_tabs": false,
      "format_on_save": "on",
      "formatter": {
        "language_server": {
          "name": "lua-language-server"
        }
      },
      "code_actions_on_format": {
        "source.organizeImports": true
      }
    }
  },
  
  "lsp": {
    "lua-language-server": {
      "binary": {
        "path": "lua-language-server",
        "arguments": []
      },
      "settings": {
        "Lua.runtime.version": "Lua 5.4",
        "Lua.runtime.path": [
          "?.lua",
          "?/init.lua"
        ],
        "Lua.diagnostics.globals": [
          "UtlMod",
          "ObjectLibrary",
          "SoundLibrary"
        ],
        "Lua.workspace.checkThirdParty": false,
        "Lua.completion.callSnippet": "Replace",
        "Lua.format.enable": true
      }
    }
  }
}
```

### Markdown Configuration

```json
{
  "languages": {
    "Markdown": {
      "tab_size": 2,
      "hard_tabs": false,
      "soft_wrap": "preferred_line_length",
      "preferred_line_length": 80,
      "format_on_save": "off"
    }
  }
}
```

---

## Advanced Configuration

### Custom Snippets

```json
{
  "snippets": {
    "Lua": {
      "sound_event": {
        "prefix": "sound",
        "body": [
          "${1:sound_name} = {",
          "    File = \"${2:filename}\",",
          "    Volume = ${3:1.0},",
          "    FallOffMin = ${4:10},",
          "    FallOffMax = ${5:90}",
          "}"
        ],
        "description": "Create a sound event"
      },
      "mod_asset": {
        "prefix": "modasset",
        "body": [
          "return {",
          "    Bones = {${1}},",
          "    Anims = {${2}},",
          "    Meshes = {${3}},",
          "    BattleSounds = {${4}}",
          "}"
        ],
        "description": "Create mod asset manifest"
      }
    }
  }
}
```

### Custom Tasks

```json
{
  "tasks": [
    {
      "label": "Run SpellForce",
      "command": "OriginalGameFiles\\SpellForce.exe",
      "args": [],
      "cwd": "${workspaceFolder}\\OriginalGameFiles"
    },
    {
      "label": "Run SpellForce Mod Tool",
      "command": "OriginalGameFiles\\SpellForce_mod.exe",
      "args": [],
      "cwd": "${workspaceFolder}\\OriginalGameFiles"
    }
  ]
}
```

### File Exclusions

```json
{
  "file_scan_exclusions": [
    "**/.git",
    "**/node_modules",
    "**/*.pak",
    "**/*.bik",
    "**/*.tga",
    "**/*.dll",
    "**/*.exe",
    "**/*.ico"
  ],
  
  "excluded_files": [
    "**/*.pak",
    "**/*.bik",
    "**/*.dll",
    "**/*.exe"
  ]
}
```

---

## Examples

### Example 1: Minimal SpellSmut Settings

**File**: `H:\SpellSmut\.zed\settings.json`

```json
{
  "tab_size": 4,
  "hard_tabs": false,
  "remove_trailing_whitespace_on_save": true,
  "ensure_final_newline_on_save": true,
  
  "lsp": {
    "lua-language-server": {
      "settings": {
        "Lua.runtime.version": "Lua 5.4",
        "Lua.diagnostics.globals": [
          "UtlMod",
          "ObjectLibrary",
          "SoundLibrary",
          "DrwSoundId"
        ]
      }
    }
  },
  
  "excluded_files": [
    "**/*.pak",
    "**/*.bik",
    "**/*.tga",
    "**/*.dll",
    "**/*.exe"
  ]
}
```

### Example 2: Full Featured Configuration

**File**: `H:\SpellSmut\.zed\settings.json`

```json
{
  "tab_size": 4,
  "hard_tabs": false,
  "soft_wrap": "preferred_line_length",
  "preferred_line_length": 100,
  "formatter": "auto",
  "format_on_save": "on",
  "remove_trailing_whitespace_on_save": true,
  "ensure_final_newline_on_save": true,
  "show_indent_guides": true,
  
  "assistant": {
    "enabled": true,
    "default_model": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022"
    }
  },
  
  "lsp": {
    "lua-language-server": {
      "settings": {
        "Lua.runtime.version": "Lua 5.4",
        "Lua.diagnostics.globals": [
          "UtlMod",
          "ObjectLibrary",
          "SoundLibrary",
          "DrwSoundId",
          "SndDrwEventSamples",
          "dir_readdirectory",
          "readfile",
          "doscript",
          "list_insert",
          "list_concat",
          "list_converttoset",
          "tkeys",
          "Find",
          "FindAnim",
          "FindBones",
          "FindMesh",
          "GetSoundFile"
        ],
        "Lua.workspace.library": [
          "${workspaceFolder}/OriginalGameFiles/script"
        ],
        "Lua.workspace.checkThirdParty": false,
        "Lua.format.enable": true
      }
    }
  },
  
  "languages": {
    "Lua": {
      "tab_size": 4,
      "hard_tabs": false,
      "format_on_save": "on",
      "formatter": "language_server"
    },
    "Markdown": {
      "tab_size": 2,
      "soft_wrap": "preferred_line_length",
      "preferred_line_length": 80,
      "format_on_save": "off"
    }
  },
  
  "file_types": {
    "Lua": ["lua"],
    "Markdown": ["md"]
  },
  
  "file_scan_exclusions": [
    "**/.git",
    "**/*.pak",
    "**/*.bik",
    "**/*.tga",
    "**/*.dll",
    "**/*.exe",
    "**/*.ico"
  ],
  
  "excluded_files": [
    "**/*.pak",
    "**/*.bik",
    "**/*.dll",
    "**/*.exe"
  ],
  
  "git": {
    "enabled": true,
    "gutter": "tracked_files"
  },
  
  "project_panel": {
    "git_status": true
  }
}
```

### Example 3: Team Collaboration Settings

**File**: `H:\SpellSmut\.zed\settings.json`

```json
{
  "tab_size": 4,
  "hard_tabs": false,
  "remove_trailing_whitespace_on_save": true,
  "ensure_final_newline_on_save": true,
  "format_on_save": "on",
  
  "collaboration": {
    "channel_id": null
  },
  
  "lsp": {
    "lua-language-server": {
      "settings": {
        "Lua.runtime.version": "Lua 5.4",
        "Lua.diagnostics.globals": [
          "UtlMod",
          "ObjectLibrary",
          "SoundLibrary"
        ]
      }
    }
  },
  
  "git": {
    "enabled": true,
    "gutter": "tracked_files"
  }
}
```

---

## Project Instructions for AI

### Creating Context for Claude

Create a file at `.zed/project-instructions.md` to give Claude context about your project:

**File**: `H:\SpellSmut\.zed\project-instructions.md`

````markdown
# SpellSmut Project Instructions

## Project Overview
This is a SpellForce Platinum Edition modding project. The game uses Lua 4.0 scripts with C++ engine bindings.

## Code Style
- Use 4 spaces for indentation (no tabs)
- Keep lines under 100 characters
- Use descriptive variable names
- Comment complex logic

## Lua Conventions
- Global functions use PascalCase: `FindAnim()`, `GetSoundFile()`
- Local variables use snake_case: `local mod_dir`
- Tables use lowercase: `local data = {}`

## Project Structure
- `OriginalGameFiles/script/` - Original Lua scripts
- `docs/` - Documentation
- `mods/` - Custom modifications

## Important Notes
- Original Lua version is 4.0 (not 5.x)
- Many C++ functions are exposed to Lua
- PAK files contain compressed game assets
- Modding system allows asset merging

## Common Tasks
- Audio system improvements
- Lua script modernization
- Mod development
- Documentation updates
````

---

## Environment-Specific Settings

### Development Environment

```json
{
  "editor": {
    "show_line_numbers": true,
    "show_git_diff_gutter": true,
    "show_code_actions": true
  },
  
  "terminal": {
    "working_directory": "current_project_directory",
    "shell": "system"
  },
  
  "diagnostics": {
    "include_warnings": true
  }
}
```

### Production/Release Environment

```json
{
  "format_on_save": "on",
  "remove_trailing_whitespace_on_save": true,
  "ensure_final_newline_on_save": true,
  
  "diagnostics": {
    "include_warnings": true
  }
}
```

---

## Keyboard Shortcuts (Project-Specific)

While keyboard shortcuts are typically global, you can document project-specific workflows:

**File**: `.zed/shortcuts.md`

```markdown
# Project Shortcuts

## Lua Development
- `Ctrl+Shift+P` → "Lua: Format Document"
- `Ctrl+Shift+P` → "Lua: Restart Language Server"

## Git Operations
- `Ctrl+Shift+G` → Open Git panel
- `Ctrl+Enter` → Commit changes

## AI Assistant
- `Ctrl+Enter` → Send to Claude
- `Ctrl+Shift+A` → Open Assistant panel
```

---

## Troubleshooting

### Settings Not Applied

1. **Check file location**: Must be `.zed/settings.json` in project root
2. **Validate JSON**: Use a JSON validator to check syntax
3. **Restart Zed**: Close and reopen the project
4. **Check logs**: `Ctrl+Shift+P` → "Zed: Open Log"

### LSP Not Working

1. **Install Lua Language Server**: `brew install lua-language-server` (Mac) or download for Windows
2. **Check LSP status**: Bottom-right corner of Zed shows LSP status
3. **Restart LSP**: `Ctrl+Shift+P` → "Restart Language Server"

### Settings Conflict

Project settings override user settings. To debug:
1. Open user settings: `Ctrl+,`
2. Compare with project settings
3. Project settings take precedence

---

## Version Control

### Should You Commit `.zed/settings.json`?

**Yes, if:**
- Team project with shared conventions
- Specific LSP configurations needed
- Project-specific formatting rules

**No, if:**
- Personal preferences vary
- IDE-specific configurations
- Sensitive information included

### Recommended `.gitignore`

```gitignore
# Optional: ignore personal Zed settings
# .zed/settings.json

# But keep project instructions
!.zed/project-instructions.md
```

Or commit settings but allow local overrides:

```gitignore
.zed/settings.local.json
```

Then use `settings.local.json` for personal overrides.

---

## Quick Setup Guide

### Step-by-Step Setup for SpellSmut

1. **Create directory**:
   ```bash
   cd H:\SpellSmut
   mkdir .zed
   ```

2. **Create settings file**:
   Copy the "Full Featured Configuration" example above into `.zed/settings.json`

3. **Create project instructions**:
   Create `.zed/project-instructions.md` with project context for Claude

4. **Install Lua Language Server** (if not installed):
   - Windows: Download from [lua-language-server releases](https://github.com/LuaLS/lua-language-server/releases)
   - Mac: `brew install lua-language-server`

5. **Restart Zed**:
   Close and reopen the project

6. **Verify**:
   - Open a `.lua` file
   - Check LSP status in bottom-right
   - Test formatting with `Ctrl+Shift+P` → "Format Document"

---

## Additional Resources

- [Zed Documentation](https://zed.dev/docs)
- [Zed Settings Reference](https://zed.dev/docs/configuring-zed)
- [Lua Language Server Docs](https://luals.github.io/)

---

*Last Updated: 2025-10-18*  
*For SpellSmut Project*  
*Zed IDE Version: Latest*