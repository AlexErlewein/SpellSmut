#!/usr/bin/env python3
"""
SpellSmut Tool Launcher
=======================

A unified GUI launcher for all SpellSmut standalone applications.
Provides a central hub to launch various modding tools.

Usage:
    python main.py

Available Tools:
- Darius Almanach: Quest browser and exporter
- Graufurter Bürger Büro: NPC creation suite
- Orthancs Schmiede: Weapon & Armor browser
- Mulandirs Zauberschule: Spell browser and forge
- CFF Editor: SpellForce GameData.cff editor
- Allwissende Almacht: Game icon browser tool
"""

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

# Base directory (src/)
BASE_DIR = Path(__file__).parent


class ToolButton(QFrame):
    """Custom styled button widget for launching tools with large icon/title and smaller description"""

    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self._callback = None
        self._is_hovered = False
        self._is_pressed = False
        self.setup_ui()

    def setup_ui(self):
        """Setup the button appearance"""
        self.setMinimumSize(QSize(240, 90))
        self.setMaximumSize(QSize(300, 110))
        self.setCursor(Qt.PointingHandCursor)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Title label (with emoji)
        self.title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #e0e0e0; background: transparent;")
        layout.addWidget(self.title_label)

        # Description label (smaller)
        self.desc_label = QLabel(self.description)
        desc_font = QFont()
        desc_font.setPointSize(10)
        self.desc_label.setFont(desc_font)
        self.desc_label.setStyleSheet("color: #aaa; background: transparent;")
        layout.addWidget(self.desc_label)

        layout.addStretch()

        self._update_style()

    def _update_style(self):
        """Update the widget style based on hover/pressed state"""
        if self._is_pressed:
            self.setStyleSheet("""
                ToolButton {
                    background-color: #2d2d2d;
                    border-radius: 8px;
                    border: 2px solid #6fb3d2;
                }
                ToolButton QLabel {
                    background: transparent;
                }
            """)
        elif self._is_hovered:
            self.setStyleSheet("""
                ToolButton {
                    background-color: #4a4a4a;
                    border-radius: 8px;
                    border: 2px solid #6fb3d2;
                }
                ToolButton QLabel {
                    background: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                ToolButton {
                    background-color: #3c3c3c;
                    border-radius: 8px;
                    border: 2px solid #555;
                }
                ToolButton QLabel {
                    background: transparent;
                }
            """)

    def enterEvent(self, event):
        """Handle mouse enter"""
        self._is_hovered = True
        self._update_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        self._is_hovered = False
        self._is_pressed = False
        self._update_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press"""
        self._is_pressed = True
        self._update_style()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release and trigger callback"""
        was_pressed = self._is_pressed
        self._is_pressed = False
        self._update_style()
        if was_pressed and self._callback and self.rect().contains(event.pos()):
            self._callback()
        super().mouseReleaseEvent(event)

    def clicked_connect(self, callback):
        """Connect a callback to the click event"""
        self._callback = callback


class SpellSmutLauncher(QMainWindow):
    """Main launcher window for SpellSmut tools"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("SpellSmut Tool Launcher")
        self.setMinimumSize(QSize(750, 600))
        self.setMaximumSize(QSize(950, 800))

        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header_label = QLabel("SpellSmut Tool Launcher")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #6fb3d2;
            padding: 10px;
        """)
        main_layout.addWidget(header_label)

        # Subtitle
        subtitle_label = QLabel("Select a tool to launch")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            color: #888;
            padding-bottom: 20px;
        """)
        main_layout.addWidget(subtitle_label)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #444;")
        separator.setFixedHeight(2)
        main_layout.addWidget(separator)

        main_layout.addSpacing(10)

        # Tools grid - Row 1
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(20)

        # Darius Almanach button
        self.darius_btn = ToolButton(
            "📜 Darius Almanach", "Browse and export SpellForce quests"
        )
        self.darius_btn.clicked_connect(self.launch_darius_almanach)
        row1_layout.addWidget(self.darius_btn)

        # Graufurter Bürger Büro button
        self.graufurter_btn = ToolButton(
            "👤 Graufurter Bürger Büro", "NPC browser and creation suite"
        )
        self.graufurter_btn.clicked_connect(self.launch_graufurter_buerger_buero)
        row1_layout.addWidget(self.graufurter_btn)

        main_layout.addLayout(row1_layout)

        # Tools grid - Row 2
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(20)

        # Orthancs Schmiede button
        self.orthancs_btn = ToolButton("⚔️ Orthancs Schmiede", "Weapon & Armor browser")
        self.orthancs_btn.clicked_connect(self.launch_orthancs_schmiede)
        row2_layout.addWidget(self.orthancs_btn)

        # Mulandirs Zauberschule button
        self.mulandirs_btn = ToolButton(
            "✨ Mulandirs Zauberschule", "Spell browser and forge"
        )
        self.mulandirs_btn.clicked_connect(self.launch_mulandirs_zauberschule)
        row2_layout.addWidget(self.mulandirs_btn)

        main_layout.addLayout(row2_layout)

        # Tools grid - Row 3
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(20)

        # CFF Editor button
        self.cff_btn = ToolButton("🔧 CFF Editor", "Edit SpellForce GameData.cff files")
        self.cff_btn.clicked_connect(self.launch_cff_editor)
        row3_layout.addWidget(self.cff_btn)

        # Allwissende Almacht button
        self.icon_btn = ToolButton(
            "🔍 Allwissende Almacht", "Browse game icons and assets"
        )
        self.icon_btn.clicked_connect(self.launch_allwissende_almacht)
        row3_layout.addWidget(self.icon_btn)

        main_layout.addLayout(row3_layout)

        main_layout.addStretch()

        # Footer
        footer_label = QLabel("TirganachReloaded Modding Tools")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("""
            font-size: 11px;
            color: #666;
            padding-top: 20px;
        """)
        main_layout.addWidget(footer_label)

        # Status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #1e1e1e;
                color: #888;
                border-top: 1px solid #444;
            }
        """)

    def launch_tool(self, script_path: Path, tool_name: str):
        """Launch a tool as a subprocess"""
        self.statusBar().showMessage(f"Launching {tool_name}...")
        try:
            # Launch the tool as a separate process
            subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(script_path.parent),
            )
            self.statusBar().showMessage(f"{tool_name} launched successfully")
        except Exception as e:
            self.show_error(tool_name, str(e))
            self.statusBar().showMessage("Ready")

    def launch_darius_almanach(self):
        """Launch Darius Almanach quest viewer"""
        script_path = BASE_DIR / "DariusAlmanach" / "run_darius_almanach.py"
        self.launch_tool(script_path, "Darius Almanach")

    def launch_graufurter_buerger_buero(self):
        """Launch Graufurter Bürger Büro NPC suite"""
        script_path = (
            BASE_DIR / "GraufurterBuergerBuero" / "run_graufurter_buerger_buero.py"
        )
        self.launch_tool(script_path, "Graufurter Bürger Büro")

    def launch_orthancs_schmiede(self):
        """Launch Orthancs Schmiede weapon & armor browser"""
        script_path = BASE_DIR / "OrthancsSchmiede" / "run_orthancs_schmiede.py"
        self.launch_tool(script_path, "Orthancs Schmiede")

    def launch_mulandirs_zauberschule(self):
        """Launch Mulandirs Zauberschule spell browser and forge"""
        script_path = (
            BASE_DIR / "MulandirsZauberschule" / "run_mulandirs_zauberschule.py"
        )
        self.launch_tool(script_path, "Mulandirs Zauberschule")

    def launch_cff_editor(self):
        """Launch CFF Editor"""
        script_path = BASE_DIR / "TirganachReloaded" / "run_cff_editor.py"
        self.launch_tool(script_path, "CFF Editor")

    def launch_allwissende_almacht(self):
        """Launch Allwissende Almacht"""
        script_path = BASE_DIR / "AllwissendeAlmacht" / "run_allwissende_almacht.py"
        self.launch_tool(script_path, "Allwissende Almacht")

    def show_error(self, tool_name: str, error_message: str):
        """Show an error dialog"""
        QMessageBox.critical(
            self,
            f"Error Launching {tool_name}",
            f"Failed to launch {tool_name}:\n\n{error_message}",
            QMessageBox.Ok,
        )


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("SpellSmut Tool Launcher")
    app.setOrganizationName("SpellSmut Modding Tools")

    # Set application-wide dark palette
    app.setStyle("Fusion")

    window = SpellSmutLauncher()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
