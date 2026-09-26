from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class QuickActionCard(QWidget):
    """A single quick-action card with a gradient accent stripe at the top."""

    ACCENT_NAMES = {
        "violet": "quick-card-accent-violet",
        "teal": "quick-card-accent-teal",
        "amber": "quick-card-accent-amber",
    }

    def __init__(self, title: str, description: str, accent: str = "violet", parent=None):
        super().__init__(parent)
        self.setObjectName("quick-card")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(18, 0, 18, 16)
        self.main_layout.setSpacing(10)

        # Gradient accent stripe
        self.accent_bar = QWidget()
        self.accent_bar.setObjectName(self.ACCENT_NAMES.get(accent, "quick-card-accent-violet"))
        self.accent_bar.setFixedHeight(3)
        self.main_layout.addWidget(self.accent_bar)

        # Spacing after stripe
        self.main_layout.addSpacing(6)

        self.label = QLabel(title)
        self.label.setObjectName("quick-card-title")

        self.desc = QLabel(description)
        self.desc.setObjectName("quick-card-desc")
        self.desc.setWordWrap(True)

        self.run_btn = QPushButton("RUN")
        self.run_btn.setObjectName("quick-run")
        self.run_btn.setCursor(Qt.PointingHandCursor)

        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.desc)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.run_btn)


class QuickActionsRow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(16)

        self.cards = [
            QuickActionCard("Open App", "Launch a targeted application", accent="violet", parent=self),
            QuickActionCard("Web Search", "Search the web for fresh results", accent="teal", parent=self),
            QuickActionCard("Automation", "Carry out a task flow", accent="amber", parent=self),
        ]

        for card in self.cards:
            self.layout.addWidget(card, 1)
