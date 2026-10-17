"""
Unit tests for the yt-dlp download fallback chain in ``youtube_helper.main``.

These tests never touch the network: ``yt_dlp.YoutubeDL`` is replaced with a
fake that records the options it was built with and raises/succeeds on
command, so the retry ordering (normal -> browser User-Agent -> Tor) can be
verified in isolation.

The chain is asserted by INVARIANT (what comes first, what comes last, which rung
appears when configured) rather than by a fixed length: rungs get added over time, and a
hard-coded count makes every such addition look like a regression.
"""

from __future__ import annotations

import pytest

import youtube_helper.branding as b
import youtube_helper.main as m


def _fake_ydl_class(seen_opts: list, fail_count: int):
    """Build a fake ``YoutubeDL`` context manager that records ``opts``."""

    class _FakeYDL:
        def __init__(self, opts):
            seen_opts.append(opts)

        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            return False

    return _FakeYDL


def _counting_action(fail_count: int):
    calls = {"n": 0}

    def action(_ydl):
        calls["n"] += 1
        if calls["n"] <= fail_count:
            raise RuntimeError(f"boom {calls['n']}")
        return "success"

    return action


def test_option_variants_order_and_shape():
    base = m.default_ytdlp_options()
    variants = m._ytdlp_option_variants(base)

    labels = [label for label, _ in variants]
    (_, normal), (_, browser_ua), (_, tor) = variants[0], variants[1], variants[-1]

    # The caller's own options are tried untouched first.
    assert labels[0] == "default options"
    assert normal is base
    assert "proxy" not in normal

    # Then the same options with a real browser User-Agent.
    assert labels[1] == "a browser User-Agent"
    assert browser_ua["http_headers"]["User-Agent"] == m._BROWSER_USER_AGENT
    assert "proxy" not in browser_ua

    # Tor stays LAST: it is the slowest rung and its exit nodes are themselves often
    # flagged, so nothing should ever be tried after it.
    assert labels[-1] == "Tor"
    assert tor["http_headers"]["User-Agent"] == m._BROWSER_USER_AGENT
    assert tor["proxy"] == m._TOR_PROXY

    # No YOUTUBE_HELPER_COOKIES_FROM_BROWSER in the test environment -> no cookies rung.
    assert not any(label.startswith("cookies from") for label in labels)


def test_option_variants_try_other_player_clients_before_cookies_and_tor():
    """Asking YouTube as another client is free and reads nobody's data, so it comes first.

    This is the account-free lever for "Sign in to confirm you're not a bot": YouTube does
    not apply the same checks to every client, so a video refused for the default client
    often loads for web_embedded or tv. Borrowing browser cookies works too but reads
    another app's private store, and Tor is slow and frequently flagged, so both must stay
    behind the client rungs.
    """
    variants = m._ytdlp_option_variants(m.default_ytdlp_options())
    labels = [label for label, _ in variants]

    client_rungs = [i for i, label in enumerate(labels) if label.startswith("player_client=")]
    assert client_rungs, "the client fallbacks should be tried"
    assert [labels[i] for i in client_rungs] == [
        f"player_client={c}" for c in m._PLAYER_CLIENT_FALLBACKS
    ]
    assert max(client_rungs) < labels.index("Tor")

    _, first_client = variants[client_rungs[0]]
    assert first_client["extractor_args"]["youtube"]["player_client"] == [
        m._PLAYER_CLIENT_FALLBACKS[0]
    ]
    # A client rung keeps the browser User-Agent won at the previous rung, and adds no proxy.
    assert first_client["http_headers"]["User-Agent"] == m._BROWSER_USER_AGENT
    assert "proxy" not in first_client


def test_option_variants_respect_a_client_the_caller_pinned():
    """A caller who named a client meant it; the ladder must not silently try others."""
    base = m.default_ytdlp_options(player_clients=["tv"])
    labels = [label for label, _ in m._ytdlp_option_variants(base)]
    assert not any(label.startswith("player_client=") for label in labels)


def test_option_variants_include_cookies_tier_when_configured(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(m, "_COOKIES_FROM_BROWSER", "chrome")
    base = m.default_ytdlp_options()
    variants = m._ytdlp_option_variants(base)

    labels = [label for label, _ in variants]
    assert "cookies from chrome" in labels
    # Cookies sit after the free client rungs and before the slow Tor one.
    assert labels.index("cookies from chrome") > max(
        i for i, label in enumerate(labels) if label.startswith("player_client=")
    )
    assert labels.index("cookies from chrome") < labels.index("Tor")

    _, cookies_opts = variants[labels.index("cookies from chrome")]
    assert cookies_opts["cookiesfrombrowser"] == ("chrome",)
    assert "proxy" not in cookies_opts

    _, tor_opts = variants[-1]
    assert tor_opts["proxy"] == m._TOR_PROXY


def test_run_ytdlp_succeeds_on_first_attempt(monkeypatch: pytest.MonkeyPatch):
    seen_opts: list = []
    monkeypatch.setattr(m.yt_dlp, "YoutubeDL", _fake_ydl_class(seen_opts, 0))

    result = m._run_ytdlp(m.default_ytdlp_options(), _counting_action(fail_count=0))

    assert result == "success"
    assert len(seen_opts) == 1
    assert "proxy" not in seen_opts[0]


def test_run_ytdlp_falls_back_to_browser_user_agent(monkeypatch: pytest.MonkeyPatch):
    seen_opts: list = []
    monkeypatch.setattr(m.yt_dlp, "YoutubeDL", _fake_ydl_class(seen_opts, 1))

    result = m._run_ytdlp(m.default_ytdlp_options(), _counting_action(fail_count=1))

    assert result == "success"
    assert len(seen_opts) == 2
    assert seen_opts[1]["http_headers"]["User-Agent"] == m._BROWSER_USER_AGENT
    assert "proxy" not in seen_opts[1]


def test_run_ytdlp_falls_back_all_the_way_to_tor(monkeypatch: pytest.MonkeyPatch):
    """Every rung but the last fails -> the last attempt is Tor, and it is reached."""
    rungs = len(m._ytdlp_option_variants(m.default_ytdlp_options()))
    seen_opts: list = []
    monkeypatch.setattr(m.yt_dlp, "YoutubeDL", _fake_ydl_class(seen_opts, rungs - 1))

    result = m._run_ytdlp(m.default_ytdlp_options(), _counting_action(fail_count=rungs - 1))

    assert result == "success"
    assert len(seen_opts) == rungs
    assert seen_opts[-1]["proxy"] == m._TOR_PROXY
    assert seen_opts[-1]["http_headers"]["User-Agent"] == m._BROWSER_USER_AGENT


def test_run_ytdlp_raises_last_error_when_all_fail(monkeypatch: pytest.MonkeyPatch):
    rungs = len(m._ytdlp_option_variants(m.default_ytdlp_options()))
    seen_opts: list = []
    monkeypatch.setattr(m.yt_dlp, "YoutubeDL", _fake_ydl_class(seen_opts, rungs))

    with pytest.raises(RuntimeError, match=f"boom {rungs}"):
        m._run_ytdlp(m.default_ytdlp_options(), _counting_action(fail_count=rungs))

    assert len(seen_opts) == rungs


def test_run_ytdlp_calls_on_attempt_start_before_every_attempt(
    monkeypatch: pytest.MonkeyPatch,
):
    # Download callers pass on_attempt_start to purge a stale partial file
    # (e.g. a .part left by a network drop mid-download) before the next
    # attempt -- without it, a leftover from a failed attempt could sit next
    # to a later successful attempt's real output and get picked up instead,
    # since the caller's own post-download glob can't tell them apart.
    seen_opts: list = []
    monkeypatch.setattr(m.yt_dlp, "YoutubeDL", _fake_ydl_class(seen_opts, 2))
    starts = {"n": 0}

    result = m._run_ytdlp(
        m.default_ytdlp_options(),
        _counting_action(fail_count=2),
        on_attempt_start=lambda: starts.__setitem__("n", starts["n"] + 1),
    )

    assert result == "success"
    assert starts["n"] == 3  # once before each of the 3 attempts, including the first


def test_download_audio_purges_a_stale_partial_file_before_the_retry_succeeds(
    monkeypatch: pytest.MonkeyPatch, tmp_path
):
    # Reproduces the bug directly: attempt 1 leaves a stray "<base>.part" file
    # in the temp dir before failing; attempt 2 (the browser-UA fallback)
    # succeeds and writes the real "<base>.mp3". Without on_attempt_start
    # purging the stale file first, the post-download glob(f"{o}.*") could
    # return both files in either order -- received_file[0] would then be
    # non-deterministic instead of always the real download.
    import os_helper as osh

    import youtube_helper.main as ym

    monkeypatch.setattr(ym, "video_url_meta_data", lambda url: {"title": "clip"})
    monkeypatch.setattr(osh, "is_working_url", lambda url: True)
    monkeypatch.setattr(osh, "temporary_folder", lambda: _FixedTempDir(tmp_path))

    calls = {"n": 0}

    def _fake_download(ydl_self, urls):
        calls["n"] += 1
        # output_path's basename ("out") is what download_audio's outtmpl uses.
        base = str(tmp_path / "out")
        if calls["n"] == 1:
            open(f"{base}.mp3.part", "w").close()  # stray leftover from a failed attempt
            raise RuntimeError("network drop mid-download")
        open(f"{base}.mp3", "w").close()  # the real, successful download

    monkeypatch.setattr(ym.yt_dlp.YoutubeDL, "download", _fake_download)
    monkeypatch.setattr(ym.ah, "is_valid_audio_file", lambda path: path.endswith(".mp3"))
    monkeypatch.setattr(ym.osh, "copyfile", lambda src, dst: None)

    output_path = str(tmp_path / "out.mp3")
    result = ym.download_audio("https://example.com/watch?v=x", output_path=output_path)

    assert result == output_path
    assert calls["n"] == 2


def test_video_url_meta_data_handles_missing_description(
    monkeypatch: pytest.MonkeyPatch,
):
    # Regression test: some extractors (live streams, certain Vimeo /
    # DailyMotion pages, ...) omit "description" entirely, so yt-dlp's info
    # dict carries it as None rather than "". video_url_meta_data used to
    # call `description.split("\n")` unconditionally, which raised
    # AttributeError on any such video -- and since download_thumbnail /
    # download_audio / download_video all call this function to build their
    # default output filename, a missing description broke every one of
    # them whenever the caller omitted output_path.
    import os_helper as osh

    monkeypatch.setattr(osh, "is_working_url", lambda url: True)
    monkeypatch.setattr(
        m,
        "_aux_ytdlp_meta_data",
        lambda url: {"title": "Live stream with no description", "description": None},
    )

    meta = m.video_url_meta_data("https://example.com/watch?v=live")

    assert meta["title"] == "Live stream with no description"
    assert meta["description"] == ""


class _FixedTempDir:
    """A ``with``-able stand-in for ``osh.temporary_folder()`` that reuses a
    fixed, already-existing directory instead of creating/removing a fresh
    one, so the test can assert on files left inside it."""

    def __init__(self, path):
        self._path = str(path)

    def __enter__(self):
        return self._path

    def __exit__(self, *exc_info):
        return False


# ---------------------------------------------------------------------------
# Channel-tab expansion — pure URL work, no network
#
# A channel root used to be walked directly. Under ``extract_flat`` YouTube
# answers it with the channel's own tabs: playlist entries carrying the
# channel id and no ``url``, which the per-video pass then skipped one by one,
# so ``channel_videos`` returned ``[]`` without ever raising. Silence is what
# made it dangerous — the retry chain above only reacts to exceptions.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "root",
    [
        "https://www.youtube.com/@BlenderOfficial",
        "https://www.youtube.com/@BlenderOfficial/",
        "http://youtube.com/@BlenderOfficial",
        "https://www.youtube.com/channel/UCSMOQeBJ2RAnuFungnQOxLg",
        "https://www.youtube.com/c/Blender",
        "https://www.youtube.com/user/BlenderFoundation",
    ],
)
def test_a_channel_root_is_expanded_to_its_videos_tab(root):
    """Every spelling of a bare channel URL resolves to the long-form tab."""
    urls = b._channel_listing_urls(root, include_shorts=False, include_lives=False)
    assert len(urls) == 1
    assert urls[0].endswith("/videos")
    assert urls[0].startswith("http")


def test_the_requested_tabs_are_the_ones_walked():
    """Shorts and past live streams are only fetched when asked for."""
    root = "https://www.youtube.com/@BlenderOfficial"
    assert b._channel_listing_urls(root, False, False) == [f"{root}/videos"]
    assert b._channel_listing_urls(root, True, False) == [
        f"{root}/videos",
        f"{root}/shorts",
    ]
    assert b._channel_listing_urls(root, True, True) == [
        f"{root}/videos",
        f"{root}/shorts",
        f"{root}/streams",
    ]


@pytest.mark.parametrize(
    "already_specific",
    [
        "https://www.youtube.com/@BlenderOfficial/videos",
        "https://www.youtube.com/@BlenderOfficial/shorts",
        "https://www.youtube.com/playlist?list=PL6B3937A5D230E335",
        "https://vimeo.com/blender",
        "https://www.dailymotion.com/blender",
    ],
)
def test_anything_already_specific_is_left_alone(already_specific):
    """Tabs, playlists and non-YouTube creator pages are walkable as they are."""
    assert b._channel_listing_urls(already_specific, True, True) == [already_specific]
