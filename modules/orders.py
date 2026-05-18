from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView)
from PyQt6.QtCore import Qt

class OrdersModule(QWidget):
    def __init__(self, db, company_id):
        super().__init__()
        self.db = db
        self.company_id = company_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        title = QLabel("Sales Orders & Quotations")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff5722;")
        header.addWidget(title)
        header.addStretch()
        
        btn = QPushButton("+ New Order")
        btn.setObjectName("ActionBtn")
        header.addWidget(btn)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Order #", "Customer", "Product", "Qty", "Total", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        data = [("ORD-2026-001", "Global Auto", "Engine Block", "50", "$25,000", "Production")]
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(val))
