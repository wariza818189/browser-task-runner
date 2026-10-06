"""The one fixed public Sauce Demo login workflow; ends at inventory."""
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from playwright.sync_api import Error, Page, TimeoutError
from browser_task_runner.extraction import extract_inventory
from browser_task_runner.screenshots import capture_screenshot

TARGET_URL = "https://www.saucedemo.com/"
# Published on the demo login page; never accept arbitrary credentials or URLs.
DEMO_USERNAME = "standard_user"
DEMO_PASSWORD = "secret_sauce"
SELECTORS = {
    "username": '[data-test="username"]',
    "password": '[data-test="password"]',
    "login": '[data-test="login-button"]',
    "heading": '[data-test="title"]',
    "inventory": '[data-test="inventory-list"]',
}


class WorkflowFailure(RuntimeError):
    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind


def run_workflow(page: Page, run_dir: Path, steps: list[dict[str, str]],
                 screenshots: list[dict[str, str]]) -> dict[str, str]:
    def step(name: str, action: Callable[[], Any]) -> Any:
        record = {"name": name, "status": "running"}
        steps.append(record)
        try:
            value = action()
        except Exception:
            record["status"] = "failed"
            raise
        record["status"] = "success"
        return value

    def navigate() -> None:
        try:
            response = page.goto(TARGET_URL, wait_until="domcontentloaded")
        except Error:
            raise WorkflowFailure("navigation", "Could not navigate to the public Sauce Demo page") from None
        if response is None or not response.ok:
            raise WorkflowFailure("navigation", "Sauce Demo returned an unsuccessful HTTP response")
        if urlsplit(page.url).hostname != "www.saucedemo.com":
            raise WorkflowFailure("unexpected_page_state", "Unexpected redirect away from Sauce Demo")

    def login() -> None:
        try:
            for key in ("username", "password", "login"):
                page.locator(SELECTORS[key]).wait_for(state="visible")
        except TimeoutError:
            raise WorkflowFailure("missing_selector", "Expected Sauce Demo login controls are missing; stop at any access barrier") from None
        try:
            page.locator(SELECTORS["username"]).fill(DEMO_USERNAME)
            page.locator(SELECTORS["password"]).fill(DEMO_PASSWORD)
            page.locator(SELECTORS["login"]).click()
        except Error:
            raise WorkflowFailure("login", "Could not fill or submit the demo login form") from None

    def verify() -> None:
        try:
            page.wait_for_url(TARGET_URL + "inventory.html", wait_until="domcontentloaded")
            page.locator(SELECTORS["inventory"]).wait_for(state="visible")
            page.locator(SELECTORS["heading"]).wait_for(state="visible")
            if page.locator(SELECTORS["heading"]).inner_text().strip() != "Products":
                raise ValueError
        except (Error, ValueError):
            raise WorkflowFailure("unexpected_page_state", "Expected inventory URL, visible inventory list, and Products heading after login") from None

    def screenshot() -> None:
        path = capture_screenshot(page, run_dir / "screenshots" / "inventory.png")
        screenshots.append({"name": "inventory", "path": path.relative_to(run_dir).as_posix()})

    def extract() -> dict[str, str]:
        try:
            return extract_inventory(page, SELECTORS["heading"])
        except (Error, ValueError):
            raise WorkflowFailure("unexpected_page_state", "Inventory result did not match the expected demo state") from None

    step("navigate", navigate)
    step("login", login)
    step("verify_inventory", verify)
    step("capture_inventory", screenshot)
    return step("extract_inventory", extract)
