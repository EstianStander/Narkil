from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QGridLayout, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go
import pandas as pd
import tempfile
import os


class KPICard(QFrame):
    """Premium KPI card with coloured top-accent bar."""

    def __init__(self, title, value, subtitle="", card_name="CardFire"):
        super().__init__()
        self.setObjectName(card_name)
        self.setMinimumHeight(112)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(6)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(
            "font-size: 10px; color: #55557a; font-weight: 700; letter-spacing: 1.5px;"
        )
        lay.addWidget(title_lbl)

        val_colors = {
            "CardFire":  "#ff5500",
            "CardAmber": "#ff8c00",
            "CardGreen": "#00d48a",
            "CardRed":   "#ff3050",
            "CardGold":  "#ffbb00",
        }
        color = val_colors.get(card_name, "#ff5500")

        val_lbl = QLabel(str(value))
        val_lbl.setStyleSheet(
            f"font-size: 30px; color: {color}; font-weight: 800; letter-spacing: -0.5px;"
        )
        lay.addWidget(val_lbl)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setStyleSheet("font-size: 11px; color: #44446a;")
            lay.addWidget(sub_lbl)

        lay.addStretch()


class DashboardModule(QWidget):
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
        title = QLabel("Operations Overview")
        title.setObjectName("PageTitle")
        sub = QLabel("Real-time production intelligence at a glance")
        sub.setObjectName("PageSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(sub)
        header_row.addLayout(title_block)
        header_row.addStretch()
        layout.addLayout(header_row)

        # ── KPI row ───────────────────────────────────────────────────────
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)
        kpi_row.addWidget(KPICard("Total Orders",       "124",   "↑ 8% this month",     "CardFire"))
        kpi_row.addWidget(KPICard("Active Production",  "18",    "6 furnaces online",   "CardAmber"))
        kpi_row.addWidget(KPICard("Quality Pass Rate",  "98.2%", "Industry avg 95.1%",  "CardGreen"))
        kpi_row.addWidget(KPICard("Pending Tickets",    "5",     "2 critical",          "CardRed"))
        layout.addLayout(kpi_row)

        # ── Charts row ────────────────────────────────────────────────────
        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        prod_wrap = self._chart_card("Monthly Production Output")
        self.prod_chart = QWebEngineView()
        self.prod_chart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        prod_wrap.layout().addWidget(self.prod_chart)
        self.update_prod_chart()
        charts_row.addWidget(prod_wrap, 2)

        dist_wrap = self._chart_card("Material Distribution")
        self.dist_chart = QWebEngineView()
        self.dist_chart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        dist_wrap.layout().addWidget(self.dist_chart)
        self.update_dist_chart()
        charts_row.addWidget(dist_wrap, 1)

        layout.addLayout(charts_row, 1)

    def _chart_card(self, title):
        card = QFrame()
        card.setObjectName("Card")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(0, 0, 0, 0)
        card_lay.setSpacing(0)

        title_bar = QWidget()
        title_bar.setStyleSheet("background: transparent;")
        tb_lay = QHBoxLayout(title_bar)
        tb_lay.setContentsMargins(20, 16, 20, 12)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #a0a0c8;")
        tb_lay.addWidget(lbl)
        tb_lay.addStretch()
        card_lay.addWidget(title_bar)
        return card

    def update_prod_chart(self):
        df = pd.DataFrame({
            "Month":  ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Output": [450, 520, 490, 610, 580, 645],
        })
        fig = go.Figure(data=go.Scatter(
            x=df["Month"], y=df["Output"],
            mode="lines+markers",
            line=dict(color="#ff5500", width=2.5),
            marker=dict(color="#ff8c00", size=7, line=dict(color="#ff5500", width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(255,85,0,0.07)",
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=16, r=16, t=8, b=16),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
            font=dict(color="#7070a0", size=11),
        )
        self._set_chart(self.prod_chart, fig)

    def update_dist_chart(self):
        labels = ["Iron", "Steel", "Aluminum", "Others"]
        values = [450, 210, 150, 80]
        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=0.45,
            marker=dict(colors=["#ff5500", "#ff8c00", "#ffbb00", "#282848"],
                        line=dict(color="#0e0e1a", width=2)),
            textfont=dict(size=12, color="#f0f0f8"),
        )])
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=8, r=8, t=8, b=8),
            legend=dict(font=dict(color="#7070a0", size=11)),
            font=dict(color="#7070a0"),
        )
        self._set_chart(self.dist_chart, fig)

    def _set_chart(self, view, fig):
        fd, path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        fig.write_html(path)
        view.setUrl(QUrl.fromLocalFile(path))

