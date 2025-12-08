# Beads Quick Reference Card

Quick reference for all AI agents (Claude, GPT-4, Gemini, Qwen, etc.)

## Essential Commands

```bash
bd ready                           # Show unblocked work
bd show SpellSmut-ISSUE-ID         # View issue details
bd update ID --status in_progress  # Claim work
bd close ID                        # Complete work
bd list --status open              # List all open issues
bd create "Task" -p 0 -t feature   # Create issue
bd dep tree ID                     # Show dependencies
```

## Priorities

- `0` = Critical (P0) - Blockers
- `1` = High (P1) - Important
- `2` = Medium (P2) - Normal
- `3` = Low (P3) - Nice-to-have

## Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - General work item

## Status Values

- `open` - Not started
- `in_progress` - Currently working
- `completed` - Done

## JSON Output

```bash
bd ready --json                    # Machine-readable
bd show ID --json                  # Parse with jq/python
bd list --status open --json       # All issues
```

## Workflow

1. `bd ready` → Pick issue
2. `bd show ID` → Read details
3. `bd update ID --status in_progress` → Claim it
4. Do the work (follow acceptance criteria)
5. `bd close ID` → Mark complete
6. Commit `.beads/` changes

## Issue Structure

Every issue has:
- Objective (what & why)
- Implementation steps
- Acceptance criteria (checkboxes)
- File locations
- Time estimate
- Dependencies
- References

## One Issue at a Time

Only ONE issue should be `in_progress` per agent.

## Documentation

- `.ai/WORKFLOW.md` - Full workflow guide
- `CONTRIBUTING.md` - Contributing guidelines
- `ProjectPlanning/` - Project docs

---

**Same commands for ALL AI agents!**
