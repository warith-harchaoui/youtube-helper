---
name: youtube-helper
description: >-
  Download and inspect online media with the `youtube-helper` toolkit — a
  local-first yt-dlp + ffmpeg wrapper. Download a video (best video+audio muxed
  to mp4), download just the audio track (re-encoded to mp3 at a chosen sample
  rate), download a thumbnail, extract yt-dlp metadata, resolve a page URL to a
  direct ffmpeg-ready media URL, enumerate / pick a video stream from the format
  catalog, stream frames straight to ML-ready arrays, and pull no-API engagement
  metadata (channel snapshot, channel video list, per-video views/likes/comments,
  auto-subtitles, comments) across YouTube, Vimeo, DailyMotion, Twitch VOD,
  SoundCloud, and any other site yt-dlp supports. Exposed as a Python library
  (`import youtube_helper as yth`), two CLIs (`youtube-helper` argparse and
  `youtube-helper-click`), a FastAPI HTTP surface, an MCP tool set, and a minimal
  browser GUI at `/gui` (paste a URL → audio or video + quality → download).
  Local-first: it fetches only the media you ask for, no telemetry, no account.

  TRIGGER — any of: the user pastes or references a media URL and wants it
  saved locally ("download this YouTube video / audio / mp3 / mp4", "grab the
  audio from this link", "save this Vimeo / DailyMotion / Twitch VOD /
  SoundCloud clip", "rip the soundtrack of this video", "get the thumbnail of
  this video", "download subtitles / captions for this URL"); the user wants
  metadata or engagement about a URL without downloading the media ("what's the
  title / duration / description of this video", "how many views / likes /
  comments does this have", "list this channel's videos", "channel subscriber
  count", "pull the top comments", "is this a valid video URL"); the user wants
  a direct/streamable media URL or the format catalog ("resolve this to a direct
  mp4/audio URL", "list the available streams / formats / resolutions", "pick
  the 1080p h264 stream", "stream frames from this URL"); the user types or
  references a command (`youtube-helper`, `youtube-helper-click`,
  `youtube-helper-mcp`, subcommands `metadata|valid|video|audio|thumbnail|
  resolve|list-streams|pick-stream|channel-info|channel-videos|engagement|
  engagement-batch|subtitles|comments|ytdlp-version`) or a library function
  (`download_video`, `download_audio`, `download_thumbnail`,
  `video_url_meta_data`, `is_valid_video_url`, `resolve_direct_url`,
  `list_video_streams`, `pick_video_stream`, `extract_frames_stream`,
  `channel_info`, `channel_videos`, `video_engagement`, `engagement_batch`,
  `video_subtitles`, `video_comments`, `is_short`, `ensure_recent_ytdlp`); the
  user wants the download API/MCP server run, or the paste-a-URL GUI; the user
  asks to install/run youtube-helper.

  SKIP when: the media is already a LOCAL file and the task is transforming it —
  converting / chunking / concatenating / separating stems / room-tone / MFCC
  similarity (use audio-helper); extracting frames / probing / converting a
  local video file (use video-helper); speech-to-text / transcription / captions
  from a local audio file (use vocal-helper / a whisper skill); text-to-speech,
  voice cloning, music generation; uploading / publishing to YouTube (this is
  download + read only, never upload); decoding a resolved stream to PCM for a
  podcast pipeline (that ownership lives in podcast-helper). youtube-helper
  FETCHES media and metadata from URLs; it does not transform local files,
  transcribe, synthesize, or upload.
---

# youtube-helper — download & inspect online media

`youtube-helper` is a small, local-first Python toolkit that wraps `yt-dlp` and
`ffmpeg`. You give it a page URL, it writes a file on disk (or returns a metadata
dict). The same functions are reachable five ways (library, two CLIs, HTTP API,
MCP, GUI) so an agent can pick whichever fits.

## Before anything: verify it is installed

```bash
youtube-helper --version            # argparse CLI (always installed with the pkg)
python -c "import youtube_helper"   # library import check
```

If missing, install it (yt-dlp and ffmpeg are hard system dependencies):

```bash
pip install youtube-helper                 # core (download / metadata / streams)
pip install 'youtube-helper[cli]'          # + click CLI twin
pip install 'youtube-helper[api]'          # + FastAPI HTTP surface + GUI
pip install 'youtube-helper[api,mcp]'      # + MCP tools over FastAPI
```

yt-dlp and ffmpeg must be on PATH:
- macOS 🍎 : `brew install yt-dlp ffmpeg` (install `brew` via [brew.sh](https://brew.sh/))
- Ubuntu 🐧 : `sudo apt install yt-dlp ffmpeg`
- Windows 🪟 : `winget install yt-dlp.yt-dlp Gyan.FFmpeg`

## The core operations

Same names across the library, both CLIs, the API, and the MCP tools:

| Intent | CLI | Library function |
|--------|-----|------------------|
| Download video (best video+audio) | `youtube-helper video` | `download_video` |
| Download audio only (mp3) | `youtube-helper audio` | `download_audio` |
| Download thumbnail | `youtube-helper thumbnail` | `download_thumbnail` |
| Metadata dict for a URL | `youtube-helper metadata` | `video_url_meta_data` |
| Is this a valid video URL? | `youtube-helper valid` | `is_valid_video_url` |
| Resolve to a direct media URL | `youtube-helper resolve` | `resolve_direct_url` |
| List the video-format catalog | `youtube-helper list-streams` | `list_video_streams` |
| Pick one best stream | `youtube-helper pick-stream` | `pick_video_stream` |
| Channel snapshot | `youtube-helper channel-info` | `channel_info` |
| Channel video list | `youtube-helper channel-videos` | `channel_videos` |
| Per-video engagement | `youtube-helper engagement` | `video_engagement` |
| Batched engagement | `youtube-helper engagement-batch` | `engagement_batch` |
| Auto-subtitles | `youtube-helper subtitles` | `video_subtitles` |
| Top comments | `youtube-helper comments` | `video_comments` |
| yt-dlp freshness check | `youtube-helper ytdlp-version` | `ensure_recent_ytdlp` |

Quick examples:

```bash
youtube-helper video     --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --output out.mp4
youtube-helper audio     --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --output out.mp3 --sample-rate 16000
youtube-helper metadata  --url https://www.youtube.com/watch?v=YE7VzlLtp-4
youtube-helper resolve   --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --prefer audio
youtube-helper channel-info --url https://www.youtube.com/@blender
```

```python
import youtube_helper as yth
meta = yth.video_url_meta_data("https://www.youtube.com/watch?v=YE7VzlLtp-4")
yth.download_audio("https://www.youtube.com/watch?v=YE7VzlLtp-4", "out.mp3")
yth.download_video("https://www.youtube.com/watch?v=YE7VzlLtp-4", "out.mp4")
```

For the full flag matrix and every option, read `references/cli-reference.md`.
For the API / MCP / GUI surfaces (endpoints, ports, the `/gui` download bench),
read `references/surfaces.md`. For the exhaustive, auditable trigger list, read
`references/triggers.md`.

## Rules of thumb

- **Pick the operation from the intent, not the site.** "get the mp3" →
  `audio`; "save the video" → `video`; "how many views" → `engagement`; "list
  the channel's uploads" → `channel-videos`; "give me a streamable URL" →
  `resolve`.
- **All these sites work** — YouTube, Vimeo, DailyMotion, Twitch VOD,
  SoundCloud, and anything else yt-dlp supports. Do not assume YouTube-only.
- **No Google Data / Vimeo API, no OAuth, no quota.** Engagement metadata comes
  from yt-dlp's public metadata only.
- **Bot-blocked environments** (CI on datacenter IPs, "Sign in to confirm you're
  not a bot"): set `YOUTUBE_HELPER_COOKIES` to a Netscape-format cookies.txt and
  yt-dlp will use it. Live YouTube downloads are not attempted in CI by design.
- **After running, report the output path(s)** the tool printed and hand them
  back — do not re-run unless something failed.
- **Local-first.** It fetches only the media you ask for from the source site;
  nothing is uploaded to a third party, no telemetry, no account. It never
  uploads or publishes.
