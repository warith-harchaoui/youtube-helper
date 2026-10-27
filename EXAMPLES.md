# YouTube Helper: Examples

[🇫🇷 EXEMPLES.md](https://github.com/warith-harchaoui/youtube-helper/blob/main/EXEMPLES.md) · 🇬🇧 English

Practical recipes for the three layers of `youtube-helper`: the download
helpers, the stream catalog and resolvers, and the no-API engagement metadata.

Every snippet here reaches the network, because that is what the package is
for. None of the outputs below were invented: where a value is shown it was
measured locally and labelled as such, and where it could not be measured the
comment names the *shape* of the answer instead of guessing at a number. View
counts and format lists change by the hour anyway, so a pasted figure would
have been stale before you read it.

---

## Table of Contents

1. [Setup](#setup)
2. [Downloads to disk](#1-downloads-to-disk)
3. [Stream catalog and picker](#2-stream-catalog-and-picker)
4. [Direct-URL resolver](#3-direct-url-resolver)
5. [Composing with video-helper](#4-composing-with-video-helper)
6. [Engagement metadata without API keys](#5-engagement-metadata-without-api-keys)
7. [Subtitles, comments, and channels](#6-subtitles-comments-and-channels)
8. [Command line](#command-line)
9. [Troubleshooting](#troubleshooting)

---

## Setup

```bash
pip install youtube-helper
```

That brings in `os-helper`, `audio-helper` and `video-helper` automatically.
You still need `yt-dlp` and `ffmpeg` on PATH — `brew install yt-dlp ffmpeg` on
macOS, see the [README](https://github.com/warith-harchaoui/youtube-helper/blob/main/README.md#installation)
for the other platforms.

Every Python snippet below assumes these imports:

```python
import youtube_helper as yth
import os_helper as osh

osh.verbosity(2)  # so the osh.info(...) calls inside the library reach stdout
```

A single URL is reused throughout, [Big Buck Bunny](https://www.youtube.com/watch?v=YE7VzlLtp-4)
on the Blender channel, because it is Creative Commons licensed and therefore
safe to actually download while reading:

```python
URL = "https://www.youtube.com/watch?v=YE7VzlLtp-4"
```

## 1. Downloads to disk

The original `youtube-helper` surface: pull a file to local storage. Each
function returns the path it wrote, so the result is directly usable.

```python
video = yth.download_video(URL, "bunny.mp4")
audio = yth.download_audio(URL, "bunny.mp3")
thumb = yth.download_thumbnail(URL, "bunny.jpg")

# Omit the output path and a name is derived from the video's own title.
same_video_auto_named = yth.download_video(URL)

# Cap the height when the destination cannot take an arbitrarily large file.
# A cap also prefers direct https formats over the HLS ones YouTube throttles,
# so it is usually faster as well as smaller.
smaller = yth.download_video(URL, "bunny-720.mp4", max_height=720)

# Cheap metadata probe — no download. Returns yt-dlp's own info dict.
meta = yth.video_url_meta_data(URL)
print(meta["title"], meta["duration"], meta["channel"])  # str, int seconds, str

# Is this URL something yt-dlp can handle at all? Never raises.
yth.is_valid_video_url(URL)  # True / False
```

Omitting `output_path` writes `<ascii-title>.mp4` (or `.mp3`, or the
thumbnail's extension) next to your working directory, as an absolute path. All
three are idempotent: if that file already exists and is a valid media file,
the call logs and returns it instead of fetching again.

`download_audio` re-encodes through `audio-helper` only when yt-dlp's output
does not already carry the extension you asked for — and `target_sample_rate`
is applied on that conversion step. So a `.wav` or `.m4a` target gets the rate
you named:

```python
yth.download_audio(URL, "bunny-16k.wav", target_sample_rate=16000)
```

whereas asking for `.mp3`, which is what yt-dlp hands back anyway, copies the
file through untouched at whatever rate the source had.

## 2. Stream catalog and picker

Where `download_*` writes a file, the catalog and picker hand you a **direct
media URL** plus the headers it needs, so a downstream decoder (PyAV, ffmpeg,
`video_helper.extract_frames`) can read it without going back through yt-dlp.

```python
# Enumerate every video format yt-dlp finds, worst to best.
streams = yth.list_video_streams(URL)
for s in streams[:5]:
    print(
        f"{s['format_id']:6} {s['width']}x{s['height']} {s['fps']}fps "
        f"{s['vcodec']:14} {s['ext']:6} ~{s['vbr_kbps']:.0f} kbps"
    )
```

Each entry is a `VideoStreamInfo` with these keys: `format_id`, `url`,
`headers`, `ext`, `container`, `vcodec`, `acodec`, `width`, `height`, `fps`,
`vbr_kbps`, `filesize_bytes`, `is_live`, `protocol`, `language`, `note`.
Audio-only formats are filtered out — this is the *video* catalog. YouTube
publishes dozens of rows for a popular video and rotates them, so the exact
`format_id` values are not worth memorising.

```python
# Pick the single best stream matching your constraints.
pick = yth.pick_video_stream(
    URL,
    prefer_codec="h264",  # substring match, and "h264" ↔ "avc1" are aliased
    prefer_format="mp4",  # exact match on ext
    max_fps=30,  # drop anything faster
)
pick["url"]  # direct media URL, ready for ffmpeg
pick["headers"]  # the headers ffmpeg must send with it
```

Every non-`None` constraint is a hard filter, applied to the catalog above;
the highest-ranked survivor wins. If the catalog is empty, or every entry gets
filtered out, `pick_video_stream` raises `ValueError` rather than silently
returning something you did not ask for.

**Note on audio**: a parallel audio catalog and picker intentionally lives in
**podcast-helper**, the suite's single owner for audio PCM streaming, not here.

## 3. Direct-URL resolver

When you don't need the catalog and just want **one** ffmpeg-ready URL:

```python
out = yth.resolve_direct_url(URL, prefer="video")  # or prefer="audio"
out["url"]  # str — may be a progressive mp4, an HLS .m3u8, a DASH .mpd
out["container"]  # "mp4" / "webm" / "hls" / "dash" / "audio"
out["is_live"]  # bool
out["headers"]  # dict[str, str] — pass to ffmpeg via -headers
out["has_audio"]  # bool — see below
```

Coarser than `pick_video_stream` (no codec, format, or fps filtering), but a
single call.

Mind `has_audio`. `prefer="audio"` always yields `True`, but `prefer="video"`
yields `False` whenever the site only offers video-only streams — which is now
YouTube's normal answer, since it retired progressive streams for most videos.
When you need both tracks from one page, resolve twice and let ffmpeg take one
input from each:

```python
v = yth.resolve_direct_url(URL, prefer="video")
if not v["has_audio"]:
    a = yth.resolve_direct_url(URL, prefer="audio")
    # ffmpeg -headers ... -i v["url"] -headers ... -i a["url"] -c copy out.mp4
```

## 4. Composing with video-helper

The whole point of the catalog and picker: feed the direct URL and headers to
`video_helper.extract_frames`, and decode without re-fetching the page.

### Two-step composition (low level)

```python
import video_helper as vh

pick = yth.pick_video_stream(URL, prefer_codec="h264", max_fps=30)

for frame in vh.extract_frames(
    pick["url"],
    http_headers=pick["headers"],
    start_instant=10.0,
    end_instant=20.0,
    frame_interval=1.0,
    destination="torch",
    device="mps",
    batch_size=10,
    layout="image",
):
    # frame.shape == (10, 3, H, W), RGB uint8, on MPS
    embeddings = model(frame)
```

### One-call composition: `extract_frames_stream`

`extract_frames_stream` collapses the two-step recipe into a single call: it
runs `pick_video_stream` under the hood, splices in the resolver's
`http_headers` automatically, and forwards every `extract_frames` keyword
verbatim.

```python
for frame in yth.extract_frames_stream(
    URL,
    # picker constraints
    prefer_codec="h264",
    prefer_format="mp4",
    max_fps=30,
    # extract_frames passthrough
    start_instant=10.0,
    end_instant=20.0,
    frame_interval=1.0,
    destination="torch",
    device="mps",
    batch_size=10,
    layout="image",
):
    embeddings = model(frame)
```

Same code drives a CPU numpy pipeline (the default) or a GPU torch pipeline,
just by changing `destination`, `device`, or `batch_size`. The picker is
invoked once and the resolved stream is reused for the entire iteration.

> **Heads-up**: `extract_frames_stream` needs a `video-helper` release with
> URL-aware `is_valid_video_file` and `video_dimensions(http_headers=)`;
> youtube-helper's `pyproject.toml` pins `video-helper>=2.0.0,<3` for this.

## 5. Engagement metadata without API keys

`youtube_helper.branding` extracts public engagement signals from yt-dlp's own
metadata dict: **no Google Data API, no Vimeo API, no OAuth, no quota.**

```python
# One-video snapshot, on the normalised schema.
meta = yth.video_engagement(URL)
print(meta["view_count"], meta["like_count"], meta["comment_count"])  # three ints
print(meta["kind"])  # "short" / "long" / "live"

# Channel snapshot: subscribers, total views, video count.
ch = yth.channel_info("https://www.youtube.com/@Blender")
print(ch["title"], ch["follower_count"], ch["video_count"])

# Channel video list with per-video engagement.
# Slow by construction: one yt-dlp fetch per video, so cap it.
videos = yth.channel_videos(
    "https://www.youtube.com/@Blender",
    max_videos=20,
    include_shorts=True,
    include_lives=False,
)
for v in videos:
    print(f"{v['upload_date']}  {v['view_count']:>10,}  {v['title']}")

# Batched engagement across a list of URLs: tolerant — a dead entry comes back
# as a stub carrying "_error" instead of aborting the whole batch.
for entry in yth.engagement_batch([URL, "https://www.youtube.com/watch?v=removed"]):
    if "_error" in entry:
        print(f"skip {entry['url']}: {entry['_error']}")
    else:
        print(entry["title"], entry["view_count"])
```

**Normalised schema** — the same twenty fields whether the source is YouTube,
Vimeo, DailyMotion, or a Twitch VOD:

```text
id, url, title, description, upload_date (ISO YYYY-MM-DD),
duration_seconds, view_count, like_count, comment_count,
channel, channel_id, channel_url, channel_follower_count,
tags, categories, thumbnail, availability, live_status,
extractor, kind  # "short" / "long" / "live"
```

Note the renames: the duration is `duration_seconds`, not yt-dlp's `duration`,
and the page URL is `url`, not `webpage_url`. Any count the extractor withheld
comes back as `0` rather than `None`, so arithmetic downstream never has to
guard for it.

## 6. Subtitles, comments, and channels

```python
# Auto-subtitles. Returns {lang: path}, with ABSOLUTE paths: output_dir is
# resolved before the files are written. Languages with nothing available are
# silently skipped, so the dict can be smaller than `langs` — or empty.
subs = yth.video_subtitles(URL, output_dir="captions", langs=("fr", "en"), auto_only=True)
# e.g. {"en": "/current/working/dir/captions/YE7VzlLtp-4.en.vtt"}

# Comments: YouTube increasingly requires browser cookies for comment threads.
comments = yth.video_comments(
    URL,
    max_count=50,
    cookies_from_browser="firefox",  # or "chrome" / "safari" — reads your session
)
for c in comments[:3]:
    print(f"@{c['author']} ({c['like_count']}): {c['text'][:80]}")
```

Each comment dict carries `id`, `parent`, `author`, `author_id`, `text`,
`like_count`, `timestamp`, `iso_date`, `is_favorited`. On YouTube, `parent` is
the string `"root"` for a top-level comment and the parent's id for a reply,
which is what you group on to rebuild threads.

To ask "is this a Short?", read `kind` off the normalised dict:

```python
yth.video_engagement(URL)["kind"] == "short"
```

`is_short` is also exported, but it reads **raw** yt-dlp keys (`duration`,
`webpage_url`), so hand it `video_url_meta_data(url)` and not the normalised
dict from `video_engagement` — on the latter its ≤ 60 s test cannot fire,
because the normalised dict spells that field `duration_seconds`:

```python
yth.is_short(yth.video_url_meta_data(URL))  # True / False
```

## Command line

One command line, built with `click`, installed as `youtube-helper` by
`pip install youtube-helper`. Fifteen subcommands, every argument a named flag,
and the FastAPI surface mirrors the names one-to-one:

```bash
youtube-helper metadata       --url https://www.youtube.com/watch?v=YE7VzlLtp-4
youtube-helper valid          --url https://www.youtube.com/watch?v=YE7VzlLtp-4
youtube-helper video          --url ... --output bunny.mp4 --max-height 720
youtube-helper audio          --url ... --output bunny.mp3 --sample-rate 16000
youtube-helper thumbnail      --url ... --output bunny.jpg
youtube-helper resolve        --url ... --prefer audio
youtube-helper list-streams   --url ... --no-video-only
youtube-helper pick-stream    --url ... --prefer-codec h264 --prefer-format mp4 --max-fps 30
youtube-helper channel-info   --url https://www.youtube.com/@Blender
youtube-helper channel-videos --url https://www.youtube.com/@Blender --max-videos 20 --no-shorts
youtube-helper engagement     --url ...
youtube-helper engagement-batch --urls URL1 --urls URL2
youtube-helper subtitles      --url ... --output-dir captions --langs en --langs fr
youtube-helper comments       --url ... --max 50 --cookies-from-browser firefox
youtube-helper ytdlp-version  --min-version 2024.12.23
```

Everything that reads rather than downloads prints JSON on stdout, so it pipes
straight into `jq`:

```bash
youtube-helper pick-stream --url "$URL" --prefer-codec h264 | jq -r .url
```

`valid` also encodes its answer in the exit status (`0` valid, `1` not), so it
works as a shell guard. A library error becomes a one-line `Error: ...` on
stderr plus exit 1, never a Python traceback.

Two invocations that need no network, so you can check your install right now.
`ytdlp-version` reports the yt-dlp it will actually call, and warns on stderr
when it is older than the version you name:

```console
$ python -m youtube_helper.cli ytdlp-version
2026.06.09

$ python -m youtube_helper.cli ytdlp-version --min-version 2099.01.01
youtube-helper: yt-dlp 2026.06.09 is older than 2099.01.01 — consider `pip install -U yt-dlp`.
2026.06.09
```

And the subcommand list itself:

```console
$ python -m youtube_helper.cli --help
Usage: python -m youtube_helper.cli [OPTIONS] COMMAND [ARGS]...

  YouTube Helper — download and inspect media from yt-dlp-supported sites.

  Downloads video, audio or thumbnails, resolves a page URL to a direct
  ffmpeg-ready media URL, browses the stream catalog, and pulls no-API
  engagement metadata on YouTube, Vimeo, DailyMotion, Twitch VOD, SoundCloud
  and anything else yt-dlp handles.

Options:
  -V, --version  Show the version and exit.
  -h, --help     Show this message and exit.

Commands:
  audio             Download only the audio track to disk.
  channel-info      Channel-level snapshot (subs, total views, video count).
  channel-videos    List channel videos with normalised engagement metadata.
  comments          Fetch top comments for a video.
  engagement        Single-video engagement snapshot.
  engagement-batch  Multi-URL engagement snapshot (tolerant of dead...
  list-streams      List every video format yt-dlp finds for a URL.
  metadata          Dump yt-dlp metadata for a video URL as JSON.
  pick-stream       Pick one best video stream matching the given...
  resolve           Resolve a URL to a direct ffmpeg-ready media URL...
  subtitles         Download subtitles (auto or manual) for a video into...
  thumbnail         Download the video's thumbnail to disk.
  valid             Check whether a URL is a valid video URL for yt-dlp...
  video             Download the video (best video + audio) to disk.
  ytdlp-version     Print installed yt-dlp version; warn if stale.
```

Those three blocks are verbatim captures, which is why their usage line reads
`python -m youtube_helper.cli`: that form works even when the console script
is missing, and the two are otherwise interchangeable. Every subcommand takes
`-h` for its own flags.

## Troubleshooting

- **A download hangs forever.** It should not: every yt-dlp call in the
  package sets `socket_timeout` to 30 s, so a half-closed connection fails and
  the retry ladder takes over. Raise or lower it with
  `YOUTUBE_HELPER_SOCKET_TIMEOUT` if 30 s is wrong for your link — the one
  thing not to do is unset it, because the retry tiers only run once an
  attempt returns, so an unbounded read disables all of them at once.
- **"Sign in to confirm you're not a bot".** The ladder already retries as
  `web_embedded`, `tv`, `android_vr` and `mweb` before asking you for
  anything. If all four are refused, set
  `YOUTUBE_HELPER_COOKIES_FROM_BROWSER=firefox` (or `chrome`, `safari`, …) to
  let yt-dlp borrow a logged-in session; that is the tier that actually clears
  the challenge. Tor is tried last and is not a reliable fix here, since exit
  nodes are themselves commonly flagged.
- **URL expiration.** Direct media URLs from yt-dlp expire, typically within
  one to six hours for YouTube. For long-running jobs, re-resolve periodically,
  or use `download_video` to materialise a local file.
- **Live streams.** `pick["is_live"] == True` means `pick["url"]` is typically
  an HLS `.m3u8` manifest. ffmpeg and PyAV handle these natively, but with no
  seeking backwards, no `frame_indices` or `frame_times` semantics, and
  hwaccel can be flaky with chunked HLS. `filesize_bytes` is always `0` for a
  live format.
- **yt-dlp freshness.** YouTube rotates its signature scheme often.
  `yth.ensure_recent_ytdlp(min_version="2024.12.23")` warns when your installed
  yt-dlp is too old, and `pip install -U yt-dlp` fixes most "broken decryption"
  errors.
- **Authentication.** Members-only, age-gated, or private videos need cookies.
  Pass `cookies_from_browser="firefox"` (or `"chrome"`, `"safari"`) to the
  catalog, picker, or branding functions; yt-dlp reads the active browser
  session. On macOS, Safari additionally needs Full Disk Access granted to
  your terminal, or extraction raises "Operation not permitted".
- **Comments come back empty.** YouTube comment threads almost always need
  `cookies_from_browser` now. Without it you will usually get an empty list or
  a 403.
- **A video arrives shorter than it should be.** It should not, here: this
  package refuses to skip unavailable HLS/DASH fragments and raises
  `fragment_retries` to 25, so fragment loss raises instead of quietly
  truncating. If you set `YOUTUBE_HELPER_ALLOW_LOSSY_FRAGMENTS=1`, you have
  opted back into yt-dlp's silent-truncation default.
