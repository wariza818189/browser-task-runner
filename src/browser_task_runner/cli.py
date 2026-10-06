"""CLI orchestration for the foundation smoke command."""

import argparse
import sys
from collections.abc import Sequence

from playwright.sync_api import Error

from browser_task_runner.browser import chromium_browser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse the command and report Chromium launch/close success or failure."""
    parser = argparse.ArgumentParser(prog="browser-task-runner")
    parser.add_argument("command", choices=("smoke",), help="launch and close Chromium")
    parser.parse_args(argv)

    try:
        with chromium_browser():
            pass
    except Error as error:
        print(f"Chromium smoke test failed: {error}", file=sys.stderr)
        return 1

    print("Chromium launched and closed successfully.")
    return 0
