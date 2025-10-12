from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QScrollArea,
    QFrame,
)

COMMON_SERVICES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP Alternate",
}


class PortScannerWorker(QThread):
    update = Signal(str)
    finished = Signal(list)

    def __init__(self, host: str):
        super().__init__()
        self.host = host
        self.running = True

    def run(self):
        open_ports = []
        self.update.emit(f"Starting full scan on {self.host}...")

        def scan_port(port: int):
            if not self.running:
                return None
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.3)
                    if sock.connect_ex((self.host, port)) == 0:
                        service = COMMON_SERVICES.get(port, "Unknown")
                        message = f"Port {port}: Open ({service})"
                        self.update.emit(message)
                        return (port, service)
            except Exception:
                return None
            return None

        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(scan_port, port): port for port in range(1, 65536)}
            for index, future in enumerate(as_completed(futures)):
                if not self.running:
                    break
                result = future.result()
                if result:
                    open_ports.append(result)
                if index and index % 5000 == 0:
                    self.update.emit(f"Progress: {index}/65535 ports scanned...")

        self.finished.emit(open_ports)

    def stop(self):
        self.running = False


class PortScannerTab(QWidget):
    def __init__(self):
        super().__init__()

        self.worker: PortScannerWorker | None = None
        self.scanning = False

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

        title = QLabel("Port Scanner")
        title.setObjectName("TabHeading")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(title)

        subtitle = QLabel("Inspect TCP ports on a remote host to identify exposed services.")
        subtitle.setObjectName("TabSubheading")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Host or IP address (e.g., example.com)")
        layout.addWidget(self.host_input)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(8)

        self.scan_btn = QPushButton("Start Full Scan")
        buttons_row.addWidget(self.scan_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        buttons_row.addWidget(self.stop_btn)

        buttons_row.addStretch(1)
        layout.addLayout(buttons_row)

        self.status_label = QLabel("Idle")
        self.status_label.setObjectName("MetricLabel")
        layout.addWidget(self.status_label)

        self.output = QTextEdit()
        self.output.setObjectName("TerminalOutput")
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(240)
        layout.addWidget(self.output, 1)

        self.scan_btn.clicked.connect(self.toggle_scan)
        self.stop_btn.clicked.connect(self.request_stop)

    def toggle_scan(self):
        if self.scanning:
            self.request_stop()
        else:
            self.start_scan()

    def start_scan(self):
        host = self.host_input.text().strip()
        if not host:
            self.output.append("Please enter a host before starting the scan.")
            return

        self.output.clear()
        self.status_label.setText(f"Scanning {host}...")
        self.worker = PortScannerWorker(host)
        self.worker.update.connect(self.output.append)
        self.worker.finished.connect(self.show_summary)
        self.worker.start()

        self.scanning = True
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def request_stop(self):
        if self.worker:
            self.worker.stop()
        self.status_label.setText("Stopping scan...")
        self.stop_btn.setEnabled(False)

    def show_summary(self, open_ports):
        self.scanning = False
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        if open_ports:
            summary = "\nScan complete. Open ports:"
            details = "\n".join(f"  - {port} ({service})" for port, service in sorted(open_ports))
            self.output.append(f"{summary}\n{details}")
        else:
            self.output.append("\nScan complete. No open ports found.")

        self.status_label.setText("Idle")
        self.worker = None
