"""
Smoke tests for the FastAPI HTTP surface.

Only exercises endpoints that do not require network calls (``/health``,
plus OpenAPI schema introspection to catch endpoint-name drift, plus
``/valid`` with an empty URL which short-circuits before any yt-dlp
call). Heavier round-trip tests belong to the ``integration`` suite
where a real network is available.

Usage Example
-------------
>>> #   pytest tests/test_api.py

Author
------
Warith Harchaoui, Ph.D. — https://linkedin.com/in/warith-harchaoui/
"""

from __future__ import annotations

import pytest

# FastAPI is in the ``[api]`` optional extra — skip cleanly otherwise.
fastapi = pytest.importorskip("fastapi")
httpx = pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

EXPECTED_PATHS = {
    "/health",
    "/metadata",
    "/valid",
    "/resolve",
    "/list-streams",
    "/pick-stream",
    "/channel-info",
    "/channel-videos",
    "/engagement",
    "/engagement-batch",
    "/comments",
    "/ytdlp-version",
    "/video",
    "/audio",
    "/thumbnail",
    "/subtitles",
}


@pytest.fixture(scope="module")
def client():
    """Yield a TestClient bound to the youtube-helper FastAPI app."""
    from youtube_helper.api import app

    with TestClient(app) as c:
        yield c


def test_health_returns_ok(client):
    """``/health`` should return 200 + ``{"status": "ok"}``."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_openapi_lists_expected_endpoints(client):
    """The OpenAPI spec should list every expected route path."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json()["paths"]
    assert EXPECTED_PATHS.issubset(set(paths.keys()))


def test_docs_endpoint_is_served(client):
    """``/docs`` should serve the Swagger UI landing HTML."""
    r = client.get("/docs")
    assert r.status_code == 200
    assert "swagger" in r.text.lower() or "openapi" in r.text.lower()


def test_gui_returns_200_html(client):
    """``GET /gui`` should return 200 with a self-contained HTML page.

    No live network is involved: we only assert the static page renders and
    that its form targets the real ``/audio`` and ``/video`` endpoints (the
    JS builds the request path as ``"/" + kind``), so the download surface the
    GUI drives cannot silently drift from the API.
    """
    r = client.get("/gui")
    assert r.status_code == 200
    # It must be an HTML document (correct content type + a doctype).
    assert r.headers["content-type"].startswith("text/html")
    body = r.text.lower()
    assert "<!doctype html>" in body
    # Sanity-check it is the download bench and offers both kinds.
    assert "download bench" in body
    assert 'value="audio"' in r.text and 'value="video"' in r.text


def test_root_redirects_to_gui(client):
    """``GET /`` should resolve to the GUI page (TestClient follows redirects)."""
    # follow_redirects defaults True in the TestClient; assert we land on HTML.
    r = client.get("/")
    assert r.status_code == 200
    assert "download bench" in r.text.lower()


def test_gui_posts_to_guarded_download_endpoint(client):
    """The GUI's target endpoint (``/audio``) must exist and be guarded.

    The GUI POSTs a JSON body to ``/audio`` / ``/video``. We do NOT hit the
    live network here — an empty URL makes ``download_audio`` fail fast, and
    the endpoint must surface that as a clean 4xx/5xx rather than crash. This
    proves the form wiring reaches a real, error-handling route.
    """
    r = client.post("/audio", json={"url": "", "sample_rate": 44100})
    # download_audio raises on an invalid/empty URL; the endpoint maps that to
    # a 502 (bad upstream) — anything but a 200 or a raw 500 traceback is fine.
    assert r.status_code >= 400
    assert r.status_code != 500 or "detail" in r.text.lower()


def test_valid_empty_url_returns_false(client):
    """``/valid`` with an empty URL short-circuits and returns ``{"valid": false}`` without a network call."""
    r = client.post("/valid", json={"url": ""})
    assert r.status_code == 200
    assert r.json() == {"valid": False}


def test_ytdlp_version_returns_string(client):
    """``/ytdlp-version`` returns whatever yt-dlp exposes as its version."""
    r = client.post("/ytdlp-version", json={})
    assert r.status_code == 200
    body = r.json()
    assert "version" in body
    assert isinstance(body["version"], str)
