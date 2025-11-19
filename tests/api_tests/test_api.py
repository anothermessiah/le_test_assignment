from __future__ import annotations

from urllib.parse import urljoin

from utils.settings_handler import Settings


def test_all_links_return_ok_or_redirect(page, settings: Settings):
    """
    As a tester, I want to check that all links on the home page
    return 2xx or 3xx status codes, and no 4xx responses.
    """
    # UI navigation uses base_url from config via browser context
    page.goto(settings.base_url)

    # Collect relative href attributes from all anchor tags
    hrefs = page.eval_on_selector_all(
        "a[href]",
        "els => els.map(e => e.getAttribute('href'))",
    )
    unique_hrefs = sorted({h for h in hrefs if h})

    assert unique_hrefs, "No links were found on the home page."

    for href in unique_hrefs:
        # Build full URL using base_url from settings
        full_url = urljoin(settings.base_url, href)

        response = page.request.get(full_url)
        status = response.status

        assert 200 <= status < 400, (
            f"Link '{full_url}' returned unexpected status code {status}. "
            "Expected 2xx or 3xx."
        )
