"""
Element Table Widget
Displays all elements in the selected category
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                               QLineEdit, QHBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class ElementTableWidget(QWidget):
    """Table widget displaying elements in a category"""

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.current_elements = []
        self.filtered_elements = []
        self.page_size = 100
        self.current_page = 0

        # Setup UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search elements...")
        self.search_box.textChanged.connect(self.filter_elements)
        layout.addWidget(self.search_box)

        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)

        # Pagination controls
        pagination_layout = QHBoxLayout()

        self.page_label = QLabel("")
        pagination_layout.addWidget(self.page_label)

        pagination_layout.addStretch()

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.previous_page)
        pagination_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_button)

        layout.addLayout(pagination_layout)

        # Connect to data model signals
        self.data_model.category_changed.connect(self.on_category_changed)

    def on_category_changed(self, category):
        """Handle category change"""
        self.current_elements = self.data_model.get_elements(category)
        self.filtered_elements = self.current_elements[:]
        self.current_page = 0
        self.search_box.clear()
        self.populate_table()

    def populate_table(self):
        """Populate table with elements"""
        if not self.filtered_elements:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.update_pagination()
            return

        # Get sample element to determine columns
        sample = self.filtered_elements[0]
        if not hasattr(sample, '_fields'):
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        # Determine which fields to show (limit to important ones)
        display_fields = self.get_display_fields(sample)

        # Setup table with icon and name columns
        self.table.setColumnCount(len(display_fields) + 2)  # +2 for icon and name columns
        self.table.setHorizontalHeaderLabels(["Icon", "Name"] + display_fields)

        # Calculate page range
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.filtered_elements))

        # Populate rows
        self.table.setRowCount(end_idx - start_idx)

        for row_idx, element_idx in enumerate(range(start_idx, end_idx)):
            element = self.filtered_elements[element_idx]

            # Icon cell (column 0)
            icon_label = QLabel()
            icon_pixmap = self.data_model.get_icon_pixmap(self.data_model.current_category, element, size=(32, 32))
            if icon_pixmap:
                icon_label.setPixmap(icon_pixmap)
            else:
                icon_label.setText("No Icon")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row_idx, 0, icon_label)

            # Name cell (column 1)
            name_text = self._get_element_name(element)
            name_item = QTableWidgetItem(name_text)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Read-only
            name_item.setData(Qt.ItemDataRole.UserRole, element_idx)  # Store actual index
            self.table.setItem(row_idx, 1, name_item)

            # Data cells (starting from column 2)
            for col_idx, field_name in enumerate(display_fields):
                try:
                    value = getattr(element, field_name)
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Read-only
                    item.setData(Qt.ItemDataRole.UserRole, element_idx)  # Store actual index
                    self.table.setItem(row_idx, col_idx + 2, item)  # +2 because icon and name are columns 0-1
                except:
                    item = QTableWidgetItem("")
                    self.table.setItem(row_idx, col_idx + 2, item)

        # Resize columns
        self.table.resizeColumnsToContents()
        self.update_pagination()

    def _get_element_name(self, element) -> str:
        """Extract name from element, trying common name fields"""
        # Special handling for weapons - check mapping first
        if self.data_model.current_category == "weapons":
            if hasattr(element, 'item_id'):
                weapon_name = self.data_model.get_weapon_name(element.item_id)
                if weapon_name:
                    return weapon_name

        # Try common name fields in order of preference
        name_fields = ['name', 'item_name', 'spell_name', 'creature_name', 'building_name']

        for field_name in name_fields:
            if hasattr(element, field_name):
                name_value = getattr(element, field_name)
                if name_value:
                    return str(name_value)

        # Fallback: try to construct a name from ID fields
        id_fields = ['item_id', 'spell_id', 'creature_id', 'building_id']
        for field_name in id_fields:
            if hasattr(element, field_name):
                id_value = getattr(element, field_name)
                if id_value is not None:
                    return f"{field_name.replace('_id', '').title()} {id_value}"

        # Last resort
        return "Unknown"

    def get_display_fields(self, element) -> list:
        """Get list of fields to display (first 6 important ones)"""
        fields = list(element._fields.keys())

        # Prioritize certain fields (excluding 'name' since it's shown in dedicated column)
        priority_fields = ['item_id', 'spell_id', 'creature_id', 'building_id',
                          'level', 'item_type', 'item_subtype']

        # Get priority fields that exist
        display = []
        for pf in priority_fields:
            if pf in fields:
                display.append(pf)
                if len(display) >= 6:
                    break

        # Add remaining fields if needed
        for f in fields:
            if f not in display:
                display.append(f)
                if len(display) >= 6:
                    break

        return display

    def filter_elements(self, text):
        """Filter elements by search text"""
        if not text:
            self.filtered_elements = self.current_elements[:]
        else:
            self.filtered_elements = []
            text_lower = text.lower()

            for elem in self.current_elements:
                # Search in name field if it exists
                if hasattr(elem, 'name'):
                    if text_lower in str(elem.name).lower():
                        self.filtered_elements.append(elem)
                        continue

                # Search in all string fields
                for field_name in elem._fields.keys():
                    try:
                        value = getattr(elem, field_name)
                        if text_lower in str(value).lower():
                            self.filtered_elements.append(elem)
                            break
                    except:
                        pass

        self.current_page = 0
        self.populate_table()

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.populate_table()

    def next_page(self):
        """Go to next page"""
        max_page = (len(self.filtered_elements) - 1) // self.page_size
        if self.current_page < max_page:
            self.current_page += 1
            self.populate_table()

    def update_pagination(self):
        """Update pagination controls"""
        total_pages = max(1, (len(self.filtered_elements) + self.page_size - 1) // self.page_size)
        start_idx = self.current_page * self.page_size + 1
        end_idx = min(start_idx + self.page_size - 1, len(self.filtered_elements))

        self.page_label.setText(
            f"Showing {start_idx}-{end_idx} of {len(self.filtered_elements)} "
            f"(Page {self.current_page + 1}/{total_pages})"
        )

        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)

    def on_selection_changed(self):
        """Handle element selection"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(self.table.row(item))

        if selected_rows:
            # Get the first selected row
            row = list(selected_rows)[0]
            # Get element index from the name column (column 1, since 0 is icon)
            name_item = self.table.item(row, 1)
            if name_item:
                element_idx = name_item.data(Qt.ItemDataRole.UserRole)
                if element_idx is not None:
                    self.data_model.current_element_index = element_idx
                    self.data_model.element_selected.emit(
                        self.data_model.current_category,
                        element_idx
                    )

    def refresh(self):
        """Refresh the table"""
        if self.data_model.current_category:
            self.on_category_changed(self.data_model.current_category)
