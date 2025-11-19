from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from _pytest.config import Config as PytestConfig

from constants.constants import (
    Environment,
    ENV_BASE_URLS,
    SUPPORTED_BROWSERS,
    DEFAULT_ENV,
    DEFAULT_BROWSER,
    DEFAULT_HEADLESS,
)


@dataclass(frozen=True)
class Settings:
    env: Environment
    base_url: str
    browser: str
    headless: bool


def _resolve_env(cli_env: Optional[str]) -> Environment:
    """
    Resolve environment name from CLI or fallback to DEFAULT_ENV.
    """
    if not cli_env:
        return DEFAULT_ENV

    name = cli_env.lower()
    try:
        return Environment(name)
    except ValueError:
        valid = ", ".join(e.value for e in Environment)
        raise ValueError(f"Unknown environment '{name}'. Supported values: {valid}")


def _resolve_browser(cli_browser: Optional[str]) -> str:
    """
    Resolve browser from CLI or fallback to DEFAULT_BROWSER.
    """
    if cli_browser:
        candidate = cli_browser.lower()
    else:
        candidate = DEFAULT_BROWSER

    if candidate not in SUPPORTED_BROWSERS:
        supported = ", ".join(sorted(SUPPORTED_BROWSERS))
        raise ValueError(
            f"Unsupported browser '{candidate}'. Supported browsers: {supported}"
        )
    return candidate


def _resolve_headless(cli_headed: bool) -> bool:
    """
    Resolve headless mode. CLI flag --app-headed has priority.
    """
    if cli_headed:
        return False
    return DEFAULT_HEADLESS


def build_settings(pytest_config: PytestConfig) -> Settings:
    """
    Build Settings from:
    1. CLI options
    2. defaults from constants
    """
    cli_env = pytest_config.getoption("--env-name")
    cli_browser = pytest_config.getoption("--app-browser")
    cli_headed = bool(pytest_config.getoption("--app-headed"))
    cli_base_url = pytest_config.getoption("--app-base-url")

    env = _resolve_env(cli_env)

    # base_url: CLI override > mapping from Environment
    if cli_base_url:
        base_url = cli_base_url
    else:
        base_url = ENV_BASE_URLS.get(env)
        if not base_url:
            raise RuntimeError(
                f"No base URL configured for environment '{env.value}'."
            )

    browser = _resolve_browser(cli_browser)
    headless = _resolve_headless(cli_headed)

    return Settings(
        env=env,
        base_url=base_url,
        browser=browser,
        headless=headless,
    )
