import socket
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTextEdit,
    QPushButton, QLabel, QComboBox
)

class DNSTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        title = QLabel("🌐 DNS Lookup")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Enter domain (e.g., google.com)")
        layout.addWidget(self.domain_input)

        self.protocol_select = QComboBox()
        self.protocol_select.addItems(["IPv4", "IPv6"])
        layout.addWidget(self.protocol_select)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.lookup_btn = QPushButton("Resolve")
        layout.addWidget(self.lookup_btn)

        self.lookup_btn.clicked.connect(self.resolve_dns)

        self.setLayout(layout)

    def resolve_dns(self):
        self.output.clear()
        domain = self.domain_input.text().strip()
        if not domain:
            self.output.append("⚠️ Please enter a domain.")
            return

        family = socket.AF_INET6 if self.protocol_select.currentText() == "IPv6" else socket.AF_INET

        try:
            results = socket.getaddrinfo(domain, None, family)
            unique_ips = sorted(set([res[4][0] for res in results]))
            self.output.append(f"✅ {domain} resolves to:")
            for ip in unique_ips:
                self.output.append(f"  - {ip}")
        except Exception as e:
            self.output.append(f"❌ Error: {e}")
