# youtube-helper non-CLI surfaces

## 1. Library

```python
import youtube_helper as yh
```

Public API (`youtube_helper.__all__`): `default_ytdlp_options`,
`video_url_meta_data`, `is_valid_video_url`, `download_thumbnail`,
`download_audio`, `download_video`, `resolve_direct_url`, `DirectMediaURL`,
`list_video_streams`, `pick_video_stream`, `VideoStreamInfo`,
`extract_frames_stream`, `channel_info`, `channel_videos`, `video_engagement`,
`video_subtitles`, `video_comments`, `engagement_batch`, `is_short`,
`ensure_recent_ytdlp`.

Two worth knowing about:

- `resolve_direct_url(url)` → a `DirectMediaURL` another tool can stream from,
  with nothing written to disk.
- `extract_frames_stream(url)` → frames straight off the network, matching
  video-helper's `extract_frames` shape (BGR uint8) without a full download.

`default_ytdlp_options()` is the suite's baseline option dict — start from it
rather than hand-building one, so logging and output templates stay consistent.

Logging and file management route through `os_helper` — the suite convention.

## 2. CLIs — argparse (core) and click (`[cli]`)

`youtube-helper` and `youtube-helper-click`. See `cli-reference.md`.

## 3. HTTP API — FastAPI (`[api]`)

```bash
pip install 'youtube-helper[api]'
python -m youtube_helper.api        # 127.0.0.1:8000, OpenAPI docs at /docs
```

One route per operation: `/metadata`, `/valid`, `/resolve`, `/list-streams`,
`/pick-stream`, `/channel-info`, `/channel-videos`, `/engagement`,
`/engagement-batch`, `/comments`, `/ytdlp-version`, `/video`, `/audio`,
`/thumbnail`, `/subtitles`, plus `/health`, `/` and `/gui`.

Probing routes return JSON; download routes write locally and report the path.

## 4. MCP — `fastapi-mcp` over the *same* app (`[mcp]`)

```bash
pip install 'youtube-helper[mcp]'
youtube-helper-mcp                  # same app, MCP mounted at /mcp
```

`youtube_helper.mcp` takes the FastAPI app from `youtube_helper.api` and
mounts `FastApiMCP` on it. Every MCP tool *is* an HTTP route, so the two
surfaces cannot drift and one process serves both doors.

Register it with Claude Code:

```bash
claude mcp add youtube-helper --transport http http://127.0.0.1:8000/mcp
```

## 5. Browser GUI (`[api]`)

`GET /gui` — paste a URL, see the metadata and the available streams, pick one
and download. The surface to hand a human who wants to look before pulling.

## Where this sits in the suite

```
youtube-helper  ──►  video-helper   (re-encode, cut, frames, subtitles)
      │         ──►  audio-helper   (resample, split, stems)
      └─────────►  vocal-helper   (transcribe, diarize)
```

youtube-helper **acquires**. Everything downstream transforms. Chaining the
packages beats reaching for raw ffmpeg between them, because each one already
carries the suite's logging, validation and temp-file discipline.
