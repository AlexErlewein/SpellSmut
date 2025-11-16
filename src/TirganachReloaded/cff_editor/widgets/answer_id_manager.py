#!/usr/bin/env python3
"""
AnswerId Management System

Manages automatic assignment and tracking of unique AnswerIds for dialogue choices.
Ensures no ID collisions and provides conflict detection and resolution.

Usage:
    manager = AnswerIdManager()
    answer_id = manager.assign_answer_id("choice_step_1")
    conflicts = manager.validate_uniqueness()
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import json
from pathlib import Path

try:
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class AnswerIdConflict:
    """Represents an AnswerId conflict"""
    answer_id: int
    step_ids: List[str]
    severity: str = "error"  # error, warning, info
    
    def __str__(self) -> str:
        return f"AnswerId {self.answer_id} used by {len(self.step_ids)} steps: {', '.join(self.step_ids)}"


@dataclass
class AnswerIdAssignment:
    """Tracks an AnswerId assignment"""
    answer_id: int
    step_id: str
    choice_index: int  # Which choice in the step (0-based)
    choice_text: str
    auto_assigned: bool = True
    timestamp: Optional[str] = None


class AnswerIdManager:
    """
    Manages AnswerId assignment and tracking for dialogue system.
    
    Features:
    - Auto-increment ID assignment
    - Manual ID assignment with validation
    - Conflict detection
    - ID reservation and release
    - Usage tracking and reporting
    - Import/export of ID mappings
    """
    
    def __init__(self, start_id: int = 1000, quest_name: str = ""):
        """
        Initialize AnswerId Manager
        
        Args:
            start_id: Starting AnswerId (default 1000 to avoid conflicts with game IDs)
            quest_name: Name of the quest for context
        """
        self.quest_name = quest_name
        self.start_id = start_id
        self.next_available_id = start_id
        
        # Map: step_id -> List[AnswerIdAssignment]
        self.assignments: Dict[str, List[AnswerIdAssignment]] = defaultdict(list)
        
        # Reverse map: answer_id -> List[(step_id, choice_index)]
        self.id_usage: Dict[int, List[Tuple[str, int]]] = defaultdict(list)
        
        # Reserved IDs (manually assigned or imported)
        self.reserved_ids: Set[int] = set()
        
        # ID range configuration
        self.min_id = 1000  # Minimum allowed ID
        self.max_id = 99999  # Maximum allowed ID
        
        logger.info(f"AnswerIdManager initialized for quest '{quest_name}' starting at ID {start_id}")
    
    def assign_answer_id(self, step_id: str, choice_index: int = 0, choice_text: str = "") -> int:
        """
        Auto-assign a unique AnswerId to a dialogue choice.
        
        Args:
            step_id: ID of the dialogue step containing the choice
            choice_index: Index of the choice in the step (0-based)
            choice_text: Text of the choice (for documentation)
            
        Returns:
            The assigned AnswerId
        """
        # Check if this step/choice already has an ID
        for assignment in self.assignments[step_id]:
            if assignment.choice_index == choice_index:
                logger.debug(f"Step {step_id} choice {choice_index} already has ID {assignment.answer_id}")
                return assignment.answer_id
        
        # Find next available ID
        answer_id = self._get_next_id()
        
        # Create assignment
        assignment = AnswerIdAssignment(
            answer_id=answer_id,
            step_id=step_id,
            choice_index=choice_index,
            choice_text=choice_text,
            auto_assigned=True
        )
        
        # Track assignment
        self.assignments[step_id].append(assignment)
        self.id_usage[answer_id].append((step_id, choice_index))
        
        logger.info(f"Assigned AnswerId {answer_id} to step '{step_id}' choice {choice_index}")
        
        return answer_id
    
    def assign_manual_id(self, step_id: str, choice_index: int, answer_id: int, choice_text: str = "") -> bool:
        """
        Manually assign a specific AnswerId to a choice.
        
        Args:
            step_id: ID of the dialogue step
            choice_index: Index of the choice
            answer_id: The specific ID to assign
            choice_text: Text of the choice
            
        Returns:
            True if assignment successful, False if ID conflicts
        """
        # Validate ID range
        if not self.min_id <= answer_id <= self.max_id:
            logger.error(f"AnswerId {answer_id} out of valid range ({self.min_id}-{self.max_id})")
            return False
        
        # Check for conflicts
        if answer_id in self.id_usage and self.id_usage[answer_id]:
            # ID already in use
            existing_usage = self.id_usage[answer_id]
            # Allow if it's the same step/choice (re-assignment)
            if len(existing_usage) == 1 and existing_usage[0] == (step_id, choice_index):
                logger.debug(f"Re-assigning same ID {answer_id} to step {step_id} choice {choice_index}")
                return True
            else:
                logger.warning(f"AnswerId {answer_id} conflicts with existing usage: {existing_usage}")
                return False
        
        # Remove any existing assignment for this step/choice
        self.remove_assignment(step_id, choice_index)
        
        # Create manual assignment
        assignment = AnswerIdAssignment(
            answer_id=answer_id,
            step_id=step_id,
            choice_index=choice_index,
            choice_text=choice_text,
            auto_assigned=False
        )
        
        # Track assignment
        self.assignments[step_id].append(assignment)
        self.id_usage[answer_id].append((step_id, choice_index))
        self.reserved_ids.add(answer_id)
        
        # Update next_available_id if needed
        if answer_id >= self.next_available_id:
            self.next_available_id = answer_id + 1
        
        logger.info(f"Manually assigned AnswerId {answer_id} to step '{step_id}' choice {choice_index}")
        
        return True
    
    def remove_assignment(self, step_id: str, choice_index: int) -> bool:
        """
        Remove AnswerId assignment for a specific step/choice.
        
        Args:
            step_id: ID of the dialogue step
            choice_index: Index of the choice
            
        Returns:
            True if removed, False if not found
        """
        if step_id not in self.assignments:
            return False
        
        # Find and remove the assignment
        removed = False
        for assignment in self.assignments[step_id][:]:  # Copy list to avoid modification during iteration
            if assignment.choice_index == choice_index:
                answer_id = assignment.answer_id
                
                # Remove from assignments
                self.assignments[step_id].remove(assignment)
                
                # Remove from id_usage
                if answer_id in self.id_usage:
                    try:
                        self.id_usage[answer_id].remove((step_id, choice_index))
                        if not self.id_usage[answer_id]:
                            del self.id_usage[answer_id]
                    except ValueError:
                        pass
                
                # Remove from reserved if it was manual
                if not assignment.auto_assigned:
                    self.reserved_ids.discard(answer_id)
                
                logger.info(f"Removed AnswerId {answer_id} from step '{step_id}' choice {choice_index}")
                removed = True
                break
        
        # Clean up empty step entry
        if step_id in self.assignments and not self.assignments[step_id]:
            del self.assignments[step_id]
        
        return removed
    
    def get_answer_id(self, step_id: str, choice_index: int) -> Optional[int]:
        """
        Get the AnswerId for a specific step/choice.
        
        Args:
            step_id: ID of the dialogue step
            choice_index: Index of the choice
            
        Returns:
            The AnswerId if assigned, None otherwise
        """
        if step_id not in self.assignments:
            return None
        
        for assignment in self.assignments[step_id]:
            if assignment.choice_index == choice_index:
                return assignment.answer_id
        
        return None
    
    def get_step_assignments(self, step_id: str) -> List[AnswerIdAssignment]:
        """
        Get all AnswerId assignments for a step.
        
        Args:
            step_id: ID of the dialogue step
            
        Returns:
            List of assignments for this step
        """
        return self.assignments.get(step_id, [])
    
    def validate_uniqueness(self) -> List[AnswerIdConflict]:
        """
        Validate that all AnswerIds are unique.
        
        Returns:
            List of conflicts found (empty if all unique)
        """
        conflicts = []
        
        for answer_id, usages in self.id_usage.items():
            if len(usages) > 1:
                step_ids = [f"{step_id}[{choice_idx}]" for step_id, choice_idx in usages]
                conflict = AnswerIdConflict(
                    answer_id=answer_id,
                    step_ids=step_ids,
                    severity="error"
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def get_usage_report(self) -> Dict[str, any]:
        """
        Generate a comprehensive usage report.
        
        Returns:
            Dictionary with usage statistics and details
        """
        total_assignments = sum(len(assignments) for assignments in self.assignments.values())
        
        report = {
            "quest_name": self.quest_name,
            "total_assignments": total_assignments,
            "total_steps": len(self.assignments),
            "next_available_id": self.next_available_id,
            "id_range": {
                "min": self.min_id,
                "max": self.max_id,
                "used_min": min(self.id_usage.keys()) if self.id_usage else None,
                "used_max": max(self.id_usage.keys()) if self.id_usage else None,
            },
            "reserved_ids": sorted(list(self.reserved_ids)),
            "conflicts": len(self.validate_uniqueness()),
            "auto_assigned": sum(1 for assigns in self.assignments.values() 
                               for a in assigns if a.auto_assigned),
            "manual_assigned": sum(1 for assigns in self.assignments.values() 
                                  for a in assigns if not a.auto_assigned),
        }
        
        return report
    
    def get_id_mapping(self) -> Dict[int, List[Dict[str, any]]]:
        """
        Get a mapping of AnswerIds to their assignments.
        
        Returns:
            Dictionary mapping answer_id to list of assignment details
        """
        mapping = {}
        
        for answer_id, usages in self.id_usage.items():
            mapping[answer_id] = []
            for step_id, choice_idx in usages:
                # Find the full assignment
                for assignment in self.assignments[step_id]:
                    if assignment.choice_index == choice_idx:
                        mapping[answer_id].append({
                            "step_id": step_id,
                            "choice_index": choice_idx,
                            "choice_text": assignment.choice_text,
                            "auto_assigned": assignment.auto_assigned
                        })
                        break
        
        return mapping
    
    def export_to_json(self) -> str:
        """
        Export all assignments to JSON format.
        
        Returns:
            JSON string of all assignments
        """
        export_data = {
            "quest_name": self.quest_name,
            "next_available_id": self.next_available_id,
            "assignments": []
        }
        
        for step_id, assignments in self.assignments.items():
            for assignment in assignments:
                export_data["assignments"].append({
                    "answer_id": assignment.answer_id,
                    "step_id": assignment.step_id,
                    "choice_index": assignment.choice_index,
                    "choice_text": assignment.choice_text,
                    "auto_assigned": assignment.auto_assigned
                })
        
        return json.dumps(export_data, indent=2)
    
    def import_from_json(self, json_str: str) -> bool:
        """
        Import assignments from JSON format.
        
        Args:
            json_str: JSON string to import
            
        Returns:
            True if import successful, False otherwise
        """
        try:
            data = json.loads(json_str)
            
            # Clear existing data
            self.assignments.clear()
            self.id_usage.clear()
            self.reserved_ids.clear()
            
            # Import quest name and next ID
            self.quest_name = data.get("quest_name", self.quest_name)
            self.next_available_id = data.get("next_available_id", self.start_id)
            
            # Import assignments
            for assign_data in data.get("assignments", []):
                assignment = AnswerIdAssignment(
                    answer_id=assign_data["answer_id"],
                    step_id=assign_data["step_id"],
                    choice_index=assign_data["choice_index"],
                    choice_text=assign_data.get("choice_text", ""),
                    auto_assigned=assign_data.get("auto_assigned", True)
                )
                
                self.assignments[assignment.step_id].append(assignment)
                self.id_usage[assignment.answer_id].append((assignment.step_id, assignment.choice_index))
                
                if not assignment.auto_assigned:
                    self.reserved_ids.add(assignment.answer_id)
            
            logger.info(f"Imported {len(data.get('assignments', []))} AnswerId assignments")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import AnswerId assignments: {e}", exc_info=True)
            return False
    
    def reset(self):
        """Reset all assignments and state"""
        self.assignments.clear()
        self.id_usage.clear()
        self.reserved_ids.clear()
        self.next_available_id = self.start_id
        logger.info("AnswerIdManager reset")
    
    def _get_next_id(self) -> int:
        """
        Get the next available AnswerId, skipping reserved IDs.
        
        Returns:
            Next available ID
        """
        while self.next_available_id in self.reserved_ids or self.next_available_id in self.id_usage:
            self.next_available_id += 1
            
            # Safety check for overflow
            if self.next_available_id > self.max_id:
                raise ValueError(f"AnswerId overflow: exceeded maximum ID {self.max_id}")
        
        current_id = self.next_available_id
        self.next_available_id += 1
        
        return current_id
    
    def preview_assignments(self, format: str = "text") -> str:
        """
        Generate a preview of all assignments.
        
        Args:
            format: Output format ('text' or 'markdown')
            
        Returns:
            Formatted string with assignment preview
        """
        if format == "markdown":
            return self._preview_markdown()
        else:
            return self._preview_text()
    
    def _preview_text(self) -> str:
        """Generate text preview of assignments"""
        lines = []
        lines.append(f"=== AnswerId Assignments for '{self.quest_name}' ===")
        lines.append(f"Next Available ID: {self.next_available_id}")
        lines.append(f"Total Assignments: {sum(len(a) for a in self.assignments.values())}")
        lines.append("")
        
        for step_id in sorted(self.assignments.keys()):
            lines.append(f"Step: {step_id}")
            for assignment in sorted(self.assignments[step_id], key=lambda a: a.choice_index):
                auto_tag = "[AUTO]" if assignment.auto_assigned else "[MANUAL]"
                lines.append(f"  Choice {assignment.choice_index}: ID {assignment.answer_id} {auto_tag}")
                if assignment.choice_text:
                    lines.append(f"    \"{assignment.choice_text}\"")
            lines.append("")
        
        conflicts = self.validate_uniqueness()
        if conflicts:
            lines.append("=== CONFLICTS ===")
            for conflict in conflicts:
                lines.append(f"  {conflict}")
        
        return "\n".join(lines)
    
    def _preview_markdown(self) -> str:
        """Generate markdown preview of assignments"""
        lines = []
        lines.append(f"# AnswerId Assignments: {self.quest_name}")
        lines.append("")
        lines.append(f"**Next Available ID**: {self.next_available_id}  ")
        lines.append(f"**Total Assignments**: {sum(len(a) for a in self.assignments.values())}")
        lines.append("")
        
        lines.append("## Assignments by Step")
        lines.append("")
        
        for step_id in sorted(self.assignments.keys()):
            lines.append(f"### {step_id}")
            lines.append("")
            for assignment in sorted(self.assignments[step_id], key=lambda a: a.choice_index):
                auto_tag = "🤖 AUTO" if assignment.auto_assigned else "✋ MANUAL"
                lines.append(f"- **Choice {assignment.choice_index}**: AnswerId `{assignment.answer_id}` {auto_tag}")
                if assignment.choice_text:
                    lines.append(f"  > {assignment.choice_text}")
            lines.append("")
        
        conflicts = self.validate_uniqueness()
        if conflicts:
            lines.append("## ⚠️ Conflicts")
            lines.append("")
            for conflict in conflicts:
                lines.append(f"- {conflict}")
        
        return "\n".join(lines)


# Convenience function for quick testing
def create_manager(quest_name: str = "", start_id: int = 1000) -> AnswerIdManager:
    """Create a new AnswerIdManager instance"""
    return AnswerIdManager(start_id=start_id, quest_name=quest_name)


if __name__ == "__main__":
    """Test the AnswerIdManager"""
    print("Testing AnswerIdManager...")
    
    # Create manager
    manager = AnswerIdManager(start_id=1000, quest_name="Test Quest")
    
    # Test auto-assignment
    id1 = manager.assign_answer_id("step1", 0, "What do you want?")
    id2 = manager.assign_answer_id("step1", 1, "Tell me about yourself")
    id3 = manager.assign_answer_id("step2", 0, "Goodbye")
    
    print(f"\nAuto-assigned IDs: {id1}, {id2}, {id3}")
    
    # Test manual assignment
    success = manager.assign_manual_id("step3", 0, 2000, "Special choice")
    print(f"\nManual assignment successful: {success}")
    
    # Test conflict detection
    conflicts = manager.validate_uniqueness()
    print(f"\nConflicts found: {len(conflicts)}")
    
    # Print preview
    print("\n" + manager.preview_assignments())
    
    # Print usage report
    print("\n=== Usage Report ===")
    report = manager.get_usage_report()
    for key, value in report.items():
        print(f"  {key}: {value}")
    
    # Test export/import
    json_export = manager.export_to_json()
    print(f"\nExported to JSON ({len(json_export)} chars)")
    
    # Test import
    manager2 = AnswerIdManager()
    manager2.import_from_json(json_export)
    print(f"Imported {len(manager2.assignments)} steps")
