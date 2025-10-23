"""
Quest Details Widget
Shows detailed quest information including dialogs and related data
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QTextEdit, QTreeWidget, QTreeWidgetItem,
                               QGroupBox, QScrollArea, QSplitter)
from PySide6.QtCore import Qt


class QuestDetailsWidget(QWidget):
    """Widget displaying detailed quest information"""

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.current_quest = None

        self.setup_ui()

        # Connect to data model signals
        self.data_model.category_changed.connect(self.on_category_changed)
        self.data_model.element_selected.connect(self.on_element_selected)

    def setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Title
        self.title_label = QLabel("Quest Details")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # Create splitter for main content
        splitter = QSplitter(Qt.Vertical)

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

        # Update dialogs
        self.update_dialogs()

        # Update hierarchy
        self.update_hierarchy()

    def update_basic_info(self):
        """Update basic quest information"""
        quest = self.current_quest

        # Quest ID
        quest_id = getattr(quest, 'quest_id', 'Unknown')
        self.quest_id_label.setText(str(quest_id))

        # Quest name
        quest_name = getattr(quest, 'name', 'Unknown')
        if quest_name:
            self.quest_name_label.setText(str(quest_name))
        else:
            self.quest_name_label.setText(f"Quest {quest_id}")

        # Description
        description = getattr(quest, 'description', '')
        if description:
            self.description_text.setPlainText(str(description))
        else:
            self.description_text.setPlainText("No description available")

    def update_dialogs(self):
        """Update quest dialogs"""
        self.dialogs_tree.clear()

        if not self.current_quest:
            return

        quest_id = getattr(self.current_quest, 'quest_id', None)
        if not quest_id:
            return

        # Find dialogs related to this quest
        dialogs = self.find_quest_dialogs(quest_id)

        for dialog_name, dialog_text in dialogs:
            item = QTreeWidgetItem([dialog_name, dialog_text])
            self.dialogs_tree.addTopLevelItem(item)

        # Resize columns
        self.dialogs_tree.resizeColumnToContents(0)
        self.dialogs_tree.resizeColumnToContents(1)

        # Expand if few items
        if len(dialogs) <= 5:
            self.dialogs_tree.expandAll()

    def update_hierarchy(self):
        """Update quest hierarchy"""
        self.hierarchy_tree.clear()

        if not self.current_quest:
            return

        quest_id = getattr(self.current_quest, 'quest_id', None)
        if not quest_id:
            return

        # Add parent quest if exists
        parent_quest = getattr(self.current_quest, 'parent_quest', None)
        if parent_quest:
            parent_id = getattr(parent_quest, 'quest_id', 'Unknown')
            parent_name = getattr(parent_quest, 'name', f'Quest {parent_id}')
            parent_item = QTreeWidgetItem([str(parent_name), str(parent_id), "Parent"])
            self.hierarchy_tree.addTopLevelItem(parent_item)

        # Add current quest
        current_name = getattr(self.current_quest, 'name', f'Quest {quest_id}')
        current_item = QTreeWidgetItem([str(current_name), str(quest_id), "Current"])
        current_item.setBackground(0, self.palette().highlight())
        self.hierarchy_tree.addTopLevelItem(current_item)

        # Add sub-quests
        sub_quests = getattr(self.current_quest, 'sub_quests', [])
        for sub_quest in sub_quests:
            sub_id = getattr(sub_quest, 'quest_id', 'Unknown')
            sub_name = getattr(sub_quest, 'name', f'Quest {sub_id}')
            sub_item = QTreeWidgetItem([str(sub_name), str(sub_id), "Sub-quest"])
            current_item.addChild(sub_item)

        # Resize columns
        self.hierarchy_tree.resizeColumnToContents(0)
        self.hierarchy_tree.resizeColumnToContents(1)
        self.hierarchy_tree.resizeColumnToContents(2)

        # Expand all
        self.hierarchy_tree.expandAll()

    def find_quest_dialogs(self, quest_id):
        """Find dialogs related to a quest"""
        dialogs = []

        try:
            # Get localisation table elements
            localisation_table = self.data_model.get_elements('localisation')
            if not localisation_table:
                return dialogs

            # Find dialogs related to this quest
            quest_id_str = str(quest_id)

            # Strategy: Show quest-related dialogues by looking for quest keywords in text
            # Since dialogue names don't directly correspond to quest IDs, we'll show
            # dialogues that contain quest-related words

            quest_keywords = ['quest', 'mission', 'task', 'objective', 'duty', 'assignment']
            english_entries = []  # Focus on English entries for cleaner display

            # First, collect English dialogue entries (language.value == 1 for ENGLISH)
            for entry in localisation_table:
                if getattr(entry, 'is_dialogue', False):
                    dialogue_name = getattr(entry, 'dialogue_name', '')
                    text = getattr(entry, 'text', '')

                    # Check if this matches the current language setting
                    try:
                        language = getattr(entry, 'language', None)
                        current_lang = self.data_model.get_current_language()
                        if language and language == current_lang:
                            english_entries.append((dialogue_name, text))
                    except:
                        # If language check fails, include the entry anyway
                        english_entries.append((dialogue_name, text))

            # Look for quest-related content in English dialogues
            for dialogue_name, text in english_entries:
                if not text:
                    continue

                text_lower = text.lower()

                # Check if text contains quest-related keywords
                if any(keyword in text_lower for keyword in quest_keywords):
                    dialogs.append((dialogue_name or "Unnamed Dialog", text))

                    # Limit results to keep UI manageable
                    if len(dialogs) >= 15:
                        break

            # If no quest-related dialogs found, show some general NPC dialogues
            if not dialogs:
                npc_keywords = ['hello', 'greetings', 'welcome', 'need help', 'looking for']
                for dialogue_name, text in english_entries[:100]:  # Check first 100 English entries
                    if not text:
                        continue

                    text_lower = text.lower()
                    if any(keyword in text_lower for keyword in npc_keywords):
                        dialogs.append((dialogue_name or "Unnamed Dialog", text))
                        if len(dialogs) >= 10:
                            break

            # Final fallback: show any English dialogues if still no matches
            if not dialogs:
                for dialogue_name, text in english_entries[:20]:  # Show first 20 English dialogues
                    if text:
                        dialogs.append((dialogue_name or "Unnamed Dialog", text))

        except Exception as e:
            print(f"Error finding quest dialogs: {e}")
            # Return a fallback message
            dialogs = [("Error", f"Could not load dialogs: {str(e)}")]

        return dialogs

    def clear_details(self):
        """Clear all quest details"""
        self.quest_id_label.setText("None")
        self.quest_name_label.setText("None")
        self.description_text.clear()
        self.dialogs_tree.clear()
        self.hierarchy_tree.clear()