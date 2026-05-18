import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QStackedWidget, QMessageBox, QListWidget)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
from core.database import NarkilDatabase
from ui.styles import NARKIL_THEME
from modules.dashboard import DashboardModule
from modules.inventory import InventoryModule
from modules.production import ProductionModule
from modules.orders import OrdersModule
from modules.planning import PlanningModule
from modules.quality import QualityModule
from modules.ticketing import TicketingModule

class LoginView(QWidget):
    def __init__(self, db, on_success):
        super().__init__()
        self.db = db
        self.on_success = on_success
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Narkil ERP - Login")
        self.setFixedSize(450, 550)
        self.setStyleSheet("background-color: #121212; color: white;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(20)

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("assets/logo.png")
        logo_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        title = QLabel("NARKIL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #ff5722; letter-spacing: 5px;")
        layout.addWidget(title)

        self.comp_box = QComboBox()
        for c in self.db.get_companies():
            self.comp_box.addItem(c['company_name'], c['_id'])
        layout.addWidget(QLabel("Select Foundry:"))
        layout.addWidget(self.comp_box)

        self.user_in = QLineEdit()
        self.user_in.setPlaceholderText("Username")
        layout.addWidget(self.user_in)

        self.pass_in = QLineEdit()
        self.pass_in.setPlaceholderText("Password")
        self.pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pass_in)

        login_btn = QPushButton("ENTER SYSTEM")
        login_btn.setStyleSheet("background-color: #ff5722; color: white; padding: 12px; font-weight: bold; border-radius: 5px;")
        login_btn.clicked.connect(self.do_login)
        layout.addWidget(login_btn)

    def do_login(self):
        user = self.db.authenticate(self.user_in.text(), self.pass_in.text(), self.comp_box.currentData())
        if user:
            self.on_success(user, self.comp_box.currentData())
        else:
            QMessageBox.critical(self, "Access Denied", "Invalid credentials for this foundry.")

class NarkilMainWindow(QMainWindow):
    def __init__(self, db, user, company_id):
        super().__init__()
        self.db = db
        self.user = user
        self.company_id = company_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"NARKIL ERP | {self.user['username']}")
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(NARKIL_THEME)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(280)
        side_layout = QVBoxLayout(sidebar)
        
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logo.png").scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setObjectName("SidebarLogo")
        side_layout.addWidget(logo)

        self.nav = QListWidget()
        self.nav.setObjectName("NavList")
        modules = ["Dashboard", "Inventory", "Production", "Orders", "Planning", "Quality", "Tickets"]
        self.nav.addItems(modules)
        self.nav.currentRowChanged.connect(self.switch_page)
        side_layout.addWidget(self.nav)
        
        side_layout.addStretch()
        
        user_info = QLabel(f"Logged in: {self.user['username']}")
        user_info.setStyleSheet("color: #777; padding: 10px;")
        side_layout.addWidget(user_info)

        layout.addWidget(sidebar)

        # Content
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        self.create_modules()
        self.nav.setCurrentRow(0)

    def create_modules(self):
        # All modules integrated into the stack
        self.stack.addWidget(DashboardModule(self.db, self.company_id))
        self.stack.addWidget(InventoryModule(self.db, self.company_id))
        self.stack.addWidget(ProductionModule(self.db, self.company_id))
        self.stack.addWidget(OrdersModule(self.db, self.company_id))
        self.stack.addWidget(PlanningModule(self.db, self.company_id))
        self.stack.addWidget(QualityModule(self.db, self.company_id))
        self.stack.addWidget(TicketingModule(self.db, self.company_id, self.user))

    def switch_page(self, idx):
        self.stack.setCurrentIndex(idx)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = NarkilDatabase()
    db.seed()
    
    def launch_main(user, cid):
        login.close()
        global main_win
        main_win = NarkilMainWindow(db, user, cid)
        main_win.show()

    login = LoginView(db, launch_main)
    login.show()
    sys.exit(app.exec())
