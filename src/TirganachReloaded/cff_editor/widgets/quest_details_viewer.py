"""
Quest Details Viewer Widget
Comprehensive view of all quest information including giver, requirements, objectives, and dialogues
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QScrollArea,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..services import QuestDataService


class QuestDetailsViewer(QWidget):
    """Comprehensive quest details viewer"""

    # Platform ID to map name mapping (updated with Amra & Lea quest data)
    PLATFORM_NAMES = {
        "P1": "Liannon",
        "P2": "Eloni",
        "P3": "Leafshade",
        "P4": "Wildland Pass",
        "P5": "Shiel",
        "P6": "Wildland Pass / Greyfell area",  # Updated
        "P7": "Ice Gate",  # Updated
        "P8": "Underhall",
        "P10": "Iron Fields",
        "P11": "The Shiel",
        "P12": "峡谷",
        "P15": "Desert / Burning Sands",  # Updated
        "P16": "Whisper",
        "P17": "Tirganach",
        "P19": "Dun Mora",
        "P23": "The Gorge",
        "P25": "Godmark / Mountains",  # Updated
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

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.current_quest = None
        self.enhanced_quest_data = None  # Store enhanced quest data
        
        # Initialize quest data service
        try:
            # Try to find project root (go up from cff_editor/widgets)
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent.parent
            self.quest_service = QuestDataService(project_root)
        except Exception as e:
            print(f"[WARNING] Could not initialize QuestDataService: {e}")
            self.quest_service = None

        self.setup_ui()
        self.connect_signals()

    @staticmethod
    def get_platform_name(platform_id: str) -> str:
        """Convert platform ID to human-readable map name"""
        if not platform_id:
            return "Unknown"
        return QuestDetailsViewer.PLATFORM_NAMES.get(platform_id, platform_id)

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        self.title_label = QLabel("Quest Details")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # Main content in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(5, 5, 5, 5)

        # Information Notice Section
        self.info_notice_group = self.create_info_notice_section()
        content_layout.addWidget(self.info_notice_group)

        # Basic Info Section
        self.basic_info_group = self.create_basic_info_section()
        content_layout.addWidget(self.basic_info_group)

        # Map Locations Section (NEW)
        self.map_locations_group = self.create_map_locations_section()
        content_layout.addWidget(self.map_locations_group)

        # Quest Giver Section
        self.quest_giver_group = self.create_quest_giver_section()
        content_layout.addWidget(self.quest_giver_group)

        # Requirements to Accept Section
        self.accept_requirements_group = self.create_accept_requirements_section()
        content_layout.addWidget(self.accept_requirements_group)

        # Objectives/Completion Requirements Section
        self.objectives_group = self.create_objectives_section()
        content_layout.addWidget(self.objectives_group)

        # Rewards Section
        self.rewards_group = self.create_rewards_section()
        content_layout.addWidget(self.rewards_group)

        # Dialogues Section
        self.dialogues_group = self.create_dialogues_section()
        content_layout.addWidget(self.dialogues_group)

        # Quest Relationships Section
        self.relationships_group = self.create_relationships_section()
        content_layout.addWidget(self.relationships_group)

        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def create_info_notice_section(self):
        """Create informational notice section explaining CFF vs Lua"""
        group = QGroupBox("📋 Important Information")
        group.setStyleSheet(
            "QGroupBox { font-weight: bold; color: #2196F3; border: 2px solid #2196F3; }"
        )
        layout = QVBoxLayout(group)

        # Main notice
        notice_label = QLabel("<b>What's in the CFF File vs Lua Scripts:</b>")
        notice_label.setStyleSheet("color: #2196F3; font-size: 12px;")
        layout.addWidget(notice_label)

        # CFF data
        cff_data = QLabel(
            "<b style='color: green;'>✓ Available in CFF:</b><br>"
            "• Quest hierarchy (parent-child relationships)<br>"
            "• Quest names and descriptions (localized text)<br>"
            "• Quest IDs and text references<br>"
            "• Basic quest structure<br>"
            "• Dialogue text strings (not branching logic)"
        )
        cff_data.setWordWrap(True)
        cff_data.setStyleSheet("padding: 5px;")
        layout.addWidget(cff_data)

        # Lua data
        lua_data = QLabel(
            "<b style='color: orange;'>⚠ Defined in Lua Scripts (not in CFF):</b><br>"
            "• Quest objectives (Kill X enemies, Collect Y items)<br>"
            "• Quest requirements (Level, previous quests)<br>"
            "• Quest rewards (XP, Gold, Items)<br>"
            "• Quest giver NPC assignments<br>"
            "• Dialogue branching logic and player choices<br>"
            "• Quest state management and triggers"
        )
        lua_data.setWordWrap(True)
        lua_data.setStyleSheet("padding: 5px;")
        layout.addWidget(lua_data)

        # Summary
        summary = QLabel(
            "<i>💡 The sections below show CFF data. For complete quest information "
            "including objectives and rewards, you'll need to examine the Lua quest scripts.</i>"
        )
        summary.setWordWrap(True)
        summary.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        layout.addWidget(summary)

        return group

    def create_basic_info_section(self):
        """Create basic quest information section"""
        group = QGroupBox("Basic Quest Information")
        layout = QVBoxLayout(group)

        # Quest ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Quest ID:"))
        self.quest_id_label = QLabel("-")
        self.quest_id_label.setStyleSheet("font-weight: bold;")
        id_layout.addWidget(self.quest_id_label)
        id_layout.addStretch()
        layout.addLayout(id_layout)

        # Name ID
        name_id_layout = QHBoxLayout()
        name_id_layout.addWidget(QLabel("Name ID:"))
        self.name_id_label = QLabel("-")
        name_id_layout.addWidget(self.name_id_label)
        name_id_layout.addStretch()
        layout.addLayout(name_id_layout)

        # Description ID
        desc_id_layout = QHBoxLayout()
        desc_id_layout.addWidget(QLabel("Description ID:"))
        self.desc_id_label = QLabel("-")
        desc_id_layout.addWidget(self.desc_id_label)
        desc_id_layout.addStretch()
        layout.addLayout(desc_id_layout)

        # Quest Name
        layout.addWidget(QLabel("Quest Name:"))
        self.quest_name_text = QTextEdit()
        self.quest_name_text.setMaximumHeight(50)
        self.quest_name_text.setReadOnly(True)
        layout.addWidget(self.quest_name_text)

        # Quest Description
        layout.addWidget(QLabel("Quest Description:"))
        self.quest_desc_text = QTextEdit()
        self.quest_desc_text.setMaximumHeight(100)
        self.quest_desc_text.setReadOnly(True)
        layout.addWidget(self.quest_desc_text)

        return group

    def create_map_locations_section(self):
        """Create map locations section"""
        group = QGroupBox("Map Locations")
        layout = QVBoxLayout(group)
        
        # Map locations list
        self.map_locations_list = QListWidget()
        self.map_locations_list.setMaximumHeight(100)
        layout.addWidget(self.map_locations_list)
        
        return group

    def create_quest_giver_section(self):
        """Create quest giver information section"""
        group = QGroupBox("Quest Giver (⚠ Usually in Lua)")
        layout = QVBoxLayout(group)

        # Add note
        note = QLabel(
            "<i>Note: Quest giver data is typically defined in Lua scripts, not in the CFF.</i>"
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(note)

        # NPC Name
        npc_layout = QHBoxLayout()
        npc_layout.addWidget(QLabel("NPC:"))
        self.quest_giver_label = QLabel("Unknown")
        self.quest_giver_label.setStyleSheet("font-weight: bold;")
        npc_layout.addWidget(self.quest_giver_label)
        npc_layout.addStretch()
        layout.addLayout(npc_layout)

        # NPC ID
        npc_id_layout = QHBoxLayout()
        npc_id_layout.addWidget(QLabel("NPC ID:"))
        self.quest_giver_id_label = QLabel("-")
        npc_id_layout.addWidget(self.quest_giver_id_label)
        npc_id_layout.addStretch()
        layout.addLayout(npc_id_layout)

        # Location/Map
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Location:"))
        self.quest_location_label = QLabel("Unknown")
        location_layout.addWidget(self.quest_location_label)
        location_layout.addStretch()
        layout.addLayout(location_layout)

        return group

    def create_accept_requirements_section(self):
        """Create requirements to accept quest section"""
        group = QGroupBox("Requirements to Accept Quest (⚠ Usually in Lua)")
        layout = QVBoxLayout(group)

        # Add note
        note = QLabel(
            "<i>Note: Accept requirements are typically defined in Lua scripts.</i>"
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(note)

        # Level requirement
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Minimum Level:"))
        self.min_level_label = QLabel("-")
        level_layout.addWidget(self.min_level_label)
        level_layout.addStretch()
        layout.addLayout(level_layout)

        # Previous quest requirement
        prev_quest_layout = QHBoxLayout()
        prev_quest_layout.addWidget(QLabel("Required Quest:"))
        self.required_quest_label = QLabel("None")
        prev_quest_layout.addWidget(self.required_quest_label)
        prev_quest_layout.addStretch()
        layout.addLayout(prev_quest_layout)

        # Other requirements list
        layout.addWidget(QLabel("Other Requirements:"))
        self.accept_requirements_list = QListWidget()
        self.accept_requirements_list.setMaximumHeight(100)
        layout.addWidget(self.accept_requirements_list)

        return group

    def create_objectives_section(self):
        """Create quest objectives/completion requirements section"""
        group = QGroupBox("Quest Objectives (⚠ Defined in Lua Scripts)")
        layout = QVBoxLayout(group)

        # Add note
        note = QLabel(
            "<i>Note: Quest objectives are defined in Lua scripts, not in the CFF file.</i>"
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(note)

        # Objectives tree
        self.objectives_tree = QTreeWidget()
        self.objectives_tree.setHeaderLabels(["Objective", "Type", "Target", "Count"])
        self.objectives_tree.setAlternatingRowColors(True)
        self.objectives_tree.setMaximumHeight(200)
        layout.addWidget(self.objectives_tree)

        return group

    def create_rewards_section(self):
        """Create quest rewards section"""
        group = QGroupBox("Quest Rewards")
        layout = QVBoxLayout(group)

        # XP reward
        xp_layout = QHBoxLayout()
        xp_layout.addWidget(QLabel("Experience:"))
        self.xp_reward_label = QLabel("0 XP")
        self.xp_reward_label.setStyleSheet("font-weight: bold;")
        xp_layout.addWidget(self.xp_reward_label)
        xp_layout.addStretch()
        layout.addLayout(xp_layout)

        # Reward flags
        layout.addWidget(QLabel("Reward Flags:"))
        self.reward_flags_list = QListWidget()
        self.reward_flags_list.setMaximumHeight(80)
        layout.addWidget(self.reward_flags_list)

        # Money rewards
        money_layout = QHBoxLayout()
        money_layout.addWidget(QLabel("Money:"))
        self.money_reward_label = QLabel("0 Gold, 0 Silver, 0 Copper")
        money_layout.addWidget(self.money_reward_label)
        money_layout.addStretch()
        layout.addLayout(money_layout)

        # Item rewards
        layout.addWidget(QLabel("Item Rewards:"))
        self.item_rewards_list = QListWidget()
        self.item_rewards_list.setMaximumHeight(80)
        layout.addWidget(self.item_rewards_list)
        
        # Source info
        self.reward_source_label = QLabel("")
        self.reward_source_label.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        layout.addWidget(self.reward_source_label)

        return group

    def create_dialogues_section(self):
        """Create quest dialogues section"""
        group = QGroupBox("Quest Dialogues")
        layout = QVBoxLayout(group)

        # Dialogue tree (enhanced with translation column)
        self.dialogues_tree = QTreeWidget()
        self.dialogues_tree.setHeaderLabels(["Type", "Text (German)", "Translation (English)", "Source"])
        self.dialogues_tree.setAlternatingRowColors(True)
        self.dialogues_tree.setColumnWidth(0, 80)
        self.dialogues_tree.setColumnWidth(1, 300)
        self.dialogues_tree.setColumnWidth(2, 300)
        self.dialogues_tree.setColumnWidth(3, 200)
        layout.addWidget(self.dialogues_tree)

        return group

    def create_relationships_section(self):
        """Create quest relationships section"""
        group = QGroupBox("Quest Relationships (✓ In CFF)")
        layout = QVBoxLayout(group)

        # Add note
        note = QLabel("<i>Note: Quest hierarchy is stored in the CFF file.</i>")
        note.setWordWrap(True)
        note.setStyleSheet("color: green; font-size: 10px;")
        layout.addWidget(note)

        # Parent quest
        parent_layout = QHBoxLayout()
        parent_layout.addWidget(QLabel("Parent Quest:"))
        self.parent_quest_label = QLabel("None (Main Quest)")
        parent_layout.addWidget(self.parent_quest_label)
        parent_layout.addStretch()
        layout.addLayout(parent_layout)

        # Sub-quests
        layout.addWidget(QLabel("Sub-quests:"))
        self.subquests_list = QListWidget()
        self.subquests_list.setMaximumHeight(100)
        layout.addWidget(self.subquests_list)

        return group

    def connect_signals(self):
        """Connect signals"""
        # Connect to data model element selection
        self.data_model.element_selected.connect(self.on_element_selected)
        self.data_model.language_changed.connect(self.on_language_changed)

    def on_element_selected(self, category, index):
        """Handle element selection"""
        if category == "quests":
            elements = self.data_model.get_elements("quests")
            if 0 <= index < len(elements):
                self.current_quest = elements[index]
                self.update_quest_details()
        else:
            self.current_quest = None
            self.clear_details()

    def on_language_changed(self, language):
        """Handle language change"""
        if self.current_quest:
            self.update_quest_details()

    def update_quest_details(self):
        """Update all quest detail sections"""
        if not self.current_quest:
            self.clear_details()
            return

        # Debug: Show which quest we're updating
        quest_id = getattr(self.current_quest, "quest_id", None)
        print(f"[DEBUG] Updating quest details for quest ID: {quest_id}")
        print(f"[DEBUG] Has Lua data available: {self.data_model.has_lua_data()}")

        # Load enhanced quest data if service is available
        if self.quest_service and quest_id:
            try:
                # Convert CFF quest to dict for service
                cff_data = {
                    'name': getattr(self.current_quest, 'name', ''),
                    'description': getattr(self.current_quest, 'description', ''),
                    'parent_quest_id': getattr(self.current_quest, 'parent_quest_id', 0),
                    'order_index': getattr(self.current_quest, 'order_index', 0),
                    'name_id': getattr(self.current_quest, 'name_id', 0),
                    'description_id': getattr(self.current_quest, 'description_id', 0),
                }
                self.enhanced_quest_data = self.quest_service.get_enhanced_quest_data(quest_id, cff_data)
                print(f"[DEBUG] Loaded enhanced data: {len(self.enhanced_quest_data.map_locations)} maps, "
                      f"{len(self.enhanced_quest_data.dialogues)} dialogues")
            except Exception as e:
                print(f"[WARNING] Could not load enhanced quest data: {e}")
                self.enhanced_quest_data = None

        self.update_basic_info()
        self.update_map_locations()  # NEW
        self.update_quest_giver()
        self.update_accept_requirements()
        self.update_objectives()
        self.update_rewards()
        self.update_dialogues()
        self.update_relationships()

    def update_basic_info(self):
        """Update basic quest information"""
        quest = self.current_quest

        # Quest ID
        quest_id = getattr(quest, "quest_id", "Unknown")
        self.quest_id_label.setText(str(quest_id))

        # Name ID
        name_id = getattr(quest, "name_id", None)
        self.name_id_label.setText(str(name_id) if name_id else "None")

        # Description ID
        desc_id = getattr(quest, "description_id", None)
        self.desc_id_label.setText(str(desc_id) if desc_id else "None")

        # Quest Name (localized)
        quest_name = self.data_model.get_localised_text(quest, "name")
        if not quest_name:
            quest_name = getattr(quest, "name", f"Quest {quest_id}")
        self.quest_name_text.setPlainText(str(quest_name))

        # Quest Description (localized)
        quest_desc = self.data_model.get_advanced_description(quest)
        if not quest_desc:
            quest_desc = "No description available"
        self.quest_desc_text.setPlainText(str(quest_desc))

    def update_map_locations(self):
        """Update map locations section"""
        self.map_locations_list.clear()
        
        # Check if we have enhanced data with map locations
        if self.enhanced_quest_data and self.enhanced_quest_data.map_locations:
            # Add each map location as a list item
            for map_loc in self.enhanced_quest_data.map_locations:
                self.map_locations_list.addItem(f"{map_loc.code}: {map_loc.name}")
        else:
            # Show placeholder if no map data
            self.map_locations_list.addItem("No map location data available")

    def update_quest_giver(self):
        """Update quest giver information"""
        quest = self.current_quest

        # Try to get Lua quest data first
        quest_id = getattr(quest, "quest_id", None)
        lua_data = None
        if quest_id and self.data_model.has_lua_data():
            lua_data = self.data_model.get_lua_quest_data(quest_id)
            print(
                f"[DEBUG] Quest Giver - Lua data for quest {quest_id}: {lua_data is not None}"
            )
            if lua_data:
                print(
                    f"[DEBUG]   NPC ID: {lua_data.npc_id}, Platform: {lua_data.platform}"
                )

        # Try to get quest giver NPC ID
        giver_id = None
        if lua_data and lua_data.npc_id:
            giver_id = lua_data.npc_id
        else:
            giver_id = getattr(quest, "quest_giver_id", None)
            if not giver_id:
                giver_id = getattr(quest, "npc_id", None)

        if giver_id:
            self.quest_giver_id_label.setText(str(giver_id))
            # Try to get NPC name from localisation
            # TODO: Implement NPC name lookup
            self.quest_giver_label.setText(f"NPC {giver_id}")
        else:
            self.quest_giver_id_label.setText("-")
            self.quest_giver_label.setText("Unknown (check Lua scripts)")

        # Location/Map
        location = None
        if lua_data and lua_data.platform:
            location = lua_data.platform
        else:
            location = getattr(quest, "map", None)
            if not location:
                location = getattr(quest, "platform", None)
        if location:
            map_name = self.get_platform_name(str(location))
            self.quest_location_label.setText(f"{map_name} ({location})")
        else:
            self.quest_location_label.setText("Unknown")

    def update_accept_requirements(self):
        """Update requirements to accept quest"""
        quest = self.current_quest
        self.accept_requirements_list.clear()

        # Try to get Lua quest data first
        quest_id = getattr(quest, "quest_id", None)
        lua_data = None
        if quest_id and self.data_model.has_lua_data():
            lua_data = self.data_model.get_lua_quest_data(quest_id)
            print(
                f"[DEBUG] Requirements - Lua data for quest {quest_id}: {lua_data is not None}"
            )
            if lua_data:
                print(f"[DEBUG]   Requirements count: {len(lua_data.requirements)}")

        # Minimum level
        min_level = getattr(quest, "min_level", None)
        if min_level:
            self.min_level_label.setText(str(min_level))
        else:
            self.min_level_label.setText("-")

        # Required previous quest
        required_quest = getattr(quest, "required_quest_id", None)
        if required_quest:
            self.required_quest_label.setText(f"Quest {required_quest}")
        else:
            self.required_quest_label.setText("None")

        # Check Lua data for requirements
        if lua_data and lua_data.requirements:
            for req in lua_data.requirements:
                req_text = f"[Lua] {req.description}"
                if req.requirement_type != "Unknown":
                    req_text += f" (Type: {req.requirement_type})"
                if req.value:
                    req_text += f" - Value: {req.value}"
                self.accept_requirements_list.addItem(req_text)
        else:
            # Fall back to CFF data
            requirements = getattr(quest, "requirements", None)
            if requirements:
                if isinstance(requirements, list):
                    for req in requirements:
                        if isinstance(req, dict):
                            condition = req.get("condition", str(req))
                            self.accept_requirements_list.addItem(condition)
                        else:
                            self.accept_requirements_list.addItem(str(req))
                else:
                    self.accept_requirements_list.addItem(str(requirements))

        if self.accept_requirements_list.count() == 0:
            self.accept_requirements_list.addItem(
                "No special requirements (check Lua scripts)"
            )

    def update_objectives(self):
        """Update quest objectives/completion requirements"""
        quest = self.current_quest
        self.objectives_tree.clear()

        # Try to get Lua quest data first
        quest_id = getattr(quest, "quest_id", None)
        lua_data = None
        if quest_id and self.data_model.has_lua_data():
            lua_data = self.data_model.get_lua_quest_data(quest_id)
            print(
                f"[DEBUG] Objectives - Lua data for quest {quest_id}: {lua_data is not None}"
            )
            if lua_data:
                print(f"[DEBUG]   Objectives count: {len(lua_data.objectives)}")

        # Check Lua data for objectives
        if lua_data and lua_data.objectives:
            for obj in lua_data.objectives:
                description = f"[Lua] {obj.description}"
                obj_type = obj.objective_type
                target = obj.target if obj.target else "-"
                count = str(obj.count) if obj.count > 1 else "-"
                item = QTreeWidgetItem([description, obj_type, target, count])
                self.objectives_tree.addTopLevelItem(item)
        else:
            # Fall back to CFF data
            objectives = getattr(quest, "objectives", None)
            if objectives:
                if isinstance(objectives, list):
                    for i, obj in enumerate(objectives):
                        if isinstance(obj, dict):
                            obj_type = obj.get("type", "Unknown")
                            target = obj.get("target", "-")
                            count = obj.get("count", "-")
                            description = obj.get("description", f"Objective {i + 1}")
                            item = QTreeWidgetItem(
                                [description, obj_type, str(target), str(count)]
                            )
                            self.objectives_tree.addTopLevelItem(item)
                        else:
                            item = QTreeWidgetItem([str(obj), "-", "-", "-"])
                            self.objectives_tree.addTopLevelItem(item)
                else:
                    item = QTreeWidgetItem([str(objectives), "-", "-", "-"])
                    self.objectives_tree.addTopLevelItem(item)

        if self.objectives_tree.topLevelItemCount() == 0:
            item = QTreeWidgetItem(
                ["No objectives defined (check Lua scripts)", "-", "-", "-"]
            )
            self.objectives_tree.addTopLevelItem(item)

    def update_rewards(self):
        """Update quest rewards"""
        quest = self.current_quest
        quest_id = getattr(quest, "quest_id", None)

        # Check enhanced quest data first
        if self.enhanced_quest_data and self.enhanced_quest_data.rewards:
            rewards = self.enhanced_quest_data.rewards
            
            # XP reward
            if rewards.xp > 0:
                self.xp_reward_label.setText(f"{rewards.xp} XP")
            else:
                self.xp_reward_label.setText("0 XP")
            
            # Reward flags
            self.reward_flags_list.clear()
            if rewards.reward_flags:
                for flag in rewards.reward_flags:
                    self.reward_flags_list.addItem(flag)
            else:
                self.reward_flags_list.addItem("No reward flags")
            
            # Money rewards
            if rewards.gold > 0:
                self.money_reward_label.setText(
                    f"{rewards.gold} Gold, {rewards.silver} Silver, {rewards.copper} Copper"
                )
            else:
                self.money_reward_label.setText("0 Gold, 0 Silver, 0 Copper")
            
            # Item rewards
            self.item_rewards_list.clear()
            if rewards.items:
                for item in rewards.items:
                    self.item_rewards_list.addItem(f"Item: {item}")
            else:
                self.item_rewards_list.addItem("No item rewards")
            
            # Source info
            self.reward_source_label.setText(f"Source: {rewards.source}")
        else:
            # Try Lua data as fallback
            lua_data = None
            if quest_id and self.data_model.has_lua_data():
                lua_data = self.data_model.get_lua_quest_data(quest_id)
            
            # XP reward
            if lua_data and lua_data.rewards and lua_data.rewards.xp > 0:
                self.xp_reward_label.setText(f"{lua_data.rewards.xp} XP")
            else:
                xp = getattr(quest, "xp_reward", None) or getattr(quest, "experience", 0)
                self.xp_reward_label.setText(f"{xp} XP" if xp else "0 XP")
            
            # Reward flags
            self.reward_flags_list.clear()
            self.reward_flags_list.addItem("No reward data available")
            
            # Money rewards
            if lua_data and lua_data.rewards:
                gold = lua_data.rewards.gold
                silver = lua_data.rewards.silver
                copper = lua_data.rewards.copper
                self.money_reward_label.setText(f"{gold} Gold, {silver} Silver, {copper} Copper")
            else:
                self.money_reward_label.setText("0 Gold, 0 Silver, 0 Copper")
            
            # Item rewards
            self.item_rewards_list.clear()
            if lua_data and lua_data.rewards and lua_data.rewards.items:
                for item_id in lua_data.rewards.items:
                    self.item_rewards_list.addItem(f"Item ID: {item_id}")
            else:
                self.item_rewards_list.addItem("No item rewards")
            
            # Source info
            self.reward_source_label.setText("Source: Lua scripts or CFF")

    def update_dialogues(self):
        """Update quest dialogues"""
        quest = self.current_quest
        self.dialogues_tree.clear()

        quest_id = getattr(quest, "quest_id", None)
        if not quest_id:
            return

        # Check enhanced quest data first
        if self.enhanced_quest_data and self.enhanced_quest_data.dialogues:
            for dialogue in self.enhanced_quest_data.dialogues:
                # Truncate text for display
                text_de = dialogue.text[:80] + "..." if len(dialogue.text) > 80 else dialogue.text
                text_en = ""
                if dialogue.translation:
                    text_en = dialogue.translation[:80] + "..." if len(dialogue.translation) > 80 else dialogue.translation
                
                # Extract filename from source
                source = dialogue.source_file
                if "/" in source:
                    source = source.split("/")[-1]  # Get just filename
                
                item = QTreeWidgetItem([
                    dialogue.dialogue_type,
                    text_de,
                    text_en or "-",
                    source
                ])
                
                # Highlight story dialogues
                if dialogue.dialogue_type == "Story":
                    font = item.font(0)
                    font.setBold(True)
                    item.setFont(0, font)
                
                self.dialogues_tree.addTopLevelItem(item)
        else:
            # Fall back to original method
            dialogues = self.find_quest_dialogues(quest_id)
            for dialogue_name, dialogue_text, speaker_type in dialogues:
                display_text = dialogue_text[:80] + "..." if len(dialogue_text) > 80 else dialogue_text
                item = QTreeWidgetItem([speaker_type, display_text, "-", "CFF"])
                self.dialogues_tree.addTopLevelItem(item)

        if self.dialogues_tree.topLevelItemCount() == 0:
            item = QTreeWidgetItem(
                ["No dialogues", "No dialogues found for this quest", "-", "-"]
            )
            self.dialogues_tree.addTopLevelItem(item)

    def find_quest_dialogues(self, quest_id):
        """Find all dialogues related to a quest"""
        dialogues = []

        # Get localisation entries
        localisation_table = self.data_model.get_elements("localisation")
        if not localisation_table:
            return dialogues

        current_language = self.data_model.get_current_language()

        # Search for dialogues that mention the quest ID or follow naming patterns
        for entry in localisation_table:
            if getattr(entry, "is_dialogue", False):
                language = getattr(entry, "language", None)
                if language == current_language:
                    dialogue_name = getattr(entry, "dialogue_name", "")
                    text = getattr(entry, "text", "")

                    # Check if dialogue is related to this quest
                    # This is a heuristic - actual relationship might be defined elsewhere
                    if dialogue_name and text:
                        # Assume quest-related if dialogue name contains quest ID
                        if (
                            str(quest_id) in dialogue_name
                            or f"q{quest_id}" in dialogue_name.lower()
                        ):
                            speaker = getattr(entry, "speaker", "NPC")
                            dialogues.append((dialogue_name, text, speaker))

        return dialogues

    def update_relationships(self):
        """Update quest relationships"""
        quest = self.current_quest
        self.subquests_list.clear()

        quest_id = getattr(quest, "quest_id", None)
        if not quest_id:
            return

        # Parent quest
        parent_id = getattr(quest, "parent_quest_id", None)
        if parent_id and parent_id != 0:
            # Find parent quest name
            quests = self.data_model.get_elements("quests")
            parent_name = f"Quest {parent_id}"
            for q in quests:
                if getattr(q, "quest_id", None) == parent_id:
                    parent_name = self.data_model.get_localised_text(q, "name")
                    if not parent_name:
                        parent_name = getattr(q, "name", f"Quest {parent_id}")
                    break
            self.parent_quest_label.setText(f"{parent_name} (ID: {parent_id})")
        else:
            self.parent_quest_label.setText("None (Main Quest)")

        # Sub-quests
        quests = self.data_model.get_elements("quests")
        for q in quests:
            q_parent_id = getattr(q, "parent_quest_id", None)
            if q_parent_id == quest_id:
                sub_id = getattr(q, "quest_id", None)
                sub_name = self.data_model.get_localised_text(q, "name")
                if not sub_name:
                    sub_name = getattr(q, "name", f"Quest {sub_id}")
                self.subquests_list.addItem(f"{sub_name} (ID: {sub_id})")

        if self.subquests_list.count() == 0:
            self.subquests_list.addItem("No sub-quests")

    def clear_details(self):
        """Clear all quest details"""
        self.quest_id_label.setText("-")
        self.name_id_label.setText("-")
        self.desc_id_label.setText("-")
        self.quest_name_text.clear()
        self.quest_desc_text.clear()
        self.quest_giver_label.setText("Unknown")
        self.quest_giver_id_label.setText("-")
        self.quest_location_label.setText("Unknown")
        self.min_level_label.setText("-")
        self.required_quest_label.setText("None")
        self.accept_requirements_list.clear()
        self.objectives_tree.clear()
        self.xp_reward_label.setText("0 XP")
        self.money_reward_label.setText("0 Gold, 0 Silver, 0 Copper")
        self.item_rewards_list.clear()
        self.dialogues_tree.clear()
        self.parent_quest_label.setText("None")
        self.subquests_list.clear()

    def refresh(self):
        """Refresh the quest details"""
        if self.current_quest:
            self.update_quest_details()
