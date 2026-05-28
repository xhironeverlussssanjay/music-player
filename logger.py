import time
import random
from datetime import datetime

# ── ANSI Color Codes (MODERN GRADIENT STYLE) ──────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
ITALIC  = "\033[3m"

# Foreground Colors
BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

# Bright Foreground (Modern Neon Style)
BGREEN   = "\033[92m"
BYELLOW  = "\033[93m"
BBLUE    = "\033[94m"
BMAGENTA = "\033[95m"
BCYAN    = "\033[96m"
BWHITE   = "\033[97m"

# Background Colors
BG_BLACK  = "\033[40m"
BG_GREEN  = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE   = "\033[44m"
BG_RED    = "\033[41m"
BG_PURPLE = "\033[45m"

# ── Modern Gradient Prefix Icons ──────────────────────────────────────────────
_PREFIX = {
    "BOOT"   : f"{BG_PURPLE}{BWHITE}{BOLD}  ♪  SOUNDWAVE  {RESET}",
    "PLAY"   : f"{BGREEN}{BOLD} ▶  PLAY     {RESET}",
    "PAUSE"  : f"{BYELLOW}{BOLD} ⏸  PAUSE    {RESET}",
    "NEXT"   : f"{BCYAN}{BOLD} ⏭  NEXT     {RESET}",
    "PREV"   : f"{BCYAN}{BOLD} ⏮  PREV     {RESET}",
    "LOAD"   : f"{BBLUE}{BOLD} ♫  LOAD     {RESET}",
    "ADD"    : f"{BGREEN}{BOLD} ＋  ADD      {RESET}",
    "LIKE"   : f"{BMAGENTA}{BOLD} ♥  LIKE     {RESET}",
    "UNLIKE" : f"{DIM} ♡  UNLIKE   {RESET}",
    "SHUFFLE": f"{BYELLOW}{BOLD} ⇄  SHUFFLE  {RESET}",
    "REPEAT" : f"{BYELLOW}{BOLD} ↺  REPEAT   {RESET}",
    "SEEK"   : f"{BCYAN}{BOLD} ◈  SEEK     {RESET}",
    "VOL"    : f"{BWHITE}{BOLD} 🔊  VOL      {RESET}",
    "NAV"    : f"{BMAGENTA}{BOLD} 🧭  NAV      {RESET}",
    "ART"    : f"{BMAGENTA}{BOLD} 🖼  ART      {RESET}",
    "END"    : f"{DIM} ■  END      {RESET}",
    "WARN"   : f"{BG_YELLOW}{BLACK}{BOLD} ⚠  WARN     {RESET}",
    "ERROR"  : f"{BG_RED}{BWHITE}{BOLD} ✖  ERROR    {RESET}",
    "INFO"   : f"{BCYAN}{BOLD} ℹ  INFO     {RESET}",
    "EXIT"   : f"{RED}{BOLD} ⏻  EXIT     {RESET}",
    "KEY"    : f"{BMAGENTA}{BOLD} ⌨  KEY      {RESET}",
    "CLEAR"  : f"{BYELLOW}{BOLD} ✕  CLEAR    {RESET}",
}

# ── AI Response Colors (Random) ───────────────────────────────────────────────
_AI_COLORS = [BGREEN, BCYAN, BMAGENTA, BYELLOW, BBLUE, BWHITE]

_PAGE_NAMES = {0: "Home Page", 1: "Search Bar", 2: "Library Music", 3: "Favorites Music", 4: "Gpt 4o Mini", 5: "Grok Ai", 6: "Playlist Manager", 7: "Recently Music", 8: "Music Quiz", 9: "Statistic Information", 10: "About Information"}


def _ts() -> str:
    """Timestamp pendek: HH:MM:SS"""
    return f"{DIM}{datetime.now().strftime('%H:%M:%S')}{RESET}"


def _divider():
    print(f"{DIM}{'─' * 56}{RESET}")


def _log(category: str, message: str):
    prefix = _PREFIX.get(category, f"[{category}]")
    print(f"  {_ts()}  {prefix}  {message}")


# ── Public API ────────────────────────────────────────────────────────────────

def boot():
    """Modern startup banner dengan gradient effect."""
    _divider()
    print(f"\n  {BG_PURPLE}{BWHITE}{BOLD}   ♪  SoundWave Music Player v4.0   {RESET}")
    print(f"  {BMAGENTA}║{RESET}  {BCYAN}🎵 Modern Music Experience{RESET} {BMAGENTA}║{RESET}")
    print(f"  {BMAGENTA}║{RESET}  {DIM}Powered : Redsilence{RESET} {BMAGENTA}║{RESET}\n")
    _log("INFO", f"{BCYAN}Aplikasi dimulai — {datetime.now().strftime('%A, %d %b %Y %H:%M')}{RESET}")
    _divider()


def song_added(name: str, total: int):
    _log("ADD", f"{BWHITE}{name}{RESET}  {DIM}(total: {total} lagu){RESET}")


def song_loaded(name: str, duration: str, index: int):
    _log("LOAD", f"{BWHITE}{name}{RESET}  {DIM}[{duration}]  #{index + 1}{RESET}")


def song_play(name: str):
    _log("PLAY", f"{BGREEN}{name}{RESET}")


def song_pause(name: str, elapsed: str):
    _log("PAUSE", f"{BWHITE}{name}{RESET}  {DIM}@ {elapsed}{RESET}")


def song_next(name: str):
    _log("NEXT", f"{BCYAN}{name}{RESET}")


def song_prev(name: str):
    _log("PREV", f"{BCYAN}{name}{RESET}")


def song_end(name: str):
    _log("END", f"{DIM}{name}{RESET}")


def song_seek(name: str, target_sec: float, duration: float):
    pct = int((target_sec / duration * 100) if duration > 0 else 0)
    bar_len = 20
    filled = int(bar_len * pct / 100)
    bar = f"{BGREEN}{'█' * filled}{RESET}{DIM}{'░' * (bar_len - filled)}{RESET}"
    _log("SEEK", f"{DIM}{name}{RESET}  [{bar}] {BGREEN}{pct}%{RESET}")


def like_added(name: str):
    _log("LIKE", f"{BMAGENTA}{name}{RESET} ♥")


def like_removed(name: str):
    _log("UNLIKE", f"{DIM}{name}{RESET}")


def shuffle_toggled(state: bool):
    if state:
        _log("SHUFFLE", f"{BGREEN}ON{RESET}")
    else:
        _log("SHUFFLE", f"{DIM}OFF{RESET}")


def repeat_toggled(state: bool):
    if state:
        _log("REPEAT", f"{BGREEN}ON{RESET}")
    else:
        _log("REPEAT", f"{DIM}OFF{RESET}")


def volume_changed(value: int):
    bar_len = 15
    filled = int(bar_len * value / 100)
    icon = "🔇" if value == 0 else "🔈" if value < 40 else "🔊"
    bar = f"{BGREEN}{'█' * filled}{RESET}{DIM}{'░' * (bar_len - filled)}{RESET}"
    _log("VOL", f"{icon} [{bar}] {BGREEN}{value}%{RESET}")


def nav_changed(page_index: int):
    name = _PAGE_NAMES.get(page_index, str(page_index))
    
    # Modern gradient colors untuk navigation
    nav_colors = [BMAGENTA, BCYAN, BGREEN, BYELLOW, BBLUE]
    random_color = random.choice(nav_colors)
    
    # Add decorative arrow
    _log("NAV", f"{random_color}→ {name}{RESET}")


def album_art_changed(path: str):
    import os
    _log("ART", f"{BMAGENTA}{os.path.basename(path)}{RESET}")


def queue_cleared(count: int):
    _log("CLEAR", f"{BYELLOW}Queue cleared ({count} songs){RESET}")


def key_shortcut(key: str, action: str):
    _log("KEY", f"{BCYAN}[{key}]{RESET}  →  {action}")


def warn(message: str):
    _log("WARN", f"{BYELLOW}{message}{RESET}")


def error(message: str):
    _log("ERROR", f"{RED}{message}{RESET}")


def info(message: str):
    _log("INFO", f"{DIM}{message}{RESET}")


def app_exit():
    _divider()
    print(f"{BYELLOW}👋 Thanks for using SoundWave!{RESET}")
    print(f"{BG_BLUE}See you next time...{RESET}")
    print()


# ── AI Chat Logger (Random Colors) ────────────────────────────────────────────

def ai_request(message: str):
    """Log AI request dengan warna random"""
    color = random.choice(_AI_COLORS)
    prefix = f"{color}{BOLD} ✦  AI REQ  {RESET}"
    preview = message[:50] + "..." if len(message) > 50 else message
    print(f"  {_ts()}  {prefix}  {DIM}{preview}{RESET}")


def ai_response(response: str, status_code: int = 200):
    """Log AI response dengan warna random"""
    color = random.choice(_AI_COLORS)
    prefix = f"{color}{BOLD} ✦  AI RES  {RESET}"
    preview = response[:60] + "..." if len(response) > 60 else response
    status_color = BGREEN if status_code == 200 else BYELLOW if status_code < 500 else RED
    print(f"  {_ts()}  {prefix}  {color}{preview}{RESET}  {status_color}[{status_code}]{RESET}")


def ai_error(error_msg: str):
    """Log AI error dengan warna merah"""
    prefix = f"{RED}{BOLD} ✦  AI ERR  {RESET}"
    print(f"  {_ts()}  {prefix}  {RED}{error_msg}{RESET}")