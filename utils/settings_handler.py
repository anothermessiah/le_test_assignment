from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict

from playwright.sync_api import Page

from constants.constants import (
    CONFIG_PATH,
    SUPPORTED_BROWSERS,
    DEFAULT_ENV,
    DEFAULT_BROWSER,
    DEFAULT_HEADLESS,
    DEFAULT_TIMEOUT_MS,
)


@dataclass
class Settings:
    env: str
    base_url: str
    browser: str
    headless: bool


def load_config_file() -> Dict[str, Any]:
    """
    Load JSON config with environment profiles.
    Returns empty dict if config file does not exist.
    """
    if not CONFIG_PATH.exists():
        return {}

    try:
        with CONFIG_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON config at {CONFIG_PATH}: {e}") from e


def build_settings(pytestconfig) -> Settings:
    """
    Resolve final Settings using:

    1) Environment name from CLI: --env-name (preferred)
       If not provided, DEFAULT_ENV is used.

    2) Environment profile from config/config.json:
       {
         "local": { "base_url": "...", "browser": "...", "headless": true },
         ...
       }

    3) Optional overrides from CLI:
       --app-base-url  (overrides profile's base_url)
       --app-browser   (overrides profile's browser)
       --app-headed    (forces headed mode, overrides 'headless' flag)
    """
    raw_cfg = load_config_file()

    # 1) Resolve environment name
    env_cli = pytestconfig.getoption("--env-name")
    env = env_cli or DEFAULT_ENV

    env_cfg: Dict[str, Any] = raw_cfg.get(env, {})
    if not env_cfg:
        raise RuntimeError(
            f"Environment '{env}' is not defined in {CONFIG_PATH}. "
            "Please add it to config.json or choose another env-name."
        )

    # 2) base_url: CLI override or value from profile
    base_url_cli = pytestconfig.getoption("--app-base-url")
    base_url_cfg = env_cfg.get("base_url")
    base_url = base_url_cli or base_url_cfg
    if not base_url:
        raise RuntimeError(
            "Base URL is not provided. "
            "Pass --app-base-url or define 'base_url' "
            f"for environment '{env}' in {CONFIG_PATH}."
        )

    # 3) browser: CLI override or value from profile or default
    browser_cli = pytestconfig.getoption("--app-browser")
    browser_cfg = env_cfg.get("browser", DEFAULT_BROWSER)
    browser = (browser_cli or browser_cfg).lower()
    if browser not in SUPPORTED_BROWSERS:
        raise RuntimeError(
            f"Unsupported browser '{browser}'. "
            f"Supported values: {', '.join(sorted(SUPPORTED_BROWSERS))}"
        )

    # 4) headless: profile or default, overridden by --app-headed if set
    headed_cli = pytestconfig.getoption("--app-headed")
    headless_cfg = bool(env_cfg.get("headless", DEFAULT_HEADLESS))

    if headed_cli is True:
        headless = False
    else:
        headless = headless_cfg

    return Settings(
        env=env,
        base_url=base_url,
        browser=browser,
        headless=headless,
    )


# ---------- generic helpers for Page Objects ----------


def open_relative(page: Page, path: str) -> None:
    """
    Open URL relative to base_url configured in browser context.
    """
    page.goto(path)


def assert_title_contains(page: Page, fragment: str) -> None:
    """
    Assert that current page title contains the given fragment.
    """
    title = page.title()
    assert fragment in title, (
        f"Expected page title to contain '{fragment}', "
        f"but got '{title}'."
    )


def wait_for_url_contains(page: Page, fragment: str, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:
    """
    Wait until current URL contains the given fragment.
    """
    page.wait_for_url(f"**{fragment}**", timeout=timeout_ms)
