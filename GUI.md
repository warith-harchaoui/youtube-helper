# GUI — YouTube Helper

> A design plan, not a CLI mirror. The CLI already handles "give me the
> audio / video / thumbnail / metadata of one URL". A GUI must go further
> — otherwise why build one? This document lays out an ambitious,
> opinionated visual product for the yt-dlp-backed
> download-and-branding workflow.

## North star

> **A single searchable board where every URL you have ever downloaded,
> every channel you have ever inspected, and every engagement metric you
> have ever pulled is one click away — with side-by-side comparison of
> videos, channels, and streams.**

`yt-dlp` is powerful but each shell invocation is a black box. The GUI's
job is to make the **library visible, browseable, and comparable** —
not to reproduce yt-dlp flags with checkboxes.

## Three surfaces, one product

### 1. Video Library *(primary surface)*

- A left rail listing every URL the user has fed into `youtube-helper`,
  grouped by channel then by upload date.
- Center pane: the selected video's **card** — thumbnail, title,
  duration, view / like / comment counts, direct-URL resolver output,
  cached transcripts, downloaded artifacts (video / audio / thumbnail
  paths, byte sizes).
- Right pane: a **stream catalog table** for that video (from
  `list_video_streams`) — one row per format (h264 1080p60, vp9 720p,
  av1 480p, …). Click a row to preview a 5-second sample decoded from
  the direct URL. This is the "we can only do this in a GUI" moment.
- Search bar (top): fuzzy over title / channel / description / tags,
  hits render as candidates in the left rail.

### 2. Channel Comparator

Two channels side by side (drag one URL onto another). Renders:

- **Overlaid growth-rate charts** built from `channel_videos` upload
  dates and view counts.
- **Distribution histograms** of view / like / comment counts, marked
  medians.
- **Shorts vs long-form split** (`is_short`) per channel with a
  quarter-by-quarter breakdown — the ratio that tells you whether a
  creator is pivoting.
- **Retention proxy**: like-to-view ratio, comment-to-view ratio, both
  medians and standard deviations. yt-dlp does not give real retention
  curves, but these engagement ratios are the best public proxies.

### 3. Batch Downloader

A single big rectangle. Drop any number of URLs (or a channel URL, or a
playlist URL) → they enter a **queue** with per-item progress bars.
Options apply to the whole batch (audio-only / video / thumbnails, target
sample rate, direct-URL resolve-only, …). Failed items surface with
their yt-dlp error message and a one-click "retry with cookies" button
that reads cookies from the selected browser profile.

## Design principles

- **Nothing invisible.** Every video shows its resolved direct URLs,
  every channel shows its cached metrics. No mystery states.
- **Cache is a first-class citizen.** All yt-dlp responses are cached
  to a project folder (opt-out). The library view is offline-first;
  network calls happen only when you press "refresh".
- **Paths, not blobs.** The recipe engine writes downloaded artifacts
  to a project folder. The CLI outputs and the GUI outputs are
  byte-identical — no "GUI produces different files".
- **Explain the metadata.** Tooltips over each metric explain what
  yt-dlp field it came from and how normalisation was applied
  (upload_date reformat, kind heuristic, …). No mystery numbers.
- **Keyboard first, mouse second.** `/` focuses search, `j`/`k` move
  in the left rail, `space` previews the selected stream, `d`
  triggers a download of the selected format, `c` opens the channel
  comparator with the current video's channel pre-selected.
- **Colorblind-safe by construction.** All state uses shape + color +
  text, never color alone (see companion `front-colors` audit skill).

## What we deliberately don't do

- **No video editor.** DAWs / NLEs already exist. We are not competing
  with them. Trims happen via external tooling — we just download.
- **No annotation UI.** Comments and subtitles are viewable but not
  editable. The GUI is a *dashboard*, not a workspace.
- **No cloud lock-in.** Everything runs on the same local FastAPI
  server the container already ships. GUI is a thin JS client.

## Stack

- Front end: TypeScript + Svelte 5 + WaveSurfer.js (audio preview) +
  Vega-Lite (comparator charts). No React — matches the `front-ui`
  companion skill's stack.
- Back end: the FastAPI app already exists (`youtube_helper.api`) and
  covers 100 % of the operations. GUI is a client only.
- Cache format: SQLite (metadata index) + a `library/` folder for the
  downloaded artifacts, both human-diffable.

## Milestones

| Milestone | What ships | Why first |
| --- | --- | --- |
| M0 | Video Library with the metadata card + downloaded-artifacts list. | Prove the library metaphor before scaling verbs. |
| M1 | Stream catalog table + 5-second preview per format. | The "we can only do this in a GUI" moment for individual videos. |
| M2 | Batch Downloader queue. | Where the GUI passes the CLI in productivity. |
| M3 | Channel Comparator with growth-rate + histogram views. | The insight layer for personal-branding workflows. |
| M4 | Subtitle transcript viewer with click-to-seek + comment sentiment overlay. | Contextualises engagement metrics with actual content. |

## Non-goals (recorded so we do not drift)

- Not a full YouTube dashboard.
- Not a hosted SaaS.
- Not a substitute for the CLI in CI (batch operations emit
  CLI-equivalent scripts that CI can replay headless).

## Success metric

> A creator preparing a competitor audit gets a side-by-side of the
> five channels they care about — growth curves, engagement ratios,
> shorts ratio, top-comments samples — in under 10 minutes, in one
> window, and finishes with a committable `report.md` per channel.

If we ship that, we win.
