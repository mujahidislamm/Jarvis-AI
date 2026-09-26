from PySide6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QPainter, QRadialGradient, QColor, QBrush, QPen
from PySide6.QtWidgets import QWidget


class GlowAura(QWidget):
    """Dual-color radial glow (violet → teal) with pulse animation
    and a slow focal-point drift for a living, organic feel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._opacity = 0.45
        self._focal_offset = 0.0  # 0 → 1 oscillation for focal drift

        # ── Primary opacity pulse ──
        self._pulse_anim = QPropertyAnimation(self, b"opacity", self)
        self._pulse_anim.setDuration(2200)
        self._pulse_anim.setLoopCount(-1)
        self._pulse_anim.setStartValue(0.22)
        self._pulse_anim.setEndValue(0.62)
        self._pulse_anim.setEasingCurve(QEasingCurve.InOutSine)
        self._pulse_anim.start()

        # ── Slow focal drift timer ──
        self._drift_timer = QTimer(self)
        self._drift_timer.timeout.connect(self._advance_drift)
        self._drift_timer.start(50)
        self._drift_step = 0

    # ── Property helpers for QPropertyAnimation ──

    def opacity(self):
        return self._opacity

    def setOpacity(self, value):
        self._opacity = value
        self.update()

    def set_opacity_value(self, value: float):
        self._opacity = max(0.0, min(1.0, value))
        self.update()

    # ── Drift animation ──

    def _advance_drift(self):
        self._drift_step = (self._drift_step + 1) % 360
        import math
        self._focal_offset = 0.5 + 0.5 * math.sin(math.radians(self._drift_step))
        self.update()

    # ── Paint dual-radial glow ──

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        cx, cy = rect.center().x(), rect.center().y()
        radius = max(rect.width(), rect.height()) * 0.92

        # Focal point drifts horizontally
        fx = cx + (self._focal_offset - 0.5) * rect.width() * 0.25
        fy = cy

        # ── Violet inner glow ──
        g1 = QRadialGradient(cx, cy, radius * 0.75, fx, fy)
        g1.setColorAt(0.0, QColor(168, 85, 247, int(220 * self._opacity)))
        g1.setColorAt(0.45, QColor(139, 92, 246, int(140 * self._opacity)))
        g1.setColorAt(1.0, QColor(88, 28, 135, 0))

        painter.setBrush(QBrush(g1))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect)

        # ── Teal outer glow ──
        fx2 = cx - (self._focal_offset - 0.5) * rect.width() * 0.20
        g2 = QRadialGradient(cx, cy, radius, fx2, fy)
        g2.setColorAt(0.0, QColor(45, 212, 191, int(120 * self._opacity)))
        g2.setColorAt(0.50, QColor(20, 184, 166, int(80 * self._opacity)))
        g2.setColorAt(1.0, QColor(13, 148, 136, 0))

        painter.setBrush(QBrush(g2))
        painter.drawEllipse(rect)

        painter.end()

    # ── Pulse control ──

    def start_pulse(self):
        self._pulse_anim.stop()
        self._pulse_anim.setStartValue(0.30)
        self._pulse_anim.setEndValue(0.78)
        self._pulse_anim.setDuration(1200)
        self._pulse_anim.start()

    def stop_pulse(self):
        self._pulse_anim.stop()
        self.setOpacity(0.32)
