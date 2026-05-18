from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFrame, QLineEdit, QComboBox,
                             QGridLayout, QProgressBar, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

class CalculatorModule(QWidget):
    def __init__(self, db, company_id):
        super().__init__()
        self.db = db
        self.company_id = company_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # ── Header ────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title_block = QVBoxLayout()
        title = QLabel("Spectral Charge Calculator")
        title.setStyleSheet("font-size: 32px; font-weight: 800; color: white;")
        sub = QLabel("Foundry Melt Chemistry Optimizer & Least Cost Charge Calculation")
        sub.setStyleSheet("color: rgba(255, 255, 255, 0.4); font-size: 14px;")
        title_block.addWidget(title)
        title_block.addWidget(sub)
        header.addLayout(title_block)
        header.addStretch()
        
        btn_optimize = QPushButton("Optimize Charge")
        btn_optimize.setObjectName("ActionBtn")
        header.addWidget(btn_optimize)
        layout.addLayout(header)

        # ── Main Content Split ────────────────────────────────────────────
        content = QHBoxLayout()
        content.setSpacing(30)

        # Left: Material Input & Charge Grid
        left_panel = QVBoxLayout()
        left_panel.setSpacing(20)
        
        input_card = QFrame()
        input_card.setObjectName("Card")
        input_card.setStyleSheet("background-color: rgba(26, 26, 48, 0.4); border-radius: 18px; border: 1px solid rgba(255, 255, 255, 0.05);")
        input_lay = QVBoxLayout(input_card)
        input_lay.setContentsMargins(20, 20, 20, 20)
        
        top_inputs = QGridLayout()
        top_inputs.addWidget(QLabel("BATCH SIZE (KG)"), 0, 0)
        batch_size = QLineEdit("1000")
        top_inputs.addWidget(batch_size, 1, 0)
        
        top_inputs.addWidget(QLabel("TARGET ALLOY"), 0, 1)
        alloy_box = QComboBox()
        alloy_box.addItems(["Ductile Iron GGG40", "Gray Iron GG25", "Steel Low Carbon"])
        top_inputs.addWidget(alloy_box, 1, 1)
        input_lay.addLayout(top_inputs)
        
        left_panel.addWidget(input_card)

        charge_grid = QTableWidget(5, 4)
        charge_grid.setHorizontalHeaderLabels(["Material", "Weight (kg)", "%", "Cost"])
        charge_grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        charge_grid.setObjectName("Card")
        left_panel.addWidget(charge_grid, 1)
        
        content.addLayout(left_panel, 3)

        # Right: Results & Deviation
        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)
        
        results_card = QFrame()
        results_card.setObjectName("Card")
        results_card.setStyleSheet("background-color: rgba(26, 26, 48, 0.4); border-radius: 18px;")
        res_lay = QVBoxLayout(results_card)
        res_lay.setContentsMargins(24, 24, 24, 24)
        
        res_title = QLabel("ELEMENTAL ANALYSIS")
        res_title.setStyleSheet("font-weight: 800; color: #ff5722; letter-spacing: 1px;")
        res_lay.addWidget(res_title)
        
        # Element Rows
        elements = [
            ("Carbon (C)", 3.4, 3.6, 3.8, 3.55, "Within Spec", "#00d48a"),
            ("Silicon (Si)", 2.2, 2.4, 2.6, 2.38, "Near Limit", "#ffbb00"),
            ("Manganese (Mn)", 0.3, 0.5, 0.7, 0.48, "Within Spec", "#00d48a"),
        ]
        
        for el, mi, ta, ma, cu, st, co in elements:
            el_box = QVBoxLayout()
            txt_row = QHBoxLayout()
            txt_row.addWidget(QLabel(el))
            txt_row.addStretch()
            val_lbl = QLabel(f"{cu}%")
            val_lbl.setStyleSheet(f"color: {co}; font-weight: 700;")
            txt_row.addWidget(val_lbl)
            el_box.addLayout(txt_row)
            
            prog = QProgressBar()
            prog.setRange(0, 100)
            prog.setValue(int((cu-mi)/(ma-mi)*100) if ma > mi else 50)
            prog.setTextVisible(False)
            prog.setFixedHeight(6)
            prog.setStyleSheet(f"QProgressBar::chunk {{ background-color: {co}; border-radius: 3px; }}")
            el_box.addWidget(prog)
            res_lay.addLayout(el_box)
            res_lay.addSpacing(10)
            
        right_panel.addWidget(results_card)
        
        # Summary Card
        summary = QFrame()
        summary.setObjectName("Card")
        sum_lay = QVBoxLayout(summary)
        sum_lay.addWidget(QLabel("TOTAL COST: $1,420.50"))
        sum_lay.addWidget(QLabel("COMPLIANCE SCORE: 98%"))
        right_panel.addWidget(summary)
        
        content.addLayout(right_panel, 2)
        layout.addLayout(content, 1)
