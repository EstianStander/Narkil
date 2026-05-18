from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go
import pandas as pd
import tempfile
import os

class KPICard(QFrame):
    def __init__(self, title, value, color="#ff5722"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e1e;
                border-radius: 10px;
                border: 1px solid #333;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #888; font-weight: bold;")
        layout.addWidget(title_label)
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 24px; color: {color}; font-weight: bold;")
        layout.addWidget(value_label)

class DashboardModule(QWidget):
    def __init__(self, db, company_id):
        super().__init__()
        self.db = db
        self.company_id = company_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        header = QLabel("Operations Overview")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff5722;")
        layout.addWidget(header)

        kpi_layout = QGridLayout()
        kpi_layout.addWidget(KPICard("Total Orders", "124"), 0, 0)
        kpi_layout.addWidget(KPICard("Active Production", "18", "#ff9800"), 0, 1)
        kpi_layout.addWidget(KPICard("Quality Pass Rate", "98.2%", "#4caf50"), 0, 2)
        kpi_layout.addWidget(KPICard("Pending Tickets", "5", "#f44336"), 0, 3)
        layout.addLayout(kpi_layout)

        charts_layout = QHBoxLayout()
        self.prod_chart = QWebEngineView()
        self.update_prod_chart()
        charts_layout.addWidget(self.prod_chart, 2)
        
        self.dist_chart = QWebEngineView()
        self.update_dist_chart()
        charts_layout.addWidget(self.dist_chart, 1)
        
        layout.addLayout(charts_layout)

    def update_prod_chart(self):
        df = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'Output': [450, 520, 490, 610, 580]
        })
        fig = go.Figure(data=go.Scatter(x=df['Month'], y=df['Output'], mode='lines+markers', line=dict(color='#ff5722', width=3)))
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=40, b=10))
        self._set_chart(self.prod_chart, fig)

    def update_dist_chart(self):
        labels = ['Iron', 'Steel', 'Aluminum', 'Others']
        values = [450, 210, 150, 80]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, marker=dict(colors=['#ff5722', '#ff9800', '#ffc107', '#444']))])
        fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=40, b=10))
        self._set_chart(self.dist_chart, fig)

    def _set_chart(self, view, fig):
        fd, path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        fig.write_html(path)
        view.setUrl(Qt.QUrl.fromLocalFile(path))
