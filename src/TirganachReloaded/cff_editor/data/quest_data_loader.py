#!/usr/bin/env python3
"""
Quest Data Loader

Loads quest data from external sources (QuestKnowledge directory)
and integrates it with CFF quest data for the enhanced quest editor.
"""

import os
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from loguru import logger


@dataclass
class QuestReward:
    """Quest reward data structure"""
    xp: int = 0
    gold: int = 0
    silver: int = 0
    copper: int = 0
    items_given: List[int] = None
    items_taken: List[int] = None

    def __post_init__(self):
        if self.items_given is None:
            self.items_given = []
        if self.items_taken is None:
            self.items_taken = []


@dataclass
class QuestInfo:
    """Complete quest information structure"""
    quest_flag: str
    quest_id: Optional[int]
    quest_name: str = ""
    quest_name_de: str = ""
    quest_description_de: str = ""
    quest_description_loc: str = ""
    quest_giver_npc_id: Optional[int] = None
    quest_giver_name: str = ""
    parent_quest_id: Optional[int] = None
    parent_chain: str = ""
    order_index: Optional[int] = None
    platform_name: str = ""
    quest_maps: str = ""
    objectives: List[str] = None
    flags: List[str] = None
    rewards: QuestReward = None

    def __post_init__(self):
        if self.rewards is None:
            self.rewards = QuestReward()
        if self.objectives is None:
            self.objectives = []
        if self.flags is None:
            self.flags = []


class QuestDataLoader:
    """Loads and manages quest data from external sources"""

    def __init__(self, quest_knowledge_path: str = None):
        if quest_knowledge_path is None:
            # Default path relative to project root
            # Navigate from src/TirganachReloaded/cff_editor/data/ to project root
            project_root = Path(__file__).parent.parent.parent.parent.parent
            quest_knowledge_path = project_root / "ModdingTools/SpellForceLUASources/QuestKnowledge"

        self.quest_knowledge_path = Path(quest_knowledge_path)
        self.quest_data: Dict[str, QuestInfo] = {}
        self.quest_id_mapping: Dict[int, QuestInfo] = {}
        self.dialogue_summary: Dict = {}

        logger.info(f"Initializing QuestDataLoader with path: {self.quest_knowledge_path}")

        if self.quest_knowledge_path.exists():
            self.load_all_quest_data()
        else:
            logger.warning(f"Quest knowledge path does not exist: {self.quest_knowledge_path}")

    def load_all_quest_data(self):
        """Load all quest data from available sources"""
        logger.info("Loading quest data from external sources...")

        try:
            self.load_quest_rewards_csv()
            self.load_quest_rewards_lua()
            self.load_dialogue_summary()
            self.load_quest_objectives()

            logger.info(f"Loaded {len(self.quest_data)} quest entries")
            logger.info(f"Quest ID mapping contains {len(self.quest_id_mapping)} entries")

        except Exception as e:
            logger.error(f"Error loading quest data: {e}")

    def load_quest_rewards_csv(self) -> bool:
        """Load quest rewards from CSV file"""
        csv_path = self.quest_knowledge_path / "QuestRewards.csv"

        if not csv_path.exists():
            logger.warning(f"Quest rewards CSV not found: {csv_path}")
            return False

        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    # Parse numeric fields
                    quest_id = self._parse_int(row.get('quest_id'))
                    quest_giver_npc_id = self._parse_int(row.get('quest_giver_npc_id'))
                    parent_quest_id = self._parse_int(row.get('parent_quest_id'))
                    order_index = self._parse_int(row.get('order_index'))

                    # Parse reward fields
                    xp = self._parse_int(row.get('xp', 0))
                    gold = self._parse_int(row.get('gold', 0))
                    silver = self._parse_int(row.get('silver', 0))
                    copper = self._parse_int(row.get('copper', 0))

                    # Parse item lists
                    items_given = self._parse_item_list(row.get('items_given', ''))
                    items_taken = self._parse_item_list(row.get('items_taken', ''))

                    # Create quest info
                    quest_info = QuestInfo(
                        quest_flag=row.get('quest_flag', ''),
                        quest_id=quest_id,
                        quest_name=row.get('quest_name_loc', '') or row.get('quest_name', ''),
                        quest_name_de=row.get('quest_name_de', ''),
                        quest_description_de=row.get('quest_description_de', ''),
                        quest_description_loc=row.get('quest_description_loc', ''),
                        quest_giver_npc_id=quest_giver_npc_id,
                        quest_giver_name=row.get('quest_giver_name', ''),
                        parent_quest_id=parent_quest_id,
                        parent_chain=row.get('parent_chain', ''),
                        order_index=order_index,
                        platform_name=row.get('platform_name', ''),
                        quest_maps=row.get('quest_maps', ''),
                        objectives=[],
                        flags=[],
                        rewards=QuestReward(
                            xp=xp,
                            gold=gold,
                            silver=silver,
                            copper=copper,
                            items_given=items_given,
                            items_taken=items_taken
                        )
                    )

                    # Store by quest flag
                    if quest_info.quest_flag:
                        self.quest_data[quest_info.quest_flag] = quest_info

                    # Store by quest ID
                    if quest_id:
                        self.quest_id_mapping[quest_id] = quest_info

                logger.info(f"Loaded {len(self.quest_data)} quest entries from CSV")
                return True

        except Exception as e:
            logger.error(f"Error loading quest rewards CSV: {e}")
            return False

    def load_quest_rewards_lua(self) -> bool:
        """Load quest rewards from LUA file"""
        # Path to script directory relative to project root
        script_path = Path(__file__).parent.parent.parent.parent / "ModdingTools/SpellForceLUASources/script/GdsQuestRewards.lua"

        if not script_path.exists():
            logger.warning(f"Quest rewards LUA not found: {script_path}")
            return False

        try:
            with open(script_path, 'r', encoding='utf-8') as file:
                content = file.read()

                # Parse LUA quest rewards dictionaries
                # Pattern: QuestFlag = { Items = {...}, XP = {...}, Money = {...} }
                import re
                pattern = r'(\w+)\s*=\s*\{([^}]+)\}'
                matches = re.findall(pattern, content)

                loaded_count = 0
                for quest_flag, rewards_text in matches:
                    try:
                        rewards_data = self._parse_lua_rewards(rewards_text)
                        if rewards_data:
                            # Create or update quest info
                            if quest_flag not in self.quest_data:
                                self.quest_data[quest_flag] = QuestInfo(quest_flag=quest_flag)

                            quest_info = self.quest_data[quest_flag]
                            if rewards_data.get('xp'):
                                quest_info.rewards.xp = rewards_data['xp']
                            if rewards_data.get('gold'):
                                quest_info.rewards.gold = rewards_data['gold']
                            if rewards_data.get('silver'):
                                quest_info.rewards.silver = rewards_data['silver']
                            if rewards_data.get('copper'):
                                quest_info.rewards.copper = rewards_data['copper']
                            if rewards_data.get('items'):
                                quest_info.rewards.items_given.extend(rewards_data['items'])
                            if rewards_data.get('objectives'):
                                quest_info.objectives.extend(rewards_data['objectives'])

                            loaded_count += 1
                    except Exception as e:
                        logger.debug(f"Error parsing quest {quest_flag}: {e}")
                        continue

                logger.info(f"Loaded {loaded_count} quest rewards from LUA")
                return True

        except Exception as e:
            logger.error(f"Error loading quest rewards LUA: {e}")
            return False

    def load_quest_objectives(self) -> bool:
        """Load quest objectives from script files"""
        # Path to script directory
        script_path = Path(__file__).parent.parent.parent.parent / "ModdingTools/SpellForceLUASources/script"

        if not script_path.exists():
            logger.warning(f"Script directory not found: {script_path}")
            return False

        try:
            objectives_loaded = 0

            # Scan all script subdirectories for quest files
            for platform_dir in script_path.iterdir():
                if not platform_dir.is_dir() or platform_dir.name.startswith('.'):
                    continue

                # Look for quest-related files in platform directories
                for script_file in platform_dir.glob("*.lua"):
                    try:
                        quest_objectives = self._parse_lua_quest_objectives(script_file)
                        if quest_objectives:
                            # Store objectives by extracting quest name from filename
                            quest_name = script_file.stem
                            if quest_name.startswith('n'):
                                quest_name = quest_name[1:]  # Remove 'n' prefix

                            # Try to find existing quest info or create new one
                            quest_info = None
                            for qi in self.quest_data.values():
                                if qi.quest_flag.lower() == quest_name.lower():
                                    quest_info = qi
                                    break

                            if quest_info is None:
                                # Create new quest entry
                                quest_flag = f"quest_{quest_name}"
                                quest_info = QuestInfo(quest_flag=quest_flag)
                                self.quest_data[quest_flag] = quest_info

                            # Add objectives
                            quest_info.objectives.extend(quest_objectives)
                            objectives_loaded += len(quest_objectives)
                    except Exception as e:
                        logger.debug(f"Error parsing objectives from {script_file}: {e}")
                        continue

            logger.info(f"Loaded {objectives_loaded} quest objectives from script files")
            return True

        except Exception as e:
            logger.error(f"Error loading quest objectives: {e}")
            return False

    def load_dialogue_summary(self) -> bool:
        """Load dialogue summary from JSON file"""
        json_path = self.quest_knowledge_path / "DialogueSummary.json"

        if not json_path.exists():
            logger.warning(f"Dialogue summary JSON not found: {json_path}")
            return False

        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                self.dialogue_summary = json.load(file)

                logger.info(f"Loaded dialogue summary: {self.dialogue_summary.get('total_npcs', 0)} NPCs, "
                           f"{self.dialogue_summary.get('total_dialogues', 0)} dialogues")
                return True

        except Exception as e:
            logger.error(f"Error loading dialogue summary JSON: {e}")
            return False

    def get_quest_by_flag(self, quest_flag: str) -> Optional[QuestInfo]:
        """Get quest information by quest flag"""
        return self.quest_data.get(quest_flag)

    def get_quest_by_id(self, quest_id: int) -> Optional[QuestInfo]:
        """Get quest information by quest ID"""
        return self.quest_id_mapping.get(quest_id)

    def get_quest_by_name_search(self, name: str) -> List[QuestInfo]:
        """Search for quests by name (partial match)"""
        name_lower = name.lower()
        matches = []

        for quest_info in self.quest_data.values():
            if (name_lower in quest_info.quest_name.lower() or
                name_lower in quest_info.quest_name_de.lower()):
                matches.append(quest_info)

        return matches

    def get_quests_by_platform(self, platform_name: str) -> List[QuestInfo]:
        """Get all quests for a specific platform"""
        platform_quests = []

        for quest_info in self.quest_data.values():
            if quest_info.platform_name.lower() == platform_name.lower():
                platform_quests.append(quest_info)

        return platform_quests

    def get_child_quests(self, parent_quest_id: int) -> List[QuestInfo]:
        """Get all child quests of a parent quest"""
        child_quests = []

        for quest_info in self.quest_data.values():
            if quest_info.parent_quest_id == parent_quest_id:
                child_quests.append(quest_info)

        # Sort by order index if available
        child_quests.sort(key=lambda q: q.order_index if q.order_index is not None else 999)
        return child_quests

    def get_quests_by_giver(self, npc_id: int) -> List[QuestInfo]:
        """Get all quests given by a specific NPC"""
        giver_quests = []

        for quest_info in self.quest_data.values():
            if quest_info.quest_giver_npc_id == npc_id:
                giver_quests.append(quest_info)

        return giver_quests

    def enhance_cff_quest(self, cff_quest) -> QuestInfo:
        """Enhance CFF quest data with external quest information"""
        try:
            # Try to find quest by ID first
            quest_id = getattr(cff_quest, 'quest_id', None)
            if quest_id and quest_id in self.quest_id_mapping:
                external_quest = self.quest_id_mapping[quest_id]
                logger.debug(f"Found external quest data for quest ID {quest_id}")
                return external_quest

            # Try to match by name if available
            quest_name = getattr(cff_quest, 'name', '')
            if quest_name:
                matches = self.get_quest_by_name_search(quest_name)
                if matches:
                    logger.debug(f"Found {len(matches)} potential matches for quest name '{quest_name}'")
                    return matches[0]  # Return first match

            # Create default quest info if no match found
            logger.debug(f"No external quest data found for quest {quest_id}, creating default")
            return QuestInfo(
                quest_flag=f"quest_{quest_id}" if quest_id else "unknown",
                quest_id=quest_id,
                quest_name=getattr(cff_quest, 'name', ''),
                quest_giver_name="",
                rewards=QuestReward()
            )

        except Exception as e:
            logger.error(f"Error enhancing CFF quest: {e}")
            return QuestInfo(quest_flag="error", quest_id=quest_id)

    def get_all_quest_flags(self) -> List[str]:
        """Get list of all quest flags"""
        return list(self.quest_data.keys())

    def get_all_quest_ids(self) -> List[int]:
        """Get list of all quest IDs"""
        return list(self.quest_id_mapping.keys())

    def get_platform_summary(self) -> Dict[str, int]:
        """Get summary of quests by platform"""
        platform_counts = {}

        for quest_info in self.quest_data.values():
            platform = quest_info.platform_name or "Unknown"
            platform_counts[platform] = platform_counts.get(platform, 0) + 1

        return platform_counts

    def _parse_int(self, value: Any) -> Optional[int]:
        """Parse integer from string value"""
        if value is None or value == '':
            return None

        try:
            return int(float(value)) if '.' in str(value) else int(value)
        except (ValueError, TypeError):
            return None

    def _parse_item_list(self, items_string: str) -> List[int]:
        """Parse item list from string format"""
        if not items_string or items_string.strip() == '':
            return []

        items = []
        try:
            # Split by comma, pipe, or vertical bar
            separators = [',', '|', ';']
            for sep in separators:
                if sep in items_string:
                    parts = items_string.split(sep)
                    break
            else:
                parts = [items_string]

            for part in parts:
                part = part.strip()
                if part:
                    # Extract numeric ID
                    import re
                    numbers = re.findall(r'\d+', part)
                    if numbers:
                        items.append(int(numbers[0]))

        except Exception as e:
            logger.warning(f"Error parsing item list '{items_string}': {e}")

        return items

    def _parse_lua_rewards(self, rewards_text: str) -> Dict[str, Any]:
        """Parse LUA rewards text into dictionary"""
        rewards = {}

        try:
            # Extract XP
            import re
            xp_match = re.search(r'XP\s*=\s*\{(\d+)\}', rewards_text)
            if xp_match:
                rewards['xp'] = int(xp_match.group(1))

            # Extract money
            gold_match = re.search(r'Money\s*=\s*\{[^}]*Gold\s*=\s*(\d+)', rewards_text)
            if gold_match:
                rewards['gold'] = int(gold_match.group(1))

            silver_match = re.search(r'Money\s*=\s*\{[^}]*Silver\s*=\s*(\d+)', rewards_text)
            if silver_match:
                rewards['silver'] = int(silver_match.group(1))

            copper_match = re.search(r'Money\s*=\s*\{[^}]*Copper\s*=\s*(\d+)', rewards_text)
            if copper_match:
                rewards['copper'] = int(copper_match.group(1))

            # Extract items
            items_match = re.search(r'Items\s*=\s*\{([^}]+)\}', rewards_text)
            if items_match:
                items_text = items_match.group(1)
                items = self._parse_item_list(items_text)
                rewards['items'] = items

        except Exception as e:
            logger.debug(f"Error parsing LUA rewards: {e}")

        return rewards

    def _parse_lua_quest_objectives(self, script_file: Path) -> List[str]:
        """Parse quest objectives from a LUA script file"""
        objectives = []

        try:
            with open(script_file, 'r', encoding='utf-8') as file:
                content = file.read()

            # Look for objective patterns
            import re

            # Pattern 1: Comments describing objectives
            objective_comments = re.findall(r'--\s*(.*objective.*:?\s*.*)', content, re.IGNORECASE)
            objectives.extend([comment.strip() for comment in objective_comments if comment.strip()])

            # Pattern 2: IsGlobalFlagTrue conditions
            flag_conditions = re.findall(r'IsGlobalFlagTrue\s*\{\s*Name\s*=\s*"([^"]+)"', content)
            for flag in flag_conditions:
                objectives.append(f"Global Flag: {flag}")

            # Pattern 3: Quest state conditions
            quest_states = re.findall(r'QuestState\s*\{\s*Quest\s*=\s*"([^"]+)"[^}]*State\s*=\s*"([^"]+)"', content)
            for quest, state in quest_states:
                objectives.append(f"Quest: {quest} - State: {state}")

        except Exception as e:
            logger.debug(f"Error parsing LUA quest objectives from {script_file}: {e}")

        return objectives


# Global instance
_quest_loader = None

def get_quest_loader() -> QuestDataLoader:
    """Get global quest loader instance"""
    global _quest_loader
    if _quest_loader is None:
        _quest_loader = QuestDataLoader()
    return _quest_loader


def load_quest_data_for_cff(cff_quest) -> QuestInfo:
    """Convenience function to load quest data for a CFF quest"""
    loader = get_quest_loader()
    return loader.enhance_cff_quest(cff_quest)