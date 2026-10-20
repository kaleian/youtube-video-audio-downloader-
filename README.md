# YouTube Video & Audio Downloader

A modern, fast, and feature-packed YouTube video and audio downloader powered by [`yt-dlp`](https://github.com/yt-dlp/yt-dlp). Features both an elegant, responsive dark-mode **Web UI** and a flexible **Command-Line Interface (CLI)**.

---

## ✨ Features

- **🎥 High-Definition Video:** Download single videos or playlists in Best Quality, 1080p, 720p, 480p, or 360p (merged automatically with audio as MP4).
- **🎵 Crystal-Clear Audio Extraction:** Convert video to high-bitrate audio in multiple formats: **MP3**, **M4A**, **OPUS**, **WAV**, or **FLAC**.
- **📑 Full Playlist Support:** Download entire playlists with sequential track numbering (`01 - Title.mp3`) and automatic skipping of private/deleted entries.
- **📦 One-Click "Download All as ZIP":** When downloading playlists via the Web UI, bundle all tracks into a single `.zip` file with one click.
- **⚡ Real-Time Progress Tracking:** Live download percentage, transfer speed, and estimated time of arrival (ETA).
- **🛡️ 403 & Bot-Detection Resilience:** Built-in player client fallbacks (`web`, `android`) and optional `cookies.txt` authentication to effortlessly bypass YouTube restrictions and DPAPI/database lock errors.
- **📂 Direct Downloads:** Automatically saves files directly to your system's `Downloads` folder or custom path.

---

## 📋 Prerequisites

1. **Python 3.8+** installed on your system.
2. **FFmpeg** installed and added to your system `PATH` (required for audio conversion and merging video+audio streams).

### Installing FFmpeg

- **Windows:**
  ```powershell
  winget install ffmpeg
  ```
  *(Or download from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) and add the `bin` folder to your system environment `PATH`)*

- **macOS:**
  ```bash
  brew install ffmpeg
  ```

- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt update && sudo apt install -y ffmpeg
  ```

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kaleian/youtube-video-audio-downloader-.git
   cd youtube-video-audio-downloader-
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Usage

### Option 1: Web Interface (Recommended)

1. **Start the Flask server:**
   ```bash
   python app.py
   ```
2. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```
3. **Download:**
   - Paste any YouTube video or playlist URL.
   - Choose **Video** (and target max resolution) or **Audio** (and preferred format).
   - Check **Download entire playlist** if pasting a playlist link.
   - Click **Download** to watch the real-time progress bar.
   - Files are automatically saved to your computer's `Downloads` directory, and individual download links (plus a **Download All as ZIP** button for playlists) appear in the UI.

---

### Option 2: Command-Line Interface (CLI)

The CLI can be run interactively or with command-line flags.

#### Interactive Mode
Simply run the script with no arguments:
```bash
python yt_downloader.py
```
You will be prompted to paste a URL and choose format, quality, and destination folder.

#### Argument-Driven Commands

| Command | Description |
| :--- | :--- |
| `python yt_downloader.py "<URL>"` | Download video in best available quality |
| `python yt_downloader.py "<URL>" -a` | Extract audio as MP3 (default) |
| `python yt_downloader.py "<URL>" -a -f m4a` | Extract audio as M4A (or `opus`, `wav`, `flac`) |
| `python yt_downloader.py "<URL>" -q 720` | Download video capped at 720p |
| `python yt_downloader.py "<PLAYLIST_URL>" -p` | Download an entire video playlist |
| `python yt_downloader.py "<PLAYLIST_URL>" -p -a` | Download an entire playlist as MP3s |
| `python yt_downloader.py "<URL>" -o "~/Music"` | Save files to a custom folder |

---

## 🍪 Bypassing YouTube 403 Forbidden & Age Restrictions

YouTube frequently restricts automated requests with HTTP 403 Forbidden errors or requires login for age-restricted videos. 

To bypass this reliably without browser database lock issues:

1. Install the extension **Get cookies.txt LOCALLY** in your browser ([Chrome / Brave Web Store](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) or [Firefox Add-ons](https://addons.mozilla.org/firefox/addon/cookies-txt/)).
2. Open [youtube.com](https://www.youtube.com) and make sure you are logged in.
3. Click the extension icon and click **Export**.
4. Save the file as **`cookies.txt`** directly in the root folder of this project.
5. The application detects `cookies.txt` automatically and uses it to authenticate all downloads.

---

## 📁 Project Structure

```
├── app.py              # Flask web backend & download job orchestrator
├── index.html          # Sleek dark-mode frontend with real-time polling
├── yt_downloader.py    # Core yt-dlp wrapper & standalone CLI tool
├── requirements.txt    # Python dependencies (flask, yt-dlp)
├── .gitignore          # Ignores downloaded media, temp files, and cookies
└── README.md           # Project documentation and guides
```

---

## ⚖️ Disclaimer

This software is for personal and educational use only. Please ensure you only download content you own, that is in the public domain, or for which you have received express permission from the copyright holder.
