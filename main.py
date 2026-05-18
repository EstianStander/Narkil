import sys
import os
import json
import base64
import smtplib
import secrets
import datetime
from email.message import EmailMessage

# Load .env before any os.getenv calls
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed; rely on environment variables already set

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QComboBox, QStackedWidget, QMessageBox,
                             QFrame, QScrollArea, QCheckBox, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
from core.database import NarkilDatabase
from ui.styles import NARKIL_THEME
from ui.splash import SplashScreen


def resource_path(relative_path):
    """Resolve a resource path that works in development and PyInstaller builds."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, relative_path)


from modules.dashboard import DashboardModule
from modules.inventory import InventoryModule
from modules.production import ProductionModule
from modules.orders import OrdersModule
from modules.planning import PlanningModule
from modules.quality import QualityModule
from modules.ticketing import TicketingModule

SMTP_CONFIG = {
    "Host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "Port": int(os.getenv("SMTP_PORT", "587")),
    "Ssl": os.getenv("SMTP_SSL", "true").lower() == "true",
    "User": os.getenv("SMTP_USER", ""),
    "Pass": os.getenv("SMTP_PASS", ""),
    "AdminEmail": os.getenv("SMTP_ADMIN_EMAIL", ""),
}


class EmailOtpService:
    def __init__(self, smtp_config):
        self.smtp_config = smtp_config
        self.pending = {}
        self.otp_ttl_minutes = 5

    def send_otp(self, email, purpose):
        if not self.smtp_config.get("User") or not self.smtp_config.get("Pass"):
            return False, "SMTP_USER and SMTP_PASS must be configured before sending OTP."

        otp_code = f"{secrets.randbelow(1000000):06d}"
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=self.otp_ttl_minutes)
        self.pending[(email.strip().lower(), purpose)] = {
            "code": otp_code,
            "expires_at": expires_at
        }

        subject = "Narkil OTP Verification"
        body = (
            f"Your verification code is: {otp_code}\n\n"
            f"This code expires in {self.otp_ttl_minutes} minutes.\n"
            "If you did not request this code, you can ignore this email."
        )

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.smtp_config["User"]
        msg["To"] = email.strip().lower()
        msg.set_content(body)

        try:
            with smtplib.SMTP(self.smtp_config["Host"], self.smtp_config["Port"]) as server:
                server.ehlo()
                if self.smtp_config.get("Ssl", True):
                    server.starttls()
                server.login(self.smtp_config["User"], self.smtp_config["Pass"])
                server.send_message(msg)
            return True, "OTP sent successfully."
        except Exception as exc:
            self.pending.pop((email.strip().lower(), purpose), None)
            return False, f"Unable to send OTP email: {exc}"

    def verify_otp(self, email, purpose, otp_code):
        key = (email.strip().lower(), purpose)
        entry = self.pending.get(key)
        if not entry:
            return False, "No pending OTP request found."
        if datetime.datetime.utcnow() > entry["expires_at"]:
            self.pending.pop(key, None)
            return False, "OTP has expired. Request a new code."
        if entry["code"] != otp_code.strip():
            return False, "Invalid OTP code."
        self.pending.pop(key, None)
        return True, "OTP verified."


# ── Session persistence (Remember Me) ────────────────────────────────────────

def _session_path() -> str:
    app_data = os.getenv("APPDATA") or os.path.expanduser("~")
    session_dir = os.path.join(app_data, "Narkil")
    os.makedirs(session_dir, exist_ok=True)
    return os.path.join(session_dir, "session.json")


def _save_session(company_id, email: str, password: str) -> None:
    data = {
        "company_id": str(company_id),
        "email": email,
        "password": base64.b64encode(password.encode()).decode(),
    }
    try:
        with open(_session_path(), "w") as f:
            json.dump(data, f)
    except OSError:
        pass


def _load_session() -> dict | None:
    path = _session_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        data["password"] = base64.b64decode(data["password"].encode()).decode()
        return data
    except Exception:
        return None


def _clear_session() -> None:
    try:
        path = _session_path()
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


class LoginView(QWidget):
    def __init__(self, db, on_success):
        super().__init__()
        self.db = db
        self.on_success = on_success
        self.otp = EmailOtpService(SMTP_CONFIG)
        self.pending_login = None
        self.init_ui()
        self._restore_session()

    def _restore_session(self):
        session = _load_session()
        if not session:
            return
        self.login_remember_me.setChecked(True)
        for i in range(self.login_company_box.count()):
            if str(self.login_company_box.itemData(i)) == session.get("company_id", ""):
                self.login_company_box.setCurrentIndex(i)
                break
        self.login_email_in.setText(session.get("email", ""))
        self.login_pass_in.setText(session.get("password", ""))

    def init_ui(self):
        self.setWindowTitle("Narkil ERP — Secure Login")
        self.setMinimumSize(520, 720)

        # Open at a comfortable fixed size, centred on screen
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = 520, 800
        self.setGeometry(
            (screen.width() - w) // 2,
            (screen.height() - h) // 2,
            w, h,
        )

        # ── Global stylesheet ──────────────────────────────────────────────
        self.setStyleSheet("""
            QWidget {
                background-color: #0e0e1e;
                color: #d5d5ee;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel { background: transparent; }
            QLineEdit {
                background-color: #20203a;
                border: 1.5px solid #363660;
                border-radius: 8px;
                padding: 11px 14px;
                color: #d5d5ee;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #ff5722;
                background-color: #262646;
            }
            QComboBox {
                background-color: #20203a;
                border: 1.5px solid #363660;
                border-radius: 8px;
                padding: 11px 14px;
                color: #d5d5ee;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #ff5722;
                background-color: #262646;
            }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #ff5722;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #20203a;
                border: 1px solid #363660;
                color: #d5d5ee;
                selection-background-color: #ff5722;
                selection-color: white;
                outline: none;
            }
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: #1a1a35;
                width: 5px;
                border-radius: 2px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #ff5722;
                border-radius: 2px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QCheckBox { color: #9090b0; font-size: 12px; spacing: 8px; }
            QCheckBox::indicator {
                width: 15px; height: 15px;
                border: 1.5px solid #363660;
                border-radius: 4px;
                background-color: #20203a;
            }
            QCheckBox::indicator:checked {
                background-color: #ff5722;
                border-color: #ff5722;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Vertical centering
        outer.addStretch(1)

        h_row = QHBoxLayout()
        h_row.setContentsMargins(0, 0, 0, 0)
        h_row.setSpacing(0)

        # Horizontal centering
        h_row.addStretch(1)

        # ── Card ───────────────────────────────────────────────────────────
        card = QFrame()
        card.setObjectName("LoginCard")
        card.setFixedWidth(468)
        card.setStyleSheet(
            "QFrame#LoginCard {"
            "  background-color: #1a1a30;"
            "  border: 1px solid #3a3a5e;"
            "  border-radius: 14px;"
            "}"
        )

        h_row.addWidget(card)
        h_row.addStretch(1)
        outer.addLayout(h_row)
        outer.addStretch(1)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(42, 32, 42, 28)
        card_layout.setSpacing(0)

        # ── Logo ───────────────────────────────────────────────────────────
        logo_label = QLabel()
        logo_label.setPixmap(
            QPixmap(resource_path("assets/logo.png")).scaled(
                88, 88,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(logo_label)
        card_layout.addSpacing(12)

        # ── App name ───────────────────────────────────────────────────────
        app_name = QLabel("NARKIL")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet(
            "color: #ff5722; font-size: 30px; font-weight: 900; letter-spacing: 10px;"
        )
        card_layout.addWidget(app_name)
        card_layout.addSpacing(5)

        subtitle = QLabel("ENTERPRISE RESOURCE PLANNING")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #6868a8; font-size: 9px; letter-spacing: 4px;")
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(20)

        # ── Divider ────────────────────────────────────────────────────────
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        divider.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            "stop:0 transparent, stop:0.3 #3a3a5e, stop:0.7 #3a3a5e, stop:1 transparent);"
            "border: none;"
        )
        card_layout.addWidget(divider)
        card_layout.addSpacing(16)

        # ── Custom tab bar ─────────────────────────────────────────────────
        self._STYLE_TAB_ACTIVE = (
            "QPushButton {"
            "  background: transparent; color: #ff5722; border: none;"
            "  border-bottom: 2px solid #ff5722;"
            "  padding: 8px 22px; font-size: 11px; font-weight: 700; letter-spacing: 2px;"
            "}"
        )
        self._STYLE_TAB_IDLE = (
            "QPushButton {"
            "  background: transparent; color: #7070a8; border: none;"
            "  border-bottom: 2px solid transparent;"
            "  padding: 8px 22px; font-size: 11px; font-weight: 700; letter-spacing: 2px;"
            "}"
            "QPushButton:hover { color: #9898c8; }"
        )

        tab_bar = QWidget()
        tab_bar.setStyleSheet("background: transparent;")
        tab_layout = QHBoxLayout(tab_bar)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(4)

        self._tab_signin_btn = QPushButton("SIGN IN")
        self._tab_signin_btn.setStyleSheet(self._STYLE_TAB_ACTIVE)
        self._tab_signin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tab_signin_btn.clicked.connect(lambda: self._switch_tab(0))

        self._tab_register_btn = QPushButton("REGISTER")
        self._tab_register_btn.setStyleSheet(self._STYLE_TAB_IDLE)
        self._tab_register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tab_register_btn.clicked.connect(lambda: self._switch_tab(1))

        tab_layout.addWidget(self._tab_signin_btn)
        tab_layout.addWidget(self._tab_register_btn)
        tab_layout.addStretch()
        card_layout.addWidget(tab_bar)
        card_layout.addSpacing(14)

        # ── Form stack ─────────────────────────────────────────────────────
        self._form_stack = QStackedWidget()
        self._form_stack.setStyleSheet("background: transparent; border: none;")
        self._form_stack.addWidget(self._build_login_tab())
        self._form_stack.addWidget(self._build_register_tab())
        card_layout.addWidget(self._form_stack, 1)

        # ── Footer ─────────────────────────────────────────────────────────
        card_layout.addSpacing(12)
        footer = QLabel("© 2025 Narkil ERP  ·  v1.0.0")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #646488; font-size: 9px; letter-spacing: 1px;")
        card_layout.addWidget(footer)

    def _switch_tab(self, idx):
        self._form_stack.setCurrentIndex(idx)
        if idx == 0:
            self._tab_signin_btn.setStyleSheet(self._STYLE_TAB_ACTIVE)
            self._tab_register_btn.setStyleSheet(self._STYLE_TAB_IDLE)
        else:
            self._tab_signin_btn.setStyleSheet(self._STYLE_TAB_IDLE)
            self._tab_register_btn.setStyleSheet(self._STYLE_TAB_ACTIVE)

    def _build_login_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        def _lbl(text):
            l = QLabel(text)
            l.setStyleSheet(
                "color: #9898c0; font-size: 10px; font-weight: 600;"
                "letter-spacing: 1px; margin-bottom: 4px;"
            )
            return l

        layout.addWidget(_lbl("FOUNDRY"))
        self.login_company_box = QComboBox()
        for c in self.db.get_companies():
            self.login_company_box.addItem(c['company_name'], c['_id'])
        layout.addWidget(self.login_company_box)
        layout.addSpacing(10)

        layout.addWidget(_lbl("EMAIL ADDRESS"))
        self.login_email_in = QLineEdit()
        self.login_email_in.setPlaceholderText("user@company.com")
        layout.addWidget(self.login_email_in)
        layout.addSpacing(10)

        layout.addWidget(_lbl("PASSWORD"))
        self.login_pass_in = QLineEdit()
        self.login_pass_in.setPlaceholderText("Enter your password")
        self.login_pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.login_pass_in)
        layout.addSpacing(12)

        self.login_remember_me = QCheckBox("Remember me")
        layout.addWidget(self.login_remember_me)
        layout.addSpacing(18)

        login_btn = QPushButton("ENTER SYSTEM")
        login_btn.setFixedHeight(46)
        login_btn.setStyleSheet(
            "QPushButton {"
            "  background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            "    stop:0 #b71c1c, stop:0.45 #ff5722, stop:1 #ffa726);"
            "  color: white; border: none; border-radius: 8px;"
            "  font-size: 13px; font-weight: 700; letter-spacing: 3px;"
            "}"
            "QPushButton:hover {"
            "  background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            "    stop:0 #c62828, stop:0.45 #ff6d00, stop:1 #ffb300);"
            "}"
            "QPushButton:pressed {"
            "  background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            "    stop:0 #9a1515, stop:0.45 #e04d1b, stop:1 #e09200);"
            "}"
        )
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.do_login)
        layout.addWidget(login_btn)
        layout.addStretch()
        return tab

    def _build_register_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(0)

        def _lbl(text):
            l = QLabel(text)
            l.setStyleSheet(
                "color: #9898c0; font-size: 10px; font-weight: 600;"
                "letter-spacing: 1px; margin-bottom: 4px;"
            )
            return l

        def _section_hdr(text):
            l = QLabel(text)
            l.setStyleSheet(
                "color: #ff7043; font-size: 11px; font-weight: 700;"
                "letter-spacing: 1px; margin-top: 4px; margin-bottom: 8px;"
            )
            return l

        def _sec_btn(text):
            btn = QPushButton(text)
            btn.setFixedHeight(38)
            btn.setStyleSheet(
                "QPushButton {"
                "  background-color: #22223e; color: #8888b0;"
                "  border: 1px solid #383860; border-radius: 7px;"
                "  font-size: 11px; font-weight: 600; letter-spacing: 1px;"
                "}"
                "QPushButton:hover {"
                "  background-color: #2c2c50; color: #d0d0ee; border-color: #ff5722;"
                "}"
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            return btn

        def _pri_btn(text):
            btn = QPushButton(text)
            btn.setFixedHeight(42)
            btn.setStyleSheet(
                "QPushButton {"
                "  background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
                "    stop:0 #b71c1c, stop:0.45 #ff5722, stop:1 #ffa726);"
                "  color: white; border: none; border-radius: 7px;"
                "  font-size: 12px; font-weight: 700; letter-spacing: 2px;"
                "}"
                "QPushButton:hover {"
                "  background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
                "    stop:0 #c62828, stop:0.45 #ff6d00, stop:1 #ffb300);"
                "}"
            )
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            return btn

        # ── Section 1: Company ────────────────────────────────────────
        layout.addWidget(_section_hdr("① REGISTER FOUNDRY"))

        layout.addWidget(_lbl("COMPANY NAME"))
        self.reg_company_name_in = QLineEdit()
        self.reg_company_name_in.setPlaceholderText("e.g. Narkil Foundry Ltd.")
        layout.addWidget(self.reg_company_name_in)
        layout.addSpacing(8)

        layout.addWidget(_lbl("ADMIN EMAIL"))
        self.reg_company_email_in = QLineEdit()
        self.reg_company_email_in.setPlaceholderText("admin@company.com")
        layout.addWidget(self.reg_company_email_in)
        layout.addSpacing(8)

        layout.addWidget(_lbl("ADMIN PASSWORD"))
        self.reg_company_pass_in = QLineEdit()
        self.reg_company_pass_in.setPlaceholderText("Create a strong password")
        self.reg_company_pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.reg_company_pass_in)
        layout.addSpacing(8)

        layout.addWidget(_lbl("OTP VERIFICATION CODE"))
        self.reg_company_otp_in = QLineEdit()
        self.reg_company_otp_in.setPlaceholderText("6-digit OTP code")
        self.reg_company_otp_in.setMaxLength(6)
        layout.addWidget(self.reg_company_otp_in)
        layout.addSpacing(8)

        btn_send_co = _sec_btn("Send Company OTP")
        btn_send_co.clicked.connect(self.send_company_otp)
        layout.addWidget(btn_send_co)
        layout.addSpacing(6)

        btn_reg_co = _pri_btn("REGISTER FOUNDRY")
        btn_reg_co.clicked.connect(self.register_company)
        layout.addWidget(btn_reg_co)
        layout.addSpacing(20)

        # ── Separator ─────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            "stop:0 transparent, stop:0.3 #3a3a5e, stop:0.7 #3a3a5e, stop:1 transparent);"
            "border: none;"
        )
        layout.addWidget(sep)
        layout.addSpacing(16)

        # ── Section 2: User ───────────────────────────────────────────
        layout.addWidget(_section_hdr("② REGISTER USER"))

        layout.addWidget(_lbl("SELECT FOUNDRY"))
        self.reg_user_company_box = QComboBox()
        layout.addWidget(self.reg_user_company_box)
        layout.addSpacing(8)

        layout.addWidget(_lbl("USER EMAIL"))
        self.reg_user_email_in = QLineEdit()
        self.reg_user_email_in.setPlaceholderText("user@company.com")
        layout.addWidget(self.reg_user_email_in)
        layout.addSpacing(8)

        layout.addWidget(_lbl("USER PASSWORD"))
        self.reg_user_pass_in = QLineEdit()
        self.reg_user_pass_in.setPlaceholderText("Create a strong password")
        self.reg_user_pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.reg_user_pass_in)
        layout.addSpacing(8)

        layout.addWidget(_lbl("OTP VERIFICATION CODE"))
        self.reg_user_otp_in = QLineEdit()
        self.reg_user_otp_in.setPlaceholderText("6-digit OTP code")
        self.reg_user_otp_in.setMaxLength(6)
        layout.addWidget(self.reg_user_otp_in)
        layout.addSpacing(10)

        self.reg_user_2fa = QCheckBox("Enable Two-Factor Authentication (2FA)")
        self.reg_user_2fa.setChecked(True)
        layout.addWidget(self.reg_user_2fa)
        layout.addSpacing(8)

        btn_send_usr = _sec_btn("Send User OTP")
        btn_send_usr.clicked.connect(self.send_user_otp)
        layout.addWidget(btn_send_usr)
        layout.addSpacing(6)

        btn_reg_usr = _pri_btn("REGISTER USER")
        btn_reg_usr.clicked.connect(self.register_user)
        layout.addWidget(btn_reg_usr)
        layout.addSpacing(16)

        scroll.setWidget(inner)
        self.refresh_company_boxes()
        return scroll

    def refresh_company_boxes(self):
        boxes = [self.login_company_box, self.reg_user_company_box]
        companies = self.db.get_companies()
        for box in boxes:
            if box is None:
                continue
            current = box.currentData() if box.count() > 0 else None
            box.clear()
            for c in companies:
                box.addItem(c['company_name'], c['_id'])
            if current:
                idx = box.findData(current)
                if idx >= 0:
                    box.setCurrentIndex(idx)

    def request_login_otp(self):
        company_id = self.login_company_box.currentData()
        email = self.login_email_in.text().strip().lower()
        password = self.login_pass_in.text()

        if not company_id or not email or not password:
            QMessageBox.warning(self, "Missing Data", "Company, email, and password are required.")
            return

        user = self.db.authenticate(email, password, company_id)
        if not user:
            QMessageBox.critical(self, "Access Denied", "Invalid credentials for this foundry.")
            return

        if not user.get("two_factor_enabled", True):
            self.on_success(user, company_id)
            return

        ok, msg = self.otp.send_otp(email, "login")
        if ok:
            self.pending_login = {
                "email": email,
                "company_id": company_id,
                "user": user
            }
            QMessageBox.information(self, "OTP Sent", "A login OTP was sent to your email.")
            return
        QMessageBox.critical(self, "OTP Error", msg)

    def do_login(self):
        company_id = self.login_company_box.currentData()
        email = self.login_email_in.text().strip().lower()
        password = self.login_pass_in.text()

        if not company_id or not email or not password:
            QMessageBox.warning(self, "Missing Data", "Please fill in all fields.")
            return

        user = self.db.authenticate(email, password, company_id)
        if not user:
            QMessageBox.critical(self, "Access Denied", "Invalid credentials for this foundry.")
            return

        if self.login_remember_me.isChecked():
            _save_session(company_id, email, password)
        else:
            _clear_session()

        self.on_success(user, company_id)

    def send_company_otp(self):
        email = self.reg_company_email_in.text().strip().lower()
        if not email:
            QMessageBox.warning(self, "Missing Data", "Admin email is required.")
            return
        ok, msg = self.otp.send_otp(email, "company_register")
        if ok:
            QMessageBox.information(self, "OTP Sent", "Company registration OTP sent.")
        else:
            QMessageBox.critical(self, "OTP Error", msg)

    def register_company(self):
        name = self.reg_company_name_in.text().strip()
        email = self.reg_company_email_in.text().strip().lower()
        password = self.reg_company_pass_in.text()
        otp_code = self.reg_company_otp_in.text().strip()

        ok, msg = self.otp.verify_otp(email, "company_register", otp_code)
        if not ok:
            QMessageBox.critical(self, "OTP Error", msg)
            return

        created, create_msg = self.db.create_company_with_admin(name, email, password)
        if created:
            self.refresh_company_boxes()
            QMessageBox.information(self, "Success", create_msg)
        else:
            QMessageBox.critical(self, "Registration Error", create_msg)

    def send_user_otp(self):
        company_id = self.reg_user_company_box.currentData()
        email = self.reg_user_email_in.text().strip().lower()
        if not company_id or not email:
            QMessageBox.warning(self, "Missing Data", "Select company and enter user email.")
            return
        ok, msg = self.otp.send_otp(email, f"user_register:{company_id}")
        if ok:
            QMessageBox.information(self, "OTP Sent", "User registration OTP sent.")
        else:
            QMessageBox.critical(self, "OTP Error", msg)

    def register_user(self):
        company_id = self.reg_user_company_box.currentData()
        email = self.reg_user_email_in.text().strip().lower()
        password = self.reg_user_pass_in.text()
        otp_code = self.reg_user_otp_in.text().strip()

        if not company_id:
            QMessageBox.warning(self, "Missing Data", "Select a company for the user.")
            return

        ok, msg = self.otp.verify_otp(email, f"user_register:{company_id}", otp_code)
        if not ok:
            QMessageBox.critical(self, "OTP Error", msg)
            return

        created, create_msg = self.db.register_user(
            company_id=company_id,
            email=email,
            password=password,
            roles=["user"],
            two_factor_enabled=self.reg_user_2fa.isChecked()
        )
        if created:
            QMessageBox.information(self, "Success", create_msg)
        else:
            QMessageBox.critical(self, "Registration Error", create_msg)



# ── Collapsible categorised sidebar ──────────────────────────────────────────

class NarkilSidebar(QWidget):
    """Premium collapsible sidebar with category groups and fire-brand styling."""

    page_changed = pyqtSignal(int)

    # (category title, [(label, stack index), ...])
    CATEGORIES = [
        ("OVERVIEW",   [("Dashboard",  0)]),
        ("OPERATIONS", [("Inventory",  1), ("Production", 2)]),
        ("COMMERCE",   [("Orders",     3), ("Planning",   4)]),
        ("CONTROL",    [("Quality",    5), ("Tickets",    6)]),
    ]

    _NAV_ACTIVE = (
        "QPushButton {"
        "  background: rgba(255,85,0,0.11);"
        "  color: #ff6622;"
        "  border: none;"
        "  border-left: 3px solid #ff5500;"
        "  border-top-right-radius: 9px;"
        "  border-bottom-right-radius: 9px;"
        "  padding: 10px 16px 10px 20px;"
        "  font-size: 13px;"
        "  font-weight: 600;"
        "  text-align: left;"
        "}"
    )
    _NAV_IDLE = (
        "QPushButton {"
        "  background: transparent;"
        "  color: #606088;"
        "  border: none;"
        "  border-left: 3px solid transparent;"
        "  border-top-right-radius: 9px;"
        "  border-bottom-right-radius: 9px;"
        "  padding: 10px 16px 10px 20px;"
        "  font-size: 13px;"
        "  font-weight: 500;"
        "  text-align: left;"
        "}"
        "QPushButton:hover {"
        "  background: rgba(255,255,255,0.04);"
        "  color: #9898c0;"
        "}"
    )
    _CAT_HDR = (
        "QPushButton {"
        "  background: transparent;"
        "  color: #38386a;"
        "  border: none;"
        "  padding: 10px 16px 4px 12px;"
        "  font-size: 9px;"
        "  font-weight: 800;"
        "  letter-spacing: 2.5px;"
        "  text-align: left;"
        "}"
        "QPushButton:hover { color: #6060a0; }"
    )

    def __init__(self, db, user, parent=None):
        super().__init__(parent)
        self.db = db
        self.user = user
        self._nav_btns: dict[int, QPushButton] = {}
        self._current = -1
        self._build()

    # ── Build ─────────────────────────────────────────────────────────────

    def _build(self):
        self.setObjectName("Sidebar")
        self.setFixedWidth(256)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_nav(), 1)
        root.addWidget(self._build_user_card())

    def _build_header(self):
        w = QWidget()
        w.setObjectName("SidebarHeader")
        w.setFixedHeight(84)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        logo_lbl = QLabel()
        pix = QPixmap(resource_path("assets/logo.png"))
        if not pix.isNull():
            logo_lbl.setPixmap(
                pix.scaled(46, 46, Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
            )
        lay.addWidget(logo_lbl)

        txt = QVBoxLayout()
        txt.setSpacing(3)
        name_lbl = QLabel("NARKIL")
        name_lbl.setObjectName("SidebarAppName")
        sub_lbl = QLabel("ERP PLATFORM")
        sub_lbl.setObjectName("SidebarSubtitle")
        txt.addWidget(name_lbl)
        txt.addWidget(sub_lbl)
        lay.addLayout(txt)
        lay.addStretch()
        return w

    def _build_nav(self):
        scroll = QScrollArea()
        scroll.setObjectName("SidebarScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        wrap = QWidget()
        wrap.setObjectName("NavContainer")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(0, 10, 0, 10)
        wl.setSpacing(0)

        for cat_title, items in self.CATEGORIES:
            self._add_category(wl, cat_title, items)

        wl.addStretch()
        scroll.setWidget(wrap)
        return scroll

    def _add_category(self, parent_layout, title, items):
        parent_layout.addSpacing(6)

        cat_btn = QPushButton(f"\u25be  {title}")
        cat_btn.setStyleSheet(self._CAT_HDR)
        cat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cat_btn.setFixedHeight(28)
        parent_layout.addWidget(cat_btn)

        items_wrap = QWidget()
        iw = QVBoxLayout(items_wrap)
        iw.setContentsMargins(0, 2, 8, 4)
        iw.setSpacing(2)

        for label, page_idx in items:
            btn = QPushButton(f"   {label}")
            btn.setStyleSheet(self._NAV_IDLE)
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _checked, i=page_idx: self.navigate(i))
            self._nav_btns[page_idx] = btn
            iw.addWidget(btn)

        parent_layout.addWidget(items_wrap)

        def _toggle():
            expanded = items_wrap.isVisible()
            items_wrap.setVisible(not expanded)
            cat_btn.setText(f"{'▸' if expanded else '▾'}  {title}")

        cat_btn.clicked.connect(_toggle)

    def _build_user_card(self):
        card = QWidget()
        card.setObjectName("UserCard")
        card.setFixedHeight(66)
        lay = QHBoxLayout(card)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)

        initial = self.user.get("username", "U")[0].upper()
        avatar = QLabel(initial)
        avatar.setObjectName("UserAvatar")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(avatar)

        info = QVBoxLayout()
        info.setSpacing(2)
        uname = QLabel(self.user.get("username", "User"))
        uname.setObjectName("UserName")
        urole = QLabel("Operator")
        urole.setObjectName("UserRole")
        info.addWidget(uname)
        info.addWidget(urole)
        lay.addLayout(info)
        lay.addStretch()
        return card

    # ── Navigation ────────────────────────────────────────────────────────

    def navigate(self, idx: int):
        if self._current in self._nav_btns:
            self._nav_btns[self._current].setStyleSheet(self._NAV_IDLE)
        self._current = idx
        if idx in self._nav_btns:
            self._nav_btns[idx].setStyleSheet(self._NAV_ACTIVE)
        self.page_changed.emit(idx)

    def set_page(self, idx: int):
        self.navigate(idx)


class NarkilMainWindow(QMainWindow):
    def __init__(self, db, user, company_id):
        super().__init__()
        self.db = db
        self.user = user
        self.company_id = company_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"NARKIL ERP  \u00b7  {self.user['username']}")
        self.setMinimumSize(1280, 800)
        self.showMaximized()
        self.setStyleSheet(NARKIL_THEME)

        central = QWidget()
        central.setObjectName("ContentArea")
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────────────
        self.sidebar = NarkilSidebar(self.db, self.user)
        self.sidebar.page_changed.connect(self._on_page_changed)
        layout.addWidget(self.sidebar)

        # ── Content stack ─────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentArea")
        layout.addWidget(self.stack, 1)

        self.create_modules()
        self.sidebar.set_page(0)

    def create_modules(self):
        self.stack.addWidget(DashboardModule(self.db, self.company_id))
        self.stack.addWidget(InventoryModule(self.db, self.company_id))
        self.stack.addWidget(ProductionModule(self.db, self.company_id))
        self.stack.addWidget(OrdersModule(self.db, self.company_id))
        self.stack.addWidget(PlanningModule(self.db, self.company_id))
        self.stack.addWidget(QualityModule(self.db, self.company_id))
        self.stack.addWidget(TicketingModule(self.db, self.company_id, self.user))

    def _on_page_changed(self, idx: int):
        self.stack.setCurrentIndex(idx)

    # kept for backwards compatibility
    def switch_page(self, idx: int):
        self._on_page_changed(idx)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(resource_path("assets/app-icon.ico")))

    splash = SplashScreen()
    splash.show()
    app.processEvents()

    _db_ref = [None]
    _login_ref = [None]
    _main_ref = [None]

    def _launch_main(user, cid):
        if _login_ref[0]:
            _login_ref[0].close()
        mw = NarkilMainWindow(_db_ref[0], user, cid)
        # showMaximized is already called inside init_ui; just ensure visible
        if not mw.isVisible():
            mw.showMaximized()
        _main_ref[0] = mw

    def _on_splash_done():
        db = NarkilDatabase()
        db.seed()
        _db_ref[0] = db
        lv = LoginView(db, _launch_main)
        lv.show()
        _login_ref[0] = lv

    splash.start(_on_splash_done)
    sys.exit(app.exec())
