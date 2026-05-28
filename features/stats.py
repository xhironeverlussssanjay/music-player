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

STATS_FILE = "stats.json"

class StatsManager:
    def __init__(self):
        self.data = {
            "total_seconds": 0,
            "play_count":    {},   # filepath → count
            "session_count": 0,
            "first_play":    None,
        }
        self._load()

    def _path(self):
        base = PROJECT_ROOT
        return os.path.join(base, STATS_FILE)

    def _load(self):
        try:
            with open(self._path(), "r", encoding="utf-8") as f:
                loaded = json.load(f)
                self.data.update(loaded)
        except Exception:
            pass

    def save(self):
        try:
            with open(self._path(), "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Stats save error: {e}")

    def add_playtime(self, seconds: float):
        self.data["total_seconds"] += seconds
        self.save()

    def record_play(self, filepath: str):
        if not self.data["first_play"]:
            self.data["first_play"] = datetime.now().strftime("%d %b %Y")
        self.data["play_count"][filepath] = self.data["play_count"].get(filepath, 0) + 1
        self.data["session_count"] += 1
        self.save()

    def top_songs(self, n: int = 5) -> list:
        counts = self.data["play_count"]
        ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        result = []
        for fp, count in ranked[:n]:
            if os.path.exists(fp):
                name = os.path.splitext(os.path.basename(fp))[0]
                result.append((name, count))
        return result

    def total_hours(self) -> float:
        return self.data["total_seconds"] / 3600

    def total_songs_played(self) -> int:
        return self.data["session_count"]

    def unique_songs(self) -> int:
        return len(self.data["play_count"])

    def first_play(self) -> str:
        return self.data.get("first_play") or "Belum ada"


class StatsWidget(QWidget):

    STYLE = """
    QWidget#statsRoot { background: transparent; }
    QLabel#statsTitle {
        color: #FFFFFF; font-size: 22px; font-weight: bold; font-family: 'Segoe UI';
    }
    QLabel#statsCardVal {
        color: #FFFFFF; font-size: 28px; font-weight: 700; font-family: 'Segoe UI';
    }
    QLabel#statsCardLbl {
        color: #6B7280; font-size: 11px; font-weight: 600;
        letter-spacing: 1px; font-family: 'Segoe UI';
    }
    QLabel#statsCardIcon { font-size: 28px; background: transparent; }
    QWidget#statsCard {
        background-color: #141420; border-radius: 16px; border: 1px solid #2D2D44;
    }
    QLabel#statsTopTitle {
        color: #A78BFA; font-size: 14px; font-weight: 700; font-family: 'Segoe UI';
    }
    QWidget#statsTopCard {
        background-color: #141420; border-radius: 16px; border: 1px solid #2D2D44;
    }
    QLabel#statsTopItem {
        color: #CBD5E1; font-size: 13px; font-family: 'Segoe UI'; background: transparent;
    }
    QLabel#statsTopCount {
        color: #A78BFA; font-size: 12px; font-family: 'Segoe UI'; background: transparent;
    }
    QPushButton#btnStatsRefresh {
        background: transparent; color: #6B7280;
        border: 1px solid #2D2D44; border-radius: 8px;
        font-size: 11px; padding: 6px 14px;
    }
    QPushButton#btnStatsRefresh:hover {
        color: #A78BFA; border-color: #A78BFA; background-color: #1A1528;
    }
    """

    def __init__(self, manager: StatsManager, parent=None):
        super().__init__(parent)
        self.setObjectName("statsRoot")
        self.setStyleSheet(self.STYLE)
        self.mgr = manager
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 20)
        root.setSpacing(16)

        hdr = QHBoxLayout()
        title = QLabel("📊  Stats")
        title.setObjectName("statsTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        btn_refresh = QPushButton("↺ Refresh")
        btn_refresh.setObjectName("btnStatsRefresh")
        btn_refresh.clicked.connect(self.refresh)
        hdr.addWidget(btn_refresh)
        root.addLayout(hdr)

        # Stat cards row
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(12)
        self._cards = {}
        for key, icon, label in [
            ("hours",   "⏱", "JAM DIDENGARKAN"),
            ("plays",   "▶", "TOTAL DIPUTAR"),
            ("unique",  "🎵", "LAGU UNIK"),
            ("since",   "📅", "PERTAMA MAIN"),
        ]:
            card = QWidget()
            card.setObjectName("statsCard")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 16, 16, 16)
            cl.setSpacing(6)
            ic = QLabel(icon); ic.setObjectName("statsCardIcon"); cl.addWidget(ic)
            val = QLabel("—"); val.setObjectName("statsCardVal"); cl.addWidget(val)
            lbl = QLabel(label); lbl.setObjectName("statsCardLbl"); cl.addWidget(lbl)
            self._cards[key] = val
            self.cards_layout.addWidget(card)
        root.addLayout(self.cards_layout)

        # Top songs
        top_card = QWidget()
        top_card.setObjectName("statsTopCard")
        tl = QVBoxLayout(top_card)
        tl.setContentsMargins(20, 16, 20, 16)
        tl.setSpacing(10)
        top_title = QLabel("🏆  Top 5 Lagu Paling Sering Diputar")
        top_title.setObjectName("statsTopTitle")
        tl.addWidget(top_title)
        self.top_items_layout = QVBoxLayout()
        self.top_items_layout.setSpacing(6)
        tl.addLayout(self.top_items_layout)
        root.addWidget(top_card)
        root.addStretch()

        self.refresh()

    def refresh(self):
        hours = self.mgr.total_hours()
        self._cards["hours"].setText(f"{hours:.1f}")
        self._cards["plays"].setText(str(self.mgr.total_songs_played()))
        self._cards["unique"].setText(str(self.mgr.unique_songs()))
        self._cards["since"].setText(self.mgr.first_play())

        # Clear top songs
        while self.top_items_layout.count():
            item = self.top_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        top = self.mgr.top_songs(5)
        if not top:
            lbl = QLabel("Belum ada data — putar beberapa lagu dulu!")
            lbl.setObjectName("statsTopItem")
            self.top_items_layout.addWidget(lbl)
        else:
            for i, (name, count) in enumerate(top):
                row = QHBoxLayout()
                rank = QLabel(f"#{i+1}")
                rank.setStyleSheet("color:#A78BFA;font-weight:700;min-width:24px;font-family:'Segoe UI';")
                song_lbl = QLabel(name)
                song_lbl.setObjectName("statsTopItem")
                count_lbl = QLabel(f"{count}×")
                count_lbl.setObjectName("statsTopCount")
                row.addWidget(rank)
                row.addWidget(song_lbl, 1)
                row.addWidget(count_lbl)
                w = QWidget()
                w.setStyleSheet("background:transparent;")
                w.setLayout(row)
                self.top_items_layout.addWidget(w)
