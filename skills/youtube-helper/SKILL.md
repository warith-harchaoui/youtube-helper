---
name: youtube-helper
description: >-
  Probe and download from YouTube and every other yt-dlp-reachable site
  (Vimeo, Twitch, SoundCloud, direct media URLs). Validate a URL, read its
  metadata, resolve the direct media URL without downloading, list and pick
  among available streams, download the video, the audio only, the thumbnail
  or the subtitles, read channel info and a channel's video list, and pull
  engagement figures (views, likes, comments) for one video or a batch. Use
  when the user says "download this YouTube video", "get the audio / mp3 from
  this link", "grab the thumbnail", "download the subtitles / captions", "what
  is the title / duration / uploader of this URL", "is this a valid video
  URL", "how many views does this have", "list this channel's videos", "best
  quality stream", "is this a Short", or names `youtube-helper`,
  `youtube-helper-mcp`, `import youtube_helper as yh`, `yt-dlp`. Do NOT use to
  transcribe (vocal-helper), edit the downloaded file (video-helper /
  audio-helper), or read a podcast RSS feed (podcast-helper).
license: BSD-3-Clause
metadata:
  author: Warith Harchaoui
  package: youtube-helper
  suite: ai-helpers
  homepage: https://deraison.ai/ai-helpers
---

# youtube-helper — probe and download from yt-dlp-reachable sites

`youtube-helper` is the suite's **media acquisition** layer for web video. It
wraps `yt-dlp` with a stable API, suite logging, and the probing calls that
usually come before a download. It downloads and reports; it does not
transcode, transcribe, or publish.

Network traffic is the whole point here — but it goes to the platform and
nowhere else. No account, no telemetry, no third-party relay, and output lands
on local paths you choose.

## Before anything: verify it is installed

```bash
youtube-helper ytdlp-version         # proves the CLI and yt-dlp are both live
python -c "import youtube_helper"    # library import check
ffmpeg -version                      # needed for merged / converted output
```

Install:

```bash
pip install youtube-helper                 # core: library + command line
pip install 'youtube-helper[api]'          # + FastAPI HTTP surface and GUI
pip install 'youtube-helper[mcp]'          # + MCP tools over the same app
```

## What it does, and how to invoke it

| Intent | CLI | Library |
|---|---|---|
| Is this a usable video URL | `youtube-helper valid --url URL` | `is_valid_video_url` |
| Title, duration, uploader, … | `youtube-helper metadata --url URL` | `video_url_meta_data` |
| Direct media URL, no download | `youtube-helper resolve --url URL` | `resolve_direct_url` |
| What streams exist | `youtube-helper list-streams --url URL` | `list_video_streams` |
| Choose a stream by constraints | `youtube-helper pick-stream --url URL` | `pick_video_stream` |
| Download the video | `youtube-helper video --url URL` | `download_video` |
| Download the audio only | `youtube-helper audio --url URL` | `download_audio` |
| Download the thumbnail | `youtube-helper thumbnail --url URL` | `download_thumbnail` |
| Download the subtitles | `youtube-helper subtitles --url URL --output-dir DIR` | `video_subtitles` |
| Channel info / video list | `youtube-helper channel-info --url URL`, `channel-videos --url URL` | `channel_info`, `channel_videos` |
| Views, likes, comment count | `youtube-helper engagement --url URL` | `video_engagement` |
| The same for many URLs | `youtube-helper engagement-batch --urls URL --urls URL` | `engagement_batch` |
| Fetch the comments | `youtube-helper comments --url URL` | `video_comments` |
| Which yt-dlp is in play | `youtube-helper ytdlp-version` | `ensure_recent_ytdlp` |

Quick examples:

```bash
youtube-helper metadata  --url "https://youtu.be/YE7VzlLtp-4"
youtube-helper audio     --url "https://youtu.be/YE7VzlLtp-4" --output talk.mp3
youtube-helper video     --url "https://youtu.be/YE7VzlLtp-4" --max-height 720
youtube-helper subtitles --url "https://youtu.be/YE7VzlLtp-4" --output-dir ./subs --langs en
```

```python
import youtube_helper as yh

meta = yh.video_url_meta_data(url)  # title, duration, uploader, …
path = yh.download_audio(url, output_path="./dl/talk.mp3")
for frame in yh.extract_frames_stream(url):  # frames without a full download
    ...
```

For the full flag matrix and the output contract, read
`references/cli-reference.md`. For the HTTP API, MCP tools and the GUI, read
`references/surfaces.md`. For the exhaustive trigger list, read
`references/triggers.md`.

## Rules of thumb

- **Probe before you download.** `valid` then `metadata` costs one cheap call
  and tells you the duration before you commit to pulling a three-hour stream.
- **Audio-only when audio is the target.** `download_audio` fetches an
  audio-only stream — far smaller and faster than downloading the video and
  stripping it afterwards.
- **`resolve` when you do not need the bytes on disk.** It hands back a direct
  media URL another tool can stream, and `extract_frames_stream` reads frames
  without materialising the file at all.
- **This package acquires; siblings transform.** Re-encode with
  `video-helper`, resample with `audio-helper`, transcribe with
  `vocal-helper`. Do not reach for raw ffmpeg in between.
- **yt-dlp ages fast.** When a download suddenly fails on a site that used to
  work, run `ytdlp-version` / `ensure_recent_ytdlp` and upgrade before
  debugging anything else — extractor rot is the usual cause.
- **Respect the source.** Download what the user is entitled to; do not batch
  through a channel to build a corpus without them saying that is the intent.
- **After downloading, report the path, the real duration and the size** — do
  not re-download to confirm.
