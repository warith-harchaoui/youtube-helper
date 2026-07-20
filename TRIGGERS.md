# TRIGGERS — youtube-helper

This is the user-facing, exhaustive catalogue of what `youtube-helper` can do and
the natural-language phrasings, commands, functions, and site cues that should
invoke it — whether you call it yourself or drive it as a Claude / OpenCode
**skill** (see [`skills/youtube-helper/SKILL.md`](skills/youtube-helper/SKILL.md)
and its [`references/triggers.md`](skills/youtube-helper/references/triggers.md)).

`youtube-helper` **fetches** online media and metadata from a page URL (yt-dlp +
ffmpeg) and writes files locally. It is local-first: it downloads only what you
ask for; nothing is uploaded to a third party. It does **not** transform local
files, transcribe, synthesize, or upload.

## Operations → how to invoke

| Intent | CLI | Library | API / MCP |
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
- **Surfaces**: "run the youtube-helper API / MCP server", "open the download
  GUI", "install youtube-helper".

## Sites it supports

YouTube, Vimeo, DailyMotion, Twitch VOD, SoundCloud, and any other site
`yt-dlp` supports — do not assume YouTube-only.

## When NOT to use youtube-helper (SKIP)

- Transforming a LOCAL media file (convert / chunk / concat / stems / room-tone /
  MFCC) → use `audio-helper`; frames / probe / convert a local video →
  `video-helper`.
- Transcription / captions from a local audio file / speech-to-text →
  `vocal-helper` / a whisper skill. (Downloading a video's *existing* subtitle
  track is youtube-helper.)
- Text-to-speech, voice cloning, synthesis, music generation.
- Uploading / publishing to YouTube — youtube-helper is download + read only.
- Decoding a resolved stream to PCM for a podcast pipeline → `podcast-helper`.

## See also

- [`README.md`](README.md) — features, install, quick start.
- [`EXAMPLES.md`](EXAMPLES.md) — runnable recipes.
- [`GUI.md`](GUI.md) — the shipped minimal GUI + the roadmap for a richer one.
- [`skills/README.md`](skills/README.md) — installing this as an agent skill.
