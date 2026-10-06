"""Own the Playwright and Chromium lifecycle."""

from collections.abc import Iterator
from contextlib import contextmanager

from playwright.sync_api import Browser, sync_playwright


@contextmanager
def chromium_browser() -> Iterator[Browser]:
    """Launch headless Chromium and close it even if the caller raises."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, timeout=30_000)
        try:
            yield browser
        finally:
            browser.close()
