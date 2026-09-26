from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class ResponsePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("response-panel")
        self.setVisible(False)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 18, 20, 18)
        self.layout.setSpacing(10)

        self.user_query = QLabel("")
        self.user_query.setObjectName("user-query")
        self.user_query.setWordWrap(True)

        self.answer = QLabel("")
        self.answer.setObjectName("assistant-answer")
        self.answer.setWordWrap(True)
        self.answer.setAlignment(Qt.AlignTop)

        self.controls = QWidget(self)
        self.controls.setObjectName("response-controls")
        self.controls_layout = QVBoxLayout(self.controls)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)

        self.copy_button = QPushButton("Copy")
        self.copy_button.setObjectName("copy-button")

        self.layout.addWidget(self.user_query)
        self.layout.addWidget(self.answer)
        self.layout.addWidget(self.copy_button)

    def set_query(self, text: str):
        self.user_query.setText(text)

    def set_answer(self, text: str):
        self.answer.setText(text)
        self.setVisible(bool(text))

    def set_error(self, message: str):
        self.answer.setText(message)
        self.setVisible(True)
