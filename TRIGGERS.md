# TRIGGERS: youtube-helper

This is the user-facing, exhaustive catalogue of what `youtube-helper` can do and
the natural-language phrasings, commands, functions, and site cues that should
invoke it.

`youtube-helper` **fetches** online media and metadata from a page URL (yt-dlp +
ffmpeg) and writes files locally. It is local-first: it downloads only what you
ask for; nothing is uploaded to a third party. It does **not** transform local
files, transcribe, synthesize, or upload.

## Operations → how to invoke

| Intent | CLI | Library | API |
|--------|-----|---------|-----------|
| Download video (best video+audio) | `youtube-helper video` | `download_video` | `POST /video` |
| Download audio only (mp3) | `youtube-helper audio` | `download_audio` | `POST /audio` |
| Download thumbnail | `youtube-helper thumbnail` | `download_thumbnail` | `POST /thumbnail` |
| Metadata dict for a URL | `youtube-helper metadata` | `video_url_meta_data` | `POST /metadata` |
| Validate a video URL | `youtube-helper valid` | `is_valid_video_url` | `POST /valid` |
| Resolve to a direct media URL | `youtube-helper resolve` | `resolve_direct_url` | `POST /resolve` |
| List the video-format catalog | `youtube-helper list-streams` | `list_video_streams` | `POST /list-streams` |
| Pick one best stream | `youtube-helper pick-stream` | `pick_video_stream` | `POST /pick-stream` |
| Channel snapshot | `youtube-helper channel-info` | `channel_info` | `POST /channel-info` |
| Channel video list | `youtube-helper channel-videos` | `channel_videos` | `POST /channel-videos` |
| Per-video engagement | `youtube-helper engagement` | `video_engagement` | `POST /engagement` |
| Batched engagement | `youtube-helper engagement-batch` | `engagement_batch` | `POST /engagement-batch` |
| Auto-subtitles | `youtube-helper subtitles` | `video_subtitles` | `POST /subtitles` |
| Top comments | `youtube-helper comments` | `video_comments` | `POST /comments` |
| yt-dlp freshness check | `youtube-helper ytdlp-version` | `ensure_recent_ytdlp` | `POST /ytdlp-version` |

Every operation is also reachable through the click CLI (`youtube-helper-click …`,
same flags) and the download bench GUI at `GET /gui` (audio/video downloads).

## Natural-language phrasings that should fire

- **Download**: "download this YouTube video / audio / mp3 / mp4", "save this
  Vimeo / DailyMotion / Twitch VOD / SoundCloud clip", "rip the soundtrack",
  "grab the thumbnail", "download the subtitles for this URL".
- **Metadata**: "what's the title / duration / description", "is this a valid
  video URL".
- **Engagement**: "how many views / likes / comments", "list this channel's
  videos", "channel subscriber count", "pull the top comments".
- **Streams**: "resolve this to a direct mp4 / audio URL", "list the available
  formats / resolutions", "pick the 1080p h264 stream", "stream frames from
  this URL".
- **Surfaces**: "run the youtube-helper API server", "open the download
  GUI", "install youtube-helper".

## Sites it supports

YouTube, Vimeo, DailyMotion, Twitch VOD, SoundCloud, and any other site
`yt-dlp` supports. Do not assume YouTube-only.

## When a download is refused, or crawls

Two failures look alike from outside and are not the same thing. Read the message.

**"Sign in to confirm you're not a bot".** YouTube scores the request, not you. The fix that
costs nothing and reads nobody's data is to ask as a different client: YouTube does not apply
the same checks to its web, mobile, TV and embedded players. `youtube-helper` now does this
automatically, trying `web_embedded`, `tv`, `android_vr` then `mweb` before it ever considers
borrowing cookies or routing through Tor. Override the list with
`YOUTUBE_HELPER_PLAYER_CLIENTS` (comma-separated; empty disables the rung).

**"The uploader has not made this video available in your country".** That is a geo-block, not
a bot check, and no client, cookie or User-Agent will clear it. `YOUTUBE_HELPER_TOR_PROXY` is
the rung that can, when an exit node happens to sit in the right country.

**The download crawls at a few hundred KiB/s.** That is almost always fragmented HLS, which
YouTube throttles hard. Measured on one 1h42 episode: 75-300 KiB/s across 1507 fragments,
against ~2 MiB/s for the same video's direct https format, which was also eight times smaller.
Pass `--max-height 720` (or `max_height=720`, or set `YOUTUBE_HELPER_MAX_HEIGHT`): the capped
selector prefers direct https formats and only falls back to HLS if nothing else exists. The
same flag is what you want when the destination has a size limit, e.g. a FAT32 volume, which
refuses any file over 4 GiB.

| Knob | Env | CLI | Library |
|---|---|---|---|
| Cap height, prefer non-HLS | `YOUTUBE_HELPER_MAX_HEIGHT` | `--max-height 720` | `download_video(..., max_height=720)` |
| Which clients to retry as | `YOUTUBE_HELPER_PLAYER_CLIENTS` | n. a. | `default_ytdlp_options(..., player_clients=[...])` |
| Borrow browser cookies | `YOUTUBE_HELPER_COOKIES_FROM_BROWSER` | n. a. | n. a. |
| Cookie file (Netscape) | `YOUTUBE_HELPER_COOKIES` | n. a. | n. a. |
| Tor proxy | `YOUTUBE_HELPER_TOR_PROXY` | n. a. | n. a. |

Nothing here depends on one person's machine: every knob is an environment variable or an
argument, all default to the previous behaviour, and the automatic client fallback needs no
configuration at all.

## When NOT to use youtube-helper (SKIP)

- Transforming a LOCAL media file (convert / chunk / concat / stems / room-tone /
  MFCC) → use `audio-helper`; frames / probe / convert a local video →
  `video-helper`.
- Transcription / captions from a local audio file / speech-to-text →
  `vocal-helper` / a whisper skill. (Downloading a video's *existing* subtitle
  track is youtube-helper.)
- Text-to-speech, voice cloning, synthesis, music generation.
- Uploading or publishing to YouTube: youtube-helper is download and read only.
- Decoding a resolved stream to PCM for a podcast pipeline → `podcast-helper`.

## See also

- [`README.md`](README.md): features, install, quick start.
- [`EXAMPLES.md`](EXAMPLES.md): runnable recipes.
- [`GUI.md`](GUI.md): the shipped minimal GUI and the roadmap for a richer one.
