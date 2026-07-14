"""Integration tests — download videos / audio / thumbnails end-to-end.

These exercises hit the live network (a real YouTube URL) and the ffmpeg
toolchain, so the whole module is marked ``pytest.mark.integration`` and
skipped by default (see ``addopts = -m 'not integration'`` in
``pyproject.toml``). They are the ground-truth checks that the public
download helpers actually produce valid media on disk.
"""

# Test imports
import audio_helper as ah
import os_helper as osh
import pytest
import video_helper as vh

from youtube_helper import (
    download_audio,
    download_thumbnail,
    download_video,
    is_valid_video_url,
    video_url_meta_data,
)

pytestmark = pytest.mark.integration

# Sample YouTube video for testing
youtube_url = "https://www.youtube.com/watch?v=YE7VzlLtp-4"
video_filename = "big-buck-bunny.mp4"
audio_filename = "big-buck-bunny.mp3"
thumbnail_filename = "thumbnail.jpg"

osh.verbosity(0)


# Helper function to get the test folder for media (video, audio, thumbnail)
def get_test_folder(filename: str) -> str:
    """Return a path under the ``yt_tests`` scratch folder for ``filename``.

    Parameters
    ----------
    filename : str
        Basename of the media file the caller wants to write.

    Returns
    -------
    str
        ``yt_tests/<filename>``, with the ``yt_tests`` directory created
        on first use so downloads have somewhere to land.
    """
    folder = "yt_tests"
    media_file = osh.join([folder, filename])
    if not osh.file_exists(media_file):
        osh.make_directory(folder)
    return media_file


# Test for video download
def test_video():
    """Download a real video and assert the file is a valid, playable clip."""
    video_file = get_test_folder(video_filename)

    assert is_valid_video_url(youtube_url), "YouTube URL should be valid"

    download_video(youtube_url, video_file)

    assert vh.is_valid_video_file(video_file), "Downloaded file should be a valid video file"

    video_dim = vh.video_dimensions(video_file)
    assert video_dim["width"] > 0, "Video width should be positive"
    assert video_dim["height"] > 0, "Video height should be positive"
    assert video_dim["duration"] > 0, "Video duration should be positive"
    assert video_dim["frame_rate"] > 0, "Video frame rate should be positive"
    assert video_dim["has_sound"], "Video should have sound"


# Test for audio download
def test_audio():
    """Download the audio track and assert it is a valid, non-empty file."""
    audio_file = get_test_folder(audio_filename)
    download_audio(youtube_url, audio_file)

    assert ah.is_valid_audio_file(audio_file), "Downloaded file should be a valid audio file"

    audio_duration = ah.get_audio_duration(audio_file)
    assert audio_duration > 0, "Audio duration should be positive"


# Test for downloading a thumbnail
def test_thumbnail():
    """Download the thumbnail and assert it exists and opens as an image."""
    thumbnail_file = get_test_folder(thumbnail_filename)
    download_thumbnail(youtube_url, thumbnail_file)

    assert osh.file_exists(thumbnail_file), "Thumbnail file should exist"

    # Optionally, test that the thumbnail can be opened
    from PIL import Image

    img = Image.open(thumbnail_file)
    assert img.size[0] > 0 and img.size[1] > 0, "Thumbnail dimensions should be valid"


# Test for video URL metadata extraction
def test_video_url_meta_data():
    """Assert metadata extraction returns a non-empty title and description."""
    metadata = video_url_meta_data(youtube_url)

    assert "title" in metadata, "Metadata should contain 'title'"
    assert "description" in metadata, "Metadata should contain 'description'"
    assert metadata["title"] != "", "Title should not be empty"
    assert metadata["description"] != "", "Description should not be empty"
