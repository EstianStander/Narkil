from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import plotly.figure_factory as ff
import tempfile
import os


class PlanningModule(QWidget):
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
        title = QLabel("Production Timeline & Scheduling")
        title.setObjectName("PageTitle")
        sub = QLabel("Gantt view of all active and upcoming production tasks")
        sub.setObjectName("PageSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(sub)
        header_row.addLayout(title_block)
        header_row.addStretch()

        refresh_btn = QPushButton("Refresh Timeline")
        refresh_btn.setObjectName("SecondaryBtn")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self.update_gantt)
        header_row.addWidget(refresh_btn)
        layout.addLayout(header_row)

        # ── Gantt ─────────────────────────────────────────────────────────
        self.gantt = QWebEngineView()
        layout.addWidget(self.gantt, 1)
        self.update_gantt()

    def update_gantt(self):
        tasks = [
            dict(Task="Furnace 1: Melt #A1",   Start="2026-05-18", Finish="2026-05-19", Resource="Melting"),
            dict(Task="Furnace 2: Melt #A2",   Start="2026-05-18", Finish="2026-05-20", Resource="Melting"),
            dict(Task="Molding Line 1: Batch X", Start="2026-05-19", Finish="2026-05-21", Resource="Molding"),
            dict(Task="Molding Line 2: Batch Y", Start="2026-05-20", Finish="2026-05-22", Resource="Molding"),
            dict(Task="Finishing: Order #001",  Start="2026-05-21", Finish="2026-05-23", Resource="Finishing"),
            dict(Task="Finishing: Order #002",  Start="2026-05-22", Finish="2026-05-24", Resource="Finishing"),
        ]
        colors = {
            "Melting":   "#ff5500",
            "Molding":   "#ff8c00",
            "Finishing": "#ffbb00",
        }
        fig = ff.create_gantt(
            tasks, index_col="Resource", colors=colors,
            show_colorbar=True, group_tasks=True, showgrid_x=True,
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(14,14,26,1)",
            margin=dict(l=16, r=16, t=16, b=16),
            font=dict(color="#7070a0", size=11),
        )
        fd, path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        fig.write_html(path)
        self.gantt.setUrl(QUrl.fromLocalFile(path))

