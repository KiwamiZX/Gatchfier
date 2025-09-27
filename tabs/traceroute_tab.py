import platform
import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTextEdit,
    QPushButton, QLabel, QComboBox
)
from PySide6.QtCore import QThread, Signal

class TracerouteWorker(QThread):
    update = Signal(str)
    finished = Signal()

    def __init__(self, host, use_ipv6=False):
        super().__init__()
        self.host = host
        self.use_ipv6 = use_ipv6
        self._process = None
        self._stop_requested = False

    def run(self):
        try:
            system = platform.system()
            if system == "Windows":
                if self.use_ipv6:
                    cmd = ["tracert", "-6", self.host]
                else:
                    cmd = ["tracert", "-4", self.host]
            else:
                if self.use_ipv6:
                    cmd = ["traceroute", "-6", self.host]
                else:
                    cmd = ["traceroute", "-4", self.host]

            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in self._process.stdout:
                if self._stop_requested:
                    self._process.terminate()
                    self.update.emit("\nTraceroute stopped by user.")
                    break
                self.update.emit(line.strip())

            self._process.wait()
        except Exception as e:
            self.update.emit(f"Error: {e}")
        finally:
            self.finished.emit()

    def stop(self):
        self._stop_requested = True
        if self._process:
            self._process.terminate()

class TracerouteTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        title = QLabel("🧭 Traceroute Utility")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Enter host to trace (e.g., google.com)")
        layout.addWidget(self.host_input)

        self.protocol_select = QComboBox()
        self.protocol_select.addItems(["IPv4", "IPv6"])
        layout.addWidget(self.protocol_select)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.trace_btn = QPushButton("Start Traceroute")
        layout.addWidget(self.trace_btn)

        self.trace_btn.clicked.connect(self.toggle_trace)
        self.worker = None
        self.tracing = False

        self.setLayout(layout)

    def toggle_trace(self):
        if self.tracing:
            self.stop_trace()
        else:
            self.start_trace()

    def start_trace(self):
        self.output.clear()
        host = self.host_input.text().strip()
        if not host:
            self.output.append("Please enter a host.")
            return

        use_ipv6 = self.protocol_select.currentText() == "IPv6"
        self.worker = TracerouteWorker(host, use_ipv6)
        self.worker.update.connect(self.output.append)
        self.worker.finished.connect(self.trace_finished)

        self.trace_btn.setText("Stop Traceroute")
        self.tracing = True
        self.worker.start()

    def stop_trace(self):
        if self.worker:
            self.worker.stop()
        self.trace_btn.setText("Stopping...")
        self.trace_btn.setEnabled(False)

    def trace_finished(self):
        self.tracing = False
        self.trace_btn.setText("Start Traceroute")
        self.trace_btn.setEnabled(True)
