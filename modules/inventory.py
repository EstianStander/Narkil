from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFrame, QSplitter)
from PyQt6.QtCore import Qt

class InventoryModule(QWidget):
    def __init__(self, db, company_id):
        super().__init__()
        self.db = db
        self.company_id = company_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        title = QLabel("Inventory & Material Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff5722;")
        header.addWidget(title)
        header.addStretch()
        
        add_btn = QPushButton("+ Add Stock")
        add_btn.setObjectName("ActionBtn")
        header.addWidget(add_btn)
        layout.addLayout(header)

        # Main Content with Splitter
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Summary Cards
        summary_frame = QFrame()
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.addWidget(self.create_stat_card("Raw Materials", "450 Tons"))
        summary_layout.addWidget(self.create_stat_card("Alloys", "12 Tons"))
        summary_layout.addWidget(self.create_stat_card("Finished Castings", "1,240 Units"))
        summary_layout.addWidget(self.create_stat_card("Low Stock Alerts", "3", "#e74c3c"))
        splitter.addWidget(summary_frame)

        # Inventory Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Item Name", "Category", "Quantity", "Unit", "Last Updated"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        splitter.addWidget(self.table)

        layout.addWidget(splitter)
        self.load_data()

    def create_stat_card(self, title, value, color="#ff5722"):
        card = QFrame()
        card.setStyleSheet(f"background-color: #252525; border-radius: 8px; border: 1px solid #333; padding: 15px;")
        l = QVBoxLayout(card)
        t = QLabel(title)
        t.setStyleSheet("color: #888; font-size: 12px;")
        v = QLabel(value)
        v.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")
        l.addWidget(t)
        l.addWidget(v)
        return card

    def load_data(self):
        # Mock data for now
        data = [
            ("Scrap Iron", "Raw Material", "320", "Tons", "2026-05-18"),
            ("Ferro-Silicon", "Alloy", "1.5", "Tons", "2026-05-17"),
            ("Bentonite", "Sand Additive", "500", "Kg", "2026-05-18"),
            ("Engine Block #X1", "Finished Goods", "45", "Units", "2026-05-16"),
        ]
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(val))
