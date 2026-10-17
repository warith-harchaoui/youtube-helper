# youtube-helper CLI reference

Two CLIs over the same operations. `youtube-helper` (argparse) ships with the
core package; `youtube-helper-click` (needs `[cli]`) is the click twin — it
covers the probing and channel commands (`channel-info`, `channel-videos`,
`engagement-batch`, `list-streams`, `pick-stream`, `ytdlp-version`); the
argparse CLI is the complete surface.

## Probing — cheap, do these first

```bash
youtube-helper valid URL                 # true/false: can yt-dlp handle it
youtube-helper metadata URL [--json]     # title, duration, uploader, upload date, …
youtube-helper resolve URL               # direct media URL, nothing downloaded
youtube-helper ytdlp-version             # the yt-dlp actually in play
```

`metadata` is the call that answers "how long is this" before you commit to a
download. `resolve` hands back a URL another tool can stream from.

## Streams — see the menu, then order

```bash
youtube-helper list-streams URL [--json]
youtube-helper pick-stream  URL [--height H] [--max-height H] [--codec CODEC]
```

`list-streams` enumerates what the site offers (resolution, codec, filesize
estimate, audio/video/muxed). `pick-stream` applies the constraints and returns
the single `VideoStreamInfo` it would use — call it when you want to *see* the
choice before downloading.

## Downloading

```bash
youtube-helper video     URL [-o OUT] [--height H] [--format FMT]
youtube-helper audio     URL [-o OUT] [--format mp3|m4a|wav]
youtube-helper thumbnail URL [-o OUT]
youtube-helper subtitles URL [--lang CODE] [--auto] [-o OUT]
```

- `video` fetches the best video+audio under the constraints and muxes them
  with ffmpeg.
- `audio` fetches an **audio-only** stream — use it whenever audio is the
  target; it is far smaller than downloading the video and stripping it.
- `subtitles` pulls the author's track by default; `--auto` accepts
  machine-generated captions. If no track exists, that is a reason to reach
  for `vocal-helper`, not to retry.

## Channels and engagement

```bash
youtube-helper channel-info   URL_OR_HANDLE [--json]
youtube-helper channel-videos URL_OR_HANDLE [--limit N] [--json]
youtube-helper engagement       URL [--json]
youtube-helper engagement-batch --urls-file FILE [--json]
youtube-helper comments         URL [--limit N] [--json]
```

`engagement` returns views, likes and comment count for one video;
`engagement-batch` does the same across a list of URLs in one run. Prefer the
batch form over a shell loop: it reuses the extractor session.

`is_short` (library) tells you whether a URL is a YouTube Short, which is often
the branch you actually want.

## Output contract

- Download commands print the path they wrote.
- Probing commands print a human-readable summary; pass `--json` whenever the
  output is going to be parsed.
- `valid` prints `true` / `false` and exits `0` either way; a genuine failure
  (network, extractor error) exits non-zero.
- Failures are logged through `os_helper`; partial downloads are removed
  rather than left behind.

## When a download breaks

Extractor rot is the usual cause, not your arguments. In order:

1. `youtube-helper ytdlp-version` — see what is installed.
2. Upgrade yt-dlp (`pip install -U yt-dlp`) and retry once.
3. Only then look at the URL, the format selector, or the network.

`ensure_recent_ytdlp()` performs that check from the library side.
