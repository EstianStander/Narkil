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
from ui.login import ModernLoginView


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


class LoginView(ModernLoginView):
    def __init__(self, db, on_success):
        super().__init__(db, on_success, EmailOtpService(SMTP_CONFIG))
        self.btn_login.clicked.connect(self.do_login)
        self.btn_send_co_otp.clicked.connect(self.send_company_otp)
        self.btn_reg_co.clicked.connect(self.register_company)
        self.btn_send_user_otp.clicked.connect(self.send_user_otp)
        self.btn_reg_user.clicked.connect(self.register_user)
        
        self._restore_session()
        self.refresh_company_boxes()

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

    def refresh_company_boxes(self):
        boxes = [self.login_company_box, self.reg_user_company_box]
        try:
            companies = self.db.get_companies()
        except Exception as exc:
            companies = []
            QMessageBox.warning(
                self,
                "Database Connection",
                f"Could not load companies yet. Check MONGODB_URI / network and try again.\n\n{exc}",
            )
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
        try:
            db = NarkilDatabase()
            # Seed is helpful for first-run, but DB outages should not kill the UI startup.
            try:
                db.seed()
            except Exception as exc:
                QMessageBox.warning(
                    None,
                    "Database Warning",
                    f"Connected UI startup, but initial database seed failed.\n\n{exc}",
                )

            _db_ref[0] = db
            lv = LoginView(db, _launch_main)
            lv.showMaximized()
            _login_ref[0] = lv
        except Exception as exc:
            QMessageBox.critical(
                None,
                "Startup Error",
                f"Narkil could not open the login page.\n\n{exc}",
            )
            app.quit()

    splash.start(_on_splash_done)
    sys.exit(app.exec())
