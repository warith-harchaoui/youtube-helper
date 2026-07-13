# LANDSCAPE

Related and competing Python (and adjacent) tools in the "download and
inspect online video / audio" space, benchmarked against
`youtube-helper`. Ratings are `⭐️` (1) to `⭐️⭐️⭐️⭐️⭐️` (5), scored on
`youtube-helper`'s intended job — everyday YouTube / Vimeo / DailyMotion
/ Twitch download + no-API engagement metadata for personal-branding and
AI pipelines. A tool optimised for a very different job (e.g. archival
mirroring, torrent-based re-uploads) is not penalised — the score just
reflects fit to *this* niche.

## At a glance

| Library / project | Multi-platform (yt-dlp coverage) | Video / audio / thumb download | Direct-URL resolver (ffmpeg-ready) | Stream catalog + picker (codec/fps/lang) | No-API engagement metadata (views / likes / channel) | Multi-surface (CLI + HTTP + MCP) | Docker-ready | AI-pipeline ergonomics (`dict` return, path-based API) |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **youtube-helper** *(this project)* | ⭐️⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️⭐️⭐️ (argparse + click + FastAPI + MCP) | ⭐️⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️⭐️⭐️ |
| yt-dlp (direct) | ⭐️⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️⭐️ (raw info dict) | ⭐️⭐️⭐️ (raw formats list, no normalised picker) | ⭐️⭐️⭐️ (raw fields, no channel snapshot) | ⭐️⭐️ (CLI + Python, no HTTP/MCP) | ⭐️⭐️⭐️ | ⭐️⭐️⭐️ |
| youtube-dl (fork parent) | ⭐️⭐️⭐️ (stale, coverage drift) | ⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️ |
| pytube | ⭐️ (YouTube only) | ⭐️⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️⭐️ |
| pytubefix (maintained fork) | ⭐️ (YouTube only) | ⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️ | ⭐️⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️⭐️ |
| YouTube Data API (googleapiclient) | ⭐️ (YouTube only) | ⭐️ (no video files, metadata only) | ⭐️ | ⭐️ | ⭐️⭐️⭐️⭐️⭐️ (canonical) | ⭐️⭐️ | ⭐️⭐️⭐️ | ⭐️⭐️ (OAuth + quota) |
| Playwright / Selenium scrapers | ⭐️⭐️⭐️ (arbitrary site) | ⭐️⭐️ (screen record) | ⭐️ | ⭐️ | ⭐️⭐️⭐️ (visible fields only) | ⭐️⭐️ | ⭐️⭐️ | ⭐️ |
| you-get | ⭐️⭐️⭐️⭐️ (broad, less than yt-dlp) | ⭐️⭐️⭐️⭐️ | ⭐️⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️ |
| streamlink | ⭐️⭐️⭐️⭐️ (live-focused) | ⭐️⭐️⭐️ (live streams, not files) | ⭐️⭐️⭐️⭐️⭐️ (live direct URL) | ⭐️⭐️ | ⭐️ | ⭐️⭐️ | ⭐️⭐️⭐️ | ⭐️⭐️ |
| youtube_transcript_api | ⭐️ (YouTube only) | ⭐️ (transcripts only) | ⭐️ | ⭐️ | ⭐️⭐️ (transcript / auto-caption) | ⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️⭐️ |
| ArchiveBox | ⭐️⭐️⭐️⭐️ (multi-site) | ⭐️⭐️⭐️ (archival focus) | ⭐️⭐️ | ⭐️⭐️ | ⭐️⭐️⭐️ | ⭐️⭐️⭐️ (self-hosted HTTP) | ⭐️⭐️⭐️⭐️ | ⭐️⭐️ (SQL + files, not code-native) |

## Positioning

`youtube-helper` deliberately sits at the intersection of **yt-dlp's
raw coverage** and **AI / personal-branding pipeline ergonomics**. It
does not compete with yt-dlp on extractor breadth (it *is* yt-dlp under
the hood). What it adds:

- **Normalised return shapes** — engagement metrics use the same schema
  across YouTube / Vimeo / DailyMotion / Twitch, so downstream code
  doesn't need per-site branches.
- **Direct-URL resolver + stream catalog + picker** — turns yt-dlp's
  raw `formats` list into a first-class object with codec / fps / lang
  filters, ready to hand off to `ffmpeg` / `video-helper.extract_frames`.
- **No-API branding metadata** — channel-level snapshots, per-video
  engagement, comment samples, subtitle downloads without touching the
  Google Data API (no OAuth, no quota, no client_id / secret dance).
- **Multi-surface exposure** — the same operations are available as a
  Python library, an argparse CLI, a click CLI, a FastAPI HTTP
  surface, and MCP tools. `yt-dlp` gives you the first two; the last
  three are unique to this wrapper.
- **Docker-ready** — one `docker run` and you have a local HTTP + MCP
  server for any yt-dlp-supported URL.

## When to pick what

- **`youtube-helper`** — download + engagement metadata for AI /
  personal-branding pipelines, especially when you want the same
  toolkit as library, CLI, HTTP, and MCP.
- **`yt-dlp`** (direct) — you already own the pipeline and just need
  the raw info dict / files, no normalisation layer needed.
- **`youtube-dl`** — legacy code paths; migration to `yt-dlp` is
  strongly recommended.
- **`pytube` / `pytubefix`** — pure Python, no yt-dlp dependency, but
  YouTube-only and slightly behind on extractor updates.
- **YouTube Data API** — you need canonical view / like / subscriber
  counts, retention / analytics data, or you are already paying the
  OAuth + quota cost.
- **Playwright / Selenium** — the site does not expose an extractor and
  you need to scrape the rendered page.
- **`streamlink`** — live-first workflow; you want to hand a live URL
  straight to a player without recording.
- **`youtube_transcript_api`** — you only need transcripts, no
  downloads, no other metadata.
- **ArchiveBox** — you are building a personal archive of URLs with a
  self-hosted UI, not a code-native pipeline.
