"""Own Playwright, Chromium, isolated contexts, and page cleanup."""

from collections.abc import Iterator
from contextlib import contextmanager
from playwright.sync_api import Browser, Page, sync_playwright


@contextmanager
def chromium_browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, timeout=30_000)
        try:
            yield browser
        finally:
            browser.close()


@contextmanager
def chromium_page() -> Iterator[Page]:
    with chromium_browser() as browser:
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        context.set_default_timeout(10_000)
        context.set_default_navigation_timeout(30_000)
        try:
            page = context.new_page()
            try:
                yield page
            finally:
                page.close()
        finally:
            context.close()
