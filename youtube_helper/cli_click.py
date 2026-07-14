"""
YouTube Helper — click-based command-line interface.

Twin of :mod:`youtube_helper.cli_argparse`: same public surface (identical
subcommand names, identical flag semantics), but implemented with
:mod:`click` so users who already have a click-native shell setup
(bash / zsh completion via ``click.shell_completion``, colored `--help`,
nested command groups) can plug it in without friction. Installed as
the ``youtube-helper-click`` entry point in ``pyproject.toml``.

Design notes
------------
- Subcommands mirror ``youtube-helper`` (the argparse twin) so both CLIs
  can be introspected identically by higher layers (FastAPI, MCP).
- Flags reuse the argparse names (``--url`` / ``--output`` / …) rather
  than the more idiomatic click positional style — consistency across
  the two CLIs beats micro-idiomaticity here.
- Errors from the library propagate unchanged; click handles the
  formatting.

Usage Example
-------------
>>> #   youtube-helper-click metadata     --url https://www.youtube.com/watch?v=YE7VzlLtp-4
>>> #   youtube-helper-click audio        --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --output out.mp3
>>> #   youtube-helper-click resolve      --url https://www.youtube.com/watch?v=YE7VzlLtp-4 --prefer audio
>>> #   youtube-helper-click channel-info --url https://www.youtube.com/@blender

Author
------
Warith Harchaoui, Ph.D. — https://linkedin.com/in/warith-harchaoui/
"""

from __future__ import annotations

import json

try:
    import click
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The click CLI requires the [cli] extra. Install with: pip install 'youtube-helper[cli]'"
    ) from exc

# Same underlying functions as the argparse twin — one source of truth.
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


def _dumps(obj: object) -> str:
    """JSON-encode with a safe default so odd yt-dlp types (bytes, sets) still print."""
    return json.dumps(obj, indent=2, default=str, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Top-level group
# ---------------------------------------------------------------------------


@click.group(
    context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 100},
)
@click.version_option(package_name="youtube-helper", prog_name="youtube-helper-click")
def cli() -> None:
    """YouTube Helper — click twin of the argparse CLI. Same subcommands."""
    # Nothing to do at the group level — every subcommand carries its
    # own arguments and side effects.


# ---------------------------------------------------------------------------
# metadata
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--url", required=True, help="Video URL.")
def metadata(url: str) -> None:
    """Dump yt-dlp metadata for a video URL as JSON."""
    click.echo(_dumps(video_url_meta_data(url)))


# ---------------------------------------------------------------------------
# valid
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--url", required=True, help="Video URL.")
def valid(url: str) -> None:
    """Check whether a URL is a valid video URL for yt-dlp (exit code encodes result)."""
    ok = is_valid_video_url(url)
    click.echo("true" if ok else "false")
    if not ok:
        raise click.exceptions.Exit(1)


# ---------------------------------------------------------------------------
# video
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--url", required=True, help="Video URL.")
@click.option("--output", type=click.Path(), default=None, help="Output path (auto if omitted).")
def video(url: str, output: str | None) -> None:
    """Download the video (best video + audio) to disk."""
    click.echo(download_video(url=url, output_path=output))


# ---------------------------------------------------------------------------
# audio
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--url", required=True, help="Video URL.")
@click.option("--output", type=click.Path(), default=None, help="Output path (auto if omitted).")
@click.option(
    "--sample-rate",
    type=int,
    default=44100,
    show_default=True,
    help="Target sample rate for the output audio.",
)
def audio(url: str, output: str | None, sample_rate: int) -> None:
    """Download only the audio track to disk."""
    click.echo(download_audio(url=url, output_path=output, target_sample_rate=sample_rate))


# ---------------------------------------------------------------------------
# thumbnail
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--url", required=True, help="Video URL.")
@click.option("--output", type=click.Path(), default=None, help="Output path (auto if omitted).")
def thumbnail(url: str, output: str | None) -> None:
    """Download the video's thumbnail to disk."""
    click.echo(download_thumbnail(url=url, output_path=output))


# ---------------------------------------------------------------------------
# resolve
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--url", required=True, help="Video URL.")
@click.option("--prefer", type=click.Choice(["audio", "video"]), default="audio", show_default=True)
@click.option(
    "--live",
    type=click.Choice(["auto", "force_live", "force_vod"]),
    default="auto",
    show_default=True,
)
def resolve(url: str, prefer: str, live: str) -> None:
    """Resolve a URL to a direct ffmpeg-ready media URL (audio or video)."""
    click.echo(_dumps(resolve_direct_url(url=url, prefer=prefer, live=live)))


# ---------------------------------------------------------------------------
# list-streams
# ---------------------------------------------------------------------------


@cli.command("list-streams")
@click.option("--url", required=True, help="Video URL.")
@click.option("--include-video-only/--no-video-only", default=True, show_default=True)
@click.option("--include-combined/--no-combined", default=True, show_default=True)
@click.option(
    "--cookies-from-browser",
    default=None,
    help="Browser to pull cookies from (firefox / chrome / safari / …).",
)
@click.option("--verbose", is_flag=True, default=False)
def list_streams(
    url: str,
    include_video_only: bool,
    include_combined: bool,
    cookies_from_browser: str | None,
    verbose: bool,
) -> None:
    """List every video format yt-dlp finds for a URL."""
    click.echo(
        _dumps(
            list_video_streams(
                url=url,
                include_video_only=include_video_only,
                include_combined=include_combined,
                cookies_from_browser=cookies_from_browser,
                verbose=verbose,
            )
        )
    )


# ---------------------------------------------------------------------------
# pick-stream
# ---------------------------------------------------------------------------


@cli.command("pick-stream")
@click.option("--url", required=True, help="Video URL.")
@click.option("--prefer-codec", default=None, help="Substring match on vcodec (h264 / vp9 / av1).")
@click.option("--prefer-format", default=None, help="Equality match on ext (mp4 / webm).")
@click.option("--max-fps", type=float, default=None, help="Drop formats with fps > max-fps.")
@click.option("--language", default=None, help="Equality match on language code.")
@click.option("--include-video-only/--no-video-only", default=True, show_default=True)
@click.option("--include-combined/--no-combined", default=True, show_default=True)
@click.option("--cookies-from-browser", default=None)
@click.option("--verbose", is_flag=True, default=False)
def pick_stream(
    url: str,
    prefer_codec: str | None,
    prefer_format: str | None,
    max_fps: float | None,
    language: str | None,
    include_video_only: bool,
    include_combined: bool,
    cookies_from_browser: str | None,
    verbose: bool,
) -> None:
    """Pick one best video stream matching the given constraints."""
    click.echo(
        _dumps(
            pick_video_stream(
                url=url,
                prefer_codec=prefer_codec,
                prefer_format=prefer_format,
                max_fps=max_fps,
                language=language,
                include_video_only=include_video_only,
                include_combined=include_combined,
                cookies_from_browser=cookies_from_browser,
                verbose=verbose,
            )
        )
    )


# ---------------------------------------------------------------------------
# channel-info
# ---------------------------------------------------------------------------


@cli.command("channel-info")
@click.option("--url", required=True, help="Channel / user page URL.")
@click.option("--verbose", is_flag=True, default=False)
def channel_info_cmd(url: str, verbose: bool) -> None:
    """Channel-level snapshot (subs, total views, video count)."""
    click.echo(_dumps(channel_info(url=url, verbose=verbose)))


# ---------------------------------------------------------------------------
# channel-videos
# ---------------------------------------------------------------------------


@cli.command("channel-videos")
@click.option("--url", required=True, help="Channel / user page URL.")
@click.option("--max-videos", type=int, default=200, show_default=True)
@click.option("--include-shorts/--no-shorts", default=True, show_default=True)
@click.option("--include-lives/--no-lives", default=False, show_default=True)
@click.option("--verbose", is_flag=True, default=False)
def channel_videos_cmd(
    url: str,
    max_videos: int,
    include_shorts: bool,
    include_lives: bool,
    verbose: bool,
) -> None:
    """List channel videos with normalised engagement metadata."""
    click.echo(
        _dumps(
            channel_videos(
                url=url,
                max_videos=max_videos,
                include_shorts=include_shorts,
                include_lives=include_lives,
                verbose=verbose,
            )
        )
    )


# ---------------------------------------------------------------------------
# engagement
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--url", required=True, help="Video URL.")
@click.option("--verbose", is_flag=True, default=False)
def engagement(url: str, verbose: bool) -> None:
    """Single-video engagement snapshot."""
    click.echo(_dumps(video_engagement(url=url, verbose=verbose)))


# ---------------------------------------------------------------------------
# engagement-batch
# ---------------------------------------------------------------------------


@cli.command("engagement-batch")
@click.option("--urls", multiple=True, required=True, help="Video URL (repeat --urls for each).")
@click.option("--verbose", is_flag=True, default=False)
def engagement_batch_cmd(urls: tuple[str, ...], verbose: bool) -> None:
    """Multi-URL engagement snapshot (tolerant of dead entries)."""
    click.echo(_dumps(engagement_batch(urls=list(urls), verbose=verbose)))


# ---------------------------------------------------------------------------
# subtitles
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--url", required=True, help="Video URL.")
@click.option(
    "--output-dir", required=True, type=click.Path(), help="Folder that receives the .vtt files."
)
@click.option(
    "--langs",
    multiple=True,
    default=("fr", "en"),
    show_default=True,
    help="Language code (repeat --langs for each).",
)
@click.option(
    "--auto-only/--manual",
    default=True,
    show_default=True,
    help="Prefer auto-generated subtitles (default) or manual ones.",
)
@click.option("--verbose", is_flag=True, default=False)
def subtitles(
    url: str, output_dir: str, langs: tuple[str, ...], auto_only: bool, verbose: bool
) -> None:
    """Download subtitles (auto or manual) for a video into a folder."""
    click.echo(
        _dumps(
            video_subtitles(
                url=url,
                output_dir=output_dir,
                langs=tuple(langs),
                auto_only=auto_only,
                verbose=verbose,
            )
        )
    )


# ---------------------------------------------------------------------------
# comments
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--url", required=True, help="Video URL.")
@click.option("--max", "max_count", type=int, default=100, show_default=True)
@click.option("--cookies-from-browser", default=None)
@click.option("--verbose", is_flag=True, default=False)
def comments(url: str, max_count: int, cookies_from_browser: str | None, verbose: bool) -> None:
    """Fetch top comments for a video."""
    click.echo(
        _dumps(
            video_comments(
                url=url,
                max_count=max_count,
                cookies_from_browser=cookies_from_browser,
                verbose=verbose,
            )
        )
    )


# ---------------------------------------------------------------------------
# ytdlp-version
# ---------------------------------------------------------------------------


@cli.command("ytdlp-version")
@click.option(
    "--min-version",
    default=None,
    help="Emit a warning to stderr if installed yt-dlp is older than this.",
)
def ytdlp_version(min_version: str | None) -> None:
    """Print installed yt-dlp version; warn if stale."""
    click.echo(ensure_recent_ytdlp(min_version=min_version))


if __name__ == "__main__":  # pragma: no cover
    cli()
