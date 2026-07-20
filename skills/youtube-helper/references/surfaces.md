# youtube-helper non-CLI surfaces

`youtube-helper` exposes the same operations through five surfaces. The Python
library and argparse CLI are always available; the others live behind optional
extras.

## 1. Python library (default)

```python
import youtube_helper as yth

# Downloads (return the output path on disk)
yth.download_video(url, output_path=None)                       # best video+audio -> mp4
yth.download_audio(url, output_path=None, target_sample_rate=44100)  # bestaudio -> mp3
yth.download_thumbnail(url, output_path=None)                   # thumbnail image

# Metadata / validation
yth.video_url_meta_data(url)     # -> dict (title, duration, description, …)
yth.is_valid_video_url(url)      # -> bool

# Direct-URL resolver + stream catalog/picker + frame streaming
yth.resolve_direct_url(url, prefer="audio", live="auto")   # -> DirectMediaURL
yth.list_video_streams(url, …)                             # -> list[VideoStreamInfo]
yth.pick_video_stream(url, prefer_codec=…, max_fps=…, …)   # -> VideoStreamInfo
yth.extract_frames_stream(url, **extract_frames_kwargs)    # URL -> ML-ready frames

# No-API engagement / branding (yt-dlp public metadata only)
yth.channel_info(url)                                      # -> dict
yth.channel_videos(url, max_videos=200, include_shorts=True, include_lives=False)
yth.video_engagement(url)                                  # -> dict
yth.engagement_batch([urls])                               # -> list[dict] (tolerant)
yth.video_subtitles(url, output_dir, langs=("fr","en"), auto_only=True)
yth.video_comments(url, max_count=100, cookies_from_browser=None)
yth.is_short(meta)                                         # -> bool
yth.ensure_recent_ytdlp(min_version=None)                 # -> str
```

The public API is fixed via `youtube_helper.__all__`; `podcast-helper` depends on
these names — treat them as stable.

## 2. CLI — argparse (default) and click

See `cli-reference.md`. `youtube-helper` (argparse) ships with the base package;
`youtube-helper-click` needs the `[cli]` extra and mirrors every subcommand and
flag name.

## 3. HTTP API — FastAPI (`youtube-helper[api]`)

```bash
pip install 'youtube-helper[api]'
uvicorn youtube_helper.api:app --host 0.0.0.0 --port 8000
# OpenAPI docs: http://localhost:8000/docs
```

Endpoints:
- `GET  /health` — liveness probe → `{"status":"ok"}`.
- `GET  /` — redirects to `/gui`.
- `GET  /gui` — the single-page download bench (see below).
- `POST /metadata` `/valid` `/resolve` `/list-streams` `/pick-stream`
  `/channel-info` `/channel-videos` `/engagement` `/engagement-batch`
  `/comments` `/ytdlp-version` — JSON body → JSON.
- `POST /video` `/audio` `/thumbnail` — JSON body `{url, sample_rate?}` → the
  resulting file streamed back (temp dir cleaned via `BackgroundTasks`).
- `POST /subtitles` — JSON body → a `.zip` of the `.vtt` files.

## 4. MCP server — FastAPI-MCP (`youtube-helper[api,mcp]`)

```bash
pip install 'youtube-helper[api,mcp]'
youtube-helper-mcp                 # serves FastAPI + MCP on :8000
# or: python -m youtube_helper.mcp
```

Wraps the exact FastAPI app with `fastapi_mcp` — the same endpoints become MCP
tools for any MCP-aware host. Bind via `YOUTUBE_HELPER_HOST` /
`YOUTUBE_HELPER_PORT` env vars.

## 5. GUI — minimal download bench (`GET /gui`)

Served by the FastAPI app; no build step, no framework — a single self-contained
HTML page (Tailwind via CDN + vanilla ES-module JS) defined in
`youtube_helper/gui.py`.

Workflow: paste a media URL → choose **audio** (with a target sample rate) or
**video** → **Download** (POSTs to the same `/audio` / `/video` routes) → a
progress line runs while yt-dlp + ffmpeg work → the result plays inline in an
`<audio>` / `<video>` element with a download link.

```bash
uvicorn youtube_helper.api:app --port 8000
# open http://localhost:8000/gui  (or just http://localhost:8000/)
```

Local-first: the page only talks to the local API; nothing is uploaded to a
third party.
