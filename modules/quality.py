from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFrame)
from PyQt6.QtCore import Qt

class QualityModule(QWidget):
    def __init__(self, db, company_id):
        super().__init__()
        self.db = db
        self.company_id = company_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        title = QLabel("Quality Assurance & Traceability")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff5722;")
        header.addWidget(title)
        header.addStretch()
        
        cert_btn = QPushButton("New Inspection")
        cert_btn.setObjectName("ActionBtn")
        header.addWidget(cert_btn)
        layout.addLayout(header)

        # Quality Metrics
        metrics = QHBoxLayout()
        metrics.addWidget(self.create_metric("Scrap Rate", "2.4%", "#2ecc71"))
        metrics.addWidget(self.create_metric("Rework Rate", "1.1%", "#f1c40f"))
        metrics.addWidget(self.create_metric("Customer Returns", "0", "#3498db"))
        layout.addLayout(metrics)

        # Inspection History
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Batch ID", "Product", "Inspector", "Result", "Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.load_inspections()

    def create_metric(self, title, value, color):
        card = QFrame()
        card.setStyleSheet("background-color: #252525; border-radius: 8px; padding: 15px; border: 1px solid #333;")
        l = QVBoxLayout(card)
        t = QLabel(title)
        t.setStyleSheet("color: #888;")
        v = QLabel(value)
        v.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        l.addWidget(t)
        l.addWidget(v)
        return card

    def load_inspections(self):
        data = [
            ("B-2026-001", "Cylinder Head", "J. Smith", "Passed", "2026-05-18"),
            ("B-2026-002", "Flywheel", "A. Doe", "Passed", "2026-05-18"),
            ("B-2026-003", "Base Plate", "J. Smith", "Failed (Porosity)", "2026-05-17"),
        ]
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(val)
                if val == "Passed": item.setForeground(Qt.GlobalColor.green)
                if "Failed" in val: item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(i, j, item)
