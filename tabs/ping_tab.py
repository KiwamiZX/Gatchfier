from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QTextEdit, QLabel, QComboBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
import ping3
import socket

class PingTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        title = QLabel("🔍 Ping Utility")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Enter host to ping (e.g., google.com)")
        layout.addWidget(self.host_input)

        self.protocol_select = QComboBox()
        self.protocol_select.addItems(["IPv4", "IPv6"])
        layout.addWidget(self.protocol_select)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        btn_layout = QHBoxLayout()
        self.ping_btn = QPushButton("Ping 4 Times")
        self.ping_btn.setIcon(QIcon("icons/ping.png"))
        self.continuous_btn = QPushButton("Start Continuous Ping")
        self.continuous_btn.setIcon(QIcon("icons/start.png"))
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setIcon(QIcon("icons/stop.png"))
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.ping_btn)
        btn_layout.addWidget(self.continuous_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.ping_once)

        self.sent = 0
        self.received = 0
        self.times = []
        self.continuous = False
        self.ping_count = 0
        self.resolved_ip = None

        self.ping_btn.clicked.connect(self.ping_summary)
        self.continuous_btn.clicked.connect(self.start_continuous)
        self.stop_btn.clicked.connect(self.stop_ping)

        self.setLayout(layout)

    def resolve_ip(self):
        host = self.host_input.text()
        family = socket.AF_INET6 if self.protocol_select.currentText() == "IPv6" else socket.AF_INET
        try:
            info = socket.getaddrinfo(host, None, family)
            self.resolved_ip = info[0][4][0]
            self.output.append(f"Resolved IP: {self.resolved_ip}")
        except Exception as e:
            self.output.append(f"Could not resolve IP: {e}")
            self.resolved_ip = None

    def ping_once(self):
        ping3.IPV6 = self.protocol_select.currentText() == "IPv6"
        self.sent += 1
        result = ping3.ping(self.resolved_ip or self.host_input.text(), unit='ms')
        if isinstance(result, float):
            self.output.append(f"Reply from {self.resolved_ip}: time={result:.2f}ms")
            self.received += 1
            self.times.append(result)
        else:
            self.output.append("Request timed out")

        if not self.continuous:
            self.ping_count -= 1
            if self.ping_count <= 0:
                self.stop_ping()

    def ping_summary(self):
        self.output.clear()
        self.sent = self.received = 0
        self.times = []
        self.continuous = False
        self.ping_count = 4
        self.stop_btn.setEnabled(True)
        self.resolve_ip()
        self.timer.start(1000)

    def start_continuous(self):
        self.output.clear()
        self.sent = self.received = 0
        self.times = []
        self.continuous = True
        self.stop_btn.setEnabled(True)
        self.resolve_ip()
        self.timer.start(1000)

    def stop_ping(self):
        self.timer.stop()
        self.stop_btn.setEnabled(False)
        self.show_summary()

    def show_summary(self):
        lost = self.sent - self.received
        host = self.host_input.text()
        if self.times:
            min_time = min(self.times)
            max_time = max(self.times)
            avg_time = sum(self.times) / len(self.times)
            summary = (
                f"\nPing statistics for {host} ({self.resolved_ip}):\n"
                f"    Packets: Sent = {self.sent}, Received = {self.received}, Lost = {lost}\n"
                f"Approximate round trip times:\n"
                f"    Minimum = {min_time:.2f}ms, Maximum = {max_time:.2f}ms, Average = {avg_time:.2f}ms"
            )
        else:
            summary = f"\nAll requests to {host} ({self.resolved_ip}) timed out."
        self.output.append(summary)
