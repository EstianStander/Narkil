from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QLineEdit, QComboBox,
                             QFrame, QMessageBox, QFormLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle("Customer Details" if customer else "Add New Customer")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog { background-color: #0f0f1c; color: white; }
            QLabel { color: #7070a0; font-weight: 700; font-size: 11px; }
            QLineEdit, QComboBox {
                background-color: #131328;
                border: 1.5px solid #20203c;
                border-radius: 8px;
                padding: 10px;
                color: white;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        form = QFormLayout()
        form.setSpacing(12)
        
        self.name_in = QLineEdit()
        self.category_in = QComboBox()
        self.category_in.addItems(["ALU", "IRON", "STEEL", "OTHER"])
        self.contact_in = QLineEdit()
        self.phone_in = QLineEdit()
        self.mobile_in = QLineEdit()

        form.addRow("COMPANY NAME", self.name_in)
        form.addRow("CATEGORY", self.category_in)
        form.addRow("CONTACT PERSON", self.contact_in)
        form.addRow("TELEPHONE", self.phone_in)
        form.addRow("MOBILE", self.mobile_in)

        if self.customer:
            self.name_in.setText(self.customer.get("name", ""))
            self.category_in.setCurrentText(self.customer.get("category", "ALU"))
            self.contact_in.setText(self.customer.get("contactName", ""))
            self.phone_in.setText(self.customer.get("telephone", ""))
            self.mobile_in.setText(self.customer.get("mobile", "") or "")

        layout.addLayout(form)
        
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save Customer")
        save_btn.setObjectName("ActionBtn")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def get_data(self):
        return {
            "name": self.name_in.text().strip(),
            "category": self.category_in.currentText(),
            "contactName": self.contact_in.text().strip(),
            "telephone": self.phone_in.text().strip(),
            "mobile": self.mobile_in.text().strip() or None,
            "active": True
        }

class CustomersModule(QWidget):
    def __init__(self, db, company_id):
        super().__init__()
        self.db = db
        self.company_id = company_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        header = QHBoxLayout()
        title_block = QVBoxLayout()
        title = QLabel("Customer Management")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: white;")
        sub = QLabel("Manage your foundry clients and contact information")
        sub.setStyleSheet("color: rgba(255, 255, 255, 0.4);")
        title_block.addWidget(title)
        title_block.addWidget(sub)
        header.addLayout(title_block)
        header.addStretch()

        add_btn = QPushButton("+ Add Customer")
        add_btn.setObjectName("ActionBtn")
        add_btn.clicked.connect(self.add_customer)
        header.addWidget(add_btn)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Category", "Contact", "Phone", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        customers = self.db.get_customers(self.company_id)
        self.table.setRowCount(len(customers))
        for i, c in enumerate(customers):
            self.table.setItem(i, 0, QTableWidgetItem(c.get("name", "")))
            self.table.setItem(i, 1, QTableWidgetItem(c.get("category", "")))
            self.table.setItem(i, 2, QTableWidgetItem(c.get("contactName", "")))
            self.table.setItem(i, 3, QTableWidgetItem(c.get("telephone", "")))
            status = "Active" if c.get("active", True) else "Inactive"
            item = QTableWidgetItem(status)
            item.setForeground(QColor("#00d48a" if c.get("active", True) else "#ff3050"))
            self.table.setItem(i, 4, item)

    def add_customer(self):
        d = CustomerDialog(self)
        if d.exec():
            data = d.get_data()
            if data["name"]:
                self.db.add_customer(self.company_id, data)
                self.load_data()
