import os
import random
import time

import pygame
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem, QWidget, QHBoxLayout, QGraphicsOpacityEffect
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QRect, QEasingCurve, QSize
from PyQt5.QtGui import QPixmap, QColor, QKeySequence, QIcon, QPainter, QPainterPath
from PyQt5.uic import loadUi

import constants as C
import logger
from ai_chatbot import AIChatWidget
from ai_chatbot_v2 import AIChatWidgetV2
from app.helpers import load_stylesheet, make_rounded_pixmap, fmt_time, song_name, _svg_icon, PROJECT_ROOT, resource_path
from widgets.equalizer import EqualizerWidget
from features import (
    LyricsWidget, MoodColorEngine,
    SleepTimerWidget, PlaylistManager, PlaylistWidget,
    RecentlyPlayedManager, RecentlyPlayedWidget,
    MusicQuizWidget, StatsManager, StatsWidget,
)

pygame.mixer.init()

class MusicPlayer(QMainWindow):

    def __init__(self):
        super().__init__()
        base    = PROJECT_ROOT
        ui_path = resource_path(C.UI_FILE)
        loadUi(ui_path, self)

        # Enable drag & drop untuk add songs
        self.setAcceptDrops(True)

        # Terapkan CSS eksternal
        self.setStyleSheet(load_stylesheet(C.CSS_FILE))

        # Pastikan tombol Play tetap bulat seperti desain awal.
        # Di beberapa layout Qt, min-width/min-height dari CSS bisa melebar jika tidak dikunci.
        self.btnPlay.setFixedSize(56, 56)
        self.btnPlay.setText("▶")

        # ── State ──────────────────────────────────────────────────────────────
        self.songs         = []
        self.favorites     = set()
        self.current_index = -1
        self.shuffle       = False
        self.repeat        = False
        self.liked         = False
        self.is_playing    = False
        self._song_length  = 0
        self._play_start   = 0.0
        self._elapsed_acc  = 0.0

        # ── Feature Managers ───────────────────────────────────────────────────
        self.playlist_mgr = PlaylistManager()
        self.recent_mgr   = RecentlyPlayedManager()
        self.stats_mgr    = StatsManager()
        self._stats_timer = QTimer()
        self._stats_timer.setInterval(5000)
        self._stats_timer.timeout.connect(self._tick_stats)

        # ── Equalizer widget (sisipkan ke nowPlayingCard layout) ───────────────
        self.equalizer = EqualizerWidget(self)
        # Tambahkan ke layout nowPlayingCard setelah albumName
        self.nowPlayingLayout.insertWidget(4, self.equalizer)

        # ── Lyrics widget (sisipkan ke home page, panel kanan bawah queue) ────
        self.lyrics_widget = LyricsWidget()
        # Tambahkan di bawah queueArea layout
        self.queueLayout.addWidget(self.lyrics_widget)

        # ── Timers ─────────────────────────────────────────────────────────────
        self.timer = QTimer()
        self.timer.setInterval(C.TIMER_INTERVAL)
        self.timer.timeout.connect(self._update_progress)

        self.end_check = QTimer()
        self.end_check.setInterval(C.END_CHECK_MS)
        self.end_check.timeout.connect(self._check_song_end)

        # ── Keyboard shortcuts (Qt) ────────────────────────────────────────────
        self.setFocusPolicy(Qt.StrongFocus)

        # ── Setup ──────────────────────────────────────────────────────────────
        self._connect_signals()
        self._setup_nav_icons()
        self._setup_default_album_art()
        self._setup_like_icon()  # Setup icon love default
        self._setup_about_page()
        self._setup_ai_chat_page()
        self._setup_ai_chat_v2_page()
        self._setup_playlist_page()
        self._setup_recent_page()
        self._setup_quiz_page()
        self._setup_stats_page()
        self._go_page(C.PAGE_HOME)
        self.volumeSlider.setValue(C.DEFAULT_VOLUME)
        self.statusBar.showMessage(
            "Selamat datang di SoundWave  —  Tambahkan lagu dengan [＋ Add Song]"
        )

        # ── Welcome Animation ──────────────────────────────────────────────────
        self._fade_in_animation()

        logger.info(f"CSS dimuat dari: {C.CSS_FILE}")
        logger.info(f"UI dimuat dari : {C.UI_FILE}")

    # =========================================================================
    # KEYBOARD SHORTCUTS
    # =========================================================================
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space:
            logger.key_shortcut("Space", "Play / Pause")
            self.toggle_play()
        elif key == Qt.Key_Right:
            logger.key_shortcut("→", "Next Song")
            self.next_song()
        elif key == Qt.Key_Left:
            logger.key_shortcut("←", "Prev Song")
            self.prev_song()
        elif key == Qt.Key_S:
            logger.key_shortcut("S", "Toggle Shuffle")
            self.toggle_shuffle()
        elif key == Qt.Key_R:
            logger.key_shortcut("R", "Toggle Repeat")
            self.toggle_repeat()
        elif key == Qt.Key_L:
            logger.key_shortcut("L", "Toggle Like")
            self.toggle_like()
        else:
            super().keyPressEvent(event)

    # =========================================================================
    # NAV ICONS — load SVG files with color tinting
    # =========================================================================
    def _setup_nav_icons(self):
        """Initial icon setup — grey (inactive) for all buttons."""
        base = PROJECT_ROOT
        configs = [
            ("btnHome",      "home.svg"),
            ("btnSearch",    "search.svg"),
            ("btnLibrary",   "library.svg"),
            ("btnFavorites", "heart.svg"),
            ("btnAIChat",    "bot.svg"),
            ("btnPlaylist",  "playlist.svg"),
            ("btnRecent",    "clock.svg"),
            ("btnQuiz",      "target.svg"),
            ("btnStats",     "chart.svg"),
            ("btnAbout",     "info.svg"),
            ("btnAIChatV2",  "zap.svg"),
        ]
        from PyQt5.QtCore import QSize
        for attr, svg_file in configs:
            btn = getattr(self, attr, None)
            if btn is None:
                continue
            icon = _svg_icon(resource_path("icons", "svg", svg_file), "#6B7280", 18)
            if not icon.isNull():
                btn.setIcon(icon)
                btn.setIconSize(QSize(18, 18))
        logger.info("Nav icons loaded from SVG files")

    # =========================================================================
    # ABOUT PAGE & ANIMATIONS
    # =========================================================================
    def _setup_default_album_art(self):
        """Load images/profile_home.jpeg sebagai default album art (tidak bisa diklik ganti)."""
        base = PROJECT_ROOT
        path = resource_path("images", "profile_home.jpeg")
        if os.path.exists(path):
            # Load pixmap langsung tanpa grayscale
            raw_px = QPixmap(path)
            if not raw_px.isNull():
                # Scale dan crop ke center
                size = C.ALBUM_ART_SIZE
                raw_px = raw_px.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                x, y = (raw_px.width() - size) // 2, (raw_px.height() - size) // 2
                raw_px = raw_px.copy(x, y, size, size)
                
                # Buat rounded corners
                result = QPixmap(size, size)
                result.fill(Qt.transparent)
                p = QPainter(result)
                p.setRenderHint(QPainter.Antialiasing)
                p.setRenderHint(QPainter.SmoothPixmapTransform)
                clip = QPainterPath()
                clip.addRoundedRect(0, 0, size, size, 14, 14)
                p.setClipPath(clip)
                p.drawPixmap(0, 0, raw_px)
                p.end()
                
                # Set ke button
                self.albumArtBtn.setText("")
                self.albumArtBtn.setIcon(QIcon(result))
                self.albumArtBtn.setIconSize(result.size())
                logger.info(f"Default album art loaded: {path} (color mode: {raw_px.depth()} bit)")
        
        # Disable click — album art sudah fixed pakai profile_home.jpeg
        self.albumArtBtn.setEnabled(False)
        self.albumArtBtn.setToolTip("SoundWave")
        logger.info("Default album art loaded: images/profile_home.jpeg")
    
    def _setup_like_icon(self):
        """Setup icon love default saat startup."""
        # Set icon heart default (grey/unliked)
        icon = _svg_icon(resource_path("icons", "svg", "heart.svg"), "#6B7280", 24)
        if not icon.isNull():
            self.btnLike.setIcon(icon)
            from PyQt5.QtCore import QSize
            self.btnLike.setIconSize(QSize(24, 24))
            self.btnLike.setText("")  # Hapus text default
            logger.info("Like icon initialized with heart.svg")
        else:
            # Fallback ke emoji
            self.btnLike.setText("♡")
            logger.warn("heart.svg not found, using emoji fallback")
        
        # Setup shuffle icon
        shuffle_icon = _svg_icon(resource_path("icons", "svg", "shuffle.svg"), "#6B7280", 20)
        if not shuffle_icon.isNull():
            self.btnShuffle.setIcon(shuffle_icon)
            self.btnShuffle.setIconSize(QSize(20, 20))
            self.btnShuffle.setText("")
            logger.info("Shuffle icon initialized")
        
        # Setup repeat icon
        repeat_icon = _svg_icon(resource_path("icons", "svg", "repeat.svg"), "#6B7280", 20)
        if not repeat_icon.isNull():
            self.btnRepeat.setIcon(repeat_icon)
            self.btnRepeat.setIconSize(QSize(20, 20))
            self.btnRepeat.setText("")
            logger.info("Repeat icon initialized")
        
        # Setup prev icon
        prev_icon = _svg_icon(resource_path("icons", "svg", "skip-back.svg"), "#A78BFA", 22)
        if not prev_icon.isNull():
            self.btnPrev.setIcon(prev_icon)
            self.btnPrev.setIconSize(QSize(22, 22))
            self.btnPrev.setText("")
            logger.info("Prev icon initialized")
        
        # Setup next icon
        next_icon = _svg_icon(resource_path("icons", "svg", "skip-forward.svg"), "#A78BFA", 22)
        if not next_icon.isNull():
            self.btnNext.setIcon(next_icon)
            self.btnNext.setIconSize(QSize(22, 22))
            self.btnNext.setText("")
            logger.info("Next icon initialized")
    
    def _setup_about_page(self):
        """Setup halaman About dengan foto developer dan info aplikasi."""
        base = PROJECT_ROOT
        photo_path = resource_path("images", "tdx.jpeg")
        
        # Load dan buat foto developer jadi rounded dengan border
        if os.path.exists(photo_path):
            # Buat pixmap rounded dengan border
            dev_pixmap = self._make_dev_photo(photo_path, 180)
            if not dev_pixmap.isNull():
                self.devPhoto.setPixmap(dev_pixmap)
                self.devPhoto.setText("")
                self.devPhoto.setStyleSheet("")  # Clear default style
        
        # Anda bisa customize info developer di sini
        self.devName.setText("Redsilence Trashdex")
        self.devRole.setText("UI/UX Engineer · Music Enthusiast")
        self.devBio.setText(
            "Passionate about creating beautiful and functional applications. "
            "SoundWave is built with love using Python, PyQt5, and modern design principles. "
            "Enjoy your music experience! 🎵"
        )
        self.devEmail.setText("📧 redsilence@gmail.com")
        self.devGithub.setText("🔗 https://t.me/bravo6core")
        
        logger.info("About page initialized with developer info")

    def _setup_ai_chat_page(self):
        """Setup halaman AI Chat dengan widget chatbot"""
        self.ai_chat_widget = AIChatWidget(self.pageAIChat)
        layout = QHBoxLayout(self.pageAIChat)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ai_chat_widget)
        logger.info("AI Chat page initialized")

    def _setup_ai_chat_v2_page(self):
        """Setup halaman AI Chat V2 dengan Groq API"""
        self.ai_chat_v2_widget = AIChatWidgetV2(self.pageAIChatV2)
        layout = QHBoxLayout(self.pageAIChatV2)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ai_chat_v2_widget)
        logger.info("AI Chat V2 (Groq) page initialized")

    def _setup_playlist_page(self):
        self.playlist_widget = PlaylistWidget(self.playlist_mgr, self.pagePlaylist)
        self.playlist_widget.load_playlist.connect(self._load_playlist_songs)
        layout = QHBoxLayout(self.pagePlaylist)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.playlist_widget)
        logger.info("Playlist page initialized")

    def _setup_recent_page(self):
        self.recent_widget = RecentlyPlayedWidget(self.recent_mgr, self.pageRecent)
        self.recent_widget.play_song.connect(self._play_from_recent)
        layout = QHBoxLayout(self.pageRecent)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.recent_widget)
        logger.info("Recently Played page initialized")

    def _setup_quiz_page(self):
        self.quiz_widget = MusicQuizWidget(self.pageQuiz)
        self.quiz_widget.play_preview.connect(self._quiz_play_preview)
        self.quiz_widget.stop_preview.connect(self._quiz_stop_preview)
        layout = QHBoxLayout(self.pageQuiz)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.quiz_widget)
        logger.info("Music Quiz page initialized")

    def _setup_stats_page(self):
        self.stats_widget = StatsWidget(self.stats_mgr, self.pageStats)
        layout = QHBoxLayout(self.pageStats)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stats_widget)
        logger.info("Stats page initialized")

    def _make_dev_photo(self, path: str, size: int = 180) -> QPixmap:
        """Buat foto developer rounded dengan border yang pas."""
        raw = QPixmap(path)
        if raw.isNull():
            return QPixmap()
        
        # Scale gambar dengan aspect ratio
        raw = raw.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        # Crop ke center
        x, y = (raw.width() - size) // 2, (raw.height() - size) // 2
        raw = raw.copy(x, y, size, size)
        
        # Buat pixmap baru dengan space untuk border
        border_width = 4
        total_size = size + (border_width * 2)
        result = QPixmap(total_size, total_size)
        result.fill(Qt.transparent)
        
        p = QPainter(result)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Gambar border (lingkaran luar)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#A78BFA"))
        p.drawEllipse(0, 0, total_size, total_size)
        
        # Gambar foto (lingkaran dalam)
        clip = QPainterPath()
        clip.addEllipse(border_width, border_width, size, size)
        p.setClipPath(clip)
        p.drawPixmap(border_width, border_width, raw)
        
        p.end()
        return result

    def _fade_in_animation(self):
        """Animasi fade-in saat aplikasi pertama kali dibuka."""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.centralwidget.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(800)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.start()

    # =========================================================================
    def _connect_signals(self):
        self.btnHome.clicked.connect(lambda: self._go_page(C.PAGE_HOME))
        self.btnSearch.clicked.connect(lambda: self._go_page(C.PAGE_SEARCH))
        self.btnLibrary.clicked.connect(lambda: self._go_page(C.PAGE_LIBRARY))
        self.btnFavorites.clicked.connect(lambda: self._go_page(C.PAGE_FAVORITES))
        self.btnAIChat.clicked.connect(lambda: self._go_page(C.PAGE_AI_CHAT))
        self.btnAIChatV2.clicked.connect(lambda: self._go_page(C.PAGE_AI_CHAT_V2))
        self.btnPlaylist.clicked.connect(lambda: self._go_page(C.PAGE_PLAYLIST))
        self.btnRecent.clicked.connect(self._go_recent)
        self.btnQuiz.clicked.connect(self._go_quiz)
        self.btnStats.clicked.connect(self._go_stats)
        self.btnAbout.clicked.connect(lambda: self._go_page(C.PAGE_ABOUT))

        self.btnAddSong.clicked.connect(self.add_songs)
        self.btnPlay.clicked.connect(self.toggle_play)
        self.btnNext.clicked.connect(self.next_song)
        self.btnPrev.clicked.connect(self.prev_song)
        self.btnShuffle.clicked.connect(self.toggle_shuffle)
        self.btnRepeat.clicked.connect(self.toggle_repeat)
        self.btnLike.clicked.connect(self.toggle_like)

        self.albumArtBtn.clicked.connect(lambda: None)  # disabled — fixed album art
        self.volumeSlider.valueChanged.connect(self._change_volume)
        self.progressSlider.sliderMoved.connect(self._seek)

        self.songList.itemDoubleClicked.connect(self._play_from_sidebar)
        self.searchInput.textChanged.connect(self._do_search)
        self.searchResultList.itemDoubleClicked.connect(self._play_from_search)
        self.libraryList.itemDoubleClicked.connect(self._play_from_library)
        self.favList.itemDoubleClicked.connect(self._play_from_favorites)
        self.btnImportLib.clicked.connect(self.add_songs)
        self.btnClearQueue.clicked.connect(self.clear_queue)

    # =========================================================================
    def _go_page(self, page_index):
        self.stackedPages.setCurrentIndex(page_index)
        nav_buttons = [
            self.btnHome, self.btnSearch, self.btnLibrary, self.btnFavorites,
            self.btnAIChat, self.btnPlaylist, self.btnRecent, self.btnQuiz,
            self.btnStats, self.btnAbout, self.btnAIChatV2
        ]
        svg_files = [
            "home.svg", "search.svg", "library.svg", "heart.svg",
            "bot.svg", "playlist.svg", "clock.svg", "target.svg",
            "chart.svg", "info.svg", "zap.svg",
        ]
        base = PROJECT_ROOT
        for i, btn in enumerate(nav_buttons):
            is_active = (i == page_index)
            btn.setStyleSheet(C.NAV_ACTIVE if is_active else C.NAV_INACTIVE)
            if i < len(svg_files):
                color = "#A78BFA" if is_active else "#6B7280"
                icon  = _svg_icon(resource_path("icons", "svg", svg_files[i]), color, 18)
                if not icon.isNull():
                    btn.setIcon(icon)
                    from PyQt5.QtCore import QSize
                    btn.setIconSize(QSize(18, 18))
        if page_index == C.PAGE_FAVORITES:
            self._refresh_fav_empty()
        logger.nav_changed(page_index)

    def _go_recent(self):
        self.recent_widget.refresh()
        self._go_page(C.PAGE_RECENT)

    def _go_quiz(self):
        self.quiz_widget.set_songs(self.songs)
        self._go_page(C.PAGE_QUIZ)

    def _go_stats(self):
        self.stats_widget.refresh()
        self._go_page(C.PAGE_STATS)

    # =========================================================================
    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Pilih File Musik", "", C.AUDIO_FILTER
        )
        added = 0
        for fp in files:
            if fp not in self.songs:
                self.songs.append(fp)
                name = song_name(fp)
                self.songList.addItem(QListWidgetItem("♪  " + name))
                li = QListWidgetItem("🎵  " + name)
                li.setData(Qt.UserRole, fp)
                self.libraryList.addItem(li)
                qi = QListWidgetItem("   " + name)
                qi.setData(Qt.UserRole, fp)
                self.queueList.addItem(qi)
                added += 1
                logger.song_added(name, len(self.songs))
        if added:
            self.statusBar.showMessage(f"{added} lagu berhasil ditambahkan")
            self._update_queue_badge()
            if self.current_index == -1:
                self._load_song(0)

    # =========================================================================
    def clear_queue(self):
        count = self.queueList.count()
        if count == 0:
            logger.warn("Queue sudah kosong")
            return
        self.queueList.clear()
        self.songs.clear()
        self.current_index = -1
        self.is_playing    = False
        self.timer.stop()
        self.end_check.stop()
        pygame.mixer.music.stop()
        self.btnPlay.setText("▶")
        self.songTitle.setText("No Song Selected")
        self.artistName.setText("Unknown Artist")
        self.albumName.setText("Unknown Album")
        self.progressSlider.setValue(0)
        self.timeElapsed.setText("0:00")
        self.timeDuration.setText("0:00")
        self.equalizer.set_active(False)
        self.songList.clear()
        self._update_queue_badge()
        self.statusBar.showMessage("Queue dikosongkan")
        logger.queue_cleared(count)

    # =========================================================================
    def change_album_art(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Foto Album Art", "", C.IMAGE_FILTER
        )
        if path:
            px = make_rounded_pixmap(path, C.ALBUM_ART_SIZE)
            if not px.isNull():
                self.albumArtBtn.setText("")
                self.albumArtBtn.setIcon(QIcon(px))
                self.albumArtBtn.setIconSize(px.size())
            self.statusBar.showMessage("Album art diperbarui!")
            logger.album_art_changed(path)

    # =========================================================================
    def _load_song(self, index):
        if not (0 <= index < len(self.songs)):
            return
        self.current_index = index
        fp = self.songs[index]
        pygame.mixer.music.load(fp)

        try:
            snd = pygame.mixer.Sound(fp)
            self._song_length = snd.get_length()
            del snd
        except Exception:
            self._song_length = 0

        self._elapsed_acc = 0.0
        self.is_playing   = False

        name = song_name(fp)
        self.songTitle.setText(name)
        self.artistName.setText("Unknown Artist")
        self.albumName.setText("Unknown Album")
        self.songList.setCurrentRow(index)
        self.progressSlider.setValue(0)
        self.timeElapsed.setText("0:00")
        self.timeDuration.setText(fmt_time(self._song_length))
        self.liked = fp in self.favorites
        self._update_like_btn()
        self.statusBar.showMessage("Now Playing: " + name)
        logger.song_loaded(name, fmt_time(self._song_length), index)

        # ── Feature hooks ──────────────────────────────────────────────────────
        # Lyrics
        self.lyrics_widget.load_lyrics(name)
        # Recently Played
        self.recent_mgr.add(fp)
        # Stats
        self.stats_mgr.record_play(fp)
        # Mood color from album art icon (if set)
        self._apply_mood_color()

    # =========================================================================
    def toggle_play(self):
        if not self.songs:
            self.statusBar.showMessage("Belum ada lagu — klik [＋ Add Song]")
            logger.warn("Tidak ada lagu di queue")
            return
        if self.current_index == -1:
            self._load_song(0)

        if self.is_playing:
            pygame.mixer.music.pause()
            elapsed = self._elapsed_acc + (time.time() - self._play_start)
            self._elapsed_acc += time.time() - self._play_start
            self.is_playing = False
            self.btnPlay.setText("▶")
            self.timer.stop()
            self.end_check.stop()
            self._stats_timer.stop()
            self.equalizer.set_active(False)
            logger.song_pause(song_name(self.songs[self.current_index]), fmt_time(elapsed))
        else:
            if pygame.mixer.music.get_pos() == -1:
                pygame.mixer.music.play()
                self._elapsed_acc = 0.0
            else:
                pygame.mixer.music.unpause()
            self._play_start = time.time()
            self.is_playing  = True
            self.btnPlay.setText("⏸")
            self.timer.start()
            self.end_check.start()
            self._stats_timer.start()
            self.equalizer.set_active(True)
            logger.song_play(song_name(self.songs[self.current_index]))

    # =========================================================================
    def _play_now(self, index):
        pygame.mixer.music.stop()
        self.timer.stop()
        self.end_check.stop()
        self._stats_timer.stop()
        self.is_playing = False
        self._load_song(index)
        pygame.mixer.music.play()
        self._play_start  = time.time()
        self._elapsed_acc = 0.0
        self.is_playing   = True
        self.btnPlay.setText("⏸")
        self.timer.start()
        self.end_check.start()
        self._stats_timer.start()
        self.equalizer.set_active(True)

    def _play_from_sidebar(self, item):
        self._play_now(self.songList.row(item))

    def _play_from_library(self, item):
        fp = item.data(Qt.UserRole)
        if fp and fp in self.songs:
            self._play_now(self.songs.index(fp))
            self._go_page(C.PAGE_HOME)

    def _play_from_search(self, item):
        fp = item.data(Qt.UserRole)
        if fp and fp in self.songs:
            self._play_now(self.songs.index(fp))
            self._go_page(C.PAGE_HOME)

    def _play_from_favorites(self, item):
        fp = item.data(Qt.UserRole)
        if fp and fp in self.songs:
            self._play_now(self.songs.index(fp))
            self._go_page(C.PAGE_HOME)

    # =========================================================================
    def next_song(self):
        if not self.songs:
            return
        idx = (random.randint(0, len(self.songs) - 1) if self.shuffle
               else (self.current_index + 1) % len(self.songs))
        self._play_now(idx)
        logger.song_next(song_name(self.songs[idx]))

    def prev_song(self):
        if not self.songs:
            return
        elapsed = self._elapsed_acc + (time.time() - self._play_start if self.is_playing else 0)
        if elapsed > C.PREV_RESTART_SEC:
            pygame.mixer.music.play()
            self._play_start  = time.time()
            self._elapsed_acc = 0.0
        else:
            idx = (random.randint(0, len(self.songs) - 1) if self.shuffle
                   else (self.current_index - 1) % len(self.songs))
            self._play_now(idx)
            logger.song_prev(song_name(self.songs[idx]))

    # =========================================================================
    def _update_progress(self):
        if not self.is_playing:
            return
        elapsed = self._elapsed_acc + (time.time() - self._play_start)
        if self._song_length > 0:
            pct = min(elapsed / self._song_length, 1.0)
            self.progressSlider.setValue(int(pct * 1000))
            self.timeElapsed.setText(fmt_time(elapsed))
            self.timeDuration.setText(fmt_time(self._song_length))

    def _seek(self, value):
        if self._song_length <= 0:
            return
        target = value / 1000 * self._song_length
        pygame.mixer.music.play(start=target)
        self._elapsed_acc = target
        self._play_start  = time.time()
        if not self.is_playing:
            self.is_playing = True
            self.btnPlay.setText("⏸")
            self.timer.start()
            self.end_check.start()
            self.equalizer.set_active(True)
        name = song_name(self.songs[self.current_index]) if self.current_index >= 0 else "?"
        logger.song_seek(name, target, self._song_length)

    def _check_song_end(self):
        if not self.is_playing:
            return
        if not pygame.mixer.music.get_busy():
            name = song_name(self.songs[self.current_index]) if self.current_index >= 0 else "?"
            logger.song_end(name)
            self.is_playing = False
            self.timer.stop()
            self.end_check.stop()
            self.btnPlay.setText("▶")
            self.equalizer.set_active(False)
            if self.repeat:
                self._play_now(self.current_index)
            else:
                self.next_song()

    # =========================================================================
    def _change_volume(self, value):
        pygame.mixer.music.set_volume(value / 100)
        self.lblVolIcon.setText(
            "🔇" if value == 0 else
            "🔈" if value < 40 else
            "🔊"
        )
        logger.volume_changed(value)

    # =========================================================================
    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        # Update icon dengan SVG
        color = "#A78BFA" if self.shuffle else "#6B7280"
        icon = _svg_icon(resource_path("icons", "svg", "shuffle.svg"), color, 20)
        if not icon.isNull():
            self.btnShuffle.setIcon(icon)
            self.btnShuffle.setIconSize(QSize(20, 20))
            self.btnShuffle.setText("")
        self.btnShuffle.setStyleSheet(C.TOGGLE_ON_STYLE if self.shuffle else C.TOGGLE_OFF_STYLE)
        self.statusBar.showMessage("Shuffle " + ("ON ⇄" if self.shuffle else "OFF"))
        logger.shuffle_toggled(self.shuffle)

    def toggle_repeat(self):
        self.repeat = not self.repeat
        # Update icon dengan SVG
        color = "#A78BFA" if self.repeat else "#6B7280"
        icon = _svg_icon(resource_path("icons", "svg", "repeat.svg"), color, 20)
        if not icon.isNull():
            self.btnRepeat.setIcon(icon)
            self.btnRepeat.setIconSize(QSize(20, 20))
            self.btnRepeat.setText("")
        self.btnRepeat.setStyleSheet(C.TOGGLE_ON_STYLE if self.repeat else C.TOGGLE_OFF_STYLE)
        self.statusBar.showMessage("Repeat " + ("ON ↺" if self.repeat else "OFF"))
        logger.repeat_toggled(self.repeat)

    def toggle_like(self):
        if self.current_index < 0:
            self.statusBar.showMessage("Putar lagu dulu sebelum like!")
            logger.warn("Like gagal — tidak ada lagu aktif")
            return
        fp = self.songs[self.current_index]
        self.liked = not self.liked
        if self.liked:
            self.favorites.add(fp)
            self._add_to_fav_list(fp)
            self.statusBar.showMessage("♥  Ditambahkan ke Favorites!")
            logger.like_added(song_name(fp))
        else:
            self.favorites.discard(fp)
            self._remove_from_fav_list(fp)
            self.statusBar.showMessage("Dihapus dari Favorites")
            logger.like_removed(song_name(fp))
        self._update_like_btn()
        self._refresh_fav_empty()
        self._update_fav_badge()

    def _update_like_btn(self):
        """Update like button dengan SVG icon yang sama dengan sidebar."""
        base = PROJECT_ROOT
        if self.liked:
            # Pakai heart.svg yang sama dengan sidebar, tapi warna pink
            icon = _svg_icon(resource_path("icons", "svg", "heart.svg"), "#F472B6", 24)
            self.btnLike.setStyleSheet(C.LIKE_ON_STYLE)
        else:
            # Pakai heart.svg dengan warna grey
            icon = _svg_icon(resource_path("icons", "svg", "heart.svg"), "#6B7280", 24)
            self.btnLike.setStyleSheet(C.LIKE_OFF_STYLE)
        
        if not icon.isNull():
            self.btnLike.setIcon(icon)
            from PyQt5.QtCore import QSize
            self.btnLike.setIconSize(QSize(24, 24))
            self.btnLike.setText("")  # Hapus text, pakai icon aja
        else:
            # Fallback ke emoji jika SVG tidak ditemukan
            self.btnLike.setText("♥" if self.liked else "♡")
            self.btnLike.setIcon(QIcon())

    def _add_to_fav_list(self, fp):
        for i in range(self.favList.count()):
            if self.favList.item(i).data(Qt.UserRole) == fp:
                return
        item = QListWidgetItem("♥  " + song_name(fp))
        item.setData(Qt.UserRole, fp)
        self.favList.addItem(item)

    def _remove_from_fav_list(self, fp):
        for i in range(self.favList.count()):
            if self.favList.item(i).data(Qt.UserRole) == fp:
                self.favList.takeItem(i)
                return

    def _refresh_fav_empty(self):
        has = self.favList.count() > 0
        self.favList.setVisible(has)
        self.lblFavEmpty.setVisible(not has)

    # ── Badge Counts ──────────────────────────────────────────────────────────
    def _update_queue_badge(self):
        count = len(self.songs)
        if hasattr(self, "lblQueueSub"):
            self.lblQueueSub.setText(f"Queue  ·  {count}" if count > 0 else "Queue")

    def _update_fav_badge(self):
        count = len(self.favorites)
        label = f"❤️   Favorites  {count}" if count > 0 else "❤️   Favorites"
        self.btnFavorites.setText(label)

    # =========================================================================
    def _do_search(self, text):
        self.searchResultList.clear()
        query = text.strip().lower()
        if not query:
            self.lblSearchHint.setText("Ketik nama lagu atau artis untuk mencari...")
            self.lblSearchHint.setVisible(True)
            self.searchResultList.setVisible(False)
            return
        results = [fp for fp in self.songs if query in song_name(fp).lower()]
        if results:
            self.lblSearchHint.setVisible(False)
            self.searchResultList.setVisible(True)
            for fp in results:
                item = QListWidgetItem("🎵  " + song_name(fp))
                item.setData(Qt.UserRole, fp)
                self.searchResultList.addItem(item)
        else:
            self.searchResultList.setVisible(False)
            self.lblSearchHint.setText(f'Tidak ditemukan: "{text}"')
            self.lblSearchHint.setVisible(True)

    def _tick_stats(self):
        """Dipanggil setiap 5 detik saat musik playing — catat playtime."""
        if self.is_playing:
            self.stats_mgr.add_playtime(5)

    def _apply_mood_color(self):
        """Ambil dominant color dari album art dan apply ke accent UI."""
        icon = self.albumArtBtn.icon()
        if icon.isNull():
            return
        px = icon.pixmap(200, 200)
        if px.isNull():
            return
        accent  = MoodColorEngine.extract(px)
        palette = MoodColorEngine.make_palette(accent)
        # Update warna progress slider & play button secara dinamis
        self.progressSlider.setStyleSheet(f"""
            QSlider#progressSlider::groove:horizontal {{
                height: 4px; background: #2D2D44; border-radius: 2px;
            }}
            QSlider#progressSlider::handle:horizontal {{
                background: #FFFFFF; width: 14px; height: 14px;
                margin: -5px 0; border-radius: 7px;
            }}
            QSlider#progressSlider::sub-page:horizontal {{
                background: {palette['accent']}; border-radius: 2px;
            }}
        """)
        self.btnPlay.setFixedSize(56, 56)
        self.btnPlay.setStyleSheet(f"""
            QPushButton#btnPlay {{
                background-color: {palette['accent']}; color: #0A0A0F;
                font-size: 20px; font-weight: bold; border: none;
                border-radius: 28px;
                min-width: 56px; max-width: 56px;
                min-height: 56px; max-height: 56px;
            }}
            QPushButton#btnPlay:hover {{ background-color: {palette['hover']}; }}
            QPushButton#btnPlay:pressed {{ background-color: {palette['dark']}; color: #E2E8F0; }}
        """)

    def _load_playlist_songs(self, filepaths: list):
        """Load semua lagu dari playlist ke queue lalu play."""
        for fp in filepaths:
            if fp not in self.songs:
                self.songs.append(fp)
                name = song_name(fp)
                self.songList.addItem(QListWidgetItem("♪  " + name))
                li = QListWidgetItem("🎵  " + name)
                li.setData(Qt.UserRole, fp)
                self.libraryList.addItem(li)
                qi = QListWidgetItem("   " + name)
                qi.setData(Qt.UserRole, fp)
                self.queueList.addItem(qi)
        self._update_queue_badge()
        self._go_page(C.PAGE_HOME)
        if self.songs:
            self._play_now(0)

    def _play_from_recent(self, filepath: str):
        """Putar lagu dari Recently Played."""
        if filepath not in self.songs:
            self.songs.append(filepath)
            name = song_name(filepath)
            self.songList.addItem(QListWidgetItem("♪  " + name))
            li = QListWidgetItem("🎵  " + name)
            li.setData(Qt.UserRole, filepath)
            self.libraryList.addItem(li)
            qi = QListWidgetItem("   " + name)
            qi.setData(Qt.UserRole, filepath)
            self.queueList.addItem(qi)
            self._update_queue_badge()
        self._play_now(self.songs.index(filepath))
        self._go_page(C.PAGE_HOME)

    def _quiz_play_preview(self, filepath: str, duration_ms: int):
        """Play preview lagu untuk kuis (tanpa mengganggu queue)."""
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            QTimer.singleShot(duration_ms, self._quiz_stop_preview)
        except Exception as e:
            logger.error(f"Quiz preview error: {e}")

    def _quiz_stop_preview(self):
        """Stop preview kuis, lanjut lagu yang sedang diputar kalau ada."""
        try:
            pygame.mixer.music.stop()
            if self.is_playing and self.current_index >= 0:
                fp = self.songs[self.current_index]
                pygame.mixer.music.load(fp)
                elapsed = self._elapsed_acc + (time.time() - self._play_start)
                pygame.mixer.music.play(start=elapsed)
        except Exception:
            pass

    # =========================================================================
    # DRAG & DROP SUPPORT
    # =========================================================================
    def dragEnterEvent(self, event):
        """Accept drag event jika ada file audio."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            # Check if any file is audio
            for url in urls:
                path = url.toLocalFile()
                if path.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                    event.accept()
                    self.statusBar.showMessage("🎵 Drop file untuk menambahkan ke queue...")
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        """Reset status bar saat drag leave."""
        self.statusBar.showMessage("Ready")

    def dropEvent(self, event):
        """Handle dropped audio files."""
        files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                files.append(path)
        
        if files:
            added = 0
            for fp in files:
                if fp not in self.songs:
                    self.songs.append(fp)
                    name = song_name(fp)
                    self.songList.addItem(QListWidgetItem("♪  " + name))
                    li = QListWidgetItem("🎵  " + name)
                    li.setData(Qt.UserRole, fp)
                    self.libraryList.addItem(li)
                    qi = QListWidgetItem("   " + name)
                    qi.setData(Qt.UserRole, fp)
                    self.queueList.addItem(qi)
                    added += 1
                    logger.song_added(name, len(self.songs))
            
            if added:
                self.statusBar.showMessage(f"✅ {added} lagu ditambahkan via drag & drop!")
                self._update_queue_badge()
                if self.current_index == -1:
                    self._load_song(0)
            else:
                self.statusBar.showMessage("⚠️ Lagu sudah ada di queue")
        
        event.accept()

    # =========================================================================
    def closeEvent(self, event):
        self._stats_timer.stop()
        self.stats_mgr.save()
        pygame.mixer.quit()
        logger.app_exit()
        event.accept()
