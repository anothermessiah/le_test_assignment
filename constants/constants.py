from __future__ import annotations

from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"

# Environments and browsers
SUPPORTED_BROWSERS = {"chromium", "firefox", "webkit"}
DEFAULT_ENV = "prod"
DEFAULT_BROWSER = "chromium"
DEFAULT_HEADLESS = True

# Timeouts
DEFAULT_TIMEOUT_MS = 5000
