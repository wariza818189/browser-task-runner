"""One live integration test for the public Selenium form."""
import json
import pytest
from browser_task_runner.cli import run_form_demo


@pytest.mark.integration
def test_form_submission_report_and_screenshot(tmp_path):
    assert run_form_demo(tmp_path) == 0, 'Public form workflow failed; inspect the run report'
    report_path = next(tmp_path.glob('*/report.json'))
    report = json.loads(report_path.read_text())
    assert report['workflow'] == 'selenium_form'
    assert report['status'] == 'success'
    assert report['result'] == {'page_title': 'Web form - target page',
                               'heading': 'Form submitted', 'confirmation': 'Received!'}
    assert all(step['status'] == 'success' for step in report['steps'])
    assert len(report['screenshots']) == 1
    screenshot = report_path.parent / report['screenshots'][0]['path']
    assert screenshot.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
