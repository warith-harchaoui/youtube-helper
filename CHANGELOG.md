# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
