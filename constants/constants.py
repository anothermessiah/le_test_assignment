from __future__ import annotations

from enum import Enum
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Environment(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PROD = "prod"


# Mapping between environment and base URL
ENV_BASE_URLS: dict[Environment, str] = {
    Environment.LOCAL: "http://localhost:4000/fashionhub/",
    Environment.STAGING: "https://staging-env/fashionhub/",
    Environment.PROD: "https://pocketaces2.github.io/fashionhub/",
}

SUPPORTED_BROWSERS = {"chromium", "firefox", "webkit"}

DEFAULT_ENV: Environment = Environment.PROD
DEFAULT_BROWSER = "chromium"
DEFAULT_HEADLESS = True

DEFAULT_TIMEOUT_MS = 5_000
