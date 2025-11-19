from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright

from utils.settings_handler import Settings, build_settings


def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Define custom CLI options for environment configuration.

    Names are prefixed with 'app-' to avoid conflicts with 3rd-party plugins.
    """
    group = parser.getgroup("env config")

    group.addoption(
        "--env-name",
        action="store",
        default=None,
        help="Environment name: local | staging | prod.",
    )
    group.addoption(
        "--app-base-url",
        action="store",
        default=None,
        help="Override base URL for the selected environment.",
    )
    group.addoption(
        "--app-browser",
        action="store",
        default=None,
        help="Override browser: chromium | firefox | webkit.",
    )
    group.addoption(
        "--app-headed",
        action="store_true",
        default=None,
        help="Run browser in headed mode.",
    )


@pytest.fixture(scope="session")
def settings(pytestconfig) -> Settings:
    """
    Session-scoped settings object with resolved config.
    """
    return build_settings(pytestconfig)


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance, settings: Settings):
    browser_type = getattr(playwright_instance, settings.browser)
    browser = browser_type.launch(headless=settings.headless)
    yield browser
    browser.close()


@pytest.fixture
def page(browser, settings: Settings):
    context = browser.new_context(base_url=settings.base_url)
    page = context.new_page()
    yield page
    context.close()
