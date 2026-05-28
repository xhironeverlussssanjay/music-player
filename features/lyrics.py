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


class LyricsThread(QThread):
    lyrics_found    = pyqtSignal(str)
    lyrics_notfound = pyqtSignal(str)

    def __init__(self, title: str, artist: str = ""):
        super().__init__()
        self.title  = title
        self.artist = artist or "Unknown"

    def run(self):
        try:
            url = f"https://api.lyrics.ovh/v1/{self.artist}/{self.title}"
            r   = requests.get(url, timeout=8)
            if r.status_code == 200:
                data = r.json()
                lyrics = data.get("lyrics", "").strip()
                if lyrics:
                    self.lyrics_found.emit(lyrics)
                    return
            self.lyrics_notfound.emit(f"Lirik tidak ditemukan untuk:\n{self.title}")
        except Exception as e:
            self.lyrics_notfound.emit(f"Gagal mengambil lirik.\nCek koneksi internet.\n\n({e})")


class LyricsWidget(QWidget):
    """Panel lirik yang bisa di-embed di home page."""

    STYLE = """
    QWidget#lyricsRoot {
        background-color: #10101C;
        border-radius: 16px;
        border: 1px solid #1E1E38;
    }
    QLabel#lyricsTitle {
        color: #A78BFA; font-size: 13px; font-weight: 700;
        font-family: 'Segoe UI'; background: transparent;
    }
    QLabel#lyricsStatus {
        color: #6B7280; font-size: 11px;
        font-family: 'Segoe UI'; background: transparent;
    }
    QScrollArea#lyricsScroll { background: transparent; border: none; }
    QWidget#lyricsScrollInner { background: transparent; }
    QLabel#lyricsText {
        color: #CBD5E1; font-size: 13px; line-height: 1.8;
        font-family: 'Segoe UI'; background: transparent;
    }
    QPushButton#btnRefreshLyrics {
        background: transparent; color: #6B7280;
        border: 1px solid #2D2D44; border-radius: 8px;
        font-size: 11px; padding: 4px 10px;
    }
    QPushButton#btnRefreshLyrics:hover {
        color: #A78BFA; border-color: #A78BFA;
        background-color: #1A1528;
    }
    QScrollBar:vertical { background: transparent; width: 3px; }
    QScrollBar::handle:vertical { background: #2D2D44; border-radius: 2px; min-height: 20px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("lyricsRoot")
        self.setStyleSheet(self.STYLE)
        self._build_ui()
        self._thread = None

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(8)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("🎵  Lyrics")
        title.setObjectName("lyricsTitle")
        self.status_lbl = QLabel("Putar lagu untuk melihat lirik")
        self.status_lbl.setObjectName("lyricsStatus")
        self.btn_refresh = QPushButton("↺ Refresh")
        self.btn_refresh.setObjectName("btnRefreshLyrics")
        self.btn_refresh.clicked.connect(self._manual_refresh)
        hdr.addWidget(title)
        hdr.addWidget(self.status_lbl)
        hdr.addStretch()
        hdr.addWidget(self.btn_refresh)
        root.addLayout(hdr)

        # Scroll area
        scroll = QScrollArea()
        scroll.setObjectName("lyricsScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner = QWidget()
        inner.setObjectName("lyricsScrollInner")
        il = QVBoxLayout(inner)
        il.setContentsMargins(0, 4, 0, 4)
        self.lyrics_lbl = QLabel("♪  Menunggu lagu diputar...")
        self.lyrics_lbl.setObjectName("lyricsText")
        self.lyrics_lbl.setWordWrap(True)
        self.lyrics_lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        il.addWidget(self.lyrics_lbl)
        il.addStretch()
        scroll.setWidget(inner)
        root.addWidget(scroll)

        self._current_title  = ""
        self._current_artist = ""

    def load_lyrics(self, title: str, artist: str = ""):
        if title == self._current_title and artist == self._current_artist:
            return
        self._current_title  = title
        self._current_artist = artist
        self.lyrics_lbl.setText("⏳  Mengambil lirik...")
        self.status_lbl.setText(f"{title}")
        self._fetch(title, artist)

    def _manual_refresh(self):
        if self._current_title:
            self._fetch(self._current_title, self._current_artist)

    def _fetch(self, title, artist):
        if self._thread and self._thread.isRunning():
            self._thread.quit()
        self._thread = LyricsThread(title, artist)
        self._thread.lyrics_found.connect(self._on_found)
        self._thread.lyrics_notfound.connect(self._on_notfound)
        self._thread.start()

    def _on_found(self, lyrics: str):
        self.lyrics_lbl.setText(lyrics)
        self.status_lbl.setText("✓  Lirik ditemukan")
        logger.info(f"Lyrics loaded: {self._current_title}")

    def _on_notfound(self, msg: str):
        self.lyrics_lbl.setText(f"💿  {msg}")
        self.status_lbl.setText("Lirik tidak tersedia")

    def clear(self):
        self._current_title  = ""
        self._current_artist = ""
        self.lyrics_lbl.setText("♪  Menunggu lagu diputar...")
        self.status_lbl.setText("Putar lagu untuk melihat lirik")
