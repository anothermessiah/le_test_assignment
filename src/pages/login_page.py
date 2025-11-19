from playwright.sync_api import expect

from src.pages.base_page import BasePage


class LoginPage(BasePage):
    """
    Page Object for the Fashionhub login page.
    """

    # Page-specific data
    _PATH = "login.html"  # NOTE: no leading slash

    # Test data (valid credentials from the assignment)
    _VALID_USERNAME = "demouser"
    _VALID_PASSWORD = "fashion123"

    # Locators (page-specific)
    _USERNAME_INPUT = "#username"
    _PASSWORD_INPUT = "#password"
    _SUBMIT_BUTTON = "input[type=\"submit\"]"
    _ERROR_MESSAGE = ".error-message"

    # Expected texts
    _ERROR_TEXT_FRAGMENT = "Invalid username or password"

    def open(self) -> None:  # type: ignore[override]
        super().open(self._PATH)

    def fill_credentials(self, username: str, password: str) -> None:
        self.page.fill(self._USERNAME_INPUT, username)
        self.page.fill(self._PASSWORD_INPUT, password)

    def submit(self) -> None:
        self.page.locator(self._SUBMIT_BUTTON).click()

    def login(self, login = _VALID_USERNAME, password = _VALID_PASSWORD) -> None:
        self.fill_credentials(login, password)
        self.submit()

    def assert_login_failed(self) -> None:
        error = self.page.locator(self._ERROR_MESSAGE)
        expect(error).to_contain_text(self._ERROR_TEXT_FRAGMENT)

    def assert_login_succeeded(self) -> None:
        # Adjust this to real success criteria (URL, header, user menu, etc.)
        assert "login" not in self.page.url
