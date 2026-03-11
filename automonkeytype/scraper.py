"""MonkeyType DOM interaction — word extraction, test control, result scraping.

Handles all direct interaction with the MonkeyType web interface:
reading words from the DOM, focusing the input area, detecting test
completion, configuring test mode, and scraping results.

Selectors are centralized here so they're easy to update if MonkeyType
changes its DOM structure.
"""

import time
from typing import Dict, List, Optional

from playwright.sync_api import Page


class MonkeyTypeScraper:
    """Reads and interacts with MonkeyType's DOM."""

    # --- Selectors (centralized for easy maintenance) ---
    SEL_WORDS_WRAPPER = "#words"
    SEL_WORD = "div.word"
    SEL_ACTIVE_WORD = "div.word.active"
    SEL_LETTER = "letter"
    SEL_CARET = "#caret"

    # Cookie / popup dismissal targets
    SEL_COOKIE_ACCEPT = [
        "button.acceptAll",
        "button#acceptAllCookies",
        ".cookie-popup .accept",
        "button:has-text('Accept all')",
        "button:has-text('I accept')",
    ]

    # Notification / banner close
    SEL_NOTIFICATIONS = [
        ".notification .close",
        "#bannerCenter .close",
        ".popupWrapper .close",
    ]

    # Results page
    SEL_RESULT = "#result"
    SEL_RESULT_WPM = "#result .group.wpm .bottom"
    SEL_RESULT_ACC = "#result .group.acc .bottom"
    SEL_RESULT_RAW = "#result .group.raw .bottom"
    SEL_RESULT_CHARS = "#result .group.key .bottom"

    # Config buttons
    SEL_MODE_BTN = 'button[mode="{mode}"]'
    SEL_WORDCOUNT_BTN = 'button[wordCount="{value}"]'
    SEL_TIMECOUNT_BTN = 'button[timeCount="{value}"]'
    SEL_RESTART_BTN = "#restartTestButton"

    def __init__(self, page: Page):
        self.page = page

    # --- Setup ---

    def wait_for_test_ready(self, timeout: float = 15000):
        """Wait until the typing test DOM is loaded."""
        self.page.wait_for_selector(self.SEL_WORDS_WRAPPER, timeout=timeout)
        self.page.wait_for_selector(self.SEL_WORD, timeout=timeout)

    def dismiss_popups(self):
        """Dismiss cookie banners, notifications, and overlays."""
        for selector in self.SEL_COOKIE_ACCEPT + self.SEL_NOTIFICATIONS:
            try:
                el = self.page.query_selector(selector)
                if el and el.is_visible():
                    el.click()
                    time.sleep(0.3)
            except Exception:
                pass

    def configure_test(self, mode: str = "words", value: str = "50"):
        """Click mode and value buttons to configure the test.

        Args:
            mode: One of 'words', 'time', 'quote', 'zen', 'custom'.
            value: Word count (for words mode) or seconds (for time mode).
        """
        # Click mode button
        mode_sel = self.SEL_MODE_BTN.format(mode=mode)
        btn = self.page.query_selector(mode_sel)
        if btn:
            btn.click()
            time.sleep(0.5)

        # Click value button
        for template in (self.SEL_WORDCOUNT_BTN, self.SEL_TIMECOUNT_BTN):
            val_sel = template.format(value=value)
            btn = self.page.query_selector(val_sel)
            if btn:
                btn.click()
                time.sleep(0.5)
                break

    def restart_test(self):
        """Press the restart button (Tab key works too)."""
        btn = self.page.query_selector(self.SEL_RESTART_BTN)
        if btn:
            btn.click()
            time.sleep(1)
        else:
            self.page.keyboard.press("Tab")
            time.sleep(1)

    # --- Word extraction ---

    def get_all_words(self) -> List[str]:
        """Extract all words from the current test."""
        words = []
        word_elements = self.page.query_selector_all(self.SEL_WORD)
        for word_el in word_elements:
            letters = word_el.query_selector_all(self.SEL_LETTER)
            word = "".join(letter.text_content() or "" for letter in letters)
            if word:
                words.append(word)
        return words

    def get_active_word(self) -> Optional[str]:
        """Get the currently active (being typed) word."""
        active = self.page.query_selector(self.SEL_ACTIVE_WORD)
        if not active:
            return None
        letters = active.query_selector_all(self.SEL_LETTER)
        return "".join(letter.text_content() or "" for letter in letters)

    def get_active_word_index(self) -> int:
        """Get the 0-based index of the active word."""
        words = self.page.query_selector_all(self.SEL_WORD)
        for i, word in enumerate(words):
            classes = word.get_attribute("class") or ""
            if "active" in classes:
                return i
        return -1

    # --- Input ---

    def focus_input(self):
        """Click the words area to focus MonkeyType's hidden input."""
        wrapper = self.page.query_selector(self.SEL_WORDS_WRAPPER)
        if wrapper:
            wrapper.click()
            time.sleep(0.2)

    # --- Completion detection ---

    def is_test_complete(self) -> bool:
        """Check if the result screen is visible."""
        result = self.page.query_selector(self.SEL_RESULT)
        if result:
            try:
                return result.is_visible()
            except Exception:
                return False
        return False

    # --- Results ---

    def get_results(self) -> Dict[str, str]:
        """Scrape the results page after test completion."""
        results = {}
        selectors = {
            "wpm": self.SEL_RESULT_WPM,
            "accuracy": self.SEL_RESULT_ACC,
            "raw_wpm": self.SEL_RESULT_RAW,
            "characters": self.SEL_RESULT_CHARS,
        }
        for key, sel in selectors.items():
            el = self.page.query_selector(sel)
            if el:
                results[key] = (el.text_content() or "").strip()
        return results
