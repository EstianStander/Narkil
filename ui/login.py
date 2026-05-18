import os
import sys
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QStackedWidget, QMessageBox, QFrame, QScrollArea,
    QCheckBox, QApplication, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QRect, QPoint
from PyQt6.QtGui import (
    QPixmap, QIcon, QPainter, QColor, QLinearGradient, QRadialGradient,
    QPen, QBrush, QFont, QColorConstants
)

# Reuse the resource path logic
def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        # Since this is in ui/, we go up one level
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base, relative_path)

class AnimatedBackground(QWidget):
    """A full-screen animated background with particles and gradients."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._frame = 0
        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._update_frame)
        self._timer.start()

    def _update_frame(self):
        self._frame += 1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        t = self._frame * 0.02

        # 1. Deep Base Gradient
        bg_grad = QLinearGradient(0, 0, w, h)
        bg_grad.setColorAt(0.0, QColor(10, 10, 22))
        bg_grad.setColorAt(1.0, QColor(20, 20, 40))
        p.fillRect(self.rect(), bg_grad)

        # 2. Large moving glows
        glow1_x = w * (0.5 + 0.3 * math.cos(t * 0.5))
        glow1_y = h * (0.5 + 0.3 * math.sin(t * 0.7))
        glow1 = QRadialGradient(glow1_x, glow1_y, w * 0.6)
        glow1.setColorAt(0.0, QColor(255, 87, 34, 15))
        glow1.setColorAt(1.0, QColor(255, 87, 34, 0))
        p.fillRect(self.rect(), glow1)

        glow2_x = w * (0.5 + 0.3 * math.sin(t * 0.4))
        glow2_y = h * (0.5 + 0.2 * math.cos(t * 0.6))
        glow2 = QRadialGradient(glow2_x, glow2_y, w * 0.5)
        glow2.setColorAt(0.0, QColor(63, 81, 181, 15))
        glow2.setColorAt(1.0, QColor(63, 81, 181, 0))
        p.fillRect(self.rect(), glow2)

        # 3. Floating Particles
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(40):
            px = (i * 137.5 + t * 20) % (w + 100) - 50
            py = (i * 91.3 + t * 15) % (h + 100) - 50
            alpha = int(30 + 20 * math.sin(t + i))
            size = 2 + (i % 3)
            p.setBrush(QColor(255, 255, 255, alpha))
            p.drawEllipse(int(px), int(py), size, size)

        # 4. Subtle Grid
        p.setPen(QPen(QColor(255, 255, 255, 5), 1))
        grid_size = 60
        for x in range(0, w, grid_size):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, grid_size):
            p.drawLine(0, y, w, y)

class ModernLoginView(QWidget):
    def __init__(self, db, on_success, email_otp_service):
        super().__init__()
        self.db = db
        self.on_success = on_success
        self.otp = email_otp_service
        self.pending_login = None
        self._bg_warned = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Narkil ERP — Enterprise Access")
        self.setMinimumSize(980, 680)
        
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Background
        self.bg = AnimatedBackground(self)
        self.bg.resize(self.size())
        self.bg.lower()
        
        # Content Wrapper (Centered)
        self.content_wrapper = QWidget(self)
        self.wrapper_layout = QHBoxLayout(self.content_wrapper)
        self.wrapper_layout.setContentsMargins(0, 0, 0, 0)
        
        # ── Main Card ──────────────────────────────────────────────────────
        self.card = QFrame()
        self.card.setObjectName("MainCard")
        self.card.setFixedSize(960, 620)
        self.card.setStyleSheet("""
            QFrame#MainCard {
                background-color: rgba(26, 26, 48, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
            }
        """)
        
        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # ── Left Side: Branding & Info ──────────────────────────────────────
        self.left_panel = QFrame()
        self.left_panel.setObjectName("LeftPanel")
        self.left_panel.setFixedWidth(440)
        self.left_panel.setStyleSheet("""
            QFrame#LeftPanel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1e3a, stop:1 #0e0e1e);
                border-top-left-radius: 24px;
                border-bottom-left-radius: 24px;
                border-right: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(50, 60, 50, 60)
        left_layout.setSpacing(0)

        # Logo with Glow
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        self.logo_label = QLabel()
        pix = QPixmap(resource_path("assets/logo.png"))
        if not pix.isNull():
            self.logo_label.setPixmap(pix.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_layout.addWidget(self.logo_label)
        left_layout.addWidget(logo_container)
        left_layout.addSpacing(30)

        app_name = QLabel("NARKIL")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet("color: #ff5722; font-size: 48px; font-weight: 900; letter-spacing: 12px;")
        left_layout.addWidget(app_name)

        subtitle = QLabel("ENTERPRISE RESOURCE PLANNING")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.4); font-size: 11px; letter-spacing: 4px; font-weight: 600;")
        left_layout.addWidget(subtitle)
        
        left_layout.addStretch()
        
        tagline = QLabel("Precision in every cast.\nIntelligence in every move.")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("color: rgba(255, 255, 255, 0.6); font-size: 14px; line-height: 1.6; font-style: italic;")
        left_layout.addWidget(tagline)
        
        left_layout.addSpacing(40)
        
        footer_info = QLabel("© 2026 Narkil Technologies")
        footer_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_info.setStyleSheet("color: rgba(255, 255, 255, 0.2); font-size: 10px; letter-spacing: 1px;")
        left_layout.addWidget(footer_info)

        # ── Right Side: Forms ──────────────────────────────────────────────
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(60, 50, 60, 50)
        right_layout.setSpacing(0)

        # Tab Selector
        tab_container = QWidget()
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(20)

        self.btn_signin_tab = QPushButton("Sign In")
        self.btn_register_tab = QPushButton("Register")
        
        for btn in [self.btn_signin_tab, self.btn_register_tab]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedWidth(100)
            tab_layout.addWidget(btn)
        
        tab_layout.addStretch()
        right_layout.addWidget(tab_container)
        right_layout.addSpacing(40)

        # Form Stack
        self.form_stack = QStackedWidget()
        self.form_stack.addWidget(self._build_login_form())
        self.form_stack.addWidget(self._build_register_form())
        right_layout.addWidget(self.form_stack)

        card_layout.addWidget(self.left_panel)
        card_layout.addWidget(self.right_panel, 1)

        # Add card to centered layout
        self.wrapper_layout.addStretch()
        self.wrapper_layout.addWidget(self.card)
        self.wrapper_layout.addStretch()

        self.main_layout.addWidget(self.content_wrapper, 1)

        # Stylesheet for inputs and buttons
        self.setStyleSheet("""
            QWidget {
                color: #e0e0f0;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QLabel { background: transparent; }
            QLineEdit, QComboBox {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 12px 16px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #ff5722;
                background-color: rgba(255, 255, 255, 0.08);
            }
            QPushButton {
                border-radius: 12px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton#PrimaryBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff5722, stop:1 #ff8a65);
                color: white;
                border: none;
                padding: 14px;
                font-size: 15px;
                letter-spacing: 1px;
            }
            QPushButton#PrimaryBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff7043, stop:1 #ffab91);
            }
            QPushButton#SecondaryBtn {
                background-color: rgba(255, 255, 255, 0.05);
                color: #ff5722;
                border: 1px solid rgba(255, 87, 34, 0.3);
                padding: 10px;
            }
            QPushButton#SecondaryBtn:hover {
                background-color: rgba(255, 87, 34, 0.1);
            }
            QCheckBox {
                color: rgba(255, 255, 255, 0.6);
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                background: rgba(255, 255, 255, 0.05);
            }
            QCheckBox::indicator:checked {
                background-color: #ff5722;
                border-color: #ff5722;
            }
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: transparent;
                width: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
            }
        """)

        # Tab Switching Logic
        self._update_tabs(0)
        self.btn_signin_tab.clicked.connect(lambda: self._switch_tab(0))
        self.btn_register_tab.clicked.connect(lambda: self._switch_tab(1))

        # Entrance Animation
        self._play_entrance_anim()

    def _play_entrance_anim(self):
        self.card.setGraphicsEffect(QGraphicsOpacityEffect())
        self.anim = QPropertyAnimation(self.card.graphicsEffect(), b"opacity")
        self.anim.setDuration(1000)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

    def _update_tabs(self, index):
        active_style = "color: #ff5722; border-bottom: 2px solid #ff5722; border-radius: 0; padding-bottom: 5px; background: transparent;"
        idle_style = "color: rgba(255, 255, 255, 0.4); border: none; background: transparent;"
        
        self.btn_signin_tab.setStyleSheet(active_style if index == 0 else idle_style)
        self.btn_register_tab.setStyleSheet(active_style if index == 1 else idle_style)

    def _switch_tab(self, index):
        self._update_tabs(index)
        self.form_stack.setCurrentIndex(index)

    def _build_login_form(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        title = QLabel("Welcome Back")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: white;")
        layout.addWidget(title)

        subtitle = QLabel("Please enter your details to sign in.")
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 14px;")
        layout.addWidget(subtitle)
        layout.addSpacing(10)

        layout.addWidget(QLabel("Foundry"))
        self.login_company_box = QComboBox()
        layout.addWidget(self.login_company_box)

        layout.addWidget(QLabel("Email Address"))
        self.login_email_in = QLineEdit()
        self.login_email_in.setPlaceholderText("name@company.com")
        layout.addWidget(self.login_email_in)

        layout.addWidget(QLabel("Password"))
        self.login_pass_in = QLineEdit()
        self.login_pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_pass_in.setPlaceholderText("••••••••")
        layout.addWidget(self.login_pass_in)

        self.login_remember_me = QCheckBox("Remember this device")
        layout.addWidget(self.login_remember_me)
        
        layout.addSpacing(10)
        
        self.btn_login = QPushButton("Sign In to Narkil")
        self.btn_login.setObjectName("PrimaryBtn")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_login)
        
        layout.addStretch()
        return w

    def _build_register_form(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setSpacing(15)

        title = QLabel("Create Account")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: white;")
        layout.addWidget(title)
        
        # Company Section
        header1 = QLabel("1. Register Foundry")
        header1.setStyleSheet("color: #ff5722; font-weight: 700; margin-top: 10px;")
        layout.addWidget(header1)
        
        self.reg_company_name_in = QLineEdit()
        self.reg_company_name_in.setPlaceholderText("Company Name")
        layout.addWidget(self.reg_company_name_in)
        
        self.reg_company_email_in = QLineEdit()
        self.reg_company_email_in.setPlaceholderText("Admin Email")
        layout.addWidget(self.reg_company_email_in)
        
        self.reg_company_pass_in = QLineEdit()
        self.reg_company_pass_in.setPlaceholderText("Admin Password")
        self.reg_company_pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.reg_company_pass_in)
        
        otp_row = QHBoxLayout()
        self.reg_company_otp_in = QLineEdit()
        self.reg_company_otp_in.setPlaceholderText("OTP")
        self.btn_send_co_otp = QPushButton("Send OTP")
        self.btn_send_co_otp.setObjectName("SecondaryBtn")
        self.btn_send_co_otp.setFixedWidth(100)
        otp_row.addWidget(self.reg_company_otp_in)
        otp_row.addWidget(self.btn_send_co_otp)
        layout.addLayout(otp_row)
        
        self.btn_reg_co = QPushButton("Register Foundry")
        self.btn_reg_co.setObjectName("PrimaryBtn")
        layout.addWidget(self.btn_reg_co)
        
        layout.addSpacing(10)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")
        layout.addWidget(line)
        layout.addSpacing(10)

        # User Section
        header2 = QLabel("2. Register User")
        header2.setStyleSheet("color: #ff5722; font-weight: 700;")
        layout.addWidget(header2)
        
        self.reg_user_company_box = QComboBox()
        layout.addWidget(self.reg_user_company_box)
        
        self.reg_user_email_in = QLineEdit()
        self.reg_user_email_in.setPlaceholderText("User Email")
        layout.addWidget(self.reg_user_email_in)
        
        self.reg_user_pass_in = QLineEdit()
        self.reg_user_pass_in.setPlaceholderText("User Password")
        self.reg_user_pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.reg_user_pass_in)
        
        otp_row2 = QHBoxLayout()
        self.reg_user_otp_in = QLineEdit()
        self.reg_user_otp_in.setPlaceholderText("OTP")
        self.btn_send_user_otp = QPushButton("Send OTP")
        self.btn_send_user_otp.setObjectName("SecondaryBtn")
        self.btn_send_user_otp.setFixedWidth(100)
        otp_row2.addWidget(self.reg_user_otp_in)
        otp_row2.addWidget(self.btn_send_user_otp)
        layout.addLayout(otp_row2)
        
        self.reg_user_2fa = QCheckBox("Enable 2FA Protection")
        self.reg_user_2fa.setChecked(True)
        layout.addWidget(self.reg_user_2fa)
        
        self.btn_reg_user = QPushButton("Create User Account")
        self.btn_reg_user.setObjectName("PrimaryBtn")
        layout.addWidget(self.btn_reg_user)
        
        scroll.setWidget(w)
        return scroll

    def resizeEvent(self, event):
        self.bg.resize(self.size())
        super().resizeEvent(event)
