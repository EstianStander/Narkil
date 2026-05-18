from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFrame, QProgressBar)
from PyQt6.QtCore import Qt

class ProductionModule(QWidget):
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
        title = QLabel("Melt Control & Production Planning")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff5722;")
        header.addWidget(title)
        header.addStretch()
        
        plan_btn = QPushButton("New Melt Plan")
        plan_btn.setObjectName("ActionBtn")
        header.addWidget(plan_btn)
        layout.addLayout(header)

        # Active Furnace Section
        furnace_label = QLabel("Active Furnaces")
        furnace_label.setStyleSheet("font-size: 18px; color: #e0e0e0; margin-top: 10px;")
        layout.addWidget(furnace_label)

        furnace_layout = QHBoxLayout()
        furnace_layout.addWidget(self.create_furnace_card("Furnace A", "Melting", 1450, 85))
        furnace_layout.addWidget(self.create_furnace_card("Furnace B", "Holding", 1380, 40))
        furnace_layout.addWidget(self.create_furnace_card("Furnace C", "Idle", 0, 0))
        layout.addLayout(furnace_layout)

        # Production Queue
        queue_label = QLabel("Production Queue")
        queue_label.setStyleSheet("font-size: 18px; color: #e0e0e0; margin-top: 20px;")
        layout.addWidget(queue_label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Order ID", "Product", "Stage", "Priority", "ETA"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.load_queue()

    def create_furnace_card(self, name, status, temp, progress):
        card = QFrame()
        card.setStyleSheet("background-color: #252525; border-radius: 10px; padding: 15px; border: 1px solid #333;")
        l = QVBoxLayout(card)
        
        n = QLabel(name)
        n.setStyleSheet("font-weight: bold; font-size: 16px; color: #ff5722;")
        l.addWidget(n)
        
        s = QLabel(f"Status: {status}")
        s.setStyleSheet("color: #aaa;")
        l.addWidget(s)
        
        t = QLabel(f"Temp: {temp}°C")
        t.setStyleSheet("color: #ff9800; font-weight: bold;")
        l.addWidget(t)
        
        pb = QProgressBar()
        pb.setValue(progress)
        pb.setStyleSheet("""
            QProgressBar { border: 1px solid #444; border-radius: 5px; text-align: center; height: 10px; color: white; }
            QProgressBar::chunk { background-color: #ff5722; }
        """)
        l.addWidget(pb)
        
        return card

    def load_queue(self):
        data = [
            ("ORD-101", "Gear Housing", "Molding", "High", "2h"),
            ("ORD-102", "Pump Body", "Melting", "Normal", "4h"),
            ("ORD-105", "Brake Disc", "Core Making", "Low", "Tomorrow"),
        ]
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(val))
