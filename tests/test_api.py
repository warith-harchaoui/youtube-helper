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
