"""Tests for human-like timing generation."""

from automonkeytype.humanizer import TypingHumanizer, BIGRAM_SPEED, TRIGRAM_SPEED


def test_base_delay_math():
    h = TypingHumanizer(target_wpm=100)
    # 100 WPM = 500 chars/min = 8.33 chars/sec => 120ms per char
    assert abs(h.base_delay - 0.120) < 0.001


def test_delays_are_positive():
    h = TypingHumanizer(target_wpm=150)
    for _ in range(100):
        d = h.get_delay("a", "b")
        assert d > 0


def test_bigram_speeds_up_common_pairs():
    h = TypingHumanizer(target_wpm=100, consistency=1.0)  # no noise
    # 'th' is a fast bigram; 'qz' is not
    d_th = h.get_delay("t", "h")
    h2 = TypingHumanizer(target_wpm=100, consistency=1.0)
    d_qz = h2.get_delay("q", "z")
    assert d_th < d_qz, "Common bigram 'th' should be faster than 'qz'"


def test_same_finger_penalty():
    h = TypingHumanizer(target_wpm=100, consistency=1.0)
    # e->d is same finger (both left middle)
    d_ed = h.get_delay("e", "d")
    h2 = TypingHumanizer(target_wpm=100, consistency=1.0)
    # e->j is different hand (much faster)
    d_ej = h2.get_delay("e", "j")
    assert d_ed > d_ej, "Same-finger pair should be slower"


def test_fatigue_increases_delay():
    h = TypingHumanizer(target_wpm=100, consistency=1.0, fatigue_factor=0.01)
    d_start = h.get_delay(None, "a")
    # Type 500 chars to accumulate fatigue
    for _ in range(500):
        h.get_delay("a", "b")
    d_fatigued = h.get_delay(None, "a")
    assert d_fatigued > d_start, "Delay should increase with fatigue"


def test_error_rate_zero_never_errors():
    h = TypingHumanizer(target_wpm=100, error_rate=0.0)
    errors = sum(h.should_make_error() for _ in range(1000))
    assert errors == 0


def test_error_rate_positive():
    h = TypingHumanizer(target_wpm=100, error_rate=0.1)
    errors = sum(h.should_make_error() for _ in range(10000))
    # Should be roughly 10% — allow wide margin
    assert 500 < errors < 1500, f"Expected ~1000 errors, got {errors}"


def test_error_notice_delay_positive():
    h = TypingHumanizer(target_wpm=100)
    for _ in range(50):
        d = h.get_error_notice_delay()
        assert d > 0


def test_word_boundary_pause():
    h = TypingHumanizer(target_wpm=100)
    pauses = [h.get_word_boundary_pause() for _ in range(100)]
    assert all(p >= 0 for p in pauses)


def test_punctuation_pause_sentence_end():
    h = TypingHumanizer(target_wpm=100)
    pauses = [h.get_punctuation_pause(".") for _ in range(50)]
    assert sum(pauses) / len(pauses) > 0.01, "Period should produce noticeable pause"


def test_punctuation_pause_none_for_letters():
    h = TypingHumanizer(target_wpm=100)
    assert h.get_punctuation_pause("a") == 0.0


def test_reset_clears_fatigue():
    h = TypingHumanizer(target_wpm=100)
    for _ in range(100):
        h.get_delay("a", "b")
    assert h.chars_typed == 100
    h.reset()
    assert h.chars_typed == 0


def test_bigram_table_values_in_range():
    for bigram, speed in BIGRAM_SPEED.items():
        assert len(bigram) == 2
        assert 0.5 < speed < 1.0, f"Bigram {bigram} speed {speed} out of range"


def test_trigram_table_values_in_range():
    for trigram, speed in TRIGRAM_SPEED.items():
        assert len(trigram) == 3
        assert 0.5 < speed < 1.0, f"Trigram {trigram} speed {speed} out of range"
