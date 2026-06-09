# Siphon-TUI — Download audio/video from YouTube, SoundCloud, and 1000+ sites via interactive terminal UI

[![Status: Archived](https://img.shields.io/badge/Status-Archived-red.svg)](https://github.com/Fkernel653/Siphon-TUI)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)

> ## 🚨 PROJECT ARCHIVED
>
> **This project is no longer maintained.**
>
> - ✅ Code is left here for historical/portfolio purposes
> - ❌ No issues or pull requests will be accepted
> - ❌ No updates or bug fixes — including yt-dlp compatibility fixes
> - ⚠️ Use at your own risk

## What this project was

An interactive terminal UI (TUI) for downloading audio and video from YouTube, SoundCloud, and 1000+ sites using yt-dlp, with metadata embedding and format selection.

**Features:**
- Interactive TUI with dropdown selectors and real-time notifications
- 1000+ supported sites (anything yt-dlp supports)
- Audio formats: MP3, AAC, FLAC, M4A, Opus, Vorbis, WAV
- Video containers: MP4, MKV, WebM, MOV, AVI, FLV
- Configurable bitrate (64–320 kbps)
- Smart codec mapping (MP4→AAC, MKV→Opus, etc.)
- Metadata embedding (title, artist, album, cover art)
- Cross-platform config support

## Requirements (historical)

- Python 3.10+
- FFmpeg (system dependency)
- `textual`, `yt-dlp`, `mutagen`, `platformdirs`, `color-kiss`, `arg-kiss`

## Keyboard Shortcuts (for reference)

| Key | Action |
|-----|--------|
| `Tab` | Navigate between fields |
| `↑`/`↓` | Navigate dropdown options |
| `Enter` | Confirm selection / Start download |
| `Esc` | Close dropdown |
| `Ctrl+C` | Exit application |

## ⚠️ Disclaimer

**For educational purposes only.** Users are responsible for complying with platform Terms of Service and applicable copyright laws. Download only content you have permission to download.

## License

MIT — see [LICENSE](LICENSE).

---

**Author:** [Fkernel653](https://github.com/Fkernel653)
**Repository:** [github.com/Fkernel653/Siphon-TUI](https://github.com/Fkernel653/Siphon-TUI)
