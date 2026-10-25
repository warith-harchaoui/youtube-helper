# youtube-helper CLI reference

One command line, `youtube-helper`, shipped with the core package — no extra to
install, no second parser. Every subcommand takes its target as a named option
(`--url`), never as a positional argument.

## Probing — cheap, do these first

```bash
youtube-helper valid        --url URL   # true/false: can yt-dlp handle it
youtube-helper metadata     --url URL   # title, duration, uploader, upload date, … (JSON)
youtube-helper resolve      --url URL [--prefer audio|video] [--live auto|force_live|force_vod]
youtube-helper ytdlp-version [--min-version X.Y.Z]
```

`metadata` is the call that answers "how long is this" before you commit to a
download. `resolve` hands back a URL another tool can stream from.

## Streams — see the menu, then order

```bash
youtube-helper list-streams --url URL [--no-video-only] [--no-combined] \
                            [--cookies-from-browser BROWSER] [--verbose]
youtube-helper pick-stream  --url URL [--prefer-codec h264|vp9|av1] \
                            [--prefer-format mp4|webm] [--max-fps N] [--language CODE] \
                            [--no-video-only] [--no-combined] \
                            [--cookies-from-browser BROWSER] [--verbose]
```

`list-streams` enumerates what the site offers (resolution, codec, filesize
estimate, audio/video/muxed). `pick-stream` applies the constraints and returns
the single `VideoStreamInfo` it would use — call it when you want to *see* the
choice before downloading.

## Downloading

```bash
youtube-helper video     --url URL [--output PATH] [--max-height 720]
youtube-helper audio     --url URL [--output PATH] [--sample-rate 44100]
youtube-helper thumbnail --url URL [--output PATH]
youtube-helper subtitles --url URL --output-dir DIR [--langs fr --langs en] \
                         [--manual] [--verbose]
```

- `video` fetches the best video+audio under the constraints and muxes them
  with ffmpeg. `--max-height` also prefers direct https formats over the HLS
  ones YouTube throttles, so capping is usually faster, not slower.
- `audio` fetches an **audio-only** stream — use it whenever audio is the
  target; it is far smaller than downloading the video and stripping it.
- `subtitles` prefers machine-generated captions by default; `--manual` asks
  for the author's track instead. Repeat `--langs` once per language. If no
  track exists, that is a reason to reach for `vocal-helper`, not to retry.
- `--output` is optional everywhere: omitted, the path is derived from the
  video's title.

## Channels and engagement

```bash
youtube-helper channel-info   --url URL [--verbose]
youtube-helper channel-videos --url URL [--max-videos 200] [--no-shorts] [--include-lives] [--verbose]
youtube-helper engagement       --url URL [--verbose]
youtube-helper engagement-batch --urls URL --urls URL [--verbose]
youtube-helper comments         --url URL [--max 100] [--cookies-from-browser BROWSER] [--verbose]
```

`engagement` returns views, likes and comment count for one video;
`engagement-batch` does the same across a list of URLs in one run — repeat
`--urls` once per video. Prefer the batch form over a shell loop: it reuses the
extractor session.

`is_short` (library) tells you whether a URL is a YouTube Short, which is often
the branch you actually want.

## Output contract

- Download commands print the path they wrote.
- Every probing command prints JSON already (indented, UTF-8 kept as-is), so
  there is nothing to switch on: pipe it straight into `jq`.
- `valid` prints `true` / `false`; it exits `0` on `true` and `1` on `false`, so
  the exit code alone is usable in a shell test.
- A library error is printed as a single `Error: …` line on stderr with exit
  `1` — never a Python traceback.
- Failures are logged through `os_helper`; partial downloads are removed
  rather than left behind.

## When a download breaks

Extractor rot is the usual cause, not your arguments. In order:

1. `youtube-helper ytdlp-version` — see what is installed.
2. Upgrade yt-dlp (`pip install -U yt-dlp`) and retry once.
3. Only then look at the URL, the format selector, or the network.

`ensure_recent_ytdlp()` performs that check from the library side.
