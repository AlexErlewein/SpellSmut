# SpellSmut Project Structure - Quick Reference

**Last Updated:** October 2025  
**Status:** ✅ Current

---

## 📁 Root Directory (Keep Clean!)

```
SpellSmut/
├── README.md              # Main project documentation
├── STRUCTURE.md           # This file - quick reference
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
└── RULES.md                      # ⚠️ CRITICAL: Folder structure rules
```

**Purpose:** Configuration files for AI assistants working on the project.

---

## 💻 Source Code (`src/`)

```
src/
├── TirganachReloaded/
│   ├── README.md                # Main README (updated)
│   ├── LICENSE                  # Project license
│   ├── run_cff_editor.py       # Launch GUI editor
│   │
│   ├── cff_editor/              # CFF Editor GUI application
│   │   ├── main_window.py
│   │   ├── data_model.py
│   │   ├── widgets/             # GUI widgets
│   │   │   ├── quest_editor.py
│   │   │   ├── spell_creator_wizard.py
│   │   │   ├── weapon_forge_wizard.py
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
│   │   ├── export_to_json.py
│   │   ├── export_to_xml.py
│   └── [other examples]
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
ProjectPlanning/                 # Planning and strategy documents
```

---

## 🎯 Quick Navigation Guide

### Want to...

**Run the CFF Editor?**
```bash
cd SpellSmut/src/TirganachReloaded
uv run python run_cff_editor.py
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

**Configure AI assistant?**
- Edit files in `.ai/`
- Follow rules in `.ai/RULES.md`

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
| Planning | `ProjectPlanning/` | `FEATURE_PLAN.md` |
| Config files | Root | `pyproject.toml` |

---

## ⚠️ Critical Rules

### ❌ NEVER Place in Root:
- Test files (`test_*.py`)
- Test data files (`test_*.json`)
- Documentation files (except README.md and STRUCTURE.md)
- Session summaries
- Planning documents
- AI instruction files
- Widget documentation
- Temporary files
- Export outputs

### ✅ ALWAYS:
- Put tests in `src/tests/`
- Put user docs in `docs/`
- Put dev notes in `docs/Development/`
- Put AI configs in `.ai/`
- Keep root directory clean!

---

## 🧹 Post-Merge Cleanup Checklist

 - **Ensure root whitelist is clean.** Allowed files: `README.md`, `STRUCTURE.md`, `pyproject.toml`, `pytest.ini`, `uv.lock`, `.gitignore`, `.gitattributes`, `.luarc.json`, `package.json`, `package-lock.json`, `_config.yml`.
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

# Check root is clean
ls -1 *.py *.json *.md 2>/dev/null | grep -v README.md | grep -v STRUCTURE.md
```

---

## 📊 Project Statistics

- **Root files:** 12 (config files only)
- **Test modules:** 20+
- **Test organization:** Fully structured
- **Documentation:** Categorized by purpose
- **AI configs:** Separate hidden directory

---

## 🚀 Getting Started

1. **Read this file** for quick orientation
2. **Check `.ai/RULES.md`** for complete folder structure rules
3. **See `README.md`** for project overview
4. **Browse `docs/`** for guides and documentation
5. **Run tests** to verify setup: `uv run pytest src/tests/`

---

## 📮 More Information

- **Complete folder rules:** `.ai/RULES.md`
- **Testing guide:** `src/tests/README.md`
- **AI setup:** `.ai/README.md`
- **Development docs:** `docs/Development/`
- **Project main:** `README.md`

---

**Questions?** Check the docs or relevant README files.  
**Adding files?** Follow `.ai/RULES.md` for proper placement.  
**Running code?** Always use `uv run` for Python scripts.

---

**Maintained by:** SpellSmut Development Team  
**Version:** 1.0