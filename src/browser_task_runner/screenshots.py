"""Capture a screenshot at an explicit destination."""
from pathlib import Path
from playwright.sync_api import Page


def capture_screenshot(page: Page, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(path), full_page=True, timeout=10_000)
    return path
