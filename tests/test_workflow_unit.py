"""Offline checks for deterministic steps and clear, sanitized failures."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from playwright.sync_api import Error, TimeoutError

from browser_task_runner.extraction import validate_inventory
from browser_task_runner.workflows.saucedemo import WorkflowFailure, run_workflow


def test_inventory_validation():
    assert validate_inventory('Swag Labs', ' Products ') == {
        'page_title': 'Swag Labs', 'inventory_heading': 'Products'}


@pytest.mark.parametrize('title,heading', [('Wrong', 'Products'), ('Swag Labs', ''), ('Swag Labs', 'Cart')])
def test_inventory_validation_rejects_unexpected_state(title, heading):
    with pytest.raises(ValueError):
        validate_inventory(title, heading)


def page_mock():
    page = MagicMock()
    page.url = 'https://www.saucedemo.com/'
    page.goto.return_value.ok = True
    page.title.return_value = 'Swag Labs'
    page.locator.return_value.inner_text.return_value = 'Products'
    return page


def test_ordered_workflow(tmp_path):
    page = page_mock()
    steps, screenshots = [], []
    result = run_workflow(page, tmp_path, steps, screenshots)
    assert result['inventory_heading'] == 'Products'
    assert [s['name'] for s in steps] == [
        'navigate', 'login', 'verify_inventory', 'capture_inventory', 'extract_inventory']
    assert all(s['status'] == 'success' for s in steps)
    assert screenshots == [{'name': 'inventory', 'path': 'screenshots/inventory.png'}]
    page.screenshot.assert_called_once_with(
        path=str(tmp_path / 'screenshots/inventory.png'), full_page=True, timeout=10_000)


@pytest.mark.parametrize('failure,kind', [('navigation', 'navigation'), ('selector', 'missing_selector'), ('state', 'unexpected_page_state'), ('http', 'navigation'), ('redirect', 'unexpected_page_state')])
def test_failure_stops_workflow(tmp_path, failure, kind):
    page = page_mock()
    if failure == 'navigation':
        page.goto.side_effect = Error('sensitive browser diagnostics')
    elif failure == 'selector':
        page.locator.return_value.wait_for.side_effect = TimeoutError('private data')
    elif failure == 'state':
        page.wait_for_url.side_effect = TimeoutError('private data')
    elif failure == 'http':
        page.goto.return_value.ok = False
    else:
        page.url = 'https://example.com/'
    steps, screenshots = [], []
    with pytest.raises(WorkflowFailure) as raised:
        run_workflow(page, tmp_path, steps, screenshots)
    assert raised.value.kind == kind
    assert 'private data' not in str(raised.value)
    assert steps[-1]['status'] == 'failed'
    assert screenshots == []
    page.screenshot.assert_not_called()
