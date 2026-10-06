# Workflow scope

## Sauce Demo login (`demo`)

Target: <https://www.saucedemo.com/>. The current milestone ends at inventory.

1. Create isolated headless Chromium context, viewport 1280x720, locator timeout
   10 seconds, and navigation timeout 30 seconds.
2. Navigate to the fixed public demo, rejecting failed HTTP responses and external redirects.
3. Wait for the central `data-test` login locators, fill the site's published
   standard demo credentials, and submit the normal form.
4. Verify the exact inventory URL, visible inventory list, and `Products` heading.
5. Save `screenshots/inventory.png` within the run directory.
6. Extract and validate page title `Swag Labs` and inventory heading `Products`.
7. Close page, context, Chromium, and Playwright; save the final JSON report.

The earlier cart plan is deferred. No cart interactions, checkout, purchase,
account creation, arbitrary site, or user-selected workflow is supported.

## Selenium public form submission (`form-demo`)

The user explicitly authorized this second workflow on 2026-10-06, advancing the
previous one-workflow scope in AGENTS.md. Exactly two workflows are supported.
Target: <https://www.selenium.dev/selenium/web/web-form.html>. The official source
is [Selenium's test form](https://github.com/SeleniumHQ/selenium/blob/trunk/common/src/web/web-form.html).

1. Reuse the isolated Chromium lifecycle and explicit timeouts.
2. Navigate to the exact fixed form URL; reject failed HTTP responses or redirects.
3. Wait for named text/textarea/select controls and the submit button. Confirm
   the form still uses GET and the relative action `submitted-form.html`.
4. Fill fixed synthetic text `Browser Task Runner demo` and textarea
   `Synthetic form submission`; select option value `2` (`Two`).
5. Submit normally. Do not fill passwords or supply personal data.
6. Verify the exact HTTPS result origin/path and submitted query values, then
   the expected page title, `Form submitted` heading, and visible `Received!` message.
7. Capture `screenshots/form-submitted.png`, extract the confirmation, and close
   resources. The shared CLI runner saves the structured report.

Maintain locators and synthetic inputs centrally in `selenium_form.py`. A changed
form, missing selector, failed navigation, submission error, or unexpected result
ends the workflow with a sanitized failure. No retries or access-barrier bypasses.
No third workflow or scraping features are in scope.

## Data flow and report

The CLI owns run ID, UTC timestamps, elapsed duration, output paths, and exit code.
Browser lifecycle owns cleanup. Workflow receives a page, output directory, and
step/screenshot records. Screenshot and extraction helpers have explicit inputs.
Report generation receives plain data and an output path, without browser access.

Outputs: `artifacts/runs/<run_id>/report.json` and
`screenshots/inventory.png` (`demo`) or `screenshots/form-submitted.png`
(`form-demo`) within that run directory on success.

Report fields:

- `schema_version`, `run_id`, `workflow`, `target_url`.
- `started_at`, `finished_at`, `duration_seconds`, `status` (`success`/`failed`).
- `steps`: ordered names and completion/failure status.
- `result`: `page_title` and `inventory_heading` for Sauce Demo, or `page_title`,
  `heading`, and `confirmation` for Selenium; null on failure.
- `screenshots`: named paths relative to the report directory.
- `error`: sanitized failure type/message; null on success.

On failure, preserve available evidence, attempt a failure report, and always
clean up resources. Browser-startup failures have empty step and screenshot lists.
Report-write failures produce exit 1. Never include credentials, cookies, or tokens
in logs or reports. A changed page or unexpected access barrier ends the run.

## Safety boundaries

Use only the two fixed public demos through normal login or form submission. Never bypass authentication,
CAPTCHAs, paywalls, anti-bot controls, or access restrictions. Do not evade detection
or retry to defeat controls. Cloud services, databases, scheduling, and AI remain
out of scope.
