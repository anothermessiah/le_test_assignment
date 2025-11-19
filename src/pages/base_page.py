from playwright.sync_api import Page


class BasePage:
    """
    Common base class for all page objects.
    """
    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, path: str) -> None:
        """
        Open a URL using a path relative to the Playwright context base_url.
        """
        self.page.goto(path)
