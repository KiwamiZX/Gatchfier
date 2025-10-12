import datetime
from typing import Any

import whois
from PySide6.QtCore import Qt
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


class WhoisTab(QWidget):
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

        title = QLabel("Whois Lookup")
        title.setObjectName("TabHeading")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(title)

        subtitle = QLabel("Query registry records for a domain to discover registration details.")
        subtitle.setObjectName("TabSubheading")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        form_row = QHBoxLayout()
        form_row.setSpacing(8)

        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Domain (e.g., example.com)")
        form_row.addWidget(self.domain_input, 1)

        self.lookup_btn = QPushButton("Lookup")
        form_row.addWidget(self.lookup_btn)

        form_row.addStretch(1)
        layout.addLayout(form_row)

        self.output = QTextEdit()
        self.output.setObjectName("TerminalOutput")
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(240)
        layout.addWidget(self.output, 1)

        self.lookup_btn.clicked.connect(self.run_lookup)

    def run_lookup(self):
        self.output.clear()
        domain = self.domain_input.text().strip()
        if not domain:
            self.output.append("Please enter a domain before requesting a Whois record.")
            return

        try:
            record = whois.whois(domain)
        except Exception as exc:  # pylint: disable=broad-except
            self.output.append(f"Lookup error: {exc}")
            return

        self.output.append(f"Whois information for {domain}:\n")
        fields = [
            "domain_name",
            "registrar",
            "creation_date",
            "expiration_date",
            "updated_date",
            "status",
            "name_servers",
            "emails",
        ]
        for field in fields:
            value = record.get(field)
            formatted = self._format_value(value)
            if formatted:
                label = field.replace("_", " ").title()
                self.output.append(f"{label}: {formatted}")

    @staticmethod
    def _format_value(value: Any) -> str:
        if not value:
            return ""
        if isinstance(value, (list, tuple, set)):
            return ", ".join(WhoisTab._format_value(item) for item in value if item)
        if isinstance(value, datetime.datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return str(value)
