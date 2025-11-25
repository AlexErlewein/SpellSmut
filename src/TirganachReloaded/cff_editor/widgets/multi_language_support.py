#!/usr/bin/env python3
"""
Multi-Language Support System

Provides comprehensive internationalization (i18n) and localization (l10n) support
for quest editor, including translation management, language switching, and
localized resource handling.
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QTabWidget,
    QTextEdit, QScrollArea, QFrame, QToolButton, QMenu, QDialog,
    QDialogButtonBox, QFormLayout, QSpinBox, QSlider, QProgressBar,
    QMessageBox, QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem,
    QApplication, QFileDialog, QProgressDialog
)
from PySide6.QtCore import (
    Qt, Signal, pyqtSignal, QThread, QTimer, QSortFilterProxyModel,
    QAbstractListModel, QModelIndex, QItemSelectionModel, QRectF,
    QLocale, QTranslator, QLibraryInfo, QStandardPaths
)
from PySide6.QtGui import (
    QFont, QIcon, QPixmap, QPainter, QColor, QPalette, QMouseEvent,
    QHelpEvent, QKeyEvent, QBrush, QLinearGradient, QRadialGradient,
    QTextDocument, QTextCursor, QTextCharFormat
)

try:
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    GERMAN = "de"
    FRENCH = "fr"
    SPANISH = "es"
    ITALIAN = "it"
    POLISH = "pl"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    PORTUGUESE = "pt"


class TranslationEntry:
    """Represents a single translation entry"""

    def __init__(self, key: str, text: str, context: str = "", comment: str = ""):
        self.key = key
        self.text = text
        self.context = context
        self.comment = comment
        self.needs_review = False
        self.last_modified = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "key": self.key,
            "text": self.text,
            "context": self.context,
            "comment": self.comment,
            "needs_review": self.needs_review,
            "last_modified": self.last_modified
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TranslationEntry':
        """Create from dictionary"""
        entry = cls(
            data.get("key", ""),
            data.get("text", ""),
            data.get("context", ""),
            data.get("comment", "")
        )
        entry.needs_review = data.get("needs_review", False)
        entry.last_modified = data.get("last_modified", "")
        return entry


class TranslationFile:
    """Represents a translation file for a specific language"""

    def __init__(self, language: Language, file_path: str = ""):
        self.language = language
        self.file_path = file_path
        self.entries = {}
        self.metadata = {}
        self.loaded = False

    def load(self) -> bool:
        """Load translation file"""
        if not self.file_path or not os.path.exists(self.file_path):
            logger.warning(f"Translation file not found: {self.file_path}")
            return False

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load metadata
            self.metadata = data.get("metadata", {})

            # Load entries
            entries_data = data.get("translations", {})
            for key, entry_data in entries_data.items():
                if isinstance(entry_data, str):
                    # Simple string format
                    self.entries[key] = TranslationEntry(key, entry_data)
                else:
                    # Object format with context
                    self.entries[key] = TranslationEntry.from_dict(entry_data)

            self.loaded = True
            logger.info(f"Loaded {len(self.entries)} translations for {self.language.value}")
            return True

        except Exception as e:
            logger.error(f"Error loading translation file {self.file_path}: {e}")
            return False

    def save(self) -> bool:
        """Save translation file"""
        if not self.file_path:
            logger.error("No file path specified for translation file")
            return False

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

            # Prepare data
            data = {
                "metadata": self.metadata,
                "language": self.language.value,
                "translations": {
                    key: entry.to_dict() if hasattr(entry, 'to_dict') else entry
                    for key, entry in self.entries.items()
                }
            }

            # Write file
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(self.entries)} translations for {self.language.value}")
            return True

        except Exception as e:
            logger.error(f"Error saving translation file {self.file_path}: {e}")
            return False

    def add_entry(self, key: str, text: str, context: str = "", comment: str = ""):
        """Add or update a translation entry"""
        if key in self.entries:
            entry = self.entries[key]
            entry.text = text
            entry.context = context
            entry.comment = comment
            entry.last_modified = self.get_current_timestamp()
        else:
            self.entries[key] = TranslationEntry(key, text, context, comment)

    def get_translation(self, key: str, default: str = None) -> str:
        """Get translation for a key"""
        entry = self.entries.get(key)
        return entry.text if entry else (default or key)

    def get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def update_metadata(self, **kwargs):
        """Update metadata"""
        self.metadata.update(kwargs)

    def get_statistics(self) -> dict:
        """Get translation statistics"""
        total_entries = len(self.entries)
        reviewed_entries = sum(1 for entry in self.entries.values() if not entry.needs_review)
        pending_review = total_entries - reviewed_entries

        return {
            "total_entries": total_entries,
            "reviewed_entries": reviewed_entries,
            "pending_review": pending_review,
            "completion_percentage": (reviewed_entries / total_entries * 100) if total_entries > 0 else 0
        }


@dataclass
class LanguageInfo:
    """Information about a supported language"""
    code: str
    name: str
    native_name: str
    direction: str = "ltr"  # Left-to-right or Right-to-left
    flag_emoji: str = ""
    date_format: str = "MM/DD/YYYY"
    time_format: str = "HH:mm"


class TranslationManager:
    """Main translation manager for the application"""

    def __init__(self, base_directory: str = "translations"):
        self.base_directory = base_directory
        self.current_language = Language.ENGLISH
        self.translations = {}
        self.fallback_language = Language.ENGLISH

        # Initialize language info
        self.language_info = {
            Language.ENGLISH: LanguageInfo(
                code="en",
                name="English",
                native_name="English",
                direction="ltr",
                flag_emoji="🇺🇸",
                date_format="MM/DD/YYYY",
                time_format="HH:mm"
            ),
            Language.GERMAN: LanguageInfo(
                code="de",
                name="German",
                native_name="Deutsch",
                direction="ltr",
                flag_emoji="🇩🇪",
                date_format="DD.MM.YYYY",
                time_format="HH:mm"
            ),
            Language.FRENCH: LanguageInfo(
                code="fr",
                name="French",
                native_name="Français",
                direction="ltr",
                flag_emoji="🇫🇷",
                date_format="DD/MM/YYYY",
                time_format="HH:mm"
            ),
            Language.SPANISH: LanguageInfo(
                code="es",
                name="Spanish",
                native_name="Español",
                direction="ltr",
                flag_emoji="🇪🇸",
                date_format="DD/MM/YYYY",
                time_format="HH:mm"
            ),
            Language.CHINESE: LanguageInfo(
                code="zh",
                name="Chinese",
                native_name="中文",
                direction="ltr",
                flag_emoji="🇨🇳",
                date_format="YYYY年MM月DD日",
                time_format="HH:mm"
            ),
            Language.JAPANESE: LanguageInfo(
                code="ja",
                name="Japanese",
                native_name="日本語",
                direction="ltr",
                flag_emoji="🇯🇵",
                date_format="YYYY年MM月DD日",
                time_format="HH:mm"
            )
        }

    def initialize(self):
        """Initialize the translation manager"""
        self.create_base_translations()
        self.load_all_translations()
        self.set_language(self.current_language)

    def create_base_translations(self):
        """Create base translation files"""
        base_translations = {
            "ui": {
                "file": "File",
                "edit": "Edit",
                "view": "View",
                "help": "Help",
                "tools": "Tools",
                "window": "Window",
                "dialog": "Dialog",
                "quest": "Quest",
                "dialogue": "Dialogue",
                "npc": "NPC",
                "item": "Item",
                "location": "Location",
                "condition": "Condition",
                "action": "Action",
                "reward": "Reward"
            },
            "quest": {
                "title": "Quest Editor",
                "create_quest": "Create Quest",
                "load_quest": "Load Quest",
                "save_quest": "Save Quest",
                "export_lua": "Export LUA",
                "validate": "Validate",
                "test": "Test",
                "preview": "Preview",
                "quest_info": "Quest Information",
                "dialogue_editor": "Dialogue Editor",
                "conditions": "Conditions",
                "actions": "Actions",
                "rewards": "Rewards",
                "variables": "Variables"
            },
            "dialogue": {
                "start_node": "Start Node",
                "npc_dialogue": "NPC Dialogue",
                "player_choice": "Player Choice",
                "end_node": "End Node",
                "add_node": "Add Node",
                "delete_node": "Delete Node",
                "edit_node": "Edit Node",
                "connect_nodes": "Connect Nodes",
                "validate": "Validate Dialogue",
                "export": "Export",
                "import": "Import"
            },
            "validation": {
                "errors_found": "Errors Found",
                "warnings_found": "Warnings Found",
                "validation_complete": "Validation Complete",
                "no_issues": "No validation issues found",
                "auto_fix_available": "Auto-fix available"
            },
            "npc_browser": {
                "title": "NPC Browser",
                "search_npcs": "Search NPCs",
                "add_to_dialogue": "Add to Dialogue",
                "npc_details": "NPC Details",
                "personality": "Personality",
                "dialogue_topics": "Dialogue Topics",
                "known_items": "Known Items",
                "available_hours": "Available Hours"
            }
        }

        # Create base translation file for each language
        for lang in Language:
            if lang != Language.ENGLISH:  # English is created from the base
                file_path = os.path.join(self.base_directory, f"{lang.value}.json")
                translation_file = TranslationFile(lang, file_path)

                # Initialize with structure
                translation_file.update_metadata(
                    language=lang.value,
                    version="1.0",
                    created=self.get_current_timestamp(),
                    last_modified=self.get_current_timestamp()
                )

                # Add structure entries
                for category, entries in base_translations.items():
                    for key, value in entries.items():
                        translation_file.add_entry(f"{category}.{key}", value)

                translation_file.save()

        # Create English translation file
        english_file = TranslationFile(Language.ENGLISH,
                                         os.path.join(self.base_directory, "en.json"))
        english_file.update_metadata(
            language="en",
            version="1.0",
            created=self.get_current_timestamp(),
            last_modified=self.get_current_timestamp()
        )

        for category, entries in base_translations.items():
            for key, value in entries.items():
                english_file.add_entry(f"{category}.{key}", value)

        english_file.save()

    def load_all_translations(self):
        """Load all translation files"""
        for lang in Language:
            file_path = os.path.join(self.base_directory, f"{lang.value}.json")
            translation_file = TranslationFile(lang, file_path)

            if translation_file.load():
                self.translations[lang] = translation_file
                logger.info(f"Loaded translations for {lang.value}")
            else:
                logger.warning(f"Could not load translations for {lang.value}")

    def set_language(self, language: Language):
        """Set the current language"""
        self.current_language = language
        logger.info(f"Switched to language: {language.value}")

    def get_translation(self, key: str, language: Language = None, default: str = None) -> str:
        """Get translation for a key"""
        target_language = language if language else self.current_language
        fallback_lang = self.fallback_language

        # Try target language first
        if target_language in self.translations:
            translation = self.translations[target_language].get_translation(key, None)
            if translation:
                return translation

        # Try fallback language
        if fallback_lang in self.translations:
            translation = self.translations[fallback_lang].get_translation(key, None)
            if translation:
                return translation

        # Return default or key
        return default if default is not None else key

    def translate(self, key: str, context: str = "", variables: Dict[str, str] = None) -> str:
        """Get translated text with context and variable substitution"""
        translation = self.get_translation(key)

        # Format with variables if provided
        if variables:
            try:
                translation = translation.format(**variables)
            except (KeyError, ValueError) as e:
                logger.warning(f"Variable substitution failed for key '{key}': {e}")
                return translation

        return translation

    def get_language_info(self, language: Language = None) -> Optional[LanguageInfo]:
        """Get language information"""
        target_language = language if language else self.current_language
        return self.language_info.get(target_language)

    def get_supported_languages(self) -> List[LanguageInfo]:
        """Get list of supported languages"""
        return list(self.language_info.values())

    def export_translations(self, output_dir: str = None) -> bool:
        """Export all translations to output directory"""
        if not output_dir:
            output_dir = self.base_directory

        try:
            os.makedirs(output_dir, exist_ok=True)

            # Export each language translation
            for lang, translation_file in self.translations.items():
                output_path = os.path.join(output_dir, f"{lang.value}_export.json")

                # Copy to new location
                import shutil
                shutil.copy2(translation_file.file_path, output_path)

            logger.info(f"Exported {len(self.translations)} translation files to {output_dir}")
            return True

        except Exception as e:
            logger.error(f"Error exporting translations: {e}")
            return False

    def import_translations(self, input_dir: str = None) -> bool:
        """Import translations from input directory"""
        if not input_dir:
            input_dir = self.base_directory

        try:
            for lang in Language:
                input_path = os.path.join(input_dir, f"{lang.value}_export.json")
                if os.path.exists(input_path):
                    # Load from exported file
                    temp_file = TranslationFile(lang, "")

                    with open(input_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Convert to regular format
                    if "translations" in data:
                        for key, entry_data in data["translations"].items():
                            if isinstance(entry_data, str):
                                temp_file.add_entry(key, entry_data)
                            else:
                                temp_file.add_entry(
                                    entry_data.get("key", ""),
                                    entry_data.get("text", ""),
                                    entry_data.get("context", ""),
                                    entry_data.get("comment", "")
                                )

                    # Save to regular location
                    regular_path = os.path.join(self.base_directory, f"{lang.value}.json")
                    temp_file.file_path = regular_path
                    temp_file.save()

                    if lang in self.translations:
                        self.translations[lang].load()

                    logger.info(f"Imported translations for {lang.value} from {input_path}")

            return True

        except Exception as e:
            logger.error(f"Error importing translations: {e}")
            return False

    def validate_translations(self) -> Dict[str, Any]:
        """Validate all translations and return statistics"""
        stats = {
            "total_languages": len(self.translations),
            "total_entries": 0,
            "total_reviewed": 0,
            "total_pending_review": 0,
            "languages": {}
        }

        for lang, translation_file in self.translations.items():
            lang_stats = translation_file.get_statistics()
            stats["languages"][lang.value] = lang_stats
            stats["total_entries"] += lang_stats["total_entries"]
            stats["total_reviewed"] += lang_stats["reviewed_entries"]
            stats["total_pending_review"] += lang_stats["pending_review"]

        return stats

    def get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


class TranslationEditorWidget(QWidget):
    """Widget for editing translations"""

    translation_updated = pyqtSignal(str, str)  # key, text

    def __init__(self, translation_manager: TranslationManager, parent=None):
        super().__init__(parent)
        self.translation_manager = translation_manager
        self.current_language = Language.ENGLISH
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Language selector
        language_group = QGroupBox("Language")
        language_layout = QHBoxLayout(language_group)

        language_layout.addWidget(QLabel("Current Language:"))

        self.language_combo = QComboBox()
        for lang_info in self.translation_manager.get_supported_languages():
            display_text = f"{lang_info.flag_emoji} {lang_info.name} ({lang_info.native_name})"
            self.language_combo.addItem(display_text, lang_info)

        self.language_combo.setCurrentIndex(0)
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        language_layout.addWidget(self.language_combo)
        language_layout.addStretch()

        layout.addWidget(language_group)

        # Translation editor
        editor_splitter = QSplitter(Qt.Vertical)

        # Translation keys tree
        keys_widget = QWidget()
        keys_layout = QVBoxLayout(keys_widget)

        keys_header = QHBoxLayout()
        keys_header.addWidget(QLabel("Translation Keys"))
        keys_search = QLineEdit()
        keys_search.setPlaceholderText("Search keys...")
        keys_search.textChanged.connect(self.on_search_keys)
        keys_header.addWidget(keys_search)
        keys_layout.addLayout(keys_header)

        self.keys_tree = QTreeWidget()
        self.keys_tree.setHeaderLabels(["Key", "Text", "Status"])
        self.keys_tree.itemSelectionChanged.connect(self.on_key_selected)
        keys_layout.addWidget(self.keys_tree)

        editor_splitter.addWidget(keys_widget)

        # Translation editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)

        # Current key display
        self.current_key_label = QLabel("No key selected")
        current_key_font = self.current_key_label.font()
        current_key_font.setBold(True)
        current_key_font.setPointSize(12)
        self.current_key_label.setFont(current_key_font)
        editor_layout.addWidget(self.current_key_label)

        # Translation text editor
        editor_layout.addWidget(QLabel("Translation:"))
        self.translation_edit = QTextEdit()
        self.translation_edit.textChanged.connect(self.on_translation_changed)
        editor_layout.addWidget(self.translation_edit)

        # Metadata
        metadata_group = QGroupBox("Metadata")
        metadata_form = QFormLayout(metadata_group)

        self.context_edit = QLineEdit()
        self.comment_edit = QLineEdit()
        self.needs_review_cb = QCheckBox("Needs Review")

        metadata_form.addRow("Context:", self.context_edit)
        metadata_form.addRow("Comment:", self.comment_edit)
        metadata_form.addRow(self.needs_review_cb)

        editor_layout.addWidget(metadata_group)

        # Save button
        self.save_btn = QPushButton("💾 Save Translation")
        self.save_btn.clicked.connect(self.save_current_translation)
        editor_layout.addWidget(self.save_btn)

        editor_layout.addStretch()
        editor_splitter.addWidget(editor_widget)

        editor_splitter.setSizes([300, 400])
        layout.addWidget(editor_splitter)

        # Load initial data
        self.load_keys_for_language(self.current_language)

    def on_language_changed(self, language_text: str):
        """Handle language change"""
        # Find selected language info
        for i in range(self.language_combo.count()):
            item_data = self.language_combo.itemData(i)
            if item_data and hasattr(item_data, 'code'):
                if item_data.code.value == self.current_language.value:
                    continue
                self.current_language = item_data.code

        # Load keys for new language
        self.load_keys_for_language(self.current_language)

        self.current_key_label.setText("No key selected")
        self.translation_edit.clear()

    def load_keys_for_language(self, language: Language):
        """Load translation keys for the specified language"""
        self.keys_tree.clear()

        if language in self.translation_manager.translations:
            translation_file = self.translation_manager.translations[language]

            # Group keys by category
            categories = {}
            for key, entry in translation_file.entries.items():
                if '.' in key:
                    category, subkey = key.split('.', 1)
                    if category not in categories:
                        categories[category] = {}
                    categories[category][subkey] = entry
                else:
                    if "uncategorized" not in categories:
                        categories["uncategorized"] = {}
                    categories["uncategorized"][key] = entry

            # Add to tree
            for category, subkeys in sorted(categories.items()):
                category_item = QTreeWidgetItem(self.keys_tree)
                category_item.setText(0, f"📁 {category}")
                category_item.setText(1, f"{len(subkeys)} entries")

                for subkey, entry in sorted(subkeys.items()):
                    item = QTreeWidgetItem(category_item)
                    item.setText(0, subkey)
                    item.setText(1, entry.text[:50] + "..." if len(entry.text) > 50 else entry.text)

                    # Status indicator
                    if entry.needs_review:
                        item.setText(2, "⚠️")
                    else:
                        item.setText(2, "✅")

                    item.setData(0, Qt.UserRole, entry)
                    item.setData(2, Qt.UserRole, entry.needs_review)

                category_item.setExpanded(True)

        self.keys_tree.expandAll()

    def on_search_keys(self, search_text: str):
        """Handle search in keys"""
        items = []
        for i in range(self.keys_tree.topLevelItemCount()):
            item = self.keys_tree.topLevelItem(i)
            items.append(item)

        if not search_text.strip():
            # Show all items
            for item in items:
                item.setHidden(False)
                item.setExpanded(True)
        else:
            # Filter items
            search_lower = search_text.lower()
            for item in items:
                self.filter_item(item, search_lower)

    def filter_item(self, item: QTreeWidgetItem, search_text: str):
        """Filter tree item recursively"""
        should_show = False
        has_visible_child = False

        # Check if current item matches
        key_text = item.text(0).lower()
        text_text = item.text(1).lower()

        if search_text in key_text or search_text in text_text:
            should_show = True

        # Check children
        for i in range(item.childCount()):
            child = item.child(i)
            if self.filter_item(child, search_text):
                has_visible_child = True

        # Set visibility and expansion
        item.setHidden(not (should_show or has_visible_child))
        item.setExpanded(has_visible_child)

        return should_show or has_visible_child

    def on_key_selected(self):
        """Handle key selection"""
        items = self.keys_tree.selectedItems()
        if items:
            item = items[0]
            entry = item.data(0, Qt.UserRole)
            if entry:
                self.current_key_label.setText(f"Key: {entry.key}")
                self.translation_edit.setPlainText(entry.text)
                self.context_edit.setText(entry.context)
                self.comment_edit.setText(entry.comment)
                self.needs_review_cb.setChecked(entry.needs_review)
            else:
                self.clear_editor()
        else:
            self.clear_editor()

    def on_translation_changed(self):
        """Handle translation text change"""
        items = self.keys_tree.selectedItems()
        if items:
            item = items[0]
            entry = item.data(0, Qt.UserRole)
            if entry:
                new_text = self.translation_edit.toPlainText()
                entry.text = new_text
                entry.last_modified = self.translation_manager.get_current_timestamp()

                # Update display
                item.setText(1, new_text[:50] + "..." if len(new_text) > 50 else new_text)
                item.setText(2, "✏️")  # Modified indicator

                self.translation_updated.emit(entry.key, new_text)

    def clear_editor(self):
        """Clear the editor"""
        self.current_key_label.setText("No key selected")
        self.translation_edit.clear()
        self.context_edit.clear()
        self.comment_edit.clear()
        self.needs_review_cb.setChecked(False)

    def save_current_translation(self):
        """Save the current translation"""
        items = self.keys_tree.selectedItems()
        if not items:
            return

        item = items[0]
        entry = item.data(0, Qt.UserRole)
        if entry:
            # Update entry
            entry.text = self.translation_edit.toPlainText()
            entry.context = self.context_edit.text()
            entry.comment = self.comment_edit.text()
            entry.needs_review = self.needs_review_cb.isChecked()
            entry.last_modified = self.translation_manager.get_current_timestamp()

            # Save translation file
            if self.current_language in self.translation_manager.translations:
                translation_file = self.translation_manager.translations[self.current_language]
                translation_file.save()
                logger.info(f"Saved translation for key '{entry.key}' in {self.current_language.value}")

                # Update status indicator
                if entry.needs_review:
                    item.setText(2, "⚠️")
                else:
                    item.setText(2, "✅")

                QMessageBox.information(self, "Translation Saved",
                                      f"Saved translation for '{entry.key}' in {self.current_language.value}")


class MultiLanguageManagerWidget(QWidget):
    """Main multi-language management widget"""

    language_changed = pyqtSignal(str)  # language code

    def __init__(self, translation_manager: TranslationManager, parent=None):
        super().__init__(parent)
        self.translation_manager = translation_manager
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Multi-Language Support")
        title_font = title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Translation editor tab
        self.translation_editor = TranslationEditorWidget(self.translation_manager)
        self.tab_widget.addTab(self.translation_editor, "📝 Editor")

        # Statistics tab
        self.statistics_widget = self.create_statistics_widget()
        self.tab_widget.addTab(self.statistics_widget, "📊 Statistics")

        # Import/Export tab
        self.import_export_widget = self.create_import_export_widget()
        self.tab_widget.addTab(self.import_export_widget, "📁 Import/Export")

        # Settings tab
        self.settings_widget = self.create_settings_widget()
        self.tab_widget.addTab(self.settings_widget, "⚙️ Settings")

        layout.addWidget(self.tab_widget)

    def create_statistics_widget(self) -> QWidget:
        """Create statistics widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Statistics display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Statistics")
        refresh_btn.clicked.connect(self.refresh_statistics)
        layout.addWidget(refresh_btn)

        layout.addStretch()

        # Initial statistics
        self.refresh_statistics()

        return widget

    def create_import_export_widget(self) -> QWidget:
        """Create import/export widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Import section
        import_group = QGroupBox("Import Translations")
        import_layout = QVBoxLayout(import_group)

        self.import_btn = QPushButton("📥 Import Translations")
        self.import_btn.clicked.connect(self.import_translations)
        import_layout.addWidget(self.import_btn)

        self.import_status_label = QLabel("No import operation performed")
        import_layout.addWidget(self.import_status_label)

        import_group.setLayout(import_layout)
        layout.addWidget(import_group)

        # Export section
        export_group = QGroupBox("Export Translations")
        export_layout = QVBoxLayout(export_group)

        self.export_btn = QPushButton("📤 Export Translations")
        self.export_btn.clicked.connect(self.export_translations)
        export_layout.addWidget(self.export_btn)

        self.export_status_label = QLabel("No export operation performed")
        export_layout.addWidget(self.export_status_label)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        layout.addStretch()

        return widget

    def create_settings_widget(self) -> QWidget:
        """Create settings widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Language settings
        language_group = QGroupBox("Language Settings")
        language_form = QFormLayout(language_group)

        # Fallback language
        self.fallback_combo = QComboBox()
        for lang_info in self.translation_manager.get_supported_languages():
            self.fallback_combo.addItem(
                f"{lang_info.flag_emoji} {lang_info.name} ({lang_info.native_name})",
                lang_info
            )
        language_form.addRow("Fallback Language:", self.fallback_combo)

        language_group.setLayout(language_form)
        layout.addWidget(language_group)

        # Auto-detect language
        auto_detect_group = QGroupBox("Auto-Detection")
        auto_detect_layout = QVBoxLayout(auto_detect_group)

        self.auto_detect_cb = QCheckBox("Auto-detect system language on startup")
        self.auto_detect_cb.setChecked(True)
        auto_detect_layout.addWidget(self.auto_detect_cb)

        auto_detect_group.setLayout(auto_detect_layout)
        layout.addWidget(auto_detect_group)

        # Validation settings
        validation_group = QGroupBox("Validation")
        validation_layout = QVBoxLayout(validation_group)

        self.validate_missing_cb = QCheckBox("Validate missing translations")
        self.validate_missing_cb.setChecked(True)
        validation_layout.addWidget(self.validate_missing_cb)

        self.validate_incomplete_cb = QCheckBox("Mark incomplete translations")
        validation_layout.addWidget(self.validate_incomplete_cb)

        validation_group.setLayout(validation_layout)
        layout.addWidget(validation_group)

        layout.addStretch()

        return widget

    def refresh_statistics(self):
        """Refresh statistics display"""
        stats = self.translation_manager.validate_translations()

        text = f"""
📊 Translation Statistics
{'='*80}

Total Languages: {total_languages}
Total Entries: {total_entries}
Reviewed Entries: {total_reviewed}
Pending Review: {total_pending_review}
Overall Completion: {completion_percentage:.1f}%

{'='*80}

Language Breakdown:
"""

        for lang_code, lang_stats in stats["languages"].items():
            lang_info = self.translation_manager.get_language_info(Language(lang_code))
            if lang_info:
                text += f"""
{lang_info.flag_emoji} {lang_info.name} ({lang_info.native_name})
  Total: {lang_stats["total_entries"]}
  Reviewed: {lang_stats["reviewed_entries"]}
  Pending: {lang_stats["pending_review"]}
  Completion: {lang_stats["completion_percentage"]:.1f}%
"""

        self.stats_text.setPlainText(text)

    def import_translations(self):
        """Import translations from directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Translation Directory",
                                                   os.path.expanduser("~/translations"))
        if directory:
            success = self.translation_manager.import_translations(directory)
            if success:
                self.import_status_label.setText(f"Successfully imported from {directory}")
                QMessageBox.information(self, "Import Successful",
                                      f"Translations imported successfully from {directory}")
                # Reload translation editor if needed
                if hasattr(self, 'translation_editor'):
                    self.translation_editor.load_keys_for_language(
                        self.translation_editor.current_language
                    )
            else:
                self.import_status_label.setText(f"Failed to import from {directory}")
                QMessageBox.warning(self, "Import Failed",
                                    f"Failed to import translations from {directory}")

    def export_translations(self):
        """Export translations to directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Export Directory",
                                                   os.path.expanduser("~/translations_export"))
        if directory:
            success = self.translation_manager.export_translations(directory)
            if success:
                self.export_status_label.setText(f"Successfully exported to {directory}")
                QMessageBox.information(self, "Export Successful",
                                      f"Translations exported successfully to {directory}")
            else:
                self.export_status_label.setText(f"Failed to export to {directory}")
                QMessageBox.warning(self, "Export Failed",
                                    f"Failed to export translations to {directory}")

    def set_language(self, language_code: str):
        """Set the current language"""
        try:
            language = Language(language_code)
            self.translation_manager.set_language(language)

            # Update language combo if it exists
            if hasattr(self, 'fallback_combo'):
                for i in range(self.fallback_combo.count()):
                    item_data = self.fallback_combo.itemData(i)
                    if hasattr(item_data, 'code') and item_data.code == language:
                        self.fallback_combo.setCurrentIndex(i)
                        break

            # Emit signal
            self.language_changed.emit(language_code)

        except ValueError:
            logger.error(f"Invalid language code: {language_code}")


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create translation manager
    base_dir = os.path.join(os.path.dirname(__file__), "translations")
    translation_manager = TranslationManager(base_dir)
    translation_manager.initialize()

    # Create and show multi-language manager
    manager_widget = MultiLanguageManagerWidget(translation_manager)
    manager_widget.resize(800, 600)
    manager_widget.setWindowTitle("Multi-Language Support Manager")
    manager_widget.show()

    # Test signals
    def on_language_changed(language_code: str):
        print(f"Language changed to: {language_code}")

    manager_widget.language_changed.connect(on_language_changed)

    sys.exit(app.exec())