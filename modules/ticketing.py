from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDialog, QLineEdit, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt
import datetime

class TicketDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Ticket")
        self.setFixedWidth(400)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.title_in = QLineEdit()
        self.title_in.setPlaceholderText("Title")
        layout.addWidget(self.title_in)

        self.pri_box = QComboBox()
        self.pri_box.addItems(["Low", "Medium", "High", "Critical"])
        layout.addWidget(self.pri_box)

        self.desc_in = QTextEdit()
        self.desc_in.setPlaceholderText("Description")
        layout.addWidget(self.desc_in)

        btn = QPushButton("SUBMIT TICKET")
        btn.setStyleSheet("background-color: #ff5722; color: white; padding: 10px; font-weight: bold;")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

class TicketingModule(QWidget):
    def __init__(self, db, company_id, user):
        super().__init__()
        self.db = db
        self.company_id = company_id
        self.user = user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        title = QLabel("Support & Maintenance Tickets")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff5722;")
        header.addWidget(title)
        header.addStretch()
        
        btn = QPushButton("+ New Ticket")
        btn.setObjectName("ActionBtn")
        btn.clicked.connect(self.add_ticket)
        header.addWidget(btn)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Priority", "Status", "Created"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        self.load_data()

    def add_ticket(self):
        d = TicketDialog(self)
        if d.exec():
            # Logic to save ticket to DB would go here
            self.load_data()

    def load_data(self):
        # Sample data
        data = [("TKT-001", "Furnace 1 Temp Sensor", "High", "Open", "2026-05-18")]
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(val))
