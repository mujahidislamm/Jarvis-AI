from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from Frontend.widgets.glow_aura import GlowAura


class HeroWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("hero")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)

        self.aura = GlowAura(self)
        self.aura.setObjectName("hero-aura")
        self.layout.addWidget(self.aura)

        self.wordmark = QLabel("Jarvis")
        self.wordmark.setObjectName("app-wordmark")
        self.wordmark.setAlignment(Qt.AlignCenter)
        self.wordmark.setAttribute(Qt.WA_TranslucentBackground)

        self.tagline = QLabel("Your Intelligent Assistant")
        self.tagline.setObjectName("hero-tagline")
        self.tagline.setAlignment(Qt.AlignCenter)

        self.subtitle = QLabel("Tap the mic or type to begin")
        self.subtitle.setObjectName("hero-subtitle")
        self.subtitle.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.wordmark)
        self.layout.addWidget(self.tagline)
        self.layout.addWidget(self.subtitle)

        self._pulse = QPropertyAnimation(self.aura, b"opacity", self)
        self._pulse.setTargetObject(self.aura)
        self._pulse.setDuration(2200)
        self._pulse.setLoopCount(-1)
        self._pulse.setStartValue(0.18)
        self._pulse.setEndValue(0.60)
        self._pulse.setEasingCurve(QEasingCurve.InOutSine)
        self._pulse.start()

    def set_state(self, state: str):
        states = {
            "IDLE": "Tap the mic or type to begin",
            "LISTENING": "Listening…",
            "PROCESSING": "Thinking…",
            "RESPONDING": "Responding…",
            "SPEAKING": "Speaking…",
            "ERROR": "Something went wrong",
        }
        text = states.get(state, states["IDLE"])
        self.subtitle.setText(text)

        if state == "LISTENING":
            self.aura.start_pulse()
        elif state in {"PROCESSING", "RESPONDING"}:
            self.aura.setOpacity(0.58)
        elif state == "ERROR":
            self.aura.setOpacity(0.38)
        else:
            self.aura.stop_pulse()
