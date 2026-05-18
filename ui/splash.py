import os
import sys

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QApplication, QFrame,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap


def _resource_path(relative):
    """Resolve a resource path that works both in development and PyInstaller builds."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        # ui/splash.py lives one level below the project root
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base, relative)


_LOAD_STEPS = [
    "Initializing system modules...",
    "Connecting to database...",
    "Loading production engine...",
    "Preparing inventory systems...",
    "Calibrating planning tools...",
    "Finalizing quality controls...",
    "System ready.",
]


class SplashScreen(QWidget):
    """Frameless animated splash screen shown on application launch."""

    def __init__(self):
        super().__init__()
        self._step = 0
        self._callback = None
        self._timer = QTimer(self)
        self._timer.setInterval(310)
        self._timer.timeout.connect(self._tick)
        self._setup_ui()
        self._center()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------
    def _setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(560, 400)

        # Outer transparent layout — the rounded "card" lives inside
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("SplashCard")
        card.setFixedSize(560, 400)
        card.setStyleSheet(
            "QFrame#SplashCard {"
            "  background-color: #0e0e1c;"
            "  border-radius: 18px;"
            "  border: 1px solid #1e1e3a;"
            "}"
        )
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(80, 52, 80, 38)
        layout.setSpacing(0)

        # ── Logo ──────────────────────────────────────────────────────
        logo = QLabel()
        pixmap = QPixmap(_resource_path("assets/logo.png"))
        logo.setPixmap(
            pixmap.scaled(
                100, 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("background: transparent;")
        layout.addWidget(logo)
        layout.addSpacing(16)

        # ── App name ──────────────────────────────────────────────────
        app_name = QLabel("NARKIL")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet(
            "background: transparent;"
            "color: #ff5722;"
            "font-size: 38px;"
            "font-weight: 900;"
            "letter-spacing: 14px;"
        )
        layout.addWidget(app_name)
        layout.addSpacing(6)

        # ── Subtitle ──────────────────────────────────────────────────
        subtitle = QLabel("ENTERPRISE RESOURCE PLANNING")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            "background: transparent;"
            "color: #38385a;"
            "font-size: 9px;"
            "letter-spacing: 5px;"
        )
        layout.addWidget(subtitle)
        layout.addStretch()

        # ── Progress bar ──────────────────────────────────────────────
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(5)
        self.progress.setStyleSheet(
            "QProgressBar {"
            "  background-color: #1a1a2e;"
            "  border: none;"
            "  border-radius: 2px;"
            "}"
            "QProgressBar::chunk {"
            "  background: qlineargradient("
            "    x1:0, y1:0, x2:1, y2:0,"
            "    stop:0 #b71c1c, stop:0.5 #ff5722, stop:1 #ffa726"
            "  );"
            "  border-radius: 2px;"
            "}"
        )
        layout.addWidget(self.progress)
        layout.addSpacing(10)

        # ── Status label ──────────────────────────────────────────────
        self.status = QLabel(_LOAD_STEPS[0])
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet(
            "background: transparent;"
            "color: #38385a;"
            "font-size: 10px;"
            "letter-spacing: 1px;"
        )
        layout.addWidget(self.status)

    def _center(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------
    def start(self, callback):
        """Start the loading animation; `callback` is invoked when done."""
        self._callback = callback
        self._timer.start()

    def _tick(self):
        if self._step < len(_LOAD_STEPS):
            self.status.setText(_LOAD_STEPS[self._step])
            val = int((self._step + 1) / len(_LOAD_STEPS) * 100)
            self.progress.setValue(val)
            self._step += 1
        else:
            self._timer.stop()
            QTimer.singleShot(420, self._finish)

    def _finish(self):
        self.close()
        if self._callback:
            self._callback()
