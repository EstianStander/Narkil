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
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(24)

        # ── Page header ───────────────────────────────────────────────────
        header_row = QHBoxLayout()
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        title = QLabel("Production & Melt Control")
        title.setObjectName("PageTitle")
        sub = QLabel("Monitor furnace status and manage production queue")
        sub.setObjectName("PageSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(sub)
        header_row.addLayout(title_block)
        header_row.addStretch()

        plan_btn = QPushButton("New Melt Plan")
        plan_btn.setObjectName("ActionBtn")
        plan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header_row.addWidget(plan_btn)
        layout.addLayout(header_row)

        # ── Furnace section ───────────────────────────────────────────────
        section_lbl = QLabel("ACTIVE FURNACES")
        section_lbl.setObjectName("SectionLabel")
        layout.addWidget(section_lbl)

        furnaces_row = QHBoxLayout()
        furnaces_row.setSpacing(16)
        furnaces_row.addWidget(self._furnace_card("Furnace A", "Melting",  1450, 85))
        furnaces_row.addWidget(self._furnace_card("Furnace B", "Holding",  1380, 40))
        furnaces_row.addWidget(self._furnace_card("Furnace C", "Idle",     0,    0))
        layout.addLayout(furnaces_row)

        # ── Production queue ──────────────────────────────────────────────
        queue_lbl = QLabel("PRODUCTION QUEUE")
        queue_lbl.setObjectName("SectionLabel")
        layout.addWidget(queue_lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Order ID", "Product", "Stage", "Priority", "ETA"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table, 1)

        self.load_queue()

    def _furnace_card(self, name, status, temp, progress):
        card = QFrame()
        card.setObjectName("Card")
        card.setMinimumHeight(160)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(12)

        status_colors = {"Melting": "#ff5500", "Holding": "#ff8c00", "Idle": "#44446a"}
        color = status_colors.get(status, "#44446a")

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("font-size: 17px; font-weight: 700; color: #e0e0f8;")
        lay.addWidget(name_lbl)

        status_row = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {color}; font-size: 10px;")
        s_lbl = QLabel(status)
        s_lbl.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")
        status_row.addWidget(dot)
        status_row.addWidget(s_lbl)
        status_row.addStretch()
        lay.addLayout(status_row)

        if temp > 0:
            t_lbl = QLabel(f"{temp} °C")
            t_lbl.setStyleSheet("color: #ff8c00; font-size: 22px; font-weight: 700;")
            lay.addWidget(t_lbl)

        pb = QProgressBar()
        pb.setValue(progress)
        pb.setTextVisible(False)
        lay.addWidget(pb)

        pct_lbl = QLabel(f"{progress}% capacity")
        pct_lbl.setStyleSheet("font-size: 11px; color: #44446a;")
        lay.addWidget(pct_lbl)
        lay.addStretch()
        return card

    def load_queue(self):
        data = [
            ("ORD-101", "Gear Housing",  "Molding",    "High",   "2h"),
            ("ORD-102", "Pump Body",     "Melting",    "Normal", "4h"),
            ("ORD-105", "Brake Disc",    "Core Making","Low",    "Tomorrow"),
            ("ORD-108", "Valve Housing", "Finishing",  "High",   "6h"),
        ]
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if j == 3:  # Priority column colour
                    colors = {"High": "#ff5500", "Normal": "#8888b0", "Low": "#44446a"}
                    item.setForeground(
                        __import__("PyQt6.QtGui", fromlist=["QColor"]).QColor(
                            colors.get(val, "#8888b0")
                        )
                    )
                self.table.setItem(i, j, item)
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 48)

