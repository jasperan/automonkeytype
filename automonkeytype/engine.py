"""Core typing engine — orchestrates browser, scraper, humanizer, and PID controller.

This is the main loop: launch browser, navigate to MonkeyType, extract words,
type them with human-like timing while servo-controlling speed to the target WPM,
then report results.
"""

import random
import time
from typing import Optional

from .browser import BrowserManager
from .controller import WPMController
from .humanizer import TypingHumanizer
from .keyboard import QWERTY_NEIGHBORS
from .scraper import MonkeyTypeScraper


class TypingEngine:
    """Full-stack typing automation engine."""

    def __init__(
        self,
        target_wpm: float = 100,
        error_rate: float = 0.0,
        headless: bool = False,
        mode: str = "words",
        word_count: str = "50",
    ):
        self.target_wpm = target_wpm
        self.error_rate = error_rate
        self.headless = headless
        self.mode = mode
        self.word_count = word_count

        self.browser_mgr = BrowserManager(headless=headless)
        self.humanizer = TypingHumanizer(target_wpm, error_rate)
        self.controller = WPMController(target_wpm)
        self.scraper: Optional[MonkeyTypeScraper] = None

    def run(self):
        """Execute the full typing session."""
        try:
            self._setup()
            words = self._prepare_test()
            if not words:
                return
            self._type_words(words)
            self._report_results()
        except KeyboardInterrupt:
            _print("\nStopped by user.")
        except Exception as e:
            _print(f"Error: {e}")
            raise
        finally:
            self.browser_mgr.close()
            _print("Done.")

    # --- Private phases ---

    def _setup(self):
        _print(f"Launching browser (target: {self.target_wpm} WPM)...")
        page = self.browser_mgr.launch()
        self.scraper = MonkeyTypeScraper(page)

        _print("Navigating to MonkeyType...")
        self.browser_mgr.navigate()
        time.sleep(2)
        self.scraper.dismiss_popups()

    def _prepare_test(self) -> list:
        _print(f"Configuring: {self.mode} mode, {self.word_count}...")
        self.scraper.configure_test(self.mode, self.word_count)
        time.sleep(1)

        self.scraper.wait_for_test_ready()
        words = self.scraper.get_all_words()
        if not words:
            _print("No words found — MonkeyType may not have loaded correctly.")
            return []

        _print(f"Extracted {len(words)} words. Starting in 1s...")
        self.scraper.focus_input()
        time.sleep(0.5)
        return words

    def _type_words(self, words: list):
        """Type all words with human-like timing and PID speed control."""
        page = self.browser_mgr.page
        prev_char = None
        total = len(words)

        for word_idx, word in enumerate(words):
            if self.scraper.is_test_complete():
                break

            for char_idx, char in enumerate(word):
                # Compute human-like delay, scaled by PID controller
                delay = self.humanizer.get_delay(prev_char, char)
                delay *= self.controller.delay_multiplier

                # Add post-punctuation pause from previous char
                if prev_char:
                    delay += self.humanizer.get_punctuation_pause(prev_char)

                time.sleep(max(0.005, delay))

                # Possibly inject a typo (not on first char of word)
                if self.humanizer.should_make_error() and char_idx > 0:
                    self._inject_error(page, char)

                # Type the correct character
                page.keyboard.type(char)
                self.controller.record_keystroke()
                prev_char = char

            # Space between words (except after the last word)
            if word_idx < total - 1:
                delay = self.humanizer.get_delay(prev_char, " ")
                delay += self.humanizer.get_word_boundary_pause()
                delay *= self.controller.delay_multiplier
                time.sleep(max(0.005, delay))
                page.keyboard.press("Space")
                self.controller.record_keystroke()
                prev_char = " "

            # Update PID controller after each word
            self.controller.update()

            # Progress reporting every 10 words
            if (word_idx + 1) % 10 == 0:
                cur = self.controller.get_current_wpm()
                ovr = self.controller.get_overall_wpm()
                _print(
                    f"  [{word_idx+1}/{total}] "
                    f"Current: {cur:.0f} WPM | "
                    f"Overall: {ovr:.0f} WPM | "
                    f"Target: {self.target_wpm}"
                )

    def _inject_error(self, page, correct_char: str):
        """Type a wrong key, pause, then backspace (mimics human error)."""
        wrong = self._nearby_key(correct_char)
        page.keyboard.type(wrong)
        self.controller.record_keystroke()

        # Human reaction time before noticing the error
        time.sleep(self.humanizer.get_error_notice_delay())

        # Backspace to correct
        page.keyboard.press("Backspace")
        time.sleep(self.humanizer.get_correction_delay())

    def _report_results(self):
        """Wait for results and display them."""
        time.sleep(2)
        if self.scraper.is_test_complete():
            results = self.scraper.get_results()
            measured = self.controller.get_overall_wpm()
            _print("")
            _print("=" * 42)
            _print(" Results")
            _print("=" * 42)
            _print(f"  WPM:        {results.get('wpm', 'N/A')}")
            _print(f"  Accuracy:   {results.get('accuracy', 'N/A')}")
            _print(f"  Raw WPM:    {results.get('raw_wpm', 'N/A')}")
            _print(f"  Characters: {results.get('characters', 'N/A')}")
            _print(f"  Measured:   {measured:.1f} WPM")
            _print(f"  Target:     {self.target_wpm} WPM")
            _print("=" * 42)
        else:
            measured = self.controller.get_overall_wpm()
            _print(f"\nTest may still be running. Measured WPM: {measured:.1f}")

    @staticmethod
    def _nearby_key(char: str) -> str:
        """Pick a neighboring key for a realistic typo."""
        neighbors = QWERTY_NEIGHBORS.get(char.lower(), list("asdfghjkl"))
        result = random.choice(neighbors)
        return result.upper() if char.isupper() else result


def _print(msg: str):
    """Print with a project prefix."""
    print(f"[automonkeytype] {msg}")
