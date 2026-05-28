import os
import json
import random
import time
import requests
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QScrollArea, QFrame,
    QInputDialog, QMessageBox, QProgressBar, QSlider,
    QStackedWidget, QGridLayout, QSizePolicy, QSpacerItem,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QPalette, QFont, QPixmap, QPainter, QPainterPath

import logger

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class MoodColorEngine:
    """Ambil dominant color dari QPixmap dan generate palette selaras."""

    @staticmethod
    def extract(pixmap: QPixmap, samples: int = 12) -> QColor:
        """Sample beberapa pixel dari pixmap, return dominant color."""
        if pixmap.isNull():
            return QColor("#A78BFA")
        img   = pixmap.toImage().scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        w, h  = img.width(), img.height()
        colors = []
        step  = max(1, (w * h) // samples)
        for i in range(0, w * h, step):
            x, y = i % w, i // w
            if y < h:
                c = img.pixelColor(x, y)
                if c.saturation() > 60 and c.value() > 40:
                    colors.append(c)
        if not colors:
            return QColor("#A78BFA")
        # average
        r = sum(c.red()   for c in colors) // len(colors)
        g = sum(c.green() for c in colors) // len(colors)
        b = sum(c.blue()  for c in colors) // len(colors)
        base = QColor(r, g, b)
        # boost saturation
        h2, s, v, _ = base.getHsv()
        return QColor.fromHsv(h2, min(255, s + 60), min(255, v + 30))

    @staticmethod
    def make_palette(accent: QColor) -> dict:
        h, s, v, _ = accent.getHsv()
        dark   = QColor.fromHsv(h, min(255, s + 30), max(20, v - 160))
        hover  = QColor.fromHsv(h, max(0, s - 40),   min(255, v + 40))
        glow   = QColor(accent.red(), accent.green(), accent.blue(), 60)
        return {
            "accent":  accent.name(),
            "dark":    dark.name(),
            "hover":   hover.name(),
            "glow":    glow.name(QColor.HexArgb),
        }
