from playwright.sync_api import Page


def test_console_errors(page: Page, base_url: str) -> None:
    console_messages = []
    page_errors = []

    def handle_console(msg):
        console_messages.append(msg)

    page.on("console", handle_console)
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))

    page.goto(base_url, wait_until="networkidle")

    error_messages = []
    for msg in console_messages:
        if msg.type == "error":
            loc = msg.location or {}
            url = loc.get("url", "<unknown>")
            line = loc.get("lineNumber", "?")
            col = loc.get("columnNumber", "?")
            error_messages.append(
                f"[console.error] {msg.text} ({url}:{line}:{col})"
            )

    if page_errors:
        error_messages.append(
            "\n".join(f"[pageerror] {e}" for e in page_errors)
        )

    assert not error_messages, (
        "Найдены ошибки в консоли/на странице:\n" + "\n".join(error_messages)
    )
