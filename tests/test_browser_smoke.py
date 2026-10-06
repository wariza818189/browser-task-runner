"""Real Chromium lifecycle check with no website access or page interactions."""

from browser_task_runner.browser import chromium_browser


def test_chromium_launches_and_closes() -> None:
    with chromium_browser() as browser:
        assert browser.is_connected()
        assert browser.contexts == []

    assert not browser.is_connected()
