# Workflow scope

## Foundation milestone: implemented scope

1. Parse the CLI's `smoke` command.
2. Start synchronous Playwright and launch headless Chromium.
3. Close Chromium and stop Playwright, including cleanup when the caller fails.
4. Return a success or failure exit code.

No page is created and no network navigation, login, page interaction, screenshot,
result extraction, or report generation happens in this milestone.

## Planned V1: one deterministic Sauce Demo workflow

Target: <https://www.saucedemo.com/>. Implement this only in a later milestone.

1. Create an isolated browser context with a fixed viewport and explicit timeouts.
2. Navigate to the demo and use its published standard demo credentials through
   the normal login form. Do not bypass authentication or access controls.
3. Wait for the inventory page and capture a named screenshot.
4. Select the single fixed product `Sauce Labs Backpack` and add it to the cart.
5. Open the cart, verify exactly that item, and capture a cart screenshot.
6. Extract the cart item's name, displayed price/currency text, and quantity.
7. Save a structured JSON report and close the page, context, and browser.

End at the cart: no checkout or purchase. Use a fresh context for each run and
stable locators with condition-based waits. Fail clearly if the demo changes.
Do not support alternate websites, user-selected workflows, or arbitrary URLs in V1.

## Planned data flow and report

The CLI will own run ID, UTC start/end timestamps, elapsed duration, artifact paths,
and the final exit code. The browser module owns resource cleanup. Workflow steps
receive a page and call screenshot/extraction helpers; report generation receives
plain data and an output path, with no browser access.

Proposed local outputs: `artifacts/runs/<run_id>/report.json` and screenshots in
that run's `screenshots/` directory. These paths are ignored by Git.

Proposed report fields:

- `schema_version`, `run_id`, `workflow`, and `target_url`.
- `started_at`, `finished_at`, `duration_seconds`, and `status` (`success`/`failed`).
- `steps`: ordered names and their completion/failure status.
- `result`: item name, displayed price/currency text, and integer quantity; null on failure.
- `screenshots`: named relative artifact paths.
- `error`: sanitized failure type/message; null on success.

On failure, preserve available evidence, attempt a failure report, and always
clean up resources. Report-write failures must also produce a nonzero CLI exit.
Never include credentials, cookies, or tokens in logs or reports.

## Safety boundaries

Use only public/demo pages or pages the user is authorized to use. Stop on an
unexpected authentication requirement, CAPTCHA, paywall, anti-bot control, or
access restriction. Do not bypass controls, evade detection, or retry to defeat
them. Cloud deployment, databases, scheduling, and AI features are out of scope.
