#!/usr/bin/env python3
"""
Simple web frontend for the YouTube downloader.

Run:
    pip install -U flask yt-dlp
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

import io
import threading
import uuid
import zipfile
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

import yt_dlp
from yt_downloader import build_options

BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = Path.home() / "Downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
jobs = {}  # job_id -> dict


COOKIES_FILE = BASE_DIR / "cookies.txt"

# Cookie error keywords - any of these means we should skip to the next source.
_COOKIE_ERRORS = (
    "DPAPI", "Failed to decrypt", "keyring",
    "Could not copy", "database is locked", "unable to read cookies",
)


def run_job(job_id, url, audio_only, quality, audio_format, playlist):
    job = jobs[job_id]

    def on_progress(d):
        if d["status"] == "downloading":
            job["status"] = "downloading"
            job["percent"] = d.get("_percent_str", "").strip()
            job["speed"] = d.get("_speed_str", "").strip()
            job["eta"] = d.get("_eta_str", "").strip()
            info = d.get("info_dict", {})
            if info.get("title"):
                job["title"] = info["title"]
        elif d["status"] == "finished":
            job["status"] = "processing"

    def on_done(path):
        job["files"].append(Path(path).name)

    def try_download(extra_opts):
        opts = build_options(audio_only, quality, audio_format, DOWNLOAD_DIR, playlist)
        opts.update(extra_opts)
        opts["progress_hooks"] = [on_progress]
        opts["post_hooks"] = [on_done]
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

    # --- Priority 1: cookies.txt file (works with any browser, no locking issues) ---
    if COOKIES_FILE.exists():
        try:
            try_download({"cookiefile": str(COOKIES_FILE)})
            job["status"] = "done"
            job["percent"] = "100%"
            return
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if not any(kw in msg for kw in _COOKIE_ERRORS):
                job["status"] = "error"
                job["error"] = msg
                return

    # --- Priority 2: no cookies (works for most public videos) ---
    try:
        try_download({})
        job["status"] = "done"
        job["percent"] = "100%"
        return
    except Exception as e:  # noqa: BLE001
        job["status"] = "error"
        job["error"] = (
            str(e) + "\n\nTip: Place a cookies.txt from Brave in the downloader "
            "folder to bypass YouTube restrictions."
        )


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.post("/api/start")
def start():
    data = request.get_json(force=True)
    url = (data.get("url") or "").strip()
    if not url.startswith(("http://", "https://")):
        return jsonify(error="Please enter a valid URL."), 400

    audio_only = data.get("mode") == "audio"
    quality = str(data.get("quality") or "best")
    audio_format = data.get("format") or "mp3"
    if audio_format not in {"mp3", "m4a", "opus", "wav", "flac"}:
        audio_format = "mp3"
    if quality != "best" and not quality.isdigit():
        quality = "best"
    playlist = bool(data.get("playlist"))

    job_id = uuid.uuid4().hex[:8]
    jobs[job_id] = {
        "status": "starting", "percent": "0%", "speed": "", "eta": "",
        "title": "", "files": [], "error": "",
    }
    threading.Thread(
        target=run_job,
        args=(job_id, url, audio_only, quality, audio_format, playlist),
        daemon=True,
    ).start()
    return jsonify(id=job_id)


@app.get("/api/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify(error="Unknown job"), 404
    return jsonify(job)


@app.get("/api/cookies-status")
def cookies_status():
    return jsonify(has_cookies=COOKIES_FILE.exists())


@app.get("/files/<path:filename>")
def get_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


@app.get("/api/zip/<job_id>")
def zip_job(job_id):
    """Stream all files for a job as a single ZIP archive."""
    job = jobs.get(job_id)
    if not job:
        return jsonify(error="Unknown job"), 404
    if job["status"] != "done" or not job["files"]:
        return jsonify(error="Job not finished or has no files."), 400

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in job["files"]:
            filepath = DOWNLOAD_DIR / name
            if filepath.exists():
                zf.write(filepath, arcname=name)
    buf.seek(0)

    return Response(
        buf.read(),
        mimetype="application/zip",
        headers={"Content-Disposition": f'attachment; filename="playlist_{job_id}.zip"'},
    )


if __name__ == "__main__":
    # 127.0.0.1 = only reachable from your own computer
    app.run(host="127.0.0.1", port=5000, debug=False)
