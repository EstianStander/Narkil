from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class OrdersModule(QWidget):
    def __init__(self, db, company_id):
        super().__init__()
        self.db = db
        self.company_id = company_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(24)

        # ── Page header ───────────────────────────────────────────────────
        header_row = QHBoxLayout()
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title = QLabel("Sales Orders & Quotations")
        title.setObjectName("PageTitle")
        sub = QLabel("Manage customer orders from quote to delivery")
        sub.setObjectName("PageSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(sub)
        header_row.addLayout(title_block)
        header_row.addStretch()

        btn = QPushButton("+ New Order")
        btn.setObjectName("ActionBtn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header_row.addWidget(btn)
        layout.addLayout(header_row)

        # ── Table ─────────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Order #", "Customer", "Product", "Qty", "Total", "Status"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table, 1)

        self.load_data()

    def load_data(self):
        data = [
            ("ORD-2026-001", "Global Auto",     "Engine Block",  "50",  "$25,000", "Production"),
            ("ORD-2026-002", "MetalWorks Co.",  "Pump Housing",  "120", "$18,500", "Pending"),
            ("ORD-2026-003", "Precision Parts", "Gear Casing",   "30",  "$9,200",  "Shipped"),
            ("ORD-2026-004", "TechDrive Ltd.",  "Brake Disc",    "200", "$44,000", "Quoted"),
        ]
        status_colors = {
            "Production": "#ff8c00",
            "Pending":    "#ffbb00",
            "Shipped":    "#00d48a",
            "Quoted":     "#7878b0",
        }
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if j == 5:
                    item.setForeground(QColor(status_colors.get(val, "#8888b0")))
                self.table.setItem(i, j, item)
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 48)

