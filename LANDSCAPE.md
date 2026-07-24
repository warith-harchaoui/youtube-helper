# Landscape

[🇫🇷 PAYSAGE.md](https://github.com/warith-harchaoui/youtube-helper/blob/main/PAYSAGE.md) · 🇬🇧 English

Related and competing Python (and adjacent) tools in the "download and
inspect online video / audio" space, benchmarked against
`youtube-helper`. Ratings are ⭐ (1) to ⭐⭐⭐⭐⭐ (5), scored on
`youtube-helper`'s intended job — everyday YouTube / Vimeo / DailyMotion
/ Twitch download plus no-API engagement metadata for personal-branding
and AI pipelines. A tool optimised for a very different job (e.g.
archival mirroring, torrent-based re-uploads) is not penalised — the
score just reflects fit to *this* niche.

## At a glance

| Media Downloading | Multi-platform | Media download | Direct-URL resolver | Stream picker | No-API engagement | Multi-surface | Docker-ready | AI-pipeline ergonomics |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **youtube-helper** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| yt-dlp | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| youtube-dl | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ |
| pytube | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| pytubefix | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| YouTube Data API | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| you-get | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ |
| streamlink | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| youtube_transcript_api | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| ArchiveBox | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

## Positioning map

2D representation of the table above.

![Positioning map](https://raw.githubusercontent.com/warith-harchaoui/youtube-helper/main/assets/landscape.png)

The map is a 2-D summary of the eight criteria, so read it as a shape, not a scoreboard. `youtube-helper` is at the top-right corner. The axes read **Horizontal — Engagement ↔ Resolver** and **Vertical — Download ↔ Surface**.

## Positioning

`youtube-helper` deliberately sits at the intersection of **yt-dlp's
raw coverage** and **AI / personal-branding pipeline ergonomics**. It
does not compete with yt-dlp on extractor breadth (it *is* yt-dlp under
the hood). What it adds:

- **Normalised return shapes** — engagement metrics use the same schema
  across YouTube / Vimeo / DailyMotion / Twitch, so downstream code
  doesn't need per-site branches. This is the gap behind yt-dlp's
  raw-info-dict rating: the data is there, but un-normalised.
- **Direct-URL resolver + stream catalog + picker** — turns yt-dlp's
  raw `formats` list into a first-class object with codec / fps / lang
  filters, ready to hand off to `ffmpeg` / `video-helper.extract_frames`.
- **No-API branding metadata** — channel-level snapshots, per-video
  engagement, comment samples, subtitle downloads without touching the
  Google Data API (no OAuth, no quota, no client_id / secret dance).
  The `YouTube Data API` scores top marks on engagement precisely
  because it is canonical, but it returns no media files and costs OAuth
  + quota.
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
- **`youtube-dl`** — legacy code paths; the extractor set has drifted,
  so migration to `yt-dlp` is strongly recommended.
- **`pytube` / `pytubefix`** — pure Python, no yt-dlp dependency, but
  YouTube-only and slightly behind on extractor updates (`pytubefix`
  is the maintained fork).
- **YouTube Data API** — you need canonical view / like / subscriber
  counts, retention / analytics data, or you are already paying the
  OAuth + quota cost.
- **`you-get`** — a broad multi-site downloader when yt-dlp is not an
  option; coverage is wide but below yt-dlp.
- **`streamlink`** — live-first workflow; you want to hand a live URL
  straight to a player without recording.
- **`youtube_transcript_api`** — you only need transcripts, no
  downloads, no other metadata.
- **ArchiveBox** — you are building a personal archive of URLs with a
  self-hosted UI, not a code-native pipeline.
