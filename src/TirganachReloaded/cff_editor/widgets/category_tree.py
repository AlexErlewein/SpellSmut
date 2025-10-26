"""
Category Tree Widget
Displays list of categories (tables) with entry counts
"""

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QLineEdit
from PySide6.QtCore import Qt


class CategoryTreeWidget(QWidget):
    """Tree widget displaying all categories"""

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search categories...")
        self.search_box.textChanged.connect(self.filter_categories)
        layout.addWidget(self.search_box)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Category", "Count"])
        self.tree.setAlternatingRowColors(True)
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)

    def populate(self):
        """Populate tree with categories"""
        self.tree.clear()

        categories = self.data_model.get_categories()

        for internal_name, display_name, count in categories:
            item = QTreeWidgetItem([display_name, str(count)])
            item.setData(0, Qt.UserRole, internal_name)  # Store internal name
            self.tree.addTopLevelItem(item)

        # Resize columns
        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)

    def filter_categories(self, text):
        """Filter categories by search text"""
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            visible = text.lower() in item.text(0).lower()
            item.setHidden(not visible)

    def on_item_clicked(self, item, column):
        """Handle category selection"""
        internal_name = item.data(0, Qt.UserRole)
        self.data_model.current_category = internal_name
        self.data_model.category_changed.emit(internal_name)

    def refresh(self):
        """Refresh the tree"""
        self.populate()
