from __future__ import annotations

import platform
import shutil
import subprocess
from typing import List

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QSpinBox,
    QScrollArea,
    QFrame,
)


class TracerouteWorker(QThread):
    update = Signal(str)
    finished = Signal(bool)
    error = Signal(str)

    def __init__(self, host: str, use_ipv6: bool = False, max_hops: int = 30, per_hop_timeout: int = 4):
        super().__init__()
        self.host = host
        self.use_ipv6 = use_ipv6
        self.max_hops = max_hops
        self.per_hop_timeout = per_hop_timeout
        self._process: subprocess.Popen | None = None
        self._stop_requested = False

    def run(self):
        try:
            command = self._build_command()
        except ValueError as exc:
            self.error.emit(str(exc))
            self.finished.emit(False)
            return

        try:
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0  # type: ignore[attr-defined]
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace",
                universal_newlines=True,
                creationflags=creationflags,
            )
        except FileNotFoundError:
            self.error.emit(f"Traceroute command not found: {command[0]}")
            self.finished.emit(False)
            return
        except Exception as exc:  # pragma: no cover
            self.error.emit(f"Failed to start traceroute: {exc}")
            self.finished.emit(False)
            return

        if not self._process.stdout:
            self.error.emit("Unable to capture traceroute output.")
            self.finished.emit(False)
            return

        try:
            for raw_line in self._process.stdout:
                if self._stop_requested:
                    break
                line = raw_line.rstrip()
                if line:
                    self.update.emit(line)
        finally:
            if self._stop_requested and self._process:
                self._terminate_process()
            if self._process:
                self._process.wait()
                success = not self._stop_requested and self._process.returncode == 0
                self._process = None
            else:
                success = False
            self.finished.emit(success)

    def stop(self):
        self._stop_requested = True
        self._terminate_process()

    def _terminate_process(self):
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
            except Exception:  # pragma: no cover
                self._process.kill()
        self._process = None

    def _build_command(self) -> List[str]:
        system = platform.system()
        if system == "Windows":
            base_cmd = "tracert"
            if not shutil.which(base_cmd):
                raise ValueError("The 'tracert' command is not available on this system.")
            args = [base_cmd, "-h", str(self.max_hops), "-d", "-6" if self.use_ipv6 else "-4"]
        else:
            base_cmd = "traceroute"
            if not shutil.which(base_cmd):
                raise ValueError("The 'traceroute' command is not available on this system.")
            args = [
                base_cmd,
                "-m",
                str(self.max_hops),
                "-n",
                "-6" if self.use_ipv6 else "-4",
                "-w",
                str(self.per_hop_timeout),
            ]
        args.append(self.host)
        return args


class TracerouteTab(QWidget):
    def __init__(self):
        super().__init__()

        self.worker: TracerouteWorker | None = None
        self.tracing = False
        self.cancelled_by_user = False

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

        title = QLabel("Traceroute Utility")
        title.setObjectName("TabHeading")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(title)

        subtitle = QLabel("Trace the network path to a destination host to diagnose routing issues.")
        subtitle.setObjectName("TabSubheading")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Host or IP address (e.g., example.com)")
        layout.addWidget(self.host_input)

        options_row = QHBoxLayout()
        options_row.setSpacing(8)

        proto_label = QLabel("Protocol:")
        proto_label.setObjectName("FieldLabel")
        options_row.addWidget(proto_label)

        self.protocol_select = QComboBox()
        self.protocol_select.addItems(["IPv4", "IPv6"])
        options_row.addWidget(self.protocol_select)

        self.hops_input = QSpinBox()
        self.hops_input.setRange(1, 60)
        self.hops_input.setValue(30)
        self.hops_input.setPrefix("Max hops: ")
        options_row.addWidget(self.hops_input)

        options_row.addStretch(1)
        layout.addLayout(options_row)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(8)

        self.trace_btn = QPushButton("Start Traceroute")
        buttons_row.addWidget(self.trace_btn)

        self.clear_btn = QPushButton("Clear Log")
        buttons_row.addWidget(self.clear_btn)

        buttons_row.addStretch(1)
        layout.addLayout(buttons_row)

        self.status_label = QLabel("Idle")
        self.status_label.setObjectName("MetricLabel")
        layout.addWidget(self.status_label)

        self.output = QTextEdit()
        self.output.setObjectName("TerminalOutput")
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(200)
        layout.addWidget(self.output, 1)

        self.trace_btn.clicked.connect(self.toggle_trace)
        self.clear_btn.clicked.connect(self.output.clear)

    def toggle_trace(self):
        if self.tracing:
            self.stop_trace()
        else:
            self.start_trace()

    def start_trace(self):
        host = self.host_input.text().strip()
        if not host:
            self.output.append("Please enter a host before starting traceroute.")
            return

        self.output.clear()
        use_ipv6 = self.protocol_select.currentText() == "IPv6"
        max_hops = self.hops_input.value()

        self.worker = TracerouteWorker(host, use_ipv6=use_ipv6, max_hops=max_hops)
        self.worker.update.connect(self.output.append)
        self.worker.error.connect(self.handle_error)
        self.worker.finished.connect(self.trace_finished)

        self.trace_btn.setText("Stop Traceroute")
        self.tracing = True
        self.cancelled_by_user = False
        self.status_label.setText(f"Tracing {host}...")
        self.worker.start()

    def stop_trace(self):
        if self.worker:
            self.cancelled_by_user = True
            self.worker.stop()
        self.trace_btn.setEnabled(False)
        self.trace_btn.setText("Stopping...")
        self.status_label.setText("Stopping traceroute...")

    def trace_finished(self, success: bool):
        self.tracing = False
        self.trace_btn.setEnabled(True)
        self.trace_btn.setText("Start Traceroute")
        if success:
            self.status_label.setText("Trace complete.")
        elif self.cancelled_by_user:
            self.status_label.setText("Trace cancelled.")
        else:
            self.status_label.setText("Trace ended with issues.")
        self.worker = None
        self.cancelled_by_user = False

    def handle_error(self, message: str):
        self.output.append(f"Error: {message}")
        self.status_label.setText(f"Error: {message}")
