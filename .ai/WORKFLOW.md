# AI Agent Workflow Guide for SpellSmut

This guide applies to **ALL AI coding agents** including Claude, GPT-4, Gemini, Qwen, Cursor, Windsurf, Zed, and others.

## 🔴 CRITICAL: Use Beads Issue Tracker

**All development work MUST be tracked in beads**, regardless of which AI agent or IDE you're using.

### Beads Command Location

The beads CLI tool is installed at:
```bash
/root/go/bin/bd
```

Or if on your own machine, ensure `bd` is in your PATH.

### Universal Workflow (Works for All AI Agents)

#### 1. Check for Work
```bash
bd ready
```
Shows unblocked tasks ready to start. This is the same for ALL agents.

#### 2. View Issue Details
```bash
bd show SpellSmut-ISSUE-ID
```
Every issue contains:
- Clear objectives
- Implementation steps
- Acceptance criteria (checkboxes)
- File locations
- Code examples
- Time estimates
- Dependencies

**Read the full description before starting!**

#### 3. Claim Work
```bash
bd update SpellSmut-ISSUE-ID --status in_progress
```

**IMPORTANT:** Only ONE issue should be `in_progress` at a time per agent.

#### 4. Do the Work
- Follow the implementation steps in the issue description
- Check off acceptance criteria as you complete them
- Reference the file locations provided
- Follow the code examples

#### 5. Complete Work
```bash
bd close SpellSmut-ISSUE-ID --reason "Brief completion note"
```

#### 6. Commit Changes
```bash
git add .beads/ <your_files>
git commit -m "feat: your changes"
git push
```

**Always commit `.beads/` directory changes!**

## JSON Output for Programmatic Access

All AI agents can use JSON output:

```bash
# Get ready work as JSON
bd ready --json

# Get specific issue
bd show SpellSmut-ISSUE-ID --json

# List all open issues
bd list --status open --json
```

Example parsing:
```python
import json
import subprocess

result = subprocess.run(['bd', 'ready', '--json'], capture_output=True, text=True)
issues = json.loads(result.stdout)

for issue in issues:
    print(f"ID: {issue['id']}")
    print(f"Title: {issue['title']}")
    print(f"Priority: P{issue['priority']}")
```

## Environment Setup

### For Cursor IDE
Add to your workspace settings (`.vscode/settings.json` or Cursor settings):
```json
{
  "beads.enabled": true,
  "beads.command": "/root/go/bin/bd",
  "beads.autoCheck": true
}
```

### For Windsurf IDE
Check `cascade.md` file for beads integration instructions.

### For Zed IDE
Add to your project settings:
```json
{
  "tasks": {
    "beads-ready": {
      "command": "/root/go/bin/bd ready"
    }
  }
}
```

### For Terminal-Based Agents (Qwen, etc.)
Beads works via standard shell commands - no special setup needed.

## Issue Structure

All 73 issues follow a consistent structure:

```markdown
Title: Clear description of task

OBJECTIVE:
What needs to be accomplished and why

CONTEXT:
Background information

IMPLEMENTATION STEPS:
1. Specific step
2. Another step
[code examples]

ACCEPTANCE CRITERIA:
- [ ] Criterion 1
- [ ] Criterion 2

FILES INVOLVED:
- path/to/file.py
- path/to/another.py

ESTIMATED TIME: X hours

DEPENDENCIES:
- Depends on: SpellSmut-XXX
- Blocks: SpellSmut-YYY

REFERENCES:
- ProjectPlanning/relevant_doc.md
```

## Creating New Issues

Any AI agent can create issues:

```bash
bd create "Description of task" -p PRIORITY -t TYPE -d "Detailed description"
```

**Priority:** 0=critical, 1=high, 2=medium, 3=low
**Type:** bug, feature, task

**Good issue descriptions include:**
- Clear objective
- Implementation approach
- Acceptance criteria
- File locations
- Time estimate

## Dependencies

View dependency trees:
```bash
bd dep tree SpellSmut-ISSUE-ID
```

Add dependencies:
```bash
# CHILD depends on PARENT (blocking)
bd dep add SpellSmut-CHILD SpellSmut-PARENT --type blocks

# Subtask relationship
bd dep add SpellSmut-SUBTASK SpellSmut-EPIC --type parent-child
```

## Integration with Different AI Models

### Claude (Anthropic)
- Reads `.claude/instructions.md` (symlinked to this file)
- Session start hook shows beads reminder
- Slash commands available

### GPT-4 / Copilot (OpenAI)
- Read this file in your context window
- Use beads commands in terminal
- Follow JSON output examples

### Gemini (Google)
- Standard shell command integration
- Parse JSON output as needed
- Follow this workflow guide

### Qwen (Alibaba)
- Terminal-based workflow
- Standard Unix commands
- JSON parsing available

### Cursor IDE
- Integrated terminal for beads commands
- Can create keyboard shortcuts
- Workspace settings support

### Windsurf IDE
- Check cascade configuration
- Terminal integration
- Project-level beads setup

### Zed IDE
- Task integration
- Terminal access
- Project commands

## Project Context

**Current State:**
- 73 total issues in beads
- 18 parent epics with 52 subtasks
- Hierarchical organization with dependencies
- All issues have detailed descriptions

**Priority Issues:**
- P0 (Critical): Icon mapping, texture blending
- P1 (High): Engine-core architecture, CFF parser, Lua integration
- P2 (Medium): 3D models, validation, animations, GUI Phase 5
- P3 (Low): Mod management, advanced editors

**Common Commands:**
```bash
bd ready                    # Show available work
bd list --status open       # All open issues
bd show SpellSmut-ISSUE-ID  # Issue details
bd update ID --status in_progress  # Claim work
bd close ID                 # Complete work
```

## Documentation

- **Contributing:** [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Project Overview:** [ProjectPlanning/PROJECT_OVERVIEW.md](../ProjectPlanning/PROJECT_OVERVIEW.md)
- **Current Status:** [ProjectPlanning/Status/CURRENT_STATUS.md](../ProjectPlanning/Status/CURRENT_STATUS.md)
- **Beads Documentation:** https://github.com/ben-vargas/ai-beads

## Getting Help

1. Check existing beads issues: `bd list`
2. Read project documentation in `ProjectPlanning/`
3. Create a question issue: `bd create "Question about X" -t task -p 2`

## Testing Your Setup

Run this test to verify beads is working:

```bash
# Should show ready work
bd ready

# Should show ~73 issues
bd list | wc -l

# Should show detailed issue
bd show SpellSmut-9z0
```

If any command fails, check:
1. Is beads installed? (`which bd` or check `/root/go/bin/bd`)
2. Is `.beads/` directory present?
3. Are you in the SpellSmut project directory?

## Rules for ALL AI Agents

1. ✅ **Always check beads first** - Run `bd ready` before starting work
2. ✅ **Read full issue descriptions** - They contain detailed implementation guidance
3. ✅ **Mark in progress** - Update status before coding
4. ✅ **Only one active** - One issue `in_progress` at a time
5. ✅ **Close when complete** - Mark done and commit `.beads/` changes
6. ✅ **Create subtasks** - Break down large work into smaller issues
7. ✅ **Follow acceptance criteria** - Check off items as you complete them

---

**This workflow is the same for Claude, GPT-4, Gemini, Qwen, Cursor, Windsurf, Zed, and any other AI agent!**
