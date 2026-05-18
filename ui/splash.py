import os
import sys
import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QApplication, QFrame,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QLinearGradient, QRadialGradient, QPen, QBrush,
)


def _resource_path(relative):
    """Resolve a resource path that works both in development and PyInstaller builds."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
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


class _AnimatedCard(QFrame):
    """QFrame with a fully custom-painted animated background (no stylesheet)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frame = 0

    def advance(self):
        self._frame += 1
        self.update()

    def paintEvent(self, event):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        t = self._frame * 0.025

        # ── Base gradient ──────────────────────────────────────────────
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(14, 12, 26))
        grad.setColorAt(0.5, QColor(18, 15, 32))
        grad.setColorAt(1.0, QColor(10, 9, 20))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(self.rect(), 18, 18)

        # ── Pulsing radial glow around logo area ───────────────────────
        glow_alpha = int(16 + 10 * math.sin(t * 1.6))
        glow = QRadialGradient(w * 0.5, 95, 210)
        glow.setColorAt(0.0, QColor(255, 87, 34, glow_alpha))
        glow.setColorAt(1.0, QColor(255, 87, 34, 0))
        p.setBrush(QBrush(glow))
        p.drawRoundedRect(self.rect(), 18, 18)

        # ── Subtle grid ────────────────────────────────────────────────
        p.setPen(QPen(QColor(255, 87, 34, 7)))
        for x in range(0, w, 38):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, 38):
            p.drawLine(0, y, w, y)

        # ── Floating particles (drift upward-left) ─────────────────────
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(22):
            px = (w - int((i * 89.3 + t * 14) % (w + 60)))
            py = int((i * 53.7 + t * 7) % (h + 60)) - 20
            alpha = max(0, int(20 + 14 * math.sin(t * 1.4 + i)))
            sz = max(1, int(2 + math.sin(t * 0.8 + i * 0.5)))
            p.setBrush(QBrush(QColor(255, 87, 34, alpha)))
            p.drawEllipse(px, py, sz, sz)

        # ── Scan line ──────────────────────────────────────────────────
        scan_period = 160
        scan_y = int(((self._frame % scan_period) / scan_period) * (h + 60)) - 30
        sg = QLinearGradient(0, scan_y - 28, 0, scan_y + 28)
        sg.setColorAt(0.0, QColor(255, 87, 34, 0))
        sg.setColorAt(0.5, QColor(255, 87, 34, 22))
        sg.setColorAt(1.0, QColor(255, 87, 34, 0))
        p.setBrush(QBrush(sg))
        p.drawRect(0, max(0, scan_y - 28), w, 56)

        # ── Animated border glow ───────────────────────────────────────
        border_alpha = int(50 + 22 * math.sin(t * 0.9))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(255, 87, 34, border_alpha), 1))
        p.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 18, 18)

        p.end()


class SplashScreen(QWidget):
    """Frameless animated splash screen shown on application launch."""

    def __init__(self):
        super().__init__()
        self._step = 0
        self._callback = None
        self._anims: list = []

        # Loading tick timer
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(380)
        self._tick_timer.timeout.connect(self._tick)

        # Background animation (~30 fps)
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(33)
        self._anim_timer.timeout.connect(self._advance_frame)
        self._anim_timer.start()

        self._setup_ui()
        self._center()
        self._play_entrance()

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
        self.setFixedSize(580, 430)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._card = _AnimatedCard()
        self._card.setFixedSize(580, 430)
        outer.addWidget(self._card)

        layout = QVBoxLayout(self._card)
        layout.setContentsMargins(80, 54, 80, 44)
        layout.setSpacing(0)

        # ── Logo ──────────────────────────────────────────────────────
        self._logo_fx = QGraphicsOpacityEffect()
        self._logo_fx.setOpacity(0.0)
        logo = QLabel()
        logo.setPixmap(
            QPixmap(_resource_path("assets/logo.png")).scaled(
                100, 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("background: transparent;")
        logo.setGraphicsEffect(self._logo_fx)
        layout.addWidget(logo)
        layout.addSpacing(18)

        # ── App name ──────────────────────────────────────────────────
        self._title_fx = QGraphicsOpacityEffect()
        self._title_fx.setOpacity(0.0)
        app_name = QLabel("NARKIL")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet(
            "background: transparent;"
            "color: #ff5722;"
            "font-size: 42px;"
            "font-weight: 900;"
            "letter-spacing: 16px;"
        )
        app_name.setGraphicsEffect(self._title_fx)
        layout.addWidget(app_name)
        layout.addSpacing(8)

        # ── Subtitle ──────────────────────────────────────────────────
        self._sub_fx = QGraphicsOpacityEffect()
        self._sub_fx.setOpacity(0.0)
        subtitle = QLabel("ENTERPRISE RESOURCE PLANNING")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            "background: transparent;"
            "color: #8888aa;"
            "font-size: 9px;"
            "letter-spacing: 5px;"
        )
        subtitle.setGraphicsEffect(self._sub_fx)
        layout.addWidget(subtitle)
        layout.addStretch()

        # ── Progress bar ──────────────────────────────────────────────
        self._prog_fx = QGraphicsOpacityEffect()
        self._prog_fx.setOpacity(0.0)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setStyleSheet(
            "QProgressBar {"
            "  background-color: #1e1a35;"
            "  border: none;"
            "  border-radius: 3px;"
            "}"
            "QProgressBar::chunk {"
            "  background: qlineargradient("
            "    x1:0, y1:0, x2:1, y2:0,"
            "    stop:0 #b71c1c, stop:0.5 #ff5722, stop:1 #ffa726"
            "  );"
            "  border-radius: 3px;"
            "}"
        )
        self.progress.setGraphicsEffect(self._prog_fx)
        layout.addWidget(self.progress)
        layout.addSpacing(12)

        # ── Status label ──────────────────────────────────────────────
        self._status_fx = QGraphicsOpacityEffect()
        self._status_fx.setOpacity(0.0)
        self.status = QLabel(_LOAD_STEPS[0])
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet(
            "background: transparent;"
            "color: #9090b0;"
            "font-size: 10px;"
            "letter-spacing: 1.5px;"
        )
        self.status.setGraphicsEffect(self._status_fx)
        layout.addWidget(self.status)

    def _center(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

    # ------------------------------------------------------------------
    # Entrance animations (staggered fade-ins)
    # ------------------------------------------------------------------
    def _fade_in(self, effect: QGraphicsOpacityEffect, duration: int, delay: int) -> None:
        def _start() -> None:
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(duration)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.start()
            self._anims.append(anim)

        QTimer.singleShot(delay, _start)

    def _play_entrance(self) -> None:
        self._fade_in(self._logo_fx,   600,  80)
        self._fade_in(self._title_fx,  700,  360)
        self._fade_in(self._sub_fx,    500,  720)
        self._fade_in(self._prog_fx,   400, 1020)
        self._fade_in(self._status_fx, 400, 1060)

    # ------------------------------------------------------------------
    # Background animation
    # ------------------------------------------------------------------
    def _advance_frame(self) -> None:
        self._card.advance()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start(self, callback) -> None:
        """Start the loading animation; `callback` is invoked when done."""
        self._callback = callback
        # Delay ticks until entrance animation is mostly complete
        QTimer.singleShot(1350, self._tick_timer.start)

    # ------------------------------------------------------------------
    # Loading ticks
    # ------------------------------------------------------------------
    def _tick(self) -> None:
        if self._step < len(_LOAD_STEPS):
            self.status.setText(_LOAD_STEPS[self._step])
            val = int((self._step + 1) / len(_LOAD_STEPS) * 100)
            self.progress.setValue(val)
            self._step += 1
        else:
            self._tick_timer.stop()
            QTimer.singleShot(500, self._begin_fade_out)

    # ------------------------------------------------------------------
    # Fade-out and close
    # ------------------------------------------------------------------
    def _begin_fade_out(self) -> None:
        self._anim_timer.stop()
        self._fadeout_step = 0
        self._fadeout_timer = QTimer(self)
        self._fadeout_timer.setInterval(18)
        self._fadeout_timer.timeout.connect(self._do_fade_out_step)
        self._fadeout_timer.start()

    def _do_fade_out_step(self) -> None:
        self._fadeout_step += 1
        opacity = max(0.0, 1.0 - self._fadeout_step / 22.0)
        self.setWindowOpacity(opacity)
        if self._fadeout_step >= 22:
            self._fadeout_timer.stop()
            self.close()
            if self._callback:
                self._callback()
