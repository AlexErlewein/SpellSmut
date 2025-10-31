"""
Theme Manager for CFF Editor
Provides multiple dark theme options with different accent colors
"""

from enum import Enum
from typing import Dict

from PySide6.QtCore import QObject, Signal


class ThemeType(Enum):
    """Available theme types"""

    DEFAULT = "Default Dark"
    DARCULA = "Darcula"
    JETBRAINS = "JetBrains"
    FOREST = "Forest Dark"
    PURPLE_NIGHT = "Purple Night"
    SUNSET = "Sunset Dark"


class ThemeManager(QObject):
    """Manages application themes"""

    theme_changed = Signal(str)  # Signal emitted when theme changes

    def __init__(self):
        super().__init__()
        self._current_theme = ThemeType.DEFAULT
        self._themes = self._create_themes()

    def _create_themes(self) -> Dict[ThemeType, str]:
        """Create all available themes"""
        return {
            ThemeType.DEFAULT: self._create_default_theme(),
            ThemeType.DARCULA: self._create_darcula_theme(),
            ThemeType.JETBRAINS: self._create_jetbrains_theme(),
            ThemeType.FOREST: self._create_forest_theme(),
            ThemeType.PURPLE_NIGHT: self._create_purple_night_theme(),
            ThemeType.SUNSET: self._create_sunset_theme(),
        }

    def _create_default_theme(self) -> str:
        """Default dark theme (current implementation)"""
        return """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QTreeWidget {
            background-color: #353535;
            border: 1px solid #555555;
            alternate-background-color: #3a3a3a;
        }
        QTreeWidget::item:selected {
            background-color: #0d47a1;
        }
        QTreeWidget::item:hover {
            background-color: #404040;
        }
        QTableWidget {
            background-color: #353535;
            border: 1px solid #555555;
            gridline-color: #555555;
            alternate-background-color: #3a3a3a;
        }
        QTableWidget::item:selected {
            background-color: #0d47a1;
        }
        QHeaderView::section {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 4px;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #353535;
            border: 1px solid #555555;
            padding: 4px;
            color: #ffffff;
        }
        QPushButton {
            background-color: #0d47a1;
            border: none;
            padding: 6px 12px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #1565c0;
        }
        QPushButton:disabled {
            background-color: #555555;
            color: #888888;
        }
        QMenuBar {
            background-color: #353535;
            color: #ffffff;
        }
        QMenuBar::item:selected {
            background-color: #0d47a1;
        }
        QMenu {
            background-color: #353535;
            color: #ffffff;
            border: 1px solid #555555;
        }
        QMenu::item:selected {
            background-color: #0d47a1;
        }
        QStatusBar {
            background-color: #353535;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
        }
        """

    def _create_darcula_theme(self) -> str:
        """Darcula-inspired theme with blue accents"""
        return """
        QMainWindow {
            background-color: #3c3f41;
            color: #bbbbbb;
        }
        QWidget {
            background-color: #3c3f41;
            color: #bbbbbb;
        }
        QTreeWidget {
            background-color: #43494a;
            border: 1px solid #646464;
            alternate-background-color: #45494a;
            selection-background-color: #365880;
        }
        QTreeWidget::item:selected {
            background-color: #365880;
            color: #ffffff;
        }
        QTreeWidget::item:hover {
            background-color: #4e5052;
        }
        QTableWidget {
            background-color: #43494a;
            border: 1px solid #646464;
            gridline-color: #646464;
            alternate-background-color: #45494a;
            selection-background-color: #365880;
        }
        QTableWidget::item:selected {
            background-color: #365880;
            color: #ffffff;
        }
        QHeaderView::section {
            background-color: #4e5052;
            color: #bbbbbb;
            border: 1px solid #646464;
            padding: 4px;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #45494a;
            border: 1px solid #646464;
            padding: 4px;
            color: #bbbbbb;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border: 1px solid #6a9ed5;
        }
        QPushButton {
            background-color: #365880;
            border: none;
            padding: 6px 12px;
            color: #ffffff;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #436a9e;
        }
        QPushButton:pressed {
            background-color: #2c4666;
        }
        QPushButton:disabled {
            background-color: #646464;
            color: #888888;
        }
        QMenuBar {
            background-color: #3c3f41;
            color: #bbbbbb;
            border-bottom: 1px solid #646464;
        }
        QMenuBar::item:selected {
            background-color: #365880;
        }
        QMenu {
            background-color: #3c3f41;
            color: #bbbbbb;
            border: 1px solid #646464;
        }
        QMenu::item:selected {
            background-color: #365880;
        }
        QStatusBar {
            background-color: #3c3f41;
            color: #bbbbbb;
            border-top: 1px solid #646464;
        }
        QLabel {
            color: #bbbbbb;
        }
        QTabWidget::pane {
            border: 1px solid #646464;
            background-color: #43494a;
        }
        QTabBar::tab {
            background-color: #3c3f41;
            color: #bbbbbb;
            border: 1px solid #646464;
            padding: 6px 12px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #43494a;
            border-bottom: 1px solid #43494a;
        }
        QTabBar::tab:hover {
            background-color: #4e5052;
        }
        """

    def _create_jetbrains_theme(self) -> str:
        """JetBrains-inspired theme with orange accents"""
        return """
        QMainWindow {
            background-color: #2b2b2b;
            color: #a9b7c6;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #a9b7c6;
        }
        QTreeWidget {
            background-color: #313335;
            border: 1px solid #5a5a5a;
            alternate-background-color: #323232;
            selection-background-color: #42516f;
        }
        QTreeWidget::item:selected {
            background-color: #42516f;
            color: #ffffff;
        }
        QTreeWidget::item:hover {
            background-color: #3c3f41;
        }
        QTableWidget {
            background-color: #313335;
            border: 1px solid #5a5a5a;
            gridline-color: #5a5a5a;
            alternate-background-color: #323232;
            selection-background-color: #42516f;
        }
        QTableWidget::item:selected {
            background-color: #42516f;
            color: #ffffff;
        }
        QHeaderView::section {
            background-color: #3c3f41;
            color: #a9b7c6;
            border: 1px solid #5a5a5a;
            padding: 4px;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #323232;
            border: 1px solid #5a5a5a;
            padding: 4px;
            color: #a9b7c6;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border: 1px solid #ff922b;
        }
        QPushButton {
            background-color: #ff922b;
            border: none;
            padding: 6px 12px;
            color: #ffffff;
            border-radius: 3px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #ffa726;
        }
        QPushButton:pressed {
            background-color: #fb8c00;
        }
        QPushButton:disabled {
            background-color: #5a5a5a;
            color: #888888;
        }
        QMenuBar {
            background-color: #2b2b2b;
            color: #a9b7c6;
            border-bottom: 1px solid #5a5a5a;
        }
        QMenuBar::item:selected {
            background-color: #42516f;
        }
        QMenu {
            background-color: #2b2b2b;
            color: #a9b7c6;
            border: 1px solid #5a5a5a;
        }
        QMenu::item:selected {
            background-color: #42516f;
        }
        QStatusBar {
            background-color: #2b2b2b;
            color: #a9b7c6;
            border-top: 1px solid #5a5a5a;
        }
        QLabel {
            color: #a9b7c6;
        }
        QTabWidget::pane {
            border: 1px solid #5a5a5a;
            background-color: #313335;
        }
        QTabBar::tab {
            background-color: #2b2b2b;
            color: #a9b7c6;
            border: 1px solid #5a5a5a;
            padding: 6px 12px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #313335;
            border-bottom: 1px solid #313335;
        }
        QTabBar::tab:hover {
            background-color: #3c3f41;
        }
        """

    def _create_forest_theme(self) -> str:
        """Forest dark theme with green accents"""
        return """
        QMainWindow {
            background-color: #1e1e1e;
            color: #d4d4d4;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #d4d4d4;
        }
        QTreeWidget {
            background-color: #252526;
            border: 1px solid #3e3e42;
            alternate-background-color: #2d2d30;
            selection-background-color: #0e6c5c;
        }
        QTreeWidget::item:selected {
            background-color: #0e6c5c;
            color: #ffffff;
        }
        QTreeWidget::item:hover {
            background-color: #2a2d2e;
        }
        QTableWidget {
            background-color: #252526;
            border: 1px solid #3e3e42;
            gridline-color: #3e3e42;
            alternate-background-color: #2d2d30;
            selection-background-color: #0e6c5c;
        }
        QTableWidget::item:selected {
            background-color: #0e6c5c;
            color: #ffffff;
        }
        QHeaderView::section {
            background-color: #2d2d30;
            color: #d4d4d4;
            border: 1px solid #3e3e42;
            padding: 4px;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #3c3c3c;
            border: 1px solid #3e3e42;
            padding: 4px;
            color: #d4d4d4;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border: 1px solid #4ec9b0;
        }
        QPushButton {
            background-color: #0e6c5c;
            border: none;
            padding: 6px 12px;
            color: #ffffff;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #117a65;
        }
        QPushButton:pressed {
            background-color: #0d5d4f;
        }
        QPushButton:disabled {
            background-color: #3e3e42;
            color: #888888;
        }
        QMenuBar {
            background-color: #1e1e1e;
            color: #d4d4d4;
            border-bottom: 1px solid #3e3e42;
        }
        QMenuBar::item:selected {
            background-color: #0e6c5c;
        }
        QMenu {
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: 1px solid #3e3e42;
        }
        QMenu::item:selected {
            background-color: #0e6c5c;
        }
        QStatusBar {
            background-color: #1e1e1e;
            color: #d4d4d4;
            border-top: 1px solid #3e3e42;
        }
        QLabel {
            color: #d4d4d4;
        }
        QTabWidget::pane {
            border: 1px solid #3e3e42;
            background-color: #252526;
        }
        QTabBar::tab {
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: 1px solid #3e3e42;
            padding: 6px 12px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #252526;
            border-bottom: 1px solid #252526;
        }
        QTabBar::tab:hover {
            background-color: #2a2d2e;
        }
        """

    def _create_purple_night_theme(self) -> str:
        """Purple night theme with purple accents"""
        return """
        QMainWindow {
            background-color: #1a1a1a;
            color: #e0e0e0;
        }
        QWidget {
            background-color: #1a1a1a;
            color: #e0e0e0;
        }
        QTreeWidget {
            background-color: #242424;
            border: 1px solid #4a4a4a;
            alternate-background-color: #2d2d2d;
            selection-background-color: #6a1b9a;
        }
        QTreeWidget::item:selected {
            background-color: #6a1b9a;
            color: #ffffff;
        }
        QTreeWidget::item:hover {
            background-color: #303030;
        }
        QTableWidget {
            background-color: #242424;
            border: 1px solid #4a4a4a;
            gridline-color: #4a4a4a;
            alternate-background-color: #2d2d2d;
            selection-background-color: #6a1b9a;
        }
        QTableWidget::item:selected {
            background-color: #6a1b9a;
            color: #ffffff;
        }
        QHeaderView::section {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #4a4a4a;
            padding: 4px;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #2d2d2d;
            border: 1px solid #4a4a4a;
            padding: 4px;
            color: #e0e0e0;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border: 1px solid #9c27b0;
        }
        QPushButton {
            background-color: #6a1b9a;
            border: none;
            padding: 6px 12px;
            color: #ffffff;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #7b1fa2;
        }
        QPushButton:pressed {
            background-color: #4a148c;
        }
        QPushButton:disabled {
            background-color: #4a4a4a;
            color: #888888;
        }
        QMenuBar {
            background-color: #1a1a1a;
            color: #e0e0e0;
            border-bottom: 1px solid #4a4a4a;
        }
        QMenuBar::item:selected {
            background-color: #6a1b9a;
        }
        QMenu {
            background-color: #1a1a1a;
            color: #e0e0e0;
            border: 1px solid #4a4a4a;
        }
        QMenu::item:selected {
            background-color: #6a1b9a;
        }
        QStatusBar {
            background-color: #1a1a1a;
            color: #e0e0e0;
            border-top: 1px solid #4a4a4a;
        }
        QLabel {
            color: #e0e0e0;
        }
        QTabWidget::pane {
            border: 1px solid #4a4a4a;
            background-color: #242424;
        }
        QTabBar::tab {
            background-color: #1a1a1a;
            color: #e0e0e0;
            border: 1px solid #4a4a4a;
            padding: 6px 12px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #242424;
            border-bottom: 1px solid #242424;
        }
        QTabBar::tab:hover {
            background-color: #303030;
        }
        """

    def _create_sunset_theme(self) -> str:
        """Sunset dark theme with red/orange accents"""
        return """
        QMainWindow {
            background-color: #1f1f1f;
            color: #cccccc;
        }
        QWidget {
            background-color: #1f1f1f;
            color: #cccccc;
        }
        QTreeWidget {
            background-color: #282828;
            border: 1px solid #4d4d4d;
            alternate-background-color: #333333;
            selection-background-color: #d32f2f;
        }
        QTreeWidget::item:selected {
            background-color: #d32f2f;
            color: #ffffff;
        }
        QTreeWidget::item:hover {
            background-color: #363636;
        }
        QTableWidget {
            background-color: #282828;
            border: 1px solid #4d4d4d;
            gridline-color: #4d4d4d;
            alternate-background-color: #333333;
            selection-background-color: #d32f2f;
        }
        QTableWidget::item:selected {
            background-color: #d32f2f;
            color: #ffffff;
        }
        QHeaderView::section {
            background-color: #333333;
            color: #cccccc;
            border: 1px solid #4d4d4d;
            padding: 4px;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #333333;
            border: 1px solid #4d4d4d;
            padding: 4px;
            color: #cccccc;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border: 1px solid #ff5722;
        }
        QPushButton {
            background-color: #d32f2f;
            border: none;
            padding: 6px 12px;
            color: #ffffff;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #f44336;
        }
        QPushButton:pressed {
            background-color: #b71c1c;
        }
        QPushButton:disabled {
            background-color: #4d4d4d;
            color: #888888;
        }
        QMenuBar {
            background-color: #1f1f1f;
            color: #cccccc;
            border-bottom: 1px solid #4d4d4d;
        }
        QMenuBar::item:selected {
            background-color: #d32f2f;
        }
        QMenu {
            background-color: #1f1f1f;
            color: #cccccc;
            border: 1px solid #4d4d4d;
        }
        QMenu::item:selected {
            background-color: #d32f2f;
        }
        QStatusBar {
            background-color: #1f1f1f;
            color: #cccccc;
            border-top: 1px solid #4d4d4d;
        }
        QLabel {
            color: #cccccc;
        }
        QTabWidget::pane {
            border: 1px solid #4d4d4d;
            background-color: #282828;
        }
        QTabBar::tab {
            background-color: #1f1f1f;
            color: #cccccc;
            border: 1px solid #4d4d4d;
            padding: 6px 12px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #282828;
            border-bottom: 1px solid #282828;
        }
        QTabBar::tab:hover {
            background-color: #363636;
        }
        """

    def get_theme(self, theme_type: ThemeType) -> str:
        """Get stylesheet for specified theme"""
        return self._themes.get(theme_type, self._themes[ThemeType.DEFAULT])

    def get_current_theme(self) -> ThemeType:
        """Get current theme type"""
        return self._current_theme

    def set_theme(self, theme_type: ThemeType) -> None:
        """Set current theme"""
        if theme_type != self._current_theme:
            self._current_theme = theme_type
            self.theme_changed.emit(theme_type.value)

    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return [theme.value for theme in ThemeType]

    def get_theme_from_name(self, theme_name: str) -> ThemeType:
        """Get ThemeType from theme name"""
        for theme in ThemeType:
            if theme.value == theme_name:
                return theme
        return ThemeType.DEFAULT
