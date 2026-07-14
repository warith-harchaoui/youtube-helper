"""
YouTube Helper — argparse-based command-line interface.

Thin wrapper around the pure functions in :mod:`youtube_helper.main`,
:mod:`youtube_helper.streaming` and :mod:`youtube_helper.branding` that
exposes the whole toolkit as subcommands under a single ``youtube-helper``
entry point. Written with :mod:`argparse` from the standard library so
the CLI works out of the box on any Python install that has the package
installed — no extra dependency required.

Subcommands
-----------
- ``metadata``      — dump JSON metadata for one video URL
- ``valid``         — exit 0 iff the URL is a valid video URL for yt-dlp
- ``video``         — download the video track to disk
- ``audio``         — download the audio track to disk
- ``thumbnail``     — download the thumbnail image to disk
- ``resolve``       — resolve a URL to a direct ffmpeg-ready media URL
- ``list-streams``  — enumerate every video format yt-dlp finds
- ``pick-stream``   — pick a single best video format matching constraints
- ``channel-info``  — channel snapshot (subs, video count, total views)
- ``channel-videos``— list channel videos with normalised engagement metrics
- ``engagement``    — one-video engagement snapshot (views/likes/comments)
- ``engagement-batch`` — multi-URL engagement snapshot
- ``subtitles``     — download (auto) subtitles for a video into a folder
- ``comments``      — dump top comments of a video
- ``ytdlp-version`` — print installed yt-dlp version

Usage Example
-------------
>>> #   youtube-helper metadata     --url https://www.youtube.com/watch?v=YE7VzlLtp-4
>>> #   youtube-helper audio        --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --output out.mp3
>>> #   youtube-helper video        --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --output out.mp4
>>> #   youtube-helper thumbnail    --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --output out.png
>>> #   youtube-helper resolve      --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --prefer audio
>>> #   youtube-helper list-streams --url https://www.youtube.com/watch?v=YE7VzlLtp-4
>>> #   youtube-helper pick-stream  --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --prefer-codec h264
>>> #   youtube-helper channel-info --url https://www.youtube.com/@blender
>>> #   youtube-helper engagement   --url https://www.youtube.com/watch?v=YE7VzlLtp-4
>>> #   youtube-helper subtitles    --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --output-dir subs/
>>> #   youtube-helper comments     --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --max 50

Author
------
Warith Harchaoui, Ph.D. — https://linkedin.com/in/warith-harchaoui/
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

# Import the pure functions once here — every subcommand is a thin dispatch
# on top of these, no logic duplication.
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
# Subcommand handlers
#
# Each handler receives the parsed ``argparse.Namespace`` and returns a
# process exit code (``0`` on success). Handlers deliberately stay short:
# they translate CLI arguments into keyword arguments for the underlying
# library function, print a machine-friendly result (JSON for structured
# outputs, plain path for single-file outputs), and let exceptions
# propagate as non-zero exit codes.
# ---------------------------------------------------------------------------


def _dumps(obj: object) -> str:
    """JSON-encode with a safe default so odd yt-dlp types (bytes, sets) still print."""
    return json.dumps(obj, indent=2, default=str, ensure_ascii=False)


def _handle_metadata(ns: argparse.Namespace) -> int:
    """Full yt-dlp info dict for the URL — verbose, useful for debugging.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Full yt-dlp info dict for the URL — verbose, useful for debugging.
    meta = video_url_meta_data(ns.url)
    print(_dumps(meta))
    return 0


def _handle_valid(ns: argparse.Namespace) -> int:
    """Exit 0 iff URL is a valid video URL. Handy in shell as `if …; then …; fi`.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Exit 0 iff URL is a valid video URL. Handy in shell as `if …; then …; fi`.
    ok = is_valid_video_url(ns.url)
    print("true" if ok else "false")
    return 0 if ok else 1


def _handle_video(ns: argparse.Namespace) -> int:
    """Download the video track (yt-dlp bestvideo+bestaudio, muxed).

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Download the video track (yt-dlp bestvideo+bestaudio, muxed).
    out = download_video(url=ns.url, output_path=ns.output)
    print(out)
    return 0


def _handle_audio(ns: argparse.Namespace) -> int:
    """Download the audio track only (yt-dlp bestaudio, re-encoded via ffmpeg).

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Download the audio track only (yt-dlp bestaudio, re-encoded via ffmpeg).
    out = download_audio(url=ns.url, output_path=ns.output, target_sample_rate=ns.sample_rate)
    print(out)
    return 0


def _handle_thumbnail(ns: argparse.Namespace) -> int:
    """Download the thumbnail image (PNG / JPG chosen by --output extension).

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Download the thumbnail image (PNG / JPG chosen by --output extension).
    out = download_thumbnail(url=ns.url, output_path=ns.output)
    print(out)
    return 0


def _handle_resolve(ns: argparse.Namespace) -> int:
    """Quick resolver — one direct ffmpeg-ready URL. Emits JSON so callers can pluck `url`, `container`, `is_live`, `headers` without shelling grep tricks.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Quick resolver — one direct ffmpeg-ready URL. Emits JSON so callers can pluck
    # `url`, `container`, `is_live`, `headers` without shelling grep tricks.
    result = resolve_direct_url(url=ns.url, prefer=ns.prefer, live=ns.live)
    print(_dumps(result))
    return 0


def _handle_list_streams(ns: argparse.Namespace) -> int:
    """Full video-format catalog. Excludes audio-only formats.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Full video-format catalog. Excludes audio-only formats.
    streams = list_video_streams(
        url=ns.url,
        include_video_only=ns.include_video_only,
        include_combined=ns.include_combined,
        cookies_from_browser=ns.cookies_from_browser,
        verbose=ns.verbose,
    )
    print(_dumps(streams))
    return 0


def _handle_pick_stream(ns: argparse.Namespace) -> int:
    """Single stream matching the constraints (or ValueError if none match).

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Single stream matching the constraints (or ValueError if none match).
    chosen = pick_video_stream(
        url=ns.url,
        prefer_codec=ns.prefer_codec,
        prefer_format=ns.prefer_format,
        max_fps=ns.max_fps,
        language=ns.language,
        include_video_only=ns.include_video_only,
        include_combined=ns.include_combined,
        cookies_from_browser=ns.cookies_from_browser,
        verbose=ns.verbose,
    )
    print(_dumps(chosen))
    return 0


def _handle_channel_info(ns: argparse.Namespace) -> int:
    """Channel-level snapshot (subs, video_count, total views).

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Channel-level snapshot (subs, video_count, total views).
    print(_dumps(channel_info(url=ns.url, verbose=ns.verbose)))
    return 0


def _handle_channel_videos(ns: argparse.Namespace) -> int:
    """Paginated video list with normalised engagement metadata.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Paginated video list with normalised engagement metadata.
    items = channel_videos(
        url=ns.url,
        max_videos=ns.max_videos,
        include_shorts=ns.include_shorts,
        include_lives=ns.include_lives,
        verbose=ns.verbose,
    )
    print(_dumps(items))
    return 0


def _handle_engagement(ns: argparse.Namespace) -> int:
    """Single-video engagement snapshot.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Single-video engagement snapshot.
    print(_dumps(video_engagement(url=ns.url, verbose=ns.verbose)))
    return 0


def _handle_engagement_batch(ns: argparse.Namespace) -> int:
    """Multi-URL variant — tolerant (dead entries surface as {"url": …, "_error": …}).

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Multi-URL variant — tolerant (dead entries surface as {"url": …, "_error": …}).
    print(_dumps(engagement_batch(urls=list(ns.urls), verbose=ns.verbose)))
    return 0


def _handle_subtitles(ns: argparse.Namespace) -> int:
    """Auto (or manual) subtitles → {lang: absolute_vtt_path}.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Auto (or manual) subtitles → {lang: absolute_vtt_path}.
    langs = tuple(ns.langs)
    result = video_subtitles(
        url=ns.url,
        output_dir=ns.output_dir,
        langs=langs,
        auto_only=ns.auto_only,
        verbose=ns.verbose,
    )
    print(_dumps(result))
    return 0


def _handle_comments(ns: argparse.Namespace) -> int:
    """Top-N comments as a JSON list.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Top-N comments as a JSON list.
    result = video_comments(
        url=ns.url,
        max_count=ns.max,
        cookies_from_browser=ns.cookies_from_browser,
        verbose=ns.verbose,
    )
    print(_dumps(result))
    return 0


def _handle_ytdlp_version(ns: argparse.Namespace) -> int:
    """Utility — cheapest way to check freshness in ops.

    Parameters
    ----------
    ns : argparse.Namespace
        Parsed CLI arguments for this subcommand.

    Returns
    -------
    int
        Process exit code (0 on success).
    """
    # Utility — cheapest way to check freshness in ops.
    version = ensure_recent_ytdlp(min_version=ns.min_version)
    print(version)
    return 0


# ---------------------------------------------------------------------------
# Parser construction
#
# One helper per subcommand keeps ``build_parser`` readable and lets the
# click twin (:mod:`youtube_helper.cli_click`) mirror the exact same flag
# names without any risk of drift.
# ---------------------------------------------------------------------------


def _add_metadata(sub: argparse._SubParsersAction) -> None:
    """Register the ``metadata`` subcommand: dump yt-dlp metadata for a video URL as JSON.

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser("metadata", help="Dump yt-dlp metadata for a video URL as JSON.")
    p.add_argument("--url", required=True, help="Video URL.")
    p.set_defaults(func=_handle_metadata)


def _add_valid(sub: argparse._SubParsersAction) -> None:
    """Register the ``valid`` subcommand: check if a URL is a valid video URL for yt-dlp.

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser("valid", help="Check if a URL is a valid video URL for yt-dlp.")
    p.add_argument("--url", required=True, help="Video URL.")
    p.set_defaults(func=_handle_valid)


def _add_video(sub: argparse._SubParsersAction) -> None:
    """Register the ``video`` subcommand: download the video (best video + audio) to disk.

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser("video", help="Download the video (best video + audio) to disk.")
    p.add_argument("--url", required=True, help="Video URL.")
    p.add_argument("--output", default=None, help="Output path (auto-named from title if omitted).")
    p.set_defaults(func=_handle_video)


def _add_audio(sub: argparse._SubParsersAction) -> None:
    """Register the ``audio`` subcommand: download only the audio track to disk.

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser("audio", help="Download only the audio track to disk.")
    p.add_argument("--url", required=True, help="Video URL.")
    p.add_argument("--output", default=None, help="Output audio path (auto-named if omitted).")
    p.add_argument(
        "--sample-rate",
        type=int,
        default=44100,
        dest="sample_rate",
        help="Target sample rate for the output audio (default 44100).",
    )
    p.set_defaults(func=_handle_audio)


def _add_thumbnail(sub: argparse._SubParsersAction) -> None:
    """Register the ``thumbnail`` subcommand: download the video's thumbnail to disk.

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser("thumbnail", help="Download the video's thumbnail to disk.")
    p.add_argument("--url", required=True, help="Video URL.")
    p.add_argument("--output", default=None, help="Output image path (auto-named if omitted).")
    p.set_defaults(func=_handle_thumbnail)


def _add_resolve(sub: argparse._SubParsersAction) -> None:
    """Register the ``resolve`` subcommand: resolve a URL to a direct ffmpeg-ready media URL (audio or video).

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser(
        "resolve",
        help="Resolve a URL to a direct ffmpeg-ready media URL (audio or video).",
    )
    p.add_argument("--url", required=True, help="Video URL.")
    p.add_argument(
        "--prefer",
        choices=["audio", "video"],
        default="audio",
        help="Format preference: audio (bestaudio) or video (best combined).",
    )
    p.add_argument(
        "--live",
        choices=["auto", "force_live", "force_vod"],
        default="auto",
        help="Live-stream classification override (default: propagate yt-dlp).",
    )
    p.set_defaults(func=_handle_resolve)


def _stream_filter_args(p: argparse.ArgumentParser) -> None:
    """Attach the shared stream-catalog filter flags used by list/pick."""
    p.add_argument(
        "--no-video-only",
        dest="include_video_only",
        action="store_false",
        default=True,
        help="Exclude video-only formats (DASH style, need separate audio mux).",
    )
    p.add_argument(
        "--no-combined",
        dest="include_combined",
        action="store_false",
        default=True,
        help="Exclude combined video+audio formats (progressive).",
    )
    p.add_argument(
        "--cookies-from-browser",
        dest="cookies_from_browser",
        default=None,
        help="Browser to pull cookies from (firefox / chrome / safari / …).",
    )
    p.add_argument("--verbose", action="store_true", help="Echo yt-dlp's output to stderr.")


def _add_list_streams(sub: argparse._SubParsersAction) -> None:
    """Register the ``list-streams`` subcommand: list every video format yt-dlp finds for a URL.

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser("list-streams", help="List every video format yt-dlp finds for a URL.")
    p.add_argument("--url", required=True, help="Video URL.")
    _stream_filter_args(p)
    p.set_defaults(func=_handle_list_streams)


def _add_pick_stream(sub: argparse._SubParsersAction) -> None:
    """Register the ``pick-stream`` subcommand: pick one best video stream matching constraints.

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser("pick-stream", help="Pick one best video stream matching constraints.")
    p.add_argument("--url", required=True, help="Video URL.")
    p.add_argument(
        "--prefer-codec",
        dest="prefer_codec",
        default=None,
        help="Substring match on vcodec (h264 / vp9 / av1).",
    )
    p.add_argument(
        "--prefer-format",
        dest="prefer_format",
        default=None,
        help="Equality match on ext (mp4 / webm).",
    )
    p.add_argument(
        "--max-fps",
        type=float,
        dest="max_fps",
        default=None,
        help="Drop formats with fps > max_fps.",
    )
    p.add_argument("--language", default=None, help="Equality match on language code.")
    _stream_filter_args(p)
    p.set_defaults(func=_handle_pick_stream)


def _add_channel_info(sub: argparse._SubParsersAction) -> None:
    """Register the ``channel-info`` subcommand: channel-level snapshot (subs, total views, video count).

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser(
        "channel-info", help="Channel-level snapshot (subs, total views, video count)."
    )
    p.add_argument("--url", required=True, help="Channel / user page URL.")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=_handle_channel_info)


def _add_channel_videos(sub: argparse._SubParsersAction) -> None:
    """Register the ``channel-videos`` subcommand: list channel videos with normalised engagement metadata.

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser(
        "channel-videos",
        help="List channel videos with normalised engagement metadata.",
    )
    p.add_argument("--url", required=True, help="Channel / user page URL.")
    p.add_argument(
        "--max-videos",
        type=int,
        dest="max_videos",
        default=200,
        help="Cap on number of videos to fetch (default 200).",
    )
    p.add_argument(
        "--no-shorts",
        dest="include_shorts",
        action="store_false",
        default=True,
        help="Exclude Shorts / vertical clips.",
    )
    p.add_argument(
        "--include-lives",
        dest="include_lives",
        action="store_true",
        default=False,
        help="Include live streams (default: skip).",
    )
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=_handle_channel_videos)


def _add_engagement(sub: argparse._SubParsersAction) -> None:
    """Register the ``engagement`` subcommand: single-video engagement snapshot.

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser("engagement", help="Single-video engagement snapshot.")
    p.add_argument("--url", required=True, help="Video URL.")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=_handle_engagement)


def _add_engagement_batch(sub: argparse._SubParsersAction) -> None:
    """Register the ``engagement-batch`` subcommand: multi-URL engagement snapshot (tolerant).

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser("engagement-batch", help="Multi-URL engagement snapshot (tolerant).")
    p.add_argument("--urls", nargs="+", required=True, help="One or more video URLs.")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=_handle_engagement_batch)


def _add_subtitles(sub: argparse._SubParsersAction) -> None:
    """Register the ``subtitles`` subcommand: download subtitles (auto or manual) for a video.

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser("subtitles", help="Download subtitles (auto or manual) for a video.")
    p.add_argument("--url", required=True, help="Video URL.")
    p.add_argument(
        "--output-dir",
        required=True,
        dest="output_dir",
        help="Folder that receives the .vtt files.",
    )
    p.add_argument(
        "--langs", nargs="+", default=["fr", "en"], help="Language codes to try (default: fr en)."
    )
    p.add_argument(
        "--manual",
        dest="auto_only",
        action="store_false",
        default=True,
        help="Prefer manual subtitles over auto-generated ones.",
    )
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=_handle_subtitles)


def _add_comments(sub: argparse._SubParsersAction) -> None:
    """Register the ``comments`` subcommand: fetch top comments for a video.

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser("comments", help="Fetch top comments for a video.")
    p.add_argument("--url", required=True, help="Video URL.")
    p.add_argument("--max", type=int, default=100, help="Comment count cap (default 100).")
    p.add_argument(
        "--cookies-from-browser",
        dest="cookies_from_browser",
        default=None,
        help="Browser to pull cookies from (firefox / chrome / safari / …).",
    )
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=_handle_comments)


def _add_ytdlp_version(sub: argparse._SubParsersAction) -> None:
    """Register the ``ytdlp-version`` subcommand: print installed yt-dlp version; warn if stale.

    Parameters
    ----------
    sub : argparse._SubParsersAction
        The subparsers object to attach this subcommand to.

    Returns
    -------
    None
        The parser is mutated in place.
    """
    p = sub.add_parser("ytdlp-version", help="Print installed yt-dlp version; warn if stale.")
    p.add_argument(
        "--min-version",
        dest="min_version",
        default=None,
        help="Emit a warning to stderr if installed yt-dlp is older than this.",
    )
    p.set_defaults(func=_handle_ytdlp_version)


def build_parser() -> argparse.ArgumentParser:
    """
    Assemble the top-level ``youtube-helper`` argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Fully wired parser with every subcommand attached.
    """
    parser = argparse.ArgumentParser(
        prog="youtube-helper",
        description=(
            "YouTube Helper — yt-dlp-backed CLI for downloading video / audio / "
            "thumbnails, resolving direct media URLs, browsing stream catalogs, "
            "and pulling no-API engagement metadata across YouTube, Vimeo, "
            "DailyMotion, Twitch VOD, SoundCloud, and any yt-dlp-supported source."
        ),
    )
    # Every non-trivial CLI benefits from `--version`. Resolve it lazily to
    # avoid any issue with importlib.metadata edge cases.
    try:
        from importlib.metadata import version as _pkg_version

        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {_pkg_version('youtube-helper')}",
        )
    except Exception:  # pragma: no cover — never fatal
        pass

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    # Register every subcommand. Order matters for help output only.
    _add_metadata(subparsers)
    _add_valid(subparsers)
    _add_video(subparsers)
    _add_audio(subparsers)
    _add_thumbnail(subparsers)
    _add_resolve(subparsers)
    _add_list_streams(subparsers)
    _add_pick_stream(subparsers)
    _add_channel_info(subparsers)
    _add_channel_videos(subparsers)
    _add_engagement(subparsers)
    _add_engagement_batch(subparsers)
    _add_subtitles(subparsers)
    _add_comments(subparsers)
    _add_ytdlp_version(subparsers)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    Entry point invoked by ``youtube-helper`` (see ``[project.scripts]``).

    Parameters
    ----------
    argv : sequence of str, optional
        Arguments to parse. Defaults to ``sys.argv[1:]`` when None.

    Returns
    -------
    int
        Process exit code (``0`` on success).
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    # Every subparser sets ``func`` via ``set_defaults`` — no dispatch table
    # needed, argparse resolved it for us.
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
