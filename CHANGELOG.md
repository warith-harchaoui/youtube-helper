# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-08-15

### Added

- **Download resilience**: every yt-dlp call in `youtube_helper.main`
  (metadata, thumbnail, audio, video) now retries automatically when the
  normal request gets blocked, in order: (1) the normal request, (2) a
  fully-populated browser User-Agent (overridable via
  `YOUTUBE_HELPER_USER_AGENT`), (3) a local Tor SOCKS proxy (overridable via
  `YOUTUBE_HELPER_TOR_PROXY`, requires a Tor daemon running locally). Added
  `PySocks` as a runtime dependency for SOCKS proxy support.

## [2.1.2] - 2026-08-15

### Fixed

- **CLI**: a library exception (e.g. `AssertionError` on an invalid URL)
  used to propagate as a raw Python traceback on both CLI twins instead of
  a clean `Error: ...` line + exit 1. `youtube-helper-click`'s
  console-script entry point now points at a new `cli_click.main()`
  wrapper (was the bare `cli` group).

## [2.1.1] - 2026-08-13

### Fixed

- `download_audio`'s already-exists log message said "Thumbnail already
  exists" (copy-pasted from `download_thumbnail`) instead of "Audio already
  exists" — misleading log output only, no functional impact.

### Changed

- Added a conda `environment.yaml`; the Dockerfile now installs
  `requirements.txt` as its own cached layer.
- `requirements-dev.txt` is now derived from `pyproject.toml`'s `[dev]`
  extra instead of maintained by hand.
- Added `EXEMPLES.md` (French sibling of `EXAMPLES.md`); documentation
  freshness pass for WRITING.md/ECRITURE.md compliance; regenerated
  LANDSCAPE/PAYSAGE positioning figures; moved Features to canonical
  position in the README.

## [2.1.0] - 2026-08-08

### Added

- **MCP surface** (`youtube_helper.mcp`, `[mcp]` extra, entry point
  `youtube-helper-mcp`): exposes the existing FastAPI app as MCP tools via
  `fastapi-mcp`, mirroring the pattern shipped in `standpoint` / `vocal-helper`
  / `md2star` / `os-helper`. Closes the CLI/API/MCP surface gap flagged in
  `ai-helpers/.private/do.md` §7.

## [2.0.0] - 2026-08-02

Major release: youtube-helper moves onto the 2.x AI Helpers foundation. The
public API is unchanged; the bump is major because three pinned suite
dependencies crossed a major boundary at once.

### Changed

- **Adopts the 2.x suite majors:** `os-helper>=2.0.0,<3` (was `>=1.5.0`),
  `audio-helper>=2.0.0,<3` (was `>=1.5.5`), `video-helper>=2.0.0,<3` (was
  `>=1.6.3`). This brings the hardened logging / file-management / smart-download
  foundation and the audio/video 2.x contracts under youtube-helper.
- **CI is now a real gate.** The lint job dropped its `continue-on-error: true`
  and `ruff check . || true` — both silently swallowed lint failures — and now
  runs a blocking `ruff check .` plus `ruff format --check .`. The test matrix
  is trimmed to a single Python (the full sweep runs locally before push).

### Fixed

- README / LISEZMOI install commands no longer self-pin to a git tag (`@v1.5.0`);
  they use `pip install youtube-helper`, which always resolves to the latest
  published release.

### Added

- `tests/test_readme_install_pin.py` guards against the stale git self-pin ever
  returning to any Markdown file.

## [1.5.1] - 2026-08-01

### Removed

- **Agent skill dropped from the public repo.** Without an MCP surface,
  the Claude/OpenCode skill (`skills/`) no longer earns its keep as public
  distribution — moved to the gitignored `.private/skills/` (kept locally
  as reference, never published). `TRIGGERS.md` stays public; its
  skill-specific framing and dead `skills/` links are removed.

## [1.5.0] - 2026-08-01

### Removed

- **MCP surface dropped.** `fastapi-mcp`'s latest release (0.4.0) is
  incompatible with the latest `mcp` SDK (`Server.__init__()` signature
  mismatch), breaking CI with no available version pairing to pin around.
  Removed `youtube_helper/mcp.py`, the `youtube-helper-mcp` entry point, the
  `mcp` extra, and every doc/skill mention. The library, both CLIs, the
  FastAPI HTTP surface, and the browser GUI are unaffected — youtube-helper
  now ships **four** surfaces instead of five.

## [1.4.0] - 2026-07-20

### Added

- **Browser GUI** — a minimal single-page "download bench" served by the
  FastAPI app at `GET /gui` (and `GET /` redirects to it). Paste a YouTube (or
  any yt-dlp-supported) URL, choose audio (with a target sample rate) or video,
  hit Download, and the result plays inline with a download link. Self-contained
  HTML + Tailwind (CDN) + vanilla JS, no build step; it POSTs to the existing
  `/audio` / `/video` endpoints so it adds zero server-side logic. Lives in
  `youtube_helper/gui.py`.
- **Agent skill** — `skills/youtube-helper/` packages youtube-helper as a Claude
  Skill and an OpenCode skill (`SKILL.md` with a trigger-rich third-person
  description + `references/{cli-reference,surfaces,triggers}.md`), plus
  `skills/README.md` with install instructions (symlink into `~/.claude/skills`
  and `~/.opencode/skills`).
- **`TRIGGERS.md`** — an exhaustive, user-facing catalogue of the phrasings,
  commands, functions, and sites that should invoke youtube-helper, referenced
  from README and LISEZMOI.
- **The Promise / La promesse** — a local-first privacy statement (EN + FR) and
  a `Local-first` badge at the top of README / LISEZMOI.

### Changed

- The FastAPI app now reports its version from installed package metadata
  (`importlib.metadata`) instead of a hard-coded string that had drifted to
  `1.3.3`.
- `.gitignore` now covers `.private/` and stray `*_ytdlp_cookie.txt` jars.
- README / LISEZMOI Features and multi-surface sections document the GUI and the
  agent skill.

### Preserved

- All hard-won yt-dlp fixes are untouched: cookie jar kept out of the working
  directory (temp-scoped), no `force_generic_extractor`, no `player_skip=js`,
  and `YOUTUBE_HELPER_COOKIES` support. Live YouTube download tests stay
  local-only (skipped in CI by design).

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
