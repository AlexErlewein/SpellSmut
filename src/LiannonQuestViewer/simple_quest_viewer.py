#!/usr/bin/env python3
"""
Simple Standalone Quest Viewer Application - CLEAN VERSION
==========================================

A lightweight application for viewing SpellForce quest data.
Uses cached Lua files and triggers cache creation if needed.

Usage:
    python simple_quest_viewer.py [--debug] [--rebuild-cache]
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QSplitter,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Add the src directory to Python path
# This file is in src/LiannonQuestViewer/, so project root is 2 levels up
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.data_model import CFFDataModel
from TirganachReloaded.cff_editor.logging_config import configure_logging, get_logger
from TirganachReloaded.cff_editor.lua_parser.lua_data_manager import LuaDataManager
from TirganachReloaded.cff_editor.services.quest_data_service import QuestDataService
from dialogue_loader import DialogueDataLoader


class DialogueNode:
    """Represents a single node in a dialogue tree"""
    
    def __init__(self, tag: str, text: str, speaker: str, answer_id: Optional[int] = None, conditions: List[str] = None):
        self.tag = tag
        self.text = text
        self.speaker = speaker
        self.answer_id = answer_id
        self.conditions = conditions or []
        self.children = []  # Nodes that can follow this one
        self.parent = None  # Node that precedes this one
    
    def add_child(self, child_node: 'DialogueNode'):
        """Add a child node (possible response)"""
        if child_node not in self.children:
            self.children.append(child_node)
            child_node.parent = self
    
    def is_player_choice(self) -> bool:
        """Check if this is a player choice"""
        return self.speaker.lower() == "player"
    
    def is_npc_statement(self) -> bool:
        """Check if this is an NPC statement"""
        return self.speaker.lower() != "player"


class DialogueTree:
    """Represents a complete dialogue tree for an NPC"""
    
    def __init__(self, npc_name: str):
        self.npc_name = npc_name
        self.nodes = {}  # tag -> DialogueNode
        self.root_nodes = []  # Starting nodes (usually NPC statements)
    
    def add_node(self, node: DialogueNode):
        """Add a node to the tree"""
        self.nodes[node.tag] = node
        
        # Determine if this is a root node (no answer_id or answer_id == 0)
        if node.answer_id is None or node.answer_id == 0:
            if node not in self.root_nodes:
                self.root_nodes.append(node)
    
    def build_connections(self):
        """Build connections between nodes based on answer IDs and dialogue flow"""
        # Group nodes by answer_id
        answer_groups = {}
        for node in self.nodes.values():
            if node.answer_id is not None:
                if node.answer_id not in answer_groups:
                    answer_groups[node.answer_id] = []
                answer_groups[node.answer_id].append(node)
        
        # Build connections based on dialogue flow patterns
        for node in self.nodes.values():
            if node.is_npc_statement():
                # NPC statements connect to player choices with same answer_id
                if node.answer_id in answer_groups:
                    for child in answer_groups[node.answer_id]:
                        if child.is_player_choice():
                            node.add_child(child)
            
            elif node.is_player_choice():
                # Player choices connect to subsequent NPC statements
                # Look for NPC statements that could logically follow this choice
                # Sort potential children by answer_id to get the next logical statement
                potential_children = []
                for potential_child in self.nodes.values():
                    if (potential_child.is_npc_statement() and 
                        potential_child.answer_id is not None and 
                        potential_child.answer_id > node.answer_id):
                        potential_children.append(potential_child)
                
                # Sort by answer_id to get the closest next statement
                potential_children.sort(key=lambda x: x.answer_id)
                
                # Connect to the next NPC statement(s) with the next higher answer_id(s)
                if potential_children:
                    # Connect to the very next statement primarily
                    node.add_child(potential_children[0])
                    
                    # If there are multiple statements with the same answer_id, connect to all
                    next_answer_id = potential_children[0].answer_id
                    for child in potential_children:
                        if child.answer_id == next_answer_id and child != potential_children[0]:
                            node.add_child(child)
    
    def get_conversation_flows(self) -> List[List[DialogueNode]]:
        """Get all possible conversation flows as linear sequences in proper order"""
        flows = []
        
        # Start from root nodes (usually initial NPC statements)
        # Sort root nodes by answer_id to get proper starting order
        sorted_roots = sorted(self.root_nodes, key=lambda x: (x.answer_id or 0, x.tag))
        
        for root in sorted_roots:
            # Build all possible flows from this root
            root_flows = self._build_all_flows_from_node(root)
            flows.extend(root_flows)
        
        # Add any isolated nodes as individual flows
        processed_tags = set()
        for flow in flows:
            for node in flow:
                processed_tags.add(node.tag)
        
        for tag, node in self.nodes.items():
            if tag not in processed_tags:
                flows.append([node])
        
        # Sort flows to maintain dialogue order:
        # 1. Primary: By starting node's answer_id (chronological order)
        # 2. Secondary: By flow length (longer conversations first)
        # 3. Tertiary: By tag for consistency
        def flow_sort_key(flow):
            if not flow:
                return (999999, 0, "")
            start_answer_id = flow[0].answer_id or 0
            flow_length = len(flow)
            start_tag = flow[0].tag or ""
            return (start_answer_id, -flow_length, start_tag)
        
        flows.sort(key=flow_sort_key)
        
        return flows
    
    def _build_all_flows_from_node(self, node: DialogueNode, current_flow: List[DialogueNode] = None, max_depth: int = 8) -> List[List[DialogueNode]]:
        """Build all possible flows starting from a node"""
        if current_flow is None:
            current_flow = []
        
        # Avoid infinite loops
        if node in current_flow or len(current_flow) >= max_depth:
            return [current_flow.copy()] if current_flow else []
        
        current_flow.append(node)
        
        if not node.children:
            # End of this flow
            return [current_flow.copy()]
        
        # Build flows for each child
        all_flows = []
        for child in node.children:
            child_flows = self._build_all_flows_from_node(child, current_flow.copy(), max_depth)
            all_flows.extend(child_flows)
        
        return all_flows
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about this dialogue tree"""
        total_nodes = len(self.nodes)
        player_choices = sum(1 for node in self.nodes.values() if node.is_player_choice())
        npc_statements = total_nodes - player_choices
        
        # Count branches (nodes with multiple children)
        branches = sum(1 for node in self.nodes.values() if len(node.children) > 1)
        
        return {
            'total_nodes': total_nodes,
            'player_choices': player_choices,
            'npc_statements': npc_statements,
            'branches': branches
        }

# Platform/Map location name mappings
PLATFORM_NAMES = {
    "P1": "Liannon",
    "P2": "Eloni",
    "P3": "Leafshade",
    "P4": "Wildland Pass",
    "P5": "Shiel",
    "P6": "Wildland Pass / Greyfell area",
    "P7": "Ice Gate",
    "P8": "Underhall",
    "P10": "Iron Fields",
    "P11": "The Shiel",
    "P12": "峡谷",
    "P15": "Desert / Burning Sands",
    "P16": "Whisper",
    "P17": "Tirganach",
    "P19": "Dun Mora",
    "P23": "The Gorge",
    "P25": "Godmark / Mountains",
    "P27": "Urgath",
    "P30": "Breathing Forest",
    "P32": "Soul Forge",
    "P63": "Greyfell",
    "P101": "Tutorial",
    "P105": "Tirganach",
    "P107": "Encounter Map",
    "P108": "Encounter Map",
    "P109": "Warzone",
    "P110": "Ghost Watch",
    "P111": "Shadow Realm",
    "P113": "Undergound",
    "P115": "Dragon Storm",
}

# German location name mappings
GERMAN_PLATFORM_NAMES = {
    "liannon": "Liannon",
    "eloni": "Eloni", 
    "leafshade": "Laubschatten",
    "wildland pass": "Wildlandpass",
    "shiel": "Shiel",
    "icegate marsh": "Eispfortensumpf",
    "northern windwalls": "Nördliche Windmauern",
    "southern windwalls": "Südliche Windmauern",
    "stoneblade mountain": "Steinklippenberg",
    "greydusk vale": "Graudämmtal",
    "howling mounds": "Heulende Hügel",
    "whisper": "Flüstern",
    "godwall": "Gottwall",
    "mulandir": "Mulandir",
    "farlorns hope": "Farlorns Hoffnung",
    "the rift": "Der Spalt",
    "southern godmark": "Südliches Gottesmal",
    "nightwhisper dale": "Nachtflüstertal",
    "breathing forest": "Atmender Wald",
    "sharrowdale": "Scharrental",
    "greyfell": "Graufell",
    "swamp city": "Sumpfstadt",
    "onyx shores": "Onyxküsten",
    "empyiria": "Empyria",
    "dryad cove": "Dryadenbucht",
    "red wastes": "Rote Wüsten",
    "raven pass": "Rabenpass",
    "blazing stones": "Flammende Steine",
    "kathai": "Kathai",
    "colloseum": "Kolosseum",
    "blackwater coast": "Schwarzwasser Küste",
    "city of souls": "Stadt der Seelen",
}


def get_platform_display_name(platform_id):
    """Convert platform ID to display name (e.g., P1 -> Liannon (P1))"""
    if not platform_id:
        return "Unknown Location"

    platform_name = PLATFORM_NAMES.get(platform_id, None)
    if platform_name:
        return f"{platform_name} ({platform_id})"
    return platform_id


def get_german_platform_name(platform_name):
    """Convert English platform name to German (e.g., liannon -> Liannon)"""
    if not platform_name:
        return "Unbekannter Ort"
    
    return GERMAN_PLATFORM_NAMES.get(platform_name.lower(), platform_name)


class SimpleQuestViewer(QMainWindow):
    """Simple standalone quest viewer"""

    def __init__(self):
        super().__init__()
        self.logger = None
        self.lua_manager = None
        self.data_model = None
        self.quest_data = {}
        self.current_quest_id = None
        self.quest_service = None
        self.dialogue_loader = None
        self.dialogue_view_mode = "simple"  # Default to simple view
        self.metadata_view_mode = "full"  # Default to full details view

        # Initialize settings for preferences persistence
        self.settings = QSettings("SpellSmut", "QuestViewer")

        self.init_ui()
        self.restore_preferences()
        self.load_data()

    def load_csv_quest_data(self):
        """Load quest data from the CSV file to fill holes in existing data"""
        csv_file = project_root / "ModdingTools/SpellForceLUASources/QuestKnowledge/QuestRewards.csv"
        
        if not csv_file.exists():
            if self.logger:
                self.logger.warning(f"CSV file not found: {csv_file}")
            return
            
        try:
            csv_data = {}
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        quest_id = int(row['quest_id']) if row['quest_id'] else None
                        if quest_id is None:
                            continue
                            
                        csv_data[quest_id] = {
                            'quest_name': row['quest_name'],
                            'quest_name_de': row['quest_name_de'],
                            'quest_description_de': row['quest_description_de'],
                            'quest_name_loc': row['quest_name_loc'],
                            'quest_description_loc': row['quest_description_loc'],
                            'quest_giver_npc_id': int(row['quest_giver_npc_id']) if row['quest_giver_npc_id'] and row['quest_giver_npc_id'].strip() else None,
                            'quest_giver_name': row['quest_giver_name'],
                            'parent_quest_id': int(row['parent_quest_id']) if row['parent_quest_id'] and row['parent_quest_id'].strip() else None,
                            'parent_chain': row['parent_chain'],
                            'order_index': int(row['order_index']) if row['order_index'] and row['order_index'].strip() else 0,
                            'quest_maps': row['quest_maps'],
                            'platform_name': row['platform_name'],
                            'platform_name_de': get_german_platform_name(row['platform_name']),
                            'xp': int(row['xp']) if row['xp'] and row['xp'].strip() else 0,
                            'gold': int(row['gold']) if row['gold'] and row['gold'].strip() else 0,
                            'silver': int(row['silver']) if row['silver'] and row['silver'].strip() else 0,
                            'copper': int(row['copper']) if row['copper'] and row['copper'].strip() else 0,
                            'items_given': row['items_given'],
                            'items_taken': row['items_taken'],
                        }
                    except ValueError as e:
                        if self.logger:
                            self.logger.warning(f"Skipping CSV row due to parsing error: {e}")
                        continue
            
            if self.logger:
                self.logger.info(f"Loaded {len(csv_data)} quest entries from CSV")
            
            # Enhance existing quest data with CSV information
            enhanced_count = 0
            for quest_id, csv_info in csv_data.items():
                if quest_id in self.quest_data:
                    quest = self.quest_data[quest_id]
                    
                    # Fill missing quest giver name
                    if csv_info['quest_giver_name'] and not quest.get('quest_giver_name'):
                        quest['quest_giver_name'] = csv_info['quest_giver_name']
                        enhanced_count += 1
                    
                    # Fill missing German name/description if available
                    if csv_info['quest_name_de'] and not quest.get('quest_name_de'):
                        quest['quest_name_de'] = csv_info['quest_name_de']
                    
                    if csv_info['quest_description_de'] and not quest.get('quest_description_de'):
                        quest['quest_description_de'] = csv_info['quest_description_de']
                    
                    # Fill platform names (both English and German)
                    if csv_info['platform_name'] and not quest.get('platform_name'):
                        quest['platform_name'] = csv_info['platform_name']
                    
                    if csv_info['platform_name_de'] and not quest.get('platform_name_de'):
                        quest['platform_name_de'] = csv_info['platform_name_de']
                    
                    # Create enhanced reward object if CSV has reward data
                    if any([csv_info['xp'], csv_info['gold'], csv_info['silver'], csv_info['copper']]):
                        if not quest.get('rewards') or (hasattr(quest.get('rewards'), 'xp') and quest['rewards'].xp == 0):
                            # Create a simple reward object
                            class CSVReward:
                                def __init__(self, xp, gold, silver, copper, items_given, items_taken):
                                    self.xp = xp
                                    self.gold = gold
                                    self.silver = silver
                                    self.copper = copper
                                    self.items = []
                                    self.reward_flags = []
                                    self.items_given = items_given
                                    self.items_taken = items_taken
                            
                            quest['rewards'] = CSVReward(
                                csv_info['xp'], csv_info['gold'], csv_info['silver'], 
                                csv_info['copper'], csv_info['items_given'], csv_info['items_taken']
                            )
                            enhanced_count += 1
                    
                    # Fill missing parent quest info
                    if csv_info['parent_quest_id'] and not quest.get('parent_id'):
                        quest['parent_id'] = csv_info['parent_quest_id']
                        enhanced_count += 1
                    
                    # Fill order index
                    if csv_info['order_index'] and not quest.get('order_index'):
                        quest['order_index'] = csv_info['order_index']
                    
                    # Add quest chain info
                    if csv_info['parent_chain'] and not quest.get('parent_chain'):
                        quest['parent_chain'] = csv_info['parent_chain']
            
            if self.logger:
                self.logger.info(f"Enhanced {enhanced_count} quests with CSV data")
                
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to load CSV quest data: {e}")

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("TirganachReloaded: Simple Quest Viewer")
        self.setMinimumSize(QSize(1200, 800))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Header with reload button
        header_layout = QHBoxLayout()
        title_label = QLabel("Quest Viewer")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        export_btn = QPushButton("Export Quest")
        export_btn.clicked.connect(self.export_quest)
        export_btn.setEnabled(False)  # Disabled until quest is selected
        self.export_btn = export_btn
        header_layout.addWidget(export_btn)

        reload_btn = QPushButton("Reload Data")
        reload_btn.clicked.connect(self.reload_data)
        header_layout.addWidget(reload_btn)

        rebuild_cache_btn = QPushButton("Rebuild Cache")
        rebuild_cache_btn.clicked.connect(self.rebuild_cache)
        header_layout.addWidget(rebuild_cache_btn)

        layout.addLayout(header_layout)

        # Main splitter
        self.splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.splitter)

        # Left side - Quest tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        tree_group = QGroupBox("Quests")
        tree_layout = QVBoxLayout(tree_group)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID, name, or description...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        tree_layout.addLayout(search_layout)

        # Filter dropdowns
        filter_layout = QHBoxLayout()

        # Platform/Location filter
        platform_label = QLabel("Location:")
        self.platform_filter = QComboBox()
        self.platform_filter.addItem("All Locations", None)
        for pid in sorted(
            PLATFORM_NAMES.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 999
        ):
            name = PLATFORM_NAMES[pid]
            self.platform_filter.addItem(f"{name} ({pid})", pid)
        self.platform_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(platform_label)
        filter_layout.addWidget(self.platform_filter)

        # Quest Giver filter (will be populated after data loads)
        giver_label = QLabel("Quest Giver:")
        self.giver_filter = QComboBox()
        self.giver_filter.addItem("All Quest Givers", None)
        self.giver_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(giver_label)
        filter_layout.addWidget(self.giver_filter)
        
        # Dialogue filter
        dialogue_label = QLabel("Has Dialogues:")
        self.dialogue_filter = QComboBox()
        self.dialogue_filter.addItem("All Quests", None)
        self.dialogue_filter.addItem("With Dialogues Only", True)
        self.dialogue_filter.addItem("Without Dialogues", False)
        self.dialogue_filter.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(dialogue_label)
        filter_layout.addWidget(self.dialogue_filter)
        
        # Metadata toggle
        metadata_label = QLabel("Show Dialogue Metadata:")
        self.metadata_toggle = QComboBox()
        self.metadata_toggle.addItem("Full Details", "full")
        self.metadata_toggle.addItem("Clean Dialogues", "dialogue_only")
        self.metadata_toggle.currentIndexChanged.connect(self.on_metadata_view_changed)
        filter_layout.addWidget(metadata_label)
        filter_layout.addWidget(self.metadata_toggle)

        filter_layout.addStretch()
        tree_layout.addLayout(filter_layout)

        # Search results label
        self.search_results_label = QLabel("")
        self.search_results_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        tree_layout.addWidget(self.search_results_label)

        self.quest_tree = QTreeWidget()
        self.quest_tree.setHeaderLabels(["Quest Name"])
        self.quest_tree.setColumnWidth(0, 400)  # Make name column wider
        self.quest_tree.itemSelectionChanged.connect(
            lambda: self.on_quest_selection_changed()
        )
        tree_layout.addWidget(self.quest_tree)

        # Tree controls
        tree_controls = QHBoxLayout()
        expand_btn = QPushButton("Expand All")
        expand_btn.clicked.connect(self.quest_tree.expandAll)
        collapse_btn = QPushButton("Collapse All")
        collapse_btn.clicked.connect(self.quest_tree.collapseAll)
        tree_controls.addWidget(expand_btn)
        tree_controls.addWidget(collapse_btn)
        tree_layout.addLayout(tree_controls)

        left_layout.addWidget(tree_group)
        self.splitter.addWidget(left_widget)

        # Right side - Quest details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        details_group = QGroupBox("Quest Details")
        details_layout = QVBoxLayout(details_group)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setHtml("<p>Select a quest to view details...</p>")
        details_layout.addWidget(self.details_text)

        right_layout.addWidget(details_group)
        self.splitter.addWidget(right_widget)

        # Set splitter proportions
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)

        # Status bar
        self.statusBar().showMessage("Ready")

    def load_data(self):
        """Load quest data with progress indication"""
        import time

        # Create progress dialog
        progress = QProgressDialog("Loading quest data...", None, 0, 7, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Loading")
        progress.setMinimumDuration(0)  # Show immediately
        progress.setValue(0)
        progress.show()
        QApplication.processEvents()

        start_time = time.time()

        try:
            self.statusBar().showMessage("Loading quest data...")

            # Configure logging
            if not self.logger:
                configure_logging()
                self.logger = get_logger("quest_viewer")

            # Step 1: Initialize data model
            progress.setLabelText("Initializing data model...")
            progress.setValue(1)
            QApplication.processEvents()

            self.data_model = CFFDataModel()

            # Initialize QuestDataService
            try:
                # Use the module-level project_root (already calculated)
                self.quest_service = QuestDataService(project_root)
                self.logger.info("QuestDataService initialized")
            except Exception as e:
                self.logger.warning(f"Could not initialize QuestDataService: {e}")
                self.quest_service = None

            # Step 2: Load GameData.cff file
            cff_file = Path("OriginalGameFiles/data/GameData.cff")
            if not cff_file.exists():
                progress.close()
                QMessageBox.critical(
                    self, "Error", f"GameData.cff not found at:\n{cff_file}"
                )
                return

            progress.setLabelText("Loading GameData.cff...")
            progress.setValue(2)
            QApplication.processEvents()

            cff_start = time.time()
            self.logger.info(f"Loading CFF file: {cff_file}")
            if not self.data_model.load_file(str(cff_file)):
                progress.close()
                QMessageBox.critical(self, "Error", "Failed to load GameData.cff")
                return
            cff_time = time.time() - cff_start
            self.logger.info(f"CFF loaded in {cff_time:.2f}s")

            # Step 3: Initialize Lua data manager
            progress.setLabelText("Loading Lua quest cache...")
            progress.setValue(3)
            QApplication.processEvents()

            # Use absolute cache path to avoid creating duplicate cache directories
            cache_dir = project_root / "src" / "TirganachReloaded" / "data" / "cache"
            lua_start = time.time()
            self.lua_manager = LuaDataManager(cache_dir=cache_dir)

            # Load quest data from CFF (all quests with names!)
            self.load_cff_quest_data()

            # Enhance with Lua data (dialogues, rewards, etc.)
            self.load_lua_quest_data()
            lua_time = time.time() - lua_start
            self.logger.info(f"Lua data loaded in {lua_time:.2f}s")

            # Step 3.5: Load CSV data to fill holes
            progress.setLabelText("Loading CSV quest data...")
            progress.setValue(4)
            QApplication.processEvents()
            
            self.load_csv_quest_data()
            
            # Step 4: Load dialogue data
            progress.setLabelText("Loading dialogue data...")
            progress.setValue(5)
            QApplication.processEvents()
            
            self.load_dialogue_data()

            # Step 5: Populate tree
            progress.setLabelText("Building quest tree...")
            progress.setValue(6)
            QApplication.processEvents()

            tree_start = time.time()
            self.populate_quest_tree()
            tree_time = time.time() - tree_start
            self.logger.info(f"Tree populated in {tree_time:.2f}s")

            # Step 6: Populate quest giver filter
            progress.setLabelText("Finalizing...")
            progress.setValue(7)
            QApplication.processEvents()

            self.populate_quest_giver_filter()

            progress.close()

            quest_count = len(self.quest_data)
            dialogue_count = sum(1 for q in self.quest_data.values() if q.get("dialogues"))
            total_time = time.time() - start_time
            status_msg = f"Loaded {quest_count} quests ({dialogue_count} with dialogues) in {total_time:.2f}s"
            self.statusBar().showMessage(status_msg)
            self.logger.info(
                f"Successfully loaded {quest_count} quests ({dialogue_count} with dialogues) in {total_time:.2f}s"
            )

            # Restore preferences that require loaded data
            self.restore_preferences_after_load()

        except Exception as e:
            progress.close()
            if self.logger:
                self.logger.exception(f"Failed to load quest data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load quest data:\n{e}")
            self.statusBar().showMessage("Failed to load data")

    def load_cff_quest_data(self):
        """Load quest data from CFF file via data model"""
        try:
            # Get all quests from the data model
            quests = self.data_model.get_elements("quests")
            if not quests:
                self.logger.warning("No quests found in CFF file")
                return

            self.logger.info(f"Loading {len(quests)} quests from CFF file")

            # Extract quest information
            for quest in quests:
                quest_id = getattr(quest, "quest_id", None)
                if quest_id is None:
                    continue

                # Get quest name (try localized first)
                name = self.data_model.get_localised_text(quest, "name")
                if not name:
                    name = getattr(quest, "name", f"Quest {quest_id}")

                # Get description
                description = self.data_model.get_localised_text(quest, "description")
                if not description:
                    description = getattr(quest, "description", "")

                # Get parent ID and order
                parent_id = getattr(quest, "parent_quest_id", None)
                order_index = getattr(quest, "order_index", 0)

                # Store quest data
                self.quest_data[quest_id] = {
                    "id": quest_id,
                    "name": name,
                    "description": description,
                    "parent_id": parent_id,
                    "order_index": order_index,
                    "quest_object": quest,  # Store reference for further processing
                }

            self.logger.info(f"Loaded {len(self.quest_data)} quests from CFF")

            # Debug: Check how many have names
            with_names = sum(
                1
                for q in self.quest_data.values()
                if q["name"] and not q["name"].startswith("Quest ")
            )
            self.logger.info(
                f"Quests with proper names: {with_names}/{len(self.quest_data)}"
            )

            # Show first 5 quest names as sample
            sample_names = []
            for quest_id in sorted(list(self.quest_data.keys())[:5]):
                sample_names.append(f"{quest_id}: {self.quest_data[quest_id]['name']}")
            self.logger.info(f"Sample quest names: {', '.join(sample_names)}")

        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to load CFF quest data: {e}")

    def load_lua_quest_data(self):
        """Load Lua quest data from cache"""
        try:
            if self.lua_manager:
                # Force cache load if not loaded
                if not self.lua_manager.cache_loaded:
                    self.lua_manager.preload_cache()

                # Get quests from Lua cache
                quest_ids = self.lua_manager.get_all_quest_ids()

                for quest_id in quest_ids:
                    quest_data_obj = self.lua_manager.get_quest_data(quest_id)
                    if quest_data_obj:
                        if quest_id not in self.quest_data:
                            # New quest from Lua that wasn't in CFF
                            self.quest_data[quest_id] = {
                                "id": quest_id,
                                "name": quest_data_obj.quest_name
                                or f"Quest {quest_id}",
                                "description": quest_data_obj.description or "",
                                "parent_id": None,
                                "order_index": 0,
                            }

                        # IMPORTANT: Don't overwrite name/description from CFF!
                        # Only add Lua-specific data (objectives, rewards, etc.)
                        self.quest_data[quest_id].update(
                            {
                                "platform": quest_data_obj.platform,
                                "npc_id": quest_data_obj.npc_id,
                                "objectives": quest_data_obj.objectives,
                                "requirements": quest_data_obj.requirements,
                                "rewards": quest_data_obj.rewards,
                                "dialogues": quest_data_obj.dialogues,
                            }
                        )

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load Lua quest data: {e}")

    def load_dialogue_data(self):
        """Load dialogue data from extracted files"""
        try:
            dialogue_dir = project_root / "ModdingTools/SpellForceLUASources/QuestKnowledge"
            if not dialogue_dir.exists():
                if self.logger:
                    self.logger.warning(f"Dialogue data directory not found: {dialogue_dir}")
                return
            
            self.dialogue_loader = DialogueDataLoader(dialogue_dir)
            if self.dialogue_loader.load_dialogue_data():
                if self.logger:
                    self.logger.info(
                        f"Loaded dialogue data: {self.dialogue_loader.get_npc_count()} NPCs, "
                        f"{self.dialogue_loader.get_quest_count()} quests, "
                        f"{self.dialogue_loader.get_total_dialogue_count()} total dialogues"
                    )
                
                # Enhance quest data with dialogues
                self.enhance_quests_with_dialogues()
            else:
                if self.logger:
                    self.logger.warning("Failed to load dialogue data")
                    
        except Exception as e:
            if self.logger:
                self.logger.exception(f"Failed to load dialogue data: {e}")
    
    def enhance_quests_with_dialogues(self):
        """Enhance quest data with loaded dialogues"""
        if not self.dialogue_loader:
            return
            
        enhanced_count = 0
        for quest_id, quest_info in self.quest_data.items():
            dialogues = self.dialogue_loader.get_dialogues_for_quest(quest_id)
            if dialogues:
                # Convert to dialogue objects compatible with existing format
                enhanced_dialogues = []
                for dlg in dialogues:
                    # Create a simple dialogue object
                    class SimpleDialogue:
                        def __init__(self, text, speaker, is_player=False):
                            self.text = text
                            self.speaker = speaker
                            self.is_player_choice = is_player
                        
                        @property
                        def dialogue_type(self):
                            return "Story" if len(self.text) > 100 else "Standard"
                    
                    is_player = dlg.speaker.lower() == "player"
                    enhanced_dialogues.append(
                        SimpleDialogue(dlg.text, dlg.speaker, is_player)
                    )
                
                # Add dialogues to quest data
                quest_info["dialogues"] = enhanced_dialogues
                enhanced_count += 1
        
        if self.logger:
            self.logger.info(f"Enhanced {enhanced_count} quests with dialogue data")

        # Enhance quest data with QuestDataService
        if self.quest_service:
            self.logger.info("Enhancing quest data with QuestDataService...")
            enhanced_count = 0
            for quest_id in list(self.quest_data.keys()):
                try:
                    # Get CFF data for this quest
                    cff_data = {
                        "name": self.quest_data[quest_id].get("name", ""),
                        "description": self.quest_data[quest_id].get("description", ""),
                        "parent_quest_id": self.quest_data[quest_id].get(
                            "parent_id", 0
                        ),
                        "order_index": self.quest_data[quest_id].get("order_index", 0),
                    }

                    # Get enhanced data from service
                    enhanced_data = self.quest_service.get_enhanced_quest_data(
                        quest_id, cff_data
                    )

                    quest_enhanced = False

                    # Add enhanced dialogues (if not already present or if we have more)
                    if enhanced_data.dialogues:
                        existing_dialogues = self.quest_data[quest_id].get(
                            "dialogues", []
                        )
                        if not existing_dialogues or len(enhanced_data.dialogues) > len(
                            existing_dialogues
                        ):
                            self.quest_data[quest_id]["dialogues"] = (
                                enhanced_data.dialogues
                            )
                            quest_enhanced = True
                            self.logger.debug(
                                f"Quest {quest_id}: Added {len(enhanced_data.dialogues)} dialogues"
                            )

                    # Add enhanced rewards (always add if available from service)
                    if enhanced_data.rewards and enhanced_data.rewards.xp > 0:
                        self.quest_data[quest_id]["rewards"] = enhanced_data.rewards
                        quest_enhanced = True
                        self.logger.debug(
                            f"Quest {quest_id}: Added rewards (XP: {enhanced_data.rewards.xp})"
                        )

                    if quest_enhanced:
                        enhanced_count += 1

                except Exception as e:
                    # Don't fail on individual quest enhancement
                    self.logger.debug(f"Failed to enhance quest {quest_id}: {e}")
                    pass

            self.logger.info(f"Enhanced {enhanced_count} quests with service data")

            # Log enhancement stats
            enhanced_with_dialogues = sum(
                1 for q in self.quest_data.values() if q.get("dialogues")
            )
            enhanced_with_rewards = sum(
                1 for q in self.quest_data.values() if q.get("rewards")
            )
            self.logger.info(
                f"Quest data enhancement complete: {enhanced_with_dialogues} quests with dialogues, {enhanced_with_rewards} quests with rewards"
            )

    def populate_quest_tree(self):
        """Populate the quest tree"""
        self.quest_tree.clear()

        if not self.quest_data:
            if self.logger:
                self.logger.warning("No quest data to populate tree")
            return

        if self.logger:
            self.logger.info(f"Populating tree with {len(self.quest_data)} quests")

        # Create quest items with format "Name [ID]"
        items_created = 0
        for quest_id, quest_info in sorted(self.quest_data.items()):
            name = quest_info.get("name", f"Quest {quest_id}")
            display_text = f"{name} [{quest_id}]"

            item = QTreeWidgetItem(self.quest_tree, [display_text])
            item.setData(0, Qt.UserRole, quest_id)
            items_created += 1

            # Debug: Log first 5 items
            if items_created <= 5 and self.logger:
                self.logger.debug(f"Created tree item: ID={quest_id}, Name={name}")

        # Create hierarchy (parent-child relationships)
        self.build_quest_hierarchy()

        # Make main quests (top-level items without parents) bold
        for i in range(self.quest_tree.topLevelItemCount()):
            item = self.quest_tree.topLevelItem(i)
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)

        self.quest_tree.expandAll()

    def build_quest_hierarchy(self):
        """Build proper multi-level quest hierarchy"""
        # Create a mapping of quest_id -> tree_item
        quest_items = {}
        
        # First, collect all tree items
        for i in range(self.quest_tree.topLevelItemCount()):
            item = self.quest_tree.topLevelItem(i)
            quest_id = item.data(0, Qt.UserRole)
            if quest_id:
                quest_items[quest_id] = item
        
        # Build parent-child relationships
        parent_to_children = {}
        for quest_id, quest_info in self.quest_data.items():
            parent_id = quest_info.get("parent_id")
            if parent_id and parent_id in self.quest_data:
                if parent_id not in parent_to_children:
                    parent_to_children[parent_id] = []
                parent_to_children[parent_id].append(quest_id)
        
        # Function to recursively build hierarchy
        def build_hierarchy_recursive(parent_id, parent_item=None):
            """Recursively build quest hierarchy"""
            children = parent_to_children.get(parent_id, [])
            
            for child_id in children:
                if child_id in quest_items:
                    child_item = quest_items[child_id]
                    
                    # Remove from top level if it's there
                    if parent_item is None:
                        # This is a root-level quest with children, keep it as parent
                        pass
                    else:
                        # Remove child from top level and add to parent
                        index = self.quest_tree.indexOfTopLevelItem(child_item)
                        if index >= 0:
                            self.quest_tree.takeTopLevelItem(index)
                        parent_item.addChild(child_item)
                    
                    # Recursively build children
                    build_hierarchy_recursive(child_id, child_item)
        
        # Build hierarchy for all parent quests
        for parent_id in parent_to_children:
            if parent_id in quest_items:
                build_hierarchy_recursive(parent_id, quest_items[parent_id])

    def _ensure_item_index(self):
        if not hasattr(self, "_items_by_id"):
            self._items_by_id = {}
            try:
                items = self.data_model.get_elements("items") if self.data_model else []
                for it in items or []:
                    iid = getattr(it, "item_id", None)
                    if iid is not None:
                        self._items_by_id[iid] = it
            except Exception:
                self._items_by_id = {}

    def _resolve_item_name(self, item_id):
        try:
            self._ensure_item_index()
            it = self._items_by_id.get(item_id)
            if it is not None and self.data_model:
                name = self.data_model.get_localised_text(it, "name")
                if name:
                    return name
            if self.data_model:
                name = self.data_model.get_weapon_name(item_id)
                if name:
                    return name
                name = self.data_model.get_armor_name(item_id)
                if name:
                    return name
        except Exception:
            pass
        return f"Item {item_id}"

    def on_quest_selection_changed(self):
        """Handle quest selection"""
        selected_items = self.quest_tree.selectedItems()
        if not selected_items:
            self.export_btn.setEnabled(False)
            self.current_quest_id = None
            return

        item = selected_items[0]
        quest_id = item.data(0, Qt.UserRole)

        if quest_id and quest_id in self.quest_data:
            self.current_quest_id = quest_id
            self.export_btn.setEnabled(True)
            self.show_quest_details(quest_id)
        else:
            self.current_quest_id = None
            self.export_btn.setEnabled(False)

    def show_quest_details(self, quest_id):
        """Show details for selected quest with enhanced formatting"""
        quest_info = self.quest_data[quest_id]

        # Debug: Check what data we have
        if self.logger:
            dialogues = quest_info.get("dialogues", [])
            rewards = quest_info.get("rewards")
            self.logger.debug(
                f"Quest {quest_id}: {len(dialogues)} dialogues, rewards={rewards is not None}"
            )
            if dialogues:
                self.logger.debug(f"  First dialogue type: {type(dialogues[0])}")
            if rewards:
                self.logger.debug(
                    f"  Rewards type: {type(rewards)}, has xp: {hasattr(rewards, 'xp')}"
                )

        # Build HTML content with dark theme styling
        html = "<html><head><meta charset='UTF-8'></head><body style='font-family: Arial; font-size: 12pt; background-color: #1e1e1e; color: #e0e0e0;'>"
        
        # Check if we should hide dialogue metadata only
        hide_dialogue_metadata = (self.metadata_toggle.currentData() == "dialogue_only") if hasattr(self, 'metadata_toggle') else False

        # Quest Header
        html += f"<h2 style='color: #6fb3d2; margin-bottom: 5px;'>{quest_info.get('name', 'Unknown')}</h2>"
        html += (
            f"<p style='color: #a0a0a0; margin-top: 0;'><b>Quest ID:</b> {quest_id}</p>"
        )

        # Description
        if quest_info.get("description"):
            html += "<div style='background-color: #2d2d30; padding: 10px; border-radius: 5px; margin: 10px 0; border: 1px solid #3c3c3c; font-size: 15pt;'>"
            html += f"<p><b>Description:</b><br>{quest_info['description']}</p>"
            html += "</div>"
        
        # German Description (if available)
        if quest_info.get("quest_description_de"):
            html += "<div style='background-color: #2d2d30; padding: 10px; border-radius: 5px; margin: 10px 0; border: 1px solid #3c3c3c; font-size: 15pt;'>"
            html += f"<p><b>German Description:</b><br>{quest_info['quest_description_de']}</p>"
            html += "</div>"

        # Location & Quest Giver Section
        html += "<h3 style='color: #6fb3d2; margin-top: 15px; margin-bottom: 5px;'>Location & Quest Giver</h3>"
        html += "<ul style='margin-top: 5px; font-size: 15pt;'>"

        # Platform/Location
        platform = quest_info.get("platform")
        platform_name_de = quest_info.get("platform_name_de")
        german_only = None
        if platform_name_de:
            german_only = platform_name_de
        elif platform and platform in PLATFORM_NAMES:
            en = PLATFORM_NAMES.get(platform)
            german_only = get_german_platform_name(en)
        if german_only and platform:
            html += f"<li><b>Location:</b> {german_only} [{platform}]</li>"
        elif german_only:
            html += f"<li><b>Location:</b> {german_only}</li>"
        else:
            html += (
                "<li><b>Location:</b> <span style='color: #808080;'>Unknown</span></li>"
            )

        # Quest Giver (NPC)
        npc_id = quest_info.get("npc_id")
        quest_giver_name = quest_info.get("quest_giver_name")
        if quest_giver_name:
            html += f"<li><b>Quest Giver:</b> {quest_giver_name} (NPC ID {npc_id})</li>"
        elif npc_id:
            html += f"<li><b>Quest Giver:</b> NPC ID {npc_id}</li>"
        else:
            html += "<li><b>Quest Giver:</b> <span style='color: #808080;'>Unknown</span></li>"

        # Parent Quest
        parent_id = quest_info.get("parent_id")
        if parent_id:
            parent_name = self.quest_data.get(parent_id, {}).get(
                "name", f"Quest {parent_id}"
            )
            html += f"<li><b>Parent Quest:</b> {parent_name} [{parent_id}]</li>"

        html += "</ul>"

        # Requirements
        requirements = quest_info.get("requirements", [])
        if requirements:
            html += "<h3 style='color: #f48771; margin-top: 15px; margin-bottom: 5px;'>Requirements</h3>"
        # Objectives
        objectives = quest_info.get("objectives")
        if objectives:
            html += "<h3 style='color: #c586c0; margin-top: 15px; margin-bottom: 5px;'>Objectives</h3>"
            html += "<div style='background-color: #2d2d30; padding: 10px; border-radius: 5px; border: 1px solid #3c3c3c;'>"
            if isinstance(objectives, list):
                for obj in objectives:
                    html += f"<div style='margin-bottom: 5px;'>• {obj}</div>"
            else:
                html += f"<div>{objectives}</div>"
            html += "</div>"

        # Requirements
        requirements = quest_info.get("requirements")
        if requirements:
            html += "<h3 style='color: #c586c0; margin-top: 15px; margin-bottom: 5px;'>Requirements</h3>"
            html += "<div style='background-color: #2d2d30; padding: 10px; border-radius: 5px; border: 1px solid #3c3c3c;'>"
            if hasattr(requirements, "__dict__"):
                req_items = []
                if hasattr(requirements, "level") and requirements.level:
                    req_items.append(f"Level: {requirements.level}")
                if hasattr(requirements, "class_type") and requirements.class_type:
                    req_items.append(f"Class: {requirements.class_type}")
                if hasattr(requirements, "skills") and requirements.skills:
                    req_items.append(f"Skills: {requirements.skills}")
                if hasattr(requirements, "items") and requirements.items:
                    req_items.append(f"Items: {requirements.items}")
                
                # Check for quest requirements
                if hasattr(requirements, "quest_requirements") and requirements.quest_requirements:
                    for quest_req in requirements.quest_requirements:
                        if hasattr(quest_req, "quest_id") and hasattr(quest_req, "state"):
                            req_items.append(f"Quest {quest_req.quest_id}: {quest_req.state}")
                
                for item in req_items:
                    html += f"<div style='margin-bottom: 3px;'>• {item}</div>"
            else:
                html += f"<div>{requirements}</div>"
            html += "</div>"

        # Rewards
        rewards = quest_info.get("rewards")
        if rewards:
            html += "<h3 style='color: #c586c0; margin-top: 15px; margin-bottom: 5px;'>Rewards</h3>"
            html += "<div style='background-color: #2d2d30; padding: 10px; border-radius: 5px; border: 1px solid #3c3c3c;'>"
            
            # XP Reward
            if hasattr(rewards, "xp") and rewards.xp:
                html += f"<div style='margin-bottom: 5px;'><span style='color: #d4d4d4;'>Experience:</span> <span style='color: #4ec9b0;'>{rewards.xp}</span></div>"
            
            # Gold Reward
            if hasattr(rewards, "gold") and rewards.gold:
                html += f"<div style='margin-bottom: 5px;'><span style='color: #d4d4d4;'>Gold:</span> <span style='color: #f48771;'>{rewards.gold}</span></div>"
            
            # Item Rewards (if available)
            if hasattr(rewards, "items") and rewards.items:
                html += "<div style='margin-bottom: 5px;'><span style='color: #d4d4d4;'>Items:</span><ul style='margin: 5px 0; padding-left: 20px;'>"
                for item in rewards.items[:10]:  # Limit to first 10 items
                    item_name = getattr(item, "name", "Unknown Item")
                    item_count = getattr(item, "count", 1)
                    html += f"<li style='color: #a0a0a0; margin-bottom: 2px;'>{item_name} x{item_count}</li>"
                if len(rewards.items) > 10:
                    html += f"<li style='color: #7f8c8d; font-style: italic;'>... and {len(rewards.items) - 10} more items</li>"
                html += "</ul></div>"
            
            html += "</div>"

        # Legacy dialogue handling (for backward compatibility)
        dialogues = quest_info.get("dialogues", [])
        if dialogues:
            html += "<h3 style='color: #c586c0; margin-top: 15px; margin-bottom: 5px;'>Dialogues</h3>"
            html += "<div style='background-color: #2d2d30; padding: 10px; border-radius: 5px; border: 1px solid #3c3c3c;'>"
            
            # Group dialogues by speaker for better organization
            npc_dialogues = []
            player_dialogues = []
            
            for dlg in dialogues:
                # Handle both Lua cache format and QuestDataService format
                if hasattr(dlg, "speaker"):
                    # Lua cache format
                    speaker = dlg.speaker
                    text = dlg.text
                else:
                    # QuestDataService format
                    speaker = dlg.get("speaker", "Unknown")
                    text = dlg.get("text", "")
                
                dialogue_info = {
                    "text": text,
                    "speaker": speaker,
                }
                
                if speaker.lower() == "player":
                    player_dialogues.append(dialogue_info)
                else:
                    npc_dialogues.append(dialogue_info)
            
            # Display NPC dialogues first
            if npc_dialogues:
                html += "<h4 style='color: #4ec9b0; margin-bottom: 5px;'>NPC Statements:</h4>"
                for dlg in npc_dialogues:
                    html += f"<div style='margin: 5px 0; padding: 8px; background-color: #252526; border-radius: 4px; border-left: 3px solid #4ec9b0;'>"
                    html += f"<div style='color: #e0e0e0;'>{dlg['text']}</div>"
                    html += "</div>"
            
            # Display player choices
            if player_dialogues:
                html += "<h4 style='color: #6fb3d2; margin-bottom: 5px; margin-top: 10px;'>Player Choices:</h4>"
                for dlg in player_dialogues:
                    html += f"<div style='margin: 5px 0; padding: 8px; background-color: #252526; border-radius: 4px; border-left: 3px solid #6fb3d2;'>"
                    html += f"<div style='color: #b3d9ff;'>• {dlg['text']}</div>"
                    html += "</div>"
            
            # Add dialogue statistics
            html += f"<p style='color: #a0a0a0; font-size: 11pt; font-style: italic; margin-top: 10px;'>"
            html += f"Total: {len(npc_dialogues)} NPC statements, {len(player_dialogues)} player choices"
            html += "</p>"
            
            html += "</div>"
            
            # Add enhanced dialogue tree view if we have dialogue loader
            if self.dialogue_loader and self.current_quest_id:
                html = self.add_enhanced_dialogue_view(html, self.current_quest_id, hide_dialogue_metadata)

        # Empty state
        if (
            not quest_info.get("description")
            and not objectives
            and not requirements
            and not rewards
            and not dialogues
        ):
            html += "<p style='color: #808080; font-style: italic; margin-top: 20px;'>Keine weiteren Informationen verfügbar.</p>"

        html += "</body></html>"

        self.details_text.setHtml(html)
    
    def add_enhanced_dialogue_view(self, html: str, quest_id: int, hide_metadata: bool = False) -> str:
        """Add enhanced dialogue tree view to the HTML"""
        if not self.dialogue_loader:
            return html
        
        dialogues = self.dialogue_loader.get_dialogues_for_quest(quest_id)
        if not dialogues:
            return html
        
        # Build dialogue trees and eliminate duplicates
        dialogue_trees = self.build_dialogue_trees(dialogues)
        
        if not dialogue_trees:
            return html
        
        # Add enhanced dialogue section
        if not hide_metadata:
            html += "<div style='margin-top: 15px; padding: 10px; background-color: #1e1e1e; border-radius: 5px; border: 1px solid #3c3c3c;'>"
            html += "<h4 style='color: #c586c0; margin-bottom: 8px;'>Dialogue Trees</h4>"
        else:
            html += "<div style='margin-top: 10px;'>"
        
        for npc_name, tree in sorted(dialogue_trees.items()):
            html += self.render_dialogue_tree(npc_name, tree, hide_metadata)
        
        html += "</div>"
        return html
    
    def build_dialogue_trees(self, dialogues) -> Dict[str, 'DialogueTree']:
        """Build organized dialogue trees from raw dialogue data"""
        from collections import defaultdict
        
        # Group by NPC and eliminate duplicates
        npc_dialogues = defaultdict(list)
        seen_dialogues = set()  # Track unique dialogues by tag+text
        
        for dlg in dialogues:
            # Create unique key for dialogue
            key = (dlg.tag, dlg.text.strip(), dlg.speaker)
            if key not in seen_dialogues:
                seen_dialogues.add(key)
                npc_dialogues[dlg.npc_name or "Unknown"].append(dlg)
        
        # Build trees for each NPC
        trees = {}
        for npc_name, npc_dialogues in npc_dialogues.items():
            tree = DialogueTree(npc_name)
            
            # Sort dialogues by answer ID and tag to establish flow
            # This ensures chronological order when building connections
            npc_dialogues.sort(key=lambda x: (x.answer_id or 0, x.tag))
            
            # Build dialogue nodes and connections
            for dlg in npc_dialogues:
                node = DialogueNode(
                    tag=dlg.tag,
                    text=dlg.text,
                    speaker=dlg.speaker,
                    answer_id=dlg.answer_id,
                    conditions=dlg.conditions
                )
                tree.add_node(node)
            
            # Build connections between nodes
            tree.build_connections()
            trees[npc_name] = tree
        
        return trees
    
    def render_dialogue_tree(self, npc_name: str, tree: 'DialogueTree', hide_metadata: bool = False) -> str:
        """Render a single dialogue tree as HTML"""
        html = f"<div style='margin-bottom: 20px; border-left: 3px solid #4ec9b0; padding-left: 15px;'>"
        html += f"<h5 style='color: #4ec9b0; margin-bottom: 10px;'>{npc_name}</h5>"
        
        # Render conversation flows
        for flow in tree.get_conversation_flows():
            html += self.render_conversation_flow(flow, hide_metadata)
        
        # Show statistics (only if not hiding metadata)
        if not hide_metadata:
            stats = tree.get_statistics()
            html += f"<div style='margin-top: 10px; padding: 5px; background-color: #2d2d30; border-radius: 3px;'>"
            html += f"<span style='color: #a0a0a0; font-size: 11pt;'>"
            html += f"{stats['total_nodes']} dialogues | {stats['player_choices']} player choices | {stats['branches']} branches"
            html += "</span></div>"
        
        html += "</div>"
        return html
    
    def render_conversation_flow(self, flow: List['DialogueNode'], hide_metadata: bool = False) -> str:
        """Render a single conversation flow as HTML"""
        if not flow:
            return ""
        
        html = "<div style='margin-bottom: 15px; padding: 8px; background-color: #252525; border-radius: 5px;'>"
        
        # Determine if this is a complete conversation or a single node
        if len(flow) == 1:
            flow_type = "Single Dialogue"
        else:
            flow_type = f"Conversation Flow ({len(flow)} steps)"
        
        html += f"<div style='color: #c586c0; font-weight: bold; margin-bottom: 8px; font-size: 11pt;'>{flow_type}</div>"
        
        for i, node in enumerate(flow):
            # Calculate indentation based on position
            indent = min(i * 25, 150)  # Cap indentation at 150px
            
            # Determine styling based on speaker - use existing color scheme
            if node.speaker.lower() == "player":
                speaker_color = "#6fb3d2"
                speaker_icon = "Player"
                text_bg = "#1e3a5f"
                border_style = "dashed"
            else:
                speaker_color = "#4ec9b0"
                speaker_icon = "NPC"
                text_bg = "#1e3a2f"
                border_style = "solid"
            
            html += f"<div style='margin-left: {indent}px; margin-bottom: 10px; position: relative;'>"
            
            # Add connection line if not first
            if i > 0:
                html += f"<div style='position: absolute; left: -25px; top: 15px; width: 20px; height: 2px; background-color: #888; border-radius: 1px;'></div>"
                if i < len(flow) - 1:  # Not the last node
                    html += f"<div style='position: absolute; left: -25px; top: 15px; width: 2px; height: calc(100% + 5px); background-color: #888;'></div>"
            
            # Node content with improved styling
            html += f"<div style='padding: 10px; background-color: {text_bg}; border-radius: 6px; border-left: 4px {border_style} {speaker_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.3);'>"
            
            # Header with speaker and metadata (only if not hiding metadata)
            if not hide_metadata:
                html += f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>"
                html += f"<span style='color: {speaker_color}; font-weight: bold; font-size: 12pt;'>{speaker_icon}: {node.speaker}</span>"
                
                # Metadata on the right
                metadata_parts = []
                if node.answer_id:
                    metadata_parts.append(f"ID: {node.answer_id}")
                if i > 0:
                    metadata_parts.append(f"Step {i+1}")
                
                if metadata_parts:
                    html += f"<span style='color: #f48771; font-size: 10pt;'>{' | '.join(metadata_parts)}</span>"
                
                html += "</div>"
            
            # Dialogue text with better formatting - ensure proper encoding
            display_text = node.text
            if len(display_text) > 200:
                display_text = display_text[:200] + "..."
            
            html += f"<div style='color: #f0f0f0; line-height: 1.4; margin-bottom: 6px;'>{display_text}</div>"
            
            # Footer with conditions and tag (only if not hiding metadata)
            if not hide_metadata:
                if node.conditions:
                    condition_text = ', '.join(node.conditions[:1])  # Show only first condition
                    if len(node.conditions) > 1:
                        condition_text += f" (+{len(node.conditions)-1} more)"
                    html += f"<div style='color: #f48771; font-size: 10pt; margin-bottom: 4px;'>Condition: {condition_text}</div>"
                
                html += f"<div style='color: #7f8c8d; font-size: 9pt; font-style: italic;'>Tag: {node.tag}</div>"
            
            html += "</div></div>"
        
        html += "</div>"
        return html

    def on_metadata_view_changed(self):
        """Handle metadata view mode change"""
        # Refresh the current quest details if a quest is selected
        if self.current_quest_id:
            self.show_quest_details(self.current_quest_id)
    
    def on_search_changed(self, text):
        """Handle search text changes - filter tree items"""
        search_text = text.lower().strip()
        platform_filter = self.platform_filter.currentData()
        giver_filter = self.giver_filter.currentData()
        dialogue_filter = self.dialogue_filter.currentData()

        visible_count = 0

        # Iterate through all top-level items
        for i in range(self.quest_tree.topLevelItemCount()):
            item = self.quest_tree.topLevelItem(i)
            visible = self.filter_tree_item(
                item, search_text, platform_filter, giver_filter, dialogue_filter
            )
            if visible:
                visible_count += 1

        # Update search results label
        if search_text or platform_filter or giver_filter or dialogue_filter:
            self.search_results_label.setText(f"Showing {visible_count} quest(s)")
        else:
            self.search_results_label.setText("")

    def on_filter_changed(self):
        """Handle filter dropdown changes"""
        # Trigger the same filtering logic as search
        self.on_search_changed(self.search_input.text())

    def filter_tree_item(self, item, search_text, platform_filter, giver_filter, dialogue_filter):
        """
        Recursively filter tree items based on search text and filters.
        Returns True if item or any child should be visible.
        """
        quest_id = item.data(0, Qt.UserRole)
        quest_info = self.quest_data.get(quest_id, {})

        # Check if this item matches filters
        matches = True

        # Search text filter (ID, name, description)
        if search_text:
            quest_id_str = str(quest_id).lower()
            name = quest_info.get("name", "").lower()
            description = quest_info.get("description", "").lower()

            matches = (
                search_text in quest_id_str
                or search_text in name
                or search_text in description
            )

        # Platform filter
        if matches and platform_filter:
            quest_platform = quest_info.get("platform", "")
            matches = quest_platform == platform_filter

        # Quest giver filter
        if matches and giver_filter:
            quest_npc = quest_info.get("npc_id")
            matches = quest_npc == giver_filter
        
        # Dialogue filter
        if matches and dialogue_filter is not None:
            has_dialogues = bool(quest_info.get("dialogues"))
            matches = has_dialogues == dialogue_filter

        # Check children recursively
        child_visible = False
        for child_idx in range(item.childCount()):
            child = item.child(child_idx)
            if self.filter_tree_item(child, search_text, platform_filter, giver_filter, dialogue_filter):
                child_visible = True

        # Show item if it matches OR if any child is visible
        should_show = matches or child_visible
        item.setHidden(not should_show)

        # Expand item if it has visible children
        if child_visible and search_text:
            item.setExpanded(True)

        return should_show

    def populate_quest_giver_filter(self):
        """Populate quest giver filter with unique NPC IDs from loaded quests"""
        # Clear existing items (keep "All Quest Givers")
        self.giver_filter.clear()
        self.giver_filter.addItem("All Quest Givers", None)

        # Collect unique NPC IDs
        npc_ids = set()
        for quest_info in self.quest_data.values():
            npc_id = quest_info.get("npc_id")
            if npc_id:
                npc_ids.add(npc_id)

        # Add to combo box sorted
        for npc_id in sorted(npc_ids):
            self.giver_filter.addItem(f"NPC {npc_id}", npc_id)

    def reload_data(self):
        """Reload quest data"""
        self.quest_data.clear()
        self.data_model = None  # Clear data model to force reload
        self.load_data()

    def rebuild_cache(self):
        """Rebuild quest cache from Lua files"""
        try:
            # Look for Lua files
            lua_paths = [
                Path("ModdingTools/SpellForceLUASources"),
                Path("OriginalGameFiles/lua"),
            ]

            lua_source_path = None
            for path in lua_paths:
                if path.exists() and path.is_dir():
                    lua_source_path = path
                    break

            if lua_source_path:
                progress = QProgressDialog(
                    "Rebuilding cache from Lua files...", None, 0, 0, self
                )
                progress.setWindowModality(Qt.WindowModal)
                progress.show()

                QApplication.processEvents()

                self.lua_manager.parse_lua_directory(
                    lua_source_path, force_refresh=True
                )

                progress.close()

                QMessageBox.information(self, "Success", "Cache rebuilt successfully!")
                self.reload_data()
            else:
                QMessageBox.warning(self, "Warning", "No Lua source directory found.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rebuild cache:\n{e}")

    def export_quest(self):
        """Export the currently selected quest"""
        if not self.current_quest_id:
            QMessageBox.warning(self, "Warning", "Please select a quest to export.")
            return

        # Ask user for export format
        from PySide6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QRadioButton

        dialog = QDialog(self)
        dialog.setWindowTitle("Export Quest")
        dialog_layout = QVBoxLayout(dialog)

        # Format selection
        format_label = QLabel("Select export format:")
        dialog_layout.addWidget(format_label)

        json_radio = QRadioButton("JSON")
        json_radio.setChecked(True)
        markdown_radio = QRadioButton("Markdown")

        dialog_layout.addWidget(json_radio)
        dialog_layout.addWidget(markdown_radio)

        # Include sub-quests option
        include_subquests_checkbox = QCheckBox("Include all sub-quests")
        include_subquests_checkbox.setChecked(True)
        dialog_layout.addWidget(include_subquests_checkbox)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)

        if dialog.exec() != QDialog.Accepted:
            return

        # Get export settings
        export_json = json_radio.isChecked()
        include_subquests = include_subquests_checkbox.isChecked()

        # Get file path from user
        if export_json:
            file_filter = "JSON Files (*.json)"
            default_ext = ".json"
        else:
            file_filter = "Markdown Files (*.md)"
            default_ext = ".md"

        quest_name = self.quest_data[self.current_quest_id].get(
            "name", f"Quest_{self.current_quest_id}"
        )
        # Sanitize filename
        safe_name = "".join(
            c for c in quest_name if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        default_filename = f"{safe_name}{default_ext}"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Quest", default_filename, file_filter
        )

        if not file_path:
            return

        try:
            # Collect quest data
            quests_to_export = [self.current_quest_id]

            if include_subquests:
                # Find all sub-quests recursively
                quests_to_export.extend(self.get_all_subquests(self.current_quest_id))

            # Export based on format
            if export_json:
                self.export_to_json(quests_to_export, file_path)
            else:
                self.export_to_markdown(quests_to_export, file_path)

            QMessageBox.information(
                self, "Success", f"Quest(s) exported successfully to:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export quest:\n{e}")

    def get_all_subquests(self, parent_quest_id):
        """Recursively get all sub-quest IDs for a parent quest"""
        subquests = []

        for quest_id, quest_info in self.quest_data.items():
            if quest_info.get("parent_id") == parent_quest_id:
                subquests.append(quest_id)
                # Recursively get sub-quests of this sub-quest
                subquests.extend(self.get_all_subquests(quest_id))

        return subquests

    def export_to_json(self, quest_ids, file_path):
        """Export quests to JSON format"""
        export_data = []

        for quest_id in quest_ids:
            quest_info = self.quest_data[quest_id].copy()

            # Convert complex objects to serializable format
            if "objectives" in quest_info and quest_info["objectives"]:
                quest_info["objectives"] = [
                    {
                        "type": getattr(obj, "type", "unknown"),
                        "text": getattr(obj, "text", ""),
                    }
                    for obj in quest_info["objectives"]
                ]

            if "requirements" in quest_info and quest_info["requirements"]:
                quest_info["requirements"] = [
                    {
                        "type": getattr(req, "type", "unknown"),
                        "text": getattr(req, "text", ""),
                    }
                    for req in quest_info["requirements"]
                ]

            if "rewards" in quest_info and quest_info["rewards"]:
                rewards = quest_info["rewards"]
                quest_info["rewards"] = {
                    "xp": getattr(rewards, "xp", 0),
                    "gold": getattr(rewards, "gold", 0),
                    "silver": getattr(rewards, "silver", 0),
                    "copper": getattr(rewards, "copper", 0),
                    "items": list(getattr(rewards, "items", [])),
                }

            if "dialogues" in quest_info and quest_info["dialogues"]:
                quest_info["dialogues"] = [
                    {
                        "speaker": getattr(dlg, "speaker", "Unknown"),
                        "text": getattr(dlg, "text", ""),
                        "is_player": getattr(dlg, "is_player_choice", False),
                    }
                    for dlg in quest_info["dialogues"]
                ]

            export_data.append(quest_info)

        # Write to JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def export_to_markdown(self, quest_ids, file_path):
        """Export quests to Markdown format"""
        lines = []

        for idx, quest_id in enumerate(quest_ids):
            quest_info = self.quest_data[quest_id]

            # Quest header
            if idx == 0:
                lines.append(f"# {quest_info.get('name', 'Unknown Quest')}")
            else:
                lines.append(f"\n## {quest_info.get('name', 'Unknown Quest')}")

            lines.append(f"\n**Quest ID:** {quest_id}")

            # Parent quest
            parent_id = quest_info.get("parent_id")
            if parent_id:
                parent_name = self.quest_data.get(parent_id, {}).get(
                    "name", f"Quest {parent_id}"
                )
                lines.append(f"**Parent Quest:** {parent_name} (ID: {parent_id})")

            # Location
            platform = quest_info.get("platform")
            if platform:
                location = get_platform_display_name(platform)
                lines.append(f"**Location:** {location}")

            # Quest Giver
            npc_id = quest_info.get("npc_id")
            if npc_id:
                lines.append(f"**Quest Giver:** NPC {npc_id}")

            # Description
            if quest_info.get("description"):
                lines.append(f"\n### Description\n\n{quest_info['description']}")

            # Objectives
            objectives = quest_info.get("objectives", [])
            if objectives:
                lines.append("\n### Objectives\n")
                for obj in objectives:
                    obj_type = getattr(obj, "type", "unknown")
                    obj_text = getattr(obj, "text", "")
                    lines.append(f"- **[{obj_type}]** {obj_text}")

            # Requirements
            requirements = quest_info.get("requirements", [])
            if requirements:
                lines.append("\n### Requirements\n")
                for req in requirements:
                    req_type = getattr(req, "type", "unknown")
                    req_text = getattr(req, "text", "")
                    lines.append(f"- **[{req_type}]** {req_text}")

            # Rewards
            rewards = quest_info.get("rewards")
            if rewards:
                lines.append("\n### Rewards\n")
                if hasattr(rewards, "xp") and rewards.xp > 0:
                    lines.append(f"- **XP:** {rewards.xp}")
                if hasattr(rewards, "gold") and rewards.gold > 0:
                    lines.append(f"- **Gold:** {rewards.gold}")
                if hasattr(rewards, "silver") or hasattr(rewards, "copper"):
                    silver = getattr(rewards, "silver", 0)
                    copper = getattr(rewards, "copper", 0)
                    if silver > 0 or copper > 0:
                        lines.append(f"- **Silver:** {silver}, **Copper:** {copper}")
                if hasattr(rewards, "items") and rewards.items:
                    items_str = ", ".join(map(str, rewards.items))
                    lines.append(f"- **Items:** {items_str}")

            # Dialogues
            dialogues = quest_info.get("dialogues", [])
            if dialogues:
                lines.append("\n### Dialogues\n")
                for dlg in dialogues:
                    speaker = getattr(dlg, "speaker", "Unknown")
                    dlg_text = getattr(dlg, "text", "")
                    is_player = getattr(dlg, "is_player_choice", False)

                    if dlg_text:
                        if speaker == "Player" or is_player:
                            lines.append(f"- **Player:** {dlg_text}")
                        else:
                            lines.append(f"- **NPC:** {dlg_text}")

            lines.append("\n---\n")

        # Write to markdown file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def restore_preferences(self):
        """Restore user preferences from settings"""
        # Restore window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        # Restore window state (maximized, etc.)
        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)

    def restore_preferences_after_load(self):
        """Restore preferences that require data to be loaded first"""
        # Restore splitter state
        splitter_state = self.settings.value("splitterState")
        if splitter_state:
            self.splitter.restoreState(splitter_state)

        # Restore last selected quest
        last_quest_id = self.settings.value("lastQuestId", type=int)
        if last_quest_id and last_quest_id in self.quest_data:
            self.select_quest_by_id(last_quest_id)

        # Restore tree expansion state
        expanded_quests = self.settings.value("expandedQuests", [])
        if expanded_quests:
            self.restore_tree_expansion(expanded_quests)

        # Restore search and filter state
        search_text = self.settings.value("searchText", "")
        if search_text:
            self.search_input.setText(search_text)

        platform_filter = self.settings.value("platformFilter")
        if platform_filter:
            index = self.platform_filter.findData(platform_filter)
            if index >= 0:
                self.platform_filter.setCurrentIndex(index)

        giver_filter = self.settings.value("giverFilter")
        if giver_filter:
            index = self.giver_filter.findData(giver_filter)
            if index >= 0:
                self.giver_filter.setCurrentIndex(index)

    def select_quest_by_id(self, quest_id):
        """Select a quest in the tree by its ID"""
        for i in range(self.quest_tree.topLevelItemCount()):
            item = self.quest_tree.topLevelItem(i)
            if self.find_and_select_item(item, quest_id):
                return True
        return False

    def find_and_select_item(self, item, quest_id):
        """Recursively find and select an item by quest ID"""
        item_quest_id = item.data(0, Qt.UserRole)
        if item_quest_id == quest_id:
            self.quest_tree.setCurrentItem(item)
            self.quest_tree.scrollToItem(item)
            return True

        # Check children
        for i in range(item.childCount()):
            child = item.child(i)
            if self.find_and_select_item(child, quest_id):
                return True

        return False

    def restore_tree_expansion(self, expanded_quest_ids):
        """Restore tree expansion state"""
        for i in range(self.quest_tree.topLevelItemCount()):
            item = self.quest_tree.topLevelItem(i)
            self.restore_item_expansion(item, expanded_quest_ids)

    def restore_item_expansion(self, item, expanded_quest_ids):
        """Recursively restore expansion state for an item"""
        quest_id = item.data(0, Qt.UserRole)
        if quest_id in expanded_quest_ids:
            item.setExpanded(True)

        # Process children
        for i in range(item.childCount()):
            child = item.child(i)
            self.restore_item_expansion(child, expanded_quest_ids)

    def save_tree_expansion_state(self):
        """Save which quests are expanded"""
        expanded = []
        for i in range(self.quest_tree.topLevelItemCount()):
            item = self.quest_tree.topLevelItem(i)
            self.collect_expanded_items(item, expanded)
        return expanded

    def collect_expanded_items(self, item, expanded_list):
        """Recursively collect expanded quest IDs"""
        if item.isExpanded():
            quest_id = item.data(0, Qt.UserRole)
            if quest_id:
                expanded_list.append(quest_id)

        # Process children
        for i in range(item.childCount()):
            child = item.child(i)
            self.collect_expanded_items(child, expanded_list)

    def closeEvent(self, event):
        """Save preferences when closing"""
        # Save window geometry and state
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        # Save splitter state
        self.settings.setValue("splitterState", self.splitter.saveState())

        # Save last selected quest
        if self.current_quest_id:
            self.settings.setValue("lastQuestId", self.current_quest_id)

        # Save tree expansion state
        expanded_quests = self.save_tree_expansion_state()
        self.settings.setValue("expandedQuests", expanded_quests)

        # Save search and filter state
        self.settings.setValue("searchText", self.search_input.text())
        self.settings.setValue("platformFilter", self.platform_filter.currentData())
        self.settings.setValue("giverFilter", self.giver_filter.currentData())

        super().closeEvent(event)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="TirganachReloaded Simple Quest Viewer"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Configure logging if debug mode
    if args.debug:
        configure_logging()

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("TirganachReloaded Simple Quest Viewer")
    app.setOrganizationName("SpellSmut Modding Tools")

    # Apply dark theme stylesheet
    app.setStyleSheet("""
        QWidget {
            background-color: #2b2b2b;
            color: #e0e0e0;
        }
        QMainWindow {
            background-color: #2b2b2b;
        }
        QTreeWidget, QListWidget, QTextEdit {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #3c3c3c;
            alternate-background-color: #252525;
        }
        QTreeWidget::item:selected, QListWidget::item:selected {
            background-color: #094771;
        }
        QTreeWidget::item:hover, QListWidget::item:hover {
            background-color: #2d2d30;
        }
        QGroupBox {
            border: 1px solid #3c3c3c;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QLabel {
            background-color: transparent;
        }
        QPushButton {
            background-color: #3c3c3c;
            color: #e0e0e0;
            border: 1px solid #555555;
            padding: 5px 10px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
        QPushButton:pressed {
            background-color: #2a2a2a;
        }
        QLineEdit, QComboBox {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #3c3c3c;
            padding: 5px;
            border-radius: 3px;
        }
        QComboBox::drop-down {
            border: none;
            background-color: #3c3c3c;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid #e0e0e0;
        }
        QScrollBar:vertical {
            background-color: #2b2b2b;
            width: 12px;
        }
        QScrollBar::handle:vertical {
            background-color: #3c3c3c;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #4a4a4a;
        }
        QHeaderView::section {
            background-color: #3c3c3c;
            color: #e0e0e0;
            padding: 5px;
            border: 1px solid #555555;
        }
        QSplitter::handle {
            background-color: #3c3c3c;
        }
        QStatusBar {
            background-color: #2b2b2b;
            color: #e0e0e0;
        }
    """)

    # Create and show main window
    window = SimpleQuestViewer()
    window.show()

    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
