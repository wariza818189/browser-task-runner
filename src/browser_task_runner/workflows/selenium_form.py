"""Fixed public Selenium test form; synthetic data, no authentication."""
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from playwright.sync_api import Error, Page, TimeoutError
from browser_task_runner.extraction import extract_form_result
from browser_task_runner.screenshots import capture_screenshot
from browser_task_runner.workflows.common import WorkflowFailure, run_step

TARGET_URL = "https://www.selenium.dev/selenium/web/web-form.html"
RESULT_URL = "https://www.selenium.dev/selenium/web/submitted-form.html"
FORM_VALUES = {"my-text": "Browser Task Runner demo", "my-textarea": "Synthetic form submission",
               "my-select": "2"}
SELECTORS = {"text": '[name="my-text"]', "textarea": '[name="my-textarea"]',
             "select": '[name="my-select"]', "submit": 'button[type="submit"]',
             "heading": "h1", "message": "#message"}


def validate_submission_url(url: str) -> None:
    actual, expected = urlsplit(url), urlsplit(RESULT_URL)
    if (actual.scheme, actual.netloc, actual.path) != (
            expected.scheme, expected.netloc, expected.path):
        raise ValueError("Unexpected form result URL")
    query = parse_qs(actual.query)
    if any(query.get(key) != [value] for key, value in FORM_VALUES.items()):
        raise ValueError("Submitted form values do not match the fixed demo data")


def run_workflow(page: Page, run_dir: Path, steps: list[dict[str, str]],
                 screenshots: list[dict[str, str]]) -> dict[str, str]:
    def navigate() -> None:
        try:
            response = page.goto(TARGET_URL, wait_until="domcontentloaded")
        except Error:
            raise WorkflowFailure("navigation", "Could not navigate to the public Selenium form") from None
        if response is None or not response.ok:
            raise WorkflowFailure("navigation", "Selenium form returned an unsuccessful HTTP response")
        if page.url != TARGET_URL:
            raise WorkflowFailure("unexpected_page_state", "Unexpected redirect from the Selenium form")

    def fill() -> None:
        try:
            for key in ("text", "textarea", "select", "submit"):
                page.locator(SELECTORS[key]).wait_for(state="visible")
        except TimeoutError:
            raise WorkflowFailure("missing_selector", "Expected Selenium form controls are missing; stop at any access barrier") from None
        try:
            # Guard against a changed form sending the synthetic data elsewhere.
            form = page.locator('form')
            if form.get_attribute("action") != "submitted-form.html" or form.get_attribute("method").lower() != "get":
                raise ValueError
            page.locator(SELECTORS["text"]).fill(FORM_VALUES["my-text"])
            page.locator(SELECTORS["textarea"]).fill(FORM_VALUES["my-textarea"])
            page.locator(SELECTORS["select"]).select_option(FORM_VALUES["my-select"])
        except (Error, ValueError, AttributeError):
            raise WorkflowFailure("form_interaction", "Could not fill the expected Selenium demo form") from None

    def submit() -> None:
        try:
            page.locator(SELECTORS["submit"]).click()
        except Error:
            raise WorkflowFailure("submission", "Could not submit the Selenium demo form") from None

    def verify() -> None:
        try:
            page.wait_for_url(RESULT_URL + "?*", wait_until="domcontentloaded")
            validate_submission_url(page.url)
            extract_form_result(page, SELECTORS["heading"], SELECTORS["message"])
        except (Error, ValueError):
            raise WorkflowFailure("unexpected_page_state", "Expected Selenium confirmation and matching submitted demo values") from None

    def screenshot() -> None:
        path = capture_screenshot(page, run_dir / "screenshots" / "form-submitted.png")
        screenshots.append({"name": "form_submitted", "path": path.relative_to(run_dir).as_posix()})

    def extract() -> dict[str, str]:
        try:
            return extract_form_result(page, SELECTORS["heading"], SELECTORS["message"])
        except (Error, ValueError):
            raise WorkflowFailure("unexpected_page_state", "Selenium confirmation changed during extraction") from None

    run_step(steps, "navigate", navigate)
    run_step(steps, "fill_form", fill)
    run_step(steps, "submit_form", submit)
    run_step(steps, "verify_submission", verify)
    run_step(steps, "capture_submission", screenshot)
    return run_step(steps, "extract_submission", extract)
