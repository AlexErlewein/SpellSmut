"""
Element Table Widget
Displays all elements in the selected category
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                               QLineEdit, QHBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import Qt


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
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
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

        # Setup table
        self.table.setColumnCount(len(display_fields))
        self.table.setHorizontalHeaderLabels(display_fields)

        # Calculate page range
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.filtered_elements))

        # Populate rows
        self.table.setRowCount(end_idx - start_idx)

        for row_idx, element_idx in enumerate(range(start_idx, end_idx)):
            element = self.filtered_elements[element_idx]

            for col_idx, field_name in enumerate(display_fields):
                try:
                    value = getattr(element, field_name)
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Read-only
                    item.setData(Qt.UserRole, element_idx)  # Store actual index
                    self.table.setItem(row_idx, col_idx, item)
                except:
                    item = QTableWidgetItem("")
                    self.table.setItem(row_idx, col_idx, item)

        # Resize columns
        self.table.resizeColumnsToContents()
        self.update_pagination()

    def get_display_fields(self, element) -> list:
        """Get list of fields to display (first 6 important ones)"""
        fields = list(element._fields.keys())

        # Prioritize certain fields
        priority_fields = ['item_id', 'spell_id', 'creature_id', 'building_id',
                          'name', 'level', 'item_type', 'item_subtype']

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
        selected = self.table.selectedItems()
        if selected:
            # Get actual element index from first item in row
            element_idx = selected[0].data(Qt.UserRole)
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
