# Browser Task Runner

A Python 3.12+ CLI using synchronous Playwright and Chromium to run one fixed
public Sauce Demo login workflow. It ends at the inventory page, captures a PNG,
extracts the page title and inventory heading, and saves a structured JSON report.

## Setup

Use the existing external virtual environment; do not create a repo-local `.venv`.

```bash
source ../browser-task-runner-venv/bin/activate
python --version
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
```

Chromium also needs permission to launch subprocesses and its system dependencies.
See the [official Playwright setup guide](https://playwright.dev/python/docs/library).
The demo requires DNS and HTTPS access to `www.saucedemo.com`.

## Run

From the repository root with the external environment active:

```bash
PYTHONPATH=src python -m browser_task_runner smoke
PYTHONPATH=src python -m browser_task_runner demo
```

`smoke` launches and closes Chromium without network access. `demo` uses only the
standard public credentials published on the Sauce Demo login page, through its
normal form. It accepts no alternate URL or credentials. It verifies the exact
inventory URL, visible inventory list, and `Products` heading, then captures the
inventory screenshot and extracts `Swag Labs` / `Products`.

Each demo attempt writes `artifacts/runs/<run_id>/report.json`; successful runs also
write `artifacts/runs/<run_id>/screenshots/inventory.png`. Optional
`--artifacts-dir /path/to/local/runs` changes the output root. Screenshot paths in
reports are relative to the report directory. Generated artifacts are ignored by
Git; keep custom output directories outside tracked source.

Exit 0 indicates success. Exit 1 indicates browser, navigation, selector, page
state, artifact, or cleanup failure. Reports contain UTC timing, duration, ordered
step outcomes, extracted result, screenshot references, and sanitized errors.
Failures preserve completed steps and available screenshots, with a null result.
A failure before browser startup has no steps or screenshots. If report writing
fails, the CLI prints an error and exits 1. No credentials, cookies, or tokens are
included in reports or CLI diagnostics.

## Verify

```bash
python -m pip check
PYTHONPATH=src python -c 'import browser_task_runner; import playwright.sync_api; import pytest'
python -m pytest
python -m pytest tests/test_workflow_unit.py tests/test_reports.py
python -m pytest -m integration
git diff --check
git status --short
```

The full suite includes offline extraction, report, orchestration, and failure
checks, the existing real Chromium lifecycle smoke test, and one public demo
integration test verifying the result, report, and PNG. Browser/network failures
fail visibly instead of skipping. Offline tests need no browser or website.

## Architecture

| Concern | Module | Responsibility |
| --- | --- | --- |
| CLI orchestration | `cli.py` | Run ID, timing, artifact paths, coordination, exit codes. |
| Browser lifecycle | `browser.py` | Chromium, fresh fixed-viewport context, page, timeouts, cleanup. |
| Workflow steps | `workflows/saucedemo.py` | Fixed login, central `data-test` selectors, inventory verification. |
| Screenshot capture | `screenshots.py` | Explicit screenshot destination and capture. |
| Result extraction | `extraction.py` | Read title/heading and validate plain values. |
| Report generation | `reports.py` | Serialize plain data to JSON using a temporary file and replacement. |

Each run uses a fresh context. Locator waits and explicit timeouts replace sleeps.
There are no retries to bypass access barriers. A changed login or inventory state
fails clearly; maintain selectors in the workflow's `SELECTORS` mapping.

Only the public demo at <https://www.saucedemo.com/> is supported. No cart actions,
checkout, purchases, account creation, CAPTCHA handling, alternate workflows,
scheduling, databases, cloud services, or AI are implemented. Stop at unexpected
access restrictions. See [WORKFLOW.md](WORKFLOW.md), [PROJECT_STATUS.md](PROJECT_STATUS.md),
and [AGENTS.md](AGENTS.md).
