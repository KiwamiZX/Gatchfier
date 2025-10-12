import socket

import ping3
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QLabel,
    QComboBox,
    QScrollArea,
    QFrame,
)


class PingTab(QWidget):
    def __init__(self):
        super().__init__()

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer_layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Ping Utility")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title.setObjectName("TabHeading")
        layout.addWidget(title)

        subtitle = QLabel("Send ICMP echo requests to measure latency and packet loss.")
        subtitle.setObjectName("TabSubheading")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Host or IP address (e.g., example.com)")
        layout.addWidget(self.host_input)

        protocol_row = QHBoxLayout()
        protocol_row.setSpacing(8)

        protocol_label = QLabel("Protocol:")
        protocol_label.setObjectName("FieldLabel")
        protocol_row.addWidget(protocol_label)

        self.protocol_select = QComboBox()
        self.protocol_select.addItems(["IPv4", "IPv6"])
        protocol_row.addWidget(self.protocol_select, 1)

        layout.addLayout(protocol_row)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(8)

        self.ping_btn = QPushButton("Ping 4 Times")
        buttons_row.addWidget(self.ping_btn)

        self.continuous_btn = QPushButton("Start Continuous Ping")
        buttons_row.addWidget(self.continuous_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        buttons_row.addWidget(self.stop_btn)

        layout.addLayout(buttons_row)

        self.stats_label = QLabel("Packets - Sent: 0 | Received: 0 | Loss: 0% | Target: idle")
        self.stats_label.setObjectName("MetricLabel")
        layout.addWidget(self.stats_label)

        self.output = QTextEdit()
        self.output.setObjectName("TerminalOutput")
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(200)
        layout.addWidget(self.output, 1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.ping_once)

        self.continuous = False
        self.ping_count = 0
        self.reset_counters()

        self.ping_btn.clicked.connect(self.ping_summary)
        self.continuous_btn.clicked.connect(self.start_continuous)
        self.stop_btn.clicked.connect(self.stop_ping)

    def resolve_ip(self):
        host = self.host_input.text()
        family = socket.AF_INET6 if self.protocol_select.currentText() == "IPv6" else socket.AF_INET
        try:
            info = socket.getaddrinfo(host, None, family)
            self.resolved_ip = info[0][4][0]
            self.output.append(f"Resolved IP: {self.resolved_ip}")
        except Exception as exc:  # pylint: disable=broad-except
            self.output.append(f"Could not resolve IP: {exc}")
            self.resolved_ip = None
        finally:
            self.update_stats_label()

    def ping_once(self):
        ping3.IPV6 = self.protocol_select.currentText() == "IPv6"
        self.sent += 1
        result = ping3.ping(self.resolved_ip or self.host_input.text(), unit="ms")
        if isinstance(result, float):
            target = self.resolved_ip or self.host_input.text()
            self.output.append(f"Reply from {target}: time={result:.2f} ms")
            self.received += 1
            self.times.append(result)
        else:
            self.output.append("Request timed out")

        self.update_stats_label()

        if not self.continuous:
            self.ping_count -= 1
            if self.ping_count <= 0:
                self.stop_ping()

    def ping_summary(self):
        self.output.clear()
        self.reset_counters()
        self.continuous = False
        self.ping_count = 4
        self.stop_btn.setEnabled(True)
        self.resolve_ip()
        self.timer.start(1000)

    def start_continuous(self):
        self.output.clear()
        self.reset_counters()
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
            minimum = min(self.times)
            maximum = max(self.times)
            average = sum(self.times) / len(self.times)
            summary = (
                f"\nPing statistics for {host} ({self.resolved_ip or 'unresolved'}):\n"
                f"  Packets: Sent = {self.sent}, Received = {self.received}, Lost = {lost}\n"
                f"Approximate round trip times:\n"
                f"  Minimum = {minimum:.2f} ms, Maximum = {maximum:.2f} ms, Average = {average:.2f} ms"
            )
        else:
            summary = f"\nAll requests to {host} ({self.resolved_ip or 'unresolved'}) timed out."
        self.output.append(summary)
        self.update_stats_label()

    def reset_counters(self):
        self.sent = 0
        self.received = 0
        self.times = []
        self.resolved_ip = None
        self.update_stats_label()

    def update_stats_label(self):
        loss = 0
        if self.sent:
            loss = int(round(((self.sent - self.received) / self.sent) * 100))
        target = self.resolved_ip or self.host_input.text().strip() or "idle"
        self.stats_label.setText(
            f"Packets - Sent: {self.sent} | Received: {self.received} | Loss: {loss}% | Target: {target}"
        )
