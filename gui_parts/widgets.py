import math

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import QWidget


class WaveWidget(QWidget):
    """Animated wave widget for the background."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)
        # Transparent for mouse events so touches pass through to content below
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def update_animation(self):
        self.phase += 0.05
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width = self.width()
        height = self.height()

        # Draw two background waves with different phases and opacities
        self._draw_wave(
            painter, width, height, self.phase, QColor(20, 184, 166, 60), 1.0, 30
        )
        self._draw_wave(
            painter,
            width,
            height,
            self.phase + math.pi * 0.5,
            QColor(20, 184, 166, 110),
            0.7,
            20,
        )

    def _draw_wave(self, painter, w, h, phase, color, frequency, amplitude):
        path = QPainterPath()
        path.moveTo(0, h)
        mid_y = h / 2
        for x in range(0, w + 1, 5):
            y = mid_y + math.sin(x * 0.008 * frequency + phase) * amplitude
            path.lineTo(float(x), y)
        path.lineTo(w, h)
        path.closeSubpath()
        painter.fillPath(path, color)
