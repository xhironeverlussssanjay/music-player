import os
import json
import random
import re
import time
import requests
from datetime import datetime, timedelta
from urllib.parse import quote

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
    lyrics_found = pyqtSignal(str)
    lyrics_notfound = pyqtSignal(str)

    LRCLIB_SEARCH_URL = "https://lrclib.net/api/search"
    LYRICS_OVH_URL = "https://api.lyrics.ovh/v1"

    HEADERS = {
        # LRCLIB menyarankan aplikasi mengirim User-Agent yang jelas.
        "User-Agent": "SoundWaveLyrics/1.0 (local PyQt music player)",
        "Accept": "application/json",
    }

    def __init__(self, title: str, artist: str = ""):
        super().__init__()
        self.title = title or ""
        self.artist = artist or ""

    # ---------- Normalizer metadata ----------
    def _clean_text(self, value: str) -> str:
        value = os.path.basename(value or "")
        value = re.sub(r"\.(mp3|wav|flac|m4a|aac|ogg)$", "", value, flags=re.I)
        value = value.replace("_", " ").replace("|", "-")
        value = re.sub(r"\s+", " ", value).strip()

        # Buang noise umum dari nama file YouTube/download.
        value = re.sub(
            r"\s*[\[(](official\s*)?(music\s*)?(video|audio|lyrics?|lyric video|visualizer|hd|4k|mv|remaster(ed)?|live|sped up|slowed|nightcore)[\])]",
            "",
            value,
            flags=re.I,
        )
        value = re.sub(r"\s+", " ", value).strip(" -–—")
        return value

    def _split_artist_title(self, title: str, artist: str):
        title = self._clean_text(title)
        artist = self._clean_text(artist)

        if artist.lower() in {"", "unknown", "unknown artist", "none", "null"}:
            # Format umum file download: "Artist - Title"
            match = re.split(r"\s[-–—]\s", title, maxsplit=1)
            if len(match) == 2:
                artist, title = match[0].strip(), match[1].strip()

        # Untuk lookup lirik, featured/remix sering bikin API gagal.
        # Simpan judul utama sebagai kandidat utama.
        title = re.sub(r"\s*(feat\.|ft\.|featuring)\s+.+$", "", title, flags=re.I).strip()
        title = re.sub(r"\s*[\[(](remix|edit|radio edit|extended mix|dj mix|bootleg|cover)[\])]", "", title, flags=re.I).strip()
        title = re.sub(r"\s+", " ", title).strip(" -–—")
        artist = re.sub(r"\s+", " ", artist).strip(" -–—")
        return title, artist

    def _strip_lrc_timestamps(self, synced_lyrics: str) -> str:
        # Ubah LRC synced lyrics menjadi plain text.
        lines = []
        for line in (synced_lyrics or "").splitlines():
            line = re.sub(r"\[\d{2}:\d{2}(?:\.\d{2,3})?\]", "", line).strip()
            if line:
                lines.append(line)
        return "\n".join(lines).strip()

    def _score_result(self, item: dict, title: str, artist: str) -> int:
        track_name = (item.get("trackName") or "").lower()
        artist_name = (item.get("artistName") or "").lower()
        title_l = title.lower()
        artist_l = artist.lower()

        score = 0
        if title_l and title_l == track_name:
            score += 50
        elif title_l and title_l in track_name:
            score += 25
        if artist_l and artist_l == artist_name:
            score += 40
        elif artist_l and artist_l in artist_name:
            score += 20
        if item.get("plainLyrics"):
            score += 10
        if item.get("syncedLyrics"):
            score += 5
        return score

    # ---------- Provider 1: LRCLIB ----------
    def _fetch_from_lrclib(self, title: str, artist: str) -> str:
        queries = []
        if title and artist:
            queries.append({"track_name": title, "artist_name": artist})
            queries.append({"q": f"{artist} {title}"})
        if title:
            queries.append({"track_name": title})
            queries.append({"q": title})

        for params in queries:
            r = requests.get(self.LRCLIB_SEARCH_URL, params=params, headers=self.HEADERS, timeout=10)
            if r.status_code != 200:
                continue

            results = r.json()
            if not isinstance(results, list) or not results:
                continue

            results = sorted(results, key=lambda x: self._score_result(x, title, artist), reverse=True)
            for item in results:
                if item.get("instrumental"):
                    return "♪ Track ini terdeteksi sebagai instrumental."

                lyrics = (item.get("plainLyrics") or "").strip()
                if not lyrics:
                    lyrics = self._strip_lrc_timestamps(item.get("syncedLyrics") or "")

                if lyrics:
                    return lyrics
        return ""

    # ---------- Provider 2: lyrics.ovh fallback ----------
    def _fetch_from_lyrics_ovh(self, title: str, artist: str) -> str:
        if not title or not artist:
            return ""

        url = f"{self.LYRICS_OVH_URL}/{quote(artist)}/{quote(title)}"
        r = requests.get(url, timeout=8, headers={"Accept": "application/json"})
        if r.status_code == 200:
            data = r.json()
            return (data.get("lyrics") or "").strip()
        return ""

    def run(self):
        title, artist = self._split_artist_title(self.title, self.artist)

        if not title:
            self.lyrics_notfound.emit("Judul lagu kosong atau metadata tidak terbaca.")
            return

        try:
            lyrics = self._fetch_from_lrclib(title, artist)
            if lyrics:
                self.lyrics_found.emit(lyrics)
                return

            lyrics = self._fetch_from_lyrics_ovh(title, artist)
            if lyrics:
                self.lyrics_found.emit(lyrics)
                return

            shown = f"{artist} - {title}" if artist else title
            self.lyrics_notfound.emit(
                "Lirik belum ditemukan untuk:\n"
                f"{shown}\n\n"
                "Coba pastikan metadata file berisi Artist dan Title yang benar."
            )
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
        color: #A78BFA;
        font-size: 13px;
        font-weight: 700;
        font-family: 'Segoe UI';
        background: transparent;
    }
    QLabel#lyricsStatus {
        color: #8A8FA8;
        font-size: 11px;
        font-family: 'Segoe UI';
        background: transparent;
    }
    QScrollArea#lyricsScroll {
        background: transparent;
        border: none;
    }
    QWidget#lyricsScrollInner {
        background: transparent;
    }
    QLabel#lyricsText {
        color: #CBD5E1;
        font-size: 13px;
        line-height: 1.8;
        font-family: 'Segoe UI';
        background: transparent;
    }

    /* Modern glass refresh button */
QPushButton#btnRefreshLyrics {
    color: #A1A1AA;
    background: transparent;
    border: 1px solid rgba(148, 163, 184, 0.28);
    border-radius: 10px;
    padding: 6px 12px;
    min-height: 18px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Segoe UI';
    letter-spacing: 0.15px;
}
QPushButton#btnRefreshLyrics:hover {
    color: #E9D5FF;
    background: rgba(139, 92, 246, 0.06);
    border: 1px solid rgba(167, 139, 250, 0.42);
}
QPushButton#btnRefreshLyrics:pressed {
    color: #C4B5FD;
    background: rgba(139, 92, 246, 0.10);
    border: 1px solid rgba(167, 139, 250, 0.58);
    padding-top: 7px;
    padding-bottom: 5px;
}
QPushButton#btnRefreshLyrics:disabled {
    color: #52525B;
    background: transparent;
    border: 1px solid rgba(82, 82, 91, 0.24);
}

    QScrollBar:vertical {
        background: transparent;
        width: 3px;
    }
    QScrollBar::handle:vertical {
        background: #3B315B;
        border-radius: 2px;
        min-height: 20px;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0;
    }
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
        hdr.setSpacing(10)

        title = QLabel("🎵  Lyrics")
        title.setObjectName("lyricsTitle")

        self.status_lbl = QLabel("Putar lagu untuk melihat lirik")
        self.status_lbl.setObjectName("lyricsStatus")

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setObjectName("btnRefreshLyrics")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
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

        self._current_title = ""
        self._current_artist = ""

    def load_lyrics(self, title: str, artist: str = ""):
        if title == self._current_title and artist == self._current_artist:
            return
        self._current_title = title
        self._current_artist = artist
        self.lyrics_lbl.setText("⏳  Mengambil lirik...")
        self.status_lbl.setText(f"{title}")
        self._fetch(title, artist)

    def _manual_refresh(self):
        if self._current_title:
            self.lyrics_lbl.setText("⏳  Refresh lirik...")
            self.status_lbl.setText("Mencari ulang...")
            self._fetch(self._current_title, self._current_artist)

    def _fetch(self, title, artist):
        if self._thread and self._thread.isRunning():
            self._thread.quit()
            self._thread.wait(200)

        self.btn_refresh.setEnabled(False)
        self._thread = LyricsThread(title, artist)
        self._thread.lyrics_found.connect(self._on_found)
        self._thread.lyrics_notfound.connect(self._on_notfound)
        self._thread.finished.connect(lambda: self.btn_refresh.setEnabled(True))
        self._thread.start()

    def _on_found(self, lyrics: str):
        self.lyrics_lbl.setText(lyrics)
        self.status_lbl.setText("✓  Lirik ditemukan")
        logger.info(f"Lyrics loaded: {self._current_title}")

    def _on_notfound(self, msg: str):
        self.lyrics_lbl.setText(f"💿  {msg}")
        self.status_lbl.setText("Lirik tidak tersedia")

    def clear(self):
        self._current_title = ""
        self._current_artist = ""
        self.lyrics_lbl.setText("♪  Menunggu lagu diputar...")
        self.status_lbl.setText("Putar lagu untuk melihat lirik")
