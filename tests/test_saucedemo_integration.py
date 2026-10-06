"""Real Chromium and public demo integration; setup/network failures are visible."""
import json
import pytest
from browser_task_runner.cli import run_demo


@pytest.mark.integration
def test_demo_login_report_and_screenshot(tmp_path):
    assert run_demo(tmp_path) == 0, 'Public demo workflow failed; inspect the run report'
    report_path = next(tmp_path.glob('*/report.json'))
    report = json.loads(report_path.read_text())
    assert report['status'] == 'success'
    assert report['result'] == {'page_title': 'Swag Labs', 'inventory_heading': 'Products'}
    assert all(step['status'] == 'success' for step in report['steps'])
    screenshot = report_path.parent / report['screenshots'][0]['path']
    assert screenshot.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
