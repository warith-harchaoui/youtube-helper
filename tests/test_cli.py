"""
Smoke tests for the argparse and click CLIs.

These tests exercise the CLI *parsing* layer and the trivial subcommands
that do not need the network. The goal here is to prevent regressions in
the CLI entry points — flag names, subcommand names, dispatch wiring —
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

# The click CLI needs the ``click`` runtime dep, which lives in the
# ``[cli]`` optional extra. Skip cleanly if it is not installed.
click = pytest.importorskip("click")

from click.testing import CliRunner  # noqa: E402


# The full list of subcommands exposed by both CLIs. Keeping it here
# (single source of truth) makes drift immediately visible.
EXPECTED_SUBCOMMANDS = {
    "metadata", "valid", "video", "audio", "thumbnail",
    "resolve", "list-streams", "pick-stream",
    "channel-info", "channel-videos",
    "engagement", "engagement-batch",
    "subtitles", "comments", "ytdlp-version",
}


def test_argparse_parser_builds_without_error():
    """Building the parser should never fail (imports, subcommand wiring)."""
    from youtube_helper.cli_argparse import build_parser

    parser = build_parser()
    # A parser with at least one subcommand exposes them via _subparsers.
    # We assert on the expected list of subcommand names to catch drift.
    subparsers_action = next(
        a for a in parser._actions if a.__class__.__name__ == "_SubParsersAction"
    )
    assert EXPECTED_SUBCOMMANDS.issubset(set(subparsers_action.choices.keys()))


def test_argparse_help_exits_zero(capsys):
    """``youtube-helper --help`` should exit with code 0 and print usage."""
    from youtube_helper.cli_argparse import main

    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "youtube-helper" in captured.out.lower()


@pytest.mark.parametrize("sub", sorted(EXPECTED_SUBCOMMANDS))
def test_argparse_subcommand_help_exits_zero(sub, capsys):
    """Every subcommand's ``--help`` should exit 0 (no wiring bug)."""
    from youtube_helper.cli_argparse import main

    with pytest.raises(SystemExit) as exc:
        main([sub, "--help"])
    assert exc.value.code == 0


def test_argparse_valid_empty_url_exits_nonzero(capsys):
    """`valid --url ""` short-circuits without a network call and exits non-zero."""
    from youtube_helper.cli_argparse import main

    rc = main(["valid", "--url", ""])
    assert rc == 1
    captured = capsys.readouterr()
    assert "false" in captured.out.strip().lower()


def test_click_group_has_expected_subcommands():
    """The click group must expose the same subcommands as the argparse CLI."""
    from youtube_helper.cli_click import cli

    assert EXPECTED_SUBCOMMANDS.issubset(set(cli.commands.keys()))


def test_click_help_exits_zero():
    """``youtube-helper-click --help`` should exit 0."""
    from youtube_helper.cli_click import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "youtube helper" in result.output.lower()


@pytest.mark.parametrize("sub", sorted(EXPECTED_SUBCOMMANDS))
def test_click_subcommand_help_exits_zero(sub):
    """Every click subcommand's ``--help`` should exit 0."""
    from youtube_helper.cli_click import cli

    runner = CliRunner()
    result = runner.invoke(cli, [sub, "--help"])
    assert result.exit_code == 0


def test_click_valid_empty_url_exits_nonzero():
    """`valid --url ""` short-circuits without a network call and exits non-zero."""
    from youtube_helper.cli_click import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["valid", "--url", ""])
    # click's Exit exception maps to non-zero exit code.
    assert result.exit_code == 1
    assert "false" in result.output.strip().lower()
