from click.testing import CliRunner

import pytest

from automonkeytype.browser import BrowserManager
from automonkeytype.cli import main
from automonkeytype.scraper import MonkeyTypeScraper
from automonkeytype import browser as browser_module
from automonkeytype import engine as engine_module
from automonkeytype import scraper as scraper_module


pytestmark = pytest.mark.integration


EXPECTED_WORDS = [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "eta",
    "theta",
    "iota",
    "kappa",
]


def test_browser_manager_and_scraper_load_local_fixture(
    chromium_available, monkeytype_fixture_url
):
    manager = BrowserManager(headless=True)
    try:
        page = manager.launch()
        manager.navigate(monkeytype_fixture_url)
        scraper = MonkeyTypeScraper(page)
        scraper.dismiss_popups()
        scraper.wait_for_test_ready(timeout=5000)

        assert scraper.get_all_words() == EXPECTED_WORDS
        assert scraper.get_active_word() == EXPECTED_WORDS[0]
        assert scraper.get_active_word_index() == 0
    finally:
        manager.close()


def test_fixture_requires_focus_before_typing(
    chromium_available, monkeytype_fixture_url
):
    manager = BrowserManager(headless=True)
    try:
        page = manager.launch()
        manager.navigate(monkeytype_fixture_url)
        scraper = MonkeyTypeScraper(page)
        scraper.wait_for_test_ready(timeout=5000)

        page.keyboard.type(EXPECTED_WORDS[0])
        page.keyboard.press("Space")
        assert scraper.get_active_word_index() == 0

        scraper.focus_input()
        page.keyboard.type(EXPECTED_WORDS[0])
        page.keyboard.press("Space")
        assert scraper.get_active_word_index() == 1
    finally:
        manager.close()


def test_cli_completes_local_fixture_end_to_end(
    chromium_available, monkeytype_fixture_url, monkeypatch
):
    def navigate_to_fixture(self, url="https://monkeytype.com"):
        if self._page is None:
            raise RuntimeError("Browser not launched — call launch() first")
        self._page.goto(monkeytype_fixture_url, wait_until="networkidle", timeout=5000)

    monkeypatch.setattr(browser_module.BrowserManager, "navigate", navigate_to_fixture)
    monkeypatch.setattr(engine_module.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(scraper_module.time, "sleep", lambda _seconds: None)

    result = CliRunner().invoke(
        main,
        ["--wpm", "180", "--mode", "words", "--count", "50", "--headless"],
    )

    assert result.exit_code == 0, result.output
    assert "Extracted 50 words" in result.output
    assert "Results" in result.output
    assert any(
        "Accuracy:" in line and "100%" in line
        for line in result.output.splitlines()
    ), result.output
    assert "Characters:" in result.output
    assert "/0/0/0" in result.output
    assert "Done." in result.output
