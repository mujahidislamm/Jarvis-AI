from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton

from Frontend.widgets.waveform import Waveform


class InputBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("input-bar")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(14, 10, 14, 10)
        self.layout.setSpacing(10)

        self.mic_button = QPushButton("🎙")
        self.mic_button.setObjectName("mic-button")
        self.mic_button.setFixedSize(42, 42)
        self.mic_button.setCursor(Qt.PointingHandCursor)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask Jarvis anything…")
        self.input_field.setObjectName("assistant-input")

        self.send_button = QPushButton("➤")
        self.send_button.setObjectName("send-button")
        self.send_button.setFixedSize(42, 42)
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.input_field.returnPressed.connect(self.send_button.click)

        self.waveform = Waveform(self)
        self.waveform.setVisible(False)

        self.layout.addWidget(self.mic_button)
        self.layout.addWidget(self.input_field, 1)
        self.layout.addWidget(self.send_button)

    def set_state(self, state: str):
        is_active = state == "LISTENING"
        self.waveform.setVisible(is_active)
        self.waveform.set_active(is_active)
        self.setEnabled(state != "PROCESSING")
        if state == "PROCESSING":
            self.input_field.setPlaceholderText("Thinking…")
        else:
            self.input_field.setPlaceholderText("Ask Jarvis anything…")
