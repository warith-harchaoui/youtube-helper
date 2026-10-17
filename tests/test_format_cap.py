"""Tests for the height cap and the non-HLS preference in ``youtube_helper.main``.

No network: these only exercise the yt-dlp option dictionary and the format selector
string, which is where the behaviour lives.
"""

from __future__ import annotations

import pytest

import youtube_helper.main as m


def test_capped_selector_prefers_non_hls_first():
    """HLS is the throttled path, so it must only ever be a fallback.

    Measured on one 1h42 episode: 75-300 KiB/s across 1507 HLS fragments, against ~2 MiB/s
    for the equivalent direct https format. ``protocol^=http`` matches ``https`` and
    ``http_dash_segments`` but not ``m3u8_native``.
    """
    rungs = m.height_capped_format(720).split("/")
    assert all("protocol^=http" in r for r in rungs[:2])
    assert not any("protocol^=http" in r for r in rungs[2:])


def test_capped_selector_degrades_to_best_available():
    """A video with no small format must still download, not fail 'format not available'."""
    assert m.height_capped_format(720).split("/")[-1] == "b"
    assert "bv*+ba" in m.height_capped_format(720)


def test_capped_selector_honours_the_requested_height():
    assert m.height_capped_format(480).count("height<=480") == 4
    assert "height<=720" not in m.height_capped_format(480)


def test_video_options_apply_the_cap():
    opts = m.default_ytdlp_options(video=True, max_height=720)
    assert opts["format"] == m.height_capped_format(720)


def test_audio_options_ignore_the_cap():
    """A height cap on an audio-only download is meaningless and must not mangle the format."""
    assert m.default_ytdlp_options(audio=True, max_height=720)["format"] == "bestaudio/best"


def test_defaults_are_unchanged_without_a_cap(monkeypatch: pytest.MonkeyPatch):
    """Existing callers keep best-available quality; the cap is strictly opt-in."""
    monkeypatch.setattr(m, "_MAX_HEIGHT", "")
    opts = m.default_ytdlp_options(video=True)
    assert opts["format"] == "bestvideo+bestaudio/best"
    assert opts.get("extractor_args") is None


def test_environment_supplies_the_cap_when_the_caller_does_not(monkeypatch: pytest.MonkeyPatch):
    """YOUTUBE_HELPER_MAX_HEIGHT lets a whole deployment cap downloads with no code change."""
    monkeypatch.setattr(m, "_MAX_HEIGHT", "480")
    assert m.default_ytdlp_options(video=True)["format"] == m.height_capped_format(480)


def test_an_explicit_cap_beats_the_environment(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(m, "_MAX_HEIGHT", "480")
    assert m.default_ytdlp_options(video=True, max_height=720)["format"] == m.height_capped_format(720)


def test_player_clients_reach_the_youtube_extractor_args():
    opts = m.default_ytdlp_options(video=True, player_clients=["web_embedded", "tv"])
    assert opts["extractor_args"]["youtube"]["player_client"] == ["web_embedded", "tv"]
