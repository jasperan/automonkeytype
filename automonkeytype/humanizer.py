"""Human-like keystroke timing generation.

Produces inter-key delays that model realistic human typing dynamics:
- Gaussian-distributed base delays calibrated to target WPM
- Bigram/trigram frequency bonuses (common pairs are faster)
- Finger travel distance penalties from keyboard geometry
- Same-finger penalties and hand-alternation bonuses
- Gradual fatigue accumulation over long sessions
- Realistic error injection with natural correction timing
"""

import random
from typing import Optional

from .keyboard import (
    key_distance,
    same_finger,
    hand_alternation,
    LAYOUT,
)

# Common English bigrams with speed multipliers.
# Lower value = faster (more muscle memory / practice).
BIGRAM_SPEED = {
    'th': 0.75, 'he': 0.75, 'in': 0.78, 'er': 0.76, 'an': 0.80,
    'on': 0.82, 'en': 0.80, 'at': 0.82, 'es': 0.83, 'ed': 0.81,
    'or': 0.82, 'ti': 0.84, 'is': 0.83, 'et': 0.85, 'it': 0.83,
    'al': 0.84, 'ar': 0.85, 'st': 0.82, 'to': 0.83, 'nt': 0.84,
    'ng': 0.85, 'se': 0.84, 'ha': 0.83, 'ou': 0.86, 're': 0.80,
    'io': 0.87, 'le': 0.85, 'nd': 0.83, 'ma': 0.86, 'de': 0.85,
    'te': 0.83, 'co': 0.86, 'me': 0.85, 'ne': 0.86, 've': 0.85,
    'ly': 0.87, 'ra': 0.85, 'ri': 0.86, 'li': 0.87, 'ce': 0.86,
    'ta': 0.85, 'el': 0.84, 'as': 0.85, 'pe': 0.86, 'of': 0.83,
    'us': 0.86, 'ea': 0.84, 'no': 0.85, 'la': 0.86, 'di': 0.87,
}

# Common trigrams that get an additional speed boost
TRIGRAM_SPEED = {
    'the': 0.90, 'and': 0.92, 'ing': 0.90, 'ent': 0.93, 'ion': 0.92,
    'tio': 0.93, 'for': 0.93, 'ate': 0.93, 'ous': 0.94, 'tha': 0.93,
}


class TypingHumanizer:
    """Generates human-like inter-key delays for typing simulation."""

    def __init__(
        self,
        target_wpm: float,
        error_rate: float = 0.0,
        fatigue_factor: float = 0.0003,
        consistency: float = 0.85,
    ):
        self.target_wpm = target_wpm
        # WPM = (chars/5) / minutes  =>  delay_per_char = 60 / (wpm * 5)
        self.base_delay = 60.0 / (target_wpm * 5)
        self.error_rate = max(0.0, min(1.0, error_rate))
        self.fatigue_factor = fatigue_factor
        # consistency 0-1: higher = less variance in timing
        self.noise_stddev = self.base_delay * (1.0 - consistency) * 0.5
        self.chars_typed = 0
        self._recent_chars: list = []  # last 3 chars for trigram detection
        self.rng = random.Random()

    def get_delay(self, prev_char: Optional[str], next_char: str) -> float:
        """Calculate delay in seconds before typing next_char."""
        delay = self.base_delay

        # --- Bigram adjustment ---
        if prev_char:
            bigram = (prev_char + next_char).lower()
            if bigram in BIGRAM_SPEED:
                delay *= BIGRAM_SPEED[bigram]

        # --- Trigram adjustment ---
        if len(self._recent_chars) >= 2:
            trigram = ''.join(self._recent_chars[-2:]) + next_char.lower()
            if trigram in TRIGRAM_SPEED:
                delay *= TRIGRAM_SPEED[trigram]

        # --- Keyboard geometry ---
        if prev_char:
            pc, nc = prev_char.lower(), next_char.lower()
            if pc in LAYOUT and nc in LAYOUT:
                dist = key_distance(pc, nc)
                # Distance penalty: ~4% slower per key-unit of travel
                delay *= 1.0 + dist * 0.04

                # Same-finger penalty (major slowdown — must lift and reposition)
                if same_finger(pc, nc):
                    delay *= 1.35

                # Hand alternation bonus (overlapping motion)
                if hand_alternation(pc, nc):
                    delay *= 0.85

        # --- Gaussian noise ---
        noise = self.rng.gauss(0, self.noise_stddev)
        delay = max(0.008, delay + noise)

        # --- Fatigue ---
        fatigue_mult = 1.0 + self.fatigue_factor * self.chars_typed
        delay *= fatigue_mult

        # --- Bookkeeping ---
        self.chars_typed += 1
        self._recent_chars.append(next_char.lower())
        if len(self._recent_chars) > 3:
            self._recent_chars.pop(0)

        return delay

    def should_make_error(self) -> bool:
        """Probabilistically determine if the next keystroke should be a typo."""
        if self.error_rate <= 0:
            return False
        return self.rng.random() < self.error_rate

    def get_error_notice_delay(self) -> float:
        """Time before the typist notices their error (reaction time)."""
        # Humans take ~200-500ms to notice a typo
        return max(0.1, self.rng.gauss(0.30, 0.08))

    def get_correction_delay(self) -> float:
        """Time to press backspace after noticing error."""
        return max(0.03, self.rng.gauss(0.08, 0.02))

    def get_word_boundary_pause(self) -> float:
        """Extra pause at word boundaries (cognitive chunking)."""
        return max(0.0, self.rng.gauss(0.015, 0.008))

    def get_punctuation_pause(self, char: str) -> float:
        """Extra pause after punctuation (natural reading rhythm)."""
        if char in '.!?':
            return max(0.0, self.rng.gauss(0.06, 0.025))
        elif char in ',;:':
            return max(0.0, self.rng.gauss(0.03, 0.015))
        return 0.0

    def reset(self):
        """Reset fatigue and state for a new test."""
        self.chars_typed = 0
        self._recent_chars.clear()
