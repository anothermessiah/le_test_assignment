# Lux Experience Test Assignment – Playwright UI/API tests

This repository contains a small, production-like test framework built with:

- Python
- Playwright
- pytest

It targets the **Fashionhub** demo site and implements:

- UI tests for the login flow
- API-style test that checks all links on the home page return valid status codes
- Configurable environments (local / staging / prod) via CLI or config file
- Simple Page Object pattern for web tests

---

## 1. Project structure

```text
lux_experience_test_assignment/
├─ config/
│  └─ config.json
├─ constants/
│  └─ constants.py
├─ scripts/
│  └─ get_pull_requests.py
├─ src/
│  ├─ __init__.py
│  └─ pages/
│     ├─ __init__.py
│     ├─ base_page.py
│     └─ login_page.py
├─ utils/
│  ├─ __init__.py
│  └─ setting_handler.py
├─ tests/
│  ├─ api_tests/
│  │  └─ test_api.py
│  └─ web_tests/
│     ├─ test_console_errors.py
│     └─ test_login.py
├─ pytest.ini
├─ requirements.txt
└─ README.md
```

Key modules:

- `config/config.json` – environment profiles (local / staging / prod)
- `constants/constants.py` – infra constants (project root, config path, default env, supported browsers)
- `utils/setting_handler.py` – configuration resolver:
  - loads `config.json`
  - merges CLI options with config values
  - exposes `Settings` dataclass and helper functions
- `scripts/get_pull_requests` – script for getting pull requests for a Github project
- `src/pages/base_page.py` – base Page Object for Playwright pages
- `src/pages/login_page.py` – Page Object for the login screen
- `tests/api_tests/test_api.py` – link status code test for home page
- `tests/web_tests/test_console_errors.py` – tests for console errors
- `tests/web_tests/test_login.py` – login tests (valid and invalid credentials)

---

## 2. Requirements

- Python 3.9+
- `pip`
- Playwright browsers (installed via `playwright install`)

---

## 3. Installation

From the project root:

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scriptsctivate         # Windows PowerShell

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers (Chromium, Firefox, WebKit)
python -m playwright install
```

`requirements.txt` contains:

- `requests` – library for HTTP requests
- `pytest` – test runner
- `playwright` – browser automation library

No external pytest plugins are required; integration is implemented in `tests/conftest.py`.

---

## 4. Environment configuration

Environment profiles are defined in `config/config.json`:

```json
{
  "local": {
    "base_url": "http://localhost:4000/fashionhub/",
    "browser": "chromium",
    "headless": true
  },
  "staging": {
    "base_url": "https://staging-env/fashionhub/",
    "browser": "chromium",
    "headless": true
  },
  "prod": {
    "base_url": "https://pocketaces2.github.io/fashionhub/",
    "browser": "chromium",
    "headless": true
  }
}
```

Each profile defines:

- `base_url` – application base URL
- `browser` – `chromium`, `firefox`, or `webkit`
- `headless` – whether to run Playwright in headless mode

Default environment is `prod` (see `DEFAULT_ENV` in `utils/constants.py`).

---

## 5. CLI options vs config file (precedence)

Custom CLI options are defined in `tests/conftest.py` via `pytest_addoption`:

- `--env-name` – environment profile name (`local`, `staging`, `prod`)
- `--app-base-url` – override `base_url` from config
- `--app-browser` – override `browser` from config
- `--app-headed` – run browser in headed mode (overrides `headless` from config)

Final `Settings` are built in `utils.setting_handler.build_settings()` using the following precedence:

1. **CLI options (preferred)**:
   - `--env-name`
   - `--app-base-url`
   - `--app-browser`
   - `--app-headed`
2. **Config file** (`config/config.json`):
   - `env-name` selects an environment profile
   - profile values are used when CLI overrides are not provided
3. **Defaults** from `utils/constants.py`:
   - `DEFAULT_ENV`, `DEFAULT_BROWSER`, `DEFAULT_HEADLESS`

If a required value (e.g. `base_url`) is missing both from CLI and config, the test run fails fast with a clear error message.

Examples:

```bash
# Run against default env (prod)
pytest

# Explicitly select environment profile
pytest --env-name=local
pytest --env-name=staging
pytest --env-name=prod

# Override base URL and browser for a given env
pytest --env-name=prod --app-base-url=https://custom-host/fashionhub/
pytest --env-name=staging --app-browser=firefox

# Force headed mode for local env
pytest --env-name=local --app-headed
```

---

## 6. Fixtures and browser lifecycle

`tests/conftest.py` defines core fixtures:

- `settings` (session scope) – resolved `Settings` object
- `playwright_instance` (session scope) – raw Playwright instance (`sync_playwright()`)
- `browser` (session scope) – browser instance (`chromium` / `firefox` / `webkit`)
- `page` (function scope) – new browser context and page per test

`page` is created as:

```python
context = browser.new_context(base_url=settings.base_url)
page = context.new_page()
```

So navigation within tests and Page Objects can use relative paths such as `"login.html"`.

---

## 7. How to run tests

From project root:

```bash
# All tests
pytest

# Only API/link tests
pytest tests/api_tests/test_api.py

# Only web/login tests
pytest tests/web_tests/test_login.py

# Run tests against a different environment
pytest --env-name=local
pytest --env-name=staging --app-headed
```

---

## 8. Extending the framework

To add a new page:

1. Create a new file under `src/pages/`, e.g. `product_page.py`.
2. Inherit from `BasePage`.
3. Define page-specific locators and methods.

To add new tests:

1. Create a new file under `tests/web_tests/` or `tests/api_tests/`.
2. Use existing fixtures: `page`, `settings`.
3. Import and use the appropriate Page Object classes from `src.pages`.

The current structure and configuration logic are designed to be easily extensible for new features and test cases.
