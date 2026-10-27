# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Documentation

- **The six reader-facing documents now sit on the suite's shared spine**
  (CODING.md rules 16-18). `## Usage` became `## Quick start` /
  `## Prise en main rapide` in README/LISEZMOI, so Installation is followed by
  the quick start and the file still ends on Author → Acknowledgements →
  License; `## Documentation` stays early, where sixteen of the seventeen
  members put it. LANDSCAPE/PAYSAGE gained the
  missing `## Sources and as-of date` / `## Sources et date de relevé`, where
  every competitor version and date is read from that project's own PyPI
  metadata on a named day rather than asserted. EXAMPLES/EXEMPLES gained
  `## Command line` / `## Ligne de commande`, their examples are now
  `## 1.`-numbered scenarios, and `## Caveats` became `## Troubleshooting` /
  `## Dépannage`.

- **Three stale or wrong claims removed from the documents.** The README
  advertised `v2.4.1` at version 2.7.0. The "Download resilience" ladder listed
  four tiers and omitted the player-client rung added in 2.4.0, so it described
  a chain the code stopped using, and it scoped itself to
  `youtube_helper.main` when `streaming` and `branding` have routed through
  `_run_ytdlp` since 2.3.0/2.4.1. The examples offered
  `is_short(video_engagement(url))`, which cannot work: `is_short` reads raw
  yt-dlp keys, and the normalised dict spells the duration `duration_seconds`,
  so the ≤ 60 s test silently never fires. The documents now point at
  `video_engagement(url)["kind"]` instead.

- **The quick start ran into a dependency the package does not declare.** It
  ended on `audio_helper.load_audio`, which decodes to a torch tensor and so
  raises `ImportError` asking for `audio-helper[demucs]` on a plain install.
  Replaced with `get_audio_duration`, and the two output lines it prints are
  measured on this repo's own `yt_tests/` fixtures rather than recalled.

- **`socket_timeout` is documented at last.** The 30 s bound and
  `YOUTUBE_HELPER_SOCKET_TIMEOUT` have existed since 2.4.1 without a word in
  the README, along with the fragment-loss policy and
  `YOUTUBE_HELPER_PLAYER_CLIENTS`. All three are now described where a reader
  debugging a hang will look.

## [2.7.0] - 2026-10-25

### Changed

- **One command line, built with click.** `youtube_helper/cli_click.py` became
  `youtube_helper/cli.py`; `youtube_helper/cli_argparse.py` (908 lines) is
  deleted, and with it the `youtube-helper-click` console script. A flag naming
  the parsing library describes the implementation, not the interface, so there
  is nothing left to choose between. `youtube-helper-mcp` is untouched: it
  starts another surface, it is not a second command line.

  Parity was measured before deleting anything, not assumed: both parsers were
  built in the same interpreter and compared programmatically — subcommand sets
  (15 on each side, identical), the `--…` option set per subcommand, and every
  option's default and required-ness. The only differences were cosmetic: the
  dest name behind `--max` (`max` vs `max_count`), `list`-vs-`tuple` defaults,
  and click's habit of exposing both halves of a boolean pair
  (`--include-shorts` alongside `--no-shorts`) where argparse declared only
  the one that flips the default. Nothing was lost in the move.

- **`click` moved out of the `[cli]` extra into the core dependencies**, and
  the extra is gone. The CLI is no longer optional, so its dependency cannot be
  either. `[dev]` no longer lists `click` for the same reason, and
  `requirements.txt` lists it under the core runtime.

- The `os-helper` cap widened from `<3` to `<4`: os-helper 3.0.0 drops its own
  CLI, which is not a break for anything this package calls.

### Fixed

- **The CLI's own help described an architecture that no longer existed.**
  `youtube-helper --help` opened with "click twin of the argparse CLI. Same
  subcommands." — meaningless to a user and, after this release, false. It now
  says what the tool does. The module docstring and the dead
  `try: import click / except ImportError` guard pointing at the `[cli]` extra
  went the same way.

- **`-V` did not exist.** Only the long `--version` was wired, so the habitual
  short form failed as an unknown option. Added as the capital `-V` because
  `-v` is `--verbose` on most subcommands. `-h` was already present.

- **The agent skill documented a command line that was never real.**
  `skills/youtube-helper/references/cli-reference.md` and `SKILL.md` showed the
  URL as a positional argument (`youtube-helper metadata URL`) and invented
  flags that no subcommand has ever accepted — `--json`, `-o`, `--height`,
  `--format`, `--lang`, `--auto`, `--limit`, `--urls-file`. Every documented
  invocation would have failed on the first argument. Both files were rewritten
  against the real parser: `--url` everywhere, plus `--output`, `--max-height`,
  `--sample-rate`, `--output-dir`, `--langs`, `--manual`, `--max`,
  `--max-videos`, `--urls`. The reference also claimed `valid` "exits 0 either
  way" where it exits 1 on `false`, and that the click CLI covered only six of
  the fifteen commands. The library example passed `output_folder=` to
  `download_audio`, whose parameter is `output_path=`.

- `tests/test_cli.py` ran every scenario twice, once per parser. Collapsed onto
  the one CLI, keeping the stronger half of each pair: the argparse test
  asserted the clean error line carries the *cause* (`Invalid URL`) where the
  click one only looked for `Error:`. The `pytest.importorskip("click")` guard
  is gone — click is a core dependency — and `-h` and `-V` are now covered.

### Migration

- `youtube-helper-click <cmd>` → `youtube-helper <cmd>`. Identical subcommands
  and flags; nothing to relearn.
- `pip install "youtube-helper[cli]"` now fails on an unknown extra. Drop the
  extra: `pip install youtube-helper` ships the CLI.
- `youtube_helper.cli_argparse` and `youtube_helper.cli_click` no longer
  import. The module is `youtube_helper.cli`, exposing `cli` (the click group)
  and `main`.

## [2.6.0] - 2026-10-21

### Changed

- **The GUI's strings moved from `locales/i18n.yaml` to a `gettext`
  catalogue**, the suite-wide mechanism as of os-helper 2.6.0. The English is
  now the source, written in the markup itself as `{{_("…")}}`; the French
  lives in `youtube_helper/locales/fr/LC_MESSAGES/youtube_helper.po` and is
  read through `os_helper.Catalog`. A translator now works in the format every
  translation tool already speaks, on real sentences rather than on key names.

  A string the French catalogue has not caught up with renders as **readable
  English** instead of as a key. The cost is the mirror image — rewording the
  English orphans its French entry, and gettext would quietly serve the
  English — so `tests/test_i18n.py` hands every source string to
  `Catalog.problems`, which names both halves of that fault.

  The URL placeholder is no longer a catalogue entry: it is the same example
  URL in every language, so it is written in the markup directly. The language
  toggle is likewise computed rather than translated — its three parts all mean
  "the other language", which is data, not copy.

### Fixed

- **The compiled catalogue would never have shipped.** The stock Python
  `.gitignore` this repository inherited carries a blanket `*.mo`, where a
  `.mo` is a build artifact. Here it is the file the GUI reads at run time:
  left ignored it would have been absent from the repository, therefore from
  the sdist, therefore from the wheel, and **every string would have rendered
  as English on an installed copy** while looking perfect locally. Negated for
  this package's catalogues and held by a "tracked by git" test.

- `tests/test_api.py` asked the GUI for its title through the old loader. It
  now reads the rendered page's `<title>`, which says "the page shows its own
  name" without naming a language at all.

## [2.5.0] — 2026-10-20

### Added

- **The GUI speaks French and English.** Every string it shows now comes from
  `youtube_helper/locales/i18n.yaml` through `os_helper.Locales`, the loader
  shared across the suite (CODING.md 21.3), instead of being written into the
  markup. `GET /gui?lang=fr|en` picks the language; anything the file does not
  carry — including a mistyped code and the empty default — falls back to the
  declared default locale, so a bad `?lang=` returns a page rather than a 500.
  A flag in the header toggles between the two.

  The template is tokenised (`{{TOKEN}}` in HTML, a `T` object for the
  script), so one piece of markup serves both languages and a translator
  never opens a Python file. The script's strings are injected as JSON rather
  than substituted as text: it is the encoding an apostrophe cannot break out
  of, and French copy is full of them.

  `GUI_HTML` still resolves, via a module-level `__getattr__` that renders on
  access — importers that predate this keep working, and the locale file is
  not read by packages that never serve the GUI.

### Fixed

- **Two tests asserted the default language rather than the page's identity.**
  They looked for the literal `"download bench"`, which is no longer what a
  French default renders. They now ask the locale file what the page is
  called, so the copy can change without touching them.

### Notes

- The locale file lives **inside** the package, with a `package-data` pattern
  that reaches it, and two tests hold that. The sibling package
  best-engine-ai-helper shipped the opposite arrangement — data beside the
  package, patterns that silently matched nothing — and its published wheels
  carried no data at all until 1.6.1.

## [2.4.2] — 2026-10-20

### Fixed

- **`branding`'s module docstring lost its feature list on the documentation
  site.** The five bullets naming what the module does — channel snapshot,
  video list, engagement signals, subtitles, comments sample — follow the line
  that announces them with no blank line between, so docutils reads the indent
  as a stray block rather than a list and Sphinx drops it. The summary of the
  module was absent from the rendered page while sitting in plain sight in the
  source.

## [2.4.1] — 2026-10-19

### Fixed

- **2.4.0's `socket_timeout` did not reach three of this package's call
  sites.** The bound was added to the two option *builders*
  (`default_ytdlp_options`, `branding._minimal_options`), but `streaming.py`
  hand-builds its option dicts literally and calls `_run_ytdlp` with them. So
  `resolve_direct_url`, `list_video_streams` and `pick_video_stream` — and
  transitively `extract_frames_stream` — stayed exactly as unbounded as before
  the release.

  The bound now lives in `_run_ytdlp`, the chokepoint every yt-dlp call in the
  package funnels through, applied with `setdefault` so a caller who chose a
  value deliberately keeps it. That is where it should have gone in 2.4.0: the
  Rust twin put it in `ytdlp::run` for exactly this reason.

  A structural note worth keeping, since this is the second time it has bitten:
  `streaming.py` does not use the shared option builders, so anything added to
  those builders does not apply to it. The 2.3.x series had the same blind spot
  with the retry ladder.

## [2.4.0] — 2026-10-18

### Added

- **Retry as a different YouTube client before touching anyone's cookies.** When YouTube
  answers "Sign in to confirm you're not a bot", the fix that costs nothing and reads
  nobody's private data is to ask as another client: YouTube does not apply the same checks
  to its web, mobile, TV and embedded players. The retry ladder now tries `web_embedded`,
  `tv`, `android_vr` then `mweb` *before* the cookies-from-browser rung and long before Tor,
  because those two are invasive and slow respectively. Needs no configuration; override the
  list with `YOUTUBE_HELPER_PLAYER_CLIENTS`, or pin one explicitly with
  `default_ytdlp_options(player_clients=[...])`, in which case the ladder leaves your choice
  alone.

- **`max_height` on `download_video`, with a non-HLS preference** (`--max-height` on both
  CLIs, `max_height` in the `/video` body, `YOUTUBE_HELPER_MAX_HEIGHT` for a whole
  deployment). Two problems, one knob. Size: left to itself yt-dlp picks the best stream
  going, which on one episode meant a 4.3 GB file heading for a FAT32 volume that refuses
  anything over 4 GiB, failing mid-write. Speed: that stream was fragmented HLS, which
  YouTube throttles hard — measured at 75-300 KiB/s across 1507 fragments, against ~2 MiB/s
  for the same video's direct https format, which was also eight times smaller. The capped
  selector (`height_capped_format`, now exported) puts `protocol^=http` formats first and
  only falls back to HLS, then to best-available, so a video with no small format still
  downloads instead of failing "Requested format is not available".

  Opt-in: with no cap set, callers keep the previous best-available behaviour exactly.

- **Video downloads merge straight into mp4, instead of being re-encoded into one.**
  A separate video+audio pair used to merge into whatever container yt-dlp preferred, often
  webm or mkv, and `download_video` then handed the result to `video_helper.video_converter`
  to reach the `.mp4` the caller asked for. That re-encodes: measured at 290 % CPU on
  libx264, for tens of minutes per episode, after VideoToolbox declined the job. mp4 accepts
  AV1, H.264, VP9 and opus, so `merge_output_format="mp4"` makes ffmpeg remux in seconds.
  When codecs genuinely cannot live in mp4, yt-dlp keeps its container and the existing
  conversion path still catches it, so this only ever removes work.

### Changed

- **A fragmented download that loses fragments now fails, instead of quietly returning a
  shorter file.** `skip_unavailable_fragments` defaults to `True` in yt-dlp: after
  `fragment_retries` attempts it drops the fragment, carries on, and finalises the container
  normally. What lands on disk is a valid, playable mp4 whose moov atom honestly reports the
  short duration, so every downstream check passes, `is_valid_video_file` included, and
  nothing raises.

  That is how seven episodes of a corpus were transcribed and reported on partial video, one
  of them covering 12 % of its runtime, with no warning anywhere. They were served as HLS in
  724-1507 fragments over a path YouTube throttles to a few hundred KiB/s, while several
  downloads and builds ran at once; fragments timed out, got skipped, and the loss became
  invisible. Re-downloading them later worked, so the source had never been the problem.

  Failing loudly is the right default for a download helper: the caller can retry, and this
  library's own ladder does, including with clients that serve no HLS at all. `fragment_retries`
  also goes from 10 to 25, since the failures were transient throttling rather than missing
  data. `YOUTUBE_HELPER_ALLOW_LOSSY_FRAGMENTS=1` restores the old behaviour, and
  `YOUTUBE_HELPER_FRAGMENT_RETRIES` tunes the patience.

- The yt-dlp fallback tests now assert the ladder by invariant (caller's options first,
  Tor last, cookies only when configured) instead of by a fixed length. A hard-coded count
  made every new rung look like a regression.

### Fixed

- **A stalled yt-dlp read could hang the caller forever.** yt-dlp inherits Python's default
  socket timeout, which is no timeout at all, so a connection the remote had half-closed was
  simply waited on. Seen twice while auditing the suite: a caption fetch sat at 0 % CPU for
  nine minutes with its sockets in `CLOSE_WAIT`, and only a kill ended it.

  The second-order damage was larger than the wait. Every recovery path in this module --
  the browser User-Agent fallback, the Tor fallback, the player-client ladder added above --
  only runs after an attempt *returns*. An attempt that never returns disables all of them,
  which is why the failure presented as a hang instead of a retry. Both the download options
  and the metadata options now set `socket_timeout` (30 s, override with
  `YOUTUBE_HELPER_SOCKET_TIMEOUT`), so a dead connection fails fast enough for that
  machinery to do its job.

- **`channel_videos` returned an empty list for any bare channel URL.** Under
  `extract_flat`, a channel root (`/@handle`, `/channel/UC…`, `/c/…`,
  `/user/…`) no longer answers with videos: it answers with the channel's own
  tabs, as playlist entries that all carry the channel id and no `url` at all.
  The per-video pass skipped every one of them for lack of a URL, so the
  function returned `[]` — and returned it *silently*, without raising, which
  is why the browser-UA / cookies-from-browser / Tor retry chain never fired:
  it only reacts to exceptions. A channel root is now expanded to the tabs
  that actually list videos (`/videos`, plus `/shorts` and `/streams` when
  `include_shorts` / `include_lives` ask for them), each walked tolerantly
  since not every channel has every tab. Explicit tabs, playlists and the
  Vimeo / DailyMotion creator pages this module also serves are untouched.
- **`resolve_direct_url(prefer="video")` failed outright on most YouTube
  videos** with "Requested format is not available". The selector was `best`,
  which in yt-dlp means "best *single file* already carrying both tracks" —
  the progressive streams YouTube has retired on all but a few videos. It is
  now `best/bestvideo*`: the progressive stream when one exists, the best
  video-only stream otherwise, so a single direct URL always comes back.
  Merging (`bestvideo*+bestaudio`) is deliberately not used — a merged
  selection has no single URL to hand to ffmpeg, which is this function's
  whole contract.

### Added

- **`has_audio` on `DirectMediaURL`.** With video-only streams now the normal
  answer for `prefer="video"`, callers need to know whether the URL they got
  carries sound, rather than finding out inside ffmpeg. `prefer="audio"`
  always reports `True`; when `prefer="video"` reports `False`, resolve a
  second URL with `prefer="audio"` and give ffmpeg one input from each.

### Changed

- The `@Blender` channel used as a test fixture no longer has a videos tab;
  the suite now points at `@BlenderOfficial`.

## [2.3.0] - 2026-08-24

### Added

- **Cookies-from-browser fallback tier** in the yt-dlp retry chain: YouTube's
  "Sign in to confirm you're not a bot" challenge survived the existing
  default → browser-UA → Tor chain untouched (Tor exit nodes are themselves
  commonly flagged). Verified live: `--cookies-from-browser chrome` clears
  it immediately where Tor did not. The new tier sits between browser-UA and
  Tor, opt-in via `YOUTUBE_HELPER_COOKIES_FROM_BROWSER` (empty by default —
  reading another app's cookie store should never happen silently).

### Fixed

- **`streaming.py`'s `resolve_direct_url`/`list_video_streams`/
  `pick_video_stream` (and transitively `extract_frames_stream`) completely
  bypassed the browser-UA / cookies-from-browser / Tor retry chain**,
  calling `YoutubeDL(...).extract_info(...)` directly with zero fallback —
  unlike every function in `main.py` and `branding.py`'s `channel_videos`/
  `video_engagement`, which already routed through `main._run_ytdlp`. The
  README's "Download resilience" section documents this resilience as
  applying to "every yt-dlp call in `youtube_helper.main`", which was true,
  but silently left `streaming.py`'s three functions with none of it. Found
  via a live bot-block in the field (YouTube's "Sign in to confirm you're
  not a bot") that `main.py`'s functions recovered from automatically but
  `streaming.py`'s did not. Both extraction call sites now go through
  `_run_ytdlp`, same as the rest of the package.
- **`video_url_meta_data` crashed on videos with no description.** Some
  extractors (live streams, certain Vimeo / DailyMotion pages, …) omit the
  `description` field entirely, so yt-dlp's info dict carries it as `None`
  rather than `""`. The function called `description.split("\n")`
  unconditionally, raising `AttributeError` on any such video — and since
  `download_thumbnail` / `download_audio` / `download_video` all call this
  function to build their default output filename when `output_path` is
  omitted, a missing description broke every one of them too. Coalesces to
  `""` before splitting; added a regression test
  (`test_video_url_meta_data_handles_missing_description`).
- **README.md/LISEZMOI.md's "Download resilience" section never documented
  the new cookies-from-browser tier**, and still numbered Tor as fallback
  #3 (now #4) — the exact same repo, same doc drift class as the missing-
  description fix above, just in the "what does this env var do" surface
  instead of code. Added the missing tier description (mirrors the code
  comment: which browsers are supported, the Safari Full Disk Access
  caveat) and fixed Tor's numbering in both the resilience section and the
  Installation section's cross-reference.

### Documentation

- **README.md/LISEZMOI.md**: added an honest "battle-tested" /
  "éprouvé en production" paragraph — on PyPI, CI-gated, semantic-versioned,
  depends on `os-helper` / `audio-helper` / `video-helper`, and
  is itself a dependency of `podcast-helper` — matching the framing already
  used across the suite (see `audio-helper`'s README).

## [2.2.1] - 2026-08-17

### Fixed

- **`download_audio`/`download_video` could pick up a stale partial file
  after a retry.** The normal -> browser-UA -> Tor fallback chain reuses the
  same temp directory across attempts; a failed attempt can leave a
  `.part` file behind (a network drop mid-download, not just a block), and
  without cleanup a leftover from attempt N could still be sitting next to
  attempt N+1's real output when the post-download glob ran, making the
  picked file order-dependent instead of always the actual result.
  `_run_ytdlp` now takes an `on_attempt_start` hook, called before every
  attempt including the first; both download functions use it to purge any
  `<base>.*` leftovers first. Reproduced against the pre-fix code (the
  stale `.part` file was picked over the real download) before fixing.
- **The download-resilience fallback chain only covered `youtube_helper.main`
  — `branding.py`'s 6 yt-dlp call sites (`channel_info`, `channel_videos`,
  `video_engagement`, `video_subtitles`, `video_comments`,
  `engagement_batch`) never retried at all**, despite being exactly as
  exposed to the same blocking/rate-limiting/bot-check failures the v2.2.0
  fallback chain was built to solve. All six now route through the same
  `_run_ytdlp`. `channel_videos`' per-video loop and `engagement_batch`'s
  per-URL loop no longer share one `YoutubeDL` instance across the whole
  loop — each item gets its own independent fallback chain, since a block
  can hit mid-walk, not only on the very first request.

### Documentation

- **README.md/LISEZMOI.md**: glossed recurring jargon at first mention
  (`yt-dlp`, `ffmpeg`, OAuth/quota, Tor's SOCKS-proxy mechanism, MCP) so a
  reader unfamiliar with these terms can follow why no API keys are
  needed and how the Tor fallback actually defeats an IP block, without
  losing any technical precision for readers who already know them.

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
