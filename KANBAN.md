# 📋 Visual Kanban Board for SpellSmut

This project uses a **hybrid task tracking approach**:

- **Beads** = Source of truth for AI agents (CLI, dependencies, automation)
- **Kanban Board** = Visual overview for humans (read-only)

## 🚀 Quick Start

### View the Kanban Board

1. **Open in Browser**: Double-click `task-manager.html`
   - Compatible browsers: Chrome 86+, Edge 86+, Opera 72+
   - Firefox and Safari not supported (File System Access API limitation)

2. **Select Folder**: Choose the SpellSmut project folder
   - The tool will read `kanban.md` automatically

3. **View Tasks**: See all open subtasks organized in columns:
   - 📝 **To Do** - Ready to start
   - 🚀 **In Progress** - Currently being worked on
   - 👀 **Review** - Needs review (manual placement)
   - ⏸️ **Blocked** - Waiting on dependencies (manual placement)
   - ✅ **Done** - Completed tasks

## 🔄 Sync Process

### Automatic Sync (Recommended)

The kanban.md file is **automatically updated** after every git commit via a git hook.

```bash
# Just commit as normal - kanban.md updates automatically
git commit -m "feat: implement feature"
# 🔄 Auto-syncing beads → kanban.md...
# ✅ Kanban board updated
```

### Manual Sync

Force a sync at any time:

```bash
# Sync beads to kanban.md manually
uv run scripts/sync_beads_to_kanban.py
```

This is useful when:
- You want to see changes immediately without committing
- You've updated beads and want to refresh the Kanban view
- The git hook failed for some reason

## 📊 What You'll See

### Kanban Features

**Task Format**:
```markdown
### TASK-7f1: [Parent Epic] Subtask title
**Priority**: 🔴 Critical
**Category**: Task
**Tags**: #task
**Created**: 2025-11-14

Brief description of what needs to be done...
```

**Key Points**:
- **Parent topic in brackets**: `[Quest System] Fix dialogue parser`
- **Only subtasks shown**: Parent epics hidden (they're organizational)
- **Priority color-coded**: 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low
- **Sorted by priority**: Highest priority tasks appear first

### Filtering Options

MarkdownTaskManager supports advanced filtering:
- **By Priority**: Click priority badge to filter
- **By Category**: Filter by Feature/Task/Bug
- **By Tags**: Filter by #tag
- **Search**: Global search across all tasks

## ⚠️ Important Notes

### One-Way Sync

The sync is **beads → kanban.md only** (one-way):

✅ **DO**:
- Use beads commands for task management (`bd create`, `bd update`, `bd close`)
- View kanban.md in MarkdownTaskManager for visual overview
- Manually drag tasks to Review/Blocked columns if needed

❌ **DON'T**:
- Edit kanban.md manually (changes will be overwritten)
- Create new tasks in MarkdownTaskManager (use beads instead)
- Rely on kanban.md as source of truth (beads is the source)

### For AI Agents

AI agents should **always use beads** for task management:

```bash
# Check for work
bd ready

# Start work
bd update SpellSmut-ISSUE-ID --status in_progress

# Complete work
bd close SpellSmut-ISSUE-ID --reason "Done"
```

The Kanban board is for **human visualization only**.

### For Humans

Humans can:
- ✅ View the Kanban board for project overview
- ✅ Filter and search tasks visually
- ✅ Manually move tasks to Review/Blocked columns (won't sync back)
- ✅ Use beads CLI for task management if comfortable

Humans should NOT:
- ❌ Edit kanban.md directly
- ❌ Create tasks in MarkdownTaskManager

Instead, ask an AI agent to create tasks via beads, or use beads CLI yourself.

## 🛠️ Technical Details

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Source of Truth: Beads                     │
│                    .beads/beads.db                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ bd export -o .beads/issues.jsonl
                            ▼
                    .beads/issues.jsonl
                            │
                            │ scripts/sync_beads_to_kanban.py
                            ▼
                        kanban.md
                            │
                            │ task-manager.html (read-only view)
                            ▼
                  📋 Visual Kanban Board
```

### Files

| File | Purpose | Git Tracked | Editable |
|------|---------|-------------|----------|
| `.beads/beads.db` | SQLite database (source of truth) | ❌ No (.gitignore) | ✅ Yes (via `bd` commands) |
| `.beads/issues.jsonl` | JSONL export for git tracking | ✅ Yes | ❌ No (auto-generated) |
| `kanban.md` | Kanban board markdown | ✅ Yes | ❌ No (auto-generated) |
| `task-manager.html` | Kanban viewer (single HTML file) | ✅ Yes | ❌ No (external tool) |
| `scripts/sync_beads_to_kanban.py` | Sync script | ✅ Yes | ✅ Yes (if modifying sync logic) |

### Sync Logic

1. **Export beads to JSONL**: `bd export -o .beads/issues.jsonl`
2. **Parse JSONL**: Read all 73 issues
3. **Filter subtasks**: Keep only 52 subtasks (hide 21 parent epics)
4. **Add parent topics**: Prepend `[Parent Title]` to each subtask
5. **Group by column**: Map status to Kanban columns
6. **Sort by priority**: Order tasks within columns
7. **Generate markdown**: Write kanban.md in MarkdownTaskManager format

### Columns

| Kanban Column | Beads Status | Notes |
|---------------|--------------|-------|
| 📝 To Do | `status: open` | Auto-populated |
| 🚀 In Progress | `status: in_progress` | Auto-populated |
| 👀 Review | *manual* | Manually move tasks here |
| ⏸️ Blocked | *manual* | Manually move tasks here |
| ✅ Done | `status: closed` | Auto-populated |

**Note**: Review and Blocked columns exist for manual task organization in the Kanban view. They don't sync back to beads.

## 🔧 Customization

### Change Sync Behavior

Edit `scripts/sync_beads_to_kanban.py`:

```python
# Show all issues (including parent epics)
def filter_subtasks_only(self) -> List[Dict]:
    return self.issues  # Don't filter

# Change column mapping
STATUS_TO_COLUMN = {
    "open": "📝 Backlog",      # Rename columns
    "in_progress": "🔨 Active",
    "closed": "🎉 Shipped",
}

# Disable parent prefix
def format_task_title(self, issue: Dict) -> str:
    return issue['title']  # No parent prefix
```

### Disable Auto-Sync

Remove the git hook:

```bash
rm .git/hooks/post-commit
```

Then sync manually when needed:

```bash
uv run scripts/sync_beads_to_kanban.py
```

## 📚 Additional Resources

- **Beads Documentation**: https://github.com/ben-vargas/ai-beads
- **MarkdownTaskManager**: https://github.com/ioniks/MarkdownTaskManager
- **Beads Workflow**: See `.ai/WORKFLOW.md`
- **Contributing Guide**: See `CONTRIBUTING.md`

---

**Remember**: Beads is the source of truth. The Kanban board is a visual overlay! 📋
