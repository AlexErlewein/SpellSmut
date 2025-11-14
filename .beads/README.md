# Beads Issue Tracker for SpellSmut

This directory contains the beads issue tracking database for the SpellSmut project.

## What is Beads?

Beads is a distributed, git-backed issue tracker designed specifically for AI coding agents. It provides:
- Long-term memory across sessions
- Dependency tracking with 4 relationship types
- Ready work detection (shows only unblocked tasks)
- Git-versioned storage (auto-syncs)
- Hash-based collision-resistant IDs

## Current Project State

- **73 total issues** created from ProjectPlanning documents
- **18 parent epics** with **52 detailed subtasks**
- **Hierarchical organization** with dependencies
- **All issues enhanced** with detailed descriptions, acceptance criteria, and implementation guidance

## Quick Commands

```bash
# Show ready work (unblocked tasks)
bd ready

# View issue details (has full implementation guide!)
bd show SpellSmut-ISSUE-ID

# Start work (required before coding)
bd update SpellSmut-ISSUE-ID --status in_progress

# Complete work
bd close SpellSmut-ISSUE-ID --reason "Done!"

# Create new issue
bd create "Task description" -p PRIORITY -t TYPE

# View dependency tree
bd dep tree SpellSmut-ISSUE-ID
```

## Files in This Directory

- `beads.db` - SQLite database (gitignored)
- `issues.jsonl` - JSONL export (git-tracked)
- `beads.left.jsonl` - Left side of git merge (git-tracked)
- `config.yaml` - Beads configuration
- `metadata.json` - Repository metadata

## Git Integration

Beads automatically:
- Exports to JSONL after CRUD operations (5s debounce)
- Imports from JSONL when newer than DB (after git pull)
- Syncs across machines via git
- Handles merge conflicts intelligently

**Always commit `.beads/` changes with your code!**

## Issue Quality

All 73 issues have been enhanced with:
- ✅ Clear objectives and context
- ✅ Implementation steps with code examples
- ✅ Acceptance criteria (checkboxes)
- ✅ File locations and references
- ✅ Time estimates
- ✅ Dependencies and blockers
- ✅ Links to ProjectPlanning docs

## Workflow for AI Agents

1. **Check ready work first**: `bd ready`
2. **Read full issue description**: `bd show ISSUE-ID`
3. **Mark in progress**: `bd update ISSUE-ID --status in_progress`
4. **Do the work** (following acceptance criteria)
5. **Close when done**: `bd close ISSUE-ID`
6. **Commit changes**: `git add .beads/ && git commit`

## Documentation

- **Contributors**: See [../CONTRIBUTING.md](../CONTRIBUTING.md)
- **AI Agents**: See [../.claude/instructions.md](../.claude/instructions.md)
- **Project Overview**: See [../ProjectPlanning/PROJECT_OVERVIEW.md](../ProjectPlanning/PROJECT_OVERVIEW.md)
- **Beads Documentation**: https://github.com/ben-vargas/ai-beads

## Support

Questions about beads or the issue tracker? See documentation or create an issue with type `question`.

---

**All development work goes through beads - no exceptions!**
