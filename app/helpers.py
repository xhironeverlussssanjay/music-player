import os
import sys

from PyQt5.QtCore import Qt, QByteArray, QRectF
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QPainterPath
from PyQt5.QtSvg import QSvgRenderer

import constants as C
import logger

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(*parts: str) -> str:
    """Resolve asset path tanpa mengubah tampilan.

    Urutan pencarian dibuat defensif supaya asset tetap kebaca walau project
    dipindah ke folder baru, dijalankan dari main.py, atau working directory beda.
    """
    candidates = [
        PROJECT_ROOT,
        os.getcwd(),
        os.path.dirname(os.path.abspath(sys.argv[0])) if sys.argv and sys.argv[0] else PROJECT_ROOT,
        os.path.dirname(PROJECT_ROOT),
        os.path.join(PROJECT_ROOT, "app"),
    ]
    for base in candidates:
        path = os.path.join(base, *parts)
        if os.path.exists(path):
            return path
    # fallback: root project, supaya warning path tetap mudah dibaca
    return os.path.join(PROJECT_ROOT, *parts)

def load_stylesheet(filename: str) -> str:
    """Baca file CSS dari folder yang sama dengan script ini."""
    base = PROJECT_ROOT
    path = resource_path(filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warn(f"File CSS '{filename}' tidak ditemukan!")
        return ""


def make_rounded_pixmap(path: str, size: int = C.ALBUM_ART_SIZE) -> QPixmap:
    """Buat QPixmap bulat/rounded dari path gambar."""
    raw = QPixmap(path)
    if raw.isNull():
        return QPixmap()
    raw = raw.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    x, y = (raw.width() - size) // 2, (raw.height() - size) // 2
    raw = raw.copy(x, y, size, size)
    result = QPixmap(size, size)
    result.fill(Qt.transparent)
    p = QPainter(result)
    p.setRenderHint(QPainter.Antialiasing)
    clip = QPainterPath()
    clip.addRoundedRect(0, 0, size, size, 14, 14)
    p.setClipPath(clip)
    p.drawPixmap(0, 0, raw)
    p.end()
    return result


def fmt_time(seconds: float) -> str:
    s = max(0, int(seconds))
    return f"{s // 60}:{s % 60:02d}"


def song_name(fp: str) -> str:
    return os.path.splitext(os.path.basename(fp))[0]

# ── SVG Icon Helper ────────────────────────────────────────────────────────────
def _svg_icon(svg_path: str, color_hex: str, size: int = 18) -> QIcon:
    """
    Load an SVG file, recolor it by replacing currentColor with color_hex,
    render to a QPixmap, and return as QIcon.
    Works with any stroke-based SVG that uses currentColor.
    """
    try:
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_data = f.read()
        # Replace currentColor with our target color
        svg_data = svg_data.replace("currentColor", color_hex)
        renderer = QSvgRenderer(QByteArray(svg_data.encode("utf-8")))
        px = QPixmap(size, size)
        px.fill(Qt.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        renderer.render(p, QRectF(0, 0, size, size))
        p.end()
        return QIcon(px)
    except Exception as e:
        logger.warn(f"SVG icon load failed: {svg_path} — {e}")
        return QIcon()
