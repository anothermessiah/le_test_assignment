# LuxExperience Test Assignment – Playwright UI/API tests

This repository contains a small, production-like test framework built with:

- Python
- Playwright
- pytest

It targets the **Fashionhub** demo site and implements:

- UI tests for the login flow
- An API-style test that checks all links on the home page return valid status codes
- A test that checks browser console for errors on key pages
- A helper script that lists open GitHub pull requests in CSV format

Configuration is done via **command-line options** with sane defaults defined in Python code (no external JSON config file is required).

---

## 1. Project structure

From the repository root:

```text
le_test_assignment/
├─ constants/
│  └─ constants.py          # Infra constants, environment enum, base URLs, defaults
├─ scripts/
│  └─ get_pull_requests.py  # Script to fetch open PRs and print CSV
├─ src/
│  ├─ __init__.py
│  └─ pages/
│     ├─ __init__.py
│     ├─ base_page.py       # Base Page Object for Playwright pages
│     └─ login_page.py      # Page Object for the login screen
├─ utils/
│  ├─ __init__.py
│  └─ setting_handler.py    # Settings dataclass + CLI/config resolver
├─ tests/
│  ├─ api_tests/
│  │  └─ test_api.py        # Link status-code test for the home page
│  └─ web_tests/
│     ├─ test_console_errors.py  # Console error checks
│     └─ test_login.py           # Login tests (valid and invalid credentials)
├─ .gitignore
├─ pytest.ini
├─ requirements.txt
└─ README.md
```

### Key modules

- `constants/constants.py`
  - `Environment` enum (e.g. `local`, `staging`, `prod`)
  - Mapping `ENV_BASE_URLS` from environment to base URL
  - Defaults (`DEFAULT_ENV`, `DEFAULT_BROWSER`, `DEFAULT_HEADLESS`, etc.)
- `utils/setting_handler.py`
  - `Settings` dataclass (`env`, `base_url`, `browser`, `headless`)
  - `build_settings(pytest_config)` that merges CLI options with defaults from `constants`
- `src/pages/base_page.py`
  - Common base class for page objects, holds a Playwright `Page` instance and shared helpers
- `src/pages/login_page.py`
  - Page Object for the login page (locators + high-level actions + assertions)
- `tests/api_tests/test_api.py`
  - Walks through all links on the home page and verifies status codes are 2xx or 3xx
- `tests/web_tests/test_login.py`
  - Verifies that login succeeds with valid credentials
  - Verifies that a proper error is shown for invalid credentials
- `tests/web_tests/test_console_errors.py`
  - Asserts there are no unexpected JavaScript errors in the browser console on selected pages
- `scripts/get_pull_requests.py`
  - Helper script that fetches open pull requests for a GitHub repository and prints CSV:
    `title, created_at, author`

---

## 2. Requirements

- Python **3.9+**
- `pip`
- Playwright browsers (installed separately)

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

`requirements.txt` contains at least:

- `pytest` – test runner
- `playwright` – browser automation library
- `requests` – HTTP client (used by the helper script)

No external pytest plugins are required; Playwright integration is implemented via fixtures in `tests/conftest.py`.

---

## 4. Environment configuration

Environment configuration is handled entirely in Python, without `config.json`.

### 4.1. Environments and base URLs

`constants/constants.py` defines:

- `Environment` – an enum with values like:
  - `LOCAL`
  - `STAGING`
  - `PROD`
- `ENV_BASE_URLS` – a dictionary mapping each `Environment` to a base URL, for example:

  ```python
  ENV_BASE_URLS = {
      Environment.LOCAL:   "http://localhost:4000/fashionhub/",
      Environment.STAGING: "https://staging-env/fashionhub/",
      Environment.PROD:    "https://pocketaces2.github.io/fashionhub/",
  }
  ```

- Defaults:

  ```python
  DEFAULT_ENV = Environment.PROD
  DEFAULT_BROWSER = "chromium"
  DEFAULT_HEADLESS = True
  ```

These act as the **config file layer**: if no CLI overrides are provided, the framework uses these values.

### 4.2. CLI options

Custom CLI options are defined in `tests/conftest.py` via `pytest_addoption`:

- `--env-name` – environment profile name (`local`, `staging`, `prod`)
- `--app-base-url` – override base URL for the selected environment
- `--app-browser` – override browser (`chromium`, `firefox`, `webkit`)
- `--app-headed` – run browser in headed mode (overrides headless default)

### 4.3. Resolution and precedence

`utils.setting_handler.build_settings()` builds a `Settings` object using the following precedence:

1. **CLI options** (highest priority)
   - `--env-name`
   - `--app-base-url`
   - `--app-browser`
   - `--app-headed`
2. **Defaults from `constants/constants.py`**
   - `DEFAULT_ENV` to pick the environment profile
   - `ENV_BASE_URLS[env]` for `base_url`
   - `DEFAULT_BROWSER` if no browser override is provided
   - `DEFAULT_HEADLESS` if `--app-headed` is not used

If a required value (e.g. `base_url` for a selected env) is missing from the mapping, the test run fails fast with a clear error.

### 4.4. Examples

```bash
# Run against default environment (DEFAULT_ENV, typically prod)
pytest

# Explicitly select environment profile
pytest --env-name=local
pytest --env-name=staging
pytest --env-name=prod

# Override base URL and browser for a given env
pytest --env-name=prod --app-base-url=https://custom-host/fashionhub/
pytest --env-name=staging --app-browser=firefox

# Force headed mode
pytest --env-name=local --app-headed
```

---

## 5. Fixtures and Playwright lifecycle

Core fixtures are defined in `tests/conftest.py`:

- `settings` (session scope)
  - Returns a `Settings` instance built from CLI + defaults
- `playwright_instance` (session scope)
  - Starts/stops Playwright (`sync_playwright().start()` / `.stop()`)
- `browser` (session scope)
  - Creates a browser instance using `settings.browser`
- `page` (function scope)
  - Creates a new browser context and page per test:

    ```python
    context = browser.new_context(base_url=settings.base_url)
    page = context.new_page()
    ```

Because `base_url` is configured at the context level, tests and Page Objects can use **relative paths**, for example:

```python
page.goto("/login.html")
```

instead of hardcoding the full URL.

---

## 6. Implemented tests

### 6.1. API-style link test

File: `tests/api_tests/test_api.py`

- Opens the home page (`"/"`).
- Collects all anchor tags with `href` attributes.
- Normalizes and deduplicates links.
- For each link:
  - builds an absolute URL using `settings.base_url`
  - performs `page.request.get(url)`
  - asserts that the HTTP status code is **2xx or 3xx** (no 4xx).

This checks that the site has no broken links from the home page.

### 6.2. Login UI tests

File: `tests/web_tests/test_login.py`  
Page object: `src/pages/login_page.py`

Scenarios:

1. **Valid login**

   - Opens the login page.
   - Enters the provided valid credentials (as per assignment, e.g. `demouser` / `fashion123`).
   - Submits the form.
   - Asserts that login is successful (using page-level assertions in `LoginPage`).

2. **Invalid login**

   - Opens the login page.
   - Enters deliberately incorrect credentials.
   - Submits the form.
   - Asserts that an appropriate error is displayed and login does not succeed.

The test code itself stays clean by delegating locators and interactions to the `LoginPage` Page Object.

### 6.3. Console error checks

File: `tests/web_tests/test_console_errors.py`

- Navigates to relevant pages of the application.
- Listens to Playwright `console` events.
- Asserts that there are no unexpected errors (for example, no `error`-level messages in the browser console).

This helps ensure the UI is free from obvious JavaScript errors.

---

## 7. GitHub pull requests script

File: `scripts/get_pull_requests.py`

This script solves an additional task:

> As a product owner, I want to see how many open pull requests are there for our product, and get them as a CSV list with PR name, created date, and author.

Key points:

- Uses the GitHub public API and the `requests` library.
- Fetches **open pull requests** for a given repository (by default the script targets `https://github.com/appwrite/appwrite/pulls` as per the assignment).
- Prints a CSV to stdout with columns:

  ```text
  title,created_at,author
  ```

To run the script:

```bash
# From project root
python scripts/get_pull_requests.py
```

If you need a different repository, adjust its owner/name directly in the script (or add CLI options if required).

---

## 8. Extending the framework

### 8.1. Adding a new page

1. Create a new file under `src/pages/`, e.g. `product_page.py`.
2. Inherit from `BasePage`.
3. Define locators as class attributes and actions/assertions as methods.

Example sketch:

```python
from src.pages.base_page import BasePage

class ProductPage(BasePage):
    _PRODUCT_CARD = ".product-card"
    _ADD_TO_CART = "button.add-to-cart"

    def open(self) -> None:
        self.page.goto("/products.html")

    def add_first_product_to_cart(self) -> None:
        self.page.click(f"{self._PRODUCT_CARD}:nth-of-type(1) {self._ADD_TO_CART}")
```

### 8.2. Adding new tests

1. Create a new file under `tests/web_tests/` or `tests/api_tests/`.
2. Use existing fixtures: `page`, `settings`.
3. Import and use the appropriate Page Object classes from `src.pages`.

Example:

```python
from src.pages.product_page import ProductPage
from utils.setting_handler import Settings

def test_add_to_cart_flow(page, settings: Settings) -> None:
    product_page = ProductPage(page)
    product_page.open()
    product_page.add_first_product_to_cart()
    # add assertions here
```

The current structure and configuration logic are designed to be easily extensible for additional scenarios and page objects without changing the core framework.
