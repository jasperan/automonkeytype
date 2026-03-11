"""PID controller for servo-locking typing speed to a target WPM.

Continuously measures rolling WPM from keystroke timestamps and outputs
a delay multiplier that the engine applies to the humanizer's base delays.
When you're typing too fast, it increases delay; too slow, it decreases.
"""

import time
from collections import deque


class WPMController:
    """PID-based WPM controller with rolling window measurement."""

    def __init__(
        self,
        target_wpm: float,
        kp: float = 0.4,
        ki: float = 0.08,
        kd: float = 0.15,
        window_size: int = 60,
    ):
        self.target_wpm = target_wpm
        self.kp = kp
        self.ki = ki
        self.kd = kd

        # Rolling window of keystroke timestamps
        self._timestamps: deque = deque(maxlen=window_size)
        self._char_count = 0
        self._start_time: float | None = None

        # PID state
        self._integral = 0.0
        self._prev_error = 0.0
        self.delay_multiplier = 1.0

    def record_keystroke(self):
        """Record the timestamp of a keystroke."""
        now = time.monotonic()
        if self._start_time is None:
            self._start_time = now
        self._timestamps.append(now)
        self._char_count += 1

    def get_current_wpm(self) -> float:
        """Calculate WPM from the rolling window."""
        if len(self._timestamps) < 2:
            return self.target_wpm
        elapsed = self._timestamps[-1] - self._timestamps[0]
        if elapsed < 0.01:
            return self.target_wpm
        chars = len(self._timestamps) - 1
        return (chars / 5.0) / (elapsed / 60.0)

    def get_overall_wpm(self) -> float:
        """Calculate WPM since the first keystroke."""
        if self._start_time is None or self._char_count < 2:
            return 0.0
        elapsed = time.monotonic() - self._start_time
        if elapsed < 0.01:
            return 0.0
        return (self._char_count / 5.0) / (elapsed / 60.0)

    def update(self) -> float:
        """Run one PID iteration and return the updated delay multiplier.

        Error is positive when we're typing too fast (need to slow down)
        and negative when too slow (need to speed up).
        """
        current_wpm = self.get_current_wpm()
        error = current_wpm - self.target_wpm

        # Accumulate integral with anti-windup clamping
        self._integral += error
        self._integral = max(-60.0, min(60.0, self._integral))

        # Derivative (rate of change of error)
        derivative = error - self._prev_error
        self._prev_error = error

        # PID output: scale down to a fractional adjustment
        adjustment = (
            self.kp * error + self.ki * self._integral + self.kd * derivative
        ) / 100.0

        # Clamp multiplier to sane range (0.3x to 3.0x base delay)
        self.delay_multiplier = max(0.3, min(3.0, 1.0 + adjustment))
        return self.delay_multiplier

    def reset(self):
        """Reset all state for a new test."""
        self._timestamps.clear()
        self._char_count = 0
        self._start_time = None
        self._integral = 0.0
        self._prev_error = 0.0
        self.delay_multiplier = 1.0
