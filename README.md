# Siphon-TUI — Download audio/video from YouTube, SoundCloud, and 1000+ sites via interactive terminal UI

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![PyPI](https://img.shields.io/pypi/v/siphon-tui.svg)](https://pypi.org/project/siphon-tui/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey)]()
[![TUI](https://img.shields.io/badge/TUI-textual-purple.svg)](https://github.com/Textualize/textual)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-261230?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)

Download and tag high-quality music and video from YouTube, YouTube Music, SoundCloud, and 1000+ sites — all from an interactive terminal UI.

![Screenshot](screenshot.png)

## ✨ Features

- **Interactive TUI** — Dropdown selectors, real-time notifications, cancel support
- **1000+ Supported Sites** — Any site yt-dlp supports
- **Audio/Video Formats** — MP3, AAC, FLAC, M4A, Opus, Vorbis, WAV, MP4, MKV, WebM, and more with configurable bitrate (64–320 kbps)
- **Smart Codec Mapping** — Automatically pairs containers with optimal audio codecs (e.g., MP4→AAC, MKV→Opus)
- **Metadata Embedding** — Title, artist, album tags + cover art thumbnails
- **Thread-safe** — Responsive UI during downloads with background processing
- **Cross-platform Config** — XDG-compliant (Linux), Application Support (macOS), AppData (Windows)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ & FFmpeg

### Installation
```bash
pip install siphon-tui         # pip
uv pip install siphon-tui      # uv
pipx install siphon-tui        # pipx
```

### Usage
```bash
siphon-tui config ~/Downloads    # Set download directory (optional)
siphon-tui                       # Launch TUI (no arguments)
```

If you skip `config`, files will be saved to `~/Downloads` (or platform equivalent).

## ⌨️ Controls

| Key | Action |
|-----|--------|
| `Tab` | Navigate between fields |
| `↑`/`↓` | Navigate dropdown options |
| `Enter` | Confirm selection / Start download |
| `Esc` | Close dropdown |
| `Ctrl+C` | Exit application |

## 📋 Interface Elements

### Input Fields
| Field | Description |
|-------|-------------|
| **URL Input** | Paste video/audio URL from any supported platform |
| **Audio Codec** | Select audio format: MP3, AAC, FLAC, M4A, Opus, Vorbis, WAV |
| **Container** | Optional video container: MP4, MKV, WebM, MOV, AVI, FLV |
| **Bitrate** | Audio quality: 64, 128, 256, 320 kbps |

### Buttons
| Button | Action |
|--------|--------|
| **Download** | Start download with selected settings |
| **Cancel** | Cancel ongoing download |

### Smart Codec Mapping
When a video container is selected, the optimal audio codec is automatically set:

| Container | Auto Audio Codec |
|-----------|:----------------:|
| MP4, MOV | AAC |
| MKV, WebM | Opus |
| AVI | MP3 |
| FLV | AAC |

## 📖 Examples

```bash
# Audio download
siphon-tui
# → Paste URL → Select "mp3" → Select "320" kbps → Press Download

# Video download
siphon-tui
# → Paste URL → Select Container "mp4" → Bitrate auto-sets → Press Download

# Cancel download
# Press "Cancel" button during active download
```

## 📁 Project Structure
```
siphon_tui/
├── __init__.py
├── main.py              # Entry point & CLI/TUI routing
├── cli.py               # CLI interface (cliss)
├── tui/
│   ├── app.py           # Textual TUI application
│   └── style.tcss       # TUI theme & layout
└── utils/
    ├── configer.py      # JSON config manager
    └── download.py      # Download engine (yt-dlp + mutagen)
```

## ⚙️ Configuration

The download path is stored in a JSON config file and can be set via CLI:

```bash
siphon-tui config ~/Music       # Set directory
siphon-tui config                # View current path (if implemented)
```

Config locations (auto-managed):
- **Linux:** `~/.config/siphon-tui/config.json`
- **macOS:** `~/Library/Application Support/siphon-tui/config.json`
- **Windows:** `%APPDATA%\siphon-tui\config.json`

## 🔧 Requirements

| Dependency | Purpose |
|------------|---------|
| `textual` | TUI framework for interactive terminal apps |
| `yt-dlp` | Media extraction from 1000+ platforms |
| `mutagen` | Audio metadata tagging and cover art embedding |
| `platformdirs` | Cross-platform config paths |
| `color-kiss` | Terminal colors |
| `cliss` | CLI framework |
| **FFmpeg** | Audio/video conversion (system) |

## 📄 License

MIT License — see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [Textual](https://github.com/Textualize/textual) – Modern TUI framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) – Download engine
- [mutagen](https://github.com/quodlibet/mutagen) – Metadata tagging
- [platformdirs](https://github.com/platformdirs/platformdirs) – Config paths
- [color-kiss](https://github.com/Fkernel653/color-kiss) – Terminal colors
- [cliss](https://github.com/Fkernel653/cliss) – CLI framework

## ⚠️ Disclaimer

**For educational purposes only.** Users are responsible for complying with platform Terms of Service and applicable copyright laws. Download only content you have permission to download.

---

**Author:** [Fkernel653](https://github.com/Fkernel653)
**Repository:** [github.com/Fkernel653/Siphon-TUI](https://github.com/Fkernel653/Siphon-TUI)
**PyPI:** [pypi.org/project/siphon-tui](https://pypi.org/project/siphon-tui/)
