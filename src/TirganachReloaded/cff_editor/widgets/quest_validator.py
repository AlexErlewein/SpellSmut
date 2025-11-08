#!/usr/bin/env python3
"""
Quest Validator (Fixed Version)

Comprehensive quest validation with:
- Quest ID conflict checking
- Dialogue flow validation
- Reward balance checking
- CFF data integrity validation
- Lua script syntax checking
- Detailed error reporting

This component ensures quests are valid before saving.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Add src directory to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData, Dialogue, QuestReward, MapLocation


@dataclass
class ValidationError:
    """Single validation error"""
    level: str  # "error", "warning", "info"
    category: str  # "general", "dialogue", "rewards", "cff", "lua"
    message: str
    suggestion: Optional[str] = None
    quest_id: Optional[int] = None
    field: Optional[str] = None
    
    def __str__(self):
        return f"[{self.level.upper()}] {self.category}: {self.message}"


@dataclass
class ValidationResult:
    """Complete validation result"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def get_all_issues(self) -> List[ValidationError]:
        return self.errors + self.warnings + self.info
    
    def get_summary(self) -> str:
        """Get validation summary"""
        if self.is_valid and not self.warnings:
            return "✓ Quest is valid and ready to save"
        elif self.is_valid:
            return f"⚠ Quest is valid with {len(self.warnings)} warnings"
        else:
            return f"✗ Quest has {len(self.errors)} errors and {len(self.warnings)} warnings"


class QuestValidator:
    """Main quest validator class"""
    
    def __init__(self):
        # Validation rules
        self.min_quest_id = 1
        self.max_quest_id = 99999
        self.custom_quest_id_range = (9000, 9999)
        self.max_dialogue_length = 200
        self.max_objectives = 10
        self.max_rewards = 20
        
        # Existing quest data for conflict checking
        self.existing_quest_ids = set()
        self.existing_quest_names = set()
    
    def set_existing_quests(self, quest_data: Dict[int, Dict]):
        """Set existing quest data for conflict checking"""
        self.existing_quest_ids = set(quest_data.keys())
        self.existing_quest_names = set(
            quest.get('name', '') for quest in quest_data.values()
            if quest.get('name')
        )
    
    def validate_quest(self, quest: EnhancedQuestData) -> Tuple[bool, List[str]]:
        """Validate a complete quest (simplified interface)"""
        result = self.validate_quest_detailed(quest)
        
        # Convert to simple error list format
        errors = []
        for error in result.get_all_issues():
            if error.level in ["error", "warning"]:
                errors.append(f"{error.level}: {error.message}")
                if error.suggestion:
                    errors.append(f"  Suggestion: {error.suggestion}")
        
        return result.is_valid, errors
    
    def validate_quest_detailed(self, quest: EnhancedQuestData) -> ValidationResult:
        """Comprehensive quest validation"""
        errors = []
        warnings = []
        info = []
        
        # Basic validation
        basic_errors, basic_warnings, basic_info = self._validate_basic_info(quest)
        errors.extend(basic_errors)
        warnings.extend(basic_warnings)
        info.extend(basic_info)
        
        # Dialogue validation
        if quest.dialogues:
            dialogue_errors, dialogue_warnings = self._validate_dialogues(quest.dialogues)
            errors.extend(dialogue_errors)
            warnings.extend(dialogue_warnings)
        
        # Reward validation
        if quest.rewards:
            reward_errors, reward_warnings = self._validate_rewards(quest.rewards)
            errors.extend(reward_errors)
            warnings.extend(reward_warnings)
        
        # Hierarchy validation
        hierarchy_errors, hierarchy_warnings = self._validate_hierarchy(quest)
        errors.extend(hierarchy_errors)
        warnings.extend(hierarchy_warnings)
        
        # CFF validation
        cff_errors, cff_warnings = self._validate_cff_compatibility(quest)
        errors.extend(cff_errors)
        warnings.extend(cff_warnings)
        
        # Lua validation
        lua_errors, lua_warnings = self._validate_lua_compatibility(quest)
        errors.extend(lua_errors)
        warnings.extend(lua_warnings)
        
        # Overall validity
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            info=info
        )
    
    def _validate_basic_info(self, quest: EnhancedQuestData) -> Tuple[List, List, List]:
        """Validate basic quest information"""
        errors = []
        warnings = []
        info = []
        
        # Quest ID validation
        if quest.quest_id is None:
            errors.append(ValidationError(
                level="error",
                category="general",
                message="Quest ID is required",
                suggestion="Assign a unique quest ID",
                field="quest_id"
            ))
        elif not isinstance(quest.quest_id, int):
            errors.append(ValidationError(
                level="error",
                category="general",
                message="Quest ID must be a number",
                suggestion="Convert quest ID to integer",
                field="quest_id"
            ))
        elif quest.quest_id < self.min_quest_id or quest.quest_id > self.max_quest_id:
            errors.append(ValidationError(
                level="error",
                category="general",
                message=f"Quest ID must be between {self.min_quest_id} and {self.max_quest_id}",
                suggestion=f"Use ID in range {self.min_quest_id}-{self.max_quest_id}",
                field="quest_id"
            ))
        elif (self.custom_quest_id_range[0] <= quest.quest_id <= self.custom_quest_id_range[1] and
              quest.quest_id in self.existing_quest_ids):
            errors.append(ValidationError(
                level="error",
                category="general",
                message=f"Quest ID {quest.quest_id} already exists",
                suggestion=f"Use next available ID: {self._get_next_custom_id()}",
                field="quest_id",
                quest_id=quest.quest_id
            ))
        elif quest.quest_id in self.existing_quest_ids:
            warnings.append(ValidationError(
                level="warning",
                category="general",
                message=f"Quest ID {quest.quest_id} conflicts with existing quest",
                suggestion="Consider using custom ID range 9000-9999",
                field="quest_id",
                quest_id=quest.quest_id
            ))
        
        # Quest name validation
        if not quest.name or not quest.name.strip():
            errors.append(ValidationError(
                level="error",
                category="general",
                message="Quest name is required",
                suggestion="Enter a descriptive quest name",
                field="name"
            ))
        elif len(quest.name.strip()) < 3:
            warnings.append(ValidationError(
                level="warning",
                category="general",
                message="Quest name is very short",
                suggestion="Use a more descriptive name (at least 3 characters)",
                field="name"
            ))
        elif len(quest.name) > 100:
            warnings.append(ValidationError(
                level="warning",
                category="general",
                message="Quest name is very long",
                suggestion="Consider shortening to name for better display",
                field="name"
            ))
        elif quest.name in self.existing_quest_names:
            warnings.append(ValidationError(
                level="warning",
                category="general",
                message=f"Quest name '{quest.name}' may conflict with existing quest",
                suggestion="Use a more unique name",
                field="name"
            ))
        elif not re.match(r'^[A-Za-z0-9\s\-_\']+$', quest.name):
            warnings.append(ValidationError(
                level="warning",
                category="general",
                message="Quest name contains special characters",
                suggestion="Use only letters, numbers, spaces, hyphens, and underscores",
                field="name"
            ))
        
        # Description validation
        if not quest.description or not quest.description.strip():
            warnings.append(ValidationError(
                level="warning",
                category="general",
                message="Quest description is empty",
                suggestion="Add a brief description to help players understand the quest",
                field="description"
            ))
        elif len(quest.description) < 10:
            info.append(ValidationError(
                level="info",
                category="general",
                message="Quest description is very short",
                suggestion="Consider adding more details about quest objectives",
                field="description"
            ))
        elif len(quest.description) > 500:
            warnings.append(ValidationError(
                level="warning",
                category="general",
                message="Quest description is very long",
                suggestion="Consider shortening for better readability",
                field="description"
            ))
        
        return errors, warnings, info
    
    def _validate_dialogues(self, dialogues: List[Dialogue]) -> Tuple[List, List]:
        """Validate dialogue content and flow"""
        errors = []
        warnings = []
        
        if not dialogues:
            return errors, warnings
        
        # Check for empty dialogues
        for i, dialogue in enumerate(dialogues):
            if not dialogue.text or not dialogue.text.strip():
                errors.append(ValidationError(
                    level="error",
                    category="dialogue",
                    message=f"Dialogue {i+1} has empty text",
                    suggestion="Enter dialogue text or remove empty dialogue",
                    field="dialogues"
                ))
            elif len(dialogue.text) > self.max_dialogue_length:
                warnings.append(ValidationError(
                    level="warning",
                    category="dialogue",
                    message=f"Dialogue {i+1} is very long ({len(dialogue.text)} characters)",
                    suggestion=f"Consider shortening to under {self.max_dialogue_length} characters",
                    field="dialogues"
                ))
            
            # Check speaker validity
            if dialogue.speaker not in ["NPC", "Player"]:
                warnings.append(ValidationError(
                    level="warning",
                    category="dialogue",
                    message=f"Dialogue {i+1} has unknown speaker: {dialogue.speaker}",
                    suggestion="Use 'NPC' or 'Player' as speaker",
                    field="dialogues"
                ))
        
        # Check dialogue flow
        npc_dialogues = [d for d in dialogues if d.speaker == "NPC"]
        player_dialogues = [d for d in dialogues if d.speaker == "Player"]
        
        if not npc_dialogues:
            warnings.append(ValidationError(
                level="warning",
                category="dialogue",
                message="No NPC dialogues found",
                suggestion="Add at least one NPC dialogue for quest giver",
                field="dialogues"
            ))
        
        if len(player_dialogues) > len(npc_dialogues) * 3:
            warnings.append(ValidationError(
                level="warning",
                category="dialogue",
                message="Too many player choices compared to NPC dialogues",
                suggestion="Add more NPC dialogues or reduce player choices",
                field="dialogues"
            ))
        
        # Check for duplicate dialogues
        dialogue_texts = [d.text.lower().strip() for d in dialogues]
        duplicate_texts = [text for text in dialogue_texts if dialogue_texts.count(text) > 1]
        if duplicate_texts:
            warnings.append(ValidationError(
                level="warning",
                category="dialogue",
                message="Duplicate dialogue text found",
                suggestion="Review dialogues and remove or modify duplicates",
                field="dialogues"
            ))
        
        return errors, warnings
    
    def _validate_rewards(self, rewards: QuestReward) -> Tuple[List, List]:
        """Validate reward configuration"""
        errors = []
        warnings = []
        
        # XP validation
        if rewards.xp < 0:
            errors.append(ValidationError(
                level="error",
                category="rewards",
                message="Experience points cannot be negative",
                suggestion="Set XP to 0 or a positive value",
                field="xp"
            ))
        elif rewards.xp > 10000:
            warnings.append(ValidationError(
                level="warning",
                category="rewards",
                message="Very high XP reward",
                suggestion="Consider if this amount is balanced for quest difficulty",
                field="xp"
            ))
        elif rewards.xp == 0:
            info.append(ValidationError(
                level="info",
                category="rewards",
                message="No XP reward set",
                suggestion="Consider adding some XP as reward",
                field="xp"
            ))
        
        # Money validation
        if any([rewards.gold < 0, rewards.silver < 0, rewards.copper < 0]):
            errors.append(ValidationError(
                level="error",
                category="rewards",
                message="Money rewards cannot be negative",
                suggestion="Set all money values to 0 or positive values",
                field="money"
            ))
        
        total_money = rewards.gold * 100 + rewards.silver * 10 + rewards.copper
        if total_money > 1000:
            warnings.append(ValidationError(
                level="warning",
                category="rewards",
                message="Very high money reward",
                suggestion="Consider if this amount is balanced",
                field="money"
            ))
        elif total_money == 0 and rewards.xp == 0 and not rewards.items:
            warnings.append(ValidationError(
                level="warning",
                category="rewards",
                message="No rewards set",
                suggestion="Add at least some XP, money, or items as reward",
                field="rewards"
            ))
        
        # Item validation
        if rewards.items:
            if len(rewards.items) > self.max_rewards:
                warnings.append(ValidationError(
                    level="warning",
                    category="rewards",
                    message=f"Too many reward items ({len(rewards.items)})",
                    suggestion=f"Consider reducing to {self.max_rewards} or fewer items",
                    field="items"
                ))
            
            # Check for invalid item IDs
            for item in rewards.items:
                if isinstance(item, dict) and 'id' in item:
                    item_id = item['id']
                elif hasattr(item, 'item_id'):
                    item_id = item.item_id
                elif isinstance(item, int):
                    item_id = item
                else:
                    warnings.append(ValidationError(
                        level="warning",
                        category="rewards",
                        message="Invalid item format in rewards",
                        suggestion="Ensure all items have valid ID format",
                        field="items"
                    ))
                    continue
                
                if item_id <= 0:
                    errors.append(ValidationError(
                        level="error",
                        category="rewards",
                        message=f"Invalid item ID: {item_id}",
                        suggestion="Use valid positive item IDs",
                        field="items"
                    ))
        
        return errors, warnings
    
    def _validate_hierarchy(self, quest: EnhancedQuestData) -> Tuple[List, List]:
        """Validate quest hierarchy relationships"""
        errors = []
        warnings = []
        
        # Parent quest validation
        if quest.parent_id is not None:
            if quest.parent_id == quest.quest_id:
                errors.append(ValidationError(
                    level="error",
                    category="general",
                    message="Quest cannot be its own parent",
                    suggestion="Set parent_id to a different quest ID or 0 for no parent",
                    field="parent_id"
                ))
            elif quest.parent_id < 0:
                errors.append(ValidationError(
                    level="error",
                    category="general",
                    message="Parent quest ID cannot be negative",
                    suggestion="Use 0 for no parent or a valid quest ID",
                    field="parent_id"
                ))
            elif quest.parent_id not in self.existing_quest_ids:
                warnings.append(ValidationError(
                    level="warning",
                    category="general",
                    message=f"Parent quest ID {quest.parent_id} not found in existing quests",
                    suggestion="Ensure parent quest exists or set to 0 for no parent",
                    field="parent_id"
                ))
        
        # Order index validation
        if quest.order_index is not None:
            if quest.order_index < 0:
                errors.append(ValidationError(
                    level="error",
                    category="general",
                    message="Order index cannot be negative",
                    suggestion="Use 0 or positive value for order index",
                    field="order_index"
                ))
            elif quest.order_index > 99:
                warnings.append(ValidationError(
                    level="warning",
                    category="general",
                    message="Very high order index",
                    suggestion="Consider using lower order index (0-99 range recommended)",
                    field="order_index"
                ))
        
        return errors, warnings
    
    def _validate_cff_compatibility(self, quest: EnhancedQuestData) -> Tuple[List, List]:
        """Validate CFF data format compatibility"""
        errors = []
        warnings = []
        
        # Check for fields that might cause CFF issues
        if quest.name and len(quest.name.encode('utf-8')) > 255:
            errors.append(ValidationError(
                level="error",
                category="cff",
                message="Quest name too long for CFF format",
                suggestion="Shorten name to under 255 bytes",
                field="name"
            ))
        
        if quest.description and len(quest.description.encode('utf-8')) > 1023:
            warnings.append(ValidationError(
                level="warning",
                category="cff",
                message="Quest description may be too long for CFF format",
                suggestion="Consider shortening description to under 1023 bytes",
                field="description"
            ))
        
        # Check for characters that might cause issues
        if quest.name and any(char in quest.name for char in ['<', '>', '|', '\0']):
            errors.append(ValidationError(
                level="error",
                category="cff",
                message="Quest name contains invalid characters for CFF format",
                suggestion="Remove special characters like <, >, |, null",
                field="name"
            ))
        
        # Validate map locations
        if quest.map_locations:
            for location in quest.map_locations:
                if not location.code:
                    warnings.append(ValidationError(
                        level="warning",
                        category="cff",
                        message="Map location has no platform code",
                        suggestion="Set platform code (e.g., P1, P2, etc.)",
                        field="map_locations"
                    ))
                elif not re.match(r'^P\d+$', location.code):
                    warnings.append(ValidationError(
                        level="warning",
                        category="cff",
                        message=f"Invalid platform code format: {location.code}",
                        suggestion="Use format like P1, P2, P63, etc.",
                        field="map_locations"
                    ))
        
        return errors, warnings
    
    def _validate_lua_compatibility(self, quest: EnhancedQuestData) -> Tuple[List, List]:
        """Validate Lua script compatibility"""
        errors = []
        warnings = []
        
        # Check for Lua reserved words in quest name
        lua_reserved = ['and', 'break', 'do', 'else', 'elseif', 'end', 'false', 
                       'for', 'function', 'if', 'in', 'local', 'nil', 'not', 
                       'or', 'repeat', 'return', 'then', 'true', 'until', 'while']
        
        if quest.name:
            name_words = re.findall(r'\b\w+\b', quest.name.lower())
            for word in name_words:
                if word in lua_reserved:
                    warnings.append(ValidationError(
                        level="warning",
                        category="lua",
                        message=f"Quest name contains Lua reserved word: {word}",
                        suggestion="Consider avoiding Lua reserved words in quest names",
                        field="name"
                    ))
        
        # Check dialogue text for Lua script patterns
        if quest.dialogues:
            for i, dialogue in enumerate(quest.dialogues):
                if dialogue.text and any(pattern in dialogue.text for pattern in ['${', '}}', 'function']):
                    warnings.append(ValidationError(
                        level="warning",
                        category="lua",
                        message=f"Dialogue {i+1} contains patterns that might interfere with Lua scripting",
                        suggestion="Avoid patterns that could be confused with Lua syntax",
                        field="dialogues"
                    ))
        
        return errors, warnings
    
    def _get_next_custom_id(self) -> int:
        """Get next available custom quest ID"""
        used_custom_ids = [qid for qid in self.existing_quest_ids 
                          if self.custom_quest_id_range[0] <= qid <= self.custom_quest_id_range[1]]
        
        if used_custom_ids:
            return max(used_custom_ids) + 1
        return self.custom_quest_id_range[0]
    
    def validate_lua_syntax(self, lua_code: str) -> Tuple[bool, List[str]]:
        """Basic Lua syntax validation"""
        errors = []
        
        if not lua_code:
            return True, errors
        
        # Check for basic syntax issues
        if lua_code.count('function(') != lua_code.count('end'):
            errors.append("Mismatched function/end blocks")
        
        if lua_code.count('{') != lua_code.count('}'):
            errors.append("Mismatched curly braces")
        
        if lua_code.count('(') != lua_code.count(')'):
            errors.append("Mismatched parentheses")
        
        # Check for common patterns
        if 'then' in lua_code and not re.search(r'if.*then', lua_code):
            errors.append("'then' found without corresponding 'if'")
        
        if '--[[]]' not in lua_code and ('--[[' in lua_code or '--]]' in lua_code):
            errors.append("Malformed multi-line comment")
        
        # Check for lines ending with operators (common syntax error)
        lines = lua_code.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and stripped[-1] in ['+', '-', '*', '/', '=', ',']:
                errors.append(f"Line {i}: Line ends with operator '{stripped[-1]}'")
        
        return len(errors) == 0, errors


# Utility functions
def validate_quest_batch(quests: List[EnhancedQuestData]) -> ValidationResult:
    """Validate multiple quests at once"""
    validator = QuestValidator()
    all_errors = []
    all_warnings = []
    all_info = []
    
    for quest in quests:
        result = validator.validate_quest_detailed(quest)
        all_errors.extend(result.errors)
        all_warnings.extend(result.warnings)
        all_info.extend(result.info)
    
    # Check for conflicts between quests in batch
    quest_ids = [q.quest_id for q in quests]
    quest_names = [q.name for q in quests if q.name]
    
    # Check for duplicate IDs
    seen_ids = set()
    for quest_id in quest_ids:
        if quest_id in seen_ids:
            all_errors.append(ValidationError(
                level="error",
                category="general",
                message=f"Duplicate quest ID in batch: {quest_id}",
                suggestion="Use unique quest IDs for each quest"
            ))
        seen_ids.add(quest_id)
    
    # Check for duplicate names
    seen_names = set()
    for quest_name in quest_names:
        if quest_name in seen_names:
            all_warnings.append(ValidationError(
                level="warning",
                category="general",
                message=f"Duplicate quest name in batch: {quest_name}",
                suggestion="Use unique quest names for each quest"
            ))
        seen_names.add(quest_name)
    
    return ValidationResult(
        is_valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings,
        info=all_info
    )


# Main testing function
if __name__ == "__main__":
    # Test quest validator
    validator = QuestValidator()
    
    # Create test quest
    test_quest = EnhancedQuestData(
        quest_id=9001,
        name="Test Quest",
        description="A test quest for validation.",
        parent_id=0,
        order_index=0
    )
    
    # Add some test data
    test_quest.map_locations.append(MapLocation(code="P1", name="Liannon"))
    test_quest.dialogues.append(Dialogue(text="Hello, adventurer!", speaker="NPC"))
    test_quest.rewards = QuestReward(xp=100, gold=10)
    
    # Validate
    result = validator.validate_quest_detailed(test_quest)
    
    print("Validation Result:")
    print(result.get_summary())
    print("\nAll Issues:")
    for issue in result.get_all_issues():
        print(f"  {issue}")