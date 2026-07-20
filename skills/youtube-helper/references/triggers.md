# youtube-helper skill — exhaustive trigger catalogue

Auditable superset of the `description:` TRIGGER clause in `SKILL.md` (the
description is what a host model sees before loading; this file is the
human-reviewable full list). Keep the two in sync, and mirror the repo-root
`TRIGGERS.md`.

## Fire (positive triggers)

**Download media to disk**
- "download this YouTube video", "save this video as mp4"
- "get the audio / mp3 from this link", "rip the soundtrack / audio track"
- "download this Vimeo / DailyMotion / Twitch VOD / SoundCloud clip"
- "grab the thumbnail / cover image of this video"
- "download the subtitles / captions / .vtt for this URL"

**Metadata & validation (no download)**
- "what's the title / duration / description / uploader of this video"
- "is this a valid video URL", "can yt-dlp handle this link"

**Engagement / branding (no Google Data API, no OAuth)**
- "how many views / likes / comments does this video have"
- "list this channel's videos / uploads", "channel subscriber count"
- "give me a channel snapshot", "pull the top N comments"
- "compare engagement across these URLs" (batch)

**Direct URL / stream catalog / frames**
- "resolve this to a direct mp4 / audio URL I can stream"
- "list the available streams / formats / resolutions / codecs"
- "pick the 1080p / h264 / vp9 / av1 stream", "best mp4 under 30 fps"
- "stream frames from this URL", "URL to ML-ready frames"

**Explicit command / function mentions**
- `youtube-helper`, `youtube-helper-click`, `youtube-helper-mcp`
- subcommands `metadata valid video audio thumbnail resolve list-streams
  pick-stream channel-info channel-videos engagement engagement-batch subtitles
  comments ytdlp-version`
- functions `download_video download_audio download_thumbnail
  video_url_meta_data is_valid_video_url resolve_direct_url list_video_streams
  pick_video_stream extract_frames_stream channel_info channel_videos
  video_engagement engagement_batch video_subtitles video_comments is_short
  ensure_recent_ytdlp default_ytdlp_options`

**Surfaces**
- "run the youtube-helper API / download server", "expose these as HTTP / MCP tools"
- "open the download GUI / download bench", "paste-a-URL downloader"
- "how do I install / run youtube-helper"

**Site cues** (with a download / inspect intent)
- youtube.com, youtu.be, vimeo.com, dailymotion.com, twitch.tv (VOD),
  soundcloud.com, and any other yt-dlp-supported site.

## Do NOT fire (SKIP)

- **Transforming a LOCAL media file** — convert / chunk / concat / stems /
  room-tone / MFCC similarity → `audio-helper`; frames / probe / convert a local
  video → `video-helper`. youtube-helper fetches; it does not transform local files.
- **Transcription / captions from a local audio file / speech-to-text** →
  `vocal-helper` / a whisper skill. (Downloading a video's *existing* subtitle
  track IS youtube-helper.)
- **Text-to-speech / voice cloning / synthesis / music generation** → not this skill.
- **Uploading / publishing to YouTube** → youtube-helper is download + read only,
  never upload.
- **Decoding a resolved stream to PCM for a podcast pipeline** → ownership lives
  in `podcast-helper` (youtube-helper only *resolves* the direct URL).

## Enforcement checklist

A trigger is "enforced" when (1) it is represented in `SKILL.md`'s `description`
TRIGGER clause so the host sees it pre-load; (2) the SKIP clause is present so the
skill does not over-fire; (3) this catalogue lists the positive and negative
buckets so a human can audit coverage against the description.
