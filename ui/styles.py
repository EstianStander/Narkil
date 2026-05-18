NARKIL_THEME = """
QMainWindow {
    background-color: #121212;
}

QWidget#Sidebar {
    background-color: #1e1e1e;
    border-right: 1px solid #333333;
}

QLabel#SidebarLogo {
    padding: 20px;
    border-bottom: 1px solid #333333;
}

QListWidget#NavList {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#NavList::item {
    color: #aaaaaa;
    padding: 15px 25px;
    font-size: 14px;
}

QListWidget#NavList::item:selected {
    background-color: #2c2c2c;
    color: #ff5722; /* Narkil Orange from logo */
    border-left: 4px solid #ff5722;
}

QPushButton#ActionBtn {
    background-color: #ff5722;
    color: white;
    border-radius: 4px;
    padding: 10px;
    font-weight: bold;
}

QTableWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #333333;
}

QHeaderView::section {
    background-color: #252525;
    color: #ff5722;
    padding: 10px;
    border: none;
    font-weight: bold;
}
"""
