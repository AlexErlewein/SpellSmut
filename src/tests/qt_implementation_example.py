"""
Qt/PySide6 Implementation Example
Shows how to add the new sections to quest_details_viewer.py
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


# ============================================================================
# Example 1: Statistics Cards Section
# ============================================================================
def create_statistics_section(self, quest_stats):
    """Create statistics dashboard with cards"""
    group = QGroupBox("📊 Quest Statistics")
    layout = QVBoxLayout(group)
    
    # Create horizontal layout for cards
    cards_layout = QHBoxLayout()
    
    # Card 1: Dialogues
    dlg_card = self._create_stat_card("💬", quest_stats.get('dialogues', 0), "Dialogues")
    cards_layout.addWidget(dlg_card)
    
    # Card 2: Files
    files_card = self._create_stat_card("📁", quest_stats.get('files', 0), "Files")
    cards_layout.addWidget(files_card)
    
    # Card 3: References
    refs_card = self._create_stat_card("🔗", quest_stats.get('references', 0), "References")
    cards_layout.addWidget(refs_card)
    
    # Card 4: Maps
    maps_card = self._create_stat_card("🗺️", quest_stats.get('maps', 0), "Maps")
    cards_layout.addWidget(maps_card)
    
    # Card 5: XP
    xp_card = self._create_stat_card("⭐", quest_stats.get('xp', 0), "XP Reward")
    cards_layout.addWidget(xp_card)
    
    layout.addLayout(cards_layout)
    return group


def _create_stat_card(self, icon, value, label):
    """Create a single statistics card"""
    card = QFrame()
    card.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
    card.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #667eea, stop:1 #764ba2);
            border-radius: 8px;
            padding: 15px;
            min-width: 120px;
        }
    """)
    
    layout = QVBoxLayout(card)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    # Value with icon
    value_label = QLabel(f"{icon} {value}")
    value_label.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 24px;
            font-weight: bold;
        }
    """)
    value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(value_label)
    
    # Label
    label_widget = QLabel(label)
    label_widget.setStyleSheet("""
        QLabel {
            color: rgba(255, 255, 255, 0.9);
            font-size: 11px;
        }
    """)
    label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label_widget)
    
    return card


# ============================================================================
# Example 2: Map Locations Section
# ============================================================================
def create_map_locations_section(self, map_locations):
    """Create map locations section with badges"""
    group = QGroupBox("🗺️ Map Locations")
    layout = QVBoxLayout(group)
    
    # Info text
    info_label = QLabel("This quest is active in the following locations:")
    info_label.setStyleSheet("color: #666; font-size: 12px;")
    layout.addWidget(info_label)
    
    # Maps container
    maps_layout = QHBoxLayout()
    maps_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    
    for map_info in map_locations:
        map_badge = self._create_map_badge(map_info['code'], map_info['name'])
        maps_layout.addWidget(map_badge)
    
    layout.addLayout(maps_layout)
    return group


def _create_map_badge(self, code, name):
    """Create a map location badge"""
    badge = QFrame()
    badge.setFrameStyle(QFrame.Shape.StyledPanel)
    badge.setStyleSheet("""
        QFrame {
            background-color: #4caf50;
            border-radius: 15px;
            padding: 8px 15px;
        }
    """)
    
    layout = QHBoxLayout(badge)
    layout.setContentsMargins(5, 5, 5, 5)
    
    # Code
    code_label = QLabel(code)
    code_label.setStyleSheet("""
        QLabel {
            color: white;
            font-weight: bold;
            font-size: 13px;
        }
    """)
    layout.addWidget(code_label)
    
    # Separator
    separator = QLabel("│")
    separator.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
    layout.addWidget(separator)
    
    # Name
    name_label = QLabel(name)
    name_label.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 13px;
        }
    """)
    layout.addWidget(name_label)
    
    return badge


# ============================================================================
# Example 3: Rewards Section
# ============================================================================
def create_rewards_section(self, rewards):
    """Create rewards section"""
    group = QGroupBox("💰 Quest Rewards")
    layout = QVBoxLayout(group)
    
    # XP Reward
    if rewards.get('xp', 0) > 0:
        xp_widget = self._create_reward_item("⭐", f"{rewards['xp']} XP", "Experience Points")
        layout.addWidget(xp_widget)
    
    # Reward Flags
    for flag in rewards.get('flags', []):
        flag_widget = self._create_reward_item("🏆", flag, "Reward Flag")
        layout.addWidget(flag_widget)
    
    # Source
    source_label = QLabel(f"<b>Source:</b> <code>{rewards.get('source', 'Unknown')}</code>")
    source_label.setStyleSheet("font-size: 11px; color: #666; margin-top: 10px;")
    layout.addWidget(source_label)
    
    return group


def _create_reward_item(self, icon, value, label):
    """Create a single reward item"""
    widget = QFrame()
    widget.setFrameStyle(QFrame.Shape.StyledPanel)
    widget.setStyleSheet("""
        QFrame {
            background-color: #fff3e0;
            border-radius: 6px;
            padding: 10px;
        }
    """)
    
    layout = QHBoxLayout(widget)
    
    # Icon
    icon_label = QLabel(icon)
    icon_label.setStyleSheet("font-size: 24px;")
    layout.addWidget(icon_label)
    
    # Details
    details_layout = QVBoxLayout()
    
    value_label = QLabel(value)
    value_label.setStyleSheet("""
        QLabel {
            font-weight: bold;
            font-size: 16px;
            color: #ff9800;
        }
    """)
    details_layout.addWidget(value_label)
    
    label_widget = QLabel(label)
    label_widget.setStyleSheet("font-size: 11px; color: #666;")
    details_layout.addWidget(label_widget)
    
    layout.addLayout(details_layout)
    layout.addStretch()
    
    return widget


# ============================================================================
# Example 4: Dialogues Section
# ============================================================================
def create_dialogues_section(self, dialogues):
    """Create dialogues section with translations"""
    group = QGroupBox(f"💬 Extended Story Dialogues ({len(dialogues)} found)")
    layout = QVBoxLayout(group)
    
    # Info box
    info = QLabel(f"<b>{len(dialogues)} narrative dialogues found</b> - "
                  "These provide story context from NPC conversations")
    info.setStyleSheet("""
        QLabel {
            background-color: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 10px;
            border-radius: 4px;
        }
    """)
    info.setWordWrap(True)
    layout.addWidget(info)
    
    # Dialogues
    for i, dlg in enumerate(dialogues, 1):
        dlg_widget = self._create_dialogue_item(i, dlg)
        layout.addWidget(dlg_widget)
    
    return group


def _create_dialogue_item(self, number, dialogue):
    """Create a single dialogue item"""
    widget = QFrame()
    widget.setFrameStyle(QFrame.Shape.StyledPanel)
    widget.setStyleSheet("""
        QFrame {
            background-color: #f8f9fa;
            border-left: 3px solid #667eea;
            border-radius: 4px;
            padding: 12px;
        }
    """)
    
    layout = QVBoxLayout(widget)
    
    # German text
    de_label = QLabel(f"🇩🇪 \"{dialogue['text_de']}\"")
    de_label.setStyleSheet("""
        QLabel {
            font-style: italic;
            color: #333;
            font-size: 13px;
        }
    """)
    de_label.setWordWrap(True)
    layout.addWidget(de_label)
    
    # English translation
    if dialogue.get('text_en'):
        en_label = QLabel(f"🇬🇧 \"{dialogue['text_en']}\"")
        en_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
            }
        """)
        en_label.setWordWrap(True)
        layout.addWidget(en_label)
    
    # Source file
    source_label = QLabel(f"📄 Source: {dialogue['source_file']}")
    source_label.setStyleSheet("""
        QLabel {
            font-size: 10px;
            color: #999;
            margin-top: 5px;
        }
    """)
    layout.addWidget(source_label)
    
    return widget


# ============================================================================
# Example 5: File References Section
# ============================================================================
def create_file_references_section(self, file_refs):
    """Create technical file references section"""
    total_refs = sum(f['count'] for f in file_refs)
    group = QGroupBox(f"📁 Technical References ({total_refs} total references)")
    layout = QVBoxLayout(group)
    
    # Info box
    info = QLabel(f"<b>{total_refs} total quest references</b> found across "
                  f"{len(file_refs)} Lua script files")
    info.setStyleSheet("""
        QLabel {
            background-color: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 10px;
            border-radius: 4px;
        }
    """)
    info.setWordWrap(True)
    layout.addWidget(info)
    
    # File list
    for file_ref in file_refs:
        file_widget = self._create_file_reference_item(file_ref)
        layout.addWidget(file_widget)
    
    return group


def _create_file_reference_item(self, file_ref):
    """Create a single file reference item"""
    widget = QFrame()
    widget.setFrameStyle(QFrame.Shape.StyledPanel)
    widget.setStyleSheet("""
        QFrame {
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 8px;
        }
        QFrame:hover {
            background-color: #e9ecef;
        }
    """)
    
    layout = QHBoxLayout(widget)
    
    # File path
    path_label = QLabel(f"📄 {file_ref['path']}")
    path_label.setStyleSheet("""
        QLabel {
            font-family: 'Courier New', monospace;
            font-size: 11px;
            color: #333;
        }
    """)
    layout.addWidget(path_label)
    
    layout.addStretch()
    
    # Reference count badge
    count_label = QLabel(f"{file_ref['count']} refs")
    count_label.setStyleSheet("""
        QLabel {
            background-color: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        }
    """)
    layout.addWidget(count_label)
    
    return widget


# ============================================================================
# Example 6: Quest Relationships with Navigation
# ============================================================================
class QuestRelationshipsSection(QWidget):
    """Quest relationships section with navigation signals"""
    
    quest_selected = Signal(int)  # Emits quest ID when navigation button clicked
    
    def __init__(self, quest_data, parent=None):
        super().__init__(parent)
        self.quest_data = quest_data
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        group = QGroupBox("🔗 Quest Relationships")
        group_layout = QVBoxLayout(group)
        
        # Parent quest
        if self.quest_data.get('parent_id'):
            parent_widget = self._create_parent_section()
            group_layout.addWidget(parent_widget)
        
        # Sibling quests
        if self.quest_data.get('siblings'):
            siblings_widget = self._create_siblings_section()
            group_layout.addWidget(siblings_widget)
        
        layout.addWidget(group)
    
    def _create_parent_section(self):
        """Create parent quest section with navigation"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("<b>Parent Quest:</b>")
        layout.addWidget(label)
        
        # Parent item
        parent_frame = QFrame()
        parent_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        parent_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 4px;
                padding: 10px;
                margin-left: 20px;
            }
        """)
        
        parent_layout = QHBoxLayout(parent_frame)
        
        # Badge
        badge = QLabel("PARENT")
        badge.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                color: #2196F3;
                padding: 3px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            }
        """)
        parent_layout.addWidget(badge)
        
        # Quest info
        parent_id = self.quest_data['parent_id']
        parent_name = self.quest_data.get('parent_name', f'Quest {parent_id}')
        info_label = QLabel(f"<b>Quest {parent_id}:</b> {parent_name}")
        parent_layout.addWidget(info_label)
        
        parent_layout.addStretch()
        
        # Navigation button
        nav_button = QPushButton("Go to Parent →")
        nav_button.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 6px 15px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5568d3;
            }
        """)
        nav_button.clicked.connect(lambda: self.quest_selected.emit(parent_id))
        parent_layout.addWidget(nav_button)
        
        layout.addWidget(parent_frame)
        return widget
    
    def _create_siblings_section(self):
        """Create sibling quests section"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("<b>Sibling Quests (same parent):</b>")
        layout.addWidget(label)
        
        # Show first 3 siblings
        for sibling in self.quest_data['siblings'][:3]:
            sibling_frame = self._create_sibling_item(sibling)
            layout.addWidget(sibling_frame)
        
        # Show count of remaining
        if len(self.quest_data['siblings']) > 3:
            remaining = len(self.quest_data['siblings']) - 3
            more_label = QLabel(f"... and {remaining} more subquests")
            more_label.setStyleSheet("""
                QLabel {
                    text-align: center;
                    color: #999;
                    font-size: 11px;
                    margin-top: 10px;
                }
            """)
            more_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(more_label)
        
        return widget
    
    def _create_sibling_item(self, sibling):
        """Create a single sibling quest item"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 4px;
                padding: 8px;
                margin-left: 20px;
            }
            QFrame:hover {
                background-color: #e9ecef;
                cursor: pointer;
            }
        """)
        
        layout = QHBoxLayout(frame)
        
        # Badge
        badge = QLabel("SIBLING")
        badge.setStyleSheet("""
            QLabel {
                background-color: #f3e5f5;
                color: #9c27b0;
                padding: 3px 8px;
                border-radius: 10px;
                font-size: 10px;
                font-weight: bold;
            }
        """)
        layout.addWidget(badge)
        
        # Quest info
        info_label = QLabel(f"Quest {sibling['id']}: {sibling['name']}")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Make clickable
        frame.mousePressEvent = lambda e: self.quest_selected.emit(sibling['id'])
        
        return frame


# ============================================================================
# Usage Example in quest_details_viewer.py
# ============================================================================
"""
In quest_details_viewer.py, you would add these sections like this:

def setup_ui(self):
    layout = QVBoxLayout(self)
    
    # ... existing code ...
    
    # Add new sections
    self.statistics_group = self.create_statistics_section({})
    content_layout.addWidget(self.statistics_group)
    
    self.map_locations_group = self.create_map_locations_section([])
    content_layout.addWidget(self.map_locations_group)
    
    self.rewards_group = self.create_rewards_section({})
    content_layout.addWidget(self.rewards_group)
    
    self.dialogues_group = self.create_dialogues_section([])
    content_layout.addWidget(self.dialogues_group)
    
    self.file_refs_group = self.create_file_references_section([])
    content_layout.addWidget(self.file_refs_group)
    
    self.relationships_widget = QuestRelationshipsSection({})
    self.relationships_widget.quest_selected.connect(self.on_quest_navigation)
    content_layout.addWidget(self.relationships_widget)

def on_quest_navigation(self, quest_id):
    '''Handle quest navigation from relationships section'''
    # Load the selected quest
    self.load_quest(quest_id)
"""
