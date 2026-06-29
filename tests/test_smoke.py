"""Smoke tests — verify the package imports cleanly without hitting the network.

The rest of the test suite (test_branding, test_streaming, test_youtube_helper)
is marked ``pytest.mark.integration`` and skipped by default. Without these
smoke tests, CI would collect zero tests and exit code 5.
"""

import pytest


def test_import_top_level():
    """``import youtube_helper`` must succeed."""
    import youtube_helper  # noqa: F401


def test_import_aliased():
    """``import youtube_helper as yth`` is the documented usage pattern."""
    import youtube_helper as yth  # noqa: F401


def test_public_api_main():
    """Key download / metadata helpers are exposed at the top level."""
    import youtube_helper as yth
    assert callable(yth.download_video)
    assert callable(yth.download_audio)
    assert callable(yth.download_thumbnail)
    assert callable(yth.video_url_meta_data)
    assert callable(yth.is_valid_video_url)


def test_public_api_streaming():
    """``streaming`` submodule pickers are reachable."""
    import youtube_helper as yth
    assert callable(yth.resolve_direct_url)
    assert callable(yth.list_video_streams)
    assert callable(yth.pick_video_stream)


def test_public_api_branding():
    """``branding`` submodule helpers are reachable."""
    import youtube_helper as yth
    assert callable(yth.channel_info)
    assert callable(yth.channel_videos)
    assert callable(yth.video_engagement)
    assert callable(yth.engagement_batch)


def test_is_valid_video_url_empty_is_false():
    """Smoke: empty string short-circuits in the function and returns False
    without going near yt-dlp (so no network call)."""
    import youtube_helper as yth
    assert yth.is_valid_video_url("") is False
