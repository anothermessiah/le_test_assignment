from src.pages.login_page import LoginPage
from utils.settings_handler import Settings


class TestLogin:

    def test_login_with_valid_credentials(self, page, settings: Settings):
        """
        As a customer, I want to verify I can log in with valid credentials.
        """
        login_page = LoginPage(page)
        login_page.open()
        login_page.login()
        login_page.assert_login_succeeded()


    def test_login_with_invalid_credentials(self, page):
        """
        As a customer, I want to see a proper error message
        when I enter invalid credentials.
        """
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("wrong-user", "wrong-pass")
        login_page.submit()
        login_page.assert_login_failed()
