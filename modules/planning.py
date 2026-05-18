from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt
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
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Production Timeline & Scheduling")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff5722;")
        layout.addWidget(title)

        self.gantt = QWebEngineView()
        self.update_gantt()
        layout.addWidget(self.gantt)

    def update_gantt(self):
        df = [
            dict(Task="Furnace 1: Melt #A1", Start='2026-05-18', Finish='2026-05-19', Resource='Melting'),
            dict(Task="Molding Line 1: Batch X", Start='2026-05-19', Finish='2026-05-21', Resource='Molding'),
            dict(Task="Finishing: Order #001", Start='2026-05-21', Finish='2026-05-23', Resource='Finishing')
        ]
        fig = ff.create_gantt(df, index_col='Resource', show_colorbar=True, group_tasks=True)
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=40, b=10))
        
        fd, path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        fig.write_html(path)
        self.gantt.setUrl(Qt.QUrl.fromLocalFile(path))
