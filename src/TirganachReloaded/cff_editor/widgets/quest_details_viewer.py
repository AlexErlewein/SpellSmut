"""
Quest Details Viewer Widget
Comprehensive view of all quest information including giver, requirements, objectives, and dialogues
"""

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


class QuestDetailsViewer(QWidget):
    """Comprehensive quest details viewer"""

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.current_quest = None

        self.setup_ui()
        self.connect_signals()

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
        group = QGroupBox("Quest Rewards (⚠ Usually in Lua)")
        layout = QVBoxLayout(group)

        # Add note
        note = QLabel(
            "<i>Note: Quest rewards are typically defined in Lua scripts.</i>"
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(note)

        # XP reward
        xp_layout = QHBoxLayout()
        xp_layout.addWidget(QLabel("Experience:"))
        self.xp_reward_label = QLabel("0 XP")
        self.xp_reward_label.setStyleSheet("font-weight: bold;")
        xp_layout.addWidget(self.xp_reward_label)
        xp_layout.addStretch()
        layout.addLayout(xp_layout)

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
        self.item_rewards_list.setMaximumHeight(100)
        layout.addWidget(self.item_rewards_list)

        return group

    def create_dialogues_section(self):
        """Create quest dialogues section"""
        group = QGroupBox("Quest Dialogues")
        layout = QVBoxLayout(group)

        # Dialogue tree
        self.dialogues_tree = QTreeWidget()
        self.dialogues_tree.setHeaderLabels(["Speaker", "Dialogue", "Type"])
        self.dialogues_tree.setAlternatingRowColors(True)
        self.dialogues_tree.setColumnWidth(0, 100)
        self.dialogues_tree.setColumnWidth(1, 400)
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

        self.update_basic_info()
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

    def update_quest_giver(self):
        """Update quest giver information"""
        quest = self.current_quest

        # Try to get quest giver NPC ID
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
            self.quest_giver_label.setText("Unknown")

        # Location/Map
        location = getattr(quest, "map", None)
        if not location:
            location = getattr(quest, "platform", None)
        if location:
            self.quest_location_label.setText(str(location))
        else:
            self.quest_location_label.setText("Unknown")

    def update_accept_requirements(self):
        """Update requirements to accept quest"""
        quest = self.current_quest
        self.accept_requirements_list.clear()

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

        # Other requirements
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
            self.accept_requirements_list.addItem("No special requirements")

    def update_objectives(self):
        """Update quest objectives/completion requirements"""
        quest = self.current_quest
        self.objectives_tree.clear()

        # Get objectives
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
            item = QTreeWidgetItem(["No objectives defined", "-", "-", "-"])
            self.objectives_tree.addTopLevelItem(item)

    def update_rewards(self):
        """Update quest rewards"""
        quest = self.current_quest

        # XP reward
        xp = getattr(quest, "xp_reward", None)
        if not xp:
            xp = getattr(quest, "experience", 0)
        self.xp_reward_label.setText(f"{xp} XP" if xp else "0 XP")

        # Money rewards
        gold = getattr(quest, "gold_reward", 0)
        silver = getattr(quest, "silver_reward", 0)
        copper = getattr(quest, "copper_reward", 0)
        self.money_reward_label.setText(
            f"{gold} Gold, {silver} Silver, {copper} Copper"
        )

        # Item rewards
        self.item_rewards_list.clear()
        item_rewards = getattr(quest, "item_rewards", None)
        if item_rewards:
            if isinstance(item_rewards, list):
                for item in item_rewards:
                    self.item_rewards_list.addItem(f"Item ID: {item}")
            else:
                self.item_rewards_list.addItem(str(item_rewards))

        if self.item_rewards_list.count() == 0:
            self.item_rewards_list.addItem("No item rewards")

    def update_dialogues(self):
        """Update quest dialogues"""
        quest = self.current_quest
        self.dialogues_tree.clear()

        quest_id = getattr(quest, "quest_id", None)
        if not quest_id:
            return

        # Find dialogues related to this quest
        dialogues = self.find_quest_dialogues(quest_id)

        for dialogue_name, dialogue_text, speaker_type in dialogues:
            # Truncate text for display
            display_text = (
                dialogue_text[:100] + "..."
                if len(dialogue_text) > 100
                else dialogue_text
            )
            item = QTreeWidgetItem([speaker_type, display_text, "Quest Dialogue"])

            # Format based on speaker
            if "Player" in speaker_type:
                font = item.font(0)
                font.setItalic(True)
                item.setFont(0, font)
                item.setFont(1, font)

            self.dialogues_tree.addTopLevelItem(item)

        if self.dialogues_tree.topLevelItemCount() == 0:
            item = QTreeWidgetItem(
                ["No dialogues", "No dialogues found for this quest", "-"]
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
