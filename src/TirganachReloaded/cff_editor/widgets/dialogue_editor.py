#!/usr/bin/env python3
"""
Visual Dialogue Tree Editor (PySide6 Compatible)

A drag-and-drop dialogue tree builder with:
- Visual node editing
- Real-time preview
- Dialogue flow management
- NPC assignment
- Voice line integration

This component integrates with the enhanced quest creation wizard and uses only PySide6.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsScene, QGraphicsView,
    QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem,
    QPushButton, QComboBox, QLineEdit, QTextEdit, QLabel, QGroupBox,
    QMenu, QMessageBox, QToolBar, QSplitter, QScrollArea
)
from PySide6.QtCore import (
    Qt, QPointF, QRectF, Signal, QLineF, Slot, 
    QObject, QThread
)
from PySide6.QtGui import (
    QPen, QBrush, QColor, QFont, QPainter, QPolygonF, 
    QAction, QWheelEvent, QMouseEvent, QContextMenuEvent
)

from TirganachReloaded.cff_editor.models.quest_models import Dialogue


@dataclass
class DialogueNode:
    """Represents a single dialogue node in the tree"""
    
    id: str
    text: str
    speaker: str  # "NPC" or "Player"
    dialogue_type: str = "Standard"
    voice_file: Optional[str] = None
    conditions: List[str] = None
    position: QPointF = None
    parent_id: Optional[str] = None
    child_ids: List[str] = None
    
    def __post_init__(self):
        if self.position is None:
            self.position = QPointF(0, 0)
        if self.conditions is None:
            self.conditions = []
        if self.child_ids is None:
            self.child_ids = []


class DialogueNodeItem(QGraphicsRectItem):
    """Visual representation of a dialogue node"""
    
    # Custom signals using PySide6 Signal
    node_selected = Signal(str)
    node_moved = Signal(str, QPointF)
    node_deleted = Signal(str)
    
    def __init__(self, node: DialogueNode, parent=None):
        super().__init__(parent)
        self.node = node
        self.setRect(QRectF(0, 0, 200, 80))
        self.setPos(node.position)
        
        # Styling based on speaker type
        if node.speaker.lower() == "player":
            self.color = QColor(52, 152, 219)  # Blue
        else:
            self.color = QColor(46, 204, 113)  # Green
        
        self.pen = QPen(self.color.darker(150), 2)
        self.brush = QBrush(self.color.lighter(130))
        
        self.setPen(self.pen)
        self.setBrush(self.brush)
        
        # Make node movable and selectable
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Create text items
        self._create_text_items()
        
        # Create connection points
        self._create_connection_points()
    
    def _create_text_items(self):
        """Create text items for the node"""
        # Speaker label
        self.speaker_text = QGraphicsTextItem(self.node.speaker, self)
        self.speaker_text.setPos(5, 5)
        self.speaker_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.speaker_text.setDefaultTextColor(Qt.white)
        
        # Dialogue text (truncated)
        display_text = self.node.text[:50]
        if len(self.node.text) > 50:
            display_text += "..."
        
        self.dialogue_text = QGraphicsTextItem(display_text, self)
        self.dialogue_text.setPos(5, 25)
        self.dialogue_text.setFont(QFont("Arial", 9))
        self.dialogue_text.setDefaultTextColor(Qt.white)
        
        # Node ID
        self.id_text = QGraphicsTextItem(f"ID: {self.node.id}", self)
        self.id_text.setPos(5, 60)
        self.id_text.setFont(QFont("Arial", 8))
        self.id_text.setDefaultTextColor(Qt.white)
    
    def _create_connection_points(self):
        """Create visual connection points"""
        # Input point (top)
        self.input_point = QRectF(95, -5, 10, 10)
        
        # Output point (bottom)
        self.output_point = QRectF(95, 75, 10, 10)
    
    def paint(self, painter, option, widget):
        """Custom paint for enhanced appearance"""
        super().paint(painter, option, widget)
        
        # Draw connection points
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(Qt.black, 1))
        
        # Input point
        painter.drawEllipse(self.input_point)
        
        # Output point
        painter.drawEllipse(self.output_point)
    
    def itemChange(self, change, value):
        """Handle item changes"""
        if change == QGraphicsItem.ItemPositionChange:
            # Update node position
            self.node.position = value
            self.node_moved.emit(self.node.id, value)
        
        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.RightButton:
            # Show context menu
            self._show_context_menu(event.screenPos())
        else:
            super().mousePressEvent(event)
            self.node_selected.emit(self.node.id)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click - open editor"""
        self._open_editor()
        super().mouseDoubleClickEvent(event)
    
    def _show_context_menu(self, pos):
        """Show context menu for the node"""
        menu = QMenu()
        
        edit_action = QAction("Edit Dialogue", None)
        edit_action.triggered.connect(self._open_editor)
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete Node", None)
        delete_action.triggered.connect(self._delete_node)
        menu.addAction(delete_action)
        
        menu.exec_(pos)
    
    def _open_editor(self):
        """Open dialogue editor dialog"""
        # This will be handled by the parent widget
        if self.scene() and self.scene().views():
            parent_view = self.scene().views()[0]
            if hasattr(parent_view, 'parent') and hasattr(parent_view.parent(), 'edit_node'):
                parent_view.parent().edit_node(self.node.id)
    
    def _delete_node(self):
        """Delete this node"""
        reply = QMessageBox.question(
            None, "Delete Node", 
            f"Are you sure you want to delete dialogue node '{self.node.id}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.node_deleted.emit(self.node.id)


class DialogueConnectionItem(QGraphicsLineItem):
    """Visual connection between dialogue nodes"""
    
    def __init__(self, start_node: DialogueNodeItem, end_node: DialogueNodeItem, parent=None):
        # Calculate connection points
        start_pos = start_node.scenePos() + QPointF(100, 75)  # Bottom center
        end_pos = end_node.scenePos() + QPointF(100, -5)   # Top center
        
        super().__init__(QLineF(start_pos, end_pos), parent)
        
        self.start_node = start_node
        self.end_node = end_node
        
        # Styling
        self.pen = QPen(QColor(100, 100, 100), 2)
        self.setPen(self.pen)
        
        # Draw arrow
        self._create_arrow()
    
    def _create_arrow(self):
        """Create arrow head"""
        line = self.line()
        
        # Calculate arrow point
        angle = line.angle()
        arrow_length = 10
        arrow_angle = 150
        
        # Calculate arrow points
        from math import cos, sin, radians
        rad1 = radians(angle - arrow_angle)
        rad2 = radians(angle + arrow_angle)
        
        p1 = line.p2()
        p2 = p1 - QPointF(arrow_length * cos(rad1), arrow_length * sin(rad1))
        p3 = p1 - QPointF(arrow_length * cos(rad2), arrow_length * sin(rad2))
        
        self.arrow_head = QPolygonF([p1, p2, p3])
    
    def paint(self, painter, option, widget):
        """Custom paint with arrow"""
        super().paint(painter, option, widget)
        
        # Draw arrow head
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.drawPolygon(self.arrow_head)
    
    def update_position(self):
        """Update connection when nodes move"""
        start_pos = self.start_node.scenePos() + QPointF(100, 75)
        end_pos = self.end_node.scenePos() + QPointF(100, -5)
        
        self.setLine(QLineF(start_pos, end_pos))
        self._create_arrow()


class DialogueTreeEditor(QWidget):
    """Main dialogue tree editor widget"""
    
    # Signals using PySide6 Signal
    dialogue_changed = Signal(list)  # List of dialogue nodes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes = {}  # id -> DialogueNode
        self.node_items = {}  # id -> DialogueNodeItem
        self.connections = []  # List of DialogueConnectionItem
        self.next_node_id = 1
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Graphics view (left side)
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, 800, 600))
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        
        # Enable editing functionality
        self.view.edit_node = self.edit_node
        self.view.parent = lambda: self
        
        splitter.addWidget(self.view)
        
        # Properties panel (right side)
        properties_panel = self._create_properties_panel()
        splitter.addWidget(properties_panel)
        
        splitter.setSizes([600, 200])
        layout.addWidget(splitter)
    
    def _create_toolbar(self) -> QToolBar:
        """Create toolbar"""
        toolbar = QToolBar()
        
        # Add NPC node
        add_npc_btn = QPushButton("Add NPC Dialogue")
        add_npc_btn.clicked.connect(lambda: self._add_node("NPC"))
        toolbar.addWidget(add_npc_btn)
        
        # Add Player node
        add_player_btn = QPushButton("Add Player Choice")
        add_player_btn.clicked.connect(lambda: self._add_node("Player"))
        toolbar.addWidget(add_player_btn)
        
        toolbar.addSeparator()
        
        # Auto-arrange
        arrange_btn = QPushButton("Auto-Arrange")
        arrange_btn.clicked.connect(self._auto_arrange)
        toolbar.addWidget(arrange_btn)
        
        # Clear all
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_all)
        toolbar.addWidget(clear_btn)
        
        return toolbar
    
    def _create_properties_panel(self) -> QWidget:
        """Create properties panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Node info
        info_group = QGroupBox("Selected Node")
        info_layout = QVBoxLayout(info_group)
        
        self.selected_id_label = QLabel("No node selected")
        info_layout.addWidget(self.selected_id_label)
        
        layout.addWidget(info_group)
        
        # Node editor
        editor_group = QGroupBox("Edit Dialogue")
        editor_layout = QFormLayout(editor_group)
        
        self.speaker_combo = QComboBox()
        self.speaker_combo.addItems(["NPC", "Player"])
        self.speaker_combo.currentTextChanged.connect(self._update_node_properties)
        editor_layout.addRow("Speaker:", self.speaker_combo)
        
        self.dialogue_edit = QTextEdit()
        self.dialogue_edit.setMaximumHeight(80)
        self.dialogue_edit.textChanged.connect(self._update_node_properties)
        editor_layout.addRow("Text:", self.dialogue_edit)
        
        self.voice_file_edit = QLineEdit()
        self.voice_file_edit.setPlaceholderText("voice file path (optional)")
        self.voice_file_edit.textChanged.connect(self._update_node_properties)
        editor_layout.addRow("Voice File:", self.voice_file_edit)
        
        layout.addWidget(editor_group)
        
        layout.addStretch()
        
        return panel
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Scene selection changed
        self.scene.selectionChanged.connect(self._on_selection_changed)
    
    @Slot()
    def _add_node(self, speaker: str):
        """Add a new dialogue node"""
        node_id = f"node_{self.next_node_id}"
        self.next_node_id += 1
        
        # Create node with default position
        position = QPointF(100, 100 + (self.next_node_id * 30))
        
        node = DialogueNode(
            id=node_id,
            text="New dialogue text...",
            speaker=speaker,
            position=position
        )
        
        # Create visual item
        node_item = DialogueNodeItem(node, self)
        
        # Connect signals
        node_item.node_selected.connect(self._on_node_selected)
        node_item.node_moved.connect(self._on_node_moved)
        node_item.node_deleted.connect(self._on_node_deleted)
        
        # Add to scene and storage
        self.scene.addItem(node_item)
        self.nodes[node_id] = node
        self.node_items[node_id] = node_item
        
        # Auto-connect to previous node if exists
        self._auto_connect_new_node(node)
        
        # Emit change signal
        self._emit_dialogue_changed()
    
    @Slot()
    def _auto_connect_new_node(self, new_node: DialogueNode):
        """Auto-connect new node to previous node"""
        if len(self.nodes) > 1:
            # Find the last added node
            sorted_nodes = sorted(self.nodes.values(), key=lambda x: x.id)
            if len(sorted_nodes) >= 2:
                previous_node = sorted_nodes[-2]
                self._connect_nodes(previous_node.id, new_node.id)
    
    @Slot()
    def _connect_nodes(self, start_id: str, end_id: str):
        """Create connection between two nodes"""
        if start_id not in self.node_items or end_id not in self.node_items:
            return
        
        start_item = self.node_items[start_id]
        end_item = self.node_items[end_id]
        
        # Create connection
        connection = DialogueConnectionItem(start_item, end_item, self)
        self.connections.append(connection)
        self.scene.addItem(connection)
        
        # Update node relationships
        self.nodes[start_id].child_ids.append(end_id)
        self.nodes[end_id].parent_id = start_id
    
    @Slot(str)
    def _on_node_selected(self, node_id: str):
        """Handle node selection"""
        # Clear selection
        for item in self.node_items.values():
            item.setSelected(False)
        
        # Select the clicked node
        if node_id in self.node_items:
            self.node_items[node_id].setSelected(True)
            self._update_properties_display(node_id)
    
    @Slot()
    def _on_selection_changed(self):
        """Handle scene selection change"""
        selected_items = self.scene.selectedItems()
        if selected_items:
            # Find selected node item
            for item in selected_items:
                if isinstance(item, DialogueNodeItem):
                    self._update_properties_display(item.node.id)
                    break
        else:
            self._clear_properties_display()
    
    @Slot(str, QPointF)
    def _on_node_moved(self, node_id: str, position: QPointF):
        """Handle node movement"""
        # Update connections
        for connection in self.connections:
            if (connection.start_node.node.id == node_id or 
                connection.end_node.node.id == node_id):
                connection.update_position()
    
    @Slot(str)
    def _on_node_deleted(self, node_id: str):
        """Handle node deletion"""
        if node_id in self.node_items:
            # Remove from scene
            self.scene.removeItem(self.node_items[node_id])
            
            # Remove connections
            connections_to_remove = []
            for connection in self.connections:
                if (connection.start_node.node.id == node_id or 
                    connection.end_node.node.id == node_id):
                    connections_to_remove.append(connection)
            
            for connection in connections_to_remove:
                self.scene.removeItem(connection)
                self.connections.remove(connection)
            
            # Remove from storage
            del self.nodes[node_id]
            del self.node_items[node_id]
            
            # Update node relationships
            for node in self.nodes.values():
                if node.parent_id == node_id:
                    node.parent_id = None
                if node_id in node.child_ids:
                    node.child_ids.remove(node_id)
            
            # Clear properties
            self._clear_properties_display()
            
            # Emit change signal
            self._emit_dialogue_changed()
    
    def edit_node(self, node_id: str):
        """Open detailed editor for a node"""
        if node_id not in self.nodes:
            return
        
        node = self.nodes[node_id]
        
        # Focus on this node in properties panel
        self._update_properties_display(node_id)
    
    def _update_properties_display(self, node_id: str):
        """Update properties panel for selected node"""
        if node_id not in self.nodes:
            return
        
        node = self.nodes[node_id]
        
        self.selected_id_label.setText(f"Selected: {node_id}")
        self.speaker_combo.setCurrentText(node.speaker)
        self.dialogue_edit.setPlainText(node.text)
        self.voice_file_edit.setText(node.voice_file or "")
    
    def _clear_properties_display(self):
        """Clear properties panel"""
        self.selected_id_label.setText("No node selected")
        self.speaker_combo.setCurrentIndex(0)
        self.dialogue_edit.clear()
        self.voice_file_edit.clear()
    
    @Slot()
    def _update_node_properties(self):
        """Update selected node properties"""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return
        
        # Find selected node item
        node_item = None
        for item in selected_items:
            if isinstance(item, DialogueNodeItem):
                node_item = item
                break
        
        if not node_item:
            return
        
        node = node_item.node
        node.speaker = self.speaker_combo.currentText()
        node.text = self.dialogue_edit.toPlainText()
        node.voice_file = self.voice_file_edit.text() or None
        
        # Update visual item
        node_item.speaker_text.setPlainText(node.speaker)
        display_text = node.text[:50]
        if len(node.text) > 50:
            display_text += "..."
        node_item.dialogue_text.setPlainText(display_text)
        
        # Update color based on speaker
        if node.speaker.lower() == "player":
            color = QColor(52, 152, 219)  # Blue
        else:
            color = QColor(46, 204, 113)  # Green
        
        node_item.color = color
        node_item.pen = QPen(color.darker(150), 2)
        node_item.brush = QBrush(color.lighter(130))
        node_item.setPen(node_item.pen)
        node_item.setBrush(node_item.brush)
        
        # Emit change signal
        self._emit_dialogue_changed()
    
    @Slot()
    def _auto_arrange(self):
        """Auto-arrange nodes in tree layout"""
        if not self.nodes:
            return
        
        # Simple hierarchical layout
        level_width = 250
        level_height = 150
        
        # Find root nodes (no parent)
        root_nodes = [node for node in self.nodes.values() if node.parent_id is None]
        
        def arrange_subtree(node: DialogueNode, level: int, index: int):
            """Recursively arrange subtree"""
            x = 50 + (level * level_width)
            y = 50 + (index * level_height)
            
            # Update position
            node.position = QPointF(x, y)
            if node.id in self.node_items:
                self.node_items[node.id].setPos(x, y)
            
            # Arrange children
            children = [self.nodes[child_id] for child_id in node.child_ids 
                       if child_id in self.nodes]
            
            for i, child in enumerate(children):
                arrange_subtree(child, level + 1, i)
        
        # Arrange all root nodes
        for i, root in enumerate(root_nodes):
            arrange_subtree(root, 0, i)
        
        # Update connections
        for connection in self.connections:
            connection.update_position()
    
    @Slot()
    def _clear_all(self):
        """Clear all nodes and connections"""
        reply = QMessageBox.question(
            self, "Clear All", 
            "Are you sure you want to clear all dialogue nodes?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Clear scene
        self.scene.clear()
        
        # Clear storage
        self.nodes.clear()
        self.node_items.clear()
        self.connections.clear()
        self.next_node_id = 1
        
        # Clear properties
        self._clear_properties_display()
        
        # Emit change signal
        self._emit_dialogue_changed()
    
    def _emit_dialogue_changed(self):
        """Emit dialogue changed signal with current dialogue data"""
        dialogues = []
        for node in self.nodes.values():
            dialogues.append({
                'id': node.id,
                'text': node.text,
                'speaker': node.speaker,
                'type': node.dialogue_type,
                'voice_file': node.voice_file,
                'conditions': node.conditions
            })
        
        self.dialogue_changed.emit(dialogues)
    
    def get_dialogues(self) -> List[Dict]:
        """Get all dialogues as list of dictionaries"""
        dialogues = []
        for node in self.nodes.values():
            dialogues.append({
                'id': node.id,
                'text': node.text,
                'speaker': node.speaker,
                'type': node.dialogue_type,
                'voice_file': node.voice_file,
                'conditions': node.conditions
            })
        
        return dialogues
    
    def get_dialogue_count(self) -> int:
        """Get total number of dialogue nodes"""
        return len(self.nodes)
    
    def load_dialogues(self, dialogues: List[Dict]):
        """Load existing dialogues into the editor"""
        self._clear_all()
        
        for dlg in dialogues:
            node_id = dlg.get('id', f"node_{self.next_node_id}")
            if node_id.startswith("node_"):
                # Extract number for ID generation
                try:
                    num = int(node_id.split("_")[1])
                    if num >= self.next_node_id:
                        self.next_node_id = num + 1
                except:
                    pass
            else:
                self.next_node_id += 1
            
            node = DialogueNode(
                id=node_id,
                text=dlg.get('text', ''),
                speaker=dlg.get('speaker', 'NPC'),
                dialogue_type=dlg.get('type', 'Standard'),
                voice_file=dlg.get('voice_file'),
                conditions=dlg.get('conditions', []),
                position=QPointF(100, 100 + (self.next_node_id * 30))
            )
            
            node_item = DialogueNodeItem(node, self)
            node_item.node_selected.connect(self._on_node_selected)
            node_item.node_moved.connect(self._on_node_moved)
            node_item.node_deleted.connect(self._on_node_deleted)
            
            self.scene.addItem(node_item)
            self.nodes[node_id] = node
            self.node_items[node_id] = node_item
        
        # Auto-arrange after loading
        self._auto_arrange()
        
        # Emit change signal
        self._emit_dialogue_changed()


# Simple test function
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Test dialogue editor
    editor = DialogueTreeEditor()
    editor.setWindowTitle("Dialogue Editor Test")
    editor.resize(1000, 600)
    editor.show()
    
    # Test with some sample dialogues
    sample_dialogues = [
        {
            'id': 'node_1',
            'text': 'Welcome, adventurer! I have a quest for you.',
            'speaker': 'NPC',
            'type': 'Greeting'
        },
        {
            'id': 'node_2',
            'text': 'What kind of quest?',
            'speaker': 'Player',
            'type': 'Question'
        },
        {
            'id': 'node_3',
            'text': 'I need you to find a lost artifact.',
            'speaker': 'NPC',
            'type': 'Request'
        }
    ]
    
    editor.load_dialogues(sample_dialogues)
    
    sys.exit(app.exec())