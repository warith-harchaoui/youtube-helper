"""
YouTube Helper — download and metadata utilities.

Module summary
--------------
Utility functions to download videos, audio, and thumbnails from URLs
such as YouTube, Vimeo, or DailyMotion using ``yt-dlp``, plus the
post-processing steps (format conversion / merging via ffmpeg) needed to
land the result in the exact container / sample-rate the caller asked
for. It consumes a user-facing page URL and produces a file on disk (or,
for :func:`video_url_meta_data`, a plain metadata ``dict``).

Dependencies
------------
- ``yt-dlp``     : extraction and download engine.
- ``ffmpeg``     : media conversion (invoked via the helper packages).
- ``PIL``        : thumbnail format conversion.
- ``os_helper``  : filesystem / URL utilities.
- ``audio_helper`` : audio validation and conversion.
- ``video_helper`` : video validation and conversion.

Author
------
Project maintainers.
"""

from __future__ import annotations

import glob
import os
from collections.abc import Callable, Sequence
from typing import Any

import audio_helper as ah
import os_helper as osh
import video_helper as vh
import yt_dlp
from PIL import Image

# Fallback #1: a fully-populated, up-to-date desktop browser User-Agent (Chrome
# on Windows), used to look less like a bare script when the site rejects the
# lighter default UA. Overridable via YOUTUBE_HELPER_USER_AGENT.
_BROWSER_USER_AGENT = os.environ.get(
    "YOUTUBE_HELPER_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
)
_BROWSER_HEADERS = {
    "User-Agent": _BROWSER_USER_AGENT,
    "Accept-Language": "en-US,en;q=0.5",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Sec-Fetch-Mode": "navigate",
}

# Fallback #2: pull a real session's cookies straight from a local browser profile
# (yt-dlp's --cookies-from-browser mechanism). This is what actually clears YouTube's
# "Sign in to confirm you're not a bot" challenge in practice — a bare browser User-Agent
# does not, and neither does routing through Tor (exit nodes are themselves commonly
# flagged). Empty by default (opt-in: reading another app's cookie store is invasive
# enough that it should not happen silently); set YOUTUBE_HELPER_COOKIES_FROM_BROWSER to
# a yt-dlp-recognized browser name (chrome, firefox, edge, brave, opera, vivaldi, safari,
# whale, chromium) to enable it. Safari's cookie store additionally needs Full Disk Access
# granted to the calling process/terminal on macOS, or extraction raises "Operation not
# permitted" — Chrome/Firefox need no such grant.
_COOKIES_FROM_BROWSER = os.environ.get("YOUTUBE_HELPER_COOKIES_FROM_BROWSER", "").strip()

# Fallback #3 (last resort): route through a local Tor SOCKS proxy (socks5h resolves DNS
# through Tor too, avoiding leaks). Requires a Tor daemon running locally
# (e.g. `brew install tor && brew services start tor`). Overridable via
# YOUTUBE_HELPER_TOR_PROXY.
_TOR_PROXY = os.environ.get("YOUTUBE_HELPER_TOR_PROXY", "socks5h://127.0.0.1:9050")

# Fallback #2bis, tried BEFORE cookies and Tor because it costs nothing and touches nobody's
# private data: ask YouTube as a different client. YouTube serves several apps (web, mobile,
# TV, embedded player) and does not apply the same checks to all of them, so a video refused
# for one client often loads for another. This is the account-free lever the yt-dlp project
# itself recommends for "Sign in to confirm you're not a bot".
#
# The order below is measured, not guessed (RZ79EY6genM, a 1h42 episode, yt-dlp 2026.08.19):
#
#   client        formats  https-only  HLS  best <=720p non-HLS
#   web_embedded       35          31    0  itag 136, 720p, 0.32 GiB   <- cleanest
#   tv                  -           -    -  "page needs to be reloaded" that day
#   android_vr          5           1    0  itag 18, 360p only
#   visionos (default) 50          28   18  itag 136 exists, but HLS is mixed in
#   web / web_safari / ios          refused outright (they need a PO token)
#
# Two things fall out of that table. First, web_embedded answers when the defaults are
# refused. Second, it exposes NO HLS at all, which matters for speed: YouTube throttles
# fragmented HLS hard (measured at 75-300 KiB/s over 1507 fragments, versus ~2 MiB/s on a
# direct https format), so a client without HLS is also the fast one.
#
# web_embedded only works for videos the uploader allows to be embedded, hence the chain.
# Override with YOUTUBE_HELPER_PLAYER_CLIENTS (comma-separated, empty disables the rung).
_PLAYER_CLIENT_FALLBACKS = tuple(
    c.strip() for c in os.environ.get(
        "YOUTUBE_HELPER_PLAYER_CLIENTS", "web_embedded,tv,android_vr,mweb"
    ).split(",") if c.strip()
)

# Default ceiling on video height, as a string ("720") or empty for "whatever yt-dlp picks".
# Empty by default so existing callers keep getting best-available quality; set
# YOUTUBE_HELPER_MAX_HEIGHT, or pass max_height=, when the destination cannot take an
# arbitrarily large file. A real case: a FAT32 volume refuses anything over 4 GiB, and
# yt-dlp left to itself chose a premium stream that blew past it mid-write.
_MAX_HEIGHT = os.environ.get("YOUTUBE_HELPER_MAX_HEIGHT", "").strip()


def height_capped_format(max_height: int) -> str:
    """yt-dlp format selector for "no taller than *max_height*, and avoid HLS if possible".

    Non-HLS first on purpose. YouTube throttles fragmented HLS far more aggressively than a
    direct https format: on one measured episode, 75-300 KiB/s across 1507 fragments against
    ~2 MiB/s for the equivalent https stream. ``protocol^=http`` keeps ``https`` and
    ``http_dash_segments`` while excluding ``m3u8_native``.

    Every rung degrades gracefully: height-capped non-HLS, then height-capped anything, then
    best available, so a video that simply has no small format still downloads instead of
    failing with "Requested format is not available".

    Parameters
    ----------
    max_height : int
        Maximum video height in pixels, e.g. ``720``.

    Returns
    -------
    str
        A yt-dlp ``format`` string.
    """
    h = int(max_height)
    return (
        f"bv*[height<={h}][protocol^=http]+ba[protocol^=http]/"
        f"b[height<={h}][protocol^=http]/"
        f"bv*[height<={h}]+ba/b[height<={h}]/"
        "bv*+ba/b"
    )


def default_ytdlp_options(
    overwrites: bool = True,
    audio: bool = False,
    video: bool = False,
    cookie_dir: str | None = None,
    max_height: int | str | None = None,
    player_clients: Sequence[str] | None = None,
) -> dict:
    """
    Generate default yt-dlp options based on provided parameters.

    Parameters
    ----------
    overwrites : bool, optional
        Whether to overwrite existing files. Default is True.
    audio : bool, optional
        Whether to download audio only. Default is False.
    video : bool, optional
        Whether to download video only (overrides audio). Default is False.
    cookie_dir : str or None, optional
        Directory in which yt-dlp's session cookie jar is written. The download
        helpers pass their ``temporary_folder`` here so the jar disappears when
        the ``with`` block exits; when omitted it falls back to the system temp
        directory. It is *never* written to the current working directory.
    max_height : int or str or None, optional
        Cap the video height, e.g. ``720``. ``None`` falls back to the
        ``YOUTUBE_HELPER_MAX_HEIGHT`` environment variable, and if that is empty too,
        yt-dlp picks best-available as before. See :func:`height_capped_format` for why
        the generated selector also prefers non-HLS.
    player_clients : sequence of str or None, optional
        Ask YouTube as these clients instead of yt-dlp's defaults (``web_embedded``,
        ``tv``, ``android_vr``, ``mweb``, …). Mostly useful for pinning one explicitly;
        callers normally leave this alone and let the retry ladder try the clients in
        :data:`_PLAYER_CLIENT_FALLBACKS` on failure.

    Returns
    -------
    dict
        A dictionary of options for yt-dlp.

    Notes
    -----
    The function sets various options for yt-dlp. If `audio` is set to True,
    the format is set to download the best audio available. If `video` is set
    to True, it overrides the audio flag and downloads video+audio.
    """
    verbosity = 0
    if max_height is None and _MAX_HEIGHT:
        max_height = _MAX_HEIGHT
    options = {
        "quiet": verbosity == 0,
        "no_warnings": verbosity < 2,
        "verbose": verbosity >= 2,
        "progress_hooks": [lambda d: None],
        "debug_printtraffic": verbosity == 3,
        "include_ads": False,
        "forceurl": verbosity < 2,
        "overwrites": overwrites,
    }

    options.update(
        {
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
                "Accept-Language": "en-US,en;q=0.5",
            },
            # NOTE: do NOT force the generic extractor — it makes yt-dlp reject
            # youtube.com / vimeo / etc. as "Unsupported URL" on modern yt-dlp
            # (2025.07+). Let yt-dlp pick the correct site extractor.
        }
    )

    # Cookies. A user-supplied cookies file (Netscape format) takes precedence:
    # some environments — notably CI on datacenter IPs — need authenticated cookies,
    # or YouTube answers "Sign in to confirm you're not a bot". Point yt-dlp at it
    # via the ``YOUTUBE_HELPER_COOKIES`` environment variable. Otherwise keep only a
    # throwaway session jar inside the caller's ``temporary_folder`` (passed as
    # ``cookie_dir``, auto-removed on ``with`` exit); metadata-only calls without a
    # directory keep cookies in memory. Nothing is ever written to the CWD.
    cookies_file = os.environ.get("YOUTUBE_HELPER_COOKIES", "").strip()
    if cookies_file and osh.file_exists(cookies_file):
        options["cookiefile"] = cookies_file
    elif cookie_dir:
        now = osh.now_string(fmt="filename")
        options["cookiefile"] = osh.join(cookie_dir, f"{now}_ytdlp_cookie.txt")

    # Do NOT skip the player JS: modern yt-dlp needs it to decipher formats and to
    # negotiate a proof-of-origin (PO) token, without which YouTube answers "Sign in
    # to confirm you're not a bot" from datacenter IPs (e.g. CI runners).

    if audio:
        options["format"] = "bestaudio/best"

    if video:
        options["format"] = "bestvideo+bestaudio/best"

    # Height cap and client choice, applied last so they override the generic audio/video
    # defaults just set above. Both are plain yt-dlp options and they live here so that every
    # surface (library, CLI, API, MCP) inherits them from one place, instead of each one
    # hand-rolling its own format string.
    if max_height and not audio:
        options["format"] = height_capped_format(int(max_height))
    if player_clients:
        extractor_args = dict(options.get("extractor_args") or {})
        youtube_args = dict(extractor_args.get("youtube") or {})
        youtube_args["player_client"] = list(player_clients)
        extractor_args["youtube"] = youtube_args
        options["extractor_args"] = extractor_args

    return options


def _ytdlp_option_variants(options: dict) -> list[tuple[str, dict]]:
    """
    Build the ordered list of yt-dlp option variants to try in turn.

    1. the caller's options as-is
    2. the same options with a fully-populated browser User-Agent
    3. the same again, with cookies pulled from a local browser profile
       (only when :data:`_COOKIES_FROM_BROWSER` is set — see its docstring)
    4. the same again, routed through a local Tor SOCKS proxy

    These are the default fallback mechanisms used whenever the normal approach gets
    blocked (rate-limiting, bot checks, IP bans, ...). In practice #3 is the one that
    actually clears YouTube's "Sign in to confirm you're not a bot" challenge; #4 is
    kept as the last resort for environments with no logged-in browser to borrow
    cookies from (Tor exit nodes are themselves commonly flagged by YouTube, so it is
    not a reliable primary fix for that particular challenge).
    """
    browser_headers = dict(options.get("http_headers", {}))
    browser_headers.update(_BROWSER_HEADERS)
    with_browser_ua = {**options, "http_headers": browser_headers}

    variants = [("default options", options), ("a browser User-Agent", with_browser_ua)]

    # Client rungs come before cookies and Tor deliberately. Asking YouTube as a different
    # client needs no account, reads nobody's browser profile, and routes through no third
    # party, so it is the cheapest thing to try and the one that works most often. Only if
    # every client is refused do we escalate to borrowing cookies, then to Tor.
    # Skipped entirely when the caller already pinned a client explicitly.
    already_pinned = bool((options.get("extractor_args") or {}).get("youtube", {}).get("player_client"))
    if not already_pinned:
        for client in _PLAYER_CLIENT_FALLBACKS:
            variants.append((
                f"player_client={client}",
                {**with_browser_ua,
                 "extractor_args": {**(with_browser_ua.get("extractor_args") or {}),
                                    "youtube": {"player_client": [client]}}},
            ))

    if _COOKIES_FROM_BROWSER:
        with_cookies = {**with_browser_ua, "cookiesfrombrowser": (_COOKIES_FROM_BROWSER,)}
        variants.append((f"cookies from {_COOKIES_FROM_BROWSER}", with_cookies))

    variants.append(("Tor", {**with_browser_ua, "proxy": _TOR_PROXY}))

    return variants


def _run_ytdlp(
    options: dict,
    action: Callable[[yt_dlp.YoutubeDL], Any],
    *,
    on_attempt_start: Callable[[], None] | None = None,
) -> Any:
    """
    Run a yt-dlp action, falling back to a browser User-Agent then to Tor on failure.

    Parameters
    ----------
    options : dict
        Base yt-dlp options, as produced by :func:`default_ytdlp_options`.
    action : Callable[[yt_dlp.YoutubeDL], Any]
        Called with a live ``YoutubeDL`` instance; its return value is
        propagated back to the caller.
    on_attempt_start : Callable[[], None] or None, optional
        Called before every attempt, including the first. Download callers
        use this to purge any partial output left behind by a prior failed
        attempt (e.g. a ``.part`` file from a network drop mid-download) —
        without it, a stale leftover can outlive a successful retry and get
        picked up by the caller's own post-download file glob instead of the
        actual result. Metadata-only callers, which write nothing to disk,
        can omit it.

    Returns
    -------
    Any
        Whatever ``action`` returns on the first attempt that succeeds.

    Raises
    ------
    Exception
        The last error encountered, if every fallback also fails.
    """
    last_error: Exception | None = None
    variants = _ytdlp_option_variants(options)
    for attempt, (label, opts) in enumerate(variants):
        if on_attempt_start is not None:
            on_attempt_start()
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return action(ydl)
        except Exception as e:
            last_error = e
            if attempt + 1 < len(variants):
                next_label = variants[attempt + 1][0]
                osh.info(f"yt-dlp failed with {label}; retrying with {next_label}")
    raise last_error


def _aux_ytdlp_meta_data(url: str) -> dict | None:
    """
    Extract metadata from a video URL using yt-dlp.

    Parameters
    ----------
    url : str
        The URL of the video.

    Returns
    -------
    dict or None
        A dictionary containing the metadata if extraction is successful, None otherwise.

    Notes
    -----
    This function is intended for internal use to extract video metadata without
    downloading the actual content.
    """
    meta = None
    try:
        opt = default_ytdlp_options()
        meta = _run_ytdlp(opt, lambda ydl: ydl.extract_info(url, download=False))
    except Exception:
        pass
    return meta


def video_url_meta_data(url: str) -> dict:
    """
    Retrieve metadata from a video URL without downloading the video.

    Parameters
    ----------
    url : str
        The URL of the video.

    Returns
    -------
    dict
        A dictionary containing the video's metadata, including title and description.

    Notes
    -----
    The function checks for metadata extraction success, logs the title and
    a part of the description, and returns metadata.
    """
    assert osh.is_working_url(url), f"Invalid URL:\n\t{url}"

    res = {}
    meta = _aux_ytdlp_meta_data(url)
    assert meta is not None, f"yt-dlp is not working on that url:\n{url}"

    res.update(meta)
    title = meta.get("title")
    res["title"] = title
    # Some extractors (live streams, certain Vimeo/DailyMotion pages, ...)
    # omit the description entirely, so yt-dlp hands back None here. Coalesce
    # to "" before splitting — without this, videos with no description
    # crash every caller that relies on this function for the default output
    # filename (download_thumbnail / download_audio / download_video).
    description = meta.get("description") or ""
    res["description"] = description

    t = description.split("\n")
    t = "\n".join(t[:3])

    osh.info(f"Title:\n\t{title}")
    osh.info(f"Description (beginning):\n\t{t}")

    return res


def is_valid_video_url(url: str) -> bool:
    """
    Check if a given URL is a valid video URL using yt-dlp.

    Parameters
    ----------
    url : str
        The URL to check.

    Returns
    -------
    bool
        True if the URL is valid, False otherwise.

    Notes
    -----
    This function extracts metadata from the URL using yt-dlp to determine
    if the URL points to a valid video.
    """
    if osh.emptystring(url):
        osh.info("Video url is empty")
        return False

    if not (osh.is_working_url(url)):
        osh.info(f"Video URL is invalid (URL not working):\n\t{url}")
        return False

    meta = _aux_ytdlp_meta_data(url)
    if meta:
        osh.info(f"yt-dlp metadata extraction is successful for {url}")
        return True

    osh.info(f"yt-dlp metadata extraction failed for {url}")
    return False


def download_thumbnail(url: str, output_path: str = None) -> str:
    """
    Download the thumbnail of a video from a given URL and save it to the specified output path.

    Parameters
    ----------
    url : str
        The URL of the video from which to download the thumbnail.
    output_path : str, optional
        The path where the downloaded thumbnail should be saved.

    Returns
    -------
    str
        Path of downloaded thumbnail

    Notes
    -----
    This function uses yt-dlp to download the thumbnail of the specified video. It handles
    different output formats and ensures the thumbnail is saved in the desired format using PIL.
    """
    if osh.emptystring(output_path):
        metadata = video_url_meta_data(url)
        title = metadata["title"]
        basename = osh.asciistring(title)
        output_path = f"{basename}.png"
        output_path = osh.relative2absolute_path(output_path)

    if osh.file_exists(output_path):
        osh.info(f"Thumbnail already exists:\n\t{output_path}")
        return output_path

    osh.info(f"Downloading thumbnail of video:\n\t{url} to:\n\t{output_path}")

    # Extract folder, basename, and thumbnail format from the output path
    folder, basename, thumb_format = osh.folder_name_ext(osh.relative2absolute_path(output_path))
    osh.make_directory(folder)

    # Download the thumbnail to a temporary folder
    with osh.temporary_folder() as temp_directory:
        o = osh.join(temp_directory, basename)

        # Set yt-dlp options to download only the thumbnail
        opts = default_ytdlp_options(cookie_dir=temp_directory)
        opts["skip_download"] = True
        opts["writethumbnail"] = True
        opts["outtmpl"] = f"{o}.%(ext)s"

        # Download the thumbnail using yt-dlp
        _run_ytdlp(opts, lambda ydl: ydl.download([url]))

        # Find the downloaded thumbnail file
        thumb_file = glob.glob(f"{o}.*")
        assert len(thumb_file) > 0, f"Failed to download thumbnail of video {url}"
        thumb_file = osh.relative2absolute_path(thumb_file[0])

        # Check if the thumbnail needs to be converted to the desired format
        _, _, ext = osh.folder_name_ext(thumb_file)
        if ext.lower() != thumb_format.lower():
            # Read the image with PIL and save it in the desired format
            try:
                img = Image.open(thumb_file)
                img.save(output_path)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to save thumbnail to {output_path} for {url}: {e}"
                ) from e
        else:
            # Move the thumbnail file to the desired output path
            osh.copyfile(thumb_file, output_path)

    osh.checkfile(output_path, msg=f"Failed to download thumbnail to {output_path} from {url}")
    osh.info(f"Successful download thumbnail to {output_path} from {url}")

    return output_path


def download_audio(url: str, output_path: str = None, target_sample_rate: int = 44100) -> str:
    """
    Download the best quality audio from a given URL and save it to the specified output path.

    Parameters
    ----------
    url : str
        The URL of the video to download the audio from.
    output_path : str, optional
        The path where the downloaded audio should be saved.
    target_sample_rate : int, optional
        The sample rate of the output audio file. Defaults to 44100.

    Returns
    -------
    str
        Path of downloaded audio

    Notes
    -----
    This function uses yt-dlp to download the best quality audio from the given URL. It handles
    different output formats and ensures the audio is saved with the desired sample rate using a
    conversion step if necessary.
    """
    if osh.emptystring(output_path):
        metadata = video_url_meta_data(url)
        title = metadata["title"]
        basename = osh.asciistring(title)
        output_path = f"{basename}.mp3"
        output_path = osh.relative2absolute_path(output_path)

    if osh.file_exists(output_path) and ah.is_valid_audio_file(output_path):
        osh.info(f"Audio already exists:\n\t{output_path}")
        return output_path

    osh.info(f"Downloading audio from:\n\t{url} to:\n\t{output_path}")
    assert osh.is_working_url(url), f"Invalid video URL:\n\t{url}"

    # Extract folder, basename, and format from the output path
    folder, basename, audio_format = osh.folder_name_ext(osh.relative2absolute_path(output_path))
    osh.make_directory(folder)

    with osh.temporary_folder() as temp_directory:
        o = osh.join(temp_directory, basename)

        # Set yt-dlp options to download the best quality audio
        opts = default_ytdlp_options(audio=True, cookie_dir=temp_directory)
        opts["outtmpl"] = f"{o}.%(ext)s"

        # Download the audio using yt-dlp. Purge any partial output before each
        # attempt (including the first) — a failed attempt can leave a `.part`
        # file behind (e.g. a network drop mid-download, not just a block), and
        # without cleanup a stale leftover from attempt N could still be sitting
        # next to attempt N+1's real output when the glob below runs, making the
        # picked file order-dependent instead of deterministic.
        _run_ytdlp(
            opts,
            lambda ydl: ydl.download([url]),
            on_attempt_start=lambda: osh.remove_files(glob.glob(f"{o}.*")),
        )

        # Find the downloaded audio file
        received_file = glob.glob(f"{o}.*")
        assert len(received_file) > 0, f"Failed to download audio from {url}"
        received_file = osh.relative2absolute_path(received_file[0])
        assert ah.is_valid_audio_file(received_file), f"Invalid audio file: {received_file}"

        # Convert to the desired format if necessary
        _, _, ext = osh.folder_name_ext(received_file)
        if ext.lower() != audio_format.lower():
            ah.sound_converter(received_file, output_path, freq=target_sample_rate)
        else:
            osh.copyfile(received_file, output_path)

    assert ah.is_valid_audio_file(output_path), f"Failed to save audio to {output_path} for {url}"
    osh.info(f"Audio saved to {output_path}")

    return output_path


def download_video(url: str, output_path: str = None, max_height: int | str | None = None) -> str:
    """
    Download video from a given URL and save it to the specified output path.

    Parameters
    ----------
    url : str
        The URL of the video to be downloaded.
    output_path : str, optional
        The path where the downloaded video should be saved.
    max_height : int or str or None, optional
        Cap the video height, e.g. ``720``. ``None`` falls back to
        ``YOUTUBE_HELPER_MAX_HEIGHT``, and if that is empty too, yt-dlp picks
        best-available as it always has. Worth setting when the destination has a
        size limit, or when speed matters more than resolution: the capped selector
        also prefers direct https formats over fragmented HLS, which YouTube
        throttles heavily (see :func:`height_capped_format`).

    Returns
    -------
    str
        Path of downloaded video

    Notes
    -----
    This function downloads the best quality video from the given URL using yt-dlp. It handles
    different formats and ensures that the video is saved in the desired format using ffmpeg
    if necessary. The function checks whether the downloaded video is valid and converts
    it to the specified output format if needed.
    """
    if osh.emptystring(output_path):
        metadata = video_url_meta_data(url)
        title = metadata["title"]
        basename = osh.asciistring(title)
        output_path = f"{basename}.mp4"
        output_path = osh.relative2absolute_path(output_path)

    if osh.file_exists(output_path) and vh.is_valid_video_file(output_path):
        osh.info(f"Video already exists:\n\t{output_path}")
        return output_path

    osh.info(f"Downloading video from:\n\t{url} to:\n\t{output_path}")

    assert osh.is_working_url(url), f"Invalid video URL:\n\t{url}"

    # Extract folder, basename, and video format from the output path
    folder, basename, video_format = osh.folder_name_ext(osh.relative2absolute_path(output_path))
    osh.make_directory(folder)

    with osh.temporary_folder() as temp_directory:
        o = osh.join([temp_directory, basename])

        # Set yt-dlp options to download the best quality video
        opts = default_ytdlp_options(video=True, cookie_dir=temp_directory, max_height=max_height)
        opts["outtmpl"] = f"{o}.%(ext)s"

        # Download the best quality video using yt-dlp. Purge any partial output
        # before each attempt (including the first) — see the matching comment
        # in download_audio for why this matters once a retry can follow a
        # partially-completed attempt.
        _run_ytdlp(
            opts,
            lambda ydl: ydl.download([url]),
            on_attempt_start=lambda: osh.remove_files(glob.glob(f"{o}.*")),
        )

        # Find the downloaded video file
        received_file = glob.glob(f"{o}.*")
        assert len(received_file) > 0, f"Failed to download video from {url}"
        received_file = received_file[0]
        received_file = osh.relative2absolute_path(received_file)

        # Validate the downloaded video file
        assert vh.is_valid_video_file(received_file), f"Invalid video file downloaded from {url}"

        # Extract the extension of the downloaded file
        _, _, ext = osh.folder_name_ext(received_file)

        # If the video format differs, convert the video to the desired format
        if ext.lower() != video_format.lower():
            vh.video_converter(received_file, output_path)
        else:
            osh.copyfile(received_file, output_path)

    # Validate that the video was saved successfully
    osh.checkfile(
        output_path,
        msg=f"Failed to save video to {output_path} from {url}",
    )

    osh.info(f"Successfully downloaded video from\n\t{url} to\n\t{output_path}")

    return output_path
