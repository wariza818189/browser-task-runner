"""Coordinate lifecycle, fixed workflow, timing, and report output."""
import argparse
import sys
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from uuid import uuid4
from browser_task_runner.browser import chromium_browser, chromium_page
from browser_task_runner.reports import write_report
from browser_task_runner.workflows.saucedemo import TARGET_URL, run_workflow
from browser_task_runner.workflows.common import WorkflowFailure
from browser_task_runner.workflows import selenium_form


def run_demo(artifacts_dir: Path) -> int:
    return _run(artifacts_dir, "saucedemo_login", TARGET_URL, run_workflow,
                "Sauce Demo inventory verified.")


def run_form_demo(artifacts_dir: Path) -> int:
    return _run(artifacts_dir, "selenium_form", selenium_form.TARGET_URL,
                selenium_form.run_workflow, "Selenium demo form submission verified.")


def _run(artifacts_dir: Path, workflow_name: str, target_url: str,
         workflow: Callable, success_message: str) -> int:
    started = datetime.now(timezone.utc)
    timer = monotonic()
    run_id = started.strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:8]
    run_dir = artifacts_dir / run_id
    report = {"schema_version": 1, "run_id": run_id, "workflow": workflow_name,
              "target_url": target_url, "started_at": started.isoformat(),
              "status": "failed", "steps": [], "result": None, "screenshots": [], "error": None}
    try:
        with chromium_page() as page:
            result = workflow(page, run_dir, report["steps"], report["screenshots"])
        report["result"] = result
        report["status"] = "success"
    except Exception as error:
        # Raw Playwright messages can contain submitted values; only known safe messages leave here.
        report["error"] = {"type": error.kind if isinstance(error, WorkflowFailure) else "runtime",
                           "message": str(error) if isinstance(error, WorkflowFailure)
                           else "Browser setup, artifact capture, or cleanup failed"}
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["duration_seconds"] = round(monotonic() - timer, 3)
    try:
        path = write_report(report, run_dir / "report.json")
    except Exception:
        print("Run report could not be written.", file=sys.stderr)
        return 1
    print(f"Report: {path.resolve()}")
    for screenshot in report["screenshots"]:
        print(f"Screenshot: {(run_dir / screenshot['path']).resolve()}")
    if report["error"]:
        print(f"Workflow failed [{report['error']['type']}]: {report['error']['message']}", file=sys.stderr)
        return 1
    print(success_message)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="browser-task-runner")
    parser.add_argument("command", choices=("smoke", "demo", "form-demo"))
    parser.add_argument("--artifacts-dir", type=Path, default=Path("artifacts/runs"))
    args = parser.parse_args(argv)
    if args.command == "demo":
        return run_demo(args.artifacts_dir)
    if args.command == "form-demo":
        return run_form_demo(args.artifacts_dir)
    try:
        with chromium_browser():
            pass
    except Exception:
        print("Chromium smoke test failed: browser launch or cleanup failed.", file=sys.stderr)
        return 1
    print("Chromium launched and closed successfully.")
    return 0
