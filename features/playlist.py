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

PLAYLISTS_FILE = "playlists.json"

class PlaylistManager:
    """Load/save playlist dari/ke JSON file."""

    def __init__(self):
        self.playlists: dict[str, list[str]] = {}
        self._load()

    def _path(self):
        base = PROJECT_ROOT
        return os.path.join(base, PLAYLISTS_FILE)

    def _load(self):
        try:
            with open(self._path(), "r", encoding="utf-8") as f:
                self.playlists = json.load(f)
        except Exception:
            self.playlists = {}

    def save(self):
        try:
            with open(self._path(), "w", encoding="utf-8") as f:
                json.dump(self.playlists, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Playlist save error: {e}")

    def create(self, name: str) -> bool:
        if name in self.playlists:
            return False
        self.playlists[name] = []
        self.save()
        return True

    def delete(self, name: str):
        self.playlists.pop(name, None)
        self.save()

    def rename(self, old: str, new: str) -> bool:
        if new in self.playlists or old not in self.playlists:
            return False
        self.playlists[new] = self.playlists.pop(old)
        self.save()
        return True

    def add_song(self, playlist: str, filepath: str):
        if playlist in self.playlists and filepath not in self.playlists[playlist]:
            self.playlists[playlist].append(filepath)
            self.save()

    def remove_song(self, playlist: str, filepath: str):
        if playlist in self.playlists:
            try:
                self.playlists[playlist].remove(filepath)
                self.save()
            except ValueError:
                pass

    def get_songs(self, playlist: str) -> list:
        return self.playlists.get(playlist, [])

    def names(self) -> list:
        return list(self.playlists.keys())


class PlaylistWidget(QWidget):
    """UI Playlist Manager — bisa diembed sebagai page."""

    load_playlist = pyqtSignal(list)   # emit list of filepaths

    STYLE = """
    QWidget#playlistRoot { background: transparent; }
    QLabel#playlistTitle {
        color: #FFFFFF; font-size: 22px; font-weight: bold;
        font-family: 'Segoe UI';
    }
    QLabel#playlistSub {
        color: #6B7280; font-size: 12px; font-family: 'Segoe UI';
    }
    QListWidget#playlistList, QListWidget#songInPlaylist {
        background-color: transparent; border: none;
        color: #CBD5E1; font-size: 13px; outline: none;
    }
    QListWidget#playlistList::item, QListWidget#songInPlaylist::item {
        background-color: #1A1A2E; color: #CBD5E1;
        padding: 10px 14px; border-radius: 10px;
        margin: 3px 4px; border: 1px solid #2D2D44;
    }
    QListWidget#playlistList::item:hover, QListWidget#songInPlaylist::item:hover {
        background-color: #1F1A3A; color: #E2E8F0;
        border: 1px solid #6D4BC2;
    }
    QListWidget#playlistList::item:selected, QListWidget#songInPlaylist::item:selected {
        background-color: #2A1A4A; color: #C4B5FD;
        border: 1px solid #A78BFA; font-weight: 600;
    }
    QPushButton#btnPlCreate, QPushButton#btnPlLoad,
    QPushButton#btnPlDelete, QPushButton#btnPlRemoveSong,
    QPushButton#btnPlRename {
        min-height: 34px;
        max-height: 34px;
        min-width: 112px;
        max-width: 112px;
        font-size: 12px;
        font-weight: 700;
        font-family: 'Segoe UI';
        border-radius: 12px;
        padding: 0px;
        text-align: center;
        background-color: rgba(255, 255, 255, 9);
        color: #D9DDE8;
        border: 1px solid rgba(255, 255, 255, 24);
    }
    QPushButton#btnPlCreate:hover, QPushButton#btnPlLoad:hover,
    QPushButton#btnPlRename:hover {
        background-color: rgba(167, 139, 250, 24);
        color: #FFFFFF;
        border: 1px solid rgba(196, 181, 253, 95);
    }
    QPushButton#btnPlDelete:hover, QPushButton#btnPlRemoveSong:hover {
        color: #FCA5A5;
        background-color: rgba(248, 113, 113, 14);
        border: 1px solid rgba(248, 113, 113, 82);
    }
    QPushButton#btnPlCreate:pressed, QPushButton#btnPlLoad:pressed,
    QPushButton#btnPlRename:pressed, QPushButton#btnPlDelete:pressed,
    QPushButton#btnPlRemoveSong:pressed {
        background-color: rgba(167, 139, 250, 34);
        border: 1px solid rgba(196, 181, 253, 115);
        color: #FFFFFF;
    }
    QPushButton#btnPlCreate:focus, QPushButton#btnPlLoad:focus,
    QPushButton#btnPlDelete:focus, QPushButton#btnPlRemoveSong:focus,
    QPushButton#btnPlRename:focus {
        outline: none;
    }
    QScrollBar:vertical { background: transparent; width: 3px; }
    QScrollBar::handle:vertical { background: #2D2D44; border-radius: 2px; min-height: 20px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    """

    def __init__(self, manager: PlaylistManager, parent=None):
        super().__init__(parent)
        self.setObjectName("playlistRoot")
        self.setStyleSheet(self.STYLE)
        self.mgr = manager
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 20)
        root.setSpacing(14)

        title = QLabel("🎼  Playlist Manager")
        title.setObjectName("playlistTitle")
        root.addWidget(title)

        sub = QLabel("Buat dan kelola playlist kamu")
        sub.setObjectName("playlistSub")
        root.addWidget(sub)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(14)

        # LEFT — daftar playlist
        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(8)

        lbl_pl = QLabel("Playlist")
        lbl_pl.setStyleSheet("color:#9CA3AF;font-size:11px;font-weight:600;letter-spacing:1px;")
        left.addWidget(lbl_pl)

        self.playlist_list = QListWidget()
        self.playlist_list.setObjectName("playlistList")
        self.playlist_list.currentRowChanged.connect(self._on_pl_select)
        left.addWidget(self.playlist_list)

        # RIGHT — lagu dalam playlist
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(8)

        lbl_songs = QLabel("Lagu dalam Playlist")
        lbl_songs.setStyleSheet("color:#9CA3AF;font-size:11px;font-weight:600;letter-spacing:1px;")
        right.addWidget(lbl_songs)

        self.song_list = QListWidget()
        self.song_list.setObjectName("songInPlaylist")
        right.addWidget(self.song_list)

        content.addLayout(left, 1)
        content.addLayout(right, 2)
        root.addLayout(content, 1)

        # Unified action bar — semua tombol dibuat satu baris agar jaraknya sama dan dempet.
        action_btn_w = 112
        action_btn_h = 34
        action_btn_gap = 4

        action_bar = QHBoxLayout()
        action_bar.setContentsMargins(0, 0, 0, 0)
        action_bar.setSpacing(action_btn_gap)
        action_bar.addStretch(1)

        self.btn_create = QPushButton("Add")
        self.btn_create.setObjectName("btnPlCreate")
        self.btn_create.clicked.connect(self._create_playlist)

        self.btn_rename = QPushButton("Rename")
        self.btn_rename.setObjectName("btnPlRename")
        self.btn_rename.clicked.connect(self._rename_playlist)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setObjectName("btnPlDelete")
        self.btn_delete.clicked.connect(self._delete_playlist)

        self.btn_load = QPushButton("Load Play")
        self.btn_load.setObjectName("btnPlLoad")
        self.btn_load.clicked.connect(self._load_playlist)

        self.btn_remove_song = QPushButton("Delete Song")
        self.btn_remove_song.setObjectName("btnPlRemoveSong")
        self.btn_remove_song.clicked.connect(self._remove_song)

        for btn in (
            self.btn_create,
            self.btn_rename,
            self.btn_delete,
            self.btn_load,
            self.btn_remove_song,
        ):
            btn.setFixedSize(action_btn_w, action_btn_h)
            btn.setCursor(Qt.PointingHandCursor)
            action_bar.addWidget(btn)

        action_bar.addStretch(1)
        root.addLayout(action_bar, 0)

    def _refresh_list(self):
        self.playlist_list.clear()
        for name in self.mgr.names():
            count = len(self.mgr.get_songs(name))
            item  = QListWidgetItem(f"🎵  {name}  ({count} lagu)")
            item.setData(Qt.UserRole, name)
            self.playlist_list.addItem(item)

    def _on_pl_select(self, row):
        self.song_list.clear()
        if row < 0:
            return
        name  = self.playlist_list.item(row).data(Qt.UserRole)
        songs = self.mgr.get_songs(name)
        for fp in songs:
            sname = os.path.splitext(os.path.basename(fp))[0]
            item  = QListWidgetItem(f"♪  {sname}")
            item.setData(Qt.UserRole, fp)
            self.song_list.addItem(item)

    def _create_playlist(self):
        name, ok = QInputDialog.getText(self, "New Playlist", "Nama playlist:")
        if ok and name.strip():
            if self.mgr.create(name.strip()):
                self._refresh_list()
            else:
                QMessageBox.warning(self, "Error", "Nama playlist sudah ada!")

    def _rename_playlist(self):
        item = self.playlist_list.currentItem()
        if not item:
            return
        old  = item.data(Qt.UserRole)
        new, ok = QInputDialog.getText(self, "Rename", "Nama baru:", text=old)
        if ok and new.strip():
            if not self.mgr.rename(old, new.strip()):
                QMessageBox.warning(self, "Error", "Nama sudah dipakai!")
            self._refresh_list()

    def _delete_playlist(self):
        item = self.playlist_list.currentItem()
        if not item:
            return
        name = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "Hapus Playlist",
                                     f"Hapus playlist '{name}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.mgr.delete(name)
            self._refresh_list()
            self.song_list.clear()

    def _load_playlist(self):
        item = self.playlist_list.currentItem()
        if not item:
            return
        name  = item.data(Qt.UserRole)
        songs = [fp for fp in self.mgr.get_songs(name) if os.path.exists(fp)]
        if songs:
            self.load_playlist.emit(songs)
        else:
            QMessageBox.information(self, "Playlist Kosong",
                                    "Playlist ini kosong atau file tidak ditemukan.")

    def _remove_song(self):
        pl_item   = self.playlist_list.currentItem()
        song_item = self.song_list.currentItem()
        if not pl_item or not song_item:
            return
        name = pl_item.data(Qt.UserRole)
        fp   = song_item.data(Qt.UserRole)
        self.mgr.remove_song(name, fp)
        self._on_pl_select(self.playlist_list.currentRow())
        self._refresh_list()

    def add_song_to_current(self, filepath: str):
        """Dipanggil dari main.py untuk add lagu aktif ke playlist yang dipilih."""
        item = self.playlist_list.currentItem()
        if not item:
            QMessageBox.information(self, "Pilih Playlist",
                                    "Pilih playlist dulu di panel kiri!")
            return
        name = item.data(Qt.UserRole)
        self.mgr.add_song(name, filepath)
        self._on_pl_select(self.playlist_list.currentRow())
        self._refresh_list()
