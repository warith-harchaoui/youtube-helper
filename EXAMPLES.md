# YouTube Helper — Examples

Practical recipes for the three layers of `youtube-helper`. Every snippet
assumes:

```python
import youtube_helper as yth
import os_helper as osh

osh.verbosity(2)   # so osh.info(...) calls surface on stdout
```

and that `yt-dlp` + `ffmpeg` are installed (`brew install yt-dlp ffmpeg`
on macOS — install `brew` thanks to [brew.sh](https://brew.sh/)).

---

## Table of Contents

1. [Setup](#setup)
2. [Downloads (to disk)](#downloads-to-disk)
3. [Stream Catalog & Picker](#stream-catalog--picker)
4. [Direct-URL Resolver](#direct-url-resolver)
5. [Composing with video-helper](#composing-with-video-helper)
6. [Branding — engagement metadata without API keys](#branding--engagement-metadata-without-api-keys)
7. [Subtitles, Comments, Channels](#subtitles-comments-channels)
8. [Caveats](#caveats)

---

## Setup

```bash
pip install --force-reinstall --no-cache-dir \
  git+https://github.com/warith-harchaoui/youtube-helper.git@v1.3.2
```

Brings in `os-helper` / `audio-helper` / `video-helper` automatically.
You still need `yt-dlp` + `ffmpeg` on PATH (see README).

## Downloads (to disk)

The original `youtube-helper` surface: pull a file to local storage.

```python
yth.download_video("https://www.youtube.com/watch?v=YE7VzlLtp-4", "bunny.mp4")
yth.download_audio("https://www.youtube.com/watch?v=YE7VzlLtp-4", "bunny.mp3")
yth.download_thumbnail("https://www.youtube.com/watch?v=YE7VzlLtp-4", "bunny.jpg")

# Cheap metadata probe (no download)
meta = yth.video_url_meta_data("https://www.youtube.com/watch?v=YE7VzlLtp-4")
print(meta["title"], meta["duration"])
# Big Buck Bunny 596
```

## Stream Catalog & Picker

Where `download_*` writes a file, the catalog / picker functions hand
you a **direct media URL** + headers so a downstream decoder (PyAV /
ffmpeg / `video_helper.extract_frames`) can read it without re-going
through yt-dlp.

```python
# Enumerate every video format yt-dlp finds.
streams = yth.list_video_streams("https://www.youtube.com/watch?v=YE7VzlLtp-4")
for s in streams[:5]:
    print(f"{s['format_id']:6} {s['width']}x{s['height']} {s['fps']}fps "
          f"{s['vcodec']:14} {s['ext']:6} ~{s['vbr_kbps']:.0f} kbps")
# 160     256x144   30.0 avc1.42c00c   mp4    ~  110 kbps
# 278     256x144   30.0 vp09.00.11... webm   ~  102 kbps
# ...

# Pick the one matching your constraints — best yt-dlp candidate among matches.
pick = yth.pick_video_stream(
    "https://www.youtube.com/watch?v=YE7VzlLtp-4",
    prefer_codec="h264",   # also matches "avc1.xxx"
    prefer_format="mp4",
    max_fps=30,
)
# pick is a VideoStreamInfo:
#   {"format_id": "22", "url": "https://...mp4", "headers": {...},
#    "width": 1280, "height": 720, "fps": 30.0, "vcodec": "avc1.64001F",
#    "acodec": "mp4a.40.2", "is_live": False, ...}
```

**Note on audio**: a parallel audio catalog / picker intentionally lives
in **podcast-helper** (single owner for audio PCM streaming), not here.

## Direct-URL Resolver

When you don't need the catalog and just want **one** ffmpeg-ready URL:

```python
out = yth.resolve_direct_url(
    "https://www.youtube.com/watch?v=YE7VzlLtp-4",
    prefer="video",   # or "audio" for the cheapest audio-only path
)
# {"url": "https://...", "container": "mp4", "is_live": False,
#  "headers": {"User-Agent": "...", ...}}
```

Coarser than `pick_video_stream` (no codec / format / fps filtering),
but a single call.

## Composing with video-helper

The whole point of the catalog/picker: feed the direct URL + headers to
`video_helper.extract_frames` and decode without re-fetching the page.

### Two-step composition (low-level)

```python
import video_helper as vh

pick = yth.pick_video_stream("https://www.youtube.com/watch?v=YE7VzlLtp-4",
                             prefer_codec="h264", max_fps=30)

for frame in vh.extract_frames(
    pick["url"],
    http_headers=pick["headers"],
    start_instant=10.0, end_instant=20.0,
    frame_interval=1.0,
    destination="torch", device="mps", batch_size=10, layout="image",
):
    # frame.shape == (10, 3, H, W), RGB uint8, on MPS
    embeddings = model(frame)
```

### One-call composition — `extract_frames_stream` (v1.2.0)

`extract_frames_stream` collapses the two-step recipe into a single
call. It runs `pick_video_stream` under the hood, splices the
resolver's `http_headers` automatically, and forwards every
`extract_frames` kwarg verbatim:

```python
for frame in yth.extract_frames_stream(
    "https://www.youtube.com/watch?v=YE7VzlLtp-4",
    # picker constraints
    prefer_codec="h264", prefer_format="mp4", max_fps=30,
    # extract_frames passthrough
    start_instant=10.0, end_instant=20.0, frame_interval=1.0,
    destination="torch", device="mps", batch_size=10, layout="image",
):
    embeddings = model(frame)
```

Same code drives a CPU numpy pipeline (the default) or a GPU torch
pipeline (just by changing `destination` / `device` / `batch_size`).
The picker is invoked once and the resolved stream is reused for the
entire iteration.

> **Heads-up**: `extract_frames_stream` requires `video-helper >= v1.5.2`
> (URL-aware `is_valid_video_file` + `video_dimensions(http_headers=)`).
> The youtube-helper v1.2.0 release pins it automatically.

## Branding — engagement metadata without API keys

`youtube_helper.branding` extracts public engagement signals using yt-dlp's
own metadata dict — **no Google Data API, no Vimeo API, no OAuth,
no quota**.

```python
# One-video snapshot
meta = yth.video_engagement("https://www.youtube.com/watch?v=YE7VzlLtp-4")
print(meta["view_count"], meta["like_count"], meta["comment_count"])
# 412309876 1893422 156003
print(meta["kind"])   # "short" / "long" / "live"
# long

# Channel snapshot — subs, total views, video count
ch = yth.channel_info("https://www.youtube.com/@Blender")
print(f"{ch['title']}: {ch['follower_count']:,} subscribers, "
      f"{ch['video_count']:,} videos")
# Blender: 1,920,000 subscribers, 487 videos

# Channel video list with per-video engagement (paginated, slow due to per-vid fetch)
videos = yth.channel_videos(
    "https://www.youtube.com/@Blender",
    max_videos=20,
    include_shorts=True,
    include_lives=False,
)
for v in videos:
    print(f"{v['upload_date']}  {v['view_count']:>10,} views  {v['title']}")
    # 2026-06-20    132,485 views  Blender Conference 2026 — call for talks
    # 2026-06-12  1,840,201 views  Cycles X — what's new in 4.5
    # ...

# Batched engagement across a list of URLs — tolerant (bad URLs → _error stub)
batch = yth.engagement_batch([url1, url2, url3])
for entry in batch:
    if "_error" in entry:
        print(f"skip {entry['url']}: {entry['_error']}")
        # skip https://www.youtube.com/watch?v=removed: Video unavailable
    else:
        print(entry["title"], entry["view_count"])
        # Big Buck Bunny 412309876
```

**Normalised schema** (same fields whether the source is YouTube,
Vimeo, DailyMotion, or Twitch VOD):

```
id, url, title, description, upload_date (ISO YYYY-MM-DD),
duration_seconds, view_count, like_count, comment_count,
channel, channel_id, channel_url, channel_follower_count,
tags, categories, thumbnail, availability, live_status,
extractor, kind  # "short" / "long" / "live"
```

## Subtitles, Comments, Channels

```python
# Auto-subtitles → {lang: path_to_vtt}
subs = yth.video_subtitles(
    "https://www.youtube.com/watch?v=YE7VzlLtp-4",
    output_dir="captions",
    langs=("fr", "en"),
    auto_only=True,
)
# {"en": "captions/YE7VzlLtp-4.en.vtt"}

# Comments — YouTube increasingly requires browser cookies for comment threads.
comments = yth.video_comments(
    "https://www.youtube.com/watch?v=YE7VzlLtp-4",
    max_count=50,
    cookies_from_browser="firefox",   # or "chrome" / "safari" — read your active session
)
for c in comments[:3]:
    print(f"@{c['author']} ({c['like_count']} ♥): {c['text'][:80]}")
    # @alice_dev (842 ♥): Bunny still holds up after 20 years. Render in Cycles X now?
    # @rab_animator (519 ♥): Where can I get the .blend file? Was archived on...
    # @kid_pixels (308 ♥): My 6yo watches this on loop. Eternal classic.

# Heuristic: is this a Short / vertical clip?
yth.is_short(yth.video_engagement(url))   # True / False
```

## Caveats

- **URL expiration** — Direct media URLs from yt-dlp expire (typically
  1-6 h for YouTube). For long-running jobs, re-resolve periodically
  or use `download_video` to materialize a local file.
- **Live streams** — `pick["is_live"] == True` and `pick["url"]` is
  typically an HLS `.m3u8` manifest. ffmpeg / PyAV handle these
  natively but: no seek backwards, no `frame_indices` / `frame_times`
  semantics, and hwaccel can be flaky with chunked HLS. The future
  `extract_frames_stream` will refuse `speed != 1.0` for live (you
  can't fast-forward past the live edge).
- **yt-dlp freshness** — YouTube rotates its signature scheme often.
  `yth.ensure_recent_ytdlp(min_version="2024.12.23")` warns when your
  installed yt-dlp is too old; `pip install -U yt-dlp` fixes most
  "broken decryption" errors.
- **Authentication** — Members-only / age-gated / private videos need
  cookies. Pass `cookies_from_browser="firefox"` (or `"chrome"` /
  `"safari"`) to the catalog / picker / branding functions; yt-dlp
  reads the active browser session.
- **Comments scraping** — YouTube comment threads almost always need
  `cookies_from_browser` now. Without it you'll usually get an empty
  list or a 403.
