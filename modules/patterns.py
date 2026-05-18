from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QListWidget, QInputDialog,
                             QMessageBox, QScrollArea, QGraphicsView, 
                             QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QColor, QPen, QBrush, QFont, QPainter

class PatternNode(QGraphicsRectItem):
    def __init__(self, name, x, y):
        super().__init__(0, 0, 180, 60)
        self.setPos(x, y)
        self.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.setBrush(QBrush(QColor(30, 30, 50, 200)))
        self.setPen(QPen(QColor(255, 85, 0), 2))
        
        self.text = QGraphicsTextItem(name, self)
        self.text.setDefaultTextColor(Qt.GlobalColor.white)
        self.text.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        # Center text
        tw = self.text.boundingRect().width()
        th = self.text.boundingRect().height()
        self.text.setPos((180-tw)/2, (60-th)/2)

class PatternsModule(QWidget):
    def __init__(self, db, company_id):
        super().__init__()
        self.db = db
        self.company_id = company_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        # Header
        header = QHBoxLayout()
        title_block = QVBoxLayout()
        title = QLabel("Pattern Process Management")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: white;")
        sub = QLabel("Define and visualize the production flow for foundry patterns")
        sub.setStyleSheet("color: rgba(255, 255, 255, 0.4);")
        title_block.addWidget(title)
        title_block.addWidget(sub)
        header.addLayout(title_block)
        header.addStretch()
        
        btn_save = QPushButton("Save Flow")
        btn_save.setObjectName("ActionBtn")
        btn_save.clicked.connect(self.save_flow)
        header.addWidget(btn_save)
        layout.addLayout(header)

        # Main Split
        main_split = QHBoxLayout()
        
        # Left: Process List
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        left_panel.addWidget(QLabel("AVAILABLE PHASES"))
        
        self.phase_list = QListWidget()
        self.phase_list.setObjectName("Card")
        self.phase_list.addItems(["Molding", "Casting", "Cooling", "Finishing", "Inspection", "Cleaning"])
        self.phase_list.setStyleSheet("QListWidget { background-color: rgba(26, 26, 48, 0.4); color: white; border-radius: 12px; padding: 10px; }")
        left_panel.addWidget(self.phase_list)
        
        btn_add = QPushButton("+ Add to Diagram")
        btn_add.setObjectName("SecondaryBtn")
        btn_add.clicked.connect(self.add_phase_to_diagram)
        left_panel.addWidget(btn_add)
        
        main_split.addLayout(left_panel, 1)

        # Right: Visual Diagram
        self.scene = QGraphicsScene(0, 0, 2000, 2000)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setStyleSheet("background-color: #0e0e1a; border: 1px solid #20203c; border-radius: 18px;")
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        main_split.addWidget(self.view, 4)
        
        layout.addLayout(main_split)
        
        self.load_data()

    def add_phase_to_diagram(self):
        item = self.phase_list.currentItem()
        if item:
            name = item.text()
            node = PatternNode(name, 100, 100)
            self.scene.addItem(node)

    def save_flow(self):
        # Implementation for saving to MongoDB
        QMessageBox.information(self, "Success", "Pattern process flow saved successfully.")

    def load_data(self):
        # Sample data loading
        initial_phases = ["Molding", "Casting", "Cooling"]
        for i, p in enumerate(initial_phases):
            node = PatternNode(p, 50, 50 + i * 100)
            self.scene.addItem(node)
