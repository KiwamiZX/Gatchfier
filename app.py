import sys, json, os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QLabel, QSplashScreen
)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QSize

from tabs.ping_tab import PingTab
from tabs.traceroute_tab import TracerouteTab
from tabs.portscan_tab import PortScannerTab
from tabs.dns_tab import DNSTab
from tabs.whois import WhoisTab

# 🔧 Access bundled resources (for PyInstaller)
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 🔧 Get writable config path in user home
def get_config_path():
    config_dir = os.path.join(os.path.expanduser("~"), ".gatchfier")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.json")

CONFIG_WRITE_PATH = get_config_path()
CONFIG_READ_PATH = resource_path("config.json")

def load_theme():
    if os.path.exists(CONFIG_WRITE_PATH):
        with open(CONFIG_WRITE_PATH, "r") as f:
            return json.load(f).get("theme", "dark")
    elif os.path.exists(CONFIG_READ_PATH):
        with open(CONFIG_READ_PATH, "r") as f:
            return json.load(f).get("theme", "dark")
    return "dark"

def save_theme(theme):
    with open(CONFIG_WRITE_PATH, "w") as f:
        json.dump({"theme": theme}, f)

def show_splash(app, theme):
    if theme == "dark":
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
        self.resize(600, 400)

        self.current_theme = load_theme()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(10, 10, 10, 0)
        top_bar.setSpacing(10)

        self.logo_label = QLabel()
        pixmap = QPixmap(resource_path("icons/gatchfier_logo.png")).scaled(170, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        top_bar.addWidget(self.logo_label)

        top_bar.addStretch()

        self.theme_btn = QPushButton()
        self.theme_btn.setFixedSize(32, 32)
        self.theme_btn.setIconSize(self.theme_btn.size())
        self.theme_btn.setFlat(True)
        self.theme_btn.setToolTip("Toggle Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.theme_btn)

        main_layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        self.tabs.addTab(PingTab(), "Ping")
        self.tabs.addTab(TracerouteTab(), "Traceroute")
        self.tabs.addTab(PortScannerTab(), "Port Scan")
        self.tabs.addTab(DNSTab(), "DNS Lookup")
        self.tabs.addTab(WhoisTab(), "Whois")
        main_layout.addWidget(self.tabs)

        self.apply_theme(self.current_theme)

    def apply_theme(self, theme):
        if theme == "dark":
            stylesheet = """
                QWidget { background-color: #121212; color: #e0e0e0; font-family: Segoe UI; font-size: 14px; }
                QLineEdit, QTextEdit { background-color: #1e1e1e; border: 1px solid #333; color: #e0e0e0; }
                QPushButton { background-color: #2c2c2c; border: 1px solid #555; padding: 5px; }
                QPushButton:hover { background-color: #3c3c3c; }
                QTabWidget::pane { border: 1px solid #444; }
                QTabBar::tab { background: #2c2c2c; padding: 8px; }
                QTabBar::tab:selected { background: #444; }
            """
            icon_path = resource_path("icons/moon.png")
            logo_path = resource_path("icons/gatchfier_logo.png")
        else:
            stylesheet = """
                QWidget { background-color: #f0f0f0; color: #202020; font-family: Segoe UI; font-size: 14px; }
                QLineEdit, QTextEdit { background-color: #ffffff; border: 1px solid #ccc; color: #202020; }
                QPushButton { background-color: #e0e0e0; border: 1px solid #aaa; padding: 5px; }
                QPushButton:hover { background-color: #d0d0d0; }
                QTabWidget::pane { border: 1px solid #aaa; }
                QTabBar::tab { background: #e0e0e0; padding: 8px; }
                QTabBar::tab:selected { background: #c0c0c0; }
            """
            icon_path = resource_path("icons/sun.png")
            logo_path = resource_path("icons/gatchfier_logo_dark.png")

        self.setStyleSheet(stylesheet)
        self.theme_btn.setIcon(QIcon(icon_path))
        self.logo_label.setPixmap(QPixmap(logo_path).scaled(170, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
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
