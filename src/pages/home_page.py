from src.pages.base_page import BasePage


class HomePage(BasePage):
    """
    Page Object for the Fashionhub home page.
    """

    # Page-specific data
    _PATH = "/"
    _TITLE_FRAGMENT = "FashionHub"

    def open(self) -> None:
        super().open(self._PATH)
