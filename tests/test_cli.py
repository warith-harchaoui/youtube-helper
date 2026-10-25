"""
Smoke tests for the command line.

These tests exercise the CLI *parsing* layer and the trivial subcommands
that do not need the network. The goal here is to prevent regressions in
the CLI entry point — flag names, subcommand names, dispatch wiring —
without pulling in yt-dlp's live extractors.

Usage Example
-------------
>>> #   pytest tests/test_cli.py

Author
------
Warith Harchaoui, Ph.D. — https://linkedin.com/in/warith-harchaoui/
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

# The full list of subcommands the CLI exposes. Keeping it here (single
# source of truth) makes drift immediately visible, and it is the list the
# FastAPI surface mirrors.
EXPECTED_SUBCOMMANDS = {
    "metadata",
    "valid",
    "video",
    "audio",
    "thumbnail",
    "resolve",
    "list-streams",
    "pick-stream",
    "channel-info",
    "channel-videos",
    "engagement",
    "engagement-batch",
    "subtitles",
    "comments",
    "ytdlp-version",
}


def test_group_has_expected_subcommands():
    """The group must expose every documented subcommand."""
    from youtube_helper.cli import cli

    assert EXPECTED_SUBCOMMANDS.issubset(set(cli.commands.keys()))


@pytest.mark.parametrize("flag", ["--help", "-h"])
def test_help_exits_zero(flag):
    """``youtube-helper --help`` and its ``-h`` short form both exit 0."""
    from youtube_helper.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, [flag])
    assert result.exit_code == 0
    assert "youtube helper" in result.output.lower()
    # The help must describe the tool, not the parsing library behind it.
    assert "argparse" not in result.output.lower()


@pytest.mark.parametrize("flag", ["--version", "-V"])
def test_version_flag_exits_zero(flag):
    """``-V`` / ``--version`` print a version and exit 0.

    ``-v`` is ``--verbose`` on most subcommands, which is why the version
    flag is the capital ``-V``; a missing short form is the defect this
    guards against.
    """
    from youtube_helper.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, [flag])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


@pytest.mark.parametrize("sub", sorted(EXPECTED_SUBCOMMANDS))
def test_subcommand_help_exits_zero(sub):
    """Every subcommand's ``--help`` should exit 0 (no wiring bug)."""
    from youtube_helper.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, [sub, "--help"])
    assert result.exit_code == 0


def test_valid_empty_url_exits_nonzero():
    """`valid --url ""` short-circuits without a network call and exits non-zero."""
    from youtube_helper.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["valid", "--url", ""])
    # click's Exit exception maps to non-zero exit code.
    assert result.exit_code == 1
    assert "false" in result.output.strip().lower()


def test_main_prints_clean_error_on_a_real_library_exception(capsys):
    """An invalid URL raises AssertionError deep in main.py; main() must not leak it.

    CliRunner.invoke (used by every test above) catches exceptions itself,
    so it never exercises ``main()`` — the actual ``youtube-helper``
    console-script entry point. Drive ``main()`` directly, and assert on the
    message too, not only on the exit code: a bare ``Error:`` with the cause
    swallowed would pass a weaker check.
    """
    import sys

    from youtube_helper.cli import main

    old_argv = sys.argv
    sys.argv = ["youtube-helper", "metadata", "--url", "not a real url"]
    try:
        with pytest.raises(SystemExit) as exc:
            main()
    finally:
        sys.argv = old_argv
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "Error:" in err and "Invalid URL" in err
