"""Keyboard layout modeling with finger assignments and distance calculations.

Models a physical QWERTY keyboard with realistic row stagger offsets,
finger-to-key assignments, and inter-key distance computation used by
the humanizer to produce realistic keystroke timing.
"""

import math
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class KeyInfo:
    row: int
    col: float  # float to account for row stagger
    finger: int  # 0-7: L-pinky, L-ring, L-mid, L-index, R-index, R-mid, R-ring, R-pinky
    hand: str  # 'left' or 'right'


# Row stagger offsets (physical keyboard geometry)
_ROW_STAGGER = {0: 0.0, 1: 0.25, 2: 0.5, 3: 0.75}

# Vertical distance between rows (keys are ~1.9cm tall, ~1.9cm wide)
_ROW_SPACING = 1.0
_COL_SPACING = 1.0


def _key(row: int, col: int, finger: int, hand: str) -> KeyInfo:
    return KeyInfo(row=row, col=col + _ROW_STAGGER[row], finger=finger, hand=hand)


# fmt: off
LAYOUT: Dict[str, KeyInfo] = {
    # Row 0 — number row
    '`': _key(0, 0, 0, 'left'),
    '1': _key(0, 1, 0, 'left'),  '2': _key(0, 2, 1, 'left'),
    '3': _key(0, 3, 2, 'left'),  '4': _key(0, 4, 3, 'left'),
    '5': _key(0, 5, 3, 'left'),  '6': _key(0, 6, 4, 'right'),
    '7': _key(0, 7, 4, 'right'), '8': _key(0, 8, 5, 'right'),
    '9': _key(0, 9, 6, 'right'), '0': _key(0, 10, 7, 'right'),
    '-': _key(0, 11, 7, 'right'), '=': _key(0, 12, 7, 'right'),

    # Row 1 — top letter row
    'q': _key(1, 0, 0, 'left'),  'w': _key(1, 1, 1, 'left'),
    'e': _key(1, 2, 2, 'left'),  'r': _key(1, 3, 3, 'left'),
    't': _key(1, 4, 3, 'left'),  'y': _key(1, 5, 4, 'right'),
    'u': _key(1, 6, 4, 'right'), 'i': _key(1, 7, 5, 'right'),
    'o': _key(1, 8, 6, 'right'), 'p': _key(1, 9, 7, 'right'),
    '[': _key(1, 10, 7, 'right'), ']': _key(1, 11, 7, 'right'),
    '\\': _key(1, 12, 7, 'right'),

    # Row 2 — home row
    'a': _key(2, 0, 0, 'left'),  's': _key(2, 1, 1, 'left'),
    'd': _key(2, 2, 2, 'left'),  'f': _key(2, 3, 3, 'left'),
    'g': _key(2, 4, 3, 'left'),  'h': _key(2, 5, 4, 'right'),
    'j': _key(2, 6, 4, 'right'), 'k': _key(2, 7, 5, 'right'),
    'l': _key(2, 8, 6, 'right'), ';': _key(2, 9, 7, 'right'),
    "'": _key(2, 10, 7, 'right'),

    # Row 3 — bottom row
    'z': _key(3, 0, 0, 'left'),  'x': _key(3, 1, 1, 'left'),
    'c': _key(3, 2, 2, 'left'),  'v': _key(3, 3, 3, 'left'),
    'b': _key(3, 4, 3, 'left'),  'n': _key(3, 5, 4, 'right'),
    'm': _key(3, 6, 4, 'right'), ',': _key(3, 7, 5, 'right'),
    '.': _key(3, 8, 6, 'right'), '/': _key(3, 9, 7, 'right'),

    # Space bar (thumb, centered)
    ' ': KeyInfo(row=4, col=5.0, finger=3, hand='left'),
}
# fmt: on


def key_distance(a: str, b: str) -> float:
    """Euclidean distance between two keys in key-unit space."""
    ka, kb = LAYOUT.get(a), LAYOUT.get(b)
    if ka is None or kb is None:
        return 1.5  # default for unknown keys
    dx = (kb.col - ka.col) * _COL_SPACING
    dy = (kb.row - ka.row) * _ROW_SPACING
    return math.sqrt(dx * dx + dy * dy)


def same_finger(a: str, b: str) -> bool:
    """Whether two keys are typed with the same finger."""
    ka, kb = LAYOUT.get(a), LAYOUT.get(b)
    if ka is None or kb is None:
        return False
    return ka.finger == kb.finger


def same_hand(a: str, b: str) -> bool:
    """Whether two keys are typed with the same hand."""
    ka, kb = LAYOUT.get(a), LAYOUT.get(b)
    if ka is None or kb is None:
        return False
    return ka.hand == kb.hand


def hand_alternation(a: str, b: str) -> bool:
    """Whether typing b after a alternates hands (faster)."""
    ka, kb = LAYOUT.get(a), LAYOUT.get(b)
    if ka is None or kb is None:
        return False
    return ka.hand != kb.hand


# Neighboring keys for realistic typo generation
QWERTY_NEIGHBORS: Dict[str, list] = {
    'q': ['w', 'a'],
    'w': ['q', 'e', 'a', 's'],
    'e': ['w', 'r', 's', 'd'],
    'r': ['e', 't', 'd', 'f'],
    't': ['r', 'y', 'f', 'g'],
    'y': ['t', 'u', 'g', 'h'],
    'u': ['y', 'i', 'h', 'j'],
    'i': ['u', 'o', 'j', 'k'],
    'o': ['i', 'p', 'k', 'l'],
    'p': ['o', 'l'],
    'a': ['q', 'w', 's', 'z'],
    's': ['a', 'w', 'e', 'd', 'z', 'x'],
    'd': ['s', 'e', 'r', 'f', 'x', 'c'],
    'f': ['d', 'r', 't', 'g', 'c', 'v'],
    'g': ['f', 't', 'y', 'h', 'v', 'b'],
    'h': ['g', 'y', 'u', 'j', 'b', 'n'],
    'j': ['h', 'u', 'i', 'k', 'n', 'm'],
    'k': ['j', 'i', 'o', 'l', 'm'],
    'l': ['k', 'o', 'p'],
    'z': ['a', 's', 'x'],
    'x': ['z', 's', 'd', 'c'],
    'c': ['x', 'd', 'f', 'v'],
    'v': ['c', 'f', 'g', 'b'],
    'b': ['v', 'g', 'h', 'n'],
    'n': ['b', 'h', 'j', 'm'],
    'm': ['n', 'j', 'k'],
}
