# 🎵 SoundWave Music Player v4.0

<div align="center">

![SoundWave](https://img.shields.io/badge/SoundWave-v4.0-purple?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![PyQt5](https://img.shields.io/badge/PyQt5-UI-green?style=for-the-badge&logo=qt)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Modern Music Player dengan UI yang Elegan dan Fitur Lengkap**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Changelog](#-changelog) • [Contributing](#-contributing)

</div>

---

## ✨ Features

### 🎨 Modern UI/UX
- **Smooth Animations** - Semua transisi menggunakan ease timing (0.2s)
- **Subtle Effects** - Hover effects dengan rgba opacity
- **SVG Icons** - Scalable vector icons dengan color tinting
- **Purple Theme** - Modern gradient purple color scheme
- **Responsive Design** - Adaptive layout untuk berbagai ukuran window

### 🎵 Core Features
- **Audio Playback** - Support MP3, WAV, OGG, FLAC
- **Queue Management** - Add, remove, reorder songs
- **Playlist Manager** - Create, edit, delete playlists
- **Favorites** - Mark songs as favorite dengan SVG icon
- **Recently Played** - Track listening history
- **Search** - Fast search dengan real-time results

### 🎛️ Audio Controls
- **Equalizer** - 10-band audio equalizer
- **Volume Control** - Smooth volume slider
- **Progress Bar** - Seekable progress dengan time display
- **Shuffle & Repeat** - Randomize dan loop playback
- **Keyboard Shortcuts** - Quick controls dengan hotkeys

### 🤖 AI Features
- **AI Chat (GPT-4o Mini)** - Chat dengan AI tentang musik
- **AI Chat V2 (Groq)** - Alternative AI chat engine
- **Music Quiz** - Test pengetahuan musik kamu
- **Smart Recommendations** - AI-powered song suggestions

> **⚠️ Catatan:** Fitur AI memerlukan API keys. Lihat [API Configuration](#-api-configuration) untuk setup.

### 📊 Statistics
- **Play Count** - Track berapa kali lagu diputar
- **Listening Time** - Total waktu mendengarkan
- **Top Songs** - Most played songs
- **Charts** - Visual statistics dengan graphs

### 🎤 Additional Features
- **Lyrics Display** - Show lyrics untuk lagu yang sedang diputar
- **Sleep Timer** - Auto-stop setelah waktu tertentu
- **Mood Colors** - Dynamic UI colors dari album art
- **Drag & Drop** - Drag file audio langsung ke aplikasi

---

## 🔐 API Configuration

### Setup API Keys

Aplikasi ini menggunakan AI features yang memerlukan API keys. API keys disimpan di file `.env` untuk keamanan.

#### 1. Copy Template
```bash
copy "rest api bot\.env.example" "rest api bot\.env"
```

#### 2. Edit File `.env`
Buka file `rest api bot/.env` dan isi dengan API keys kamu:

```env
# GPT-4o-mini API (untuk ai_chatbot.py)
GPT_API_URL=https://kyuu2nd.dev/api/ai/gpt-4o-mini

# Groq API (untuk ai_chatbot_v2.py)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions
```

#### 3. Dapatkan API Keys

**Groq API (Gratis):**
1. Kunjungi [console.groq.com](https://console.groq.com)
2. Daftar/login ke akun kamu
3. Buat API key baru
4. Copy dan paste ke file `.env`

#### 4. Keamanan

✅ File `.env` sudah ditambahkan ke `.gitignore`  
✅ API keys tidak akan ter-upload ke Git  
✅ Aman untuk share repository tanpa expose keys  
✅ `python-dotenv` akan auto-install via `running_system.py`

> **⚠️ PENTING:** Jangan pernah commit file `.env` ke Git! Gunakan `.env.example` sebagai template.

---

## 🚀 Installation

### Prerequisites
- Python 3.11 atau lebih baru
- Windows OS (tested on Windows 10/11)

### Quick Start

1. **Clone atau Download Repository**
```bash
git clone https://github.com/yourusername/soundwave.git
cd soundwave
```

2. **Setup API Configuration (PENTING!)**
```bash
# Copy template .env
copy "rest api bot\.env.example" "rest api bot\.env"

# Edit file .env dan isi dengan API keys kamu
# Untuk Groq API: dapatkan key dari https://console.groq.com
```

3. **Install Dependencies & Run**
```bash
python running_system.py
```

File `running_system.py` akan otomatis install semua dependencies termasuk `python-dotenv`.

### Alternative: Using start.bat
Double-click `start.bat` untuk menjalankan aplikasi langsung.

---

## 📖 Usage

### Basic Controls

#### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `→` | Next Song |
| `←` | Previous Song |
| `S` | Toggle Shuffle |
| `R` | Toggle Repeat |
| `L` | Toggle Like |

#### Adding Songs
1. **Method 1:** Click `＋ Add Song` button
2. **Method 2:** Drag & drop audio files ke window
3. **Method 3:** Import dari Library page

#### Creating Playlist
1. Go to **Playlist** page
2. Click `＋ New` button
3. Enter playlist name
4. Add songs dari library

#### Using AI Chat
1. Go to **AI Chat** page
2. Type your message
3. Get AI recommendations dan insights

---

## 🎨 UI Renovasi (v4.0)

### What's New?

#### ✅ Sidebar Navigation
- Smooth transition effects
- Subtle hover background (rgba opacity)
- TranslateX animation
- Larger border-radius (12px)

#### ✅ Favorite Icon
- SVG icons (`love.svg` & `love-filled.svg`)
- Scale animation on hover (1.08x)
- Smooth color transitions

#### ✅ Buttons
- Clear Queue: border-radius 18px
- Import Library: border-radius 16px
- Add Song: box-shadow on hover
- All buttons: smooth transitions

#### ✅ Console Logger
- Modern gradient colors
- Box borders (╔═╗)
- Decorative arrows (→)
- Better spacing

#### ✅ Drag & Drop
- Visual feedback
- Multiple files support
- Auto-add to queue

---

## 📁 Project Structure

```
soundwave/
├── app/
│   ├── player.py          # Main player class
│   ├── helpers.py         # Helper functions
│   └── __init__.py
├── features/
│   ├── lyrics.py          # Lyrics widget
│   ├── playlist.py        # Playlist manager
│   ├── quiz.py            # Music quiz
│   ├── recent.py          # Recently played
│   ├── sleep_timer.py     # Sleep timer
│   ├── stats.py           # Statistics
│   ├── theme.py           # Theme engine
│   └── __init__.py
├── widgets/
│   ├── equalizer.py       # Equalizer widget
│   └── __init__.py
├── rest api bot/          # 🔐 API Configuration
│   ├── .env               # API keys (JANGAN UPLOAD!)
│   └── .env.example       # Template untuk .env
├── icons/
│   └── svg/               # SVG icons
├── images/                # Images & photos
├── ai_chatbot.py          # AI chat (GPT-4o)
├── ai_chatbot_v2.py       # AI chat (Groq)
├── constants.py           # App constants
├── logger.py              # Console logger
├── main.py                # Entry point
├── running_system.py      # Auto-installer
├── styles.css             # Stylesheet
├── music_player.ui        # Qt UI file
├── .gitignore             # Git ignore rules
├── CHANGELOG.md           # Version history
├── IMPROVEMENT_SUGGESTIONS.md  # Future features
└── README.md              # This file
```

---

## 🎯 Roadmap

### High Priority
- [ ] Audio Visualizer (FFT spectrum)
- [ ] Mini Player Mode (floating window)
- [ ] Lyrics Sync (time-synced LRC)
- [ ] Theme Customization (light/dark mode)

### Medium Priority
- [ ] Smart Playlist Generator
- [ ] More Keyboard Shortcuts
- [ ] Context Menu (right-click)
- [ ] System Tray Integration

### Low Priority
- [ ] Cloud Sync
- [ ] Social Features
- [ ] Gesture Controls
- [ ] Performance Monitoring

Lihat `IMPROVEMENT_SUGGESTIONS.md` untuk detail lengkap.

---

## 🐛 Known Issues

1. ⚠️ Album art loading bisa lambat untuk file besar
2. ⚠️ Pygame mixer bisa crash jika file corrupt
3. ⚠️ Search bisa lambat jika 1000+ songs

### Workarounds
- Use smaller album art images
- Validate audio files before adding
- Use search filters untuk large libraries

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings untuk functions
- Test before committing
- Update CHANGELOG.md

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

**Redsilence Trashdex**  
UI/UX Engineer · Music Enthusiast

- 📧 Email: redsilence@gmail.com
- 🔗 Telegram First: [@bravo6core](https://t.me/bravo6core)
- 🔗 Telegram Second: [@bravo6core](https://t.me/redsilencesfx)

---

## 🙏 Acknowledgments

- **PyQt5** - UI Framework
- **Pygame** - Audio Engine
- **Colorama** - Console Colors
- **Requests** - HTTP Library

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/soundwave?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/soundwave?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/yourusername/soundwave?style=social)

---

## 🎵 Screenshots

### Home Page
Modern now playing interface dengan album art, controls, dan queue.

### Library
Browse semua lagu dengan search dan filter.

### Playlist Manager
Create dan manage playlists dengan drag & drop.

### AI Chat
Chat dengan AI untuk music recommendations.

### Statistics
Visual charts untuk listening habits.

---

## 💡 Tips & Tricks

### Performance
- Close unused pages untuk save memory
- Clear queue regularly
- Use playlists untuk organize songs

### Customization
- Edit `styles.css` untuk custom colors
- Modify `constants.py` untuk app settings
- Add custom SVG icons di `icons/svg/`

### Keyboard Shortcuts
- Learn shortcuts untuk faster navigation
- Use Space untuk quick play/pause
- Arrow keys untuk song navigation

---

## 🔧 Troubleshooting

### App Won't Start
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install --upgrade PyQt5 pygame colorama requests

# Run with verbose logging
python main.py --verbose
```

### Audio Not Playing
- Check audio file format (MP3, WAV, OGG, FLAC)
- Verify file is not corrupted
- Check system audio settings

### UI Issues
- Clear cache: delete `__pycache__` folders
- Reset settings: delete config files
- Reinstall PyQt5

---

## 📞 Support

Need help? Here's how to get support:

1. **Check Documentation** - Read this README and CHANGELOG
2. **Search Issues** - Look for similar problems
3. **Create Issue** - Open new issue dengan detail
4. **Contact Developer** - Email atau Telegram

---

<div align="center">

**Made with ❤️ and 🎵 by Redsilence Trashdex**

⭐ Star this repo if you like it!

</div>
