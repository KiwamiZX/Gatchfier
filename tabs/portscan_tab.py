import socket
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QLabel
from PySide6.QtCore import QThread, Signal
from concurrent.futures import ThreadPoolExecutor, as_completed

# Common ports and their services
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
    5900: "VNC",
    8080: "HTTP-Alt",
    6379: "Redis",
    5432: "PostgreSQL",
    27017: "MongoDB"
}

class PortScannerWorker(QThread):
    update = Signal(str)
    finished = Signal(list)

    def __init__(self, host):
        super().__init__()
        self.host = host
        self.running = True

    def run(self):
        open_ports = []
        self.update.emit(f"🔍 Starting full scan on {self.host}...\n")

        def scan_port(port):
            if not self.running:
                return None
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.3)
                    result = s.connect_ex((self.host, port))
                    if result == 0:
                        service = COMMON_SERVICES.get(port, "Unknown")
                        self.update.emit(f"🟢 Port {port}: Open ({service})")
                        return (port, service)
            except:
                pass
            return None

        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(scan_port, port): port for port in range(1, 65536)}
            for i, future in enumerate(as_completed(futures)):
                if not self.running:
                    break
                result = future.result()
                if result:
                    open_ports.append(result)
                if i % 5000 == 0:
                    self.update.emit(f"Progress: {i}/65535 ports scanned...")

        self.finished.emit(open_ports)

    def stop(self):
        self.running = False

class PortScannerTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        title = QLabel("🛡️ Port Scanner")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Enter host to scan (e.g., google.com)")
        layout.addWidget(self.host_input)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.scan_btn = QPushButton("Start Full Scan")
        layout.addWidget(self.scan_btn)

        self.scan_btn.clicked.connect(self.toggle_scan)
        self.worker = None
        self.scanning = False

        self.setLayout(layout)

    def toggle_scan(self):
        if self.scanning:
            self.output.append("\n⏹️ Stopping scan...")
            self.worker.stop()
            self.scan_btn.setEnabled(False)
        else:
            self.start_scan()

    def start_scan(self):
        self.output.clear()
        host = self.host_input.text()
        if not host:
            self.output.append("⚠️ Please enter a host.")
            return

        self.worker = PortScannerWorker(host)
        self.worker.update.connect(self.output.append)
        self.worker.finished.connect(self.show_summary)
        self.worker.start()

        self.scanning = True
        self.scan_btn.setText("Stop Scan")

    def show_summary(self, open_ports):
        self.scanning = False
        self.scan_btn.setText("Start Full Scan")
        self.scan_btn.setEnabled(True)

        self.output.append("\n✅ Scan complete.")
        self.output.append(f"🔢 Total open ports: {len(open_ports)}")
        if open_ports:
            self.output.append("🟢 Open ports:")
            for port, service in sorted(open_ports):
                self.output.append(f"  - {port} ({service})")
        else:
            self.output.append("🚫 No open ports found.")
