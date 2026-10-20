#!/usr/bin/env python3
"""
YouTube downloader (video or audio) built on yt-dlp.

Setup:
    pip install -U yt-dlp
    # ffmpeg is needed for MP3 conversion and merging HD video + audio:
    #   Windows: winget install ffmpeg   (or download from ffmpeg.org)
    #   macOS:   brew install ffmpeg
    #   Linux:   sudo apt install ffmpeg

Usage:
    python yt_downloader.py                      # interactive mode
    python yt_downloader.py URL                  # download video (best quality)
    python yt_downloader.py URL -a               # download audio as MP3
    python yt_downloader.py URL -q 720           # video capped at 720p
    python yt_downloader.py URL -a -f m4a        # audio as m4a
    python yt_downloader.py URL -o ~/Downloads   # choose output folder
    python yt_downloader.py PLAYLIST_URL -p      # whole playlist

Only download content you own, that is licensed for download,
or that you otherwise have the right to save.
"""

import argparse
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    sys.exit("yt-dlp is not installed. Run: pip install -U yt-dlp")


def progress_hook(d):
    if d["status"] == "downloading":
        pct = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        print(f"\r  {pct}  {speed}  ETA {eta}   ", end="", flush=True)
    elif d["status"] == "finished":
        print("\n  Download finished, processing...")


def build_options(audio_only, quality, audio_format, out_dir, playlist, browser=None):
    name = "%(playlist_index)02d - %(title)s.%(ext)s" if playlist else "%(title)s.%(ext)s"
    opts = {
        "outtmpl": str(out_dir / name),
        "noplaylist": not playlist,
        "ignoreerrors": playlist,  # skip private/deleted videos in playlists
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": False,
        # --- YouTube 403 / bot-detection fixes ---
        # Use the web player client which is less aggressively blocked.
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "android"],
                "skip": ["hls", "dash"],  # prefer direct http streams
            }
        },
        # Retry fragments on transient failures
        "fragment_retries": 10,
        "retries": 5,
    }

    # Inject browser cookies if a browser was resolved by the caller.
    if browser:
        opts["cookiesfrombrowser"] = (browser, None, None, None)

    if audio_only:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": "192",
            }
        ]
    else:
        if quality == "best":
            opts["format"] = "bestvideo+bestaudio/best"
        else:
            opts["format"] = (
                f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
            )
        opts["merge_output_format"] = "mp4"

    return opts


def download(url, audio_only=False, quality="best", audio_format="mp3",
             out_dir="downloads", playlist=False):
    out_path = Path(out_dir).expanduser()
    out_path.mkdir(parents=True, exist_ok=True)

    opts = build_options(audio_only, quality, audio_format, out_path, playlist)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "Unknown")
            kind = "audio" if audio_only else "video"
            print(f"\nDownloading {kind}: {title}")
            ydl.download([url])
        print(f"Saved to: {out_path.resolve()}")
    except yt_dlp.utils.DownloadError as e:
        print(f"\nDownload failed: {e}")
        print("Tip: update yt-dlp with `pip install -U yt-dlp` — YouTube changes often.")
    except KeyboardInterrupt:
        print("\nCancelled.")


def interactive():
    print("=== YouTube Downloader ===")
    url = input("Paste the YouTube URL: ").strip()
    if not url:
        sys.exit("No URL given.")

    choice = input("Download [1] Video or [2] Audio (MP3)? [1/2]: ").strip()
    audio_only = choice == "2"

    quality = "best"
    if not audio_only:
        q = input("Max quality (e.g. 1080, 720, 480) or Enter for best: ").strip()
        if q.isdigit():
            quality = q

    out_dir = input("Output folder [downloads]: ").strip() or "downloads"
    download(url, audio_only=audio_only, quality=quality, out_dir=out_dir)


def main():
    parser = argparse.ArgumentParser(description="Download YouTube videos or audio.")
    parser.add_argument("url", nargs="?", help="YouTube video or playlist URL")
    parser.add_argument("-a", "--audio", action="store_true", help="audio only")
    parser.add_argument("-f", "--format", default="mp3",
                        choices=["mp3", "m4a", "opus", "wav", "flac"],
                        help="audio format (default: mp3)")
    parser.add_argument("-q", "--quality", default="best",
                        help="max video height, e.g. 1080, 720, 480 (default: best)")
    parser.add_argument("-o", "--output", default="downloads", help="output folder")
    parser.add_argument("-p", "--playlist", action="store_true",
                        help="download the whole playlist")
    args = parser.parse_args()

    if not args.url:
        interactive()
    else:
        download(args.url, args.audio, args.quality, args.format,
                 args.output, args.playlist)


if __name__ == "__main__":
    main()
