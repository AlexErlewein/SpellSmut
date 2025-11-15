#!/usr/bin/env python3
"""
Sync beads issues to MarkdownTaskManager kanban.md format.

This script provides a visual Kanban board view of beads issues for humans,
while AI agents continue using beads CLI for task management.

Usage:
    uv run scripts/sync_beads_to_kanban.py
    uv run scripts/sync_beads_to_kanban.py --watch  # Watch mode (future)
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class BeadsToKanbanSync:
    """Convert beads JSONL to MarkdownTaskManager kanban.md format."""

    # Priority mapping
    PRIORITY_MAP = {
        0: "🔴 Critical",
        1: "🟠 High",
        2: "🟡 Medium",
        3: "🟢 Low",
    }

    # Status to column mapping
    STATUS_TO_COLUMN = {
        "open": "📝 To Do",
        "in_progress": "🚀 In Progress",
        "closed": "✅ Done",
        # Review and Blocked columns available but not auto-populated
        # Users can manually move tasks in the Kanban board
    }

    # Column order (defines all available columns)
    COLUMNS = [
        "📝 To Do",
        "🚀 In Progress",
        "👀 Review",
        "⏸️ Blocked",
        "✅ Done"
    ]

    def __init__(self, beads_jsonl_path: str, kanban_md_path: str):
        self.beads_jsonl_path = Path(beads_jsonl_path)
        self.kanban_md_path = Path(kanban_md_path)
        self.issues: List[Dict] = []
        self.parent_titles: Dict[str, str] = {}  # issue_id -> title

    def load_beads_issues(self) -> None:
        """Load issues from beads JSONL export."""
        if not self.beads_jsonl_path.exists():
            print(f"❌ Error: {self.beads_jsonl_path} not found")
            print("   Run: /root/go/bin/bd export -o .beads/issues.jsonl")
            sys.exit(1)

        self.issues = []
        with open(self.beads_jsonl_path, 'r') as f:
            for line in f:
                if line.strip():
                    self.issues.append(json.loads(line))

        # Build parent title lookup
        for issue in self.issues:
            self.parent_titles[issue['id']] = issue['title']

        print(f"✓ Loaded {len(self.issues)} issues from beads")

    def get_parent_id(self, issue: Dict) -> Optional[str]:
        """Get parent issue ID if this is a subtask."""
        for dep in issue.get('dependencies', []):
            if dep.get('type') == 'parent-child':
                return dep.get('depends_on_id')
        return None

    def is_subtask(self, issue: Dict) -> bool:
        """Check if issue is a subtask (has parent-child dependency)."""
        return self.get_parent_id(issue) is not None

    def filter_subtasks_only(self) -> List[Dict]:
        """Filter to show only subtasks (not parent epics)."""
        subtasks = [issue for issue in self.issues if self.is_subtask(issue)]
        print(f"✓ Filtered to {len(subtasks)} subtasks (hiding {len(self.issues) - len(subtasks)} parent epics)")
        return subtasks

    def format_task_title(self, issue: Dict) -> str:
        """Format task title with parent topic in brackets."""
        parent_id = self.get_parent_id(issue)
        if parent_id and parent_id in self.parent_titles:
            parent_title = self.parent_titles[parent_id]
            return f"[{parent_title}] {issue['title']}"
        return issue['title']

    def format_task(self, issue: Dict) -> str:
        """Format a single task in MarkdownTaskManager format."""
        task_id = issue['id'].replace('SpellSmut-', 'TASK-')
        title = self.format_task_title(issue)
        priority = self.PRIORITY_MAP.get(issue.get('priority', 3), "🟢 Low")
        issue_type = issue.get('issue_type', 'task')
        created = issue.get('created_at', '')[:10]  # Just the date part

        # Build task in MarkdownTaskManager format
        lines = [
            f"### {task_id}: {title}",
            f"**Priority**: {priority}",
            f"**Category**: {issue_type.capitalize()}",
            f"**Tags**: #{issue_type}",
            f"**Created**: {created}",
            "",
        ]

        # Add description (first paragraph only for kanban view)
        description = issue.get('description', '').strip()
        if description:
            # Take first 200 chars or first paragraph
            first_para = description.split('\n\n')[0]
            if len(first_para) > 200:
                first_para = first_para[:200] + "..."
            lines.append(first_para)
            lines.append("")

        lines.append("---")
        lines.append("")

        return '\n'.join(lines)

    def group_by_column(self, subtasks: List[Dict]) -> Dict[str, List[Dict]]:
        """Group subtasks by Kanban column."""
        columns = defaultdict(list)

        for issue in subtasks:
            status = issue.get('status', 'open')
            column = self.STATUS_TO_COLUMN.get(status, "📝 To Do")
            columns[column].append(issue)

        # Sort by priority within each column
        for column in columns:
            columns[column].sort(key=lambda x: (x.get('priority', 3), x['id']))

        return columns

    def generate_kanban_md(self) -> str:
        """Generate complete kanban.md content."""
        subtasks = self.filter_subtasks_only()
        columns_data = self.group_by_column(subtasks)

        lines = [
            "# SpellSmut Kanban Board",
            "",
            "> **Auto-generated from beads issue tracker**",
            f"> Last sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "> ",
            "> **Source of Truth**: Beads (`.beads/beads.db`)",
            "> **AI Agents**: Use `bd` commands for task management",
            "> **Humans**: Use this Kanban board for visual overview",
            "> ",
            "> ⚠️ **Note**: This file is auto-generated. Manual edits will be overwritten on next sync.",
            "",
            "## ⚙️ Configuration",
            "",
            f"**Columns**: {' | '.join(self.COLUMNS)}",
            "**Categories**: Feature, Task, Bug",
            "**Tags**: #feature, #task, #bug",
            "",
        ]

        # Add each column
        for column in self.COLUMNS:
            task_count = len(columns_data.get(column, []))
            lines.append(f"## {column}")
            lines.append("")

            if column in columns_data and columns_data[column]:
                for issue in columns_data[column]:
                    lines.append(self.format_task(issue))
            else:
                lines.append("*No tasks in this column*")
                lines.append("")

        return '\n'.join(lines)

    def write_kanban_md(self, content: str) -> None:
        """Write kanban.md file."""
        self.kanban_md_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.kanban_md_path, 'w') as f:
            f.write(content)
        print(f"✓ Generated {self.kanban_md_path}")

    def sync(self) -> None:
        """Main sync process."""
        print("🔄 Syncing beads → Kanban...")
        self.load_beads_issues()
        content = self.generate_kanban_md()
        self.write_kanban_md(content)
        print("✅ Sync complete!")
        print(f"📋 Open kanban.md in MarkdownTaskManager to view visual board")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sync beads issues to MarkdownTaskManager kanban.md"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch mode: auto-sync on file changes (future feature)"
    )
    parser.add_argument(
        "--beads-jsonl",
        default=".beads/issues.jsonl",
        help="Path to beads JSONL export (default: .beads/issues.jsonl)"
    )
    parser.add_argument(
        "--output",
        default="kanban.md",
        help="Output kanban.md path (default: kanban.md)"
    )

    args = parser.parse_args()

    if args.watch:
        print("⚠️ Watch mode not yet implemented")
        print("   For now, run this script manually after beads changes")
        sys.exit(1)

    syncer = BeadsToKanbanSync(
        beads_jsonl_path=args.beads_jsonl,
        kanban_md_path=args.output
    )
    syncer.sync()


if __name__ == "__main__":
    main()
