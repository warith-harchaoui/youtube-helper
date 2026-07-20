# youtube-helper CLI reference

Two CLIs expose the exact same subcommands and flags:

- **argparse** `youtube-helper <sub> …` — ships with the base package, zero extra
  deps. Primary surface.
- **click** `youtube-helper-click <sub> …` — install `youtube-helper[cli]`. Same
  subcommands and flag names; nicer `--help`.

Every subcommand prints a machine-friendly result to stdout: a plain file path
for single-file downloads, JSON for structured outputs (metadata, streams,
engagement). Errors propagate as non-zero exit codes.

## Downloads

```bash
youtube-helper video     --url URL [--output out.mp4]
youtube-helper audio     --url URL [--output out.mp3] [--sample-rate 44100]
youtube-helper thumbnail --url URL [--output out.png]
```

- `--output` is auto-named from the video title when omitted.
- `audio --sample-rate` sets the output sample rate (default 44100).
- `video` downloads `bestvideo+bestaudio`, muxed by ffmpeg to the `--output`
  container (mp4 by default).

## Metadata / validation

```bash
youtube-helper metadata --url URL          # full yt-dlp info dict as JSON
youtube-helper valid    --url URL          # prints true/false; exit 0 iff valid
```

## Direct-URL resolver & stream catalog

```bash
youtube-helper resolve      --url URL [--prefer audio|video] [--live auto|force_live|force_vod]
youtube-helper list-streams --url URL [--no-video-only] [--no-combined] \
                            [--cookies-from-browser firefox|chrome|safari] [--verbose]
youtube-helper pick-stream  --url URL [--prefer-codec h264|vp9|av1] [--prefer-format mp4|webm] \
                            [--max-fps 30] [--language en] [--no-video-only] [--no-combined] \
                            [--cookies-from-browser …] [--verbose]
```

- `resolve` emits JSON with `url`, `container`, `is_live`, `headers` — feed it to
  an ffmpeg reader.
- `pick-stream` returns one `VideoStreamInfo` (or errors if none match the
  constraints), ready to hand to `video_helper.extract_frames`.

## No-API engagement / branding

```bash
youtube-helper channel-info    --url CHANNEL_URL [--verbose]
youtube-helper channel-videos  --url CHANNEL_URL [--max-videos 200] [--no-shorts] \
                               [--include-lives] [--verbose]
youtube-helper engagement       --url URL [--verbose]
youtube-helper engagement-batch --urls URL1 URL2 … [--verbose]
youtube-helper subtitles        --url URL --output-dir DIR [--langs fr en] [--manual] [--verbose]
youtube-helper comments         --url URL [--max 100] [--cookies-from-browser …] [--verbose]
youtube-helper ytdlp-version    [--min-version 2024.12.23]
```

- `engagement-batch` is tolerant: dead entries surface as
  `{"url": …, "_error": …}` rather than aborting the batch.
- `subtitles` writes `.vtt` files into `--output-dir`; `--manual` prefers
  human-authored subtitles over auto-generated ones.
- `channel-videos` normalises engagement metrics into a cross-platform schema.

## Output contract

- Single-file downloads (`video` / `audio` / `thumbnail`) print the absolute
  output path — capture it and hand it back.
- Structured commands print JSON (pretty-printed, `ensure_ascii=False`).
- `valid` prints `true`/`false` and sets the exit code accordingly for shell use.

## Environment

- `YOUTUBE_HELPER_COOKIES` — path to a Netscape cookies.txt for authenticated /
  bot-blocked downloads.
- `YOUTUBE_HELPER_HOST` / `YOUTUBE_HELPER_PORT` — bind host/port for the
  `youtube-helper-mcp` server (default `0.0.0.0:8000`).
