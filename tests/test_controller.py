"""Tests for PID WPM controller."""

import time

from automonkeytype.controller import WPMController


def test_initial_multiplier_is_one():
    c = WPMController(target_wpm=100)
    assert c.delay_multiplier == 1.0


def test_initial_wpm_is_target():
    c = WPMController(target_wpm=100)
    assert c.get_current_wpm() == 100.0


def test_overall_wpm_zero_before_start():
    c = WPMController(target_wpm=100)
    assert c.get_overall_wpm() == 0.0


def test_typing_too_fast_increases_multiplier():
    c = WPMController(target_wpm=50)
    # Simulate very fast typing (tiny delays)
    for _ in range(30):
        c.record_keystroke()
        time.sleep(0.005)
    c.update()
    assert c.delay_multiplier > 1.0, "Should slow down when typing too fast"


def test_typing_too_slow_decreases_multiplier():
    c = WPMController(target_wpm=500)
    # Simulate slow typing (large delays)
    for _ in range(20):
        c.record_keystroke()
        time.sleep(0.05)
    c.update()
    assert c.delay_multiplier < 1.0, "Should speed up when typing too slow"


def test_multiplier_clamped():
    c = WPMController(target_wpm=50)
    # Extreme speed
    for _ in range(100):
        c.record_keystroke()
        time.sleep(0.001)
    c.update()
    assert c.delay_multiplier <= 3.0, "Multiplier should be clamped at 3.0"


def test_reset():
    c = WPMController(target_wpm=100)
    for _ in range(10):
        c.record_keystroke()
        time.sleep(0.01)
    c.update()
    c.reset()
    assert c.delay_multiplier == 1.0
    assert c.get_overall_wpm() == 0.0
    assert c.get_current_wpm() == 100.0


def test_overall_wpm_tracks_cumulative():
    c = WPMController(target_wpm=100)
    for _ in range(50):
        c.record_keystroke()
        time.sleep(0.01)
    wpm = c.get_overall_wpm()
    assert wpm > 0, "Overall WPM should be positive after typing"
