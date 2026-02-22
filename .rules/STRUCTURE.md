# SpellSmut Project Structure - Quick Reference

**Last Updated:** February 22, 2026
**Status:** ✅ Current
**Location:** `.rules/STRUCTURE.md` (Project rules directory)

---

## 📁 Root Directory (Keep Clean!)

```
SpellSmut/
├── README.md              # Main project documentation
├── pyproject.toml         # Python project configuration
├── pytest.ini             # Pytest configuration
├── uv.lock                # UV dependency lock file
├── .gitignore             # Git ignore rules
├── .gitattributes         # Git attributes
├── .luarc.json            # Lua configuration
├── package.json           # Node.js configuration
├── _config.yml            # Jekyll/GitHub Pages configuration
└── package-lock.json      # Node.js dependencies
```

**Rule:** Only essential configuration files belong in root!
**Note:** `STRUCTURE.md` lives in `.rules/` directory

---

## 🧪 Tests (`src/tests/`)

```
src/tests/
├── README.md                     # Testing guide
├── conftest.py                   # Pytest fixtures and configuration
│
├── test_*.py                     # Test modules
│   ├── test_armor_names.py
│   ├── test_cff_extract.py
│   ├── test_quest_*.py          # Quest system tests
│   ├── test_spell_*.py          # Spell system tests
│   ├── test_weapon_*.py         # Weapon system tests
│   └── test_widget_*.py         # Widget tests
│
├── test_data/                    # Test data & pytest artifacts
│   ├── README.md                 # Test data documentation
│   ├── .gitignore                # Ignore pytest outputs
│   ├── test_integration_ids.json # Test data (committed)
│   ├── test_weapon_ids.json      # Test data (committed)
│   ├── .pytest_cache/            # Pytest cache (gitignored)
│   ├── tmp/                      # Pytest temp files (gitignored)
│   ├── .coverage                 # Coverage data (gitignored)
│   └── htmlcov/                  # Coverage reports (gitignored)
│
├── test_outputs/                 # Test outputs (gitignored)
│   ├── test_export/
│   ├── test_spell_export/
│   └── test_template_export/
│
└── docs/                         # Test documentation
    └── [test-specific guides]
```

**Running tests:**
```bash
cd SpellSmut
uv run pytest src/tests/
```

---

## 📚 Documentation (`docs/`)

```
docs/
├── README.md                     # Documentation index
├── Development/                  # Development docs
│   ├── SESSION_SUMMARY.md
│   └── [planning notes]
├── Extraction/                   # Asset extraction guides
├── Guides/                       # User guides and tutorials
├── Project/                      # Project-level documentation
├── Site/                         # Jekyll/GitHub Pages site
└── Tools/                        # Tool documentation
```

---

## 🤖 AI Assistant Instructions (`.ai/`)

```
.ai/
├── README.md                     # AI instructions overview
├── CLAUDE.md                     # Claude assistant config
├── CRUSH.md                      # Crush assistant config
├── GEMINI.md                     # Gemini assistant config
├── QWEN.md                       # Qwen assistant config
├── WINDSURF.md                   # Windsurf AI assistant config
├── RULES.md                      # ⚠️ CRITICAL: Folder structure rules
├── WORKFLOW.md                   # Beads issue tracking workflow
├── shortcuts.md                  # Keyboard shortcuts reference
└── settings.local.json           # Local AI settings (gitignored)
```

**Purpose:** Configuration files for AI assistants working on the project.

---

## ⚙️ Project Rules (`.rules/`)

```
.rules/
├── RULES.md                      # ⚠️ CRITICAL: Folder structure rules
└── STRUCTURE.md                  # This file - Project structure reference
```

**Purpose:** Project structure and organization rules.

---

## 📋 Project Planning (`ProjectPlanning/`)

```
ProjectPlanning/
├── README.md                     # Planning documentation index
├── PROJECT_OVERVIEW.md           # Overall project overview
├── COMPREHENSIVE_PROJECT_PLAN.md # Detailed project plan
├── TODO.md                       # Project-wide TODO list
│
├── Components/                   # Component-specific planning
│   ├── QUEST_CREATION_PLAN.md
│   ├── SPELL_CREATION_PLAN.md
│   ├── WEAPON_CREATION_PLAN.md
│   ├── LAUNCH_QUEST_EDITOR.md
│   ├── QuestViewerDocumentation.md
│   ├── Spell_Icon_Mapping.md
│   └── [other component plans]
│
├── Status/                       # Current status documents
│   ├── BLOCKERS.md
│   ├── CURRENT_STATUS.md
│   ├── COMPLETED_WORK.md
│   ├── QUEST_CREATION_STATUS.md
│   ├── CurrentStatusQuestEditor.md
│   ├── QUEST_EDITOR_FIXES_TODO.md
│   ├── SPELL_CREATION_STATUS.md
│   ├── WEAPON_CREATION_STATUS.md
│   ├── SESSION_RESUME_NOTES.md
│   ├── SESSION_SUMMARY.md
│   ├── ITM_EXTRACTION_COMPLETE.md
│   ├── ITM_INTEGRATION_COMPLETE.md
│   ├── QUEST_INTEGRATION_SUMMARY.md
│   └── WEAPON_CREATOR_STATUS.md
│
├── Research/                     # Research and analysis
│   ├── SpellForce_Quest_Modding_Example_Quest.md
│   ├── SpellForce_Quest_Modding_Workflow.md
│   ├── SpellForce_P1_Quest_Script_Index.md
│   └── [other research documents]
│
└── Archive/                      # Archived planning documents
    └── [obsolete plans]
```

---

## 💻 Source Code (`src/`)

```
src/
├── TirganachReloaded/
│   ├── README.md                # Main README (updated)
│   ├── LICENSE                  # Project license
│   ├── run_cff_editor.py       # Launch GUI editor
│   ├── run_map_viewer.py       # Launch map viewer
│   │
│   ├── cff_editor/              # CFF Editor GUI application
│   │   ├── main_window.py
│   │   ├── data_model.py
│   │   ├── widgets/             # GUI widgets
│   │   │   ├── quest_editor.py
│   │   │   ├── spell_creator_wizard.py
│   │   │   ├── weapon_forge_wizard.py
│   │   │   ├── armor_forge_wizard.py
│   │   │   ├── enhanced_weapon_browser.py
│   │   │   ├── enhanced_armor_browser.py
│   │   │   └── docs/            # Widget-specific documentation
│   │   ├── models/              # Data models
│   │   ├── exporters/           # Export functionality
│   │   ├── shared/              # Shared utilities (ID manager, etc.)
│   │   └── templates/           # Templates
│   │
│   ├── tirganach/               # Core CFF parsing library
│   │   ├── __init__.py
│   │   ├── entities.py
│   │   ├── fields.py
│   │   ├── structure.py
│   │   └── types.py
│   │
│   ├── data/                    # Reference data files
│   │   ├── README.md            # Data directory documentation
│   │   ├── MIGRATION_NOTE.md    # project_ids.json migration notes
│   │   ├── id_name_mappings.json       # ID to name mappings
│   │   ├── project_ids.json     # Project ID tracking (used by wizards)
│   │   ├── ui_icon_mapping.json        # UI icon mappings (43 MB)
│   │   └── weapon_icon_mapping.json    # Weapon icon atlas data
│   │
│   ├── docs/                    # Documentation
│   │   ├── CFF_EDITOR_README.md
│   │   ├── CFF_FORMAT_EXPLANATION.md
│   │   ├── FORMAT_COMPARISON.md
│   │   ├── JSON_EXPORT_GUIDE.md
│   │   ├── XML_EXPORT_GUIDE.md
│   │   ├── INSTALLATION.md
│   │   └── SCRIPTS_GUIDE.md
│   │
│   ├── examples/                # Example scripts & utilities
│   │   ├── README.md
│   │   ├── cff_modding_examples.py
│   │   ├── analyze_events.py   # Quest event analysis
│   │   ├── export_to_json.py
│   │   ├── export_to_xml.py
│   │   └── [other examples]
│   │
│   ├── scripts/                 # Utility scripts
│   │   ├── json_utils.py
│   │   ├── split_json.py
│   │   ├── check_end.py
│   │   ├── count_lines.py
│   │   ├── find_tab_methods.py
│   │   └── find_tab_pages.py
│   │
│   ├── map_viewer/              # Map Viewer application
│   │   ├── README.md
│   │   ├── QUICKSTART.md
│   │   ├── PHASE2_PROGRESS.md
│   │   ├── IMPLEMENTATION_PLAN.md
│   │   ├── MAP_FORMAT_DISCOVERED.md
│   │   ├── map_viewer_window.py
│   │   ├── chunk_map_loader.py
│   │   ├── simple_map_loader.py
│   │   ├── camera.py
│   │   ├── dds_loader.py
│   │   ├── analyze_map.py       # Map analysis utility
│   │   └── [other map viewer files]
│   │
│   ├── tests/                   # TirganachReloaded-specific tests
│   │   ├── README.md
│   │   ├── test_armor_forge.py
│   │   └── test_weapon_forge.py
│   │
│   ├── exports/                 # Exported data (gitignored)
│   │   ├── README.md
│   │   ├── .gitignore
│   │   ├── GameData.json        # 73 MB (gitignored)
│   │   ├── GameData.xml         # 63 MB (gitignored)
│   │   └── c2003_items.json     # 3.3 MB (gitignored)
│   │
│   ├── armor_forge.py           # Armor creation system
│   ├── enhanced_armor.json      # Active armor database (656 KB)
│   └── enhanced_weapons.json    # Active weapon database (349 KB)
│
├── OrthancsSchmiede/            # Standalone item browser application
│   ├── README.md               # Application documentation (updated Nov 2025)
│   ├── run_orthancs_schmiede.py # Launcher script
│   ├── orthancs_schmiede.py    # Main application window
│   ├── cff_weapon_loader.py    # Enhanced weapon data extraction from CFF
│   ├── cff_armor_loader.py     # Enhanced armor data extraction from CFF
│   ├── cff_npc_loader.py       # NPC data extraction from CFF
│   └── custom_weapons/         # Custom weapon data
│
└── tests/                        # Main test suite (see Tests section)
```

---

## 🎮 Game Files

```
OriginalGameFiles/               # Original game data (untouched)
ModdedGameFiles/                 # Modified game files
ExtractedAssets/                 # Extracted game assets
├── UI/                          # User interface assets
└── [other asset types]
ModdingTools/                    # Third-party modding tools
```

---

## 🎯 Quick Navigation Guide

### Want to...

**Run the CFF Editor?**
```bash
cd SpellSmut/src/TirganachReloaded
uv run python run_cff_editor.py
```

**Run the Map Viewer?**
```bash
cd SpellSmut/src/TirganachReloaded
uv run python run_map_viewer.py
```

**Run OrthancsSchmiede (Item Browser)?**
```bash
cd SpellSmut/src/OrthancsSchmiede
uv run python run_orthancs_schmiede.py
```

**Run tests?**
```bash
cd SpellSmut
uv run pytest src/tests/
```

**Run specific test?**
```bash
cd SpellSmut
uv run pytest src/tests/test_weapon_names.py -v
```

**Add a new test?**
1. Create `src/tests/test_<feature>.py`
2. Add test data to `src/tests/test_data/` if needed
3. Test outputs go to `src/tests/test_outputs/` (gitignored)

**Add documentation?**
- Development docs → `docs/Development/`
- User guides → `docs/Guides/`
- Widget docs → `src/TirganachReloaded/cff_editor/widgets/docs/`
- Test docs → `src/tests/docs/`
- Planning docs → `ProjectPlanning/`
- Status docs → `ProjectPlanning/Status/`

**Configure AI assistant?**
- Edit files in `.ai/`
- Follow rules in `.ai/RULES.md` or `.rules/RULES.md`

---

## 📋 File Placement Rules (Quick Reference)

| File Type | Location | Example |
|-----------|----------|---------|
| Test scripts | `src/tests/` | `test_weapon_names.py` |
| Test data | `src/tests/test_data/` | `test_weapon_ids.json` |
| Test outputs | `src/tests/test_outputs/` | `test_export/` |
| Test docs | `src/tests/docs/` | `TEST_GUIDE.md` |
| User guides | `docs/Guides/` | `QUEST_GUIDE.md` |
| Dev notes | `docs/Development/` | `SESSION_SUMMARY.md` |
| Widget docs | `src/.../widgets/docs/` | `WEAPON_FORGE_TODO.md` |
| AI configs | `.ai/` | `CLAUDE.md` |
| Project rules | `.rules/` | `RULES.md`, `STRUCTURE.md` |
| Planning | `ProjectPlanning/` | `FEATURE_PLAN.md` |
| Status | `ProjectPlanning/Status/` | `CURRENT_STATUS.md` |
| Research | `ProjectPlanning/Research/` | `QUEST_RESEARCH.md` |
| Config files | Root | `pyproject.toml` |
| Utility scripts | `src/TirganachReloaded/scripts/` | `count_lines.py` |
| Example scripts | `src/TirganachReloaded/examples/` | `analyze_events.py` |
| Map utilities | `src/TirganachReloaded/map_viewer/` | `analyze_map.py` |

---

## ⚠️ Critical Rules

### ❌ NEVER Place in Root:
- Test files (`test_*.py`)
- Test data files (`test_*.json`)
- Documentation files (except README.md)
- Session summaries
- Planning documents
- AI instruction files
- Widget documentation
- Temporary files
- Export outputs
- Structure documentation
- Utility/helper scripts

### ✅ ALWAYS:
- Put tests in `src/tests/`
- Put user docs in `docs/`
- Put dev notes in `docs/Development/`
- Put AI configs in `.ai/`
- Put project rules in `.rules/`
- Put planning in `ProjectPlanning/`
- Put utility scripts in `src/TirganachReloaded/scripts/`
- Keep root directory clean!

---

## 🧹 Post-Merge Cleanup Checklist

 - **Ensure root whitelist is clean.** Allowed files: `README.md`, `pyproject.toml`, `pytest.ini`, `uv.lock`, `.gitignore`, `.gitattributes`, `.luarc.json`, `package.json`, `package-lock.json`, `_config.yml`.
 - **Move any stray tests/docs/AI files.** Follow the "File Placement Rules" table above.
 - **Re-run tests.** `uv run pytest src/tests/`
 - **Commit cleanup if needed.** Use a message like: `chore: post-merge cleanup (structure compliance)`.

---

## 🔍 Finding Things

### Search Commands

```bash
# Find all test files
find src/tests -name "test_*.py"

# Find all documentation
find docs -name "*.md"

# Find widget docs
find src/TirganachReloaded/cff_editor/widgets/docs -name "*.md"

# Find AI configs
ls .ai/*.md

# Find project rules
ls .rules/*.md

# Find planning documents
find ProjectPlanning -name "*.md"

# Check root is clean
ls -1 *.py *.json *.md 2>/dev/null | grep -v README.md
```

---

## 📊 Project Statistics

- **Root files:** 10 (config files only)
- **Test modules:** 20+
- **Test organization:** Fully structured
- **Documentation:** Categorized by purpose
- **AI configs:** Separate .ai directory
- **Project rules:** Separate .rules directory
- **Planning:** Organized in ProjectPlanning/

---

## 🚀 Getting Started

1. **Read this file** for quick orientation
2. **Check `.rules/RULES.md`** for complete folder structure rules
3. **See `README.md`** for project overview
4. **Browse `docs/`** for guides and documentation
5. **Run tests** to verify setup: `uv run pytest src/tests/`

---

## 📮 More Information

- **Complete folder rules:** `.rules/RULES.md`
- **Testing guide:** `src/tests/README.md`
- **AI setup:** `.ai/README.md`
- **Development docs:** `docs/Development/`
- **Project main:** `README.md`
- **Planning docs:** `ProjectPlanning/README.md`

---

**Questions?** Check the docs or relevant README files.
**Adding files?** Follow `.rules/RULES.md` for proper placement.
**Running code?** Always use `uv run` for Python scripts.

---

**Maintained by:** SpellSmut Development Team
**Version:** 1.1 (February 2026)
