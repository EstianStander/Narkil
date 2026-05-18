# ── NARKIL Design System — Fire & Iron Theme ───────────────────────────────
#
#   Palette:
#     bg_base    #08080f   deep obsidian
#     bg_raised  #0e0e1a   raised surface
#     bg_card    #131324   card / panel
#     bg_hover   #1a1a2e   hover & input
#     fire_deep  #cc3300   deep ember
#     fire_mid   #ff5500   flame ← primary CTA
#     fire_hot   #ff8c00   hot orange
#     fire_gold  #ffbb00   ember gold
#     text_hi    #f0f0f8   headlines
#     text_mid   #a0a0c0   body
#     text_lo    #55557a   captions / muted
#     border     #1c1c30   subtle borders
#     success    #00d48a   green
#     warning    #ffaa00   amber
#     danger     #ff3050   red
#
# ───────────────────────────────────────────────────────────────────────────

NARKIL_THEME = """

/* ── Global base ──────────────────────────────────────────────── */
QMainWindow, QDialog {
    background-color: #08080f;
    color: #f0f0f8;
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
}

QWidget {
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
    color: #f0f0f8;
    font-size: 13px;
}

/* ── Sidebar ──────────────────────────────────────────────────── */
QWidget#Sidebar {
    background-color: #0b0b17;
    border-right: 1px solid #181830;
}

QWidget#SidebarHeader {
    background-color: #0b0b17;
    border-bottom: 1px solid #181830;
}

QLabel#SidebarAppName {
    color: #ff5500;
    font-size: 19px;
    font-weight: 900;
    letter-spacing: 5px;
}

QLabel#SidebarSubtitle {
    color: #3e3e62;
    font-size: 8px;
    letter-spacing: 3px;
    font-weight: 700;
}

QScrollArea#SidebarScroll {
    background-color: #0b0b17;
    border: none;
}

QScrollArea#SidebarScroll > QWidget > QWidget {
    background-color: #0b0b17;
}

QWidget#NavContainer {
    background-color: #0b0b17;
}

/* ── User card ────────────────────────────────────────────────── */
QWidget#UserCard {
    background-color: #09091400;
    border-top: 1px solid #181830;
}

QLabel#UserAvatar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #cc3300, stop:1 #ff5500);
    color: white;
    border-radius: 18px;
    font-size: 15px;
    font-weight: 700;
}

QLabel#UserName {
    color: #c0c0e0;
    font-size: 13px;
    font-weight: 600;
}

QLabel#UserRole {
    color: #44446a;
    font-size: 11px;
}

/* ── Content area ─────────────────────────────────────────────── */
QWidget#ContentArea {
    background-color: #0e0e1a;
}

QStackedWidget {
    background-color: #0e0e1a;
}

/* ── Section page headers ─────────────────────────────────────── */
QLabel#PageTitle {
    font-size: 26px;
    font-weight: 700;
    color: #f0f0f8;
    letter-spacing: 0.3px;
}

QLabel#PageSubtitle {
    font-size: 13px;
    color: #50507a;
}

QLabel#SectionLabel {
    font-size: 13px;
    font-weight: 700;
    color: #7070a0;
    letter-spacing: 1px;
}

/* ── Cards ────────────────────────────────────────────────────── */
QFrame#Card {
    background-color: #131324;
    border: 1px solid #1c1c30;
    border-radius: 14px;
}

QFrame#CardFire {
    background-color: #131324;
    border: 1px solid #1c1c30;
    border-top: 3px solid #ff5500;
    border-radius: 14px;
}

QFrame#CardAmber {
    background-color: #131324;
    border: 1px solid #1c1c30;
    border-top: 3px solid #ff8c00;
    border-radius: 14px;
}

QFrame#CardGold {
    background-color: #131324;
    border: 1px solid #1c1c30;
    border-top: 3px solid #ffbb00;
    border-radius: 14px;
}

QFrame#CardGreen {
    background-color: #131324;
    border: 1px solid #1c1c30;
    border-top: 3px solid #00d48a;
    border-radius: 14px;
}

QFrame#CardRed {
    background-color: #131324;
    border: 1px solid #1c1c30;
    border-top: 3px solid #ff3050;
    border-radius: 14px;
}

/* ── Tables ───────────────────────────────────────────────────── */
QTableWidget {
    background-color: #0e0e1a;
    color: #d0d0ec;
    border: 1px solid #1c1c30;
    border-radius: 12px;
    gridline-color: #13132a;
    font-size: 13px;
    selection-background-color: transparent;
    alternate-background-color: #10101e;
    outline: none;
}

QTableWidget::item {
    padding: 12px 16px;
    border-bottom: 1px solid #12122a;
    border-right: none;
}

QTableWidget::item:selected {
    background-color: rgba(255, 85, 0, 0.13);
    color: #f0f0f8;
}

QTableWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.03);
}

QTableWidget QTableCornerButton::section {
    background-color: #0b0b17;
    border: none;
}

QHeaderView {
    background-color: transparent;
}

QHeaderView::section {
    background-color: #0c0c18;
    color: #ff5500;
    padding: 13px 16px;
    border: none;
    border-bottom: 1px solid #1c1c30;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

QHeaderView::section:first {
    border-top-left-radius: 12px;
}

QHeaderView::section:last {
    border-top-right-radius: 12px;
}

/* ── Scrollbars ───────────────────────────────────────────────── */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    border-radius: 3px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #28285a;
    border-radius: 3px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: #ff5500;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }

QScrollBar:horizontal {
    background: transparent;
    height: 6px;
    border-radius: 3px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #28285a;
    border-radius: 3px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background: #ff5500;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Buttons ──────────────────────────────────────────────────── */
QPushButton#ActionBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #cc3300, stop:0.5 #ff5500, stop:1 #ff8c00);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
    min-height: 36px;
}

QPushButton#ActionBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #dd4411, stop:0.5 #ff6600, stop:1 #ffa000);
}

QPushButton#ActionBtn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #aa2200, stop:0.5 #dd4400, stop:1 #dd7700);
}

QPushButton#SecondaryBtn {
    background-color: #141430;
    color: #8888b8;
    border: 1px solid #242448;
    border-radius: 10px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
    min-height: 36px;
}

QPushButton#SecondaryBtn:hover {
    background-color: #1c1c3c;
    color: #c0c0e0;
    border-color: #ff5500;
}

QPushButton#DangerBtn {
    background-color: rgba(255, 48, 80, 0.10);
    color: #ff3050;
    border: 1px solid rgba(255, 48, 80, 0.28);
    border-radius: 10px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
    min-height: 36px;
}

QPushButton#DangerBtn:hover {
    background-color: rgba(255, 48, 80, 0.20);
    border-color: #ff3050;
}

/* ── Progress bar ─────────────────────────────────────────────── */
QProgressBar {
    background-color: #14142a;
    border: none;
    border-radius: 6px;
    min-height: 8px;
    max-height: 8px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #cc3300, stop:1 #ff8c00);
    border-radius: 6px;
}

/* ── Input fields ─────────────────────────────────────────────── */
QLineEdit, QTextEdit {
    background-color: #121228;
    border: 1.5px solid #20203c;
    border-radius: 8px;
    padding: 10px 14px;
    color: #e0e0f0;
    font-size: 13px;
    selection-background-color: #ff5500;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #ff5500;
    background-color: #14142e;
}

QComboBox {
    background-color: #121228;
    border: 1.5px solid #20203c;
    border-radius: 8px;
    padding: 10px 14px;
    color: #e0e0f0;
    font-size: 13px;
    min-height: 36px;
}

QComboBox:focus {
    border-color: #ff5500;
}

QComboBox::drop-down { border: none; width: 30px; }

QComboBox::down-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #ff5500;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #121228;
    border: 1px solid #20203c;
    color: #e0e0f0;
    selection-background-color: #ff5500;
    selection-color: white;
    outline: none;
    border-radius: 8px;
}

/* ── Dividers ─────────────────────────────────────────────────── */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: #1c1c30;
    border: none;
    max-height: 1px;
    background-color: #1c1c30;
}

/* ── Message boxes ────────────────────────────────────────────── */
QMessageBox {
    background-color: #0e0e1a;
    color: #f0f0f8;
}

QMessageBox QPushButton {
    background-color: #131324;
    color: #e0e0f0;
    border: 1px solid #1c1c30;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    border-color: #ff5500;
    color: #ff5500;
}

"""
