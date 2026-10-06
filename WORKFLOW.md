# Workflow scope

## Implemented V1: one deterministic Sauce Demo login workflow

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
account creation, alternate site, or user-selected workflow is supported.

## Data flow and report

The CLI owns run ID, UTC timestamps, elapsed duration, output paths, and exit code.
Browser lifecycle owns cleanup. Workflow receives a page, output directory, and
step/screenshot records. Screenshot and extraction helpers have explicit inputs.
Report generation receives plain data and an output path, without browser access.

Outputs: `artifacts/runs/<run_id>/report.json` and
`artifacts/runs/<run_id>/screenshots/inventory.png` on successful runs.

Report fields:

- `schema_version`, `run_id`, `workflow`, `target_url`.
- `started_at`, `finished_at`, `duration_seconds`, `status` (`success`/`failed`).
- `steps`: ordered names and completion/failure status.
- `result`: `page_title` and `inventory_heading`; null on failure.
- `screenshots`: named paths relative to the report directory.
- `error`: sanitized failure type/message; null on success.

On failure, preserve available evidence, attempt a failure report, and always
clean up resources. Browser-startup failures have empty step and screenshot lists.
Report-write failures produce exit 1. Never include credentials, cookies, or tokens
in logs or reports. A changed page or unexpected access barrier ends the run.

## Safety boundaries

Use only the fixed public demo through normal login. Never bypass authentication,
CAPTCHAs, paywalls, anti-bot controls, or access restrictions. Do not evade detection
or retry to defeat controls. Cloud services, databases, scheduling, and AI remain
out of scope.
