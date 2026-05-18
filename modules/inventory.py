from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame)
from PyQt6.QtCore import Qt


class InventoryModule(QWidget):
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
        title = QLabel("Inventory & Materials")
        title.setObjectName("PageTitle")
        sub = QLabel("Track raw materials, alloys, and finished goods")
        sub.setObjectName("PageSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(sub)
        header_row.addLayout(title_block)
        header_row.addStretch()

        add_btn = QPushButton("+ Add Stock")
        add_btn.setObjectName("ActionBtn")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        # ── Stat cards ────────────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        cards_row.addWidget(self._stat_card("Raw Materials", "450 Tons",  "CardFire"))
        cards_row.addWidget(self._stat_card("Alloys",        "12 Tons",   "CardAmber"))
        cards_row.addWidget(self._stat_card("Finished Goods","1,240 Units","CardGold"))
        cards_row.addWidget(self._stat_card("Low Stock Alerts", "3",      "CardRed"))
        layout.addLayout(cards_row)

        # ── Inventory table ───────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Item Name", "Category", "Quantity", "Unit", "Last Updated"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table, 1)

        self.load_data()

    def _stat_card(self, title, value, card_name="CardFire"):
        card = QFrame()
        card.setObjectName(card_name)
        card.setMinimumHeight(90)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(6)

        t = QLabel(title.upper())
        t.setStyleSheet("font-size: 10px; color: #55557a; font-weight: 700; letter-spacing: 1.5px;")

        colors = {"CardFire": "#ff5500", "CardAmber": "#ff8c00",
                  "CardGold": "#ffbb00", "CardRed": "#ff3050"}
        v = QLabel(value)
        v.setStyleSheet(f"font-size: 22px; color: {colors.get(card_name,'#ff5500')}; font-weight: 800;")

        lay.addWidget(t)
        lay.addWidget(v)
        lay.addStretch()
        return card

    def load_data(self):
        data = [
            ("Scrap Iron",      "Raw Material",  "320",  "Tons",  "2026-05-18"),
            ("Ferro-Silicon",   "Alloy",         "1.5",  "Tons",  "2026-05-17"),
            ("Bentonite",       "Sand Additive", "500",  "Kg",    "2026-05-18"),
            ("Engine Block #X1","Finished Goods","45",   "Units", "2026-05-16"),
            ("Coke",            "Fuel",          "12",   "Tons",  "2026-05-15"),
        ]
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(i, j, item)
        self.table.setRowHeight(0, 48)
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 48)

