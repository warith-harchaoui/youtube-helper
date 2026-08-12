# Landscape

[🇫🇷 PAYSAGE.md](https://github.com/warith-harchaoui/youtube-helper/blob/main/PAYSAGE.md) · 🇬🇧 English

Related and competing Python (and adjacent) tools in the "download and
inspect online video and audio" space, benchmarked against
`youtube-helper`. Ratings run from ⭐ (1) to ⭐⭐⭐⭐⭐ (5), scored on
`youtube-helper`'s intended job: everyday YouTube, Vimeo, DailyMotion,
and Twitch downloads, plus no-API engagement metadata for personal-branding
and AI pipelines. A tool optimised for a very different job, archival
mirroring or torrent-based re-uploads for instance, is not penalised;
the score just reflects fit to *this* niche.

## At a glance

<!-- TABLE:START -->
| Media Downloading | Multi-platform | Media download | Direct-URL resolver | Stream picker | No-API engagement | Multi-surface | Docker-ready | AI-pipeline ergonomics |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **youtube-helper** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| yt-dlp | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| youtube-dl | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ |
| pytube | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| pytubefix | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| streamlink | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| gallery-dl | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| scrapetube | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| youtube-comment-downloader | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| google-api-python-client | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
<!-- TABLE:END -->

## Positioning map

<!-- FIGURE:START -->
2D representation of the table above.

![Positioning map](https://raw.githubusercontent.com/warith-harchaoui/youtube-helper/main/assets/landscape.png)

The map is a 2-D summary of the eight criteria, so read it as a shape, not a scoreboard. `youtube-helper` is at the top-right corner. The axes read **Horizontal — Accessible ↔ Versatile** and **Vertical — Convenient ↔ Adaptable**.
<!-- FIGURE:END -->

## Positioning

`youtube-helper` deliberately sits at the intersection of **yt-dlp's
raw coverage** and **AI and personal-branding pipeline ergonomics**. It
does not compete with yt-dlp on extractor breadth; it *is* yt-dlp under
the hood. What it adds:

- **Normalised return shapes**: engagement metrics use the same schema
  across YouTube, Vimeo, DailyMotion, and Twitch, so downstream code
  needs no per-site branches. This is the gap behind yt-dlp's
  raw-info-dict rating: the data is there, but not normalised.
- **Direct-URL resolver, stream catalog, and picker**: turns yt-dlp's
  raw `formats` list into a first-class object with codec, fps, and
  language filters, ready to hand off to `ffmpeg` or `video-helper.extract_frames`.
- **No-API branding metadata**: channel-level snapshots, per-video
  engagement, comment samples, and subtitle downloads without touching
  the Google Data API, so no OAuth, no quota, no client_id/secret dance.
  `google-api-python-client` scores top marks on engagement precisely
  because it is canonical, but it returns no media files and costs OAuth
  and quota.
- **Multi-surface exposure**: the same operations are available as a
  Python library, an argparse CLI, a click CLI, and a FastAPI HTTP
  surface. `yt-dlp` gives you the first two; the last two are unique
  to this wrapper.
- **Docker-ready**: one `docker run` and you have a local HTTP
  server for any yt-dlp-supported URL.

## When to pick what

- **`youtube-helper`**: download and engagement metadata for AI and
  personal-branding pipelines, especially when you want the same
  toolkit as library, CLI, and HTTP.
- **`yt-dlp`** (direct): you already own the pipeline and just need
  the raw info dict or files, no normalisation layer needed.
- **`youtube-dl`**: legacy code paths; the extractor set has drifted,
  so migration to `yt-dlp` is strongly recommended.
- **`pytube` / `pytubefix`**: pure Python, no yt-dlp dependency, but
  YouTube-only and slightly behind on extractor updates (`pytubefix`
  is the maintained fork).
- **`google-api-python-client`**: you need canonical view, like, or
  subscriber counts, retention or analytics data, or you are already
  paying the OAuth and quota cost.
- **`streamlink`**: live-first workflow; you want to hand a live URL
  straight to a player without recording.
- **`gallery-dl`**: bulk image or media gallery downloads across many
  sites; coverage is broad but it is not built around video streams or
  engagement metadata.
- **`scrapetube`**: you only need to enumerate a channel, playlist, or
  search result's video IDs without the Data API, no downloads.
- **`youtube-comment-downloader`**: you only need to bulk-scrape a
  video's comments without touching the Data API, nothing else.
