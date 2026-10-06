# Browser Task Runner

A Python 3.12+ CLI portfolio project using Playwright and Chromium. Planned V1
will run one deterministic demo workflow, capture screenshots, extract a result,
and save a structured JSON run report.

The foundation milestone implements only Chromium launch and clean shutdown.
It does not visit a website, log in, interact with a page, or produce run reports.

## Setup

Use the existing external virtual environment. Do not create a repository-local
`.venv`. In this workspace:

```bash
source ../browser-task-runner-venv/bin/activate
python --version
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
```

Python must be 3.12 or newer. On another machine, activate your existing external
environment instead. Chromium installation downloads the browser to Playwright's
external cache; Linux may also need Playwright's documented system dependencies.
See the [official Playwright setup guide](https://playwright.dev/python/docs/library).

## Run the foundation smoke command

From the repository root with the external environment active:

```bash
PYTHONPATH=src python -m browser_task_runner smoke
```

This launches headless Chromium and closes it immediately. Success exits with
code 0; a Playwright launch or cleanup failure prints an error and exits with
code 1. No URL, credentials, or browser interactions are accepted.

## Verify

```bash
python -m pip check
PYTHONPATH=src python -c 'import browser_task_runner; import playwright.sync_api; import pytest'
python -m pytest
git diff --check
git status --short
```

The smoke test uses a real Chromium process and checks that it disconnects after
cleanup. It needs installed browser binaries and permission to start subprocesses,
but no website access. Missing browsers or failed launches fail the test rather
than silently skipping it. pytest uses the `src` import path from `pytest.ini`.
See [pytest configuration](https://docs.pytest.org/en/stable/reference/customize.html).

## Small V1 architecture

| Concern | Module | Responsibility |
| --- | --- | --- |
| CLI orchestration | `cli.py` | Parse arguments, coordinate a run, translate failures into exit codes. |
| Browser lifecycle | `browser.py` | Own Playwright and Chromium; later own an isolated context and page with reliable cleanup. |
| Workflow steps | `workflows/saucedemo.py` | Execute only the fixed demo sequence and expose step outcomes. |
| Screenshot capture | `screenshots.py` | Save screenshots at named checkpoints and return artifact paths. |
| Result extraction | `extraction.py` | Read and validate the workflow's final result without writing files. |
| Report generation | `reports.py` | Serialize result, timings, steps, screenshots, and errors to JSON. |

Use synchronous Playwright and ordinary functions. Pass pages, values, and output
paths explicitly; avoid global browser state and unnecessary abstractions.
Only the CLI and browser lifecycle are implemented in this milestone. The other
modules reserve these concerns with docstrings, without executable workflows.

```text
src/browser_task_runner/
  __init__.py
  __main__.py
  cli.py
  browser.py
  screenshots.py
  extraction.py
  reports.py
  workflows/
    __init__.py
    saucedemo.py
tests/
  test_browser_smoke.py
artifacts/screenshots/.gitkeep
```

## Planned demo and boundaries

V1 will support only the fixed Sauce Demo workflow described in [WORKFLOW.md](WORKFLOW.md),
targeting <https://www.saucedemo.com/>. General URL automation is out of scope.
Automate only public/demo pages or pages the user is authorized to use. Never
bypass authentication, CAPTCHAs, paywalls, anti-bot controls, or access restrictions.
Stop and report an unexpected access barrier.

No cloud deployment, databases, scheduling, or AI features. Generated artifacts
stay local and untracked. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for milestone
progress and [AGENTS.md](AGENTS.md) for contributor rules.
