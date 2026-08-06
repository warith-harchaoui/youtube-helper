"""youtube-helper: Model Context Protocol (MCP) surface.

A thin adapter that exposes the FastAPI app from :mod:`youtube_helper.api` as
MCP tools, so any MCP-aware host (an agent runtime, an IDE integration, a
custom shell) can call the yt-dlp-backed operations — resolving direct media
URLs, browsing stream catalogs, downloading video/audio/thumbnails/subtitles,
and pulling no-API engagement metadata (channel/video/comments) across
YouTube, Vimeo, DailyMotion, Twitch VOD, SoundCloud, and any yt-dlp-supported
source — as first-class tools. Uses `fastapi-mcp`
(https://github.com/tadata-org/fastapi_mcp): one wrapper publishes the whole
existing HTTP surface, so the routes are never duplicated.

Install the extra to pull in ``fastapi-mcp``::

    pip install "youtube-helper[mcp]"

Then run the server (HTTP API + MCP endpoint at ``/mcp``)::

    youtube-helper-mcp                 # console entry point
    python -m youtube_helper.mcp       # equivalent

Author
------
Warith Harchaoui, Ph.D. — https://linkedin.com/in/warith-harchaoui/
"""

from __future__ import annotations

try:
    from fastapi_mcp import FastApiMCP
except ImportError as exc:  # pragma: no cover - exercised only without the extra
    raise ImportError(
        'The MCP surface needs the [mcp] extra: pip install "youtube-helper[mcp]"'
    ) from exc

# Reuse the exact same FastAPI app: MCP is a thin wrapper on top, no new routes.
from youtube_helper.api import app

# Publish the HTTP endpoints (metadata / resolve / streams / downloads / engagement) as MCP tools.
mcp = FastApiMCP(
    app,
    name="youtube-helper",
    description=(
        "youtube-helper MCP tools: a yt-dlp wrapper for downloading videos, "
        "audio, thumbnails and subtitles, resolving direct media URLs, "
        "browsing stream catalogs, and pulling no-API engagement metadata "
        "(channel / video / comments) on YouTube, Vimeo, DailyMotion, "
        "Twitch VOD, SoundCloud, and any yt-dlp-supported source."
    ),
)
# Newer fastapi-mcp splits mount() into transport-specific mount_http(); fall back to
# the legacy mount() so a range of fastapi-mcp versions keeps working.
if hasattr(mcp, "mount_http"):
    mcp.mount_http()
else:  # pragma: no cover - legacy fastapi-mcp
    mcp.mount()


def main() -> None:
    """Console entry point (``youtube-helper-mcp``): serve the API + MCP endpoint.

    Boots the FastAPI app (now serving both the ``/...`` HTTP routes and the
    ``/mcp`` MCP endpoint) with uvicorn in a single worker. Local-first: binds
    to loopback by default (override with ``YOUTUBE_HELPER_HOST`` /
    ``YOUTUBE_HELPER_PORT``).
    """
    import os

    import uvicorn

    host = os.environ.get("YOUTUBE_HELPER_HOST", "127.0.0.1")
    port = int(os.environ.get("YOUTUBE_HELPER_PORT", "8000"))
    print(f"YouTube Helper API + MCP -> http://{host}:{port}  (MCP at /mcp)")
    uvicorn.run(app, host=host, port=port, workers=1)


if __name__ == "__main__":  # pragma: no cover
    main()
