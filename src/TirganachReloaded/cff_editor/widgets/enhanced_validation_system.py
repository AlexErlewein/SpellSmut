#!/usr/bin/env python3
"""
Enhanced Validation System for Quest Editor

Provides comprehensive validation and error checking for quest data,
dialogue trees, conditions, actions, and related content.
"""

import re
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QComboBox, QCheckBox, QGroupBox, QTextEdit,
    QSplitter, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QFrame, QScrollArea, QFormLayout, QPushButtonGroup,
    QDialog, QDialogButtonBox, QSpinBox, QRadioButton, QButtonGroup,
    QCollapsibleButton, QToolButton, QMenu
)
from PySide6.QtCore import Qt, Signal, QThread, pyqtSignal, QTimer
from PySide6.QtGui import QFont, QColor, QIcon, QTextCharFormat, QTextCursor, QBrush

try:
    from TirganachReloaded.cff_editor.models.enhanced_dialogue_models import (
        DialogueTree, DialogueNode, DialogueChoice, DialogueCondition, DialogueAction,
        DialogueConditionType, DialogueActionType
    )
    from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    @classmethod
    def get_color(cls, severity: str) -> QColor:
        """Get color for severity level"""
        colors = {
            cls.INFO.value: QColor(200, 200, 255),  # Light blue
            cls.WARNING.value: QColor(255, 255, 200),  # Light yellow
            cls.ERROR.value: QColor(255, 200, 200),  # Light red
            cls.CRITICAL.value: QColor(255, 150, 150)  # Darker red
        }
        return colors.get(severity, QColor(255, 255, 255))

    @classmethod
    def get_icon(cls, severity: str) -> str:
        """Get icon for severity level"""
        icons = {
            cls.INFO.value: "ℹ️",
            cls.WARNING.value: "⚠️",
            cls.ERROR.value: "❌",
            cls.CRITICAL.value: "🔴"
        }
        return icons.get(severity, "❓")


class ValidationCategory(Enum):
    """Categories for validation issues"""
    QUEST_STRUCTURE = "quest_structure"
    DIALOGUE_FLOW = "dialogue_flow"
    ANSWER_IDS = "answer_ids"
    CONDITIONS = "conditions"
    ACTIONS = "actions"
    VARIABLES = "variables"
    LUA_CODE = "lua_code"
    NAMING = "naming"
    CONNECTIVITY = "connectivity"
    CONSISTENCY = "consistency"


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    id: str
    title: str
    description: str
    severity: ValidationSeverity
    category: ValidationCategory
    item_type: str  # "quest", "node", "choice", "condition", "action"
    item_id: str
    parent_id: Optional[str] = None
    location: str = ""
    suggestion: str = ""
    auto_fixable: bool = False
    fix_action: Optional[str] = None

    def get_severity_display(self) -> str:
        """Get severity display text"""
        return f"{ValidationSeverity.get_icon(self.severity.value)} {self.severity.value.title()}"

    def get_category_display(self) -> str:
        """Get category display text"""
        return self.category.value.replace("_", " ").title()


class ValidationRule:
    """Base class for validation rules"""

    def __init__(self, id: str, title: str, description: str):
        self.id = id
        self.title = title
        self.description = description
        self.enabled = True
        self.severity = ValidationSeverity.WARNING
        self.category = ValidationCategory.CONSISTENCY

    def validate(self, data: dict) -> List[ValidationIssue]:
        """Validate data and return issues"""
        raise NotImplementedError("Subclasses must implement validate")

    def can_fix(self, issue: ValidationIssue) -> bool:
        """Check if this rule can fix the given issue"""
        return False

    def fix_issue(self, issue: ValidationIssue, data: dict) -> Tuple[bool, dict]:
        """Fix the issue and return (success, updated_data)"""
        return False, data


class QuestStructureRule(ValidationRule):
    """Validation rule for quest structure"""

    def __init__(self):
        super().__init__(
            "quest_structure_001",
            "Quest Structure Validation",
            "Validates basic quest structure and required fields"
        )
        self.severity = ValidationSeverity.ERROR
        self.category = ValidationCategory.QUEST_STRUCTURE

    def validate(self, data: dict) -> List[ValidationIssue]:
        """Validate quest structure"""
        issues = []

        quest_info = data.get('quest_info', {})
        quest_data = data.get('quest_data')

        # Check quest ID
        quest_id = quest_info.get('quest_id')
        if not quest_id or quest_id <= 0:
            issues.append(ValidationIssue(
                id="quest_id_missing",
                title="Missing or Invalid Quest ID",
                description="Quest must have a valid positive ID",
                severity=self.severity,
                category=self.category,
                item_type="quest",
                item_id="unknown",
                location="Quest Information",
                suggestion="Set a positive quest ID between 1 and 99999"
            ))

        # Check quest name
        quest_name = quest_info.get('quest_name', '').strip()
        if not quest_name:
            issues.append(ValidationIssue(
                id="quest_name_missing",
                title="Missing Quest Name",
                description="Quest must have a name",
                severity=self.severity,
                category=self.category,
                item_type="quest",
                item_id=str(quest_id or "unknown"),
                location="Quest Information",
                suggestion="Provide a descriptive name for the quest"
            ))
        elif len(quest_name) < 3:
            issues.append(ValidationIssue(
                id="quest_name_too_short",
                title="Quest Name Too Short",
                description="Quest name should be at least 3 characters long",
                severity=ValidationSeverity.WARNING,
                category=self.category,
                item_type="quest",
                item_id=str(quest_id or "unknown"),
                location="Quest Information",
                suggestion="Use a more descriptive quest name"
            ))

        # Check dialogue tree presence
        dialogue_trees = data.get('dialogue_trees', {})
        if not dialogue_trees:
            issues.append(ValidationIssue(
                id="dialogue_tree_missing",
                title="No Dialogue Tree Found",
                description="Quest should have at least one dialogue tree",
                severity=self.severity,
                category=ValidationCategory.DIALOGUE_FLOW,
                item_type="quest",
                item_id=str(quest_id or "unknown"),
                location="Dialogue Trees",
                suggestion="Create a dialogue tree for the quest"
            ))

        return issues


class DialogueFlowRule(ValidationRule):
    """Validation rule for dialogue flow and connectivity"""

    def __init__(self):
        super().__init__(
            "dialogue_flow_001",
            "Dialogue Flow Validation",
            "Validates dialogue tree structure and connectivity"
        )
        self.severity = ValidationSeverity.ERROR
        self.category = ValidationCategory.DIALOGUE_FLOW

    def validate(self, data: dict) -> List[ValidationIssue]:
        """Validate dialogue flow"""
        issues = []
        dialogue_trees = data.get('dialogue_trees', {})

        for tree_id, tree in dialogue_trees.items():
            if not isinstance(tree, dict):
                continue

            nodes = tree.get('nodes', [])
            node_ids = set()
            start_nodes = []
            end_nodes = []

            # Collect node information
            for node in nodes:
                node_id = node.get('node_id')
                if node_id:
                    node_ids.add(node_id)
                    node_type = node.get('node_type', '')
                    if node_type == 'start':
                        start_nodes.append(node_id)
                    elif node_type == 'end':
                        end_nodes.append(node_id)

            # Check for start node
            if not start_nodes:
                issues.append(ValidationIssue(
                    id="start_node_missing",
                    title="No Start Node Found",
                    description=f"Dialogue tree '{tree_id}' must have at least one start node",
                    severity=self.severity,
                    category=self.category,
                    item_type="dialogue_tree",
                    item_id=tree_id,
                    location=f"Dialogue Tree: {tree_id}",
                    suggestion="Add a start node to the dialogue tree"
                ))

            # Check for multiple start nodes
            if len(start_nodes) > 1:
                issues.append(ValidationIssue(
                    id="multiple_start_nodes",
                    title="Multiple Start Nodes Found",
                    description=f"Dialogue tree '{tree_id}' has {len(start_nodes)} start nodes (should have exactly 1)",
                    severity=ValidationSeverity.WARNING,
                    category=self.category,
                    item_type="dialogue_tree",
                    item_id=tree_id,
                    location=f"Dialogue Tree: {tree_id}",
                    suggestion="Remove extra start nodes and keep only one"
                ))

            # Check node connectivity
            all_next_nodes = set()
            orphan_nodes = set()
            unreachable_nodes = set()

            for node in nodes:
                node_id = node.get('node_id')
                if not node_id:
                    continue

                # Check choices and next nodes
                choices = node.get('choices', [])
                if not choices and node.get('node_type') not in ['end', 'start']:
                    # Node has no choices and isn't start/end
                    orphan_nodes.add(node_id)

                for choice in choices:
                    next_node = choice.get('next_node')
                    if next_node:
                        all_next_nodes.add(next_node)

                        # Check if next node exists
                        if next_node not in node_ids:
                            issues.append(ValidationIssue(
                                id="broken_link",
                                title="Broken Dialogue Link",
                                description=f"Choice in node '{node_id}' points to non-existent node '{next_node}'",
                                severity=self.severity,
                                category=ValidationCategory.CONNECTIVITY,
                                item_type="choice",
                                item_id=f"{node_id}_choice",
                                parent_id=node_id,
                                location=f"Dialogue Tree: {tree_id}, Node: {node_id}",
                                suggestion=f"Create node '{next_node}' or update choice destination",
                                auto_fixable=True,
                                fix_action="remove_broken_link"
                            ))

            # Find unreachable nodes (nodes that are never referenced)
            referenced_nodes = set(start_nodes)
            referenced_nodes.update(all_next_nodes)
            unreachable_nodes = node_ids - referenced_nodes

            for orphan_node in orphan_nodes:
                issues.append(ValidationIssue(
                    id="orphan_node",
                    title="Orphaned Node Found",
                    description=f"Node '{orphan_node}' has no choices and is not an end node",
                    severity=ValidationSeverity.WARNING,
                    category=self.category,
                    item_type="node",
                    item_id=orphan_node,
                    location=f"Dialogue Tree: {tree_id}",
                    suggestion="Add choices to the node or mark it as an end node"
                ))

            for unreachable_node in unreachable_nodes:
                issues.append(ValidationIssue(
                    id="unreachable_node",
                    title="Unreachable Node Found",
                    description=f"Node '{unreachable_node}' is never referenced by any choices",
                    severity=ValidationSeverity.WARNING,
                    category=self.category,
                    item_type="node",
                    item_id=unreachable_node,
                    location=f"Dialogue Tree: {tree_id}",
                    suggestion="Add a choice that leads to this node or remove the node"
                ))

        return issues


class AnswerIdRule(ValidationRule):
    """Validation rule for AnswerId consistency and conflicts"""

    def __init__(self):
        super().__init__(
            "answer_id_001",
            "AnswerId Validation",
            "Validates AnswerId assignments and detects conflicts"
        )
        self.severity = ValidationSeverity.ERROR
        self.category = ValidationCategory.ANSWER_IDS

    def validate(self, data: dict) -> List[ValidationIssue]:
        """Validate AnswerId assignments"""
        issues = []
        dialogue_trees = data.get('dialogue_trees', {})

        answer_id_map = {}  # answer_id -> list of (tree_id, node_id, choice_index)
        node_answer_id_map = {}  # answer_id -> list of (tree_id, node_id)

        for tree_id, tree in dialogue_trees.items():
            if not isinstance(tree, dict):
                continue

            nodes = tree.get('nodes', [])

            for node in nodes:
                node_id = node.get('node_id')
                if not node_id:
                    continue

                # Check node-level AnswerId
                node_answer_id = node.get('answer_id')
                if node_answer_id is not None:
                    if node_answer_id in node_answer_id_map:
                        node_answer_id_map[node_answer_id].append((tree_id, node_id))
                    else:
                        node_answer_id_map[node_answer_id] = [(tree_id, node_id)]

                # Check choice-level AnswerIds
                choices = node.get('choices', [])
                for i, choice in enumerate(choices):
                    answer_id = choice.get('answer_id')
                    if answer_id is not None:
                        if answer_id in answer_id_map:
                            answer_id_map[answer_id].append((tree_id, node_id, i))
                        else:
                            answer_id_map[answer_id] = [(tree_id, node_id, i)]

                        # Check for invalid AnswerId values
                        if answer_id <= 0:
                            issues.append(ValidationIssue(
                                id="invalid_answer_id",
                                title="Invalid AnswerId Value",
                                description=f"AnswerId must be positive, found {answer_id}",
                                severity=self.severity,
                                category=self.category,
                                item_type="choice",
                                item_id=f"{node_id}_choice_{i}",
                                parent_id=node_id,
                                location=f"Dialogue Tree: {tree_id}, Node: {node_id}, Choice: {i}",
                                suggestion="Set a positive AnswerId value"
                            ))

        # Check for AnswerId conflicts
        for answer_id, assignments in answer_id_map.items():
            if len(assignments) > 1:
                locations = [f"{tree}:{node}:{choice}" for tree, node, choice in assignments]
                issues.append(ValidationIssue(
                    id="answer_id_conflict",
                    title="AnswerId Conflict Detected",
                    description=f"AnswerId {answer_id} is assigned to {len(assignments)} different choices",
                    severity=self.severity,
                    category=self.category,
                    item_type="choice",
                    item_id=f"conflict_{answer_id}",
                    location=f"Multiple locations: {', '.join(locations)}",
                    suggestion="Assign unique AnswerIds to each choice",
                    auto_fixable=True,
                    fix_action="resolve_answer_id_conflicts"
                ))

        for answer_id, assignments in node_answer_id_map.items():
            if len(assignments) > 1:
                locations = [f"{tree}:{node}" for tree, node in assignments]
                issues.append(ValidationIssue(
                    id="node_answer_id_conflict",
                    title="Node AnswerId Conflict Detected",
                    description=f"AnswerId {answer_id} is assigned to {len(assignments)} different nodes",
                    severity=self.severity,
                    category=self.category,
                    item_type="node",
                    item_id=f"node_conflict_{answer_id}",
                    location=f"Multiple locations: {', '.join(locations)}",
                    suggestion="Assign unique AnswerIds to each node"
                ))

        return issues


class TextContentRule(ValidationRule):
    """Validation rule for text content quality and consistency"""

    def __init__(self):
        super().__init__(
            "text_content_001",
            "Text Content Validation",
            "Validates dialogue text quality and consistency"
        )
        self.severity = ValidationSeverity.WARNING
        self.category = ValidationCategory.NAMING

    def validate(self, data: dict) -> List[ValidationIssue]:
        """Validate text content"""
        issues = []
        dialogue_trees = data.get('dialogue_trees', {})

        # Common text issues to check
        issues_patterns = {
            r'\s+$': "Trailing whitespace",
            r'^\s+': "Leading whitespace",
            r'\s{2,}': "Multiple consecutive spaces",
            r'\.{2,}': "Multiple consecutive dots",
            r'^[^A-Za-zÄÖÜäöüß]': "Text starts with special character",
            r'[^.!?]$': "Text doesn't end with punctuation"
        }

        for tree_id, tree in dialogue_trees.items():
            if not isinstance(tree, dict):
                continue

            nodes = tree.get('nodes', [])

            for node in nodes:
                node_id = node.get('node_id')
                if not node_id:
                    continue

                # Check node text
                node_text = node.get('text', '').strip()
                if node_text:
                    for pattern, issue_desc in issues_patterns.items():
                        if re.search(pattern, node_text):
                            issues.append(ValidationIssue(
                                id="text_issue_node",
                                title=issue_desc,
                                description=f"Node '{node_id}' text has {issue_desc.lower()}",
                                severity=ValidationSeverity.INFO,
                                category=self.category,
                                item_type="node",
                                item_id=node_id,
                                location=f"Dialogue Tree: {tree_id}, Node: {node_id}",
                                suggestion="Clean up the text formatting",
                                auto_fixable=True,
                                fix_action="clean_text_formatting"
                            ))

                    # Check for placeholder text
                    placeholder_patterns = [r'placeholder', r'todo', r'xxx', r'example', r'test']
                    for pattern in placeholder_patterns:
                        if re.search(pattern, node_text, re.IGNORECASE):
                            issues.append(ValidationIssue(
                                id="placeholder_text",
                                title="Placeholder Text Found",
                                description=f"Node '{node_id}' contains placeholder text",
                                severity=self.severity,
                                category=self.category,
                                item_type="node",
                                item_id=node_id,
                                location=f"Dialogue Tree: {tree_id}, Node: {node_id}",
                                suggestion="Replace placeholder text with actual dialogue content"
                            ))
                            break

                # Check choice text
                choices = node.get('choices', [])
                for i, choice in enumerate(choices):
                    choice_text = choice.get('text', '').strip()
                    if choice_text:
                        # Check for empty or very short choices
                        if len(choice_text) < 3:
                            issues.append(ValidationIssue(
                                id="short_choice_text",
                                title="Very Short Choice Text",
                                description=f"Choice {i} in node '{node_id}' is very short",
                                severity=self.severity,
                                category=self.category,
                                item_type="choice",
                                item_id=f"{node_id}_choice_{i}",
                                parent_id=node_id,
                                location=f"Dialogue Tree: {tree_id}, Node: {node_id}, Choice: {i}",
                                suggestion="Use more descriptive choice text"
                            ))

                        # Check for duplicate choices within same node
                        for j, other_choice in enumerate(choices):
                            if i != j and choice_text == other_choice.get('text', '').strip():
                                issues.append(ValidationIssue(
                                    id="duplicate_choice",
                                    title="Duplicate Choice Text",
                                    description=f"Choices {i} and {j} in node '{node_id}' have identical text",
                                    severity=self.severity,
                                    category=self.category,
                                    item_type="choice",
                                    item_id=f"{node_id}_choice_{i}",
                                    parent_id=node_id,
                                    location=f"Dialogue Tree: {tree_id}, Node: {node_id}, Choices: {i}, {j}",
                                    suggestion="Make choices distinct or remove duplicates"
                                ))
                                break

        return issues


class ValidationEngine:
    """Main validation engine"""

    def __init__(self):
        self.rules = []
        self.setup_default_rules()

    def setup_default_rules(self):
        """Setup default validation rules"""
        self.rules = [
            QuestStructureRule(),
            DialogueFlowRule(),
            AnswerIdRule(),
            TextContentRule()
        ]

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule"""
        self.rules.append(rule)

    def remove_rule(self, rule_id: str):
        """Remove a validation rule by ID"""
        self.rules = [rule for rule in self.rules if rule.id != rule_id]

    def validate_data(self, data: dict, enabled_rules: Optional[List[str]] = None) -> List[ValidationIssue]:
        """Validate data and return all issues"""
        all_issues = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            if enabled_rules and rule.id not in enabled_rules:
                continue

            try:
                issues = rule.validate(data)
                all_issues.extend(issues)
            except Exception as e:
                logger.error(f"Error in validation rule {rule.id}: {e}")
                # Add an issue about the validation rule failure
                all_issues.append(ValidationIssue(
                    id=f"rule_error_{rule.id}",
                    title="Validation Rule Error",
                    description=f"Validation rule '{rule.title}' encountered an error: {e}",
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.CONSISTENCY,
                    item_type="system",
                    item_id="validation_error",
                    location="Validation Engine",
                    suggestion="Check validation rule implementation"
                ))

        return all_issues

    def fix_issue(self, issue: ValidationIssue, data: dict) -> Tuple[bool, dict, str]:
        """Attempt to fix an issue"""
        for rule in self.rules:
            if rule.can_fix(issue):
                success, updated_data = rule.fix_issue(issue, data)
                message = "Issue fixed successfully" if success else "Failed to fix issue"
                return success, updated_data, message

        return False, data, "No fix available for this issue"

    def get_summary(self, issues: List[ValidationIssue]) -> dict:
        """Get validation summary"""
        summary = {
            'total': len(issues),
            'by_severity': {},
            'by_category': {},
            'auto_fixable': 0
        }

        for issue in issues:
            # Count by severity
            severity = issue.severity.value
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1

            # Count by category
            category = issue.category.value
            summary['by_category'][category] = summary['by_category'].get(category, 0) + 1

            # Count auto-fixable
            if issue.auto_fixable:
                summary['auto_fixable'] += 1

        return summary


if __name__ == "__main__":
    # Test the validation engine
    engine = ValidationEngine()

    # Sample test data
    test_data = {
        'quest_info': {
            'quest_id': 0,  # Invalid
            'quest_name': '',  # Missing
            'quest_description': 'A test quest'
        },
        'dialogue_trees': {
            'test_tree': {
                'nodes': [
                    {
                        'node_id': 'start_node',
                        'node_type': 'start',
                        'text': 'Hello!  ',  # Trailing whitespace
                        'choices': [
                            {
                                'text': 'Choice 1',
                                'answer_id': 1,
                                'next_node': 'nonexistent_node'  # Broken link
                            },
                            {
                                'text': 'Choice 1',  # Duplicate
                                'answer_id': 1,  # Conflict
                                'next_node': 'end_node'
                            }
                        ]
                    },
                    {
                        'node_id': 'orphan_node',  # Unreachable
                        'node_type': 'npc',
                        'text': 'I am orphaned',
                        'choices': []
                    }
                ]
            }
        }
    }

    # Run validation
    issues = engine.validate_data(test_data)

    print(f"Found {len(issues)} validation issues:")
    for issue in issues:
        print(f"  [{issue.get_severity_display()}] {issue.title}")
        print(f"    {issue.description}")
        print(f"    Location: {issue.location}")
        print()