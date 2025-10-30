"""
Quest Details Widget
Shows detailed quest information including dialogs and related data
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class QuestDetailsWidget(QWidget):
    """Widget displaying detailed quest information"""

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.current_quest = None

        # Cache for dialog lookups to avoid repeated searches
        self.dialog_cache = {}
        self.localisation_index = None  # Index for faster lookups
        self.cache_valid = False

        self.setup_ui()

        # Connect to data model signals
        self.data_model.category_changed.connect(self.on_category_changed)
        self.data_model.element_selected.connect(self.on_element_selected)
        self.data_model.data_loaded.connect(self.on_data_loaded)

    def setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        self.title_label = QLabel("Quest Details")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Top section - Basic quest info
        self.setup_basic_info_section()
        splitter.addWidget(self.basic_info_group)

        # Middle section - Quest dialogs
        self.setup_dialogs_section()
        splitter.addWidget(self.dialogs_group)

        # Bottom section - Quest hierarchy
        self.setup_hierarchy_section()
        splitter.addWidget(self.hierarchy_group)

        # Set splitter proportions
        splitter.setSizes([200, 300, 200])

        layout.addWidget(splitter)

    def setup_basic_info_section(self):
        """Setup basic quest information section"""
        self.basic_info_group = QGroupBox("Quest Information")
        layout = QVBoxLayout(self.basic_info_group)

        # Quest ID and name
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Quest ID:"))
        self.quest_id_label = QLabel("None")
        id_layout.addWidget(self.quest_id_label)
        id_layout.addStretch()
        layout.addLayout(id_layout)

        # Quest name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.quest_name_label = QLabel("None")
        self.quest_name_label.setWordWrap(True)
        name_layout.addWidget(self.quest_name_label)
        name_layout.addStretch()
        layout.addLayout(name_layout)

        # Description
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.description_text = QTextEdit()
        self.description_text.setMaximumHeight(80)
        self.description_text.setReadOnly(True)
        desc_layout.addWidget(self.description_text)
        layout.addLayout(desc_layout)

    def setup_dialogs_section(self):
        """Setup quest dialogs section"""
        self.dialogs_group = QGroupBox("Quest Dialogs")
        layout = QVBoxLayout(self.dialogs_group)

        # Load button and status
        button_layout = QHBoxLayout()
        self.load_dialogs_button = QPushButton("Load Dialogs")
        self.load_dialogs_button.clicked.connect(self.load_dialogs_on_demand)
        self.load_dialogs_button.setEnabled(False)
        button_layout.addWidget(self.load_dialogs_button)

        self.dialogs_status = QLabel("Select a quest to view dialogs")
        self.dialogs_status.setStyleSheet("color: gray; font-style: italic;")
        button_layout.addWidget(self.dialogs_status)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Dialogs tree
        self.dialogs_tree = QTreeWidget()
        self.dialogs_tree.setHeaderLabels(["Dialog Name", "Text"])
        self.dialogs_tree.setAlternatingRowColors(True)
        layout.addWidget(self.dialogs_tree)

    def setup_hierarchy_section(self):
        """Setup quest hierarchy section"""
        self.hierarchy_group = QGroupBox("Quest Hierarchy")
        layout = QVBoxLayout(self.hierarchy_group)

        # Hierarchy tree
        self.hierarchy_tree = QTreeWidget()
        self.hierarchy_tree.setHeaderLabels(["Quest", "ID", "Type"])
        self.hierarchy_tree.setAlternatingRowColors(True)
        layout.addWidget(self.hierarchy_tree)

    def on_category_changed(self, category):
        """Handle category change"""
        if category == "quests":
            self.show()
            self.title_label.setText("Quest Details")
        else:
            self.hide()

    def on_data_loaded(self):
        """Handle data loaded signal - invalidate caches"""
        self.dialog_cache.clear()
        self.localisation_index = None
        self.cache_valid = False

    def on_element_selected(self, category, element_index):
        """Handle element selection"""
        if category != "quests":
            return

        # Get the actual quest element from the index
        elements = self.data_model.get_elements(category)

        if 0 <= element_index < len(elements):
            self.current_quest = elements[element_index]
            self.update_quest_details()
        else:
            self.current_quest = None
            self.clear_details()

    def update_quest_details(self):
        """Update all quest detail sections"""
        if not self.current_quest:
            self.clear_details()
            return

        # Update basic info
        self.update_basic_info()

        # Auto-load dialogs (now optimized with caching)
        self.load_dialogs_on_demand()

        # Update hierarchy
        self.update_hierarchy()

    def update_basic_info(self):
        """Update basic quest information"""
        quest = self.current_quest

        # Quest ID
        quest_id = getattr(quest, "quest_id", "Unknown")
        self.quest_id_label.setText(str(quest_id))

        # Quest name - use localised text lookup (fast with index)
        quest_name = self.data_model.get_localised_text(quest, "name")
        if quest_name:
            self.quest_name_label.setText(str(quest_name))
        else:
            # Fallback to name field if localisation fails
            quest_name = getattr(quest, "name", "Unknown")
            if quest_name and quest_name != "Unknown":
                self.quest_name_label.setText(str(quest_name))
            else:
                self.quest_name_label.setText(f"Quest {quest_id}")

        # Description - use advanced description lookup (fast with index)
        # IMPORTANT: Do NOT use getattr(quest, "description") - it's a Relation that does expensive lookups!
        description = self.data_model.get_advanced_description(quest)
        if description:
            self.description_text.setPlainText(str(description))
        else:
            self.description_text.setPlainText("No description available")

    def load_dialogs_on_demand(self):
        """Load dialogs when user clicks the button"""
        if not self.current_quest:
            return

        quest_id = getattr(self.current_quest, "quest_id", None)
        if not quest_id:
            return

        self.dialogs_status.setText("Loading dialogs...")
        self.load_dialogs_button.setEnabled(False)

        # Process events to show the loading message
        from PySide6.QtWidgets import QApplication

        QApplication.processEvents()

        # Find dialogs related to this quest
        dialogs = self.find_quest_dialogs(quest_id)

        self.dialogs_tree.clear()
        for dialog_name, dialog_text in dialogs:
            item = QTreeWidgetItem([dialog_name, dialog_text])
            self.dialogs_tree.addTopLevelItem(item)

        # Resize columns
        self.dialogs_tree.resizeColumnToContents(0)
        self.dialogs_tree.resizeColumnToContents(1)

        # Expand if few items
        if len(dialogs) <= 5:
            self.dialogs_tree.expandAll()

        if dialogs:
            self.dialogs_status.setText(f"Loaded {len(dialogs)} dialog(s)")
        else:
            self.dialogs_status.setText("No dialogs found for this quest")

    def update_dialogs(self):
        """Update quest dialogs - kept for compatibility but now uses lazy loading"""
        # This is now handled by load_dialogs_on_demand
        pass

    def update_hierarchy(self):
        """Update quest hierarchy"""
        self.hierarchy_tree.clear()

        if not self.current_quest:
            return

        quest_id = getattr(self.current_quest, "quest_id", None)
        if not quest_id:
            return

        # Add parent quest if exists
        parent_quest = getattr(self.current_quest, "parent_quest", None)
        if parent_quest:
            parent_id = getattr(parent_quest, "quest_id", "Unknown")
            parent_name = getattr(parent_quest, "name", f"Quest {parent_id}")
            parent_item = QTreeWidgetItem([str(parent_name), str(parent_id), "Parent"])
            self.hierarchy_tree.addTopLevelItem(parent_item)

        # Add current quest
        current_name = getattr(self.current_quest, "name", f"Quest {quest_id}")
        current_item = QTreeWidgetItem([str(current_name), str(quest_id), "Current"])
        current_item.setBackground(0, self.palette().highlight())
        self.hierarchy_tree.addTopLevelItem(current_item)

        # Add sub-quests
        sub_quests = getattr(self.current_quest, "sub_quests", [])
        for sub_quest in sub_quests:
            sub_id = getattr(sub_quest, "quest_id", "Unknown")
            sub_name = getattr(sub_quest, "name", f"Quest {sub_id}")
            sub_item = QTreeWidgetItem([str(sub_name), str(sub_id), "Sub-quest"])
            current_item.addChild(sub_item)

        # Resize columns
        self.hierarchy_tree.resizeColumnToContents(0)
        self.hierarchy_tree.resizeColumnToContents(1)
        self.hierarchy_tree.resizeColumnToContents(2)

        # Expand all
        self.hierarchy_tree.expandAll()

    def build_localisation_index(self):
        """Build an index of localisation entries for fast lookup"""
        if self.localisation_index is not None and self.cache_valid:
            return  # Already built

        self.localisation_index = {"by_text_id": {}, "by_quest_id": {}, "dialogues": []}

        try:
            localisation_table = self.data_model.get_elements("localisation")
            if not localisation_table:
                return

            current_language = self.data_model.get_current_language()

            # Build index - do this once instead of iterating every time
            for entry in localisation_table:
                entry_language = getattr(entry, "language", None)

                # Only index entries for current language
                if entry_language != current_language:
                    continue

                text_id = getattr(entry, "text_id", None)
                dialogue_name = getattr(entry, "dialogue_name", "")
                is_dialogue = getattr(entry, "is_dialogue", False)

                # Index by text ID
                if text_id is not None:
                    self.localisation_index["by_text_id"][text_id] = entry

                # Index dialogues by quest ID (if quest ID is in dialogue name)
                if is_dialogue and dialogue_name:
                    # Extract quest ID from dialogue name if present
                    import re

                    quest_id_match = re.search(
                        r"quest[_\s]*(\d+)", dialogue_name.lower()
                    )
                    if quest_id_match:
                        quest_id = int(quest_id_match.group(1))
                        if quest_id not in self.localisation_index["by_quest_id"]:
                            self.localisation_index["by_quest_id"][quest_id] = []
                        self.localisation_index["by_quest_id"][quest_id].append(entry)

                    # Also add to general dialogues list
                    self.localisation_index["dialogues"].append(entry)

            self.cache_valid = True

        except Exception as e:
            print(f"Error building localisation index: {e}")

    def find_quest_dialogs(self, quest_id):
        """Find dialogs related to a quest (optimized with caching)"""
        # Check cache first
        cache_key = (quest_id, self.data_model.get_current_language())
        if cache_key in self.dialog_cache:
            return self.dialog_cache[cache_key]

        dialogs = []

        try:
            # Build index if not already built
            self.build_localisation_index()

            # Get quests table to understand dialog naming patterns
            quests_table = self.data_model.get_elements("quests")
            if not quests_table:
                return dialogs

            # Find the specific quest to understand its connections
            current_quest = None
            for quest in quests_table:
                if getattr(quest, "quest_id", None) == quest_id:
                    current_quest = quest
                    break

            if not current_quest:
                return dialogs

            # Get quest name ID and description ID to find related text
            quest_name_id = getattr(current_quest, "name_id", None)
            quest_description_id = getattr(current_quest, "description_id", None)

            # Look up by text IDs (fast O(1) lookup)
            if (
                quest_name_id is not None
                and quest_name_id in self.localisation_index["by_text_id"]
            ):
                entry = self.localisation_index["by_text_id"][quest_name_id]
                text_content = getattr(entry, "text", "")
                dialogue_name = getattr(entry, "dialogue_name", "")
                if text_content:
                    dialogs.append((dialogue_name or "Quest Name", text_content))

            if (
                quest_description_id is not None
                and quest_description_id in self.localisation_index["by_text_id"]
            ):
                entry = self.localisation_index["by_text_id"][quest_description_id]
                text_content = getattr(entry, "text", "")
                dialogue_name = getattr(entry, "dialogue_name", "")
                if text_content:
                    dialogs.append((dialogue_name or "Quest Description", text_content))

            # Look up dialogues by quest ID (fast indexed lookup)
            if quest_id in self.localisation_index["by_quest_id"]:
                for entry in self.localisation_index["by_quest_id"][quest_id]:
                    text_content = getattr(entry, "text", "")
                    dialogue_name = getattr(entry, "dialogue_name", "")
                    if text_content:
                        dialogs.append((dialogue_name, text_content))

            # Only do expensive search if we haven't found anything yet
            if not dialogs:
                quest_name = getattr(current_quest, "name", "").lower()
                if quest_name:
                    # Search only through dialogues (much smaller subset)
                    for entry in self.localisation_index["dialogues"][
                        :100
                    ]:  # Limit search
                        text_content = getattr(entry, "text", "")
                        dialogue_name = getattr(entry, "dialogue_name", "")

                        if quest_name in text_content.lower():
                            dialogs.append(
                                (dialogue_name or "Related Dialog", text_content)
                            )
                            if len(dialogs) >= 10:  # Limit results
                                break

        except Exception as e:
            print(f"Error finding quest dialogs: {e}")
            import traceback

            traceback.print_exc()
            dialogs = [("Error", f"Could not load dialogs: {str(e)}")]

        # Cache the result
        self.dialog_cache[cache_key] = dialogs
        return dialogs

    def clear_details(self):
        """Clear all quest details"""
        self.quest_id_label.setText("None")
        self.quest_name_label.setText("None")
        self.description_text.clear()
        self.dialogs_tree.clear()
        self.dialogs_status.setText("Click 'Load Dialogs' to view quest dialogs")
        self.load_dialogs_button.setEnabled(True)
        self.hierarchy_tree.clear()
