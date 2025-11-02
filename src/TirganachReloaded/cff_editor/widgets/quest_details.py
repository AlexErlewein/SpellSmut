"""
Quest Details Widget
Shows detailed quest information including dialogs and related data
"""

from loguru import logger
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
        logger.warning("⚠️  OLD QuestDetailsWidget initialized (THIS SHOULD NOT HAPPEN!)")
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
        self.title_label = QLabel("Quest Dialogs & Hierarchy")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Top section - Quest dialogs
        self.setup_dialogs_section()
        splitter.addWidget(self.dialogs_group)

        # Bottom section - Quest hierarchy
        self.setup_hierarchy_section()
        splitter.addWidget(self.hierarchy_group)

        # Set splitter proportions (dialogs get more space)
        splitter.setSizes([400, 200])

        layout.addWidget(splitter)

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

        self.view_dialog_button = QPushButton("View in Window")
        self.view_dialog_button.clicked.connect(self.open_dialog_viewer)
        self.view_dialog_button.setEnabled(False)
        button_layout.addWidget(self.view_dialog_button)

        self.dialogs_status = QLabel("Select a quest to view dialogs")
        self.dialogs_status.setStyleSheet("color: gray; font-style: italic;")
        button_layout.addWidget(self.dialogs_status)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Dialogs tree
        self.dialogs_tree = QTreeWidget()
        self.dialogs_tree.setHeaderLabels(["Dialog Name", "Text Preview"])
        self.dialogs_tree.setAlternatingRowColors(True)
        self.dialogs_tree.itemDoubleClicked.connect(self.on_dialog_double_clicked)
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
            
            # Also try to load Lua quest data if available
            self.load_lua_quest_details()
        else:
            self.current_quest = None
            self.clear_details()

    def update_quest_details(self):
        """Update all quest detail sections"""
        if not self.current_quest:
            self.clear_details()
            return

        # Auto-load dialogs (now optimized with caching)
        self.load_dialogs_on_demand()

        # Update hierarchy
        self.update_hierarchy()

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
        self.current_dialogs = self.find_quest_dialogs(quest_id)

        self.dialogs_tree.clear()
        for dialog_name, dialog_text in self.current_dialogs:
            # Show truncated text preview
            preview = (
                dialog_text[:100] + "..." if len(dialog_text) > 100 else dialog_text
            )
            item = QTreeWidgetItem([dialog_name, preview])
            # Store full text in user data
            item.setData(0, Qt.ItemDataRole.UserRole, dialog_text)
            self.dialogs_tree.addTopLevelItem(item)

        # Resize columns
        self.dialogs_tree.resizeColumnToContents(0)
        self.dialogs_tree.resizeColumnToContents(1)

        # Expand if few items
        if len(self.current_dialogs) <= 5:
            self.dialogs_tree.expandAll()

        if self.current_dialogs:
            self.dialogs_status.setText(f"Loaded {len(self.current_dialogs)} dialog(s)")
            self.view_dialog_button.setEnabled(True)
        else:
            self.dialogs_status.setText("No dialogs found for this quest")
            self.view_dialog_button.setEnabled(False)

    def update_dialogs(self):
        """Update quest dialogs - kept for compatibility but now uses lazy loading"""
        # This is now handled by load_dialogs_on_demand
        pass

    def on_dialog_double_clicked(self, item, column):
        """Handle double-click on dialog item"""
        dialog_name = item.text(0)
        dialog_text = item.data(0, Qt.ItemDataRole.UserRole)
        if dialog_text:
            self.show_dialog_window(dialog_name, dialog_text)

    def open_dialog_viewer(self):
        """Open dialog viewer window with all quest dialogs"""
        if not hasattr(self, "current_dialogs") or not self.current_dialogs:
            return

        quest_name = self.data_model.safe_get_text_field(self.current_quest, "name")
        if not quest_name:
            quest_name = f"Quest {getattr(self.current_quest, 'quest_id', 'Unknown')}"

        self.show_dialog_window(f"Dialogs for: {quest_name}", self.format_all_dialogs())

    def format_all_dialogs(self):
        """Format all dialogs for display"""
        if not hasattr(self, "current_dialogs") or not self.current_dialogs:
            return "No dialogs loaded."

        formatted = []
        for dialog_name, dialog_text in self.current_dialogs:
            formatted.append(f"=== {dialog_name} ===\n{dialog_text}\n")
        return "\n".join(formatted)

    def show_dialog_window(self, title, text):
        """Show dialog text in a separate window"""
        from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(700, 500)

        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit()
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)

        dialog.exec()

    def update_hierarchy(self):
        """Update quest hierarchy using safe lookups"""
        self.hierarchy_tree.clear()

        if not self.current_quest:
            return

        quest_id = getattr(self.current_quest, "quest_id", None)
        if not quest_id:
            return

        # Get parent quest ID directly instead of using Relation
        parent_quest_id = getattr(self.current_quest, "parent_quest_id", 0)
        if parent_quest_id and parent_quest_id != 0:
            # Find parent quest in the quests table
            quests_table = self.data_model.get_elements("quests")
            parent_quest = None
            for quest in quests_table:
                if getattr(quest, "quest_id", None) == parent_quest_id:
                    parent_quest = quest
                    break

            if parent_quest:
                parent_name = self.data_model.safe_get_text_field(parent_quest, "name")
                if not parent_name:
                    parent_name = f"Quest {parent_quest_id}"
                parent_item = QTreeWidgetItem(
                    [str(parent_name), str(parent_quest_id), "Parent"]
                )
                self.hierarchy_tree.addTopLevelItem(parent_item)

        # Add current quest
        current_name = self.data_model.safe_get_text_field(self.current_quest, "name")
        if not current_name:
            current_name = f"Quest {quest_id}"
        current_item = QTreeWidgetItem([str(current_name), str(quest_id), "Current"])
        current_item.setBackground(0, self.palette().highlight())
        self.hierarchy_tree.addTopLevelItem(current_item)

        # Find sub-quests by searching for quests with matching parent_quest_id
        quests_table = self.data_model.get_elements("quests")
        for quest in quests_table:
            quest_parent_id = getattr(quest, "parent_quest_id", 0)
            if quest_parent_id == quest_id:
                sub_id = getattr(quest, "quest_id", "Unknown")
                sub_name = self.data_model.safe_get_text_field(quest, "name")
                if not sub_name:
                    sub_name = f"Quest {sub_id}"
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
            logger.error(f"Error building localisation index: {e}")

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
            logger.error(f"Error finding quest dialogs: {e}")
            import traceback

            traceback.print_exc()
            dialogs = [("Error", f"Could not load dialogs: {str(e)}")]

        # Cache the result
        self.dialog_cache[cache_key] = dialogs
        return dialogs

    def clear_details(self):
        """Clear all quest details"""
        self.dialogs_tree.clear()
        self.dialogs_status.setText("Select a quest to view dialogs")
        self.load_dialogs_button.setEnabled(False)
        self.view_dialog_button.setEnabled(False)
        self.hierarchy_tree.clear()
        if hasattr(self, "current_dialogs"):
            self.current_dialogs = []

    def load_lua_quest_details(self):
        """Load and display Lua quest data if available"""
        if not self.current_quest:
            return
            
        quest_id = getattr(self.current_quest, "quest_id", None)
        if not quest_id:
            return
            
        # Try to get Lua quest data from the data model
        try:
            lua_quest_data = self.data_model.get_lua_quest_data(quest_id)
            if lua_quest_data:
                # Display Lua quest information in the details
                self.display_lua_quest_data(lua_quest_data)
        except Exception as e:
            # Silently fail if Lua data is not available
            pass
            
    def display_lua_quest_data(self, lua_quest):
        """Display Lua quest data in the details panel"""
        # This could be enhanced to show Lua-specific information
        # For now, we'll just log that Lua data is available
        logger.info(f"Lua quest data available for quest {lua_quest.quest_id}: {lua_quest.quest_name}")
