from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QLineEdit, QTextEdit, QComboBox,
                             QFrame, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import datetime


class TicketDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Support Ticket")
        self.setMinimumWidth(440)
        self.setStyleSheet("""
            QDialog {
                background-color: #0f0f1c;
                border: 1px solid #1c1c30;
                border-radius: 14px;
            }
            QLabel {
                color: #7070a0;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1.5px;
                margin-bottom: 2px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #131328;
                border: 1.5px solid #20203c;
                border-radius: 8px;
                padding: 10px 14px;
                color: #e0e0f0;
                font-size: 13px;
                margin-bottom: 4px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #ff5500;
            }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #ff5500;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #131328;
                border: 1px solid #20203c;
                color: #e0e0f0;
                selection-background-color: #ff5500;
                outline: none;
            }
        """)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(16)

        # Title
        hdr = QLabel("CREATE TICKET")
        hdr.setStyleSheet("font-size: 12px; font-weight: 800; color: #f0f0f8; letter-spacing: 3px;")
        root.addWidget(hdr)

        # Customer Selection
        root.addWidget(self._lbl("CUSTOMER"))
        self.customer_box = QComboBox()
        self.customer_box.addItem("Internal / General", None)
        # We will populate this from the module
        root.addWidget(self.customer_box)

        # Ticket title
        root.addWidget(self._lbl("TICKET TITLE"))
        self.title_in = QLineEdit()
        self.title_in.setPlaceholderText("Brief description of the issue")
        root.addWidget(self.title_in)

        # Priority
        root.addWidget(self._lbl("PRIORITY"))
        self.pri_box = QComboBox()
        self.pri_box.addItems(["Low", "Medium", "High", "Critical"])
        self.pri_box.setCurrentIndex(1)
        root.addWidget(self.pri_box)

        # Description
        root.addWidget(self._lbl("DESCRIPTION"))
        self.desc_in = QTextEdit()
        self.desc_in.setPlaceholderText("Detailed description, steps to reproduce, affected equipment…")
        self.desc_in.setMinimumHeight(100)
        root.addWidget(self.desc_in)

        root.addSpacing(8)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryBtn")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        submit_btn = QPushButton("Submit Ticket")
        submit_btn.setObjectName("ActionBtn")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.clicked.connect(self.accept)

        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(submit_btn)
        root.addLayout(btn_row)

    def _lbl(self, text):
        l = QLabel(text)
        return l

    def get_data(self):
        return {
            "customer_id": self.customer_box.currentData(),
            "customer_name": self.customer_box.currentText(),
            "title":    self.title_in.text().strip(),
            "priority": self.pri_box.currentText(),
            "desc":     self.desc_in.toPlainText().strip(),
        }


class TicketingModule(QWidget):
    def __init__(self, db, company_id, user):
        super().__init__()
        self.db = db
        self.company_id = company_id
        self.user = user
        self._tickets = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(24)

        # ── Page header ───────────────────────────────────────────────────
        header_row = QHBoxLayout()
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title = QLabel("Support & Maintenance Tickets")
        title.setObjectName("PageTitle")
        sub = QLabel("Track equipment issues, maintenance requests, and system alerts")
        sub.setObjectName("PageSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(sub)
        header_row.addLayout(title_block)
        header_row.addStretch()

        btn = QPushButton("+ New Ticket")
        btn.setObjectName("ActionBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.add_ticket)
        header_row.addWidget(btn)
        layout.addLayout(header_row)

        # ── Table ─────────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Title", "Priority", "Status", "Created"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table, 1)

        self.load_data()

    def add_ticket(self):
        d = TicketDialog(self)
        # Populate customers
        customers = self.db.get_customers(self.company_id)
        for c in customers:
            d.customer_box.addItem(c["name"], str(c["_id"]))
            
        if d.exec():
            data = d.get_data()
            if data["title"]:
                tid = f"TKT-{len(self._tickets) + 2:03d}"
                today = datetime.date.today().isoformat()
                self._tickets.append(
                    (tid, data["title"], data["priority"], "Open", today)
                )
                self.load_data()

    def load_data(self):
        base = [("TKT-001", "Furnace 1 Temp Sensor Fault", "High",   "Open",   "2026-05-18")]
        all_rows = base + self._tickets
        pri_colors = {
            "Critical": "#ff3050", "High": "#ff5500",
            "Medium":   "#ff8c00", "Low":  "#7878b0",
        }
        status_colors = {"Open": "#ffbb00", "Closed": "#00d48a", "In Progress": "#ff8c00"}
        self.table.setRowCount(len(all_rows))
        for i, row in enumerate(all_rows):
            for j, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if j == 2:
                    item.setForeground(QColor(pri_colors.get(val, "#8888b0")))
                elif j == 3:
                    item.setForeground(QColor(status_colors.get(val, "#8888b0")))
                self.table.setItem(i, j, item)
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 48)

