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

HISTORY_FILE = "history.json"
HISTORY_LIMIT = 50

class RecentlyPlayedManager:
    def __init__(self):
        self.history: list[dict] = []
        self._load()

    def _path(self):
        base = PROJECT_ROOT
        return os.path.join(base, HISTORY_FILE)

    def _load(self):
        try:
            with open(self._path(), "r", encoding="utf-8") as f:
                self.history = json.load(f)
        except Exception:
            self.history = []

    def _save(self):
        try:
            with open(self._path(), "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"History save error: {e}")

    def add(self, filepath: str):
        name = os.path.splitext(os.path.basename(filepath))[0]
        ts   = datetime.now().strftime("%d %b %Y · %H:%M")
        # Hapus duplikat
        self.history = [h for h in self.history if h.get("path") != filepath]
        self.history.insert(0, {"path": filepath, "name": name, "time": ts})
        self.history = self.history[:HISTORY_LIMIT]
        self._save()

    def get_all(self) -> list:
        return self.history

    def clear(self):
        self.history = []
        self._save()


class RecentlyPlayedWidget(QWidget):
    play_song = pyqtSignal(str)   # emit filepath

    STYLE = """
    QWidget#recentRoot { background: transparent; }
    QLabel#recentTitle {
        color: #FFFFFF; font-size: 22px; font-weight: bold; font-family: 'Segoe UI';
    }
    QLabel#recentSub { color: #6B7280; font-size: 12px; font-family: 'Segoe UI'; }
    QListWidget#recentList {
        background: transparent; border: none;
        color: #CBD5E1; font-size: 13px; outline: none;
    }
    QListWidget#recentList::item {
        background-color: #1A1A2E; color: #CBD5E1;
        padding: 10px 14px; border-radius: 10px;
        margin: 3px 4px; border: 1px solid #2D2D44;
    }
    QListWidget#recentList::item:hover {
        background-color: #1F1A3A; color: #E2E8F0; border: 1px solid #6D4BC2;
    }
    QListWidget#recentList::item:selected {
        background-color: #2A1A4A; color: #C4B5FD;
        border: 1px solid #A78BFA; font-weight: 600;
    }
    QPushButton#btnRecentClear {
        background: transparent; color: #9CA3AF;
        border: 1px solid #2D2D44; border-radius: 8px;
        font-size: 11px; padding: 6px 14px;
        text-align: center;
    }
    QPushButton#btnRecentClear:hover {
        color: #E2E8F0;
        border-color: #6B7280;
        background-color: rgba(156,163,175,0.08);
    }
    QScrollBar:vertical { background: transparent; width: 3px; }
    QScrollBar::handle:vertical { background: #2D2D44; border-radius: 2px; min-height: 20px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    """

    def __init__(self, manager: RecentlyPlayedManager, parent=None):
        super().__init__(parent)
        self.setObjectName("recentRoot")
        self.setStyleSheet(self.STYLE)
        self.mgr = manager
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 20)
        root.setSpacing(10)

        hdr = QHBoxLayout()
        title = QLabel("🕐  Recently Played")
        title.setObjectName("recentTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        self.btn_clear = QPushButton("🗑  Clear History")
        self.btn_clear.setObjectName("btnRecentClear")
        self.btn_clear.clicked.connect(self._clear)
        hdr.addWidget(self.btn_clear)
        root.addLayout(hdr)

        sub = QLabel("Double-click lagu untuk langsung memutar")
        sub.setObjectName("recentSub")
        root.addWidget(sub)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("recentList")
        self.list_widget.itemDoubleClicked.connect(self._on_double)
        root.addWidget(self.list_widget)

        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        for entry in self.mgr.get_all():
            item = QListWidgetItem(f"♪  {entry['name']}  ·  {entry['time']}")
            item.setData(Qt.UserRole, entry["path"])
            self.list_widget.addItem(item)
        if self.list_widget.count() == 0:
            self.list_widget.addItem("Belum ada riwayat pemutaran")

    def _on_double(self, item):
        fp = item.data(Qt.UserRole)
        if fp and os.path.exists(fp):
            self.play_song.emit(fp)

    def _clear(self):
        self.mgr.clear()
        self.refresh()
