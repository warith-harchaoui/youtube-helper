# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.9] - 2026-07-18

### Added

- Support authenticated downloads via a cookies file: set the `YOUTUBE_HELPER_COOKIES` environment variable to a Netscape-format cookies.txt and yt-dlp uses it. This is the reliable way to download from environments YouTube bot-blocks (e.g. CI on datacenter IPs, which otherwise get 'Sign in to confirm you're not a bot').

## [1.3.8] - 2026-07-18

### Fixed

- Stopped skipping the YouTube player JS (`player_skip=js`). Modern yt-dlp needs
  it to decipher formats and negotiate a proof-of-origin (PO) token; without it,
  downloads from datacenter IPs fail with 'Sign in to confirm you're not a bot'.

## [1.3.7] - 2026-07-18

### Fixed

- Removed `force_generic_extractor` from the default yt-dlp options. It forced
  yt-dlp's generic extractor, which modern yt-dlp (2025.07+) rejects with
  `ERROR: Unsupported URL` on youtube.com / vimeo / etc.; yt-dlp now selects
  the correct site extractor, so downloads work again on current yt-dlp.

## [1.3.6] - 2026-07-18

### Fixed

- yt-dlp's session cookie jar is no longer written to the current working
  directory (which left a stray `<timestamp>_ytdlp_cookie.txt` next to
  callers). `default_ytdlp_options` now takes an optional `cookie_dir`; the
  download helpers pass their temporary folder so the jar is removed on
  context exit, and metadata-only calls keep cookies in memory.

## [1.3.5] - 2026-07-15

### Documentation

- Harmonize README/LISEZMOI to the AI Helpers common structure (single H1,
  PyPI + source install paths, refreshed pins to v1.3.5); no code changes.

## [1.3.4] - 2026-07-14

### Maintenance

- Apply the project coding standards across the package and `tests/`:
  Numpy-style docstrings on every function/class (including private and
  nested helpers), full type annotations with `from __future__ import
  annotations`, and comment density raised above the floor in every
  module. No public API or behavior changes.
- Route library logging through the os-helper logging surface
  (`osh.info/warning/error`) and adopt os-helper path/file utilities
  more widely; pin `os-helper>=1.5.0`.
- Refresh the project logo asset.


## [1.3.3] - 2026-07-08

### Documentation

- Cross-platform Install prerequisites (macOS / Ubuntu / Windows).

## [1.3.2] - 2026-07-07

### Changed

- Bump audio-helper pin to v1.5.4 (ffmpeg-based load_audio; any format incl. m4a).

## [1.3.1] - 2026-07-07

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
