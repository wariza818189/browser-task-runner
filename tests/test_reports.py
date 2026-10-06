"""Offline report and orchestration checks."""
import json
from contextlib import contextmanager
from unittest.mock import MagicMock

from browser_task_runner import cli
from browser_task_runner.reports import write_report
from browser_task_runner.workflows.saucedemo import WorkflowFailure


def test_json_report_round_trip(tmp_path):
    data = {'status': 'success', 'result': {'inventory_heading': 'Products'}, 'error': None}
    path = write_report(data, tmp_path / 'nested' / 'report.json')
    assert json.loads(path.read_text()) == data
    assert not path.with_suffix('.json.tmp').exists()


@contextmanager
def fake_page():
    yield MagicMock()


def test_failed_run_writes_report(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, 'chromium_page', fake_page)
    def fail(*args):
        raise WorkflowFailure('navigation', 'Could not navigate to the public Sauce Demo page')
    monkeypatch.setattr(cli, 'run_workflow', fail)
    assert cli.run_demo(tmp_path) == 1
    report = json.loads(next(tmp_path.glob('*/report.json')).read_text())
    assert report['status'] == 'failed'
    assert report['result'] is None
    assert report['error']['type'] == 'navigation'
    assert report['duration_seconds'] >= 0
    assert report['finished_at'] >= report['started_at']


def test_report_write_failure_returns_nonzero(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, 'chromium_page', fake_page)
    monkeypatch.setattr(cli, 'run_workflow', lambda *args: {'page_title': 'Swag Labs'})
    def fail(*args):
        raise OSError('write failed')
    monkeypatch.setattr(cli, 'write_report', fail)
    assert cli.run_demo(tmp_path) == 1


def test_successful_run_writes_report_after_cleanup(tmp_path, monkeypatch):
    closed = []
    @contextmanager
    def page():
        try:
            yield MagicMock()
        finally:
            closed.append(True)
    monkeypatch.setattr(cli, 'chromium_page', page)
    monkeypatch.setattr(cli, 'run_workflow', lambda *args: {'page_title': 'Swag Labs', 'inventory_heading': 'Products'})
    assert cli.run_demo(tmp_path) == 0
    assert closed == [True]
    report = json.loads(next(tmp_path.glob('*/report.json')).read_text())
    assert report['status'] == 'success'
    assert report['error'] is None
