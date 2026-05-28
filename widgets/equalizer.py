import random

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor, QPainter

class EqualizerWidget(QWidget):
    """Widget animasi bar equalizer sederhana, aktif saat musik diputar."""

    BAR_COUNT  = 12
    BAR_WIDTH  = 4
    BAR_GAP    = 3
    BAR_MAX_H  = 28
    BAR_MIN_H  = 3
    COLOR_ON   = QColor("#1DB954")
    COLOR_DIM  = QColor("#2D2D44")

    def __init__(self, parent=None):
        super().__init__(parent)
        self._heights   = [self.BAR_MIN_H] * self.BAR_COUNT
        self._targets   = [self.BAR_MIN_H] * self.BAR_COUNT
        self._active    = False
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(80)
        self._anim_timer.timeout.connect(self._tick)
        self._anim_timer.start()
        total_w = self.BAR_COUNT * (self.BAR_WIDTH + self.BAR_GAP) - self.BAR_GAP
        self.setFixedSize(total_w, self.BAR_MAX_H + 4)

    def set_active(self, state: bool):
        self._active = state

    def _tick(self):
        if self._active:
            self._targets = [
                random.randint(self.BAR_MIN_H, self.BAR_MAX_H)
                for _ in range(self.BAR_COUNT)
            ]
        else:
            self._targets = [self.BAR_MIN_H] * self.BAR_COUNT
        # smooth interpolation
        for i in range(self.BAR_COUNT):
            diff = self._targets[i] - self._heights[i]
            self._heights[i] += int(diff * 0.4) or (1 if diff > 0 else -1 if diff < 0 else 0)
            self._heights[i] = max(self.BAR_MIN_H, min(self.BAR_MAX_H, self._heights[i]))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        for i, bar_h in enumerate(self._heights):
            x = i * (self.BAR_WIDTH + self.BAR_GAP)
            y = h - bar_h
            color = self.COLOR_ON if self._active else self.COLOR_DIM
            p.setBrush(color)
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(x, y, self.BAR_WIDTH, bar_h, 2, 2)
        p.end()
