"""
YouTube Helper

Utilities for downloading videos, audio, thumbnails, resolving direct
media URLs, and pulling public engagement metadata — from YouTube, Vimeo,
DailyMotion, Twitch VOD, and any other site `yt-dlp` supports.

Modules
-------
- ``main``       : download helpers (videos / audio / thumbnails) and
                   metadata extraction.
- ``streaming``  : URL resolver that turns a user-facing page URL into a
                   direct media URL (with the right headers / cookies) so
                   an ffmpeg-based reader can consume it without going
                   through yt-dlp again. Pure resolution — no PCM
                   decoding (that's ``podcast_helper``'s job).
- ``branding``   : no-API engagement helpers (channel info, video lists
                   with normalised metrics, subtitles, comments). Built
                   on yt-dlp's public metadata — no Google Data API,
                   no Vimeo API, no OAuth, no quota.

Multi-surface exposure
----------------------
The same functions are also available as:

- ``youtube_helper.cli_argparse`` — argparse-based CLI, entry point
  ``youtube-helper``. No extra dependency.
- ``youtube_helper.cli_click``    — click-based twin CLI, entry point
  ``youtube-helper-click``. Requires the ``[cli]`` extra.
- ``youtube_helper.api``          — FastAPI HTTP surface. Requires the
  ``[api]`` extra.
- ``youtube_helper.mcp``          — MCP tools over the FastAPI app,
  entry point ``youtube-helper-mcp``. Requires the ``[api,mcp]`` extras.

Dependencies
- yt-dlp
- ffmpeg (on PATH)
- os-helper / audio-helper / video-helper

Usage Example
-------------
>>> import youtube_helper as yth
>>> meta = yth.video_url_meta_data("https://www.youtube.com/watch?v=YE7VzlLtp-4")
>>> yth.download_audio("https://www.youtube.com/watch?v=YE7VzlLtp-4", "out.mp3")

Author
------
Warith Harchaoui, Ph.D. — https://linkedin.com/in/warith-harchaoui/
"""

__author__ = "Warith Harchaoui, Ph.D."
__email__ = "warithmetics@deraison.ai"

__all__ = [
    # main — download helpers
    "default_ytdlp_options",
    "video_url_meta_data",
    "is_valid_video_url",
    "download_thumbnail",
    "download_audio",
    "download_video",
    # streaming — URL resolver + catalog/picker + one-call frame stream
    "resolve_direct_url",
    "DirectMediaURL",
    "list_video_streams",
    "pick_video_stream",
    "VideoStreamInfo",
    "extract_frames_stream",
    # branding — engagement / channel helpers (no Data / Analytics API)
    "channel_info",
    "channel_videos",
    "video_engagement",
    "video_subtitles",
    "video_comments",
    "engagement_batch",
    "is_short",
    "ensure_recent_ytdlp",
]


from .branding import (
    channel_info,
    channel_videos,
    engagement_batch,
    ensure_recent_ytdlp,
    is_short,
    video_comments,
    video_engagement,
    video_subtitles,
)
from .main import (
    default_ytdlp_options,
    download_audio,
    download_thumbnail,
    download_video,
    is_valid_video_url,
    video_url_meta_data,
)
from .streaming import (
    DirectMediaURL,
    VideoStreamInfo,
    extract_frames_stream,
    list_video_streams,
    pick_video_stream,
    resolve_direct_url,
)
