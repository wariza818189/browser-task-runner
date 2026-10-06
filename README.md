# Browser Task Runner

A Python 3.12+ CLI using synchronous Playwright and Chromium to run two fixed
public demo workflows: Sauce Demo login and Selenium form submission. Each verifies
a deterministic result, captures a PNG, and saves a structured JSON report.

## Setup

Install Python 3.12+ and Git. Clone your copy of this repository, then create a
virtual environment outside the checkout. The commands below use Bash on
Linux/macOS; replace `<repository-url>` with the clone URL.

```bash
git clone <repository-url> browser-task-runner
cd browser-task-runner
python3.12 -m venv ../browser-task-runner-venv
source ../browser-task-runner-venv/bin/activate
python --version
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
```

`requirements-dev.txt` includes the runtime dependencies and pytest. For runtime
use only, install `requirements.txt` instead. Browser binaries are a separate,
required installation. On supported Linux systems with missing browser libraries,
run `python -m playwright install --with-deps chromium` (system package installation
may require administrator privileges).

Chromium also needs permission to launch subprocesses and its system dependencies.
See the official [Playwright setup guide](https://playwright.dev/python/docs/library)
and [browser/system dependency instructions](https://playwright.dev/python/docs/browsers).
The workflows require DNS and HTTPS access to `www.saucedemo.com` or
`www.selenium.dev`, respectively.

## Run

From the repository root with the external environment active:

```bash
PYTHONPATH=src python -m browser_task_runner smoke
PYTHONPATH=src python -m browser_task_runner demo
PYTHONPATH=src python -m browser_task_runner form-demo
```

`smoke` launches and closes Chromium without network access. `demo` uses only the
standard public credentials published on the Sauce Demo login page, through its
normal form. It accepts no alternate URL or credentials. It verifies the exact
inventory URL, visible inventory list, and `Products` heading, then captures the
inventory screenshot and extracts `Swag Labs` / `Products`.

`form-demo` targets Selenium's [public test form](https://www.selenium.dev/selenium/web/web-form.html).
It fills a text input and textarea with fixed synthetic data, selects dropdown
option `Two`, and submits through the normal form. It checks the result URL and
submitted query values, then verifies title `Web form - target page`, heading
`Form submitted`, and visible `Received!` confirmation. No password or personal
information is supplied. Selectors and synthetic values live in `selenium_form.py`.
The form action and method must match the documented test form before submission.

Each workflow attempt writes `artifacts/runs/<run_id>/report.json`; successful runs also
write `artifacts/runs/<run_id>/screenshots/inventory.png` for `demo` or
`artifacts/runs/<run_id>/screenshots/form-submitted.png` for `form-demo`. Optional
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
python -m pytest tests/test_workflow_unit.py tests/test_reports.py tests/test_selenium_form_unit.py
python -m pytest -m integration
git diff --check
git status --short
```

The full suite includes offline extraction, report, orchestration, and failure
checks, the existing real Chromium lifecycle smoke test, and one integration test per public demo
workflow verifying the result, report, and PNG. Browser/network failures
fail visibly instead of skipping. Offline tests need no browser or website.

## Architecture

| Concern | Module | Responsibility |
| --- | --- | --- |
| CLI orchestration | `cli.py` | Run ID, timing, artifact paths, coordination, exit codes. |
| Browser lifecycle | `browser.py` | Chromium, fresh fixed-viewport context, page, timeouts, cleanup. |
| Workflow steps | `workflows/saucedemo.py`, `workflows/selenium_form.py` | Fixed login or form submission, central selectors, result verification. |
| Shared steps | `workflows/common.py` | Ordered step recording and sanitized workflow failures. |
| Screenshot capture | `screenshots.py` | Explicit screenshot destination and capture. |
| Result extraction | `extraction.py` | Read visible text and validate inventory or submission confirmation. |
| Report generation | `reports.py` | Serialize plain data to JSON using a temporary file and replacement. |

Each run uses a fresh context. Locator waits and explicit timeouts replace sleeps.
There are no retries to bypass access barriers. A changed login or inventory state
fails clearly; maintain selectors in the workflow's `SELECTORS` mapping.

Only the two fixed demo targets described above are supported. No cart actions,
checkout, purchases, account creation, CAPTCHA handling, third workflow, arbitrary URLs,
scheduling, databases, cloud services, or AI are implemented. Stop at unexpected
access restrictions. See [WORKFLOW.md](WORKFLOW.md), [PROJECT_STATUS.md](PROJECT_STATUS.md),
and [AGENTS.md](AGENTS.md).
