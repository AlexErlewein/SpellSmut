#!/usr/bin/env python3
"""
Dialogue Data Loader for Quest Viewer
=====================================

Loads and manages dialogue data extracted from Lua quest files.
Integrates with the quest viewer to provide complete dialogue trees.
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass


@dataclass
class DialogueLine:
    """Represents a single dialogue line"""
    tag: str
    text: str
    speaker: str  # "NPC" or "Player"
    answer_id: Optional[int] = None
    conditions: List[str] = None
    quest_id: Optional[int] = None
    npc_name: Optional[str] = None
    file_path: Optional[str] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []


@dataclass
class DialogueTree:
    """Represents a complete dialogue tree for an NPC"""
    npc_name: str
    npc_id: Optional[int]
    file_path: str
    quest_ids: Set[int]
    dialogues: List[DialogueLine]
    
    def get_dialogues_for_quest(self, quest_id: int) -> List[DialogueLine]:
        """Get all dialogues for a specific quest"""
        return [d for d in self.dialogues if d.quest_id == quest_id or not d.quest_id]
    
    def get_player_choices(self, answer_id: int) -> List[DialogueLine]:
        """Get player choices for a specific answer ID"""
        return [d for d in self.dialogues if d.answer_id == answer_id]


class DialogueDataLoader:
    """Loads and manages dialogue data from extracted files"""
    
    def __init__(self, data_directory: Path):
        self.data_directory = data_directory
        self.dialogue_trees: Dict[str, DialogueTree] = {}  # npc_name -> DialogueTree
        self.quest_dialogues: Dict[int, List[DialogueLine]] = {}  # quest_id -> dialogues
        self.loaded = False
    
    def load_dialogue_data(self) -> bool:
        """Load dialogue data from CSV and JSON files"""
        try:
            # Load CSV data
            csv_file = self.data_directory / "CompleteQuestDialogues.csv"
            if not csv_file.exists():
                print(f"Dialogue CSV file not found: {csv_file}")
                return False
            
            # Load JSON summary for quest mappings
            json_file = self.data_directory / "DialogueSummary.json"
            quest_mapping = {}
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    summary = json.load(f)
                    # Create quest ID to NPC mappings
                    for file_path, npc_info in summary.get('file_path_to_npc', {}).items():
                        if isinstance(npc_info, dict):
                            npc_name = npc_info.get('name', 'Unknown')
                        else:
                            npc_name = str(npc_info)
                        # Extract quest IDs from file path or use the summary data
                        quest_ids = set()
                        for quest_id in summary.get('quest_ids', []):
                            quest_ids.add(quest_id)
                        quest_mapping[file_path] = (npc_name, quest_ids)
            
            # Parse CSV data
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Parse dialogue line(s) - can return multiple for multiple quest IDs
                        dialogues = self._parse_csv_row(row, quest_mapping)
                        for dialogue in dialogues:
                            if dialogue:
                                self._add_dialogue(dialogue)
                    except Exception as e:
                        print(f"Error parsing dialogue row: {e}")
                        continue
            
            self.loaded = True
            print(f"Loaded dialogue data for {len(self.dialogue_trees)} NPCs and {len(self.quest_dialogues)} quests")
            return True
            
        except Exception as e:
            print(f"Failed to load dialogue data: {e}")
            return False
    
    def _parse_csv_row(self, row: Dict[str, str], quest_mapping: Dict[str, Tuple[str, Set[int]]]) -> List[DialogueLine]:
        """Parse a single CSV row into one or more DialogueLine objects (one for each quest ID)"""
        try:
            # Map CSV headers to expected fields
            tag = row.get('dialogue_tag', '').strip()
            text = row.get('text', '').strip()
            speaker = row.get('speaker', '').strip()
            answer_id_str = row.get('answer_id', '').strip()
            conditions_str = row.get('conditions', '').strip()
            quest_ids_str = row.get('quest_ids', '').strip()
            npc_name = row.get('npc_name', '').strip()
            npc_id_str = row.get('npc_id', '').strip()
            file_path = row.get('file_path', '').strip()
            
            if not tag or not text:
                return []
            
            # Parse answer ID
            answer_id = None
            if answer_id_str and answer_id_str != 'None' and answer_id_str.strip():
                try:
                    answer_id = int(answer_id_str)
                except ValueError:
                    pass
            
            # Parse NPC ID
            npc_id = None
            if npc_id_str and npc_id_str.strip():
                try:
                    npc_id = int(npc_id_str)
                except ValueError:
                    pass
            
            # Parse quest IDs (semicolon separated) - create multiple dialogues
            quest_ids = []
            if quest_ids_str and quest_ids_str.strip():
                try:
                    # Split by semicolon and parse each quest ID
                    for quest_str in quest_ids_str.split(';'):
                        quest_str = quest_str.strip()
                        if quest_str:
                            quest_id = int(quest_str)
                            quest_ids.append(quest_id)
                except ValueError:
                    pass
            
            # If no quest IDs found, create one dialogue with no quest ID
            if not quest_ids:
                quest_ids = [None]
            
            # Parse conditions
            conditions = []
            if conditions_str and conditions_str.strip() and conditions_str != 'None':
                # Clean up conditions and split by comma if needed
                conditions = [conditions_str.strip()]
            
            # Create a dialogue line for each quest ID
            dialogues = []
            for quest_id in quest_ids:
                dialogues.append(DialogueLine(
                    tag=tag,
                    text=text,
                    speaker=speaker,
                    answer_id=answer_id,
                    conditions=conditions,
                    quest_id=quest_id,
                    npc_name=npc_name,
                    file_path=file_path
                ))
            
            return dialogues
            
        except Exception as e:
            print(f"Error parsing CSV row: {e}")
            return []
    
    def _add_dialogue(self, dialogue: DialogueLine):
        """Add a dialogue line to the appropriate trees"""
        npc_name = dialogue.npc_name or "Unknown"
        
        # Create or get dialogue tree for this NPC
        if npc_name not in self.dialogue_trees:
            self.dialogue_trees[npc_name] = DialogueTree(
                npc_name=npc_name,
                npc_id=None,  # Could be extracted from file path if needed
                file_path=dialogue.file_path or "",
                quest_ids=set(),
                dialogues=[]
            )
        
        # Add dialogue to the tree
        tree = self.dialogue_trees[npc_name]
        tree.dialogues.append(dialogue)
        
        # Track quest IDs
        if dialogue.quest_id:
            tree.quest_ids.add(dialogue.quest_id)
            
            # Add to quest dialogues mapping
            if dialogue.quest_id not in self.quest_dialogues:
                self.quest_dialogues[dialogue.quest_id] = []
            self.quest_dialogues[dialogue.quest_id].append(dialogue)
    
    def get_dialogues_for_quest(self, quest_id: int) -> List[DialogueLine]:
        """Get all dialogues for a specific quest.
        Primary source: rows explicitly mapped to quest_id in CSV.
        Fallback: scan all dialogues without quest_id and include those
        whose conditions mention this quest id (e.g., QuestState {QuestId = X}).
        """
        direct = self.quest_dialogues.get(quest_id)
        if direct:
            return direct

        # Fallback: scan conditions for QuestId references
        pattern = re.compile(rf"\\bQuestId\\s*=\\s*{quest_id}\\b")
        fallback: List[DialogueLine] = []
        for tree in self.dialogue_trees.values():
            for d in tree.dialogues:
                if d.quest_id in (None, 0):
                    conds = d.conditions or []
                    for c in conds:
                        if pattern.search(c):
                            fallback.append(d)
                            break

        # Cache fallback so subsequent calls are fast
        if fallback:
            self.quest_dialogues[quest_id] = fallback
            return fallback
        return []
    
    def get_npc_dialogue_trees(self) -> Dict[str, DialogueTree]:
        """Get all NPC dialogue trees"""
        return self.dialogue_trees
    
    def get_dialogues_for_npc(self, npc_name: str) -> Optional[DialogueTree]:
        """Get dialogue tree for a specific NPC"""
        return self.dialogue_trees.get(npc_name)
    
    def get_quest_count(self) -> int:
        """Get number of quests with dialogues"""
        return len(self.quest_dialogues)
    
    def get_npc_count(self) -> int:
        """Get number of NPCs with dialogues"""
        return len(self.dialogue_trees)
    
    def get_total_dialogue_count(self) -> int:
        """Get total number of dialogue lines"""
        return sum(len(tree.dialogues) for tree in self.dialogue_trees.values())
    
    def search_dialogues(self, query: str) -> List[DialogueLine]:
        """Search dialogues by text"""
        query = query.lower()
        results = []
        for tree in self.dialogue_trees.values():
            for dialogue in tree.dialogues:
                if query in dialogue.text.lower():
                    results.append(dialogue)
        return results
