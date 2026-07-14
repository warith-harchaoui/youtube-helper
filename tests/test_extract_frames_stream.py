"""
v1.2.0 — ``extract_frames_stream`` wrapper tests.

Unit tests for the new one-call composition over ``pick_video_stream`` +
``video_helper.extract_frames``. These tests are network-free:

- We monkeypatch ``pick_video_stream`` to return a canned
  :class:`VideoStreamInfo` so no yt-dlp HTTP round-trip happens.
- We monkeypatch ``video_helper.extract_frames`` to capture the call
  arguments without actually decoding anything.

Integration coverage against live URLs lives in ``test_streaming.py``
(skipped by default, run with ``pytest -m integration``).
"""

from __future__ import annotations

from typing import Any

import pytest

import youtube_helper as yth
from youtube_helper.streaming import VideoStreamInfo

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


_SAMPLE_STREAM: VideoStreamInfo = {
    "format_id": "137",
    "url": "https://r1---sn-uxa.example/videoplayback?token=xyz",
    "headers": {"User-Agent": "Mozilla/5.0 (test)", "Cookie": "foo=bar"},
    "ext": "mp4",
    "container": "mp4",
    "vcodec": "avc1.640028",
    "acodec": "none",
    "width": 1920,
    "height": 1080,
    "fps": 30.0,
    "vbr_kbps": 4500.0,
    "filesize_bytes": 12345678,
    "is_live": False,
    "protocol": "https",
    "language": None,
    "note": "1080p",
}


@pytest.fixture
def patched_pick(monkeypatch: pytest.MonkeyPatch):
    """Replace ``pick_video_stream`` with a canned response — no network."""
    calls: list[tuple[str, dict]] = []

    def _fake(url: str, **kwargs: Any) -> VideoStreamInfo:
        """Record the call and return the canned stream instead of hitting yt-dlp."""
        calls.append((url, kwargs))
        return _SAMPLE_STREAM

    monkeypatch.setattr("youtube_helper.streaming.pick_video_stream", _fake)
    return calls


@pytest.fixture
def patched_extract_frames(monkeypatch: pytest.MonkeyPatch):
    """Replace ``video_helper.extract_frames`` — no real decoding."""
    calls: list[tuple[tuple, dict]] = []

    def _fake(*args: Any, **kwargs: Any):
        """Record the call args and return an empty iterator (no decoding)."""
        calls.append((args, kwargs))

        def _empty_iter():
            """Yield nothing — a stand-in for the real frame generator."""
            if False:
                yield  # pragma: no cover — empty generator stub

        return _empty_iter()

    monkeypatch.setattr("video_helper.extract_frames", _fake)
    return calls


# ---------------------------------------------------------------------------
# extract_frames_stream
# ---------------------------------------------------------------------------


def test_extract_frames_stream_returns_iterator(patched_pick, patched_extract_frames) -> None:
    """The wrapper returns the iterator produced by ``extract_frames``."""
    it = yth.extract_frames_stream("https://www.youtube.com/watch?v=test")
    # The return value is the iterator that extract_frames yields.
    assert hasattr(it, "__iter__")


def test_extract_frames_stream_forwards_url_to_picker(patched_pick, patched_extract_frames) -> None:
    """The source URL is forwarded verbatim to ``pick_video_stream``."""
    yth.extract_frames_stream("https://vimeo.com/123")
    assert patched_pick[0][0] == "https://vimeo.com/123"


def test_extract_frames_stream_forwards_picker_constraints(
    patched_pick, patched_extract_frames
) -> None:
    """All picker constraints (codec / format / fps / language / …) pass through."""
    yth.extract_frames_stream(
        "https://www.youtube.com/watch?v=test",
        prefer_codec="h264",
        prefer_format="mp4",
        max_fps=30,
        language="en",
        cookies_from_browser="firefox",
        verbose=True,
    )
    _, kwargs = patched_pick[0]
    assert kwargs["prefer_codec"] == "h264"
    assert kwargs["prefer_format"] == "mp4"
    assert kwargs["max_fps"] == 30
    assert kwargs["language"] == "en"
    assert kwargs["cookies_from_browser"] == "firefox"
    assert kwargs["verbose"] is True


def test_extract_frames_stream_auto_wires_headers(patched_pick, patched_extract_frames) -> None:
    """The resolver's headers MUST land on the extract_frames call."""
    yth.extract_frames_stream(
        "https://www.youtube.com/watch?v=test",
        frame_interval=1.0,
        output_width=224,
        output_height=224,
    )
    args, kwargs = patched_extract_frames[0]
    # extract_frames is called with the resolved direct URL as positional arg.
    assert args[0] == _SAMPLE_STREAM["url"]
    # Headers are spliced in automatically.
    assert kwargs["http_headers"] == _SAMPLE_STREAM["headers"]


def test_extract_frames_stream_explicit_headers_win(
    patched_pick,
    patched_extract_frames,
) -> None:
    """Caller-supplied ``http_headers`` override the resolver's headers."""
    custom = {"Authorization": "Bearer xyz"}
    yth.extract_frames_stream(
        "https://members.example.com/clip",
        http_headers=custom,
    )
    _, kwargs = patched_extract_frames[0]
    assert kwargs["http_headers"] == custom


def test_extract_frames_stream_forwards_extract_frames_kwargs(
    patched_pick,
    patched_extract_frames,
) -> None:
    """Random extract_frames kwargs pass through verbatim."""
    yth.extract_frames_stream(
        "https://www.youtube.com/watch?v=test",
        destination="torch",
        device="auto",
        batch_size=32,
        output_width=224,
        output_height=224,
        frame_step=5,
    )
    _, kwargs = patched_extract_frames[0]
    assert kwargs["destination"] == "torch"
    assert kwargs["device"] == "auto"
    assert kwargs["batch_size"] == 32
    assert kwargs["output_width"] == 224
    assert kwargs["output_height"] == 224
    assert kwargs["frame_step"] == 5


def test_extract_frames_stream_is_exported_at_package_root() -> None:
    """Public surface check — the wrapper is reachable as ``yth.extract_frames_stream``."""
    assert hasattr(yth, "extract_frames_stream")
    assert callable(yth.extract_frames_stream)
