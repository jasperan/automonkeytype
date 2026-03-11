"""Browser lifecycle management with anti-detection stealth.

Launches a Playwright Chromium instance configured to evade basic
bot-detection: randomized viewport, spoofed navigator properties,
rotated user agents, and disabled automation flags.
"""

import random
from typing import Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
]

_STEALTH_SCRIPT = """
// Remove webdriver flag
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// Fake plugins array (real browsers have plugins)
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5],
});

// Fake languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
});

// Fake chrome runtime (present in real Chrome)
window.chrome = { runtime: {}, loadTimes: () => {}, csi: () => {} };

// Spoof permissions query
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) =>
    parameters.name === 'notifications'
        ? Promise.resolve({ state: Notification.permission })
        : originalQuery(parameters);
"""


class BrowserManager:
    """Manages a stealth Playwright browser session."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self._pw = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    def launch(self) -> Page:
        """Launch browser and return the page object."""
        self._pw = sync_playwright().start()

        # Randomize viewport for fingerprint diversity
        width = random.randint(1280, 1920)
        height = random.randint(800, 1080)

        self._browser = self._pw.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                f"--window-size={width},{height}",
                "--disable-dev-shm-usage",
            ],
        )

        self._context = self._browser.new_context(
            viewport={"width": width, "height": height},
            user_agent=random.choice(_USER_AGENTS),
            locale="en-US",
            timezone_id="America/New_York",
        )

        # Inject stealth patches before any page script runs
        self._context.add_init_script(_STEALTH_SCRIPT)

        self._page = self._context.new_page()
        return self._page

    def navigate(self, url: str = "https://monkeytype.com"):
        """Navigate to MonkeyType and wait for network idle."""
        if self._page is None:
            raise RuntimeError("Browser not launched — call launch() first")
        self._page.goto(url, wait_until="networkidle", timeout=30000)

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Browser not launched — call launch() first")
        return self._page

    def close(self):
        """Tear down browser resources."""
        for resource in (self._context, self._browser):
            if resource:
                try:
                    resource.close()
                except Exception:
                    pass
        if self._pw:
            try:
                self._pw.stop()
            except Exception:
                pass
