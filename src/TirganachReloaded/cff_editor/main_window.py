"""
Main Window for CFF Editor
"""

from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from tirganach.types import Language
from .logging_config import get_logger
from .data_model import CFFDataModel
from .theme_manager import ThemeManager, ThemeType
from .widgets.building_wizard import BuildingWizard
from .widgets.category_tree import CategoryTreeWidget
from .widgets.element_table import ElementTableWidget
from .widgets.progress_dialog import ProgressDialog
from .widgets.property_editor import PropertyEditorWidget
from .widgets.quest_details import QuestDetailsWidget
from .widgets.quest_hierarchy_tree import QuestHierarchyTreeWidget


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        
        # Initialize logger
        self.logger = get_logger("main_window")
        self.logger.debug("Initializing MainWindow")
        
        self.setWindowTitle("TirganachReloaded: SpellForce GameData Editor")
        self.setMinimumSize(QSize(1500, 900))

        # Data model
        self.data_model = CFFDataModel()
        self.logger.debug("Data model initialized")

        # Theme manager
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.on_theme_changed)

        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.setup_connections()

        # Apply initial theme
        self.apply_theme(self.theme_manager.get_current_theme())

        # Auto-load default file
        self.auto_load_default_file()

    def auto_load_default_file(self):
        """Automatically load the default file on startup"""
        default_file = self.data_model.get_default_file_path()
        if default_file and Path(default_file).exists():
            self.statusBar.showMessage("Loading default file...")
            if self.data_model.load_file(default_file):
                self.statusBar.showMessage("Default file loaded successfully", 3000)
            else:
                self.statusBar.showMessage("Failed to load default file", 3000)

    def setup_ui(self):
        """Setup the main UI layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Create splitter for 3-panel layout
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Category tree
        self.category_tree = CategoryTreeWidget(self.data_model)
        splitter.addWidget(self.category_tree)

        # Center panel - Element table and Quest hierarchy tree (switchable)
        self.element_table = ElementTableWidget(self.data_model)
        self.quest_hierarchy_tree = QuestHierarchyTreeWidget(self.data_model)
        self.quest_hierarchy_tree.hide()  # Hidden by default

        splitter.addWidget(self.element_table)
        splitter.addWidget(self.quest_hierarchy_tree)

        # Right panel - Property editor
        self.property_editor = PropertyEditorWidget(self.data_model)
        splitter.addWidget(self.property_editor)

        # 4th panel - Quest details (initially hidden)
        self.quest_details = QuestDetailsWidget(self.data_model)
        self.quest_details.hide()  # Hidden by default
        self.quest_details.setMinimumWidth(150)  # Ensure minimum width when visible
        splitter.addWidget(self.quest_details)

        # Set initial sizes (20%, 35%, 30%, 15%)
        splitter.setSizes([250, 400, 350, 150])

        main_layout.addWidget(splitter)

    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open CFF...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        reload_cache_action = QAction("&Reload from CFF and Rebuild Cache", self)
        reload_cache_action.setStatusTip("Force reload from CFF file and rebuild cache")
        reload_cache_action.triggered.connect(self.reload_and_rebuild_cache)
        file_menu.addAction(reload_cache_action)

        compare_action = QAction("&Compare with...", self)
        compare_action.setStatusTip("Compare current CFF with another CFF file")
        compare_action.triggered.connect(self.compare_with_file)
        file_menu.addAction(compare_action)

        cache_info_action = QAction("Cache &Info...", self)
        cache_info_action.setStatusTip("View cache statistics and management controls")
        cache_info_action.triggered.connect(self.show_cache_info)
        file_menu.addAction(cache_info_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_view)
        edit_menu.addAction(refresh_action)

        # Language menu
        language_menu = menubar.addMenu("&Language")
        self._setup_language_menu(language_menu)

        # Theme menu
        theme_menu = menubar.addMenu("&Theme")
        self._setup_theme_menu(theme_menu)

        # View menu
        view_menu = menubar.addMenu("&View")

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        quest_editor_action = QAction("&Quest Editor", self)
        quest_editor_action.setShortcut("Ctrl+Q, E")
        quest_editor_action.setStatusTip("Edit quests with the integrated Quest Editor")
        quest_editor_action.triggered.connect(self.show_quest_editor)
        tools_menu.addAction(quest_editor_action)

        load_lua_quests_action = QAction("Load &Lua Quest Scripts...", self)
        load_lua_quests_action.setShortcut("Ctrl+L, Q")
        load_lua_quests_action.setStatusTip(
            "Load quest objectives, requirements, and rewards from Lua scripts"
        )
        load_lua_quests_action.triggered.connect(self.load_lua_quest_directory)
        tools_menu.addAction(load_lua_quests_action)

        tools_menu.addSeparator()

        spell_wizard_action = QAction("Spell &Wizard", self)
        spell_wizard_action.setShortcut("Ctrl+W")
        spell_wizard_action.setStatusTip("Create custom spells with the Spell Wizard")
        spell_wizard_action.triggered.connect(self.show_spell_wizard)
        tools_menu.addAction(spell_wizard_action)

        tools_menu.addSeparator()

        armor_forge_action = QAction("&Armor Forge", self)
        armor_forge_action.setShortcut("Ctrl+A, F")
        armor_forge_action.setStatusTip("Create and edit custom armor pieces")
        armor_forge_action.triggered.connect(self.show_armor_forge)
        tools_menu.addAction(armor_forge_action)

        weapon_forge_action = QAction("&Weapon Forge", self)
        weapon_forge_action.setShortcut("Ctrl+W, F")
        weapon_forge_action.setStatusTip("Create and edit custom weapons")
        weapon_forge_action.triggered.connect(self.show_weapon_forge)
        tools_menu.addAction(weapon_forge_action)

        tools_menu.addSeparator()
        npc_creator_action = QAction("&NPC Creator", self)
        npc_creator_action.setShortcut("Ctrl+N, C")
        npc_creator_action.setStatusTip(
            "Create and edit custom NPCs with the NPC Creator Wizard"
        )
        npc_creator_action.triggered.connect(self.show_npc_creator)
        tools_menu.addAction(npc_creator_action)

        building_wizard_action = QAction("&Building Wizard", self)
        building_wizard_action.setStatusTip("Create and edit custom buildings")
        building_wizard_action.triggered.connect(self.show_building_wizard)
        tools_menu.addAction(building_wizard_action)

        race_creator_action = QAction("&Race Creator", self)
        race_creator_action.setStatusTip("Create and edit custom races")
        race_creator_action.triggered.connect(self.show_race_creator)
        tools_menu.addAction(race_creator_action)

        tools_menu.addSeparator()

        id_manager_action = QAction("&ID Manager", self)
        id_manager_action.setShortcut("Ctrl+I, M")
        id_manager_action.setStatusTip("Manage unique IDs for all content types")
        id_manager_action.triggered.connect(self.show_id_manager)
        tools_menu.addAction(id_manager_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _setup_language_menu(self, language_menu):
        """Setup language selection menu"""
        # Language options
        languages = [
            ("&German", Language.GERMAN),
            ("&English", Language.ENGLISH),
            ("&French", Language.FRENCH),
            ("&Spanish", Language.SPANISH),
            ("&Italian", Language.ITALIAN),
            ("&_HAEGAR", Language._HAEGAR),
        ]

        # Create action group for radio button behavior
        language_group = QActionGroup(self)
        language_group.setExclusive(True)

        for lang_name, lang_enum in languages:
            action = QAction(lang_name, self)
            action.setCheckable(True)
            action.setChecked(self.data_model.get_current_language() == lang_enum)
            action.triggered.connect(
                lambda checked, lang=lang_enum: self._on_language_selected(lang)
            )
            language_menu.addAction(action)
            language_group.addAction(action)

    def _on_language_selected(self, language: Language):
        """Handle language selection"""
        self.data_model.set_current_language(language)
        self.statusBar.showMessage(f"Language changed to {language.name}", 2000)
        self.refresh_view()

    def _setup_theme_menu(self, theme_menu):
        """Setup theme selection menu"""
        # Create action group for radio button behavior
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)

        for theme_type in ThemeType:
            action = QAction(theme_type.value, self)
            action.setCheckable(True)
            action.setChecked(self.theme_manager.get_current_theme() == theme_type)
            action.triggered.connect(
                lambda checked, theme=theme_type: self._on_theme_selected(theme)
            )
            theme_menu.addAction(action)
            theme_group.addAction(action)

    def _on_theme_selected(self, theme_type: ThemeType):
        """Handle theme selection"""
        self.theme_manager.set_theme(theme_type)
        self.statusBar.showMessage(f"Theme changed to {theme_type.value}", 2000)

    def on_theme_changed(self, theme_name: str):
        """Handle theme change signal"""
        self.apply_theme(self.theme_manager.get_current_theme())

    def apply_theme(self, theme_type: ThemeType):
        """Apply specified theme to the application"""
        stylesheet = self.theme_manager.get_theme(theme_type)
        self.setStyleSheet(stylesheet)

    def setup_statusbar(self):
        """Setup status bar"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # File path label
        self.file_label = QLabel("No file loaded")
        self.statusBar.addWidget(self.file_label)

        # Modified indicator
        self.modified_label = QLabel("")
        self.statusBar.addPermanentWidget(self.modified_label)

        # Stats label
        self.stats_label = QLabel("")
        self.statusBar.addPermanentWidget(self.stats_label)

    def setup_connections(self):
        """Setup signal/slot connections"""
        self.data_model.data_loaded.connect(self.on_data_loaded)
        self.data_model.data_modified.connect(self.on_data_modified)
        self.data_model.category_changed.connect(self.on_category_changed)
        self.data_model.language_changed.connect(self.on_language_changed)
        self.data_model.element_selected.connect(self.on_element_selected)

    def open_file(self):
        """Open CFF file dialog"""
        # Get default directory (last opened file's directory or fallback)
        default_file = self.data_model.get_default_file_path()
        default_dir = (
            str(Path(default_file).parent)
            if default_file
            else "H:/SpellSmut/OriginalGameFiles/data"
        )

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open GameData.cff", default_dir, "CFF Files (*.cff);;All Files (*)"
        )

        if file_path:
            self.statusBar.showMessage("Loading file...")
            if self.data_model.load_file(file_path):
                self.statusBar.showMessage("File loaded successfully", 3000)
            else:
                QMessageBox.critical(self, "Error", "Failed to load CFF file")
                self.statusBar.showMessage("Failed to load file", 3000)

    def save_file(self):
        """Save current file"""
        if not self.data_model.game_data:
            QMessageBox.warning(self, "Warning", "No file loaded")
            return

        if self.data_model.save_file():
            self.statusBar.showMessage("File saved successfully", 3000)
            self.update_status()
        else:
            QMessageBox.critical(self, "Error", "Failed to save file")

    def save_file_as(self):
        """Save as new file"""
        if not self.data_model.game_data:
            QMessageBox.warning(self, "Warning", "No file loaded")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save GameData.cff As",
            "H:/SpellSmut/ModdedGameFiles",
            "CFF Files (*.cff);;All Files (*)",
        )

        if file_path:
            if self.data_model.save_file(file_path):
                self.statusBar.showMessage("File saved successfully", 3000)
                self.update_status()
            else:
                QMessageBox.critical(self, "Error", "Failed to save file")

    def reload_and_rebuild_cache(self):
        """Force reload from CFF and rebuild cache with progress dialog"""
        if not self.data_model.file_path:
            QMessageBox.warning(self, "Warning", "No file currently loaded")
            return

        def rebuild_operation(progress_callback=None, step_callback=None):
            """Background operation to rebuild cache"""
            if step_callback:
                step_callback("Parsing CFF file")
            if progress_callback:
                progress_callback(10, "Parsing CFF file...")

            success = self.data_model.load_file(
                self.data_model.file_path, force_parse=True
            )

            if success:
                if progress_callback:
                    progress_callback(100, "Cache rebuilt successfully")
            else:
                raise Exception("Failed to rebuild cache")

            return success

        # Show progress dialog
        progress_dialog = ProgressDialog(
            "Rebuilding Cache",
            f"Rebuilding cache for {self.data_model.file_path}",
            self,
        )

        # Create worker thread first
        progress_dialog.worker_thread = progress_dialog._create_worker(
            rebuild_operation
        )

        # Connect completion handler to refresh UI in main thread
        def on_rebuild_complete(result):
            """Called in main thread when rebuild completes"""
            if result:
                # Now safely refresh UI in main thread
                self.refresh_view()
                self.on_data_loaded()

        progress_dialog.worker_thread.operation_completed.connect(on_rebuild_complete)

        # Now start the operation
        progress_dialog._start_worker()

    def compare_with_file(self):
        """Compare current CFF with another CFF file"""
        if not self.data_model.game_data:
            QMessageBox.warning(self, "Warning", "No file currently loaded")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CFF file to compare with",
            str(Path(self.data_model.file_path).parent)
            if self.data_model.file_path
            else "",
            "CFF Files (*.cff);;All Files (*)",
        )

        if file_path:
            self._perform_comparison(file_path)

    def show_cache_info(self):
        """Show the cache information dialog"""
        try:
            from .widgets.cache_info_dialog import CacheInfoDialog

            dialog = CacheInfoDialog(self.data_model, self)
            dialog.exec()

        except ImportError as e:
            QMessageBox.warning(
                self, "Import Error", f"Failed to load cache info dialog: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred opening cache info: {str(e)}"
            )

    def _perform_comparison(self, compare_file_path: str):
        """Perform the actual comparison between current and selected file"""
        if not self.data_model.game_data:
            QMessageBox.warning(self, "Warning", "No current file loaded")
            return

        try:
            self.statusBar.showMessage("Loading comparison file...")

            # Check if we can use DB-based comparison
            if (
                hasattr(self.data_model, "data_provider")
                and self.data_model.data_provider
                and hasattr(self.data_model.data_provider, "get_quests")
            ):
                # Use DB-based comparison
                comparison_text = self._perform_db_comparison(compare_file_path)
            else:
                # Use traditional CFF comparison
                comparison_text = self._perform_cff_comparison(compare_file_path)

            # Show results in a dialog
            self._show_comparison_results(comparison_text, compare_file_path)

            self.statusBar.showMessage("Comparison completed", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to compare files: {str(e)}")
            self.statusBar.showMessage("Comparison failed", 3000)

    def _perform_cff_comparison(self, compare_file_path: str) -> str:
        """Perform traditional CFF file comparison"""
        from tirganach import GameData
        from tirganach.compare import compare

        # Load the comparison file
        compare_data = GameData(compare_file_path)

        # Create a simple text output for the comparison
        import io
        from contextlib import redirect_stdout

        # Capture the comparison output
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            compare(self.data_model.game_data, compare_data)

        return output_buffer.getvalue()

    def _perform_db_comparison(self, compare_file_path: str) -> str:
        """Perform database-based comparison for faster results"""
        try:
            import os
            import tempfile

            from cff_editor.data_providers import DatabaseManager, DBProvider

            # Create temporary database for comparison file
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
                temp_db_path = f.name

            try:
                # Load comparison file and create its database
                from tirganach import GameData

                compare_data = GameData(compare_file_path)

                # Generate fingerprint for comparison file
                import hashlib
                from pathlib import Path

                path = Path(compare_file_path)
                stat = path.stat()
                compare_fingerprint = hashlib.sha256(
                    f"{path.absolute()}{stat.st_size}{stat.st_mtime}".encode()
                ).hexdigest()

                # Create and populate comparison database
                compare_db = DatabaseManager(temp_db_path)
                compare_db.create_schema()
                compare_db.populate_from_cff(compare_data, compare_fingerprint)
                compare_provider = DBProvider(temp_db_path)

                # Perform DB-based comparison
                return self._compare_databases(
                    self.data_model.data_provider, compare_provider, compare_file_path
                )

            finally:
                # Clean up temporary database
                try:
                    os.unlink(temp_db_path)
                except:
                    pass

        except Exception as e:
            # Fall back to CFF comparison
            self.logger.warning(f"DB comparison failed, falling back to CFF: {e}")
            return self._perform_cff_comparison(compare_file_path)

    def _compare_databases(
        self, db1_provider, db2_provider, compare_file_path: str
    ) -> str:
        """Compare two database providers and return formatted diff"""
        lines = []
        lines.append("Database-based Comparison Results")
        lines.append("=" * 50)
        lines.append(f"File 1: {self.data_model.file_path or 'Current'}")
        lines.append(f"File 2: {compare_file_path}")
        lines.append("")

        try:
            # Compare quests
            quests1 = db1_provider.get_quests()
            quests2 = db2_provider.get_quests()

            lines.append("QUESTS COMPARISON")
            lines.append("-" * 20)

            quests1_dict = {q.quest_id: q for q in quests1}
            quests2_dict = {q.quest_id: q for q in quests2}

            # Quests in file 1 but not in file 2
            only_in_1 = set(quests1_dict.keys()) - set(quests2_dict.keys())
            if only_in_1:
                lines.append(f"Quests only in file 1 ({len(only_in_1)}):")
                for qid in sorted(only_in_1):
                    quest = quests1_dict[qid]
                    lines.append(f"  - ID {qid}: {quest.name or 'Unnamed'}")
                lines.append("")

            # Quests in file 2 but not in file 1
            only_in_2 = set(quests2_dict.keys()) - set(quests1_dict.keys())
            if only_in_2:
                lines.append(f"Quests only in file 2 ({len(only_in_2)}):")
                for qid in sorted(only_in_2):
                    quest = quests2_dict[qid]
                    lines.append(f"  - ID {qid}: {quest.name or 'Unnamed'}")
                lines.append("")

            # Modified quests
            modified = []
            for qid in set(quests1_dict.keys()) & set(quests2_dict.keys()):
                q1 = quests1_dict[qid]
                q2 = quests2_dict[qid]
                if (
                    q1.name_id != q2.name_id
                    or q1.description_id != q2.description_id
                    or q1.name != q2.name
                    or q1.description != q2.description
                ):
                    modified.append((qid, q1, q2))

            if modified:
                lines.append(f"Modified quests ({len(modified)}):")
                for qid, q1, q2 in modified[:10]:  # Limit to first 10
                    lines.append(f"  - ID {qid}:")
                    if q1.name != q2.name:
                        lines.append(f"    Name: '{q1.name}' -> '{q2.name}'")
                    if q1.name_id != q2.name_id:
                        lines.append(f"    Name ID: {q1.name_id} -> {q2.name_id}")
                    if q1.description_id != q2.description_id:
                        lines.append(
                            f"    Description ID: {q1.description_id} -> {q2.description_id}"
                        )
                if len(modified) > 10:
                    lines.append(f"  ... and {len(modified) - 10} more")
                lines.append("")

            lines.append(
                f"Summary: {len(quests1)} quests in file 1, {len(quests2)} quests in file 2"
            )

        except Exception as e:
            lines.append(f"Error during quest comparison: {e}")

        return "\n".join(lines)

    def _show_comparison_results(self, comparison_text: str, compare_file_path: str):
        """Show comparison results in a dialog"""
        from PySide6.QtWidgets import (
            QDialog,
            QHBoxLayout,
            QPushButton,
            QTextEdit,
            QVBoxLayout,
        )

        dialog = QDialog(self)
        compare_path = Path(compare_file_path)
        dialog.setWindowTitle(f"Comparison Results - {compare_path.name}")
        dialog.setMinimumSize(800, 600)

        layout = QVBoxLayout(dialog)

        # Text area for results
        text_edit = QTextEdit()
        text_edit.setPlainText(comparison_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)

        # Buttons
        button_layout = QHBoxLayout()

        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(lambda: self._copy_to_clipboard(comparison_text))
        button_layout.addWidget(copy_button)

        save_button = QPushButton("Save As...")
        save_button.clicked.connect(
            lambda: self._save_comparison_results(comparison_text, compare_file_path)
        )
        button_layout.addWidget(save_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        dialog.exec()

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        from PySide6.QtWidgets import QApplication

        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def _save_comparison_results(self, comparison_text: str, compare_file_path: str):
        """Save comparison results to file"""
        current_file_stem = (
            Path(self.data_model.file_path).stem
            if self.data_model.file_path
            else "current"
        )
        default_name = (
            f"comparison_{current_file_stem}_vs_{Path(compare_file_path).stem}.txt"
        )

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Comparison Results",
            default_name,
            "Text Files (*.txt);;Markdown Files (*.md);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("# CFF Comparison Results\n\n")
                    f.write(f"**File 1:** {self.data_model.file_path}\n")
                    f.write(f"**File 2:** {compare_file_path}\n\n")
                    f.write("```\n")
                    f.write(comparison_text)
                    f.write("```\n")
                self.statusBar.showMessage("Comparison results saved", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save results: {str(e)}")

    def refresh_view(self):
        """Refresh the current view"""
        self.category_tree.refresh()
        self.element_table.refresh()
        self.quest_hierarchy_tree.refresh()
        self.property_editor.refresh()
        self.quest_details.update_quest_details()  # Refresh quest details if visible

    def on_data_loaded(self):
        """Called when data is loaded"""
        self.category_tree.populate()
        self.update_status()
        self.statusBar.showMessage("Data loaded successfully", 3000)

    def on_data_modified(self):
        """Called when data is modified"""
        self.update_status()

    def on_category_changed(self, category):
        """Called when category changes"""
        # Show/hide quest details panel and quest hierarchy tree based on category
        if category == "quests":
            # Hide element table, show quest hierarchy tree
            self.element_table.hide()
            self.quest_hierarchy_tree.show()
            self.quest_hierarchy_tree.load_quests()

            # Show quest details panel
            self.quest_details.show()
            # Adjust splitter sizes to accommodate 4th panel
            self.adjust_splitter_for_quests()
        else:
            # Show element table, hide quest hierarchy tree
            self.element_table.show()
            self.quest_hierarchy_tree.hide()

            # Hide quest details panel
            self.quest_details.hide()
            # Reset to 3-panel layout
            self.adjust_splitter_for_normal()

    def on_language_changed(self, language):
        """Called when language changes"""
        # Refresh all views to show text in new language
        self.refresh_view()

    def on_element_selected(self, category, element_index):
        """Called when an element is selected in any view"""
        if category == "quests":
            # Update quest details with selected quest
            self.quest_details.on_element_selected(category, element_index)
            self.logger.debug(f"Selected quest at index {element_index}")

    def adjust_splitter_for_quests(self):
        """Adjust splitter sizes when showing quest details"""
        # Find the splitter containing our widgets
        for child in self.findChildren(QSplitter):
            if self.category_tree in [child.widget(i) for i in range(child.count())]:
                # Set sizes: categories, elements, properties, quest details
                child.setSizes([200, 350, 300, 200])
                break

    def adjust_splitter_for_normal(self):
        """Adjust splitter sizes for normal 3-panel layout"""
        # Find the splitter containing our widgets
        for child in self.findChildren(QSplitter):
            if self.category_tree in [child.widget(i) for i in range(child.count())]:
                # Set sizes: categories, elements, properties (hide quest details)
                child.setSizes([250, 400, 400, 0])
                break

    def update_status(self):
        """Update status bar"""
        if self.data_model.file_path:
            self.file_label.setText(f"File: {self.data_model.file_path}")
        else:
            self.file_label.setText("No file loaded")

        if self.data_model.is_modified():
            self.modified_label.setText("Modified")
            self.modified_label.setStyleSheet("color: orange;")
        else:
            self.modified_label.setText("")

        # Show category stats
        if self.data_model.current_category:
            elements = self.data_model.get_elements(self.data_model.current_category)
            self.stats_label.setText(f"{len(elements)} entries")
        else:
            self.stats_label.setText("")

    def show_quest_editor(self):
        """Show the integrated quest editor in a separate window"""
        try:
            from .widgets.quest_editor import QuestEditorWidget

            # Create a new window for the quest editor
            if (
                not hasattr(self, "quest_editor_window")
                or not self.quest_editor_window.isVisible()
            ):
                from PySide6.QtWidgets import QDialog

                self.quest_editor_window = QDialog(self)
                self.quest_editor_window.setWindowTitle("Quest Editor")
                self.quest_editor_window.setMinimumSize(1000, 700)

                # Create layout for the dialog
                from PySide6.QtWidgets import QVBoxLayout

                layout = QVBoxLayout(self.quest_editor_window)
                layout.setContentsMargins(0, 0, 0, 0)

                # Create and add the quest editor widget
                quest_editor_widget = QuestEditorWidget(self.data_model)
                layout.addWidget(quest_editor_widget)

                self.quest_editor_window.setLayout(layout)

            # Show the quest editor window
            self.quest_editor_window.show()
            self.quest_editor_window.raise_()
            self.quest_editor_window.activateWindow()

        except Exception as e:
            QMessageBox.critical(
                self, "Quest Editor Error", f"Failed to open Quest Editor:\n{str(e)}"
            )

    def load_lua_quest_directory(self):
        """Load Lua quest scripts directory for objectives and rewards"""
        from pathlib import Path

        from PySide6.QtWidgets import QFileDialog, QMessageBox

        # Suggest the default Original Scripts path if it exists
        default_path = (
            Path(__file__).parent.parent.parent.parent
            / "OriginalGameFiles"
            / "modding"
            / "Original Scripts"
            / "script"
        )

        if not default_path.exists():
            default_path = str(Path.home())
        else:
            default_path = str(default_path)

        # Open directory selection dialog
        lua_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Lua Quest Scripts Directory",
            default_path,
            QFileDialog.Option.ShowDirsOnly,
        )

        if not lua_dir:
            return  # User cancelled

        # Set the directory in data model
        if not self.data_model.set_lua_quest_directory(lua_dir):
            QMessageBox.warning(
                self,
                "Invalid Directory",
                f"The selected directory could not be accessed:\n{lua_dir}",
            )
            return

        # Load quest data with progress feedback
        try:
            self.statusBar.showMessage("Parsing Lua quest scripts...")
            QApplication.processEvents()  # Update UI

            quest_count = self.data_model.load_lua_quest_data(force_refresh=False)

            if quest_count > 0:
                QMessageBox.information(
                    self,
                    "Lua Quest Data Loaded",
                    f"Successfully loaded quest data from {quest_count} quest(s).\n\n"
                    f"Quest objectives, requirements, and rewards from Lua scripts\n"
                    f"are now available in the Quest Editor.",
                )
                self.statusBar.showMessage(
                    f"Loaded Lua data for {quest_count} quests", 5000
                )
            else:
                QMessageBox.information(
                    self,
                    "No Quest Data Found",
                    "No quest data was found in the selected directory.\n\n"
                    "Make sure you selected the correct 'script' directory containing\n"
                    "Lua quest files (e.g., P1, P2, P3... subdirectories).",
                )
                self.statusBar.showMessage("No Lua quest data found", 5000)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading Lua Scripts",
                f"Failed to load Lua quest scripts:\n{str(e)}",
            )
            self.statusBar.showMessage("Error loading Lua quest data", 5000)

    def show_spell_wizard(self):
        """Show the Spell Creation Wizard"""
        try:
            from .widgets.spell_creator_wizard import SpellCreatorWizard

            # Create and show the spell wizard
            wizard = SpellCreatorWizard(self)

            # Connect to spell creation signal
            wizard.spellCreated.connect(self.on_spell_created)

            # Show the wizard
            wizard.exec()

        except Exception as e:
            QMessageBox.critical(
                self, "Spell Wizard Error", f"Failed to open Spell Wizard:\n{str(e)}"
            )

    def on_spell_created(self, spell_data):
        """Handle spell creation completion"""
        QMessageBox.information(
            self,
            "Spell Created",
            f"Spell '{spell_data.spell_name}' has been created!\n\n"
            f"Check the 'exported_spells' folder for the generated Lua files.",
        )

    def show_armor_forge(self):
        """Show the armor forge wizard"""
        try:
            from .shared.id_manager import IDManager
            from .widgets.armor_forge_wizard import ArmorForgeWizard

            # Initialize ID manager if not already done
            if not hasattr(self, "id_manager"):
                self.id_manager = IDManager()

            # Create and show the armor forge wizard
            wizard = ArmorForgeWizard(self.id_manager, self)
            result = wizard.exec()

            if result == wizard.Accepted:
                QMessageBox.information(
                    self,
                    "Success",
                    "Armor created successfully!\n\n"
                    "The armor has been saved and is ready for use in-game.",
                )

        except ImportError as e:
            QMessageBox.warning(
                self, "Import Error", f"Failed to load armor forge: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred while creating armor: {str(e)}"
            )

    def show_id_manager(self):
        """Show the ID manager widget"""
        try:
            from .shared.id_manager import IDManager
            from .shared.id_manager_widget import IDManagerWidget

            # Initialize ID manager if not already done
            if not hasattr(self, "id_manager"):
                self.id_manager = IDManager()

            # Create and show the ID manager dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("ID Management System")
            dialog.resize(600, 400)

            layout = QVBoxLayout()
            id_widget = IDManagerWidget(self.id_manager)
            layout.addWidget(id_widget)

            # Add close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)

            dialog.setLayout(layout)
            dialog.exec()

        except ImportError as e:
            QMessageBox.warning(
                self, "Import Error", f"Failed to load ID manager: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred in ID manager: {str(e)}"
            )

    def show_weapon_forge(self):
        """Show the weapon forge wizard"""
        try:
            from .shared.id_manager import IDManager
            from .widgets.weapon_forge_wizard import WeaponForgeWizard

            # Initialize ID manager if not already done
            if not hasattr(self, "id_manager"):
                self.id_manager = IDManager()

            # Create and show the weapon forge wizard
            wizard = WeaponForgeWizard(self.id_manager, self)
            result = wizard.exec()

            if result == wizard.Accepted:
                QMessageBox.information(
                    self,
                    "Success",
                    "Weapon created successfully!\n\n"
                    "The weapon has been saved and is ready for use in-game.",
                )

        except ImportError as e:
            QMessageBox.warning(
                self, "Import Error", f"Failed to load weapon forge: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred while creating weapon: {str(e)}"
            )

    def show_building_wizard(self):
        """Show the building wizard"""
        try:
            from .shared.id_manager import IDManager

            wizard = BuildingWizard(self)
            result = wizard.exec()

            if result == wizard.Accepted:
                QMessageBox.information(
                    self,
                    "Success",
                    "Building created successfully!",
                )
        except ImportError as e:
            QMessageBox.warning(
                self, "Import Error", f"Failed to load building: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred while creating building: {str(e)}"
            )

    def show_race_creator(self):
        """Show the Race Creator wizard"""
        try:
            from .shared.id_manager import IDManager
            from .widgets.race_creator_wizard import RaceCreatorWizard

            # Initialize ID manager if not already done
            if not hasattr(self, "id_manager"):
                self.id_manager = IDManager()

            # Create and show the race creator wizard
            wizard = RaceCreatorWizard(self.id_manager, self)
            result = wizard.exec()

            if result == wizard.Accepted and hasattr(wizard, "race_data"):
                QMessageBox.information(
                    self,
                    "Success",
                    f"Race '{wizard.race_data.race_name}' created successfully!\n\n"
                    "The race data has been collected and is ready for export.",
                )

        except ImportError as e:
            QMessageBox.warning(
                self, "Import Error", f"Failed to load race creator: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred while creating race: {str(e)}"
            )

    def show_npc_creator(self):
        """Show the NPC Creator wizard"""
        try:
            from .shared.id_manager import IDManager
            from .widgets.npc_creator_wizard import NpcCreatorWizard

            # Initialize ID manager if not already done
            if not hasattr(self, "id_manager"):
                self.id_manager = IDManager()

            # Create and show the NPC creator wizard
            wizard = NpcCreatorWizard(self.id_manager, self)
            result = wizard.exec()

            if result == QDialog.Accepted and hasattr(wizard, "npc_data"):
                QMessageBox.information(
                    self,
                    "Success",
                    f"NPC '{wizard.npc_data.name}' created successfully!\n\n"
                    "The NPC data has been collected and is ready for export.",
                )

        except ImportError as e:
            QMessageBox.warning(
                self, "Import Error", f"Failed to load NPC wizard: {str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"An error occurred while creating NPC: {str(e)}"
            )

    def show_main_interface(self):
        """Show the main interface with category tree, element table, etc."""
        if hasattr(self, "original_central_widget"):
            self.setCentralWidget(self.original_central_widget)

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About CFF Editor",
            "<h3>SpellForce GameData.cff Editor</h3>"
            "<p>Version 1.0.0</p>"
            "<p>A modern GUI editor for SpellForce Platinum Edition game data files.</p>"
            "<p>Built with PySide6 and the tirganach library.</p>",
        )

    def closeEvent(self, event):
        """Handle window close event"""
        if self.data_model.is_modified():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )

            if reply == QMessageBox.Save:
                self.save_file()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
