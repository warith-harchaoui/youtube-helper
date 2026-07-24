# YouTube Helper

[🇫🇷](https://github.com/warith-harchaoui/youtube-helper/blob/main/LISEZMOI.md) · [🇬🇧](https://github.com/warith-harchaoui/youtube-helper/blob/main/README.md)

[![CI](https://github.com/warith-harchaoui/youtube-helper/actions/workflows/ci.yml/badge.svg)](https://github.com/warith-harchaoui/youtube-helper/actions/workflows/ci.yml) [![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://github.com/warith-harchaoui/youtube-helper/blob/main/LICENSE) [![Python](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue.svg)](#) [![Local-first](https://img.shields.io/badge/privacy-local--first-2f6f5e.svg)](#the-promise)

`YouTube Helper` belongs to a collection of libraries called `AI Helpers` developed for building Artificial Intelligence.

## The Promise

**Local-first by design.** youtube-helper runs entirely on your machine — it fetches only the media you ask for; your data is never uploaded to a third-party service, no telemetry, no account, no cloud lock-in. You own the whole pipeline. Part of the [AI Helpers](https://github.com/warith-harchaoui/ai-helpers) suite: sovereignty over your data through local-first Open Source.

*(youtube-helper does reach the internet — it downloads media from the source site you point it at. The promise is about no exfiltration and no telemetry: nothing about you or your requests is ever sent anywhere except the site hosting the media you asked for.)*

[🌍 AI Helpers](https://harchaoui.org/warith/ai-helpers)

[![logo](https://raw.githubusercontent.com/warith-harchaoui/youtube-helper/main/assets/logo.png)](https://harchaoui.org/warith/ai-helpers)

YouTube Helper is a Python library that provides utility functions for downloading videos, audio, and thumbnails from platforms like YouTube, Vimeo, and DailyMotion using `yt-dlp`.
It also supports post-processing tasks such as converting or merging media files with `ffmpeg`.

## Documentation

[💻 Documentation](https://harchaoui.org/warith/ai-helpers/docs/youtube-helper-doc/)

[🗺️ Landscape](https://github.com/warith-harchaoui/youtube-helper/blob/main/LANDSCAPE.md)

[📋 Examples](https://github.com/warith-harchaoui/youtube-helper/blob/main/EXAMPLES.md)

## Installation

**Prerequisites** — **Python 3.10–3.13**, **git**, **yt-dlp**, and **ffmpeg**, cross-platform:

- 🍎 **macOS** ([Homebrew](https://brew.sh)): `brew install python git yt-dlp ffmpeg`
- 🐧 **Ubuntu/Debian**: `sudo apt update && sudo apt install -y python3 python3-pip git yt-dlp ffmpeg`
- 🪟 **Windows** (PowerShell): `winget install Python.Python.3.12 Git.Git yt-dlp.yt-dlp Gyan.FFmpeg`

We recommend using Python environments. Check this link if you're unfamiliar with setting one up: [🥸 Tech tips](https://harchaoui.org/warith/4ml/#install).

### From PyPI (recommended)

```bash
pip install youtube-helper

# Optional surfaces
pip install "youtube-helper[cli]"       # click-based CLI twin
pip install "youtube-helper[api]"       # FastAPI HTTP surface
pip install "youtube-helper[api,mcp]"   # MCP tools over FastAPI
```

### From source (no PyPI)

```bash
pip install "git+https://github.com/warith-harchaoui/youtube-helper.git@v1.4.0"

# Optional surfaces
pip install "youtube-helper[cli] @ git+https://github.com/warith-harchaoui/youtube-helper.git@v1.4.0"
pip install "youtube-helper[api] @ git+https://github.com/warith-harchaoui/youtube-helper.git@v1.4.0"
pip install "youtube-helper[api,mcp] @ git+https://github.com/warith-harchaoui/youtube-helper.git@v1.4.0"
```

## Usage

For the full catalog of recipes (downloads, stream catalog / picker, direct-URL
resolver, composing with `video-helper`, branding metadata, subtitles &
comments), see [📋 EXAMPLES.md](https://github.com/warith-harchaoui/youtube-helper/blob/main/EXAMPLES.md).

Quick start — download a video, extract metadata, and download the audio:

```python
import youtube_helper as yth
import video_helper as vh
import audio_helper as ah
import os_helper as osh
import os

osh.verbosity(0)

# Example YouTube URL
youtube_url = "https://www.youtube.com/watch?v=YE7VzlLtp-4"

folder = "yt_tests"
os.makedirs(folder, exist_ok=True)

# Download a video
video = "big-buck-bunny.mp4"
video = os.path.join(folder, video)
yth.download_video(youtube_url, video)

# Extract metadata from the video URL
metadata = yth.video_url_meta_data(youtube_url)
print(metadata["title"])
# Big Buck Bunny

print(metadata["duration"])
# 597

print(metadata["description"])
# Big Buck Bunny tells the story of a giant rabbit with a heart bigger than himself. When one sunny day three rodents rudely harass him, something snaps... and the rabbit ain't no bunny anymore! In the typical cartoon tradition he prepares the nasty rodents a comical revenge.
# 
# Licensed under the Creative Commons Attribution license
# 
# http://www.bigbuckbunny.org/

print(metadata["channel"])
# Blender

details = vh.video_dimensions(video)
print(details)
# {'width': 1280, 'height': 720, 'duration': 596.458, 'frame_rate': 24.0, 'has_sound': True}

# Download the audio from the video
audio = "big-buck-bunny.mp3"
audio = os.path.join(folder, audio)
yth.download_audio(youtube_url, audio)

audio, sample_rate = ah.load_audio(audio)
print(sample_rate)
# 44100
```

## Legal and Ethical Use

YouTube Helper is a thin wrapper around `yt-dlp` and `ffmpeg`. You are responsible for how you use it. Only download or process media that you own, that is in the public domain or under a permissive license (e.g. Creative Commons), or for which you have explicit permission from the rights holder. Respect each platform's Terms of Service and any applicable copyright, privacy, and data-protection laws in your jurisdiction. The authors provide this library for legitimate uses such as personal archiving, accessibility, research, and content you have rights to — not for circumventing access controls or redistributing copyrighted material.

## Features

**Downloads (to disk)** — `youtube_helper.main`
- `download_video(url, output_path)` / `download_audio(url, output_path)` / `download_thumbnail(url, output_path)`.
- `video_url_meta_data(url)` / `is_valid_video_url(url)` for cheap metadata probes.
- `default_ytdlp_options(verbose, ...)` for customisable yt-dlp options.

**Stream catalog & direct-URL resolution** — `youtube_helper.streaming`
- `resolve_direct_url(url, prefer="audio"|"video")` → quick "give me one direct ffmpeg-ready URL".
- `list_video_streams(url)` → enumerate every video format yt-dlp finds (codec, resolution, fps, bitrate, …).
- `pick_video_stream(url, prefer_codec=, prefer_format=, max_fps=, language=, cookies_from_browser=)` → constrained picker, returns one `VideoStreamInfo` ready to feed `video_helper.extract_frames`.
- `extract_frames_stream(url, ..., **extract_frames_kwargs)` → one-call composition of `pick_video_stream` + `video_helper.extract_frames`, auto-wires headers, forwards any `extract_frames` kwarg (`destination`, `device`, `batch_size`, `output_width`, `frame_step`, …). The shortest path from a YouTube / Vimeo / Twitch URL to ML-ready frames.
- Audio stream catalog / picker intentionally lives in **podcast-helper** (single owner for audio PCM streaming).

**No-API engagement metadata** — `youtube_helper.branding`
- `channel_info(url)` / `channel_videos(url, max_videos, include_shorts, include_lives)` — channel snapshot + paginated video list with normalised engagement metrics, cross-platform schema.
- `video_engagement(url)` / `engagement_batch([urls])` — per-video views / likes / comments / channel follower count, tolerant batched variant.
- `video_subtitles(url, output_dir, langs=("fr","en"))` — auto-subtitle download.
- `video_comments(url, max_count, cookies_from_browser="firefox"|"chrome"|...)` — comments sample.
- `is_short(meta)` / `ensure_recent_ytdlp(min_version)` — helpers.
- Built on yt-dlp's public metadata only — **no Google Data API, no Vimeo API, no OAuth, no quota.**

## Multi-surface exposure

`youtube-helper` is not just a library — the same functions are exposed
as two CLIs, a FastAPI HTTP surface, an MCP tool set, and a browser GUI:

```bash
# Python library (default)
import youtube_helper as yth

# argparse-based CLI (installed automatically)
youtube-helper metadata     --url https://www.youtube.com/watch?v=YE7VzlLtp-4
youtube-helper audio        --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --output out.mp3
youtube-helper resolve      --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --prefer audio
youtube-helper channel-info --url https://www.youtube.com/@blender

# click-based CLI twin (needs the [cli] extra)
pip install 'youtube-helper[cli] @ git+https://github.com/warith-harchaoui/youtube-helper.git@v1.4.0'
youtube-helper-click metadata --url https://www.youtube.com/watch?v=YE7VzlLtp-4

# FastAPI HTTP surface (needs the [api] extra)
pip install 'youtube-helper[api] @ git+https://github.com/warith-harchaoui/youtube-helper.git@v1.4.0'
uvicorn youtube_helper.api:app --port 8000
# → OpenAPI docs at http://localhost:8000/docs

# MCP tools over FastAPI (needs the [api,mcp] extras)
pip install 'youtube-helper[api,mcp] @ git+https://github.com/warith-harchaoui/youtube-helper.git@v1.4.0'
youtube-helper-mcp                # serves FastAPI + MCP on port 8000

# Browser GUI (needs the [api] extra) — paste a URL, pick audio or video
uvicorn youtube_helper.api:app --port 8000
# → open http://localhost:8000/gui  (or just http://localhost:8000/)
```

**Download bench GUI** (`GET /gui`): a single self-contained page (Tailwind via
CDN + vanilla JS, no build step). Paste a YouTube (or any yt-dlp-supported) URL,
choose **audio** (with a sample rate) or **video**, hit Download, and the result
plays inline with a download link. It POSTs to the same `/audio` / `/video`
endpoints — zero extra server logic. Local-first: the page only talks to your
local API.

**Agent skill** (Claude Code / Claude Desktop / OpenCode): install
[`skills/youtube-helper/`](https://github.com/warith-harchaoui/youtube-helper/blob/main/skills/README.md)
so an agent can download and inspect media on your behalf. See
[TRIGGERS.md](https://github.com/warith-harchaoui/youtube-helper/blob/main/TRIGGERS.md)
for the exhaustive catalogue of what fires it.

Docker image:

```bash
docker build -t youtube-helper .
docker run --rm -p 8000:8000 youtube-helper
```

A richer GUI plan (video library board, channel comparator, batch downloader)
lives in [GUI.md](https://github.com/warith-harchaoui/youtube-helper/blob/main/GUI.md).

The competitive landscape (yt-dlp, pytubefix, YouTube Data API,
streamlink, ArchiveBox, …) is analysed, with a positioning map, in
[LANDSCAPE.md](https://github.com/warith-harchaoui/youtube-helper/blob/main/LANDSCAPE.md).

## Author
 - [Warith HARCHAOUI](https://linkedin.com/in/warith-harchaoui)

## Acknowledgements
Special thanks to [Mohamed Chelali](https://mchelali.github.io) and [Bachir Zerroug](https://www.linkedin.com/in/bachirzerroug) for fruitful discussions.

## License

This project is licensed under the BSD-3-Clause License — see the [LICENSE](LICENSE) file for details.
