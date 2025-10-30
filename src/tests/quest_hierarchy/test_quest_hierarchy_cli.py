"""
Command-line Quest Hierarchy Viewer
Prints quest hierarchy in a text-based tree format
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from TirganachReloaded.cff_editor.data_model import CFFDataModel


class QuestHierarchyPrinter:
    """Print quest hierarchy as text tree"""

    def __init__(self):
        self.data_model = CFFDataModel()
        self.quest_nodes = {}

    def load_and_print(self, cff_path):
        """Load CFF file and print quest hierarchy"""
        print(f"Loading: {cff_path}")
        print("=" * 80)

        if not self.data_model.load_file(cff_path):
            print("ERROR: Failed to load CFF file")
            return False

        print("✓ CFF file loaded successfully")
        print()

        return self.build_and_print_hierarchy()

    def build_and_print_hierarchy(self):
        """Build quest hierarchy and print it"""
        # Get all quests
        quests = self.data_model.get_elements("quests")
        if not quests:
            print("No quests found in CFF file")
            return False

        print(f"Found {len(quests)} quests")
        print()

        # Build quest node map
        for quest in quests:
            quest_id = getattr(quest, "quest_id", None)
            if quest_id is not None:
                parent_id = getattr(quest, "parent_quest_id", None)
                order_index = getattr(quest, "order_index", 0)

                # Get quest name (try localized first)
                name = self.data_model.get_localised_text(quest, "name")
                if not name:
                    name = getattr(quest, "name", f"Quest {quest_id}")

                self.quest_nodes[quest_id] = {
                    "quest": quest,
                    "quest_id": quest_id,
                    "name": name,
                    "parent_id": parent_id,
                    "order_index": order_index,
                    "children": [],
                }

        # Build parent-child relationships
        root_quests = []
        orphaned_quests = []

        for quest_id, node in self.quest_nodes.items():
            parent_id = node["parent_id"]
            if parent_id and parent_id != 0:
                if parent_id in self.quest_nodes:
                    # Add as child to parent
                    self.quest_nodes[parent_id]["children"].append(quest_id)
                else:
                    # Orphaned quest (parent doesn't exist)
                    orphaned_quests.append(quest_id)
                    root_quests.append(quest_id)  # Treat as root
            else:
                # Root level quest (no parent)
                root_quests.append(quest_id)

        # Sort children by order_index
        for node in self.quest_nodes.values():
            node["children"].sort(key=lambda qid: self.quest_nodes[qid]["order_index"])

        # Sort root quests by order_index
        root_quests.sort(key=lambda qid: self.quest_nodes[qid]["order_index"])

        # Print statistics
        print("QUEST HIERARCHY STATISTICS")
        print("-" * 80)
        print(f"Total Quests:     {len(self.quest_nodes)}")
        print(f"Main Quests:      {len(root_quests)}")
        print(f"Sub-quests:       {len(self.quest_nodes) - len(root_quests)}")
        if orphaned_quests:
            print(f"Orphaned Quests:  {len(orphaned_quests)} (parent not found)")
        print()

        # Print hierarchy
        print("QUEST HIERARCHY TREE")
        print("=" * 80)
        for quest_id in root_quests:
            is_orphaned = quest_id in orphaned_quests
            self.print_quest_branch(quest_id, "", True, is_orphaned)

        return True

    def print_quest_branch(self, quest_id, prefix, is_last, is_orphaned=False):
        """Print a quest and its children recursively"""
        node = self.quest_nodes[quest_id]

        # Prepare the tree characters
        if not prefix:
            # Root level
            connector = ""
        else:
            connector = "└── " if is_last else "├── "

        # Quest type indicator
        if node["parent_id"] is None or node["parent_id"] == 0:
            type_marker = "[MAIN]"
        else:
            if node["children"]:
                type_marker = "[SUB+]"  # Sub-quest with children
            else:
                type_marker = "[SUB]"

        # Orphaned indicator
        orphan_marker = " ⚠️ ORPHANED" if is_orphaned else ""

        # Print quest line
        print(
            f"{prefix}{connector}{type_marker} {node['name']} (ID: {quest_id}, Order: {node['order_index']}){orphan_marker}"
        )

        # Print children
        child_count = len(node["children"])
        for i, child_id in enumerate(node["children"]):
            is_last_child = i == child_count - 1

            # Update prefix for children
            if not prefix:
                child_prefix = "    "
            else:
                child_prefix = prefix + ("    " if is_last else "│   ")

            self.print_quest_branch(child_id, child_prefix, is_last_child)

    def print_flat_list(self):
        """Print a flat list of all quests sorted by ID"""
        print()
        print("FLAT QUEST LIST (sorted by ID)")
        print("=" * 80)

        sorted_quests = sorted(self.quest_nodes.items(), key=lambda x: x[0])

        for quest_id, node in sorted_quests:
            parent_str = (
                f"Parent: {node['parent_id']}" if node["parent_id"] else "Parent: None"
            )
            child_str = f"Children: {len(node['children'])}"
            print(
                f"[{quest_id:4d}] {node['name']:50s} | {parent_str:15s} | {child_str}"
            )


def main():
    """Run the command-line viewer"""
    # Check for CFF file argument
    if len(sys.argv) > 1:
        cff_path = sys.argv[1]
    else:
        # Try default path
        default_path = (
            Path.home()
            / "Desktop"
            / "code"
            / "Others"
            / "SpellSmut"
            / "data"
            / "spellforce.cff"
        )
        if default_path.exists():
            cff_path = str(default_path)
        else:
            print("Usage: python test_quest_hierarchy_cli.py <path_to_cff_file>")
            print()
            print("Or place spellforce.cff in: ~/Desktop/code/Others/SpellSmut/data/")
            return 1

    printer = QuestHierarchyPrinter()

    if printer.load_and_print(cff_path):
        # Also print flat list for reference
        printer.print_flat_list()
        print()
        print("✓ Quest hierarchy printed successfully")
        return 0
    else:
        print("✗ Failed to print quest hierarchy")
        return 1


if __name__ == "__main__":
    sys.exit(main())
