#!/usr/bin/env python3
"""
LUA Export Dialog
==================

UI dialog for exporting quests to SpellForce LUA scripts.

Features:
- Preview LUA output before export
- Select export options (include rewards, platform ID, etc.)
- Export single quest or batch export multiple quests
- Save to file system

Author: Quest Editor Development Team
Date: November 17, 2025
"""

from pathlib import Path
from typing import Dict, List, Optional, Any

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QSpinBox,
    QCheckBox,
    QGroupBox,
    QFormLayout,
    QFileDialog,
    QMessageBox,
    QTabWidget,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from .lua_exporter import LuaExporter


class LuaExportDialog(QDialog):
    """
    Dialog for exporting quests to LUA format.
    """

    export_complete = Signal(int)  # Emits number of files exported

    def __init__(self, quest_data: Dict[str, Any], parent=None):
        super().__init__(parent)

        self.quest_data = quest_data
        self.exporter = LuaExporter()
        self.exported_files = []

        self.setWindowTitle("Export Quest to LUA")
        self.resize(900, 700)

        self._init_ui()
        self._update_preview()

    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel(
            f"<h2>Export Quest: {self.quest_data.get('name', 'Unknown')}</h2>"
        )
        layout.addWidget(title)

        # Options group
        options_group = QGroupBox("Export Options")
        options_layout = QFormLayout()

        # Platform ID
        self.platform_spin = QSpinBox()
        self.platform_spin.setRange(1, 999)
        self.platform_spin.setValue(1)
        self.platform_spin.setToolTip(
            "Platform/Map ID (P1 = Liannon, P2 = Eloni, etc.)"
        )
        self.platform_spin.valueChanged.connect(self._update_preview)
        options_layout.addRow("Platform ID:", self.platform_spin)

        # Include rewards
        self.include_rewards_check = QCheckBox("Include Quest Rewards")
        self.include_rewards_check.setChecked(True)
        self.include_rewards_check.setToolTip("Include GdsQuestRewards table in export")
        self.include_rewards_check.stateChanged.connect(self._update_preview)
        options_layout.addRow("", self.include_rewards_check)

        # Include conditions
        self.include_conditions_check = QCheckBox("Include Custom Conditions")
        self.include_conditions_check.setChecked(True)
        self.include_conditions_check.setToolTip(
            "Include custom condition logic from Condition Builder"
        )
        self.include_conditions_check.stateChanged.connect(self._update_preview)
        options_layout.addRow("", self.include_conditions_check)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Tabs for preview and file list
        self.tabs = QTabWidget()

        # Preview tab
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)

        preview_label = QLabel("<b>LUA Script Preview:</b>")
        preview_layout.addWidget(preview_label)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Courier", 10))
        self.preview_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        preview_layout.addWidget(self.preview_text)

        self.tabs.addTab(preview_tab, "Script Preview")

        # Quest info tab
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)

        info_label = QLabel("<b>Quest Information:</b>")
        info_layout.addWidget(info_label)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self._populate_info()
        info_layout.addWidget(self.info_text)

        self.tabs.addTab(info_tab, "Quest Info")

        layout.addWidget(self.tabs)

        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Button layout
        button_layout = QHBoxLayout()

        self.export_btn = QPushButton("📁 Export to File...")
        self.export_btn.setToolTip("Save LUA script to file")
        self.export_btn.clicked.connect(self._export_to_file)
        button_layout.addWidget(self.export_btn)

        self.copy_btn = QPushButton("📋 Copy to Clipboard")
        self.copy_btn.setToolTip("Copy LUA script to clipboard")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _populate_info(self):
        """Populate quest information tab."""
        info_lines = []

        quest_id = self.quest_data.get("quest_id", 0)
        quest_name = self.quest_data.get("name", "Unknown")
        internal_name = self.quest_data.get("internal_name", f"Quest{quest_id}")

        info_lines.append(f"<h3>Quest: {quest_name}</h3>")
        info_lines.append(f"<b>Quest ID:</b> {quest_id}<br>")
        info_lines.append(f"<b>Internal Name:</b> {internal_name}<br>")

        # Objectives
        objectives = self.quest_data.get("objectives", [])
        if objectives:
            info_lines.append(f"<br><b>Objectives ({len(objectives)}):</b><ul>")
            for i, obj in enumerate(objectives, 1):
                obj_type = obj.get("type", "Unknown")
                obj_desc = obj.get("description", obj.get("text", "No description"))
                info_lines.append(f"<li>{i}. [{obj_type}] {obj_desc}</li>")
            info_lines.append("</ul>")

        # Rewards
        rewards = self.quest_data.get("rewards", {})
        if rewards:
            info_lines.append("<br><b>Rewards:</b><ul>")

            xp = rewards.get("xp", 0)
            if xp > 0:
                info_lines.append(f"<li>XP: {xp}</li>")

            money = rewards.get("money", {})
            if money:
                gold = money.get("gold", 0)
                silver = money.get("silver", 0)
                copper = money.get("copper", 0)
                if any([gold, silver, copper]):
                    money_str = ", ".join(
                        [
                            f"{gold} Gold" if gold else "",
                            f"{silver} Silver" if silver else "",
                            f"{copper} Copper" if copper else "",
                        ]
                    )
                    money_str = money_str.replace(", , ", ", ").strip(", ")
                    info_lines.append(f"<li>Money: {money_str}</li>")

            items = rewards.get("items", [])
            if items:
                info_lines.append(f"<li>Items: {len(items)} item(s)</li>")

            info_lines.append("</ul>")

        # Conditions
        conditions = self.quest_data.get("conditions", {})
        if conditions and conditions.get("children"):
            condition_count = len(conditions.get("children", []))
            info_lines.append(
                f"<br><b>Custom Conditions:</b> {condition_count} condition(s)<br>"
            )

        # Flags
        flags = self.quest_data.get("flags", [])
        if flags:
            info_lines.append(f"<br><b>Flags Used:</b> {len(flags)} flag(s)<br>")

        self.info_text.setHtml("".join(info_lines))

    def _update_preview(self):
        """Update the LUA script preview."""
        platform_id = self.platform_spin.value()
        include_rewards = self.include_rewards_check.isChecked()

        # Generate LUA script
        script = self.exporter.export_quest_script(
            self.quest_data, include_rewards=include_rewards, platform_id=platform_id
        )

        self.preview_text.setPlainText(script)

    def _export_to_file(self):
        """Export LUA script to a file."""
        platform_id = self.platform_spin.value()
        quest_id = self.quest_data.get("quest_id", 0)
        internal_name = self.quest_data.get("internal_name", f"Quest{quest_id}")

        # Suggest filename
        suggested_name = f"{internal_name}_P{platform_id}.lua"

        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Quest to LUA",
            suggested_name,
            "LUA Scripts (*.lua);;All Files (*)",
        )

        if not file_path:
            return  # User cancelled

        try:
            # Get the current script from preview
            script = self.preview_text.toPlainText()

            # Write to file
            Path(file_path).write_text(script, encoding="utf-8")

            self.exported_files.append(file_path)

            # Show success message
            QMessageBox.information(
                self,
                "Export Successful",
                f"Quest exported successfully to:\n{file_path}\n\n"
                f"Platform: P{platform_id}\n"
                f"Quest ID: {quest_id}",
            )

            self.export_complete.emit(1)

        except Exception as e:
            QMessageBox.critical(
                self, "Export Failed", f"Failed to export quest:\n{str(e)}"
            )

    def _copy_to_clipboard(self):
        """Copy LUA script to clipboard."""
        from PySide6.QtGui import QGuiApplication

        script = self.preview_text.toPlainText()
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(script)

        QMessageBox.information(self, "Copied", "LUA script copied to clipboard!")


class LuaBatchExportDialog(QDialog):
    """
    Dialog for batch exporting multiple quests.
    """

    export_complete = Signal(int)  # Emits number of files exported

    def __init__(self, quests: List[Dict[str, Any]], parent=None):
        super().__init__(parent)

        self.quests = quests
        self.exporter = LuaExporter()
        self.output_dir = None

        self.setWindowTitle("Batch Export Quests to LUA")
        self.resize(800, 600)

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel(f"<h2>Batch Export {len(self.quests)} Quest(s) to LUA</h2>")
        layout.addWidget(title)

        # Quest list
        list_group = QGroupBox("Quests to Export")
        list_layout = QVBoxLayout()

        self.quest_list = QListWidget()
        for quest in self.quests:
            quest_id = quest.get("quest_id", 0)
            quest_name = quest.get("name", "Unknown")
            item = QListWidgetItem(f"[{quest_id}] {quest_name}")
            item.setData(Qt.ItemDataRole.UserRole, quest)
            self.quest_list.addItem(item)

        list_layout.addWidget(self.quest_list)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # Options
        options_group = QGroupBox("Export Options")
        options_layout = QFormLayout()

        # Platform ID
        self.platform_spin = QSpinBox()
        self.platform_spin.setRange(1, 999)
        self.platform_spin.setValue(1)
        self.platform_spin.setToolTip("Platform/Map ID for all quests")
        options_layout.addRow("Platform ID:", self.platform_spin)

        # Include rewards
        self.include_rewards_check = QCheckBox("Generate GdsQuestRewards.lua")
        self.include_rewards_check.setChecked(True)
        self.include_rewards_check.setToolTip("Create separate rewards file")
        options_layout.addRow("", self.include_rewards_check)

        # Separate files
        self.separate_files_check = QCheckBox("Export each quest to separate file")
        self.separate_files_check.setChecked(True)
        self.separate_files_check.setToolTip(
            "Create one file per quest, or combine all into one file"
        )
        options_layout.addRow("", self.separate_files_check)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Output directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Output Directory:"))

        self.dir_label = QLabel("<i>Not selected</i>")
        dir_layout.addWidget(self.dir_label, 1)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._select_output_dir)
        dir_layout.addWidget(browse_btn)

        layout.addLayout(dir_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()

        self.export_btn = QPushButton("📁 Export All")
        self.export_btn.setToolTip("Export all quests to selected directory")
        self.export_btn.clicked.connect(self._export_all)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _select_output_dir(self):
        """Select output directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", str(Path.home())
        )

        if dir_path:
            self.output_dir = Path(dir_path)
            self.dir_label.setText(str(self.output_dir))
            self.export_btn.setEnabled(True)

    def _export_all(self):
        """Export all quests."""
        if not self.output_dir:
            QMessageBox.warning(
                self, "No Directory", "Please select an output directory first."
            )
            return

        platform_id = self.platform_spin.value()
        include_rewards = self.include_rewards_check.isChecked()
        separate_files = self.separate_files_check.isChecked()

        try:
            # Show progress
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(self.quests))
            self.progress_bar.setValue(0)

            if separate_files:
                # Export each quest to separate file
                exports = self.exporter.export_multiple_quests(
                    self.quests, platform_id=platform_id, output_dir=self.output_dir
                )

                file_count = len(exports)

            else:
                # Combine all into one file
                all_scripts = []

                for i, quest in enumerate(self.quests):
                    script = self.exporter.export_quest_logic(quest)
                    all_scripts.append(script)
                    self.progress_bar.setValue(i + 1)

                # Combine all quest scripts
                combined_script = "\n\n".join(
                    [
                        f"-- SpellForce Quest Scripts - Batch Export",
                        f"-- Generated by TirganachReloaded Quest Editor",
                        f"-- Platform: P{platform_id}",
                        f"-- Total Quests: {len(self.quests)}",
                        "",
                        "\n\n".join(all_scripts),
                    ]
                )

                # Add rewards if requested
                if include_rewards:
                    rewards_table = self.exporter.export_rewards_table(
                        self.quests, platform_id
                    )
                    combined_script += "\n\n" + rewards_table

                # Write combined file
                output_file = self.output_dir / f"quests_P{platform_id}_combined.lua"
                output_file.write_text(combined_script, encoding="utf-8")

                file_count = 1

            self.progress_bar.setValue(len(self.quests))

            # Show success message
            QMessageBox.information(
                self,
                "Export Successful",
                f"Successfully exported {len(self.quests)} quest(s) to:\n{self.output_dir}\n\n"
                f"Files created: {file_count}\n"
                f"Platform: P{platform_id}",
            )

            self.export_complete.emit(file_count)
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self, "Export Failed", f"Failed to export quests:\n{str(e)}"
            )

        finally:
            self.progress_bar.setVisible(False)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    # Test data
    sample_quest = {
        "quest_id": 999,
        "name": "Test Quest Export",
        "internal_name": "TestQuestExport",
        "objectives": [
            {
                "type": "Kill Target",
                "target_id": 1234,
                "target_name": "Goblin Chief",
                "quantity": 1,
                "description": "Defeat the Goblin Chief",
            },
            {
                "type": "Gather Items",
                "target_id": 626,
                "target_name": "Simple Metal Helmet",
                "quantity": 3,
                "description": "Collect 3 helmets",
            },
        ],
        "rewards": {
            "xp": 500,
            "money": {"gold": 5, "silver": 10, "copper": 0},
            "items": [{"id": 626, "name": "Simple Metal Helmet"}],
        },
        "conditions": {"operator": "UND", "children": []},
        "flags": [],
    }

    app = QApplication(sys.argv)
    dialog = LuaExportDialog(sample_quest)
    dialog.show()
    sys.exit(app.exec())
