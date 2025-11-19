from __future__ import annotations

from playwright.sync_api import Page

from utils.settings_handler import open_relative, assert_title_contains, wait_for_url_contains


class BasePage:
    """
    Base class for all page objects.
    """

    def __init__(self, page: Page):
        self.page = page

    def open(self, path: str) -> None:
        open_relative(self.page, path)

    def assert_title_contains(self, fragment: str) -> None:
        assert_title_contains(self.page, fragment)

    def wait_for_url_contains(self, fragment: str) -> None:
        wait_for_url_contains(self.page, fragment)
