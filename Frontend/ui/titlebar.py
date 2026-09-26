from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)
        self.setObjectName("titlebar")
        self._drag_pos = QPoint()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 12, 6)
        layout.setSpacing(10)

        self.app_icon = QLabel("J")
        self.app_icon.setObjectName("title-icon")
        self.app_name = QLabel("Jarvis AI")
        self.app_name.setObjectName("title-name")

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Sidebar toggle button
        self.sidebar_toggle = QPushButton("☰")
        self.sidebar_toggle.setObjectName("sidebar-toggle")
        self.sidebar_toggle.setFixedSize(32, 26)
        self.sidebar_toggle.setCursor(Qt.PointingHandCursor)
        self.sidebar_toggle.setToolTip("Toggle chat history")

        self.min_button = QPushButton("—")
        self.close_button = QPushButton("×")
        self.min_button.setObjectName("title-button")
        self.close_button.setObjectName("title-button-close")

        self.min_button.clicked.connect(parent.showMinimized if parent else lambda: None)
        self.close_button.clicked.connect(parent.close if parent else lambda: None)

        layout.addWidget(self.app_icon)
        layout.addWidget(self.app_name)
        layout.addWidget(spacer)
        layout.addWidget(self.sidebar_toggle)
        layout.addWidget(self.min_button)
        layout.addWidget(self.close_button)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
