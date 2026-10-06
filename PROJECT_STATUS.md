# Project status

## Deterministic login milestone

Implemented the single fixed public Sauce Demo login workflow requested on
2026-10-06. The user advanced the foundation milestone and narrowed the earlier
cart plan to stop at inventory. No cart actions or additional workflows were added.

The CLI coordinates timing and reports; browser lifecycle owns isolated contexts
and reliable cleanup; workflow, central selectors, screenshot capture, extraction,
and JSON serialization remain separate. Inventory success requires the exact URL,
visible inventory list, and Products heading. Reports preserve ordered steps and
sanitized failures without credentials. Output artifacts are ignored by Git.

Added offline validation, workflow ordering/failure, report round-trip, and CLI
success/failure tests, plus one real public-demo browser integration test. Retained
the real Chromium launch/close smoke test. Updated README and WORKFLOW scope.

## Validation and blockers

Using external `../browser-task-runner-venv`, Python 3.12.3,
Playwright 1.63.0, pytest 9.1.1:

- `python -m pip check`: passed, no broken requirements.
- Package, Playwright, and pytest imports: passed.
- `python -m pytest`: 14 passed, 2 failed. All offline tests passed. Both the
  Chromium smoke test and demo integration test failed because the execution
  sandbox denied a Chromium system call (`Operation not permitted`) at launch.
- Standalone `python -m browser_task_runner demo`: attempted once, exited 1 at
  Chromium launch; saved a structured failure report at
  `artifacts/runs/20261006T064535-c7fb2207/report.json`. No screenshot was produced.
- DNS probe to the target failed (`Could not resolve host`), so access to the
  public demo must also be verified in a network-enabled execution context.
- `git diff --check`: passed. `git status --short`: reviewed; existing code and
  documentation are modified, with three new untracked test files. An additional
  whitespace scan passed for source/documentation and untracked test files.

Live inventory verification and screenshot capture remain unvalidated due to
these environment blockers. No skip or browser-evasion flags were added. A context
that permits Chromium and demo DNS/HTTPS access is required to finish live validation.
No dependencies installed, commits made, or pushes performed.


## Second deterministic workflow milestone (2026-10-06)

Added exactly one second workflow: Selenium's public Web form at
<https://www.selenium.dev/selenium/web/web-form.html>, exposed as
`PYTHONPATH=src python -m browser_task_runner form-demo`. This user-requested
milestone expands the earlier single-workflow limit; no third workflow was added.
Existing `smoke` and Sauce Demo `demo` commands retain their behavior.

The form workflow uses fixed synthetic text/textarea values and a select control,
normal submission, exact result URL and submitted-value checks, and visible
confirmation validation. It captures `form-submitted.png` and reports the page
title, heading, and confirmation. Central selectors are based on the official
Selenium test form source. No passwords or personal information are supplied.

Extracted reusable ordered step recording and sanitized failures into
`workflows/common.py`, and shared CLI run orchestration across both workflows.
Reused Chromium lifecycle, screenshot capture, visible text extraction, and JSON
report serialization. Added 19 offline tests for form validation, control use,
failures, dispatch, and report identity, plus one new browser integration test.
README and WORKFLOW document the two fixed targets and artifact contracts.

Validation with the existing external Python 3.12.3 environment:

- Full `python -m pytest`: **33 passed, 3 failed (36 total)**. All offline tests
  passed. The smoke test and both demo integration tests fail at Chromium launch
  because this sandbox denies a system call (`Operation not permitted`).
- New workflow attempted once locally: exited 1 at Chromium launch; failure report
  saved at `artifacts/runs/20261006T065710-d076bfee/report.json`. No screenshot was
  produced. On a successful run its relative path is `screenshots/form-submitted.png`.
- Local DNS probe: `www.selenium.dev` could not resolve. Live form verification
  requires a context permitting Chromium and DNS/HTTPS access. Browser and network
  failures remain visible; no skips or bypass flags were added.
- Dependency check and Python imports: passed; no dependencies installed.
- `git diff --check`: passed. `git status --short`: reviewed; generated artifacts
  remain ignored. Additional whitespace scan includes new untracked files.

The new workflow's live success and screenshot remain unvalidated due to the
above environment blockers. No commits or pushes were made.
