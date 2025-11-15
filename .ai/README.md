# AI Assistant Instructions

## 📍 Location: `.ai/` folder

This **hidden directory** contains instructions and guidelines for various AI assistants working on the SpellSmut project.

## Purpose

These files provide context, rules, and project-specific information to AI assistants to ensure consistent and high-quality contributions to the codebase.

## 🔴 CRITICAL: Beads Issue Tracker

**ALL AI assistants MUST use beads for task tracking.**

Beads is a distributed, git-backed issue tracker. Quick commands:
```bash
bd ready              # Show available work
bd show SpellSmut-ID  # View issue details
bd update ID --status in_progress  # Claim work
bd close ID           # Complete work
```

📖 **See `WORKFLOW.md` for complete beads workflow guide.**

---

## 🤖 Which File for Which AI?

**IMPORTANT:** Each AI assistant should read their own specific file from this `.ai/` folder:

| AI Assistant | File Location | Purpose |
|--------------|---------------|---------|
| **Claude Code** | `.ai/CLAUDE.md` | Instructions for Anthropic's Claude assistant |
| **Gemini CLI** | `.ai/GEMINI.md` | Instructions for Google's Gemini AI |
| **Qwen** | `.ai/QWEN.md` | Instructions for Qwen assistant |
| **Crush** | `.ai/CRUSH.md` | Instructions for Crush assistant |
| **Windsurf** | `.ai/WINDSURF.md` | Instructions for Windsurf AI assistant |

**All files are in the `.ai/` folder** - NOT in root, NOT in `docs/`!

---

## Files

### CLAUDE.md
**Location:** `.ai/CLAUDE.md`  
Instructions and project rules for Claude (Anthropic's AI assistant). Contains:
- Project architecture overview
- Technology stack details
- Coding standards and conventions
- Python environment management (UV-based)
- File structure analysis
- Folder organization rules

### CRUSH.md
**Location:** `.ai/CRUSH.md`  
Instructions for Crush AI assistant.

### GEMINI.md
**Location:** `.ai/GEMINI.md`  
Instructions for Google's Gemini AI assistant.

### WINDSURF.md
**Location:** `.ai/WINDSURF.md`  
Instructions for Windsurf AI assistant. Contains:
- Complete project overview and current status
- Detailed file organization rules
- Technology stack and development standards
- Game-specific knowledge and guidelines
- Current priorities and development workflow

### QWEN.md
**Location:** `.ai/QWEN.md`  
Instructions for Qwen AI assistant.

### WORKFLOW.md
**Location:** `.ai/WORKFLOW.md`
**CRITICAL:** Universal beads workflow guide for ALL AI assistants.
- How to use beads issue tracker
- Required workflow steps
- JSON output for automation
- IDE integration instructions

ALL AI assistants MUST use beads for task tracking.

### RULES.md
**Location:** `.ai/RULES.md` (also available in root as `RULES.md`)
**CRITICAL:** Complete folder structure rules and file organization conventions.
- Where to place test files
- Where to place documentation
- Where to place source code
- Root directory policy
- Best practices and common mistakes

ALL AI assistants MUST follow the rules in RULES.md when creating or organizing files.

---

## 🎯 Quick Start for AI Assistants

1. **Read beads workflow:** Check `.ai/WORKFLOW.md` - **REQUIRED FOR ALL ASSISTANTS**

2. **Find your file:** Look for your specific instruction file in `.ai/` folder
   - Claude Code? → Read `.ai/CLAUDE.md`
   - Gemini CLI? → Read `.ai/GEMINI.md`
   - Qwen? → Read `.ai/QWEN.md`
   - Crush? → Read `.ai/CRUSH.md`
   - Windsurf? → Read `.ai/WINDSURF.md`
   - Cursor? → Read `.ai/WORKFLOW.md` + IDE integration
   - Zed? → Read `.ai/WORKFLOW.md` + IDE integration

3. **Check beads for work:** Run `bd ready` before starting ANY development

4. **Read the rules:** Check `.ai/RULES.md` for folder organization

5. **Follow standards:** All AI assistants must follow the same organizational rules

---

## Usage for Humans

When working with an AI assistant on this project:

1. **Tell the AI their file location**: Point them to `.ai/CLAUDE.md` or `.ai/GEMINI.md` etc.
2. **Let them read their file**: Each AI should read their specific instruction file
3. **Consistency**: All AI files follow the same standards, just tailored per assistant
4. **Quick onboarding**: New AI assistants can quickly understand project structure

## Key Standards (All Assistants)

### Beads Issue Tracker (MANDATORY)
- **ALWAYS check beads before starting work:** `bd ready`
- **Mark issues in progress:** `bd update ID --status in_progress`
- **Close completed work:** `bd close ID`
- **Read full issue descriptions:** They contain implementation guidance
- **Commit .beads/ changes:** Always include beads updates in commits
- **See WORKFLOW.md for complete guide**

### Python Environment
- **ALWAYS use UV** for package management and execution
- Use `uv run` for all Python scripts
- Use `uv pip install` for dependencies
- **NEVER** use plain `pip` or `python` commands

### File Organization (CRITICAL)
- **Tests** → `src/tests/` (NEVER in root!)
  - Test scripts: `src/tests/test_*.py`
  - Test data: `src/tests/test_data/`
  - Test outputs: `src/tests/test_outputs/`
  - Test docs: `src/tests/docs/`

- **Documentation** → `docs/` or next to code
  - User guides: `docs/Guides/`
  - Development notes: `docs/Development/`
  - Widget docs: `src/TirganachReloaded/cff_editor/widgets/docs/`

- **AI Configs** → `.ai/` (this directory)

- **Root Directory** → Config files ONLY
  - Keep root clean!
  - No test files, no docs, no temporary files

See `RULES.md` for complete folder structure rules.

### Code Style
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write comprehensive docstrings
- Maintain test coverage

### Project Structure
```
SpellSmut/
├── .ai/                      # ← AI assistant instructions (THIS FOLDER!)
│   ├── CLAUDE.md            # ← Claude Code reads this
│   ├── GEMINI.md            # ← Gemini CLI reads this
│   ├── QWEN.md              # ← Qwen reads this
│   ├── CRUSH.md             # ← Crush reads this
│   ├── RULES.md             # ← Folder structure rules
│   └── README.md            # ← This file
├── src/
│   ├── TirganachReloaded/    # Main codebase
│   └── tests/                # Test suite
├── docs/                     # User documentation
└── [config files only]
```

## Maintenance

- **Update Regularly**: Keep these files in sync with project evolution
- **Version Control**: All instruction files are tracked in Git
- **Consistency**: Ensure changes are reflected across all assistant files
- **Follow RULES.md**: All file organization follows RULES.md conventions

## Notes

- These files are internal documentation for AI assistants
- They complement, not replace, human-readable documentation in `/docs`
- They contain technical details that help AI understand the codebase architecture
- **RULES.md is the authoritative source for file organization**

---

**Last Updated**: October 2025  
**Maintained By**: Project contributors