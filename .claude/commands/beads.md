---
description: Show beads ready work and usage guide
---

# Beads Issue Tracker Quick Reference

## 🎯 Ready Work

Show unblocked issues ready to start:

```bash
/root/go/bin/bd ready
```

## 📖 Common Commands

```bash
# View issue details
bd show SpellSmut-ISSUE-ID

# Mark as in progress (do this BEFORE starting work!)
bd update SpellSmut-ISSUE-ID --status in_progress

# Complete issue
bd close SpellSmut-ISSUE-ID --reason "Brief note"

# List all open issues
bd list --status open

# Create new issue
bd create "Task description" -p PRIORITY -t TYPE

# Show dependency tree
bd dep tree SpellSmut-ISSUE-ID

# Get JSON output (for automation)
bd ready --json
```

## 🔴 Required Workflow

1. **Check beads first** - Always run `bd ready` before starting work
2. **Read full issue** - Run `bd show ISSUE-ID` to see implementation details
3. **Mark in progress** - Update status before coding
4. **Only one active** - One issue `in_progress` at a time
5. **Close when done** - Mark complete and commit `.beads/` changes

## 📊 Current Status

Run this to see project stats:
```bash
bd list --status open | wc -l  # Count open issues
bd ready | head -10             # Top 10 ready tasks
```

## 🔗 Full Documentation

- Contributing: [CONTRIBUTING.md](../CONTRIBUTING.md)
- AI Instructions: [.claude/instructions.md](../.claude/instructions.md)
- Beads Docs: https://github.com/ben-vargas/ai-beads

---

**Remember: ALL development work must go through beads!**
