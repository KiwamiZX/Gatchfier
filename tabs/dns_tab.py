import socket

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QHBoxLayout,
    QScrollArea,
    QFrame,
)


class DNSTab(QWidget):
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

        title = QLabel("DNS Lookup")
        title.setObjectName("TabHeading")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(title)

        subtitle = QLabel("Resolve hostnames to IPv4 or IPv6 addresses using system DNS.")
        subtitle.setObjectName("TabSubheading")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Domain or host (e.g., example.com)")
        layout.addWidget(self.domain_input)

        options_row = QHBoxLayout()
        options_row.setSpacing(8)

        protocol_label = QLabel("Protocol:")
        protocol_label.setObjectName("FieldLabel")
        options_row.addWidget(protocol_label)

        self.protocol_select = QComboBox()
        self.protocol_select.addItems(["IPv4", "IPv6"])
        options_row.addWidget(self.protocol_select, 1)

        self.lookup_btn = QPushButton("Resolve")
        options_row.addWidget(self.lookup_btn)

        options_row.addStretch(1)
        layout.addLayout(options_row)

        self.output = QTextEdit()
        self.output.setObjectName("TerminalOutput")
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(200)
        layout.addWidget(self.output, 1)

        self.lookup_btn.clicked.connect(self.resolve_dns)

    def resolve_dns(self):
        self.output.clear()
        domain = self.domain_input.text().strip()
        if not domain:
            self.output.append("Please enter a domain before resolving.")
            return

        family = socket.AF_INET6 if self.protocol_select.currentText() == "IPv6" else socket.AF_INET

        try:
            results = socket.getaddrinfo(domain, None, family)
            unique_ips = sorted({res[4][0] for res in results})
            if unique_ips:
                self.output.append(f"{domain} resolves to:")
                for ip in unique_ips:
                    self.output.append(f"  - {ip}")
            else:
                self.output.append(f"No {self.protocol_select.currentText()} records found for {domain}.")
        except Exception as exc:  # pylint: disable=broad-except
            self.output.append(f"Lookup error: {exc}")
