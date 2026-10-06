"""Offline form controls, confirmation, failure boundaries, and CLI dispatch."""
import json
from contextlib import contextmanager
from unittest.mock import MagicMock
from urllib.parse import urlencode

import pytest
from playwright.sync_api import Error, TimeoutError
from browser_task_runner import cli
from browser_task_runner.extraction import validate_form_result
from browser_task_runner.workflows import selenium_form as form
from browser_task_runner.workflows.common import WorkflowFailure

RESULT = {'page_title': 'Web form - target page', 'heading': 'Form submitted', 'confirmation': 'Received!'}


def result_url():
    return form.RESULT_URL + '?' + urlencode(form.FORM_VALUES)


def fake_page():
    page = MagicMock()
    controls = {selector: MagicMock() for selector in [*form.SELECTORS.values(), 'form']}
    page.locator.side_effect = controls.__getitem__
    page.url = form.TARGET_URL
    page.goto.return_value.ok = True
    controls['form'].get_attribute.side_effect = {'action': 'submitted-form.html', 'method': 'get'}.__getitem__
    controls['h1'].inner_text.return_value = 'Form submitted'
    controls['#message'].inner_text.return_value = 'Received!'
    page.title.return_value = RESULT['page_title']
    def submit():
        page.url = result_url()
    controls[form.SELECTORS['submit']].click.side_effect = submit
    return page, controls


def test_form_result_validation():
    assert validate_form_result('Web form - target page', ' Form submitted ', 'Received!') == RESULT


@pytest.mark.parametrize('values', [('Wrong', 'Form submitted', 'Received!'), ('Web form - target page', 'Web form', 'Received!'), ('Web form - target page', 'Form submitted', 'Denied')])
def test_form_result_rejects_unexpected_state(values):
    with pytest.raises(ValueError):
        validate_form_result(*values)


def test_submission_url_matches_encoded_values():
    form.validate_submission_url(result_url() + '&my-hidden=')


@pytest.mark.parametrize('url', [form.RESULT_URL, form.RESULT_URL + '?my-select=1', 'https://example.com/submitted-form.html', 'http://www.selenium.dev/selenium/web/submitted-form.html'])
def test_submission_url_rejects_wrong_target_or_values(url):
    with pytest.raises(ValueError):
        form.validate_submission_url(url)


def test_form_workflow_controls_and_order(tmp_path):
    page, controls = fake_page()
    steps, screenshots = [], []
    assert form.run_workflow(page, tmp_path, steps, screenshots) == RESULT
    controls[form.SELECTORS['text']].fill.assert_called_once_with(form.FORM_VALUES['my-text'])
    controls[form.SELECTORS['textarea']].fill.assert_called_once_with(form.FORM_VALUES['my-textarea'])
    controls[form.SELECTORS['select']].select_option.assert_called_once_with('2')
    controls[form.SELECTORS['submit']].click.assert_called_once()
    assert [s['name'] for s in steps] == ['navigate', 'fill_form', 'submit_form', 'verify_submission', 'capture_submission', 'extract_submission']
    assert all(s['status'] == 'success' for s in steps)
    assert screenshots == [{'name': 'form_submitted', 'path': 'screenshots/form-submitted.png'}]
    page.screenshot.assert_called_once_with(path=str(tmp_path / 'screenshots/form-submitted.png'), full_page=True, timeout=10_000)


@pytest.mark.parametrize('failure,kind', [('navigation', 'navigation'), ('http', 'navigation'), ('selector', 'missing_selector'), ('submit', 'submission'), ('result', 'unexpected_page_state'), ('action', 'form_interaction')])
def test_form_failure_stops_and_sanitizes(tmp_path, failure, kind):
    page, controls = fake_page()
    if failure == 'navigation':
        page.goto.side_effect = Error('private diagnostics')
    elif failure == 'http':
        page.goto.return_value.ok = False
    elif failure == 'selector':
        controls[form.SELECTORS['text']].wait_for.side_effect = TimeoutError('private diagnostics')
    elif failure == 'submit':
        controls[form.SELECTORS['submit']].click.side_effect = Error('private diagnostics')
    elif failure == 'action':
        controls['form'].get_attribute.side_effect = None
        controls['form'].get_attribute.return_value = 'https://example.com/'
    else:
        controls['#message'].inner_text.return_value = 'Unexpected access barrier'
    steps, screenshots = [], []
    with pytest.raises(WorkflowFailure) as raised:
        form.run_workflow(page, tmp_path, steps, screenshots)
    assert raised.value.kind == kind
    assert 'private diagnostics' not in str(raised.value)
    assert steps[-1]['status'] == 'failed'
    assert screenshots == []
    page.screenshot.assert_not_called()
    if failure == 'action':
        controls[form.SELECTORS['submit']].click.assert_not_called()


@pytest.mark.parametrize('command,runner', [('form-demo', 'run_form_demo'), ('demo', 'run_demo')])
def test_cli_dispatch_preserves_commands(monkeypatch, tmp_path, command, runner):
    run = MagicMock(return_value=0)
    monkeypatch.setattr(cli, runner, run)
    assert cli.main([command, '--artifacts-dir', str(tmp_path)]) == 0
    run.assert_called_once_with(tmp_path)


def test_form_report_identity_and_failure(monkeypatch, tmp_path):
    @contextmanager
    def page():
        yield MagicMock()
    def fail(*args):
        raise WorkflowFailure('navigation', 'Could not navigate to the public Selenium form')
    monkeypatch.setattr(cli, 'chromium_page', page)
    monkeypatch.setattr(form, 'run_workflow', fail)
    assert cli.run_form_demo(tmp_path) == 1
    report = json.loads(next(tmp_path.glob('*/report.json')).read_text())
    assert report['workflow'] == 'selenium_form'
    assert report['target_url'] == form.TARGET_URL
    assert report['error']['type'] == 'navigation'
    assert report['result'] is None
