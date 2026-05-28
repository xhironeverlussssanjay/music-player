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


class MusicQuizWidget(QWidget):
    """Tebak judul lagu dari 10 detik pertama pakai library sendiri."""

    play_preview   = pyqtSignal(str, int)   # filepath, duration_ms
    stop_preview   = pyqtSignal()

    STYLE = """
    QWidget#quizRoot { background: transparent; }
    QLabel#quizTitle {
        color: #FFFFFF; font-size: 22px; font-weight: bold; font-family: 'Segoe UI';
    }
    QLabel#quizScore {
        color: #A78BFA; font-size: 14px; font-weight: 600; font-family: 'Segoe UI';
    }
    QLabel#quizQuestion {
        color: #E2E8F0; font-size: 15px; font-family: 'Segoe UI';
        background-color: #141420; border-radius: 14px;
        padding: 20px; border: 1px solid #2D2D44;
    }
    QLabel#quizTimer {
        color: #F59E0B; font-size: 20px; font-weight: 700; font-family: 'Segoe UI';
    }
    QPushButton#btnQuizAnswer {
        background-color: #1A1A2E; color: #CBD5E1;
        border: 1px solid #2D2D44; border-radius: 12px;
        font-size: 13px; padding: 14px 10px; text-align: left;
    }
    QPushButton#btnQuizAnswer:hover {
        background-color: #1F1A3A; color: #E2E8F0; border-color: #6D4BC2;
    }
    QPushButton#btnQuizCorrect {
        background-color: #14532d; color: #4ADE80;
        border: 1px solid #4ADE80; border-radius: 12px;
        font-size: 13px; padding: 14px 10px; text-align: left;
    }
    QPushButton#btnQuizWrong {
        background-color: rgba(156,163,175,0.10); color: #9CA3AF;
        border: 1px solid #2D2D44; border-radius: 12px;
        font-size: 13px; padding: 14px 10px; text-align: left;
    }
    QPushButton#btnQuizStart, QPushButton#btnQuizNext {
        background-color: #A78BFA; color: #0A0A0F;
        border: none; border-radius: 12px;
        font-size: 13px; font-weight: bold; padding: 12px 28px;
    }
    QPushButton#btnQuizStart:hover, QPushButton#btnQuizNext:hover {
        background-color: #C4B5FD;
    }
    QPushButton#btnQuizStop {
        background: transparent; color: #9CA3AF;
        border: 1px solid #2D2D44; border-radius: 10px;
        font-size: 12px; padding: 8px 16px;
        text-align: center;
    }
    QPushButton#btnQuizStop:hover {
        color: #E2E8F0;
        border-color: #6B7280;
        background-color: rgba(156,163,175,0.08);
    }
    QProgressBar#quizProgress {
        background-color: #1A1A28; border-radius: 4px; border: none; height: 6px;
    }
    QProgressBar#quizProgress::chunk { background-color: #A78BFA; border-radius: 4px; }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("quizRoot")
        self.setStyleSheet(self.STYLE)
        self.songs: list[str] = []
        self._score     = 0
        self._total     = 0
        self._current   = ""
        self._choices   = []
        self._answered  = False
        self._countdown = 0
        self._ctimer    = QTimer(self)
        self._ctimer.setInterval(1000)
        self._ctimer.timeout.connect(self._tick_timer)
        self._build_ui()

    def set_songs(self, songs: list):
        self.songs = songs

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 20)
        root.setSpacing(14)

        hdr = QHBoxLayout()
        title = QLabel("🎯  Music Quiz")
        title.setObjectName("quizTitle")
        self.score_lbl = QLabel("Score: 0 / 0")
        self.score_lbl.setObjectName("quizScore")
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self.score_lbl)
        root.addLayout(hdr)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setObjectName("quizProgress")
        self.progress.setMaximum(20)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        root.addWidget(self.progress)

        # Timer
        self.timer_lbl = QLabel("⏱  --")
        self.timer_lbl.setObjectName("quizTimer")
        self.timer_lbl.setAlignment(Qt.AlignCenter)
        root.addWidget(self.timer_lbl)

        # Question
        self.question_lbl = QLabel("Tekan START untuk mulai kuis!\nPastikan kamu sudah punya lagu di library.")
        self.question_lbl.setObjectName("quizQuestion")
        self.question_lbl.setWordWrap(True)
        self.question_lbl.setAlignment(Qt.AlignCenter)
        root.addWidget(self.question_lbl)

        # Answer buttons (2x2 grid)
        self.btn_answers = []
        grid = QGridLayout()
        grid.setSpacing(10)
        for i in range(4):
            btn = QPushButton("")
            btn.setObjectName("btnQuizAnswer")
            btn.clicked.connect(lambda _, idx=i: self._answer(idx))
            btn.setVisible(False)
            grid.addWidget(btn, i // 2, i % 2)
            self.btn_answers.append(btn)
        root.addLayout(grid)

        # Control buttons
        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)
        self.btn_start = QPushButton("▶  Start Quiz")
        self.btn_start.setObjectName("btnQuizStart")
        self.btn_start.clicked.connect(self._start)
        self.btn_next  = QPushButton("Next ⏭")
        self.btn_next.setObjectName("btnQuizNext")
        self.btn_next.clicked.connect(self._next_question)
        self.btn_next.setVisible(False)
        self.btn_stop  = QPushButton("✕  Stop Quiz")
        self.btn_stop.setObjectName("btnQuizStop")
        self.btn_stop.clicked.connect(self._stop)
        self.btn_stop.setVisible(False)
        ctrl.addWidget(self.btn_start)
        ctrl.addWidget(self.btn_next)
        ctrl.addStretch()
        ctrl.addWidget(self.btn_stop)
        root.addLayout(ctrl)
        root.addStretch()

    def _start(self):
        if len(self.songs) < 4:
            self.question_lbl.setText("⚠️  Butuh minimal 4 lagu di library untuk main kuis!")
            return
        self._score   = 0
        self._total   = 0
        self.progress.setValue(0)
        self.btn_start.setVisible(False)
        self.btn_stop.setVisible(True)
        self._next_question()

    def _next_question(self):
        if self._total >= 10:
            self._show_result()
            return
        self.btn_next.setVisible(False)
        self._answered = False
        self._current  = random.choice(self.songs)
        # Generate 3 wrong answers
        wrong = [s for s in self.songs if s != self._current]
        random.shuffle(wrong)
        self._choices  = ([self._current] + wrong[:3])
        random.shuffle(self._choices)

        name = os.path.splitext(os.path.basename(self._current))[0]
        self.question_lbl.setText(f"🎵  Tebak lagu ini!\n\n(Preview 10 detik pertama sedang diputar...)")
        self.play_preview.emit(self._current, 10000)

        for i, fp in enumerate(self._choices):
            sname = os.path.splitext(os.path.basename(fp))[0]
            self.btn_answers[i].setText(f"  {chr(65+i)}.  {sname}")
            self.btn_answers[i].setObjectName("btnQuizAnswer")
            self.btn_answers[i].setStyleSheet("")
            self.btn_answers[i].setEnabled(True)
            self.btn_answers[i].setVisible(True)

        self._countdown = 15
        self.timer_lbl.setText(f"⏱  {self._countdown}s")
        self._ctimer.start()
        self.progress.setValue(self._total)

    def _tick_timer(self):
        self._countdown -= 1
        self.timer_lbl.setText(f"⏱  {self._countdown}s")
        if self._countdown <= 0:
            self._ctimer.stop()
            if not self._answered:
                self._reveal_answer(-1)

    def _answer(self, idx: int):
        if self._answered:
            return
        self._ctimer.stop()
        self._answered = True
        self._total   += 1
        self.stop_preview.emit()
        correct_idx = self._choices.index(self._current)
        correct_name = os.path.splitext(os.path.basename(self._current))[0]

        if idx == correct_idx:
            self._score += 1
            self.btn_answers[idx].setObjectName("btnQuizCorrect")
            self.btn_answers[idx].setStyleSheet(
                "background-color:#14532d;color:#4ADE80;border:1px solid #4ADE80;border-radius:12px;font-size:13px;padding:14px 10px;"
            )
            self.question_lbl.setText(f"✅  Benar! Lagu itu adalah:\n{correct_name}")
            self.timer_lbl.setText("✓")
        else:
            self._reveal_answer(idx)

        self.score_lbl.setText(f"Score: {self._score} / {self._total}")
        self.btn_next.setVisible(True)
        self.progress.setValue(self._total)

    def _reveal_answer(self, wrong_idx: int):
        correct_idx = self._choices.index(self._current)
        correct_name = os.path.splitext(os.path.basename(self._current))[0]
        if wrong_idx >= 0:
            self.btn_answers[wrong_idx].setObjectName("btnQuizWrong")
            self.btn_answers[wrong_idx].setStyleSheet(
                "background-color:rgba(156,163,175,0.10);color:#9CA3AF;border:1px solid #2D2D44;border-radius:12px;font-size:13px;padding:14px 10px;"
            )
        self.btn_answers[correct_idx].setObjectName("btnQuizCorrect")
        self.btn_answers[correct_idx].setStyleSheet(
            "background-color:#14532d;color:#4ADE80;border:1px solid #4ADE80;border-radius:12px;font-size:13px;padding:14px 10px;"
        )
        for btn in self.btn_answers:
            btn.setEnabled(False)
        msg = f"❌  Waktu habis!" if wrong_idx == -1 else f"❌  Salah!"
        self.question_lbl.setText(f"{msg}\nJawaban: {correct_name}")
        self.timer_lbl.setText("✗")
        self._total += (1 if wrong_idx == -1 else 0)
        self.score_lbl.setText(f"Score: {self._score} / {self._total}")
        self.btn_next.setVisible(True)

    def _show_result(self):
        self._ctimer.stop()
        self.stop_preview.emit()
        pct = int(self._score / max(1, self._total) * 100)
        if pct >= 80:
            msg = "🏆 Luar biasa! Kamu hafal semua lagu!"
        elif pct >= 60:
            msg = "🎵 Bagus! Kamu cukup hapal library-mu."
        elif pct >= 40:
            msg = "🎧 Lumayan! Coba lagi untuk nilai lebih tinggi."
        else:
            msg = "😅 Kurang! Mungkin perlu lebih sering dengerin?"
        self.question_lbl.setText(
            f"Quiz Selesai! 🎉\n\nSkor kamu: {self._score} / {self._total}  ({pct}%)\n\n{msg}"
        )
        for btn in self.btn_answers:
            btn.setVisible(False)
        self.btn_next.setVisible(False)
        self.btn_start.setText("▶  Main Lagi")
        self.btn_start.setVisible(True)
        self.btn_stop.setVisible(False)
        self.timer_lbl.setText(f"🏅  {pct}%")

    def _stop(self):
        self._ctimer.stop()
        self.stop_preview.emit()
        for btn in self.btn_answers:
            btn.setVisible(False)
        self.btn_next.setVisible(False)
        self.btn_stop.setVisible(False)
        self.btn_start.setText("▶  Start Quiz")
        self.btn_start.setVisible(True)
        self.question_lbl.setText("Quiz dihentikan.\nTekan START untuk mulai lagi.")
        self.timer_lbl.setText("⏱  --")
        self.score_lbl.setText("Score: 0 / 0")
        self.progress.setValue(0)
