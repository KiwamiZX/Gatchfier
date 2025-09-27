import whois
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTextEdit,
    QPushButton, QLabel
)

class WhoisTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        title = QLabel("🔎 Whois Lookup")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Enter domain (e.g., google.com)")
        layout.addWidget(self.domain_input)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.lookup_btn = QPushButton("Lookup")
        layout.addWidget(self.lookup_btn)

        self.lookup_btn.clicked.connect(self.run_lookup)

        self.setLayout(layout)

    def run_lookup(self):
        self.output.clear()
        domain = self.domain_input.text().strip()
        if not domain:
            self.output.append("⚠️ Please enter a domain.")
            return

        try:
            w = whois.whois(domain)
            self.output.append(f"✅ Whois info for {domain}:\n")
            for key in ["domain_name", "registrar", "creation_date", "expiration_date", "name_servers", "emails"]:
                value = w.get(key)
                if value:
                    self.output.append(f"{key.capitalize().replace('_', ' ')}: {value}")
        except Exception as e:
            self.output.append(f"❌ Error: {e}")
