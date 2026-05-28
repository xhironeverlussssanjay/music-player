"""
AI CHATBOT MODULE - GPT-4o-mini Integration

"""

import os
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
#  STYLESHEET — scoped ke objectName, kebal override styles.css
# ═══════════════════════════════════════════════════════════════
GLOBAL_STYLE = """
QWidget#chatRootWidget { background-color: #0D0D14; border: none; }

/* ── Header ─────────────────────────────── */
QWidget#chatHeader { background-color: #111120; border-bottom: 1px solid #222235; }
QLabel#chatHeaderName {
    color: #EEEEFF; font-size: 14px; font-weight: 700;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#chatHeaderStatus {
    color: #4ADE80; font-size: 10px;
    font-family: 'Segoe UI'; background-color: transparent;
}
QPushButton#btnClearHeader {
    background-color: transparent; color: #44445A;
    border: 1px solid #222235; border-radius: 8px;
    padding: 5px 13px; font-size: 11px; font-family: 'Segoe UI';
}
QPushButton#btnClearHeader:hover {
    color: #F87171; border-color: #F87171;
    background-color: #22161C;
}

/* ── Scroll & body ──────────────────────── */
QScrollArea#chatScrollArea { background-color: #0D0D14; border: none; }
QWidget#chatScrollAreaWidget { background-color: #0D0D14; }
QScrollBar:vertical { background-color: #111120; width: 4px; border-radius: 2px; }
QScrollBar::handle:vertical {
    background-color: #2A2A45; border-radius: 2px; min-height: 28px;
}
QScrollBar::handle:vertical:hover { background-color: #7C6EF5; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Welcome section ────────────────────── */
QFrame#featureCard {
    background-color: #111120; border: 1px solid #252540;
    border-radius: 14px;
}
QFrame#featureCard:hover { border: 1px solid #7C6EF5; background-color: #16162A; }
QLabel#featureCardIcon  { font-size: 22px; background-color: transparent; }
QLabel#featureCardTitle {
    color: #DDDDF5; font-size: 12px; font-weight: 600;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#featureCardDesc  {
    color: #44445A; font-size: 10px;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#welcomeTitle {
    color: #EEEEFF; font-size: 21px; font-weight: 700;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#welcomeSub {
    color: #6666AA; font-size: 12px;
    font-family: 'Segoe UI'; background-color: transparent;
}

/* ── Bubbles ────────────────────────────── */
QFrame#bubbleUser {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #2D1B69, stop:1 #1E1444);
    border-radius: 20px; border-top-right-radius: 6px;
    border: 1px solid #4C3299;
}
QLabel#bubbleUserText {
    color: #EDE9FF; font-size: 15px; font-weight: 700;
    font-family: 'Segoe UI'; background-color: transparent;
}
QFrame#bubbleAI {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #131325, stop:1 #0F0F22);
    border-radius: 20px; border-top-left-radius: 6px;
    border: 1px solid #252545;
}
QLabel#bubbleAIText {
    color: #F0EEFF; font-size: 15px; font-weight: 700;
    font-family: 'Segoe UI'; background-color: transparent;
}
QLabel#avatarUser {
    background-color: #7C3AED;
    color: white; border-radius: 17px;
    font-size: 11px; font-weight: 700; font-family: 'Segoe UI';
}
QLabel#avatarAI {
    background-color: #7C3AED;
    color: white; border-radius: 17px;
    font-size: 14px; font-family: 'Segoe UI';
}

/* ── Reaction buttons ───────────────────── */
QPushButton#reactionBtn {
    background-color: transparent; color: #44445A;
    border: none; border-radius: 6px; font-size: 13px;
}
QPushButton#reactionBtn:hover {
    background-color: #18172A;
}
QPushButton#reactionBtnActive {
    background-color: transparent;
    border: none; border-radius: 6px; font-size: 13px;
}
QPushButton#reactionBtnDislike {
    background-color: transparent;
    border: none; border-radius: 6px; font-size: 13px;
}

/* ── Input bar ──────────────────────────── */
QWidget#chatInputBar {
    background-color: #0D0D14; border-top: 1px solid #1A1A2E;
}
QFrame#modernInputPill {
    background-color: #13131F;
    border: 1.5px solid #28283D;
    border-radius: 22px;
}
QTextEdit#chatInput {
    background-color: transparent; color: #E8E8FA; border: none;
    font-size: 15px; font-weight: 400; font-family: 'Segoe UI';
    selection-background-color: #7C6EF5;
}
QPushButton#btnAttach {
    background-color: transparent; color: #44445A;
    border: none; border-radius: 9px;
}
QPushButton#btnAttach:hover {
    background-color: #211E3C; color: #A78BFA;
}
QPushButton#btnAttachActive {
    background-color: #29254C; color: #C4B5FD;
    border: 1px solid #7C6EF5; border-radius: 9px;
}
QPushButton#btnSend {
    background-color: #7C3AED;
    color: white; border: none; border-radius: 25px;
    font-size: 18px; font-weight: 600; font-family: 'Segoe UI';
}
QPushButton#btnSend:hover {
    background-color: #8B5CF6;
}
QPushButton#btnSend:pressed { background-color: #3730A3; }
QPushButton#btnSend:disabled { background-color: #18182E; color: #33334A; }
QLabel#imagePreviewLabel {
    color: #A78BFA; background-color: #1D1B34;
    border: 1px solid #6B5CE7; border-radius: 6px;
    padding: 3px 9px; font-size: 10px; font-family: 'Segoe UI';
}
QLabel#inputHint {
    color: #252540; font-size: 10px;
    font-family: 'Segoe UI'; background-color: transparent;
}
QPushButton#pillIconBtn {
    background-color: transparent;
    border: none;
    border-radius: 14px;
}
QPushButton#pillIconBtn:hover {
    background-color: #1E1C32;
}
QPushButton#pillIconBtn:pressed {
    background-color: #2A2448;
}
QPushButton#modelDropdownBtn {
    background-color: transparent;
    color: #9B8BFF;
    border: 0.5px solid #3A3A5A;
    border-radius: 14px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'Segoe UI';
}
QPushButton#modelDropdownBtn:hover {
    background-color: rgba(36, 28, 58, 118);
    border: 0.5px solid rgba(196, 181, 253, 42);
    color: #DDD6FE;
}
"""


# ═══════════════════════════════════════════════════════════════
#  ALISA / BLACK-HOLE SKIN PATCH
#  Patch ini sengaja hanya menyentuh visual root + welcome screen.
#  Komponen chat asli tetap dipakai: REST API, input bar, SVG icons,
#  ChatBubble, ReactionBar, attach image, model popup, dan send button.
# ═══════════════════════════════════════════════════════════════
ALISA_STYLE_PATCH = """
QWidget#chatRootWidget {
    background-color: transparent;
    border: none;
}
QWidget#chatHeader {
    background: transparent;
    border: none;
}

QPushButton#headerIconButton {
    background-color: transparent;
    color: #F3EFFF;
    border: none;
    border-radius: 19px;
    font-size: 25px;
    font-weight: 700;
    font-family: 'Segoe UI';
    text-align: center;
    padding: 0px;
}
QPushButton#headerIconButton:hover {
    background-color: rgba(139, 92, 246, 52);
    color: #FFFFFF;
}
QPushButton#headerIconButton:pressed {
    background-color: rgba(109, 40, 217, 84);
}
QScrollArea#chatScrollArea {
    background-color: transparent;
    border: none;
}
QWidget#chatScrollAreaWidget {
    background-color: transparent;
}
QWidget#chatInputBar {
    background-color: rgba(7, 8, 18, 225);
    border-top: 1px solid rgba(125, 92, 255, 55);
}
QFrame#modernInputPill {
    background-color: rgba(14, 15, 28, 238);
    border: 1.5px solid rgba(191, 167, 255, 58);
    border-radius: 22px;
}
QFrame#modernInputPill:hover {
    border: 1.5px solid rgba(191, 167, 255, 58);
}
QLabel#welcomeTitle {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 850;
}
QLabel#welcomeSub {
    color: #A99BE2;
    font-size: 12px;
}
QFrame#featureCard {
    background-color: rgba(23, 24, 39, 220);
    border: 1px solid rgba(255, 255, 255, 35);
    border-radius: 18px;
}
QFrame#featureCard:hover {
    background-color: rgba(35, 28, 63, 235);
    border: 1px solid rgba(192, 132, 252, 150);
}
QFrame#bubbleAI {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(20, 22, 36, 238), stop:1 rgba(13, 14, 26, 238));
    border: 1px solid rgba(255, 255, 255, 35);
}
QFrame#bubbleUser {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #7C3AED, stop:0.55 #5B21B6, stop:1 #2E1065);
    border: 1px solid rgba(216, 180, 254, 125);
}
QTextEdit#chatInput {
    color: #F5F3FF;
}
QPushButton#modelDropdownBtn {
    color: #BCA7FF;
    border: 0.5px solid rgba(155, 139, 255, 95);
}
QPushButton#btnSend {
    background-color: #8B5CF6;
}
QPushButton#btnSend:hover {
    background-color: #A78BFA;
}
QPushButton#clearChatButton {
    background-color: rgba(139, 92, 246, 32);
    color: #F3EFFF;
    border: 1px solid rgba(216, 180, 254, 70);
    border-radius: 14px;
    padding: 0px 12px;
    font-size: 11px;
    font-weight: 800;
    font-family: 'Segoe UI';
    text-align: center;
}
QPushButton#clearChatButton:hover {
    background-color: rgba(168, 85, 247, 62);
    border: 1px solid rgba(216, 180, 254, 130);
    color: #FFFFFF;
}
QPushButton#clearChatButton:pressed {
    background-color: rgba(109, 40, 217, 95);
}
"""


# ─────────────────────────────────────────────
#  EMOJI LIST — 18 reaksi, clean & selaras
# ─────────────────────────────────────────────
EMOJI_LIST = [
    "👍", "❤️", "😂", "🔥", "😮", "👏", 
    "🎉", "💯", "🤔", "😢", "⭐", "🙏",
    "💪", "🚀", "✨", "💡", "🎯", "⚡"
]


# ─────────────────────────────────────────────
#  API THREAD
# ─────────────────────────────────────────────
class AIRequestThread(QThread):
    response_received = pyqtSignal(str)
    error_occurred    = pyqtSignal(str)

    def __init__(self, message, image_path=None):
        super().__init__()
        self.message    = message
        self.image_path = image_path
        # Load API URL dari environment variable
        self.api_url    = os.getenv("GPT_API_URL", "https://kyuu2nd.dev/api/ai/gpt-4o-mini")
        # Random colors for console output
        self.colors = [
            '\033[95m',  # Magenta
            '\033[94m',  # Blue
            '\033[96m',  # Cyan
            '\033[92m',  # Green
            '\033[93m',  # Yellow
            '\033[91m',  # Red
            '\033[35m',  # Purple
            '\033[36m',  # Light Cyan
            '\033[32m',  # Light Green
            '\033[33m',  # Orange
        ]
        self.reset_color = '\033[0m'

    def _get_random_color(self):
        return random.choice(self.colors)

    def run(self):
        try:
            data  = {"prompt": self.message}
            files = None
            color = self._get_random_color()
            logger.info(f"{color}Sending to: {self.api_url}{self.reset_color}")
            if self.image_path:
                files = {"image": open(self.image_path, "rb")}
            if files:
                response = requests.post(self.api_url, data=data, files=files, timeout=30)
                files["image"].close()
            else:
                response = requests.post(self.api_url, data=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("status"):
                    answer = result.get("result", {}).get("answer", "No response")
                    logger.info(f"{color}✓ API Response received: {len(answer)} chars{self.reset_color}")
                    self.response_received.emit(answer)
                else:
                    error_msg = f"API Error: {result.get('message','Unknown')}"
                    logger.error(f"{color}✗ {error_msg}{self.reset_color}")
                    self.error_occurred.emit(error_msg)
            else:
                error_msg = f"HTTP {response.status_code}"
                logger.error(f"{color}✗ {error_msg}{self.reset_color}")
                self.error_occurred.emit(error_msg)
        except requests.exceptions.Timeout:
            error_msg = "Request timeout – AI took too long."
            logger.error(f"{self._get_random_color()}✗ {error_msg}{self.reset_color}")
            self.error_occurred.emit(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "Connection error – check your internet."
            logger.error(f"{self._get_random_color()}✗ {error_msg}{self.reset_color}")
            self.error_occurred.emit(error_msg)
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(f"{self._get_random_color()}✗ {error_msg}{self.reset_color}")
            self.error_occurred.emit(error_msg)



# ─────────────────────────────────────────────
#  SAFE GRADIENT ROOT — no graphics effect
# ─────────────────────────────────────────────
class _AlisaGradientRoot(QWidget):
    """Background ungu gelap + glow. Aman karena tidak memakai QGraphicsEffect."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatRootWidget")
        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setAutoFillBackground(False)
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(80)

    def _tick(self):
        self._phase = (self._phase + 0.018) % (math.pi * 2)
        self.update()

    def _draw_glow(self, painter, x, y, radius, color):
        rg = QRadialGradient(QPointF(x, y), radius)
        rg.setColorAt(0.0, color)
        rg.setColorAt(0.52, QColor(color.red(), color.green(), color.blue(), max(12, color.alpha() // 3)))
        rg.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(rg))
        painter.drawEllipse(QRectF(x - radius, y - radius, radius * 2, radius * 2))

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            w, h = max(1, self.width()), max(1, self.height())

            bg = QLinearGradient(0, 0, w, h)
            bg.setColorAt(0.00, QColor("#070812"))
            bg.setColorAt(0.34, QColor("#0A0B16"))
            bg.setColorAt(0.68, QColor("#160A2E"))
            bg.setColorAt(1.00, QColor("#2B1154"))
            painter.fillRect(self.rect(), bg)

            drift = math.sin(self._phase) * 18
            self._draw_glow(painter, w * 0.83 + drift, h * 0.08, min(w, h) * 0.38, QColor(118, 45, 255, 105))
            self._draw_glow(painter, w * 0.18 - drift * 0.6, h * 0.92, min(w, h) * 0.42, QColor(86, 21, 160, 82))
            self._draw_glow(painter, w * 0.52, h * 0.42 + drift * 0.3, min(w, h) * 0.25, QColor(40, 105, 255, 34))

            vignette = QRadialGradient(QPointF(w * 0.5, h * 0.45), max(w, h) * 0.72)
            vignette.setColorAt(0.0, QColor(0, 0, 0, 0))
            vignette.setColorAt(1.0, QColor(0, 0, 0, 145))
            painter.fillRect(self.rect(), QBrush(vignette))
        finally:
            painter.end()


class BlackHoleOrb(QWidget):
    """Ultra-smooth realistic black-hole orb.

    Fokus desain:
    - Phase animasi dibuat terus berjalan tanpa reset modulo di state utama,
      sehingga tidak ada loncatan saat cycle visual kembali ke posisi awal.
    - Cincin bukan 1 gradient besar saja, tapi gabungan photon ring,
      accretion disk, dan ratusan brush-like vortex strokes.
    - Event horizon tetap hitam, tetapi diberi rim-light, inner rotating
      turbulence, dan tiny singularity glint agar tidak terasa monoton.
    """
    def __init__(self, size=360, parent=None):
        super().__init__(parent)
        self._size = size
        self._phase = 0.0          # main disk rotation; sengaja tidak dimodulo
        self._slow_phase = 0.0     # slow lensing / tilt drift
        self._core_phase = 0.0     # event-horizon inner rotation
        self._twinkle = 0.0
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

        # Deterministic particles: tidak random ulang di setiap repaint,
        # jadi animasi terlihat stabil dan profesional.
        rng = random.Random(89241)
        self._stars = []
        for _ in range(168):
            self._stars.append((
                rng.uniform(0.03, 0.97),
                rng.uniform(0.03, 0.97),
                rng.uniform(0.38, 1.55),
                rng.randint(20, 135),
                rng.uniform(-0.10, 0.10),
            ))

        self._dust = []
        for i in range(118):
            self._dust.append((
                i * 137.508,
                rng.uniform(0.73, 1.24),
                rng.uniform(0.62, 1.38),
                rng.randint(26, 122),
                rng.uniform(0.70, 1.38),
            ))

        # Brush/vortex strokes terinspirasi dari sample gambar: cincin tampak
        # seperti guratan spiral, bukan lingkaran flat.
        self._vortex_strokes = []
        for i in range(224):
            self._vortex_strokes.append((
                rng.uniform(0, 360),          # base angle
                rng.uniform(0.68, 1.22),      # radius multiplier
                rng.uniform(13, 44),          # arc span degree
                rng.uniform(0.55, 2.7),       # pen width
                rng.randint(16, 112),         # alpha
                rng.uniform(0.22, 1.18),      # rotation speed multiplier
                rng.uniform(-0.55, 0.55),     # subtle angle jitter
                rng.choice((0, 1, 2, 3)),     # color family
            ))

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)  # ±60 FPS

    def _tick(self):
        # Tidak memakai `% 360` pada state. Reset modulo pada phase utama sering
        # menimbulkan micro-jump pada gradient/conical seam. Drawing boleh wrap,
        # tetapi value internal dibiarkan kontinu.
        self._phase += 0.265
        self._slow_phase += 0.042
        self._core_phase += 0.415
        self._twinkle += 0.018
        self.update()

    def _quality(self, painter):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        if hasattr(QPainter, "HighQualityAntialiasing"):
            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)

    def _angle(self, base=0.0, speed=1.0):
        return (base + self._phase * speed) % 360.0

    def _radial_glow(self, painter, cx, cy, radius, color):
        glow = QRadialGradient(QPointF(cx, cy), radius)
        glow.setColorAt(0.00, color)
        glow.setColorAt(0.34, QColor(color.red(), color.green(), color.blue(), max(7, color.alpha() // 3)))
        glow.setColorAt(0.73, QColor(color.red(), color.green(), color.blue(), max(2, color.alpha() // 8)))
        glow.setColorAt(1.00, QColor(color.red(), color.green(), color.blue(), 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow))
        painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

    def _draw_stars(self, painter, w, h, cx, cy):
        painter.setPen(Qt.NoPen)
        for i, (xf, yf, r, alpha, drift) in enumerate(self._stars):
            dx = (xf - 0.5) * w
            dy = (yf - 0.5) * h
            a = math.radians(self._slow_phase * drift)
            x = cx + dx * math.cos(a) - dy * math.sin(a) * 0.105
            y = cy + dy * math.cos(a) + dx * math.sin(a) * 0.105
            if math.hypot(x - cx, y - cy) < min(w, h) * 0.175:
                continue
            pulse = 0.76 + 0.24 * math.sin(self._twinkle + i * 0.47)
            aa = max(8, min(165, int(alpha * pulse)))
            if i % 9 == 0:
                col = QColor(255, 236, 196, aa)
            elif i % 5 == 0:
                col = QColor(216, 205, 255, aa)
            else:
                col = QColor(148, 163, 184, aa)
            painter.setBrush(col)
            painter.drawEllipse(QRectF(x - r / 2, y - r / 2, r, r))

    def _draw_ellipse_ring(self, painter, cx, cy, radius, y_scale, rotation, width, gradient, alpha_shadow=0):
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(rotation)
        painter.scale(1.0, y_scale)
        if alpha_shadow:
            painter.setPen(QPen(QColor(0, 0, 0, alpha_shadow), width + 6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QRectF(-radius, -radius, radius * 2, radius * 2))
        painter.setPen(QPen(QBrush(gradient), width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QRectF(-radius, -radius, radius * 2, radius * 2))
        painter.restore()

    def _draw_arc(self, painter, cx, cy, radius, y_scale, rotation, start_deg, span_deg, width, color):
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(rotation)
        painter.scale(1.0, y_scale)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawArc(QRectF(-radius, -radius, radius * 2, radius * 2), int(start_deg * 16), int(span_deg * 16))
        painter.restore()

    def _seamless_disk_gradient(self, angle_offset=0.0, alpha=255):
        # Stop 0.00 dan 1.00 sengaja identik agar conical seam tidak kelihatan.
        g = QConicalGradient(QPointF(0, 0), angle_offset)
        g.setColorAt(0.00, QColor(255, 242, 216, int(alpha * 0.96)))
        g.setColorAt(0.08, QColor(255, 190, 121, int(alpha * 0.93)))
        g.setColorAt(0.18, QColor(225, 225, 232, int(alpha * 0.78)))
        g.setColorAt(0.30, QColor(174, 164, 255, int(alpha * 0.66)))
        g.setColorAt(0.43, QColor(63, 55, 95, int(alpha * 0.34)))
        g.setColorAt(0.55, QColor(18, 19, 32, int(alpha * 0.23)))
        g.setColorAt(0.68, QColor(109, 91, 176, int(alpha * 0.52)))
        g.setColorAt(0.80, QColor(242, 229, 210, int(alpha * 0.84)))
        g.setColorAt(0.91, QColor(255, 185, 104, int(alpha * 0.92)))
        g.setColorAt(1.00, QColor(255, 242, 216, int(alpha * 0.96)))
        return g

    def _photon_gradient(self, cx, cy, angle_offset=0.0, alpha=255):
        g = QConicalGradient(QPointF(cx, cy), angle_offset)
        g.setColorAt(0.00, QColor(255, 252, 232, int(alpha * 0.98)))
        g.setColorAt(0.15, QColor(255, 196, 132, int(alpha * 0.78)))
        g.setColorAt(0.32, QColor(224, 214, 255, int(alpha * 0.88)))
        g.setColorAt(0.52, QColor(93, 78, 145, int(alpha * 0.42)))
        g.setColorAt(0.71, QColor(201, 196, 218, int(alpha * 0.68)))
        g.setColorAt(0.86, QColor(255, 226, 172, int(alpha * 0.82)))
        g.setColorAt(1.00, QColor(255, 252, 232, int(alpha * 0.98)))
        return g

    def _draw_vortex_texture(self, painter, cx, cy, disk_r, tilt):
        # Guratan melingkar seperti sample: banyak arc tipis dengan radius,
        # panjang, alpha, dan speed berbeda. Karena semua param deterministik,
        # tidak ada flicker/reset visual.
        for i, (base_angle, radius_mul, span, width, alpha, speed, jitter, family) in enumerate(self._vortex_strokes):
            radius = disk_r * radius_mul
            shimmer = 0.68 + 0.32 * math.sin(math.radians(self._phase * 0.23 + i * 23.7))
            aa = max(5, min(160, int(alpha * shimmer)))

            if family == 0:
                color = QColor(238, 238, 244, aa)
            elif family == 1:
                color = QColor(255, 210, 148, int(aa * 0.72))
            elif family == 2:
                color = QColor(192, 181, 255, int(aa * 0.58))
            else:
                color = QColor(92, 88, 116, int(aa * 0.52))

            start = base_angle + self._phase * speed + math.sin(self._twinkle + i) * jitter * 8.0
            local_tilt = tilt + math.sin(math.radians(i * 19 + self._slow_phase)) * 1.05
            y_scale = 0.39 + 0.035 * math.sin(math.radians(i * 11 + self._slow_phase * 2.1))
            self._draw_arc(painter, cx, cy, radius, y_scale, local_tilt, start, span, width, color)

    def _draw_core_turbulence(self, painter, cx, cy, core_r):
        # Clip inner turbulence ke horizon supaya pusat black hole terasa hidup,
        # lebih tegas, dan tetap tampak sebagai lubang gelap.
        painter.save()
        clip = QPainterPath()
        clip.addEllipse(QRectF(cx - core_r, cy - core_r, core_r * 2, core_r * 2))
        painter.setClipPath(clip)

        painter.translate(cx, cy)
        painter.rotate((self._core_phase * 0.82) % 360.0)
        painter.setBrush(Qt.NoBrush)

        # Layer 1: orbit arc lebih tegas.
        for i in range(18):
            r = core_r * (0.20 + i * 0.040)
            pulse = 0.72 + 0.28 * math.sin(self._twinkle * 0.72 + i * 0.85)
            alpha = int((18 + i * 1.25) * pulse)
            if i % 3 == 0:
                col = QColor(206, 196, 255, max(10, alpha))
            elif i % 3 == 1:
                col = QColor(124, 114, 182, max(8, int(alpha * 0.90)))
            else:
                col = QColor(55, 50, 86, max(7, int(alpha * 0.78)))
            width = max(0.7, core_r * (0.010 + i * 0.00028))
            start = (i * 31 + self._core_phase * (1.08 + i * 0.018))
            span = 96 + i * 7
            painter.setPen(QPen(col, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawArc(QRectF(-r, -r, r * 2, r * 2), int(start * 16), int(span * 16))

        # Layer 2: spiral throat di tengah, dibuat lebih kelihatan.
        throat = QPainterPath()
        first = True
        for t in range(150):
            a = math.radians(t * 12.6 + self._core_phase * 1.85)
            r = core_r * (0.02 + t / 150.0 * 0.82)
            x = math.cos(a) * r
            y = math.sin(a) * r * (0.96 + 0.05 * math.sin(a * 2.0))
            if first:
                throat.moveTo(x, y)
                first = False
            else:
                throat.lineTo(x, y)
        painter.setPen(QPen(QColor(232, 226, 255, 40), 1.35, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(throat)

        # Layer 3: inner glow vortex tipis agar pusaran tengah lebih terlihat.
        for j in range(6):
            rr = core_r * (0.11 + j * 0.06)
            a2 = int(42 + 14 * math.sin(self._twinkle * 1.35 + j))
            painter.setPen(QPen(QColor(245, 240, 255, max(16, a2)), max(0.8, core_r * 0.012), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawEllipse(QRectF(-rr, -rr, rr * 2, rr * 2))

        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return
        try:
            self._quality(painter)
            w, h = max(1, self.width()), max(1, self.height())
            s = min(w, h)
            cx, cy = w / 2, h / 2

            # Deep-space glass background.
            self._radial_glow(painter, cx, cy, s * 0.62, QColor(75, 63, 118, 56))
            self._radial_glow(painter, cx + s * 0.11, cy - s * 0.07, s * 0.43, QColor(160, 130, 255, 42))
            self._radial_glow(painter, cx - s * 0.18, cy + s * 0.13, s * 0.36, QColor(255, 189, 115, 18))
            self._draw_stars(painter, w, h, cx, cy)

            disk_r = s * 0.338
            tilt = -8.5 + math.sin(math.radians(self._slow_phase * 1.9)) * 1.15

            # Outer gravitational lensing rings: tipis, realistis, tidak terlalu neon.
            outer_grad = QConicalGradient(QPointF(0, 0), self._angle(35, -0.20))
            outer_grad.setColorAt(0.00, QColor(238, 238, 244, 55))
            outer_grad.setColorAt(0.25, QColor(255, 205, 142, 22))
            outer_grad.setColorAt(0.50, QColor(98, 90, 138, 18))
            outer_grad.setColorAt(0.75, QColor(199, 190, 255, 34))
            outer_grad.setColorAt(1.00, QColor(238, 238, 244, 55))
            self._draw_ellipse_ring(painter, cx, cy, disk_r + 56, 0.40, tilt, 1.35, outer_grad)

            mid_grad = QConicalGradient(QPointF(0, 0), self._angle(190, 0.13))
            mid_grad.setColorAt(0.00, QColor(255, 232, 194, 66))
            mid_grad.setColorAt(0.38, QColor(140, 126, 196, 26))
            mid_grad.setColorAt(0.72, QColor(240, 240, 246, 42))
            mid_grad.setColorAt(1.00, QColor(255, 232, 194, 66))
            self._draw_ellipse_ring(painter, cx, cy, disk_r + 36, 0.37, tilt, 2.15, mid_grad)

            # Diffuse bright mass behind disk.
            self._radial_glow(painter, cx, cy, disk_r * 1.37, QColor(235, 226, 255, 33))
            self._radial_glow(painter, cx + disk_r * 0.26, cy - disk_r * 0.10, disk_r * 0.86, QColor(255, 199, 120, 31))

            # Main accretion disk: smooth gradient bed.
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(tilt)
            painter.scale(1.0, 0.39)

            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(0, 0, 0, 100), 32.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawEllipse(QRectF(-disk_r, -disk_r, disk_r * 2, disk_r * 2))

            main_disk = self._seamless_disk_gradient(self._angle(0, -1.0), 236)
            painter.setPen(QPen(QBrush(main_disk), 23.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawEllipse(QRectF(-disk_r, -disk_r, disk_r * 2, disk_r * 2))

            inner_disk = self._seamless_disk_gradient(self._angle(92, -0.68), 132)
            painter.setPen(QPen(QBrush(inner_disk), 7.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawEllipse(QRectF(-(disk_r - 18), -(disk_r - 18), (disk_r - 18) * 2, (disk_r - 18) * 2))

            outer_disk = self._seamless_disk_gradient(self._angle(210, 0.34), 92)
            painter.setPen(QPen(QBrush(outer_disk), 5.3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawEllipse(QRectF(-(disk_r + 15), -(disk_r + 15), (disk_r + 15) * 2, (disk_r + 15) * 2))
            painter.restore()

            # Brush-like swirl texture layered on top. Ini bagian yang membuatnya
            # mendekati sample black-hole hand-drawn/realistic vortex.
            self._draw_vortex_texture(painter, cx, cy, disk_r, tilt)

            # Bright front crescent and back shadow give depth/lensing.
            self._draw_arc(painter, cx, cy, disk_r + 4, 0.39, tilt, 199 + self._phase * 0.06, 116, 2.4, QColor(255, 247, 232, 102))
            self._draw_arc(painter, cx, cy, disk_r - 8, 0.39, tilt, 214 + self._phase * 0.08, 78, 1.5, QColor(255, 208, 145, 76))
            self._draw_arc(painter, cx, cy, disk_r + 2, 0.39, tilt, 18 + self._phase * 0.04, 76, 5.5, QColor(0, 0, 0, 46))

            # Photon ring before event horizon.
            photon_r = disk_r * 0.635
            photon_grad = self._photon_gradient(cx, cy, self._angle(70, -0.28), 210)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QBrush(photon_grad), 3.4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawEllipse(QRectF(cx - photon_r, cy - photon_r, photon_r * 2, photon_r * 2))
            painter.setPen(QPen(QColor(255, 255, 255, 48), 0.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawEllipse(QRectF(cx - photon_r - 3, cy - photon_r - 3, (photon_r + 3) * 2, (photon_r + 3) * 2))

            # Event horizon: deep black, but with material depth and rotating inner turbulence.
            core_r = disk_r * 0.49
            rim = QRadialGradient(QPointF(cx, cy), core_r * 1.70)
            rim.setColorAt(0.00, QColor(0, 0, 2, 255))
            rim.setColorAt(0.46, QColor(1, 2, 8, 255))
            rim.setColorAt(0.70, QColor(5, 5, 14, 255))
            rim.setColorAt(0.84, QColor(20, 17, 35, 245))
            rim.setColorAt(0.94, QColor(190, 181, 255, 92))
            rim.setColorAt(1.00, QColor(255, 225, 174, 40))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(rim))
            painter.drawEllipse(QRectF(cx - core_r, cy - core_r, core_r * 2, core_r * 2))

            self._draw_core_turbulence(painter, cx, cy, core_r)

            # Rim highlight yang ikut rotasi secara halus.
            rim_grad = self._photon_gradient(cx, cy, self._angle(12, -0.50), 92)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QBrush(rim_grad), 1.45, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawEllipse(QRectF(cx - core_r - 2, cy - core_r - 2, (core_r + 2) * 2, (core_r + 2) * 2))

            # Singularity/glint dibuat lebih tegas supaya animasi tengah lebih kelihatan,
            # tapi tetap elegan dan tidak berubah jadi lampu biasa.
            glint = 0.74 + 0.26 * math.sin(self._twinkle * 1.95)
            self._radial_glow(painter, cx, cy, core_r * 0.33, QColor(255, 255, 248, int(62 * glint)))
            self._radial_glow(painter, cx, cy, core_r * 0.18, QColor(218, 208, 255, int(46 * glint)))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 255, 252, int(128 * glint)))
            tiny = max(2.1, core_r * 0.048)
            painter.drawEllipse(QRectF(cx - tiny / 2, cy - tiny / 2, tiny, tiny))
            painter.setPen(QPen(QColor(255, 255, 250, int(72 * glint)), 0.9, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(QPointF(cx - core_r * 0.36, cy), QPointF(cx + core_r * 0.36, cy))
            painter.drawLine(QPointF(cx, cy - core_r * 0.36), QPointF(cx, cy + core_r * 0.36))
            painter.setPen(QPen(QColor(220, 212, 255, int(38 * glint)), 0.75, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(QPointF(cx - core_r * 0.24, cy - core_r * 0.24), QPointF(cx + core_r * 0.24, cy + core_r * 0.24))
            painter.drawLine(QPointF(cx - core_r * 0.24, cy + core_r * 0.24), QPointF(cx + core_r * 0.24, cy - core_r * 0.24))

            # Orbiting dust around disk.
            painter.setPen(Qt.NoPen)
            for i, (base_angle, orbit_mul, size_mul, alpha, speed_mul) in enumerate(self._dust):
                angle = math.radians(base_angle + self._phase * (0.58 + (i % 7) * 0.038) * speed_mul)
                orbit = (disk_r + 20) * orbit_mul
                x = cx + math.cos(angle) * orbit
                y = cy + math.sin(angle) * orbit * 0.375
                if abs(x - cx) < core_r * 0.88 and abs(y - cy) < core_r * 0.88:
                    continue
                particle_size = 0.78 * size_mul
                if i % 4 == 0:
                    color = QColor(255, 222, 173, alpha)
                elif i % 5 == 0:
                    color = QColor(220, 214, 255, max(16, int(alpha * 0.72)))
                else:
                    color = QColor(238, 238, 244, max(14, int(alpha * 0.56)))
                painter.setBrush(color)
                painter.drawEllipse(QRectF(x - particle_size / 2, y - particle_size / 2, particle_size, particle_size))
        finally:
            painter.end()


# ─────────────────────────────────────────────
#  TYPING INDICATOR  (pure QPainter)
# ─────────────────────────────────────────────
class TypingIndicator(QWidget):
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
        # bubble bg
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#1C1C30"))
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        p.drawPath(path)
        # border
        p.setPen(QPen(QColor("#2E2E50"), 1))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)
        p.setPen(Qt.NoPen)
        # dots
        dot_r   = 5
        spacing = 17
        sx      = (self.width() - spacing * 2 - dot_r * 2) // 2
        cy      = self.height() // 2
        for i in range(3):
            dy    = -4 if i == self._phase else 0
            color = QColor("#9B8BFF") if i == self._phase else QColor("#33334A")
            p.setBrush(color)
            p.drawEllipse(sx + i * spacing, cy - dot_r + dy, dot_r * 2, dot_r * 2)
        p.end()


# ─────────────────────────────────────────────
#  EMOJI PICKER POPUP  (pure QPainter bg)
# ─────────────────────────────────────────────

class PromptCard(QFrame):
    """Clickable welcome prompt card. Dipisah dari QFrame biasa supaya card bisa mengisi input_text."""
    clicked = pyqtSignal(str)

    def __init__(self, icon, title, desc, prompt, parent=None):
        super().__init__(parent)
        self.prompt = prompt
        self.setObjectName("featureCard")
        self.setFixedSize(162, 96)
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
        ico.setObjectName("featureCardIcon")
        ico.setFixedHeight(26)
        top.addWidget(ico)
        top.addStretch()

        sparkle = QLabel("✦")
        sparkle.setStyleSheet("color:#8B5CF6; background:transparent; font-size:18px; font-weight:800;")
        top.addWidget(sparkle)
        lay.addLayout(top)

        ttl = QLabel(title)
        ttl.setObjectName("featureCardTitle")
        ttl.setWordWrap(True)
        lay.addWidget(ttl)

        dsc = QLabel(desc)
        dsc.setObjectName("featureCardDesc")
        dsc.setWordWrap(True)
        lay.addWidget(dsc)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.prompt)
            event.accept()
            return
        super().mouseReleaseEvent(event)

class EmojiPickerPopup(QFrame):
    emoji_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

        # 3 rows × 6 columns (18 emoji total)
        grid = QHBoxLayout(self)
        grid.setContentsMargins(10, 8, 10, 8)
        grid.setSpacing(0)

        cols_per_row = 6
        row1 = QHBoxLayout(); row1.setSpacing(2)
        row2 = QHBoxLayout(); row2.setSpacing(2)
        row3 = QHBoxLayout(); row3.setSpacing(2)

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
                QPushButton:hover { background-color: #2C2853; }
            """)
            btn.clicked.connect(lambda _, e=emoji: self._pick(e))
            if idx < cols_per_row:
                row1.addWidget(btn)
            elif idx < cols_per_row * 2:
                row2.addWidget(btn)
            else:
                row3.addWidget(btn)

        vlay = QVBoxLayout()
        vlay.setSpacing(2)
        vlay.addLayout(row1)
        vlay.addLayout(row2)
        vlay.addLayout(row3)
        grid.addLayout(vlay)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor("#111120"))
        p.setPen(QPen(QColor("#2A2A45"), 1))
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
class ReactionBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._liked     = False
        self._disliked  = False
        self._loved     = False
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
        btn.setObjectName("reactionBtn")
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
        popup = EmojiPickerPopup()
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
                    background-color: #252246;
                    color: #C4B5FD;
                    border: 1px solid #3A3A5C;
                    border-radius: 12px;
                    padding: 0 10px;
                }
                QPushButton:hover {
                    background-color: #39346E;
                    border: 1px solid #7C6EF5;
                }
            """)
            chip.clicked.connect(lambda _, e=emoji: self._add_reaction(e))
            self.chips_l.addWidget(chip)


# ─────────────────────────────────────────────
#  CHAT BUBBLE
# ─────────────────────────────────────────────
class _MessageBubbleFrame(QFrame):
    """Purple V2-like connected bubble: avatar-attached, dark, rounded, and smooth."""
    def __init__(self, is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.setObjectName("bubbleUser" if is_user else "bubbleAI")

    def paintEvent(self, event):
        p = QPainter(self)
        if not p.isActive():
            return
        try:
            p.setRenderHint(QPainter.Antialiasing, True)
            p.setRenderHint(QPainter.SmoothPixmapTransform, True)
            if hasattr(QPainter, "HighQualityAntialiasing"):
                p.setRenderHint(QPainter.HighQualityAntialiasing, True)

            w, h = max(1, self.width()), max(1, self.height())
            tail = 18.0
            pad = 2.0
            radius = 25.0

            if self.is_user:
                body = QRectF(pad, pad, w - tail - pad * 2, h - pad * 2)
                connector = QRectF(w - tail - 16, h * 0.5 - 18, 34, 36)
                shadow_connector = QRectF(connector.x() + 1, connector.y() + 4, connector.width(), connector.height())
                c0, c1, c2 = QColor(76, 29, 149, 242), QColor(38, 24, 76, 246), QColor(12, 10, 24, 248)
                border0, border1 = QColor(216, 180, 254, 116), QColor(124, 58, 237, 62)
                shine0, shine1 = QColor(255, 255, 255, 20), QColor(216, 180, 254, 38)
            else:
                body = QRectF(tail + pad, pad, w - tail - pad * 2, h - pad * 2)
                connector = QRectF(-1, h * 0.5 - 18, 34, 36)
                shadow_connector = QRectF(connector.x() + 1, connector.y() + 4, connector.width(), connector.height())
                c0, c1, c2 = QColor(31, 28, 48, 244), QColor(17, 15, 31, 248), QColor(8, 8, 18, 250)
                border0, border1 = QColor(196, 181, 253, 76), QColor(109, 40, 217, 42)
                shine0, shine1 = QColor(255, 255, 255, 15), QColor(167, 139, 250, 30)

            # contained shadow, so it looks lifted without dirty glow.
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(0, 0, 0, 68))
            p.drawRoundedRect(QRectF(body.x() + 1.5, body.y() + 4.0, body.width(), body.height()), radius, radius)
            p.drawEllipse(shadow_connector)

            grad = QLinearGradient(body.topLeft(), body.bottomRight())
            grad.setColorAt(0.00, c0)
            grad.setColorAt(0.56, c1)
            grad.setColorAt(1.00, c2)
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(body, radius, radius)
            p.drawEllipse(connector)

            # Thin premium top highlight.
            shine = QLinearGradient(body.topLeft(), body.topRight())
            shine.setColorAt(0.0, shine0)
            shine.setColorAt(0.52, shine1)
            shine.setColorAt(1.0, QColor(255, 255, 255, 10))
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QBrush(shine), 1.0))
            p.drawRoundedRect(QRectF(body.x() + 1.0, body.y() + 1.0, body.width() - 2.0, body.height() - 2.0), radius, radius)

            border = QLinearGradient(body.topLeft(), body.bottomRight())
            border.setColorAt(0.0, border0)
            border.setColorAt(1.0, border1)
            p.setPen(QPen(QBrush(border), 1.15))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(body, radius, radius)
            p.drawEllipse(connector)
        finally:
            p.end()


class ChatBubble(QWidget):
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
            rrow.addWidget(ReactionBar())
            rrow.addStretch()
            outer.addLayout(rrow)

    def _avatar(self, user=True):
        """Create bigger connected avatar with premium purple halo."""
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

        center = QPointF(outer_size / 2, outer_size / 2)
        halo = QRadialGradient(center, outer_size / 2)
        if user:
            halo.setColorAt(0.00, QColor(216, 180, 254, 86))
            halo.setColorAt(0.62, QColor(124, 58, 237, 48))
        else:
            halo.setColorAt(0.00, QColor(167, 139, 250, 76))
            halo.setColorAt(0.62, QColor(31, 28, 48, 50))
        halo.setColorAt(1.00, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(halo))
        painter.drawEllipse(QRectF(0, 0, outer_size, outer_size))

        ix = (outer_size - inner_size) / 2
        iy = (outer_size - inner_size) / 2
        border_color = QColor("#D8B4FE") if user else QColor("#A78BFA")
        painter.setPen(QPen(border_color, 2.35))
        painter.setBrush(QColor(10, 8, 22, 232))
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
            painter.setPen(QColor("#F5F3FF"))
            painter.setFont(QFont("Segoe UI", 15 if not user else 12, QFont.Bold))
            painter.drawText(QRectF(ix, iy, inner_size, inner_size), Qt.AlignCenter, "✦" if not user else "U")

        painter.end()
        av.setPixmap(result)
        return av

    def _bubble(self):
        f = _MessageBubbleFrame(is_user=self.is_user)
        f.setMaximumWidth(560)
        f.setMinimumWidth(170)
        lay = QVBoxLayout(f)
        if self.is_user:
            lay.setContentsMargins(18, 12, 34, 13)
        else:
            lay.setContentsMargins(34, 12, 18, 13)
        lay.setSpacing(4)

        meta = QLabel(("YOU" if self.is_user else "ASSISTANT") + "  " + datetime.now().strftime("%H:%M"))
        meta.setAlignment(Qt.AlignLeft)
        meta.setStyleSheet("""
            QLabel {
                color: rgba(216, 180, 254, 150);
                font-size: 9px;
                font-weight: 820;
                letter-spacing: 0.9px;
                font-family: 'Segoe UI';
                background-color: transparent;
            }
        """)
        lay.addWidget(meta)

        lbl = QLabel(self.message)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl.setObjectName("bubbleUserText" if self.is_user else "bubbleAIText")
        lbl.setStyleSheet("""
            QLabel {
                color: #F5F3FF;
                font-size: 14px;
                font-weight: 680;
                line-height: 1.35;
                font-family: 'Segoe UI';
                background-color: transparent;
            }
        """)
        lbl.setFont(QFont("Segoe UI", 14, QFont.DemiBold))
        lay.addWidget(lbl)
        return f



# ─────────────────────────────────────────────
#  SEND BUTTON (SVG icon from ai_bar folder)
# ─────────────────────────────────────────────
class _SendButton(QPushButton):
    """Send button — icon di-render manual via paintEvent, 100% center."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("btnSend")
        self.setFixedSize(38, 38)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Send message (Ctrl+Enter)")
        self._bg_normal   = QColor("#7C3AED")
        self._bg_hover    = QColor("#8B5CF6")
        self._bg_pressed  = QColor("#6D28D9")
        self._bg_disabled = QColor("#1E1C32")
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
        # Background circle
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
        # Icon — manual center
        icon = self.icon()
        if not icon.isNull():
            sz   = self.iconSize()
            x    = (r.width()  - sz.width())  // 2
            y    = (r.height() - sz.height()) // 2
            from PyQt5.QtCore import QRect as _QRect
            icon.paint(p, _QRect(x, y, sz.width(), sz.height()))
        p.end()


# ─────────────────────────────────────────────
#  ATTACH ICON  (pure QPainter — modern image gallery icon)
# ─────────────────────────────────────────────
class _AttachIcon(QWidget):
    """Ikon attach custom: modern image gallery icon via QPainter."""
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

        # Background circle
        if self._active:
            bg = QColor(124, 110, 245, 60)
            border = QColor("#7C6EF5")
        elif self._hovered:
            bg = QColor(124, 110, 245, 40)
            border = QColor("#6B5CE7")
        else:
            bg = QColor(0, 0, 0, 0)
            border = QColor(0, 0, 0, 0)

        p.setBrush(bg)
        p.setPen(QPen(border, 1))
        p.drawRoundedRect(1, 1, s - 2, s - 2, 9, 9)

        # Draw modern gallery/image icon (stacked cards style)
        icon_color = QColor("#9B8BFF") if (self._active or self._hovered) else QColor("#44445A")
        
        pen = QPen(icon_color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        
        cx = s / 2
        cy = s / 2
        
        # Back card (smaller, offset)
        back_w = s * 0.42
        back_h = s * 0.38
        back_x = cx - back_w / 2 + 2.5
        back_y = cy - back_h / 2 - 2.5
        p.drawRoundedRect(int(back_x), int(back_y), int(back_w), int(back_h), 3, 3)
        
        # Front card (larger, main)
        front_w = s * 0.50
        front_h = s * 0.45
        front_x = cx - front_w / 2 - 1.5
        front_y = cy - front_h / 2 + 1.5
        p.drawRoundedRect(int(front_x), int(front_y), int(front_w), int(front_h), 4, 4)
        
        # Small circle (sun/dot) in front card
        dot_r = s * 0.08
        dot_x = front_x + front_w * 0.28
        dot_y = front_y + front_h * 0.30
        p.setBrush(QBrush(icon_color))
        p.setPen(Qt.NoPen)
        p.drawEllipse(int(dot_x - dot_r/2), int(dot_y - dot_r/2), int(dot_r), int(dot_r))
        
        # Mountain line in front card (simple diagonal)
        p.setPen(QPen(icon_color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        mountain_path = QPainterPath()
        mountain_path.moveTo(front_x + 2, front_y + front_h - 2)
        mountain_path.lineTo(front_x + front_w * 0.35, front_y + front_h * 0.55)
        mountain_path.lineTo(front_x + front_w * 0.65, front_y + front_h * 0.70)
        mountain_path.lineTo(front_x + front_w - 2, front_y + front_h - 2)
        p.drawPath(mountain_path)
        
        p.end()


# ─────────────────────────────────────────────
#  ROUNDED PHOTO LABEL  (pure QPainter)
# ─────────────────────────────────────────────
class _RoundPhotoLabel(QWidget):
    """Load sfx.jpeg dan tampilkan sebagai lingkaran dengan purple stroke."""
    def __init__(self, path: str, size: int = 110, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size + 8, size + 8)  # +8 for border space

        self._pixmap = QPixmap()
        raw = QPixmap(path)
        if not raw.isNull():
            scaled = raw.scaled(size, size,
                                Qt.KeepAspectRatioByExpanding,
                                Qt.SmoothTransformation)
            x = (scaled.width()  - size) // 2
            y = (scaled.height() - size) // 2
            self._pixmap = scaled.copy(x, y, size, size)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        s    = self._size
        off  = 4   # border offset
        total = s + off * 2

        # Purple stroke ring (outer border)
        p.setPen(QPen(QColor("#9B8BFF"), 3))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(1, 1, total - 2, total - 2)

        # Dark gap ring
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#0D0D14"))
        p.drawEllipse(3, 3, total - 6, total - 6)

        # Photo clipped to circle
        clip = QPainterPath()
        clip.addEllipse(off, off, s, s)
        p.setClipPath(clip)

        if not self._pixmap.isNull():
            p.drawPixmap(off, off, self._pixmap)
        else:
            # Fallback gradient circle
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
#  AI MODELS LIST  (dummy — for model selector popup)
# ─────────────────────────────────────────────
_AI_MODELS_V1 = [
    {
        "id": "GPT-4o-mini",
        "name": "GPT-4o mini",
        "provider": "OpenAI",
        "badge": "FAST",
        "badge_color": "#4ADE80",
        "badge_bg": "#0D2E1A",
        "desc": "Lightweight, quick everyday tasks",
        "svg": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke="#4ADE80" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
        "color": "#4ADE80",
    },
    {
        "id": "GPT-4o",
        "name": "GPT-4o",
        "provider": "OpenAI",
        "badge": "POWERFUL",
        "badge_color": "#A78BFA",
        "badge_bg": "#1E1040",
        "desc": "Flagship multimodal, image + text",
        "svg": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="3" stroke="#A78BFA" stroke-width="1.8"/>
  <path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12" stroke="#A78BFA" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",
        "color": "#A78BFA",
    },
    {
        "id": "o1-mini",
        "name": "o1 mini",
        "provider": "OpenAI · Reasoning",
        "badge": "REASONING",
        "badge_color": "#F472B6",
        "badge_bg": "#2A0D20",
        "desc": "Chain-of-thought, math & code",
        "svg": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h18" stroke="#F472B6" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
        "color": "#F472B6",
    },
    {
        "id": "claude-3-5-haiku",
        "name": "Claude 3.5 Haiku",
        "provider": "Anthropic",
        "badge": "EFFICIENT",
        "badge_color": "#FBBF24",
        "badge_bg": "#231A00",
        "desc": "Fast, compact, cost-effective",
        "svg": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3C7.03 3 3 7.03 3 12s4.03 9 9 9 9-4.03 9-9" stroke="#FBBF24" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M12 8v4l3 3" stroke="#FBBF24" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="18.5" cy="5.5" r="2.5" fill="#FBBF24" opacity="0.3" stroke="#FBBF24" stroke-width="1.4"/>
</svg>""",
        "color": "#FBBF24",
    },
    {
        "id": "gemini-2.0-flash",
        "name": "Gemini 2.0 Flash",
        "provider": "Google DeepMind",
        "badge": "LONG CTX",
        "badge_color": "#38BDF8",
        "badge_bg": "#0C2233",
        "desc": "1M token context, multimodal",
        "svg": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 6h16M4 10h10M4 14h13M4 18h8" stroke="#38BDF8" stroke-width="1.8" stroke-linecap="round"/>
  <circle cx="19" cy="17" r="3" stroke="#38BDF8" stroke-width="1.6"/>
  <path d="M19 15.5v1.5l1 1" stroke="#38BDF8" stroke-width="1.4" stroke-linecap="round"/>
</svg>""",
        "color": "#38BDF8",
    },
]


class _SVGIconLabel(QWidget):
    """Renders SVG string via QSvgRenderer onto a circular background."""
    def __init__(self, svg_str: str, size: int = 36, parent=None):
        super().__init__(parent)
        self._size = size
        self._svg  = svg_str
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
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#1A1A30"))
        p.drawEllipse(0, 0, self._size, self._size)
        if not self._pixmap.isNull():
            offset = 6
            p.drawPixmap(offset, offset,
                         self._size - offset * 2, self._size - offset * 2,
                         self._pixmap)
        p.end()


class ModelSelectorPopup(QFrame):
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
        inner.setObjectName("modelPopupInner")
        inner.setStyleSheet("""
            QWidget#modelPopupInner {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(18, 18, 28, 248),
                    stop:0.55 rgba(12, 13, 22, 248),
                    stop:1 rgba(8, 9, 16, 248));
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
            color: #F5F3FF;
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

        for model in _AI_MODELS_V1:
            inner_lay.addWidget(self._make_model_btn(model))

        lay.addWidget(inner)

    def _make_model_btn(self, model: dict):
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(54)

        is_active = (model["id"] == self.current_model_id)
        if is_active:
            bg_color = "rgba(124, 58, 237, 72)"
            border_color = "rgba(167, 139, 250, 96)"
            side_alpha = 180
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
                background-color: rgba(30, 27, 48, 165);
                border: 1px solid rgba(167, 139, 250, 68);
            }}
            QPushButton:pressed {{
                background-color: rgba(24, 22, 38, 220);
            }}
        """)

        row = QHBoxLayout(btn)
        row.setContentsMargins(10, 7, 10, 7)
        row.setSpacing(10)

        # Soft left accent. Satu aksen saja supaya popup tidak terasa warna-warni/nabrak.
        accent_bar = QFrame()
        accent_bar.setFixedSize(3, 30)
        accent_bar.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(167, 139, 250, {side_alpha});
                border-radius: 2px;
            }}
        """)
        row.addWidget(accent_bar)

        icon_lbl = QLabel("AI")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFixedSize(30, 30)
        icon_lbl.setStyleSheet("""
            QLabel {
                color: #D8D2FF;
                background-color: rgba(15, 23, 42, 160);
                border: 1px solid rgba(167, 139, 250, 48);
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
                color: #C4B5FD;
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

# ─────────────────────────────────────────────
#  MAIN CHAT WIDGET
# ─────────────────────────────────────────────
class AIChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image    = None
        self.typing_widget    = None
        self.chat_started     = False
        self._typing_row_w    = None
        self._current_model_id = "GPT-4o-mini"
        self._model_btn       = None
        self._setup_ui()

    def _compact_model_label(self, model_id: str, model_name: str = None) -> str:
        labels = {
            "GPT-4o-mini": "4o mini",
            "GPT-4o": "4o",
            "o1-mini": "o1 mini",
            "claude-3-5-haiku": "Haiku",
            "gemini-2.0-flash": "Gemini",
        }
        if model_id in labels:
            return labels[model_id]
        name = model_name or model_id or "AI"
        return name if len(name) <= 11 else name[:10] + "…"

    def _on_model_changed(self, model_id: str, model_name: str):
        self._current_model_id = model_id
        if self._model_btn:
            self._model_btn.setText(f"{self._compact_model_label(model_id, model_name)} ▾")
            self._model_btn.setToolTip(f"Current model: {model_name} ({model_id})")
        logger.info(f"[v1] Model switched → {model_id}")

    def _setup_ui(self):
        root = _AlisaGradientRoot()
        root.setStyleSheet(GLOBAL_STYLE + ALISA_STYLE_PATCH)

        rl = QVBoxLayout(self)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        rl.addWidget(root)

        il = QVBoxLayout(root)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(0)
        il.addWidget(self._build_header())

        # Scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("chatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.viewport().setAutoFillBackground(False)
        self.scroll_area.viewport().setStyleSheet("background: transparent;")

        self.chat_container = QWidget()
        self.chat_container.setObjectName("chatScrollAreaWidget")
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

    def _create_header_avatar(self, path: str, size: int = 38):
        """Create circular avatar for header with photo and purple stroke."""
        av = QLabel()
        av.setFixedSize(size, size)
        av.setAlignment(Qt.AlignCenter)
        
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            # Create circular mask with purple stroke
            scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (scaled.width() - size) // 2
            y = (scaled.height() - size) // 2
            cropped = scaled.copy(x, y, size, size)
            
            # Apply circular mask with stroke
            result = QPixmap(size, size)
            result.fill(Qt.transparent)
            painter = QPainter(result)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # Draw purple stroke (border)
            stroke_pen = QPen(QColor("#9B8BFF"), 2.5)
            painter.setPen(stroke_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(1, 1, size - 2, size - 2)
            
            # Clip to circle and draw image
            path_circle = QPainterPath()
            path_circle.addEllipse(2, 2, size - 4, size - 4)
            painter.setClipPath(path_circle)
            painter.drawPixmap(2, 2, size - 4, size - 4, cropped)
            painter.end()
            
            av.setPixmap(result)
        else:
            # Fallback to icon
            av.setObjectName("avatarAI")
            av.setText("✦")
            av.setFont(QFont("Segoe UI", 16))
        
        return av

    # ── HEADER ──────────────────────────────
    def _build_header(self):
        h = QWidget()
        h.setObjectName("chatHeader")
        h.setFixedHeight(64)
        h.setStyleSheet("""
            QWidget#chatHeader {
                background-color: transparent;
                border: none;
            }
            QPushButton#headerIconButton {
                background-color: transparent;
                color: #EDE9FE;
                border: none;
                border-radius: 19px;
                font-size: 25px;
                font-weight: 700;
                font-family: 'Segoe UI';
                text-align: center;
                padding: 0px;
            }
            QPushButton#headerIconButton:hover {
                background-color: rgba(167, 139, 250, 28);
                color: #FFFFFF;
            }
            QPushButton#headerIconButton:pressed {
                background-color: rgba(124, 58, 237, 58);
            }
            QLabel#chatHeaderName {
                color: #F5F3FF;
                font-size: 14px;
                font-weight: 780;
                font-family: 'Segoe UI';
                background-color: transparent;
                letter-spacing: 0.2px;
            }
            QPushButton#clearChatButton {
                background-color: rgba(23, 18, 38, 118);
                color: #D8B4FE;
                border: 1px solid rgba(196, 181, 253, 34);
                border-radius: 14px;
                padding: 0px 12px;
                font-size: 11px;
                font-weight: 760;
                font-family: 'Segoe UI';
                text-align: center;
            }
            QPushButton#clearChatButton:hover {
                background-color: rgba(46, 32, 82, 138);
                border: 1px solid rgba(196, 181, 253, 58);
                color: #F5F3FF;
            }
            QPushButton#clearChatButton:pressed {
                background-color: rgba(76, 29, 149, 125);
            }
        """)

        lay = QHBoxLayout(h)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(8)

        back = QPushButton("‹")
        back.setObjectName("headerIconButton")
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
        title.setObjectName("chatHeaderName")
        title.setAlignment(Qt.AlignCenter)
        title_box.addWidget(title)

        lay.addLayout(title_box)
        lay.addStretch(1)

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("clearChatButton")
        clear_btn.setFixedSize(62, 32)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setToolTip("Clear chat")
        clear_btn.clicked.connect(self._clear_chat)
        lay.addWidget(clear_btn)
        return h

    # ── INPUT BAR ───────────────────────────
    def _build_input_bar(self):
        """Gemini-style compact input pill.
        Dibuat single-row supaya tidak ada kesan 2 kotakan / papan ketik terlalu tinggi.
        SVG icon tetap dipakai: model, attach, voice, send.
        """
        bar = QWidget()
        bar.setObjectName("chatInputBar")
        bar.setStyleSheet("""
            QWidget#chatInputBar {
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
                color: #C4B5FD;
                background-color: rgba(20, 15, 34, 220);
                border: 1px solid rgba(167, 139, 250, 85);
                border-radius: 9px;
                padding: 5px 10px;
                font-size: 10px;
                font-family: 'Segoe UI';
            }
        """)
        self.lbl_image.hide()
        lay.addWidget(self.lbl_image)

        # ── CLEAN SINGLE PILL ──────────────────────────────────────
        pill = QFrame()
        pill.setObjectName("modernInputPill")
        pill.setFixedHeight(54)
        pill.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pill.setStyleSheet("""
            QFrame#modernInputPill {
                background-color: rgba(18, 18, 27, 238);
                border: 1px solid rgba(214, 206, 255, 42);
                border-radius: 27px;
            }
            QFrame#modernInputPill:hover {
                background-color: rgba(22, 21, 33, 242);
                border: 1px solid rgba(196, 181, 253, 72);
            }
            QPushButton#pillIconBtn,
            QPushButton#modelDropdownBtn {
                background-color: transparent;
                border: none;
                border-radius: 17px;
                padding: 0px;
            }
            QPushButton#pillIconBtn:hover,
            QPushButton#modelDropdownBtn:hover {
                background-color: rgba(139, 92, 246, 42);
            }
            QPushButton#pillIconBtn:pressed,
            QPushButton#modelDropdownBtn:pressed {
                background-color: rgba(109, 40, 217, 70);
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

        # Text input dibuat pendek seperti Gemini search/chat bar
        self.input_text = QTextEdit()
        self.input_text.setObjectName("chatInput")
        self.input_text.setPlaceholderText("Minta AI Assistant")
        self.input_text.setFixedHeight(36)
        self.input_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_text.setFont(QFont("Segoe UI", 14))
        self.input_text.setStyleSheet("""
            QTextEdit#chatInput {
                background-color: transparent;
                border: none;
                color: #F5F3FF;
                padding: 7px 2px 0px 2px;
                font-size: 14px;
                font-weight: 400;
                font-family: 'Segoe UI';
                selection-background-color: #7C3AED;
                selection-color: #FFFFFF;
            }
            QTextEdit#chatInput:disabled { color: #5A5A72; }
        """)
        pill_layout.addWidget(self.input_text, 1)

        # Model button dibuat compact-chip: teks model tidak kepotong, tapi tetap hemat ruang.
        model_btn = QPushButton()
        model_btn.setObjectName("modelDropdownBtn")
        model_btn.setFixedHeight(34)
        model_btn.setMinimumWidth(104)
        model_btn.setMaximumWidth(116)
        model_btn.setCursor(Qt.PointingHandCursor)
        model_btn.setText(f"{self._compact_model_label(getattr(self, '_current_model_id', 'GPT-4o-mini'), 'GPT-4o mini')}")
        model_btn.setToolTip("Current model: GPT-4o mini")
        model_btn.setStyleSheet("""
            QPushButton#modelDropdownBtn {
                background-color: rgba(255, 255, 255, 7);
                color: #D8D2FF;
                border: 1px solid rgba(167, 139, 250, 42);
                border-radius: 17px;
                padding: 0px 10px;
                font-size: 11px;
                font-weight: 750;
                font-family: 'Segoe UI';
                text-align: center;
            }
            QPushButton#modelDropdownBtn:hover {
                background-color: rgba(124, 58, 237, 42);
                border: 1px solid rgba(196, 181, 253, 82);
                color: #F5F3FF;
            }
            QPushButton#modelDropdownBtn:pressed {
                background-color: rgba(109, 40, 217, 74);
            }
        """)
        try:
            from app.helpers import _svg_icon
            _nm_icon = _svg_icon(_ai_name_icon_path, "#C4B5FD", 14)
            if not _nm_icon.isNull():
                model_btn.setIcon(_nm_icon)
                model_btn.setIconSize(QSize(14, 14))
        except Exception:
            pass
        self._model_btn = model_btn

        def _show_model_popup_v1():
            popup = ModelSelectorPopup(getattr(self, '_current_model_id', 'GPT-4o-mini'))
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

        model_btn.clicked.connect(_show_model_popup_v1)
        pill_layout.addWidget(model_btn)

        # Attach / add icon button
        self.btn_attach = QPushButton()
        self.btn_attach.setObjectName("pillIconBtn")
        self.btn_attach.setFixedSize(34, 34)
        self.btn_attach.setCursor(Qt.PointingHandCursor)
        self.btn_attach.setToolTip("Attach image")
        try:
            from app.helpers import _svg_icon
            _add_icon = _svg_icon(_add_icon_path, "#9CA3AF", 18)
            if not _add_icon.isNull():
                self.btn_attach.setIcon(_add_icon)
                self.btn_attach.setIconSize(QSize(18, 18))
        except Exception:
            self.btn_attach.setText("＋")
        self.btn_attach.clicked.connect(self._attach_image)

        def _set_active(state):
            try:
                from app.helpers import _svg_icon
                _color = "#C4B5FD" if state else "#9CA3AF"
                _ic = _svg_icon(_add_icon_path, _color, 18)
                if not _ic.isNull():
                    self.btn_attach.setIcon(_ic)
                    self.btn_attach.setIconSize(QSize(18, 18))
            except Exception:
                pass
        self.btn_attach.set_active = _set_active
        pill_layout.addWidget(self.btn_attach)

        # Voice icon button
        btn_voice = QPushButton()
        btn_voice.setObjectName("pillIconBtn")
        btn_voice.setFixedSize(34, 34)
        btn_voice.setCursor(Qt.PointingHandCursor)
        btn_voice.setToolTip("Voice input")
        try:
            from app.helpers import _svg_icon
            _voice_icon = _svg_icon(_voice_icon_path, "#9CA3AF", 18)
            if not _voice_icon.isNull():
                btn_voice.setIcon(_voice_icon)
                btn_voice.setIconSize(QSize(18, 18))
        except Exception:
            btn_voice.setText("🎙")
        btn_voice.clicked.connect(lambda: self.input_text.setFocus())
        pill_layout.addWidget(btn_voice)

        # Send button
        self.btn_send = _SendButton()
        self.btn_send.setFixedSize(38, 38)
        try:
            from app.helpers import _svg_icon
            _send_icon = _svg_icon(_send_icon_path, "#FFFFFF", 18)
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
        self.welcome_widget = QWidget()
        self.welcome_widget.setStyleSheet("background: transparent;")
        wl = QVBoxLayout(self.welcome_widget)
        # Setting sama seperti V2 untuk konsistensi
        wl.setContentsMargins(0, 2, 0, 4)  # Top margin: 8 (sama dengan V2)
        wl.setSpacing(12)  # Spacing: 12 (sama dengan V2)
        wl.setAlignment(Qt.AlignHCenter)

        # Black hole size dikecilkan agar proporsi seimbang seperti V2
        orb = BlackHoleOrb(size=300)  # Dari 360 → 300 (sama dengan V2)
        wl.addWidget(orb, alignment=Qt.AlignHCenter)

        title = QLabel("Mulai dari apa?")
        title.setObjectName("welcomeTitle")
        title.setAlignment(Qt.AlignCenter)
        wl.addWidget(title)

        sub = QLabel("Tanya apa saja, kirim gambar, atau mulai dari rekomendasi cepat.")
        sub.setObjectName("welcomeSub")
        sub.setAlignment(Qt.AlignCenter)
        wl.addWidget(sub)

        self.welcome_cards_widget = QWidget()
        self.welcome_cards_widget.setStyleSheet("background: transparent;")
        cards = QHBoxLayout(self.welcome_cards_widget)
        cards.setContentsMargins(0, 4, 0, 0)
        cards.setSpacing(11)

        card_data = [
            ("🏠", "Ide dekor rumah", "Bikin konsep ruang yang estetik", "Bantu aku cari ide dekor rumah yang estetik, minimalis, dan realistis."),
            ("✨", "Buat prompt AI", "Prompt gambar/video siap pakai", "Buatkan prompt AI yang detail, cinematic, dan rapi."),
            ("🖼", "Analisis gambar", "Kirim foto lalu minta dibedah", "Aku ingin menganalisis gambar yang akan aku lampirkan."),
        ]
        for icon, title, desc, prompt in card_data:
            card = PromptCard(icon, title, desc, prompt)
            card.clicked.connect(self._use_prompt)
            cards.addWidget(card)
        wl.addWidget(self.welcome_cards_widget, alignment=Qt.AlignHCenter)

        self.chat_layout.addWidget(self.welcome_widget)

    # ── ACTIONS ─────────────────────────────
    def _use_prompt(self, prompt: str):
        self.input_text.setPlainText(prompt)
        self.input_text.setFocus()

    def _attach_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if path:
            self.current_image = path
            fname = os.path.basename(path)
            self.lbl_image.setText(f"🖼  {fname}")
            self.lbl_image.show()
            self.btn_attach.set_active(True)
            logger.info(f"Image attached: {fname}")

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

        self.ai_thread = AIRequestThread(message, self.current_image)
        self.ai_thread.response_received.connect(self._on_response)
        self.ai_thread.error_occurred.connect(self._on_error)
        self.ai_thread.start()

        self.current_image = None
        self.lbl_image.hide()
        self.lbl_image.setText("")
        self.btn_attach.set_active(False)
        logger.info(f"Sent: {message[:60]}…")

    def _add_bubble(self, message, is_user=True):
        self._pop_stretch()
        self.chat_layout.addWidget(ChatBubble(message, is_user))
        self.chat_layout.addStretch()
        QTimer.singleShot(80, self._scroll_bottom)

    def _show_typing(self):
        self._pop_stretch()
        rw = QWidget()
        rw.setStyleSheet("background-color: transparent;")
        rl = QHBoxLayout(rw)
        rl.setContentsMargins(46, 0, 0, 0)
        self.typing_widget = TypingIndicator()
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
        self._enable_input()

    def _on_error(self, msg):
        self._remove_typing()
        self._add_bubble(f"⚠️  {msg}", is_user=False)
        self._enable_input()

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
        self.chat_started = False
        self._add_welcome()
        self.chat_layout.addStretch()
        logger.info("Chat cleared")

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
