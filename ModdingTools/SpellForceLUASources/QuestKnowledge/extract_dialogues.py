#!/usr/bin/env python3
"""
Dialogue Extraction Script for SpellForce Quest System

This script extracts all dialogues from Lua files in the SpellForce project,
organizing them into complete dialogue trees with questions and answers.
Outputs both Markdown and CSV formats for easy analysis and reference.
"""

import os
import re
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class DialogueLine:
    """Represents a single dialogue line"""
    tag: str
    text: str
    speaker: str  # NPC or Player
    answer_id: Optional[int] = None
    conditions: List[str] = None
    actions: List[str] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []
        if self.actions is None:
            self.actions = []

@dataclass
class DialogueTree:
    """Represents a complete dialogue tree for an NPC"""
    npc_name: str
    npc_id: str
    file_path: str
    quest_ids: List[int]
    dialogues: List[DialogueLine]
    dialogue_branches: Dict[str, List[DialogueLine]] = None
    
    def __post_init__(self):
        if self.dialogue_branches is None:
            self.dialogue_branches = {}

class DialogueExtractor:
    """Extracts dialogues from SpellForce Lua files"""
    
    def __init__(self, lua_sources_path: str):
        self.lua_sources_path = Path(lua_sources_path)
        self.dialogue_trees = []
        self.quest_mapping = {}
    
    def _read_text(self, lua_file: Path) -> str:
        data = lua_file.read_bytes()
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return data.decode('cp1252')
            except UnicodeDecodeError:
                return data.decode('latin-1', errors='replace')
        
    def extract_all_dialogues(self) -> List[DialogueTree]:
        """Extract all dialogues from Lua files"""
        print("Starting dialogue extraction...")
        
        # Find all Lua files in script directories
        lua_files = list(self.lua_sources_path.rglob("script/**/*.lua"))
        print(f"Found {len(lua_files)} Lua files to process")
        
        # Filter to only files that likely contain dialogues
        dialogue_files = []
        for lua_file in lua_files:
            try:
                with open(lua_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'OnBeginDialog' in content or 'OnAnswer' in content:
                        dialogue_files.append(lua_file)
            except Exception:
                continue
                
        print(f"Found {len(dialogue_files)} files with dialogue content")
        
        for i, lua_file in enumerate(dialogue_files):
            try:
                dialogue_tree = self.extract_dialogues_from_file(lua_file)
                if dialogue_tree and dialogue_tree.dialogues:
                    self.dialogue_trees.append(dialogue_tree)
                    if (i + 1) % 10 == 0 or i < 10:
                        print(f"Extracted {len(dialogue_tree.dialogues)} dialogues from {lua_file.name}")
            except Exception as e:
                print(f"Error processing {lua_file}: {e}")
                
        print(f"Total dialogue trees extracted: {len(self.dialogue_trees)}")
        return self.dialogue_trees
    
    def extract_dialogues_from_file(self, lua_file: Path) -> Optional[DialogueTree]:
        """Extract dialogues from a single Lua file"""
        try:
            content = self._read_text(lua_file)
        except Exception as e:
            print(f"Could not read file {lua_file}: {e}")
            return None
            
        # Extract NPC name from INFO comment or filename
        npc_name = self.extract_npc_name(content, lua_file)
        npc_id = self.extract_npc_id(content, lua_file)
        
        # Find all dialogue blocks
        dialogue_lines = []
        quest_ids = set()
        
        # Extract OnBeginDialog blocks
        begin_dialogs = self.extract_begin_dialogs(content, quest_ids)
        dialogue_lines.extend(begin_dialogs)
        
        # Extract OnAnswer blocks
        answer_dialogs = self.extract_answer_dialogs(content, quest_ids)
        dialogue_lines.extend(answer_dialogs)
        
        if not dialogue_lines:
            return None
            
        # Organize dialogues into branches
        dialogue_branches = self.organize_dialogue_branches(dialogue_lines)
        
        # Fallback: if we still have no quest ids but the file contains QuestId references
        if not quest_ids:
            file_qids = re.findall(r'QuestId\s*=\s*(\d+)', content)
            quest_ids.update(map(int, file_qids))
        
        return DialogueTree(
            npc_name=npc_name,
            npc_id=npc_id,
            file_path=str(lua_file.relative_to(self.lua_sources_path)),
            quest_ids=list(quest_ids),
            dialogues=dialogue_lines,
            dialogue_branches=dialogue_branches
        )
    
    def extract_npc_name(self, content: str, lua_file: Path) -> str:
        """Extract NPC name from file content or filename"""
        # Look for INFO comment
        info_match = re.search(r'-->INFO:\s*(.+)', content)
        if info_match:
            return info_match.group(1).strip()
            
        # Try to extract from filename
        filename = lua_file.stem
        if filename.startswith('n'):
            # Remove 'n' prefix and _Cutscene suffix if present
            name = filename[1:]
            if '_Cutscene' in name:
                name = name.split('_Cutscene')[0]
            return name
            
        return filename
    
    def extract_npc_id(self, content: str, lua_file: Path) -> str:
        """Extract NPC ID from filename"""
        filename = lua_file.stem
        # Look for numeric ID in filename
        id_match = re.search(r'n(\d+)', filename)
        if id_match:
            return id_match.group(1)
        return "unknown"
    
    def extract_begin_dialogs(self, content: str, quest_ids: set) -> List[DialogueLine]:
        """Extract dialogues from OnBeginDialog blocks"""
        dialogues = []
        
        # Pattern to match OnBeginDialog blocks with proper brace handling
        # We need to handle nested braces, so we'll parse manually
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('OnBeginDialog{'):
                # Found start of block, find the end
                brace_count = 1
                start_line = i
                i += 1
                while i < len(lines) and brace_count > 0:
                    current_line = lines[i]
                    brace_count += current_line.count('{')
                    brace_count -= current_line.count('}')
                    i += 1
                
                # Extract the block content (excluding the outer braces)
                block_content = '\n'.join(lines[start_line+1:i-1])
                
                # Extract conditions
                conditions = self.extract_conditions(block_content)
                
                # Extract Say statements
                say_matches = re.findall(r'Say\{\s*Tag\s*=\s*"([^"]+)",\s*String\s*=\s*"([^"]+)"\s*\}', block_content)
                for tag, text in say_matches:
                    dialogues.append(DialogueLine(
                        tag=tag,
                        text=self.clean_text(text),
                        speaker="NPC",
                        conditions=conditions
                    ))
                    
                # Extract Answer and OfferAnswer statements
                answer_pattern = r'(OfferAnswer|Answer)\{\s*Tag\s*=\s*"([^"]+)",\s*String\s*=\s*"([^"]+)",\s*AnswerId\s*=\s*(\d+)\s*\}'
                answer_matches = re.findall(answer_pattern, block_content)
                for answer_type, tag, text, answer_id in answer_matches:
                    dialogues.append(DialogueLine(
                        tag=tag,
                        text=self.clean_text(text),
                        speaker="Player",
                        answer_id=int(answer_id),
                        conditions=conditions
                    ))
                
                # Extract quest IDs from conditions
                for condition in conditions:
                    quest_matches = re.findall(r'QuestId\s*=\s*(\d+)', condition)
                    quest_ids.update(map(int, quest_matches))
                
                # Extract quest IDs from actions inside OnBeginDialog blocks
                action_matches = re.findall(r'Quest(Begin|Solve)\{\s*QuestId\s*=\s*(\d+)\s*\}', block_content)
                for action, qid in action_matches:
                    quest_ids.add(int(qid))
                
                # Extract quest IDs anywhere in the block content
                block_qids = re.findall(r'QuestId\s*=\s*(\d+)', block_content)
                quest_ids.update(map(int, block_qids))
            else:
                i += 1
                
        return dialogues
    
    def extract_answer_dialogs(self, content: str, quest_ids: set) -> List[DialogueLine]:
        """Extract dialogues from OnAnswer blocks"""
        dialogues = []
        
        # Manual parsing for OnAnswer blocks with proper brace handling
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('OnAnswer{'):
                # Extract answer ID from the opening line
                answer_id_match = re.search(r'OnAnswer\{(\d+);', line)
                if not answer_id_match:
                    i += 1
                    continue
                    
                answer_id = int(answer_id_match.group(1))
                
                # Found start of block, find the end
                brace_count = 1
                start_line = i
                i += 1
                while i < len(lines) and brace_count > 0:
                    current_line = lines[i]
                    brace_count += current_line.count('{')
                    brace_count -= current_line.count('}')
                    i += 1
                
                # Extract the block content (excluding the outer braces)
                block_content = '\n'.join(lines[start_line+1:i-1])
                
                # Extract conditions
                conditions = self.extract_conditions(block_content)
                
                # Extract Say statements
                say_matches = re.findall(r'Say\{\s*Tag\s*=\s*"([^"]+)",\s*String\s*=\s*"([^"]+)"\s*\}', block_content)
                for tag, text in say_matches:
                    dialogues.append(DialogueLine(
                        tag=tag,
                        text=self.clean_text(text),
                        speaker="NPC",
                        conditions=conditions,
                        answer_id=answer_id
                    ))
                    
                # Extract Answer and OfferAnswer statements
                answer_pattern = r'(OfferAnswer|Answer)\{\s*Tag\s*=\s*"([^"]+)",\s*String\s*=\s*"([^"]+)",\s*AnswerId\s*=\s*(\d+)\s*\}'
                answer_matches = re.findall(answer_pattern, block_content)
                for answer_type, tag, text, new_answer_id in answer_matches:
                    dialogues.append(DialogueLine(
                        tag=tag,
                        text=self.clean_text(text),
                        speaker="Player",
                        answer_id=int(new_answer_id),
                        conditions=conditions
                    ))
                
                # Extract quest IDs from conditions and actions
                for condition in conditions:
                    quest_matches = re.findall(r'QuestId\s*=\s*(\d+)', condition)
                    quest_ids.update(map(int, quest_matches))
                    
                # Extract quest actions
                action_matches = re.findall(r'Quest(Begin|Solve)\{\s*QuestId\s*=\s*(\d+)\s*\}', block_content)
                for action, quest_id in action_matches:
                    quest_ids.add(int(quest_id))
                
                # Extract quest IDs anywhere in the block content
                block_qids = re.findall(r'QuestId\s*=\s*(\d+)', block_content)
                quest_ids.update(map(int, block_qids))
            else:
                i += 1
                
        return dialogues
    
    def extract_conditions(self, block: str) -> List[str]:
        """Extract conditions from a dialogue block"""
        conditions = []
        
        # Find Conditions block (handle flexible whitespace)
        conditions_match = re.search(r'Conditions\s*=\s*\{(.*?)\}', block, re.DOTALL)
        if conditions_match:
            conditions_text = conditions_match.group(1)
            # Split by lines and clean up
            for line in conditions_text.split('\n'):
                line = line.strip()
                if line and not line.startswith('--'):
                    conditions.append(line)
                    
        return conditions
    
    def clean_text(self, text: str) -> str:
        """Clean dialogue text"""
        s = text.replace('\\n', '\n')
        # Fix common mojibake (e.g., 'Ã¤', 'ÃŸ', 'â€¦') by latin1->utf8 roundtrip
        if 'Ã' in s or 'â' in s or '�' in s:
            try:
                s = s.encode('latin1').decode('utf-8')
            except Exception:
                # If roundtrip fails, leave as-is
                pass
        return s.strip()
    
    def organize_dialogue_branches(self, dialogues: List[DialogueLine]) -> Dict[str, List[DialogueLine]]:
        """Organize dialogues into conversation branches"""
        branches = defaultdict(list)
        
        # Group by answer_id to create conversation flows
        for dialogue in dialogues:
            if dialogue.answer_id is not None:
                branch_key = f"answer_{dialogue.answer_id}"
                branches[branch_key].append(dialogue)
            else:
                branches["initial"].append(dialogue)
                
        return dict(branches)
    
    def export_to_markdown(self, output_path: str):
        """Export dialogues to Markdown format"""
        print(f"Exporting dialogues to Markdown: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# SpellForce Quest Dialogues\n\n")
            f.write("This document contains all extracted dialogues from SpellForce quest scripts.\n\n")
            
            # Table of contents
            f.write("## Table of Contents\n\n")
            for i, tree in enumerate(self.dialogue_trees):
                f.write(f"{i+1}. [{tree.npc_name}](#{tree.npc_name.lower().replace(' ', '-')})\n")
            f.write("\n---\n\n")
            
            # Export each dialogue tree
            for tree in self.dialogue_trees:
                f.write(f"## {tree.npc_name}\n\n")
                f.write(f"**NPC ID:** {tree.npc_id}  \n")
                f.write(f"**File:** `{tree.file_path}`  \n")
                f.write(f"**Quest IDs:** {', '.join(map(str, tree.quest_ids))}  \n\n")
                
                # Organize by conversation flow
                if tree.dialogue_branches:
                    for branch_name, branch_dialogues in tree.dialogue_branches.items():
                        if branch_name == "initial":
                            f.write("### Initial Dialogue\n\n")
                        else:
                            f.write(f"### Response Branch {branch_name}\n\n")
                            
                        for dialogue in branch_dialogues:
                            speaker_icon = "🗣️" if dialogue.speaker == "NPC" else "💬"
                            f.write(f"{speaker_icon} **{dialogue.speaker}:** {dialogue.text}\n\n")
                            f.write(f"*Tag: `{dialogue.tag}`*\n\n")
                            
                            if dialogue.conditions:
                                f.write("**Conditions:**\n")
                                for condition in dialogue.conditions:
                                    f.write(f"- `{condition}`\n")
                                f.write("\n")
                                
                            if dialogue.answer_id:
                                f.write(f"*Answer ID: {dialogue.answer_id}*\n\n")
                                
                f.write("---\n\n")
                
        print(f"Markdown export completed: {len(self.dialogue_trees)} dialogue trees")
    
    def export_to_csv(self, output_path: str):
        """Export dialogues to CSV format"""
        print(f"Exporting dialogues to CSV: {output_path}")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'npc_name', 'npc_id', 'file_path', 'quest_ids',
                'dialogue_tag', 'speaker', 'text', 'answer_id',
                'conditions', 'branch_type'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for tree in self.dialogue_trees:
                for branch_name, branch_dialogues in tree.dialogue_branches.items():
                    for dialogue in branch_dialogues:
                        writer.writerow({
                            'npc_name': tree.npc_name,
                            'npc_id': tree.npc_id,
                            'file_path': tree.file_path,
                            'quest_ids': ';'.join(map(str, tree.quest_ids)),
                            'dialogue_tag': dialogue.tag,
                            'speaker': dialogue.speaker,
                            'text': dialogue.text,
                            'answer_id': dialogue.answer_id or '',
                            'conditions': ';'.join(dialogue.conditions),
                            'branch_type': branch_name
                        })
                        
        print(f"CSV export completed: {len(self.dialogue_trees)} dialogue trees")
    
    def export_dialogue_summary(self, output_path: str):
        """Export a summary of all dialogues"""
        print(f"Exporting dialogue summary: {output_path}")
        
        summary = {
            'total_npcs': len(self.dialogue_trees),
            'total_dialogues': sum(len(tree.dialogues) for tree in self.dialogue_trees),
            'quests_covered': set(),
            'npcs_by_file': {}
        }
        
        for tree in self.dialogue_trees:
            summary['quests_covered'].update(tree.quest_ids)
            summary['npcs_by_file'][tree.file_path] = tree.npc_name
            
        summary['quests_covered'] = list(summary['quests_covered'])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        print(f"Summary exported: {summary['total_npcs']} NPCs, {summary['total_dialogues']} dialogues")

def main():
    """Main execution function"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent.parent
    lua_sources_path = project_root / "ModdingTools" / "SpellForceLUASources"
    output_dir = Path(__file__).parent
    
    print(f"Project root: {project_root}")
    print(f"Lua sources: {lua_sources_path}")
    print(f"Output directory: {output_dir}")
    
    # Initialize extractor
    extractor = DialogueExtractor(lua_sources_path)
    
    # Extract all dialogues
    dialogue_trees = extractor.extract_all_dialogues()
    
    if dialogue_trees:
        # Export to different formats
        extractor.export_to_markdown(output_dir / "CompleteQuestDialogues.md")
        extractor.export_to_csv(output_dir / "CompleteQuestDialogues.csv")
        extractor.export_dialogue_summary(output_dir / "DialogueSummary.json")
        
        print("\n" + "="*50)
        print("DIALOGUE EXTRACTION COMPLETED")
        print("="*50)
        print(f"Total NPCs processed: {len(dialogue_trees)}")
        print(f"Total dialogue lines: {sum(len(tree.dialogues) for tree in dialogue_trees)}")
        print(f"Output files created:")
        print(f"  - CompleteQuestDialogues.md")
        print(f"  - CompleteQuestDialogues.csv")
        print(f"  - DialogueSummary.json")
    else:
        print("No dialogues were extracted!")

if __name__ == "__main__":
    main()
