from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class QualityModule(QWidget):
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
        title = QLabel("Quality Assurance & Traceability")
        title.setObjectName("PageTitle")
        sub = QLabel("Inspection records, scrap rates, and batch traceability")
        sub.setObjectName("PageSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(sub)
        header_row.addLayout(title_block)
        header_row.addStretch()

        cert_btn = QPushButton("New Inspection")
        cert_btn.setObjectName("ActionBtn")
        cert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header_row.addWidget(cert_btn)
        layout.addLayout(header_row)

        # ── Metric cards ──────────────────────────────────────────────────
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(16)
        metrics_row.addWidget(self._metric_card("Scrap Rate",        "2.4%", "CardGreen"))
        metrics_row.addWidget(self._metric_card("Rework Rate",       "1.1%", "CardAmber"))
        metrics_row.addWidget(self._metric_card("Customer Returns",  "0",    "CardFire"))
        metrics_row.addWidget(self._metric_card("Passed Inspections","47",   "CardGold"))
        layout.addLayout(metrics_row)

        # ── Inspection table ──────────────────────────────────────────────
        section_lbl = QLabel("RECENT INSPECTIONS")
        section_lbl.setObjectName("SectionLabel")
        layout.addWidget(section_lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Batch ID", "Product", "Inspector", "Result", "Date"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table, 1)

        self.load_inspections()

    def _metric_card(self, title, value, card_name):
        card = QFrame()
        card.setObjectName(card_name)
        card.setMinimumHeight(100)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(6)

        colors = {"CardGreen": "#00d48a", "CardAmber": "#ff8c00",
                  "CardFire": "#ff5500", "CardGold": "#ffbb00", "CardRed": "#ff3050"}

        t = QLabel(title.upper())
        t.setStyleSheet("font-size: 10px; color: #55557a; font-weight: 700; letter-spacing: 1.5px;")
        v = QLabel(value)
        v.setStyleSheet(f"font-size: 26px; color: {colors.get(card_name,'#ff5500')}; font-weight: 800;")
        lay.addWidget(t)
        lay.addWidget(v)
        lay.addStretch()
        return card

    def load_inspections(self):
        data = [
            ("B-2026-001", "Cylinder Head", "J. Smith", "Passed",          "2026-05-18"),
            ("B-2026-002", "Flywheel",      "A. Doe",   "Passed",          "2026-05-18"),
            ("B-2026-003", "Base Plate",    "J. Smith", "Failed (Porosity)","2026-05-17"),
            ("B-2026-004", "Gear Casing",   "B. Chen",  "Passed",          "2026-05-16"),
            ("B-2026-005", "Pump Body",     "A. Doe",   "Rework",          "2026-05-15"),
        ]
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if j == 3:
                    if val == "Passed":
                        item.setForeground(QColor("#00d48a"))
                    elif "Failed" in val:
                        item.setForeground(QColor("#ff3050"))
                    elif val == "Rework":
                        item.setForeground(QColor("#ffbb00"))
                self.table.setItem(i, j, item)
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 48)

