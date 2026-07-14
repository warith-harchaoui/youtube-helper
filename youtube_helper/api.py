"""
YouTube Helper — FastAPI HTTP surface.

Exposes every public function in :mod:`youtube_helper.main`,
:mod:`youtube_helper.streaming` and :mod:`youtube_helper.branding` as an
HTTP endpoint so `youtube-helper` can be dropped behind any reverse
proxy and consumed by other services. Kept intentionally minimal:

- Read endpoints (``/metadata``, ``/valid``, ``/resolve``,
  ``/list-streams``, ``/pick-stream``, ``/channel-info``,
  ``/channel-videos``, ``/engagement``, ``/engagement-batch``,
  ``/comments``, ``/ytdlp-version``) accept a JSON body or query params
  and return JSON.
- Download endpoints (``/video``, ``/audio``, ``/thumbnail``) stream the
  resulting file back to the caller and clean the temp folder as a
  background task, so no leftover bytes on disk after a request.
- ``/subtitles`` bundles the downloaded .vtt files into a ZIP.

Install the extra to get the runtime dependencies::

    pip install 'youtube-helper[api]'

Then run the app with any ASGI server::

    uvicorn youtube_helper.api:app --host 0.0.0.0 --port 8000

Usage Example
-------------
>>> # Start the server:
>>> #   uvicorn youtube_helper.api:app --reload
>>> # Get metadata for a URL:
>>> #   curl -X POST -H 'Content-Type: application/json' \\
>>> #        -d '{"url":"https://www.youtube.com/watch?v=YE7VzlLtp-4"}' \\
>>> #        http://localhost:8000/metadata
>>> # Download the audio:
>>> #   curl -X POST -H 'Content-Type: application/json' \\
>>> #        -d '{"url":"https://www.youtube.com/watch?v=YE7VzlLtp-4"}' \\
>>> #        -o out.mp3 http://localhost:8000/audio
>>> # Full OpenAPI docs at http://localhost:8000/docs

Author
------
Warith Harchaoui, Ph.D. — https://linkedin.com/in/warith-harchaoui/
"""

from __future__ import annotations

import io
import shutil
import tempfile
import zipfile
from pathlib import Path

try:
    from fastapi import BackgroundTasks, FastAPI, HTTPException
    from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The FastAPI HTTP surface requires the [api] extra. "
        "Install with: pip install 'youtube-helper[api]'"
    ) from exc

from . import (
    channel_info,
    channel_videos,
    download_audio,
    download_thumbnail,
    download_video,
    engagement_batch,
    ensure_recent_ytdlp,
    is_valid_video_url,
    list_video_streams,
    pick_video_stream,
    resolve_direct_url,
    video_comments,
    video_engagement,
    video_subtitles,
    video_url_meta_data,
)

# ---------------------------------------------------------------------------
# App factory + shared plumbing
# ---------------------------------------------------------------------------


app = FastAPI(
    title="YouTube Helper API",
    description=(
        "HTTP surface for the youtube-helper utilities: download video / "
        "audio / thumbnails, resolve direct media URLs, browse video "
        "stream catalogs, pull no-API engagement metadata."
    ),
    version="1.3.3",
    docs_url="/docs",
    redoc_url="/redoc",
)


def _cleanup(*paths: Path | str) -> None:
    """Best-effort cleanup — never let a tidy-up failure kill a response."""
    for p in paths:
        try:
            path = Path(p)
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            elif path.exists():
                path.unlink(missing_ok=True)
        except Exception:
            pass


def _new_tmpdir() -> Path:
    """Create a request-scoped temp directory under the system temp root."""
    return Path(tempfile.mkdtemp(prefix="youtube-helper-"))


def _zip_folder(folder: Path) -> io.BytesIO:
    """Bundle ``folder``'s contents into an in-memory ZIP for streaming."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in folder.rglob("*"):
            if p.is_file():
                zf.write(p, arcname=p.relative_to(folder))
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# Pydantic request models
#
# Named schemas so the OpenAPI documentation reads cleanly. Each model
# has an example that shows up in `/docs` — it makes the "try it" flow
# far friendlier than raw JSON-editor screens.
# ---------------------------------------------------------------------------


class UrlBody(BaseModel):
    """Single-URL request body — used by most read endpoints."""

    url: str = Field(..., description="Any URL yt-dlp can extract.")
    verbose: bool = False


class DownloadBody(BaseModel):
    """Request body for the download endpoints (video / audio / thumbnail)."""

    url: str = Field(..., description="Any URL yt-dlp can extract.")
    # Sample rate lives here rather than on a dedicated /audio-body because
    # the same schema drives both audio and thumbnail (unused for the latter).
    sample_rate: int = Field(44100, description="Target sample rate (audio only).")


class ResolveBody(BaseModel):
    """Request body for the /resolve endpoint."""

    url: str = Field(..., description="Any URL yt-dlp can extract.")
    prefer: str = Field("audio", description="'audio' or 'video'.")
    live: str = Field("auto", description="'auto' | 'force_live' | 'force_vod'.")


class StreamFiltersBody(BaseModel):
    """Shared body for /list-streams and /pick-stream (constraint filters)."""

    url: str
    prefer_codec: str | None = None
    prefer_format: str | None = None
    max_fps: float | None = None
    language: str | None = None
    include_video_only: bool = True
    include_combined: bool = True
    cookies_from_browser: str | None = None
    verbose: bool = False


class ChannelVideosBody(BaseModel):
    """Request body for /channel-videos."""

    url: str
    max_videos: int = 200
    include_shorts: bool = True
    include_lives: bool = False
    verbose: bool = False


class EngagementBatchBody(BaseModel):
    """Request body for /engagement-batch."""

    urls: list[str]
    verbose: bool = False


class SubtitlesBody(BaseModel):
    """Request body for /subtitles."""

    url: str
    langs: list[str] = Field(default_factory=lambda: ["fr", "en"])
    auto_only: bool = True
    verbose: bool = False


class CommentsBody(BaseModel):
    """Request body for /comments."""

    url: str
    max_count: int = 100
    cookies_from_browser: str | None = None
    verbose: bool = False


class YtDlpVersionBody(BaseModel):
    """Request body for /ytdlp-version."""

    min_version: str | None = None


# ---------------------------------------------------------------------------
# Meta
# ---------------------------------------------------------------------------


@app.get("/health", tags=["meta"])
def health() -> dict:
    """Simple liveness probe — no dependency check, just proves the app is up."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Read endpoints
# ---------------------------------------------------------------------------


@app.post("/metadata", tags=["reads"])
def metadata(body: UrlBody) -> JSONResponse:
    """Return yt-dlp metadata for the given video URL."""
    # video_url_meta_data raises AssertionError on invalid input — surface
    # a 400 rather than a raw 500 traceback.
    try:
        meta = video_url_meta_data(body.url)
    except AssertionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return JSONResponse(meta)


@app.post("/valid", tags=["reads"])
def valid(body: UrlBody) -> JSONResponse:
    """Return whether a URL is a valid video URL for yt-dlp."""
    return JSONResponse({"valid": bool(is_valid_video_url(body.url))})


@app.post("/resolve", tags=["reads"])
def resolve(body: ResolveBody) -> JSONResponse:
    """Resolve a URL to a direct ffmpeg-ready media URL."""
    try:
        result = resolve_direct_url(url=body.url, prefer=body.prefer, live=body.live)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return JSONResponse(dict(result))


@app.post("/list-streams", tags=["reads"])
def list_streams(body: StreamFiltersBody) -> JSONResponse:
    """List every video format yt-dlp finds for a URL."""
    try:
        streams = list_video_streams(
            url=body.url,
            include_video_only=body.include_video_only,
            include_combined=body.include_combined,
            cookies_from_browser=body.cookies_from_browser,
            verbose=body.verbose,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return JSONResponse([dict(s) for s in streams])


@app.post("/pick-stream", tags=["reads"])
def pick_stream(body: StreamFiltersBody) -> JSONResponse:
    """Pick one best video stream matching the constraints."""
    try:
        chosen = pick_video_stream(
            url=body.url,
            prefer_codec=body.prefer_codec,
            prefer_format=body.prefer_format,
            max_fps=body.max_fps,
            language=body.language,
            include_video_only=body.include_video_only,
            include_combined=body.include_combined,
            cookies_from_browser=body.cookies_from_browser,
            verbose=body.verbose,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return JSONResponse(dict(chosen))


@app.post("/channel-info", tags=["reads"])
def channel_info_endpoint(body: UrlBody) -> JSONResponse:
    """Channel-level snapshot (subs, total views, video count)."""
    return JSONResponse(channel_info(url=body.url, verbose=body.verbose))


@app.post("/channel-videos", tags=["reads"])
def channel_videos_endpoint(body: ChannelVideosBody) -> JSONResponse:
    """List channel videos with normalised engagement metadata."""
    items = channel_videos(
        url=body.url,
        max_videos=body.max_videos,
        include_shorts=body.include_shorts,
        include_lives=body.include_lives,
        verbose=body.verbose,
    )
    return JSONResponse(items)


@app.post("/engagement", tags=["reads"])
def engagement_endpoint(body: UrlBody) -> JSONResponse:
    """Single-video engagement snapshot."""
    return JSONResponse(video_engagement(url=body.url, verbose=body.verbose))


@app.post("/engagement-batch", tags=["reads"])
def engagement_batch_endpoint(body: EngagementBatchBody) -> JSONResponse:
    """Multi-URL engagement snapshot (tolerant of dead entries)."""
    return JSONResponse(engagement_batch(urls=body.urls, verbose=body.verbose))


@app.post("/comments", tags=["reads"])
def comments_endpoint(body: CommentsBody) -> JSONResponse:
    """Fetch top comments for a video."""
    return JSONResponse(
        video_comments(
            url=body.url,
            max_count=body.max_count,
            cookies_from_browser=body.cookies_from_browser,
            verbose=body.verbose,
        )
    )


@app.post("/ytdlp-version", tags=["reads"])
def ytdlp_version_endpoint(body: YtDlpVersionBody) -> JSONResponse:
    """Return installed yt-dlp version; warn if stale."""
    return JSONResponse({"version": ensure_recent_ytdlp(min_version=body.min_version)})


# ---------------------------------------------------------------------------
# Download endpoints
# ---------------------------------------------------------------------------


@app.post("/video", tags=["actions"])
def video_endpoint(body: DownloadBody, background: BackgroundTasks) -> FileResponse:
    """Download the video (best video + audio) and stream the file back."""
    tmp = _new_tmpdir()
    dst = tmp / "video.mp4"
    try:
        download_video(url=body.url, output_path=str(dst))
    except Exception as exc:
        _cleanup(tmp)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    background.add_task(_cleanup, tmp)
    return FileResponse(str(dst), filename=dst.name, media_type="application/octet-stream")


@app.post("/audio", tags=["actions"])
def audio_endpoint(body: DownloadBody, background: BackgroundTasks) -> FileResponse:
    """Download the audio track only and stream the file back."""
    tmp = _new_tmpdir()
    dst = tmp / "audio.mp3"
    try:
        download_audio(url=body.url, output_path=str(dst), target_sample_rate=body.sample_rate)
    except Exception as exc:
        _cleanup(tmp)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    background.add_task(_cleanup, tmp)
    return FileResponse(str(dst), filename=dst.name, media_type="application/octet-stream")


@app.post("/thumbnail", tags=["actions"])
def thumbnail_endpoint(body: DownloadBody, background: BackgroundTasks) -> FileResponse:
    """Download the video's thumbnail and stream the file back."""
    tmp = _new_tmpdir()
    dst = tmp / "thumbnail.png"
    try:
        download_thumbnail(url=body.url, output_path=str(dst))
    except Exception as exc:
        _cleanup(tmp)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    background.add_task(_cleanup, tmp)
    return FileResponse(str(dst), filename=dst.name, media_type="application/octet-stream")


@app.post("/subtitles", tags=["actions"])
def subtitles_endpoint(body: SubtitlesBody, background: BackgroundTasks) -> StreamingResponse:
    """Download subtitles (auto or manual); response is a ZIP with the .vtt files."""
    tmp = _new_tmpdir()
    subs_dir = tmp / "subs"
    subs_dir.mkdir()
    try:
        video_subtitles(
            url=body.url,
            output_dir=str(subs_dir),
            langs=tuple(body.langs),
            auto_only=body.auto_only,
            verbose=body.verbose,
        )
    except Exception as exc:
        _cleanup(tmp)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    buf = _zip_folder(subs_dir)
    background.add_task(_cleanup, tmp)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="subtitles.zip"'},
    )
