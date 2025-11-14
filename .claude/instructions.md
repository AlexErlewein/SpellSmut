# AI Agent Instructions for SpellSmut Project

## 🔴 CRITICAL: Use Beads Issue Tracker

This project uses **beads** (`bd` command) for all task tracking. You MUST interact with beads for any development work.

### Before Starting ANY Task

1. **Check for existing issues:**
   ```bash
   /root/go/bin/bd ready
   ```
   This shows unblocked work ready to start.

2. **Search for related issues:**
   ```bash
   /root/go/bin/bd list | grep "keyword"
   ```

3. **View issue details:**
   ```bash
   /root/go/bin/bd show ISSUE-ID
   ```
   Read the full description for context, acceptance criteria, and implementation guidance.

### During Development

1. **Mark issue as in progress:**
   ```bash
   /root/go/bin/bd update ISSUE-ID --status in_progress
   ```

2. **Only ONE issue should be in_progress at a time**

3. **If you discover new work, create an issue:**
   ```bash
   /root/go/bin/bd create "Description of new task" -p PRIORITY -t TYPE
   ```
   Priority: 0=critical, 1=high, 2=medium, 3=low
   Type: bug, feature, task

4. **Add dependencies if needed:**
   ```bash
   /root/go/bin/bd dep add CHILD-ID PARENT-ID --type blocks
   ```

### After Completing Work

1. **Close the issue:**
   ```bash
   /root/go/bin/bd close ISSUE-ID --reason "Completed implementation"
   ```

2. **Commit changes that include beads updates:**
   - The `.beads/` directory tracks all issue changes
   - Always commit and push `.beads/` changes

### Issue Hierarchy

Issues use parent-child relationships:
- **Parent issues** = Epics (high-level features)
- **Child issues** = Subtasks (specific implementation steps)

Always work on child/subtask issues, not parent epics directly.

### JSON Output for Automation

Use `--json` flag for programmatic access:
```bash
/root/go/bin/bd ready --json | jq '.[] | select(.priority == 0)'
```

### Examples

**Good Workflow:**
```bash
# 1. Check ready work
/root/go/bin/bd ready

# 2. Pick issue SpellSmut-i3t
/root/go/bin/bd show SpellSmut-i3t

# 3. Mark in progress
/root/go/bin/bd update SpellSmut-i3t --status in_progress

# 4. Do the work...

# 5. Complete
/root/go/bin/bd close SpellSmut-i3t --reason "Found mapping data in PAK files"

# 6. Commit
git add .beads/ && git commit -m "fix: resolve icon mapping"
```

**Bad Workflow:**
```bash
# ❌ Starting work without checking beads
# ❌ Not marking issues as in_progress
# ❌ Not closing completed issues
# ❌ Not committing .beads/ changes
```

## Issue Structure

All 73 issues have been enhanced with:
- ✅ Clear objectives
- ✅ Implementation steps
- ✅ Acceptance criteria (checkboxes)
- ✅ File locations
- ✅ Time estimates
- ✅ Dependencies
- ✅ References to docs

**Read the full issue description before starting work!**

## Current Project State

- **73 total issues** in the tracker
- **18 parent epics** with **52 subtasks**
- **10+ unblocked issues** ready to start
- **Hierarchical organization** with dependencies

## Critical Issues (P0)

- `SpellSmut-9z0`: Icon handle-to-atlas mapping (BLOCKER)
- `SpellSmut-6l2`: Multi-layer texture blending

Always prioritize P0 issues unless explicitly instructed otherwise.

## Integration Points

Beads integrates with:
- Git (auto-sync via hooks)
- ProjectPlanning/ docs (references in descriptions)
- ID Manager (for content creators)

## Getting Help

- View this file: `.claude/instructions.md`
- Project docs: `ProjectPlanning/`
- Beads docs: `https://github.com/ben-vargas/ai-beads`

---

**Remember: ALL development tasks must go through beads!**
