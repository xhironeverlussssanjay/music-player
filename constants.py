"""
CONFIGURATIONS SETTING

"""

# ── App Info ──────────────────────────────────────────────────────────────────
APP_NAME    = "SoundWave"
APP_VERSION = "4.0"
APP_TITLE   = f"{APP_NAME} Music Player v{APP_VERSION}"

# ── File Config ───────────────────────────────────────────────────────────────
UI_FILE  = "music_player.ui"
CSS_FILE = "styles.css"

# ── Audio ─────────────────────────────────────────────────────────────────────
AUDIO_FILTER   = "Audio Files (*.mp3 *.wav *.ogg *.flac)"
IMAGE_FILTER   = "Images (*.png *.jpg *.jpeg *.bmp)"
DEFAULT_VOLUME = 70
TIMER_INTERVAL = 500
END_CHECK_MS   = 300
PREV_RESTART_SEC = 3

# ── Palet Warna (Soft Purple) ─────────────────────────────────────────────────
COLOR_BG           = "#0A0A0F"
COLOR_SIDEBAR      = "#0F0F15"
COLOR_CARD         = "#141420"
COLOR_ACCENT       = "#A78BFA"
COLOR_ACCENT_HOVER = "#C4B5FD"
COLOR_ACCENT_DARK  = "#8B5CF6"
COLOR_TEXT         = "#E2E8F0"
COLOR_TEXT_DIM     = "#9CA3AF"
COLOR_TEXT_MUTED   = "#6B7280"
COLOR_BORDER       = "#1A1A28"
COLOR_PINK         = "#F472B6"

# ── Sidebar Nav Styles ────────────────────────────────────────────────────────
NAV_ACTIVE = (
    f"background-color: rgba(167, 139, 250, 0.15); color: {COLOR_ACCENT};"
    f"border-left: 3px solid {COLOR_ACCENT}; font-weight: bold;"
    "font-size: 13px; font-family: 'Segoe UI';"
    "text-align: left; padding: 11px 16px; border-radius: 12px;"
)
NAV_INACTIVE = (
    "background-color: transparent; color: #6B7280;"
    "border-left: 3px solid transparent;"
    "font-size: 13px; font-family: 'Segoe UI';"
    "text-align: left; padding: 11px 16px; border-radius: 12px; border: none;"
)

# ── Toggle Button Colors ──────────────────────────────────────────────────────
TOGGLE_ON_STYLE  = f"color: {COLOR_ACCENT};"
TOGGLE_OFF_STYLE = f"color: {COLOR_TEXT_MUTED};"
LIKE_ON_STYLE    = f"color: {COLOR_PINK};"
LIKE_OFF_STYLE   = f"color: {COLOR_TEXT_MUTED};"

# ── Album Art Size ────────────────────────────────────────────────────────────
ALBUM_ART_SIZE = 200

# ── Keyboard Shortcuts ────────────────────────────────────────────────────────
SHORTCUTS = {
    "Space"     : ("Play / Pause",  "toggle_play"),
    "Right"     : ("Next Song",     "next_song"),
    "Left"      : ("Prev Song",     "prev_song"),
    "S"         : ("Toggle Shuffle","toggle_shuffle"),
    "R"         : ("Toggle Repeat", "toggle_repeat"),
    "L"         : ("Toggle Like",   "toggle_like"),
}

# ── Page Indices ──────────────────────────────────────────────────────────────
PAGE_HOME      = 0
PAGE_SEARCH    = 1
PAGE_LIBRARY   = 2
PAGE_FAVORITES = 3
PAGE_AI_CHAT   = 4
PAGE_PLAYLIST  = 5
PAGE_RECENT    = 6
PAGE_QUIZ      = 7
PAGE_STATS     = 8
PAGE_ABOUT     = 9
PAGE_AI_CHAT_V2 = 10

PAGE_NAMES = {
    PAGE_HOME       : "Home",
    PAGE_SEARCH     : "Search",
    PAGE_LIBRARY    : "Library",
    PAGE_FAVORITES  : "Favorites",
    PAGE_AI_CHAT    : "AI Chat",
    PAGE_PLAYLIST   : "Playlist",
    PAGE_RECENT     : "Recently Played",
    PAGE_QUIZ       : "Music Quiz",
    PAGE_STATS      : "Stats",
    PAGE_ABOUT      : "About",
    PAGE_AI_CHAT_V2 : "AI Chat V2 (Groq)",
}