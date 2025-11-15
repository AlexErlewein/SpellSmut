# Contributing to SpellSmut

Thank you for contributing to SpellSmut! This document outlines our development workflow.

## 🔴 Required: Beads Issue Tracker

**All development work MUST be tracked in beads.** This applies to:
- Human developers
- AI coding agents (Claude, etc.)
- Automated scripts
- Any code changes

### Why Beads?

Beads is a distributed, git-backed issue tracker designed for AI-agent collaboration. It provides:
- Long-term memory across sessions
- Dependency tracking
- Ready work detection
- Git-versioned history
- No central server needed

### Installation

Beads is already installed in this repository at `/root/go/bin/bd`.

If working on your own machine:
```bash
curl -fsSL https://raw.githubusercontent.com/steveyegge/beads/main/scripts/install.sh | bash
```

## Workflow

### 1. Find Work

```bash
# See unblocked work ready to start
bd ready

# View specific issue
bd show SpellSmut-ISSUE-ID

# List all open issues
bd list --status open
```

### 2. Claim Work

```bash
# Mark as in progress (REQUIRED before starting)
bd update SpellSmut-ISSUE-ID --status in_progress
```

**Rule:** Only ONE issue should be `in_progress` at a time per agent/developer.

### 3. Do the Work

- Read the full issue description (it has implementation guidance!)
- Follow acceptance criteria checkboxes
- Reference file locations provided
- Check dependencies

### 4. Complete Work

```bash
# Close the issue
bd close SpellSmut-ISSUE-ID --reason "Brief completion note"

# Commit beads changes with your code
git add .beads/ src/...
git commit -m "feat: your changes"
git push
```

### 5. Create New Issues (When Needed)

```bash
# Discovered new work?
bd create "Description of task" -p PRIORITY -t TYPE

# Priority: 0=critical, 1=high, 2=medium, 3=low
# Type: bug, feature, task

# Add dependencies if needed
bd dep add CHILD-ID PARENT-ID --type blocks
```

## Issue Guidelines

### When to Create Issues

✅ **DO create issues for:**
- New features or enhancements
- Bug fixes
- Refactoring tasks
- Documentation improvements
- Research tasks

❌ **DON'T create issues for:**
- Trivial typo fixes (just fix it)
- Single-line comment additions
- Formatting changes (use linter)

### Issue Quality

Good issues have:
- Clear, descriptive title
- Detailed description (see existing issues for examples)
- Appropriate priority (0-3)
- Correct type (bug/feature/task)
- Dependencies specified

All issues in this repo have been enhanced with:
- Implementation steps
- Acceptance criteria
- File locations
- Time estimates
- References

Follow this pattern when creating new issues.

## Dependencies

Understanding issue dependencies:

```bash
# Show dependency tree
bd dep tree SpellSmut-ISSUE-ID

# Add blocking dependency (CHILD depends on PARENT)
bd dep add SpellSmut-CHILD SpellSmut-PARENT --type blocks

# Add parent-child relationship (for epics/subtasks)
bd dep add SpellSmut-SUBTASK SpellSmut-EPIC --type parent-child
```

**Types:**
- `blocks`: Task B must complete before task A
- `parent-child`: Epic/subtask relationship
- `related`: Soft connection
- `discovered-from`: Auto-created by AI

## Branching Strategy

- Main development branch: `main`
- AI agent branches: `claude/feature-name-SESSION-ID`
- Always work on feature branches
- Create PRs for review

## Commit Messages

Follow conventional commits:
```
feat: add icon mapping system
fix: resolve texture blending bug
docs: update beads workflow guide
refactor: separate engine from UI
test: add CFF parser tests
```

Include issue references:
```
feat: implement multi-layer texture blending

Completes SpellSmut-6l2
Addresses SpellSmut-7f1, SpellSmut-kls, SpellSmut-9at
```

## Testing

- All code changes should include tests
- Run test suite before committing: `pytest`
- Update beads issue with test results

## Code Review

1. AI agents: Self-review code before marking complete
2. Humans: Request review via PR
3. Check beads status: Are acceptance criteria met?

## Communication

- Issues: Use beads for task tracking
- Discussions: GitHub Discussions or Discord
- Documentation: Update ProjectPlanning/ docs
- Questions: Open an issue with `type: question`

## Getting Help

- **Beads usage**: See `.ai/WORKFLOW.md` (universal guide for all AI agents)
- **Project structure**: See `ProjectPlanning/PROJECT_OVERVIEW.md`
- **Current status**: See `ProjectPlanning/Status/CURRENT_STATUS.md`
- **Beads docs**: https://github.com/ben-vargas/ai-beads

## Special Notes for AI Agents

AI coding agents (Claude, GPT-4, Gemini, Qwen, Cursor, Windsurf, Zed, etc.) should:

1. **Always check beads first** - Don't start work without checking `bd ready`
2. **Read full issue descriptions** - They contain detailed implementation guidance
3. **Update status in real-time** - Mark in_progress before starting, close when done
4. **Create subtasks** - Break down large work into smaller beads issues
5. **Commit .beads/ changes** - Always include beads updates in commits

See `.ai/WORKFLOW.md` for the universal AI agent workflow guide (works for ALL agents).

## Questions?

Open an issue with type `question` or check existing documentation in `ProjectPlanning/`.

---

**Remember: All work goes through beads! 📋**
