"""
Unit tests for the yt-dlp download fallback chain in ``youtube_helper.main``.

These tests never touch the network: ``yt_dlp.YoutubeDL`` is replaced with a
fake that records the options it was built with and raises/succeeds on
command, so the retry ordering (normal -> browser User-Agent -> Tor) can be
verified in isolation.
"""

from __future__ import annotations

import pytest

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

    assert len(variants) == 3
    normal, browser_ua, tor = variants

    assert normal is base
    assert "proxy" not in normal

    assert browser_ua["http_headers"]["User-Agent"] == m._BROWSER_USER_AGENT
    assert "proxy" not in browser_ua

    assert tor["http_headers"]["User-Agent"] == m._BROWSER_USER_AGENT
    assert tor["proxy"] == m._TOR_PROXY


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


def test_run_ytdlp_falls_back_to_tor(monkeypatch: pytest.MonkeyPatch):
    seen_opts: list = []
    monkeypatch.setattr(m.yt_dlp, "YoutubeDL", _fake_ydl_class(seen_opts, 2))

    result = m._run_ytdlp(m.default_ytdlp_options(), _counting_action(fail_count=2))

    assert result == "success"
    assert len(seen_opts) == 3
    assert seen_opts[2]["proxy"] == m._TOR_PROXY
    assert seen_opts[2]["http_headers"]["User-Agent"] == m._BROWSER_USER_AGENT


def test_run_ytdlp_raises_last_error_when_all_fail(monkeypatch: pytest.MonkeyPatch):
    seen_opts: list = []
    monkeypatch.setattr(m.yt_dlp, "YoutubeDL", _fake_ydl_class(seen_opts, 3))

    with pytest.raises(RuntimeError, match="boom 3"):
        m._run_ytdlp(m.default_ytdlp_options(), _counting_action(fail_count=3))

    assert len(seen_opts) == 3
