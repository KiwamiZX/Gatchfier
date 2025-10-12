import sys, json, os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QLabel, QSplashScreen, QFrame, QSizePolicy
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize

from tabs.ping_tab import PingTab
from tabs.traceroute_tab import TracerouteTab
from tabs.portscan_tab import PortScannerTab
from tabs.dns_tab import DNSTab
from tabs.whois import WhoisTab

# 🔧 Locate resources when running from source or a bundled executable
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 🔧 Build the path where the app stores user-specific configuration
def get_config_path():
    config_dir = os.path.join(os.path.expanduser("~"), ".gatchfier")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.json")

CONFIG_WRITE_PATH = get_config_path()
CONFIG_READ_PATH = resource_path("config.json")


def normalize_theme_name(raw_theme: str) -> str:
    """Map legacy theme names to the current set."""
    if not raw_theme:
        return "neon"
    cleaned = raw_theme.lower()
    if cleaned in {"dark", "neon"}:
        return "neon"
    return "light"

def load_theme():
    if os.path.exists(CONFIG_WRITE_PATH):
        with open(CONFIG_WRITE_PATH, "r") as f:
            return normalize_theme_name(json.load(f).get("theme", "neon"))
    elif os.path.exists(CONFIG_READ_PATH):
        with open(CONFIG_READ_PATH, "r") as f:
            return normalize_theme_name(json.load(f).get("theme", "neon"))
    return "neon"

def save_theme(theme):
    with open(CONFIG_WRITE_PATH, "w") as f:
        json.dump({"theme": normalize_theme_name(theme)}, f)

def show_splash(app, theme):
    if normalize_theme_name(theme) == "neon":
        splash_path = resource_path("icons/splash_dark.png")
    else:
        splash_path = resource_path("icons/splash.png")

    splash_pix = QPixmap(splash_path).scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    splash = QSplashScreen(splash_pix)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.show()
    app.processEvents()
    return splash

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gatchfier")
        self.setWindowIcon(QIcon(resource_path("icons/gatchfier_icon.png")))
        self.setMinimumSize(900, 600)

        self.current_theme = load_theme()

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(32, 32, 32, 32)
        root_layout.setSpacing(28)

        header_card = QFrame()
        header_card.setObjectName("HeaderCard")
        header_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_card.setMinimumHeight(140)
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(24)

        logo_pixmap = QPixmap(resource_path("icons/gatchfier_logo.png")).scaled(
            120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.logo_label = QLabel()
        self.logo_label.setPixmap(logo_pixmap)
        header_layout.addWidget(self.logo_label)

        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        self.title_label = QLabel("Gatchfier Network Toolkit")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setWordWrap(True)
        title_block.addWidget(self.title_label)

        self.subtitle_label = QLabel("Ping • Traceroute • Port Scan • DNS • Whois")
        self.subtitle_label.setObjectName("SubtitleLabel")
        self.subtitle_label.setWordWrap(True)
        title_block.addWidget(self.subtitle_label)
        title_block.addStretch()
        header_layout.addLayout(title_block, 1)

        header_layout.addStretch()

        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("AccentButton")
        self.theme_btn.setFixedHeight(40)
        self.theme_btn.setMinimumWidth(160)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setToolTip("Toggle between neon and light themes")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_btn, 0, Qt.AlignTop)

        root_layout.addWidget(header_card)

        content_card = QFrame()
        content_card.setObjectName("ContentCard")
        content_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QVBoxLayout(content_card)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(28)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("MainTabs")
        self.tabs.setElideMode(Qt.ElideRight)
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tabs.addTab(PingTab(), "Ping")
        self.tabs.addTab(TracerouteTab(), "Traceroute")
        self.tabs.addTab(PortScannerTab(), "Port Scan")
        self.tabs.addTab(DNSTab(), "DNS Lookup")
        self.tabs.addTab(WhoisTab(), "Whois")
        content_layout.addWidget(self.tabs)

        root_layout.addWidget(content_card, 1)

        self.status_label = QLabel("Ready • Select a tool above to get started.")
        self.status_label.setObjectName("StatusStrip")
        self.status_label.setAlignment(Qt.AlignCenter)
        root_layout.addWidget(self.status_label)

        self.apply_theme(self.current_theme)

    def apply_theme(self, theme):
        if theme == "neon":
            stylesheet = """
                QWidget {
                    background-color: #040910;
                    color: #E4FFF9;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                }
                QLabel {
                    background-color: transparent;
                }
                QLabel#TitleLabel {
                    font-size: 24px;
                    font-weight: 600;
                    color: #3CFFDD;
                }
                QLabel#SubtitleLabel {
                    font-size: 13px;
                    color: #84FFE8;
                }
                QLabel#TabHeading {
                    font-size: 18px;
                    font-weight: 600;
                    color: #3CFFDD;
                }
                QLabel#TabSubheading {
                    font-size: 12px;
                    color: #9AFEF1;
                }
                QLabel#FieldLabel {
                    font-size: 13px;
                    font-weight: 600;
                    color: #9AFEF1;
                }
                QLabel#MetricLabel {
                    font-size: 12px;
                    color: #73F5D6;
                }
                QLabel#StatusStrip {
                    background-color: rgba(12, 24, 40, 0.85);
                    border: 1px solid rgba(60, 255, 221, 0.35);
                    border-radius: 16px;
                    padding: 14px;
                    color: #88FFF0;
                }
                QFrame#HeaderCard {
                    background-color: rgba(8, 18, 34, 0.9);
                    border: 1px solid rgba(60, 255, 221, 0.45);
                    border-radius: 28px;
                }
                QFrame#ContentCard {
                    background-color: rgba(6, 14, 26, 0.95);
                    border: 1px solid rgba(60, 255, 221, 0.3);
                    border-radius: 28px;
                }
                QTabWidget#MainTabs::pane {
                    border: 1px solid rgba(60, 255, 221, 0.28);
                    border-radius: 18px;
                    padding: 16px;
                    background-color: rgba(8, 18, 34, 0.88);
                    margin-top: 10px;
                }
                QTabWidget#MainTabs > QWidget {
                    background-color: transparent;
                }
                QScrollArea {
                    background-color: transparent;
                    border: none;
                }
                QScrollArea > QWidget > QWidget {
                    background-color: transparent;
                }
                QTabBar::tab {
                    background-color: rgba(9, 22, 38, 0.9);
                    border: 1px solid rgba(60, 255, 221, 0.35);
                    padding: 8px 22px;
                    border-radius: 16px;
                    margin-right: 8px;
                    color: #8EFFF0;
                }
                QTabBar::tab:selected {
                    background-color: rgba(14, 32, 52, 0.95);
                    color: #3CFFDD;
                    border: 1px solid rgba(60, 255, 221, 0.6);
                }
                QTabBar::tab:hover {
                    color: #3CFFDD;
                }
                QPushButton {
                    background-color: rgba(10, 24, 40, 0.9);
                    border: 1px solid rgba(60, 255, 221, 0.35);
                    border-radius: 12px;
                    padding: 8px 18px;
                    color: #E4FFF9;
                }
                QPushButton:hover {
                    background-color: rgba(14, 32, 52, 0.95);
                }
                QPushButton:pressed {
                    background-color: rgba(6, 14, 24, 0.9);
                }
                QPushButton:disabled {
                    color: rgba(150, 210, 210, 0.4);
                    border: 1px solid rgba(60, 100, 100, 0.25);
                }
                QPushButton#AccentButton {
                    background-color: #3CFFDD;
                    color: #002A24;
                    font-weight: 600;
                    border-radius: 18px;
                    padding: 10px 26px;
                }
                QPushButton#AccentButton:hover {
                    background-color: #67FFE6;
                }
                QPushButton#AccentButton:pressed {
                    background-color: #2CE2C5;
                }
                QLineEdit, QTextEdit, QComboBox, QSpinBox {
                    background-color: rgba(12, 28, 50, 0.92);
                    border: 1px solid rgba(60, 255, 221, 0.45);
                    border-radius: 8px;
                    padding: 8px 10px;
                    selection-background-color: #3CFFDD;
                    selection-color: #001824;
                    color: #E4FFF9;
                }
                QLineEdit::placeholder {
                    color: rgba(150, 255, 240, 0.55);
                }
                QTextEdit#TerminalOutput {
                    font-family: 'Cascadia Code', 'Consolas', monospace;
                    font-size: 13px;
                }
                QComboBox::drop-down {
                    border-left: 1px solid rgba(60, 255, 221, 0.35);
                    width: 26px;
                    background-color: transparent;
                }
                QComboBox QAbstractItemView {
                    background-color: rgba(6, 14, 24, 0.98);
                    border: 1px solid rgba(60, 255, 221, 0.35);
                    selection-background-color: #3CFFDD;
                    selection-color: #002A24;
                }
                QScrollBar:vertical, QScrollBar:horizontal {
                    background-color: rgba(5, 12, 24, 0.95);
                    border: 1px solid rgba(60, 255, 221, 0.25);
                    margin: 6px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                    background-color: rgba(60, 255, 221, 0.35);
                    border-radius: 6px;
                    min-height: 32px;
                }
                QScrollBar::handle:hover {
                    background-color: rgba(60, 255, 221, 0.55);
                }
                QScrollBar::add-line, QScrollBar::sub-line {
                    background: transparent;
                    border: none;
                    height: 0px;
                    width: 0px;
                }
                QScrollBar::add-page, QScrollBar::sub-page {
                    background: transparent;
                }
            """
            self.theme_btn.setText("Switch to Light Theme")
            logo_path = resource_path("icons/gatchfier_logo.png")
        else:
            stylesheet = """
                QWidget {
                    background-color: #f4f6fb;
                    color: #1a1d25;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                }
                QLabel {
                    background-color: transparent;
                }
                QLabel#TitleLabel {
                    font-size: 24px;
                    font-weight: 600;
                    color: #113f73;
                }
                QLabel#SubtitleLabel {
                    font-size: 13px;
                    color: #3d4d63;
                }
                QLabel#TabHeading {
                    font-size: 18px;
                    font-weight: 600;
                    color: #113f73;
                }
                QLabel#TabSubheading {
                    font-size: 12px;
                    color: #4a5c78;
                }
                QLabel#FieldLabel {
                    font-size: 13px;
                    font-weight: 600;
                    color: #3d4d63;
                }
                QLabel#MetricLabel {
                    font-size: 12px;
                    color: #4a5c78;
                }
                QLabel#StatusStrip {
                    background-color: #ffffff;
                    border: 1px solid #d0d6e2;
                    border-radius: 16px;
                    padding: 14px;
                    color: #3d4d63;
                }
                QFrame#HeaderCard {
                    background-color: #ffffff;
                    border: 1px solid #d0d6e2;
                    border-radius: 28px;
                }
                QFrame#ContentCard {
                    background-color: #ffffff;
                    border: 1px solid #d0d6e2;
                    border-radius: 28px;
                }
                QTabWidget#MainTabs::pane {
                    border: 1px solid #d8deea;
                    border-radius: 18px;
                    padding: 16px;
                    background-color: #ffffff;
                    margin-top: 10px;
                }
                QTabWidget#MainTabs > QWidget {
                    background-color: transparent;
                }
                QScrollArea {
                    background-color: transparent;
                    border: none;
                }
                QScrollArea > QWidget > QWidget {
                    background-color: transparent;
                }
                QTabBar::tab {
                    background: #eef1f7;
                    border: 1px solid #ccd4e2;
                    padding: 8px 22px;
                    border-radius: 16px;
                    margin-right: 8px;
                    color: #46556f;
                }
                QTabBar::tab:selected {
                    background: #ffffff;
                    color: #0f4c81;
                    border: 1px solid #0f4c81;
                }
                QPushButton {
                    background-color: #eef1f7;
                    border: 1px solid #ccd4e2;
                    border-radius: 12px;
                    padding: 8px 18px;
                    color: #1a1d25;
                }
                QPushButton:hover {
                    background-color: #e2e7f1;
                }
                QPushButton:pressed {
                    background-color: #d4dae6;
                }
                QPushButton#AccentButton {
                    background-color: #0f4c81;
                    color: #ffffff;
                    font-weight: 600;
                    border-radius: 18px;
                    padding: 10px 26px;
                }
                QPushButton#AccentButton:hover {
                    background-color: #145f9b;
                }
                QPushButton#AccentButton:pressed {
                    background-color: #0c3c66;
                }
                QLineEdit, QTextEdit, QComboBox, QSpinBox {
                    background-color: #ffffff;
                    border: 1px solid #c7cfde;
                    border-radius: 8px;
                    padding: 8px 10px;
                    selection-background-color: #0f4c81;
                    selection-color: #ffffff;
                }
                QTextEdit#TerminalOutput {
                    font-family: 'Cascadia Code', 'Consolas', monospace;
                    font-size: 13px;
                }
                QComboBox::drop-down {
                    border-left: 1px solid #c7cfde;
                    width: 26px;
                    background-color: transparent;
                }
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    border: 1px solid #c7cfde;
                    selection-background-color: #0f4c81;
                    selection-color: #ffffff;
                }
                QScrollBar:vertical, QScrollBar:horizontal {
                    background-color: #f1f4fb;
                    border: 1px solid #d8deea;
                    margin: 6px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                    background-color: #c7cfde;
                    border-radius: 6px;
                    min-height: 32px;
                }
                QScrollBar::handle:hover {
                    background-color: #a8b4c9;
                }
                QScrollBar::add-line, QScrollBar::sub-line {
                    background: transparent;
                    border: none;
                    height: 0px;
                    width: 0px;
                }
                QScrollBar::add-page, QScrollBar::sub-page {
                    background: transparent;
                }
            """
            self.theme_btn.setText("Switch to Neon Theme")
            logo_path = resource_path("icons/gatchfier_logo_dark.png")

        self.setStyleSheet(stylesheet)
        self.logo_label.setPixmap(
            QPixmap(logo_path).scaled(120, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "neon" else "neon"
        self.apply_theme(self.current_theme)
        save_theme(self.current_theme)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    theme = load_theme()
    splash = show_splash(app, theme)

    window = MainWindow()
    window.show()

    splash.finish(window)
    sys.exit(app.exec())
