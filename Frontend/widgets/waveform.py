from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QLinearGradient
from PySide6.QtWidgets import QWidget


class Waveform(QWidget):
    """Animated audio waveform bars with a violet-to-teal gradient fill."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(22)
        self.setMaximumHeight(22)
        self._bars = [0.18, 0.33, 0.58, 0.44, 0.72, 0.52, 0.4, 0.76, 0.62, 0.3, 0.68, 0.5]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._active = False
        self._phase = 0

    def set_active(self, active: bool):
        self._active = active
        if active:
            self._timer.start(110)
        else:
            self._timer.stop()
            self._phase = 0
            self.update()

    def _animate(self):
        self._phase += 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        bar_width = max(4, width // len(self._bars))
        gap = 3
        total_w = len(self._bars) * (bar_width + gap)

        for idx, amplitude in enumerate(self._bars):
            x = idx * (bar_width + gap) + 6
            if self._active:
                t = (idx + self._phase * 0.8) % 1.0
                relative = 0.35 + 0.65 * (0.5 + 0.5 * ((1 if idx % 2 else -1) * (t - 0.5)))
                level = max(0.1, min(1.0, amplitude * (0.6 + relative * 0.7)))
            else:
                level = amplitude * 0.5

            bar_h = max(4, int(level * height))
            y = (height - bar_h) // 2

            # Per-bar gradient: violet at left → teal at right
            ratio = idx / max(1, len(self._bars) - 1)
            r = int(168 + (45 - 168) * ratio)
            g = int(85 + (212 - 85) * ratio)
            b = int(247 + (191 - 247) * ratio)
            painter.fillRect(x, y, bar_width - 2, bar_h, QColor(r, g, b, 200))

        painter.end()
