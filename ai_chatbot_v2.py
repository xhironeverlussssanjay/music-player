"""
AI CHATBOT V2 MODULE - Groq API (llama-3.1-8b-instant)

"""

import os
import json
import math
import requests
import random
from datetime import datetime
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QScrollArea, QLabel, QFrame, QFileDialog,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QRect, QRectF, QPointF
from PyQt5.QtGui import (
    QFont, QPixmap, QPainter, QPainterPath, QColor,
    QBrush, QPen, QLinearGradient, QRadialGradient, QConicalGradient,
)

import logger

# Load environment variables dari file .env
load_dotenv(os.path.join(os.path.dirname(__file__), "rest api bot", ".env"))


# ── Image Asset Helper ─────────────────────────────────────────────
# Semua gambar bawaan project disimpan di folder: images/
try:
    from app.helpers import resource_path
except Exception:
    def resource_path(*parts: str) -> str:
        base = os.path.dirname(os.path.abspath(__file__))
        candidates = [base, os.getcwd(), os.path.dirname(base)]
        for candidate in candidates:
            path = os.path.join(candidate, *parts)
            if os.path.exists(path):
                return path
        return os.path.join(base, *parts)


def image_resource(filename: str) -> str:
    return resource_path("images", filename)


# ═══════════════════════════════════════════════════════════════
#  GROQ API CONFIGURATION
#  API keys sekarang dimuat dari file .env untuk keamanan
# ═══════════════════════════════════════════════════════════════
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")


# ═══════════════════════════════════════════════════════════════
#  STYLESHEET — scoped ke objectName, kebal override styles.css
#  (identik dengan v1, hanya warna aksen sedikit berbeda: teal)
# ═══════════════════════════════════════════════════════════════
GLOBAL_STYLE = """
QWidget#chatRootWidgetV2 { background-color: #0D0D14; border: none; }

/* ── Header ─────────────────────────────── */
QWidget#chatHeaderV2 { background-color: #111120; border-bottom: 1px solid #222235; }
QLabel#chatHeaderNameV2 {
    color: #EEEEFF; font-size: 14px; font-weight: 700;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#chatHeaderStatusV2 {
    color: #4ADE80; font-size: 10px;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#chatHeaderBadge {
    background-color: #162C24;
    color: #4ADE80;
    border: 1px solid #22563A;
    border-radius: 8px;
    padding: 2px 8px;
    font-size: 9px; font-weight: 700;
    font-family: 'Segoe UI';
}
QPushButton#btnClearHeaderV2 {
    background-color: transparent; color: #44445A;
    border: 1px solid #222235; border-radius: 8px;
    padding: 5px 13px; font-size: 11px; font-family: 'Segoe UI';
}
QPushButton#btnClearHeaderV2:hover {
    color: #F87171; border-color: #F87171;
    background-color: #22161C;
}

/* ── Scroll & body ──────────────────────── */
QScrollArea#chatScrollAreaV2 { background-color: #0D0D14; border: none; }
QWidget#chatScrollAreaWidgetV2 { background-color: #0D0D14; }
QScrollBar:vertical { background-color: #111120; width: 4px; border-radius: 2px; }
QScrollBar::handle:vertical {
    background-color: #2A2A45; border-radius: 2px; min-height: 28px;
}
QScrollBar::handle:vertical:hover { background-color: #7C6EF5; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Welcome section ────────────────────── */
QFrame#featureCardV2 {
    background-color: #111120; border: 1px solid #252540;
    border-radius: 14px;
}
QFrame#featureCardV2:hover { border: 1px solid #7C6EF5; background-color: #16162A; }
QLabel#featureCardIconV2  { font-size: 22px; background-color: transparent; }
QLabel#featureCardTitleV2 {
    color: #DDDDF5; font-size: 12px; font-weight: 600;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#featureCardDescV2  {
    color: #44445A; font-size: 10px;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#welcomeTitleV2 {
    color: #EEEEFF; font-size: 21px; font-weight: 700;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#welcomeSubV2 {
    color: #6666AA; font-size: 12px;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#groqBadge {
    background-color: #211E3C;
    color: #A78BFA;
    border: 1px solid #39346E;
    border-radius: 10px;
    padding: 4px 14px;
    font-size: 11px; font-weight: 600;
    font-family: 'Segoe UI';
}

/* ── Bubbles ────────────────────────────── */
QFrame#bubbleUserV2 {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #2D1B69, stop:1 #1E1444);
    border-radius: 20px; border-top-right-radius: 6px;
    border: 1px solid #4C3299;
}
QLabel#bubbleUserTextV2 {
    color: #EDE9FF; font-size: 15px; font-weight: 700;
    font-family: 'Segoe UI'; background-color: transparent;
}
QFrame#bubbleAIV2 {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #131325, stop:1 #0F0F22);
    border-radius: 20px; border-top-left-radius: 6px;
    border: 1px solid #252545;
}
QLabel#bubbleAITextV2 {
    color: #F0EEFF; font-size: 15px; font-weight: 700;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#avatarUserV2 {
    background-color: #7C3AED;
    color: white; border-radius: 17px;
    font-size: 11px; font-weight: 700; font-family: 'Segoe UI';
}
QLabel#avatarAIV2 {
    background-color: #7C3AED;
    color: white; border-radius: 17px;
    font-size: 14px; font-family: 'Segoe UI';
}
/* Bubble timestamp label */
QLabel#bubbleTimeV2 {
    color: #44445A; font-size: 9px;
    font-family: 'Segoe UI'; background-color: transparent;
}

/* ── Reaction buttons ───────────────────── */
QPushButton#reactionBtnV2 {
    background-color: transparent; color: #44445A;
    border: none; border-radius: 6px; font-size: 13px;
}
QPushButton#reactionBtnV2:hover {
    background-color: #18172A;
}
QPushButton#reactionBtnActiveV2 {
    background-color: transparent;
    border: none; border-radius: 6px; font-size: 13px;
}
QPushButton#reactionBtnDislikeV2 {
    background-color: transparent;
    border: none; border-radius: 6px; font-size: 13px;
}

/* ── Input bar ──────────────────────────── */
QWidget#chatInputBarV2 {
    background-color: #0D0D14; border-top: 1px solid #1A1A2E;
}
QFrame#modernInputPillV2 {
    background-color: #13131F;
    border: 1.5px solid #28283D;
    border-radius: 22px;
}
QTextEdit#chatInputV2 {
    background-color: transparent; color: #E8E8FA; border: none;
    font-size: 15px; font-weight: 400; font-family: 'Segoe UI';
    selection-background-color: #7C6EF5;
}
QPushButton#btnSendV2 {
    background-color: #7C3AED;
    color: white; border: none; border-radius: 25px;
    font-size: 18px; font-weight: 600; font-family: 'Segoe UI';
}
QPushButton#btnSendV2:hover {
    background-color: #8B5CF6;
}
QPushButton#btnSendV2:pressed { background-color: #3730A3; }
QPushButton#btnSendV2:disabled { background-color: #18182E; color: #33334A; }
QLabel#inputHintV2 {
    color: #252540; font-size: 10px;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#modelBadge {
    color: #6B5CE7;
    font-size: 10px;
    font-family: 'Segoe UI';
    background-color: transparent;
}
QPushButton#pillIconBtnV2 {
    background-color: transparent;
    border: none;
    border-radius: 14px;
    padding: 0px;
}
QPushButton#pillIconBtnV2:hover {
    background-color: #1E1C32;
}
QPushButton#pillIconBtnV2:pressed {
    background-color: #2A2448;
}
QPushButton#modelDropdownBtnV2 {
    background-color: transparent;
    color: #9B8BFF;
    border: 0.5px solid #3A3A5A;
    border-radius: 14px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Segoe UI';
}
QPushButton#modelDropdownBtnV2:hover {
    background-color: #1C1A30;
    border-color: #6B6B8A;
    color: #C4B5FD;
}
"""


# ═══════════════════════════════════════════════════════════════
#  DARK ORBIT / BLACK-HOLE SKIN PATCH FOR V2
#  Patch ini hanya menyentuh visual: root, header, welcome, bubbles,
#  input bar, dan micro-interaction. Konfigurasi Groq/API tetap utuh.
# ═══════════════════════════════════════════════════════════════
ALISA_STYLE_PATCH_V2 = """
QWidget#chatRootWidgetV2 {
    background-color: transparent;
    border: none;
}
QWidget#chatHeaderV2 {
    background: transparent;
    border: none;
}
QLabel#chatHeaderNameV2 {
    color: #F8FAFC;
    font-size: 14px;
    font-weight: 850;
    letter-spacing: 0.3px;
}
QLabel#chatHeaderStatusV2 {
    color: #34D399;
    font-size: 10px;
    font-weight: 700;
}
QPushButton#btnClearHeaderV2 {
    background-color: rgba(15, 23, 42, 150);
    color: #CBD5E1;
    border: 1px solid rgba(148, 163, 184, 45);
    border-radius: 14px;
    padding: 0px 12px;
    font-size: 11px;
    font-weight: 800;
    font-family: 'Segoe UI';
    text-align: center;
}
QPushButton#btnClearHeaderV2:hover {
    background-color: rgba(30, 41, 59, 210);
    color: #FFFFFF;
    border: 1px solid rgba(125, 211, 252, 110);
}
QPushButton#btnClearHeaderV2:pressed {
    background-color: rgba(49, 46, 129, 220);
}

QScrollArea#chatScrollAreaV2 {
    background-color: transparent;
    border: none;
}
QWidget#chatScrollAreaWidgetV2 {
    background-color: transparent;
}

QWidget#chatInputBarV2 {
    background-color: rgba(3, 7, 18, 226);
    border-top: 1px solid rgba(125, 211, 252, 42);
}
QFrame#modernInputPillV2 {
    background-color: rgba(8, 13, 27, 236);
    border: 1.5px solid rgba(148, 163, 184, 50);
    border-radius: 24px;
}
QFrame#modernInputPillV2:hover {
    border: 1.5px solid rgba(125, 211, 252, 120);
    background-color: rgba(10, 17, 32, 242);
}
QTextEdit#chatInputV2, QTextEdit {
    color: #F8FAFC;
    background-color: transparent;
    border: none;
    selection-background-color: #334155;
    selection-color: #FFFFFF;
}
QTextEdit:disabled {
    color: #64748B;
}

QLabel#welcomeTitleV2 {
    color: #FFFFFF;
    font-size: 26px;
    font-weight: 900;
    letter-spacing: 0.2px;
}
QLabel#welcomeSubV2 {
    color: #94A3B8;
    font-size: 12px;
}
QLabel#groqBadge {
    background-color: rgba(15, 23, 42, 178);
    color: #BAE6FD;
    border: 1px solid rgba(125, 211, 252, 75);
    border-radius: 12px;
    padding: 5px 15px;
    font-size: 11px;
    font-weight: 800;
    font-family: 'Segoe UI';
}
QFrame#featureCardV2 {
    background-color: rgba(15, 23, 42, 182);
    border: 1px solid rgba(255, 255, 255, 32);
    border-radius: 18px;
}
QFrame#featureCardV2:hover {
    background-color: rgba(23, 37, 84, 210);
    border: 1px solid rgba(125, 211, 252, 120);
}
QLabel#featureCardIconV2  {
    font-size: 23px;
    background-color: transparent;
}
QLabel#featureCardTitleV2 {
    color: #E5E7EB;
    font-size: 12px;
    font-weight: 800;
    font-family: 'Segoe UI';
    background-color: transparent;
}
QLabel#featureCardDescV2  {
    color: #7E8EA8;
    font-size: 10px;
    font-family: 'Segoe UI';
    background-color: transparent;
}

QFrame#bubbleAIV2 {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(17, 24, 39, 242),
        stop:0.52 rgba(10, 15, 28, 242),
        stop:1 rgba(4, 8, 18, 242));
    border: 1px solid rgba(148, 163, 184, 42);
    border-radius: 20px;
    border-top-left-radius: 6px;
}
QFrame#bubbleUserV2 {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1E3A8A,
        stop:0.55 #172554,
        stop:1 #0B1120);
    border: 1px solid rgba(125, 211, 252, 125);
    border-radius: 20px;
    border-top-right-radius: 6px;
}
QLabel#bubbleAITextV2,
QLabel#bubbleUserTextV2 {
    color: #F8FAFC;
    font-size: 15px;
    font-weight: 650;
    font-family: 'Segoe UI';
    background-color: transparent;
}
QLabel#bubbleTimeV2 {
    color: #64748B;
    font-size: 9px;
    font-family: 'Segoe UI';
    background-color: transparent;
}
QLabel#avatarUserV2 {
    background-color: #172554;
    color: white;
    border-radius: 17px;
    font-size: 11px;
    font-weight: 800;
    font-family: 'Segoe UI';
}
QLabel#avatarAIV2 {
    background-color: #020617;
    color: #BAE6FD;
    border-radius: 17px;
    font-size: 14px;
    font-family: 'Segoe UI';
}

QPushButton#reactionBtnV2 {
    background-color: transparent;
    color: #64748B;
    border: none;
    border-radius: 7px;
    font-size: 13px;
}
QPushButton#reactionBtnV2:hover {
    background-color: rgba(30, 41, 59, 175);
}

QPushButton#pillIconBtnV2 {
    background-color: transparent;
    border: none;
    border-radius: 14px;
    padding: 0px;
}
QPushButton#pillIconBtnV2:hover {
    background-color: rgba(30, 41, 59, 170);
}
QPushButton#pillIconBtnV2:pressed {
    background-color: rgba(51, 65, 85, 220);
}
QPushButton#modelDropdownBtnV2 {
    background-color: rgba(15, 23, 42, 150);
    color: #BAE6FD;
    border: 0.5px solid rgba(125, 211, 252, 70);
    border-radius: 14px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 800;
    font-family: 'Segoe UI';
}
QPushButton#modelDropdownBtnV2:hover {
    background-color: rgba(23, 37, 84, 210);
    border: 0.5px solid rgba(125, 211, 252, 135);
    color: #FFFFFF;
}
QPushButton#btnSendV2 {
    background-color: #1D4ED8;
    color: white;
    border: none;
    border-radius: 19px;
    padding: 0px;
    font-size: 18px;
    font-weight: 700;
}
QPushButton#btnSendV2:hover {
    background-color: #2563EB;
}
QPushButton#btnSendV2:pressed {
    background-color: #1E40AF;
}
QPushButton#btnSendV2:disabled {
    background-color: rgba(30, 41, 59, 180);
    color: #475569;
}
QLabel#imagePreviewLabel {
    color: #BAE6FD;
    background-color: rgba(15, 23, 42, 175);
    border: 1px solid rgba(125, 211, 252, 82);
    border-radius: 8px;
    padding: 5px 10px;
    font-size: 10px;
    font-family: 'Segoe UI';
}
QLabel#inputHintV2 {
    color: #334155;
    font-size: 10px;
    font-family: 'Segoe UI';
    background-color: transparent;
}
"""


# ═══════════════════════════════════════════════════════════════
#  LUXURY HEADER + CONNECTED CHAT BUBBLE PATCH FOR V2
#  Visual-only patch. API/model/request flow tetap milik V2.
# ═══════════════════════════════════════════════════════════════
LUX_CHAT_STYLE_PATCH_V2 = """
QFrame#headerGlassCardV2 {
    background-color: transparent;
    border: none;
}
QLabel#headerTitleV2 {
    color: #F8FAFC;
    font-size: 15px;
    font-weight: 900;
    letter-spacing: 0.4px;
    font-family: 'Segoe UI';
    background-color: transparent;
}
QLabel#headerSubtitleV2 {
    color: #7E8EA8;
    font-size: 10px;
    font-weight: 650;
    font-family: 'Segoe UI';
    background-color: transparent;
}
QLabel#statusPillV2 {
    color: #A7F3D0;
    background-color: rgba(6, 78, 59, 132);
    border: 1px solid rgba(52, 211, 153, 96);
    border-radius: 10px;
    padding: 3px 9px;
    font-size: 10px;
    font-weight: 850;
    font-family: 'Segoe UI';
}
QLabel#headerModelChipV2 {
    color: #BFDBFE;
    background-color: rgba(15, 23, 42, 145);
    border: 1px solid rgba(96, 165, 250, 58);
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 800;
    font-family: 'Segoe UI';
}
QLabel#headerTinyHintV2 {
    color: #64748B;
    background-color: transparent;
    font-size: 9px;
    font-family: 'Segoe UI';
}
QPushButton#btnClearHeaderV2 {
    background-color: rgba(15, 23, 42, 155);
    color: #CBD5E1;
    border: 1px solid rgba(148, 163, 184, 48);
    border-radius: 16px;
    padding: 0px 14px;
    font-size: 11px;
    font-weight: 850;
    font-family: 'Segoe UI';
}
QPushButton#btnClearHeaderV2:hover {
    background-color: rgba(30, 41, 59, 220);
    color: #F8FAFC;
    border: 1px solid rgba(125, 211, 252, 130);
}
QPushButton#btnClearHeaderV2:pressed {
    background-color: rgba(15, 23, 42, 235);
}
QPushButton#headerIconMiniV2 {
    background-color: rgba(15, 23, 42, 130);
    color: #93C5FD;
    border: 1px solid rgba(125, 211, 252, 45);
    border-radius: 16px;
    font-size: 14px;
    font-weight: 800;
    font-family: 'Segoe UI';
}
QPushButton#headerIconMiniV2:hover {
    background-color: rgba(30, 41, 59, 210);
    color: #FFFFFF;
    border: 1px solid rgba(125, 211, 252, 120);
}

QLabel#bubbleMetaV2 {
    color: #93A4BD;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: 0.55px;
    font-family: 'Segoe UI';
    background-color: transparent;
}
QLabel#bubbleAITextV2, QLabel#bubbleUserTextV2 {
    color: #F8FAFC;
    font-size: 14px;
    font-weight: 600;
    line-height: 1.32;
    font-family: 'Segoe UI';
    background-color: transparent;
}
QFrame#bubbleUserV2, QFrame#bubbleAIV2 {
    background-color: transparent;
    border: none;
}
QLabel#avatarUserV2, QLabel#avatarAIV2 {
    background-color: transparent;
    border: none;
}

QWidget#chatInputBarV2 {
    background-color: rgba(2, 6, 23, 222);
    border-top: 1px solid rgba(148, 163, 184, 34);
}
QFrame#modernInputPillV2 {
    background-color: rgba(7, 12, 25, 238);
    border: 1.5px solid rgba(148, 163, 184, 54);
    border-radius: 28px;
}
QFrame#modernInputPillV2:hover {
    background-color: rgba(10, 17, 32, 246);
    border: 1.5px solid rgba(125, 211, 252, 118);
}
QTextEdit#chatInputV2 {
    color: #F8FAFC;
    background-color: transparent;
    border: none;
    padding: 4px 6px;
    font-size: 14px;
    font-weight: 520;
    font-family: 'Segoe UI';
    selection-background-color: #1D4ED8;
}
QPushButton#modelDropdownBtnV2 {
    background-color: rgba(15, 23, 42, 156);
    color: #BFDBFE;
    border: 0.5px solid rgba(125, 211, 252, 66);
    border-radius: 15px;
    padding: 5px 11px;
    font-size: 11px;
    font-weight: 850;
}
QPushButton#pillIconBtnV2 {
    background-color: rgba(15, 23, 42, 72);
    border: 1px solid rgba(148, 163, 184, 24);
    border-radius: 16px;
}
QPushButton#pillIconBtnV2:hover {
    background-color: rgba(30, 41, 59, 190);
    border: 1px solid rgba(125, 211, 252, 84);
}
QLabel#inputHintV2 {
    color: #475569;
    font-size: 10px;
    font-family: 'Segoe UI';
    background-color: transparent;
}
"""

# ─────────────────────────────────────────────
EMOJI_LIST = [
    "👍", "❤️", "😂", "🔥", "😮", "👏",
    "🎉", "💯", "🤔", "😢", "⭐", "🙏",
    "💪", "🚀", "✨", "💡", "🎯", "⚡"
]


# ─────────────────────────────────────────────
#  GROQ API THREAD
# ─────────────────────────────────────────────
class GroqRequestThread(QThread):
    response_received = pyqtSignal(str)
    error_occurred    = pyqtSignal(str)

    def __init__(self, message, conversation_history=None):
        super().__init__()
        self.message = message
        # conversation_history: list of {"role": "user"/"assistant", "content": "..."}
        self.history = conversation_history or []
        self._colors = [
            '\033[95m', '\033[94m', '\033[96m', '\033[92m',
            '\033[93m', '\033[91m', '\033[35m', '\033[36m',
        ]
        self._reset = '\033[0m'

    def _color(self):
        return random.choice(self._colors)

    def run(self):
        try:
            # Build messages array: history + current
            messages = list(self.history)
            messages.append({"role": "user", "content": self.message})

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": GROQ_MODEL,
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7,
            }

            c = self._color()
            logger.info(f"{c}[Groq v2] Sending → model={GROQ_MODEL}{self._reset}")

            resp = requests.post(
                GROQ_API_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=30,
            )

            if resp.status_code == 200:
                data   = resp.json()
                answer = data["choices"][0]["message"]["content"]
                logger.info(
                    f"{c}[Groq v2] ✓ Response: {len(answer)} chars{self._reset}"
                )
                self.response_received.emit(answer)

            elif resp.status_code == 401:
                self.error_occurred.emit("API Key tidak valid — cek GROQ_API_KEY kamu.")
            elif resp.status_code == 429:
                self.error_occurred.emit("Rate limit tercapai — tunggu sebentar lalu coba lagi.")
            else:
                try:
                    err_detail = resp.json().get("error", {}).get("message", "Unknown error")
                except Exception:
                    err_detail = resp.text[:120]
                self.error_occurred.emit(f"Groq API error {resp.status_code}: {err_detail}")

        except requests.exceptions.Timeout:
            self.error_occurred.emit("Request timeout — AI terlalu lama merespons.")
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("Koneksi gagal — periksa internet kamu.")
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")



# ─────────────────────────────────────────────
#  DARK GRADIENT ROOT — no graphics effect
# ─────────────────────────────────────────────
class _AlisaGradientRootV2(QWidget):
    """Dark cinematic root background. Pure QPainter, safe for PyQt widgets."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatRootWidgetV2")
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setAutoFillBackground(False)
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

    def _tick(self):
        self._phase = (self._phase + 0.012) % (math.pi * 2)
        self.update()

    def _safe_render_hints(self, painter):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        if hasattr(QPainter, "HighQualityAntialiasing"):
            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)

    def _draw_glow(self, painter, x, y, radius, color):
        rg = QRadialGradient(QPointF(x, y), radius)
        rg.setColorAt(0.00, color)
        rg.setColorAt(0.48, QColor(color.red(), color.green(), color.blue(), max(10, color.alpha() // 3)))
        rg.setColorAt(1.00, QColor(color.red(), color.green(), color.blue(), 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(rg))
        painter.drawEllipse(QRectF(x - radius, y - radius, radius * 2, radius * 2))

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return
        try:
            self._safe_render_hints(painter)
            w, h = max(1, self.width()), max(1, self.height())

            bg = QLinearGradient(0, 0, w, h)
            bg.setColorAt(0.00, QColor("#020617"))
            bg.setColorAt(0.28, QColor("#050816"))
            bg.setColorAt(0.58, QColor("#08111F"))
            bg.setColorAt(0.82, QColor("#0F172A"))
            bg.setColorAt(1.00, QColor("#111827"))
            painter.fillRect(self.rect(), bg)

            drift = math.sin(self._phase) * 24
            cross = math.cos(self._phase * 0.76) * 18
            self._draw_glow(painter, w * 0.78 + drift, h * 0.08 + cross, min(w, h) * 0.44, QColor(37, 99, 235, 82))
            self._draw_glow(painter, w * 0.20 - drift * 0.7, h * 0.88, min(w, h) * 0.46, QColor(14, 165, 233, 58))
            self._draw_glow(painter, w * 0.52, h * 0.44 + drift * 0.25, min(w, h) * 0.34, QColor(99, 102, 241, 34))
            self._draw_glow(painter, w * 0.92, h * 0.78, min(w, h) * 0.30, QColor(15, 23, 42, 125))

            # subtle star field / dust, deterministic so it doesn't flicker harshly
            painter.setPen(Qt.NoPen)
            for i in range(86):
                ax = (i * 97.31 + self._phase * 14) % w
                ay = (i * 53.17 + math.sin(self._phase + i) * 2.5) % h
                alpha = 12 + (i % 7) * 5
                size = 0.75 + (i % 4) * 0.24
                painter.setBrush(QColor(191, 219, 254, alpha))
                painter.drawEllipse(QRectF(ax, ay, size, size))

            # vignette keeps the UI professional instead of neon/noisy
            vignette = QRadialGradient(QPointF(w * 0.50, h * 0.45), max(w, h) * 0.78)
            vignette.setColorAt(0.00, QColor(0, 0, 0, 0))
            vignette.setColorAt(0.72, QColor(0, 0, 0, 62))
            vignette.setColorAt(1.00, QColor(0, 0, 0, 178))
            painter.fillRect(self.rect(), QBrush(vignette))
        finally:
            painter.end()


class BlackHoleOrbV2(QWidget):
    """Realistic-ish animated black-hole orb with tilted orbit lines and moving mini planets."""
    def __init__(self, size=260, parent=None):
        super().__init__(parent)
        self._size = size
        self._phase = 0.0
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

    def _tick(self):
        self._phase = (self._phase + 1.55) % 360
        self.update()

    def _safe_render_hints(self, painter):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        if hasattr(QPainter, "HighQualityAntialiasing"):
            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)

    def _draw_planet(self, painter, cx, cy, orbit_rx, orbit_ry, angle_deg, radius, color, front=True):
        ang = math.radians(angle_deg)
        x = cx + math.cos(ang) * orbit_rx
        y = cy + math.sin(ang) * orbit_ry
        depth = 0.55 + 0.45 * ((math.sin(ang) + 1.0) / 2.0)
        pr = radius * depth

        # small orbital shadow/glow
        glow = QRadialGradient(QPointF(x, y), pr * 4.0)
        glow.setColorAt(0.0, QColor(color.red(), color.green(), color.blue(), 75 if front else 38))
        glow.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QRectF(x - pr * 4.0, y - pr * 4.0, pr * 8.0, pr * 8.0))

        body = QRadialGradient(QPointF(x - pr * 0.35, y - pr * 0.45), pr * 1.55)
        body.setColorAt(0.00, QColor(255, 255, 255, 205 if front else 115))
        body.setColorAt(0.25, color)
        body.setColorAt(1.00, QColor(max(0, color.red() - 70), max(0, color.green() - 70), max(0, color.blue() - 70), 230 if front else 140))
        painter.setBrush(QBrush(body))
        painter.setPen(QPen(QColor(226, 232, 240, 75 if front else 32), 0.7))
        painter.drawEllipse(QRectF(x - pr, y - pr, pr * 2, pr * 2))

        # tiny motion tail, gives orbit movement without looking childish
        tail = QPainterPath()
        tail.moveTo(x, y)
        tail.lineTo(x - math.cos(ang) * pr * 5, y - math.sin(ang) * pr * 2.5)
        painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 55 if front else 25), max(0.6, pr * 0.38), Qt.SolidLine, Qt.RoundCap))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(tail)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return
        try:
            self._safe_render_hints(painter)
            s = min(self.width(), self.height())
            cx, cy = self.width() / 2, self.height() / 2
            r = s * 0.285

            # deep spatial aura
            for idx, alpha in enumerate([86, 58, 34, 18]):
                radius = r + 26 + idx * 22
                aura = QRadialGradient(QPointF(cx, cy), radius)
                aura.setColorAt(0.00, QColor(37, 99, 235, alpha))
                aura.setColorAt(0.34, QColor(14, 165, 233, max(0, alpha - 22)))
                aura.setColorAt(0.68, QColor(79, 70, 229, max(0, alpha - 35)))
                aura.setColorAt(1.00, QColor(0, 0, 0, 0))
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(aura))
                painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

            orbit_pen = QPen(QColor(148, 163, 184, 38), 1.05, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            orbit_pen.setCosmetic(True)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(orbit_pen)
            for off, alpha in [(0, 38), (18, 24), (-15, 18)]:
                orbit_pen.setColor(QColor(148, 163, 184, alpha))
                painter.setPen(orbit_pen)
                painter.drawEllipse(QRectF(cx - r * 1.48 - off, cy - r * 0.56, r * 2.96 + off * 2, r * 1.12))

            # planets behind the disk
            self._draw_planet(painter, cx, cy, r * 1.45, r * 0.53, self._phase * 0.80 + 215, 4.7, QColor("#38BDF8"), front=False)
            self._draw_planet(painter, cx, cy, r * 1.72, r * 0.64, -self._phase * 0.58 + 188, 3.6, QColor("#A7F3D0"), front=False)

            # accretion disk
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(self._phase)

            disk = QConicalGradient(QPointF(0, 0), -28)
            disk.setColorAt(0.00, QColor("#FBBF24"))
            disk.setColorAt(0.11, QColor("#F97316"))
            disk.setColorAt(0.25, QColor("#38BDF8"))
            disk.setColorAt(0.43, QColor("#2563EB"))
            disk.setColorAt(0.58, QColor("#7DD3FC"))
            disk.setColorAt(0.74, QColor("#312E81"))
            disk.setColorAt(0.88, QColor("#0EA5E9"))
            disk.setColorAt(1.00, QColor("#FBBF24"))

            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QBrush(disk), 11.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawEllipse(QRectF(-r, -r * 0.78, r * 2, r * 1.56))

            painter.setPen(QPen(QColor(226, 232, 240, 72), 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawArc(QRectF(-r - 3, -r * 0.78 - 3, (r + 3) * 2, (r * 0.78 + 3) * 2), 42 * 16, 112 * 16)

            # front-side relativistic shadow cuts the ring, improves depth
            painter.setPen(QPen(QColor(2, 6, 23, 235), 16, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawArc(QRectF(-r - 2, -r * 0.78 - 2, (r + 2) * 2, (r * 0.78 + 2) * 2), 205 * 16, 50 * 16)
            painter.restore()

            # lens streaks / particles inside the disk
            painter.setPen(Qt.NoPen)
            for i in range(72):
                ang = math.radians(i * 137.5 + self._phase * 0.45)
                rr = (0.18 + (i % 17) / 17) * r * 0.78
                x = cx + math.cos(ang) * rr
                y = cy + math.sin(ang) * rr * 0.56
                alpha = 16 + (i % 6) * 6
                painter.setBrush(QColor(186, 230, 253, alpha))
                painter.drawEllipse(QRectF(x, y, 1.2, 1.2))

            # event horizon
            inner_r = r - 10
            core = QRadialGradient(QPointF(cx - 8, cy - 10), inner_r * 1.40)
            core.setColorAt(0.00, QColor(15, 23, 42, 248))
            core.setColorAt(0.58, QColor(2, 6, 23, 253))
            core.setColorAt(1.00, QColor(0, 0, 0, 255))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(core))
            painter.drawEllipse(QRectF(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2))

            horizon = QRadialGradient(QPointF(cx, cy), inner_r * 1.04)
            horizon.setColorAt(0.0, QColor(0, 0, 0, 0))
            horizon.setColorAt(0.78, QColor(0, 0, 0, 0))
            horizon.setColorAt(1.0, QColor(125, 211, 252, 36))
            painter.setBrush(QBrush(horizon))
            painter.drawEllipse(QRectF(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2))

            # planets in front
            self._draw_planet(painter, cx, cy, r * 1.48, r * 0.53, self._phase * 0.80 + 35, 4.7, QColor("#38BDF8"), front=True)
            self._draw_planet(painter, cx, cy, r * 1.72, r * 0.64, -self._phase * 0.58 + 12, 3.6, QColor("#A7F3D0"), front=True)
            self._draw_planet(painter, cx, cy, r * 1.23, r * 0.44, self._phase * 1.18 + 318, 3.1, QColor("#FBBF24"), front=True)

            # soft glass highlight
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(255, 255, 255, 24), 1.1))
            painter.drawEllipse(QRectF(cx - inner_r + 3, cy - inner_r + 3, (inner_r - 3) * 2, (inner_r - 3) * 2))
        finally:
            painter.end()


class PromptCardV2(QFrame):
    """Clickable welcome prompt card, kept visual-only and scoped to V2."""
    clicked = pyqtSignal(str)

    def __init__(self, icon, title, desc, prompt, parent=None):
        super().__init__(parent)
        self.prompt = prompt
        self.setObjectName("featureCardV2")
        self.setFixedSize(164, 96)
        self.setCursor(Qt.PointingHandCursor)
        self._setup(icon, title, desc)

    def _setup(self, icon, title, desc):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(5)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(4)

        ico = QLabel(icon)
        ico.setObjectName("featureCardIconV2")
        ico.setFixedHeight(26)
        top.addWidget(ico)
        top.addStretch()

        pulse = QLabel("●")
        pulse.setStyleSheet("color:#38BDF8; background:transparent; font-size:12px; font-weight:900;")
        top.addWidget(pulse)
        lay.addLayout(top)

        ttl = QLabel(title)
        ttl.setObjectName("featureCardTitleV2")
        ttl.setWordWrap(True)
        lay.addWidget(ttl)

        dsc = QLabel(desc)
        dsc.setObjectName("featureCardDescV2")
        dsc.setWordWrap(True)
        lay.addWidget(dsc)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.prompt)
            event.accept()
            return
        super().mouseReleaseEvent(event)


# ─────────────────────────────────────────────
#  TYPING INDICATOR  (identik dengan v1)
# ─────────────────────────────────────────────
class TypingIndicatorV2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(68, 40)
        self._phase = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(320)

    def _tick(self):
        self._phase = (self._phase + 1) % 3
        self.update()

    def stop(self):
        self._timer.stop()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#0F172A"))
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        p.drawPath(path)
        p.setPen(QPen(QColor(125, 211, 252, 58), 1))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)
        p.setPen(Qt.NoPen)
        dot_r   = 5
        spacing = 17
        sx      = (self.width() - spacing * 2 - dot_r * 2) // 2
        cy      = self.height() // 2
        for i in range(3):
            dy    = -4 if i == self._phase else 0
            color = QColor("#7DD3FC") if i == self._phase else QColor("#334155")
            p.setBrush(color)
            p.drawEllipse(sx + i * spacing, cy - dot_r + dy, dot_r * 2, dot_r * 2)
        p.end()


# ─────────────────────────────────────────────
#  EMOJI PICKER POPUP
# ─────────────────────────────────────────────
class EmojiPickerPopupV2(QFrame):
    emoji_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

        grid = QHBoxLayout(self)
        grid.setContentsMargins(10, 8, 10, 8)
        grid.setSpacing(0)

        cols_per_row = 6
        rows = [QHBoxLayout() for _ in range(3)]
        for r in rows:
            r.setSpacing(2)

        for idx, emoji in enumerate(EMOJI_LIST):
            btn = QPushButton()
            btn.setFixedSize(40, 38)
            # Use multiple fallback fonts for emoji support
            font = QFont()
            font.setFamily("Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji, Segoe UI Symbol")
            font.setPointSize(16)
            btn.setFont(font)
            btn.setText(emoji)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { background-color: transparent; border: none; border-radius: 8px; }
                QPushButton:hover { background-color: #1E3A8A; }
            """)
            btn.clicked.connect(lambda _, e=emoji: self._pick(e))
            rows[idx // cols_per_row].addWidget(btn)

        vlay = QVBoxLayout()
        vlay.setSpacing(2)
        for r in rows:
            vlay.addLayout(r)
        grid.addLayout(vlay)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor("#0F172A"))
        p.setPen(QPen(QColor(125, 211, 252, 58), 1))
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 14, 14)
        p.drawPath(path)
        p.end()

    def _pick(self, emoji):
        self.emoji_selected.emit(emoji)
        self.close()


# ─────────────────────────────────────────────
#  REACTION BAR
# ─────────────────────────────────────────────
class ReactionBarV2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._liked    = False
        self._disliked = False
        self._loved    = False
        self._reactions = {}
        self.setStyleSheet("background-color: transparent;")
        self._setup()

    def _setup(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(2)

        self.btn_like    = self._mk_svg("thumbs-up.svg", "Like")
        self.btn_dislike = self._mk_svg("thumbs-down.svg", "Dislike")
        self.btn_love    = self._mk_svg("love.svg", "Love")
        self.btn_emoji   = self._mk_svg("smile-plus.svg", "Add Reaction")

        self.btn_like.clicked.connect(self._on_like)
        self.btn_dislike.clicked.connect(self._on_dislike)
        self.btn_love.clicked.connect(self._on_love)
        self.btn_emoji.clicked.connect(self._show_picker)

        lay.addWidget(self.btn_like)
        lay.addWidget(self.btn_dislike)
        lay.addWidget(self.btn_love)
        lay.addWidget(self.btn_emoji)

        self.chips_w = QWidget()
        self.chips_w.setStyleSheet("background-color: transparent;")
        self.chips_l = QHBoxLayout(self.chips_w)
        self.chips_l.setContentsMargins(4, 0, 0, 0)
        self.chips_l.setSpacing(4)
        lay.addWidget(self.chips_w)
        lay.addStretch()

    def _mk_svg(self, svg_file, tooltip):
        """Create button with SVG icon using the same system as sidebar"""
        import os
        from app.helpers import _svg_icon, resource_path
        from PyQt5.QtCore import QSize
        
        btn = QPushButton()
        btn.setObjectName("reactionBtnV2")
        btn.setToolTip(tooltip)
        btn.setFixedSize(32, 28)
        btn.setCursor(Qt.PointingHandCursor)
        
        # Load SVG icon with default color
        icon = _svg_icon(resource_path("icons", "svg", svg_file), "#6B7280", 16)
        if not icon.isNull():
            btn.setIcon(icon)
            btn.setIconSize(QSize(16, 16))
        
        return btn

    def _repaint(self, btn):
        btn.style().unpolish(btn)
        btn.style().polish(btn)
    
    def _update_icon_color(self, btn, svg_file, color, filled=False):
        """Update button icon color and style (outline or filled)"""
        from app.helpers import _svg_icon, resource_path
        from PyQt5.QtCore import QSize
        
        # Use filled version if active
        if filled:
            svg_file = svg_file.replace('.svg', '-filled.svg')
        
        icon = _svg_icon(resource_path("icons", "svg", svg_file), color, 16)
        if not icon.isNull():
            btn.setIcon(icon)
            btn.setIconSize(QSize(16, 16))

    def _on_like(self):
        self._liked = not self._liked
        if self._liked:
            self._disliked = False
            # Reset dislike to outline grey
            self._update_icon_color(self.btn_dislike, "thumbs-down.svg", "#6B7280", filled=False)
            # Set like to filled purple
            self._update_icon_color(self.btn_like, "thumbs-up.svg", "#A78BFA", filled=True)
        else:
            # Reset like to outline grey
            self._update_icon_color(self.btn_like, "thumbs-up.svg", "#6B7280", filled=False)

    def _on_dislike(self):
        self._disliked = not self._disliked
        if self._disliked:
            self._liked = False
            # Reset like to outline grey
            self._update_icon_color(self.btn_like, "thumbs-up.svg", "#6B7280", filled=False)
            # Set dislike to filled red
            self._update_icon_color(self.btn_dislike, "thumbs-down.svg", "#F87171", filled=True)
        else:
            # Reset dislike to outline grey
            self._update_icon_color(self.btn_dislike, "thumbs-down.svg", "#6B7280", filled=False)

    def _on_love(self):
        self._loved = not self._loved
        if self._loved:
            # Set love to filled pink
            self._update_icon_color(self.btn_love, "love.svg", "#F472B6", filled=True)
        else:
            # Reset love to outline grey
            self._update_icon_color(self.btn_love, "love.svg", "#6B7280", filled=False)

    def _show_picker(self):
        popup = EmojiPickerPopupV2()
        popup.emoji_selected.connect(self._add_reaction)
        pos = self.btn_emoji.mapToGlobal(self.btn_emoji.rect().topLeft())
        popup.adjustSize()
        popup.move(pos.x(), pos.y() - popup.height() - 6)
        popup.show()

    def _add_reaction(self, emoji):
        self._reactions[emoji] = self._reactions.get(emoji, 0) + 1
        self._refresh_chips()

    def _refresh_chips(self):
        while self.chips_l.count():
            item = self.chips_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for emoji, count in self._reactions.items():
            chip = QPushButton()
            chip.setFixedHeight(24)
            # Use multiple fallback fonts for emoji support
            font = QFont()
            font.setFamily("Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji, Segoe UI Symbol")
            font.setPointSize(10)
            chip.setFont(font)
            chip.setText(f"{emoji} {count}")
            chip.setCursor(Qt.PointingHandCursor)
            chip.setStyleSheet("""
                QPushButton {
                    background-color: rgba(15, 23, 42, 190);
                    color: #BAE6FD;
                    border: 1px solid rgba(125, 211, 252, 70);
                    border-radius: 12px;
                    padding: 0 10px;
                }
                QPushButton:hover {
                    background-color: rgba(23, 37, 84, 210);
                    border: 1px solid rgba(125, 211, 252, 135);
                }
            """)
            chip.clicked.connect(lambda _, e=emoji: self._add_reaction(e))
            self.chips_l.addWidget(chip)


# ═══════════════════════════════════════════════════════════════
#  MINIMAL EXECUTIVE HEADER PATCH FOR V2
#  Clean, static, no orbit animation. Visual-only.
# ═══════════════════════════════════════════════════════════════
MINIMAL_HEADER_STYLE_PATCH_V2 = """
/* ── CLEAN V1-LIKE HEADER: transparent, centered, no status/model/orbit text ── */
QWidget#chatHeaderV2 {
    background-color: transparent;
    border: none;
}
QPushButton#headerIconButtonV2 {
    background-color: transparent;
    color: #CBD5E1;
    border: 1px solid rgba(148, 163, 184, 28);
    border-radius: 18px;
    font-size: 24px;
    font-weight: 700;
    font-family: 'Segoe UI';
    text-align: center;
    padding: 0px;
}
QPushButton#headerIconButtonV2:hover {
    background-color: rgba(15, 23, 42, 126);
    color: #F8FAFC;
    border: 1px solid rgba(148, 163, 184, 48);
}
QPushButton#headerIconButtonV2:pressed {
    background-color: rgba(15, 23, 42, 190);
}
QLabel#headerTitleV2 {
    color: #F8FAFC;
    font-size: 13px;
    font-weight: 760;
    letter-spacing: 0.35px;
    font-family: 'Segoe UI';
    background-color: transparent;
}
QLabel#headerSubtitleV2,
QLabel#statusPillV2,
QLabel#headerModelChipV2,
QLabel#headerTinyHintV2,
QFrame#headerDividerV2 {
    color: transparent;
    background-color: transparent;
    border: none;
}
QPushButton#btnClearHeaderV2 {
    background-color: transparent;
    color: #94A3B8;
    border: 1px solid rgba(148, 163, 184, 28);
    border-radius: 15px;
    padding: 0px 12px;
    font-size: 10px;
    font-weight: 750;
    font-family: 'Segoe UI';
}
QPushButton#btnClearHeaderV2:hover {
    background-color: rgba(15, 23, 42, 128);
    color: #E2E8F0;
    border: 1px solid rgba(148, 163, 184, 54);
}
QPushButton#btnClearHeaderV2:pressed {
    background-color: rgba(15, 23, 42, 205);
    color: #FFFFFF;
}

/* ── Input: no bright stroke on hover/focus ── */
QWidget#chatInputBarV2 {
    background-color: rgba(2, 6, 23, 218);
    border-top: 1px solid rgba(148, 163, 184, 24);
}
QFrame#modernInputPillV2 {
    background-color: rgba(7, 12, 25, 238);
    border: 1px solid rgba(148, 163, 184, 42);
    border-radius: 28px;
}
QFrame#modernInputPillV2:hover {
    background-color: rgba(7, 12, 25, 238);
    border: 1px solid rgba(148, 163, 184, 42);
}
QTextEdit#chatInputV2 {
    color: #F8FAFC;
    background-color: transparent;
    border: none;
    padding: 4px 6px;
    font-size: 14px;
    font-weight: 520;
    font-family: 'Segoe UI';
    selection-background-color: #334155;
    selection-color: #FFFFFF;
}
QPushButton#modelDropdownBtnV2 {
    background-color: rgba(15, 23, 42, 96);
    color: #CBD5E1;
    border: 1px solid rgba(148, 163, 184, 30);
    border-radius: 14px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 720;
    font-family: 'Segoe UI';
}
QPushButton#modelDropdownBtnV2:hover {
    background-color: rgba(15, 23, 42, 132);
    color: #E2E8F0;
    border: 1px solid rgba(148, 163, 184, 46);
}
QPushButton#pillIconBtnV2 {
    background-color: transparent;
    border: none;
    border-radius: 16px;
}
QPushButton#pillIconBtnV2:hover {
    background-color: rgba(15, 23, 42, 126);
    border: none;
}
QPushButton#btnSendV2 {
    background-color: #1E293B;
    color: #E2E8F0;
    border: 1px solid rgba(148, 163, 184, 32);
    border-radius: 19px;
    padding: 0px;
    font-size: 18px;
    font-weight: 700;
}
QPushButton#btnSendV2:hover {
    background-color: #263449;
    border: 1px solid rgba(148, 163, 184, 46);
}
QPushButton#btnSendV2:pressed {
    background-color: #111827;
}
QPushButton#btnSendV2:disabled {
    background-color: rgba(15, 23, 42, 120);
    color: #475569;
    border: 1px solid rgba(148, 163, 184, 18);
}
QLabel#inputHintV2 {
    color: #475569;
    font-size: 10px;
    font-family: 'Segoe UI';
    background-color: transparent;
}
"""


# ─────────────────────────────────────────────
#  PREMIUM HEADER + CONNECTED BUBBLE PAINTERS
# ─────────────────────────────────────────────
class _HeaderGlassCardV2(QFrame):
    """Static executive-glass header shell. No orbit animation, no moving HUD."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("headerGlassCardV2")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        p = QPainter(self)
        if not p.isActive():
            return
        try:
            p.setRenderHint(QPainter.Antialiasing, True)
            p.setRenderHint(QPainter.SmoothPixmapTransform, True)
            if hasattr(QPainter, "HighQualityAntialiasing"):
                p.setRenderHint(QPainter.HighQualityAntialiasing, True)

            rect = QRectF(0.7, 0.7, self.width() - 1.4, self.height() - 1.4)
            radius = 20.0

            # soft depth, not flashy
            p.setPen(Qt.NoPen)
            for i, alpha in enumerate([34, 18]):
                shadow = QRectF(rect.x(), rect.y() + 3 + i * 2, rect.width(), rect.height() - i)
                p.setBrush(QColor(0, 0, 0, alpha))
                p.drawRoundedRect(shadow, radius, radius)

            bg = QLinearGradient(rect.topLeft(), rect.bottomRight())
            bg.setColorAt(0.00, QColor(15, 23, 42, 224))
            bg.setColorAt(0.50, QColor(7, 12, 24, 238))
            bg.setColorAt(1.00, QColor(2, 6, 23, 242))
            p.setBrush(QBrush(bg))
            p.drawRoundedRect(rect, radius, radius)

            # restrained left accent only
            accent = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            accent.setColorAt(0.00, QColor(125, 211, 252, 120))
            accent.setColorAt(0.50, QColor(59, 130, 246, 72))
            accent.setColorAt(1.00, QColor(14, 165, 233, 18))
            p.setBrush(QBrush(accent))
            p.drawRoundedRect(QRectF(rect.x(), rect.y() + 8, 3.0, rect.height() - 16), 1.5, 1.5)

            # subtle top highlight for premium glass look
            top_line = QLinearGradient(rect.topLeft(), rect.topRight())
            top_line.setColorAt(0.00, QColor(255, 255, 255, 22))
            top_line.setColorAt(0.45, QColor(125, 211, 252, 52))
            top_line.setColorAt(1.00, QColor(255, 255, 255, 12))
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QBrush(top_line), 1.0))
            p.drawRoundedRect(rect.adjusted(0.2, 0.2, -0.2, -0.2), radius, radius)

            # low contrast outer border
            p.setPen(QPen(QColor(148, 163, 184, 36), 1.0))
            p.drawRoundedRect(rect, radius, radius)
        finally:
            p.end()


class _MessageBubbleFrameV2(QFrame):
    """Dark connected chat bubble inspired by avatar-attached chat UI samples."""
    def __init__(self, is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.setObjectName("bubbleUserV2" if is_user else "bubbleAIV2")

    def paintEvent(self, event):
        p = QPainter(self)
        if not p.isActive():
            return
        try:
            p.setRenderHint(QPainter.Antialiasing, True)
            p.setRenderHint(QPainter.SmoothPixmapTransform, True)
            if hasattr(QPainter, "HighQualityAntialiasing"):
                p.setRenderHint(QPainter.HighQualityAntialiasing, True)

            w, h = self.width(), self.height()
            tail = 18.0
            pad = 2.0
            radius = 25.0
            if self.is_user:
                body = QRectF(pad, pad, w - tail - pad * 2, h - pad * 2)
                connector = QRectF(w - tail - 16, h * 0.5 - 18, 34, 36)
                shadow_connector = QRectF(connector.x() + 1, connector.y() + 4, connector.width(), connector.height())
                g_start, g_end = body.topLeft(), body.bottomRight()
                c0, c1, c2 = QColor(30, 58, 138, 242), QColor(15, 23, 42, 246), QColor(3, 7, 18, 248)
                border0, border1 = QColor(125, 211, 252, 128), QColor(59, 130, 246, 55)
            else:
                body = QRectF(tail + pad, pad, w - tail - pad * 2, h - pad * 2)
                connector = QRectF(-1, h * 0.5 - 18, 34, 36)
                shadow_connector = QRectF(connector.x() + 1, connector.y() + 4, connector.width(), connector.height())
                g_start, g_end = body.topLeft(), body.bottomRight()
                c0, c1, c2 = QColor(24, 31, 43, 244), QColor(10, 15, 26, 248), QColor(2, 6, 23, 250)
                border0, border1 = QColor(148, 163, 184, 70), QColor(125, 211, 252, 36)

            # contained soft shadow
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(0, 0, 0, 62))
            p.drawRoundedRect(QRectF(body.x() + 1.5, body.y() + 4.0, body.width(), body.height()), radius, radius)
            p.drawEllipse(shadow_connector)

            grad = QLinearGradient(g_start, g_end)
            grad.setColorAt(0.00, c0)
            grad.setColorAt(0.56, c1)
            grad.setColorAt(1.00, c2)
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(body, radius, radius)
            p.drawEllipse(connector)

            # glossy top edge, not white bubble; only very thin highlight
            shine = QLinearGradient(body.topLeft(), body.topRight())
            shine.setColorAt(0.0, QColor(255, 255, 255, 22))
            shine.setColorAt(0.5, QColor(125, 211, 252, 36))
            shine.setColorAt(1.0, QColor(255, 255, 255, 12))
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QBrush(shine), 1.0))
            top = QRectF(body.x() + 1.0, body.y() + 1.0, body.width() - 2.0, body.height() - 2.0)
            p.drawRoundedRect(top, radius, radius)

            border = QLinearGradient(body.topLeft(), body.bottomRight())
            border.setColorAt(0.0, border0)
            border.setColorAt(1.0, border1)
            p.setPen(QPen(QBrush(border), 1.15))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(body, radius, radius)
            p.drawEllipse(connector)
        finally:
            p.end()


# ─────────────────────────────────────────────
#  CHAT BUBBLE
# ─────────────────────────────────────────────
class ChatBubbleV2(QWidget):
    def __init__(self, message, is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.message = message
        self.setStyleSheet("background-color: transparent;")
        self._setup()

    def _setup(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(5)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        if self.is_user:
            row.addStretch(1)
            row.addWidget(self._bubble(), 0, Qt.AlignTop)
            row.addWidget(self._avatar(user=True), 0, Qt.AlignTop)
        else:
            row.addWidget(self._avatar(user=False), 0, Qt.AlignTop)
            row.addWidget(self._bubble(), 0, Qt.AlignTop)
            row.addStretch(1)

        outer.addLayout(row)

        if not self.is_user:
            rrow = QHBoxLayout()
            rrow.setContentsMargins(62, 0, 0, 0)
            rrow.addWidget(ReactionBarV2())
            rrow.addStretch()
            outer.addLayout(rrow)

    def _avatar(self, user=True):
        av = QLabel()
        outer_size = 52
        inner_size = 43
        av.setFixedSize(outer_size, outer_size)
        av.setAlignment(Qt.AlignCenter)

        USER_AVATAR_FILE = "profile_user_input.jpeg"
        AI_AVATAR_FILE   = "sfx.jpeg"
        avatar_path = image_resource(USER_AVATAR_FILE if user else AI_AVATAR_FILE)
        pixmap = QPixmap(avatar_path)

        result = QPixmap(outer_size, outer_size)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        if hasattr(QPainter, "HighQualityAntialiasing"):
            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)

        # halo ring makes avatar feel physically attached to the bubble
        center = QPointF(outer_size / 2, outer_size / 2)
        halo = QRadialGradient(center, outer_size / 2)
        if user:
            halo.setColorAt(0.00, QColor(56, 189, 248, 80))
            halo.setColorAt(0.62, QColor(37, 99, 235, 42))
        else:
            halo.setColorAt(0.00, QColor(148, 163, 184, 72))
            halo.setColorAt(0.62, QColor(15, 23, 42, 48))
        halo.setColorAt(1.00, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(halo))
        painter.drawEllipse(QRectF(0, 0, outer_size, outer_size))

        ix = (outer_size - inner_size) / 2
        iy = (outer_size - inner_size) / 2
        border_color = QColor("#7DD3FC") if user else QColor("#CBD5E1")
        painter.setPen(QPen(border_color, 2.4))
        painter.setBrush(QColor(2, 6, 23, 230))
        painter.drawEllipse(QRectF(ix, iy, inner_size, inner_size))

        if not pixmap.isNull():
            scaled = pixmap.scaled(inner_size, inner_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = max(0, (scaled.width() - inner_size) // 2)
            y = max(0, (scaled.height() - inner_size) // 2)
            cropped = scaled.copy(x, y, inner_size, inner_size)
            path_circle = QPainterPath()
            path_circle.addEllipse(QRectF(ix + 2, iy + 2, inner_size - 4, inner_size - 4))
            painter.setClipPath(path_circle)
            painter.drawPixmap(int(ix + 2), int(iy + 2), inner_size - 4, inner_size - 4, cropped)
        else:
            painter.setPen(QColor("#BAE6FD" if not user else "#FFFFFF"))
            painter.setFont(QFont("Segoe UI", 15 if not user else 12, QFont.Bold))
            painter.drawText(QRectF(ix, iy, inner_size, inner_size), Qt.AlignCenter, "✦" if not user else "U")

        painter.end()
        av.setPixmap(result)
        return av

    def _bubble(self):
        f = _MessageBubbleFrameV2(is_user=self.is_user)
        f.setMaximumWidth(560)
        f.setMinimumWidth(170)
        lay = QVBoxLayout(f)
        if self.is_user:
            lay.setContentsMargins(18, 12, 34, 13)
        else:
            lay.setContentsMargins(34, 12, 18, 13)
        lay.setSpacing(4)

        meta = QLabel(("YOU" if self.is_user else "GROQ") + "  " + datetime.now().strftime("%H:%M"))
        meta.setObjectName("bubbleMetaV2")
        meta.setAlignment(Qt.AlignLeft)
        lay.addWidget(meta)

        lbl = QLabel(self.message)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl.setObjectName("bubbleUserTextV2" if self.is_user else "bubbleAITextV2")
        lbl.setFont(QFont("Segoe UI", 14, QFont.DemiBold))
        lay.addWidget(lbl)
        return f


# ─────────────────────────────────────────────
#  SEND BUTTON  (SVG icon from ai_bar folder)
# ─────────────────────────────────────────────
class _SendButtonV2(QPushButton):
    """Send button V2 — icon di-render manual via paintEvent, 100% center."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("btnSendV2")
        self.setFixedSize(38, 38)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Send message (Ctrl+Enter)")
        self._bg_normal   = QColor("#0F4C81")
        self._bg_hover    = QColor("#2563EB")
        self._bg_pressed  = QColor("#0B2A4A")
        self._bg_disabled = QColor(30, 41, 59, 180)
        self._hovered     = False
        self._pressed     = False

    def enterEvent(self, e):  self._hovered = True;  self.update()
    def leaveEvent(self, e):  self._hovered = False; self.update()
    def mousePressEvent(self, e):
        self._pressed = True;  self.update(); super().mousePressEvent(e)
    def mouseReleaseEvent(self, e):
        self._pressed = False; self.update(); super().mouseReleaseEvent(e)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        r = self.rect()
        if not self.isEnabled():
            bg = self._bg_disabled
        elif self._pressed:
            bg = self._bg_pressed
        elif self._hovered:
            bg = self._bg_hover
        else:
            bg = self._bg_normal
        p.setPen(Qt.NoPen)
        p.setBrush(bg)
        p.drawEllipse(r)
        icon = self.icon()
        if not icon.isNull():
            sz = self.iconSize()
            x  = (r.width()  - sz.width())  // 2
            y  = (r.height() - sz.height()) // 2
            from PyQt5.QtCore import QRect as _QRect
            icon.paint(p, _QRect(x, y, sz.width(), sz.height()))
        p.end()


# ─────────────────────────────────────────────
#  ATTACH ICON  (identik v1)
# ─────────────────────────────────────────────
class _AttachIconV2(QWidget):
    clicked_sig = pyqtSignal()

    def __init__(self, size=32, parent=None):
        super().__init__(parent)
        self._sz      = size
        self._hovered = False
        self._active  = False
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Attach image")

    def set_active(self, state: bool):
        self._active = state
        self.update()

    def enterEvent(self, e): self._hovered = True;  self.update()
    def leaveEvent(self, e): self._hovered = False; self.update()
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked_sig.emit()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = self._sz

        if self._active:
            bg, border = QColor(124, 110, 245, 60), QColor("#7C6EF5")
        elif self._hovered:
            bg, border = QColor(124, 110, 245, 40), QColor("#6B5CE7")
        else:
            bg, border = QColor(0, 0, 0, 0), QColor(0, 0, 0, 0)

        p.setBrush(bg)
        p.setPen(QPen(border, 1))
        p.drawRoundedRect(1, 1, s - 2, s - 2, 9, 9)

        icon_color = QColor("#9B8BFF") if (self._active or self._hovered) else QColor("#44445A")
        pen = QPen(icon_color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)

        cx, cy = s / 2, s / 2
        bw, bh = s * 0.42, s * 0.38
        p.drawRoundedRect(int(cx - bw/2 + 2.5), int(cy - bh/2 - 2.5), int(bw), int(bh), 3, 3)

        fw, fh = s * 0.50, s * 0.45
        fx, fy = cx - fw/2 - 1.5, cy - fh/2 + 1.5
        p.drawRoundedRect(int(fx), int(fy), int(fw), int(fh), 4, 4)

        dot_r = s * 0.08
        p.setBrush(QBrush(icon_color))
        p.setPen(Qt.NoPen)
        p.drawEllipse(int(fx + fw*0.28 - dot_r/2), int(fy + fh*0.30 - dot_r/2), int(dot_r), int(dot_r))

        p.setPen(QPen(icon_color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        mp = QPainterPath()
        mp.moveTo(fx + 2, fy + fh - 2)
        mp.lineTo(fx + fw*0.35, fy + fh*0.55)
        mp.lineTo(fx + fw*0.65, fy + fh*0.70)
        mp.lineTo(fx + fw - 2, fy + fh - 2)
        p.drawPath(mp)
        p.end()


# ─────────────────────────────────────────────
#  ROUNDED PHOTO LABEL  (identik v1)
# ─────────────────────────────────────────────
class _RoundPhotoLabelV2(QWidget):
    def __init__(self, path: str, size: int = 110, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size + 8, size + 8)
        self._pixmap = QPixmap()
        raw = QPixmap(path)
        if not raw.isNull():
            scaled = raw.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (scaled.width()  - size) // 2
            y = (scaled.height() - size) // 2
            self._pixmap = scaled.copy(x, y, size, size)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        s, off = self._size, 4
        total  = s + off * 2

        p.setPen(QPen(QColor("#9B8BFF"), 3))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(1, 1, total - 2, total - 2)

        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#0D0D14"))
        p.drawEllipse(3, 3, total - 6, total - 6)

        clip = QPainterPath()
        clip.addEllipse(off, off, s, s)
        p.setClipPath(clip)

        if not self._pixmap.isNull():
            p.drawPixmap(off, off, self._pixmap)
        else:
            fg = QLinearGradient(off, off, off + s, off + s)
            fg.setColorAt(0, QColor("#2D2880"))
            fg.setColorAt(1, QColor("#6B5CE7"))
            p.setBrush(QBrush(fg))
            p.drawEllipse(off, off, s, s)
            p.setPen(QColor("#FFFFFF"))
            p.setFont(QFont("Segoe UI", 30))
            p.drawText(QRect(off, off, s, s), Qt.AlignCenter, "✦")
        p.end()


# ─────────────────────────────────────────────
#  MODEL SELECTOR POPUP  (Modern AI Model Chooser)
# ─────────────────────────────────────────────
AI_MODELS = [
    {
        "id": "llama-3.1-8b-instant",
        "name": "LLaMA 3.1 Instant",
        "provider": "Groq · Meta",
        "badge": "FAST",
        "badge_color": "#4ADE80",
        "badge_bg": "#0D2E1A",
        "desc": "Ultra-low latency, everyday tasks",
        "svg": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke="#4ADE80" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
        "color": "#4ADE80",
    },
    {
        "id": "llama3-70b-8192",
        "name": "LLaMA 3 · 70B",
        "provider": "Groq · Meta",
        "badge": "POWERFUL",
        "badge_color": "#A78BFA",
        "badge_bg": "#1E1040",
        "desc": "Deep reasoning, complex analysis",
        "svg": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="3" stroke="#A78BFA" stroke-width="1.8"/>
  <path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12" stroke="#A78BFA" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",
        "color": "#A78BFA",
    },
    {
        "id": "mixtral-8x7b-32768",
        "name": "Mixtral 8×7B",
        "provider": "Groq · Mistral AI",
        "badge": "LONG CTX",
        "badge_color": "#38BDF8",
        "badge_bg": "#0C2233",
        "desc": "32k context, mixture of experts",
        "svg": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 6h16M4 10h10M4 14h13M4 18h8" stroke="#38BDF8" stroke-width="1.8" stroke-linecap="round"/>
  <circle cx="19" cy="17" r="3" stroke="#38BDF8" stroke-width="1.6"/>
  <path d="M19 15.5v1.5l1 1" stroke="#38BDF8" stroke-width="1.4" stroke-linecap="round"/>
</svg>""",
        "color": "#38BDF8",
    },
    {
        "id": "gemma2-9b-it",
        "name": "Gemma 2 · 9B",
        "provider": "Groq · Google DeepMind",
        "badge": "EFFICIENT",
        "badge_color": "#FBBF24",
        "badge_bg": "#231A00",
        "desc": "Compact, instruction-tuned, Google",
        "svg": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3C7.03 3 3 7.03 3 12s4.03 9 9 9 9-4.03 9-9" stroke="#FBBF24" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M12 8v4l3 3" stroke="#FBBF24" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="18.5" cy="5.5" r="2.5" fill="#FBBF24" opacity="0.3" stroke="#FBBF24" stroke-width="1.4"/>
</svg>""",
        "color": "#FBBF24",
    },
    {
        "id": "deepseek-r1-distill-llama-70b",
        "name": "DeepSeek R1 · 70B",
        "provider": "Groq · DeepSeek",
        "badge": "REASONING",
        "badge_color": "#F472B6",
        "badge_bg": "#2A0D20",
        "desc": "Advanced chain-of-thought reasoning",
        "svg": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" stroke="#F472B6" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
        "color": "#F472B6",
    },
]


class ModelSelectorPopupV2(QFrame):
    model_selected = pyqtSignal(str, str)   # (model_id, model_name)

    def __init__(self, current_model_id: str, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.current_model_id = current_model_id
        self.setFixedWidth(318)
        self._setup()

    def _setup(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        inner = QWidget()
        inner.setObjectName("modelPopupInnerV2")
        inner.setStyleSheet("""
            QWidget#modelPopupInnerV2 {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 17, 28, 248),
                    stop:0.55 rgba(10, 12, 22, 248),
                    stop:1 rgba(5, 8, 15, 248));
                border: 1px solid rgba(148, 163, 184, 42);
                border-radius: 20px;
            }
        """)
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(12, 12, 12, 12)
        inner_lay.setSpacing(7)

        header = QHBoxLayout()
        header.setContentsMargins(4, 0, 4, 5)
        header.setSpacing(8)

        header_lbl = QLabel("AI model")
        header_lbl.setStyleSheet("""
            color: #F8FAFC;
            font-size: 12px;
            font-weight: 850;
            font-family: 'Segoe UI';
            background-color: transparent;
        """)
        header.addWidget(header_lbl)
        header.addStretch()

        hint_lbl = QLabel("tap to switch")
        hint_lbl.setStyleSheet("""
            color: rgba(203, 213, 225, 150);
            font-size: 9px;
            font-weight: 700;
            font-family: 'Segoe UI';
            background-color: transparent;
            border: none;
            padding: 0px;
        """)
        header.addWidget(hint_lbl)
        inner_lay.addLayout(header)

        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: rgba(148, 163, 184, 22); margin: 0px 4px;")
        inner_lay.addWidget(div)
        inner_lay.addSpacing(2)

        for model in AI_MODELS:
            inner_lay.addWidget(self._make_model_btn(model))

        lay.addWidget(inner)

    def _make_model_btn(self, model: dict):
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(54)

        is_active = (model["id"] == self.current_model_id)
        if is_active:
            bg_color = "rgba(59, 130, 246, 52)"
            border_color = "rgba(125, 211, 252, 82)"
            side_alpha = 175
        else:
            bg_color = "rgba(255, 255, 255, 4)"
            border_color = "rgba(148, 163, 184, 22)"
            side_alpha = 0

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 15px;
                text-align: left;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: rgba(15, 23, 42, 210);
                border: 1px solid rgba(125, 211, 252, 72);
            }}
            QPushButton:pressed {{
                background-color: rgba(8, 15, 28, 235);
            }}
        """)

        row = QHBoxLayout(btn)
        row.setContentsMargins(10, 7, 10, 7)
        row.setSpacing(10)

        accent_bar = QFrame()
        accent_bar.setFixedSize(3, 30)
        accent_bar.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(125, 211, 252, {side_alpha});
                border-radius: 2px;
            }}
        """)
        row.addWidget(accent_bar)

        icon_lbl = QLabel("AI")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFixedSize(30, 30)
        icon_lbl.setStyleSheet("""
            QLabel {
                color: #BAE6FD;
                background-color: rgba(15, 23, 42, 165);
                border: 1px solid rgba(125, 211, 252, 44);
                border-radius: 15px;
                font-size: 9px;
                font-weight: 900;
                font-family: 'Segoe UI';
            }
        """)
        row.addWidget(icon_lbl)

        col = QVBoxLayout()
        col.setSpacing(1)
        col.setContentsMargins(0, 0, 0, 0)

        name_row = QHBoxLayout()
        name_row.setSpacing(6)
        name_row.setContentsMargins(0, 0, 0, 0)

        name_lbl = QLabel(model.get("name", "Model"))
        name_lbl.setStyleSheet("""
            color: #F8FAFC;
            font-size: 12px;
            font-weight: 820;
            font-family: 'Segoe UI';
            background-color: transparent;
        """)
        name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        name_row.addWidget(name_lbl, 1)

        badge_lbl = QLabel(model.get("badge", "MODEL"))
        badge_lbl.setStyleSheet("""
            color: rgba(226, 232, 240, 185);
            background-color: rgba(148, 163, 184, 18);
            border: 1px solid rgba(148, 163, 184, 28);
            border-radius: 6px;
            font-size: 8px;
            font-weight: 850;
            font-family: 'Segoe UI';
            padding: 1px 5px;
        """)
        name_row.addWidget(badge_lbl)

        if is_active:
            check = QLabel("✓")
            check.setAlignment(Qt.AlignCenter)
            check.setFixedWidth(12)
            check.setStyleSheet("""
                color: #7DD3FC;
                font-size: 12px;
                font-weight: 900;
                background-color: transparent;
                font-family: 'Segoe UI';
            """)
            name_row.addWidget(check)

        col.addLayout(name_row)

        provider = QLabel(model.get("provider", ""))
        provider.setStyleSheet("""
            color: rgba(203, 213, 225, 170);
            font-size: 10px;
            font-weight: 620;
            font-family: 'Segoe UI';
            background-color: transparent;
        """)
        col.addWidget(provider)

        desc = QLabel(model.get("desc", ""))
        desc.setStyleSheet("""
            color: rgba(148, 163, 184, 150);
            font-size: 9px;
            font-family: 'Segoe UI';
            background-color: transparent;
        """)
        col.addWidget(desc)

        row.addLayout(col, 1)
        btn.clicked.connect(lambda _, m=model: self._on_select(m))
        return btn

    def _on_select(self, model: dict):
        self.model_selected.emit(model["id"], model["name"])
        self.close()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        p.setBrush(Qt.transparent)
        p.drawRect(self.rect())
        p.end()

class _SVGIconLabelV2(QWidget):
    """Renders a simple SVG string using QPainter paths — fallback colored circle."""
    def __init__(self, svg_str: str, size: int = 36, parent=None):
        super().__init__(parent)
        self._size = size
        self._svg = svg_str
        self.setFixedSize(size, size)
        self._pixmap = self._render_svg()

    def _render_svg(self):
        from PyQt5.QtSvg import QSvgRenderer
        from PyQt5.QtCore import QByteArray
        px = QPixmap(self._size, self._size)
        px.fill(Qt.transparent)
        try:
            renderer = QSvgRenderer(QByteArray(self._svg.encode()))
            if renderer.isValid():
                painter = QPainter(px)
                painter.setRenderHint(QPainter.Antialiasing)
                renderer.render(painter)
                painter.end()
        except Exception:
            pass
        return px

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        # Background circle
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#1A1A30"))
        p.drawEllipse(0, 0, self._size, self._size)
        if not self._pixmap.isNull():
            offset = 6
            p.drawPixmap(offset, offset, self._size - offset * 2, self._size - offset * 2, self._pixmap)
        p.end()


# ─────────────────────────────────────────────
#  MAIN CHAT WIDGET V2  (Groq)
# ─────────────────────────────────────────────
class AIChatWidgetV2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image    = None
        self.typing_widget    = None
        self.chat_started     = False
        self._typing_row_w    = None
        self._current_model_id = GROQ_MODEL
        self._model_btn       = None
        self._history: list   = []
        self._setup_ui()

    def _setup_ui(self):
        root = _AlisaGradientRootV2()
        root.setStyleSheet(GLOBAL_STYLE + ALISA_STYLE_PATCH_V2 + LUX_CHAT_STYLE_PATCH_V2 + MINIMAL_HEADER_STYLE_PATCH_V2)

        rl = QVBoxLayout(self)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        rl.addWidget(root)

        il = QVBoxLayout(root)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(0)
        il.addWidget(self._build_header())

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("chatScrollAreaV2")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.viewport().setAutoFillBackground(False)
        self.scroll_area.viewport().setStyleSheet("background: transparent;")

        self.chat_container = QWidget()
        self.chat_container.setObjectName("chatScrollAreaWidgetV2")
        self.chat_container.setAttribute(Qt.WA_TranslucentBackground)
        self.chat_container.setAutoFillBackground(False)
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(18, 18, 18, 18)
        self.chat_layout.setSpacing(14)
        self._add_welcome()
        self.chat_layout.addStretch()

        self.scroll_area.setWidget(self.chat_container)
        il.addWidget(self.scroll_area, 1)

        # Divider dimatikan agar tidak muncul kotakan/garis belakang input
        div = QFrame()
        div.setFixedHeight(0)
        div.setStyleSheet("background-color: transparent;")
        il.addWidget(div)

        il.addWidget(self._build_input_bar())
        self.input_text.installEventFilter(self)

    # ── HEADER ──────────────────────────────
    def _build_header(self):
        h = QWidget()
        h.setObjectName("chatHeaderV2")
        h.setFixedHeight(64)

        lay = QHBoxLayout(h)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(8)

        back = QPushButton("‹")
        back.setObjectName("headerIconButtonV2")
        back.setFixedSize(38, 38)
        back.setCursor(Qt.PointingHandCursor)
        back.setToolTip("Back")
        back.clicked.connect(lambda: self.window().close() if self.window() else None)
        lay.addWidget(back)

        lay.addStretch(1)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title_box.setContentsMargins(0, 0, 0, 0)

        title = QLabel("AI Assistant")
        title.setObjectName("headerTitleV2")
        title.setAlignment(Qt.AlignCenter)
        title_box.addWidget(title)

        lay.addLayout(title_box)
        lay.addStretch(1)

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("btnClearHeaderV2")
        clear_btn.setFixedSize(62, 32)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setToolTip("Clear chat")
        clear_btn.clicked.connect(self._clear_chat)
        lay.addWidget(clear_btn)
        return h

    def _create_header_avatar(self, path: str, size: int = 46):
        av = QLabel()
        av.setFixedSize(size, size)
        av.setAlignment(Qt.AlignCenter)

        pixmap = QPixmap(path)
        result = QPixmap(size, size)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        if hasattr(QPainter, "HighQualityAntialiasing"):
            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)

        center = QPointF(size / 2, size / 2)
        halo = QRadialGradient(center, size / 2)
        halo.setColorAt(0.00, QColor(125, 211, 252, 62))
        halo.setColorAt(0.54, QColor(37, 99, 235, 24))
        halo.setColorAt(1.00, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(halo))
        painter.drawEllipse(QRectF(0, 0, size, size))

        inner = size - 8
        ix = (size - inner) / 2
        iy = (size - inner) / 2
        painter.setPen(QPen(QColor(125, 211, 252, 165), 1.8))
        painter.setBrush(QColor(2, 6, 23, 235))
        painter.drawEllipse(QRectF(ix, iy, inner, inner))

        if not pixmap.isNull():
            scaled = pixmap.scaled(inner, inner, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = max(0, (scaled.width() - inner) // 2)
            y = max(0, (scaled.height() - inner) // 2)
            cropped = scaled.copy(x, y, inner, inner)
            path_circle = QPainterPath()
            path_circle.addEllipse(QRectF(ix + 2, iy + 2, inner - 4, inner - 4))
            painter.setClipPath(path_circle)
            painter.drawPixmap(int(ix + 2), int(iy + 2), int(inner - 4), int(inner - 4), cropped)
        else:
            painter.setPen(QColor("#BAE6FD"))
            painter.setFont(QFont("Segoe UI", 17, QFont.Bold))
            painter.drawText(QRectF(ix, iy, inner, inner), Qt.AlignCenter, "✦")

        painter.end()
        av.setPixmap(result)
        return av

    # ── INPUT BAR ───────────────────────────
    def _build_input_bar(self):
        """Gemini-style compact input pill for V2.
        Single-row, transparent outer bar, no hint row, SVG icons tetap dipakai.
        """
        bar = QWidget()
        bar.setObjectName("chatInputBarV2")
        bar.setStyleSheet("""
            QWidget#chatInputBarV2 {
                background-color: transparent;
                border: none;
            }
        """)

        lay = QVBoxLayout(bar)
        lay.setContentsMargins(18, 6, 18, 10)
        lay.setSpacing(6)

        self.lbl_image = QLabel("")
        self.lbl_image.setObjectName("imagePreviewLabel")
        self.lbl_image.setStyleSheet("""
            QLabel#imagePreviewLabel {
                color: #BAE6FD;
                background-color: rgba(15, 23, 42, 175);
                border: 1px solid rgba(125, 211, 252, 82);
                border-radius: 8px;
                padding: 5px 10px;
                font-size: 10px;
                font-family: 'Segoe UI';
            }
        """)
        self.lbl_image.hide()
        lay.addWidget(self.lbl_image)

        # ── CLEAN SINGLE PILL (V2) ─────────────────────────────────
        pill = QFrame()
        pill.setObjectName("modernInputPillV2")
        pill.setFixedHeight(54)
        pill.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pill.setStyleSheet("""
            QFrame#modernInputPillV2 {
                background-color: rgba(7, 12, 25, 238);
                border: 1px solid rgba(148, 163, 184, 42);
                border-radius: 27px;
            }
            QFrame#modernInputPillV2:hover {
                background-color: rgba(10, 17, 32, 242);
                border: 1px solid rgba(148, 163, 184, 65);
            }
            QPushButton#pillIconBtnV2,
            QPushButton#modelDropdownBtnV2 {
                background-color: transparent;
                border: none;
                border-radius: 17px;
                padding: 0px;
            }
            QPushButton#pillIconBtnV2:hover,
            QPushButton#modelDropdownBtnV2:hover {
                background-color: rgba(30, 41, 59, 170);
            }
            QPushButton#pillIconBtnV2:pressed,
            QPushButton#modelDropdownBtnV2:pressed {
                background-color: rgba(51, 65, 85, 220);
            }
        """)

        pill_layout = QHBoxLayout(pill)
        pill_layout.setContentsMargins(16, 7, 8, 7)
        pill_layout.setSpacing(6)

        from PyQt5.QtCore import QSize
        _ai_svg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons", "svg", "ai_bar")
        _dropdown_icon_path = os.path.join(_ai_svg_dir, "drop_down_model_ai.svg")
        _ai_name_icon_path  = os.path.join(_ai_svg_dir, "icon_nama_ai_di_drop_downnya.svg")
        _add_icon_path      = os.path.join(_ai_svg_dir, "add_icon_bar_text_ai_nya.svg")
        _voice_icon_path    = os.path.join(_ai_svg_dir, "voice_bar_text.svg")
        _send_icon_path     = os.path.join(_ai_svg_dir, "send_message_bar_text_ainya.svg")

        # Text input dibuat compact seperti input Gemini
        self.input_text = QTextEdit()
        self.input_text.setObjectName("chatInputV2")
        self.input_text.setPlaceholderText("Minta Gemini")
        self.input_text.setFixedHeight(36)
        self.input_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_text.setFont(QFont("Segoe UI", 14))
        self.input_text.setStyleSheet("""
            QTextEdit#chatInputV2 {
                background-color: transparent;
                border: none;
                color: #F8FAFC;
                padding: 7px 2px 0px 2px;
                font-size: 14px;
                font-weight: 520;
                font-family: 'Segoe UI';
                selection-background-color: #334155;
                selection-color: #FFFFFF;
            }
            QTextEdit#chatInputV2:disabled { color: #64748B; }
        """)
        pill_layout.addWidget(self.input_text, 1)

        # Model selector dibuat compact-chip: teks model tidak kepotong, tapi tetap hemat ruang.
        model_btn = QPushButton()
        model_btn.setObjectName("modelDropdownBtnV2")
        model_btn.setFixedHeight(34)
        model_btn.setMinimumWidth(108)
        model_btn.setMaximumWidth(122)
        model_btn.setCursor(Qt.PointingHandCursor)
        model_btn.setText(f"{self._compact_model_label(getattr(self, '_current_model_id', GROQ_MODEL), 'LLaMA 3.1 Instant')}")
        model_btn.setToolTip(f"Current model: {GROQ_MODEL}")
        model_btn.setStyleSheet("""
            QPushButton#modelDropdownBtnV2 {
                background-color: rgba(255, 255, 255, 7);
                color: #BAE6FD;
                border: 1px solid rgba(125, 211, 252, 36);
                border-radius: 17px;
                padding: 0px 10px;
                font-size: 11px;
                font-weight: 760;
                font-family: 'Segoe UI';
                text-align: center;
            }
            QPushButton#modelDropdownBtnV2:hover {
                background-color: rgba(14, 165, 233, 32);
                border: 1px solid rgba(125, 211, 252, 76);
                color: #F8FAFC;
            }
            QPushButton#modelDropdownBtnV2:pressed {
                background-color: rgba(37, 99, 235, 60);
            }
        """)
        try:
            from app.helpers import _svg_icon
            _nm_icon = _svg_icon(_ai_name_icon_path, "#BAE6FD", 14)
            if not _nm_icon.isNull():
                model_btn.setIcon(_nm_icon)
                model_btn.setIconSize(QSize(14, 14))
        except Exception:
            pass

        self._model_btn = model_btn

        def _show_model_popup():
            popup = ModelSelectorPopupV2(self._current_model_id)
            popup.model_selected.connect(self._on_model_changed)
            popup.adjustSize()

            # Smart placement: popup tidak akan kepotong di tepi layar.
            # Kalau tombol model dekat sisi kanan, popup otomatis align ke kanan tombol.
            from PyQt5.QtWidgets import QApplication
            top_left = model_btn.mapToGlobal(model_btn.rect().topLeft())
            bottom_right = model_btn.mapToGlobal(model_btn.rect().bottomRight())
            try:
                screen = QApplication.screenAt(top_left)
                geo = screen.availableGeometry() if screen else QApplication.desktop().availableGeometry(model_btn)
            except Exception:
                geo = QApplication.desktop().availableGeometry(model_btn)

            margin = 10
            preferred_x = bottom_right.x() - popup.width()
            left_limit = geo.x() + margin
            right_limit = geo.x() + geo.width() - popup.width() - margin
            if right_limit < left_limit:
                x = left_limit
            else:
                x = max(left_limit, min(preferred_x, right_limit))

            y_above = top_left.y() - popup.height() - 8
            y_below = bottom_right.y() + 8
            top_limit = geo.y() + margin
            bottom_limit = geo.y() + geo.height() - popup.height() - margin
            y = y_above if y_above >= top_limit else y_below
            y = top_limit if bottom_limit < top_limit else max(top_limit, min(y, bottom_limit))

            popup.move(x, y)
            popup.show()

        model_btn.clicked.connect(_show_model_popup)
        pill_layout.addWidget(model_btn)

        # Attach icon
        self.btn_attach = QPushButton()
        self.btn_attach.setObjectName("pillIconBtnV2")
        self.btn_attach.setFixedSize(34, 34)
        self.btn_attach.setCursor(Qt.PointingHandCursor)
        self.btn_attach.setToolTip("Attach image")
        try:
            from app.helpers import _svg_icon
            _add_icon = _svg_icon(_add_icon_path, "#94A3B8", 18)
            if not _add_icon.isNull():
                self.btn_attach.setIcon(_add_icon)
                self.btn_attach.setIconSize(QSize(18, 18))
        except Exception:
            self.btn_attach.setText("＋")
        self.btn_attach.clicked.connect(self._attach_image)

        def _set_active_v2(state):
            try:
                from app.helpers import _svg_icon
                _ic = _svg_icon(_add_icon_path, "#7DD3FC" if state else "#7E8EA8", 18)
                if not _ic.isNull():
                    self.btn_attach.setIcon(_ic)
                    self.btn_attach.setIconSize(QSize(18, 18))
            except Exception:
                pass
        self.btn_attach.set_active = _set_active_v2
        pill_layout.addWidget(self.btn_attach)

        # Voice icon
        btn_voice = QPushButton()
        btn_voice.setObjectName("pillIconBtnV2")
        btn_voice.setFixedSize(34, 34)
        btn_voice.setCursor(Qt.PointingHandCursor)
        btn_voice.setToolTip("Voice input")
        try:
            from app.helpers import _svg_icon
            _voice_icon = _svg_icon(_voice_icon_path, "#94A3B8", 18)
            if not _voice_icon.isNull():
                btn_voice.setIcon(_voice_icon)
                btn_voice.setIconSize(QSize(18, 18))
        except Exception:
            btn_voice.setText("🎙")
        btn_voice.clicked.connect(lambda: self.input_text.setFocus())
        pill_layout.addWidget(btn_voice)

        # Send button
        self.btn_send = _SendButtonV2()
        self.btn_send.setFixedSize(38, 38)
        try:
            from app.helpers import _svg_icon
            _send_icon = _svg_icon(_send_icon_path, "#E2E8F0", 18)
            if not _send_icon.isNull():
                self.btn_send.setIcon(_send_icon)
                self.btn_send.setIconSize(QSize(18, 18))
        except Exception:
            pass
        self.btn_send.clicked.connect(self._send_message)
        pill_layout.addWidget(self.btn_send)

        lay.addWidget(pill)
        return bar

    # ── WELCOME ─────────────────────────────
    def _add_welcome(self):
        w = QWidget()
        w.setStyleSheet("background-color: transparent;")
        wl = QVBoxLayout(w)
        wl.setContentsMargins(0, 8, 0, 4)
        wl.setSpacing(12)
        wl.setAlignment(Qt.AlignHCenter)

        orb = BlackHoleOrbV2(size=260)
        wl.addWidget(orb, alignment=Qt.AlignHCenter)

        title = QLabel("Mulai dari apa?")
        title.setObjectName("welcomeTitleV2")
        title.setAlignment(Qt.AlignCenter)
        wl.addWidget(title)

        sub = QLabel("Dark orbit AI workspace · Groq multi-turn chat · clean professional interface")
        sub.setObjectName("welcomeSubV2")
        sub.setAlignment(Qt.AlignCenter)
        wl.addWidget(sub)

        badge = QLabel(f"⚡  Model: {GROQ_MODEL}")
        badge.setObjectName("groqBadge")
        badge.setAlignment(Qt.AlignCenter)
        wl.addWidget(badge, alignment=Qt.AlignHCenter)

        self.welcome_cards_widget = QWidget()
        self.welcome_cards_widget.setStyleSheet("background: transparent;")
        cards = QHBoxLayout(self.welcome_cards_widget)
        cards.setContentsMargins(0, 4, 0, 0)
        cards.setSpacing(11)

        card_data = [
            ("⚡", "Fast answer", "Jawaban cepat dan rapi", "Jawab pertanyaan ini secara ringkas, jelas, dan praktis: "),
            ("🧠", "Deep thinking", "Analisis lebih kritis", "Analisis topik ini secara mendalam dengan asumsi, kontra-argumen, dan kesimpulan: "),
            ("🚀", "Build prompt", "Prompt siap pakai", "Buatkan prompt AI yang detail, profesional, dan mudah dieksekusi untuk: "),
        ]
        for icon, title, desc, prompt in card_data:
            card = PromptCardV2(icon, title, desc, prompt)
            card.clicked.connect(self._use_prompt)
            cards.addWidget(card)

        wl.addWidget(self.welcome_cards_widget, alignment=Qt.AlignHCenter)
        self.chat_layout.addWidget(w)
        self.welcome_widget = w

    # ── ACTIONS ─────────────────────────────
    def _use_prompt(self, prompt: str):
        self.input_text.setPlainText(prompt)
        self.input_text.setFocus()
    def _compact_model_label(self, model_id: str, model_name: str = None) -> str:
        labels = {
            "llama-3.1-8b-instant": "LLaMA 3.1",
            "llama3-70b-8192": "LLaMA 70B",
            "mixtral-8x7b-32768": "Mixtral",
            "gemma2-9b-it": "Gemma 2",
            "deepseek-r1-distill-llama-70b": "DeepSeek",
        }
        if model_id in labels:
            return labels[model_id]
        name = model_name or model_id or "AI"
        return name if len(name) <= 11 else name[:10] + "…"

    def _on_model_changed(self, model_id: str, model_name: str):
        global GROQ_MODEL
        GROQ_MODEL = model_id
        self._current_model_id = model_id
        if self._model_btn:
            self._model_btn.setText(f"{self._compact_model_label(model_id, model_name)} ▾")
            self._model_btn.setToolTip(f"Current model: {model_name} ({model_id})")
        logger.info(f"[Groq v2] Model switched → {model_id}")

    def _attach_image(self):
        # Groq REST API standard tidak support image input via this endpoint
        # Tampilkan info saja
        self.lbl_image.setText("⚠  Groq llama-3.1 tidak mendukung input gambar")
        self.lbl_image.show()
        QTimer.singleShot(3000, self.lbl_image.hide)
        logger.info("[Groq v2] Image attach attempted — model doesn't support vision")

    def _send_message(self):
        message = self.input_text.toPlainText().strip()
        if not message:
            return

        if not self.chat_started:
            self.welcome_widget.hide()
            self.chat_started = True

        self.input_text.setEnabled(False)
        self.btn_send.setEnabled(False)
        self.btn_attach.setEnabled(False)

        self._add_bubble(message, is_user=True)
        self.input_text.clear()
        self._show_typing()

        # Pass current history for multi-turn context
        self.ai_thread = GroqRequestThread(message, list(self._history))
        self.ai_thread.response_received.connect(self._on_response)
        self.ai_thread.error_occurred.connect(self._on_error)
        self.ai_thread.start()

        # Append user turn to local history
        self._history.append({"role": "user", "content": message})

        logger.ai_request(message)

    def _add_bubble(self, message, is_user=True):
        self._pop_stretch()
        self.chat_layout.addWidget(ChatBubbleV2(message, is_user))
        self.chat_layout.addStretch()
        QTimer.singleShot(80, self._scroll_bottom)

    def _show_typing(self):
        self._pop_stretch()
        rw = QWidget()
        rw.setStyleSheet("background-color: transparent;")
        rl = QHBoxLayout(rw)
        rl.setContentsMargins(46, 0, 0, 0)
        self.typing_widget = TypingIndicatorV2()
        rl.addWidget(self.typing_widget)
        rl.addStretch()
        self.chat_layout.addWidget(rw)
        self._typing_row_w = rw
        self.chat_layout.addStretch()
        QTimer.singleShot(80, self._scroll_bottom)

    def _remove_typing(self):
        if self._typing_row_w:
            if self.typing_widget:
                self.typing_widget.stop()
            for _ in range(2):
                if self.chat_layout.count():
                    item = self.chat_layout.takeAt(self.chat_layout.count() - 1)
                    if item and item.widget():
                        item.widget().deleteLater()
            self._typing_row_w = None
            self.typing_widget  = None

    def _on_response(self, text):
        self._remove_typing()
        self._add_bubble(text, is_user=False)
        # Append assistant turn to history (multi-turn context)
        self._history.append({"role": "assistant", "content": text})
        self._enable_input()
        logger.ai_response(text, 200)

    def _on_error(self, msg):
        self._remove_typing()
        self._add_bubble(f"⚠️  {msg}", is_user=False)
        # Remove last user turn from history since it errored
        if self._history and self._history[-1]["role"] == "user":
            self._history.pop()
        self._enable_input()
        logger.ai_error(msg)

    def _enable_input(self):
        self.input_text.setEnabled(True)
        self.btn_send.setEnabled(True)
        self.btn_attach.setEnabled(True)
        self.input_text.setFocus()

    def _clear_chat(self):
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._history.clear()
        self.chat_started = False
        self._add_welcome()
        self.chat_layout.addStretch()
        logger.info("[Groq v2] Chat cleared — history reset")

    def _pop_stretch(self):
        if self.chat_layout.count():
            last = self.chat_layout.itemAt(self.chat_layout.count() - 1)
            if last and last.spacerItem():
                self.chat_layout.takeAt(self.chat_layout.count() - 1)

    def _scroll_bottom(self):
        sb = self.scroll_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    def eventFilter(self, obj, event):
        if obj == self.input_text and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self._send_message()
                return True
        return super().eventFilter(obj, event)