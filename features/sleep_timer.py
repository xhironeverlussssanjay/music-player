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


class SleepTimerWidget(QWidget):
    """Widget sleep timer — bisa dipasang sebagai overlay/panel kecil."""

    stop_music = pyqtSignal()

    STYLE = """
    QWidget#sleepRoot {
        background-color: #141420; border-radius: 14px;
        border: 1px solid #1E1E38;
    }
    QLabel#sleepTitle {
        color: #A78BFA; font-size: 12px; font-weight: 700;
        font-family: 'Segoe UI'; background: transparent;
    }
    QLabel#sleepCountdown {
        color: #E2E8F0; font-size: 22px; font-weight: 700;
        font-family: 'Segoe UI'; background: transparent;
    }
    QLabel#sleepSub {
        color: #6B7280; font-size: 10px;
        font-family: 'Segoe UI'; background: transparent;
    }
    QPushButton#btnSleepPreset {
        background-color: #1A1A28; color: #9CA3AF;
        border: 1px solid #2D2D44; border-radius: 8px;
        font-size: 11px; padding: 6px 10px;
    }
    QPushButton#btnSleepPreset:hover {
        background-color: #1A1528; color: #A78BFA;
        border-color: #A78BFA;
    }
    QPushButton#btnSleepCancel {
        background-color: transparent; color: #9CA3AF;
        border: 1px solid #2D2D44; border-radius: 8px;
        font-size: 11px; padding: 6px 14px;
        text-align: center;
    }
    QPushButton#btnSleepCancel:hover {
        color: #E2E8F0;
        border-color: #6B7280;
        background-color: rgba(156,163,175,0.08);
    }
    """

    PRESETS = [("5m", 5), ("15m", 15), ("30m", 30), ("45m", 45), ("60m", 60)]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sleepRoot")
        self.setStyleSheet(self.STYLE)
        self._remaining = 0
        self._timer     = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        hdr = QHBoxLayout()
        title = QLabel("😴  Sleep Timer")
        title.setObjectName("sleepTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        root.addLayout(hdr)

        self.countdown = QLabel("--:--")
        self.countdown.setObjectName("sleepCountdown")
        self.countdown.setAlignment(Qt.AlignCenter)
        root.addWidget(self.countdown)

        self.sub = QLabel("Pilih durasi untuk mulai timer")
        self.sub.setObjectName("sleepSub")
        self.sub.setAlignment(Qt.AlignCenter)
        root.addWidget(self.sub)

        # Preset buttons
        presets_row = QHBoxLayout()
        presets_row.setSpacing(6)
        for label, minutes in self.PRESETS:
            btn = QPushButton(label)
            btn.setObjectName("btnSleepPreset")
            btn.clicked.connect(lambda _, m=minutes: self._start(m))
            presets_row.addWidget(btn)
        root.addLayout(presets_row)

        self.btn_cancel = QPushButton("✕  Cancel Timer")
        self.btn_cancel.setObjectName("btnSleepCancel")
        self.btn_cancel.clicked.connect(self._cancel)
        self.btn_cancel.setVisible(False)
        root.addWidget(self.btn_cancel)

    def _start(self, minutes: int):
        self._remaining = minutes * 60
        self._timer.start()
        self.btn_cancel.setVisible(True)
        self.sub.setText(f"Musik berhenti dalam {minutes} menit")
        self._update_display()
        logger.info(f"Sleep timer set: {minutes} menit")

    def _cancel(self):
        self._timer.stop()
        self._remaining = 0
        self.countdown.setText("--:--")
        self.sub.setText("Pilih durasi untuk mulai timer")
        self.btn_cancel.setVisible(False)
        logger.info("Sleep timer dibatalkan")

    def _tick(self):
        self._remaining -= 1
        if self._remaining <= 0:
            self._timer.stop()
            self.countdown.setText("00:00")
            self.sub.setText("⏹  Musik dihentikan")
            self.btn_cancel.setVisible(False)
            self.stop_music.emit()
            logger.info("Sleep timer: musik dihentikan")
        else:
            self._update_display()

    def _update_display(self):
        m = self._remaining // 60
        s = self._remaining % 60
        self.countdown.setText(f"{m:02d}:{s:02d}")
