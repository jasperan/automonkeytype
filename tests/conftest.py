from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


class QuietRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # pragma: no cover
        pass


def _chromium_launch_skip_reason(message: str) -> str | None:
    normalized = message.lower()

    if "executable doesn't exist" in normalized or "download new browsers" in normalized:
        return (
            "Chromium is not installed. Run 'playwright install chromium' before "
            "running browser-backed tests."
        )

    if any(
        hint in normalized
        for hint in (
            "host system is missing dependencies",
            "install-deps",
            "missing libraries",
            "error while loading shared libraries",
            "cannot open shared object file",
            "running as root without --no-sandbox",
            "no usable sandbox",
            "setuid sandbox",
            "crbug.com/638180",
        )
    ):
        return (
            "Chromium could not launch in this environment. Install the required "
            "Playwright OS dependencies/shared libraries (usually "
            "'playwright install-deps chromium') or fix the browser "
            "sandbox/runtime setup before running browser-backed tests."
        )

    return None


def _playwright_launch_error_detail(message: str) -> str:
    lines = [line.strip() for line in message.splitlines() if line.strip()]
    for line in lines:
        normalized = line.lower()
        if any(
            hint in normalized
            for hint in (
                "executable doesn't exist",
                "download new browsers",
                "dependencies",
                "install-deps",
                "shared libr",
                "shared object file",
                "sandbox",
            )
        ):
            return line
    return lines[0] if lines else "unknown Playwright launch error"


@pytest.fixture(scope="session")
def chromium_available():
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            browser.close()
    except PlaywrightError as exc:
        message = str(exc)
        skip_reason = _chromium_launch_skip_reason(message)
        if skip_reason:
            pytest.skip(
                f"{skip_reason} Playwright said: {_playwright_launch_error_detail(message)}"
            )
        raise


@pytest.fixture(scope="session")
def monkeytype_fixture_url():
    fixtures_dir = Path(__file__).parent / "fixtures"
    handler = partial(QuietRequestHandler, directory=str(fixtures_dir))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        port = server.server_address[1]
        yield f"http://127.0.0.1:{port}/monkeytype_fixture.html"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
