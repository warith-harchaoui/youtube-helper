# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Documentation

- Establish suite-wide Python coding-style mandate in `CONTRIBUTING.md`:
  numpy-style docstrings on every function and class, module-level
  docstring header (with usage example + author), full type annotations,
  generous explanatory comments.
- `EXAMPLES.md` cookbook present at the repo root and linked from
  README + LISEZMOI.
- `print(...)` in docs (EXAMPLES.md / README / LISEZMOI) is followed by
  a `#`-comment showing the expected output (doctest / REPL style);
  library `.py` code uses `osh.info` / `osh.warning` / `osh.error`
  instead of bare `print`.
- Every `brew install <pkg>` mention is paired with a brew.sh hint when
  not already obvious from context.
- `.gitignore` updated to drop accidental `*config.json` commits while
  keeping `*config.json.example` templates tracked.

### Changed

- Add GitHub Actions CI.

## [1.1.0] - 2026-06-29

First release under the `youtube-helper` name (formerly the
`yt-helper` repository, renamed for PyPI naming-conflict reasons).

### Features at release

- **Downloads (to disk)** — `youtube_helper.main`:
  `download_video` / `download_audio` / `download_thumbnail`,
  `video_url_meta_data`, `is_valid_video_url`,
  `default_ytdlp_options`.
- **Stream catalog & direct-URL resolution** —
  `youtube_helper.streaming`: `resolve_direct_url`,
  `list_video_streams`, `pick_video_stream` (constrained picker
  for video-helper consumption).
- **No-API engagement metadata** — `youtube_helper.branding`:
  `channel_info`, `channel_videos`, `video_engagement`,
  `engagement_batch`, `video_subtitles`, `video_comments`,
  `is_short`, `ensure_recent_ytdlp`. All built on yt-dlp public
  metadata — no Google Data API, no Vimeo API, no OAuth, no quota.
