"""Scraped result text must not carry terminal control characters."""

from automonkeytype.scraper import MonkeyTypeScraper


class _El:
    def text_content(self):
        return "\x1b]0;pwn\x07 85\r\x1b[2K"


class _Page:
    def query_selector(self, _sel):
        return _El()


def test_get_results_strips_control_characters():
    results = MonkeyTypeScraper(_Page()).get_results()
    assert results
    for value in results.values():
        assert not any(ord(c) < 32 or 0x7F <= ord(c) <= 0x9F for c in value)
        assert "85" in value
