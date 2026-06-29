# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-06-29

### Added

- `extract_frames_stream(url, ...)` — one-call composition of
  `pick_video_stream` + `video_helper.extract_frames`. Resolves a
  yt-dlp-supported URL to its best matching video stream, plumbs the
  resolver's `http_headers` automatically into the decoder, and
  forwards any `extract_frames` kwarg (`destination`, `device`,
  `batch_size`, `output_width` / `output_height`, `frame_step` /
  `frame_interval`, `backend`, `hwaccel`, …) verbatim. Lets the
  documented "stream-to-frames" recipe collapse from two calls into
  one without losing any of the existing knobs.

### Changed

- Bump `video-helper` pin from `v1.5.1` to `v1.5.2` — adds URL-aware
  `is_valid_video_file` (short-circuits to `True` for `http(s)://`
  inputs) and `video_dimensions(http_headers=...)` so the resolved
  direct media URL passes through the assertion + metadata probe at
  the top of `extract_frames`.

### Tests

- `tests/test_extract_frames_stream.py` — 7 unit tests covering the
  wrapper's URL forwarding, picker constraint passthrough, automatic
  header wiring, explicit-header override, extract_frames kwarg
  passthrough, and package-root export. Network-free
  (`pick_video_stream` and `video_helper.extract_frames` are
  monkeypatched).

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
