# syntax=docker/dockerfile:1.6
#
# youtube-helper — reproducible container image.
#
# Two-stage build: the base stage pulls system deps (ffmpeg is
# mandatory for the whole toolkit) and installs the package with the
# [api,mcp] extras so the container can serve the HTTP + MCP surfaces
# out of the box.
#
# Build:
#   docker build -t youtube-helper .
#
# Run (HTTP + MCP on 0.0.0.0:8000):
#   docker run --rm -p 8000:8000 youtube-helper
#
# Run CLI one-shot:
#   docker run --rm -v $PWD:/data youtube-helper \
#     youtube-helper audio --url https://www.youtube.com/watch?v=YE7VzlLtp-4 \
#                          --output /data/out.mp3

# --- base -------------------------------------------------------------------
FROM python:3.11-slim AS base

# System deps: ffmpeg for every audio/video pipeline, libsndfile for
# soundfile (pulled in transitively via audio-helper), tini for signal
# handling. Also git — the intra-family deps (`os-helper`,
# `audio-helper`, `video-helper`) are installed from git tags.
RUN apt-get update && apt-get install --no-install-recommends -y \
        ffmpeg \
        libsndfile1 \
        git \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Non-root runtime user; the app never needs root at runtime.
RUN useradd --create-home --shell /bin/bash app
WORKDIR /app

# --- deps -------------------------------------------------------------------
# Copy the package first so pip picks up pyproject.toml before we invalidate
# the layer with source changes.
COPY --chown=app:app pyproject.toml README.md LICENSE ./
COPY --chown=app:app youtube_helper ./youtube_helper

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir '.[api,mcp]'

# --- runtime ----------------------------------------------------------------
USER app
EXPOSE 8000
ENV PYTHONUNBUFFERED=1 \
    YOUTUBE_HELPER_HOST=0.0.0.0 \
    YOUTUBE_HELPER_PORT=8000

# tini reaps orphan children (ffmpeg / yt-dlp subprocesses) cleanly on SIGTERM.
ENTRYPOINT ["/usr/bin/tini", "--"]
# Default: serve FastAPI + MCP. Override for one-shot CLI usage.
CMD ["youtube-helper-mcp"]
