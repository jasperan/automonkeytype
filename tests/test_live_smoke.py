import os

import pytest

from automonkeytype.browser import BrowserManager
from automonkeytype.scraper import MonkeyTypeScraper


pytestmark = [pytest.mark.live, pytest.mark.slow]


@pytest.mark.skipif(
    os.getenv("AUTOMONKEYTYPE_RUN_LIVE") != "1",
    reason="Set AUTOMONKEYTYPE_RUN_LIVE=1 to run the live monkeytype.com smoke test.",
)
def test_live_monkeytype_words_load(chromium_available):
    manager = BrowserManager(headless=True)
    try:
        page = manager.launch()
        manager.navigate()
        scraper = MonkeyTypeScraper(page)
        scraper.dismiss_popups()
        scraper.wait_for_test_ready(timeout=15000)

        words = scraper.get_all_words()
        assert len(words) >= 10
        assert all(word for word in words[:10])
        assert scraper.get_active_word_index() == 0
    finally:
        manager.close()
